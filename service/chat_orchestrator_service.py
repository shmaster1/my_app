import json
from openai import OpenAI
from repository import order_repository
from service import rag_service, favorite_item_service, item_service, order_service


async def chat_with_customer(user_message: str, client: OpenAI, weaviate_client, user_id: int):

    # 1️⃣ Detect intent using AI
    intent = await detect_intent(user_message, client)

    if intent == "db_orders":
        orders = await order_service.get_all_by_user_id(user_id)
        if not orders:
            return {"response": "You have no orders yet."}
        return str("\n\n".join(f"Order status: {o.status.value}, Total: ${o.total_price}" for o in orders))

    elif intent == "db_favorites":
        favorites = await favorite_item_service.get_favorite_items_by_user_id(user_id)
        if not favorites:
            return {"response": "You have no favorites yet."}
        return str(", ".join(f.item_name for f in favorites))

    elif intent == "db_items":
        items = await item_service.get_items()
        if not items:
            return {"response": "Inventory is empty."}
        return str("\n\n".join(f"{i.item_name}: {i.stock_available} units in stock" for i in items))

    elif intent == "db_cart":
        temp_order = await order_repository.get_temp_order_item_details(user_id)
        return {f"Cart total: ${temp_order['total_price']}"}

    elif intent == "knowledge_base":
        return await rag_service.handle_rag(user_message, client, weaviate_client)

    # 3️⃣ Fallback — General GPT
    general_messages = [
        {"role": "system", "content": "You are a helpful AI assistant for an e-commerce platform."},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=general_messages, temperature=0.7)
    return response.choices[0].message.content


async def detect_intent(user_message: str, client: OpenAI) -> str:
    system_prompt = """
    You are an AI intent classifier for an e-commerce backend.

    Classify the user request into ONE of these intents:
    - db_orders
    - db_favorites
    - db_items
    - db_cart
    - knowledge_base
    - general

    Rules:
    - If the question requires live user data (orders, favorites, cart) → db_*
    - If it asks about stock/inventory → db_items
    - If it asks about policies, explanations, documentation → knowledge_base
    - If unrelated to platform data → general

    Return ONLY valid JSON:
    {"intent": "<intent_name>"}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=0)

    try:
        intent_json = response.choices[0].message.content
        intent_data = json.loads(intent_json)
        return intent_data.get("intent", "general")
    except Exception:
        return "general"