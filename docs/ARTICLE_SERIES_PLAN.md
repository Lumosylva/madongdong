# 文章合集功能实施计划

## 目标

增加文章合集（系列）能力：作者可为多篇文章填写相同的合集名称和序号；访问其中一篇文章时，详情页显示该合集的已发布文章列表，并标记当前文章。

## 已确认方案与假设

- 采用轻量方案：每篇文章保存可选的合集名称和序号；名称相同的文章自动归为一组，不新增独立合集管理页或合集表。
- 合集名称去除首尾空格；序号为可选正整数。未填写序号的文章排在已编号文章之后；同序号时按文章 ID 稳定排序。
- 详情页只列出已发布且未删除的文章，并包含当前文章。没有合集名称时不显示合集区块。
- 现有“上一篇/下一篇”仍按全站发布时间计算，不改变含义；合集信息暂不纳入文章修订历史。

## 接口与数据约定

- 文章记录增加可选 `series_name` 和 `series_order` 字段，供后台创建、编辑及详情读取。
- 前台文章详情响应增加 `series_articles` 列表项，包含文章 ID、slug、标题和序号；按 ID 与 slug 访问时均返回合集数据。
- 后端按合集名称筛选文章，排除未发布及已删除文章。合集名称为空时返回空列表，前端不渲染合集区域。
- 启动迁移为既有 SQLite `articles` 表补充字段并建立查询索引；已有文章保持未加入合集的状态。
- 后台表单校验序号为正整数；保存空合集名称时清空合集序号。创建、编辑、本地草稿恢复和提交请求都应包含合集字段。

## 影响范围

- 后端：`app/models/article.py`、`app/core/init_db.py`、`app/schemas/article.py`、`app/schemas/web.py`、`app/services/article.py`、`app/services/web.py`、`app/api/admin/article.py`、`app/api/web.py`
- 后台：`admin/src/components/ArticleCreatePanel.vue`、`admin/src/views/DashboardView.vue`、`admin/src/locales/zh-CN.ts`、`admin/src/locales/en.ts`、`admin/src/locales/ja.ts`
- 前台：`web/src/types.ts`、`web/src/views/ArticleView.vue`、`web/src/styles/article-detail-layout.css`、`web/src/locales/zh-CN.ts`、`web/src/locales/en.ts`、`web/src/locales/ja.ts`
- 测试：扩展 `tests/test_article_workflow.py` 或新增聚焦合集的后端测试。

## 执行清单

1. [x] 在文章模型和创建/更新 schema 中加入合集字段及校验。
2. [x] 在 `init_db` 增加兼容旧 SQLite 数据库的补列迁移和合集查询索引。
3. [x] 更新文章创建、编辑 API 与服务层，保存并规范化合集名称、序号。
4. [x] 增加合集文章查询及详情响应模型，并接入 ID、slug 两种公开详情接口。
5. [x] 在后台编辑表单加入合集名称和序号；打通 Dashboard 状态、文章回填、草稿存取和提交，并补齐中英日文案。
6. [x] 在文章正文后、现有标签及上一篇/下一篇区域附近展示合集列表，链接至对应文章并高亮当前文章。
7. [x] 增加测试，覆盖旧库迁移、字段校验、合集文章筛选与排序、空合集行为，以及两种详情路由的响应。
8. [x] 运行后端测试、前端类型检查与构建，并检查差异和迁移兼容性。

## 当前进度

- 第 1 步已完成：`Article` 模型和请求/响应 schema 已加入 `series_name`、`series_order` 字段，文章模型声明合集复合索引。
- 第 2 步已完成：`init_db` 会幂等补齐既有 `articles` 表的合集字段，并确保复合查询索引存在；旧库模拟迁移及重复运行验证通过。
- 第 3 步已完成：后台创建、更新接口透传合集字段；服务层统一去除合集名称首尾空格，并在合集名称为空时清除序号。文章工作流测试和名称规范化边界检查通过。
- 第 4 步已完成：公开详情响应增加 `series_articles`；ID 与 slug 路由均接入同一合集查询，限制为已发布且未删除文章，并按序号、文章 ID 排序。内存 SQLite 行为验证通过。
- 第 5 步已完成：后台创建/编辑表单支持合集名称与序号；编辑回填、自动保存和恢复草稿、提交 payload 均已接入。空合集名称提交时清除序号；前端校验序号为正整数，并已补齐中英日文案。
- 第 6 步已完成：前台文章详情在标签与上一篇/下一篇之间展示合集文章有序列表，非当前文章链接到详情页，当前文章以高亮样式和 `aria-current` 标记；已补齐中英日文案并通过 web 生产构建。
- 第 7 步已完成：新增合集后端测试，覆盖旧 SQLite 表的幂等迁移、创建 schema 校验、合集文章筛选/排序/空名称，以及 ID 和 slug 详情路由的响应；新增测试 4 项全部通过。
- 第 8 步已完成：后端全量测试 9 项全部通过；web 和 admin 的 `vue-tsc --noEmit` 及生产构建均通过；`git diff --check` 通过。迁移验证确认旧 SQLite 表缺失字段时可补列、重复执行保持幂等、合集复合索引创建成功，已有文章的合集字段保持 `NULL`。admin 构建输出已有的 `:deep()` CSS 解析警告和大 chunk 提示，但未阻断构建。
