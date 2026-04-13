# MaDongDong Blog

基于 `FastAPI + Vue 3 + SQLite` 的前后端分离个人博客系统，面向轻量部署场景。

## 当前版本说明（已简化）

当前代码已调整为“可运行的简化版”，重点是保留主流程，去除部分复杂交互。

### 已实现功能

- 后端
  - FastAPI 应用与健康检查
  - SQLite 数据模型与启动初始化
  - JWT 登录认证与基础角色校验
  - 文章基础流程：列表 / 创建 / 更新 / 审核通过 / 驳回
  - 分类与标签：列表 / 创建 / 更新
  - 媒体库：列表、目录树、建目录、改目录、上传、批量移动、批量删除
  - 评论：前台提交、后台列表、后台通过/拒绝
  - 站点设置与导航项：读取与更新
  - 前台公开接口：首页、文章详情、搜索、提交评论

- 前台（`web`）
  - 首页
  - 文章详情页（简化展示）
  - 搜索页
  - 匿名评论提交

- 后台（`admin`）
  - 登录页
  - 控制台简化面板（文章/媒体/评论/站点设置概览）
  - 快速创建文章
  - 站点设置编辑

## 本次简化后的边界

以下能力在当前版本中已移除或暂不提供：

- 文章“软删除/垃圾箱/恢复/永久删除”流程
- 后台文章编辑弹窗与对应前端入口
- 后台评论审核按钮在当前简化 UI 中未提供（后端接口仍保留）
- 前台文章页的增强交互（目录自动生成、代码块复制、分享按钮、封面懒加载、嵌套回复等）
- 管理端主题切换等视觉增强逻辑

## 技术栈

### 后端

- Python 3.13+
- FastAPI
- SQLAlchemy 2
- SQLite
- Passlib + python-jose
- Pydantic Settings

### 前端

- Vue 3
- Vue Router
- Pinia
- Vite
- TypeScript

## 项目结构

```text
app/        FastAPI 后端
web/        前台 Vue 应用
admin/      后台 Vue 应用
```

## 本地开发启动

### 1) 启动后端

在项目根目录执行：

```powershell
.\.venv\Scripts\activate; uv sync; uvicorn app.main:app --reload
```

默认地址：`http://127.0.0.1:8000`

### 2) 启动前台

```powershell
cd "e:\Project\madongdong\web"; npm install; npm run dev
```

默认地址：`http://127.0.0.1:5173`

### 3) 启动后台

```powershell
cd "e:\Project\madongdong\admin"; npm install; npm run dev
```

默认地址：`http://127.0.0.1:5174`（或 Vite 自动分配端口）

## 默认管理员账号

首次启动会自动初始化默认管理员：

- 用户名：`admin`
- 密码：`admin123456`

## 主要接口（当前版本）

### 后台认证

- `POST /api/v1/admin/auth/login`
- `GET /api/v1/admin/auth/me`

### 后台文章

- `GET /api/v1/admin/articles`
- `GET /api/v1/admin/articles/{article_id}`
- `POST /api/v1/admin/articles`
- `PUT /api/v1/admin/articles/{article_id}`
- `POST /api/v1/admin/articles/{article_id}/approve`
- `POST /api/v1/admin/articles/{article_id}/reject`

### 后台分类标签

- `GET /api/v1/admin/categories`
- `POST /api/v1/admin/categories`
- `PUT /api/v1/admin/categories/{category_id}`
- `GET /api/v1/admin/tags`
- `POST /api/v1/admin/tags`
- `PUT /api/v1/admin/tags/{tag_id}`

### 后台媒体库

- `GET /api/v1/admin/media`
- `GET /api/v1/admin/media/folders`
- `POST /api/v1/admin/media/folders`
- `PUT /api/v1/admin/media/folders/{folder_id}`
- `POST /api/v1/admin/media/upload`
- `POST /api/v1/admin/media/move`
- `POST /api/v1/admin/media/delete`

### 后台评论

- `GET /api/v1/admin/comments`
- `POST /api/v1/admin/comments/{comment_id}/approve`
- `POST /api/v1/admin/comments/{comment_id}/reject`

### 后台站点配置

- `GET /api/v1/admin/site/settings`
- `PUT /api/v1/admin/site/settings`
- `GET /api/v1/admin/site/nav-items`
- `POST /api/v1/admin/site/nav-items`
- `PUT /api/v1/admin/site/nav-items/{nav_id}`

### 前台公开接口

- `GET /api/v1/web/home`
- `GET /api/v1/web/articles/{article_id}`
- `GET /api/v1/web/search`
- `POST /api/v1/web/comments`

## 部署建议

- 后端使用 `uvicorn`（生产建议配合进程守护）
- 前后台执行 `npm run build` 后由 `Nginx` 托管静态资源
- `Nginx` 反向代理 `/api` 到 FastAPI
- 上传目录需做持久化
- 生产环境请通过 `.env` 覆盖 `secret_key` 等敏感配置
