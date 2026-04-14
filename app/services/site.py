"""站点配置业务逻辑。"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site import NavItem, SiteSetting


async def get_or_create_site_setting(session: AsyncSession) -> SiteSetting:
    """获取站点配置，如不存在则创建默认值。"""

    result = await session.execute(select(SiteSetting).limit(1))
    setting = result.scalar_one_or_none()
    if setting is None:
        setting = SiteSetting()
        session.add(setting)
        await session.commit()
        await session.refresh(setting)
    return setting


async def update_site_setting(
    session: AsyncSession,
    site_title: str,
    site_logo: str | None,
    site_subtitle: str | None,
    icp_beian: str | None,
    copyright_text: str | None,
    homepage_page_size: int,
    comment_requires_review: bool,
) -> SiteSetting:
    """更新站点配置。"""

    setting = await get_or_create_site_setting(session)
    setting.site_title = site_title
    setting.site_logo = site_logo
    setting.site_subtitle = site_subtitle
    setting.icp_beian = icp_beian
    setting.copyright_text = copyright_text
    setting.homepage_page_size = homepage_page_size
    setting.comment_requires_review = comment_requires_review
    await session.commit()
    await session.refresh(setting)
    return setting


async def list_nav_items(session: AsyncSession, visible_only: bool = False) -> list[NavItem]:
    """查询导航项。"""

    statement = select(NavItem).order_by(NavItem.sort_order.asc(), NavItem.id.asc())
    if visible_only:
        statement = statement.where(NavItem.is_visible.is_(True))
    result = await session.execute(statement)
    items = list(result.scalars().all())
    return [item for item in items if str(item.title or '').strip() != '搜索']


async def create_nav_item(
    session: AsyncSession,
    title: str,
    path: str,
    sort_order: int,
    is_visible: bool,
    target: str | None,
    description: str | None,
) -> NavItem:
    """创建导航项。"""

    item = NavItem(
        title=title,
        path=path,
        sort_order=sort_order,
        is_visible=is_visible,
        target=target,
        description=description,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def update_nav_item(
    session: AsyncSession,
    nav_id: int,
    title: str,
    path: str,
    sort_order: int,
    is_visible: bool,
    target: str | None,
    description: str | None,
) -> NavItem:
    """更新导航项。"""

    item = await get_nav_item_or_404(session, nav_id)
    item.title = title
    item.path = path
    item.sort_order = sort_order
    item.is_visible = is_visible
    item.target = target
    item.description = description
    await session.commit()
    await session.refresh(item)
    return item


async def get_nav_item_or_404(session: AsyncSession, nav_id: int) -> NavItem:
    """获取导航项。"""

    result = await session.execute(select(NavItem).where(NavItem.id == nav_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="导航项不存在")
    return item
