import streamlit as st

# 1. Clear Authentication and User Data
if st.session_state.get("logged_in", False):
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.current_user = None

    # 2. Reset Application State
    st.session_state.cart = []
    st.session_state.search = ""
    st.session_state.auth_mode = "login"
    st.session_state.chat_open = False

# 3. REDIRECT TO THE ROOT
# This moves the browser from localhost:8000/Logout to localhost:8000/
# Your check_auth() in Main.py will see 'logged_in=False' and show the login form.
st.switch_page("Main.py")