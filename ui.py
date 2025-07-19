import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def setup_page():
    """Setup the Streamlit page configuration"""
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .skill-high {
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem;
        display: inline-block;
    }
    
    .skill-medium {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem;
        display: inline-block;
    }
    
    .skill-low {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem;
        display: inline-block;
    }
    
    .weakness-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
    
    .strength-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Recruitr - AI-Powered Resume Analysis</h1>
        <p>Analyze resumes, generate interview questions, and improve candidate profiles</p>
    </div>
    """, unsafe_allow_html=True)


def setup_sidebar():
    """Setup the sidebar with configuration options"""
    st.sidebar.header("Configuration")
    
    config = {}
    
    # OpenAI API Key
    config["openai_api_key"] = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key to enable AI features"
    )
    
    # Cutoff Score
    config["cutoff_score"] = st.sidebar.slider(
        "Selection Cutoff Score",
        min_value=50,
        max_value=100,
        value=80,
        help="Minimum score for candidate selection"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This tool uses AI to analyze resumes against job requirements, "
        "providing detailed insights and recommendations."
    )
    
    return config


def create_tabs():
    """Create the main navigation tabs"""
    return st.tabs([
        "📋 Resume Analysis",
        "💬 Resume Q&A",
        "🎯 Interview Questions",
        "📈 Resume Improvement",
        "✨ Improved Resume"
    ])


def role_selection_section(role_requirements):
    """Create the role selection section"""
    st.header("Job Role Selection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_predefined = st.radio(
            "Choose analysis method:",
            ["Use predefined role", "Upload custom job description"],
            key="role_selection"
        )
    
    role = None
    custom_jd = None
    
    if use_predefined == "Use predefined role":
        with col2:
            role = st.selectbox(
                "Select target role:",
                options=list(role_requirements.keys()),
                key="role_select"
            )
            
        # Display role requirements
        if role:
            st.subheader(f"{role} Requirements")
            requirements = role_requirements[role]
            
            # Display as columns
            cols = st.columns(3)
            for i, req in enumerate(requirements):
                with cols[i % 3]:
                    st.markdown(f"• {req}")
    
    else:
        st.subheader("📄 Upload Job Description")
        custom_jd = st.file_uploader(
            "Upload job description (PDF or TXT)",
            type=['pdf', 'txt'],
            key="custom_jd_upload"
        )
        
        if custom_jd:
            st.success("✅ Job description uploaded successfully!")
    
    return role, custom_jd


def resume_upload_section():
    """Create the resume upload section"""
    st.header("📄 Resume Upload")
    
    uploaded_file = st.file_uploader(
        "Upload resume (PDF or TXT)",
        type=['pdf', 'txt'],
        key="resume_upload",
        help="Upload the candidate's resume for analysis"
    )
    
    if uploaded_file:
        st.success("✅ Resume uploaded successfully!")
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size} bytes")
        with col3:
            st.metric("File Type", uploaded_file.type)
    
    return uploaded_file


def display_analysis_results(analysis_result):
    """Display the analysis results"""
    if not analysis_result:
        return
    
    st.header("Analysis Results")
    
    # Overall Score
    overall_score = analysis_result.get('overall_score', 0)
    selected = analysis_result.get('selected', False)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Overall Score",
            f"{overall_score}%",
            delta=f"{overall_score - 70}% vs baseline"
        )
    
    with col2:
        st.metric(
            "Selection Status",
            "✅ SELECTED" if selected else "❌ NOT SELECTED",
            delta="Passed" if selected else "Failed"
        )
    
    with col3:
        skill_scores = analysis_result.get('skill_scores', {})
        avg_skill_score = sum(skill_scores.values()) / len(skill_scores) if skill_scores else 0
        st.metric(
            "Avg Skill Score",
            f"{avg_skill_score:.1f}/10",
            delta=f"{avg_skill_score - 5:.1f} vs median"
        )
    
    # Score Distribution Chart
    if skill_scores:
        st.subheader("📈 Skill Score Distribution")
        
        fig = px.bar(
            x=list(skill_scores.keys()),
            y=list(skill_scores.values()),
            title="Skill Scores (0-10 scale)",
            color=list(skill_scores.values()),
            color_continuous_scale="RdYlGn"
        )
        fig.update_layout(
            xaxis_title="Skills",
            yaxis_title="Score",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💪 Strengths")
        strengths = analysis_result.get('strengths', [])
        if strengths:
            for strength in strengths:
                score = skill_scores.get(strength, 0)
                st.markdown(f"""
                <div class="strength-card">
                    <strong>{strength}</strong><br>
                    <small>Score: {score}/10</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific strengths identified")
    
    with col2:
        st.subheader("🔍 Areas for Improvement")
        missing_skills = analysis_result.get('missing_skills', [])
        if missing_skills:
            for skill in missing_skills:
                score = skill_scores.get(skill, 0)
                st.markdown(f"""
                <div class="weakness-card">
                    <strong>{skill}</strong><br>
                    <small>Score: {score}/10</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No major weaknesses identified!")
    
    # Detailed Weaknesses
    detailed_weaknesses = analysis_result.get('detailed_weaknesses', [])
    if detailed_weaknesses:
        st.subheader("🔎 Detailed Weakness Analysis")
        
        for weakness in detailed_weaknesses:
            with st.expander(f"📌 {weakness.get('skill', 'Unknown Skill')} (Score: {weakness.get('score', 0)}/10)"):
                st.markdown(f"**Issue:** {weakness.get('detail', 'No details available')}")
                
                suggestions = weakness.get('suggestions', [])
                if suggestions:
                    st.markdown("**Improvement Suggestions:**")
                    for i, suggestion in enumerate(suggestions, 1):
                        st.markdown(f"{i}. {suggestion}")
                
                example = weakness.get('example', '')
                if example:
                    st.markdown("**Example Addition:**")
                    st.code(example, language=None)
    
    # Skill Reasoning
    skill_reasoning = analysis_result.get('skill_reasoning', {})
    if skill_reasoning:
        st.subheader("🧠 AI Reasoning")
        
        for skill, reasoning in skill_reasoning.items():
            if reasoning.strip():
                with st.expander(f"Reasoning for {skill}"):
                    st.write(reasoning)


def resume_qa_section(has_resume, ask_question_func):
    """Create the resume Q&A section"""
    st.header("💬 Resume Q&A")
    
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    st.markdown("Ask specific questions about the candidate's resume:")
    
    # Predefined questions
    st.subheader(" Common Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("What is the candidate's experience level?"):
            response = ask_question_func("What is the candidate's total years of experience?")
            st.write("**Answer:**", response)
    
    with col2:
        if st.button("What are their key technical skills?"):
            response = ask_question_func("What are the candidate's main technical skills and technologies?")
            st.write("**Answer:**", response)
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("What projects have they worked on?"):
            response = ask_question_func("What notable projects or achievements are mentioned in the resume?")
            st.write("**Answer:**", response)
    
    with col4:
        if st.button("What is their educational background?"):
            response = ask_question_func("What is the candidate's educational background and qualifications?")
            st.write("**Answer:**", response)
    
    # Custom question
    st.subheader("❓ Ask Custom Question")
    
    question = st.text_input("Enter your question about the resume:")
    
    if st.button("🔍 Get Answer") and question:
        response = ask_question_func(question)
        st.write("**Answer:**", response)


def interview_questions_section(has_resume, generate_questions_func):
    """Create the interview questions section"""
    st.header("Interview Questions Generator")
    
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    st.markdown("Generate personalized interview questions based on the candidate's profile:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        question_types = st.multiselect(
            "Question Types",
            ["Technical", "Behavioral", "Coding", "System Design", "Experience"],
            default=["Technical", "Behavioral"],
            key="question_types"
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard"],
            index=1,
            key="difficulty"
        )
    
    with col3:
        num_questions = st.slider(
            "Number of Questions",
            min_value=1,
            max_value=15,
            value=5,
            key="num_questions"
        )
    
    if st.button("Generate Questions", type="primary"):
        if question_types:
            questions = generate_questions_func(question_types, difficulty, num_questions)
            
            if questions:
                st.subheader("Generated Interview Questions")
                
                for i, (q_type, question) in enumerate(questions, 1):
                    with st.expander(f"Question {i}: {q_type}"):
                        st.markdown(f"**Type:** {q_type}")
                        st.markdown(f"**Question:** {question}")
                        
                        # Add copy button
                        if st.button(f"Copy Question {i}", key=f"copy_{i}"):
                            st.code(question, language=None)
            else:
                st.warning("No questions generated. Please try again.")
        else:
            st.warning("Please select at least one question type.")


def resume_improvement_section(has_resume, improve_resume_func):
    """Create the resume improvement section"""
    st.header("📈 Resume Improvement Suggestions")
    
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    st.markdown("Get specific suggestions to improve the resume:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        improvement_areas = st.multiselect(
            "Select improvement areas:",
            [
                "Skills Highlighting",
                "Experience Description",
                "Achievement Quantification",
                "Keyword Optimization",
                "Format & Structure",
                "Education Section",
                "Project Descriptions"
            ],
            default=["Skills Highlighting", "Achievement Quantification"],
            key="improvement_areas"
        )
    
    with col2:
        target_role = st.text_input(
            "Target Role (optional):",
            placeholder="e.g., Senior Software Engineer",
            key="target_role_improvement"
        )
    
    if st.button("Generate Improvements", type="primary"):
        if improvement_areas:
            improvements = improve_resume_func(improvement_areas, target_role)
            
            if improvements:
                st.subheader("💡 Improvement Suggestions")
                
                for area, details in improvements.items():
                    with st.expander(f"📌 {area}"):
                        st.markdown(f"**Overview:** {details.get('description', 'No description available')}")
                        
                        specific_suggestions = details.get('specific', [])
                        if specific_suggestions:
                            st.markdown("**Specific Suggestions:**")
                            for i, suggestion in enumerate(specific_suggestions, 1):
                                st.markdown(f"{i}. {suggestion}")
                        
                        before_after = details.get('before_after', {})
                        if before_after:
                            st.markdown("**Before/After Example:**")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Before:**")
                                st.code(before_after.get('before', ''), language=None)
                            
                            with col2:
                                st.markdown("**After:**")
                                st.code(before_after.get('after', ''), language=None)
            else:
                st.warning("No improvements generated. Please try again.")
        else:
            st.warning("Please select at least one improvement area.")


def improved_resume_section(has_resume, get_improved_resume_func):
    """Create the improved resume section"""
    st.header("Generate Improved Resume")
    
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    st.markdown("Generate an optimized version of the resume:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_role = st.text_input(
            "Target Role:",
            placeholder="e.g., Senior Data Scientist",
            key="target_role_improved"
        )
    
    with col2:
        highlight_skills = st.text_area(
            "Skills to Highlight (comma-separated or job description):",
            placeholder="Python, Machine Learning, TensorFlow, etc.",
            height=100,
            key="highlight_skills"
        )
    
    if st.button("Generate Improved Resume", type="primary"):
        improved_resume = get_improved_resume_func(target_role, highlight_skills)
        
        if improved_resume and improved_resume != "Error generating improved resume":
            st.subheader("Improved Resume")
            
            # Display improved resume
            st.text_area(
                "Improved Resume Content:",
                value=improved_resume,
                height=600,
                key="improved_resume_display"
            )
            
            # Download button
            st.download_button(
                label="⬇️ Download Improved Resume",
                data=improved_resume,
                file_name="improved_resume.txt",
                mime="text/plain"
            )
            
            # Comparison section
            st.subheader("Improvement Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Content Length",
                    f"{len(improved_resume.split())} words",
                    delta="Optimized"
                )
            
            with col2:
                st.metric(
                    "Structure",
                    "Enhanced",
                    delta="Improved"
                )
            
            with col3:
                st.metric(
                    "ATS Optimization",
                    "Optimized",
                    delta="Keywords Added"
                )
            
        else:
            st.error("Failed to generate improved resume. Please try again.")