# Chatbot RAG — Cấu trúc tái sử dụng

Chatbot trả lời dựa trên **dữ liệu của bạn** (RAG). Bạn chỉ cần:
- **Đưa dữ liệu** vào thư mục `data/` (JSON hoặc file văn bản)
- **Sửa file `config.json`** để đổi nguồn dữ liệu và lĩnh vực trả lời
- Chạy **nạp dữ liệu** → **chat**

Không cần sửa code. Người khác có thể copy cả thư mục này về, thay dữ liệu và config là dùng được.

---

## Cấu trúc thư mục

```
rag_chatbot/
├── config.json          ← Cấu hình (database, lĩnh vực, model)
├── config.example.json  ← Mẫu config để copy
├── ingest.py            ← Script nạp dữ liệu vào ChromaDB
├── chat.py              ← Chạy chatbot (CLI)
├── rag_core/            ← Module RAG (không cần sửa)
├── data/                ← Đặt dữ liệu của bạn ở đây
│   └── sample.json      ← Ví dụ
└── chromadb/            ← Tạo ra sau khi chạy ingest.py
```

---

## Cách dùng nhanh (3 bước)

### 1. Cài đặt

- Python 3.10+
- Trong thư mục **project gốc** (chứa `rag_chatbot`):  
  `pip install -r requirements.txt`
- Tạo file `.env` với `OPENAI_API_KEY=sk-...` (đặt ở thư mục project gốc hoặc trong `rag_chatbot`; `ingest.py` và `chat.py` sẽ load qua `python-dotenv`)

### 2. Cấu hình và dữ liệu

- **Dữ liệu:** Đặt file JSON (hoặc .txt) vào `rag_chatbot/data/`.  
  Sửa `config.json` → `data.files` (tên file) và `data.content_template` cho đúng trường trong JSON.
- **Lĩnh vực trả lời:** Sửa `config.json` → `prompt.role`, `prompt.instruction`, `prompt.output_guide` (ví dụ: trợ lý pháp lý, FAQ, du lịch…).

### 3. Nạp dữ liệu và chạy chat

Từ thư mục **project gốc**:

```bash
cd rag_chatbot
python ingest.py
python chat.py
```

Hoặc từ project gốc:

```bash
python -m rag_chatbot.ingest
python -m rag_chatbot.chat
```

Thoát chat: gõ `exit` hoặc `quit`.

---

## Thay đổi database (nguồn dữ liệu)

Trong `config.json`:

- **data.path**: Thư mục chứa file (mặc định `data` = `rag_chatbot/data/`).
- **data.format**: `json_list` (nhiều file JSON, mỗi file là mảng object) hoặc `text` (file .txt, mỗi file = 1 document).
- **data.files**: Danh sách tên file (với `json_list`).
- **data.content_template**: Chuỗi ghép nội dung mỗi bản ghi, dùng `{{tên_trường}}` (ví dụ: `{{name}} - {{description}}`).
- **data.metadata_fields**: Các trường lưu làm metadata (tên, loại, quận…).
- **data.field_aliases**: Map tên trường khác nhau giữa các file (ví dụ: `"open_time": ["open_time", "Check-in hour"]`).

Sau khi đổi config hoặc đổi file trong `data/`, chạy lại `python ingest.py`.

---

## Thay đổi lĩnh vực trả lời

Chỉ cần sửa **prompt** trong `config.json`:

- **prompt.role**: Vai trò bot (vd: "Bạn là hướng dẫn viên du lịch", "Bạn là trợ lý FAQ nội bộ").
- **prompt.instruction**: Quy tắc trả lời (chỉ dựa tài liệu, ngôn ngữ, không bịa…).
- **prompt.output_guide**: Gợi ý format (vd: "Trình bày: Tên, Loại, Mô tả, Khu vực").

Không cần sửa code trong `rag_core/`.

---

## Cho người khác “lấy cấu trúc về và chỉ cần đưa dữ liệu”

1. Copy cả thư mục **rag_chatbot** (gồm `rag_core/`, `ingest.py`, `chat.py`, `config.json`, `config.example.json`, `data/`).
2. Cài đặt: `pip install -r requirements.txt` (từ project chứa rag_chatbot), tạo `.env` với `OPENAI_API_KEY`.
3. Chỉnh `config.json`: `data.path`, `data.files`, `content_template`, `metadata_fields` cho đúng dữ liệu của họ; chỉnh `prompt` theo lĩnh vực.
4. Bỏ dữ liệu (JSON hoặc .txt) vào `data/`.
5. Chạy: `python ingest.py` rồi `python chat.py`.

Họ **chỉ cần đưa dữ liệu** và sửa config, không cần sửa code.

---

## Ví dụ config cho lĩnh vực khác

**FAQ nội bộ:**

- `data.files`: `["faq.json"]`
- `content_template`: `"{{câu_hỏi}} {{câu_trả_lời}}"`
- `metadata_fields`: `["chủ_đề", "câu_hỏi"]`
- `prompt.role`: "Bạn là trợ lý trả lời FAQ nội bộ công ty."
- `prompt.instruction`: "Chỉ trả lời theo tài liệu FAQ. Nếu không có, nói không có thông tin."

**Du lịch (nhiều file):**

- `data.files`: `["restaurant.json", "hotel.json", "destination.json"]`
- `content_template`: ghép tên, mô tả, quận, giờ mở/đóng…
- `field_aliases`: map `open_time` / `Check-in hour`, `close_time` / `Check-out hour` nếu cần.
