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
