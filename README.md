# 🎯 AI Resume Analyzer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

An intelligent resume analysis tool that serves both job seekers and HR professionals using advanced NLP techniques.

## 🚀 Live Demo
**Try it now:** [https://your-app-url.streamlit.app](https://your-app-url.streamlit.app)

## ✨ Features

### For Job Seekers 🔍
- Upload your resume and get instant feedback
- Compare against specific job descriptions  
- Get personalized improvement suggestions
- Identify skill gaps and missing keywords

### For HR/Recruiters 👔
- Rank multiple resumes against job requirements
- Get detailed candidate comparisons
- Download ranking reports
- Visualize candidate analytics

## 🛠️ Technologies Used
- **Frontend:** Streamlit
- **NLP:** Spacy, Scikit-learn (TF-IDF, Cosine Similarity)
- **Data Processing:** Pandas, NumPy
- **File Processing:** PyPDF2, python-docx
- **Visualizations:** Plotly
- **Deployment:** Streamlit Cloud

## 📊 Key Algorithms
- **Text Similarity:** TF-IDF Vectorization + Cosine Similarity
- **Skill Matching:** Pattern matching with comprehensive tech skills database
- **Experience Extraction:** Regex-based pattern recognition
- **Weighted Scoring:** Configurable multi-factor ranking system

## 🏃‍♂️ Quick Start

### Local Installation
```bash
git clone https://github.com/your-username/ai-resume-analyzer.git
cd ai-resume-analyzer
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
