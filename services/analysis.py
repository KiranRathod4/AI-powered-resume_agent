import re
from concurrent.futures import ThreadPoolExecutor
from lm_factory import get_llm
from services.embeddings import create_single_vectorstore


def extract_skills_from_jd(jd_text: str):
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

    match = re.search(r"\[(.*?)\]", response, re.DOTALL)
    if match:
        try:
            return eval(match.group(0))
        except Exception:
            pass
    return []


def analyze_single_skill(qa_chain, skill):
    query = (
        f"Rate resume proficiency in {skill} from 0–10. "
        f"Start with the number, then one sentence explanation."
    )
    response = qa_chain.run(query)

    score_match = re.search(r"(\d{1,2})", response)
    score = min(int(score_match.group(1)), 10) if score_match else 0
    reasoning = response.split(".", 1)[1].strip() if "." in response else ""

    return skill, score, reasoning


def semantic_skill_analysis(resume_text: str, skills: list, cutoff_score=80):
    retriever = create_single_vectorstore(resume_text).as_retriever(k=3)
    try:
        from langchain.chains import RetrievalQA
    except Exception:
        try:
            from langchain_community.chains import RetrievalQA
        except Exception:
            RetrievalQA = None

    if RetrievalQA is None:
        raise RuntimeError("RetrievalQA not available; install a compatible langchain package")

    qa_chain = RetrievalQA.from_chain_type(
        llm=get_llm(),
        chain_type="stuff",
        retriever=retriever
    )

    scores = {}
    reasoning = {}
    missing = []
    total = 0

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = pool.map(
            lambda s: analyze_single_skill(qa_chain, s),
            skills
        )

    for skill, score, reason in results:
        scores[skill] = score
        reasoning[skill] = reason
        total += score
        if score <= 5:
            missing.append(skill)

    overall = int((total / (10 * len(skills))) * 100)
    strengths = [k for k, v in scores.items() if v >= 7]

    return {
        "overall_score": overall,
        "skill_scores": scores,
        "skill_reasoning": reasoning,
        "strengths": strengths,
        "missing_skills": missing,
        "selected": overall >= cutoff_score
    }
