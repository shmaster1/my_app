import time
import jwt
import requests
import streamlit as st
from login import show_login_page

CHAT_END_POINT = "http://localhost:8000/ragchat"

def side_bar_panel():
    st.markdown("""
        <style>
        /* 1. Force the navigation list to be fully visible (removes the arrow/collapsing) */
        [data-testid="stSidebarNav"] ul {
            max-height: none !important;
            display: block !important;
        }

        /* Hide the collapse arrow icon */
        [data-testid="stSidebarNav"] svg[class^="st-"] {
            display: none !important;
        }

        /* 2. Target the Logout tab (last item) */
        /* Idle state: Same as other tabs */
        [data-testid="stSidebarNav"] ul li:last-child a {
            background-color: transparent !important;
            margin-top: 0px; /* Slight gap to separate from Settings */
            transition: background-color 0.3s ease;
        }

        /* Hover state: Red background, white text */
        [data-testid="stSidebarNav"] ul li:last-child a:hover {
            background-color: #ff4b4b !important;
        }

        [data-testid="stSidebarNav"] ul li:last-child a:hover span {
            color: white !important;
        }

        /* 3. Style for the Chat Assistant button */
        div[data-testid="stSidebar"] .chat-wrapper button {
            background-color: #2e7bcf !important;
            color: white !important;
            font-weight: bold !important;
            margin-top: 15px;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Chat Assistant Logic ---

    # --- Initialize session state variables ---§x
    current_user = st.session_state.get("current_user", {})
    if not current_user.get("id"):
        # Force a unique session-based guest id for truly anonymous sessions
        if "guest_id" not in st.session_state:
            st.session_state["guest_id"] = str(int(time.time() * 1000))
        user_id = st.session_state["guest_id"]
    else:
        user_id = current_user["id"]

    chat_open_key = f"chat_open_{user_id}"
    chat_locked_key = f"chat_locked_{user_id}"
    chat_history_key = f"chat_history_{user_id}"
    chat_counter_key = f"chat_counter_{user_id}"

    # Initialize user-specific session state
    if chat_open_key not in st.session_state:
        st.session_state[chat_open_key] = False

    if chat_locked_key not in st.session_state:
        st.session_state[chat_locked_key] = False

    if chat_history_key not in st.session_state:
        st.session_state[chat_history_key] = []

    if chat_counter_key not in st.session_state:
        st.session_state[chat_counter_key] = 0

    with st.sidebar:

        # Toggle button
        if st.button("💬 Chat Assistant", key="chat_toggle_btn", use_container_width=True):
            st.session_state[chat_open_key] = not st.session_state[chat_open_key]

        # Chat window
        if st.session_state[chat_open_key]:

            with st.container(border=True):

                def handle_chat(user_text):

                    if not user_text or st.session_state[chat_locked_key]:
                        return

                    st.session_state[chat_history_key].append({
                        "role": "user",
                        "content": user_text
                    })

                    try:

                        user_details =  {
                                        "user_id" : user_id,
                                        "user_text": user_text
                        }

                        response = requests.post(
                            f"{CHAT_END_POINT}",
                            json=user_details,
                            timeout=15
                        )

                        if response.status_code == 200:
                            ai_response = response.text.replace("\\n", "\n") # replace the escaped, so it'll drop line

                            # Append assistant response
                            st.session_state[chat_history_key].append({
                                "role": "assistant",
                                "content": ai_response
                            })

                            # Keep only last 5 exchanges (10 messages total) for UI display
                            if len(st.session_state[chat_history_key]) > 10:
                                st.session_state[chat_history_key] = st.session_state[chat_history_key][-10:]

                        elif response.status_code == 429:
                            try:
                                data = response.json()
                                # Check if this is OpenAI API error
                                if data.get("error", {}).get("type") == "insufficient_quota":
                                    st.warning("⚠️ OpenAI API quota exceeded. Please check your plan or try later.")
                                else:
                                    st.warning("⚠️ You have reached the max prompts.")
                            except ValueError:
                                st.warning("⚠️ 429 error occurred.")
                            st.session_state[chat_locked_key] = True


                        else:
                            try:
                                data = response.json()
                                error_msg = data.get("detail") or f"Error: {response.status_code}"
                            except ValueError:  # JSON decode failed
                                error_msg = f"Error: {response.status_code} (no JSON body returned)"

                            st.session_state[chat_history_key].append({
                                "role": "assistant",
                                "content": error_msg
                            })


                    except Exception as e:
                        st.session_state[chat_history_key].append({
                            "role": "assistant",
                            "content": f"Connection failed: {e}"
                        })

                # -------------------------
                # Display chat history
                # -------------------------
                for message in st.session_state[chat_history_key]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # -------------------------
                # Chat input (GPT-style)
                # -------------------------
                if not st.session_state[chat_locked_key]:
                    user_input = st.chat_input("Type your message...")
                    if user_input:
                        handle_chat(user_input)
                        st.rerun()
                # else:
                #     st.warning("Chat is locked. Prompt limit reached.")


def check_auth():
    """
    The Universal Gatekeeper.
    If not logged in, it shows the login page and stops the script.
    """
    is_logged_in = st.session_state.get("logged_in", False)
    token = st.session_state.get("token")

    if not is_logged_in:
        show_login_page()
        st.stop()  # Critical: Stops Favorites/Orders from executing further

    # --- Token Expiration Guard ---
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        expire_time = decoded_token.get("exp")

        if expire_time and time.time() > expire_time:
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.current_user = None
            # Show login page with error
            st.error("Your session expired. Please log in again. ❌")
            show_login_page()
            st.stop()

    except Exception:
        st.session_state.logged_in = False
        st.session_state.token = None
        show_login_page()
        st.stop()