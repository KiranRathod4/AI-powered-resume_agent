import streamlit as st
import plotly.express as px


# =========================
# Page Setup
# =========================
def setup_page():
    st.set_page_config(
        page_title="Recruitr – AI Resume Analyzer",
        page_icon="🤖",
        layout="wide"
    )

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
    st.markdown("""
    <div class="header-box">
        <h1>🤖 Recruitr</h1>
        <p>AI-powered Resume Analysis, Interview Prep & Resume Improvement</p>
    </div>
    """, unsafe_allow_html=True)


# =========================
# Sidebar
# =========================
def setup_sidebar():
    st.sidebar.header("⚙️ Configuration")

    config = {}

    config["openai_api_key"] = st.sidebar.text_input(
        "OpenAI API Key (optional)",
        type="password",
        help="Only required if using OpenAI backend"
    )

    config["cutoff_score"] = st.sidebar.slider(
        "Selection Cutoff (%)",
        50, 100, 80
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "Recruitr analyzes resumes using AI + semantic search.\n\n"
        "• Skill scoring\n"
        "• Interview questions\n"
        "• Resume rewriting\n"
    )

    return config


# =========================
# Tabs
# =========================
def create_tabs():
    return st.tabs([
        "📄 Resume Analysis",
        "💬 Ask About Resume",
        "🎯 Interview Questions",
        "📈 Improvement Suggestions",
        "✨ Rewrite Resume"
    ])


# =========================
# Role Selection
# =========================
def role_selection_section(role_requirements):
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

        with st.expander("View required skills"):
            for skill in role_requirements[role]:
                st.markdown(f"- {skill}")

    else:
        custom_jd = st.file_uploader(
            "Upload Job Description (PDF / TXT)",
            type=["pdf", "txt"]
        )

    return role, custom_jd


# =========================
# Resume Upload
# =========================
def resume_upload_section():
    st.subheader("Upload Resume")

    resume = st.file_uploader(
        "PDF or TXT format",
        type=["pdf", "txt"]
    )

    if resume:
        st.success("Resume uploaded successfully")

    return resume


# =========================
# Analysis Results
# =========================
def display_analysis_results(result):
    if not result:
        return

    st.subheader("📊 Overall Evaluation")

    col1, col2, col3 = st.columns(3)

    col1.metric("Overall Score", f"{result['overall_score']}%")
    col2.metric(
        "Decision",
        "SELECTED ✅" if result["selected"] else "NOT SELECTED ❌"
    )
    col3.metric(
        "Strength Count",
        len(result.get("strengths", []))
    )

    # Skill chart
    st.subheader("Skill Scores")
    skill_scores = result.get("skill_scores", {})

    if skill_scores:
        fig = px.bar(
            x=list(skill_scores.keys()),
            y=list(skill_scores.values()),
            labels={"x": "Skill", "y": "Score (0-10)"},
            color=list(skill_scores.values()),
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Strengths & gaps
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💪 Strengths")
        for s in result.get("strengths", []):
            st.markdown(
                f"<div class='card good'><b>{s}</b></div>",
                unsafe_allow_html=True
            )

    with col2:
        st.subheader("⚠️ Gaps")
        for s in result.get("missing_skills", []):
            st.markdown(
                f"<div class='card bad'><b>{s}</b></div>",
                unsafe_allow_html=True
            )

    # Detailed weaknesses
    if result.get("detailed_weaknesses"):
        st.subheader("🔍 Detailed Feedback")

        for w in result["detailed_weaknesses"]:
            with st.expander(f"{w['skill']} (Score {w['score']}/10)"):
                st.write(w["detail"])
                for s in w.get("suggestions", []):
                    st.markdown(f"- {s}")
                if w.get("example"):
                    st.code(w["example"])


# =========================
# Resume Q&A
# =========================
def resume_qa_section(has_resume, ask_question_func):
    st.subheader("Ask Questions About the Resume")

    if not has_resume:
        st.warning("Analyze a resume first.")
        return

    question = st.text_input("Your question")

    if st.button("Get Answer") and question:
        st.write(ask_question_func(question))


# =========================
# Interview Questions
# =========================
def interview_questions_section(has_resume, generate_questions_func):
    st.subheader("Generate Interview Questions")

    if not has_resume:
        st.warning("Analyze a resume first.")
        return

    types = st.multiselect(
        "Question Types",
        ["Technical", "Behavioral", "Coding", "System Design"],
        default=["Technical", "Behavioral"]
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        index=1
    )

    count = st.slider("Number of Questions", 1, 10, 5)

    if st.button("Generate"):
        questions = generate_questions_func(types, difficulty, count)
        for i, (t, q) in enumerate(questions, 1):
            with st.expander(f"{i}. {t}"):
                st.write(q)


# =========================
# Improvement Suggestions
# =========================
def resume_improvement_section(has_resume, improve_resume_func):
    st.subheader("Resume Improvement Suggestions")

    if not has_resume:
        st.warning("Analyze a resume first.")
        return

    areas = st.multiselect(
        "Improvement Areas",
        [
            "Skills Highlighting",
            "Experience Description",
            "Achievement Quantification",
            "Keyword Optimization",
            "Formatting"
        ]
    )

    role = st.text_input("Target Role (optional)")

    if st.button("Generate Suggestions"):
        data = improve_resume_func(areas, role)
        for area, content in data.items():
            with st.expander(area):
                st.write(content.get("description", ""))
                for s in content.get("specific", []):
                    st.markdown(f"- {s}")


# =========================
# Improved Resume
# =========================
def improved_resume_section(has_resume, get_improved_resume_func):
    st.subheader("Rewrite Resume")

    if not has_resume:
        st.warning("Analyze a resume first.")
        return

    role = st.text_input("Target Role")
    skills = st.text_area("Skills to emphasize")

    if st.button("Generate Resume"):
        text = get_improved_resume_func(role, skills)

        if text:
            st.text_area("Improved Resume", text, height=500)
            st.download_button(
                "Download Resume",
                text,
                file_name="improved_resume.txt"
            )
