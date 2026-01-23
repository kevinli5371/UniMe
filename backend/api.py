import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import datetime
import random
from match_me import (INTEREST_MAPPINGS, COURSE_MAPPINGS, INTEREST_DESCRIPTIONS, 
                       enhanced_interest_score, enhanced_course_score,
                       normalize_string, detect_program_type, PROGRAM_TYPE_WEIGHTS,
                       calculate_trait_score_with_confidence, score_categorical_distance)
from chanceMe import predict_admission_chance

app = Flask(__name__)
CORS(app)  # Allow all origins for production

app.static_folder = 'static'

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# Fix the file path here - change from 'backend/program_profiles.json' to just 'program_profiles.json'
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'program_profiles.json')
with open(file_path, 'r', encoding='utf-8') as f:
    programs = json.load(f)

def compute_matches(answers, num_results=10):
    # Unpack answers from frontend (make sure keys match your frontend)
    wa = float(answers.get("wa", 1))
    wc = float(answers.get("wc", 1))
    wso = float(answers.get("wso", 1))
    W_TOTAL = wa + wc + wso

    AA = answers.get("AA", [])
    LS = int(answers.get("LS", 3))
    SP = int(answers.get("SP", 3))
    CO = int(answers.get("CO", 3))
    UR = int(answers.get("UR", 3))
    CR = int(answers.get("CR", 3))
    CE = int(answers.get("CE", 3))
    LC = answers.get("LC", [])
    ME = int(answers.get("ME", 3))
    CP = int(answers.get("CP", 3))
    ALT = answers.get("ALT", [])
    CSB = answers.get("CSB", "")
    SET = answers.get("SET", "")
    HS = set(answers.get("HS", []))
    CPS = answers.get("CPS", "")
    NS = int(answers.get("NS", 3))
    SPT = set(answers.get("SPT", []))
    CLB = set(answers.get("CLB", []))
    CEV = int(answers.get("CEV", 3))

    def score_academic(p):
        prog_int = p['academic']['interests']
        i_score = enhanced_interest_score(AA, prog_int) * 0.4
        prog_lc = p['academic'].get('liked_hs_courses', [])
        lc_score = enhanced_course_score(LC, prog_lc) * 0.2
        
        # Normalize alternatives for matching
        prog_alt = {normalize_string(a) for a in p['academic'].get('alt_to_engineering', [])}
        alt_score = 0
        if ALT:
            user_alt_normalized = {normalize_string(a) for a in ALT}
            matched_alts = prog_alt.intersection(user_alt_normalized)
            alt_score = (len(matched_alts) / max(len(ALT), 1)) * 0.1
        
        keys = ['learning_style', 'first_year_specialization', 'coop_importance', 
                'research_importance', 'creativity_orientation', 'career_certainty', 
                'math_enjoyment', 'collaboration_preference']
        vals = [LS, SP, CO, UR, CR, CE, ME, CP]
        
        # Base weights
        weights = {
            'learning_style': 1.2,
            'first_year_specialization': 1.0,
            'coop_importance': 1.5 if CO >= 4 else 1.0,
            'research_importance': 1.5 if UR >= 4 else 1.0,
            'creativity_orientation': 1.2 if CR >= 4 else 1.0,
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
        num_score = sum(num_scores) / total_weight * 0.3
        return i_score + lc_score + num_score + alt_score

    def score_campus(p):
        base = p['campus']
        scores = []
        
        # Class size - using distance-based scoring
        class_size_order = ["< 60", "60-200", "200+"]
        class_size_score = score_categorical_distance(
            CSB, 
            base.get('class_size_bin', '60-200'),
            class_size_order
        )
        scores.append(class_size_score)
        
        # Setting - with normalized comparison and distance
        user_setting = normalize_string(SET) if SET else ''
        prog_setting = normalize_string(base.get('setting', ''))
        
        setting_order = ['urban', 'suburban', 'small town', 'rural']
        
        if user_setting == prog_setting:
            scores.append(1.0)
        else:
            user_setting_mapped = user_setting.replace('-', ' ')
            prog_setting_mapped = prog_setting.replace('-', ' ')
            
            if user_setting_mapped in setting_order and prog_setting_mapped in setting_order:
                scores.append(score_categorical_distance(user_setting_mapped, prog_setting_mapped, setting_order))
            else:
                urban_suburban = {'urban', 'suburban'}
                rural_small = {'small town', 'rural', 'small-town'}
                
                if user_setting in urban_suburban and prog_setting in urban_suburban:
                    scores.append(0.6)
                elif user_setting in rural_small and prog_setting in rural_small:
                    scores.append(0.6)
                else:
                    scores.append(0.2)
        
        # Housing style - with normalization
        hs_prog = {normalize_string(h) for h in base.get('housing_styles', [])}
        user_hs = {normalize_string(h) for h in HS} if HS else set()
        
        if hs_prog and user_hs:
            housing_score = len(user_hs.intersection(hs_prog)) / len(user_hs)
            scores.append(housing_score)
        elif not user_hs:
            scores.append(0.5)
        else:
            scores.append(0.2)
        
        # Campus size - using distance-based scoring
        campus_size_order = ["Small", "Medium", "Large"]
        user_cps = CPS if CPS else 'Medium'
        prog_cps = base.get('campus_size', 'Medium')
        
        user_cps_normalized = user_cps.capitalize() if user_cps else 'Medium'
        prog_cps_normalized = prog_cps.capitalize() if prog_cps else 'Medium'
        
        campus_score = score_categorical_distance(user_cps_normalized, prog_cps_normalized, campus_size_order)
        scores.append(campus_score)
        
        return sum(scores) / len(scores)

    def score_social(p):
        base = p['social']
        
        # Night scene - with confidence weighting
        prog_ns = base.get('night_scene', 3)
        ns_score = calculate_trait_score_with_confidence(NS, prog_ns)
        
        # Sports - with normalization
        sp_prog = {normalize_string(s) for s in base.get('sports', [])}
        user_spt = {normalize_string(s) for s in SPT} if SPT else set()
        
        if "none" in user_spt or not user_spt:
            spt_score = 1.0
        else:
            spt_score = len(sp_prog.intersection(user_spt)) / max(len(user_spt), 1)
        
        # Clubs - with normalization
        cl_prog = {normalize_string(c) for c in base.get('clubs', [])}
        user_clb = {normalize_string(c) for c in CLB} if CLB else set()
        
        if user_clb:
            cl_score = len(cl_prog.intersection(user_clb)) / len(user_clb)
        else:
            cl_score = 0.5
        
        # Cultural events - with confidence weighting
        prog_cev = base.get('cultural_event_freq', 3)
        cev_score = calculate_trait_score_with_confidence(CEV, prog_cev)
        
        return (ns_score + spt_score + cl_score + cev_score) / 4

    results = []
    for p in programs:
        a = score_academic(p)
        c = score_campus(p)
        s = score_social(p)
        total = (wa*a + wc*c + wso*s) / W_TOTAL
        results.append({
            "school": p['uni'],
            "program": p['program'],
            "overall": total,
            "academic": a,
            "campus": c,
            "social": s
        })
    results.sort(key=lambda x: x["overall"], reverse=True)
    return results[:num_results]

@app.route('/api/match', methods=['POST'])
def match_api():
    try:
        data = request.json
        matches = compute_matches(data)
        return jsonify(matches)
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/chance-me', methods=['POST'])
def chance_me_api():
    try:
        data = request.json
        
        # Extract data from request
        university = data.get('school', '')
        program = data.get('program', '')
        top6_avg = float(data.get('top6', 0))
        ecs_input = data.get('ecs', '')
        
        # Parse ECs (split by comma and clean up)
        ecs = []
        if ecs_input:
            ecs = [ec.strip() for ec in ecs_input.split(',') if ec.strip()]
        
        # Path to CSV file (adjust this path as needed)
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admissionsData.csv')
        
        # Get prediction
        result = predict_admission_chance(csv_path, university, program, top6_avg, ecs)
        
        return jsonify({
            "success": True,
            "prediction": result,
            "inputs": {
                "university": university,
                "program": program,
                "top6_average": top6_avg,
                "extracurriculars": ecs
            }
        })
        
    except Exception as e:
        print("ChanceMe Error:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    try:
        # Get results from request
        data = request.json
        results = data.get('results', [])
        weights = data.get('weights', {'wa': 0.6, 'wc': 0.2, 'wso': 0.2})
        
        # Generate PDF bytes
        from match_me import generate_matches_pdf_bytes
        pdf_buffer = generate_matches_pdf_bytes(results, weights)
        
        # Generate filename with timestamp
        filename = f"LinkU_matches_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Send file to client for download
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/full-matches', methods=['POST'])
def get_full_matches():
    try:
        # Get quiz answers
        answers = request.json
        
        # Compute all matches
        results = compute_matches(answers, num_results=100)
        
        # Results are already in the right format, no need to transform
        return jsonify({
            "success": True,
            "matches": results
        })
    except Exception as e:
        print(f"Error computing matches: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# For Flask 2.0+ 
mentors_data = {}

def load_mentors_data():
    global mentors_data
    try:
        mentors_file = os.path.join(os.path.dirname(__file__), 'mentors.json')
        with open(mentors_file, 'r', encoding='utf-8') as f:
            mentors_data = json.load(f)
    except Exception as e:
        print(f"Error loading mentors data: {e}")
        mentors_data = {
            "mentors": [],
            "programMentors": {}
        }

# Load data at startup
load_mentors_data()

@app.route('/api/mentors', methods=['GET'])
def get_all_mentors():
    return jsonify(mentors_data.get('mentors', []))

@app.route('/api/program-mentors/<path:program_key>', methods=['GET'])
def get_program_mentors(program_key):
    try:
        print(f"Received request for program key: {program_key}")
        
        # Debug: Print all available program keys
        available_keys = list(mentors_data.get('programMentors', {}).keys())
        print(f"Available keys: {available_keys}")
        
        # Find specific mentors for this program first
        mentor_ids = mentors_data.get('programMentors', {}).get(program_key, [])
        print(f"Found mentor IDs for {program_key}: {mentor_ids}")
        
        program_mentors = [
            mentor for mentor in mentors_data.get('mentors', []) 
            if mentor['id'] in mentor_ids
        ]
        
        # If we found ANY program-specific mentors, return them (even just one)
        if program_mentors:
            print(f"Found {len(program_mentors)} specific mentors for {program_key}")
            return jsonify(program_mentors)
        
        # Extract university name for fallback
        parts = program_key.split('_')
        university = parts[0] if len(parts) >= 1 else None
        
        # Look for university match if no program match was found
        if university:
            university_mentors = [
                mentor for mentor in mentors_data.get('mentors', [])
                if university.lower() in mentor['school'].lower()
            ]
            
            if university_mentors:
                print(f"Found {len(university_mentors)} mentors from {university}")
                return jsonify(university_mentors[:2])
        
        # Last resort: random mentors
        print("No matches found, using random mentors")
        all_mentors = mentors_data.get('mentors', [])
        random_mentors = random.sample(all_mentors, min(2, len(all_mentors)))
        
        return jsonify(random_mentors)
        
    except Exception as e:
        print(f"Error in program-mentors endpoint: {str(e)}")
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)