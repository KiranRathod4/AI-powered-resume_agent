import streamlit as st
import plotly.express as px


# =========================
# Page Setup
# =========================
def setup_page():
    """Setup page styling"""
    st.markdown("""
    <style>
        .header-box {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        .good { border-left: 4px solid #28a745; }
        .bad { border-left: 4px solid #dc3545; }
    </style>
    """, unsafe_allow_html=True)


# =========================
# Header
# =========================
def display_header():
    """Display app header"""
    st.markdown("""
    <div class="header-box">
        <h1>🤖 Recruitr</h1>
        <p>AI-powered Resume Analysis, Interview Prep & Resume Improvement</p>
    </div>
    """, unsafe_allow_html=True)


# =========================
# Tabs - ALL 5 TABS
# =========================
def create_tabs():
    """Create main navigation tabs"""
    return st.tabs([
        "📄 Resume Analysis",
        "💬 Ask About Resume",
        "✨ Rewrite Resume",
        "📈 Improvement Suggestions",
        "🎯 Interview Questions"                     #✨ Rewrite Resume
    ])


# =========================
# Role Selection
# =========================
def role_selection_section(role_requirements):
    """Role and JD selection UI"""
    st.subheader("Target Role")

    method = st.radio(
        "Choose analysis method",
        ["Predefined Role", "Upload Job Description"]
    )

    role = None
    custom_jd = None

    if method == "Predefined Role":
        role = st.selectbox(
            "Select role",
            list(role_requirements.keys())
        )

        with st.expander("👁️ View required skills"):
            for skill in role_requirements[role]:
                st.markdown(f"- {skill}")

    else:
        custom_jd = st.file_uploader(
            "Upload Job Description (PDF / TXT)",
            type=["pdf", "txt"]
        )
        if custom_jd:
            st.success("✅ Job description uploaded")

    return role, custom_jd


# =========================
# Resume Upload
# =========================
def resume_upload_section():
    """Resume upload UI"""
    st.subheader("Upload Resume")

    resume = st.file_uploader(
        "PDF or TXT format",
        type=["pdf", "txt"],
        help="Upload your resume in PDF or TXT format (max 200MB)"
    )

    if resume:
        st.success("✅ Resume uploaded successfully")

    return resume


# =========================
# Analysis Results
# =========================
def display_analysis_results(result):
    """Display analysis results with metrics and charts"""
    if not result:
        st.warning("No results to display")
        return

    st.divider()
    st.subheader("📊 Analysis Results")

    # Overall metrics
    col1, col2, col3 = st.columns(3)

    overall_score = result.get('overall_score', 0)
    
    col1.metric("Overall Score", f"{overall_score}%")
    col2.metric(
        "Decision",
        "✅ SELECTED" if result.get("selected", False) else "❌ NOT SELECTED"
    )
    col3.metric(
        "Strengths",
        len(result.get("strengths", []))
    )

    # Skill scores chart
    skill_scores = result.get("skill_scores", {})

    if skill_scores:
        st.subheader("📈 Skill Breakdown")
        
        fig = px.bar(
            x=list(skill_scores.keys()),
            y=list(skill_scores.values()),
            labels={"x": "Skill", "y": "Score (0-10)"},
            color=list(skill_scores.values()),
            color_continuous_scale="RdYlGn",
            range_color=[0, 10]
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Strengths & gaps
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💪 Strengths (Score ≥ 7)")
        strengths = result.get("strengths", [])
        if strengths:
            for s in strengths:
                score = skill_scores.get(s, 0)
                st.markdown(
                    f"<div class='card good'><b>{s}</b> - {score}/10</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No strong skills identified")

    with col2:
        st.subheader("⚠️ Gaps (Score ≤ 5)")
        gaps = result.get("missing_skills", [])
        if gaps:
            for s in gaps:
                score = skill_scores.get(s, 0)
                st.markdown(
                    f"<div class='card bad'><b>{s}</b> - {score}/10</div>",
                    unsafe_allow_html=True
                )
        else:
            st.success("No major skill gaps!")

    # Detailed reasoning
    with st.expander("🔍 Detailed Skill Analysis"):
        reasoning = result.get("skill_reasoning", {})
        for skill, reason in reasoning.items():
            score = skill_scores.get(skill, 0)
            st.markdown(f"**{skill}** ({score}/10): {reason}")


# =========================
# Resume Q&A
# =========================
def resume_qa_section(has_resume, ask_question_func):
    """Resume Q&A interface"""
    st.subheader("💬 Ask Questions About the Resume")

    if not has_resume:
        st.warning("⚠️ Please analyze a resume first in the 'Resume Analysis' tab.")
        return

    question = st.text_input(
        "Your question",
        placeholder="e.g., What are the candidate's main strengths in Python?"
    )

    if st.button("Get Answer"):
        if question:
            with st.spinner("🤔 Thinking..."):
                answer = ask_question_func(question)
                st.markdown("### Answer:")
                st.write(answer)
        else:
            st.warning("Please enter a question.")


# =========================
# Interview Questions Section
# =========================
def interview_questions_section(has_resume, generate_questions_func=None):
    """Interview questions generation interface"""
    st.subheader("🎯 Generate Interview Questions")

    if not has_resume:
        st.warning("⚠️ Please analyze a resume first in the 'Resume Analysis' tab.")
        return

    # Question type selection
    types = st.multiselect(
        "Question Types",
        ["Technical", "Behavioral", "Coding", "System Design"],
        default=["Technical", "Behavioral"]
    )

    # Difficulty selection
    difficulty = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1
    )

    # Number of questions
    count = st.slider("Number of Questions", 1, 10, 5)

    if st.button("Generate Questions", type="primary"):
        if generate_questions_func:
            with st.spinner("Generating interview questions..."):
                try:
                    questions = generate_questions_func(types, difficulty, count)
                    
                    st.success(f"✅ Generated {len(questions)} questions!")
                    
                    for i, (q_type, question) in enumerate(questions, 1):
                        with st.expander(f"Question {i}: {q_type}"):
                            st.write(question)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.info("🚧 Interview question generation coming soon!")


# =========================
# Improvement Suggestions Section
# =========================
def improvement_suggestions_section(has_resume, analysis_result=None):
    """Resume improvement suggestions interface"""
    st.subheader("📈 Resume Improvement Suggestions")

    if not has_resume:
        st.warning("⚠️ Please analyze a resume first in the 'Resume Analysis' tab.")
        return

    if not analysis_result:
        st.info("No analysis results available.")
        return

    # Show missing skills
    missing_skills = analysis_result.get("missing_skills", [])
    if missing_skills:
        st.markdown("### ⚠️ Skills to Develop")
        st.write("Consider improving or adding these skills to your resume:")
        for skill in missing_skills:
            score = analysis_result.get("skill_scores", {}).get(skill, 0)
            st.markdown(f"- **{skill}** (Current score: {score}/10)")
        st.divider()

    # Show strengths to highlight
    strengths = analysis_result.get("strengths", [])
    if strengths:
        st.markdown("### 💪 Strengths to Emphasize")
        st.write("Make sure these skills are prominently featured:")
        for skill in strengths:
            score = analysis_result.get("skill_scores", {}).get(skill, 0)
            st.markdown(f"- **{skill}** (Score: {score}/10)")
        st.divider()

    # General improvement tips
    st.markdown("### 💡 General Tips")
    
    overall_score = analysis_result.get("overall_score", 0)
    
    if overall_score < 60:
        st.warning("""
        **Your resume needs significant improvement:**
        - Add more relevant technical skills
        - Include quantifiable achievements
        - Expand on project experience
        - Use industry-standard keywords
        """)
    elif overall_score < 80:
        st.info("""
        **Your resume is good but can be better:**
        - Strengthen weak skill areas
        - Add more specific examples
        - Optimize for ATS systems
        - Highlight leadership experience
        """)
    else:
        st.success("""
        **Your resume is strong!**
        - Minor refinements in weak areas
        - Keep content current and relevant
        - Tailor for specific roles
        """)


# =========================
# Improved Resume Section
# =========================
def improved_resume_section(has_resume, get_improved_resume_func):
    """Resume rewriting interface"""
    st.subheader("✨ Rewrite Resume for Target Role")

    if not has_resume:
        st.warning("⚠️ Please analyze a resume first in the 'Resume Analysis' tab.")
        return

    # Target role input
    role = st.text_input(
        "Target Role",
        placeholder="e.g., Senior Data Scientist"
    )

    # Skills input
    skills = st.text_area(
        "Skills to emphasize (comma-separated)",
        placeholder="Python, Machine Learning, SQL, etc.",
        help="Leave empty to use skills from the analyzed role"
    )

    if st.button("Generate Resume", type="primary"):
        if not role:
            st.warning("⚠️ Please enter a target role.")
        else:
            with st.spinner("✍️ Generating improved resume..."):
                try:
                    improved_text = get_improved_resume_func(role, skills)
                    
                    if improved_text:
                        st.success("✅ Resume generated successfully!")
                        st.divider()
                        
                        # Display improved resume
                        st.markdown("### Improved Resume:")
                        st.text_area(
                            "Preview",
                            improved_text,
                            height=500,
                            label_visibility="collapsed"
                        )
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Resume",
                            data=improved_text,
                            file_name=f"improved_resume_{role.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("Failed to generate resume. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.code(str(e))