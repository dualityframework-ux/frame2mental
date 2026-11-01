"""Tests for frame²mental's engine: frames, tones, warnings, patterns, plans, storage and safety resources."""
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import data  # noqa: E402
import settings  # noqa: E402
import storage  # noqa: E402
from engine import (  # noqa: E402
    analyze_journal, apply_tone, build_frame, build_pattern_summary, build_reset_plan, build_weekly_summary,
    calculate_warning_score, detect_early_warning_patterns, detect_risk_flags, get_mood_style, get_warning_level,
)


def ci(mood=5, stress=5, anxiety=5, sleep=6, energy=5):
    return {"mood": mood, "stress": stress, "anxiety": anxiety, "sleep": sleep, "energy": energy}


OVERWHELM = ci(stress=9, anxiety=9, sleep=3)
OVERLOAD = ci(stress=7, sleep=5)
STUCK = ci(anxiety=8, sleep=7, energy=3)
DRAINED = ci(mood=3, sleep=7, energy=3)
STEADY = ci(mood=8, stress=3, anxiety=3, sleep=8, energy=7)
MIXED = ci()
ALL_FRAMES = [OVERWHELM, OVERLOAD, STUCK, DRAINED, STEADY, MIXED]


# ---------------------------------------------------------------- frames

@pytest.mark.parametrize("checkin,phrase", [
    (OVERWHELM, "overloaded and under-recovered"),
    (OVERLOAD, "compounding each other"),
    (STUCK, "overactivation and depletion"),
    (DRAINED, "emotionally drained"),
    (STEADY, "enough recovery"),
    (MIXED, "tension between"),
])
def test_each_frame_branch(checkin, phrase):
    assert phrase in build_frame(checkin)["mechanism"]


def test_frame_has_all_four_parts():
    for c in ALL_FRAMES:
        assert set(build_frame(c)) == {"observation", "mechanism", "implication", "next_step"}


def test_overwhelm_takes_priority_over_overload():
    # 9/9/3 also matches the stress+sleep rule; the more severe frame must win
    assert "overwhelm" in build_frame(OVERWHELM)["implication"]


# ---------------------------------------------------------------- tones

def test_calm_tone_adds_gentle_prefixes():
    t = apply_tone(build_frame(MIXED), "calm")
    assert t["observation"].startswith("gently noticing:") and t["next_step"].startswith("for now:")


def test_unknown_tone_falls_back_to_calm():
    assert apply_tone(build_frame(MIXED), "anything")["observation"].startswith("gently noticing:")


def test_encouraging_tone():
    t = apply_tone(build_frame(STEADY), "encouraging")
    assert t["implication"].startswith("be gentle with yourself")


@pytest.mark.parametrize("checkin", ALL_FRAMES)
def test_direct_tone_drops_hedging_but_stays_grammatical(checkin):
    t = apply_tone(build_frame(checkin), "direct")
    text = " ".join(t.values())
    assert not re.search(r"\bmay\b", text)
    # regression: hedges used to be deleted outright, leaving "your system overloaded", "you emotionally drained"
    assert not re.search(r"\b(system|you|fatigue|there) (overloaded|stuck|getting|emotionally|compounding|tension)\b", text)


def test_direct_tone_examples():
    assert apply_tone(build_frame(OVERWHELM), "direct")["mechanism"].startswith("your system is overloaded")
    assert apply_tone(build_frame(DRAINED), "direct")["mechanism"].startswith("you are emotionally drained")
    assert apply_tone(build_frame(OVERLOAD), "direct")["mechanism"].startswith("pressure and fatigue are compounding")


def test_apply_tone_does_not_mutate_the_frame():
    f = build_frame(MIXED)
    before = dict(f)
    apply_tone(f, "direct")
    assert f == before


# ---------------------------------------------------------------- warnings

def test_warning_score_bounds_and_levels():
    assert calculate_warning_score(STEADY) == 0
    worst = ci(mood=1, stress=10, anxiety=10, sleep=1, energy=1)
    assert calculate_warning_score(worst) == 20
    assert [get_warning_level(s) for s in (0, 7, 8, 12, 13, 20)] == ["low", "low", "moderate", "moderate", "high", "high"]


def test_risk_flags():
    assert detect_risk_flags(STEADY) == []
    flags = detect_risk_flags(ci(mood=2, stress=9, anxiety=9, sleep=3, energy=2))
    assert len(flags) == 4


def test_early_warning_needs_three_checkins():
    assert detect_early_warning_patterns([STEADY, MIXED]) == []


def test_early_warning_trends():
    trend = [ci(mood=7, stress=3, sleep=8), ci(mood=5, stress=5, sleep=6), ci(mood=3, stress=7, sleep=4)]
    alerts = detect_early_warning_patterns(trend)
    assert "mood has dropped across the last 3 check-ins" in alerts
    assert "stress has risen across the last 3 check-ins" in alerts
    assert "low sleep and high stress are appearing together" in alerts


def test_flat_week_raises_no_trend_alerts():
    assert detect_early_warning_patterns([STEADY, STEADY, STEADY]) == []


# ---------------------------------------------------------------- patterns and summaries

def test_pattern_summary():
    assert build_pattern_summary([]) == "no pattern data yet"
    assert "higher stress" in build_pattern_summary([OVERLOAD, OVERWHELM])
    assert "steadiness" in build_pattern_summary([STEADY] * 3)


def test_weekly_summary_uses_last_seven_only():
    old_bad = [OVERWHELM] * 10
    recent_good = [STEADY] * 7
    assert "steadier" in build_weekly_summary(old_bad + recent_good)


def test_journal_keywords_and_priority():
    assert analyze_journal("  ").startswith("no journal note")
    assert "overload" in analyze_journal("I feel overwhelmed and anxious")  # stress words are checked first
    assert "anxious tension" in analyze_journal("racing thoughts tonight")
    assert "heaviness" in analyze_journal("pretty lonely")
    assert "recovery" in analyze_journal("feeling calmer")


def test_mood_style_bands():
    assert [get_mood_style(m)["label"] for m in (1, 3, 4, 6, 7, 10)] == ["heavy day"] * 2 + ["mixed day"] * 2 + ["steady day"] * 2


# ---------------------------------------------------------------- reset plans

def test_reset_plan_for_a_good_day():
    assert build_reset_plan(STEADY, []) == ["keep protecting what is working and check in again tomorrow"]


def test_reset_plan_suggests_reaching_out_when_alerts_fire():
    plan = build_reset_plan(OVERWHELM, ["stress has risen across the last 3 check-ins"])
    assert any("trusted person" in step for step in plan)
    assert any("sleep" in step for step in plan) and any("grounding" in step for step in plan)


# ---------------------------------------------------------------- safety resources

def test_crisis_resources_include_988():
    text = json.dumps(data.SUPPORT_RESOURCES).lower()
    assert "988" in text


# ---------------------------------------------------------------- storage

def test_checkins_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", tmp_path / "checkins.json")
    assert storage.load_checkins() == []
    storage.save_checkins([STEADY])
    assert storage.load_checkins() == [STEADY]


def test_corrupt_checkins_file_returns_empty(tmp_path, monkeypatch):
    f = tmp_path / "checkins.json"
    f.write_text("{not json")
    monkeypatch.setattr(storage, "DATA_FILE", f)
    assert storage.load_checkins() == []


def test_settings_fill_in_defaults(tmp_path, monkeypatch):
    f = tmp_path / "settings.json"
    f.write_text(json.dumps({"name": "Ian"}))
    monkeypatch.setattr(settings, "SETTINGS_FILE", f)
    s = settings.load_settings()
    assert s["name"] == "Ian" and s["preferred_tone"] == "calm"
