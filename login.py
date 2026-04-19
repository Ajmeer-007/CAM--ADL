import streamlit as st


def render() -> None:
    st.markdown(
        """
        <div class="login-container">
            <div class="login-card">
                <div class="login-header">
                    <h2>Welcome Back</h2>
                    <p>Enter your credentials to access the dashboard</p>
                </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email Address", placeholder="name@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        # Add a little spacing before the button through markdown or just let Streamlit do it.
        st.markdown("<br>", unsafe_allow_html=True)
        
        login_clicked = st.form_submit_button("Sign In ✨", use_container_width=True)
        if login_clicked:
            if email.strip() and password.strip():
                st.session_state.logged_in = True
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.error("Please enter your email and password.")

    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )