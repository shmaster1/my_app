from openai import OpenAI


async def handle_rag(user_message: str, client: OpenAI, weaviate_client):
    # Step 1: create the vectors from the user input
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=user_message
        )
        user_embedding = response.data[0].embedding
    except Exception:
        return "Unable to process your request right now (embedding error)."

    # Step 2: query Weaviate for similar chunks
    try:
        result = (
            weaviate_client.query
            .get("KnowledgeChunk", ["text", "source"])
            .with_near_vector({"vector": user_embedding})
            .with_limit(3)
            .do()
        )
        chunks = result["data"]["Get"]["KnowledgeChunk"]
        retrieved_texts = [chunk["text"] for chunk in chunks]
    except Exception:
        return "Knowledge base is currently unavailable."

    if not retrieved_texts:
        return "I don't have enough information to answer that."

    context = "\n\n".join(retrieved_texts)  # the raw content before GPT polishes it

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
    except Exception:
        return "AI service is temporarily unavailable. Please try again later."
    return answer