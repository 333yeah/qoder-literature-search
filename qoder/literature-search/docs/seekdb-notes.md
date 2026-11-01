# seekdb 已验证事实与约束（实现时必须遵守）

> 本文件记录在本机 + seekdb 云端实例上实际跑通、并被探针验证过的结论。
> Qoder 实现检索层时以本文件为准，不要凭空换用未验证的 SQL 语法或索引类型。

## 1. 运行环境与连接

- 应用通过 MySQL 协议（`pymysql`）连接 seekdb **服务端**（云端实例 / 本地 seekdb server / Docker 均可）。
- 依赖：`pyseekdb`（仅复用其内置 `DefaultEmbeddingFunction` 本地生成向量）、`pymysql`。
- 连接参数全部来自环境变量（见 `.env.example`），代码内不允许出现真实账号密码。
- 云端匿名实例认证：**不带 tenant 后缀**，用户名原样传入；`pymysql.connect(..., ssl={})`。
- 本机 Windows 不支持嵌入式（embedded）seekdb；本地复现请用本地 server / Docker / 云端实例。

## 2. 向量模型

- `ef = pyseekdb.DefaultEmbeddingFunction()`，输出 **384 维** float32 向量。
- `ef(["文本"])` 返回 `list[list[float]]`；`ef.dimension` 为维度。
- 模型首次运行自动从 Hugging Face 镜像下载并缓存到 `~/.cache/pyseekdb/onnx_models`。
- 该模型偏英文，**中文语义由全文检索（IK 分词）补强**，混合检索由 RRF 融合两路结果。

## 3. 表结构（已在建表探针上验证通过）

```sql
CREATE TABLE IF NOT EXISTS lit_chunks (
  _id        VARCHAR(128) PRIMARY KEY,
  title      TEXT,
  source     TEXT,          -- paper | note | lab | book | doc
  topic      TEXT,
  document   TEXT,
  embedding  VECTOR(384),
  metadata   JSON,
  FULLTEXT INDEX idx_fts (document) WITH PARSER ik,
  VECTOR INDEX idx_vec (embedding) WITH (DISTANCE=cosine, TYPE=IVF_FLAT, LIB=OB)
) ORGANIZATION = HEAP;
```

- 云端匿名实例**不支持 HNSW/HGRAPH**；向量索引用 `IVF_FLAT`，距离 `cosine`。
- 全文索引用 `IK` 分词器，字段为 `document`。

## 4. 向量字面量（关键坑，已踩过）

- 向量不能作为 `%s` 参数走 `pymysql` 占位符；必须先把 `list[float]` 打包成小端 float32，
  转成十六进制，**直接拼进 SQL 字符串** `X'<hex>'`。
- 生成方式（与 `pyseekdb` 内部 `_embedding_to_hexstring` 一致）：

```python
import struct
hexstr = struct.pack(f"<{len(vec)}f", *vec).hex()
sql = f"..., embedding = X'{hexstr}' ..."   # hexstr 只含 0-9a-f，无注入面
```

## 5. 三类查询（探针已全部跑通）

### 5.1 向量语义检索

```sql
SELECT _id, title, source, topic, document,
       cosine_distance(embedding, X'<hex>') AS distance
FROM lit_chunks
[WHERE topic = %s] [AND source = %s]
ORDER BY cosine_distance(embedding, X'<hex>') APPROXIMATE LIMIT %s;
```

- `distance` 越小越相近。

### 5.2 关键词全文检索（IK 分词）

```sql
SELECT _id, title, source, topic, document,
       MATCH(document) AGAINST(%s IN NATURAL LANGUAGE MODE) AS score
FROM lit_chunks
WHERE MATCH(document) AGAINST(%s IN NATURAL LANGUAGE MODE)
[AND topic = %s] [AND source = %s]
ORDER BY score DESC
LIMIT %s;
```

### 5.3 混合检索（应用层 RRF 融合，等价 seekdb 官方 hybrid RRF）

- 分别在 seekdb 内执行向量检索与全文检索，各自得到排序列表。
- 应用层 RRF：`score_rrf = Σ 1/(k + rank + 1)`，默认 `k = 60`。
- 两路候选合并后按 RRF 分数降序返回；同时保留 `vector_rank`、`ft_rank`、`distance`、`ft_score` 便于前端展示来源。

## 6. 已验证的辅助 SQL

- 标量过滤：`WHERE topic = %s`、`WHERE source = %s`，可与检索条件组合。
- 统计：`SELECT source, COUNT(*) AS n FROM lit_chunks GROUP BY source;`
- 总量：`SELECT COUNT(*) FROM lit_chunks;`
- 删除：`DELETE FROM lit_chunks WHERE _id = %s;`
- `metadata` 列为 JSON，可正常回读。

## 7. 探针位置（开发记录附件，不进入正式运行代码）

- `literature-search` 目录旁的 `probe3_sql_hybrid.py`：向量 + 全文 + RRF 混合检索验证。
- `probe4_filters.py`：标量过滤、分组统计、多词全文、删除、JSON 回读验证。
