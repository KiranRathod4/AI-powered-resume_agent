SKILL_EXTRACTION_PROMPT = """
Extract a clean list of technical and professional skills from the job description.
Rules:
- No explanations
- No duplicates
- Use industry-standard names
- Return ONLY a Python list

Job Description:
{jd}
"""

RESUME_SCORING_PROMPT = """
Evaluate how clearly the resume demonstrates proficiency in {skill}.
Rules:
1. Start with a number from 0–10
2. Then give ONE sentence justification
3. Base judgment ONLY on resume evidence
"""

RESUME_REWRITE_PROMPT = """
Rewrite the resume to be ATS-optimized and recruiter-ready.

Rules:
- Quantify achievements
- Use strong action verbs
- Preserve truthfulness
- Do NOT invent experience
- Optimize for {target_role}

Resume:
{resume}
"""