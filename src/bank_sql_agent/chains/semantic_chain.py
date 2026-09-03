"""
زنجیره‌ی بررسی + اصلاح معنایی (یک فراخوانی، بدون لوپ).
"""

import json
import re
from typing import Optional

from langchain_core.output_parsers import StrOutputParser

from ..llm import llm
from ..database import SCHEMA_TEXT
from ..prompts import semantic_prompt
from ..utils import _clean_sql, call_with_retries
from ..ui import stage, C

semantic_chain = semantic_prompt | llm | StrOutputParser()

MAX_RESULT_CHARS_FOR_SEMANTIC_CHECK = 1500


def _parse_semantic_json(raw: str) -> Optional[dict]:
    raw = raw.strip()
    raw = re.sub(r"^```json", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"^```", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def reflect_and_fix_semantic_issue(
    user_question: str, current_sql: str, results: Optional[str]
) -> Optional[str]:
    """یک فراخوانی مدل: هم تشخیص می‌دهد هم (در صورت لزوم) اصلاح می‌کند. بدون لوپ."""
    result_text = results.strip() if results else ""
    if len(result_text) > MAX_RESULT_CHARS_FOR_SEMANTIC_CHECK:
        result_text = result_text[:MAX_RESULT_CHARS_FOR_SEMANTIC_CHECK] + " ...(بریده‌شده)"
    if result_text == "":
        result_text = "(خروجی کاملاً خالی بود)"

    raw = call_with_retries(semantic_chain.invoke, {
        "schema": SCHEMA_TEXT,
        "question": user_question,
        "sql": current_sql,
        "result": result_text,
    })

    parsed = _parse_semantic_json(raw)
    if parsed is None:
        stage("⚠️", "خروجی بررسی معنایی قابل‌تفسیر نبود؛ از این مرحله صرف‌نظر شد", C.YELLOW)
        return None

    if parsed.get("has_issue") and parsed.get("corrected_sql"):
        stage("💡", f"دلیل تشخیص: {parsed.get('reason', '')}", C.MAGENTA)
        return _clean_sql(parsed["corrected_sql"])

    return None
