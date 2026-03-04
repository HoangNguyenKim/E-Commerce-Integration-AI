"""
Chatbot RAG: trả lời dựa trên dữ liệu đã nạp trong ChromaDB.
Cấu hình qua config.json (prompt, llm, retrieval).
Chạy từ thư mục rag_chatbot: python chat.py [đường_dẫn_config]
Hoặc từ project root: python -m rag_chatbot.chat
"""
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from rag_core import load_config, query_rag


def main():
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = os.path.join(_SCRIPT_DIR, "config.json")

    config = load_config(config_path)
    # Đường dẫn ChromaDB luôn nằm trong thư mục rag_chatbot
    if "vectorstore" not in config:
        config["vectorstore"] = {}
    rel_persist = config["vectorstore"].get("persist_directory", "chromadb")
    config["vectorstore"]["persist_directory"] = os.path.join(_SCRIPT_DIR, rel_persist)
    print("RAG Chatbot — Thoát: gõ 'exit' hoặc 'quit'\n")
    while True:
        try:
            user_input = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTạm biệt.")
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("Tạm biệt.")
            break
        try:
            answer = query_rag(user_input, config=config)
            print("Bot:", answer, "\n")
        except Exception as e:
            print("Lỗi:", e, "\n")


if __name__ == "__main__":
    main()
