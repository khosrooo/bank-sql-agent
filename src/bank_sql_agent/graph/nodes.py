"""
گره‌های (nodes) گراف و توابع مسیریابی شرطی (conditional edges).
"""

from ..chains import (
    generate_initial_sql,
    fix_sql_syntax,
    reflect_and_fix_semantic_issue,
    stream_user_answer,
)
from ..tools import run_sql
from ..ui import stage, print_code_block, typewriter_print, C
from .state import AgentState


def node_generate_sql(state: AgentState) -> dict:
    stage("🧠", "در حال تحلیل سوال و ساخت کوئری بانکی...", C.CYAN)
    sql = generate_initial_sql(state["user_question"])
    print_code_block(sql)
    return {"current_sql": sql, "attempt": 0}


def node_execute_sql(state: AgentState) -> dict:
    attempt = state.get("attempt", 0) + 1
    stage("⚙️", f"اجرای کوئری روی دیتابیس — تلاش {attempt} از {state['max_syntactic_attempts']}", C.CYAN)
    result = run_sql(state["current_sql"])

    if result["status"] != "error":
        stage("✅", "کوئری بدون خطای ساختاری اجرا شد", C.GREEN)
        return {"attempt": attempt, "db_status": "success", "db_data": result["data"], "db_error": None}

    stage("🚧", "خطای ساختاری شناسایی شد", C.YELLOW)
    print_code_block(result["message"], color=C.YELLOW)
    return {"attempt": attempt, "db_status": "error", "db_error": result["message"], "db_data": None}


def route_after_execute(state: AgentState) -> str:
    if state["db_status"] != "error":
        return "semantic_check"
    if state["attempt"] >= state["max_syntactic_attempts"]:
        return "syntax_failed"
    return "fix_syntax"


def node_fix_syntax(state: AgentState) -> dict:
    stage("🔧", "در حال اصلاح ساختار کوئری...", C.YELLOW)
    fixed = fix_sql_syntax(state["current_sql"], state["db_error"])
    print_code_block(fixed)
    return {"current_sql": fixed}


def node_syntax_failed(state: AgentState) -> dict:
    stage("❌", "پس از حداکثر تعداد تلاش، کوئری سالمی تولید نشد", C.RED)
    return {
        "status": "failed",
        "payload": "متاسفانه پس از چند بار تلاش نتونستم یک کوئری درست برای این سوال بسازم. "
                   "می‌شه لطفاً واضح‌تر یا با جزئیات بیشتر بپرسید؟ 🙏",
        "final_sql": None,
    }


def node_semantic_check(state: AgentState) -> dict:
    stage("🔎", "در حال بررسی منطقی بودن نتیجه...", C.MAGENTA)
    corrected = reflect_and_fix_semantic_issue(state["user_question"], state["current_sql"], state["db_data"])
    if not corrected:
        stage("👍", "نتیجه از نظر منطقی درست به نظر می‌رسد", C.GREEN)
    return {"semantic_corrected_sql": corrected}


def route_after_semantic(state: AgentState) -> str:
    return "semantic_execute" if state.get("semantic_corrected_sql") else "finalize"


def node_semantic_execute(state: AgentState) -> dict:
    stage("🩹", "مشکل منطقی پیدا شد؛ در حال اصلاح و اجرای مجدد...", C.YELLOW)
    sql = state["semantic_corrected_sql"]
    print_code_block(sql)
    result = run_sql(sql)

    if result["status"] == "error":
        stage("❌", "اصلاح معنایی به یک خطای ساختاری جدید منجر شد", C.RED)
        return {
            "current_sql": sql,
            "status": "error",
            "payload": "در تلاش برای اصلاح خودکار درخواست، مشکلی پیش اومد. ممکنه سوال رو یه‌جور دیگه بپرسید؟ 🙏",
            "final_sql": sql,
        }

    stage("✅", "کوئری اصلاح‌شده با موفقیت اجرا شد", C.GREEN)
    return {"current_sql": sql, "db_data": result["data"], "db_status": "success"}


def route_after_semantic_execute(state: AgentState) -> str:
    return "answer" if state.get("status") == "error" else "finalize"


def node_finalize(state: AgentState) -> dict:
    data = state.get("db_data")
    if not data or data.strip() == "":
        stage("🔍", "نتیجه‌ای برای این درخواست پیدا نشد", C.YELLOW)
        return {"status": "empty", "payload": "نتیجه‌ای برای درخواست شما پیدا نشد. 🤷‍♂️", "final_sql": state["current_sql"]}
    return {"status": "success", "payload": data, "final_sql": state["current_sql"]}


def node_answer(state: AgentState) -> dict:
    status = state["status"]

    if status == "success":
        stage("✨", "در حال آماده‌سازی پاسخ نهایی...", C.MAGENTA)
        print(f"{C.BOLD}🤖 پاسخ: {C.RESET}", end="")
        full = stream_user_answer(state["user_question"], state["payload"])
        return {"final_answer": full}

    print(f"{C.BOLD}🤖 پاسخ: {C.RESET}", end="")
    color = C.YELLOW if status == "empty" else C.RED
    typewriter_print(state["payload"], color=color)
    return {"final_answer": state["payload"]}
