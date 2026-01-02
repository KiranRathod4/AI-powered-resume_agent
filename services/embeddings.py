import importlib
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    try:
        from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore
    except Exception:
        from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore
    from langchain_community.vectorstores import FAISS  # type: ignore
else:
    try:
        _mod = importlib.import_module("langchain_huggingface")
        HuggingFaceEmbeddings = getattr(_mod, "HuggingFaceEmbeddings")
    except Exception:
        _mod = importlib.import_module("langchain_community.embeddings")
        HuggingFaceEmbeddings = getattr(_mod, "HuggingFaceEmbeddings")

    FAISS = importlib.import_module("langchain_community.vectorstores").FAISS


# Singleton embeddings (avoid reloading model repeatedly)
EMBEDDINGS = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_rag_vectorstore(text: str):
    try:
        _split_mod = importlib.import_module("langchain.text_splitter")
        RecursiveCharacterTextSplitter = getattr(_split_mod, "RecursiveCharacterTextSplitter")
    except Exception:
        _split_mod = importlib.import_module("langchain_community.text_splitter")
        RecursiveCharacterTextSplitter = getattr(_split_mod, "RecursiveCharacterTextSplitter")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_text(text)
    return FAISS.from_texts(chunks, EMBEDDINGS)


def create_single_vectorstore(text: str):
    return FAISS.from_texts([text], EMBEDDINGS)
