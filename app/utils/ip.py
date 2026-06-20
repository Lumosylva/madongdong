"""通用工具函数。"""

from __future__ import annotations

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """从请求中提取客户端真实 IP。"""

    from app.core.config import settings

    if settings.trusted_proxy:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

    if request.client:
        return request.client.host
    return "unknown"
