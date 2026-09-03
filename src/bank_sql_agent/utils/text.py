"""
توابع کمکیِ عمومی برای پردازش متن (مشترک بین چند زنجیره).
"""

import re


def _clean_sql(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```sql", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text.strip().rstrip(";").strip() + ";"
