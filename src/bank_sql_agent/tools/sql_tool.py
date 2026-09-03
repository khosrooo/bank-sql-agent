"""
ابزار (Tool) اجرای SQL روی دیتابیس.

این تنها بخشی است که واقعاً به یک سیستم بیرونی (دیتابیس) وصل می‌شود، پس
به‌عنوان یک @tool واقعی تعریف شده. توجه: این تابع مستقیماً و به‌صورت
قطعی از داخل گره‌های گراف صدا زده می‌شود، نه اینکه به یک LLM برای
تصمیم‌گیری خودکار داده شود — همان درسی که از نسخه‌ی create_agent قبلی
گرفتیم: تصمیم «کِی SQL اجرا شود» باید دست کد باشد، نه مدل.
"""

from langchain_core.tools import tool
from sqlalchemy.exc import SQLAlchemyError

from ..database import db


@tool
def execute_sql_tool(query: str) -> dict:
    """اجرای یک کوئری SQL روی دیتابیس بانک و بازگرداندن وضعیت + نتیجه یا پیام خطا."""
    try:
        results = db.run(query)
        return {"status": "success", "data": results}
    except SQLAlchemyError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_sql(query: str) -> dict:
    return execute_sql_tool.invoke({"query": query})
