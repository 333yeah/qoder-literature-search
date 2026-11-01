# 大赛提交操作手册（LitSeek · Qoder × OceanBase · seekdb 赛道）

> 目标：按赛题「用 Qoder 开发项目 → 接入 seekdb → Qoder Sites 发布网站 → 整理材料 → 提交测试平台」完成提交。
> 平台：https://open.oceanbase.com/train/detail/21?questionId=600078 （侧边栏 **Qoder** 页签，questionId=600078；不要进入 600071 seekdb 基础实践题）。
> 状态基准：后端 + 前端 + 测试已在本地跑通，冒烟测试 **28 项全部通过**；`site/` 静态演示站点已生成并本地复核通过；站点产物描述文件 `.LitSeek Demo.qoder.site` 已存在。

## 阶段总览（严格按顺序执行）

| 阶段 | 动作 | 谁来做 | 产物 |
|---|---|---|---|
| A | 在 Qoder Sites 面板发布站点并设为公开 | 用户在 Qoder 桌面操作 | 公网站点网址、dev-12/dev-13 截图 |
| B | 回到 Qoder 会话补齐开发闭环记录，取得 Qoder UID | 用户在 Qoder 会话操作 | dev-03 ~ dev-11 截图、数值化 UID |
| C | 导入基线、提交并推送到 GitHub 私有仓库，生成带 token 的 clone 地址 | 助手执行 git；用户提供账号/仓库/PAT/身份 | 仓库 clone 地址 |
| D | 回填 README、站点、清单中的网址与仓库链接 | 助手执行 | 无占位符残留 |
| E | 登录平台 Qoder 题目，填写三项信息并上传材料，无痕复核后提交 | 用户登录操作；助手逐项核对 | 提交完成记录 |

---

## 阶段 A · 发布 Qoder Sites 站点（当前第一步）

### A.1 打开站点产物

1. 在 Qoder 左侧栏选择 **站点** → **我的站点**；或回到 `@sites` 任务回复，点击回复中的**网站产物卡片**（也可从任务「产出」中打开站点产物）。
2. 右侧 **站点** 面板打开预览，对照下方清单逐项检查（本地已复核，这里做发布前最终确认）：

- [ ] 首屏标题「LitSeek 文献与资料混合检索」、状态徽标「演示模式 · 内置 18 条示例资料」正常；
- [ ] 混合 / 语义 / 关键词三种模式可切换，输入「检索增强生成」有结果；
- [ ] 类型、主题、Top-K 过滤下拉可用；
- [ ] 侧边统计：总量 18；note 7、paper 4、lab 4、book 3；database 4、rag 4、vector-search 4、nlp 3、machine-learning 2、workflow 1；
- [ ] 向下滚动，7 张演示截图（01-home ~ 07-docs-list）全部加载成功；
- [ ] 下方说明区块齐全：解决的问题、核心功能、界面演示、seekdb 技术结合、本地复现步骤、仓库与入口、页脚；
- [ ] 页面没有报错、没有 CDN/框架加载失败。

### A.2 发布当前版本

1. 站点面板右上角点 **发布**，等待状态变为 **已发布**。
2. 打开发布详情查看网站地址，点 **访问** 看一眼已发布页面。
   > 新站点默认「仅自己可访问」，发布后**必须**继续做 A.3 改公开范围，否则评审未登录打不开。

### A.3 设置任何人都可访问（个人账号）

1. 在站点列表或站点详情中点 **分享** → **更改访问范围**。
2. 选择 **任何人都可访问**，个人账号点 **允许公开访问** 确认。
3. **复制链接**，得到完整公网网址（形如 `https://...qoder.app/...`）。

### A.4 公开验证与取证（缺一不可）

1. 另开 **无痕窗口**（不登录任何 Qoder 账号）粘贴网址，确认能打开首屏、说明区块和截图。
2. 在 `docs/screenshots/dev-record/` 留存：
   - `dev-12-sites-publish.png`：站点预览 + 发布成功 + 「任何人都可访问」设置页；
   - `dev-13-incognito.png`：无痕窗口未登录打开站点的画面。
3. 把站点网址发回助手，回填 README 1.3 节与 `docs/submission-checklist.md`。

> 注意：发布后若再改页面，必须**再次点发布**才会更新线上版本；评审结束前不要暂停或删除站点。

---

## 阶段 B · 补齐 Qoder 开发闭环记录并取得 UID

### B.1 回到同一会话按阶段执行

在原来的 Qoder 开发会话中，逐条复制发送 `docs/qoder-stage-prompts.txt` 的阶段 0 ~ 7 提示词，由 Qoder 在会话内完成现状盘点、后端自查修复、seekdb seed、测试调试到全绿、前端复核、文档对齐、最终总结。每完成一个阶段，按 `docs/screenshots/dev-record/DEV-RECORD.md` 第 2 节对照表截图保存：

| 截图 | 环节 |
|---|---|
| dev-03-task-dispatch.png | 任务下发提示词 |
| dev-04-reading-specs.png | Qoder 阅读 PRD / seekdb 笔记并拆解需求 |
| dev-05-gap-analysis.png | 需求 vs 现状对照盘点 |
| dev-06-backend-fix.png | Qoder 自查并修改后端的对话与改动 |
| dev-07-seed-stats.png | seed 输出与 `/api/stats` 真实统计 JSON |
| dev-08-smoke-test.png | 冒烟测试全绿汇总、问题→根因→改动 |
| dev-09-frontend-review.png | 三模式 / 过滤 / 高亮前端复核 |
| dev-10-docs-review.png | README、验证样例对齐记录 |
| dev-11-final-summary.png | Qoder 最终总结（需求拆解 / 编码 / 调试 / seekdb 结合） |

红线：源码改动一律由 Qoder 在会话内完成，不在 Qoder 之外另开编辑器直接改源码后入库。

### B.2 取得数值化 Qoder UID

1. Qoder → **设置 → 个人资料 → 编辑**，查看数值化 UID。
2. 填入 `DEV-RECORD.md` 第 1 节；平台「Qoder 账号 UID」填同一个值。

---

## 阶段 C · GitHub 私有仓库（需要用户先提供信息）

### C.1 用户准备（提供给助手）

- GitHub 用户名；
- 新建私有仓库名称（建议 `powercontext-2026` 或 `literature-search-2026`）；
- 个人访问令牌 PAT（Settings → Developer settings → Personal access tokens，勾选 `repo` 权限；生成后只显示一次，立即保存）；
- git 提交显示用的姓名与邮箱。

### C.2 仓库方式（按赛题 GitHub 使用说明）

1. GitHub 右上角 **Import repository**，源地址 `https://github.com/oceanbase/powercontext`，新建仓库选择 **Private**，Begin import；导入后本地所在分支 `2026-competition-ecosystem` 保持不变。
2. 本地配置 git 身份，检查 `.gitignore` 已排除 `.env`、`*.log`、`__pycache__/`、`.venv/`。
3. 仅提交 `qoder/literature-search/` 项目目录（含 `site/` 站点源文件作为证据；不含 `.env` 真实凭据、运行日志、缓存与虚拟环境）。
4. 推送到该私有仓库。
5. 平台填写带 token 的 clone 地址：`https://<用户名>:<PAT>@github.com/<owner>/<repo>.git`。
   > 真实 token 只用于平台填写与 clone，不写入 README、站点或仓库文件。

### C.3 提交前安全核对（助手执行）

- [ ] `git status` 不出现 `.env`、`*.log`、`__pycache__`、`.venv`；
- [ ] `.env.example` 全部为占位符；
- [ ] 仓库内没有真实 seekdb 主机、用户名、密码；
- [ ] 用不带 token 的地址无法匿名 clone（私有生效）。

---

## 阶段 D · 信息回填

助手在站点网址、仓库地址、UID 齐备后完成：

- [ ] README 1.3 节回填站点网址与仓库地址；
- [ ] `docs/submission-checklist.md` 第 1、2 项回填；
- [ ] 站点「仓库与入口」区块链接更新为真实仓库；
- [ ] 全仓搜索占位符（`待发布后填写`、`待推送后填写`、`<Qoder Sites 网址>`、`<GitHub 私有仓库`），确认无残留。

---

## 阶段 E · 平台提交

### E.1 登录并进入 Qoder 题目

1. 打开 https://open.oceanbase.com/train/detail/21?questionId=600078 ；
2. 点 **立即提测**，完成 OceanBase 社区手机号验证码或密码登录；
3. 确认当前页签是 **Qoder**（不要停在 seekdb 基础实践）。

### E.2 表单填写与材料上传

| 平台项 | 内容 | 本地来源 |
|---|---|---|
| 项目网站网址 | A.3 复制的公网网址 | Qoder Sites 分享链接 |
| 代码仓库 | 带 PAT 的 clone 地址 | C.2 第 5 步 |
| Qoder 账号 UID | B.2 取得的数值化 UID | DEV-RECORD.md 第 1 节 |
| 运行说明 | 环境、依赖版本、seekdb 接入、安装到启动完整步骤 | `README.md` |
| 验证样例 | 初始数据 / 输入 / 步骤 / 预期结果 / seekdb 作用记录 | `docs/validation-samples.md`、`docs/search-results-record.json` |
| Qoder 开发记录 | 关键环节对话截图/录屏 + UID | `docs/screenshots/dev-record/` |

### E.3 提交前最终核对

- [ ] 无痕窗口打开站点，未登录可访问；
- [ ] 带 token 地址可正常 clone，代码目录在 `qoder/literature-search/`；
- [ ] 材料齐全：网站网址、仓库、运行说明、验证样例、开发记录、UID；
- [ ] 表单核对无误后提交；提交后保留站点公开与仓库可访问，评审结束前不删除、不下线。

## 附：本项目已完成的本地证据

- 冒烟测试：`tests/smoke_test.py` 28 项全部通过（2026-10-29 回归复跑通过）；
- 初始语料：18 文档 → 18 片段；note 7 / paper 4 / lab 4 / book 3；database 4 / rag 4 / vector-search 4 / nlp 3 / machine-learning 2 / workflow 1；
- 真实检索结果留存：`docs/search-results-record.json`；
- 界面验证截图：`docs/screenshots/01-home.png` ~ `07-docs-list.png`；
- 站点发布前本地复核：`site-preview-01-search.png`、`site-preview-02-screenshots.png`。
