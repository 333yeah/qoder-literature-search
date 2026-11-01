# 在 Qoder 内完成 LitSeek 开发的操作手册（合规版）

> 对应赛题：**Qoder × OceanBase**，题目「Build with Qoder」。
> 本手册目的：保证项目**主要开发工作在 Qoder 内完成**，每一步都留有 Qoder 对话与终端记录，符合 2.1、3.1.3 与评价维度「Qoder 开发实践」。
> 外部助手只负责提供提示词、整理材料与核对结果；**源码改动一律由 Qoder 在它自己的会话里完成**，不在外部编辑器直接改。

## 0. 先看赛题原文要求（合规红线）

> **2.1 用 Qoder 开发项目**
> 项目的主要开发工作必须在 Qoder 中完成。桌面端、IDE、JetBrains 插件和 CLI 均可使用。
> 参赛者需保留开发过程记录，说明 Qoder 在需求拆解、编码、调试等环节中完成了哪些工作。
> **仅用 Qoder 发布网站而项目在其他工具中开发的作品，不符合本赛道要求。**

> **3.1.3 Qoder 开发可核对**：开发记录能够体现项目的主要功能由 Qoder 参与完成。
> **评价维度「Qoder 开发实践」**：开发记录是否清楚展示了 Qoder 在项目中的作用。

## 1. 当前合规状态判断

- **主体代码已经由 Qoder 生成**：Qoder CN 会话「开发 LitSeek 文献检索应用」读取 `docs/PRD.md`、`docs/seekdb-notes.md` 后，在 `app/`、`web/`、`scripts/`、`tests/` 下生成了全部源码（右侧文件清单可核对：14 个文件、约 +1852 行，截图见 `dev-record/dev-01-final-summary.png`）。这一步满足「Qoder 承担主要编码工作」。
- **后续复核阶段必须回到 Qoder 内完成**：本手册第二部分的提示词，就是让 Qoder 在同一会话中做现状盘点、自查缺陷、连库 seed、跑测试并修复、复核前端、完善文档。所有最终留在仓库里的代码状态，都要能在 Qoder 对话记录中追溯到 Qoder 的操作。
- **不要做的事**：在 Qoder 之外另开编辑器直接改源码；不要把外部助手改出来的代码直接覆盖 Qoder 产物而不留 Qoder 对话记录。

## 2. 进入 Qoder 会话（准备动作）

1. 打开 **Qoder CN**，确认登录账号为 `aliyun6529798870`（个人账号，后续 Sites 才能公开）。
2. 确认绑定的本地工作区是基线仓库 `2026-competition-ecosystem`（右侧环境信息应显示该目录）。
3. 打开已有会话 **「开发 LitSeek 文献检索应用」**；若会话已丢失，新建会话并把工作区绑定到同一仓库根目录。
4. 项目根目录：`qoder/literature-search/`（相对仓库根）。
5. 每完成下面一个阶段：**先等 Qoder 回复完成 → 截图 → 再发下一条提示词**。截图命名对照第 5 节。

## 3. 分阶段提示词（按顺序逐条复制发送）

### 阶段 0：Qoder 重新通读需求与已验证约束（证据：需求拆解环节）

发送：

```
我们继续 LitSeek 文献与资料混合检索系统这个参赛项目。请先用内置 CLI 完整阅读：
1. docs/PRD.md（产品需求、目录结构、HTTP 接口契约、前端要求、验收标准）
2. docs/seekdb-notes.md（已在 seekdb 实例上实测通过的连接方式、表结构、SQL、向量字面量拼接、索引约束）
3. data/sample_docs.jsonl（18 条示例语料）

读完后请输出一份简短的需求拆解：本项目要解决什么痛点、需要哪些功能模块、seekdb 分别承担什么职责、对应 PRD 第 10 节验收标准逐条列出。不要改动 docs/seekdb-notes.md 里已验证的事实。
```

**Qoder 应交付**：需求拆解清单（痛点 / 模块 / seekdb 职责 / 验收标准对照）。
**截图**：`dev-03-task-dispatch.png`（任务下发）、`dev-04-reading-specs.png`（Qoder 读取文档与需求拆解回复）。

### 阶段 1：现状盘点与差距分析（证据：Qoder 审查现有代码）

发送：

```
请通读 app/、web/、scripts/、tests/ 下现有代码，对照 docs/PRD.md 第 5、6、8 节逐项核对：
- 三类检索 hybrid / vector / fulltext 是否齐全；
- topic、source 标量过滤三路是否都支持；
- health / stats / documents / search / seed / 新增 / 删除接口是否齐全；
- 前端是否包含模式切换、过滤下拉、结果卡片、排名徽标、命中词高亮、统计面板、新增表单；
- 连接参数是否全部来自环境变量，代码内是否出现真实账号密码。

输出一张对照表：PRD 要求 → 当前实现位置（文件:函数/组件）→ 状态（已满足/有缺口）。只做盘点，先不要改代码。
```

**Qoder 应交付**：对照表，列出缺口（若有）。
**截图**：`dev-05-gap-analysis.png`。

### 阶段 2：后端自查与缺陷修复（证据：Qoder 编码 + 调试环节）

发送：

```
基于上一步对照表，由你（Qoder）在 app/ 内完成后端自查与修复，要求：
1. 检索层严格遵守 docs/seekdb-notes.md：向量字面量用 struct 打包小端 float32 后以 X'<hex>' 拼入 SQL，向量不要走 %s 占位符；
2. search_vector / search_fulltext 的 LIMIT 绑定参数只能追加一次，核对参数列表与 SQL 占位符数量一致；
3. hybrid 两路各取 top_k*3，应用层按 RRF（k=60）融合，回填 vector_rank、fulltext_rank、distance、ft_score、score；
4. 数据库不可达时服务不崩溃，/api/health 返回 503 与可读错误信息；
5. 所有主机、端口、用户名、密码、库名、租户只从环境变量读取，代码内不得硬编码真实凭据；
6. 修完后说明你改了哪个文件、哪个函数、为什么改。
```

**Qoder 应交付**：修复后的后端代码 + 改动说明（文件、函数、原因）。
**截图**：`dev-06-backend-fix.png`（Qoder 编辑文件的对话与 diff）。

### 阶段 3：接入 seekdb 并初始化示例语料（证据：技术结合环节）

发送：

```
现在接入本机 .env 中配置的 seekdb 实例（凭据只从 .env 读取，不要把密码贴进对话）。
1. 执行 python scripts/seed.py --reset 初始化示例语料；
2. 调用 GET /api/stats，核对总量与分布：按类型 note 7、paper 4、lab 4、book 3；按主题 database 4、rag 4、vector-search 4、nlp 3、machine-learning 2、workflow 1；
3. 如果建表或入库报错，由你定位并修复 SQL / 连接问题，直到 seed 成功、统计数字与上面一致；
4. 把你执行的命令、返回的统计 JSON 原样贴在回复里。
```

**Qoder 应交付**：seed 命令输出 + `/api/stats` 真实 JSON。
**截图**：`dev-07-seed-stats.png`。

### 阶段 4：跑通冒烟测试并由 Qoder 调试到全绿（证据：调试环节，最关键）

发送：

```
请在项目根目录运行 python tests/smoke_test.py，覆盖：健康检查、统计、三类检索、topic/source 过滤、新增可检索、删除回落、静态首页。
- 任何用例失败，由你自己读报错、定位根因并修改代码，不要跳过或删除失败用例；
- 反复运行直到全部通过；
- 回复里贴出最终测试汇总（通过数 / 失败数）和你修复过的问题清单（现象 → 根因 → 改动）。
```

**Qoder 应交付**：测试全绿汇总 + 调试问题清单。
**截图**：`dev-08-smoke-test.png`（终端 28 项通过的画面）。

### 阶段 5：前端复核与体验打磨（证据：Qoder 编码环节）

发送：

```
启动服务后在浏览器打开首页，对照 PRD 第 8 节复核前端：
1. 未登录可打开；连通状态指示灯、统计面板正常；
2. 混合 / 语义 / 关键词三模式切换，结果卡片显示标题、来源、主题、原文、排名徽标、距离或全文得分，命中词高亮；
3. source、topic 过滤联动生效；top_k 可选；空态与错误态有提示；
4. 保持浅灰白底、单一 teal 强调色 #0d7377，不要出现大面积紫/靛蓝；移动端宽度可读；
5. 发现问题由你直接修改 web/index.html、web/style.css、web/app.js，并说明改动点。
```

**Qoder 应交付**：前端复核结论 + 必要的样式/交互改动说明。
**截图**：`dev-09-frontend-review.png`。

### 阶段 6：文档与验证样例对齐实测结果（证据：交付环节）

发送：

```
请核对并更新交付文档，保证与真实实现、实测结果一致：
1. README.md：环境要求、依赖安装、.env 配置说明、seed、启动、接口清单与示例请求、seekdb 职责、目录说明、常见问题；配置示例只允许占位符；
2. docs/validation-samples.md：初始数据清单、6 组用例（混合 / 语义 / 关键词 / 主题过滤 / 类型过滤 / 新增删除闭环）的输入、步骤、预期、实测结果与 seekdb 作用记录；
3. 不要在任何提交文档里写入真实密码；.env 保持不入库。
完成后列出你更新了哪些文档、关键数据来自哪次真实运行。
```

**Qoder 应交付**：更新后的 README 与验证样例 + 数据来源说明。
**截图**：`dev-10-docs-review.png`。

### 阶段 7：Qoder 输出最终开发总结（证据：开发记录收尾）

发送：

```
请输出一份「Qoder 开发记录总结」，按环节说明你在本项目中完成的工作：
1. 需求拆解：你如何阅读 PRD 与 seekdb-notes、划分模块；
2. 编码：你创建/修改了哪些文件，各自职责；
3. 调试：你解决过哪些 seekdb 连接、SQL、向量字面量、检索排序、测试失败问题；
4. 技术结合：seekdb 在向量索引、IK 全文索引、距离计算、标量过滤、统计聚合上分别承担什么作用；
5. 最终测试结果与运行方式。
这份总结将作为大赛 Qoder 开发记录的一部分，请基于真实对话与代码事实写，不要夸大。
```

**Qoder 应交付**：可直接归档的开发总结（存入 `IMPLEMENTATION_SUMMARY.txt` 或对话截图）。
**截图**：`dev-11-final-summary.png`。

## 4. 然后才是 Qoder Sites（与代码开发分开）

代码在 Qoder 内复核到全绿、文档对齐之后，再按 `docs/sites-prompt.md` 在「站点 → 添加站点」中构建站点：首屏复用现有 LitSeek 应用界面（内置示例数据只读演示），下方放置问题说明、功能、截图、seekdb 技术说明与本地复现步骤，然后公开发布。**站点只是展示入口，不等于开发过程**；开发记录以第 3 节各阶段对话和终端截图为准。

## 5. 截图与录屏归档对照

全部存入 `docs/screenshots/dev-record/`，索引维护在 `DEV-RECORD.md`：

| 文件名 | 对应阶段 | 必须拍到的内容 |
|---|---|---|
| dev-03-task-dispatch.png | 阶段 0 | 用户任务提示词、Qoder 收到的需求 |
| dev-04-reading-specs.png | 阶段 0 | Qoder 读取 PRD / seekdb-notes / 语料的记录与需求拆解回复 |
| dev-05-gap-analysis.png | 阶段 1 | PRD 要求 vs 实现对照表 |
| dev-06-backend-fix.png | 阶段 2 | Qoder 编辑后端文件、改动说明 |
| dev-07-seed-stats.png | 阶段 3 | seed 命令、stats 真实 JSON（18 条与分布） |
| dev-08-smoke-test.png | 阶段 4 | 测试全绿汇总、调试问题清单 |
| dev-09-frontend-review.png | 阶段 5 | 浏览器复核画面、前端改动说明 |
| dev-10-docs-review.png | 阶段 6 | README / 验证样例更新记录 |
| dev-11-final-summary.png | 阶段 7 | Qoder 最终开发总结回复 |
| dev-12-sites-publish.png | Sites 发布 | 预览、发布成功、「任何人都可访问」设置 |
| dev-13-incognito.png | Sites 发布 | 无痕窗口未登录打开站点 |

> 若录制整段流程的录屏：从阶段 0 任务下发开始，连续录到阶段 7 测试全绿与总结，作为截图之外的补充证据。

## 6. 提交前自检（对照赛题 3.1 基础验收）

- [ ] 网站由 Qoder Sites 发布，无痕未登录可打开；
- [ ] README 步骤能在干净环境跑通，seed 后统计为 18；
- [ ] 开发记录覆盖需求拆解、编码、调试，且能看出主要功能由 Qoder 完成；
- [ ] seekdb 作用有真实检索结果 / 入库 / 统计记录可核对；
- [ ] 仓库无真实 Key、密码；`.env`、日志、缓存不入库；
- [ ] 记录 Qoder 账号数值化 UID（设置 → 个人资料 → 编辑）。
