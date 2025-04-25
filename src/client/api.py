import qrcode
import requests
from typing import Dict, List, Optional, Any, Tuple
import time
import logging

logger = logging.getLogger("biliinsight.client.api")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}


def get_qr_code() -> Optional[str]:
    """Get Bilibili login QR code and return the QR code key."""
    try:
        response = requests.get(
            "https://passport.bilibili.com/x/passport-login/web/qrcode/generate",
            headers=HEADERS
        )
        response.raise_for_status()
        data = response.json()
        if data["code"] == 0:
            qr_code_url = data["data"]["url"]
            login_qrcode_key = data["data"]["qrcode_key"]
            # 生成带时间戳的文件名防止缓存
            import time
            timestamp = int(time.time())
            qr_file_path = f"qr_code_{timestamp}.png"

            # 生成二维码图片
            img = qrcode.make(qr_code_url)
            img.save(qr_file_path)

            return login_qrcode_key, qr_file_path

        return None
    except (requests.RequestException, KeyError) as e:
        print(f"Error generating QR code: {e}")
        return None


def check_login_status(qrcode_key: str) -> Tuple[int, Optional[requests.cookies.RequestsCookieJar]]:
    """Check QR code login status."""
    try:
        response = requests.get(
            f"https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}",
            headers=HEADERS
        )
        response.raise_for_status()
        data = response.json()
        status = data["data"]["code"]

        if status == 0:  # Login successful
            return status, response.cookies
        else:
            return status, None
    except (requests.RequestException, KeyError) as e:
        print(f"Error checking login status: {e}")
        return -1, None


def get_user_info(cookies) -> Optional[Dict[str, Any]]:
    """Get user information using the login cookies."""
    try:
        response = requests.get(
            "https://api.bilibili.com/x/web-interface/nav",
            headers=HEADERS,
            cookies=cookies
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] == 0:
            user_info = data["data"]
            return {
                "uname": user_info["uname"],
                "mid": user_info["mid"],
                "face": user_info["face"],
            }
        else:
            print(f"Failed to get user info: {data['message']}")
            return None
    except (requests.RequestException, KeyError) as e:
        print(f"Error getting user info: {e}")
        return None


def get_watch_history(cookies, days=7, page_size=30) -> Optional[List[Dict[str, Any]]]:
    """
    获取完整的观看历史记录，通过多次分页请求获取全部数据。

    Args:
        cookies: 用户登录的cookies
        days: 获取最近几天的记录，默认7天
        page_size: 每页返回的记录数，默认30条(API最大允许值)

    Returns:
        历史记录列表
    """
    all_history = []
    page_size = 30  # 最大页大小
    current_time = int(time.time())
    one_week_ago = current_time - (days * 24 * 60 * 60)

    # 设置初始请求参数 - 不指定view_at，先获取最新的记录
    params = {
        "ps": page_size,
        "type": "all"
    }

    total_pages = 0
    try:
        while True:
            total_pages += 1
            logger.debug(f"获取历史记录第{total_pages}页，参数：{params}")

            response = requests.get(
                "https://api.bilibili.com/x/web-interface/history/cursor",
                headers=HEADERS,
                cookies=cookies,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            if data["code"] != 0:
                logger.error(f"获取观看历史失败: {data.get('message', '未知错误')}")
                break

            # 提取记录
            history_list = data["data"]["list"]
            if not history_list:
                logger.debug("没有更多记录，结束获取")
                break

            # 检查返回数据中是否有需要的信息
            filtered_list = []
            for item in history_list:
                view_at = item.get("view_at", 0)
                # 只保留一周内的记录
                if view_at >= one_week_ago:
                    filtered_list.append(item)

            logger.debug(
                f"本页获取{len(history_list)}条记录，过滤后保留{len(filtered_list)}条")
            all_history.extend(filtered_list)

            # 检查是否已经超出时间范围 - 如果本页最后一条记录时间早于一周前，不再继续
            if history_list and history_list[-1].get("view_at", 0) < one_week_ago:
                logger.debug("已到达时间范围边界，停止获取")
                break

            # 检查是否有下一页 - 获取游标
            cursor = data["data"].get("cursor")
            if not cursor:
                logger.debug("没有游标信息，结束获取")
                break

            # 检查获取页数是否过多，防止无限循环
            if total_pages >= 20:  # 设置合理的上限，通常一周的记录不会超过20页
                logger.warning("达到最大页数限制，停止获取")
                break

            # 更新参数用于获取下一页
            params = {
                "type": "all",
                "ps": page_size
            }

            # 添加游标参数
            if cursor.get("max"):
                params["max"] = cursor.get("max")
            if cursor.get("view_at"):
                params["view_at"] = cursor.get("view_at")
            if cursor.get("business"):
                params["business"] = cursor.get("business")

    except Exception as e:
        logger.exception(f"获取完整观看历史时发生错误: {e}")

    logger.info(f"成功获取历史记录，共{len(all_history)}条，查询了{total_pages}页")
    return all_history
