import streamlit as st
import atexit

from agents import ResumeAnalyzer
from services.export import export_to_excel, export_to_pdf, export_comparison_to_pdf
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
    "DevOps Engineer": [
        "Linux", "Docker", "Kubernetes", "AWS/GCP/Azure", "CI/CD",
        "Terraform", "Ansible", "Jenkins", "Monitoring", "Prometheus",
        "Grafana", "Shell Scripting", "System Design"
    ],
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

    # -------- TAB 0: Resume Analysis --------
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
            
            # Export single resume report
            st.divider()
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                pdf_data = export_to_pdf(
                    st.session_state.analysis_result,
                    uploaded_resume.name if uploaded_resume else "Resume"
                )
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name="resume_analysis_report.pdf",
                    mime="application/pdf"
                )

    # -------- TAB 1: Bulk Analysis --------
    with tabs[1]:
        ui.bulk_analysis_section(
            analyze_bulk_func=lambda resumes, jd: st.session_state.agent.analyze_bulk_resumes(resumes, jd),
            export_to_excel_func=export_to_excel
        )

    # -------- TAB 2: Comparison Mode --------
    with tabs[2]:
        ui.comparison_section(
            compare_func=lambda a, b, jd: st.session_state.agent.compare_resumes(a, b, jd),
            export_comparison_pdf_func=export_comparison_to_pdf
        )

    # -------- TAB 3: Resume Q&A --------
    with tabs[3]:
        ui.resume_qa_section(
            has_resume=st.session_state.resume_analyzed,
            ask_question_func=lambda q: st.session_state.agent.ask_question(q)
        )

    # -------- TAB 4: Rewrite Resume --------
    with tabs[4]:
        ui.improved_resume_section(
            has_resume=st.session_state.resume_analyzed,
            get_improved_resume_func=lambda role, skills: 
                st.session_state.agent.get_improved_resume(role, skills)
        )

    # -------- TAB 5: Improvement Suggestions --------
    with tabs[5]:
        ui.improvement_suggestions_section(
            has_resume=st.session_state.resume_analyzed,
            analysis_result=st.session_state.analysis_result
        )

    # -------- TAB 6: Interview Questions --------
    with tabs[6]:
        ui.interview_questions_section(
            has_resume=st.session_state.resume_analyzed,
            generate_questions_func=None  # Coming soon
        )


if __name__ == "__main__":
    main()