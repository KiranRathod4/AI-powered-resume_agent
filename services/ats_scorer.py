import re


def calculate_ats_score(resume_text):
    """
    Calculate ATS compatibility score based on resume content
    
    Args:
        resume_text: Resume text content
    
    Returns:
        Dict with score and detailed breakdown
    """
    score_breakdown = {}
    total_score = 0
    max_score = 100
    
    # 1. Check for standard sections (20 points)
    standard_sections = ['experience', 'education', 'skills', 'projects']
    sections_found = sum(1 for section in standard_sections if section.lower() in resume_text.lower())
    section_score = (sections_found / len(standard_sections)) * 20
    score_breakdown['Standard Sections'] = {
        'score': section_score,
        'max': 20,
        'details': f'Found {sections_found}/{len(standard_sections)} standard sections'
    }
    total_score += section_score
    
    # 2. Check for contact information (15 points)
    contact_score = 0
    contact_items = []
    
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
        contact_score += 7.5
        contact_items.append('Email')
    
    if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', resume_text):
        contact_score += 7.5
        contact_items.append('Phone')
    
    score_breakdown['Contact Information'] = {
        'score': contact_score,
        'max': 15,
        'details': f'Found: {", ".join(contact_items) if contact_items else "None"}'
    }
    total_score += contact_score
    
    # 3. Check for quantifiable achievements (20 points)
    numbers_pattern = r'\b\d+%|\b\d+\+|\b\d+x|\$\d+|\d+\s*(million|billion|thousand|k|m)'
    quantifiable_matches = len(re.findall(numbers_pattern, resume_text, re.IGNORECASE))
    achievement_score = min(quantifiable_matches * 2, 20)
    score_breakdown['Quantifiable Achievements'] = {
        'score': achievement_score,
        'max': 20,
        'details': f'Found {quantifiable_matches} quantified achievements'
    }
    total_score += achievement_score
    
    # 4. Check for action verbs (15 points)
    action_verbs = [
        'developed', 'managed', 'led', 'created', 'implemented', 'designed',
        'built', 'achieved', 'improved', 'increased', 'reduced', 'optimized',
        'analyzed', 'coordinated', 'executed', 'delivered'
    ]
    verbs_found = sum(1 for verb in action_verbs if verb.lower() in resume_text.lower())
    verb_score = min((verbs_found / len(action_verbs)) * 15, 15)
    score_breakdown['Action Verbs'] = {
        'score': verb_score,
        'max': 15,
        'details': f'Used {verbs_found}/{len(action_verbs)} strong action verbs'
    }
    total_score += verb_score
    
    # 5. Check for keywords density (10 points)
    word_count = len(resume_text.split())
    keyword_score = 0
    if 300 <= word_count <= 800:
        keyword_score = 10
        density_msg = 'Optimal length'
    elif word_count < 300:
        keyword_score = 5
        density_msg = 'Too short'
    else:
        keyword_score = 7
        density_msg = 'Slightly long'
    
    score_breakdown['Resume Length'] = {
        'score': keyword_score,
        'max': 10,
        'details': f'{word_count} words - {density_msg}'
    }
    total_score += keyword_score
    
    # 6. Check for formatting issues (10 points)
    formatting_score = 10
    formatting_issues = []
    
    # Check for excessive special characters
    special_chars = len(re.findall(r'[★☆●○■□▪▫◆◇]', resume_text))
    if special_chars > 5:
        formatting_score -= 3
        formatting_issues.append('Too many special characters')
    
    # Check for proper capitalization
    if resume_text.isupper():
        formatting_score -= 3
        formatting_issues.append('All caps detected')
    
    # Check for line breaks consistency
    if '\n\n\n' in resume_text:
        formatting_score -= 2
        formatting_issues.append('Inconsistent spacing')
    
    score_breakdown['Formatting'] = {
        'score': max(formatting_score, 0),
        'max': 10,
        'details': 'Clean' if not formatting_issues else ', '.join(formatting_issues)
    }
    total_score += max(formatting_score, 0)
    
    # 7. Check for dates in experience (10 points)
    date_patterns = r'\b(19|20)\d{2}\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(19|20)\d{2}\b'
    dates_found = len(re.findall(date_patterns, resume_text, re.IGNORECASE))
    date_score = min(dates_found * 2, 10)
    score_breakdown['Timeline/Dates'] = {
        'score': date_score,
        'max': 10,
        'details': f'Found {dates_found} date references'
    }
    total_score += date_score
    
    # Final score
    final_score = min(int(total_score), max_score)
    
    # Generate recommendations
    recommendations = []
    if score_breakdown['Standard Sections']['score'] < 15:
        recommendations.append("Add missing standard sections (Experience, Education, Skills, Projects)")
    if score_breakdown['Contact Information']['score'] < 10:
        recommendations.append("Include complete contact information (email and phone)")
    if score_breakdown['Quantifiable Achievements']['score'] < 10:
        recommendations.append("Add more quantifiable achievements with numbers and metrics")
    if score_breakdown['Action Verbs']['score'] < 10:
        recommendations.append("Use stronger action verbs to describe your experience")
    if score_breakdown['Timeline/Dates']['score'] < 5:
        recommendations.append("Include dates for all positions and education")
    
    return {
        'score': final_score,
        'grade': get_ats_grade(final_score),
        'breakdown': score_breakdown,
        'recommendations': recommendations
    }


def get_ats_grade(score):
    """Convert ATS score to letter grade"""
    if score >= 90:
        return 'A+ (Excellent)'
    elif score >= 80:
        return 'A (Very Good)'
    elif score >= 70:
        return 'B (Good)'
    elif score >= 60:
        return 'C (Fair)'
    else:
        return 'D (Needs Improvement)'