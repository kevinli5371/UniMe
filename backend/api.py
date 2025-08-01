import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import datetime
import random
from match_me import INTEREST_MAPPINGS, COURSE_MAPPINGS, INTEREST_DESCRIPTIONS, enhanced_interest_score, enhanced_course_score
from chanceMe import predict_admission_chance

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

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
        prog_alt = set(p['academic'].get('alt_to_engineering', []))
        alt_score = 0
        if ALT:
            matched_alts = prog_alt.intersection(set(ALT))
            alt_score = (len(matched_alts) / max(len(ALT), 1)) * 0.1
        keys = ['learning_style', 'first_year_specialization', 'coop_importance', 
                'research_importance', 'creativity_orientation', 'career_certainty', 
                'math_enjoyment', 'collaboration_preference']
        vals = [LS, SP, CO, UR, CR, CE, ME, CP]
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
        total_weight = sum(weights.values())
        num_scores = []
        for k, s in zip(keys, vals):
            prog_val = p['academic'].get(k, 3)
            similarity = 1 - (abs(prog_val - s) / 4.0)
            weight = weights[k]
            num_scores.append(similarity * weight)
        num_score = sum(num_scores) / total_weight * 0.3
        return i_score + lc_score + num_score + alt_score

    def score_campus(p):
        base = p['campus']
        scores = []
        if base.get('class_size_bin') == CSB:
            scores.append(1.0)
        else:
            if CSB == "< 60" and base.get('class_size_bin') == "60-200":
                scores.append(0.5)
            elif CSB == "200+" and base.get('class_size_bin') == "60-200":
                scores.append(0.5)
            else:
                scores.append(0.0)
        if base.get('setting') == SET:
            scores.append(1.0)
        else:
            urban_suburban = {"Urban", "Suburban"}
            rural_small = {"Small-town", "Rural"}
            if SET in urban_suburban and base.get('setting') in urban_suburban:
                scores.append(0.5)
            elif SET in rural_small and base.get('setting') in rural_small:
                scores.append(0.5)
            else:
                scores.append(0.0)
        hs_prog = set(base.get('housing_styles', []))
        if hs_prog:
            housing_score = len(HS.intersection(hs_prog)) / len(HS) if HS else 0
            scores.append(housing_score)
        else:
            scores.append(0.0)
        if base.get('campus_size') == CPS:
            scores.append(1.0)
        else:
            sizes = ["Small", "Medium", "Large"]
            user_idx = sizes.index(CPS) if CPS in sizes else -1
            prog_idx = sizes.index(base.get('campus_size')) if base.get('campus_size') in sizes else -1
            if user_idx != -1 and prog_idx != -1:
                scores.append(0.5 if abs(user_idx - prog_idx) == 1 else 0.0)
            else:
                scores.append(0.0)
        return sum(scores) / len(scores)

    def score_social(p):
        base = p['social']
        prog_ns = base.get('night_scene', 3)
        ns_score = 1 - (abs(prog_ns - NS) / 4.0)
        sp_prog = set(base.get('sports', []))
        if "None" in SPT:
            spt_score = 1.0
        else:
            spt_score = len(sp_prog.intersection(SPT)) / max(len(SPT), 1)
        cl_prog = set(base.get('clubs', []))
        cl_score = len(cl_prog.intersection(CLB)) / max(len(CLB), 1) if CLB else 0.5
        prog_cev = base.get('cultural_event_freq', 3)
        cev_score = 1 - (abs(prog_cev - CEV) / 4.0)
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
        print("Request received!")  # Debug print
        data = request.json
        print("Received data:", data)  # Debug print
        matches = compute_matches(data)
        return jsonify(matches)
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/api/chance-me', methods=['POST'])
def chance_me_api():
    try:
        print("ChanceMe request received!")  # Debug print
        data = request.json
        print("Received ChanceMe data:", data)  # Debug print
        
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
        csv_path = 'backend/admissionsData.csv'
        
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
    print("Starting Flask server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)