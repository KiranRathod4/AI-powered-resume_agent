import re
from concurrent.futures import ThreadPoolExecutor
from lm_factory import get_llm
from services.embeddings import create_single_vectorstore


def extract_skills_from_jd(jd_text: str):
    """Extract skills from job description using LLM"""
    llm = get_llm()
    prompt = f"""
Extract technical and professional skills from the job description.

Rules:
- Return ONLY a Python list
- No explanations
- Use standard industry terms

Job Description:
{jd_text}
"""
    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    match = re.search(r"\[(.*?)\]", content, re.DOTALL)
    if match:
        try:
            return eval(match.group(0))
        except Exception:
            pass
    return []


def query_with_context(vectorstore, query):
    """
    Simple RAG: retrieve relevant docs and query LLM with context
    Modern approach without deprecated chains
    """
    llm = get_llm()
    
    # Get relevant documents using invoke (modern API)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    
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


def analyze_single_skill(vectorstore, skill):
    """
    Analyze a single skill using simple RAG
    No chains needed - direct retrieval + LLM call
    """
    query = (
        f"Rate resume proficiency in {skill} from 0 to 10. "
        f"Start with the number, then one sentence explanation."
    )
    
    response = query_with_context(vectorstore, query)

    # Parse score
    score_match = re.search(r"(\d{1,2})", response)
    score = min(int(score_match.group(1)), 10) if score_match else 0
    reasoning = response.split(".", 1)[1].strip() if "." in response else response

    return skill, score, reasoning


def semantic_skill_analysis(resume_text: str, skills: list, cutoff_score=80):
    """
    Analyze resume against required skills using semantic search
    Returns detailed scoring and recommendations
    """
    if not skills:
        return {
            "overall_score": 0,
            "skill_scores": {},
            "skill_reasoning": {},
            "strengths": [],
            "missing_skills": [],
            "selected": False
        }

    # Create vectorstore once for all skills
    vectorstore = create_single_vectorstore(resume_text)

    scores = {}
    reasoning = {}
    missing = []
    total = 0

    # Analyze skills in parallel
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = pool.map(
            lambda s: analyze_single_skill(vectorstore, s),
            skills
        )

    # Process results
    for skill, score, reason in results:
        scores[skill] = score
        reasoning[skill] = reason
        total += score
        if score <= 5:
            missing.append(skill)

    # Calculate overall score
    overall = int((total / (10 * len(skills))) * 100) if skills else 0
    strengths = [k for k, v in scores.items() if v >= 7]

    return {
        "overall_score": overall,
        "skill_scores": scores,
        "skill_reasoning": reasoning,
        "strengths": strengths,
        "missing_skills": missing,
        "selected": overall >= cutoff_score
    }