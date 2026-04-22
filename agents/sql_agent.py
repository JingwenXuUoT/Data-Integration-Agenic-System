import os
import sys
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.structured_db import init_db

load_dotenv()

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "customer.db")


def run_sql_agent(query: str) -> str:
    init_db()
    db = SQLDatabase.from_uri(f"sqlite:///{_DB_PATH}")
    agent = create_sql_agent(
        llm=ChatOpenAI(model="gpt-4o-mini"),
        db=db,
        verbose=False,
    )
    return agent.invoke(query)["output"]
