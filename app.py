import streamlit as st
import atexit

from agents import ResumeAnalyzer
import ui


# -------------------- PAGE CONFIG --------------------

st.set_page_config(
    page_title="Recruitr – AI-Powered Recruitment",
    page_icon="🤖",
    layout="wide"
)

# -------------------- ROLE REQUIREMENTS --------------------

ROLE_REQUIREMENTS = {
    "AI/ML Engineer": [
        "Python", "PyTorch", "TensorFlow", "Machine Learning", "Deep Learning",
        "MLOps", "Scikit-Learn", "NLP", "Computer Vision"
    ],
    "Frontend Engineer": [
        "React", "HTML", "CSS", "JavaScript", "TypeScript", "Next.js", "Tailwind CSS"
    ],
    "Backend Engineer": [
        "Python", "Java", "Node.js", "REST APIs", "Docker", "Kubernetes",
        "FastAPI", "Databases", "CI/CD"
    ],
    "Data Scientist": [
        "Python", "SQL", "Pandas", "NumPy", "Statistics", "Machine Learning",
        "EDA", "Data Visualization"
    ],

    # ✅ NEW ROLE 1
    "DevOps Engineer": [
        "Linux", "Docker", "Kubernetes", "AWS/GCP/Azure", "CI/CD",
        "Terraform", "Ansible", "Jenkins", "Monitoring", "Prometheus",
        "Grafana", "Shell Scripting", "System Design"
    ],

    # ✅ NEW ROLE 2
    "Data Engineer": [
        "Python", "SQL", "ETL Pipelines", "Apache Spark", "Airflow",
        "Kafka", "Data Warehousing", "BigQuery", "Snowflake",
        "Data Modeling", "Distributed Systems", "Cloud Platforms"
    ]
}

# -------------------- SESSION STATE --------------------

if "agent" not in st.session_state:
    st.session_state.agent = ResumeAnalyzer()

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "resume_analyzed" not in st.session_state:
    st.session_state.resume_analyzed = False


# -------------------- CLEANUP --------------------

def cleanup():
    if st.session_state.agent:
        st.session_state.agent.cleanup()

atexit.register(cleanup)


# -------------------- MAIN APP --------------------

def main():
    ui.setup_page()
    ui.display_header()

    tabs = ui.create_tabs()

    # -------- TAB 1: Resume Analysis --------
    with tabs[0]:
        role, custom_jd = ui.role_selection_section(ROLE_REQUIREMENTS)
        uploaded_resume = ui.resume_upload_section()

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔍 Analyze Resume", type="primary"):
                if uploaded_resume:
                    with st.spinner("Analyzing resume…"):
                        result = st.session_state.agent.analyze_resume(
                            resume_file=uploaded_resume,
                            custom_jd=custom_jd
                        )
                        st.session_state.analysis_result = result
                        st.session_state.resume_analyzed = True

        if st.session_state.analysis_result:
            ui.display_analysis_results(st.session_state.analysis_result)

    # -------- TAB 2: Resume Q&A --------
    with tabs[1]:
        if st.session_state.resume_analyzed:
            ui.resume_qa_section(
                has_resume=True,
                ask_question_func=lambda q: st.session_state.agent.ask_question(q)
            )
        else:
            st.warning("Please analyze a resume first.")

    # -------- TAB 3: Improved Resume --------
    with tabs[2]:
        if st.session_state.resume_analyzed:
            ui.improved_resume_section(
                has_resume=True,
                get_improved_resume_func=lambda role:
                st.session_state.agent.get_improved_resume(role)
            )
        else:
            st.warning("Please analyze a resume first.")


if __name__ == "__main__":
    main()
