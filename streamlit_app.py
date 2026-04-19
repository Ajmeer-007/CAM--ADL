import streamlit as st

import dashboard
import history
import login
import model_info
import predict
from app_utils import clear_session_and_logout, init_state, inject_styles, set_page


PAGES = {
    "Dashboard": dashboard.render,
    "Predict": predict.render,
    "History": history.render,
    "Model Info": model_info.render,
}


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="nav-title">CM-ADAL</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="nav-current">Current: {st.session_state.page}</div>', unsafe_allow_html=True)
        for page_name in PAGES:
            if st.button(
                page_name,
                use_container_width=True,
                type="primary" if st.session_state.page == page_name else "secondary",
                key=f"nav_{page_name}",
            ):
                st.session_state.page = page_name
                st.rerun()
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            clear_session_and_logout()
            st.rerun()


def main() -> None:
    set_page()
    inject_styles()
    init_state()

    if not st.session_state.logged_in:
        login.render()
        return

    render_sidebar()
    PAGES[st.session_state.page]()


if __name__ == "__main__":
    main()
