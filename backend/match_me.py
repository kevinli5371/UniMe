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
import sys
from tqdm import tqdm

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

# Helper for multi-select input with descriptions
def multi_select(prompt, options, descriptions=None):
    print(f"{prompt} (separate choices by comma)")
    for i, opt in enumerate(options, 1):
        desc = f" - {descriptions[opt]}" if descriptions and opt in descriptions else ""
        print(f"  {i}. {opt}{desc}")
    choices = input("Enter numbers: ")
    selected = set()
    for token in choices.split(','):
        token = token.strip()
        if token.isdigit() and 1 <= int(token) <= len(options):
            selected.add(options[int(token)-1])
    return selected

# Helper for single-select input
def single_select(prompt, options):
    print(f"{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    choice = input("Enter number: ")
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        return options[int(choice)-1]
    return None

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

# Ask weights
print("Rate how much each factor matters to you (they will be normalized):")
wa = float(input("Academics weight (e.g. 1): ") or 1)
wc = float(input("Campus life weight  (e.g. 1): ") or 1)
wso = float(input("Social weight       (e.g. 1): ") or 1)
W_TOTAL = wa + wc + wso

# Academic questions
print("\n--- Academics ---")
AA = multi_select("Pick up to three broad academic interests", ["Engineering","CS/Math","Business","Arts/Humanities","Sciences","Health","Undecided"], INTEREST_DESCRIPTIONS)
LS = int(input("How do you prefer to learn? (1=Theoretical ... 5=Hands-on): ") or 3)
SP = int(input("How specialized should 1st-year be? (1=Very broad ... 5=Highly specialized): ") or 3)
CO = int(input("How critical is co-op/internship? (1=Not important ... 5=Essential): ") or 3)
UR = int(input("Undergraduate research importance? (1=Not at all ... 5=Essential): ") or 3)
CR = int(input("Are you creative? (1=Not creative ... 5=Very creative): ") or 3)
CE = int(input("Career certainty? (1=Not sure ... 5=Very sure): ") or 3)
LC = multi_select("What HS courses did you like?", ["Autoshop","Biology","Business","Chemistry","Computer Science","Geography","History","Language Arts","Math","Physics","Visual Arts"])
ME = int(input("Math enjoyment? (1=Hate ... 5=Love): ") or 3)
CP = int(input("Collaboration preference? (1=Alone ... 5=Group): ") or 3)
ALT = []
if "Engineering" in AA:
    ALT = list(multi_select("If not Eng, alternatives?", ["Applied Science","Business","Computer Science","Economics","English Literature","Environmental Studies","Finance","Geography","Graphic Design","Health Studies","Marketing","Math","Political Science","Psychology","Visual Arts"]))

# Campus questions
print("\n--- Campus Life ---")
CSB = single_select("Ideal class size?", ["< 60","60-200","200+"])
SET = single_select("Campus setting you'd enjoy most?", ["Urban","Suburban","Small-town","Rural"])
HS = set(multi_select("Preferred first-year housing style", ["Traditional dorm","Suite-style","Apartment","Off-campus"]))
CPS = single_select("Preferred campus size?", ["Small","Medium","Large"])

# Social questions
print("\n--- Social & Extracurriculars ---")
NS = int(input("Night-and-weekend scene? (1=Quiet ... 5=Very lively): ") or 3)
SPT = multi_select("Which varsity/rec sports?", ["Basketball","Soccer","Hockey","Rugby","Volleyball","Football","None"])
CLB = multi_select("Which clubs interest you?", ["Hackathons","Case comps","Design teams","Performing arts","Volunteering","Entrepreneurship"])
CEV = int(input("How often attend concerts/cultural events? (1=Never ... 5=Very often): ") or 3)

# Scoring functions
from math import fabs

def score_academic(p):
    # interests (weighted 40%)
    prog_int = p['academic']['interests']
    i_score = enhanced_interest_score(AA, prog_int) * 0.4
    
    # courses (weighted 20%)
    prog_lc = p['academic'].get('liked_hs_courses', [])
    lc_score = enhanced_course_score(LC, prog_lc) * 0.2
    
    # alt (weighted 10% if engineering interest)
    prog_alt = set(p['academic'].get('alt_to_engineering', []))
    alt_score = 0
    if ALT:
        matched_alts = prog_alt.intersection(set(ALT))
        alt_score = (len(matched_alts) / max(len(ALT), 1)) * 0.1
    
    # numeric (weighted 30%)
    keys = ['learning_style', 'first_year_specialization', 'coop_importance', 
            'research_importance', 'creativity_orientation', 'career_certainty', 
            'math_enjoyment', 'collaboration_preference']
    vals = [LS, SP, CO, UR, CR, CE, ME, CP]
    
    # Adjust weight based on importance
    weights = {
        'learning_style': 1.2,
        'first_year_specialization': 1.0,
        'coop_importance': 1.5 if CO >= 4 else 1.0,  # Boost if user cares about co-op
        'research_importance': 1.5 if UR >= 4 else 1.0,  # Boost if user cares about research
        'creativity_orientation': 1.2 if CR >= 4 else 1.0,
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

def score_campus(p):
    base = p['campus']
    scores = []
    
    # Class size (weighted 25%)
    if base.get('class_size_bin') == CSB:
        scores.append(1.0)
    else:
        # Partial credit for close sizes
        if CSB == "< 60" and base.get('class_size_bin') == "60-200":
            scores.append(0.5)
        elif CSB == "200+" and base.get('class_size_bin') == "60-200":
            scores.append(0.5)
        else:
            scores.append(0.0)
    
    # Setting (weighted 25%)
    if base.get('setting') == SET:
        scores.append(1.0)
    else:
        # Partial credit for related settings
        urban_suburban = {"Urban", "Suburban"}
        rural_small = {"Small-town", "Rural"}
        
        if SET in urban_suburban and base.get('setting') in urban_suburban:
            scores.append(0.5)
        elif SET in rural_small and base.get('setting') in rural_small:
            scores.append(0.5)
        else:
            scores.append(0.0)
    
    # Housing style (weighted 25%)
    hs_prog = set(base.get('housing_styles', []))
    if hs_prog:
        # How many of the user's preferences are available
        housing_score = len(HS.intersection(hs_prog)) / len(HS) if HS else 0
        scores.append(housing_score)
    else:
        scores.append(0.0)
    
    # Campus size (weighted 25%)
    if base.get('campus_size') == CPS:
        scores.append(1.0)
    else:
        # Partial credit for close sizes
        sizes = ["Small", "Medium", "Large"]
        user_idx = sizes.index(CPS) if CPS in sizes else -1
        prog_idx = sizes.index(base.get('campus_size')) if base.get('campus_size') in sizes else -1
        
        if user_idx != -1 and prog_idx != -1:
            # 0.5 points if only one size category difference
            scores.append(0.5 if abs(user_idx - prog_idx) == 1 else 0.0)
        else:
            scores.append(0.0)
    
    # Average all scores with equal weighting
    return sum(scores) / len(scores)

def score_social(p):
    base = p['social']
    
    # Night scene similarity (weighted 25%)
    prog_ns = base.get('night_scene', 3)
    # Closer values score higher (5 point scale, max difference is 4)
    ns_score = 1 - (abs(prog_ns - NS) / 4.0)
    
    # Sports (weighted 25%)
    sp_prog = set(base.get('sports', []))
    if "None" in SPT:
        # User doesn't care about sports
        spt_score = 1.0
    else:
        # Calculate match between user preferences and available sports
        spt_score = len(sp_prog.intersection(SPT)) / max(len(SPT), 1)
    
    # Clubs (weighted 25%)
    cl_prog = set(base.get('clubs', []))
    # Calculate match between user preferences and available clubs
    cl_score = len(cl_prog.intersection(CLB)) / max(len(CLB), 1) if CLB else 0.5
    
    # Cultural events frequency (weighted 25%)
    prog_cev = base.get('cultural_event_freq', 3)
    # Closer values score higher (5 point scale, max difference is 4)
    cev_score = 1 - (abs(prog_cev - CEV) / 4.0)
    
    # Average all scores with equal weighting
    return (ns_score + spt_score + cl_score + cev_score) / 4

# Compute and rank
results = []
for p in tqdm(programs, desc="Scoring programs"):
    try:
        a = score_academic(p)
        c = score_campus(p)
        sos = score_social(p)
        total = (wa*a + wc*c + wso*sos) / W_TOTAL
        results.append((total, a, c, sos, p['uni'], p['program']))
    except Exception as e:
        print(f"Error scoring {p.get('uni', 'Unknown')} - {p.get('program', 'Unknown')}: {e}")

results.sort(reverse=True, key=lambda x: x[0])

print("\nTop 10 Matches:\n")
for rank, (tot, a, c, soc, uni, prog) in enumerate(results[:10], 1):
    print(f"{rank}. {uni} – {prog}")
    print(f"   Total Score: {tot:.3f}  (A={a:.3f}, C={c:.3f}, S={soc:.3f})")

# Display breakdown of top match
if results:
    print("\nBreakdown of your top match:")
    top = results[0]
    print(f"{top[4]} – {top[5]}")
    
    # Find the program object
    top_program = None
    for p in programs:
        if p['uni'] == top[4] and p['program'] == top[5]:
            top_program = p
            break
            
    if top_program:
        print("Academic interests that matched yours:")
        for interest in top_program['academic']['interests']:
            for category in AA:
                mapped = False
                for key_term in INTEREST_MAPPINGS:
                    if key_term in interest.lower() and INTEREST_MAPPINGS[key_term] == category:
                        print(f"  • {interest} (matched with your {category} interest)")
                        mapped = True
                        break
                if mapped:
                    break

print("\nDone.")
