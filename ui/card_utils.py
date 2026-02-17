import requests
import streamlit as st

FAVORITES_ENDPOINT = "http://localhost:8000/favorites"
ORDERS_ENDPOINT = "http://localhost:8000/order/item"
DEFAULT_IMAGE = "https://images.pexels.com/photos/3394655/pexels-photo-3394655.jpeg"


def render_image_grid(items, cols_per_row=3, force_fav=False):
    st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white; border: none; border-radius: 8px;
        transition: all 0.3s ease; font-weight: 600;
        height: 2.5rem; width: 100%;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
        transform: translateY(-1px); color: white;
    }
    .img-wrapper { border-radius: 8px; overflow: hidden; position: relative; height: 180px; margin-bottom: 10px; }
    .img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
    .badge { position: absolute; padding: 2px 8px; background-color: rgba(0,0,0,0.7); color: white; font-size: 11px; border-radius: 4px; bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

    for i in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row, gap="large")
        row_items = items[i: i + cols_per_row]

        for idx, item in enumerate(row_items):
            with cols[idx]:

                item_id = str(item.get("id") or item.get("item_id") or f"fav_{i}_{idx}")
                title = item.get("item_name")
                price = float(item.get("price", 0.0))
                stock_val = int(item.get("stock_available"))
                image_url = str(item.get("image_url") or DEFAULT_IMAGE)

                # --- UNIQUE KEY FOR THIS CARD ---
                key_base = f"{item_id}_{i}_{idx}"

                # --- CARD UI ---
                st.markdown(f"""
                <div style="border-radius: 12px; border: 1px solid #ddd; padding: 0.8rem; text-align: center; background-color: #fff; margin-bottom: 10px;">
                    <div style="font-weight: bold; margin-bottom: 8px;">{title}</div>
                    <div class="img-wrapper">
                        <img src="{image_url}" />
                        <div class="badge" style="left: 8px;">In Stock: {stock_val}</div>
                        <div class="badge" style="right: 8px;">${price:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- Favorite Button ---
                is_fav = True if force_fav else item.get("is_favorite", False)
                fav_label = "★ Unfavorite" if is_fav else "💛 Favorite"

                if st.button(fav_label, key=f"fav_btn_{key_base}", use_container_width=True):
                    current_user = st.session_state.get("current_user")
                    if current_user and current_user.get("id"):
                        user_id = current_user.get("id")
                        url = f"{FAVORITES_ENDPOINT}/user_id/{user_id}?item_id={item_id}"
                        try:
                            if is_fav:
                                response = requests.delete(url, timeout=5)
                                if response.status_code == 200:
                                    st.toast("Removed! 🗑️")
                            else:
                                response = requests.post(url, timeout=5)
                                if response.status_code == 200:
                                    st.toast("Added! ❤️")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Log in to favorite items")

                # --- Quantity + Add to Cart ---
                if st.session_state.get("logged_in"):
                    qty_col, add_col = st.columns([0.45, 0.55])

                    with qty_col:
                        safe_stock = max(1, stock_val)
                        selected_qty = st.selectbox(
                            label=f"Quantity selection for {title}",
                            options=list(range(1, safe_stock + 1)),
                            index=0,
                            key=f"qty_{key_base}",
                            label_visibility="collapsed",
                            format_func=lambda x: f"Qty: {x}"
                        )

                    with add_col:
                        if st.button("Add to Cart", key=f"add_btn_{key_base}", use_container_width=True, type="primary"):
                            token = st.session_state.get("token")
                            payload = {
                                "item_id": item_id,
                                "quantity": selected_qty,
                                "shipping_address": "Default Tel Aviv"
                            }
                            try:
                                response = requests.post(
                                    f"{ORDERS_ENDPOINT}",
                                    json=payload,
                                    headers={"Authorization": f"Bearer {token}"},
                                    timeout=5
                                )

                                if response.status_code in [200, 201]:
                                    st.toast("Added Successfully!", icon="✅")
                                elif response.status_code == 400:
                                    st.error("Out of stock.")
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.caption("Login to buy")
