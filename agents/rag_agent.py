import os
import sys
from dotenv import load_dotenv
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.vector_db import get_vectorstore

load_dotenv()

_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Use the following context to answer the question. "
        "If you don't know the answer, say you don't know.\n\n"
        "Context: {context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    ),
)

_RELEVANCE_THRESHOLD = 0.7  # cosine distance; lower = more similar

_NO_POLICY_MSG = (
    "No policy documents have been uploaded yet. "
    "Please upload a policy PDF via the sidebar to get started."
)
_NO_MATCH_MSG = (
    "No relevant policy was found for your question. "
    "Please upload the related policy document to proceed."
)


def run_rag_agent(query: str) -> str:
    vs = get_vectorstore()

    if len(vs) == 0:
        return _NO_POLICY_MSG

    docs_and_scores = vs.similarity_search_with_score(query, k=3)
    if not docs_and_scores or min(score for _, score in docs_and_scores) > _RELEVANCE_THRESHOLD:
        return _NO_MATCH_MSG

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4o-mini"),
        retriever=vs.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": _PROMPT},
    )
    return chain.invoke({"query": query})["result"]
