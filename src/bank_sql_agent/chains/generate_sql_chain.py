"""
زنجیره‌ی تولید اولیه‌ی SQL.
"""

from langchain_core.output_parsers import StrOutputParser

from ..llm import llm
from ..database import SCHEMA_TEXT
from ..prompts import generate_prompt, FEW_SHOT_EXAMPLES
from ..utils import _clean_sql, call_with_retries

generate_sql_chain = generate_prompt | llm | StrOutputParser()


def generate_initial_sql(user_question: str) -> str:
    raw = call_with_retries(generate_sql_chain.invoke, {
        "schema": SCHEMA_TEXT,
        "examples": FEW_SHOT_EXAMPLES,
        "question": user_question,
    })
    return _clean_sql(raw)
