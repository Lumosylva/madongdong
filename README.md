# MaDongDong Blog

基于 `FastAPI + Vue 3 + SQLite` 的前后端分离博客系统，支持前台展示与后台管理。支持中文、English、日本語 三种语言。

## 主要功能

### 后端（FastAPI）

- 健康检查、应用生命周期初始化、首次安装向导
- 安装向导支持配置：站点域名（自动检测）、JWT 签名密钥（自动生成）、数据库连接（默认 SQLite）
- 安装完成后自动写入 `.env` 配置文件，域名配置自动生成 4 个 CORS 变体（http/https × 域名/www.域名）
- JWT 登录认证与角色鉴权（admin / author / reader）
- 细粒度能力权限系统：15 个能力权限，支持 `require_capability()` 装饰器
- CSRF 防护（双重提交 Cookie 模式，保护所有写请求）
- 文章能力：创建 / 更新 / 审核通过 / 审核驳回 / 摘要自动生成 / 定时发布 / 修订历史
- 文章 slug URL：`/article/{slug}`，自动生成，标题变更时重新生成
- 文章垃圾箱：删除 → 软删除 → 恢复 / 彻底删除
- 文章锁定：防并发编辑（15 分钟自动过期，锁定者或管理员可解锁）
- 分类管理（CRUD，支持层级分类）
- 标签管理（CRUD）
- 媒体库管理（文件上传、图片分辨率自动提取、目录管理、批量移动/删除）
- 评论管理与审核（通过 / 拒绝 / 彻底删除 / 垃圾标记 / 垃圾箱）
- 友情链接管理（前台申请、后台审核/编辑/删除）
- 站点配置与导航项管理（含首页背景大图、背景音乐配置、页脚版权/ICP备案/公安备案信息）
- 服务器级配置管理（域名、JWT 密钥、数据库连接、上传目录）
- 用户管理（创建/编辑/删除/批量角色变更）
- 应用密码（API 认证增强，支持创建/删除/查询应用密码）
- 个人资料更新（头像 base64 存储、昵称、邮箱、密码）
- 前台公开接口：首页 / 文章详情 / 搜索 / 评论提交 / 友链 / 归档 / 分类 / 标签
- RSS Feed（`/api/v1/web/rss`）、Sitemap（`/api/v1/web/sitemap.xml`）和 robots.txt（`/api/v1/web/robots.txt`）
- 浏览量去重（同一 IP 24 小时内同一文章只计 1 次）
- 速率限制（按端点配置，防止暴力破解）
- 登录失败锁定（数据库持久化，6 次失败锁定 15 分钟，启动时自动清理过期记录）
- 数学验证码（HMAC 签名，防止批量注册和暴力破解）
- Cookie 隔离（admin / web 前端使用独立 Cookie 命名空间）
- 数据库迁移自动处理（启动时自动添加新字段）
- URL 301 重定向系统（尾部斜杠移除、小写路径规范化、www/non-www 重定向）
- 旧 slug 重定向（文章标题变更时自动保存旧 slug，支持 301 重定向）

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
- **SEO 优化**：智能文档标题生成系统、动态 og:title / og:description / og:image / twitter:card meta 标签、canonical URL、JSON-LD 结构化数据（Article schema）、article:published_time / article:modified_time / article:author / article:section / article:tag 标签、增强的 robots 指令系统（支持多种爬虫规则）、301 重定向系统（URL 规范化）、旧 slug 重定向（保持 SEO 权重）
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
- **文章管理**：列表 / 搜索 / 筛选 / 编辑 / 垃圾箱完整流程 / 定时发布 / 修订历史
- **创建/编辑文章**：Markdown 编辑器（支持深色模式自动切换）、插入视频（本地上传 + YouTube/Bilibili 嵌入）、插入音频（本地上传 + 网易云音乐嵌入）、封面图选择、分类/标签/状态、临时草稿保存、定时发布设置
- **评论管理**：审核通过/拒绝/删除、批量操作、搜索筛选、刷新按钮
- **友链管理**：列表/搜索/筛选/编辑/审核/删除，首字符头像、数据刷新按钮
- **用户管理**：列表/搜索/角色筛选/创建/编辑/删除/批量操作、数据刷新按钮
- **媒体库**：Tab 设计（图片/音频/视频），文件上传自动提取图片分辨率，目录管理、拖拽排序
- **概览页**：快捷操作入口、最近文章列表、待处理事项、统计卡片带图标、7 日趋势图
- **站点设置**：Tab 设计（品牌信息 / 页脚信息 / 服务器配置 / 首页设置），页脚信息支持版权信息、ICP 备案号、公安备案号独立输入
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
- Pillow（图片分辨率提取）

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
  core/       核心模块（config / database / security / redirect / csrf / rate_limit）
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
Dockerfile    后端容器镜像构建
docker-compose.yml  容器编排配置
nginx.conf    Nginx 反向代理配置（Docker 使用）
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

# URL 重定向配置
REDIRECT_WWW_TO_NON_WWW=true  # www.example.com -> example.com
ENABLE_CANONICAL_REDIRECT=true  # 启用 URL 规范化重定向
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
| GET | `/api/v1/admin/auth/capabilities` | 获取当前用户的能力列表 |

### 后台用户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/auth/users` | 用户列表 |
| POST | `/api/v1/admin/auth/users` | 创建用户 |
| PUT | `/api/v1/admin/auth/users/{user_id}` | 更新用户 |
| DELETE | `/api/v1/admin/auth/users/{user_id}` | 删除用户 |
| POST | `/api/v1/admin/auth/users/batch/delete` | 批量删除 |
| POST | `/api/v1/admin/auth/users/batch/role` | 批量变更角色 |
| GET | `/api/v1/admin/auth/app-passwords` | 获取应用密码列表 |
| POST | `/api/v1/admin/auth/app-passwords` | 创建应用密码 |
| DELETE | `/api/v1/admin/auth/app-passwords/{id}` | 删除应用密码 |

### 后台文章

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/articles` | 文章列表 |
| GET | `/api/v1/admin/articles/deleted` | 垃圾箱列表 |
| GET | `/api/v1/admin/articles/scheduled` | 定时发布列表 |
| GET | `/api/v1/admin/articles/{id}` | 文章详情 |
| POST | `/api/v1/admin/articles` | 创建文章（自动生成 slug） |
| PUT | `/api/v1/admin/articles/{id}` | 更新文章 |
| DELETE | `/api/v1/admin/articles/{id}` | 删除（软删除） |
| POST | `/api/v1/admin/articles/{id}/restore` | 恢复 |
| DELETE | `/api/v1/admin/articles/{id}/permanent` | 彻底删除 |
| POST | `/api/v1/admin/articles/{id}/approve` | 审核通过 |
| POST | `/api/v1/admin/articles/{id}/reject` | 审核拒绝 |
| POST | `/api/v1/admin/articles/{id}/schedule` | 设置定时发布 |
| POST | `/api/v1/admin/articles/{id}/cancel-schedule` | 取消定时发布 |
| POST | `/api/v1/admin/articles/{id}/lock` | 锁定文章 |
| POST | `/api/v1/admin/articles/{id}/unlock` | 解锁文章 |
| GET | `/api/v1/admin/articles/{id}/lock-status` | 获取锁定状态 |
| GET | `/api/v1/admin/articles/{id}/revisions` | 获取修订历史 |
| GET | `/api/v1/admin/articles/{id}/revisions/{revision_id}` | 获取修订详情 |
| POST | `/api/v1/admin/articles/{id}/revisions/{revision_id}/restore` | 从修订恢复 |

### 后台分类/标签

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/admin/categories` | 分类列表/创建（支持 parent_id） |
| PUT | `/api/v1/admin/categories/{id}` | 更新分类（支持 parent_id） |
| DELETE | `/api/v1/admin/categories/{id}` | 删除分类（子分类自动提升） |
| GET | `/api/v1/admin/categories/{id}/meta` | 获取分类元数据 |
| PUT | `/api/v1/admin/categories/{id}/meta` | 更新分类元数据 |
| DELETE | `/api/v1/admin/categories/{id}/meta/{key}` | 删除分类元数据 |
| POST | `/api/v1/admin/categories/{id}/convert-to-tag` | 将分类转换为标签 |
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
| GET | `/api/v1/admin/comments` | 评论列表（分页） |
| GET | `/api/v1/admin/comments/spam` | 垃圾评论列表 |
| GET | `/api/v1/admin/comments/trash` | 垃圾箱评论列表 |
| POST | `/api/v1/admin/comments/{id}/approve` | 通过 |
| POST | `/api/v1/admin/comments/{id}/reject` | 拒绝 |
| POST | `/api/v1/admin/comments/{id}/spam` | 标记为垃圾 |
| POST | `/api/v1/admin/comments/{id}/trash` | 移入垃圾箱 |
| POST | `/api/v1/admin/comments/{id}/restore` | 从垃圾箱恢复 |
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
| GET | `/api/v1/web/articles/{id}/comments` | 获取文章评论（分页） |
| GET | `/api/v1/web/search` | 搜索 |
| GET | `/api/v1/web/archive` | 归档 |
| GET | `/api/v1/web/categories` | 分类索引 |
| GET | `/api/v1/web/categories/{slug}/articles` | 分类文章 |
| GET | `/api/v1/web/tags/{slug}/articles` | 标签文章 |
| GET | `/api/v1/web/rss` | RSS Feed |
| GET | `/api/v1/web/sitemap.xml` | Sitemap |
| GET | `/api/v1/web/robots.txt` | robots.txt |
| GET | `/api/v1/web/redirect/slug/{old_slug}` | 通过旧 slug 重定向到文章（301） |
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

### Docker 部署

#### 前置条件

1. 构建前端静态文件：

```bash
cd web && npm install && npm run build
cd ../admin && npm install && npm run build
```

2. 准备 `.env` 文件（参考 `.env.example`）：

```bash
cp .env.example .env
# 编辑 .env 设置 SECRET_KEY 等必要配置
```

#### 启动服务

```bash
# 构建并启动
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

#### 数据持久化

Docker Compose 自动创建以下数据卷：

- `uploads` — 用户上传的文件
- `db-data` — SQLite 数据库文件
- `web-dist` — 前台构建产物
- `admin-dist` — 后台构建产物

#### 自定义端口

在 `.env` 中设置 `PORT` 变量：

```env
PORT=8080
```

然后重启：`docker compose up -d`

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

### 2026-07-03

**后端**
- 新增文章修订历史功能：`article_revisions` 表存储修订版本，支持版本回滚
- 新增定时发布功能：`scheduled_at` 字段 + 后台调度器自动发布到期文章
- 新增文章锁定功能：`locked_by` / `locked_at` 字段，防止并发编辑（15 分钟自动过期）
- 新增分类元数据支持：`term_meta` 表存储分类扩展字段
- 新增分类/标签转换工具：支持将分类转换为同名标签
- 新增垃圾评论分类：`spam` / `trash` 状态 + 自动垃圾检测评分
- 新增评论分页：后台评论列表支持分页查询
- 新增应用密码：`application_passwords` 表支持 API 认证
- 新增细粒度能力权限系统：15 个能力权限，支持 `require_capability()` 装饰器
- **新增对象缓存系统**：内存缓存实现，支持 TTL 过期、LRU 淘汰、缓存统计，文章查询自动缓存（30 分钟）
- **新增数据库索引优化**：`published_at`、`scheduled_at` 字段添加索引，加速排序查询
- 修复 SQLAlchemy 多外键歧义：明确指定 `foreign_keys` 参数
- 修复数据库迁移：添加 `spam_score`、`locked_by`、`locked_at`、`scheduled_at` 字段
- 修复评论服务：添加缺失的 `get_comment_or_404` 函数
- **安全修复**：应用密码接口和分类元数据读取接口限制为管理员角色，防止普通用户越权访问

**前台（web）**
- 新增文章评论分页接口：`GET /api/v1/web/articles/{id}/comments`
- **翻译字符串优化**：新增通用翻译 key（delete/edit/create/refresh/reset 等），改进量词表达

**后台（admin）**
- 新增定时发布 API：设置 / 取消 / 查询定时发布文章
- 新增文章锁定 API：锁定 / 解锁 / 查询锁定状态
- 新增文章修订 API：查询修订历史 / 查看修订详情 / 从修订恢复
- 新增分类元数据 API：获取 / 更新 / 删除分类元数据
- 新增分类转换 API：将分类转换为标签
- 新增垃圾评论 API：标记垃圾 / 移入垃圾箱 / 恢复
- 新增评论分页：评论列表支持分页查询
- 新增应用密码 API：创建 / 查询 / 删除应用密码
- 新增能力查询 API：`GET /api/v1/admin/auth/capabilities` 返回用户能力列表
- **媒体库视图增强**：支持网格/列表视图切换，列表视图显示文件详情
- **多尺寸图片生成**：上传图片自动生成 thumbnail/medium/large 三种尺寸
- 修复评论管理前端：适配分页 API 响应格式

### 2026-07-02

**后端**
- 修复 Sitemap 文章 URL：`/article/{slug}` → `/article/details/{id}`（与前端路由一致）
- 修复 Sitemap lastmod：使用 `updated_at` 替代 `published_at`（更准确的修改时间）
- Sitemap 新增分类和标签页面（优先级 0.5/0.4）
- RSS Feed 增强：添加 `atom:link rel="self"`、`<category>`、`<content:encoded>` 元素
- RSS 文章 URL 同步修复为 `/article/details/{id}`
- 新增 `robots.txt` 端点（`GET /api/v1/web/robots.txt`），包含 Sitemap 指令
- 新增 301 重定向系统：URL 规范化中间件（尾部斜杠移除、小写路径、www/non-www 重定向）
- 新增旧 slug 重定向系统：`article_slug_history` 表存储旧 slug，支持 301 重定向

**前台（web）**
- 新增智能文档标题生成系统：`generateDocumentTitle()` 函数支持 9 种页面类型
- 新增增强的 robots 指令系统：`setRobotsMeta()` 函数支持多种指令组合
- 新增 canonical URL 支持（所有页面自动添加 `<link rel="canonical">`）
- 新增 JSON-LD 结构化数据（Article schema），提升搜索结果富摘要展示
- 文章页新增 `og:type=article`、`article:published_time`、`article:modified_time`、`article:author`、`article:section`、`article:tag` meta 标签
- 分类页和标签页新增 `og:description`、`twitter:description` meta 标签
- 搜索页和 404 页新增 robots meta 标签（noindex）
- 首页新增 `og:image` 支持（使用 Hero 背景大图或站点 Logo）
- robots.txt 开发代理配置

**配置**
- URL 风险扫描白名单新增 XML 命名空间 URL（`http://www.w3.org/2005/Atom`、`http://purl.org/rss/1.0/modules/content/`）
- 新增环境变量：`REDIRECT_WWW_TO_NON_WWW`、`ENABLE_CANONICAL_REDIRECT`

### 2026-07-01

**后端**
- 新增 Pillow 依赖，媒体上传时自动提取图片分辨率（width/height）
- 修复 `aiofiles.os` 兼容性问题（新版 aiofiles 移除了 `os` 模块）
- 新增 `police_beian`（公安备案号）字段到站点配置，启动时自动迁移数据库

**前台（web）**
- 页脚组件重构：支持显示版权信息、ICP 备案号、公安备案号三项独立内容
- 新增 `police_beian` 到 `SiteSetting` 类型定义
- 所有页面的 WebFooter 组件传递 `police-beian` 属性

**后台（admin）**
- **概览页 UI 重构**：新增欢迎横幅、4 个快捷操作卡片（写文章/上传媒体/管理评论/站点设置）、最近文章列表、待处理事项面板、7 日趋势迷你图
- **媒体库 Tab 化**：图片/音频/视频分 Tab 展示，每个 Tab 显示数量徽章，移动端只显示图标
- **站点设置 Tab 化**：品牌信息/页脚信息/服务器配置/首页设置分 Tab，页脚信息拆分为版权信息、ICP 备案号、公安备案号三个独立 textarea
- **媒体上传分辨率**：图片上传后自动提取并显示分辨率（格式：`宽 × 高 px`）
- 修复媒体上传 403 问题：uploadMediaFile 函数添加 CSRF token header
- 修复站点设置版权信息无法保存问题：补充 `update:copyrightText` 事件监听
- 修复公安备案号字段导致的 500 错误：新增数据库迁移函数

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
