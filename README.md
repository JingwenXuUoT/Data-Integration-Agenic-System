# Data Interaction Agent

An AI agent that answers questions about policy documents and customer data using LangChain, ChromaDB, and OpenAI.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key** — add your OpenAI key to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

## Run

1. **Start the agent backend**
   ```bash
   python mcp_server.py
   ```

2. **Open the UI**
   ```bash
   streamlit run ui/app.py
   ```
   > First-time Streamlit users will be prompted for an email address.

   - **Policy documents** — upload any PDF via the sidebar; it is indexed automatically and immediately searchable.
   - **Customer database** — created and seeded with sample data automatically on the first customer query.

## Project Structure

```
data/                    — PDF policy documents (uploaded via UI)
db/
  vector_db.py           — PDF ingestion, chunking, embedding, and ChromaDB persistence
  structured_db.py       — SQLite schema + seed data; auto-initializes on first use
chroma_db/               — Persistent vector store (generated, do not commit)
agents/
  rag_agent.py           — Retrieval-augmented Q&A over policy documents
  sql_agent.py           — Natural-language queries over the customer database
  orchestration_agent.py — LangGraph router that dispatches to the right agent
ui/
  app.py                 — Streamlit chat interface with PDF upload sidebar
tests/
  test_agents.py         — Integration tests for RAG and SQL agents
mcp_server.py            — FastMCP server exposing agent tools over HTTP
```

## Video Demo
https://www.loom.com/share/7539e8509f7c4600b78fba3082fd69fd