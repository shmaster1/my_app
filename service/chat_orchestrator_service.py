import json
import openai
from openai import OpenAI
from repository import order_repository
from service import rag_service, favorite_item_service, item_service, order_service


async def chat_with_customer(user_message: str, client: OpenAI, weaviate_client, user_id: int, fallback_client: OpenAI = None, history: list = None):

    history = history or []

    # 1️⃣ Detect intent using AI
    intent = await detect_intent(user_message, client, fallback_client, history)

    if intent == "db_orders":
        orders = await order_service.get_all_by_user_id(user_id)
        if not orders:
            return {"response": "You have no orders yet."}
        return {"response": "\n\n".join(f"Order status: {o.status.value}, Total: ${o.total_price}" for o in orders)}

    elif intent == "db_favorites":
        favorites = await favorite_item_service.get_favorite_items_by_user_id(user_id)
        if not favorites:
            return {"response": "You have no favorites yet."}
        return {"response": ", ".join(f.item_name for f in favorites)}

    elif intent == "db_items":
        items = await item_service.get_items()
        if not items:
            return {"response": "Inventory is empty."}
        return {"response": "\n\n".join(f"{i.item_name}: {i.stock_available} units in stock" for i in items)}

    elif intent == "db_cart":
        temp_order = await order_repository.get_temp_order_item_details(user_id)
        return {"response": f"Cart total: ${temp_order['total_price']}"}

    elif intent == "knowledge_base":
        answer = await rag_service.handle_rag(user_message, client, weaviate_client)
        return {"response": answer}

    elif intent == "quota_exceeded":
        return {"response": "I'm currently unavailable due to high demand or exceeded the max quota!"}

    elif intent == "service_unavailable":
        return {"response": "I'm temporarily unavailable. Please try again in a moment."}

    elif intent == "product_search":
        price_sort = rag_service.detect_price_sort(user_message)

        if price_sort:
            items = await item_service.get_items()
            if not items:
                return {"response": "No items are currently available."}
            sorted_items = sorted(items, key=lambda i: i.price, reverse=(price_sort == "desc"))
            filtered_items = sorted_items[:3]
            answer = "Here are the most affordable items:" if price_sort == "asc" else "Here are the most expensive items:"
        else:
            search_query = await resolve_search_query(user_message, history, client, fallback_client)
            recommended_items = await rag_service.get_semantic_recommendations(search_query, weaviate_client, client)
            if not recommended_items:
                return {"response": "I couldn't find any items matching that description. Anything else?"}
            filtered_items = await item_service.filter_items_by_id(recommended_items)
            answer = "I found some items that match your request:"

        return {"answer": answer, "type": "product_recommendation", "products": filtered_items}

    # Fallback — General GPT
    general_messages = [
        {"role": "system", "content": "You are a helpful AI assistant for an e-commerce platform."},
        *history[-10:],
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=general_messages, temperature=0.7)
        return {"response": response.choices[0].message.content}
    except openai.RateLimitError:
        if fallback_client:
            response = fallback_client.chat.completions.create(model="llama-3.1-8b-instant", messages=general_messages, temperature=0.7)
            return {"response": response.choices[0].message.content}
        return {"response": "I'm currently unavailable due to high demand or exceeded the max quota!"}


async def detect_intent(user_message: str, client: OpenAI, fallback_client: OpenAI = None, history: list = None) -> str:
    system_prompt = """
        You are an AI intent classifier for a luxury e-commerce store.
        Classify the user's message into exactly one of these categories:

        - db_orders: Questions about order status, tracking, or history.
        - db_favorites: Questions about the user's saved or favorite items.
        - db_items: Requests to list all available products or inventory.
        - db_cart: Viewing, adding to, or removing items from the shopping cart.
        - product_search: Requests for recommendations, gift ideas, or questions about item qualities
          (e.g., "Show me precious items," "I need an elegant gift," "What is the most expensive thing you have?").
        - knowledge_base: Store policies, shipping info, or "About Us" info.
        - general: Greetings, small talk, or unrelated questions.
        
        Return ONLY a JSON object: {"intent": "category_name"}
    """

    history = history or []
    messages = [
        {"role": "system", "content": system_prompt},
        *history[-6:],
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
        intent_json = response.choices[0].message.content
        intent_data = json.loads(intent_json)
        return intent_data.get("intent", "general")
    except openai.RateLimitError:
        if fallback_client:
            try:
                response = fallback_client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0)
                intent_json = response.choices[0].message.content
                intent_data = json.loads(intent_json)
                return intent_data.get("intent", "general")
            except Exception:
                return "general"
        return "quota_exceeded"
    except (openai.APIConnectionError, openai.APITimeoutError):
        return "service_unavailable"
    except json.JSONDecodeError:
        return "general"
    except Exception:
        return "general"


async def resolve_search_query(user_message: str, history: list, client: OpenAI, fallback_client: OpenAI = None) -> str:
    if not history:
        return user_message

    system_prompt = (
        "You are a search query assistant. Given a conversation history and the user's latest message, "
        "rewrite the latest message into a single standalone product search query. "
        "Return only the search query string, nothing else."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        *history[-6:],
        {"role": "user", "content": user_message}
    ]

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
        return response.choices[0].message.content.strip() or user_message
    except openai.RateLimitError:
        if fallback_client:
            try:
                response = fallback_client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, temperature=0)
                return response.choices[0].message.content.strip() or user_message
            except Exception:
                return user_message
        return user_message
    except Exception:
        return user_message