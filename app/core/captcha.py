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


def _hash_answer(answer: int) -> str:
    """对验证码答案做 SHA-256，避免答案明文出现在 token 中。

    token 仍是 `哈希:时间戳:签名` 的形式，但即便被读出也无法还原出答案。
    """

    return hashlib.sha256(f"answer:{answer}".encode()).hexdigest()


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
    # 用答案哈希替代明文答案，配合 HMAC 签名防篡改
    payload = f"{_hash_answer(answer)}:{ts}"
    sig = hmac.new(_get_captcha_secret(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    token = f"{payload}:{sig}"

    return {"question": question, "token": token}


def verify_captcha(token: str, answer: str) -> None:
    """校验验证码。失败时抛出 400。"""

    try:
        parts = token.split(":")
        if len(parts) != 3:
            raise ValueError
        expected_hash, ts_str, sig = parts
        payload = f"{expected_hash}:{ts_str}"
        expected_sig = hmac.new(_get_captcha_secret(), payload.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError
        ts = int(ts_str)
        if time.time() - ts > _TTL:
            raise ValueError
        # 对用户提交的答案同样哈希后比对，全程不接触明文答案
        try:
            answer_int = int(str(answer).strip())
        except (TypeError, ValueError):
            raise ValueError
        if not hmac.compare_digest(_hash_answer(answer_int), expected_hash):
            raise ValueError
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )
