"""首次安装业务逻辑。"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine
from app.core.security import get_password_hash
from app.models.article import Category
from app.models.auth import Permission, Role, User
from app.models.site import NavItem, SiteSetting
from app.schemas.install import InstallRequest

_INSTALLED_MARKER = Path(settings.upload_dir).parent / ".installed"

DEFAULT_ROLES = {
    'admin': '系统管理员',
    'author': '内容作者',
    'reader': '普通读者',
}

DEFAULT_PERMISSIONS = {
    'article:create': '创建文章',
    'article:review': '审核文章',
    'media:manage': '管理媒体',
    'user:manage': '管理用户',
    'comment:review': '审核评论',
    'site:manage': '管理站点配置',
}

ROLE_PERMISSION_MAP = {
    'admin': list(DEFAULT_PERMISSIONS.keys()),
    'author': ['article:create'],
    'reader': [],
}

DEFAULT_TABLES = [
    SiteSetting.__tablename__,
    User.__tablename__,
    Role.__tablename__,
    Permission.__tablename__,
    NavItem.__tablename__,
    Category.__tablename__,
]


async def _table_exists(session: AsyncSession, table_name: str) -> bool:
    """检查单个数据表是否存在。"""

    def _check() -> bool:
        inspector = inspect(engine.sync_engine)
        return inspector.has_table(table_name)

    return bool(await session.run_sync(lambda _: _check()))


async def _ensure_schema_ready(session: AsyncSession) -> bool:
    """检查安装所需表是否已准备就绪。"""

    try:
        for table_name in DEFAULT_TABLES:
            if not await _table_exists(session, table_name):
                return False
        return True
    except Exception:
        return False


async def get_install_state(session: AsyncSession) -> tuple[bool, bool]:
    """检查系统是否已安装。"""

    if _INSTALLED_MARKER.exists():
        return True, True

    try:
        schema_ready = await _ensure_schema_ready(session)
        if not schema_ready:
            return False, False

        site_exists = (await session.execute(select(SiteSetting.id).limit(1))).scalar_one_or_none() is not None
        user_exists = (await session.execute(select(User.id).limit(1))).scalar_one_or_none() is not None
        role_exists = (await session.execute(select(Role.id).limit(1))).scalar_one_or_none() is not None
        nav_exists = (await session.execute(select(NavItem.id).limit(1))).scalar_one_or_none() is not None

        installed = site_exists and user_exists and role_exists and nav_exists
        initialized = site_exists or user_exists or role_exists or nav_exists
        return installed, initialized
    except Exception:
        return False, False


async def _ensure_permissions(session: AsyncSession) -> dict[str, Permission]:
    items: dict[str, Permission] = {}
    for code, description in DEFAULT_PERMISSIONS.items():
        result = await session.execute(select(Permission).where(Permission.code == code))
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
        result = await session.execute(select(Role).where(Role.name == name))
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(name=name, description=description)
            session.add(role)
            await session.flush()
        items[name] = role
    return items


async def _bind_role_permissions(session: AsyncSession, roles: dict[str, Role], permissions: dict[str, Permission]) -> None:
    role_permission_table = Role.permissions.property.secondary
    for role_name, permission_codes in ROLE_PERMISSION_MAP.items():
        role = roles[role_name]
        await session.execute(role_permission_table.delete().where(role_permission_table.c.role_id == role.id))
        for code in permission_codes:
            await session.execute(
                role_permission_table.insert().values(role_id=role.id, permission_id=permissions[code].id)
            )
    await session.flush()


async def perform_install(session: AsyncSession, payload: InstallRequest) -> None:
    """执行首次安装。"""

    installed, _ = await get_install_state(session)
    if installed:
        return

    permissions = await _ensure_permissions(session)
    roles = await _ensure_roles(session)
    await _bind_role_permissions(session, roles, permissions)

    site_result = await session.execute(select(SiteSetting).limit(1))
    site = site_result.scalar_one_or_none()
    if site is None:
        site = SiteSetting()
        session.add(site)

    site.site_title = payload.site_title
    site.site_subtitle = payload.site_subtitle
    site.icp_beian = payload.icp_beian
    site.copyright_text = payload.copyright_text
    site.homepage_page_size = payload.homepage_page_size
    site.comment_requires_review = payload.comment_requires_review

    admin_role = roles['admin']
    user_result = await session.execute(select(User).where(User.username == payload.admin_username))
    user = user_result.scalar_one_or_none()
    if user is None:
        user = User(
            username=payload.admin_username,
            password_hash=get_password_hash(payload.admin_password),
            nickname=payload.admin_nickname,
            email=payload.admin_email,
            is_active=True,
            roles=[admin_role],
        )
        session.add(user)
    else:
        user.password_hash = get_password_hash(payload.admin_password)
        user.nickname = payload.admin_nickname
        user.email = payload.admin_email
        user.is_active = True
        if admin_role not in user.roles:
            user.roles.append(admin_role)

    nav_result = await session.execute(select(NavItem).limit(1))
    if nav_result.scalar_one_or_none() is None:
        session.add_all(
            [
                NavItem(title='首页', path='/', sort_order=1, is_visible=True),
                NavItem(title='搜索', path='/search', sort_order=2, is_visible=True),
            ]
        )

    category_result = await session.execute(select(Category).where(Category.slug == 'uncategorized'))
    category = category_result.scalar_one_or_none()
    if category is None:
        session.add(Category(name='未分类', slug='uncategorized', description='系统默认文章分类'))

    await session.commit()

    _INSTALLED_MARKER.parent.mkdir(parents=True, exist_ok=True)
    _INSTALLED_MARKER.write_text("installed")
