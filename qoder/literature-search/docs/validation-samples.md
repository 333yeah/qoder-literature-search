# 验证样例（Validation Samples）

> 项目：LitSeek 文献与资料混合检索系统
> 技术底座：seekdb（MySQL 协议）+ FastAPI + 原生前端；仅使用 seekdb，不接入 PowerContext。
> 本文所有结果均来自 **2026-10-28 本机真实运行** 记录。

## 1. 运行环境与启动步骤

### 1.1 环境

- 操作系统：Windows 11（本机无 Docker / WSL，故不使用 embedded seekdb）
- Python：3.13（虚拟环境 `.venv`）
- 后端框架：FastAPI + uvicorn；驱动：pymysql（直连 seekdb MySQL 协议）
- 向量模型：pyseekdb `DefaultEmbeddingFunction`，384 维
- 前端：原生 HTML / CSS / JavaScript，无框架、无构建步骤

### 1.2 启动步骤（评审可按此复现）

```bash
# 1) 进入项目目录
cd qoder/literature-search

# 2) 创建并激活虚拟环境，安装依赖
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3) 复制配置模板，填写可用的 seekdb 服务端 / 云端实例连接参数
copy .env.example .env
# 编辑 .env，填写 SEEKDB_HOST / PORT / USER / PASSWORD / DATABASE / TENANT

# 4) 初始化示例语料（--reset 表示先清表再导入）
python scripts/seed.py --reset

# 5) 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 6) 浏览器打开 http://localhost:8000 ；未登录即可访问首页
```

### 1.3 自动化验证

```bash
python tests/smoke_test.py
```

实测结果：**28 项检查全部通过，0 失败**（连接、建表入库、统计、三类检索、标量过滤、HTTP API、新增/删除、静态页面）。日志见 `smoke.log`。

## 2. 初始数据（seed 后状态）

内置语料 `data/sample_docs.jsonl` 共 **18 条文档**，每条切片为 1 个片段，入库后共 **18 个片段（chunks）**。

### 2.1 按资料类型 source 统计（GET /api/stats 实测）

| source | 含义 | 数量 |
|---|---|---|
| note | 课程笔记 | 7 |
| paper | 论文 | 4 |
| lab | 实验记录 | 4 |
| book | 资料/书籍 | 3 |

### 2.2 按主题 topic 统计（GET /api/stats 实测）

| topic | 数量 |
|---|---|
| database | 4 |
| rag | 4 |
| vector-search | 4 |
| nlp | 3 |
| machine-learning | 2 |
| workflow | 1 |

### 2.3 18 条初始文档清单

| # | 标题 | source | topic |
|---|---|---|---|
| 1 | LSM 树与写优化笔记 | note | database |
| 2 | 事务隔离级别梳理 | note | database |
| 3 | OceanBase 分布式架构要点 | paper | database |
| 4 | 索引与查询计划实验记录 | lab | database |
| 5 | 检索增强生成 RAG 综述 | paper | rag |
| 6 | RAG 落地踩坑笔记 | note | rag |
| 7 | 实验记录：RAG 召回率对比 | lab | rag |
| 8 | 知识库问答资料整理 | book | rag |
| 9 | 向量相似度检索方法 | paper | vector-search |
| 10 | 嵌入模型选型笔记 | note | vector-search |
| 11 | 实验记录：IVF 与 HNSW 对比 | lab | vector-search |
| 12 | 倒排索引与全文检索 | book | vector-search |
| 13 | 中文分词与 IK 词典 | note | nlp |
| 14 | 文本向量化原理 | paper | nlp |
| 15 | 实验记录：分词错误案例 | lab | nlp |
| 16 | 机器学习评估指标笔记 | note | machine-learning |
| 17 | 过拟合与正则化资料 | book | machine-learning |
| 18 | 周报与实验记录整理模板 | note | workflow |

## 3. 验证用例（输入 / 步骤 / 预期 / 实测结果）

> 检索接口：`POST /api/search`，请求体 `{"query": ..., "mode": hybrid|vector|fulltext, "top_k": 3, "topic"?, "source"?}`。
> 排名从 1 开始；向量结果 `distance` 为余弦距离（越小越相似）；全文结果 `ft_score` 为自然语言模式相关性得分（越大越相关）；混合结果 `rrf` 为 RRF 融合分。

### 用例 1：混合检索（hybrid，语义 + 关键词，RRF 融合）

- **输入**：`query = "检索增强生成"`，`mode = "hybrid"`，`top_k = 3`
- **步骤**：前端点「混合检索」→ 搜索；后端分别取向量候选与全文候选各 `top_k*3`，应用层按 RRF `1/(k+rank+1)`（k=60）合并排序。
- **预期**：返回与 RAG 直接相关的片段；第一条同时出现在两路候选前列；结果携带语义排名、关键词排名与 RRF 分数。
- **实测结果**（共 3 条，2026-10-28 本机实测）：

| 排名 | 标题 | source | topic | 语义排名 | 关键词排名 | 余弦距离 | 全文得分 | RRF |
|---|---|---|---|---|---|---|---|---|
| 1 | 检索增强生成 RAG 综述 | paper | rag | 1 | 1 | 0.2128 | 3.0040 | 0.03279 |
| 2 | 知识库问答资料整理 | book | rag | 2 | 2 | 0.3277 | 1.1011 | 0.03226 |
| 3 | 实验记录：分词错误案例 | lab | nlp | 6 | 4 | 0.5524 | 0.2087 | 0.03078 |

- **seekdb 作用记录**：向量索引 `idx_vec`（IVF_FLAT，cosine）完成语义召回；IK 全文索引 `idx_fts` 完成关键词召回；两路候选在应用层 RRF 融合，seekdb 本身不执行跨路排序。

### 用例 2：语义检索（vector，自然语言提问）

- **输入**：`query = "如何减少大模型生成答案时的幻觉"`，`mode = "vector"`，`top_k = 3`
- **步骤**：后端对提问生成 384 维向量，调用 `cosine_distance(embedding, X'<hex>')` 按向量索引近似检索，距离升序返回。
- **预期**：语义最接近的 RAG 片段排在首位；结果仅带余弦距离与语义排名，不出现全文得分。
- **实测结果**（共 3 条，2026-10-28 本机实测）：

| 排名 | 标题 | source | topic | 余弦距离 |
|---|---|---|---|---|
| 1 | 检索增强生成 RAG 综述 | paper | rag | 0.2352 |
| 2 | 知识库问答资料整理 | book | rag | 0.3106 |
| 3 | 索引与查询计划实验记录 | lab | database | 0.4012 |

- **seekdb 作用记录**：`cosine_distance()` 由 seekdb 在向量索引上计算；`ORDER BY ... APPROXIMATE LIMIT n` 使用 IVF_FLAT 近似最近邻检索。

### 用例 3：关键词检索（fulltext，IK 分词 + 自然语言相关性）

- **输入**：`query = "事务 隔离 级别"`，`mode = "fulltext"`，`top_k = 3`
- **步骤**：`MATCH(document) AGAINST(%s IN NATURAL LANGUAGE MODE)`，IK 分词后按倒排相关性得分降序。
- **预期**：直接包含「事务/隔离/级别」的数据库笔记排第一；结果仅带全文得分与关键词排名。
- **实测结果**（共 2 条，2026-10-28 本机实测）：

| 排名 | 标题 | source | topic | 全文得分 |
|---|---|---|---|---|
| 1 | 事务隔离级别梳理 | note | database | 3.2314 |
| 2 | OceanBase 分布式架构要点 | paper | database | 0.9329 |

- **seekdb 作用记录**：`idx_fts` 使用 `WITH PARSER ik` 中文分词；倒排索引与相关性打分均由 seekdb 完成。

### 用例 4：主题标量过滤（topic = vector-search，混合检索）

- **输入**：`query = "向量索引 近似最近邻"`，`mode = "hybrid"`，`topic = "vector-search"`，`top_k = 3`
- **步骤**：两路 SQL 均追加 `WHERE topic = %s` 标量条件后再各自召回、融合。
- **预期**：返回结果全部属于 `vector-search` 主题。
- **实测结果**（共 3 条，topic 均为 vector-search，2026-10-28 本机实测）：

| 排名 | 标题 | source | 语义排名 | 关键词排名 | RRF |
|---|---|---|---|---|---|
| 1 | 嵌入模型选型笔记 | note | 1 | 2 | 0.03252 |
| 2 | 向量相似度检索方法 | paper | 3 | 1 | 0.03227 |
| 3 | 实验记录：IVF 与 HNSW 对比 | lab | 2 | 4 | 0.03175 |

### 用例 5：资料类型标量过滤（source = paper，关键词检索）

- **输入**：`query = "倒排索引 全文检索"`，`mode = "fulltext"`，`source = "paper"`，`top_k = 3`
- **预期**：返回结果全部为 `paper`。
- **实测结果**（共 2 条，source 均为 paper，2026-10-28 本机实测）：

| 排名 | 标题 | topic | 全文得分 |
|---|---|---|---|
| 1 | 向量相似度检索方法 | vector-search | 0.5896 |
| 2 | 检索增强生成 RAG 综述 | rag | 0.1809 |

### 用例 6：新增资料 → 可检索 → 删除后不再出现

- **步骤**：
  1. `POST /api/documents` 提交：标题《中文分词与 IK 词典扩展实测笔记》，source=note，topic=nlp，正文含独有标识词「星芒分词机」。返回 `{"id": "56b0de9ebce9450b", "chunks": 1, "message": "ok"}`。
  2. `GET /api/stats`：总量由 18 变为 **19**（note 7→8，nlp 3→4）。
  3. `POST /api/search`，`query="星芒分词机"`，`mode="fulltext"`：新文档以全文得分 **5.4302** 排第 1，确认可检索到。
  4. `DELETE /api/documents/56b0de9ebce9450b`：返回 200 `{"deleted": true, "id": "56b0de9ebce9450b"}`。
  5. 再次 `GET /api/stats`：总量回到 **18**，note=7、nlp=3，与初始状态一致。
- **预期**：新增即入库可召回；删除后该条目消失，统计回落。
- **实测**（2026-10-28 本机实测）：全部符合。

## 4. 接口与功能验收对照

| # | 验收标准 | 结果 | 证据 |
|---|---|---|---|
| 1 | 未登录即可打开网站首页 | 通过 | 截图 `screenshots/01-home.png`；首页无登录墙 |
| 2 | `GET /api/health` 返回 connected | 通过 | smoke 测试第 5 节；`server.log` 200 OK |
| 3 | seed 后 `GET /api/stats` 总量与语料一致 | 通过 | 18 片段；source/topic 统计见第 2 节 |
| 4 | 三种模式各执行一次检索均返回结果 | 通过 | 用例 1 / 2 / 3；截图 02 / 03 / 04 |
| 5 | topic / source 过滤生效 | 通过 | 用例 4 / 5；截图 05 |
| 6 | 新增资料可检索到，删除后不再出现 | 通过 | 用例 6；`verify_add_delete.log` |
| 7 | `tests/smoke_test.py` 可运行并通过 | 通过 | 28 通过 / 0 失败，`smoke.log` |
| 8 | 代码内无真实账号密码 | 通过 | 密钥仅存于本机 `.env`（已被 `.gitignore` 忽略）；仓库内仅 `.env.example` 占位符 |

## 5. seekdb 在本项目中的具体作用（读写记录可核对）

| 能力 | seekdb 内实现 | 对应代码 |
|---|---|---|
| 建表与向量列 | `embedding VECTOR(384)`；`VECTOR INDEX idx_vec ... DISTANCE=cosine, TYPE=IVF_FLAT, LIB=OB`，`ORGANIZATION=HEAP` | `app/store.py` `ensure_schema()` |
| 向量写入 | 384 维 float32 以小端 hex 字面量 `X'<hex>'` 直接拼入 INSERT SQL | `app/store.py` `_vec_to_hex()` / `add_document()` |
| 语义检索 | `cosine_distance(embedding, X'<hex>')`，`ORDER BY ... APPROXIMATE LIMIT n` | `app/store.py` `search_vector()` |
| 中文全文检索 | `FULLTEXT INDEX idx_fts (document) WITH PARSER ik`；`MATCH ... AGAINST(... NATURAL LANGUAGE MODE)` | `app/store.py` `search_fulltext()` |
| 标量过滤 | `WHERE topic = %s AND source = %s` | `app/store.py` `_build_filter_clauses()` |
| 统计聚合 | `COUNT(*)`、`GROUP BY source`、`GROUP BY topic` | `app/store.py` `stats()` |
| 删除 | `DELETE FROM lit_chunks WHERE _id = %s` | `app/store.py` `delete_document()` |
| 混合排序 | 两路候选在应用层 RRF 融合（seekdb 只提供单路排序结果） | `app/store.py` `search_hybrid()` |

## 6. 界面截图清单（`docs/screenshots/`）

| 文件 | 内容 |
|---|---|
| 01-home.png | 首页：连接状态、统计概览、三种模式与过滤控件 |
| 02-hybrid-search.png | 混合检索结果：语义/关键词排名徽标、RRF 分数、命中词高亮 |
| 03-vector-search.png | 语义检索结果：仅余弦距离与语义排名 |
| 04-fulltext-search.png | 关键词检索结果：仅全文得分与关键词排名、命中词高亮 |
| 05-filter-paper-rag.png | source=paper 且 topic=rag 双重过滤结果 |
| 06-add-document.png | 新增资料表单与已入库资料列表 |
| 07-docs-list.png | 刷新后的已入库资料列表（18 chunks） |

## 7. 已知限制与说明

- 向量模型为 384 维通用嵌入模型，对中文长句的语义区分能力有限；口语化提问的向量召回可能弱于关键词召回，因此默认采用混合模式互补。
- 云端免费 seekdb 实例有有效期，过期后需在 `.env` 更换新实例参数并重新执行 `python scripts/seed.py --reset`。
- 每条初始文档篇幅较短，当前各为 1 个片段；长文档会按段落/句子在 `app/embeddings.py` `split_text()` 中自动切片。
