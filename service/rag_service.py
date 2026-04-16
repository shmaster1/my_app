from openai import OpenAI


async def handle_rag(user_message: str, client: OpenAI, weaviate_client):
    # Step 1: embed the user query
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=user_message
        )
        user_embedding = response.data[0].embedding
    except Exception as e:
        print(f"[RAG] Embedding error: {e}")
        return "Unable to process your request right now (embedding error)."

    # Step 2: query Weaviate for similar chunks
    try:
        collection = weaviate_client.collections.get("KnowledgeChunk")
        result = collection.query.near_vector(
            near_vector=user_embedding,
            limit=3,
            return_properties=["text", "source"]
        )
        retrieved_texts = [obj.properties["text"] for obj in result.objects]
    except Exception as e:
        print(f"[RAG] Weaviate query error: {e}")
        return "Knowledge base is currently unavailable."

    if not retrieved_texts:
        return "I don't have enough information to answer that."

    context = "\n\n".join(retrieved_texts)

    prompt_to_gpt = f"""
    You are an AI assistant.

    Use ONLY the information provided in the context below.
    If the answer cannot be found in the context, say "I don't know."

    CONTEXT: {context}
    USER QUESTION: {user_message}
    """

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt_to_gpt}
    ]

    # Step 3: call GPT
    try:
        gpt_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0
        )
        answer = gpt_response.choices[0].message.content
    except Exception as e:
        print(f"[RAG] GPT error: {e}")
        return "AI service is temporarily unavailable. Please try again later."

    return answer


async def get_semantic_recommendations(user_query: str, weaviate_client):
    try:
        products = weaviate_client.collections.get("Item")

        response = products.query.near_text(
            query=user_query,
            limit=3,
            return_properties=["itemName", "price", "itemID", "content"]
        )

        results = []
        for obj in response.objects:
            results.append({
                "id": obj.properties["itemID"],
                "name": obj.properties["itemName"],
                "price": obj.properties["price"],
                "description": obj.properties["content"]
            })

        return results

    except Exception as e:
        print(f"[Weaviate] Semantic search error: {e}")
        return []
