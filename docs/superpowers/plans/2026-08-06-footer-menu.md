# Footer Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 web 端 footer「友情链接/RSS 行」上方新增一行可配置的页脚菜单（如「CTP手册」），支持内链/外链，由 admin 站点设置新增独立 Tab 管理。

**Architecture:** 复用 `nav_items` 表，加 `location` 字段区分 `header/footer`（默认 `header` 兼容老数据）。Admin 后台在「站点设置」新增独立 Tab「页脚菜单」，复用现有 `/admin/site/nav-items` CRUD 接口 +新增 DELETE。Web 端新增独立公开接口 `GET /web/footer-nav`，`WebFooter.vue` 通过模块级缓存的组合式函数 `useFooterNav()` 一次拉取，外链走 `<a target="_blank">`，内链走 `<RouterLink>`；无启用项时整行隐藏。

**Tech Stack:** FastAPI + SQLAlchemy 2 async + SQLite；Vue 3 + Vite + TypeScript + vue-i18n；`vue-tsc --noEmit` + `npm run build` 做前端类型/构建校验。

## Global Constraints

- 项目**无形式化测试框架**（无 pytest / vitest 配置）；验证靠 `PRAGMA` / `curl` / 类型检查 / 构建 / 浏览器 e2e，不写自动化测试代码
- 后端数据库为 SQLite；建列迁移必须走 `app/core/init_db.py` 的 `_migrate_*` 风格（`PRAGMA table_info` 检查 + `ALTER TABLE ADD COLUMN`）
- 前端资源 URL 一律走 `resolveAssetUrl()` / `webApi` / `adminApi`；构建阶段会跑 `scripts/check-hardcoded-urls.mjs`，不得引入裸的 `http://` / `localhost` / `127.0.0.1` 字面量
- 所有 admin 后端响应必须用 `success_response()` 包装信封
- Admin JWT 存 `localStorage['blog_admin_token']`；admin base path `/admin/`
- 三语（zh-CN / en / ja）文案必须同步添加，`admin/src/locales/*` 与 `web/src/locales/*` 各自维护
- `location` 值域固定为字符串 `'header'` 或 `'footer'`；默认 `'header'`

---

### Task 1: 后端数据模型 + 迁移 + Schema

**Files:**
- Modify: `app/models/site.py` — `NavItem` 加 `location` 列
- Modify: `app/schemas/site.py` — `NavItemBase` 加 `location` 字段
- Modify: `app/core/init_db.py` — 新增 `_migrate_nav_item_location` 并在 `init_db()` 调用

**Interfaces:**
- Consumes: 无（首个任务）
- Produces:
  - `NavItem.location: Mapped[str]`（默认 `'header'`，不可空，加索引）
  - `NavItemBase.location: Literal['header', 'footer'] = 'header'`（`NavItemCreate/Update/Response` 继承自动带上）
  - 启动时 `nav_items` 表自动补 `location` 列 + `ix_nav_items_location` 索引

- [ ] **Step 1: 修改 NavItem 模型**

编辑 `app/models/site.py` 的 `NavItem` 类，在 `description` 之后追加：

```python
class NavItem(TimestampMixin, Base):
    """导航项。"""

    __tablename__ = "nav_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    target: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(16), default='header', nullable=False, index=True)
```

- [ ] **Step 2: 修改 NavItemBase schema**

编辑 `app/schemas/site.py`，顶部 import 加入 `Literal`（如未存在），并在 `NavItemBase` 追加字段：

```python
from typing import Literal

class NavItemBase(BaseModel):
    """导航项基础字段。"""

    title: str = Field(min_length=1, max_length=100)
    path: str = Field(min_length=1, max_length=255)
    sort_order: int = 0
    is_visible: bool = True
    target: str | None = Field(default=None, max_length=20)
    description: str | None = None
    location: Literal['header', 'footer'] = 'header'
```

- [ ] **Step 3: 新增迁移函数**

编辑 `app/core/init_db.py`，在文件末尾（`_migrate_application_passwords` 之后）追加：

```python
async def _migrate_nav_item_location(session: AsyncSession) -> None:
    """为 nav_items 表添加 location 列（如果不存在）。"""

    try:
        result = await session.execute(text("PRAGMA table_info(nav_items)"))
        columns = [row[1] for row in result.fetchall()]
        if "location" in columns:
            return
    except Exception:
        return

    await session.execute(
        text("ALTER TABLE nav_items ADD COLUMN location VARCHAR(16) NOT NULL DEFAULT 'header'")
    )
    await session.execute(
        text("CREATE INDEX IF NOT EXISTS ix_nav_items_location ON nav_items (location)")
    )
    await session.commit()
```

- [ ] **Step 4: 在 init_db 注册迁移**

编辑 `app/core/init_db.py` 的 `init_db()` 函数，在 `await _migrate_application_passwords(session)` 之后追加一行：

```python
        await _migrate_application_passwords(session)
        await _migrate_nav_item_location(session)
```

- [ ] **Step 5: 启动后端验证迁移**

停掉正在运行的后端（如有），然后运行：

```powershell
.\.venv\Scripts\activate; uvicorn app.main:app --reload
```

在 uvicorn 完成启动（看到 `Application startup complete.`）后另开一个 PowerShell 验证列已加：

```powershell
python -c "import sqlite3; c=sqlite3.connect('madongdong.db'); print([r[1] for r in c.execute('PRAGMA table_info(nav_items)').fetchall()])"
```

Expected 输出包含 `'location'`。

- [ ] **Step 6: Commit**

```powershell
git add app/models/site.py app/schemas/site.py app/core/init_db.py
git commit -m "feat(nav): add location column to nav_items for footer menu support"
```

---

### Task 2: 后端 Service 层扩展

**Files:**
- Modify: `app/services/site.py` — `list_nav_items` 增参、`create/update_nav_item` 增参、新增 `delete_nav_item`

**Interfaces:**
- Consumes:
  - `NavItem.location`（Task 1 提供）
- Produces:
  - `list_nav_items(session, visible_only=False, location: str | None = None) -> list[NavItem]`
  - `create_nav_item(session, *, title, path, sort_order, is_visible, target, description, location='header') -> NavItem`
  - `update_nav_item(session, *, nav_id, title, path, sort_order, is_visible, target, description, location='header') -> NavItem`
  - `delete_nav_item(session, nav_id: int) -> None`

- [ ] **Step 1: 修改 list_nav_items 增加 location 过滤**

编辑 `app/services/site.py`，替换 `list_nav_items` 全体：

```python
async def list_nav_items(
    session: AsyncSession,
    visible_only: bool = False,
    location: str | None = None,
) -> list[NavItem]:
    """查询导航项。"""

    statement = select(NavItem).order_by(NavItem.sort_order.asc(), NavItem.id.asc())
    if visible_only:
        statement = statement.where(NavItem.is_visible.is_(True))
    if location:
        statement = statement.where(NavItem.location == location)
    result = await session.execute(statement)
    items = list(result.scalars().all())
    return [item for item in items if str(item.title or '').strip() != '搜索']
```

- [ ] **Step 2: 修改 create_nav_item 增加 location**

在同一文件替换 `create_nav_item`：

```python
async def create_nav_item(
    session: AsyncSession,
    title: str,
    path: str,
    sort_order: int,
    is_visible: bool,
    target: str | None,
    description: str | None,
    location: str = 'header',
) -> NavItem:
    """创建导航项。"""

    item = NavItem(
        title=title,
        path=path,
        sort_order=sort_order,
        is_visible=is_visible,
        target=target,
        description=description,
        location=location,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
```

- [ ] **Step 3: 修改 update_nav_item 增加 location**

替换 `update_nav_item`：

```python
async def update_nav_item(
    session: AsyncSession,
    nav_id: int,
    title: str,
    path: str,
    sort_order: int,
    is_visible: bool,
    target: str | None,
    description: str | None,
    location: str = 'header',
) -> NavItem:
    """更新导航项。"""

    item = await get_nav_item_or_404(session, nav_id)
    item.title = title
    item.path = path
    item.sort_order = sort_order
    item.is_visible = is_visible
    item.target = target
    item.description = description
    item.location = location
    await session.commit()
    await session.refresh(item)
    return item
```

- [ ] **Step 4: 新增 delete_nav_item**

在 `get_nav_item_or_404` 之后追加：

```python
async def delete_nav_item(session: AsyncSession, nav_id: int) -> None:
    """删除导航项。"""

    item = await get_nav_item_or_404(session, nav_id)
    await session.delete(item)
    await session.commit()
```

- [ ] **Step 5: Commit**

```powershell
git add app/services/site.py
git commit -m "feat(nav): extend service layer with location filter and delete"
```

---

### Task 3: 后端 Admin API 扩展

**Files:**
- Modify: `app/api/admin/site.py` — GET 加 `location` 查询参数、POST/PUT 透传 location、新增 DELETE

**Interfaces:**
- Consumes:
  - `list_nav_items(session, location=...)`、`create/update/delete_nav_item`（Task 2 提供）
  - `NavItemCreate/Update/Response` 已带 `location`（Task 1 提供）
- Produces:
  - `GET /admin/site/nav-items?location=header|footer|<omit>`
  - `POST /admin/site/nav-items` 支持 body 中 `location` 字段
  - `PUT /admin/site/nav-items/{id}` 支持 body 中 `location` 字段
  - `DELETE /admin/site/nav-items/{id}` → `success_response(None)`

- [ ] **Step 1: 修改 GET 端点**

编辑 `app/api/admin/site.py`，替换 `get_nav_items_endpoint`：

```python
@router.get("/nav-items", summary="查询导航项")
async def get_nav_items_endpoint(
    location: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    items = await list_nav_items(session, location=location)
    return success_response([NavItemResponse.model_validate(item).model_dump() for item in items])
```

- [ ] **Step 2: 修改 POST 端点透传 location**

替换 `create_nav_item_endpoint`：

```python
@router.post("/nav-items", summary="创建导航项")
async def create_nav_item_endpoint(
    payload: NavItemCreate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    item = await create_nav_item(
        session=session,
        title=payload.title,
        path=payload.path,
        sort_order=payload.sort_order,
        is_visible=payload.is_visible,
        target=payload.target,
        description=payload.description,
        location=payload.location,
    )
    return success_response(NavItemResponse.model_validate(item).model_dump())
```

- [ ] **Step 3: 修改 PUT 端点透传 location**

替换 `update_nav_item_endpoint`：

```python
@router.put("/nav-items/{nav_id}", summary="更新导航项")
async def update_nav_item_endpoint(
    nav_id: int,
    payload: NavItemUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    item = await update_nav_item(
        session=session,
        nav_id=nav_id,
        title=payload.title,
        path=payload.path,
        sort_order=payload.sort_order,
        is_visible=payload.is_visible,
        target=payload.target,
        description=payload.description,
        location=payload.location,
    )
    return success_response(NavItemResponse.model_validate(item).model_dump())
```

- [ ] **Step 4: 新增 DELETE 端点**

在 `update_nav_item_endpoint` 之后、`# ---------- 服务器级配置` 分隔线之前追加：

```python
@router.delete("/nav-items/{nav_id}", summary="删除导航项")
async def delete_nav_item_endpoint(
    nav_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    await delete_nav_item(session, nav_id)
    return success_response(None)
```

顶部 import 处加上 `delete_nav_item`：

```python
from app.services.site import (
    create_nav_item,
    delete_nav_item,
    get_or_create_site_setting,
    list_nav_items,
    update_nav_item,
    update_site_setting,
)
```

- [ ] **Step 5: 手动验证 admin API**

后端 `--reload` 应已自动重启。用登录后的 admin cookie 手动测试（或用浏览器 devtools console 中登录状态下调用）：

```powershell
# 假设你在浏览器 admin 页已登录，从 DevTools Console 中运行下面 JS：
# await fetch('/api/v1/admin/site/nav-items?location=footer', {credentials:'include'}).then(r=>r.json())
```

Expected：`{"success": true, "data": []}`（空数组，因为还没有 footer 项）。

- [ ] **Step 6: Commit**

```powershell
git add app/api/admin/site.py
git commit -m "feat(admin): support location filter and delete for nav-items"
```

---

### Task 4: 后端 Web API 扩展

**Files:**
- Modify: `app/api/web.py` — `_get_site_and_nav` 固定 `location='header'`、新增 `GET /web/footer-nav`

**Interfaces:**
- Consumes:
  - `list_nav_items(session, visible_only=True, location='footer')`（Task 2 提供）
- Produces:
  - `GET /web/footer-nav` → `list[NavItemResponse]` 直接返回数组（与 `/web/friend-links` 风格一致，不包信封）
  - `_get_site_and_nav()` 只回 header 导航项

- [ ] **Step 1: `_get_site_and_nav` 固定 header 过滤**

编辑 `app/api/web.py`，找到 `_get_site_and_nav`，替换 `list_nav_items(...)` 那一行：

```python
async def _get_site_and_nav(session: AsyncSession) -> tuple[SiteSettingResponse, list[NavItemResponse]]:
    """获取站点配置和导航项（复用，避免加载首页文章列表）。"""
    site = await get_or_create_site_setting(session)
    nav_items = await list_nav_items(session, visible_only=True, location='header')
    return SiteSettingResponse.model_validate(site), [NavItemResponse.model_validate(item) for item in nav_items]
```

- [ ] **Step 2: 同步 `/web/home` 内部导航加载**

在同一文件全局搜索所有其它 `list_nav_items(session, visible_only=True)` 调用（`get_homepage_data` / `get_search_page_data` / `get_archive_data` / `get_categories_page_data` / `get_category_page_data` / `get_tag_page_data` 中调用点），因为它们在 `app/services/web.py`，我们下一步处理。这一步先只处理 `web.py` 内 `_get_site_and_nav` 一处。

- [ ] **Step 3: 修改 services/web.py 中的 nav 加载**

搜索 `app/services/web.py` 里所有 `list_nav_items(` 出现位置：

```powershell
python -c "import re,pathlib; p=pathlib.Path('app/services/web.py'); print('\n'.join(f'{i+1}:{l}' for i,l in enumerate(p.read_text(encoding='utf-8').splitlines()) if 'list_nav_items' in l))"
```

对**每一处** `list_nav_items(session, visible_only=True)` 调用，改为：

```python
list_nav_items(session, visible_only=True, location='header')
```

（不要改变量名或缩进；只在参数尾部加 `, location='header'`。）

- [ ] **Step 4: 新增 footer-nav 端点**

在 `app/api/web.py` 中找到 `get_friend_links` 端点（`@router.get("/friend-links", …)`），在其之后追加：

```python
@router.get("/footer-nav", summary="获取页脚菜单")
async def footer_nav(
    session: AsyncSession = Depends(get_db_session),
) -> list[NavItemResponse]:
    items = await list_nav_items(session, visible_only=True, location='footer')
    return [NavItemResponse.model_validate(item) for item in items]
```

- [ ] **Step 5: 手动验证 /web/footer-nav**

后端已 `--reload` 重启。在浏览器打开：

```
http://127.0.0.1:8000/api/v1/web/footer-nav
```

Expected：`[]`（空数组）。

也验证顶部导航仍正常：

```
http://127.0.0.1:8000/api/v1/web/home
```

Expected：`nav_items` 数组包含现有 header 项。

- [ ] **Step 6: Commit**

```powershell
git add app/api/web.py app/services/web.py
git commit -m "feat(web): add /web/footer-nav endpoint and pin _get_site_and_nav to header"
```

---

### Task 5: Admin 前端 API 客户端

**Files:**
- Modify: `admin/src/api.ts` — 新增 4 个 nav-items 相关方法

**Interfaces:**
- Consumes:
  - `GET/POST/PUT/DELETE /admin/site/nav-items[?location=]`（Task 3 提供）
- Produces:
  - `adminApi.getNavItems(location?: 'header' | 'footer'): Promise<WrappedResponse<any[]>>`
  - `adminApi.createNavItem(payload): Promise<WrappedResponse<any>>`
  - `adminApi.updateNavItem(id, payload): Promise<WrappedResponse<any>>`
  - `adminApi.deleteNavItem(id): Promise<WrappedResponse<any>>`

- [ ] **Step 1: 在 adminApi 追加 4 个方法**

编辑 `admin/src/api.ts`，在 `adminApi` 对象内的 `deleteFriendLink` 方法之后（或其它任何合适位置）追加以下 4 个属性：

```ts
  getNavItems(location?: 'header' | 'footer'): Promise<WrappedResponse<any[]>> {
    const qs = location ? `?location=${location}` : ''
    return request<WrappedResponse<any[]>>(`/admin/site/nav-items${qs}`)
  },
  createNavItem(payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>('/admin/site/nav-items', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
  updateNavItem(id: number, payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/site/nav-items/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
  },
  deleteNavItem(id: number): Promise<WrappedResponse<any>> {
    return request<WrappedResponse<any>>(`/admin/site/nav-items/${id}`, {
      method: 'DELETE',
    })
  },
```

- [ ] **Step 2: 类型检查**

```powershell
cd admin; npx vue-tsc --noEmit
```

Expected：无错误退出。

- [ ] **Step 3: Commit**

```powershell
git add admin/src/api.ts
git commit -m "feat(admin): add nav-items API client methods"
```

---

### Task 6: Admin i18n 文案

**Files:**
- Modify: `admin/src/locales/zh-CN.ts`
- Modify: `admin/src/locales/en.ts`
- Modify: `admin/src/locales/ja.ts`

**Interfaces:**
- Consumes: 无
- Produces:
  - `siteSettings.tabFooterMenu` / `footerMenuSubtitle` / `addFooterMenuItem` / `fmTitle` / `fmTitlePlaceholder` / `fmPath` / `fmPathPlaceholder` / `fmPathTip` / `fmOpenInNewTab` / `fmEnabled` / `fmSortOrder` / `fmEmpty` / `fmTitleRequired` / `fmPathRequired` / `fmSaved` / `fmDeleted`

- [ ] **Step 1: zh-CN 追加**

编辑 `admin/src/locales/zh-CN.ts`，在 `siteSettings: {` 命名空间的对象里追加（放在末尾一条已有 key 之后）：

```ts
    tabFooterMenu: '页脚菜单',
    footerMenuSubtitle: '配置显示在页脚顶部的菜单项，如「使用手册」「联系我们」',
    addFooterMenuItem: '新建菜单项',
    fmTitle: '标题',
    fmTitlePlaceholder: '例如：CTP手册',
    fmPath: '链接',
    fmPathPlaceholder: '/article/details/12 或 https://...',
    fmPathTip: '以 / 开头为站内路径，以 http(s):// 开头为外链',
    fmOpenInNewTab: '新窗打开',
    fmEnabled: '启用',
    fmSortOrder: '排序',
    fmEmpty: '还没有菜单项，点上方按钮新建',
    fmTitleRequired: '请输入标题',
    fmPathRequired: '请输入链接',
    fmSaved: '已保存',
    fmDeleted: '已删除',
```

- [ ] **Step 2: en 追加**

编辑 `admin/src/locales/en.ts`，同样定位到 `siteSettings: {` 命名空间末尾，追加：

```ts
    tabFooterMenu: 'Footer Menu',
    footerMenuSubtitle: 'Configure menu items shown at the top of the footer, e.g. "Manual", "Contact"',
    addFooterMenuItem: 'Add menu item',
    fmTitle: 'Title',
    fmTitlePlaceholder: 'e.g. CTP Manual',
    fmPath: 'Link',
    fmPathPlaceholder: '/article/details/12 or https://...',
    fmPathTip: 'Paths starting with / are internal; http(s):// links open externally',
    fmOpenInNewTab: 'Open in new tab',
    fmEnabled: 'Enabled',
    fmSortOrder: 'Sort order',
    fmEmpty: 'No menu items yet. Click the button above to add one.',
    fmTitleRequired: 'Title is required',
    fmPathRequired: 'Link is required',
    fmSaved: 'Saved',
    fmDeleted: 'Deleted',
```

- [ ] **Step 3: ja 追加**

编辑 `admin/src/locales/ja.ts`，同样定位到 `siteSettings: {` 命名空间末尾，追加：

```ts
    tabFooterMenu: 'フッターメニュー',
    footerMenuSubtitle: 'フッター上部に表示するメニュー項目を設定します',
    addFooterMenuItem: '項目を追加',
    fmTitle: 'タイトル',
    fmTitlePlaceholder: '例：CTPマニュアル',
    fmPath: 'リンク',
    fmPathPlaceholder: '/article/details/12 または https://...',
    fmPathTip: '/ で始まるものは内部パス、http(s):// で始まるものは外部リンクです',
    fmOpenInNewTab: '新しいタブで開く',
    fmEnabled: '有効',
    fmSortOrder: '並び順',
    fmEmpty: 'メニュー項目はまだありません。上のボタンから追加してください。',
    fmTitleRequired: 'タイトルを入力してください',
    fmPathRequired: 'リンクを入力してください',
    fmSaved: '保存しました',
    fmDeleted: '削除しました',
```

- [ ] **Step 4: 类型检查**

```powershell
cd admin; npx vue-tsc --noEmit
```

Expected：无错误。

- [ ] **Step 5: Commit**

```powershell
git add admin/src/locales/zh-CN.ts admin/src/locales/en.ts admin/src/locales/ja.ts
git commit -m "feat(admin): add footer menu i18n strings"
```

---

### Task 7: Admin FooterMenuPanel 组件

**Files:**
- Create: `admin/src/components/FooterMenuPanel.vue`

**Interfaces:**
- Consumes:
  - `adminApi.getNavItems('footer') / createNavItem / updateNavItem / deleteNavItem`（Task 5）
  - i18n keys `siteSettings.tabFooterMenu / footerMenu* / fm*`（Task 6）
- Produces:
  - `<FooterMenuPanel />` — 组件自取自管的列表 CRUD 面板；不需要外部 props；仅 emit（可选）无外部依赖

- [ ] **Step 1: 创建面板组件**

创建 `admin/src/components/FooterMenuPanel.vue`，全文如下：

```vue
<template>
  <section class="panel fm-panel">
    <div class="fm-head">
      <div>
        <h3>{{ t('siteSettings.tabFooterMenu') }}</h3>
        <p class="fm-subtitle">{{ t('siteSettings.footerMenuSubtitle') }}</p>
      </div>
      <button type="button" class="fm-add-btn" @click="addItem">{{ t('siteSettings.addFooterMenuItem') }}</button>
    </div>

    <p v-if="toastMessage" class="fm-toast" :class="`toast-${toastStatus}`">{{ toastMessage }}</p>

    <ul v-if="items.length" class="fm-list">
      <li v-for="(item, idx) in items" :key="item.id ?? `new-${idx}`" class="fm-card">
        <label class="fm-field">
          <span>{{ t('siteSettings.fmTitle') }}</span>
          <input class="fm-input" v-model="item.title" :placeholder="t('siteSettings.fmTitlePlaceholder')" />
        </label>
        <label class="fm-field">
          <span>{{ t('siteSettings.fmPath') }}</span>
          <input class="fm-input" v-model="item.path" :placeholder="t('siteSettings.fmPathPlaceholder')" />
          <p class="fm-tips">{{ t('siteSettings.fmPathTip') }}</p>
        </label>
        <div class="fm-row-inline">
          <label class="fm-checkbox">
            <input type="checkbox" :checked="item.target === '_blank'" @change="onToggleBlank(item, $event)" />
            <span>{{ t('siteSettings.fmOpenInNewTab') }}</span>
          </label>
          <label class="fm-checkbox">
            <input type="checkbox" v-model="item.is_visible" />
            <span>{{ t('siteSettings.fmEnabled') }}</span>
          </label>
          <label class="fm-field fm-sort-field">
            <span>{{ t('siteSettings.fmSortOrder') }}</span>
            <input class="fm-input fm-sort-input" type="number" v-model.number="item.sort_order" />
          </label>
        </div>
        <div class="fm-actions">
          <button type="button" class="fm-btn fm-btn-save" :disabled="savingId === item.id" @click="save(item)">
            {{ t('common.save') }}
          </button>
          <button type="button" class="fm-btn fm-btn-delete" @click="remove(item, idx)">
            {{ t('common.delete') }}
          </button>
        </div>
      </li>
    </ul>
    <p v-else class="fm-empty">{{ t('siteSettings.fmEmpty') }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { adminApi } from '../api'

type Draft = {
  id?: number
  title: string
  path: string
  sort_order: number
  is_visible: boolean
  target: string | null
  description: string | null
  location: 'footer'
}

const { t } = useI18n()
const items = ref<Draft[]>([])
const savingId = ref<number | null>(null)
const toastMessage = ref('')
const toastStatus = ref<'success' | 'error' | ''>('')
let toastTimer: number | null = null

const showToast = (message: string, status: 'success' | 'error') => {
  toastMessage.value = message
  toastStatus.value = status
  if (toastTimer !== null) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toastMessage.value = ''
    toastStatus.value = ''
    toastTimer = null
  }, 2400)
}

const refetch = async () => {
  const res = await adminApi.getNavItems('footer')
  items.value = (res.data || []).map((raw: any) => ({
    id: raw.id,
    title: String(raw.title || ''),
    path: String(raw.path || ''),
    sort_order: Number(raw.sort_order || 0),
    is_visible: Boolean(raw.is_visible),
    target: raw.target ?? null,
    description: raw.description ?? null,
    location: 'footer',
  }))
}

const addItem = () => {
  const maxSort = items.value.reduce((max, it) => Math.max(max, it.sort_order), 0)
  items.value.unshift({
    title: '',
    path: '',
    sort_order: maxSort + 10,
    is_visible: true,
    target: null,
    description: null,
    location: 'footer',
  })
}

const onToggleBlank = (item: Draft, event: Event) => {
  item.target = (event.target as HTMLInputElement).checked ? '_blank' : null
}

const validate = (item: Draft): string | null => {
  if (!String(item.title || '').trim()) return t('siteSettings.fmTitleRequired')
  if (!String(item.path || '').trim()) return t('siteSettings.fmPathRequired')
  return null
}

const save = async (item: Draft) => {
  const err = validate(item)
  if (err) {
    showToast(err, 'error')
    return
  }
  savingId.value = item.id ?? -1
  try {
    const payload = {
      title: item.title.trim(),
      path: item.path.trim(),
      sort_order: Number(item.sort_order) || 0,
      is_visible: !!item.is_visible,
      target: item.target,
      description: item.description,
      location: 'footer' as const,
    }
    if (item.id) {
      await adminApi.updateNavItem(item.id, payload)
    } else {
      await adminApi.createNavItem(payload)
    }
    await refetch()
    showToast(t('siteSettings.fmSaved'), 'success')
  } catch (error) {
    showToast(error instanceof Error ? error.message : 'error', 'error')
  } finally {
    savingId.value = null
  }
}

const remove = async (item: Draft, idx: number) => {
  if (!item.id) {
    items.value.splice(idx, 1)
    return
  }
  try {
    await adminApi.deleteNavItem(item.id)
    await refetch()
    showToast(t('siteSettings.fmDeleted'), 'success')
  } catch (error) {
    showToast(error instanceof Error ? error.message : 'error', 'error')
  }
}

onMounted(() => {
  void refetch()
})
</script>

<style scoped>
.fm-panel {
  display: grid;
  gap: 14px;
}
.fm-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.fm-head h3 {
  margin: 0;
  font-size: 20px;
}
.fm-subtitle {
  margin: 4px 0 0;
  color: var(--text-soft);
  font-size: 13px;
}
.fm-add-btn {
  min-height: 40px;
  border-radius: 12px;
  padding: 0 16px;
  font-weight: 600;
  border: 1px solid rgba(14, 165, 164, 0.2);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.14), rgba(56, 189, 248, 0.08));
  color: var(--text);
  cursor: pointer;
}
.fm-add-btn:hover {
  border-color: rgba(14, 165, 164, 0.36);
}
.fm-toast {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
}
.fm-toast.toast-success {
  background: rgba(16, 185, 129, 0.1);
  color: #0f766e;
  border: 1px solid rgba(16, 185, 129, 0.24);
}
.fm-toast.toast-error {
  background: rgba(227, 91, 119, 0.1);
  color: #be123c;
  border: 1px solid rgba(227, 91, 119, 0.24);
}
.fm-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 12px;
}
.fm-card {
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.7);
  display: grid;
  gap: 10px;
}
.fm-field {
  display: grid;
  gap: 4px;
}
.fm-field > span {
  font-size: 13px;
  color: var(--text-soft);
}
.fm-input {
  min-height: 40px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(255, 255, 255, 0.85);
  padding: 0 12px;
  font-size: 14px;
  color: var(--text);
}
.fm-input:focus {
  outline: none;
  border-color: rgba(14, 165, 164, 0.6);
  box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.15);
}
.fm-tips {
  margin: 0;
  color: var(--text-soft);
  font-size: 12px;
}
.fm-row-inline {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  align-items: center;
}
.fm-checkbox {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text);
}
.fm-sort-field {
  min-width: 120px;
}
.fm-sort-input {
  max-width: 100px;
}
.fm-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
.fm-btn {
  min-height: 36px;
  border-radius: 10px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(148, 163, 184, 0.08);
  color: var(--text-soft);
  cursor: pointer;
}
.fm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.fm-btn-save {
  border-color: rgba(14, 165, 164, 0.24);
  background: linear-gradient(135deg, rgba(14, 165, 164, 0.14), rgba(56, 189, 248, 0.08));
  color: var(--text);
}
.fm-btn-delete {
  border-color: rgba(227, 91, 119, 0.24);
  background: linear-gradient(135deg, rgba(227, 91, 119, 0.12), rgba(227, 91, 119, 0.06));
  color: #be123c;
}
.fm-empty {
  margin: 0;
  padding: 24px;
  text-align: center;
  color: var(--text-soft);
  border: 1px dashed var(--line);
  border-radius: 14px;
}
</style>
```

- [ ] **Step 2: 类型检查**

```powershell
cd admin; npx vue-tsc --noEmit
```

Expected：无错误。

- [ ] **Step 3: Commit**

```powershell
git add admin/src/components/FooterMenuPanel.vue
git commit -m "feat(admin): add FooterMenuPanel component"
```

---

### Task 8: 挂载 FooterMenuPanel 到 SiteSettingsPanel

**Files:**
- Modify: `admin/src/components/SiteSettingsPanel.vue`

**Interfaces:**
- Consumes:
  - `FooterMenuPanel.vue`（Task 7）
  - i18n `siteSettings.tabFooterMenu`（Task 6）
- Produces: 无外部依赖变化；用户可在 admin 站点设置里看到「页脚菜单」Tab 并完整增删改

- [ ] **Step 1: import 组件**

编辑 `admin/src/components/SiteSettingsPanel.vue`，在 `<script setup lang="ts">` 顶部 import 区追加：

```ts
import FooterMenuPanel from './FooterMenuPanel.vue'
```

- [ ] **Step 2: tabIcons 追加 footerMenu 图标**

在 `const tabIcons = { ... }` 对象里，`footer` 键之后、`server` 键之前插入 `footerMenu` 键（选用链条图标，风格与既有 tab 图标一致）：

```ts
const tabIcons = {
  brand: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
  footer: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="15" x2="21" y2="15"/></svg>',
  footerMenu: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
  server: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>',
  homepage: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
}
```

- [ ] **Step 3: tabs 数组插入 footerMenu**

替换 `const tabs = computed(() => [ ... ])`：

```ts
const tabs = computed(() => [
  { key: 'brand', label: t('siteSettings.tabBrand'), icon: tabIcons.brand },
  { key: 'footer', label: t('siteSettings.tabFooter'), icon: tabIcons.footer },
  { key: 'footerMenu', label: t('siteSettings.tabFooterMenu'), icon: tabIcons.footerMenu },
  { key: 'server', label: t('siteSettings.tabServer'), icon: tabIcons.server },
  { key: 'homepage', label: t('siteSettings.tabHomepage'), icon: tabIcons.homepage },
])
```

- [ ] **Step 4: 在模板中挂载 FooterMenuPanel**

在 `<div v-show="activeTab === 'footer'" class="settings-card">` 整块（Tab 2 页脚）**结束**之后、`<div v-show="activeTab === 'server'" class="settings-card">` 开始之前，插入：

```vue
      <!-- Tab: Footer Menu -->
      <div v-show="activeTab === 'footerMenu'" class="settings-card">
        <FooterMenuPanel />
      </div>
```

- [ ] **Step 5: 类型检查 + 构建**

```powershell
cd admin; npx vue-tsc --noEmit; npm run build
```

Expected：类型无错误；构建成功（含 URL 硬编码扫描通过）。

- [ ] **Step 6: 浏览器手动 e2e**

启动 admin dev 服务器（如未运行）：

```powershell
cd admin; npm run dev
```

在浏览器 `http://127.0.0.1:5174/admin/site` 登录后：
1. 看到 tabs 顺序：品牌 / 页脚 / **页脚菜单** / 服务器 / 首页
2. 点「页脚菜单」→ 看到空态提示
3. 点「新建菜单项」→ 出现一张卡片
4. 填 title=`CTP手册`, path=`/about`, 勾选「启用」，点保存 → 显示「已保存」toast
5. 再新建一项：title=`GitHub`, path=`https://github.com`, 勾「新窗打开」，勾「启用」，保存
6. 切换 zh-CN / en / ja → 面板文案切换正常

- [ ] **Step 7: Commit**

```powershell
git add admin/src/components/SiteSettingsPanel.vue
git commit -m "feat(admin): mount FooterMenuPanel as a new Site Settings tab"
```

---

### Task 9: Web 前端 API 客户端 + 组合式函数

**Files:**
- Modify: `web/src/api.ts`
- Create: `web/src/composables/useFooterNav.ts`

**Interfaces:**
- Consumes:
  - `GET /web/footer-nav`（Task 4 提供）
- Produces:
  - `webApi.getFooterNav(): Promise<FooterNavItem[]>`
  - `useFooterNav(): Ref<FooterNavItem[]>` — 组合式函数，模块级缓存，SPA 会话内单次拉取

- [ ] **Step 1: webApi 追加 getFooterNav**

编辑 `web/src/api.ts`，在 `webApi` 对象内 `submitFriendLink` 之后追加：

```ts
  getFooterNav(): Promise<Array<{
    id: number
    title: string
    path: string
    target: string | null
    is_visible: boolean
    sort_order: number
  }>> {
    return request('/web/footer-nav')
  },
```

- [ ] **Step 2: 创建 composables 目录（若不存在）**

```powershell
if (-not (Test-Path web/src/composables)) { New-Item -ItemType Directory -Path web/src/composables }
```

- [ ] **Step 3: 创建 useFooterNav.ts**

创建 `web/src/composables/useFooterNav.ts`：

```ts
import { ref } from 'vue'
import { webApi } from '../api'

type FooterNavItem = {
  id: number
  title: string
  path: string
  target: string | null
  is_visible: boolean
  sort_order: number
}

const cache = ref<FooterNavItem[] | null>(null)
let inflight: Promise<void> | null = null

export function useFooterNav() {
  const items = ref<FooterNavItem[]>(cache.value ?? [])

  if (cache.value == null && inflight == null) {
    inflight = webApi
      .getFooterNav()
      .then((list) => {
        cache.value = list
        items.value = list
      })
      .catch(() => {
        cache.value = []
        items.value = []
      })
      .finally(() => {
        inflight = null
      })
  } else if (inflight) {
    void inflight.then(() => {
      items.value = cache.value ?? []
    })
  }

  return items
}
```

- [ ] **Step 4: 类型检查**

```powershell
cd web; npx vue-tsc --noEmit
```

Expected：无错误。

- [ ] **Step 5: Commit**

```powershell
git add web/src/api.ts web/src/composables/useFooterNav.ts
git commit -m "feat(web): add getFooterNav API and useFooterNav composable"
```

---

### Task 10: Web 前端 i18n + WebFooter 渲染菜单行

**Files:**
- Modify: `web/src/locales/zh-CN.ts`
- Modify: `web/src/locales/en.ts`
- Modify: `web/src/locales/ja.ts`
- Modify: `web/src/components/WebFooter.vue`

**Interfaces:**
- Consumes:
  - `useFooterNav()`（Task 9 提供）
- Produces:
  - Web footer 在「友情链接/RSS 行」上方多出「页脚菜单行」（有启用项时显示，无启用项时隐藏）
  - 外链走 `<a target="_blank" rel="noopener noreferrer">`；内链走 `<RouterLink>`

- [ ] **Step 1: 三语 footer.footerMenuLabel 追加**

在 `web/src/locales/zh-CN.ts` 的 `footer: { ... }` 命名空间末尾追加：

```ts
    footerMenuLabel: '页脚菜单',
```

在 `web/src/locales/en.ts` 的 `footer: { ... }` 追加：

```ts
    footerMenuLabel: 'Footer menu',
```

在 `web/src/locales/ja.ts` 的 `footer: { ... }` 追加：

```ts
    footerMenuLabel: 'フッターメニュー',
```

- [ ] **Step 2: 修改 WebFooter.vue 模板**

编辑 `web/src/components/WebFooter.vue`，在 `<div class="footer-inner">` 直接子元素中，`<div class="footer-links-row">` **之前**插入一个新的 `<nav class="footer-menu-row">`：

```vue
  <footer class="footer">
    <div class="footer-inner">
      <nav v-if="footerNav.length" class="footer-menu-row" :aria-label="t('footer.footerMenuLabel')">
        <template v-for="item in footerNav" :key="item.id">
          <a
            v-if="isExternal(item.path)"
            :href="item.path"
            class="footer-menu-link"
            :target="item.target || '_blank'"
            rel="noopener noreferrer"
          >{{ item.title }}</a>
          <RouterLink
            v-else
            :to="item.path"
            class="footer-menu-link"
          >{{ item.title }}</RouterLink>
        </template>
      </nav>

      <div class="footer-links-row">
        …（保持原样）
      </div>
      …
    </div>
  </footer>
```

（不要真的把原来的 `.footer-links-row` 替换为省略号，保留其全部内容。）

- [ ] **Step 3: WebFooter.vue script 追加 useFooterNav**

在 `<script setup lang="ts">` 末尾追加：

```ts
import { useFooterNav } from '../composables/useFooterNav'

const footerNav = useFooterNav()
const isExternal = (p: string) => /^https?:\/\//i.test(String(p || ''))
```

（`import` 要放在其它 import 附近；`const` 放在 `sanitizedPolice` 计算属性附近或末尾均可。）

- [ ] **Step 4: WebFooter.vue 样式追加**

在 `<style scoped>` 里 `.footer-links-row` 相关规则之前或之后追加：

```css
.footer-menu-row {
  justify-self: center;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  justify-content: center;
}

.footer-menu-link {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--text);
  padding: 8px 2px;
  position: relative;
  text-decoration: none;
}

.footer-menu-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 2px;
  width: 100%;
  height: 1px;
  background: color-mix(in srgb, var(--accent) 55%, transparent);
  transform: scaleX(0.7);
  transform-origin: center;
  transition: transform 0.18s ease, opacity 0.18s ease;
  opacity: 0.8;
}

.footer-menu-link:hover::after {
  transform: scaleX(1);
  opacity: 1;
}
```

- [ ] **Step 5: 类型检查 + 构建**

```powershell
cd web; npx vue-tsc --noEmit; npm run build
```

Expected：类型无错误；构建成功（含 URL 硬编码扫描通过）。

- [ ] **Step 6: 浏览器手动 e2e**

启动 web dev 服务器（若未运行）：

```powershell
cd web; npm run dev
```

在浏览器 `http://127.0.0.1:5173/` 滚动到底部：
1. 看到菜单行在「友情链接/RSS」之上，包含 Task 8 中创建的两项
2. 点「CTP手册」→ SPA 内跳转到 `/about`，页面不整体刷新
3. 回到首页，点「GitHub」→ 新窗口打开 `https://github.com`
4. 打开 DevTools Network，全站切换几次页面 → `/api/v1/web/footer-nav` 只请求一次
5. 回到 admin，把两项都取消勾选「启用」→ web 刷新 → 菜单行消失
6. 切换 zh-CN / en / ja → aria-label 切换正常（可通过 DevTools 检查元素）

- [ ] **Step 7: Commit**

```powershell
git add web/src/locales/zh-CN.ts web/src/locales/en.ts web/src/locales/ja.ts web/src/components/WebFooter.vue
git commit -m "feat(web): render footer menu row above friend-links using useFooterNav"
```

---

### Task 11: 端到端回归 + 文档收尾

**Files:**
- 无新增或修改

**Interfaces:**
- Consumes: 全部前序 Task 的成果
- Produces: 验证通过后的功能收尾

- [ ] **Step 1: 后端 sanity 检查**

确认后端仍在 `--reload` 运行，然后手动 curl（或浏览器打开）：

```powershell
# 查看 nav_items 表的行（应该都在，且默认 location=header）
python -c "import sqlite3; c=sqlite3.connect('madongdong.db'); print(list(c.execute('SELECT id, title, path, location FROM nav_items').fetchall()))"
```

Expected：既有 header 项都保留，同时应看到 Task 8 e2e 创建的 footer 项。

- [ ] **Step 2: 顶部导航回归**

在浏览器打开首页 `http://127.0.0.1:5173/`：
- 顶部导航栏原有条目依然出现（未受 footer 菜单影响）
- 顶部导航栏不含被打为 footer 位置的条目

- [ ] **Step 3: 页脚菜单空状态回归**

在 admin 把所有 footer 菜单项**删除**（不是禁用），刷新 web → 页脚菜单行消失，页脚样式与改动前一致。

- [ ] **Step 4: 再建一次并验证外链新窗**

admin 新建一项：title=`GitHub`, path=`https://github.com/`, 勾选新窗、启用，保存 → 刷新 web → 点「GitHub」→ 在新标签页打开。

- [ ] **Step 5: 关闭本地开发服务器（可选）**

如果本地开发环境需清理，`Ctrl+C` 停止 backend / admin / web 三个 dev 服务器。

- [ ] **Step 6: 最终 Commit（无代码变化时跳过）**

若前 10 个 task 已全部各自提交，本 task 无需再 commit。若途中还有零散未提交，用：

```powershell
git status
```

审查后按需 `git add … && git commit -m …`。

---

## Global Verification Recap

- 后端启动无异常，`init_db` 输出无迁移错误
- `sqlite> PRAGMA table_info(nav_items)` 含 `location`
- `GET /web/footer-nav` 只返回启用的 footer 项，按 `sort_order asc, id asc`
- `GET /web/home` 顶部 `nav_items` 只含 header 项
- Admin 站点设置 Tab 顺序：品牌 / 页脚 / 页脚菜单 / 服务器 / 首页
- Admin 三语文案完整
- Web footer：内链走 SPA、外链新窗、无项时行隐藏
- `cd admin && npm run build` 通过（URL 硬编码扫描无告警）
- `cd web && npm run build` 通过
