import qrcode
import requests
import io
import base64
from typing import Dict, List, Optional, Any, Tuple

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


def get_watch_history(cookies) -> Optional[List[Dict[str, Any]]]:
    """Get user's watch history."""
    try:
        response = requests.get(
            "https://api.bilibili.com/x/web-interface/history/cursor",
            headers=HEADERS,
            cookies=cookies
        )
        response.raise_for_status()
        data = response.json()

        if data["code"] == 0:
            return data["data"]["list"]
        else:
            print(f"Failed to get watch history: {data['message']}")
            return None
    except (requests.RequestException, KeyError) as e:
        print(f"Error getting watch history: {e}")
        return None
