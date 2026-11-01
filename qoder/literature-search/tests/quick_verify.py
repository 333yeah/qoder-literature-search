import json, urllib.request, time, urllib.error
BASE = "http://127.0.0.1:8000"
time.sleep(6)

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        return r.status, r.read().decode("utf-8")

def post(path, payload):
    req = urllib.request.Request(BASE + path, method="POST",
        data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, json.loads(r.read().decode("utf-8"))

s, h = get("/api/health"); print("health", s, h)
s, st = get("/api/stats"); print("stats", s, json.dumps(st, ensure_ascii=False))
s, sr = post("/api/search", {"query": "检索增强生成", "mode": "hybrid", "top_k": 3})
print("search", s, "total", sr["total"], "top", sr["results"][0]["title"], sr["results"][0]["score"])
s, home = get("/")
print("home", s, "LitSeek" in home, len(home))
