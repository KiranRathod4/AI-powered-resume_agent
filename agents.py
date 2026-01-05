import re
import io
import os
from concurrent.futures import ThreadPoolExecutor

import PyPDF2

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
from services.ats_scorer import calculate_ats_score


# =========================================================
# LLM FACTORY
# =========================================================

USE_GPT = os.getenv("USE_GPT", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_llm(temperature=0.4):
    """Default: Local LLaMA 3.2 via Ollama"""
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
        """Simple RAG: retrieve relevant docs and query LLM with context"""
        llm = get_llm()
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(query)
        
        context = "\n\n".join([doc.page_content for doc in docs])
        
        full_prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
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
        
        # Add ATS score
        ats_result = calculate_ats_score(self.resume_text)
        self.analysis_result['ats_score'] = ats_result

        return self.analysis_result


    # -----------------------------------------------------
    # BULK PROCESSING (NEW)
    # -----------------------------------------------------

    def analyze_bulk_resumes(self, resume_files, custom_jd=None):
        """
        Analyze multiple resumes at once
        
        Args:
            resume_files: List of uploaded resume files
            custom_jd: Optional job description file
        
        Returns:
            List of results with format: [{'name': str, 'result': dict}, ...]
        """
        results = []
        
        # Extract JD skills once
        if custom_jd:
            self.jd_text = self.extract_text_from_file(custom_jd)
            self.extracted_skills = self.extract_skills_from_jd(self.jd_text)
        
        if not self.extracted_skills:
            return []
        
        # Analyze each resume
        for resume_file in resume_files:
            try:
                resume_text = self.extract_text_from_file(resume_file)
                result = self.semantic_skill_analysis(resume_text, self.extracted_skills)
                
                # Add ATS score
                ats_result = calculate_ats_score(resume_text)
                result['ats_score'] = ats_result
                
                results.append({
                    'name': resume_file.name,
                    'result': result
                })
            except Exception as e:
                print(f"Error analyzing {resume_file.name}: {e}")
                results.append({
                    'name': resume_file.name,
                    'result': {'error': str(e)}
                })
        
        return results


    # -----------------------------------------------------
    # COMPARISON MODE (NEW)
    # -----------------------------------------------------

    def compare_resumes(self, resume_a, resume_b, custom_jd=None):
        """
        Compare two resumes side-by-side
        
        Args:
            resume_a: First resume file
            resume_b: Second resume file
            custom_jd: Optional job description
        
        Returns:
            Dict with comparison results
        """
        # Extract skills from JD
        if custom_jd:
            self.jd_text = self.extract_text_from_file(custom_jd)
            self.extracted_skills = self.extract_skills_from_jd(self.jd_text)
        
        if not self.extracted_skills:
            return None
        
        # Analyze both resumes
        text_a = self.extract_text_from_file(resume_a)
        text_b = self.extract_text_from_file(resume_b)
        
        result_a = self.semantic_skill_analysis(text_a, self.extracted_skills)
        result_b = self.semantic_skill_analysis(text_b, self.extracted_skills)
        
        # Add ATS scores
        result_a['ats_score'] = calculate_ats_score(text_a)
        result_b['ats_score'] = calculate_ats_score(text_b)
        
        # Compare
        comparison = {
            'scores': {
                'resume_a': result_a['overall_score'],
                'resume_b': result_b['overall_score']
            },
            'ats_scores': {
                'resume_a': result_a['ats_score']['score'],
                'resume_b': result_b['ats_score']['score']
            },
            'strengths_count': {
                'resume_a': len(result_a['strengths']),
                'resume_b': len(result_b['strengths'])
            },
            'gaps_count': {
                'resume_a': len(result_a['missing_skills']),
                'resume_b': len(result_b['missing_skills'])
            },
            'winner': 'Resume A' if result_a['overall_score'] > result_b['overall_score'] else 'Resume B'
        }
        
        return {
            'resume_a': result_a,
            'resume_b': result_b,
            'comparison': comparison
        }


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