"""LitSeek 冒烟测试：针对 API 与检索层，需要可用的 seekdb 连接"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import store
from fastapi.testclient import TestClient
from app.main import app


passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name}  {detail}")


def main():
    global passed, failed

    print("=" * 60)
    print("LitSeek 冒烟测试")
    print("=" * 60)

    # 0. 连通性
    print("\n--- 0. 连通性 ---")
    try:
        conn = store.get_conn()
        conn.close()
        check("seekdb 连接", True)
    except Exception as e:
        check("seekdb 连接", False, str(e))
        print("\n无法连接 seekdb，终止测试。")
        sys.exit(1)

    # 1. 重置 & 入库
    print("\n--- 1. 重置 & 入库 ---")
    store.reset()
    check("reset() 执行", True)

    jsonl_path = Path(__file__).parent.parent / "data" / "sample_docs.jsonl"
    docs = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))

    total_chunks = store.bulk_add(docs)
    check(f"bulk_add 入库 ({len(docs)} 条文档 → {total_chunks} 片段)", total_chunks >= len(docs))

    # 2. 统计
    print("\n--- 2. 统计 ---")
    s = store.stats()
    check("stats() 返回总量", s["total"] == total_chunks, f"期望 {total_chunks}，实际 {s['total']}")
    check("stats() 含 by_source", "paper" in s["by_source"])
    check("stats() 含 by_topic", "rag" in s["by_topic"])

    # 3. 三类检索
    print("\n--- 3. 三类检索 ---")
    vec_r = store.search("向量检索", mode="vector", top_k=3)
    check("vector 检索返回结果", len(vec_r["results"]) > 0)
    if vec_r["results"]:
        r0 = vec_r["results"][0]
        check("vector 结果含 distance", r0["distance"] is not None)
        check("vector 结果 vector_rank 不为空", r0["vector_rank"] is not None)
        check("vector 结果 fulltext_rank 为空", r0["fulltext_rank"] is None)

    ft_r = store.search("事务 隔离", mode="fulltext", top_k=3)
    check("fulltext 检索返回结果", len(ft_r["results"]) > 0)
    if ft_r["results"]:
        r0 = ft_r["results"][0]
        check("fulltext 结果含 ft_score", r0["ft_score"] is not None)
        check("fulltext 结果 fulltext_rank 不为空", r0["fulltext_rank"] is not None)
        check("fulltext 结果 vector_rank 为空", r0["vector_rank"] is None)

    hyb_r = store.search("检索增强生成", mode="hybrid", top_k=3)
    check("hybrid 检索返回结果", len(hyb_r["results"]) > 0)
    if hyb_r["results"]:
        r0 = hyb_r["results"][0]
        check("hybrid 结果含 score (RRF)", r0["score"] is not None)
        check("hybrid 结果含 vector_rank", r0["vector_rank"] is not None)

    # 4. 标量过滤
    print("\n--- 4. 标量过滤 ---")
    filter_r = store.search("向量", mode="vector", top_k=10, source="paper")
    all_paper = all(r["source"] == "paper" for r in filter_r["results"])
    check("source=paper 过滤", all_paper and len(filter_r["results"]) > 0)

    filter_r2 = store.search("检索", mode="fulltext", top_k=10, topic="rag")
    all_rag = all(r["topic"] == "rag" for r in filter_r2["results"])
    check("topic=rag 过滤", all_rag and len(filter_r2["results"]) > 0)

    # 5. API 接口测试
    print("\n--- 5. API 接口 ---")
    client = TestClient(app)

    resp = client.get("/api/health")
    check("GET /api/health", resp.status_code == 200 and resp.json().get("seekdb") == "connected")

    resp = client.get("/api/stats")
    check("GET /api/stats", resp.status_code == 200 and resp.json()["total"] > 0)

    resp = client.get("/api/documents?limit=5")
    check("GET /api/documents", resp.status_code == 200 and len(resp.json()) <= 5)

    resp = client.post("/api/search", json={"query": "向量", "mode": "hybrid", "top_k": 3})
    check("POST /api/search", resp.status_code == 200 and resp.json()["total"] > 0)

    # 6. 新增 & 删除
    print("\n--- 6. 新增 & 删除 ---")
    # 正文包含可被 IK 全文精确命中的独有标识词，便于验证新增资料确实可检索
    sample_text = "这是一条用于冒烟测试的文档，编号关键词为 锌铍实验样本，用于验证新增和删除功能是否正常工作。"
    resp = client.post("/api/documents", json={
        "title": "冒烟测试文档",
        "source": "lab",
        "topic": "workflow",
        "text": sample_text,
    })
    check("POST /api/documents 新增", resp.status_code == 200 and resp.json()["chunks"] > 0)
    new_id = resp.json()["id"]

    resp = client.post("/api/search", json={"query": "锌铍实验样本", "mode": "fulltext", "top_k": 3})
    found = any(r["id"] == new_id for r in resp.json()["results"])
    check("新增文档可被检索到", found)

    resp = client.delete(f"/api/documents/{new_id}")
    check("DELETE /api/documents/{id}", resp.status_code == 200)

    resp = client.delete(f"/api/documents/{new_id}")
    check("重复删除返回 404", resp.status_code == 404)

    # 7. 静态页面
    print("\n--- 7. 静态页面 ---")
    resp = client.get("/")
    check("GET / 返回 HTML", resp.status_code == 200 and "LitSeek" in resp.text)

    # 汇总
    print("\n" + "=" * 60)
    print(f"测试完成：{passed} 通过，{failed} 失败")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
