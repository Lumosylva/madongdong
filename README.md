# MaDongDong

基于 `FastAPI + Vue 3 + SQLite` 的前后端分离博客系统，支持前台展示与后台管理。

## 主要功能

### 后端（FastAPI）

- 健康检查、应用生命周期初始化、首次安装向导
- JWT 登录认证与角色鉴权（admin / author / reader）
- 文章能力：创建 / 更新 / 审核通过 / 审核驳回 / 摘要自动生成
- 文章垃圾箱：删除 → 软删除 → 恢复 / 彻底删除
- 分类与标签管理（CRUD）
- 媒体库管理（文件上传、目录管理、批量移动/删除）
- 评论管理与审核（通过 / 拒绝 / 彻底删除）
- 友情链接管理（前台申请、后台审核/编辑/删除）
- 站点配置与导航项管理
- 用户管理（创建/编辑/删除/批量角色变更）
- 个人资料更新（头像 base64 存储、昵称、邮箱、密码）
- 前台公开接口：首页 / 文章详情 / 搜索 / 评论提交 / 友链 / 归档 / 分类 / 标签

### 前台（web）

- 首页、文章详情页、搜索页、归档页、分类页、标签页、友链页、关于页
- **用户系统**：注册 / 登录 / 个人中心（头像上传、昵称、邮箱、密码修改）
- 全站白天/黑夜主题切换（持久化）
- 页面辅助工具（右下角浮动按钮）：主题切换、返回顶部、到达底部
- 顶部导航与底部页脚组件化复用
- 移动端 hamburger 抽屉菜单
- 非首页折叠搜索（展开/收起动画）
- 评论区用户头像：已注册用户显示真实头像，匿名用户显示首字符头像
- 友链申请表单（实时校验）
- 静态资源地址统一解析（`assets/index.ts`）

### 后台（admin）

- 登录页 + 控制台概览
- 页面辅助工具（主题切换、返回顶部、到达底部）
- 顶部栏：用户昵称、角色标记、下拉菜单（个人中心 / 退出登录）
- 左侧菜单：主菜单 + 文章二级菜单
- 角色差异化发布策略（admin 直接发布 / author 提交审核）
- **文章管理**：列表 / 搜索 / 筛选 / 编辑 / 垃圾箱完整流程
- **创建/编辑文章**：Markdown 编辑器、封面图选择、分类/标签/状态、临时草稿保存
- **评论管理**：审核通过/拒绝/删除、批量操作、搜索筛选
- **友链管理**：列表/搜索/筛选/编辑/审核/删除，首字符头像
- **用户管理**：列表/搜索/角色筛选/创建/编辑/删除/批量操作
- **媒体库**：文件上传、目录管理、拖拽排序
- **站点设置**：品牌信息、Logo 上传（拖拽）、页脚 HTML
- **个人中心**：头像上传、昵称、邮箱、密码修改
- **分类管理**：CRUD

---

## 技术栈

### 后端

- Python 3.13+
- FastAPI
- SQLAlchemy 2（async）
- aiosqlite + SQLite
- Passlib + python-jose（JWT）
- Pydantic Settings

### 前端

- Vue 3 + TypeScript
- Vue Router
- Vite
- md-editor-v3（admin Markdown 编辑器）
- marked + DOMPurify（web Markdown 渲染）

---

## 项目结构

```text
app/          FastAPI 后端（api / models / schemas / services / core）
web/          前台 Vue 应用（端口 5173）
admin/        后台 Vue 应用（端口 5174，基础路径 /admin/）
assets/       前后端共享工具（resolveAssetUrl）
scripts/      构建辅助脚本（URL 风险扫描）
```

---

## 本地开发启动

### 1) 启动后端

```powershell
.\.venv\Scripts\activate; uvicorn app.main:app --reload
```

默认地址：`http://127.0.0.1:8000`

### 2) 启动前台

```powershell
cd web; npm install; npm run dev
```

默认地址：`http://127.0.0.1:5173`

### 3) 启动后台

```powershell
cd admin; npm install; npm run dev
```

默认地址：`http://127.0.0.1:5174`

### 4) 环境变量

#### `web/.env`

```env
VITE_API_BASE=/api/v1
VITE_APP_NAME=MadongDong
VITE_ADMIN_BASE_PATH=/admin
```

#### `admin/.env`

```env
VITE_API_BASE=/api/v1
VITE_APP_NAME=MadongDong Admin
VITE_WEB_BASE_URL=
```

---

## 默认管理员账号

首次启动自动初始化：

- 用户名：`admin`
- 密码：`admin123456`

---

## 主要接口

### 后台认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/auth/login` | 后台登录 |
| GET | `/api/v1/admin/auth/me` | 获取当前用户 |
| PUT | `/api/v1/admin/auth/me` | 更新个人资料 |

### 后台用户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/auth/users` | 用户列表 |
| POST | `/api/v1/admin/auth/users` | 创建用户 |
| PUT | `/api/v1/admin/auth/users/{user_id}` | 更新用户 |
| DELETE | `/api/v1/admin/auth/users/{user_id}` | 删除用户 |
| POST | `/api/v1/admin/auth/users/batch/delete` | 批量删除 |
| POST | `/api/v1/admin/auth/users/batch/role` | 批量变更角色 |

### 后台文章

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/articles` | 文章列表 |
| GET | `/api/v1/admin/articles/deleted` | 垃圾箱列表 |
| GET | `/api/v1/admin/articles/{id}` | 文章详情 |
| POST | `/api/v1/admin/articles` | 创建文章 |
| PUT | `/api/v1/admin/articles/{id}` | 更新文章 |
| DELETE | `/api/v1/admin/articles/{id}` | 删除（软删除） |
| POST | `/api/v1/admin/articles/{id}/restore` | 恢复 |
| DELETE | `/api/v1/admin/articles/{id}/permanent` | 彻底删除 |
| POST | `/api/v1/admin/articles/{id}/approve` | 审核通过 |
| POST | `/api/v1/admin/articles/{id}/reject` | 审核拒绝 |

### 后台分类/标签

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/admin/categories` | 分类列表/创建 |
| PUT | `/api/v1/admin/categories/{id}` | 更新分类 |
| DELETE | `/api/v1/admin/categories/{id}` | 删除分类 |
| GET/POST | `/api/v1/admin/tags` | 标签列表/创建 |
| PUT | `/api/v1/admin/tags/{id}` | 更新标签 |

### 后台媒体库

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/media` | 文件列表 |
| POST | `/api/v1/admin/media/upload` | 上传文件 |
| POST | `/api/v1/admin/media/delete` | 批量删除 |
| POST | `/api/v1/admin/media/move` | 批量移动 |
| GET/POST | `/api/v1/admin/media/folders` | 目录列表/创建 |
| PUT | `/api/v1/admin/media/folders/{id}` | 更新目录 |

### 后台评论

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/comments` | 评论列表 |
| POST | `/api/v1/admin/comments/{id}/approve` | 通过 |
| POST | `/api/v1/admin/comments/{id}/reject` | 拒绝 |
| POST | `/api/v1/admin/comments/delete` | 彻底删除 |

### 后台友链

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/friend-links` | 友链列表 |
| PUT | `/api/v1/admin/friend-links/{id}` | 更新友链 |
| DELETE | `/api/v1/admin/friend-links/{id}` | 删除友链 |

### 后台站点配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/PUT | `/api/v1/admin/site/settings` | 站点设置 |
| GET/POST | `/api/v1/admin/site/nav-items` | 导航项 |
| PUT | `/api/v1/admin/site/nav-items/{id}` | 更新导航项 |

### 前台公开接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/web/home` | 首页数据 |
| GET | `/api/v1/web/articles/{id}` | 文章详情 |
| GET | `/api/v1/web/search` | 搜索 |
| GET | `/api/v1/web/archive` | 归档 |
| GET | `/api/v1/web/categories` | 分类索引 |
| GET | `/api/v1/web/categories/{slug}/articles` | 分类文章 |
| GET | `/api/v1/web/tags/{slug}/articles` | 标签文章 |
| POST | `/api/v1/web/comments` | 提交评论 |
| GET | `/api/v1/web/friend-links` | 友链列表 |
| POST | `/api/v1/web/friend-links` | 申请友链 |
| POST | `/api/v1/web/auth/register` | 读者注册 |
| POST | `/api/v1/web/auth/login` | 读者登录 |
| GET | `/api/v1/web/auth/me` | 获取当前用户 |
| PUT | `/api/v1/web/auth/me` | 更新个人资料 |

---

## 角色权限矩阵

| 角色 | Web 前台 | Admin 登录 | 文章创建 | 直接发布 | 提交审核 | 审核文章 | 垃圾箱 | 媒体 | 评论管理 | 友链管理 | 用户管理 | 站点设置 | 个人中心 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 系统管理员 | ✅ | ✅ | ✅ | ✅ | （可选） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 内容作者 | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅（仅本人） | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| 普通读者 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 部署

### 开发环境

- 前端通过 Vite proxy 代理 `/api/v1` 到 `http://127.0.0.1:8000`
- `web` 运行在 5173，`admin` 运行在 5174

### 生产环境（Ubuntu + Nginx）

推荐同域名同端口，路径区分前后台：

- 前台：`/`
- 安装页：`/install`
- 后台：`/admin/`
- API：`/api/v1/`
- 上传文件：`/uploads/`

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/madongdong/web/dist;
        try_files $uri $uri/ /index.html;
    }

    location /admin/ {
        alias /var/www/madongdong/admin/dist/;
        try_files $uri $uri/ /admin/index.html;
    }

    location /api/v1/ {
        proxy_pass http://127.0.0.1:8000/api/v1/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8000/uploads/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

### 后端生产配置

```env
APP_NAME=MaDongDong Blog
DEBUG=false
SECRET_KEY=请替换为强随机密钥
DATABASE_URL=sqlite+aiosqlite:///./madongdong.db
UPLOAD_DIR=app/static/uploads
API_V1_PREFIX=/api/v1
```

---

## URL 风险扫描

前端构建前自动执行 URL 风险扫描，拦截可能影响 HTTPS 上线的硬编码地址。

- 扫描范围：`app`、`web/src`、`admin/src`
- 规则维护：`scripts/check-hardcoded-urls.config.json`
- 命中禁止规则时构建直接失败

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

---

欢迎提交 [Issues](https://github.com/Lumosylva/madongdong/issues) 以便项目变得更好
