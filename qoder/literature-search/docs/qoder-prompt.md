# 提交给 Qoder agent 的任务指令（复制后粘贴到 Qoder 输入框发送）

请在目录 `C:\Users\86139\Doubao\chats\2026-10-28\new-chat\powercontext\qoder\literature-search` 下开发 **LitSeek 文献与资料混合检索 Web 应用**。

第一步先用内置 CLI 完整读取该目录的 `docs\PRD.md`（产品需求、目录结构、HTTP 接口契约、前端要求、验收标准）和 `docs\seekdb-notes.md`（已在 seekdb 实例上实测通过的连接方式、表结构、SQL 写法、向量字面量拼接与索引约束），严格按这两份文档实现，不要改动其中已验证的事实。

实现要求：
- 技术栈：Python 3 + FastAPI + pymysql（seekdb 服务端 MySQL 协议）+ 原生 HTML/CSS/JS，不引入前端框架与打包器。
- 在 `app/`、`web/`、`scripts/`、`tests/` 下生成 PRD 第 3 节列出的全部代码文件。
- `data/sample_docs.jsonl`、`requirements.txt`、`.env.example` 已存在，不要覆盖。
- 连接参数一律来自环境变量，代码内不得出现真实账号密码；`.env` 不入库。
- 实现三类检索：hybrid（RRF 融合）、vector（余弦距离）、fulltext（IK 全文），支持 topic/source 标量过滤，提供统计、列表、新增、删除接口。
- 完成后：列出你创建的每个文件及其作用；给出 `pip install`、`python scripts/seed.py`、`uvicorn app.main:app` 的启动步骤；并在本地跑通 `tests/smoke_test.py`。
