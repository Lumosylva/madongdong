# MaDongDong Blog

基于 `FastAPI + Vue 3 + SQLite` 的前后端分离博客系统，支持前台展示与后台管理。支持中文、English、日本語 三种语言。

## 主要功能

### 后端（FastAPI）

- 健康检查、应用生命周期初始化、首次安装向导
- 安装向导支持配置：站点域名（自动检测）、JWT 签名密钥（自动生成）、数据库连接（默认 SQLite）
- 安装完成后自动写入 `.env` 配置文件，域名配置自动生成 4 个 CORS 变体（http/https × 域名/www.域名）
- JWT 登录认证与角色鉴权（admin / author / reader）
- CSRF 防护（双重提交 Cookie 模式，保护所有写请求）
- 文章能力：创建 / 更新 / 审核通过 / 审核驳回 / 摘要自动生成
- 文章 slug URL：`/article/{slug}`，自动生成，标题变更时重新生成
- 文章垃圾箱：删除 → 软删除 → 恢复 / 彻底删除
- 分类管理（CRUD，支持层级分类）
- 标签管理（CRUD）
- 媒体库管理（文件上传、目录管理、批量移动/删除）
- 评论管理与审核（通过 / 拒绝 / 彻底删除）
- 友情链接管理（前台申请、后台审核/编辑/删除）
- 站点配置与导航项管理（含首页背景大图、背景音乐配置）
- 服务器级配置管理（域名、JWT 密钥、数据库连接、上传目录）
- 用户管理（创建/编辑/删除/批量角色变更）
- 个人资料更新（头像 base64 存储、昵称、邮箱、密码）
- 前台公开接口：首页 / 文章详情 / 搜索 / 评论提交 / 友链 / 归档 / 分类 / 标签
- RSS Feed（`/api/v1/web/rss`）和 Sitemap（`/api/v1/web/sitemap.xml`）
- 浏览量去重（同一 IP 24 小时内同一文章只计 1 次）
- 速率限制（按端点配置，防止暴力破解）
- 登录失败锁定（数据库持久化，6 次失败锁定 15 分钟，启动时自动清理过期记录）
- 数学验证码（HMAC 签名，防止批量注册和暴力破解）
- Cookie 隔离（admin / web 前端使用独立 Cookie 命名空间）
- 数据库迁移自动处理（启动时自动添加新字段）

### 前台（web）

- **多语言支持**：中文 / English / 日本語，语言切换器持久化
- 首页、文章详情页（slug URL）、搜索页、归档页、分类页、标签页、友链页、关于页
- **用户系统**：注册 / 登录 / 个人中心（头像上传、昵称、邮箱、密码修改）
- 全站白天/黑夜主题切换（持久化）
- 页面辅助工具（右下角浮动按钮）：主题切换、返回顶部、到达底部
- 顶部导航与底部页脚组件化复用
- 热门文章卡片固定悬浮（桌面端）
- 移动端 hamburger 抽屉菜单
- 非首页折叠搜索（展开/收起动画）
- **搜索页优化**：加载状态、空结果提示、关键词高亮、结果计数、卡片悬停动效、元信息 SVG 图标、移动端适配
- 评论区用户头像：已注册用户显示真实头像，匿名用户显示首字符头像
- 友链申请表单（实时校验）
- 静态资源地址统一解析（`assets/index.ts`）
- SEO 优化：动态 og:title / og:description / og:image / twitter:card meta 标签
- 页面标题无闪烁（HTML 默认标题 + Vue 异步更新）
- **首页 Hero 背景大图**：可配置背景大图，导航栏透明，滚动时自动隐藏/显示（半透明毛玻璃）
- **首页背景音乐**：左下角浮动播放器，支持网易云音乐链接嵌入
- **文章视频/音频插入**：编辑器支持插入本地视频/音频文件、YouTube/Bilibili/网易云音乐链接嵌入
- **无障碍支持**：所有交互元素添加 aria-label，表单使用 label 关联，屏幕阅读器友好的隐藏文本

### 后台（admin）

- 登录页 + 控制台概览 + 数学验证码
- **多语言支持**：中文 / English / 日本語，~470 个翻译 key，覆盖全部 16 个 Vue 组件，语言切换器（顶栏下拉菜单）
- 页面辅助工具（主题切换、返回顶部、到达底部）
- **URL 路由**：每个页面独立 URL（如 `/admin/articles`、`/admin/media`），刷新不丢失当前页面
- 顶部栏：用户昵称、角色标记、语言切换下拉、下拉菜单（个人中心 / 退出登录）
- 左侧菜单：主菜单 + 文章二级菜单（编辑文章未选中时禁用，仅从列表进入）
- 角色差异化发布策略（admin 直接发布 / author 提交审核）
- **文章管理**：列表 / 搜索 / 筛选 / 编辑 / 垃圾箱完整流程
- **创建/编辑文章**：Markdown 编辑器（支持深色模式自动切换）、插入视频（本地上传 + YouTube/Bilibili 嵌入）、插入音频（本地上传 + 网易云音乐嵌入）、封面图选择、分类/标签/状态、临时草稿保存
- **评论管理**：审核通过/拒绝/删除、批量操作、搜索筛选、刷新按钮
- **友链管理**：列表/搜索/筛选/编辑/审核/删除，首字符头像、数据刷新按钮
- **用户管理**：列表/搜索/角色筛选/创建/编辑/删除/批量操作、数据刷新按钮
- **媒体库**：文件上传、目录管理、拖拽排序
- **站点设置**：品牌信息（Logo 上传/拖拽、站点标题/副标题、页脚 HTML）、首页背景大图（URL 输入 + 媒体库选择）、首页背景音乐（网易云音乐链接/iframe 嵌入）
- **服务器配置**：域名、JWT 密钥（可编辑）、数据库连接/上传目录（只读显示）
- **个人中心**：头像上传、昵称、邮箱、密码修改
- **分类管理**：CRUD（支持层级分类，拼音自动生成 slug）

---

## 安全特性

### 认证与授权

- JWT + httpOnly Cookie 认证（admin / web 独立 Cookie 命名空间）
- Access Token 有效期 1 小时，Refresh Token 有效期 7 天
- Refresh Token 存储于数据库，支持单个/全部撤销
- JWT 中包含 `roles` claim，通过 `require_token_role()` 从 Token 校验角色
- JWT `sub` 使用用户 ID（非 username），改名不影响 Token
- CSRF 防护：双重提交 Cookie 模式（`csrf_token` cookie + `X-CSRF-Token` header），使用 `hmac.compare_digest` 防时序攻击
- 登录失败锁定：数据库持久化记录，6 次失败锁定 15 分钟，启动时自动清理过期记录

### 请求保护

- 全站速率限制（按端点配置，兜底 120 次/分钟）
- 登录端点 5 次/分钟，注册 3 次/5 分钟，上传 20 次/分钟
- 安装端点 3 次/10 分钟，安装状态 30 次/分钟
- 可选的反向代理 IP 信任（`TRUSTED_PROXY` 配置）

### 输入验证

- Pydantic v2 严格校验，所有字段有长度和格式限制
- 评论内容 `max_length=2000`，文章内容 `max_length=500000`
- 友链状态限制枚举值（`pending` / `approved` / `rejected`）
- 文件上传白名单限制扩展名和大小（默认 10MB，支持图片/音频/视频/文档）

### XSS 防护

- 前端 `v-html` 全部使用 DOMPurify 消毒
- CSP 安全头：`script-src 'self'`（无 unsafe-inline/eval）
- API 响应 `default-src 'none'`
- 上传文件 `.html`/`.svg` 等 Content-Type 覆盖为 `application/octet-stream`

### 其他安全头

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` + CSP `frame-ancestors 'none'`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- Cookie `SameSite=Lax`，生产环境支持 `Secure` 标志
- Swagger UI / Redoc 生产环境自动禁用
- 安装端点文件锁保护，防止重复安装

### CORS

- 来源白名单，禁止 `*` 通配符
- 方法限制为 `GET/POST/PUT/DELETE`
- 头限制为 `Content-Type/Authorization`

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
- Vue Router（路由懒加载）
- Vite
- vue-i18n（多语言）
- md-editor-v3（admin Markdown 编辑器）
- DOMPurify（web Markdown 渲染消毒）
- pinyin-pro（分类 slug 自动生成）

---

## 项目结构

```text
app/          FastAPI 后端（api / core / models / schemas / services / utils）
web/          前台 Vue 应用（端口 5173，多语言：zh-CN / en / ja）
  src/
    views/    页面组件（13 个视图）
    components/ 组件（FloatingTools / HomeBgmPlayer / WebFooter / WebTopbar）
    styles/   模块化 CSS（base / components / layout / pages / article-detail-*）
admin/        后台 Vue 应用（端口 5174，基础路径 /admin/）
  src/
    views/    页面组件（LoginView / DashboardView）
    components/ 面板组件（13 个管理面板）
    styles/   模块化 CSS（13 个独立样式文件）
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

#### 后端 `.env`

```env
# JWT 签名密钥（必填，生产环境务必设置）
SECRET_KEY=

# 数据库连接
DATABASE_URL=sqlite+aiosqlite:///./madongdong.db

# 调试模式
DEBUG=false

# SQL 查询日志
SQL_ECHO=false

# Cookie 安全标志（生产环境启用 HTTPS 后设为 true）
COOKIE_SECURE=false

# 信任代理头
TRUSTED_PROXY=false

# 文件上传目录
UPLOAD_DIR=app/static/uploads

# 文件上传大小限制（字节，默认 10MB）
UPLOAD_MAX_SIZE=10485760

# CORS 来源（JSON 数组格式）
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174"]
```

#### `web/.env`

```env
VITE_API_BASE=/api/v1
VITE_ADMIN_BASE_PATH=/admin
```

#### `admin/.env`

```env
VITE_API_BASE=/api/v1
VITE_WEB_BASE_URL=http://localhost:5173
```

---

## 默认管理员账号

首次启动后访问 `http://127.0.0.1:5173/install` 进入安装向导，可配置：

- 站点标题、副标题、域名（自动检测）
- JWT 签名密钥（自动生成或手动设置）
- 数据库连接（默认 SQLite）
- 管理员账号信息

安装完成后配置自动写入 `.env` 文件，重启后端生效。

---

## 主要接口

### 安装

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/install/status` | 获取安装状态 |
| GET | `/api/v1/install/secret-key` | 生成随机密钥 |
| POST | `/api/v1/install` | 执行首次安装（含域名、密钥、数据库配置） |

### 后台认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/auth/login` | 后台登录（含验证码） |
| POST | `/api/v1/admin/auth/refresh` | 刷新令牌 |
| POST | `/api/v1/admin/auth/revoke` | 登出（撤销令牌） |
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
| POST | `/api/v1/admin/articles` | 创建文章（自动生成 slug） |
| PUT | `/api/v1/admin/articles/{id}` | 更新文章 |
| DELETE | `/api/v1/admin/articles/{id}` | 删除（软删除） |
| POST | `/api/v1/admin/articles/{id}/restore` | 恢复 |
| DELETE | `/api/v1/admin/articles/{id}/permanent` | 彻底删除 |
| POST | `/api/v1/admin/articles/{id}/approve` | 审核通过 |
| POST | `/api/v1/admin/articles/{id}/reject` | 审核拒绝 |

### 后台分类/标签

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/admin/categories` | 分类列表/创建（支持 parent_id） |
| PUT | `/api/v1/admin/categories/{id}` | 更新分类（支持 parent_id） |
| DELETE | `/api/v1/admin/categories/{id}` | 删除分类（子分类自动提升） |
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
| GET/PUT | `/api/v1/admin/site/server-config` | 服务器配置（域名、密钥、数据库、上传目录） |

### 前台公开接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/web/home` | 首页数据 |
| GET | `/api/v1/web/articles/slug/{slug}` | 通过 slug 获取文章详情 |
| GET | `/api/v1/web/articles/{id}` | 通过 ID 获取文章详情（兼容） |
| GET | `/api/v1/web/search` | 搜索 |
| GET | `/api/v1/web/archive` | 归档 |
| GET | `/api/v1/web/categories` | 分类索引 |
| GET | `/api/v1/web/categories/{slug}/articles` | 分类文章 |
| GET | `/api/v1/web/tags/{slug}/articles` | 标签文章 |
| GET | `/api/v1/web/rss` | RSS Feed |
| GET | `/api/v1/web/sitemap.xml` | Sitemap |
| POST | `/api/v1/web/comments` | 提交评论 |
| GET | `/api/v1/web/friend-links` | 友链列表 |
| POST | `/api/v1/web/friend-links` | 申请友链 |
| GET | `/api/v1/web/captcha` | 获取验证码 |
| POST | `/api/v1/web/auth/register` | 读者注册（含验证码） |
| POST | `/api/v1/web/auth/login` | 读者登录（含验证码） |
| POST | `/api/v1/web/auth/refresh` | 刷新令牌 |
| POST | `/api/v1/web/auth/revoke` | 登出 |
| GET | `/api/v1/web/auth/me` | 获取当前用户 |
| PUT | `/api/v1/web/auth/me` | 更新个人资料 |

---

## 角色权限矩阵

| 角色 | Web 前台 | Admin 登录 | 文章创建 | 直接发布 | 提交审核 | 审核文章 | 垃圾箱 | 媒体 | 评论管理 | 友链管理 | 用户管理 | 站点设置 | 个人中心 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 系统管理员 | ❌ | ✅ | ✅ | ✅ | （可选） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 内容作者 | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅（仅本人） | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
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
SECRET_KEY=请替换为强随机密钥
DATABASE_URL=sqlite+aiosqlite:///./madongdong.db
DEBUG=false
SQL_ECHO=false
COOKIE_SECURE=true
TRUSTED_PROXY=true
UPLOAD_DIR=app/static/uploads
CORS_ORIGINS=["https://your-domain.com"]
```

---

## URL 风险扫描

前端构建前自动执行 URL 风险扫描，拦截可能影响 HTTPS 上线的硬编码地址。

- 扫描范围：`app`、`web/src`、`admin/src`
- 规则维护：`scripts/check-hardcoded-urls.config.json`
- 命中禁止规则时构建直接失败

---

## 预览

### 初始化安装步骤一

![](assets/images/22.png)

### 初始化安装步骤二

![](assets/images/23.png)

### 初始化安装步骤三

![](assets/images/24.png)

### 首页

![](assets/images/01.png)

### 读者注册

![](assets/images/02.png)

### 读者登录

![](assets/images/03.png)

### 首页（读者已登录）

![](assets/images/04.png)

### 文章详情

![](assets/images/05.png)

### 文章标签

![](assets/images/06.png)

### 文章评论区

![](assets/images/07.png)

### 管理员登录

![](assets/images/08.png)

### 管理员概览

![](assets/images/09.png)

### 文章管理

![10](assets/images/10.png)

### 创建文章

![](assets/images/11.png)

### 创建文章尾部

![12](assets/images/12.png)

### 编辑文章

![](assets/images/13.png)

### 文章分类管理

![](assets/images/14.png)

### 垃圾箱

![](assets/images/15.png)

### 媒体管理

![](assets/images/16.png)

### 评论管理

![](assets/images/17.png)

### 友链管理

![](assets/images/18.png)

### 用户管理

![](assets/images/19.png)

### 个人中心

![](assets/images/20.png)

### 设置

![](assets/images/21.png)

---

## 更新日志

### 2026-06-21

**后端**
- 新增 CSRF 防护中间件（双重提交 Cookie 模式），保护所有写请求
- 新增 RSS Feed（`/api/v1/web/rss`）和 Sitemap（`/api/v1/web/sitemap.xml`）接口
- 登录失败锁定改为数据库持久化（`login_attempts` 表），启动时自动清理过期记录
- 分类支持层级结构（`parent_id` 字段），删除父分类时子分类自动提升

**前台（web）**
- 无障碍支持：所有交互元素添加 aria-label，表单使用 for/id 关联，屏幕阅读器友好的隐藏文本（.sr-only）
- 新增 i18n key：`common.close`、`topbar.switchLanguage`
- 路由懒加载优化，提升首屏加载速度
- 修复登录页用户名/密码输入框图标显示异常（Unicode 编码修复）

**后台（admin）**
- 分类管理支持层级分类，拼音自动生成 slug

**样式**
- CSS 模块化重构：web 和 admin 样式拆分为独立模块文件，提升可维护性

### 2026-06-16

**前台（web）**
- 首页 Hero 背景大图：透明导航栏 + 全屏背景图，滚动时导航栏自动隐藏/半透明毛玻璃显示
- 首页背景音乐：左下角浮动播放器，支持网易云音乐歌曲/歌单链接嵌入
- 首页"热谈"卡片随页面滚动，与文章列表平齐
- 文章编辑器支持插入视频（本地 MP4/WebM 上传 + YouTube/Bilibili 嵌入）
- 文章编辑器支持插入音频（本地 MP3/WAV 上传 + 网易云音乐嵌入）
- 前端 DOMPurify 配置允许 video/audio/iframe 标签渲染
- md-editor-v3 开启 HTML 渲染（`markdownItConfig`）

**后台（admin）**
- 站点设置页面 UI 重构：3 列卡片布局（品牌信息 / 首页设置 / 服务器配置），每张卡片带图标
- 首页背景大图设置：URL 输入 + 媒体库图片选择器
- 首页背景音乐设置：网易云音乐链接/iframe 嵌入配置
- 语言切换器从浮动按钮移至顶栏下拉菜单
- 后端新增 `homepage_bgm_url` 和 `homepage_hero_image` 字段（含数据库自动迁移）
- 修复 `web.py` 中 `Request` 未导入的 ruff 警告

### 2026-06-15

**前台（web）**
- 搜索页 UI/UX 优化：加载状态、空结果提示、关键词高亮、结果计数、卡片悬停动效、SVG 元信息图标
- 搜索页移动端适配：960px / 480px 断点响应式布局
- 关于页内容更新：聚焦 MaDongDong 开源博客系统介绍（中/英/日三语言）
- 新增搜索页 i18n：`search.resultCount` / `search.noResults` / `search.noResultsHint` / `search.searching` / `search.tryOther`

**后台（admin）**
- **多语言支持**：中文 / English / 日本語 三语言，~470 个翻译 key，覆盖全部 16 个 Vue 组件
- URL 路由优化：每个页面独立 URL（如 `/admin/articles`、`/admin/media`），刷新不丢失当前页面
- Markdown 编辑器深色模式适配：通过 `MutationObserver` 监听 `data-theme` 自动切换编辑器主题
- 友链管理：刷新按钮改为 API 数据刷新（不再整页 reload）
- 用户管理：新增刷新按钮
- 编辑文章菜单：未选中文章时禁用，仅从文章列表编辑按钮进入
- 分类管理：输入框深色模式适配
- 废弃 `style.css`（Vite 脚手架初始样式，未被使用）

---

欢迎提交 [Issues](https://github.com/Lumosylva/madongdong/issues) 以便项目变得更好
