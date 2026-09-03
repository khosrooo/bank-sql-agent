"""
زنجیره‌ی تبدیل نتیجه به پاسخ دوستانه (Streaming).
"""

from langchain_core.output_parsers import StrOutputParser

from ..llm import llm
from ..prompts import user_answer_prompt
from ..ui import C, stage, typewriter_print
from ..utils import MAX_LLM_RETRIES, RETRY_BASE_DELAY_SECONDS

import time

user_answer_chain = user_answer_prompt | llm | StrOutputParser()


def stream_user_answer(user_question: str, sql_result: str) -> str:
    """
    استریم واقعیِ پاسخ. اگر وسط استریم (مثلاً به‌خاطر rate-limit سرویس مدل)
    خطا بخوریم، متن نیمه‌کاره را دور می‌ریزیم و از اول دوباره تلاش می‌کنیم
    (نمی‌شود یک استریم نیمه‌کاره را ادامه داد). اگر همه‌ی تلاش‌های استریم
    شکست خورد، یک تلاش آخر به‌صورت غیر-استریم می‌زنیم، و اگر آن هم شکست خورد،
    به‌جای کرش کردن برنامه، نتیجه‌ی خام SQL را مستقیم نشان می‌دهیم.
    """
    for attempt in range(1, MAX_LLM_RETRIES + 1):
        full_text = ""
        try:
            print(f"{C.GREEN}", end="", flush=True)
            for chunk in user_answer_chain.stream({
                "user_question": user_question,
                "sql_result": sql_result,
            }):
                print(chunk, end="", flush=True)
                full_text += chunk
            print(f"{C.RESET}")
            return full_text
        except Exception as e:
            print(f"{C.RESET}")
            stage(
                "⚠️",
                f"ارتباط استریم وسط پاسخ قطع شد (تلاش {attempt} از {MAX_LLM_RETRIES}): {type(e).__name__} — {e}",
                C.YELLOW,
            )
            if attempt < MAX_LLM_RETRIES:
                wait_seconds = RETRY_BASE_DELAY_SECONDS * attempt
                stage("⏳", f"{wait_seconds:.0f} ثانیه صبر می‌کنیم و از اول تلاش می‌کنیم...", C.YELLOW)
                time.sleep(wait_seconds)

    # همه‌ی تلاش‌های استریم شکست خورد؛ یک تلاش آخر بدون استریم
    stage("🔁", "تلاش نهایی به‌صورت غیر-استریم...", C.YELLOW)
    try:
        full_text = user_answer_chain.invoke({
            "user_question": user_question,
            "sql_result": sql_result,
        })
        print(f"{C.GREEN}{full_text}{C.RESET}")
        return full_text
    except Exception:
        fallback = (
            "متأسفانه ارتباط با سرویس هوش مصنوعی برای تبدیل نتیجه به پاسخ طبیعی برقرار نشد "
            "(احتمالاً محدودیت نرخ درخواست یا قطعی موقت). این هم نتیجه‌ی خامی که از دیتابیس گرفتیم:\n\n"
            f"{sql_result}"
        )
        typewriter_print(fallback, color=C.RED)
        return fallback
