import os
from openai import OpenAI
import weaviate
from config.config import Config
import uuid


config = Config()
openai_client = OpenAI(api_key=config.OPEN_AI_KEY)
weaviate_client = weaviate.Client(url=config.WEAVIATE_BASE_URL, startup_period=5, timeout_config=(5, 60))

# -------------------------------
# 2️⃣ Ensure schema exists
# -------------------------------
class_obj = {
    "class": "KnowledgeChunk",
    "vectorizer": "none",  # we provide vectors manually
    "properties": [
        {"name": "text", "dataType": ["text"]},
        {"name": "source", "dataType": ["string"]}
    ]
}

existing_classes = [c["class"] for c in weaviate_client.schema.get().get("classes", [])]


def chunk_text(text, chunk_size=300):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

kb_dir = "./knowledge_base"
total_ingested = 0

for filename in os.listdir(kb_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(kb_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = chunk_text(content, chunk_size=300)

        for chunk in chunks:
            # Get embedding from OpenAI Convert text → vector (list of floats). This is the semantic representation
            embedding = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            ).data[0].embedding

            # Store in Weaviate
            weaviate_client.data_object.create(
                data_object={
                    "text": chunk,
                    "source": filename
                },
                class_name="KnowledgeChunk",
                vector=embedding,
                uuid=str(uuid.uuid4())
            )

            total_ingested += 1

