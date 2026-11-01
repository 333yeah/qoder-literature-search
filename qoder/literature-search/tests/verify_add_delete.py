import json, urllib.request

BASE = "http://127.0.0.1:8000"

def call(method, path, payload=None):
    req = urllib.request.Request(BASE + path, method=method)
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=body, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

# 1. 全文检索独有词，确认新文档可召回
res = call("POST", "/api/search", {"query": "星芒分词机", "mode": "fulltext", "top_k": 3})
print("FULLTEXT RESULTS:", [(x["id"], x["title"], round(x["ft_score"], 4)) for x in res["results"]])

# 2. 语义检索自然语言问题，验证一路召回
res2 = call("POST", "/api/search", {"query": "怎么扩展中文分词词典", "mode": "vector", "top_k": 3})
print("VECTOR TOP3:", [(x["id"], x["title"], round(x["distance"], 4)) for x in res2["results"]])

# 3. 定位并删除测试新文档
docs = call("GET", "/api/documents?limit=200")
target = [d for d in docs if d["id"] == "f27858aec58c4326"]
print("TARGET FOUND:", bool(target))
if target:
    call("DELETE", "/api/documents/f27858aec58c4326")
stats = call("GET", "/api/stats")
print("STATS AFTER DELETE:", json.dumps(stats, ensure_ascii=False))
