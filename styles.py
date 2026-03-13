import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        .main {
            background-color: #0f1117;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .soft-card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 18px;
            background: rgba(255,255,255,0.03);
            margin-bottom: 14px;
        }
        .metric-card {
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 12px;
            color: white;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .small-label {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 6px;
        }
        .big-text {
            font-size: 1.15rem;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
