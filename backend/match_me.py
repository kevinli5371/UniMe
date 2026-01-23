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
    with open('program_profiles.json', 'r', encoding='utf-8') as f:
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

# Program-type specific weight adjustments for more accurate matching
PROGRAM_TYPE_WEIGHTS = {
    'Engineering': {
        'math_enjoyment': 1.8,
        'learning_style': 1.4,  # Hands-on important for engineering
        'coop_importance': 1.3,
        'creativity_orientation': 1.0
    },
    'CS/Math': {
        'math_enjoyment': 1.7,
        'collaboration_preference': 1.2,
        'coop_importance': 1.3
    },
    'Business': {
        'collaboration_preference': 1.5,
        'career_certainty': 1.3,
        'coop_importance': 1.4
    },
    'Arts/Humanities': {
        'creativity_orientation': 1.8,
        'math_enjoyment': 0.7,  # Less important
        'research_importance': 1.3
    },
    'Sciences': {
        'research_importance': 1.6,
        'math_enjoyment': 1.4,
        'learning_style': 1.3
    },
    'Health': {
        'collaboration_preference': 1.4,
        'research_importance': 1.3,
        'career_certainty': 1.2
    }
}

# String normalization for consistent matching
def normalize_string(s):
    """Normalize strings for comparison by lowercasing and replacing separators"""
    if not s:
        return ""
    return s.lower().replace('-', ' ').replace('/', ' ').replace('_', ' ').strip()

# Detect program type from interests
def detect_program_type(program):
    """Detect the primary type of a program based on its interests"""
    interests = program.get('academic', {}).get('interests', [])
    program_name = program.get('program', '').lower()
    
    # Count category matches
    category_counts = {}
    for interest in interests:
        interest_lower = interest.lower()
        for key_term, category in INTEREST_MAPPINGS.items():
            if key_term in interest_lower:
                category_counts[category] = category_counts.get(category, 0) + 1
                break
    
    # Also check program name for hints
    name_hints = {
        'Engineering': ['engineering', 'mechanical', 'electrical', 'civil', 'chemical'],
        'CS/Math': ['computer', 'software', 'math', 'data science', 'computing'],
        'Business': ['business', 'commerce', 'management', 'finance', 'accounting', 'marketing'],
        'Arts/Humanities': ['arts', 'humanities', 'english', 'philosophy', 'history', 'music'],
        'Sciences': ['science', 'biology', 'chemistry', 'physics', 'environmental'],
        'Health': ['health', 'nursing', 'medicine', 'kinesiology', 'pharmacy']
    }
    
    for category, hints in name_hints.items():
        for hint in hints:
            if hint in program_name:
                category_counts[category] = category_counts.get(category, 0) + 2
    
    if not category_counts:
        return None
    
    return max(category_counts, key=category_counts.get)

# Enhanced interest matching using mappings with continuous scoring
def enhanced_interest_score(user_interests, program_interests):
    """Calculate interest score with continuous scoring instead of discrete jumps"""
    if not user_interests:
        return 0
    
    # Normalize user interests for comparison
    user_interests_normalized = {normalize_string(i) for i in user_interests}
    
    total_score = 0.0
    max_possible = len(user_interests)
    matched_categories = set()
    
    for interest in program_interests:
        interest_normalized = normalize_string(interest)
        
        # Direct match = full points
        if interest_normalized in user_interests_normalized:
            total_score += 1.0
            matched_categories.add(interest_normalized)
            continue
        
        # Try mapped categories with partial credit
        for key_term, category in INTEREST_MAPPINGS.items():
            if key_term in interest_normalized:
                category_normalized = normalize_string(category)
                if category_normalized in user_interests_normalized:
                    if category_normalized not in matched_categories:
                        total_score += 0.75  # Partial credit for category match
                        matched_categories.add(category_normalized)
                    break
                # Check original category name too
                if category in user_interests:
                    if category not in matched_categories:
                        total_score += 0.75
                        matched_categories.add(category)
                    break
    
    # Calculate continuous score with diminishing returns for extra matches
    if total_score == 0:
        return 0
    
    # Base score from matches, capped at 1.0
    base_score = min(total_score / max_possible, 1.0)
    
    # Bonus for multiple strong matches (up to 15% bonus)
    match_bonus = min(len(matched_categories) * 0.05, 0.15)
    
    return min(base_score + match_bonus, 1.0)

# Enhanced course matching using mappings with normalization
def enhanced_course_score(user_courses, program_courses):
    """Calculate course match score with improved mapping and normalization"""
    if not user_courses or not program_courses:
        return 0
    
    # Normalize user courses for comparison
    user_courses_normalized = {normalize_string(c) for c in user_courses}
    
    total_score = 0.0
    matched_courses = set()
    
    for course in program_courses:
        course_normalized = normalize_string(course)
        
        # Direct match = full points
        if course_normalized in user_courses_normalized:
            total_score += 1.0
            matched_courses.add(course_normalized)
            continue
        
        # Try mapped categories with partial credit
        for key_term, category in COURSE_MAPPINGS.items():
            if key_term in course_normalized:
                category_normalized = normalize_string(category)
                if category_normalized in user_courses_normalized or category in user_courses:
                    if category_normalized not in matched_courses:
                        total_score += 0.8  # Good partial credit for category match
                        matched_courses.add(category_normalized)
                    break
    
    match_ratio = total_score / max(len(user_courses), 1)
    return min(match_ratio, 1.0)  # Cap at 1.0

# Confidence weighting for Likert responses
def calculate_trait_score_with_confidence(user_val, prog_val):
    """Calculate similarity score with confidence weighting based on response extremity"""
    # Base similarity (0 to 1)
    similarity = 1 - (abs(prog_val - user_val) / 4.0)
    
    # Users with neutral answers (3) care less about this dimension
    # Importance ranges from 0.0 (neutral) to 1.0 (extreme)
    importance = abs(user_val - 3) / 2.0
    
    # Confidence weight ranges from 0.6 to 1.0
    # Neutral responses still contribute, but less decisively
    confidence_weight = 0.6 + (importance * 0.4)
    
    return similarity * confidence_weight

# Distance-based scoring for categorical values
def score_categorical_distance(user_pref, prog_val, order_list):
    """Score based on distance in ordered categories"""
    if user_pref not in order_list or prog_val not in order_list:
        return 0.5  # Neutral if unknown
    
    user_idx = order_list.index(user_pref)
    prog_idx = order_list.index(prog_val)
    max_distance = len(order_list) - 1
    
    if max_distance == 0:
        return 1.0
    
    distance = abs(user_idx - prog_idx)
    # Gradual falloff based on distance
    return 1.0 - (distance / max_distance) * 0.7

# Scoring functions
from math import fabs

def score_academic(p, user_answers):
    # interests (weighted 40%)
    prog_int = p['academic']['interests']
    i_score = enhanced_interest_score(user_answers['AA'], prog_int) * 0.4
    
    # courses (weighted 20%)
    prog_lc = p['academic'].get('liked_hs_courses', [])
    lc_score = enhanced_course_score(user_answers['LC'], prog_lc) * 0.2
    
    # alt (weighted 10% if engineering interest) - with normalization
    prog_alt = {normalize_string(a) for a in p['academic'].get('alt_to_engineering', [])}
    alt_score = 0
    if user_answers['ALT']:
        user_alt_normalized = {normalize_string(a) for a in user_answers['ALT']}
        matched_alts = prog_alt.intersection(user_alt_normalized)
        alt_score = (len(matched_alts) / max(len(user_answers['ALT']), 1)) * 0.1
    
    # numeric (weighted 30%)
    keys = ['learning_style', 'first_year_specialization', 'coop_importance', 
            'research_importance', 'creativity_orientation', 'career_certainty', 
            'math_enjoyment', 'collaboration_preference']
    vals = [user_answers['LS'], user_answers['SP'], user_answers['CO'], user_answers['UR'], user_answers['CR'], user_answers['CE'], user_answers['ME'], user_answers['CP']]
    
    # Base weights
    weights = {
        'learning_style': 1.2,
        'first_year_specialization': 1.0,
        'coop_importance': 1.5 if user_answers['CO'] >= 4 else 1.0,
        'research_importance': 1.5 if user_answers['UR'] >= 4 else 1.0,
        'creativity_orientation': 1.2 if user_answers['CR'] >= 4 else 1.0,
        'career_certainty': 1.0,
        'math_enjoyment': 1.3,
        'collaboration_preference': 1.0
    }
    
    # Apply program-type-specific weight adjustments
    program_type = detect_program_type(p)
    if program_type and program_type in PROGRAM_TYPE_WEIGHTS:
        type_weights = PROGRAM_TYPE_WEIGHTS[program_type]
        for key, multiplier in type_weights.items():
            if key in weights:
                weights[key] *= multiplier
    
    total_weight = sum(weights.values())
    
    num_scores = []
    for k, s in zip(keys, vals):
        prog_val = p['academic'].get(k, 3)
        # Use confidence-weighted scoring
        weighted_similarity = calculate_trait_score_with_confidence(s, prog_val)
        weight = weights[k]
        num_scores.append(weighted_similarity * weight)
        
    # Normalize by weights
    num_score = sum(num_scores) / total_weight * 0.3
    
    return i_score + lc_score + num_score + alt_score

def score_campus(p, user_answers):
    base = p['campus']
    scores = []
    
    # Class size (weighted 25%) - using distance-based scoring
    class_size_order = ["< 60", "60-200", "200+"]
    class_size_score = score_categorical_distance(
        user_answers['CSB'], 
        base.get('class_size_bin', '60-200'),
        class_size_order
    )
    scores.append(class_size_score)
    
    # Setting (weighted 25%) - with normalized comparison and distance
    user_setting = normalize_string(user_answers.get('SET', ''))
    prog_setting = normalize_string(base.get('setting', ''))
    
    # Define setting order for distance calculation
    setting_order = ['urban', 'suburban', 'small town', 'rural']
    
    if user_setting == prog_setting:
        scores.append(1.0)
    else:
        # Try to find in order list
        user_setting_mapped = user_setting.replace('-', ' ')
        prog_setting_mapped = prog_setting.replace('-', ' ')
        
        if user_setting_mapped in setting_order and prog_setting_mapped in setting_order:
            scores.append(score_categorical_distance(user_setting_mapped, prog_setting_mapped, setting_order))
        else:
            # Fallback to old logic with partial credit
            urban_suburban = {'urban', 'suburban'}
            rural_small = {'small town', 'rural', 'small-town'}
            
            if user_setting in urban_suburban and prog_setting in urban_suburban:
                scores.append(0.6)
            elif user_setting in rural_small and prog_setting in rural_small:
                scores.append(0.6)
            else:
                scores.append(0.2)  # Not zero - some compatibility
    
    # Housing style (weighted 25%) - with normalization
    hs_prog = {normalize_string(h) for h in base.get('housing_styles', [])}
    user_hs = {normalize_string(h) for h in user_answers.get('HS', set())}
    
    if hs_prog and user_hs:
        housing_score = len(user_hs.intersection(hs_prog)) / len(user_hs)
        scores.append(housing_score)
    elif not user_hs:
        scores.append(0.5)  # Neutral if user has no preference
    else:
        scores.append(0.2)  # Low score if program has no housing info
    
    # Campus size (weighted 25%) - using distance-based scoring
    campus_size_order = ["Small", "Medium", "Large"]
    user_cps = user_answers.get('CPS', 'Medium')
    prog_cps = base.get('campus_size', 'Medium')
    
    # Normalize for comparison
    user_cps_normalized = user_cps.capitalize() if user_cps else 'Medium'
    prog_cps_normalized = prog_cps.capitalize() if prog_cps else 'Medium'
    
    campus_score = score_categorical_distance(user_cps_normalized, prog_cps_normalized, campus_size_order)
    scores.append(campus_score)
    
    # Average all scores with equal weighting
    return sum(scores) / len(scores)

def score_social(p, user_answers):
    base = p['social']
    
    # Night scene similarity (weighted 25%) - with confidence weighting
    prog_ns = base.get('night_scene', 3)
    ns_score = calculate_trait_score_with_confidence(user_answers['NS'], prog_ns)
    
    # Sports (weighted 25%) - with normalization
    sp_prog = {normalize_string(s) for s in base.get('sports', [])}
    user_spt = {normalize_string(s) for s in user_answers.get('SPT', set())}
    
    if "none" in user_spt or not user_spt:
        # User doesn't care about sports
        spt_score = 1.0
    else:
        # Calculate match between user preferences and available sports
        spt_score = len(sp_prog.intersection(user_spt)) / max(len(user_spt), 1)
    
    # Clubs (weighted 25%) - with normalization
    cl_prog = {normalize_string(c) for c in base.get('clubs', [])}
    user_clb = {normalize_string(c) for c in user_answers.get('CLB', set())}
    
    if user_clb:
        cl_score = len(cl_prog.intersection(user_clb)) / len(user_clb)
    else:
        cl_score = 0.5  # Neutral if user has no preference
    
    # Cultural events frequency (weighted 25%) - with confidence weighting
    prog_cev = base.get('cultural_event_freq', 3)
    cev_score = calculate_trait_score_with_confidence(user_answers['CEV'], prog_cev)
    
    # Average all scores with equal weighting
    return (ns_score + spt_score + cl_score + cev_score) / 4


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
    content.append(Paragraph("UniMe: Your University Program Matches", styles['Title']))
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
