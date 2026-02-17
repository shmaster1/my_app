import requests
import streamlit as st
import pandas as pd
from sidebar_utils import side_bar_panel, check_auth

# Settings
st.set_page_config(layout="wide", page_title="My Orders")

# --- SECURITY GUARD ---
check_auth()
side_bar_panel()


##################################################################################################################
################################################## IMPORTRANT!!! ################################################
##################################################################################################################
# TODO: ADD EVENT WHEN USER NAVIGATES HERE TO TRIGGER VALIDATE STOCK IN BE (IT SHOULD CHECK CURR STOCK VS EXIST ITEMS AND WARN RESPECTIVELY)



if "last_action" in st.session_state:
    st.toast(st.session_state.last_action)
    del st.session_state.last_action # Clear it so it doesn't show again


ORDERS_ENDPOINT = "http://localhost:8000/order"
token = st.session_state.get("token")
current_user = st.session_state.get("current_user")
user_id = current_user["id"] if current_user else None
if not user_id:
    st.error("User ID missing. Please log out and log in again.")
    st.stop()


# -----------------------------
# 1. Unified Data Fetching
# -----------------------------
def fetch_order_data(user_id):
    """Fetches the unified list (TEMP + CLOSED) from the backend."""
    try:
        # Using the Authorization header for GET as well, as backends often require it
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{ORDERS_ENDPOINT}/user_id/{user_id}", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Connection error: {e}")
        return []


def format_orders_to_df(orders_list):
    """Flattens a list of order objects into a displayable DataFrame."""
    rows = []
    for order in orders_list:
        order_items = order.get("order_items") or order.get("items", [])
        for item in order_items:
            rows.append({
                "Order ID": order.get("id") or order.get("order_id"),
                "Product": item.get("item_name") or item.get("title"),
                "Price": f"${item.get('price', 0.0):.2f}",
                "Qty": item.get("quantity", 0),
                "Subtotal": f"${(item.get('price', 0.0) * item.get('quantity', 0)):.2f}",
                "Date": order.get("order_date")
            })
    return pd.DataFrame(rows)


# -----------------------------
# 2. UI Header & Sidebar
# -----------------------------
st.markdown("<h1 style='text-align: center; color: #007BFF;'>🛍️ My Orders</h1>", unsafe_allow_html=True)

# Fetch all data once
all_orders = fetch_order_data(user_id)

# --- SHOW SUCCESS AFTER PURCHASE ---
if st.session_state.get("purchase_success"):
    st.toast("Purchase successful! 🎉", icon="✅")
    st.balloons()
    del st.session_state["purchase_success"]

# -----------------------------
# 3. Temp Order Section (Active Cart)
# -----------------------------
st.markdown("### 📥 Temp Order")

# Find the order with status 'TEMP'
temp_order = next((o for o in all_orders if o.get("status") == "TEMP"), None)

if temp_order and (temp_order.get("items") or temp_order.get("order_items")):
    # Support both key names just in case
    cart_items = temp_order.get("order_items") or temp_order.get("items", [])
    order_id = temp_order.get("id") or temp_order.get("order_id")

    # --- TABLE HEADERS ---
    h1, h2, h3, h4, h5 = st.columns([3, 1, 1, 1, 0.5])
    h1.write("**Product**")
    h2.write("**Qty**")
    h3.write("**Price**")
    h4.write("**Total**")
    h5.write("")  # Trash bin column
    st.divider()

    # --- TABLE ROWS ---
    for idx, item in enumerate(cart_items):
        item_id = item.get("item_id")

        r1, r2, r3, r4, r5 = st.columns([3, 1, 1, 1, 0.5])

        r1.write(item.get("item_name"))
        r2.write(str(item.get("quantity")))
        r3.write(f"${item.get('price'):.2f}")
        r4.write(f"${(item.get('price', 0.0) * item.get('quantity', 0)):.2f}")

        # REMOVE ITEM BUTTON
        if r5.button("🗑️", key=f"del_{item_id}_{idx}"):
            try:
                url = f"{ORDERS_ENDPOINT}/item/{item_id}"
                res = requests.delete(url, headers={"Authorization": f"Bearer {token}"})

                if res.status_code == 200:
                    st.session_state.last_action = "❌ Item removed!"
                    st.rerun()
                else:
                    st.error(f"Delete failed: {res.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- STOCK CHECK BEFORE BUY NOW ---
    if any(item.get("stock_available") == 0 for item in cart_items):
        st.warning("⚠️ Some items are out of stock. Please adjust your cart.")
        buy_now_disabled = True
    else:
        buy_now_disabled = False

    st.divider()

    # --- FOOTER & PURCHASE ---
    c1, c2 = st.columns([1, 1])
    with c1:
        st.metric("Total Bill", f"${temp_order.get('total_price', 0.0):.2f}")

    with c2:
        st.write("")
        if st.button("Buy Now", type="primary", use_container_width=True, disabled=buy_now_disabled):
            shipping_addr = current_user.get("address") or "tlv"

            try:
                res = requests.post(
                    f"{ORDERS_ENDPOINT}/purchase_order",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"shipping_address": shipping_addr}
                )

                if res.ok:
                    st.session_state["purchase_success"] = True
                    st.rerun()
                else:
                    try:
                        error_msg = res.json().get("detail", "Purchase failed.")
                    except:
                        error_msg = f"Purchase failed ({res.status_code})"

                    st.error(error_msg)

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

    st.info("Your Temp Order is empty. Go to the home page to add items!")

# -----------------------------
# 4. Historical Orders Section (Past Purchases)
# -----------------------------
st.divider()
st.markdown("### 📜 Past Purchases")

# Filter only 'CLOSED' orders
historical_orders = [o for o in all_orders if str(o.get("status", "")).upper() == "CLOSED"]

if historical_orders:
    df_history = format_orders_to_df(historical_orders)
    st.dataframe(df_history, use_container_width=True, hide_index=True)
else:
    st.write("No past purchases found in your account history.")