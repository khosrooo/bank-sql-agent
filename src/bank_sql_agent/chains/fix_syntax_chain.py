"""
زنجیره‌ی اصلاح خطای سینتکسی.
"""

from langchain_core.output_parsers import StrOutputParser

from ..llm import llm
from ..database import SCHEMA_TEXT
from ..prompts import fix_syntax_prompt
from ..utils import _clean_sql, call_with_retries

fix_syntax_chain = fix_syntax_prompt | llm | StrOutputParser()


def fix_sql_syntax(current_sql: str, db_error_message: str) -> str:
    raw = call_with_retries(fix_syntax_chain.invoke, {
        "schema": SCHEMA_TEXT,
        "sql": current_sql,
        "error": db_error_message,
    })
    return _clean_sql(raw)
