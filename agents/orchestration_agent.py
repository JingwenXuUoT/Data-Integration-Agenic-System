import os
import sys
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.rag_agent import run_rag_agent
from agents.sql_agent import run_sql_agent

load_dotenv()


class AgentState(TypedDict):
    query: str
    route: Literal["rag", "sql"]
    answer: str


_ROUTER_PROMPT = """You are a query router. Classify the user query into exactly one category:
- "sql": questions about customers, names, emails, ages, or specific data records
- "rag": questions about policies, returns, shipping, privacy, or general document content

Respond with only the single word: sql or rag

Query: {query}"""


def _router_node(state: AgentState) -> AgentState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke(_ROUTER_PROMPT.format(query=state["query"]))
    route = response.content.strip().lower()
    state["route"] = "sql" if route == "sql" else "rag"
    return state


def _rag_node(state: AgentState) -> AgentState:
    state["answer"] = run_rag_agent(state["query"])
    return state


def _sql_node(state: AgentState) -> AgentState:
    state["answer"] = run_sql_agent(state["query"])
    return state


def _pick_route(state: AgentState) -> Literal["rag", "sql"]:
    return state["route"]


_graph = StateGraph(AgentState)
_graph.add_node("router", _router_node)
_graph.add_node("rag", _rag_node)
_graph.add_node("sql", _sql_node)
_graph.add_edge(START, "router")
_graph.add_conditional_edges("router", _pick_route, {"rag": "rag", "sql": "sql"})
_graph.add_edge("rag", END)
_graph.add_edge("sql", END)
_runnable = _graph.compile()


def run_orchestrator(query: str) -> str:
    result = _runnable.invoke({"query": query, "route": "rag", "answer": ""})
    return result["answer"]
