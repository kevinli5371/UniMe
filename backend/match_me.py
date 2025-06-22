#!/usr/bin/env python3
"""
Quiz Matcher CLI

This script prompts a user in the terminal through a series of questions
and then ranks the top 10 university programs from program_profiles.json
based on their responses.

Usage:
    pip3 install tqdm
    python3 quiz_cli.py

Outputs the top 10 matches with scores.
"""
import json
from tqdm import tqdm
import sys
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

# Load program profiles
try:
    with open('backend/program_profiles.json', 'r', encoding='utf-8') as f:
        programs = json.load(f)
except FileNotFoundError:
    print("Error: program_profiles.json not found. Make sure it exists in this folder.")
    sys.exit(1)

# Interest mappings - standardized categories for better matching
INTEREST_MAPPINGS = {
    # Engineering related interests
    "mechanical engineering": "Engineering",
    "civil engineering": "Engineering",
    "electrical engineering": "Engineering",
    "robotics": "Engineering",
    "mechatronics": "Engineering",
    "automotive": "Engineering", 
    "aerospace": "Engineering",
    "structural design": "Engineering",
    "manufacturing": "Engineering",
    "product development": "Engineering",
    "engineering design": "Engineering",
    
    # CS/Math related interests
    "programming": "CS/Math",
    "software development": "CS/Math",
    "algorithms": "CS/Math",
    "data science": "CS/Math",
    "mathematics": "CS/Math",
    "statistics": "CS/Math",
    "computer science": "CS/Math",
    "web development": "CS/Math",
    "artificial intelligence": "CS/Math",
    "machine learning": "CS/Math",
    "cryptography": "CS/Math",
    "cybersecurity": "CS/Math",
    "computational": "CS/Math",
    
    # Business related interests
    "finance": "Business",
    "marketing": "Business",
    "entrepreneurship": "Business",
    "economics": "Business",
    "accounting": "Business",
    "management": "Business",
    "business": "Business",
    "consulting": "Business",
    "human resources": "Business",
    "sales": "Business",
    "investment": "Business",
    "stock market": "Business",
    "taxation": "Business",
    "audit": "Business",
    
    # Arts/Humanities related interests
    "literature": "Arts/Humanities",
    "philosophy": "Arts/Humanities",
    "history": "Arts/Humanities",
    "languages": "Arts/Humanities",
    "writing": "Arts/Humanities",
    "cultural studies": "Arts/Humanities",
    "art history": "Arts/Humanities",
    "music": "Arts/Humanities",
    "film": "Arts/Humanities",
    "theatre": "Arts/Humanities",
    "creative writing": "Arts/Humanities",
    "linguistics": "Arts/Humanities",
    "anthropology": "Arts/Humanities",
    "archaeology": "Arts/Humanities",
    
    # Sciences related interests
    "biology": "Sciences",
    "chemistry": "Sciences",
    "physics": "Sciences",
    "environmental science": "Sciences",
    "astronomy": "Sciences",
    "earth sciences": "Sciences",
    "geology": "Sciences",
    "biochemistry": "Sciences",
    "molecular biology": "Sciences",
    "genetics": "Sciences",
    "ecology": "Sciences",
    "marine biology": "Sciences",
    "forensic science": "Sciences",
    
    # Health related interests
    "medicine": "Health",
    "nursing": "Health",
    "kinesiology": "Health",
    "public health": "Health",
    "nutrition": "Health",
    "psychology": "Health",
    "healthcare": "Health",
    "anatomy": "Health",
    "physiology": "Health",
    "pharmacy": "Health",
    "biomedical": "Health",
    "dentistry": "Health",
    "therapy": "Health",
    "mental health": "Health",
    "psychiatry": "Health",
    "rehabilitation": "Health"
}

# Course mappings - connect high school courses to program preferences
COURSE_MAPPINGS = {
    "calculus": "Math",
    "algebra": "Math",
    "statistics": "Math",
    "physics": "Physics",
    "biology": "Biology",
    "chemistry": "Chemistry",
    "computer programming": "Computer Science",
    "business studies": "Business",
    "economics": "Business",
    "english": "Language Arts",
    "literature": "Language Arts",
    "creative writing": "Language Arts",
    "history": "History",
    "geography": "Geography",
    "art": "Visual Arts",
    "visual arts": "Visual Arts",
    "design": "Visual Arts",
    "shop class": "Autoshop",
    "auto mechanics": "Autoshop"
}

# Interest category descriptions for better context
INTEREST_DESCRIPTIONS = {
    "Engineering": "Design and build physical systems and infrastructure",
    "CS/Math": "Computing, programming, data analysis, and mathematics",
    "Business": "Finance, marketing, management, and entrepreneurship",
    "Arts/Humanities": "Creative writing, languages, philosophy, and cultural studies",
    "Sciences": "Natural sciences like biology, chemistry, physics",
    "Health": "Healthcare, medicine, nursing, and wellness fields",
    "Undecided": "Not sure yet or interested in multiple areas"
}

# Enhanced interest matching using mappings
def enhanced_interest_score(user_interests, program_interests):
    """Calculate interest score with mapping to standardized categories"""
    if not user_interests:
        return 0
        
    mapped_program_interests = set()
    for interest in program_interests:
        # Convert to lowercase for matching
        interest_lower = interest.lower()
        # Direct match first
        if interest_lower in [i.lower() for i in user_interests]:
            mapped_program_interests.add(interest_lower)
            continue
            
        # Try mapped categories
        for key_term in INTEREST_MAPPINGS:
            if key_term in interest_lower:
                category = INTEREST_MAPPINGS[key_term]
                if category in user_interests:
                    mapped_program_interests.add(category)
                    break
    
    # Calculate match score with bonus for multiple matches
    match_count = len(mapped_program_interests)
    if match_count == 0:
        return 0
    elif match_count == 1:
        return 0.6  # Single match
    elif match_count == 2:
        return 0.8  # Two matches
    else:
        return 1.0  # Three or more matches

# Enhanced course matching using mappings
def enhanced_course_score(user_courses, program_courses):
    """Calculate course match score with improved mapping"""
    if not user_courses or not program_courses:
        return 0
        
    mapped_program_courses = set()
    for course in program_courses:
        # Convert to lowercase for matching
        course_lower = course.lower()
        # Direct match first
        if course_lower in [c.lower() for c in user_courses]:
            mapped_program_courses.add(course_lower)
            continue
            
        # Try mapped categories
        for key_term in COURSE_MAPPINGS:
            if key_term in course_lower:
                category = COURSE_MAPPINGS[key_term]
                if category in user_courses:
                    mapped_program_courses.add(category)
                    break
    
    match_ratio = len(mapped_program_courses) / max(len(user_courses), 1)
    return min(match_ratio, 1.0)  # Cap at 1.0

# Scoring functions
from math import fabs

def score_academic(p, user_answers):
    # interests (weighted 40%)
    prog_int = p['academic']['interests']
    i_score = enhanced_interest_score(user_answers['AA'], prog_int) * 0.4
    
    # courses (weighted 20%)
    prog_lc = p['academic'].get('liked_hs_courses', [])
    lc_score = enhanced_course_score(user_answers['LC'], prog_lc) * 0.2
    
    # alt (weighted 10% if engineering interest)
    prog_alt = set(p['academic'].get('alt_to_engineering', []))
    alt_score = 0
    if user_answers['ALT']:
        matched_alts = prog_alt.intersection(set(user_answers['ALT']))
        alt_score = (len(matched_alts) / max(len(user_answers['ALT']), 1)) * 0.1
    
    # numeric (weighted 30%)
    keys = ['learning_style', 'first_year_specialization', 'coop_importance', 
            'research_importance', 'creativity_orientation', 'career_certainty', 
            'math_enjoyment', 'collaboration_preference']
    vals = [user_answers['LS'], user_answers['SP'], user_answers['CO'], user_answers['UR'], user_answers['CR'], user_answers['CE'], user_answers['ME'], user_answers['CP']]
    
    # Adjust weight based on importance
    weights = {
        'learning_style': 1.2,
        'first_year_specialization': 1.0,
        'coop_importance': 1.5 if user_answers['CO'] >= 4 else 1.0,  # Boost if user cares about co-op
        'research_importance': 1.5 if user_answers['UR'] >= 4 else 1.0,  # Boost if user cares about research
        'creativity_orientation': 1.2 if user_answers['CR'] >= 4 else 1.0,
        'career_certainty': 1.0,
        'math_enjoyment': 1.3,  # Math is important for many programs
        'collaboration_preference': 1.0
    }
    
    total_weight = sum(weights.values())
    
    num_scores = []
    weight_sum = 0
    for k, s, i in zip(keys, vals, range(len(keys))):
        prog_val = p['academic'].get(k, 3)
        # Closer values should score higher (5 point scale, max difference is 4)
        similarity = 1 - (abs(prog_val - s) / 4.0)
        weight = weights[k]
        num_scores.append(similarity * weight)
        weight_sum += weight
        
    # Normalize by weights
    num_score = sum(num_scores) / total_weight * 0.3
    
    return i_score + lc_score + num_score + alt_score

def score_campus(p, user_answers):
    base = p['campus']
    scores = []
    
    # Class size (weighted 25%)
    if base.get('class_size_bin') == user_answers['CSB']:
        scores.append(1.0)
    else:
        # Partial credit for close sizes
        if user_answers['CSB'] == "< 60" and base.get('class_size_bin') == "60-200":
            scores.append(0.5)
        elif user_answers['CSB'] == "200+" and base.get('class_size_bin') == "60-200":
            scores.append(0.5)
        else:
            scores.append(0.0)
    
    # Setting (weighted 25%)
    if base.get('setting') == user_answers['SET']:
        scores.append(1.0)
    else:
        # Partial credit for related settings
        urban_suburban = {"Urban", "Suburban"}
        rural_small = {"Small-town", "Rural"}
        
        if user_answers['SET'] in urban_suburban and base.get('setting') in urban_suburban:
            scores.append(0.5)
        elif user_answers['SET'] in rural_small and base.get('setting') in rural_small:
            scores.append(0.5)
        else:
            scores.append(0.0)
    
    # Housing style (weighted 25%)
    hs_prog = set(base.get('housing_styles', []))
    if hs_prog:
        # How many of the user's preferences are available
        housing_score = len(user_answers['HS'].intersection(hs_prog)) / len(user_answers['HS']) if user_answers['HS'] else 0
        scores.append(housing_score)
    else:
        scores.append(0.0)
    
    # Campus size (weighted 25%)
    if base.get('campus_size') == user_answers['CPS']:
        scores.append(1.0)
    else:
        # Partial credit for close sizes
        sizes = ["Small", "Medium", "Large"]
        user_idx = sizes.index(user_answers['CPS']) if user_answers['CPS'] in sizes else -1
        prog_idx = sizes.index(base.get('campus_size')) if base.get('campus_size') in sizes else -1
        
        if user_idx != -1 and prog_idx != -1:
            # 0.5 points if only one size category difference
            scores.append(0.5 if abs(user_idx - prog_idx) == 1 else 0.0)
        else:
            scores.append(0.0)
    
    # Average all scores with equal weighting
    return sum(scores) / len(scores)

def score_social(p, user_answers):
    base = p['social']
    
    # Night scene similarity (weighted 25%)
    prog_ns = base.get('night_scene', 3)
    # Closer values score higher (5 point scale, max difference is 4)
    ns_score = 1 - (abs(prog_ns - user_answers['NS']) / 4.0)
    
    # Sports (weighted 25%)
    sp_prog = set(base.get('sports', []))
    if "None" in user_answers['SPT']:
        # User doesn't care about sports
        spt_score = 1.0
    else:
        # Calculate match between user preferences and available sports
        spt_score = len(sp_prog.intersection(user_answers['SPT'])) / max(len(user_answers['SPT']), 1)
    
    # Clubs (weighted 25%)
    cl_prog = set(base.get('clubs', []))
    # Calculate match between user preferences and available clubs
    cl_score = len(cl_prog.intersection(user_answers['CLB'])) / max(len(user_answers['CLB']), 1) if user_answers['CLB'] else 0.5
    
    # Cultural events frequency (weighted 25%)
    prog_cev = base.get('cultural_event_freq', 3)
    # Closer values score higher (5 point scale, max difference is 4)
    cev_score = 1 - (abs(prog_cev - user_answers['CEV']) / 4.0)
    
    # Average all scores with equal weighting
    return (ns_score + spt_score + cl_score + cev_score) / 4

# Add these imports at the top of the file
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def generate_matches_pdf_bytes(results, weights=None):
    """
    Generate a PDF with the top 100 program matches and return as bytes
    for browser download.
    
    Args:
        results: List of tuples (total_score, academic_score, campus_score, social_score, university, program)
        weights: Optional dictionary with weights {'wa': academic_weight, 'wc': campus_weight, 'wso': social_weight}
    
    Returns:
        BytesIO object containing the PDF data
    """
    # Set default weights if not provided
    if weights is None:
        weights = {'wa': 0.6, 'wc': 0.2, 'wso': 0.2}
    
    # Create a BytesIO buffer instead of file
    buffer = BytesIO()
    
    # Create PDF - Switch to landscape orientation
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, 
                           topMargin=30, bottomMargin=18)
    
    # Rotate the page to landscape orientation
    doc.pagesize = landscape(letter)
    
    # Take top 100 or all results if less than 100
    top_programs = results[:min(100, len(results))]
    
    styles = getSampleStyleSheet()
    
    styles['Title'].alignment = 1  # Center
    styles['Title'].spaceAfter = 12
    
    # Create a custom subtitle style with a unique name
    styles.add(ParagraphStyle(name='CustomSubtitle', 
                              parent=styles['Heading2'], 
                              alignment=1,  # Center
                              spaceAfter=10))
    
    # Create style for program name cells with wrapping
    program_style = ParagraphStyle(
        name='ProgramStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=10,
        alignment=0,  # Left alignment
    )

    university_style = ParagraphStyle(
        name='UniversityStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=10,
        alignment=0,  # Left alignment
    )
    
    # Build content
    content = []
    
    # Title
    content.append(Paragraph("LinkU: Your University Program Matches", styles['Title']))
    content.append(Spacer(1, 0.25*inch))
    
    # Summary of weights
    content.append(Paragraph(f"<b>Academic Weight:</b> {weights['wa']:.2f}", styles['Normal']))
    content.append(Paragraph(f"<b>Campus Life Weight:</b> {weights['wc']:.2f}", styles['Normal']))
    content.append(Paragraph(f"<b>Social Weight:</b> {weights['wso']:.2f}", styles['Normal']))
    content.append(Paragraph(f"<b>Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    content.append(Spacer(1, 0.25*inch))
    
    # Top programs heading
    content.append(Paragraph(f"<b>Top {len(top_programs)} Program Matches</b>", styles['Heading2']))
    content.append(Spacer(1, 0.1*inch))
    
    # Table data with wrapping program text
    table_data = [["Rank", "University", "Program", "Academic", "Campus", "Social", "Total"]]
    
    for i, (tot, a, c, soc, uni, prog) in enumerate(top_programs):
        # Convert the program name to a Paragraph object for wrapping
        university_cell = Paragraph(uni, university_style)
        program_cell = Paragraph(prog, program_style)
        
        table_data.append([
            str(i+1),
            university_cell,
            program_cell,  # Using Paragraph instead of string
            f"{a:.3f}",
            f"{c:.3f}",
            f"{soc:.3f}",
            f"{tot:.3f}"
        ])
    
    # Create the table with column widths
    col_widths = [30, 110, 200, 60, 60, 60, 60]  # Adjust column widths
    table = Table(table_data, repeatRows=1, colWidths=col_widths)
    
    # Define basic style first
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Make rank column centered
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        # Make university column left-aligned
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        # Program column already left-aligned by the Paragraph style
        # Make numeric columns right-aligned
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        # Vertical alignment
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Add padding to cells
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]
    
    # Add alternating row backgrounds
    for row in range(1, len(table_data), 2):
        style.append(('BACKGROUND', (0, row), (-1, row), colors.lightgrey))
    
    # Add conditional formatting for high scores
    for row in range(1, len(table_data)):
        # Academic score highlighting
        try:
            if float(table_data[row][3]) > 0.7:
                style.append(('BACKGROUND', (3, row), (3, row), colors.palegreen))
        except (ValueError, TypeError):
            pass
        
        # Campus score highlighting
        try:
            if float(table_data[row][4]) > 0.7:
                style.append(('BACKGROUND', (4, row), (4, row), colors.palegreen))
        except (ValueError, TypeError):
            pass
        
        # Social score highlighting
        try:
            if float(table_data[row][5]) > 0.7:
                style.append(('BACKGROUND', (5, row), (5, row), colors.palegreen))
        except (ValueError, TypeError):
            pass
    
    table.setStyle(TableStyle(style))
    content.append(table)
    
    # Build the PDF
    doc.build(content)
    
    # Reset buffer position to the beginning
    buffer.seek(0)
    return buffer

# Compute and rank
def compute_matches(user_answers):
    results = []
    for p in tqdm(programs, desc="Scoring programs"):
        try:
            a = score_academic(p, user_answers)
            c = score_campus(p, user_answers)
            sos = score_social(p, user_answers)
            total = (user_answers['wa']*a + user_answers['wc']*c + user_answers['wso']*sos) / (user_answers['W_TOTAL'] or 1)
            results.append((total, a, c, sos, p['uni'], p['program']))
        except Exception as e:
            print(f"Error scoring {p.get('uni', 'Unknown')} - {p.get('program', 'Unknown')}: {e}")

    results.sort(reverse=True, key=lambda x: x[0])
    return results

print("\nDone.")
