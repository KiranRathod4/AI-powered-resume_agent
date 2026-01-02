def rewrite_resume_ats(
    llm,
    resume_text: str,
    target_role: str,
    skills: list[str]
) -> str:

    prompt = f"""
You are an ATS optimization engine.

Goal:
Rewrite the resume to maximize ATS match for the target role.

Rules:
- Use bullet points
- Start bullets with strong action verbs
- Include metrics (% / numbers) wherever possible
- Integrate missing keywords naturally
- Do NOT add fake experience

Target Role:
{target_role}

Keywords to prioritize:
{", ".join(skills)}

Original Resume:
{resume_text}

Return ONLY the rewritten resume.
No explanations.
"""

    response = llm.invoke(prompt)
    return response.content.strip()
