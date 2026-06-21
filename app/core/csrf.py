"""CSRF 防护中间件（双重提交 Cookie 模式）。

工作原理：
1. 用户登录/刷新令牌成功时，后端通过 ``set_csrf_cookie`` 写入一个
   **非 httpOnly** 的 ``csrf_token`` cookie（随机值）。
2. 前端读取该 cookie，在所有写请求（POST/PUT/PATCH/DELETE）的
   ``X-CSRF-Token`` 请求头里回传同一个值。
3. 本中间件对写方法校验：请求头值必须与 cookie 值相等，否则返回 403。

豁免规则：
- 安全方法（GET/HEAD/OPTIONS/TRACE）放行。
- 列入 ``CSRF_EXEMPT_PATHS`` 的公开写接口放行——这些接口在用户尚未登录、
  因此也没有 csrf cookie 时就需要被调用（安装、注册、友链申请、评论）。
  这些接口本身已有验证码 / 频率限制 / 可选登录态等防护。
"""

from __future__ import annotations

import hmac

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.status import HTTP_403_FORBIDDEN

CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

# 不需要 CSRF 校验的写方法路径（精确匹配前缀）
# 这些接口在用户尚未登录、没有 csrf cookie 时就会被调用
CSRF_EXEMPT_PREFIXES: tuple[str, ...] = (
    "/api/v1/install",          # 安装向导：首次部署时站点尚未初始化
    "/api/v1/web/auth/register",  # 读者注册：登录前，已有验证码 + 限流
    "/api/v1/web/auth/login",     # 登录本身：登录成功才会下发 csrf cookie
    "/api/v1/web/friend-links",   # 友链申请：未登录用户提交
    "/api/v1/admin/auth/login",   # 后台登录
)

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def _is_exempt(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") or path == prefix.rstrip("/") for prefix in CSRF_EXEMPT_PREFIXES)


class CSRFMiddleware(BaseHTTPMiddleware):
    """校验写请求的 X-CSRF-Token 头是否与 csrf_token cookie 一致。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method.upper()

        # 安全方法与豁免路径直接放行
        if method in SAFE_METHODS or _is_exempt(request.url.path):
            return await call_next(request)

        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)

        # 双重提交：两者都必须存在且相等（用 compare_digest 防时序攻击）
        if (
            not cookie_token
            or not header_token
            or not hmac.compare_digest(cookie_token, header_token)
        ):
            return Response(
                content='{"success":false,"detail":"CSRF 校验失败，请刷新页面后重试"}',
                status_code=HTTP_403_FORBIDDEN,
                media_type="application/json",
            )

        return await call_next(request)
