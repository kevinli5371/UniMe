import pandas as pd
import re

def clean_words(text):
    """Helper function to lowercase and tokenize words."""
    return set(re.findall(r'\b\w+\b', str(text).lower()))

def match_ec_strength(user_ecs, notes_series, max_bonus=3):
    """
    More flexible EC matching. Partial matches against full notes.
    """
    match_count = 0

    for note in notes_series.fillna(''):
        note_lower = note.lower()
        for ec in user_ecs:
            if ec.lower() in note_lower:
                match_count += 1

    base_bonus = 1 if len(user_ecs) >= 3 else 0
    flexible_bonus = match_count * 0.5

    total_bonus = min(base_bonus + flexible_bonus, max_bonus)
    return round(total_bonus, 1)

def predict_admission_chance(csv_path, university, program_name, user_avg, user_ecs=None):
    # Load CSV, skip metadata comment line
    df = pd.read_csv(csv_path, skiprows=[1])
    df.columns = df.columns.str.strip()

    # Clean numeric average values
    df["Top 6 Average"] = pd.to_numeric(df["Top 6 Average"], errors="coerce")
    df = df.dropna(subset=["Top 6 Average"])

    # Match rows by partial (case-insensitive) substring match for program name
    university_match = df["University"].str.lower() == university.lower()
    program_match = df["Program name"].str.lower().str.contains(program_name.lower(), regex=False)
    decision_match = df["Decision"].str.lower() == "offer"

    offers = df[university_match & program_match & decision_match]

    if offers.empty:
        return "⚠️ No offer data found for that program."

    avg_accept = offers["Top 6 Average"].mean()
    min_accept = offers["Top 6 Average"].min()
    max_accept = offers["Top 6 Average"].max()

    # Check for supp app
    supp_required = offers["Supp App?"].fillna('').str.strip().astype(bool).any()


    # EC scoring
    ec_bonus = 0
    if supp_required and user_ecs:
        combined_notes = offers["Notable info from supp app"].fillna('') + " " + offers["Comments"].fillna('')
        ec_bonus = match_ec_strength(user_ecs, combined_notes)

    adjusted_avg = user_avg + ec_bonus

    # Verdict
        # Calculate prediction score
    if adjusted_avg >= max_accept:
        score = 95 + ((adjusted_avg - max_accept) / 5) * 5  # small bonus if far above max
        verdict = "✅ Very likely"
    elif adjusted_avg >= avg_accept:
        score = 75 + ((adjusted_avg - avg_accept) / (max_accept - avg_accept)) * 19
        verdict = "✅ Likely"
    elif adjusted_avg >= min_accept:
        score = 50 + ((adjusted_avg - min_accept) / (avg_accept - min_accept)) * 24
        verdict = "⚠️ Possible, but below average"
    else:
        score = max(10, (adjusted_avg / min_accept) * 40)  # still give a small score
        verdict = "❌ Unlikely"

    score = min(round(score, 1), 100)


    return f"""
🎓 Program: {program_name} at {university}
📑 Supplementary App Required: {'Yes' if supp_required else 'No'}
📈 Your average: {user_avg}% + EC bonus ({ec_bonus}%) → {adjusted_avg:.1f}%
📊 Past offers average: {avg_accept:.1f}%
🔎 Offer range: {min_accept:.1f}% – {max_accept:.1f}%
🎯 Predicted chance: {score}%
"""


# === Example Usage ===
if __name__ == "__main__":
    csv_file = "admissionsData.csv"
    university = "Waterloo"
    program = "Software Engineering"
    top6 = 93
    ecs = ["robotics", "student council", "volunteering"]

    print(predict_admission_chance(csv_file, university, program, top6, ecs))
