import PyPDF2
import docx
import re
import nltk
from typing import List, Dict
import streamlit as st

class ResumeProcessor:
    def __init__(self):
        try:
            # Download NLTK data quietly
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.nltk_available = True
        except:
            self.nltk_available = False
            st.warning("NLTK not available, using basic text processing")
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF resume"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, docx_file):
        """Extract text from DOCX resume"""
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\.\+\#\-]', ' ', text)
        return text.strip()
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text using simple pattern matching"""
        # Comprehensive tech skills list
        tech_skills = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'express', 'django', 'flask',
            'spring', 'laravel', 'rails', 'asp.net', 'jquery', 'bootstrap', 'sass', 'less',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite',
            'cassandra', 'dynamodb', 'neo4j',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
            'terraform', 'ansible', 'chef', 'puppet', 'vagrant', 'linux', 'unix',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
            'numpy', 'matplotlib', 'seaborn', 'jupyter', 'tableau', 'power bi', 'spark', 'hadoop',
            'kafka', 'airflow', 'mlflow',
            
            # Mobile Development
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic',
            
            # Other Technologies
            'microservices', 'rest api', 'graphql', 'websockets', 'oauth', 'jwt', 'agile', 'scrum',
            'ci/cd', 'tdd', 'bdd', 'design patterns', 'algorithms', 'data structures'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in tech_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience using regex patterns"""
        if not text:
            return 0
            
        # Look for patterns like "5 years", "3+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'experience\s*(?:of\s*)?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*year\s*experience'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                years.extend([int(match) for match in matches])
        
        return max(years) if years else 0
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'certificate',
            'b.tech', 'm.tech', 'b.sc', 'm.sc', 'mba', 'bba', 'be', 'me',
            'computer science', 'engineering', 'information technology', 'software'
        ]
        
        found_education = []
        text_lower = text.lower()
        
        for edu in education_keywords:
            if edu in text_lower:
                found_education.append(edu)
        
        return list(set(found_education))
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern
        phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = phones[0]
        
        return contact_info
