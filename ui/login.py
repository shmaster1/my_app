import requests
import streamlit as st
import jwt

AUTH_END_POINT = "http://localhost:8000/auth"
USER_END_POINT = "http://localhost:8000/user"


def show_login_page():
    # 1. Initialize session state variables if they don't exist
    # This prevents crashes when checking keys later
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Hide sidebar until logged in
    st.markdown(
        "<style>[data-testid='stSidebarNav'] {display: none;}</style>",
        unsafe_allow_html=True
    )

    _, col, _ = st.columns([1, 2, 1])

    with col:
        if st.session_state.auth_mode == "login":
            st.markdown("<h1 style='text-align:center;'>🔐 Login</h1>", unsafe_allow_html=True)

            with st.form("login_form"):
                username = st.text_input("Username*")
                pwd_input = st.text_input("Password*", type="password")
                submit_clicked = st.form_submit_button("Log In", use_container_width=True)

            if submit_clicked:
                try:
                    payload = {"username": username, "password": pwd_input}
                    res = requests.post(f"{AUTH_END_POINT}/token", data=payload, timeout=5)

                    if res.status_code == 200:
                        data = res.json()
                        token_value = data.get("jwt_token") or data.get("access_token")

                        if token_value:
                            # Decode the token to get the user ID
                            decoded = jwt.decode(token_value, options={"verify_signature": False})
                            user_id = decoded.get("user_id") or decoded.get("sub") or decoded.get("id")

                            st.session_state.token = token_value
                            st.session_state.logged_in = True
                            st.session_state.current_user = {
                                "id": user_id,
                                "username": username,
                            }

                            st.rerun()

                    else:
                        st.error("Invalid username or password.")
                except Exception as e:
                    st.error(f"Connection error: {e}")

            if st.button("Sign Up"):
                st.session_state.auth_mode = "register"
                st.rerun()

        else:
            st.markdown("<h1 style='text-align:center;'>📝 Create Account</h1>", unsafe_allow_html=True)

            with st.form("register_form"):
                username = st.text_input("Username*")
                firstname = st.text_input("First Name*")
                lastname = st.text_input("Last Name*")
                email = st.text_input("Email*")
                phone = st.text_input("Phone*")
                country = st.text_input("Country*")
                city = st.text_input("City*")
                password_input = st.text_input("Password*", type="password")
                confirm_pass_input = st.text_input("Confirm Password*", type="password")

                if st.form_submit_button("Register", use_container_width=True):
                    fields = [username, firstname, lastname, email, phone, country, city, password_input,
                              confirm_pass_input]
                    if not all(fields):
                        st.error("All fields marked with * are mandatory.")
                    elif password_input != confirm_pass_input:
                        st.error("Passwords do not match")
                    else:
                        try:
                            # 2. SERVER-SIDE VALIDATION
                            check_res = requests.get(f"{USER_END_POINT}/check-username/{username}", timeout=5)
                            if check_res.status_code == 200:
                                if check_res.json().get("is_taken"):
                                    st.error("Username taken, please try again ❌")
                                else:
                                    # 3. CREATION
                                    payload = {
                                        "username": username,
                                        "first_name": firstname,
                                        "last_name": lastname,
                                        "email": email,
                                        "phone": phone,
                                        "country": country,
                                        "city": city,
                                        "password": password_input
                                    }
                                    reg_res = requests.post(f"{USER_END_POINT}", json=payload, timeout=5)

                                    if reg_res.status_code == 201:
                                        user_data = reg_res.json()
                                        if not user_data.get("id"):
                                            st.error("Registration failed: user ID missing from backend.")
                                            return

                                        # FIX: Ensure we store the ID returned by the MySQL SELECT fix
                                        st.session_state.current_user = {
                                            "id": user_data.get("id"),
                                            "username": username
                                        }
                                        st.session_state.logged_in = True
                                        # IMPORTANT: Register usually doesn't return a JWT.
                                        # You might need to set st.session_state.token = user_data.get("token")
                                        # if your backend provides one upon registration.

                                        st.success(f"Welcome, {username}!")
                                        # Auto-login after registration (CRITICAL)
                                        login_res = requests.post(
                                            f"{AUTH_END_POINT}/token",
                                            data={"username": username, "password": password_input},
                                            timeout=5
                                        )
                                        if login_res.status_code == 200:
                                            st.session_state.token = login_res.json().get("jwt_token")

                                        st.rerun()
                                    else:
                                        st.error(f"Error: {reg_res.json().get('detail', 'Registration failed')}")
                        except Exception as e:
                            st.error(f"Connection error: {e}")

            if st.button("Log in"):
                st.session_state.auth_mode = "login"
                st.rerun()