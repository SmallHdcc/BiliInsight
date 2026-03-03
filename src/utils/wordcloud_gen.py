"""Word cloud generation helpers."""

from __future__ import annotations

import base64
import os
from io import BytesIO
from typing import Iterable, List



def generate_wordcloud(tags: Iterable[str], background_color: str = "#18191C") -> str:
    """Generate a word cloud image encoded in base64.

    Args:
        tags: Iterable of tag strings.
        background_color: Hex color string used as the background.

    Returns:
        Base64-encoded PNG string.

    Raises:
        ValueError: If `tags` contains no valid content.
    """
    cleaned_tags = _sanitize_tags(tags)
    if not cleaned_tags:
        raise ValueError("tags is empty")

    normalized_bg = _normalize_hex_color(background_color)

    # 根据背景色确定词云文字的颜色属性
    colormap = "viridis" if is_dark_color(normalized_bg) else "plasma"

    font_path = os.path.join(os.path.dirname(__file__), "..", "static", "PingFang.otf")

    from wordcloud import WordCloud

    wordcloud = WordCloud(
        width=800,
        height=500,
        font_path=font_path,
        background_color=normalized_bg,
        colormap=colormap,
        min_font_size=10,
        max_font_size=120,
        random_state=42,
    ).generate(" ".join(cleaned_tags))

    buffer = BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _sanitize_tags(tags: Iterable[str]) -> List[str]:
    """Keep only non-empty tag strings."""
    return [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]


def _normalize_hex_color(color: str) -> str:
    """Return a safe `#RRGGBB` color; fallback to the default theme color."""
    default_color = "#18191C"
    if not isinstance(color, str):
        return default_color

    raw = color.strip().lstrip("#")
    if len(raw) != 6:
        return default_color

    try:
        int(raw, 16)
    except ValueError:
        return default_color

    return f"#{raw.upper()}"


def is_dark_color(hex_color: str) -> bool:
    """判断颜色是否为深色。"""
    safe_color = _normalize_hex_color(hex_color).lstrip("#")

    r = int(safe_color[0:2], 16)
    g = int(safe_color[2:4], 16)
    b = int(safe_color[4:6], 16)

    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128
