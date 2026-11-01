"""留存三类检索与过滤的真实返回结果，供 docs/validation-samples.md 引用"""
import json, urllib.request, sys
from pathlib import Path

BASE = "http://127.0.0.1:8000"
OUT = Path(__file__).parent.parent / "docs" / "search-results-record.json"

def call(method, path, payload=None):
    req = urllib.request.Request(BASE + path, method=method)
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=body, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

queries = [
    ("hybrid", "检索增强生成", None, None),
    ("vector", "如何减少大模型生成答案时的幻觉", None, None),
    ("fulltext", "事务 隔离 级别", None, None),
    ("hybrid", "向量索引 近似最近邻", None, "vector-search"),
    ("vector", "实验记录 周报 模板", None, None),
    ("fulltext", "倒排索引 全文检索", "paper", None),
]

record = {"stats": call("GET", "/api/stats"), "cases": []}
for mode, q, source, topic in queries:
    payload = {"query": q, "mode": mode, "top_k": 3}
    if source: payload["source"] = source
    if topic: payload["topic"] = topic
    res = call("POST", "/api/search", payload)
    record["cases"].append({
        "mode": mode, "query": q, "source": source, "topic": topic,
        "total": res["total"],
        "results": [
            {
                "rank": x["rank"] + 1, "title": x["title"],
                "source": x["source"], "topic": x["topic"],
                "text": x["text"],
                "distance": round(x["distance"], 4) if x["distance"] is not None else None,
                "ft_score": round(x["ft_score"], 4) if x["ft_score"] is not None else None,
                "rrf": round(x["score"], 5) if x["score"] is not None else None,
                "vector_rank": None if x["vector_rank"] is None else x["vector_rank"] + 1,
                "fulltext_rank": None if x["fulltext_rank"] is None else x["fulltext_rank"] + 1,
            } for x in res["results"]
        ],
    })

OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
print("written:", OUT, "cases:", len(record["cases"]))
