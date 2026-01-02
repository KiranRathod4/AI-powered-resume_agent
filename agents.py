import re
import io
import os
from concurrent.futures import ThreadPoolExecutor

import PyPDF2

# ✅ FIXED: Use new non-deprecated imports
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    from langchain_community.llms import Ollama as OllamaLLM

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from services.improvement import rewrite_resume_ats


# =========================================================
# LLM FACTORY
# =========================================================

USE_GPT = os.getenv("USE_GPT", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_llm(temperature=0.4):
    """
    Default: Local LLaMA 3.2 via Ollama
    Optional: GPT (if USE_GPT=true and API key is set)
    """
    if USE_GPT and OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o",
            temperature=temperature,
            api_key=OPENAI_API_KEY
        )

    return OllamaLLM(
        model="llama3.2",
        temperature=temperature
    )


# =========================================================
# MAIN AGENT
# =========================================================

class ResumeAnalyzer:
    def __init__(self, cutoff_score=80):
        self.cutoff_score = cutoff_score

        self.resume_text = None
        self.jd_text = None
        self.extracted_skills = []
        self.analysis_result = None

        self.resume_strengths = []
        self.resume_weaknesses = []

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.rag_vectorstore = None


    # -----------------------------------------------------
    # FILE EXTRACTION
    # -----------------------------------------------------

    def extract_text_from_pdf(self, pdf_file):
        try:
            reader = (
                PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
                if hasattr(pdf_file, "getvalue")
                else PyPDF2.PdfReader(pdf_file)
            )
            return "".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""


    def extract_text_from_txt(self, txt_file):
        try:
            if hasattr(txt_file, "getvalue"):
                data = txt_file.getvalue()
                return data.decode("utf-8") if isinstance(data, bytes) else data
            with open(txt_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"TXT extraction error: {e}")
            return ""


    def extract_text_from_file(self, file):
        name = file.name if hasattr(file, "name") else file
        ext = name.split(".")[-1].lower()

        if ext == "pdf":
            return self.extract_text_from_pdf(file)
        if ext == "txt":
            return self.extract_text_from_txt(file)
        return ""


    # -----------------------------------------------------
    # VECTOR STORES
    # -----------------------------------------------------

    def create_rag_vectorstore(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_text(text)
        return FAISS.from_texts(chunks, self.embeddings)


    def create_vector_store(self, text):
        return FAISS.from_texts([text], self.embeddings)


    # -----------------------------------------------------
    # JOB DESCRIPTION → SKILLS
    # -----------------------------------------------------

    def extract_skills_from_jd(self, jd_text):
        llm = get_llm()

        prompt = f"""
Extract a clean list of technical and professional skills.

Rules:
- Return ONLY a Python list
- No explanations
- Standard skill names only

Job Description:
{jd_text}
"""
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else response

        match = re.search(r"\[(.*?)\]", content, re.DOTALL)
        if match:
            try:
                return eval(match.group(0))
            except Exception:
                pass
        return []


    # -----------------------------------------------------
    # SIMPLE RAG QUERY FUNCTION
    # -----------------------------------------------------

    def query_with_context(self, vectorstore, query):
        """
        Simple RAG: retrieve relevant docs and query LLM with context
        No chains needed - direct approach
        """
        llm = get_llm()
        
        # Get relevant documents using invoke (modern API)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(query)  # ✅ FIXED: Changed from get_relevant_documents to invoke
        
        # Combine context
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create prompt with context
        full_prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        # Get response
        response = llm.invoke(full_prompt)
        return response.content if hasattr(response, "content") else str(response)


    # -----------------------------------------------------
    # SEMANTIC SKILL ANALYSIS
    # -----------------------------------------------------

    def analyze_skill(self, vectorstore, skill):
        """Analyze a single skill using simple RAG"""
        query = (
            f"Rate resume proficiency in {skill} from 0 to 10. "
            f"Start with the number, then one sentence justification."
        )
        
        response = self.query_with_context(vectorstore, query)
        
        # Parse score
        match = re.search(r"(\d{1,2})", response)
        score = min(int(match.group(1)), 10) if match else 0
        reasoning = response.split(".", 1)[1].strip() if "." in response else response

        return skill, score, reasoning


    def semantic_skill_analysis(self, resume_text, skills):
        vectorstore = self.create_vector_store(resume_text)

        skill_scores = {}
        skill_reasoning = {}
        missing_skills = []
        total_score = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(
                lambda s: self.analyze_skill(vectorstore, s),
                skills
            )

        for skill, score, reasoning in results:
            skill_scores[skill] = score
            skill_reasoning[skill] = reasoning
            total_score += score
            if score <= 5:
                missing_skills.append(skill)

        overall_score = int((total_score / (10 * len(skills))) * 100) if skills else 0
        strengths = [s for s, v in skill_scores.items() if v >= 7]

        self.resume_strengths = strengths

        return {
            "overall_score": overall_score,
            "skill_scores": skill_scores,
            "skill_reasoning": skill_reasoning,
            "strengths": strengths,
            "missing_skills": missing_skills,
            "selected": overall_score >= self.cutoff_score
        }


    # -----------------------------------------------------
    # MAIN ENTRY
    # -----------------------------------------------------

    def analyze_resume(self, resume_file, custom_jd=None):
        self.resume_text = self.extract_text_from_file(resume_file)
        self.rag_vectorstore = self.create_rag_vectorstore(self.resume_text)

        if custom_jd:
            self.jd_text = self.extract_text_from_file(custom_jd)
            self.extracted_skills = self.extract_skills_from_jd(self.jd_text)

        if not self.extracted_skills:
            return {}

        self.analysis_result = self.semantic_skill_analysis(
            self.resume_text,
            self.extracted_skills
        )

        return self.analysis_result


    # -----------------------------------------------------
    # Q&A
    # -----------------------------------------------------

    def ask_question(self, question):
        if not self.rag_vectorstore:
            return "Please analyze a resume first."

        return self.query_with_context(self.rag_vectorstore, question)


    # -----------------------------------------------------
    # ATS REWRITE
    # -----------------------------------------------------

    def get_improved_resume(self, target_role="", highlight_skills=""):
        llm = get_llm(temperature=0.4)

        if isinstance(highlight_skills, str):
            skills = [s.strip() for s in highlight_skills.split(",") if s.strip()]
        else:
            skills = highlight_skills or self.extracted_skills

        return rewrite_resume_ats(
            llm=llm,
            resume_text=self.resume_text,
            target_role=target_role,
            skills=skills
        )
    
    
    # -----------------------------------------------------
    # CLEANUP
    # -----------------------------------------------------
    
    def cleanup(self):
        """Clean up resources"""
        self.rag_vectorstore = None
        self.resume_text = None
        self.jd_text = None