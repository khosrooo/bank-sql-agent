"""
پرامپتِ تولید اولیه‌ی SQL از روی سوال فارسیِ کاربر.
"""

from langchain_core.prompts import ChatPromptTemplate

generate_prompt = ChatPromptTemplate.from_messages([
    ("system", """شما یک متخصص SQLite هستید که سوالات فارسیِ مربوط به یک دیتابیس بانکی را
به کوئری SQL معتبر تبدیل می‌کنید.

اسکیمای کامل دیتابیس:
{schema}

چند نمونه‌ی حل‌شده:
{examples}

قوانین سخت‌گیرانه:
1. فقط و فقط یک کوئری SQL معتبر SQLite برگردان؛ هیچ توضیح، عنوان یا متن اضافه ننویس.
2. کوئری را داخل بک‌تیک یا ```sql نگذار؛ متن خام SQL کافی است.
3. فقط از نام جدول‌ها و ستون‌هایی که در اسکیمای بالا آمده استفاده کن؛ هیچ نام ستونی را حدس نزن.
4. اگر سوال به شماره حساب (مثل 'ACC...') اشاره دارد، حتماً با JOIN به جدول Account برو."""),
    ("human", "سوال: {question}\nSQL:"),
])

FEW_SHOT_EXAMPLES = """
مثال ۱:
سوال: نام و نام‌خانوادگی مشتریانی که بعد از سال ۲۰۲۱ ثبت‌نام کرده‌اند را نشان بده.
SQL: SELECT FirstName, LastName FROM Customer WHERE CreatedAt > '2021-12-31';

مثال ۲:
سوال: مجموع مبالغ انتقال وجه از حساب با شماره ACC100001 چقدر است؟
SQL: SELECT SUM(t.Amount) FROM Transfer t JOIN Account a ON t.FromAccountID = a.AccountID WHERE a.AccountNumber = 'ACC100001';

مثال ۳:
سوال: حساب‌های غیرفعال را با شماره حساب و موجودی نشان بده.
SQL: SELECT AccountNumber, Balance FROM Account WHERE Status = 'Inactive';

مثال ۴:
سوال: تمام تراکنش‌های حساب با شماره ACC300002 را نشان بده.
SQL: SELECT tr.* FROM "Transaction" tr JOIN Account a ON tr.AccountID = a.AccountID WHERE a.AccountNumber = 'ACC300002';
"""
