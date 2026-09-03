"""
تعریف State گراف.
"""

from typing import Optional, TypedDict


class AgentState(TypedDict, total=False):
    user_question: str
    current_sql: str
    attempt: int
    max_syntactic_attempts: int
    db_status: str                 # "success" | "error"
    db_data: Optional[str]
    db_error: Optional[str]
    semantic_corrected_sql: Optional[str]
    status: str                    # "success" | "empty" | "error" | "failed"
    payload: str
    final_sql: Optional[str]
    final_answer: str
