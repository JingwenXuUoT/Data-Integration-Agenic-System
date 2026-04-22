import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_BASE, "data")
CHROMA_DIR = os.path.join(_BASE, "chroma_db")

def load_and_index_pdfs():
    docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.lower().endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_DIR, filename))
            docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    print(f"Indexed {len(chunks)} chunks into {CHROMA_DIR}")
    return vectorstore


def get_vectorstore():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"},
    )


def index_single_pdf(filepath: str) -> int:
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    vs = get_vectorstore()
    vs.add_documents(chunks)
    return len(chunks)


def delete_single_pdf(filepath: str) -> int:
    vs = get_vectorstore()
    result = vs.get(where={"source": filepath})
    ids = result["ids"]
    if ids:
        vs.delete(ids=ids)
    if os.path.isfile(filepath):
        os.remove(filepath)
    return len(ids)
