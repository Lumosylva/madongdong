# MaDongDong博客系统

基于 `FastAPI + Vue 3 + SQLite` 的前后端分离个人博客系统，面向 `2核2G Linux` 轻量部署环境。

## 当前实现进度

已完成的核心能力：

- 后端基础骨架与应用启动
- SQLite 数据模型与默认初始化
- JWT 登录认证与 RBAC 角色权限基础
- 后台文章管理、分类标签管理、作者提审与管理员审核发布流
- 媒体库基础：上传、目录树、列表、批量移动、批量删除
- 评论基础：匿名评论、登录评论、后台审核
- 站点配置与导航管理
- 前台公开接口：首页、文章详情、搜索、评论提交
- Vue 前台工程：首页、文章详情页、搜索页
- Vue 后台工程：登录页、控制台、站点设置、快速发文面板

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

### 1. 启动后端

在项目根目录执行：

```powershell
.\.venv\Scripts\activate; uv sync; uvicorn app.main:app --reload
```

默认接口地址：`http://127.0.0.1:8000`

### 2. 启动前台

```powershell
cd "e:\Project\madongdong\web"; npm install; npm run dev
```

默认地址：`http://127.0.0.1:5173`

### 3. 启动后台

```powershell
cd "e:\Project\madongdong\admin"; npm install; npm run dev
```

默认地址：`http://127.0.0.1:5174` 或 Vite 自动分配端口

## 默认管理员账号

首次启动会自动初始化默认管理员：

- 用户名：`admin`
- 密码：`admin123456`

## 已提供的主要接口

### 后台认证

- `POST /api/v1/admin/auth/login`
- `GET /api/v1/admin/auth/me`

### 后台文章

- `GET /api/v1/admin/articles`
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

## 当前限制说明

当前版本属于第一版可运行原型，下面这些能力还未完整覆盖：

- 前台用户注册与登录页面尚未完成
- 后台用户管理页面尚未落地
- 后台媒体上传页面目前是基础接口已完成，界面仍偏简化
- Markdown 编辑器当前为基础文本输入，尚未接入专业可视化编辑器
- 图片缩略图目前为 URL 占位逻辑，未做真实图像处理
- 还未加入 Alembic 等迁移体系
- 还未补充完整自动化测试

## 部署建议

生产环境建议：

- 后端使用 `uvicorn` 配合进程守护运行
- 前台与后台使用 `npm run build` 输出静态文件后交给 `Nginx` 托管
- `Nginx` 反向代理 `/api` 到 FastAPI 服务
- 上传文件目录需持久化保存
- 生产环境务必通过 `.env` 覆盖 `secret_key`

## 后续推荐迭代

- 接入真正的 Markdown 编辑器
- 完成后台用户管理与权限分配页面
- 完成媒体库树形目录界面与批量操作 UI
- 补充评论前台展示优化与回复层级处理
- 增加数据库迁移与自动化测试
