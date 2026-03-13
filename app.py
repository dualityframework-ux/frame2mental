import streamlit as st

from renderers import (
    render_checkin_tab,
    render_dashboard_tab,
    render_frame_tab,
    render_settings_tab,
    render_support_tab,
    render_tools_tab,
)
from settings import load_settings
from storage import load_checkins
from styles import apply_styles

st.set_page_config(page_title="frame2mental", page_icon="🧠", layout="wide")


def main():
    apply_styles()

    st.title("frame2mental")
    st.caption("check in → get your frame → reset → learn your pattern")

    if "checkins" not in st.session_state:
        st.session_state.checkins = load_checkins()

    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "daily check-in",
            "your frame",
            "pattern dashboard",
            "reset tools",
            "support",
            "settings",
        ]
    )

    with tab1:
        render_checkin_tab()

    with tab2:
        render_frame_tab()

    with tab3:
        render_dashboard_tab()

    with tab4:
        render_tools_tab()

    with tab5:
        render_support_tab()

    with tab6:
        render_settings_tab()


if __name__ == "__main__":
    main()
