# Bank SQL Agent

A Text-to-SQL agent for a banking database, built with **LangGraph**. Converts Persian user queries into SQL, self-corrects syntax errors up to 3 times, runs a single semantic check on the result, and streams the final answer back to the user.

## Project Structure

```text
bank-sql-agent/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── bank_database.db
└── src/
    └── bank_sql_agent/
        ├── __init__.py        # Package version
        ├── __main__.py        # Entry point (python -m bank_sql_agent)
        ├── main.py            # Interactive CLI loop + file logging
        ├── config.py          # .env loading and database path
        ├── database.py        # SQLDatabase connection + schema text
        ├── llm.py             # LLM initialization
        ├── prompts/           # Prompts for each stage (generate/fix/check/finalize)
        ├── chains/            # LangChain chains for each prompt
        ├── tools/             # SQL execution tool
        ├── graph/             # State, nodes, and StateGraph
        ├── ui/                # Terminal colors/icons + Tee logger
        └── utils/             # Shared helpers (e.g., SQL output cleanup)
```

## Agent Architecture (LangGraph)

```text
generate_sql → execute_sql ⇄ fix_syntax   (max 3 attempts, real graph loop)
                    │
                    ▼ (on success)
              semantic_check              (runs once, no back edges)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  semantic_execute          finalize
        │                       │
        └───────────┬───────────┘
                    ▼
                 answer (final response, streamed)
```

- **Syntactic path**: a real graph loop (`execute_sql` ⇄ `fix_syntax`), controlled by an `attempt` counter against `max_syntactic_attempts`.
- **Semantic path**: no back edges — the graph is topologically unable to loop at this stage.
- **Tool execution**: the only tool in the project is the SQL executor. It is called directly from code, not by the model's autonomous tool-calling.

## Installation & Usage

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment variables (in the project root)
cp .env.example .env
# Set OPENAI_API_KEY and OPENAI_API_BASE in .env

# 3. Place bank_database.db in the project root (next to src/)

# 4. Run (from inside src/ — no pyproject.toml install needed)
cd src
python -m bank_sql_agent
```

To exit the interactive loop, type `exit` or `خروج`.

Each session writes a log file named `sql_agent_log_YYYYMMDD_HHMMSS.txt` in the working directory. ANSI color codes are stripped so the log stays readable in any text editor.

## Model Configuration

The project uses an OpenAI-compatible endpoint (e.g., a Gemini proxy). Base URL and API key are set in `.env` — see `llm.py` → `init_llm`.

## Database

`bank_database.db` must be in the project root (next to `src/`).

Main tables: `Customer`, `Account`, `"Transaction"`, `Transfer`. Full schema details are in `database.py` → `get_schema_text`.