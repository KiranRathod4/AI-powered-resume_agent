def rewrite_resume_ats(llm, resume_text, target_role, skills):
    """
    Rewrite resume to be ATS-friendly and optimized for target role
    
    Args:
        llm: Language model instance
        resume_text: Original resume text
        target_role: Target job role
        skills: List of skills to emphasize
    
    Returns:
        Improved resume text
    """
    
    skills_str = ", ".join(skills) if isinstance(skills, list) else skills
    
    prompt = f"""You are an expert resume writer specializing in ATS-optimized resumes.

Rewrite the following resume to be highly optimized for the role of "{target_role}".

Key Requirements:
1. Emphasize these skills: {skills_str}
2. Use strong action verbs (Led, Developed, Implemented, etc.)
3. Quantify achievements with metrics where possible
4. Make it ATS-friendly with clear section headers
5. Highlight relevant experience for {target_role}
6. Keep the same factual information, but reframe it effectively
7. Use industry-standard keywords for {target_role}

Original Resume:
{resume_text}

Generate an improved, ATS-optimized resume that will pass automated screening and impress hiring managers:
"""

    try:
        response = llm.invoke(prompt)
        improved_text = response.content if hasattr(response, "content") else str(response)
        return improved_text
    except Exception as e:
        return f"Error generating resume: {str(e)}"