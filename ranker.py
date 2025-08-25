from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Tuple
import streamlit as st

class ResumeRanker:
    def __init__(self):
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            try:
            # Try to download the model
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                st.error("Spacy model loading failed. Some features may not work properly.")
                self.nlp = None
    
    def calculate_skill_match_score(self, resume_skills: List[str], 
                                  required_skills: List[str]) -> float:
        """Calculate skill matching score"""
        if not required_skills:
            return 0.0
        
        if not resume_skills:
            return 0.0
        
        resume_skills_lower = [skill.lower().strip() for skill in resume_skills]
        required_skills_lower = [skill.lower().strip() for skill in required_skills]
        
        matched_skills = set(resume_skills_lower) & set(required_skills_lower)
        return len(matched_skills) / len(required_skills_lower)
    
    def calculate_text_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        if not resume_text or not job_description:
            return 0.0
            
        try:
            documents = [resume_text, job_description]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity[0][0])
        except Exception as e:
            st.error(f"Error calculating text similarity: {str(e)}")
            return 0.0
    
    def calculate_experience_score(self, resume_experience: int, 
                                 required_experience: int) -> float:
        """Calculate experience matching score"""
        if required_experience == 0:
            return 1.0
        
        if resume_experience >= required_experience:
            return 1.0
        elif resume_experience == 0:
            return 0.0
        else:
            return min(resume_experience / required_experience, 1.0)
    
    def rank_resumes(self, resumes_data: List[Dict], job_requirements: Dict) -> List[Dict]:
        """Main ranking function"""
        ranked_resumes = []
        
        for resume_data in resumes_data:
            try:
                # Calculate individual scores
                skill_score = self.calculate_skill_match_score(
                    resume_data.get('skills', []), 
                    job_requirements.get('required_skills', [])
                )
                
                text_similarity = self.calculate_text_similarity(
                    resume_data.get('text', ''), 
                    job_requirements.get('job_description', '')
                )
                
                experience_score = self.calculate_experience_score(
                    resume_data.get('experience_years', 0),
                    job_requirements.get('min_experience', 0)
                )
                
                # Weighted final score
                final_score = (
                    skill_score * 0.4 +           # 40% weight on skills
                    text_similarity * 0.35 +      # 35% weight on text similarity
                    experience_score * 0.25       # 25% weight on experience
                )
                
                # Find matched skills
                matched_skills = []
                if resume_data.get('skills') and job_requirements.get('required_skills'):
                    resume_skills_lower = [s.lower() for s in resume_data['skills']]
                    required_skills_lower = [s.lower() for s in job_requirements['required_skills']]
                    matched_skills = list(set(resume_skills_lower) & set(required_skills_lower))
                
                resume_result = {
                    'filename': resume_data.get('filename', 'Unknown'),
                    'final_score': final_score,
                    'skill_score': skill_score,
                    'text_similarity': text_similarity,
                    'experience_score': experience_score,
                    'matched_skills': matched_skills,
                    'total_skills': len(resume_data.get('skills', [])),
                    'experience_years': resume_data.get('experience_years', 0),
                    'contact_info': resume_data.get('contact_info', {})
                }
                
                ranked_resumes.append(resume_result)
                
            except Exception as e:
                st.error(f"Error processing {resume_data.get('filename', 'Unknown')}: {str(e)}")
                continue
        
        # Sort by final score (descending)
        ranked_resumes.sort(key=lambda x: x['final_score'], reverse=True)
        
        return ranked_resumes
    
    def get_improvement_suggestions(self, skill_score: float, text_similarity: float, 
                                  experience_score: float, missing_skills: List[str]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if skill_score < 0.3:
            suggestions.append("🎯 **Critical Skill Gap**: You're missing most required skills. Consider learning the key technologies.")
        elif skill_score < 0.6:
            suggestions.append("🎯 **Skill Enhancement**: Focus on learning the missing skills to improve your match.")
        
        if text_similarity < 0.2:
            suggestions.append("📝 **Resume Content**: Your resume content doesn't align well with the job description. Use more relevant keywords.")
        elif text_similarity < 0.4:
            suggestions.append("📝 **Content Optimization**: Tailor your resume to better match the job requirements.")
        
        if experience_score < 0.5:
            suggestions.append("💼 **Experience Gap**: Consider highlighting relevant projects or internships to bridge the experience gap.")
        
        if missing_skills:
            top_missing = missing_skills[:3]
            suggestions.append(f"📚 **Priority Learning**: Focus on these skills: {', '.join(top_missing)}")
        
        if not suggestions:
            suggestions.append("🎉 **Excellent Match**: Your resume aligns well with this position!")
        
        return suggestions
