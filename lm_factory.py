from config import USE_GPT, OPENAI_API_KEY


def get_llm(temperature=0.2):
    if USE_GPT and OPENAI_API_KEY:
        try:
            from langchain.chat_models import ChatOpenAI
            return ChatOpenAI(
                model_name="gpt-4o",
                temperature=temperature,
                openai_api_key=OPENAI_API_KEY
            )
        except Exception:
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model="gpt-4o",
                    temperature=temperature,
                    api_key=OPENAI_API_KEY
                )
            except Exception:
                raise RuntimeError("No ChatOpenAI implementation available; install langchain or langchain_openai")

    try:
        from langchain_community.llms import Ollama
    except Exception:
        Ollama = None

    if Ollama is None:
        raise RuntimeError("Ollama LLM not available; set USE_GPT=true or install langchain-community")

    return Ollama(
        model="llama3.2",
        temperature=temperature
    )
