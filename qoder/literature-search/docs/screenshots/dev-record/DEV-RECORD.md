# Qoder 开发记录（DEV RECORD）

> 赛题要求：**项目主要开发工作必须在 Qoder 中完成**，开发记录要体现 Qoder 在需求拆解、编码、调试各环节做了什么；仅用 Qoder 发布网站、代码在别处开发，不符合要求。
> 本目录集中存放 Qoder 会话截图与录屏；操作流程与逐条提示词见 `../qoder-development-playbook.md`。

## 1. Qoder 账号信息

- 账号显示名：aliyun6529798870
- Qoder 数值化 UID：**01a17c90-2514-7966-a7d4-601d10ef1294**（Qoder → 设置 → 个人资料 → 编辑 中查看；2026-11-01 用户提供，已核对为账号 ID）
- 账号类型：个人账号（Qoder Sites 才能设置公开访问；企业版无法公开）

## 2. 开发环节与截图对照（按 `qoder-development-playbook.md` 阶段拍摄）

| 文件名 | Qoder 环节 | 必须拍到的内容 | 状态 |
|---|---|---|---|
| 1-1.png | 阶段 0 任务下发 + 需求阅读 | 任务提示词（先读 PRD/seekdb-notes/sample_docs）与 Qoder 输出「LitSeek 需求拆解」：痛点、功能模块表（配置层/嵌入与切片/检索存储层） | 已有（2026-11-01） |
| 2.png | 阶段 1 现状盘点 | 「通读现有代码对照 PRD 第 5/6/8 节」任务；PRD 检索层逐项核对表（PRD 要求 / 实现位置 / ✅ 已满足） | 已有 |
| 3.png | 阶段 3 接入 seekdb | seed 初始化 18 条、`/api/stats` 统计匹配、health 连通、三模式检索、curl 中文编码改 Python、标量过滤、中文关键词调整 | 已有 |
| 4.png | 阶段 4 测试调试 | `python tests/smoke_test.py` **28 项全部通过 0 失败**，code.txt 详情（连通性/重置入库/统计/检索/过滤/API/新增删除/静态页），修复清单：无 | 已有 |
| 5.png | 阶段 5 前端复核 | 浏览器首页、混合/语义/关键词三模式切换、命中高亮、source/topic 过滤联动、top_k | 已有 |
| 6.png | 阶段 6 文档对齐 | 核对更新 README.md 与 validation-samples.md，实测数据捕获、Python 版本更新、`.env` 未入库验证 | 已有（含版本口径问题，见第 6 节） |
| 7.png | 阶段 7 最终总结 | 「Qoder 开发记录总结」：需求拆解（痛点→混合检索+标量过滤→模块划分）、编码文件清单、seekdb 职责边界 | 已有 |
| 8.png | Sites 站点生成 | 「站点」任务：首屏复用现有应用界面 + 说明区块、teal 强调色、纯静态；文件创建与预览 | 已有 |
| 9.png | Sites 部署 | 调用 Qoder Sites 构建/部署把 site/ 部署为网站产物，已有站点 `LitSeek`（project_id 01a1828e-…）更新，插件/skill 调用与重试过程 | 已有 |
| 1-2.png | 测试与验收说明 | tests/smoke_test.py 说明、18 条语料特征、seekdb 六项职责、PRD 第 10 节验收标准逐条对照 | 已有 |
| dev-01-final-summary.png | 首轮生成总结 | Qoder 首轮读取需求后生成全部源码：右侧文件清单 14 个文件、约 +1852 行，工作区 `2026-competition-ecosystem` | 已有 |
| dev-06-backend-fix.png | 阶段 2 后端自查修复 | Qoder 编辑后端文件、改动文件/函数/原因说明 | **缺**（2.png 为盘点，修复环节未单独留图；若评审要求可补） |
| dev-12-sites-publish.png | Sites 发布设置 | 「任何人都可访问」公开范围设置页 + 发布成功 | **缺**（9.png 为部署操作日志，公开设置页未单独留图；可补） |
| site-preview-01-search.png | 站点本地复核 | 本地浏览器打开 site/index.html 的混合检索结果（发布前复核） | 已有 |
| site-preview-02-screenshots.png | 站点本地复核 | 7 张演示截图在站点说明区全部加载成功（发布前复核） | 已有 |
| online-public-01-search.png | 站点公开复核 | 未登录浏览器打开线上站点的混合检索结果（https://litseek-demo-kgb0khpkzds.qoder.zone/） | 已有 |
| online-public-02-screenshots.png | 站点公开复核 | 线上站点 7 张演示截图全部加载成功、无 4xx/5xx 请求 | 已有 |

> 注：编号 02 已废弃（历史重复截图），不要使用。

## 3. Qoder 在项目中的作用（提交时据此核对）

1. **需求拆解**：Qoder 读取 `docs/PRD.md` 与 `docs/seekdb-notes.md`，划分后端检索层、前端单页、脚本、测试模块。
2. **主体编码**：Qoder 在 `app/`、`web/`、`scripts/`、`tests/` 生成首轮全部源码（dev-01 右侧文件清单为证）。
3. **复核与调试**：按 `qoder-development-playbook.md` 阶段 1–7，由 Qoder 在会话内完成对照盘点、缺陷修复、连库 seed、跑测试、前端复核与文档对齐；调试过程以阶段 2、4、5 截图为准。
4. **seekdb 实际作用**（须在开发记录与验证样例中可核对）：
   - IVF_FLAT 余弦向量索引：语义检索；
   - IK 全文索引：关键词检索；
   - `cosine_distance()` 距离计算；
   - `WHERE topic/source` 标量过滤；
   - `COUNT(*)` + `GROUP BY` 统计聚合；
   - 混合检索由应用层 RRF 融合，seekdb 负责单路排序。

## 4. 诚实记录原则

- Qoder 首轮生成了主体代码；复核阶段若存在问题修复、文档补全，应在开发记录里如实写明由 Qoder 在哪个对话环节完成。
- 不在 Qoder 会话之外直接修改源码；确需调整，先把诉求写成提示词交给 Qoder。
- 真实 seekdb 凭据只存在本机 `.env`，不进入对话截图、仓库与站点页面。

## 5. 录屏备选

平台若要求录屏：从阶段 0 任务下发开始，连续录制 Qoder 阅读需求、生成与修改代码、跑通测试，以及 Qoder Sites 预览与公开设置全过程；录屏与本目录截图一并作为附件提交。

## 6. 待修正事项（如实记录，2026-11-01 核对）

- 6.png 文档对齐环节 Qoder 输出「实测为 3.11，非 3.13」，但本机核对结果：系统 Python 与 `.venv` 虚拟环境**均为 Python 3.13.16**，本机不存在 3.11。
- 受此影响，`README.md` 第 62 行「本项目在 Windows 11 + Python 3.11 上完成实测」不准确，需在 Qoder 会话内修正为「Windows 11 + Python 3.13.16 完成实测」（要求仍为 3.11+）。
- 修正动作在 Qoder 会话内执行并补截图，保持「文档改动由 Qoder 完成」的合规口径；本目录如实记录差异，不隐瞒。
