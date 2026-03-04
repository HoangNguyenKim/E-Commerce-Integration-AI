"""
Nạp dữ liệu vào ChromaDB theo config.json.
Chạy từ thư mục rag_chatbot: python ingest.py [đường_dẫn_config]
Hoặc từ project root: python -m rag_chatbot.ingest
"""
import os
import sys

# Đảm bảo import từ rag_core trong cùng package
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from rag_core import load_config, load_documents_from_config, build_vectorstore


def main():
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = os.path.join(_SCRIPT_DIR, "config.json")
    base_path = _SCRIPT_DIR

    print("Dang doc cau hinh...")
    config = load_config(config_path)
    print("Dang tai tai lieu tu nguon trong config...")
    documents = load_documents_from_config(config, base_path=base_path)
    if not documents:
        print("Khong co document nao. Kiem tra data.path va data.files trong config.")
        return
    print(f"Tong so document: {len(documents)}")
    print("Dang tao va luu vectorstore (ChromaDB)...")
    persist_dir = os.path.join(
        base_path,
        config.get("vectorstore", {}).get("persist_directory", "chromadb"),
    )
    build_vectorstore(documents, config=config, persist_dir=persist_dir)
    print("Hoan thanh. Chay: python chat.py")


if __name__ == "__main__":
    main()
