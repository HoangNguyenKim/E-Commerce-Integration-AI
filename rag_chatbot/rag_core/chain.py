"""
Tạo RAG chain (retriever + QA) theo config. Prompt lấy từ config (role, instruction, output_guide).
Dùng Google Gemini cho LLM (GOOGLE_API_KEY trong .env).
"""
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
except ModuleNotFoundError:
    from langchain_classic.chains import RetrievalQA
    from langchain_classic.prompts import PromptTemplate

from .config import load_config, get_prompt_config, get_llm_config, get_retrieval_config
from .vectorstore import get_vectorstore

_DEFAULT_TEMPLATE = """{role}

{instruction}

{output_guide}

Câu hỏi của người dùng: {question}
Dữ liệu truy xuất được:
{context}

Trả lời (bằng ngôn ngữ người dùng hỏi):"""


def _build_qa_prompt(config: dict) -> PromptTemplate:
    prompt_cfg = get_prompt_config(config)
    role = prompt_cfg.get("role", "Bạn là trợ lý trả lời dựa trên tài liệu.")
    instruction = prompt_cfg.get("instruction", "Trả lời dựa trên dữ liệu bên dưới. Nếu không có thông tin, nói rõ.")
    output_guide = prompt_cfg.get("output_guide", "")
    if prompt_cfg.get("template"):
        template = prompt_cfg["template"]
    else:
        # Chỉ thay role/instruction/output_guide, giữ {question} và {context} cho chain điền sau
        template = _DEFAULT_TEMPLATE.replace("{role}", role).replace("{instruction}", instruction).replace("{output_guide}", output_guide)
    return PromptTemplate.from_template(template)


def get_rag_chain(config: dict | None = None, vectorstore=None):
    """
    Trả về RetrievalQA chain đã cấu hình.
    """
    if config is None:
        config = load_config()
    if vectorstore is None:
        vectorstore = get_vectorstore(config)
    llm_cfg = get_llm_config(config)
    ret_cfg = get_retrieval_config(config)
    llm = ChatGoogleGenerativeAI(
        model=llm_cfg.get("model", "gemini-2.5-flash"),
        temperature=llm_cfg.get("temperature", 0),
    )
    retriever = vectorstore.as_retriever(
        search_type=ret_cfg.get("search_type", "mmr"),
        search_kwargs={"k": ret_cfg.get("k", 5)},
    )
    qa_prompt = _build_qa_prompt(config)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": qa_prompt},
    )
    return chain


def query_rag(question: str, config: dict | None = None, vectorstore=None) -> str:
    """Hỏi RAG một câu và trả về chuỗi trả lời. Tự retry khi gặp 429 (quota)."""
    import time
    chain = get_rag_chain(config=config, vectorstore=vectorstore)
    last_error = None
    for attempt in range(3):
        try:
            result = chain.invoke({"query": question})
            return result.get("result", "")
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
                wait = 25
                if attempt < 2:
                    time.sleep(wait)
                    continue
            raise
    raise last_error


def get_rag_tool(config: dict | None = None, description: str | None = None):
    """Trả về LangChain tool gọi RAG theo config (để gắn vào agent)."""
    from langchain.tools import tool

    _config = config

    @tool
    def rag_query(query: str) -> str:
        """Trả lời câu hỏi dựa trên dữ liệu đã nạp trong vectorstore (theo config)."""
        return query_rag(query, config=_config)

    if description:
        rag_query.description = description
    return rag_query
