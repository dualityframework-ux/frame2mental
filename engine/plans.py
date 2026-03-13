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
