# RAG core - module RAG tổng quát (đổi lĩnh vực/database chỉ qua config)
from .config import load_config
from .data_loader import load_documents_from_config
from .vectorstore import build_vectorstore, get_vectorstore
from .chain import get_rag_chain, query_rag, get_rag_tool

__all__ = [
    "load_config",
    "load_documents_from_config",
    "build_vectorstore",
    "get_vectorstore",
    "get_rag_chain",
    "query_rag",
    "get_rag_tool",
]
