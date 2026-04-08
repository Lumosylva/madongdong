"""数据库初始化。"""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.auth import Permission, Role, User
from app.models.article import Article, Category, Tag
from app.models.comment import Comment
from app.models.media import MediaFile, MediaFolder
from app.models.site import NavItem, SiteSetting

DEFAULT_ROLES = {
    "admin": "系统管理员",
    "author": "内容作者",
    "reader": "普通读者",
}

DEFAULT_PERMISSIONS = {
    "article:create": "创建文章",
    "article:review": "审核文章",
    "media:manage": "管理媒体",
    "user:manage": "管理用户",
    "comment:review": "审核评论",
    "site:manage": "管理站点配置",
}

ROLE_PERMISSION_MAP = {
    "admin": list(DEFAULT_PERMISSIONS.keys()),
    "author": ["article:create"],
    "reader": [],
}


async def init_db() -> None:
    """初始化数据库结构和默认数据。"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await _seed_defaults(session)


async def _seed_defaults(session: AsyncSession) -> None:
    """写入默认角色、权限和管理员。"""

    permissions = await _ensure_permissions(session)
    roles = await _ensure_roles(session)
    await _bind_role_permissions(session, roles, permissions)
    await _ensure_admin_user(session, roles["admin"])
    await _ensure_default_site(session)
    await session.commit()


async def _ensure_permissions(session: AsyncSession) -> dict[str, Permission]:
    items: dict[str, Permission] = {}
    for code, description in DEFAULT_PERMISSIONS.items():
        statement = select(Permission).where(Permission.code == code)
        result = await session.execute(statement)
        permission = result.scalar_one_or_none()
        if permission is None:
            permission = Permission(code=code, description=description)
            session.add(permission)
            await session.flush()
        items[code] = permission
    return items


async def _ensure_roles(session: AsyncSession) -> dict[str, Role]:
    items: dict[str, Role] = {}
    for name, description in DEFAULT_ROLES.items():
        statement = select(Role).where(Role.name == name)
        result = await session.execute(statement)
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(name=name, description=description)
            session.add(role)
            await session.flush()
        items[name] = role
    return items


async def _bind_role_permissions(
    session: AsyncSession,
    roles: dict[str, Role],
    permissions: dict[str, Permission],
) -> None:
    role_permission_table = Role.permissions.property.secondary
    for role_name, permission_codes in ROLE_PERMISSION_MAP.items():
        role = roles[role_name]
        await session.execute(delete(role_permission_table).where(role_permission_table.c.role_id == role.id))
        for code in permission_codes:
            await session.execute(
                role_permission_table.insert().values(role_id=role.id, permission_id=permissions[code].id)
            )
    await session.flush()


async def _ensure_admin_user(session: AsyncSession, admin_role: Role) -> None:
    statement = select(User).where(User.username == "admin")
    result = await session.execute(statement)
    admin_user = result.scalar_one_or_none()
    if admin_user is None:
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123456"),
            nickname="系统管理员",
            email="admin@example.com",
            is_active=True,
            roles=[admin_role],
        )
        session.add(admin_user)
        await session.flush()
        return

    role_names = {role.name for role in admin_user.roles}
    if "admin" not in role_names:
        admin_user.roles.append(admin_role)
        await session.flush()

    author_statement = select(Role).where(Role.name == "author")
    author_result = await session.execute(author_statement)
    author_role = author_result.scalar_one_or_none()
    if author_role is not None and "author" not in role_names:
        admin_user.roles.append(author_role)
        await session.flush()


async def _ensure_default_site(session: AsyncSession) -> None:
    statement = select(SiteSetting).limit(1)
    result = await session.execute(statement)
    site_setting = result.scalar_one_or_none()
    if site_setting is None:
        session.add(
            SiteSetting(
                site_title="MaDongDong Blog",
                site_subtitle="记录技术、生活与长期主义",
                icp_beian="备案信息待配置",
                copyright_text="© MaDongDong Blog",
                homepage_page_size=10,
                comment_requires_review=True,
            )
        )

    nav_result = await session.execute(select(NavItem))
    nav_items = list(nav_result.scalars().all())
    if not nav_items:
        session.add_all(
            [
                NavItem(title="首页", path="/", sort_order=1, is_visible=True),
                NavItem(title="搜索", path="/search", sort_order=2, is_visible=True),
            ]
        )
