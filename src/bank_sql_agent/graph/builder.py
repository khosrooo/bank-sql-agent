"""
ساخت گراف (StateGraph) و تابع اجرای آن برای یک سوال.
"""

from langgraph.graph import StateGraph, START, END

from .state import AgentState
from ..ui import C, stage, typewriter_print
from .nodes import (
    node_generate_sql,
    node_execute_sql,
    node_fix_syntax,
    node_syntax_failed,
    node_semantic_check,
    node_semantic_execute,
    node_finalize,
    node_answer,
    route_after_execute,
    route_after_semantic,
    route_after_semantic_execute,
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("generate_sql", node_generate_sql)
    graph.add_node("execute_sql", node_execute_sql)
    graph.add_node("fix_syntax", node_fix_syntax)
    graph.add_node("syntax_failed", node_syntax_failed)
    graph.add_node("semantic_check", node_semantic_check)
    graph.add_node("semantic_execute", node_semantic_execute)
    graph.add_node("finalize", node_finalize)
    graph.add_node("answer", node_answer)

    graph.add_edge(START, "generate_sql")
    graph.add_edge("generate_sql", "execute_sql")

    # مسیر سینتکسی: حلقه‌ی واقعیِ execute_sql <-> fix_syntax، حداکثر ۳ بار
    graph.add_conditional_edges(
        "execute_sql",
        route_after_execute,
        {
            "semantic_check": "semantic_check",
            "fix_syntax": "fix_syntax",
            "syntax_failed": "syntax_failed",
        },
    )
    graph.add_edge("fix_syntax", "execute_sql")
    graph.add_edge("syntax_failed", "answer")

    # مسیر معنایی: هیچ یال برگشتی وجود ندارد -> فیزیکاً فقط یک‌بار قابل عبور است
    graph.add_conditional_edges(
        "semantic_check",
        route_after_semantic,
        {"semantic_execute": "semantic_execute", "finalize": "finalize"},
    )
    graph.add_conditional_edges(
        "semantic_execute",
        route_after_semantic_execute,
        {"answer": "answer", "finalize": "finalize"},
    )

    graph.add_edge("finalize", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


agent_graph = build_graph()


def run_text_to_sql_agent(user_question: str, max_syntactic_attempts: int = 3) -> AgentState:
    initial_state: AgentState = {
        "user_question": user_question,
        "current_sql": "",
        "attempt": 0,
        "max_syntactic_attempts": max_syntactic_attempts,
        "db_status": "",
        "db_data": None,
        "db_error": None,
        "semantic_corrected_sql": None,
        "status": "",
        "payload": "",
        "final_sql": None,
        "final_answer": "",
    }
    try:
        return agent_graph.invoke(initial_state, {"recursion_limit": 50})
    except Exception as e:
        # لایه‌ی محافظتی نهایی: اگر با وجود همه‌ی retryهای داخلی، خطا همچنان
        # تا اینجا بالا آمده باشد (مثلاً قطعی طولانی سرویس مدل)، به‌جای کرش
        # کردن کل برنامه، یک پیام دوستانه چاپ می‌کنیم و کنترل را برمی‌گردانیم
        # تا main() بتواند حلقه‌ی while را ادامه دهد و سوال بعدی را بپرسد.
        stage("💥", f"پردازش این سوال با خطای غیرمنتظره متوقف شد: {type(e).__name__} — {e}", C.RED)
        payload = (
            "متأسفانه در ارتباط با سرویس هوش مصنوعی مشکلی پیش اومد که با چند بار تلاش هم "
            "برطرف نشد (احتمالاً قطعی یا محدودیت طولانی‌مدت سرویس). لطفاً چند لحظه صبر کنید "
            "و دوباره سوال‌تون رو بپرسید. 🙏"
        )
        print(f"{C.BOLD}🤖 پاسخ: {C.RESET}", end="")
        typewriter_print(payload, color=C.RED)
        return {
            "user_question": user_question,
            "current_sql": "",
            "attempt": 0,
            "max_syntactic_attempts": max_syntactic_attempts,
            "db_status": "error",
            "db_data": None,
            "db_error": str(e),
            "semantic_corrected_sql": None,
            "status": "error",
            "payload": payload,
            "final_sql": None,
            "final_answer": payload,
        }
