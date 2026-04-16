# admin 组件与样式文件映射表

## 入口与全局
- `admin/src/styles.css`：全局入口、变量、重置、模块导入
- `admin/src/styles/layout.css`：页面布局、顶栏、侧边栏、主区域
- `admin/src/styles/markdown.css`：Markdown 编辑器与预览

## 业务页面
- `admin/src/components/OverviewPanel.vue` → `admin/src/styles/overview.css`
- `admin/src/components/ArticleManagePanel.vue` → `admin/src/styles/article-manage.css`
- `admin/src/components/ArticleCreatePanel.vue` → `admin/src/styles/article-create.css`
- `admin/src/components/CategoryManagePanel.vue` → `admin/src/styles/category.css`
- `admin/src/components/CommentsPanel.vue` → `admin/src/styles/comments.css`
- `admin/src/components/MediaPanel.vue` → `admin/src/styles/media.css`
- `admin/src/components/SiteSettingsPanel.vue` → `admin/src/styles/site.css`
- `admin/src/components/LoginView.vue` → `admin/src/styles/login.css`

## 共享与兜底
- `admin/src/styles/comments.css`：评论管理列表与操作区
- `admin/src/styles/media.css`：媒体管理列表、上传区、危险按钮、提示文案
- `admin/src/styles/category.css`：分类管理表单、列表、编辑区
- `admin/src/styles/overview.css`：概览统计卡片、列表、行布局
- `admin/src/styles/article-manage.css`：文章筛选、列表、分页、状态标签
- `admin/src/styles/article-create.css`：文章创建表单、封面选择、提交区
- `admin/src/styles/site.css`：站点设置、Logo 上传、站点信息表单
- `admin/src/styles/login.css`：登录页布局与表单

## 说明
- 以上映射按当前拆分结果整理。
- 如新增页面组件，优先为其新增独立样式模块，再在 `admin/src/styles.css` 中导入。
