import base64
from io import BytesIO
from wordcloud import WordCloud
import os


import base64
from io import BytesIO
from wordcloud import WordCloud
import os


def generate_wordcloud(tags, background_color="#18191C"):
    """Generate a word cloud from a list of tags."""
    # 根据背景色确定词云文字的颜色属性
    is_dark_bg = is_dark_color(background_color)
    colormap = "viridis" if is_dark_bg else "plasma"

    # Get the font path
    font_path = os.path.join(os.path.dirname(
        __file__), "..", "static", "PingFang.otf")

    # Generate word cloud
    wordcloud = WordCloud(
        width=800,
        height=500,
        font_path=font_path,
        background_color=background_color,
        colormap=colormap,
        min_font_size=10,
        max_font_size=120,
        random_state=42
    ).generate(" ".join(tags))

    # Convert to image and encode as base64
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def is_dark_color(hex_color):
    """判断颜色是否为深色"""
    # 去掉#号
    hex_color = hex_color.lstrip('#')

    # 将十六进制颜色转换为RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # 计算亮度 (简化版)
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    # 亮度小于128认为是深色
    return brightness < 128
