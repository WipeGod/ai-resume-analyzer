import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from resume_processor import ResumeProcessor
from ranker import ResumeRanker
import time

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

@st.cache_resource
def load_processors():
    return ResumeProcessor(), ResumeRanker()

def main():
    st.title("🎯 AI Resume Analyzer")
    st.markdown("**Intelligent Resume Analysis for Job Seekers and Recruiters**")
    
    mode = st.radio(
        "Choose your mode:",
        ["🔍 Job Seeker - Check My Resume", "👔 HR/Recruiter - Rank Multiple Resumes"],
        horizontal=True
    )
    
    if mode == "🔍 Job Seeker - Check My Resume":
        job_seeker_mode()
    else:
        hr_recruiter_mode()

def job_seeker_mode():
    """Mode for individual job seekers to check their resume"""
    st.header("🔍 Check Your Resume Against Job Requirements")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Your Resume")
        uploaded_resume = st.file_uploader(
            "Upload your resume",
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format"
        )
        
        if uploaded_resume:
            st.success("✅ Resume uploaded successfully!")
    
    with col2:
        st.subheader("💼 Job You're Applying For")
        job_title = st.text_input("Job Title", "Software Engineer")
        
        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the complete job description here...",
            height=200
        )
        
        required_skills = st.text_input(
            "Key Skills Required (comma-separated)",
            placeholder="python, react, sql, machine learning"
        )
        
        min_experience = st.number_input("Minimum Experience (years)", 0, 20, 0)
    
    if st.button("🚀 Analyze My Resume", type="primary"):
        if uploaded_resume and job_description:
            analyze_single_resume(uploaded_resume, job_title, job_description, required_skills, min_experience)
        else:
            st.error("Please upload your resume and provide job description!")

def analyze_single_resume(uploaded_resume, job_title, job_description, required_skills, min_experience):
    """Analyze single resume for job seeker"""
    processor, ranker = load_processors()
    
    with st.spinner("🔄 Analyzing your resume..."):
        if uploaded_resume.type == "application/pdf":
            text = processor.extract_text_from_pdf(uploaded_resume)
        else:
            text = processor.extract_text_from_docx(uploaded_resume)
        
        if not text:
            st.error("Could not extract text from your resume. Please check the file format.")
            return
        
        cleaned_text = processor.clean_text(text)
        resume_skills = processor.extract_skills(text)
        experience_years = processor.extract_experience_years(text)
        education = processor.extract_education(text)
        contact_info = processor.extract_contact_info(text)
        
        required_skills_list = [skill.strip().lower() for skill in required_skills.split(',') if skill.strip()]
        
        job_requirements = {
            'job_description': job_description,
            'required_skills': required_skills_list,
            'min_experience': min_experience
        }
        
        skill_score = ranker.calculate_skill_match_score(resume_skills, required_skills_list)
        text_similarity = ranker.calculate_text_similarity(cleaned_text, job_description)
        experience_score = ranker.calculate_experience_score(experience_years, min_experience)
        
        overall_score = (skill_score * 0.4 + text_similarity * 0.35 + experience_score * 0.25)
        
        display_personal_analysis(
            overall_score, skill_score, text_similarity, experience_score,
            resume_skills, required_skills_list, experience_years, job_title, ranker
        )

def display_personal_analysis(overall_score, skill_score, text_similarity, experience_score,
                            resume_skills, required_skills, experience_years, job_title, ranker):
    """Display personalized analysis for job seeker"""
    
    st.header("📊 Your Resume Analysis Results")
    
    if overall_score >= 0.8:
        score_color = "🟢"
        message = "Excellent match! You're a strong candidate."
    elif overall_score >= 0.6:
        score_color = "🟡"
        message = "Good match! Consider highlighting relevant experience."
    else:
        score_color = "🔴"
        message = "Needs improvement. Focus on missing skills."
    
    st.markdown(f"## {score_color} Overall Match Score: {overall_score:.1%}")
    st.markdown(f"**{message}**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Skill Match", f"{skill_score:.1%}")
    
    with col2:
        st.metric("📝 Content Relevance", f"{text_similarity:.1%}")
    
    with col3:
        st.metric("💼 Experience Match", f"{experience_score:.1%}")
    
    with col4:
        st.metric("📚 Experience Years", f"{experience_years} years")
    
    st.subheader("🔧 Skills Analysis")
    
    matched_skills = list(set([s.lower() for s in resume_skills]) & set(required_skills))
    missing_skills = list(set(required_skills) - set([s.lower() for s in resume_skills]))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✅ Skills You Have:**")
        if matched_skills:
            for skill in matched_skills:
                st.markdown(f"- ✅ {skill.title()}")
        else:
            st.markdown("- No direct skill matches found")
    
    with col2:
        st.markdown("**❌ Skills You're Missing:**")
        if missing_skills:
            for skill in missing_skills:
                st.markdown(f"- ❌ {skill.title()}")
        else:
            st.markdown("- You have all required skills! 🎉")
    
    st.subheader("💡 Improvement Suggestions")
    
    suggestions = ranker.get_improvement_suggestions(
        skill_score, text_similarity, experience_score, missing_skills
    )
    
    for suggestion in suggestions:
        st.markdown(suggestion)

def hr_recruiter_mode():
    """Mode for HR/Recruiters to rank multiple resumes"""
    st.header("👔 Rank Multiple Resumes")
    
    with st.sidebar:
        st.header("📋 Job Requirements")
        
        job_title = st.text_input("Job Title", "Software Engineer")
        
        job_description = st.text_area(
            "Job Description",
            "We are looking for a skilled software engineer with experience in Python, machine learning, and web development.",
            height=150
        )
        
        required_skills = st.text_area(
            "Required Skills (comma-separated)",
            "python, machine learning, flask, sql, git"
        ).split(',')
        required_skills = [skill.strip().lower() for skill in required_skills if skill.strip()]
        
        min_experience = st.number_input("Minimum Experience (years)", 0, 20, 2)
        
        job_requirements = {
            'job_title': job_title,
            'job_description': job_description,
            'required_skills': required_skills,
            'min_experience': min_experience
        }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 Upload Resumes")
        uploaded_files = st.file_uploader(
            "Choose resume files",
            accept_multiple_files=True,
            type=['pdf', 'docx']
        )
        
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} resume(s)")
    
    with col2:
        st.header("⚙️ Processing Options")
        
        if st.button("🚀 Rank Resumes", type="primary"):
            if uploaded_files:
                rank_resumes(uploaded_files, job_requirements)
            else:
                st.error("Please upload at least one resume!")

def rank_resumes(uploaded_files, job_requirements):
    """Process and rank uploaded resumes"""
    processor, ranker = load_processors()
    
    with st.spinner("Processing resumes..."):
        resumes_data = []
        
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                text = processor.extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = processor.extract_text_from_docx(uploaded_file)
            else:
                continue
            
            if text:
                cleaned_text = processor.clean_text(text)
                skills = processor.extract_skills(text)
                experience = processor.extract_experience_years(text)
                education = processor.extract_education(text)
                contact_info = processor.extract_contact_info(text)
                
                resumes_data.append({
                    'filename': uploaded_file.name,
                    'text': cleaned_text,
                    'skills': skills,
                    'experience_years': experience,
                    'education': education,
                    'contact_info': contact_info
                })
    
    if not resumes_data:
        st.error("Could not process any resumes. Please check file formats.")
        return
    
    ranked_results = ranker.rank_resumes(resumes_data, job_requirements)
    
    display_ranking_results(ranked_results, job_requirements)

def display_ranking_results(ranked_results, job_requirements):
    """Display ranking results with visualizations"""
    
    st.header("🏆 Ranking Results")
    
    tab1, tab2, tab3 = st.tabs(["📊 Rankings", "📈 Analytics", "📋 Report"])
    
    with tab1:
        for i, result in enumerate(ranked_results):
            with st.expander(f"#{i+1} - {result['filename']} (Score: {result['final_score']:.2f})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Overall Score", f"{result['final_score']:.2f}")
                    st.metric("Experience", f"{result['experience_years']} years")
                
                with col2:
                    st.metric("Skill Match", f"{result['skill_score']:.2f}")
                    st.metric("Text Similarity", f"{result['text_similarity']:.2f}")
                
                with col3:
                    st.metric("Experience Match", f"{result['experience_score']:.2f}")
                    st.metric("Total Skills", result['total_skills'])
                
                if result['matched_skills']:
                    st.write("**Matched Skills:**", ", ".join(result['matched_skills']))
    
    with tab2:
        if ranked_results:
            df = pd.DataFrame(ranked_results)
            
            fig1 = px.bar(
                df, 
                x='filename', 
                y='final_score',
                title='Resume Scores Comparison',
                color='final_score',
                color_continuous_scale='viridis'
            )
            fig1.update_xaxis(tickangle=45)
            st.plotly_chart(fig1, use_container_width=True)
    
    with tab3:
        st.subheader("📋 Detailed Ranking Report")
        
        if ranked_results:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Resumes", len(ranked_results))
            with col2:
                avg_score = sum(r['final_score'] for r in ranked_results) / len(ranked_results)
                st.metric("Average Score", f"{avg_score:.2f}")
            with col3:
                top_score = ranked_results[0]['final_score']
                st.metric("Top Score", f"{top_score:.2f}")
            with col4:
                qualified = sum(1 for r in ranked_results if r['final_score'] > 0.5)
                st.metric("Qualified Candidates", qualified)
            
            report_df = pd.DataFrame(ranked_results)
            csv = report_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Report (CSV)",
                data=csv,
                file_name=f"resume_ranking_report.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
