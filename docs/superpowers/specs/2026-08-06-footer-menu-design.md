# Footer Menu 设计文档

- 日期：2026-08-06
- 作者：Lumosylva（与 Claude 协作）
- 状态：待审阅

## 背景

Web 端 footer 目前只显示两块内容：

1. 「友情链接」+「RSS」一行
2. 版权/ICP/公安备案一行

需要在这两块之上新增一行**可配置的页脚菜单**（如「CTP手册」），由 admin 后台管理，点击后可跳转到站内页面或外部 URL。

## 目标与非目标

**目标**
- 提供一份「页脚菜单」的可视化 CRUD 管理入口（admin）
- Web footer 在友情链接/RSS 上方展示已启用的菜单项
- 每项支持站内路径或外部 URL；外链默认新窗打开
- 无启用项时整行隐藏
- 三语（zh-CN / en / ja）admin 文案完备

**非目标**
- 不做嵌套菜单/分组
- 不引入图标字段
- 不改动顶部导航（header nav）的现有行为

## 关键决策

| # | 决策 | 结论 | 备注 |
|---|---|---|---|
| Q1 | 跳转形式 | 支持站内路径与外部 URL（两者都要） | 与顶部导航 NavItem 语义一致 |
| Q2 | 数据存储 | 复用 `nav_items` 表，加 `location` 字段区分 | 避免新建重复表和重复 CRUD |
| Q3 | Admin 入口 | 「站点设置」新增独立 Tab「页脚菜单」 | 与 3 个 textarea 的「页脚 Tab」分离，避免耦合列表 UI |
| Q4 | 字段范围 | 最小集：标题、链接、新窗开关、启用、排序 | 复用 NavItem 已有字段 |
| Q5 | 无启用项 | Web footer 整行隐藏 | 保持 footer 简洁 |
| —  | Web 取数 | 新增 `GET /web/footer-nav` 独立接口 | WebFooter 是全局组件，独立取更内聚，不动 7 处响应模型 |
| —  | 方案 | 方案 A：复用 nav_items + location | 相比 B（新表）/C（JSON 字段）代价最小 |

## 架构与数据流

```
┌─ Admin ────────────────────────────────────────────────┐
│  SiteSettingsPanel (Tab: FooterMenu)                   │
│      └─ FooterMenuPanel.vue                            │
│            │  (onMount / mutate) adminApi.*NavItem     │
│            ▼                                           │
│  GET/POST/PUT/DELETE /admin/site/nav-items[?location=] │
└────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌── FastAPI service layer ──┐
              │  list_nav_items(location) │
              │  create/update/delete     │
              └───────────┬───────────────┘
                          ▼
              ┌── SQLite: nav_items ──┐
              │  + location column    │
              └───────────┬───────────┘
                          │
                          ▼
┌─ Web ──────────────────────────────────────────────────┐
│  GET /web/footer-nav  →  location='footer', visible=1  │
│                          order by sort_order, id       │
│                                                        │
│  WebFooter.vue                                         │
│    └─ useFooterNav()  (module-level cached ref)        │
│    └─ 渲染 menu row，仅当 items.length > 0             │
│    └─ 外链 → <a target="_blank" rel="noopener">        │
│    └─ 内链 → <RouterLink>                              │
└────────────────────────────────────────────────────────┘
```

## 详细设计

### 1. 数据模型

**`app/models/site.py`** 的 `NavItem` 新增：

```python
location: Mapped[str] = mapped_column(
    String(16), default='header', nullable=False, index=True
)
```

- 值域：`"header"`（顶部导航）| `"footer"`（页脚菜单）
- 默认 `"header"`：老数据自动兼容
- 建索引：`GET /web/footer-nav` 会按 `location='footer'` 过滤

**`app/core/init_db.py`** 新增迁移函数 `_migrate_nav_item_location`，风格对齐现有 `_migrate_*`：

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

    await session.execute(text(
        "ALTER TABLE nav_items ADD COLUMN location VARCHAR(16) NOT NULL DEFAULT 'header'"
    ))
    await session.execute(text(
        "CREATE INDEX IF NOT EXISTS ix_nav_items_location ON nav_items (location)"
    ))
    await session.commit()
```

在 `init_db()` 里注册调用（放在 `_migrate_police_beian_column` 附近，按顺序追加一行即可）。

**`app/schemas/site.py`** 的 `NavItemBase`：

```python
from typing import Literal

class NavItemBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    path: str = Field(min_length=1, max_length=255)
    sort_order: int = 0
    is_visible: bool = True
    target: str | None = Field(default=None, max_length=20)
    description: str | None = None
    location: Literal['header', 'footer'] = 'header'
```

`NavItemCreate / NavItemUpdate / NavItemResponse` 因继承 base，自动带上 `location`。

### 2. 服务层

**`app/services/site.py`**

`list_nav_items` 增参：

```python
async def list_nav_items(
    session: AsyncSession,
    visible_only: bool = False,
    location: str | None = None,
) -> list[NavItem]:
    statement = select(NavItem).order_by(NavItem.sort_order.asc(), NavItem.id.asc())
    if visible_only:
        statement = statement.where(NavItem.is_visible.is_(True))
    if location:
        statement = statement.where(NavItem.location == location)
    result = await session.execute(statement)
    items = list(result.scalars().all())
    return [item for item in items if str(item.title or '').strip() != '搜索']
```

`create_nav_item / update_nav_item` 增参 `location: str = 'header'`，写入实体。

新增 `delete_nav_item`：

```python
async def delete_nav_item(session: AsyncSession, nav_id: int) -> None:
    item = await get_nav_item_or_404(session, nav_id)
    await session.delete(item)
    await session.commit()
```

### 3. Admin API

**`app/api/admin/site.py`**：

```python
@router.get("/nav-items", summary="查询导航项")
async def get_nav_items_endpoint(
    location: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    items = await list_nav_items(session, location=location)
    return success_response([NavItemResponse.model_validate(x).model_dump() for x in items])
```

`create_nav_item_endpoint / update_nav_item_endpoint` 透传 `payload.location`。

新增：

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

### 4. Web API

**`app/api/web.py`**：

`_get_site_and_nav()` 内部改为：

```python
nav_items = await list_nav_items(session, visible_only=True, location='header')
```

新增端点：

```python
@router.get("/footer-nav", summary="获取页脚菜单")
async def footer_nav(session: AsyncSession = Depends(get_db_session)) -> list[NavItemResponse]:
    items = await list_nav_items(session, visible_only=True, location='footer')
    return [NavItemResponse.model_validate(item) for item in items]
```

### 5. Admin 前端

#### 5.1 API 客户端

**`admin/src/api.ts`** 的 `adminApi` 新增：

```ts
getNavItems(location?: 'header' | 'footer'): Promise<WrappedResponse<any[]>> {
  const qs = location ? `?location=${location}` : ''
  return request<WrappedResponse<any[]>>(`/admin/site/nav-items${qs}`)
},
createNavItem(payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
  return request<WrappedResponse<any>>('/admin/site/nav-items', {
    method: 'POST', body: JSON.stringify(payload),
  })
},
updateNavItem(id: number, payload: Record<string, unknown>): Promise<WrappedResponse<any>> {
  return request<WrappedResponse<any>>(`/admin/site/nav-items/${id}`, {
    method: 'PUT', body: JSON.stringify(payload),
  })
},
deleteNavItem(id: number): Promise<WrappedResponse<any>> {
  return request<WrappedResponse<any>>(`/admin/site/nav-items/${id}`, {
    method: 'DELETE',
  })
},
```

#### 5.2 面板组件

新增 `admin/src/components/FooterMenuPanel.vue`：

结构：

```
<section class="panel fm-panel">
  <header>
    <h3>{{ t('siteSettings.tabFooterMenu') }}</h3>
    <p>{{ t('siteSettings.footerMenuSubtitle') }}</p>
    <button @click="addItem">{{ t('siteSettings.addFooterMenuItem') }}</button>
  </header>

  <ul v-if="items.length">
    <li v-for="(item, idx) in items" :key="item.id ?? `new-${idx}`" class="fm-card">
      <label>{{ t('siteSettings.fmTitle') }}
        <input v-model="item.title" :placeholder="t('siteSettings.fmTitlePlaceholder')" />
      </label>
      <label>{{ t('siteSettings.fmPath') }}
        <input v-model="item.path" :placeholder="t('siteSettings.fmPathPlaceholder')" />
        <p class="tips">{{ t('siteSettings.fmPathTip') }}</p>
      </label>
      <label class="fm-inline">
        <input type="checkbox" :checked="item.target === '_blank'" @change="toggleBlank(item, $event)" />
        {{ t('siteSettings.fmOpenInNewTab') }}
      </label>
      <label class="fm-inline">
        <input type="checkbox" v-model="item.is_visible" />
        {{ t('siteSettings.fmEnabled') }}
      </label>
      <label>{{ t('siteSettings.fmSortOrder') }}
        <input type="number" v-model.number="item.sort_order" />
      </label>
      <div class="fm-actions">
        <button @click="save(item)">{{ t('common.save') }}</button>
        <button class="fm-danger" @click="remove(item)">{{ t('common.delete') }}</button>
      </div>
    </li>
  </ul>
  <p v-else class="fm-empty">{{ t('siteSettings.fmEmpty') }}</p>
</section>
```

关键逻辑：
- `onMounted` 调 `adminApi.getNavItems('footer')`
- 「新建」在本地数组 unshift 一个未保存的空项（`id` 缺失作为“未保存”标识）
- 「保存」：若无 `id` → `createNavItem({ ...item, location: 'footer' })`；有 `id` → `updateNavItem(id, { ...item, location: 'footer' })`；成功后 refetch
- 「删除」：本地未保存项直接 splice；已保存项调 `deleteNavItem(id)` + refetch
- `target` 只在 checkbox 勾选时提交 `"_blank"`，否则 `null`

#### 5.3 SiteSettingsPanel 集线

`admin/src/components/SiteSettingsPanel.vue` 的 `tabs` 数组，在 `footer` 之后、`server` 之前插入 `footerMenu`。使用与现有 tab 一致的 inline SVG 风格（`viewBox="0 0 24 24"`, `stroke="currentColor"`, `stroke-width=2`），选用链条图标：

在现有 `tabIcons` 对象字面量里追加 `footerMenu` 键，并把 `footerMenu` 加入 `tabs` 计算属性数组：

```ts
const tabIcons = {
  brand:      '<svg …>…</svg>',
  footer:     '<svg …>…</svg>',
  footerMenu: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
  server:     '<svg …>…</svg>',
  homepage:   '<svg …>…</svg>',
}

const tabs = computed(() => [
  { key: 'brand',       label: t('siteSettings.tabBrand'),      icon: tabIcons.brand },
  { key: 'footer',      label: t('siteSettings.tabFooter'),     icon: tabIcons.footer },
  { key: 'footerMenu',  label: t('siteSettings.tabFooterMenu'), icon: tabIcons.footerMenu },
  { key: 'server',      label: t('siteSettings.tabServer'),     icon: tabIcons.server },
  { key: 'homepage',    label: t('siteSettings.tabHomepage'),   icon: tabIcons.homepage },
])
```

模板里 `v-show="activeTab === 'footerMenu'"` 的容器内直接渲染 `<FooterMenuPanel />`，无需从父组件 `DashboardView` 传 props（组件自取自管）。

#### 5.4 字段处理细节

- **`description` 字段**：不在 UI 里编辑；`FooterMenuPanel` 保留 fetch 到的原值原样回传；新建项默认 `null`。
- **前端校验**：`save(item)` 提交前做本地校验；`title.trim() === '' || path.trim() === ''` 时不发请求，就地展示错误提示（复用 `SiteSettingsPanel` 的 toast 风格，可通过 emit 事件冒泡给 `DashboardView`，或组件内维护本地 toast）。
- **`target` 语义**：仅 `null` 或 `"_blank"` 两种取值。UI 上以「新窗打开」勾选框呈现；勾选 → `_blank`；未勾选 → `null`。后端 schema `target: str | None`（已存在）兼容。
- **`sort_order` 默认**：新建项默认取「当前列表最大 `sort_order` + 10」，避免与已有项冲突且方便后续插队。

### 6. Web 前端

#### 6.1 API 客户端

**`web/src/api.ts`** 的 `webApi` 新增：

```ts
getFooterNav(): Promise<Array<{
  id: number; title: string; path: string;
  target: string | null; is_visible: boolean; sort_order: number
}>> {
  return request('/web/footer-nav')
}
```

#### 6.2 组合式函数

**`web/src/composables/useFooterNav.ts`**：

```ts
import { ref } from 'vue'
import { webApi } from '../api'

type FooterNavItem = {
  id: number; title: string; path: string;
  target: string | null; is_visible: boolean; sort_order: number
}

const cache = ref<FooterNavItem[] | null>(null)
let inflight: Promise<void> | null = null

export function useFooterNav() {
  const items = ref<FooterNavItem[]>(cache.value ?? [])
  if (cache.value == null && !inflight) {
    inflight = webApi.getFooterNav()
      .then((list) => {
        cache.value = list
        items.value = list
      })
      .catch(() => { cache.value = [] })
      .finally(() => { inflight = null })
  } else if (inflight) {
    inflight.then(() => { items.value = cache.value ?? [] })
  }
  return items
}
```

模块级 `cache` + `inflight` 保证同一 SPA 会话只请求一次（footer 菜单变更频率极低）。

#### 6.3 WebFooter 改动

**`web/src/components/WebFooter.vue`** 在 `<div class="footer-links-row">` 之上插入：

```html
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
```

`<script setup>` 新增：

```ts
import { useFooterNav } from '../composables/useFooterNav'
const footerNav = useFooterNav()
const isExternal = (p: string) => /^https?:\/\//i.test(String(p || ''))
```

样式 `.footer-menu-row / .footer-menu-link`：与 `.footer-links-row / .footer-friend-links-link` 完全同款（居中、间距 20px、字号 14 / 字重 700 / 下划线 hover 动画一致），保证视觉一致性。

### 7. i18n

Admin 和 Web 各有独立 locale 目录：
- `admin/src/locales/{zh-CN,en,ja}.ts`：面板相关 key（`siteSettings.*`）
- `web/src/locales/{zh-CN,en,ja}.ts`：footer 相关 key（`footer.*`）

**Admin 新增 key**（追加到 `siteSettings` 命名空间）：

| Key | zh-CN | en | ja |
|---|---|---|---|
| `tabFooterMenu` | 页脚菜单 | Footer Menu | フッターメニュー |
| `footerMenuSubtitle` | 配置显示在页脚顶部的菜单项，如「使用手册」「联系我们」 | Configure menu items shown at the top of the footer, e.g. "Manual", "Contact" | フッター上部に表示するメニュー項目を設定します |
| `addFooterMenuItem` | 新建菜单项 | Add menu item | 項目を追加 |
| `fmTitle` | 标题 | Title | タイトル |
| `fmTitlePlaceholder` | 例如：CTP手册 | e.g. CTP Manual | 例：CTPマニュアル |
| `fmPath` | 链接 | Link | リンク |
| `fmPathPlaceholder` | /article/details/12 或 https://... | /article/details/12 or https://... | /article/details/12 または https://... |
| `fmPathTip` | 以 / 开头为站内路径，以 http(s):// 开头为外链 | Paths starting with / are internal; http(s):// links open externally | / で始まるものは内部パス、http(s):// で始まるものは外部リンクです |
| `fmOpenInNewTab` | 新窗打开 | Open in new tab | 新しいタブで開く |
| `fmEnabled` | 启用 | Enabled | 有効 |
| `fmSortOrder` | 排序 | Sort order | 並び順 |
| `fmEmpty` | 还没有菜单项，点上方按钮新建 | No menu items yet. Click the button above to add one. | メニュー項目はまだありません。上のボタンから追加してください。 |
| `fmTitleRequired` | 请输入标题 | Title is required | タイトルを入力してください |
| `fmPathRequired` | 请输入链接 | Link is required | リンクを入力してください |
| `fmSaved` | 已保存 | Saved | 保存しました |
| `fmDeleted` | 已删除 | Deleted | 削除しました |

**Web 新增 key**（追加到 `footer` 命名空间）：

| Key | zh-CN | en | ja |
|---|---|---|---|
| `footerMenuLabel` | 页脚菜单 | Footer menu | フッターメニュー |

（`footerMenuLabel` 仅用于 `<nav aria-label>`，用户不直接可见。）

## 验证策略

项目无形式化测试框架，采用「类型检查 + 构建 + 手动 e2e」：

**后端**
- 启动服务，观察 `init_db` 迁移日志
- `sqlite3 madongdong.db "PRAGMA table_info(nav_items)"` 确认 `location` 列
- 通过 admin API 分别以 `location=header / footer / 不传` 拉取，确认过滤生效
- 通过 admin API 走一遍 POST/PUT/DELETE，每步 200 且数据落库正确
- `GET /web/footer-nav` 返回只含 `visible=true` 且 `location='footer'`，按 `sort_order asc, id asc` 排序
- `GET /web/home` / 文章详情 → 顶部导航仍工作（历史数据 `location='header'`）

**前端**
- `cd admin && npx vue-tsc --noEmit` 通过
- `cd web && npx vue-tsc --noEmit` 通过
- `cd admin && npm run build`（含硬编码 URL 扫描）通过
- `cd web && npm run build` 通过
- 浏览器 e2e：
  1. admin：站点设置 → 页脚菜单 Tab；新建一个内链项（`/about`）和一个外链项（`https://example.com`），保存
  2. web：任意页面滚到底部，看到菜单行；内链 SPA 跳转不刷新；外链新窗
  3. 全部禁用 `is_visible` 后刷新 → 菜单行消失（`v-if="footerNav.length"`）
  4. 三语切换 → admin 面板文案切换正常
  5. 关闭再打开浏览器 tab（清缓存） → footer 只请求一次 `/web/footer-nav`（DevTools Network 验证）

**回归**
- 顶部导航现有 nav_items 全部落到 `location='header'`，展现无变化
- 友情链接页 / RSS 链接可用

## 兼容性与风险

- **数据兼容**：`location` 默认 `'header'`，老 `nav_items` 数据零变化；`_get_site_and_nav()` 显式过滤 `location='header'`，确保之后新增 footer 项不会污染顶部导航
- **缓存**：`useFooterNav` 模块级缓存生存期是 SPA 会话；admin 侧修改后 web 端用户需要 F5 才能看到（可接受，因为 footer 变更极低频）。如需实时性，后续可改为 SWR 或在 `HomeResponse` 内联返回
- **XSS**：菜单项 `title` 直接文本渲染（不用 `v-html`），`path` 只用于 `href` / `to`；外链使用 `rel="noopener noreferrer"` 防止 tabnabbing
- **URL 硬编码扫描**：本次改动无新增 `http://` / `localhost` 字面量；`useFooterNav` 走 `webApi.getFooterNav()` 内部拼 `API_BASE`，不触发 `check-hardcoded-urls`

## 变更清单

**新增文件**
- `admin/src/components/FooterMenuPanel.vue`
- `web/src/composables/useFooterNav.ts`
- `docs/superpowers/specs/2026-08-06-footer-menu-design.md`（本文档）

**修改文件**
- `app/models/site.py` — `NavItem.location`
- `app/schemas/site.py` — `NavItemBase.location`
- `app/services/site.py` — `list_nav_items` 增参、`create/update_nav_item` 增参、新增 `delete_nav_item`
- `app/api/admin/site.py` — `GET` 增 `location` 参数、`POST/PUT` 透传 location、新增 `DELETE`
- `app/api/web.py` — `_get_site_and_nav` 固定 header、新增 `GET /web/footer-nav`
- `app/core/init_db.py` — 新增 `_migrate_nav_item_location` 并在 `init_db()` 里调用
- `admin/src/api.ts` — 新增 4 个 `*NavItem` 方法
- `admin/src/components/SiteSettingsPanel.vue` — tabs 里插入 `footerMenu` 项 + 渲染 `<FooterMenuPanel />`
- `web/src/api.ts` — 新增 `webApi.getFooterNav`
- `web/src/components/WebFooter.vue` — footer menu row + `useFooterNav` 引入 + isExternal 判断
- `admin/src/locales/{zh-CN,en,ja}.ts` — `siteSettings.*` 命名空间新增 16 个 key
- `web/src/locales/{zh-CN,en,ja}.ts` — `footer.footerMenuLabel` 一个 key

## 未来延展（非本次范围）

- 图标：如未来需要，添加 `NavItem.icon` 列并在两处渲染
- 多列/分组：如 footer 菜单条目多，可增加 `group` 字段做分栏
- SSR/首屏：如接入 SSR，`useFooterNav` 需要改成注水
