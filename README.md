# MaDongDong Blog

基于 `FastAPI + Vue 3 + SQLite` 的前后端分离博客系统，支持前台展示与后台管理。

## 当前版本状态（已同步）

当前仓库已从“极简演示”升级为“可持续迭代版本”，重点包括：

- 前台（`web`）统一导航/页脚组件化、主题切换、移动端抽屉菜单
- 后台（`admin`）菜单体系升级（主菜单 + 文章二级菜单）、角色差异化能力、垃圾箱流程
- 后台右侧内容区完成组件化与动态组件映射（`menuKey -> component`）

---

## 主要功能

### 后端（FastAPI）

- 健康检查、应用生命周期初始化
- JWT 登录认证与角色鉴权
- 文章能力：创建 / 更新 / 审核通过 / 审核驳回
- 文章垃圾箱：
  - 删除文章 -> 软删除（进入垃圾箱）
  - 恢复文章
  - 垃圾箱彻底删除
- 分类与标签管理
- 媒体库管理
- 评论管理与审核
- 站点配置与导航项管理
- 前台公开接口：首页 / 文章详情 / 搜索 / 评论提交

### 前台（web）

- 首页、文章详情页、搜索页
- 全站白天/黑夜主题切换（持久化）
- 顶部导航与底部页脚组件化复用：
  - `WebTopbar.vue`
  - `WebFooter.vue`
- 移动端 `hamburger` 抽屉菜单
- 菜单高亮（支持带 query 的精确匹配）
- 非首页折叠搜索（展开/收起动画）
- 首页布局优化：
  - 内容区域更宽，左右留白减少
  - 热门文章固定高度 + 超出滚动
  - 热度/评论分行显示
  - 分页按钮居中，首页不显示“上一页”、末页不显示“下一页”
- Footer 内容横向居中展示（版权优先于备案）

### 后台（admin）

- 登录页 + 控制台
- 顶部栏：主题切换、用户昵称、角色标记、下拉退出登录
- 角色显示：系统管理员 / 内容作者
- 左侧菜单：
  - 主菜单（概览、文章、媒体、评论、站点）
  - 文章二级菜单（文章管理、垃圾箱、创建文章）
- 角色差异化文章发布策略：
  - 系统管理员：可“直接发布”，不显示“提交审核”
  - 内容作者：可“提交审核”，不显示“直接发布”
- 文章垃圾箱完整流程（UI 与 API 对齐）
- 文章状态中文展示（已发布/草稿/待审核/已驳回）
- 创建文章摘要自动生成：根据正文自动提取前 120 字符（去除基础 Markdown 符号）
- 评论管理增强：
  - 系统管理员与内容作者均可审核评论
  - 支持通过/拒绝（含拒绝二次确认）
  - 显示昵称、邮箱、时间、状态
  - 评论内容后可跳转所属文章标题（50 字截断）
- 右侧内容区组件化 + 动态映射渲染（可扩展）：
  - `OverviewPanel`
  - `ArticleManagePanel`
  - `ArticleTrashPanel`
  - `ArticleCreatePanel`
  - `MediaPanel`
  - `CommentsPanel`
  - `SiteSettingsPanel`

---

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

---

## 项目结构

```text
app/        FastAPI 后端
web/        前台 Vue 应用
admin/      后台 Vue 应用
```

---

## 预览

![](assets/images/01.png)

![](assets/images/02.png)

![](assets/images/03.png)

![](assets/images/04.png)

![](assets/images/05.png)

![](assets/images/06.png)

![](assets/images/07.png)

![](assets/images/08.png)

![](assets/images/09.png)

![](assets/images/10.png)

![](assets/images/11.png)

![](assets/images/12.png)

![](assets/images/13.png)

![](assets/images/14.png)

![](assets/images/15.png)

![](assets/images/16.png)

![](assets/images/17.png)

## 本地开发启动

### 1) 启动后端

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

### 4) 前端环境变量模板说明

当前 `web` 与 `admin` 前端都已统一采用“环境变量 + 开发代理”的方式，建议按下面的模板分别配置。

#### `web/.env.example`

```env
VITE_API_BASE=/api/v1
VITE_APP_NAME=MadongDong
VITE_ADMIN_BASE_PATH=/admin
```

- `VITE_API_BASE`：前台接口基础路径。开发环境和生产环境都建议使用 `/api/v1`，再由 Vite 开发代理或 Nginx 反向代理转发到后端。
- `VITE_APP_NAME`：前台应用名称，仅用于前端展示或后续扩展。
- `VITE_ADMIN_BASE_PATH`：前台安装完成后跳转到后台登录页的路径前缀。默认使用 `/admin`，与 WordPress 的 `/wp-admin/` 风格一致。

#### `admin/.env.example`

```env
VITE_API_BASE=/api/v1
VITE_APP_NAME=MadongDong Admin
VITE_WEB_BASE_PATH=/
```

- `VITE_API_BASE`：后台接口基础路径。与前台保持一致，方便统一部署。
- `VITE_APP_NAME`：后台应用名称，仅用于前端展示或后续扩展。
- `VITE_WEB_BASE_PATH`：后台中需要跳转到前台时使用的路径前缀。默认使用 `/`。

#### 推荐写法

本地开发时可以保持如下配置：

```env
# web/.env
VITE_API_BASE=/api/v1
VITE_ADMIN_BASE_PATH=/admin

# admin/.env
VITE_API_BASE=/api/v1
VITE_WEB_BASE_PATH=/
```

生产环境建议保持同域名、同端口、不同路径的方式部署：

```env
# web/.env
VITE_API_BASE=/api/v1
VITE_ADMIN_BASE_PATH=/admin

# admin/.env
VITE_API_BASE=/api/v1
VITE_WEB_BASE_PATH=/
```

#### 路径规划建议

- 前台访问：`/`
- 安装页：`/install`
- 后台登录页：`/admin/login`
- 后台控制台：`/admin/`

这套方式与 WordPress 的“同域名同端口，路径区分前后台”一致，更适合博客系统的部署和维护。

#### 部署建议

- 本地开发时，前端分别运行在 `5173`（web）和 `5174`（admin），并通过 Vite `proxy` 代理到 `http://127.0.0.1:8000`。
- 生产环境部署时，建议前端静态站点由 Nginx/Apache/Caddy 托管，并将 `/api/v1` 反向代理到后端服务。
- 不建议在源码里写死 `http://127.0.0.1:8000` 之类的后端地址。

---

## 默认管理员账号

首次启动自动初始化默认管理员：

- 用户名：`admin`
- 密码：`admin123456`

---

## 主要接口（当前版本）

### 后台认证

- `POST /api/v1/admin/auth/login`
- `GET /api/v1/admin/auth/me`

### 后台文章

- `GET /api/v1/admin/articles`
- `GET /api/v1/admin/articles/deleted`
- `GET /api/v1/admin/articles/{article_id}`
- `POST /api/v1/admin/articles`
- `PUT /api/v1/admin/articles/{article_id}`
- `DELETE /api/v1/admin/articles/{article_id}`
- `POST /api/v1/admin/articles/{article_id}/restore`
- `DELETE /api/v1/admin/articles/{article_id}/permanent`
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

---

## 角色权限矩阵

| 角色 | Web 前台 | Admin 登录 | 文章创建 | 直接发布 | 提交审核 | 审核他人文章 | 垃圾箱管理 | 媒体管理 | 评论管理 | 站点设置 |
|---|---|---|---|---|---|---|---|---|---|---|
| 系统管理员 | ✅ | ✅ | ✅ | ✅ | （可选） | ✅ | ✅ | ✅ | ✅ | ✅ |
| 内容作者 | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅（仅本人） | ❌（当前 UI 隐藏） | ❌（当前 UI 隐藏） | ❌（当前 UI 隐藏） |
| 普通读者 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

说明：

- 内容作者发布文章默认走“提交审核”，由系统管理员审核后发布。
- 系统管理员在创建文章时显示“直接发布”选项，不显示“提交审核”。
- 当前后台 UI 中，媒体/评论/站点菜单仅对系统管理员显示。
- 垃圾箱流程为：删除 -> 进入垃圾箱（软删除）-> 恢复 / 彻底删除。

---

## 接口权限矩阵（简化版）

> 说明：以下按“当前实现与当前 UI 约束”给出。`admin` 为系统管理员，`author` 为内容作者。

### 认证接口

| 接口 | admin | author | reader |
|---|---|---|---|
| `POST /api/v1/admin/auth/login` | ✅ | ✅ | ❌ |
| `GET /api/v1/admin/auth/me` | ✅ | ✅ | ❌ |

### 后台文章接口

| 接口 | admin | author | 说明 |
|---|---|---|---|
| `GET /api/v1/admin/articles` | ✅ | ✅ | 作者仅可见本人文章 |
| `GET /api/v1/admin/articles/deleted` | ✅ | ✅ | 作者仅可见本人垃圾箱文章 |
| `GET /api/v1/admin/articles/{article_id}` | ✅ | ✅ | 作者仅可见本人 |
| `POST /api/v1/admin/articles` | ✅ | ✅ | admin 可直发，author 提审 |
| `PUT /api/v1/admin/articles/{article_id}` | ✅ | ✅ | 作者仅可编辑本人可编辑文章 |
| `DELETE /api/v1/admin/articles/{article_id}` | ✅ | ✅ | 软删除进垃圾箱 |
| `POST /api/v1/admin/articles/{article_id}/restore` | ✅ | ✅ | 从垃圾箱恢复 |
| `DELETE /api/v1/admin/articles/{article_id}/permanent` | ✅ | ✅ | 彻底删除（需先在垃圾箱） |
| `POST /api/v1/admin/articles/{article_id}/approve` | ✅ | ❌ | 审核通过 |
| `POST /api/v1/admin/articles/{article_id}/reject` | ✅ | ❌ | 审核拒绝 |

### 后台分类/标签接口

| 接口 | admin | author |
|---|---|---|
| `GET /api/v1/admin/categories` | ✅ | ✅ |
| `POST /api/v1/admin/categories` | ✅ | ❌ |
| `PUT /api/v1/admin/categories/{category_id}` | ✅ | ❌ |
| `GET /api/v1/admin/tags` | ✅ | ✅ |
| `POST /api/v1/admin/tags` | ✅ | ❌ |
| `PUT /api/v1/admin/tags/{tag_id}` | ✅ | ❌ |

### 后台媒体接口

| 接口 | admin | author |
|---|---|---|
| `GET /api/v1/admin/media` | ✅ | ❌（当前 UI 隐藏） |
| `GET /api/v1/admin/media/folders` | ✅ | ❌（当前 UI 隐藏） |
| `POST /api/v1/admin/media/folders` | ✅ | ❌ |
| `PUT /api/v1/admin/media/folders/{folder_id}` | ✅ | ❌ |
| `POST /api/v1/admin/media/upload` | ✅ | ❌ |
| `POST /api/v1/admin/media/move` | ✅ | ❌ |
| `POST /api/v1/admin/media/delete` | ✅ | ❌ |

### 后台评论接口

| 接口 | admin | author |
|---|---|---|
| `GET /api/v1/admin/comments` | ✅ | ❌（当前 UI 隐藏） |
| `POST /api/v1/admin/comments/{comment_id}/approve` | ✅ | ❌ |
| `POST /api/v1/admin/comments/{comment_id}/reject` | ✅ | ❌ |

### 后台站点配置接口

| 接口 | admin | author |
|---|---|---|
| `GET /api/v1/admin/site/settings` | ✅ | ❌（当前 UI 隐藏） |
| `PUT /api/v1/admin/site/settings` | ✅ | ❌ |
| `GET /api/v1/admin/site/nav-items` | ✅ | ❌ |
| `POST /api/v1/admin/site/nav-items` | ✅ | ❌ |
| `PUT /api/v1/admin/site/nav-items/{nav_id}` | ✅ | ❌ |

### 前台公开接口

| 接口 | admin | author | reader |
|---|---|---|---|
| `GET /api/v1/web/home` | ✅ | ✅ | ✅ |
| `GET /api/v1/web/articles/{article_id}` | ✅ | ✅ | ✅ |
| `GET /api/v1/web/search` | ✅ | ✅ | ✅ |
| `POST /api/v1/web/comments` | ✅ | ✅ | ✅ |

---

## Ubuntu + Nginx 生产部署指南

下面以 **Ubuntu + Nginx + FastAPI + Vue 3** 的方式说明如何部署本项目。该方案与 WordPress 的部署体验接近，前台、后台和安装页都使用同一套域名与端口，仅通过路径区分。

### 1. 推荐访问路径

- 前台首页：`/`
- 首次安装页：`/install`
- 后台登录页：`/admin/login`
- 后台控制台：`/admin/`
- 后端接口：`/api/v1/`
- 上传文件：`/uploads/`

### 2. 生产环境目录规划

建议在服务器上准备如下目录：

```text
/var/www/madongdong/web/dist
/var/www/madongdong/admin/dist
/var/www/madongdong/backend
/var/www/madongdong/uploads
```

其中：

- `web/dist`：前台打包产物
- `admin/dist`：后台打包产物
- `backend`：FastAPI 后端代码
- `uploads`：上传文件持久化目录

### 3. 后端部署

#### 3.1 安装依赖

进入后端目录后安装 Python 依赖：

```bash
cd /var/www/madongdong/backend
uv sync
```

如果你使用的是虚拟环境，也可以按你的项目习惯激活后执行对应安装命令。

#### 3.2 配置环境变量

在后端目录准备 `.env`，至少建议配置：

```env
APP_NAME=MaDongDong Blog
DEBUG=false
SECRET_KEY=请替换为强随机密钥
DATABASE_URL=sqlite+aiosqlite:///./madongdong.db
UPLOAD_DIR=app/static/uploads
API_V1_PREFIX=/api/v1
```

说明：

- `SECRET_KEY` 一定要在生产环境更换
- `UPLOAD_DIR` 建议指向持久化目录
- 如果后续你切换成 MySQL/PostgreSQL，只需要改 `DATABASE_URL`

#### 3.3 启动后端

推荐使用 `uvicorn` 配合系统守护进程（例如 `systemd`）运行：

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

如果需要长期运行，建议把它做成 `systemd` 服务，避免手工保持终端开启。

### 4. 前台与后台构建

#### 4.1 Web 前台

进入 `web` 目录，先准备生产环境变量，然后构建：

```env
# web/.env.production
VITE_API_BASE=/api/v1
VITE_APP_NAME=MadongDong
VITE_ADMIN_BASE_PATH=/admin
```

构建命令：

```bash
cd /var/www/madongdong/web
npm install
npm run build
```

构建后生成：

- `/var/www/madongdong/web/dist`

#### 4.2 Admin 后台

进入 `admin` 目录，准备生产环境变量并构建：

```env
# admin/.env.production
VITE_API_BASE=/api/v1
VITE_APP_NAME=MadongDong Admin
VITE_WEB_BASE_PATH=/
```

构建命令：

```bash
cd /var/www/madongdong/admin
npm install
npm run build
```

构建后生成：

- `/var/www/madongdong/admin/dist`

### 5. Nginx 配置示例

下面是一个推荐的同域名同端口部署方式，前台和后台通过路径区分：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前台站点
    location / {
        root /var/www/madongdong/web/dist;
        try_files $uri $uri/ /index.html;
    }

    # 首次安装页与后台
    location /admin/ {
        alias /var/www/madongdong/admin/dist/;
        try_files $uri $uri/ /admin/index.html;
    }

    # API
    location /api/v1/ {
        proxy_pass http://127.0.0.1:8000/api/v1/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 上传文件
    location /uploads/ {
        proxy_pass http://127.0.0.1:8000/uploads/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

### 6. 首次安装流程

首次部署时，数据库为空或未初始化完成，访问前台站点后会自动进入安装向导：

1. 打开 `http://your-domain.com/`
2. 如果系统未安装，自动跳转到 `http://your-domain.com/install`
3. 填写站点标题、管理员账号、邮箱等信息
4. 点击“确认并安装”
5. 后端初始化默认角色、权限、站点配置和导航
6. 安装完成后自动跳转到 `http://your-domain.com/admin/login`
7. 使用刚创建的管理员账号登录后台

### 7. 生产环境注意事项

- `.env` 文件主要用于**构建阶段**与**后端运行阶段**，不会打进前端 `dist`
- 前端 `dist` 只需要上传到服务器即可
- `web` 和 `admin` 都建议使用 `/api/v1` 作为 API 前缀，由 Nginx 统一反代到 FastAPI
- 上传目录需要持久化，避免容器重建或服务器清理后丢失文件
- 生产环境务必替换 `SECRET_KEY`，不要使用默认值

## 后续

欢迎提交 [Issues](https://github.com/Lumosylva/madongdong/issues) 以便项目变得更好

