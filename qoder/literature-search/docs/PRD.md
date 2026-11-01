# PRD：LitSeek 文献与资料混合检索系统（Qoder × seekdb 参赛项目）

## 1. 项目背景与目标

学习、科研和工作中，论文片段、课程笔记、实验记录、资料文档分散存放，
用户想找到「讲同一个主题、但用词不同」的段落非常困难。本项目用 **seekdb** 作为
向量 + 全文 + 标量条件的混合检索引擎，构建一个轻量、可复现的**文献与资料检索 Web 应用**：

- 导入论文 / 课程笔记 / 实验记录 / 资料文档，自动切片入库；
- 支持**语义检索**（找意思相近、用词不同的段落）、**关键词检索**（精确命中术语）、
  **混合检索**（RRF 融合两路）；
- 可按资料类型（source）、主题（topic）过滤；
- 每条结果给出标题、出处、主题、原文段落、相似度/得分与排名来源，便于回溯出处；
- 提供内置示例语料，一键初始化即可体验。

技术栈：**Python 3 + FastAPI + pymysql（seekdb 服务端 MySQL 协议）+ 原生静态前端（HTML/CSS/JS，无前端构建步骤）**。

## 2. 必须先读

实现前先阅读同目录 `docs/seekdb-notes.md`，其中记录了已在 seekdb 实例上验证通过的
表结构、SQL 写法、向量字面量拼接方式、索引类型与连接约束，**严格照做**。

## 3. 目录结构（在当前项目根 `qoder/literature-search/` 下生成）

```
literature-search/
├── README.md                 # 运行说明（由 Qoder 按实现结果补全，见第 9 节）
├── .env.example             # 占位配置，禁止真实密钥
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── config.py            # 从环境变量读取 seekdb 连接与应用配置
│   ├── embeddings.py         # 封装 DefaultEmbeddingFunction 与文本切片
│   ├── store.py             # seekdb 访问层：建表、入库、三类检索、统计、删除、列表
│   ├── schemas.py           # Pydantic 请求/响应模型
│   └── main.py              # FastAPI 应用、路由、静态文件托管、健康检查
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── data/
│   └── sample_docs.jsonl    # 内置示例语料（已提供，见第 7 节）
├── scripts/
│   ├── seed.py              # 读取 sample_docs.jsonl 入库（幂等：先清表再导入）
│   └── reset_db.py          # 删除并重建 lit_chunks 表
├── tests/
│   └── smoke_test.py        # 不依赖前端、针对 API 与检索层的冒烟测试
└── docs/
    ├── seekdb-notes.md      # 已给定，勿改事实
    └── validation-samples.md# 验证样例（实现后补全实测结果）
```

## 4. 配置（app/config.py）

从环境变量读取，缺省值仅用于本地；`.env.example` 全部用占位符：

| 变量 | 说明 | 默认 |
|---|---|---|
| `SEEKDB_HOST` | seekdb 服务端主机 | `127.0.0.1` |
| `SEEKDB_PORT` | 端口 | `2881` |
| `SEEKDB_USER` | 用户名 | `root` |
| `SEEKDB_PASSWORD` | 密码（不入库、不提交） | 空 |
| `SEEKDB_DATABASE` | 数据库名 | `literature` |
| `SEEKDB_TENANT` | 租户；云端匿名实例留空，普通 OceanBase server 可填 `sys` | 空 |
| `EMBEDDING_DIM` | 向量维度 | `384` |
| `RRF_K` | RRF 常数 | `60` |
| `APP_HOST` / `APP_PORT` | 监听地址端口 | `0.0.0.0` / `8000` |

连接：`pymysql.connect(host, port, user, password, database, ssl={}, autocommit=True, charset="utf8mb4")`。
若 `SEEKDB_TENANT` 非空，用户名拼接为 `user@tenant`；为空则使用纯用户名（云端匿名实例要求）。
提供单例连接管理（`get_conn()`），每次查询取连接、用完归还/关闭，避免长连接断线。

## 5. 检索层（app/store.py）接口约定

### 5.1 初始化
- `ensure_schema()`：按 `docs/seekdb-notes.md` 第 3 节建表（`CREATE TABLE IF NOT EXISTS`）。
- `reset()`：`DROP TABLE IF EXISTS lit_chunks` 后重建。

### 5.2 文档入库
- `add_document(title, source, topic, text, metadata=None) -> list[chunk_id]`
  - 调用 `embeddings.py` 的切片函数，把长文按段落/句子切成 200~400 字的 chunk；
  - 每个 chunk 本地生成 384 维向量；
  - 按 notes 第 4 节方式拼向量字面量，写入 `lit_chunks`；
  - chunk id 用 `uuid4().hex[:16]`；`metadata` 存入原始标题、来源、主题、chunk 序号。
- `bulk_add(documents)`：批量调用上述方法。

### 5.3 检索
统一返回结构：

```json
{
  "mode": "hybrid",
  "query": "用户提问",
  "total": 18,
  "results": [
    {
      "id": "ab12...",
      "title": "RAG 架构综述",
      "source": "paper",
      "topic": "rag",
      "text": "命中段落原文……",
      "distance": 0.4203,
      "ft_score": null,
      "rank": 1,
      "vector_rank": 1,
      "fulltext_rank": 2,
      "score": 0.03226
    }
  ]
}
```

- `search(query, mode="hybrid"|"vector"|"fulltext", top_k=6, topic=None, source=None)`
  - `mode=vector`：只走向量检索；`distance` 填余弦距离，`fulltext_rank=null`。
  - `mode=fulltext`：只走 IK 全文；`ft_score` 填全文得分，`vector_rank=null`。
  - `mode=hybrid`：两路各取候选（建议各取 `top_k * 3`），RRF 融合排序，
    回填两路排名与 RRF 分数；`distance`/`ft_score` 取各自命中值，未命中的一路为 `null`。
  - `topic`、`source` 为可选标量过滤，三路查询都要支持。
- `stats() -> {"total": n, "by_source": {"paper": n, ...}, "by_topic": {...}}`
- `list_documents(limit=50)`：按 `_id` 返回已入库条目（用于前端列表）。
- `delete_document(doc_id)`：按 `_id` 删除。

### 5.4 切片（app/embeddings.py）
- `split_text(text, max_chars=300)`：先按空行分段，超长段再按句号/分号切分，
  保证每段不超过 `max_chars` 且不切断中文句子；返回 chunk 列表。
- `embed(texts) -> list[list[float]]`：封装 `DefaultEmbeddingFunction()`，线程内复用单例。

## 6. HTTP 接口（app/main.py，FastAPI）

- `GET /api/health`：返回 `{"status":"ok","seekdb":"connected","total": n}`，用于连通性检查。
- `GET /api/stats`：返回 `stats()` 结果。
- `GET /api/documents?limit=`：返回已入库条目列表。
- `POST /api/search`：JSON `{ "query": str, "mode": "hybrid", "top_k": 6, "topic": str|null, "source": str|null }`，返回第 5.3 节结构。
- `POST /api/documents`：JSON `{ "title", "source", "topic", "text" }`，入库后返回新增 chunk 数量。
- `DELETE /api/documents/{doc_id}`：删除。
- `GET /` 与静态资源：托管 `web/` 目录，前端从 `/app.js`、`/style.css` 加载。
- 允许跨域（`CORSMiddleware` 放行本地开发来源）。
- 错误处理：seekdb 连接失败时 `/api/health` 返回 503 与可读错误信息，而不是崩溃。

## 7. 示例语料 data/sample_docs.jsonl

每行一条 JSON：`{"title", "source", "topic", "text"}`。
至少 **18 条**，覆盖：
- `source`：`paper`（论文）、`note`（课程笔记）、`lab`（实验记录）、`book`（教材/资料）；
- `topic`：`database`、`rag`、`vector-search`、`nlp`、`machine-learning`、`workflow`；
- 中文为主，包含可被 IK 精确命中的术语（事务、倒排索引、向量、余弦、切片、分词、幻觉、监控、周报等）；
- 同时包含语义相近但用词不同的段落，用于演示混合检索优于单一路径。
- `scripts/seed.py` 读取该文件幂等入库；`--reset` 先清表。

## 8. 前端（web/，原生三件套，不得引入打包器/框架 CDN 依赖构建）

单页应用 `index.html`：

1. 顶部：项目名 **LitSeek 文献与资料检索**、简短副标题、连通状态指示灯（调 `/api/health`）。
2. 搜索区：
   - 大输入框；
   - 模式切换：**混合检索 / 语义检索 / 关键词检索**（三个按钮，默认混合）；
   - 过滤下拉：资料类型 `source`（全部 / paper / note / lab / book）、主题 `topic`（全部 + 现有主题）；
   - 结果数量 `top_k` 选择（3/6/10）；「搜索」按钮与回车触发。
3. 结果列表：卡片展示标题、来源标签、主题标签、段落原文、
   排名徽标（混合：同时显示语义排名/关键词排名）、相似度距离或关键词得分；命中关键词在段落中高亮。
4. 侧边/下方：`stats()` 汇总（总量、各类型数量、各主题数量）；「导入示例语料」按钮调用 seed 等价逻辑或提供说明；
   提供一个「新增资料」小表单（标题/类型/主题/正文），提交到 `POST /api/documents`。
5. 空态与错误态：未输入给提示；检索报错展示后端返回的可读信息。
6. 风格：简洁学术风，浅灰白底 + 单一强调色（避免大面积紫/靛蓝），移动端可读。

## 9. README.md 运行说明（最终需包含）

- 项目简介、功能截图占位、技术栈；
- 环境要求（Python 3.11+；seekdb 服务端三种接入方式：云端免费实例 / 本地 seekdb server / Docker）；
- 安装：创建虚拟环境、`pip install -r requirements.txt`；
- 配置：复制 `.env.example` 为 `.env`，填写连接参数（占位符说明，禁止真实密钥入库）；
- 初始化：`python scripts/seed.py`；
- 启动：`uvicorn app.main:app --host 0.0.0.0 --port 8000`，浏览器打开首页；
- 接口清单与示例请求；
- seekdb 在本项目中承担的职责说明（向量索引、IK 全文索引、距离计算、标量过滤、统计）；
- 目录说明、常见问题（向量模型首次下载、Windows 不支持 embedded、云端实例有效期）。

## 10. 验收标准（实现完成后必须自测通过）

1. 不登录即可打开网站首页；
2. `GET /api/health` 返回 connected；
3. seed 后 `GET /api/stats` 总量与示例语料一致；
4. 三条模式各执行一次检索，都能返回结果；混合模式同时记录两路排名；
5. `topic` / `source` 过滤生效；
6. 新增资料可检索到；删除后不再出现在列表；
7. `tests/smoke_test.py` 在本地可运行并通过；
8. 代码内无真实账号密码，密钥只来自环境变量。

## 11. 非目标（本期不做）

- 不做用户登录注册、不做多租户权限；
- 不接大模型问答生成，只做检索与出处定位；
- 不引入前端框架与构建工具；
- 不实现 seekdb 嵌入式（Windows 不支持），检索层统一走服务端 MySQL 协议。
