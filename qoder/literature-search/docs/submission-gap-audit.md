# 提交材料缺口审计（2026-10-29）

> 对照赛题「四、提交材料」五项要求逐项核对。状态：✅ 已具备 / 🟡 基本具备待小修 / ❌ 缺失待补。
> 站点网址：https://litseek-demo-kgb0khpkzds.qoder.zone/ （未登录浏览器已复核可访问）。

## 总览

| # | 平台材料 | 状态 | 一句话结论 |
|---|---|---|---|
| 1 | 项目网站网址 | ✅ | 已公开发布、未登录可访问；仅缺仓库链接回填后的二次发布 |
| 2 | 代码仓库 | ✅ | 比赛仓库 powercontext-2026 已推送（516c4db）；公开仓库备份已同步 |
| 3 | 运行说明 | 🟡 | README 步骤完整；待补实测 Python 与依赖版本口径，并修正 Python 版本描述 |
| 4 | 验证样例 | 🟡 | 6 组用例与初始数据齐全；把被忽略日志的证据出处改为已入库截图 / JSON |
| 5 | Qoder 开发记录 | ✅ | 阶段 0–7 截图 10 张 + 首轮总结 + UID 均已齐；可选补后端修复与公开设置页各一张 |

---

## 1. 项目网站网址 —— ✅ 已完成（小尾巴：二次发布）

### 已有证据

- 公网网址：https://litseek-demo-kgb0khpkzds.qoder.zone/
- 未登录浏览器复核记录：
  - `docs/screenshots/dev-record/online-public-01-search.png`：线上混合检索「检索增强生成」4 条 RAG 结果、排名徽标、RRF、命中高亮；
  - `docs/screenshots/dev-record/online-public-02-screenshots.png`：7 张演示截图在线加载成功、无 4xx/5xx。
- 页面已包含赛题 2.3 要求的：项目简介、解决的问题、核心功能、演示截图、本地复现步骤；静态前端无外部 CDN / 框架依赖。

### 剩余动作

- 仓库地址确定后，把站点「仓库与入口」区块占位文字改为真实仓库链接；
- 在 `@sites` 会话让 Qoder 更新页面后**再次点发布**，线上版本才会更新；
- 留存 `dev-12-sites-publish.png`（发布成功 + 「任何人都可访问」设置页）；`dev-13-incognito.png` 已由 online-public 两张图覆盖，可再补一张无痕窗口完整首屏。

## 2. 代码仓库 —— ✅ 已提交比赛仓库（2026-11-01）

### 现状

- **比赛仓库（最终提交位置）**：https://github.com/LiuMingyang-1/powercontext-2026 （私有，333yeah 为协作者）；分支 `2026-competition-ecosystem` 已更新至 `516c4db`（3 个 commit：`0625a3e`/`98d0f83`/`516c4db`），`ls-remote` 已验证；
- **公开备份仓库**：https://github.com/333yeah/qoder-literature-search （visibility=public，默认分支 `2026-competition-ecosystem`，未登录浏览器已验证）；
- 远程：`origin` = 个人公开仓库，`upstream` = 官方 `oceanbase/powercontext.git`；比赛仓库通过带 token 的临时 remote 推送；
- 项目目录 `qoder/literature-search/` 共 **68 个文件**已提交并推送；
- 已确认被 `.gitignore` 排除：`.env`、`*.log`、`__pycache__/`、`.venv/`；真实 seekdb 主机 / 账号 / 密码 0 命中。

### 平台填写

- 评审 clone 地址（含 token）：`https://333yeah:<PAT>@github.com/LiuMingyang-1/powercontext-2026.git`（PAT = 333yeah 账号 repo 权限 classic token）
- 或公开仓库地址：`https://github.com/333yeah/qoder-literature-search`（匿名可 clone）
- PAT 仅在平台表单与推送时使用；提交后如不再需要可撤销。

### 待办

- 站点「仓库与入口」区块在 Qoder Sites 面板**重新发布**（线上当前仍为占位文字）；README 1.3 已回填公开仓库地址（Qoder 会话完成）。

## 3. 运行说明 —— 🟡 基本具备，待补版本口径

### 已有内容（`README.md`）

- 运行环境说明、操作系统范围；
- seekdb 三种接入方式（云端实例 / 本地 server / Docker）与 `.env` 参数逐项说明；
- 安装虚拟环境 → 安装依赖 → 配置 `.env` → seed → 启动 → 冒烟测试完整步骤；
- HTTP 接口清单、seekdb 职责对照表、目录结构。

### 缺口与修正项

1. **Python 版本口径不一致**：README 4.1 写「Windows 11 + Python 3.11 实测」，本机虚拟环境实测为 **Python 3.13.16**；应改为「要求 Python 3.11+，本机实测 3.13.16」。
2. **依赖实测版本缺失**：`requirements.txt` 使用 `>=` 下限，README 未列本机实测锁定版本。应在 README 补一张实测版本表（本机虚拟环境实测版本如下，供核对）：

| 包 | 实测版本 |
|---|---|
| fastapi | 0.162.0 |
| uvicorn | 0.54.0 |
| PyMySQL | 1.2.3 |
| pyseekdb | 1.4.0.post1 |
| python-dotenv | 1.2.4 |
| pydantic | 2.14.1 |
| numpy | 2.5.4 |
| onnxruntime | 1.31.1 |
| tokenizers | 0.23.3 |
| httpx | 0.28.1 |

3. 上述文档改动按合规要求，应在 Qoder 会话内由 Qoder 修改（提示词可直接引用本节内容）。

## 4. 验证样例 —— 🟡 内容齐全，证据出处需小修

### 已有内容（`docs/validation-samples.md` + `docs/search-results-record.json`）

- 初始数据：18 文档 → 18 片段；source / topic 统计与 18 条清单；
- 6 组可执行用例，均含输入、步骤、预期结果、实测排名 / 距离 / 得分 / RRF 与 seekdb 作用记录：
  1. 混合检索（RRF 融合）；2. 语义检索；3. 关键词检索（IK 分词）；
  4. topic 过滤；5. source 过滤；6. 新增 → 可检索 → 删除回落；
- 28 项冒烟测试全部通过；7 张界面截图归档在 `docs/screenshots/`。

### 缺口与修正项

- 第 4 节「接口与功能验收对照」中引用的 `server.log`、`verify_add_delete.log`、`smoke.log` 已被 `.gitignore` 排除，不会进入仓库；评审在仓库中看不到这些日志。应把对应证据出处改为已入库的：
  - `docs/screenshots/01-home.png`、`02-hybrid-search.png` … `07-docs-list.png`；
  - `docs/search-results-record.json`；
  - `tests/smoke_test.py` 可由评审本地复跑得到 28 通过 / 0 失败。
- 本次小修同样回到 Qoder 会话内完成。

## 5. Qoder 开发记录 —— ✅ 截图与 UID 已齐（两处可选补强）

### 已有证据（2026-11-01 全部核实）

- `docs/screenshots/dev-record/` 新增阶段截图 **1-1 / 1-2 / 2~9 共 10 张**，逐张核对内容：
  - 1-1：阶段 0 任务下发 + 需求阅读（Qoder 输出「LitSeek 需求拆解」痛点与功能模块表）；
  - 2：阶段 1 现状盘点（PRD 第 5 节检索层逐项核对表）；
  - 3：阶段 3 接入 seekdb（seed 18 条、stats 统计匹配、health、三模式、过滤）；
  - 4：阶段 4 冒烟测试 **28 项全绿 0 失败**；
  - 5：阶段 5 前端复核（三模式/高亮/过滤联动）；
  - 6：阶段 6 文档对齐（README、validation-samples 实测数据更新、`.env` 未入库验证）；
  - 7：阶段 7 Qoder 开发记录总结（需求拆解/编码清单/seekdb 职责边界）；
  - 8、9：Sites 站点生成与部署操作日志；
  - 1-2：测试说明 + seekdb 六项职责 + PRD 第 10 节验收逐条对照。
- `dev-01-final-summary.png`：首轮生成主体源码（右侧 14 文件、约 +1852 行）；
- `docs/qoder-development-playbook.md`、`docs/qoder-stage-prompts.txt`：阶段流程与提示词备份；
- 站点本地 / 公开复核截图各 2 张（online-public-01/02）；
- **Qoder 数值化 UID 已取得并填入 `DEV-RECORD.md` 第 1 节**：`01a17c90-2514-7966-a7d4-601d10ef1294`（2026-11-01 用户提供，个人资料账号 ID；平台表单填此值，与任务 ID 区分）。

### 可选补强（不阻塞提交）

- dev-06 后端自查修复单独截图（2.png 之后未见修复环节留图；若评审追问可补）；
- dev-12「任何人都可访问」公开范围设置页单独截图（9.png 为部署操作日志，公开设置页未单独留图）。

### 合规提醒

- 后续 README、验证样例、站点的任何改动都要在 Qoder 会话内由 Qoder 完成，不在 Qoder 之外直接改源码 / 文档后入库；截图要能体现这些环节发生在 Qoder 中。
- 已如实记录一处口径差异（见 `DEV-RECORD.md` 第 6 节）：Qoder 文档环节写「实测 Python 3.11」，本机实测为 3.13.16，README 第 62 行需在 Qoder 会话内修正。

---

## 提交前最终核对顺序

1. 补齐第 5 项 Qoder 阶段截图与 UID；
2. 完成第 3、4 项小修（版本表、Python 版本、日志证据出处替换），由 Qoder 在会话内完成；
3. 执行第 2 项 GitHub 私有仓库推送，取得评审 clone 地址；
4. 回填站点仓库链接并二次发布；
5. 无痕窗口复核站点；登录平台 `questionId=600078`，填写网站网址、仓库地址、UID，上传 / 引用运行说明、验证样例、开发记录后提交。
