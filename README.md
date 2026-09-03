# Bank SQL Agent

دستیار هوشمند Text-to-SQL برای یک دیتابیس بانکی، پیاده‌سازی‌شده با **LangGraph**.
سوال فارسیِ کاربر را به کوئری SQL تبدیل می‌کند، در صورت خطای ساختاری تا ۳ بار
خودش را اصلاح می‌کند، نتیجه را از نظر منطقی هم یک‌بار بررسی می‌کند، و در نهایت
پاسخ را به‌صورت طبیعی و زنده (streaming) به کاربر نمایش می‌دهد.

## ساختار پروژه

```
bank-sql-agent/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── bank_database.db
└── src/
    └── bank_sql_agent/
        ├── __init__.py        # نسخه‌ی پکیج
        ├── __main__.py        # نقطه‌ی ورود (python -m bank_sql_agent)
        ├── main.py            # حلقه‌ی تعاملی خط‌فرمان + لاگ فایل
        ├── config.py          # بارگذاری .env و مسیر دیتابیس
        ├── database.py        # اتصال SQLDatabase + متن اسکیما
        ├── llm.py             # راه‌اندازی مدل زبانی
        ├── prompts/           # پرامپت‌های هر مرحله (تولید/اصلاح/بررسی/پاسخ)
        ├── chains/            # زنجیره‌های LangChain متناظر با هر پرامپت
        ├── tools/              # ابزار (Tool) اجرای SQL روی دیتابیس
        ├── graph/              # State + گره‌ها + ساخت StateGraph
        ├── ui/                 # رنگ/آیکون ترمینال + لاگر Tee
        └── utils/              # توابع کمکیِ مشترک (پاک‌سازی خروجی SQL)
```

## معماری ایجنت (LangGraph)

```
generate_sql → execute_sql ⇄ fix_syntax   (حداکثر ۳ بار، حلقه‌ی واقعی)
                    │
                    ▼ (وقتی موفق شد)
              semantic_check              (فقط یک‌بار، بدون یال برگشتی)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  semantic_execute          finalize
        │                       │
        └───────────┬───────────┘
                     ▼
                  answer (پاسخ نهایی، Streaming)
```

- **مسیر سینتکسی** یک حلقه‌ی واقعیِ گراف است (`execute_sql ⇄ fix_syntax`) و
  با شمارنده‌ی `attempt` در برابر `max_syntactic_attempts` کنترل می‌شود.
- **مسیر معنایی** هیچ یال برگشتی ندارد — از نظر توپولوژی گراف اصلاً امکان
  لوپ‌شدن ندارد، نه فقط با یک شرط کدی.
- تنها ابزار (`@tool`) پروژه، اجرای SQL روی دیتابیس است؛ مستقیم و قطعی از
  کد صدا زده می‌شود، نه توسط تصمیم خودکار مدل.

## نصب و اجرا

```bash
# ۱) نصب وابستگی‌ها
pip install -r requirements.txt

# ۲) کپی و تنظیم متغیرهای محیطی (در ریشه‌ی پروژه)
cp .env.example .env
# سپس OPENAI_API_KEY و OPENAI_API_BASE را در .env مقداردهی کنید

# ۳) دیتابیس bank_database.db را در ریشه‌ی پروژه (کنار پوشه‌ی src/) قرار دهید

# ۴) اجرا — از داخل پوشه‌ی src (نیازی به نصب/pyproject.toml نیست)
cd src
python -m bank_sql_agent
```

برای خروج از حلقه‌ی تعاملی، کافی است بنویسید: `خروج` یا `exit`.

هر جلسه یک فایل لاگ به‌صورت `sql_agent_log_YYYYMMDD_HHMMSS.txt` در همان
مسیر اجرا ذخیره می‌شود (بدون کدهای رنگیِ ANSI، برای خوانایی در ادیتور).

## پیکربندی مدل

پیش‌فرض پروژه از یک endpoint سازگار با OpenAI (مثلاً پراکسیِ Gemini) استفاده
می‌کند؛ آدرس و کلید آن در `.env` تنظیم می‌شود (`llm.py` → `init_llm`).

## دیتابیس

فایل `bank_database.db` باید در ریشه‌ی پروژه (کنار پوشه‌ی `src/`) قرار داشته
باشد. جداول اصلی: `Customer`، `Account`، `"Transaction"`، `Transfer`
(جزئیات کامل روابط در `database.py` → `get_schema_text`).

## لایسنس

MIT — به فایل [LICENSE](./LICENSE) مراجعه کنید.
