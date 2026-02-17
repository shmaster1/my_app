from typing import List
from openai import OpenAI


async def fetch_data_from_gpt(client: OpenAI, messages_buffer: List[dict]) -> str:
    """
    Sends the messages buffer to GPT and returns assistant response.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages_buffer,
        max_tokens=300,
        temperature=0.5
    )

    assistant_reply = response.choices[0].message.content

    # Append GPT reply to the buffer for context
    messages_buffer.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply
