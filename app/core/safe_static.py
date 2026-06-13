"""安全的静态文件服务，强制覆盖危险文件类型的 Content-Type。"""

from __future__ import annotations

import mimetypes
from pathlib import Path

from starlette.responses import Response
from starlette.staticfiles import StaticFiles

_DANGEROUS_TYPES: dict[str, str] = {
    ".html": "application/octet-stream",
    ".htm": "application/octet-stream",
    ".xhtml": "application/octet-stream",
    ".svg": "application/octet-stream",
    ".xml": "application/octet-stream",
    ".js": "application/octet-stream",
    ".mjs": "application/octet-stream",
    ".json": "application/octet-stream",
    ".css": "application/octet-stream",
    ".php": "application/octet-stream",
    ".phtml": "application/octet-stream",
    ".exe": "application/octet-stream",
    ".bat": "application/octet-stream",
    ".cmd": "application/octet-stream",
    ".sh": "application/octet-stream",
    ".ps1": "application/octet-stream",
}


class SafeStaticFiles(StaticFiles):
    """覆盖危险扩展名的 Content-Type，防止浏览器渲染。"""

    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)
        ext = Path(path).suffix.lower()
        if ext in _DANGEROUS_TYPES:
            response.headers["Content-Type"] = _DANGEROUS_TYPES[ext]
            response.headers["Content-Disposition"] = "attachment"
        return response
