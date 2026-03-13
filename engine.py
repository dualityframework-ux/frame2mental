def build_frame(checkin: dict) -> dict:
    mood = checkin["mood"]
    stress = checkin["stress"]
    anxiety = checkin["anxiety"]
    sleep = checkin["sleep"]
    energy = checkin["energy"]

    if stress >= 8 and anxiety >= 8 and sleep <= 4:
        return {
            "observation": "stress and anxiety are both very high while sleep is very low",
            "mechanism": "your system may be overloaded and under-recovered at the same time",
            "implication": "this looks more like overwhelm than a motivation problem",
            "next_step": "reduce pressure, lower stimulation, and use a grounding reset right now",
        }

    if stress >= 7 and sleep <= 5:
        return {
            "observation": "stress is elevated and sleep is running low",
            "mechanism": "pressure and fatigue may be compounding each other",
            "implication": "this may be overload, not failure",
            "next_step": "lower the pressure today and use a short grounding reset",
        }

    if anxiety >= 7 and energy <= 4:
        return {
            "observation": "anxiety is high and energy feels low",
            "mechanism": "your system may be stuck between mental overactivation and depletion",
            "implication": "pushing harder may increase the spiral",
            "next_step": "pause, breathe slowly, and reduce stimulation for the next 10 minutes",
        }

    if mood <= 4 and energy <= 4:
        return {
            "observation": "mood and energy are both trending low",
            "mechanism": "you may be emotionally drained, not just unmotivated",
            "implication": "today may require care before output",
            "next_step": "choose one small supportive action instead of expecting a full reset",
        }

    if mood >= 7 and stress <= 4:
        return {
            "observation": "your emotional state looks relatively steady today",
            "mechanism": "your system may be getting enough recovery and less internal friction",
            "implication": "this is a good day to notice what is helping",
            "next_step": "write down what is working so you can repeat it later",
        }

    return {
        "observation": "your check-in shows a mixed emotional state",
        "mechanism": "there may be tension between what your mind needs and what the day is asking from you",
        "implication": "clarity matters more than judgment right now",
        "next_step": "do one small reset and check back in later",
    }


def build_pattern_summary(checkins: list[dict]) -> str:
    if not checkins:
        return "no pattern data yet"

    avg_stress = sum(item["stress"] for item in checkins) / len(checkins)
    avg_sleep = sum(item["sleep"] for item in checkins) / len(checkins)
    avg_mood = sum(item["mood"] for item in checkins) / len(checkins)
    avg_anxiety = sum(item["anxiety"] for item in checkins) / len(checkins)
    avg_energy = sum(item["energy"] for item in checkins) / len(checkins)

    if avg_stress >= 7 and avg_sleep <= 6:
        return "recent pattern: higher stress is showing up alongside lower sleep"

    if avg_anxiety >= 7 and avg_energy <= 5:
        return "recent pattern: anxiety has been elevated while energy stays lower"

    if avg_mood <= 4.5:
        return "recent pattern: your mood trend has been running lower than baseline"

    if avg_mood >= 7 and avg_stress <= 5:
        return "recent pattern: your recent check-ins suggest more emotional steadiness"

    return "recent pattern: mixed signals so far — keep checking in to make the pattern clearer"


def detect_risk_flags(checkin: dict) -> list[str]:
    flags = []

    if checkin["sleep"] <= 3:
        flags.append("very low sleep can intensify emotional strain")

    if checkin["stress"] >= 9:
        flags.append("stress is extremely elevated right now")

    if checkin["anxiety"] >= 9:
        flags.append("anxiety is extremely elevated right now")

    if checkin["mood"] <= 2 and checkin["energy"] <= 2:
        flags.append("very low mood and energy may signal a hard day that needs extra support")

    return flags


def analyze_journal(note: str) -> str:
    if not note or not note.strip():
        return "no journal note yet — even one sentence can help reveal the pattern"

    text = note.lower()

    stress_words = ["overwhelmed", "stressed", "pressure", "too much", "burned out", "burnout"]
    sadness_words = ["sad", "down", "empty", "hopeless", "lonely", "numb"]
    anxiety_words = ["anxious", "panic", "nervous", "racing", "worried", "tense"]
    recovery_words = ["better", "calmer", "rested", "good", "steady", "okay"]

    if any(word in text for word in stress_words):
        return "your note suggests overload or pressure may be a major part of today"

    if any(word in text for word in anxiety_words):
        return "your note suggests mental overactivation or anxious tension may be present"

    if any(word in text for word in sadness_words):
        return "your note suggests emotional heaviness or lower mood may be part of the pattern"

    if any(word in text for word in recovery_words):
        return "your note suggests some recovery or steadiness may be showing up today"

    return "your note adds useful context — keep tracking language patterns over time"


def build_weekly_summary(checkins: list[dict]) -> str:
    if not checkins:
        return "no weekly summary yet"

    recent = checkins[-7:]
    avg_mood = sum(item["mood"] for item in recent) / len(recent)
    avg_stress = sum(item["stress"] for item in recent) / len(recent)
    avg_sleep = sum(item["sleep"] for item in recent) / len(recent)

    if avg_stress >= 7 and avg_sleep <= 6:
        return "this week looks stress-heavy with lower sleep. the pattern suggests recovery needs more protection."

    if avg_mood >= 7 and avg_stress <= 5:
        return "this week looks steadier overall. try to notice what routines or conditions helped."

    if avg_mood <= 4.5:
        return "this week looks emotionally heavy. lower the bar, increase support, and focus on smaller resets."

    return "this week shows mixed signals. more consistent check-ins will make the pattern easier to read."


def get_mood_style(mood: int) -> dict:
    if mood <= 3:
        return {
            "label": "heavy day",
            "description": "more care, less pressure",
            "bg": "linear-gradient(135deg, #5c4b51, #3b2f35)",
        }
    if mood <= 6:
        return {
            "label": "mixed day",
            "description": "slow down and listen to the pattern",
            "bg": "linear-gradient(135deg, #5c5a4b, #3d3a2f)",
        }
    return {
        "label": "steady day",
        "description": "notice what is helping",
        "bg": "linear-gradient(135deg, #425b52, #2d3d37)",
    }


def calculate_warning_score(checkin: dict) -> int:
    score = 0

    score += max(0, 6 - checkin["mood"])
    score += max(0, checkin["stress"] - 5)
    score += max(0, checkin["anxiety"] - 5)
    score += max(0, 6 - checkin["sleep"])
    score += max(0, 6 - checkin["energy"])

    return min(score, 20)


def get_warning_level(score: int) -> str:
    if score >= 13:
        return "high"
    if score >= 8:
        return "moderate"
    return "low"


def detect_early_warning_patterns(checkins: list[dict]) -> list[str]:
    alerts = []

    if len(checkins) < 3:
        return alerts

    recent = checkins[-3:]

    moods = [x["mood"] for x in recent]
    stresses = [x["stress"] for x in recent]
    anxieties = [x["anxiety"] for x in recent]
    sleeps = [x["sleep"] for x in recent]
    energies = [x["energy"] for x in recent]

    if moods[0] > moods[1] > moods[2]:
        alerts.append("mood has dropped across the last 3 check-ins")

    if stresses[0] < stresses[1] < stresses[2]:
        alerts.append("stress has risen across the last 3 check-ins")

    if anxieties[0] < anxieties[1] < anxieties[2]:
        alerts.append("anxiety has risen across the last 3 check-ins")

    if sleeps[0] > sleeps[1] > sleeps[2]:
        alerts.append("sleep has fallen across the last 3 check-ins")

    if energies[0] > energies[1] > energies[2]:
        alerts.append("energy has fallen across the last 3 check-ins")

    if recent[-1]["sleep"] <= 5 and recent[-1]["stress"] >= 7:
        alerts.append("low sleep and high stress are appearing together")

    if recent[-1]["mood"] <= 4 and recent[-1]["energy"] <= 4:
        alerts.append("low mood and low energy are appearing together")

    return alerts


def build_reset_plan(checkin: dict, alerts: list[str]) -> list[str]:
    plan = []

    if checkin["sleep"] <= 5:
        plan.append("protect sleep tonight: reduce screens, lower stimulation, and aim for a calmer evening")

    if checkin["stress"] >= 7:
        plan.append("lower pressure where possible: shrink the to-do list to the next 1 or 2 important things")

    if checkin["anxiety"] >= 7:
        plan.append("use a grounding or breathing reset before making the next decision")

    if checkin["mood"] <= 4 or checkin["energy"] <= 4:
        plan.append("replace performance pressure with one supportive action: water, food, rest, sunlight, or a short walk")

    if alerts:
        plan.append("consider reaching out to one trusted person earlier rather than waiting for things to feel worse")

    if not plan:
        plan.append("keep protecting what is working and check in again tomorrow")

    return plan
