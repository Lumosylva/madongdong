"""通用响应工具。"""

from typing import Any


def success_response(data: Any) -> dict[str, Any]:
    """返回统一成功结构。"""

    return {"success": True, "data": data}
