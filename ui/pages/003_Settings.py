import requests
import streamlit as st
from sidebar_utils import side_bar_panel, check_auth

USER_ENDPOINT = "http://localhost:8000/user"

check_auth()

side_bar_panel()

st.header("Account Settings")

st.markdown(
    "<div style='background-color:#FFF3CD; padding:10px; border-radius:5px; margin-bottom:15px;'>"
    "⚠️ Deleting your account is permanent and cannot be undone. "
    "All your orders and favorites will also be permanently deleted."
    "</div>",
    unsafe_allow_html=True
)

if st.button("🗑️ Delete Account"):
    token = st.session_state.get("token")
    if not token:
        st.error("You are not authenticated!")
    else:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.delete(f"{USER_ENDPOINT}", headers=headers, timeout=5)

            if res.status_code == 200:
                st.success("Your account, orders, and favorites have been deleted!")
                # Logout user automatically after deletion
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.experimental_rerun()
            else:
                st.error(f"Failed to remove user: {res.text}")
        except Exception as e:
            st.error(f"Failed request: {e}")


