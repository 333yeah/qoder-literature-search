# GitHub 打包清单（提交评审用）

> 仓库基线：`https://github.com/oceanbase/powercontext`，分支 `2026-competition-ecosystem`（基线 commit `d647275`）。
> 本项目代码与材料统一放在 `qoder/literature-search/` 目录下；基线仓库原有内容保持不变。
> 已通过 `git add --dry-run qoder/literature-search` 核对：下表「入库」分组即实际被版本库跟踪的文件；「排除」分组已被 `.gitignore` 拦截，不会推送。

## 1. 必须打包入库的内容

### 1.1 后端源码 `app/`

| 文件 | 作用 |
|---|---|
| `app/__init__.py` | 包初始化 |
| `app/config.py` | 环境变量与 `.env` 加载、默认配置 |
| `app/embeddings.py` | 384 维嵌入函数、文本切片 |
| `app/schemas.py` | Pydantic 请求 / 响应模型 |
| `app/store.py` | seekdb 访问层：建表、入库、向量/全文/混合检索、过滤、统计、删除 |
| `app/main.py` | FastAPI 路由、静态文件、健康检查、CORS |

### 1.2 本地应用前端 `web/`

| 文件 | 作用 |
|---|---|
| `web/index.html` | 本地应用单页界面 |
| `web/style.css` | 浅色学术风样式（teal `#0d7377` 强调色） |
| `web/app.js` | 前端交互与 `/api/*` 对接 |

### 1.3 数据与脚本

| 文件 | 作用 |
|---|---|
| `data/sample_docs.jsonl` | 18 条内置中文示例语料 |
| `scripts/seed.py` | 初始化 / 重置示例语料（支持 `--reset`） |
| `scripts/reset_db.py` | 删除并重建表结构 |

### 1.4 测试与验证脚本 `tests/`

| 文件 | 作用 |
|---|---|
| `tests/smoke_test.py` | 28 项冒烟测试（连接、入库、统计、三模式检索、过滤、API、新增/删除、静态页） |
| `tests/verify_add_delete.py` | 新增 → 可检索 → 删除回落专项验证 |
| `tests/record_search_results.py` | 留存真实检索排名 / 距离 / 得分 / RRF |
| `tests/quick_verify.py` | 快速连通与检索复核 |

### 1.5 配置与依赖

| 文件 | 作用 |
|---|---|
| `requirements.txt` | 全部 Python 依赖与版本约束 |
| `.env.example` | 连接参数模板，**全部占位符**，供评审复制为 `.env` 填写 |
| `.gitignore` | 排除密钥、日志、缓存、虚拟环境 |

### 1.6 文档与提交材料 `docs/`

| 文件 | 对应赛题材料 |
|---|---|
| `README.md` | 运行说明：环境、依赖版本、seekdb 部署接入、安装到启动完整步骤、接口、seekdb 职责、目录结构 |
| `docs/validation-samples.md` | 验证样例：初始数据、输入、步骤、预期结果、seekdb 技术作用记录 |
| `docs/search-results-record.json` | 6 组真实检索结果留存（排名、距离、得分、RRF） |
| `docs/PRD.md` | 产品需求（Qoder 实现主依据） |
| `docs/seekdb-notes.md` | 已验证的 seekdb 事实、约束、SQL 与向量写入注意事项 |
| `docs/qoder-development-playbook.md` | Qoder 内开发阶段流程与取证要求 |
| `docs/qoder-stage-prompts.txt` | 阶段 0–7 提交给 Qoder 的提示词备份 |
| `docs/qoder-prompt.md` / `docs/qoder-task-prompt.txt` | 首轮任务指令备份 |
| `docs/sites-prompt.md` | Qoder Sites 站点构建与发布提示词 |
| `docs/submission-checklist.md` | 大赛提交材料对照表与状态 |
| `docs/submission-runbook.md` | 阶段 A–E 提交操作手册 |
| `docs/submission-gap-audit.md` | 五项提交材料缺口审计与待补清单 |
| `docs/github-package-manifest.md` | 本打包清单 |
| `docs/screenshots/01-home.png` ~ `07-docs-list.png` | 本地应用 7 张界面验证截图 |
| `docs/screenshots/dev-record/` | Qoder 开发记录、站点本地与公开复核截图、`DEV-RECORD.md` |

### 1.7 Qoder Sites 站点源文件 `site/`

| 文件 | 作用 |
|---|---|
| `site/index.html` | 已发布站点的页面源文件（首屏演示 + 说明区块） |
| `site/style.css` | 站点样式 |
| `site/app.js` | 18 条内嵌语料与浏览器本地三模式演示检索 |
| `site/screenshots/01-home.png` ~ `07-docs-list.png` | 站点引用的演示截图 |
| `.LitSeek Demo.qoder.site` | Qoder Sites 产物描述文件（siteId / deploymentId / releaseId，作为站点由 Qoder 生成的证据） |

### 1.8 根目录证据文件

| 文件 | 作用 |
|---|---|
| `IMPLEMENTATION_SUMMARY.txt` | Qoder 首轮实现总结与本地复核结论 |

## 2. 绝对不能打包上传的内容（已被 `.gitignore` 排除）

| 排除项 | 原因 |
|---|---|
| `.env` | 本机真实 seekdb 主机、用户名、密码、数据库名；只存在本机，严禁入库 |
| `*.log`（`seed.log`、`smoke.log`、`server.log`、`verify_add_delete.log`、`quick_verify.log`、`record_results.log`） | 运行日志；评审按 README 与验证样例复现，不需要本机日志 |
| `app/__pycache__/`、`*.pyc` | Python 缓存 |
| `.venv/`、`venv/` | 虚拟环境，体积大且与机器相关，由评审自行 `pip install -r requirements.txt` 重建 |
| `node_modules/`、`seekdb.db`、`.pytest_cache/` | 本项目未使用，预留排除 |
| `.vscode/`、`.idea/` | 编辑器个人配置 |

## 3. 推送前安全核对（逐项执行）

1. `git status` 中不出现 `.env`、`*.log`、`__pycache__/`、`.venv/`；
2. 全仓搜索真实 seekdb 主机、用户名、密码，0 命中；
3. `.env.example` 保持占位符，不含真实凭据；
4. 站点页面与文档中不出现真实连接信息；
5. 仓库为**公开**（Public，符合赛题「公开或向评审开放访问权限」）；平台填写带 PAT 的 `https://333yeah:<PAT>@github.com/333yeah/qoder-literature-search.git` clone 地址，token 本身不写进任何仓库文件；
6. 推送后用带 token 地址验证可 clone，用匿名地址验证不可访问。

## 4. 当前入库文件统计（已提交 commit `0625a3e`）

共 **68 个文件**，按目录分组：

| 目录 / 文件 | 数量 |
|---|---|
| `app/` 后端源码 | 6 |
| `web/` 本地应用前端 | 3 |
| `scripts/` 初始化脚本 | 2 |
| `tests/` 测试与验证脚本 | 4 |
| `data/` 示例语料 | 1 |
| `site/` 站点源文件 + 截图 | 10 |
| `docs/` 文档、提示词、验证样例、截图与开发记录 | 36 |
| 根目录配置与证据（`README.md`、`requirements.txt`、`.env.example`、`.gitignore`、`.LitSeek Demo.qoder.site`、`IMPLEMENTATION_SUMMARY.txt`） | 6 |

## 5. 推送状态（2026-11-01 已完成）

1. ✅ **比赛仓库已提交**：`LiuMingyang-1/powercontext-2026`（私有，333yeah 为协作者），分支 `2026-competition-ecosystem` = `516c4db`，3 个 commit 全部推送（用 333yeah repo 权限 classic token，`ls-remote` 已验证）；
2. ✅ 公开仓库已创建：`333yeah/qoder-literature-search`（visibility=public，默认分支 `2026-competition-ecosystem`），已同步全部 commit；
3. ✅ 本地 git 身份已配置（user.name=333yeah，user.email=2990961464@qq.com，仓库级）；
4. ✅ 远程：`origin` = 个人公开仓库，`upstream` = 官方 `oceanbase/powercontext.git`；
5. ✅ PAT（333yeah repo 权限）仅用于创建仓库与推送，未写入任何文件；平台 clone 地址：`https://333yeah:<PAT>@github.com/LiuMingyang-1/powercontext-2026.git`；
6. ⏳ 待办：站点「仓库与入口」区块已在 Qoder 会话内回填公开仓库地址，但线上仍为占位文字，需在 Qoder Sites 面板**重新发布**。
