"""seekdb 访问层：建表、入库、三类检索、统计、删除、列表"""
import struct
import uuid
import json
import pymysql
from app import config
from app.embeddings import embed, split_text


def _get_user():
    if config.SEEKDB_TENANT:
        return f"{config.SEEKDB_USER}@{config.SEEKDB_TENANT}"
    return config.SEEKDB_USER


def get_conn():
    return pymysql.connect(
        host=config.SEEKDB_HOST,
        port=config.SEEKDB_PORT,
        user=_get_user(),
        password=config.SEEKDB_PASSWORD,
        database=config.SEEKDB_DATABASE,
        ssl={},
        autocommit=True,
        charset="utf8mb4",
    )


def ensure_schema():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS lit_chunks (
                  _id        VARCHAR(128) PRIMARY KEY,
                  title      TEXT,
                  source     TEXT,
                  topic      TEXT,
                  document   TEXT,
                  embedding  VECTOR({config.EMBEDDING_DIM}),
                  metadata   JSON,
                  FULLTEXT INDEX idx_fts (document) WITH PARSER ik,
                  VECTOR INDEX idx_vec (embedding) WITH (DISTANCE=cosine, TYPE=IVF_FLAT, LIB=OB)
                ) ORGANIZATION = HEAP
            """)
    finally:
        conn.close()


def reset():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS lit_chunks")
    finally:
        conn.close()
    ensure_schema()


def _vec_to_hex(vec: list[float]) -> str:
    return struct.pack(f"<{len(vec)}f", *vec).hex()


def add_document(title: str, source: str, topic: str, text: str, metadata: dict | None = None) -> list[str]:
    chunks = split_text(text)
    if not chunks:
        return []

    vectors = embed(chunks)
    chunk_ids = []

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
                chunk_id = uuid.uuid4().hex[:16]
                hexstr = _vec_to_hex(vec)
                meta = json.dumps({
                    **(metadata or {}),
                    "original_title": title,
                    "source": source,
                    "topic": topic,
                    "chunk_index": i,
                }, ensure_ascii=False)

                sql = (
                    "INSERT INTO lit_chunks (_id, title, source, topic, document, embedding, metadata) "
                    f"VALUES (%s, %s, %s, %s, %s, X'{hexstr}', %s)"
                )
                cur.execute(sql, (chunk_id, title, source, topic, chunk, meta))
                chunk_ids.append(chunk_id)
    finally:
        conn.close()

    return chunk_ids


def bulk_add(documents: list[dict]) -> int:
    total_chunks = 0
    for doc in documents:
        ids = add_document(doc["title"], doc["source"], doc["topic"], doc["text"])
        total_chunks += len(ids)
    return total_chunks


def _build_filter_clauses(filters: dict, param_list: list, alias: str = "") -> str:
    """构建可选的 WHERE 子句（topic / source 标量过滤）"""
    clauses = []
    prefix = f"{alias}." if alias else ""
    if filters.get("topic"):
        clauses.append(f"{prefix}topic = %s")
        param_list.append(filters["topic"])
    if filters.get("source"):
        clauses.append(f"{prefix}source = %s")
        param_list.append(filters["source"])
    return (" WHERE " + " AND ".join(clauses)) if clauses else ""


def search_vector(query: str, top_k: int = 6, topic: str | None = None, source: str | None = None) -> list[dict]:
    vec = embed([query])[0]
    hexstr = _vec_to_hex(vec)

    filters = {"topic": topic, "source": source}
    params = []
    where = _build_filter_clauses(filters, params)

    sql = (
        f"SELECT _id, title, source, topic, document, "
        f"cosine_distance(embedding, X'{hexstr}') AS distance "
        f"FROM lit_chunks{where} "
        f"ORDER BY cosine_distance(embedding, X'{hexstr}') APPROXIMATE LIMIT %s"
    )
    params.append(top_k)

    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {
            "id": r["_id"],
            "title": r["title"],
            "source": r["source"],
            "topic": r["topic"],
            "text": r["document"],
            "distance": float(r["distance"]),
            "ft_score": None,
            "vector_rank": i,
            "fulltext_rank": None,
            "rank": i,
            "score": None,
        }
        for i, r in enumerate(rows)
    ]


def search_fulltext(query: str, top_k: int = 6, topic: str | None = None, source: str | None = None) -> list[dict]:
    filters = {"topic": topic, "source": source}
    params = [query, query]
    filter_params = []
    where_ft = _build_filter_clauses(filters, filter_params)

    where_clause = ""
    if where_ft:
        where_clause = f" AND {where_ft.strip(' WHERE ')}"
        params.extend(filter_params)
    params.append(top_k)

    sql = (
        "SELECT _id, title, source, topic, document, "
        "MATCH(document) AGAINST(%s IN NATURAL LANGUAGE MODE) AS score "
        "FROM lit_chunks "
        f"WHERE MATCH(document) AGAINST(%s IN NATURAL LANGUAGE MODE){where_clause} "
        "ORDER BY score DESC LIMIT %s"
    )

    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {
            "id": r["_id"],
            "title": r["title"],
            "source": r["source"],
            "topic": r["topic"],
            "text": r["document"],
            "distance": None,
            "ft_score": float(r["score"]),
            "vector_rank": None,
            "fulltext_rank": i,
            "rank": i,
            "score": None,
        }
        for i, r in enumerate(rows)
    ]


def search_hybrid(query: str, top_k: int = 6, topic: str | None = None, source: str | None = None) -> list[dict]:
    candidate_k = top_k * 3
    vec_results = search_vector(query, top_k=candidate_k, topic=topic, source=source)
    ft_results = search_fulltext(query, top_k=candidate_k, topic=topic, source=source)

    k = config.RRF_K
    combined = {}

    for rank, r in enumerate(vec_results):
        cid = r["id"]
        combined[cid] = {
            "id": cid,
            "title": r["title"],
            "source": r["source"],
            "topic": r["topic"],
            "text": r["text"],
            "distance": r["distance"],
            "ft_score": None,
            "vector_rank": rank,
            "fulltext_rank": None,
            "rrf": 1.0 / (k + rank + 1),
        }

    for rank, r in enumerate(ft_results):
        cid = r["id"]
        if cid in combined:
            combined[cid]["ft_score"] = r["ft_score"]
            combined[cid]["fulltext_rank"] = rank
            combined[cid]["rrf"] += 1.0 / (k + rank + 1)
        else:
            combined[cid] = {
                "id": cid,
                "title": r["title"],
                "source": r["source"],
                "topic": r["topic"],
                "text": r["text"],
                "distance": None,
                "ft_score": r["ft_score"],
                "vector_rank": None,
                "fulltext_rank": rank,
                "rrf": 1.0 / (k + rank + 1),
            }

    sorted_results = sorted(combined.values(), key=lambda x: x["rrf"], reverse=True)[:top_k]

    for i, r in enumerate(sorted_results):
        r["rank"] = i
        r["score"] = r.pop("rrf")

    return sorted_results


def search(query: str, mode: str = "hybrid", top_k: int = 6,
           topic: str | None = None, source: str | None = None) -> dict:
    if mode == "vector":
        results = search_vector(query, top_k, topic, source)
    elif mode == "fulltext":
        results = search_fulltext(query, top_k, topic, source)
    else:
        results = search_hybrid(query, top_k, topic, source)

    return {"mode": mode, "query": query, "total": len(results), "results": results}


def stats() -> dict:
    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS n FROM lit_chunks")
            total = cur.fetchone()["n"]

            cur.execute("SELECT source, COUNT(*) AS n FROM lit_chunks GROUP BY source")
            by_source = {r["source"]: r["n"] for r in cur.fetchall()}

            cur.execute("SELECT topic, COUNT(*) AS n FROM lit_chunks GROUP BY topic")
            by_topic = {r["topic"]: r["n"] for r in cur.fetchall()}
    finally:
        conn.close()

    return {"total": total, "by_source": by_source, "by_topic": by_topic}


def list_documents(limit: int = 50) -> list[dict]:
    conn = get_conn()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                "SELECT _id, title, source, topic, document, metadata "
                "FROM lit_chunks ORDER BY _id LIMIT %s",
                (limit,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    results = []
    for r in rows:
        meta = r["metadata"]
        if isinstance(meta, str):
            meta = json.loads(meta)
        results.append({
            "id": r["_id"],
            "title": r["title"],
            "source": r["source"],
            "topic": r["topic"],
            "text": r["document"],
            "metadata": meta,
        })
    return results


def delete_document(doc_id: str) -> bool:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM lit_chunks WHERE _id = %s", (doc_id,))
            return cur.rowcount > 0
    finally:
        conn.close()
