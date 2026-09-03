"""
اتصال به دیتابیس SQLite بانک و آماده‌سازی متن اسکیما برای تزریق در پرامپت‌ها.
"""

from langchain_community.utilities import SQLDatabase

from .config import DB_PATH

db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")


def get_schema_text() -> str:
    raw = db.get_table_info()
    notes = """
روابط بین جداول:
- Customer (مشتری) -> Account (حساب): یک به چند
- Account (حساب) -> "Transaction" (تراکنش): یک به چند
- Account (حساب) -> Transfer (انتقال): دو رابطه (FromAccountID و ToAccountID هر دو به Account.AccountID اشاره دارند)

نکات حیاتی سینتکسی SQLite:
- نام جدول Transaction باید همیشه داخل کوتیشن نوشته شود: "Transaction" (چون کلمه‌ی رزرو شده است)
- AccountType فقط 'Savings' یا 'Checking' است
- Status فقط 'Active' یا 'Inactive' است
- برای فیلتر بر اساس شماره حساب (رشته‌ای مثل 'ACC100001') باید ابتدا با JOIN به Account رسید و روی
  ستون AccountNumber فیلتر کرد؛ FromAccountID/ToAccountID در Transfer عدد (کلید خارجی) هستند، نه رشته.
"""
    return raw + notes


SCHEMA_TEXT = get_schema_text()
