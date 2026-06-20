"""通用响应工具。

Admin API 使用 success_response() 包装所有响应为
{"success": true, "data": ...} 信封格式。

Web API 直接返回 Pydantic 模型（无信封包装）。
"""

from typing import Any


def success_response(data: Any) -> dict[str, Any]:
    """返回统一成功结构（Admin API 使用）。"""

    return {"success": True, "data": data}
