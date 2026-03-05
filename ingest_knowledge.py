import os
from openai import OpenAI
import weaviate
from config.config import Config
import uuid

config = Config()
openai_client = OpenAI(api_key=config.OPEN_AI_KEY)

# 1️⃣ SAFE INITIALIZATION
try:
    weaviate_client = weaviate.Client(
        url=config.WEAVIATE_BASE_URL,
        startup_period=2,
        timeout_config=(5, 60)
    )
    # Check if we can actually reach the schema
    schema = weaviate_client.schema.get()
    print("✅ Weaviate reachable. Starting ingestion check...")
except Exception as e:
    print(f"⚠️ Weaviate connection failed: {e}. Ingestion skipped.")
    weaviate_client = None


if weaviate_client:
    class_obj = {
        "class": "KnowledgeChunk",
        "vectorizer": "none",
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "source", "dataType": ["string"]}
        ]
    }

    # Only create class if it doesn't exist
    existing_classes = [c["class"] for c in schema.get("classes", [])]
    if "KnowledgeChunk" not in existing_classes:
        weaviate_client.schema.create_class(class_obj)


    def chunk_text(text, chunk_size=300):
        words = text.split()
        return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


    kb_dir = "./knowledge_base"

    # Ensure directory exists before looping
    if os.path.exists(kb_dir):
        total_ingested = 0
        for filename in os.listdir(kb_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(kb_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                chunks = chunk_text(content, chunk_size=300)

                for chunk in chunks:
                    embedding = openai_client.embeddings.create(
                        model="text-embedding-3-small",
                        input=chunk
                    ).data[0].embedding

                    weaviate_client.data_object.create(
                        data_object={"text": chunk, "source": filename},
                        class_name="KnowledgeChunk",
                        vector=embedding,
                        uuid=str(uuid.uuid4())
                    )
                    total_ingested += 1
else:
    print("🛑 App starting without Weaviate features.")