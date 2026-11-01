"""FastAPI 应用、路由、静态文件托管、健康检查"""
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import json as _json

from app import store
from app.schemas import (
    SearchRequest, SearchResponse,
    DocumentCreate, DocumentCreateResponse,
    StatsResponse,
)

WEB_DIR = Path(__file__).parent.parent / "web"
DATA_DIR = Path(__file__).parent.parent / "data"


@asynccontextmanager
async def lifespan(application: FastAPI):
    # 建表失败不应阻断服务启动：数据库不可用时由 /api/health 返回 503，页面仍可打开
    try:
        store.ensure_schema()
    except Exception as exc:  # pragma: no cover - 启动期容错
        print(f"[startup] ensure_schema 未完成（数据库暂不可达）：{exc}")
    yield


app = FastAPI(title="LitSeek", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    try:
        s = store.stats()
        conn = store.get_conn()
        conn.close()
        return {"status": "ok", "seekdb": "connected", "total": s["total"]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"seekdb connection failed: {e}")


@app.get("/api/stats", response_model=StatsResponse)
def get_stats():
    return store.stats()


@app.get("/api/documents")
def get_documents(limit: int = Query(default=50, ge=1, le=500)):
    return store.list_documents(limit=limit)


@app.post("/api/search", response_model=SearchResponse)
def do_search(req: SearchRequest):
    if req.mode not in ("hybrid", "vector", "fulltext"):
        raise HTTPException(status_code=400, detail=f"invalid mode: {req.mode}")
    return store.search(
        query=req.query,
        mode=req.mode,
        top_k=req.top_k,
        topic=req.topic,
        source=req.source,
    )


@app.post("/api/documents", response_model=DocumentCreateResponse)
def create_document(doc: DocumentCreate):
    try:
        chunk_ids = store.add_document(doc.title, doc.source, doc.topic, doc.text)
        return {"id": chunk_ids[0] if chunk_ids else "", "chunks": len(chunk_ids), "message": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{doc_id}")
def remove_document(doc_id: str):
    deleted = store.delete_document(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="document not found")
    return {"deleted": True, "id": doc_id}


@app.post("/api/seed")
def seed_documents():
    """从 data/sample_docs.jsonl 导入示例语料（幂等：先清表再导入）"""
    try:
        store.reset()
        jsonl_path = DATA_DIR / "sample_docs.jsonl"
        if not jsonl_path.exists():
            raise HTTPException(status_code=404, detail="sample_docs.jsonl not found")

        documents = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    documents.append(_json.loads(line))

        chunks = store.bulk_add(documents)
        return {"imported": len(documents), "chunks": chunks, "message": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/style.css")
def style_css():
    return FileResponse(WEB_DIR / "style.css", media_type="text/css")


@app.get("/app.js")
def app_js():
    return FileResponse(WEB_DIR / "app.js", media_type="application/javascript")
