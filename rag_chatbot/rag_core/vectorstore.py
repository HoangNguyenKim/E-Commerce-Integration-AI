"""
Tạo và load ChromaDB vectorstore theo config.
Dùng Google Gemini cho embedding (GOOGLE_API_KEY trong .env).
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata

from .config import get_vectorstore_config


def _get_embedding():
    load_dotenv()
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("Cần thiết lập GOOGLE_API_KEY (hoặc GEMINI_API_KEY) trong file .env")
    return GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")


def build_vectorstore(documents: list, config: dict | None = None, persist_dir: str | None = None):
    """
    Tạo ChromaDB từ danh sách Document và lưu vào thư mục persist.
    """
    if config is None and persist_dir is None:
        persist_dir = "chromadb"
    if config is not None:
        vs_config = get_vectorstore_config(config)
        persist_dir = persist_dir or vs_config.get("persist_directory", "chromadb")
    simple_docs = filter_complex_metadata(documents)
    embedding = _get_embedding()
    chroma = Chroma.from_documents(
        documents=simple_docs,
        embedding=embedding,
        persist_directory=persist_dir,
    )
    return chroma


def get_vectorstore(config: dict | None = None, persist_dir: str | None = None):
    """Load vectorstore có sẵn từ thư mục persist."""
    if config is not None:
        vs_config = get_vectorstore_config(config)
        persist_dir = persist_dir or vs_config.get("persist_directory", "chromadb")
    else:
        persist_dir = persist_dir or "chromadb"
    embedding = _get_embedding()
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embedding,
    )
