"""page ui"""

import streamlit as st

from app.constants import APP_PAGE_ICON, APP_PAGE_TITLE, APP_SIDEBAR_LOGO


def set_page_layout() -> None:
    """ページレイアウト設定"""
    st.set_page_config(
        page_title=APP_PAGE_TITLE,
        page_icon=APP_PAGE_ICON,
        layout="centered",
    )
    st.title(APP_PAGE_TITLE)
    st.caption("development by streamlit")

    if APP_SIDEBAR_LOGO is not None:
        st.sidebar.image(APP_SIDEBAR_LOGO, width=180)
