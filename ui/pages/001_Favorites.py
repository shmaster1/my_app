import streamlit as st
import requests
from sidebar_utils import side_bar_panel, check_auth
from card_utils import render_image_grid

FAVORITES_ENDPOINT = "http://localhost:8000/favorites"

st.set_page_config(layout="wide", page_title="My Favorites")

# --- 1. SECURITY GUARD ---
check_auth()

# --- 2. SIDEBAR ---
side_bar_panel()

st.markdown(
    "<h1 style='text-align: center;'>💖 Your Favorites</h1>",
    unsafe_allow_html=True
)

# --- 3. FETCH FAVORITES ---
items = []
user = st.session_state.get("current_user")

if isinstance(user, dict) and user.get("id"):
    user_id = user["id"]

    try:
        response = requests.get(
            f"{FAVORITES_ENDPOINT}/user_id/{user_id}",
            timeout=5
        )

        if response.status_code == 200:
            raw_favorites = response.json()

            if isinstance(raw_favorites, list):
                # ✅ Ensure SAME structure as main shop page
                items = [
                    {
                        "id": fav["item_id"],
                        "item_name": fav["item_name"],
                        "price": float(fav["price"]),
                        "stock_available": int(fav["stock_available"]),
                        "image_url": fav.get("image_url")
                    }
                    for fav in raw_favorites
                ]
            else:
                st.warning("Unexpected favorites data format.")

        elif response.status_code == 404:
            # No favorites yet
            items = []

        else:
            st.error(f"Error {response.status_code}: Could not retrieve favorites.")

    except requests.exceptions.RequestException as e:
        st.error(f"Connection failed: {e}")

else:
    st.error("User profile is incomplete (ID missing). Please logout and log in again.")
    st.stop()

# --- 4. RENDER ---
if not items:
    st.info("You haven't favorited anything yet! Browse the shop to add items.")
else:
    # force_fav=True keeps hearts red and layout identical to main
    render_image_grid(items, force_fav=True)
