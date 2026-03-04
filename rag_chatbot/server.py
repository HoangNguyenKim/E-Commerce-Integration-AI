"""
FastAPI server — cầu nối giữa E-Commerce frontend và RAG chatbot.
Chạy: python server.py
"""
import os
import sys
import json
import re

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_core import load_config, query_rag

# ── Load config & menu data khi khởi tạo ──────────────────────────
config = load_config(os.path.join(_SCRIPT_DIR, "config.json"))

# Đường dẫn ChromaDB
if "vectorstore" not in config:
    config["vectorstore"] = {}
rel_persist = config["vectorstore"].get("persist_directory", "chromadb")
config["vectorstore"]["persist_directory"] = os.path.join(_SCRIPT_DIR, rel_persist)

# Load danh sách tên món từ menu.json để matching sản phẩm
_menu_names: list[str] = []
data_cfg = config.get("data", {})
data_dir = os.path.join(_SCRIPT_DIR, data_cfg.get("path", "data"))
for fname in data_cfg.get("files", []):
    fpath = os.path.join(data_dir, fname)
    if os.path.isfile(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            items = json.load(f)
        if isinstance(items, list):
            for item in items:
                name = item.get("name", "").strip()
                if name and name not in _menu_names:
                    _menu_names.append(name)


def _extract_suggested_products(reply: str) -> list[str]:
    """Trích xuất tên món ăn được đề cập trong câu trả lời."""
    found: list[str] = []
    reply_lower = reply.lower()
    for name in _menu_names:
        if name.lower() in reply_lower and name not in found:
            found.append(name)
    return found


# ── FastAPI app ────────────────────────────────────────────────────
app = FastAPI(title="Vy Food AI Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    suggested_products: list[str]


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = query_rag(req.message, config=config)
    suggested = _extract_suggested_products(reply)
    return ChatResponse(reply=reply, suggested_products=suggested)


if __name__ == "__main__":
    import uvicorn
    print("Vy Food AI Chatbot API -- http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
