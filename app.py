import streamlit as st

st.set_page_config(
    page_title = "Recruitr - AI-Powered Recruitment",
    page_icon = "🤖",
    layout = "wide"
)

import ui 
from agents import ResumeAnalyzer
import atexit  



ROLE_REQUIREMENTS = {
    "AI/ML Engineer": [
        "Python", "PyTorch", "TensorFlow", "Machine Learning", "Deep Learning",
        "MLOps", "Scikit-Learn", "NLP", "Computer Vision", "Reinforcement Learning",
        "Hugging Face", "Data Engineering", "Feature Engineering", "AutoML"
    ],
    "Frontend Engineer": [
        "React", "Vue", "Angular", "HTML5", "CSS3", "JavaScript", "TypeScript",
        "Next.js", "Svelte", "Bootstrap", "Tailwind CSS", "GraphQL", "Redux",
        "WebAssembly", "Three.js", "Performance Optimization"
    ],
    "Backend Engineer": [
        "Python", "Java", "Node.js", "REST APIs", "Cloud services", "Kubernetes",
        "Docker", "GraphQL", "Microservices", "gRPC", "Spring Boot", "Flask",
        "FastAPI", "SQL & NoSQL Databases", "Redis", "RabbitMQ", "CI/CD"
    ],
    "Data Engineer": [
        "Python", "SQL", "ETL Pipelines", "Apache Spark", "Airflow", "Kafka",
        "Data Warehousing", "AWS/GCP/Azure", "Data Lakes", "BigQuery",
        "Snowflake", "DBT", "Distributed Systems", "Data Modeling", "Scala"
    ],
    "Data Scientist": [
        "Python", "R", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Matplotlib",
        "Seaborn", "Statistics", "Hypothesis Testing", "Machine Learning",
        "Deep Learning", "Data Visualization", "Feature Engineering",
        "EDA", "Storytelling with Data", "A/B Testing", "BigQuery", "Jupyter Notebook"
    ],
    "DevOps Engineer": [
        "Linux", "Docker", "Kubernetes", "AWS/GCP/Azure", "CI/CD", "Terraform",
        "Ansible", "Jenkins", "Git", "Monitoring (Prometheus/Grafana)",
        "Scripting (Bash/Python)", "Networking Basics", "System Design",
        "Incident Management", "Logging & Alerting"
    ],
    "Full Stack Developer": [
        "HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Node.js",
        "Express.js", "MongoDB", "SQL", "Next.js", "Tailwind CSS", "Redux",
        "REST APIs", "GraphQL", "Authentication", "Testing", "Docker", "CI/CD"
    ],
    "Product Manager": [
        "Product Lifecycle", "Agile Methodology", "JIRA", "User Research",
        "Wireframing", "A/B Testing", "Market Analysis", "KPIs & Metrics",
        "Roadmapping", "Stakeholder Communication", "Figma", "Data-driven Decision Making",
        "Basic SQL", "Competitor Analysis", "Storytelling", "Prioritization Frameworks"
    ]
}


if 'resume_agent' not in st.session_state:
    st.session_state.resume_agent = None

if 'resume_analyzed' not in st.session_state:
    st.session_state.resume_analyzed = False

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None


def setup_agent(config):
    """set up the resume analysis agent with the provided configuration"""
    if not  config["openai_api_key"]:
        st.error("OpenAI API key is required to run the agent.")
        return None
    

    if st.session_state.resume_agent is None:
        st.session_state.resume_agent = ResumeAnalyzer(api_key=config["openai_api_key"])
    else:
        st.session_state.resume_agent.api_key  = config["openai_api_key"]
    return st.session_state.resume_agent

def analyze_resume(agent, resume_file, role, custom_jd):
    """analyze the resume with the agent """

    if not resume_file:
        st.error("Please upload a resume file.")
        return None
    
    try:
        with st.spinner("🔍 Analyzing_resume... This may take a minute."):
            if custom_jd:
                result = agent.analyze_resume(resume_file, custom_jd = custom_jd)
            else:
                result = agent.analyze_resume(resume_file,role_requirements = ROLE_REQUIREMENTS[role])

            st.session_state.analysis_result = result
            st.session_state.resume_analyzed = True
            return result 
    except Exception as e:
        st.error(f"Error analyzing resume: {e}")
        return None

def ask_question(agent, question):
    """ask a question about the resume"""
    try:
        with st.spinner("Generating response..."):
            response = agent.ask_question(question)
            return response
    except Exception as e:
        return f"Error: {e}"

def generate_interview_questions(agent, question_types, difficulty, num_questions):
    """generating interview questions based on the resume"""
    try:
        with st.spinner("Generating interview questions..."):
            questions = agent.generate_interview_questions(question_types,difficulty,num_questions)

            return questions
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

def improve_resume(agent, improvement_areas,target_role):
    """Generate resume improvements suggestions"""

    try:
        with st.spinner("Analyzing and generating improvements..."):
            return agent.improve_resume(improvement_areas, target_role)
    except Exception as e:
        st.error(f"Error generating improvements: {e}")
        return {}
        
                                              
def get_improved_resume(agent, target_role, highlight_skills):
    """Get an improved version of the resume"""

    try:
        with st.spinner("Generating improved resume..."):
            return agent.get_improved_resume(target_role, highlight_skills)
    except Exception as e:
        st.error(f"Error generating improved resume: {e}")
        return "Error generating improved resume"
    
def cleanup():
    """clean up resources on exit"""

    if st.session_state.resume_agent:
        st.session_state.resume_agent.cleanup()
atexit.register(cleanup)


def main():
    ui.setup_page()
    ui.display_header()

    config = ui.setup_sidebar()

    agent = setup_agent(config)

    tabs = ui.create_tabs()

    with tabs[0]:
        role, custom_jd = ui.role_selection_section (ROLE_REQUIREMENTS)
        uploaded_resume = ui.resume_upload_section()

        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button("🔍 Analyze Resume", type = "primary"):
                if agent and uploaded_resume:

                    analyze_resume(agent, uploaded_resume, role, custom_jd)

        
        if st.session_state.analysis_result:
            ui.display_analysis_results(st.session_state.analysis_result)

    with tabs[1]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.resume_qa_section(
                has_resume = True, 
                ask_question_func = lambda q: ask_question(st.session_state.resume_agent, q)

            )
        else:
            st.warning("please upload and analyze a resume first in the 'Resume Analysis' tab. ")

    with tabs[2]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.interview_questions_section(
                has_resume = True,
                generate_questions_func = lambda types, diff, num:
                generate_interview_questions(st.session_state.resume_agent, types,diff, num)

            )

        else:
            st.warning("please upload and analyze a resume first in the 'Resume Analysis' tab. ")

    with tabs[3]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.resume_improvement_section(
                has_resume = True,
                improve_resume_func = lambda areas , role: improve_resume(st.session_state.resume_agent, areas, role)

            )
        else:
            st.warning("please upload and analyze a resume first in the 'Resume Analysis' tab. ")

    with tabs[4]:
        if st.session_state.resume_analyzed and st.session_state.resume_agent:
            ui.improved_resume_section(
                has_resume = True,
                get_improved_resume_func = lambda role, skills: get_improved_resume
                (st.session_state.resume_agent, role, skills)
            )
        else:
            st.warning("please upload and analyze a resume first in the 'Resume Analysis' tab. ")

if __name__ == "__main__":
    main()




