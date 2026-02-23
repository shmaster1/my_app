import re
from fastapi import HTTPException
from typing import Dict
from openai import OpenAI
from service import order_service, favorite_item_service, item_service
import json
from repository import order_repository, item_repository
from repository.ecom import chat_repository

MAX_PROMPTS = 5
user_prompt_counter: Dict[int, int] = {}

# Define mapping: keywords -> intent
KEYWORD_INTENT_MAP = {
    "get_items": ["summarize of items","item list", "items list", "list of item", "item", "items", "product", "products", "stock", "inventory"],
    "items_names": ["apple", "apples", "banana", "bananas", "orange", "oranges"],
    "get_user_orders": ["order", "orders", "my orders", "list of orders", "status of order", "historical order", "summarize of orders"],
    "get_favorites": ["favorite", "favorites", "wishlist", "favorite items", "favrite list"],
    "temp_order": ["temp order", "temp", "current order", "open order", "cart"],
    # add more as needed
}


async def chat_with_customer(user_message: str, client: OpenAI, user_id: int) -> str:
    if not user_id:
        raise HTTPException(status_code=401, detail="User not recognized. Please log in again.")

    if user_id not in user_prompt_counter:
        user_prompt_counter[user_id] = 0

    if user_prompt_counter[user_id] >= MAX_PROMPTS:
        raise HTTPException(status_code=429, detail="You have reached the max prompts.")

    # Prompt limit
    count = user_prompt_counter.get(user_id)
    user_prompt_counter[user_id] = count + 1

    user_message_lower = user_message.lower()

    # Step 1: Check keyword map first
    intent = None
    for key, vocabulary_list in KEYWORD_INTENT_MAP.items():
        if any(k in user_message_lower for k in vocabulary_list):
            intent = key
            break

    # Step 2: If no keyword match, ask GPT for general intent
    if not intent:
        system_prompt = f"""
           You are an AI assistant for an e-commerce platform.
           Extract the intent and parameters in JSON.
           Map any user message to the closest intent, ignoring extra words like "the", "a", "my", or punctuation.
           Allowed intents: {list(KEYWORD_INTENT_MAP.keys()) + ['general']}
           Return ONLY JSON.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0
        )

        intent_json = response.choices[0].message.content

        try:
            intent_data = json.loads(intent_json)
            intent = intent_data.get("intent")
        except json.JSONDecodeError:
            return await chat_repository.fetch_data_from_gpt(client, messages)

    # --- Handle intents ---
    if intent == "get_user_orders":
        orders = await order_service.get_all_by_user_id(user_id)
        if not orders:
            return "You have no orders yet."
        return "\n\n".join(
            f"Order status: {o.status.value}, Total: ${o.total_price}, Date: {o.order_date}" for o in orders
        )

    elif intent == "get_favorites":
        favorites = await favorite_item_service.get_favorite_items_by_user_id(user_id)
        if not favorites:
            return "You have no favorites yet."
        return ", ".join(f.item_name for f in favorites)

    elif intent == "get_items":
        items = await item_service.get_items()
        if not items:
            return "Inventory/stock is empty."
        return "\n\n".join(f"{i.item_name}: {i.stock_available} units in stock" for i in items)

    elif intent == "temp_order":
        temp_order_details = await order_repository.get_temp_order_item_details(user_id)
        return f"Temp order total_price: {temp_order_details['total_price']}, Address: {temp_order_details['shipping_address']}"


    elif intent == "items_names":
        item_details_vocabulary = KEYWORD_INTENT_MAP[intent]
        words_from_user = re.findall(r"\b\w+\b", user_message_lower)
        items_names = [w for w in item_details_vocabulary if w in words_from_user]

        if not items_names:
            return "No matching items found."

        details = [await item_repository.get_item_by_name(item) for item in items_names]
        return "\n\n".join(f"{i.item_name} price: $ {i.price}, currently :{i.stock_available} in stock" for i in details)


    # Fallback for any general or unknown intents
    general_messages = [
        {"role": "system", "content": "You are a helpful AI assistant for an e-commerce platform."},
        {"role": "user", "content": user_message}
    ]
    return await chat_repository.fetch_data_from_gpt(client, general_messages)
