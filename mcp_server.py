from dotenv import load_dotenv
load_dotenv()

import os
from fastmcp import FastMCP
from agents.orchestration_agent import run_orchestrator
from db.vector_db import DATA_DIR, index_single_pdf, delete_single_pdf

mcp = FastMCP("policy-agent")


@mcp.tool()
def query(user_query: str) -> str:
    """Answer questions about company policies or customer data."""
    return run_orchestrator(user_query)


@mcp.tool()
def index_document(filename: str) -> str:
    """Index a PDF that has already been saved to the data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.isfile(filepath):
        return f"Error: '{filename}' not found in the data directory."
    n = index_single_pdf(filepath)
    return f"'{filename}' indexed successfully ({n} chunks added)."


@mcp.tool()
def delete_document(filename: str) -> str:
    """Remove a PDF's chunks from ChromaDB and delete the file from data/."""
    filepath = os.path.join(DATA_DIR, filename)
    n = delete_single_pdf(filepath)
    return f"'{filename}' removed ({n} chunks deleted)."


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
