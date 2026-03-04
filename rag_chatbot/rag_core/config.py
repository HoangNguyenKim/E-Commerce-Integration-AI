"""
Đọc và trả về cấu hình RAG từ file JSON.
Đường dẫn config: tham số config_path, hoặc RAG_CONFIG_PATH, hoặc config.json trong thư mục gốc chatbot.
"""
import os
import json


def load_config(config_path: str | None = None) -> dict:
    path = config_path or os.environ.get("RAG_CONFIG_PATH")
    if not path:
        # Mặc định: config.json cùng thư mục với rag_chatbot
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "config.json")
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Không tìm thấy file cấu hình: {path}. "
            "Hãy copy config.example.json thành config.json và chỉnh sửa."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_data_config(config: dict) -> dict:
    return config.get("data", {})


def get_vectorstore_config(config: dict) -> dict:
    return config.get("vectorstore", {})


def get_prompt_config(config: dict) -> dict:
    return config.get("prompt", {})


def get_llm_config(config: dict) -> dict:
    return config.get("llm", {})


def get_retrieval_config(config: dict) -> dict:
    return config.get("retrieval", {})
