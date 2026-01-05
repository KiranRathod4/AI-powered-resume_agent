import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


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
        .ats-excellent { background: #d4edda; border-left: 4px solid #28a745; }
        .ats-good { background: #d1ecf1; border-left: 4px solid #17a2b8; }
        .ats-fair { background: #fff3cd; border-left: 4px solid #ffc107; }
        .ats-poor { background: #f8d7da; border-left: 4px solid #dc3545; }
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
# Tabs - NOW 8 TABS
# =========================
def create_tabs():
    """Create main navigation tabs"""
    return st.tabs([
        "📄 Resume Analysis",
        "📦 Bulk Analysis",         # NEW
        "⚖️ Compare Resumes",       # NEW
        "💬 Ask About Resume",
        "✨ Rewrite Resume",
        "📈 Improvement Suggestions",
        "🎯 Interview Questions"
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
# ATS Score Display (NEW)
# =========================
def display_ats_score(ats_result):
    """Display ATS compatibility score"""
    if not ats_result:
        return
    
    score = ats_result['score']
    grade = ats_result['grade']
    
    # Determine color based on score
    if score >= 80:
        color = "#28a745"
        css_class = "ats-excellent"
    elif score >= 70:
        color = "#17a2b8"
        css_class = "ats-good"
    elif score >= 60:
        color = "#ffc107"
        css_class = "ats-fair"
    else:
        color = "#dc3545"
        css_class = "ats-poor"
    
    st.divider()
    st.subheader("🎯 ATS Compatibility Score")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "ATS Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
        <div class='card {css_class}'>
            <h3 style='margin:0'>{grade}</h3>
            <p style='margin:0'>Score: {score}/100</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Score Breakdown")
        breakdown = ats_result['breakdown']
        
        for category, details in breakdown.items():
            score_pct = (details['score'] / details['max']) * 100
            st.markdown(f"**{category}**: {details['score']:.1f}/{details['max']}")
            st.progress(score_pct / 100)
            st.caption(details['details'])
    
    # Recommendations
    if ats_result['recommendations']:
        with st.expander("💡 Improvement Recommendations"):
            for rec in ats_result['recommendations']:
                st.markdown(f"- {rec}")


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
    col1, col2, col3, col4 = st.columns(4)

    overall_score = result.get('overall_score', 0)
    ats_score = result.get('ats_score', {}).get('score', 0)
    
    col1.metric("Overall Score", f"{overall_score}%")
    col2.metric("ATS Score", f"{ats_score}/100")
    col3.metric(
        "Decision",
        "✅ SELECTED" if result.get("selected", False) else "❌ NOT SELECTED"
    )
    col4.metric(
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
    
    # ATS Score Section
    display_ats_score(result.get('ats_score'))


# =========================
# Bulk Analysis Section (NEW)
# =========================
def bulk_analysis_section(analyze_bulk_func, export_to_excel_func):
    """Bulk resume analysis interface"""
    st.subheader("📦 Bulk Resume Analysis")
    st.info("Upload multiple resumes to analyze them all at once (up to 50)")
    
    # Job description
    custom_jd = st.file_uploader(
        "Upload Job Description (Required)",
        type=["pdf", "txt"],
        key="bulk_jd"
    )
    
    # Resume uploads
    resumes = st.file_uploader(
        "Upload Resumes (PDF or TXT)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key="bulk_resumes"
    )
    
    if resumes:
        st.success(f"✅ {len(resumes)} resumes uploaded")
    
    if st.button("🔍 Analyze All Resumes", type="primary"):
        if not custom_jd:
            st.warning("⚠️ Please upload a job description")
        elif not resumes:
            st.warning("⚠️ Please upload at least one resume")
        elif len(resumes) > 50:
            st.error("❌ Maximum 50 resumes allowed")
        else:
            with st.spinner(f"Analyzing {len(resumes)} resumes... This may take a while"):
                results = analyze_bulk_func(resumes, custom_jd)
                
                if results:
                    st.success(f"✅ Analyzed {len(results)} resumes!")
                    
                    # Summary table
                    st.subheader("📊 Results Summary")
                    
                    summary_data = []
                    for item in results:
                        result = item['result']
                        if 'error' not in result:
                            summary_data.append({
                                'Resume': item['name'],
                                'Overall Score': f"{result['overall_score']}%",
                                'ATS Score': f"{result.get('ats_score', {}).get('score', 0)}/100",
                                'Selected': '✅' if result['selected'] else '❌',
                                'Strengths': len(result['strengths']),
                                'Gaps': len(result['missing_skills'])
                            })
                    
                    st.dataframe(summary_data, use_container_width=True)
                    
                    # Export button
                    st.divider()
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        excel_data = export_to_excel_func(results)
                        st.download_button(
                            label="📥 Download Excel Report",
                            data=excel_data,
                            file_name="bulk_resume_analysis.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    # Detailed results
                    with st.expander("📄 View Detailed Results"):
                        for item in results:
                            st.markdown(f"### {item['name']}")
                            display_analysis_results(item['result'])
                            st.divider()


# =========================
# Comparison Section (NEW)
# =========================
def comparison_section(compare_func, export_comparison_pdf_func):
    """Resume comparison interface"""
    st.subheader("⚖️ Compare Two Resumes")
    st.info("Upload two resumes to see a side-by-side comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Resume A")
        resume_a = st.file_uploader(
            "Upload first resume",
            type=["pdf", "txt"],
            key="compare_a"
        )
    
    with col2:
        st.markdown("### Resume B")
        resume_b = st.file_uploader(
            "Upload second resume",
            type=["pdf", "txt"],
            key="compare_b"
        )
    
    custom_jd = st.file_uploader(
        "Upload Job Description (Required)",
        type=["pdf", "txt"],
        key="compare_jd"
    )
    
    if st.button("⚖️ Compare Resumes", type="primary"):
        if not all([resume_a, resume_b, custom_jd]):
            st.warning("⚠️ Please upload both resumes and job description")
        else:
            with st.spinner("Comparing resumes..."):
                comparison_data = compare_func(resume_a, resume_b, custom_jd)
                
                if comparison_data:
                    st.success("✅ Comparison complete!")
                    
                    # Winner announcement
                    comp = comparison_data['comparison']
                    st.markdown(f"## 🏆 Winner: {comp['winner']}")
                    st.divider()
                    
                    # Comparison metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Resume A Score",
                            f"{comp['scores']['resume_a']}%"
                        )
                        st.metric(
                            "Resume A ATS",
                            f"{comp['ats_scores']['resume_a']}/100"
                        )
                    
                    with col2:
                        st.metric(
                            "Score Difference",
                            f"{abs(comp['scores']['resume_a'] - comp['scores']['resume_b'])}%"
                        )
                        st.metric(
                            "ATS Difference",
                            f"{abs(comp['ats_scores']['resume_a'] - comp['ats_scores']['resume_b'])}"
                        )
                    
                    with col3:
                        st.metric(
                            "Resume B Score",
                            f"{comp['scores']['resume_b']}%"
                        )
                        st.metric(
                            "Resume B ATS",
                            f"{comp['ats_scores']['resume_b']}/100"
                        )
                    
                    # Side-by-side comparison chart
                    st.subheader("📊 Visual Comparison")
                    
                    fig = go.Figure(data=[
                        go.Bar(name='Resume A', x=['Overall', 'ATS', 'Strengths'], 
                               y=[comp['scores']['resume_a'], comp['ats_scores']['resume_a'], comp['strengths_count']['resume_a']]),
                        go.Bar(name='Resume B', x=['Overall', 'ATS', 'Strengths'], 
                               y=[comp['scores']['resume_b'], comp['ats_scores']['resume_b'], comp['strengths_count']['resume_b']])
                    ])
                    fig.update_layout(barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.expander("📄 Resume A Details"):
                            display_analysis_results(comparison_data['resume_a'])
                    
                    with col2:
                        with st.expander("📄 Resume B Details"):
                            display_analysis_results(comparison_data['resume_b'])
                    
                    # Export comparison
                    st.divider()
                    pdf_data = export_comparison_pdf_func(comparison_data)
                    st.download_button(
                        label="📥 Download Comparison Report (PDF)",
                        data=pdf_data,
                        file_name="resume_comparison.pdf",
                        mime="application/pdf"
                    )


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
# Improved Resume Section
# =========================
def improved_resume_section(has_resume, get_improved_resume_func):
    """Resume rewriting interface"""
    st.subheader("✨ Rewrite Resume for Target Role")

    if not has_resume:
        st.warning("⚠️ Please analyze a resume first in the 'Resume Analysis' tab.")
        return

    role = st.text_input(
        "Target Role",
        placeholder="e.g., Senior Data Scientist"
    )

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
                        
                        st.markdown("### Improved Resume:")
                        st.text_area(
                            "Preview",
                            improved_text,
                            height=500,
                            label_visibility="collapsed"
                        )
                        
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
        st.info("No analysis results available. Please analyze a resume first.")
        return

    missing_skills = analysis_result.get("missing_skills", [])
    if missing_skills:
        st.markdown("### ⚠️ Skills to Develop")
        st.write("Consider improving or adding these skills to your resume:")
        for skill in missing_skills:
            score = analysis_result.get("skill_scores", {}).get(skill, 0)
            st.markdown(f"- **{skill}** (Current score: {score}/10)")
        st.divider()

    strengths = analysis_result.get("strengths", [])
    if strengths:
        st.markdown("### 💪 Strengths to Emphasize")
        st.write("Make sure these skills are prominently featured:")
        for skill in strengths:
            score = analysis_result.get("skill_scores", {}).get(skill, 0)
            st.markdown(f"- **{skill}** (Score: {score}/10)")
        st.divider()

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
# Interview Questions Section
# =========================
def interview_questions_section(has_resume, generate_questions_func=None):
    """Interview questions generation interface"""
    st.subheader("🎯 Generate Interview Questions")

    if not has_resume:
        st.warning("⚠️ Please analyze a resume first in the 'Resume Analysis' tab.")
        return

    types = st.multiselect(
        "Question Types",
        ["Technical", "Behavioral", "Coding", "System Design"],
        default=["Technical", "Behavioral"]
    )

    difficulty = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1
    )

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