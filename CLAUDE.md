# CLAUDE.md — Project Context for Claude Code

## What this project is
A local AI agent system that answers natural-language questions about policy documents (RAG) and customer data (SQL). Users interact via a Streamlit chat UI; the backend runs as a FastMCP server.

## Stack
- **LLM**: OpenAI `gpt-4o-mini` (all agents)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Vector store**: ChromaDB (persisted to `chroma_db/`)
- **Relational DB**: SQLite (`customer.db`)
- **Orchestration**: LangGraph state machine
- **Backend**: FastMCP server (`mcp_server.py`) on `http://localhost:8000`
- **UI**: Streamlit (`ui/app.py`)

## Architecture decisions

### Agent routing
`orchestration_agent.py` uses a LangGraph router that classifies every query as `"rag"` or `"sql"` via a zero-shot GPT-4o-mini call, then dispatches to the appropriate agent.

### RAG agent (`agents/rag_agent.py`)
- Before calling the LLM, checks two things in order:
  1. `len(vs) == 0` → returns a "no documents uploaded" message (no LLM call)
  2. `similarity_search_with_score` min score > `_RELEVANCE_THRESHOLD` (0.7) → returns a "not found, please upload" message
- `similarity_search_with_score` returns cosine **distance** — lower = more similar. Threshold 0.7 is tunable.

### PDF upload/delete flow
- **Upload**: UI saves file to `data/`, calls MCP tool `index_document(filename)` → `index_single_pdf(filepath)` adds chunks to existing ChromaDB incrementally (does not rebuild).
- **Delete**: UI detects file removal via `st.session_state.indexed_files`, calls MCP tool `delete_document(filename)` → `delete_single_pdf(filepath)` uses `vs.get(where={"source": filepath})` to find IDs then `vs.delete(ids=...)`. Also deletes the file from `data/` and clears the chat history.
- Never use `load_and_index_pdfs()` (full rebuild) for incremental updates — use `index_single_pdf` / `delete_single_pdf`.

### Customer DB (`db/structured_db.py`)
- `init_db()` is idempotent: `CREATE TABLE IF NOT EXISTS`, inserts seed rows only if table is empty.
- `sql_agent.py` calls `init_db()` on every invocation — safe no-op if DB already exists.
- Seed data: Alice (30), Bob (25), Carol (28), Ema (32) with support tickets.
- To fully reset the DB, delete `customer.db` and run `python db/structured_db.py`.

### MCP tools (in `mcp_server.py`)
| Tool | Purpose |
|---|---|
| `query(user_query)` | Routes to orchestration agent |
| `index_document(filename)` | Indexes a PDF already saved to `data/` |
| `delete_document(filename)` | Purges a PDF's chunks from ChromaDB + deletes file |

### UI (`ui/app.py`)
- Sidebar is expanded by default (`initial_sidebar_state="expanded"`).
- Tracks uploaded files in `st.session_state.indexed_files` (a `set`) to prevent re-indexing on reruns.
- Clears `st.session_state.messages` when a document is removed, to prevent stale context.
- MCP responses accessed via `result.content[0].text` (not `result[0].text` or `["text"]`).

## Project rules
- **Do not use pytest** — tests run directly: `python tests/test_agents.py` from project root.
- **Do not commit `chroma_db/`** — it is generated and gitignored.
- **Do not commit `customer.db`** — auto-created at runtime.
- Test assertions use keyword/substring matching (not exact match) because LLM output is free-form.
- The out-of-scope RAG test (`rag_out_of_scope`) uses OR logic and is inherently flaky — expected.
- Keep all agent functions as simple `str → str` callables; orchestration is LangGraph's job.
