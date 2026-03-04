"""
Nạp tài liệu từ nhiều định dạng theo config.
Hỗ trợ: json_list (nhiều file JSON, mỗi file là mảng object), text (file .txt).
"""
import os
import json
import re
from langchain_core.documents import Document
from .config import get_data_config


def _get_value(item: dict, key: str, aliases: dict | None) -> str:
    """Lấy giá trị từ item, hỗ trợ field_aliases (thử nhiều tên trường)."""
    if aliases and key in aliases:
        for alias in aliases[key]:
            val = item.get(alias)
            if val is not None:
                return str(val) if not isinstance(val, list) else ", ".join(str(x) for x in val)
    val = item.get(key)
    if val is None:
        return ""
    if isinstance(val, list):
        return ", ".join(str(x) for x in val)
    return str(val)


def _render_template(template: str, item: dict, aliases: dict | None) -> str:
    """Thay thế {{key}} trong template bằng item[key] (có aliases)."""
    content = template
    for key in item.keys():
        val = _get_value(item, key, aliases)
        content = content.replace(f"{{{{{key}}}}}", val)
    remaining = set(re.findall(r"\{\{(\w+)\}\}", content))
    for key in remaining:
        content = content.replace(f"{{{{{key}}}}}", _get_value(item, key, aliases))
    return content


def _item_to_metadata(item: dict, metadata_fields: list, aliases: dict | None) -> dict:
    """Lấy metadata từ item, chỉ giữ giá trị đơn giản (str, int, float, bool)."""
    meta = {}
    for key in metadata_fields:
        val = _get_value(item, key, aliases) or item.get(key)
        if val is None:
            continue
        if isinstance(val, (str, int, float, bool)):
            meta[key] = val
        elif isinstance(val, list):
            meta[key] = ", ".join(str(x) for x in val)
        else:
            meta[key] = str(val)
    return meta


def load_json_list_documents(data_config: dict, base_path: str | None = None) -> list:
    """Đọc các file JSON (mảng object), mỗi object → 1 Document."""
    path = data_config.get("path", "data")
    files = data_config.get("files", [])
    content_template = data_config.get(
        "content_template",
        "{{name}} {{description}}"
    )
    metadata_fields = data_config.get("metadata_fields", ["name", "type"])
    field_aliases = data_config.get("field_aliases") or {}
    base_path = base_path or os.getcwd()
    data_dir = os.path.join(base_path, path)
    documents = []
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        if not os.path.isfile(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        if not isinstance(items, list):
            items = [items]
        for item in items:
            if not isinstance(item, dict):
                continue
            content = _render_template(content_template, item, field_aliases)
            meta = _item_to_metadata(item, metadata_fields, field_aliases)
            meta["_source_file"] = file_name
            documents.append(Document(page_content=content, metadata=meta))
    return documents


def load_text_documents(data_config: dict, base_path: str | None = None) -> list:
    """Mỗi file .txt trong path → 1 Document."""
    path = data_config.get("path", "data")
    base_path = base_path or os.getcwd()
    data_dir = os.path.join(base_path, path)
    documents = []
    if not os.path.isdir(data_dir):
        return documents
    for name in os.listdir(data_dir):
        if not name.lower().endswith(".txt"):
            continue
        file_path = os.path.join(data_dir, name)
        if not os.path.isfile(file_path):
            continue
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        documents.append(Document(page_content=content.strip(), metadata={"source": name}))
    return documents


def load_documents_from_config(config: dict, base_path: str | None = None) -> list:
    """
    Đọc config, gọi loader tương ứng (json_list hoặc text), trả về list Document.
    """
    data_config = get_data_config(config)
    fmt = data_config.get("format", "json_list")
    base_path = base_path or os.getcwd()
    if fmt == "json_list":
        return load_json_list_documents(data_config, base_path)
    if fmt == "text":
        return load_text_documents(data_config, base_path)
    raise ValueError(f"Định dạng dữ liệu không hỗ trợ: {fmt}. Dùng 'json_list' hoặc 'text'.")
