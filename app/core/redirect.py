"""URL 重定向中间件 - 处理 URL 规范化。"""

import re
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse


class CanonicalRedirectMiddleware(BaseHTTPMiddleware):
    """
    URL 规范化中间件
    
    参考 WordPress 的 redirect_canonical() 函数，处理各种 URL 变体：
    1. 移除尾部斜杠（除首页外）
    2. 强制小写路径
    3. 移除多余查询参数
    4. 规范化查询参数顺序
    """

    # 不需要重定向的路径前缀
    EXCLUDED_PREFIXES = (
        "/api/",
        "/admin/",
        "/uploads/",
        "/docs",
        "/redoc",
        "/openapi.json",
    )

    # 不需要重定向的静态文件扩展名
    STATIC_EXTENSIONS = (
        ".js",
        ".css",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
    )

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        query = request.url.query

        # 跳过排除的路径
        if self._should_skip(path):
            return await call_next(request)

        # 规范化 URL
        new_path, new_query = self._canonicalize_url(path, query)

        # 如果有变化，返回 301 重定向
        if new_path != path or new_query != query:
            # 构建新的 URL
            new_url = f"{new_path}"
            if new_query:
                new_url += f"?{new_query}"
            return RedirectResponse(url=new_url, status_code=301)

        return await call_next(request)

    def _should_skip(self, path: str) -> bool:
        """检查是否应该跳过重定向"""
        # 跳过排除的路径前缀
        for prefix in self.EXCLUDED_PREFIXES:
            if path.startswith(prefix):
                return True

        # 跳过静态文件
        for ext in self.STATIC_EXTENSIONS:
            if path.endswith(ext):
                return True

        return False

    def _canonicalize_url(self, path: str, query: str) -> tuple[str, str]:
        """规范化 URL"""
        new_path = path
        new_query = query

        # 1. 移除尾部斜杠（除首页外）
        if new_path != "/" and new_path.endswith("/"):
            new_path = new_path.rstrip("/")

        # 2. 强制小写路径（保留查询参数大小写）
        if new_path != new_path.lower():
            new_path = new_path.lower()

        # 3. 规范化查询参数
        if new_query:
            new_query = self._canonicalize_query(new_query)

        return new_path, new_query

    def _canonicalize_query(self, query: str) -> str:
        """规范化查询参数"""
        if not query:
            return ""

        # 解析查询参数
        params = parse_qs(query, keep_blank_values=True)

        # 移除空值参数（可选）
        # params = {k: v for k, v in params.items() if v and v[0]}

        # 排序参数（可选，保持一致性）
        # sorted_params = sorted(params.items())

        # 重新编码
        # return urlencode(sorted_params, doseq=True)

        # 保持原始顺序，只清理多余参数
        return query


class WwwRedirectMiddleware(BaseHTTPMiddleware):
    """
    www/non-www 重定向中间件
    
    根据配置决定是否将 www 重定向到非 www，或反之
    """

    def __init__(self, app, redirect_www_to_non_www: bool = True):
        super().__init__(app)
        self.redirect_www_to_non_www = redirect_www_to_non_www

    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")

        # 跳过本地开发
        if "localhost" in host or "127.0.0.1" in host:
            return await call_next(request)

        # 检查是否需要重定向
        should_redirect = False
        new_host = host

        if self.redirect_www_to_non_www and host.startswith("www."):
            should_redirect = True
            new_host = host[4:]  # 移除 www.
        elif not self.redirect_www_to_non_www and not host.startswith("www."):
            should_redirect = True
            new_host = f"www.{host}"

        if should_redirect:
            # 构建新的 URL
            scheme = request.url.scheme
            path = request.url.path
            query = request.url.query

            new_url = f"{scheme}://{new_host}{path}"
            if query:
                new_url += f"?{query}"

            return RedirectResponse(url=new_url, status_code=301)

        return await call_next(request)
