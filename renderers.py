from settings import save_settings
import pandas as pd
import streamlit as st

from data import RESET_TOOLS, SUPPORT_RESOURCES
from engine import (
    analyze_journal,
    apply_tone,
    build_frame,
    build_pattern_summary,
    build_reset_plan,
    build_weekly_summary,
    calculate_warning_score,
    detect_early_warning_patterns,
    detect_risk_flags,
    get_mood_style,
    get_warning_level,
)
from storage import save_checkins


def render_checkin_tab():
    st.subheader("daily check-in")

    col1, col2 = st.columns(2)

    with col1:
        mood = st.slider("mood", 1, 10, 5)
        stress = st.slider("stress", 1, 10, 5)
        anxiety = st.slider("anxiety", 1, 10, 5)

    with col2:
        sleep = st.slider("sleep hours", 0, 12, 7)
        energy = st.slider("energy", 1, 10, 5)
        note = st.text_area("short note", placeholder="how are you feeling today?")

    mood_style = get_mood_style(mood)
    st.markdown(
        f"""
        <div class="metric-card" style="background:{mood_style['bg']};">
            <div class="small-label">current mood state</div>
            <div class="big-text">{mood_style['label']}</div>
            <div>{mood_style['description']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("save check-in", use_container_width=True):
        checkin = {
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "mood": mood,
            "stress": stress,
            "anxiety": anxiety,
            "sleep": sleep,
            "energy": energy,
            "note": note,
        }
        st.session_state.checkins.append(checkin)
        save_checkins(st.session_state.checkins)
        st.success("check-in saved")

    if st.session_state.checkins:
        st.markdown("### latest check-in")
        st.json(st.session_state.checkins[-1])

        if st.button("clear all check-ins", use_container_width=True):
            st.session_state.checkins = []
            save_checkins([])
            st.warning("all check-ins cleared")


def render_frame_tab():
    st.subheader("your frame")

    if not st.session_state.checkins:
        st.info("save a check-in first to generate your frame")
        return

    latest = st.session_state.checkins[-1]

    settings = st.session_state.settings
    name = settings.get("name", "").strip()

    if name:
        st.markdown(f"### {name}, here is your frame.")
    else:
        st.markdown("### here is your frame.")

    raw_frame = build_frame(latest)
    tone = st.session_state.settings.get("preferred_tone", "calm")
    frame = apply_tone(raw_frame, tone)
    flags = detect_risk_flags(latest)
    journal_insight = analyze_journal(latest.get("note", ""))
    warning_score = calculate_warning_score(latest)
    warning_level = get_warning_level(warning_score)
    early_alerts = detect_early_warning_patterns(st.session_state.checkins)
    reset_plan = build_reset_plan(latest, early_alerts)

    st.markdown(
        f"""
        <div class="soft-card">
            <div class="small-label">observation</div>
            <div class="big-text">{frame['observation']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="soft-card">
            <div class="small-label">mechanism</div>
            <div>{frame['mechanism']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="soft-card">
            <div class="small-label">implication</div>
            <div>{frame['implication']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(frame["next_step"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### pattern summary")
        st.write(build_pattern_summary(st.session_state.checkins))

        st.markdown("### journal insight")
        st.write(journal_insight)

    with col2:
        st.markdown("### early warning score")
        st.write(f"score: {warning_score}/20")
        st.write(f"level: {warning_level}")

    if early_alerts:
        st.markdown("### early warning patterns")
        for alert in early_alerts:
            st.warning(alert)

    st.markdown("### reset plan")
    for step in reset_plan:
        st.markdown(f"- {step}")

    if flags:
        st.markdown("### watch-outs")
        for flag in flags:
            st.warning(flag)


def render_dashboard_tab():
    st.subheader("pattern dashboard")

    if not st.session_state.checkins:
        st.info("save a few check-ins to see patterns")
        return

    df = pd.DataFrame(st.session_state.checkins)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    st.markdown("### weekly summary")
    st.info(build_weekly_summary(st.session_state.checkins))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### mood over time")
        st.line_chart(df.set_index("date")["mood"])

        st.markdown("### anxiety over time")
        st.line_chart(df.set_index("date")["anxiety"])

        st.markdown("### energy over time")
        st.line_chart(df.set_index("date")["energy"])

    with col2:
        st.markdown("### stress over time")
        st.line_chart(df.set_index("date")["stress"])

        st.markdown("### sleep over time")
        st.line_chart(df.set_index("date")["sleep"])

    st.markdown("### check-in history")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "export check-ins to csv",
        data=csv,
        file_name="frame2mental_checkins.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render_tools_tab():
    st.subheader("reset tools")

    for category, tools in RESET_TOOLS.items():
        with st.expander(category):
            for tool in tools:
                st.markdown(f"- **{tool['name']}** — {tool['description']}")


def render_support_tab():
    st.subheader("support")

    st.warning(
        "if you are in immediate danger or think you may harm yourself, call emergency services immediately."
    )

    for item in SUPPORT_RESOURCES:
        st.markdown(f"**{item['name']}**")
        st.write(item["description"])
        st.write(item["contact"])
        st.markdown("---")

def render_settings_tab():
    st.subheader("settings")

    settings = st.session_state.settings

    name = st.text_input("name", value=settings.get("name", ""))
    preferred_tone = st.selectbox(
        "preferred tone",
        ["calm", "direct", "encouraging"],
        index=["calm", "direct", "encouraging"].index(settings.get("preferred_tone", "calm")),
    )
    focus_area = st.selectbox(
        "focus area",
        ["stress", "anxiety", "sleep", "burnout", "self-awareness"],
        index=["stress", "anxiety", "sleep", "burnout", "self-awareness"].index(
            settings.get("focus_area", "stress")
        ),
    )
    daily_reminder = st.text_input(
        "daily reminder time",
        value=settings.get("daily_reminder", "09:00"),
    )

if st.button("save settings", use_container_width=True):
    st.session_state.settings = {
        "name": name,
        "preferred_tone": preferred_tone,
        "focus_area": focus_area,
        "daily_reminder": daily_reminder,
    }
    save_settings(st.session_state.settings)
    st.success("settings saved")
