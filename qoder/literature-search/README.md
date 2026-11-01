# LitSeek 文献与资料混合检索系统

> Qoder × OceanBase 参赛项目（Qoder × seekdb 赛道）—— 面向论文、课程笔记、实验记录与资料文档的语义 + 关键词 + 标量条件混合检索 Web 应用。
> 技术组合：**仅使用 seekdb**（未接入 PowerContext）。

## 1. 项目简介

### 1.1 解决的问题

学习、科研和工作中，论文、课堂笔记、实验记录、会议资料往往分散在多个文档里：
- 按关键词搜不到「换个说法描述」的相关段落；
- 纯语义检索又难以命中专有名词、术语编号；
- 资料类型（论文/笔记/实验/资料）和主题混杂，难以按范围收敛。

LitSeek 把这些资料导入 seekdb，同时建立向量索引与中文全文索引，提供**语义检索、关键词检索、混合检索**三种方式，并支持按资料类型与主题做标量过滤，快速定位到相关段落与出处。

### 1.2 核心功能

- 资料导入：论文 / 笔记 / 实验记录 / 资料文档在线新增，自动切片、生成 384 维向量入库；内置 18 条中文示例语料，一键初始化。
- 语义检索（vector）：基于 IVF_FLAT 余弦向量索引，按 `cosine_distance` 升序召回语义相近段落。
- 关键词检索（fulltext）：IK 中文分词倒排索引，`MATCH ... AGAINST (... NATURAL LANGUAGE MODE)` 相关性排序，支持专有名词精确命中。
- 混合检索（hybrid）：向量与全文两路候选各取 `top_k*3`，应用层按 RRF `1/(k+rank+1)`（k=60）融合排序。
- 标量过滤：按 `source`（paper/note/lab/book）与 `topic`（database/rag/vector-search/nlp/machine-learning/workflow）组合过滤。
- 检索结果给出标题、出处、主题、原文段落、语义排名、关键词排名、RRF/距离/全文得分，并高亮命中词。
- 数据概览：总量与按类型、主题的分组统计；已入库资料列表、单条删除。

### 1.3 项目演示与代码仓库

- 项目展示网站（Qoder Sites 公开发布）：https://litseek-demo-kgb0khpkzds.qoder.zone/ 。站点首屏复用现有应用界面，以内置 18 条示例数据做浏览器只读演示；静态站点不承载后端，完整 seekdb 混合检索按第 4、5 节在本地复现。
- 代码仓库：https://github.com/333yeah/qoder-literature-search （公开仓库，默认分支 `2026-competition-ecosystem`）。
- 本地运行与复现步骤见本文第 4、5 节；完整验证样例见 `docs/validation-samples.md`。

### 1.4 Qoder 开发说明（对应赛题「项目必须使用 Qoder 开发」）

本项目主体开发工作在 **Qoder CN** 中完成：Qoder agent 依据 `docs/PRD.md` 与 `docs/seekdb-notes.md` 完成需求拆解、后端检索层、前端单页、脚本与测试的主体编码，后续在同一会话内由 Qoder 完成对照盘点、缺陷修复、连库初始化、测试调试与文档对齐。开发环节提示词、阶段顺序与截图要求见 `docs/qoder-development-playbook.md`；对话与终端证据归档在 `docs/screenshots/dev-record/`。本仓库不包含在 Qoder 之外另行开发的独立工程。

## 2. 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11+ / FastAPI / uvicorn / pydantic v2 |
| 数据库 | seekdb（MySQL 协议；IVF_FLAT 余弦向量索引 + IK 全文索引） |
| 数据库驱动 | pymysql（直连 MySQL 协议） |
| 向量模型 | pyseekdb `DefaultEmbeddingFunction`（384 维，ONNX Runtime 本地推理） |
| 前端 | 原生 HTML / CSS / JavaScript，无框架、无构建步骤、无外部 CDN |

## 3. seekdb 部署与接入方式

本项目通过 MySQL 协议直连 seekdb 服务端，不使用嵌入式（embedded）实例。三选一准备可用实例：

1. **云端免费实例（推荐评审快速复现）**：在 seekdb 控制台申请临时实例，获得 `host/port/user/password/database`；云端实例认证用户名不带租户，`SEEKDB_TENANT` 留空。
2. **本地 seekdb server**：在本机或内网启动 seekdb 服务端，填写本地 `host/port`；普通服务端如需租户，在 `SEEKDB_TENANT` 填写对应租户。
3. **Docker 容器**：按 seekdb 官方文档以 Docker 方式启动服务端，将端口映射到本机后填写连接参数。

> Windows 本机当前不支持嵌入式 embedded seekdb；本项目统一走服务端 MySQL 协议，因此不依赖本地嵌入式进程。
> 云端免费实例有有效期，过期后在 `.env` 更换新实例参数，重新执行 `python scripts/seed.py --reset` 即可。

## 4. 环境准备与安装

### 4.1 运行环境

- 操作系统：Windows / macOS / Linux 均可（本项目在 Windows 11 + Python 3.13.16 上完成实测）
- Python：3.11 及以上（依赖见 `requirements.txt`）

### 4.2 创建虚拟环境并安装依赖

```bash
# 进入项目目录
cd qoder/literature-search

# 创建虚拟环境
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

`requirements.txt` 关键依赖：`fastapi`、`uvicorn`、`pymysql`、`pyseekdb`、`python-dotenv`、`pydantic`、`numpy`、`onnxruntime`、`tokenizers`、`httpx`（测试客户端）。

### 4.3 配置连接参数

```bash
# 复制模板
cp .env.example .env        # Windows: copy .env.example .env
```

编辑 `.env`，填写可用 seekdb 实例参数：

| 变量 | 说明 | 默认 |
|---|---|---|
| `SEEKDB_HOST` | seekdb 主机 | `127.0.0.1` |
| `SEEKDB_PORT` | 端口 | `2881` |
| `SEEKDB_USER` | 用户名 | `root` |
| `SEEKDB_PASSWORD` | 密码 | 空 |
| `SEEKDB_DATABASE` | 数据库名 | `literature` |
| `SEEKDB_TENANT` | 租户；云端匿名/纯用户名实例留空 | 空 |
| `EMBEDDING_DIM` | 向量维度 | `384` |
| `RRF_K` | RRF 常数 | `60` |
| `APP_HOST` / `APP_PORT` | 监听地址与端口 | `0.0.0.0:8000` |

> `.env` 已在 `.gitignore` 中，**禁止提交真实账号、密码或实例地址**；仓库内仅保留占位符模板 `.env.example`。

## 5. 初始化数据、启动服务与验证

### 5.1 初始化示例语料

```bash
# 确保表结构存在并导入示例语料（不加 --reset 为增量导入）
python scripts/seed.py

# 需要清空重建时：先 DROP + CREATE 再导入
python scripts/seed.py --reset
```

`data/sample_docs.jsonl` 内置 18 条中文示例语料；实测入库后共 18 个片段，统计为：
- 按类型：note 7、paper 4、lab 4、book 3
- 按主题：database 4、rag 4、vector-search 4、nlp 3、machine-learning 2、workflow 1

### 5.2 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

浏览器打开 `http://localhost:8000`，**无需登录**即可访问首页；右上角状态指示为「已连接（N chunks）」表示 seekdb 正常。

### 5.3 运行冒烟测试

```bash
python tests/smoke_test.py
```

覆盖：连接、建表入库、统计、三类检索、topic/source 过滤、HTTP API、新增可检索、删除回落、静态页面。实测 **28 项检查全部通过**。

## 6. HTTP 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查，返回连接状态与片段总量；连接失败返回 503 |
| GET | `/api/stats` | 总量、按 source / topic 分组统计 |
| GET | `/api/documents?limit=50` | 已入库条目列表 |
| POST | `/api/search` | 检索：`{query, mode, top_k, topic?, source?}` |
| POST | `/api/documents` | 新增资料：`{title, source, topic, text}` |
| POST | `/api/seed` | 从内置语料重置并导入（幂等） |
| DELETE | `/api/documents/{doc_id}` | 删除指定片段 |

### 6.1 示例请求

```bash
# 混合检索
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"检索增强生成","mode":"hybrid","top_k":6}'

# 带过滤的语义检索
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"事务一致性","mode":"vector","top_k":3,"source":"paper"}'

# 主题过滤的关键词检索
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"倒排索引","mode":"fulltext","top_k":5,"topic":"vector-search"}'
```

## 7. seekdb 在本项目中的职责（可核对）

| 能力 | seekdb 内实现 | 代码位置 |
|---|---|---|
| 向量列与向量索引 | `embedding VECTOR(384)`；`VECTOR INDEX idx_vec ... DISTANCE=cosine, TYPE=IVF_FLAT, LIB=OB`，`ORGANIZATION=HEAP` | `app/store.py` `ensure_schema()` |
| 向量写入 | float32 小端字节转为十六进制字面量 `X'<hex>'` 拼入 INSERT SQL | `app/store.py` `_vec_to_hex()` / `add_document()` |
| 语义检索 | `cosine_distance(embedding, X'<hex>')`，`ORDER BY ... APPROXIMATE LIMIT n` | `app/store.py` `search_vector()` |
| 中文全文检索 | `FULLTEXT INDEX idx_fts (document) WITH PARSER ik`；`MATCH ... AGAINST(... NATURAL LANGUAGE MODE)` | `app/store.py` `search_fulltext()` |
| 标量过滤 | `WHERE topic = %s AND source = %s` | `app/store.py` `_build_filter_clauses()` |
| 统计聚合 | `COUNT(*)`、`GROUP BY source`、`GROUP BY topic` | `app/store.py` `stats()` |
| 删除 | `DELETE FROM lit_chunks WHERE _id = %s` | `app/store.py` `delete_document()` |
| 混合排序 | 两路候选在应用层 RRF 融合（seekdb 只负责单路排序） | `app/store.py` `search_hybrid()` |

## 8. 目录结构

```
literature-search/
├── app/
│   ├── __init__.py
│   ├── config.py          # 环境变量与 .env 加载
│   ├── embeddings.py      # 嵌入函数与文本切片
│   ├── store.py           # seekdb 访问层（建表/入库/检索/统计/删除）
│   ├── schemas.py         # Pydantic 请求/响应模型
│   └── main.py            # FastAPI 路由、静态文件、CORS、健康检查
├── web/
│   ├── index.html         # 单页前端
│   ├── style.css         # 浅色学术风样式（teal 单一强调色）
│   └── app.js            # 前端交互与 API 对接
├── data/
│   └── sample_docs.jsonl  # 内置示例语料（18 条）
├── scripts/
│   ├── seed.py            # 导入示例数据（支持 --reset）
│   └── reset_db.py        # 删除并重建表结构
├── tests/
│   ├── smoke_test.py      # 冒烟测试（28 项）
│   ├── verify_add_delete.py
│   └── record_search_results.py
├── docs/
│   ├── PRD.md             # 产品需求文档
│   ├── seekdb-notes.md    # 已验证的 seekdb 事实与约束
│   ├── qoder-development-playbook.md  # 在 Qoder 内开发的阶段提示词与取证流程
│   ├── validation-samples.md  # 验证样例（输入/步骤/预期/技术作用记录）
│   ├── search-results-record.json  # 真实检索结果留存
│   ├── submission-checklist.md     # 大赛提交材料对照清单
│   └── screenshots/      # 界面验证截图与 Qoder 开发记录截图
├── requirements.txt
├── .env.example
└── .gitignore
```

## 9. 截图与验证材料

界面截图位于 `docs/screenshots/`：

| 文件 | 内容 |
|---|---|
| 01-home.png | 首页：连接状态、统计概览、三种模式与过滤控件 |
| 02-hybrid-search.png | 混合检索：语义/关键词排名徽标、RRF、命中词高亮 |
| 03-vector-search.png | 语义检索：余弦距离与语义排名 |
| 04-fulltext-search.png | 关键词检索：全文得分与命中词高亮 |
| 05-filter-paper-rag.png | source=paper 且 topic=rag 双重过滤 |
| 06-add-document.png | 新增资料表单与已入库列表 |
| 07-docs-list.png | 已入库资料列表（18 chunks） |

## 10. 已知限制

- 384 维通用嵌入模型对中文长句语义区分能力有限；口语化提问的向量召回可能弱于关键词召回，因此默认使用混合模式互补。
- 云端免费 seekdb 实例有生命周期，过期需更换实例参数并重新 seed。
- 初始语料篇幅较短，每条为 1 个片段；长文档由 `app/embeddings.py` 按段落 / 句子自动切片。
- 首次运行 `pyseekdb` 会在本地缓存嵌入模型；后续启动无需重复下载。
