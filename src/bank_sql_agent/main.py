"""
حلقه‌ی تعاملی (while) خط‌فرمان با لاگ فایل.
"""

import sys
import datetime

from .ui import C, print_code_block, stage, typewriter_print, TeeLogger
from .graph import run_text_to_sql_agent


def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"sql_agent_log_{timestamp}.txt"
    log_file = open(log_filename, "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = TeeLogger(original_stdout, log_file)

    try:
        print(f"{C.BOLD}{C.CYAN}")
        print("=" * 70)
        print("🏦  دستیار هوشمند بانک | Text-to-SQL Agent (LangGraph)")
        print("=" * 70)
        print(C.RESET)
        print(f"{C.DIM}برای خروج بنویسید: 'خروج' یا 'exit'{C.RESET}")

        while True:
            try:
                user_question = input(f"\n{C.BOLD}{C.BLUE}💬 سوال شما: {C.RESET}").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{C.CYAN}👋 خداحافظ!{C.RESET}")
                break

            if not user_question:
                continue
            if user_question.lower() in {"خروج", "exit", "quit"}:
                print(f"{C.CYAN}👋 خداحافظ!{C.RESET}")
                break

            print()
            try:
                final_state = run_text_to_sql_agent(user_question)
            except Exception as e:
                # لایه‌ی آخرِ آخر: حتی اگر خطایی کاملاً غیرمنتظره (نه فقط از
                # مدل) رخ دهد، برنامه نباید بمیرد؛ فقط این سوال را رد می‌کنیم.
                stage("💥", f"خطای غیرمنتظره: {type(e).__name__} — {e}", C.RED)
                print(f"{C.BOLD}🤖 پاسخ: {C.RESET}", end="")
                typewriter_print("متأسفانه یه خطای غیرمنتظره پیش اومد. لطفاً دوباره امتحان کنید. 🙏", color=C.RED)
                print(f"{C.DIM}{'-' * 70}{C.RESET}")
                continue

            final_sql = final_state.get("final_sql")
            if final_sql:
                print(f"\n{C.DIM}📄 کوئری نهایی مورد استفاده:{C.RESET}")
                print_code_block(final_sql)

            print(f"{C.DIM}{'-' * 70}{C.RESET}")

    finally:
        sys.stdout = original_stdout
        log_file.close()
        original_stdout.write(f"\n✅ تمام مکالمات با موفقیت در فایل '{log_filename}' ذخیره شد.\n")


if __name__ == "__main__":
    main()
