"""Rule-based plan builder. It runs locally and never calls an external API."""
from copy import deepcopy


def generate_workout(user: dict) -> dict:
    goal = user["goal"]
    intensity = user["intensity"]
    level = {"Low": (2, "30–35 minutes"), "Medium": (3, "40–45 minutes"), "High": (4, "45–55 minutes")}[intensity]
    sets, session = level

    focus_by_goal = {
        "Weight Loss": ["Full-body movement", "Low-impact cardio", "Lower body + core", "Active recovery", "Upper body + cardio", "Cardio intervals", "Rest and mobility"],
        "Muscle Gain": ["Full body A", "Lower body", "Upper body", "Recovery and mobility", "Full body B", "Core + light cardio", "Rest"],
        "General Wellness": ["Full body basics", "Brisk walk + mobility", "Strength foundations", "Active recovery", "Full body circuit", "Easy cardio", "Rest"],
        "Flexibility": ["Full-body mobility", "Yoga flow", "Hips and hamstrings", "Restorative stretch", "Shoulders and spine", "Gentle yoga", "Rest"],
        "Strength": ["Lower-body strength", "Upper-body strength", "Easy cardio + mobility", "Rest and mobility", "Full-body strength", "Core stability", "Rest"],
        "Endurance": ["Easy cardio base", "Full-body strength", "Steady cardio", "Active recovery", "Cardio intervals", "Long easy session", "Rest"],
    }
    exercises = {
        "Weight Loss": ["Bodyweight squat", "Incline push-up", "Glute bridge", "March in place"],
        "Muscle Gain": ["Chair/bodyweight squat", "Push-up variation", "Hip hinge", "Bird-dog"],
        "General Wellness": ["Sit-to-stand squat", "Wall push-up", "Glute bridge", "Standing march"],
        "Flexibility": ["Cat-cow", "World's-greatest stretch", "Seated hamstring stretch", "Child's pose"],
        "Strength": ["Squat to chair", "Wall or incline push-up", "Hip hinge", "Dead bug"],
        "Endurance": ["Brisk walk or march", "Step-up (low step)", "Bodyweight squat", "Standing knee drive"],
    }
    days = []
    for i, focus in enumerate(focus_by_goal[goal]):
        is_rest = "rest" in focus.lower()
        warmup = "5 minutes of easy walking and comfortable joint circles" if not is_rest else "Optional gentle 5-minute walk"
        if is_rest:
            day_exercises = ["Rest; optional comfortable mobility or an easy walk"]
            prescribed_sets = "—"
            reps = "20–30 minutes optional easy movement"
            rest = "Take a full rest day if tired or sore"
        elif goal == "Flexibility":
            day_exercises = exercises[goal]
            prescribed_sets = "2 rounds"
            reps = "Hold each comfortable stretch for 20–30 seconds; no bouncing"
            rest = "Rest 20–30 seconds between movements"
        else:
            day_exercises = exercises[goal]
            prescribed_sets = f"{sets} sets"
            reps = "8–12 controlled repetitions (or 30 seconds for marching)"
            rest = "Rest 60–90 seconds between sets; extend rest as needed"
        if intensity == "Low" and not is_rest:
            reps = "6–10 easy repetitions (or 20 seconds for marching); stop before strain"
        elif intensity == "High" and not is_rest and goal != "Flexibility":
            reps = "8–12 controlled repetitions; keep 2–3 good-form repetitions in reserve"
        cooldown = "3–5 minutes of easy breathing and gentle, pain-free stretching" if not is_rest else "Prioritize sleep, hydration, and recovery"
        days.append({"day": f"Day {i + 1}", "focus": focus, "warmup": warmup, "exercises": day_exercises,
                     "sets": prescribed_sets, "repetitions": reps, "rest": rest, "cooldown": cooldown, "duration": session if not is_rest else "Recovery day"})
    return {"days": days, "disclaimer": "General wellness guidance only—not medical advice. Stop if you feel pain, dizziness, or unusual shortness of breath. Consult a qualified healthcare or fitness professional if you have health concerns."}


def generate_nutrition_tip(goal: str) -> str:
    tips = {
        "Weight Loss": "Build satisfying meals around vegetables, a protein source, and high-fiber carbohydrates. Avoid extreme restriction; gradual, sustainable habits are safer.",
        "Muscle Gain": "Include a source of protein and varied whole foods in regular meals, and allow enough sleep and recovery between challenging sessions.",
        "General Wellness": "Aim for balanced meals with colorful produce, protein, and fiber-rich carbohydrates, and drink water regularly according to thirst and activity.",
        "Flexibility": "Hydrate regularly and pair mobility practice with balanced meals; gentle movement and adequate sleep support recovery.",
        "Strength": "Eat regular balanced meals with protein and carbohydrates, and schedule recovery time so strength sessions remain comfortable and controlled.",
        "Endurance": "For longer activity, have a familiar balanced meal beforehand and drink water according to thirst; increase activity gradually.",
    }
    return tips.get(goal, tips["General Wellness"])


def update_workout_plan(original: dict, feedback: str, intensity: str) -> dict:
    """Apply safe, transparent local adjustments while preserving the original."""
    result = deepcopy(original)
    text = feedback.casefold()
    if any(word in text for word in ("unsafe", "injury", "pain", "extreme", "starve", "no rest")):
        return result
    for day in result["days"]:
        focus = day["focus"].casefold()
        if "short" in text or "less time" in text or "quick" in text:
            day["duration"] = "20–25 minutes; choose 2–3 movements and keep the pace comfortable"
            day["sets"] = "2 sets (or one easy round)"
        if "reduce" in text or "easier" in text or "lower intensity" in text:
            day["repetitions"] = "6–8 comfortable repetitions; stop well before strain"
            day["sets"] = "2 easy sets" if day["sets"] != "—" else day["sets"]
            day["rest"] = "Rest 90–120 seconds or longer as needed"
        if "cardio" in text and "rest" not in focus:
            day["focus"] = f"{day['focus']} + easy cardio"
            day["exercises"] = list(day["exercises"]) + ["5–10 minutes of easy walking or marching"]
        if "yoga" in text and "rest" not in focus:
            day["cooldown"] = "5–10 minutes of gentle yoga-style mobility; stay within a comfortable range"
        if ("upper body" in text or "upper-body" in text) and "rest" not in focus and "upper" not in focus:
            day["focus"] = f"{day['focus']} with an upper-body emphasis"
        if "rest day" in text or "more rest" in text or "more recovery" in text:
            if day["day"] in ("Day 3", "Day 6"):
                day.update({"focus": "Rest and recovery", "exercises": ["Rest; optional easy walk or gentle mobility"], "sets": "—", "repetitions": "Optional 15–20 minutes easy movement", "rest": "Take a full rest day if tired or sore", "duration": "Recovery day", "cooldown": "Prioritize sleep and comfortable recovery"})
    result["adjustment_note"] = f"Local rule-based adjustment for: {feedback.strip()} (selected intensity: {intensity}). Requests that could be unsafe are not applied."
    return result
