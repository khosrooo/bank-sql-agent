"""
ارورهندلینگ فراخوانی‌های مدل.

گاهی سرویس مدل (چه OpenAI-compatible، چه Ollama محلی) موقتاً خطا می‌دهد —
مثلاً محدودیت نرخ درخواست (429) یا قطعی شبکه‌ی لحظه‌ای. بدون این لایه، هر
کدام از این خطاها مستقیم تا بالای برنامه بالا می‌آید و کل حلقه‌ی تعاملی را
می‌کشد. call_with_retries چند بار با فاصله‌ی زمانی افزایشی دوباره تلاش
می‌کند؛ اگر همه‌ی تلاش‌ها شکست بخورد، آخرین خطا را دوباره raise می‌کند تا
لایه‌ی بالاتر آن را به یک پیام دوستانه تبدیل کند.
"""

import time
from typing import Optional

from ..ui import stage, C

MAX_LLM_RETRIES = 3
RETRY_BASE_DELAY_SECONDS = 2.0


def call_with_retries(
    fn,
    *args,
    max_retries: int = MAX_LLM_RETRIES,
    base_delay: float = RETRY_BASE_DELAY_SECONDS,
    **kwargs,
):
    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_error = e
            stage(
                "⚠️",
                f"خطا در ارتباط با مدل (تلاش {attempt} از {max_retries}): {type(e).__name__} — {e}",
                C.YELLOW,
            )
            if attempt < max_retries:
                wait_seconds = base_delay * attempt
                stage("⏳", f"{wait_seconds:.0f} ثانیه صبر می‌کنیم و دوباره تلاش می‌کنیم...", C.YELLOW)
                time.sleep(wait_seconds)
    raise last_error
