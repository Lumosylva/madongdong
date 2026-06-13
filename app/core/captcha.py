"""验证码生成与校验。"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time

from fastapi import HTTPException, status

_TTL = 300  # 5 分钟有效


def _get_captcha_secret() -> bytes:
    from app.core.config import settings
    return hashlib.sha256(f"captcha:{settings.secret_key}".encode()).digest()


def generate_captcha() -> dict[str, str]:
    """生成一道简单数学题，返回题目和签名令牌。"""

    a = secrets.randbelow(90) + 10
    b = secrets.randbelow(90) + 10
    op = secrets.choice(["+", "-"])
    if op == "-":
        a, b = max(a, b), min(a, b)
    answer = a + b if op == "+" else a - b
    question = f"{a} {op} {b} = ?"

    ts = str(int(time.time()))
    payload = f"{answer}:{ts}"
    sig = hmac.new(_get_captcha_secret(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    token = f"{payload}:{sig}"

    return {"question": question, "token": token}


def verify_captcha(token: str, answer: str) -> None:
    """校验验证码。失败时抛出 400。"""

    try:
        parts = token.split(":")
        if len(parts) != 3:
            raise ValueError
        correct_answer_str, ts_str, sig = parts
        payload = f"{correct_answer_str}:{ts_str}"
        expected_sig = hmac.new(_get_captcha_secret(), payload.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError
        ts = int(ts_str)
        if time.time() - ts > _TTL:
            raise ValueError
        if str(answer).strip() != correct_answer_str:
            raise ValueError
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )
