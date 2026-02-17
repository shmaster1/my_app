import time
import streamlit as st
import requests
from sidebar_utils import side_bar_panel, check_auth
from card_utils import render_image_grid

# -----------------------------
# 1. Page Config & API Config
# -----------------------------
ITEM_END_POINT = "http://localhost:8000/item"

st.set_page_config(layout="wide", page_title="My Store")

# -----------------------------
# 2. Session State Init
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "last_search_time" not in st.session_state:
    st.session_state.last_search_time = 0.0

if "last_items" not in st.session_state:
    st.session_state.last_items = []

# -----------------------------
# 3. Auth Guard
# -----------------------------
check_auth()       # Stops the page if not logged in
# -----------------------------
# 4. Main App Content
# -----------------------------
side_bar_panel()

user = st.session_state.current_user
welcome_name = user.get("username") if isinstance(user, dict) else user

st.markdown(
    f"<h1 style='text-align:center;'>🛍️ Welcome, {welcome_name}</h1>",
    unsafe_allow_html=True
)

# -----------------------------
# 5. Search Bar
# -----------------------------
search_query = st.text_input(
    "Search Store",
    placeholder="🔍 Search items...",
    label_visibility="collapsed",
    key="store_search"
)

# -----------------------------
# 6. Fetch Items (with throttle)
# -----------------------------
try:
    now = time.time()
    res = None

    # --- Search mode (throttled) ---
    if search_query and (now - st.session_state.last_search_time > 0.5):
        st.session_state.last_search_time = now

        res = requests.get(
            f"{ITEM_END_POINT}/search",
            params={"name": search_query},
            timeout=5
        )

    # --- Default mode ---
    elif not search_query:
        user_id = (
            st.session_state.current_user.get("id")
            if isinstance(st.session_state.current_user, dict)
            else None
        )

        params = {"user_id": user_id} if user_id else {}
        res = requests.get(
            f"{ITEM_END_POINT}/",
            params=params,
            timeout=5
        )

    # --- Handle response ---
    if res and res.status_code == 200:
        items = res.json()
        st.session_state.last_items = items
    else:
        items = st.session_state.last_items

except Exception as e:
    st.error(f"Backend connection error: {e}")
    items = st.session_state.last_items

# -----------------------------
# 7. Normalize data
# -----------------------------
for item in items:
    item["is_favorite"] = item.get("is_favorite", False)

# -----------------------------
# 8. Render UI
# -----------------------------
render_image_grid(items, cols_per_row=3)
