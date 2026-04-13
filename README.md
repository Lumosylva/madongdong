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

## 部署建议

- 后端使用 `uvicorn`（生产建议配合进程守护）
- 前后台执行 `npm run build` 后由 `Nginx` 托管静态资源
- `Nginx` 反向代理 `/api` 到 FastAPI
- 上传目录需做持久化
- 生产环境请通过 `.env` 覆盖 `secret_key` 等敏感配置
