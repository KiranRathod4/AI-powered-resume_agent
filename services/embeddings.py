try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS
from config import EMBEDDING_MODEL


def get_embeddings():
    """Get embeddings model instance"""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


def create_single_vectorstore(text):
    """
    Create a FAISS vectorstore from a single text document
    
    Args:
        text: Text content to index
    
    Returns:
        FAISS vectorstore
    """
    embeddings = get_embeddings()
    return FAISS.from_texts([text], embeddings)