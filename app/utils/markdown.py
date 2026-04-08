"""Markdown 工具。"""

import html


def render_markdown(content: str) -> str:
    """将 Markdown 文本临时渲染为安全 HTML。"""

    escaped = html.escape(content)
    return escaped.replace("\n", "<br>")
