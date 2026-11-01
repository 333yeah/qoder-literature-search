# 提交材料清单（大赛测试平台）

> 对应赛题「四、提交材料」。逐步执行手册见 `submission-runbook.md`；逐项缺口判定见 `submission-gap-audit.md`；本清单跟踪材料状态；带「待填写」的项在私有仓库推送后补齐。

## 1. 材料对照表

| # | 平台要求 | 本项目对应材料 | 路径 / 链接 | 状态 |
|---|---|---|---|---|
| 1 | 项目网站网址（Qoder Sites，任何人可访问） | 首屏复用现有 LitSeek 应用界面（内置 18 条示例数据只读演示），下方为问题说明、功能、截图、seekdb 技术说明与本地复现步骤 | https://litseek-demo-kgb0khpkzds.qoder.zone/ （未登录已复核可访问，三模式检索、18 条统计、7 张截图正常，无 4xx/5xx） | 已完成；待 Qoder 会话回填站点「代码仓库」链接并重新发布 |
| 2 | 代码仓库（公开或向评审开放） | 基线 `2026-competition-ecosystem` 分支下 `qoder/literature-search/`，68 个文件、3 个 commit（`0625a3e`/`98d0f83`/`516c4db`）已推送 | **比赛仓库已提交**：https://github.com/LiuMingyang-1/powercontext-2026 （分支 `2026-competition-ecosystem` = `516c4db`，已验证 ls-remote）；公开备份 https://github.com/333yeah/qoder-literature-search ；平台填带 token clone 地址 `https://333yeah:<PAT>@github.com/LiuMingyang-1/powercontext-2026.git` | ✅ 已完成（2026-11-01 推送成功）；待站点重新发布后线上链接可见 |
| 3 | 运行说明（环境、依赖版本、seekdb 接入、安装到启动完整步骤） | `README.md`：环境、seekdb 三种接入方式、安装、seed、启动、测试、接口、seekdb 职责、目录结构齐全 | `README.md`；依赖清单 `requirements.txt` | 基本完成；待补「本机实测依赖版本表」（当前 requirements 为 `>=` 下限，README 未列实测锁定版本） |
| 4 | 验证样例（初始数据 / 输入 / 步骤 / 预期结果 / 技术作用记录） | 6 组可执行用例（混合/语义/关键词/主题过滤/类型过滤/新增-删除），含初始 18 条统计、实测排名与 seekdb 作用记录 | `docs/validation-samples.md`；`docs/search-results-record.json`；界面截图 `docs/screenshots/01~07` | 已完成；小修：验收对照中引用的 `*.log` 已被忽略不入库，证据出处应改指已入库的截图与 JSON |
| 5 | Qoder 开发记录（关键环节截图/录屏 + Qoder 账号 UID） | 会话截图 + 个人资料 UID；阶段流程见 `docs/qoder-development-playbook.md` | `docs/screenshots/dev-record/`：1-1/1-2/2~9 十张阶段截图 + dev-01 首轮总结 + 站点复核 4 张；UID `01a17c90-2514-7966-a7d4-601d10ef1294` 已填入 `DEV-RECORD.md` | 已完成：阶段 0–7 与 Sites 环节截图齐全；可选补 dev-06 后端修复、dev-12 公开设置页各一张；README 版本口径修正待 Qoder 会话内完成 |
| 6 | 使用效果材料（鼓励项，非必选） | 本项目未安排真实用户推广，暂不提交；站点「访问统计」可后续补充 | — | 可选 |

## 1.1 合规前置：开发过程必须发生在 Qoder 内

赛题 2.1 明确：**仅用 Qoder 发布网站、而项目在其他工具中开发，不符合赛道要求**。因此：
- 主体源码由 Qoder agent 在 Qoder 会话内生成；后续自查、修复、测试、文档对齐也应在同一会话内由 Qoder 执行。
- 操作顺序与逐条提示词见 `docs/qoder-development-playbook.md`；不要在 Qoder 之外另开编辑器直接改源码后直接入库。
- 开发记录截图须覆盖：任务下发、阅读需求、编码、调试、测试全绿、最终总结六个环节。

## 2. 运行说明覆盖情况（README.md）

- 运行环境：Python 3.11+，Windows/macOS/Linux；本机实测 Windows 11 + Python 3.13。
- 依赖版本：见 `requirements.txt`，安装命令 `pip install -r requirements.txt`。
- seekdb 接入：云端实例 / 本地 server / Docker 三选一，`.env` 参数逐项说明；明确 Windows 不支持 embedded。
- 完整步骤：虚拟环境 → 安装依赖 → 配置 `.env` → `python scripts/seed.py --reset` → `uvicorn app.main:app` → 浏览器访问 → `python tests/smoke_test.py`。

## 3. 验证样例覆盖情况（docs/validation-samples.md）

- 初始数据：18 条文档 → 18 片段；按类型、按主题统计与完整清单。
- 用例：混合检索、语义检索、关键词检索、主题过滤、类型过滤、新增→可检索→删除回落，共 6 组，含输入、步骤、预期、实测分数与 seekdb 作用记录。
- 自动化测试：`tests/smoke_test.py` 28 项全部通过（日志 `smoke.log`）。

## 4. 提交前必须补齐的三项信息

### 4.1 Qoder Sites 网址
- 在 Qoder「站点」中按 `docs/sites-prompt.md` 构建站点：首屏复用现有应用界面做内置示例只读演示，下方放置说明与截图；
- 可见范围设为「任何人都可访问」，个人版点击「允许公开访问」；
- 无痕窗口验证未登录可打开；
- 将网址回填到本表第 1 项与测试平台「项目网站网址」。

### 4.2 代码仓库地址
- 基于 `2026-competition-ecosystem` 基线导入新建 GitHub 私有仓库；
- 配置 git 身份后提交 `qoder/literature-search/`，推送到该私有仓库；
- 生成带 Personal Access Token 的 `https://<user>:<token>@github.com/<owner>/<repo>.git` 形式地址，供评审 clone；
- 回填本表第 2 项与测试平台「代码仓库」。

### 4.3 Qoder 账号 UID
- Qoder → 设置 → 个人资料 → 编辑，查看并复制数值化 UID；
- 记录在 `docs/screenshots/dev-record/DEV-RECORD.md`；
- 测试平台「Qoder 账号 UID」填写同一值。

## 5. 禁止入库内容核对

- 真实 seekdb 主机、用户名、密码仅存在于本机 `.env`（已被 `.gitignore` 忽略）；
- 仓库内 `.env.example` 全部为占位符；
- 提交前再次执行 `git status`，确认无 `.env`、`*.log`、`__pycache__`、`.venv` 进入版本库。

## 6. 测试平台填写顺序（用户最后操作）

### 6.1 平台入口（已核实）

- 大赛测试平台：https://open.oceanbase.com/train/detail/21?questionId=600078
- Qoder 赛道题目标签：`Qoder`，`questionId=600078`（侧边栏切换到 Qoder 页签后进入；当前默认题 600071 为 seekdb 基础实践，不要填错）。
- 进入页面后点「**立即提测**」，先完成 OceanBase 社区手机号/密码登录，登录后才会出现 Qoder 赛道提测表单。

### 6.2 提测表单与本项目材料对照

| 平台填写项 | 填写内容 / 上传文件 | 本地来源 |
|---|---|---|
| 项目网站网址 | Qoder Sites 发布后的完整公网网址，可见范围「任何人都可访问」 | Sites 面板复制；回填 README 1.3 |
| 代码仓库地址 | 带 PAT 的 `https://<GitHub用户名>:<token>@github.com/<owner>/<repo>.git` clone 地址 | 私有仓库推送后生成 |
| Qoder 账号 UID | 设置 → 个人资料 → 编辑 中数值化 UID | `DEV-RECORD.md` 第 1 节 |
| 运行说明（附件或仓库内 README） | 环境、依赖版本、seekdb 接入方式、安装到启动完整步骤 | `README.md` |
| 验证样例（附件或仓库内文档） | 初始数据、输入、步骤、预期结果、seekdb 技术作用记录 | `docs/validation-samples.md`、`docs/search-results-record.json` |
| Qoder 开发记录（附件：截图/录屏） | 关键环节对话截图、终端记录、最终总结；含 Qoder UID | `docs/screenshots/dev-record/` |

### 6.3 提交前最终核对

1. 无痕窗口打开项目网站，未登录能看到首屏演示、说明区块与 7 张截图；
2. 私有仓库可由带 token 地址 clone，`git status` 中不含 `.env`、`*.log`、`__pycache__`、`.venv`；
3. README、站点中的仓库链接与网址已回填，无占位符残留；
4. 提交后不要删除站点与私有仓库；评审结束前保持站点公开、仓库可访问。
