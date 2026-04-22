import sys
import os
import asyncio
import streamlit as st
from fastmcp import Client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.vector_db import DATA_DIR

MCP_URL = "http://localhost:8000/mcp"

st.set_page_config(page_title="Policy & Data Agent", page_icon="🤖", initial_sidebar_state="expanded")
st.title("Policy & Data Agent")
st.caption("Ask about company policies or customer data")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = set()

# ── Sidebar: document upload ──────────────────────────────────────────────────
with st.sidebar:
    st.header("Upload Policy Document")
    st.caption("Upload a PDF to make it searchable in the chat.")
    uploaded = st.file_uploader("Choose a PDF file", type=["pdf"])

    async def _index_mcp(filename: str) -> str:
        async with Client(MCP_URL) as client:
            result = await client.call_tool("index_document", {"filename": filename})
            return result.content[0].text

    async def _delete_mcp(filename: str) -> str:
        async with Client(MCP_URL) as client:
            result = await client.call_tool("delete_document", {"filename": filename})
            return result.content[0].text

    # Detect removed file and purge from index + chat history
    current_name = uploaded.name if uploaded else None
    for fname in list(st.session_state.indexed_files):
        if fname != current_name:
            with st.spinner(f"Removing '{fname}' from index…"):
                asyncio.run(_delete_mcp(fname))
            st.session_state.indexed_files.discard(fname)
            st.session_state.messages.clear()
            st.info(f"'{fname}' removed. Chat history cleared.")

    if uploaded and uploaded.name not in st.session_state.indexed_files:
        save_path = os.path.join(DATA_DIR, uploaded.name)
        with open(save_path, "wb") as f:
            f.write(uploaded.getbuffer())

        with st.spinner(f"Indexing {uploaded.name}…"):
            status = asyncio.run(_index_mcp(uploaded.name))

        st.session_state.indexed_files.add(uploaded.name)
        st.success(status)

    if st.session_state.indexed_files:
        st.divider()
        st.markdown("**Indexed this session:**")
        for name in st.session_state.indexed_files:
            st.markdown(f"- {name}")

# ── Chat ──────────────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


async def _call_mcp(user_query: str) -> str:
    async with Client(MCP_URL) as client:
        result = await client.call_tool("query", {"user_query": user_query})
        return result.content[0].text


user_input = st.chat_input("Ask a question…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.spinner("Thinking…"):
        answer = asyncio.run(_call_mcp(user_input))

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
