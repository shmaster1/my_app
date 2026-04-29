import weaviate
import weaviate.classes.config as wc
import weaviate.classes.init as wvc
import uuid
from openai import OpenAI
from config.config import Config

config = Config()
openai_client = OpenAI(api_key=config.OPEN_AI_KEY)

client = weaviate.connect_to_local(
    host="127.0.0.1",
    port=8080,
    grpc_port=50051,
    additional_config=wvc.AdditionalConfig(
        timeout=wvc.Timeout(init=30, query=60, insert=120)
    ),
    skip_init_checks=True
)

COLLECTION_NAME = "Item"

items_data = [
    {"id": 1, "name": "Item 1", "price": 10.00, "stock": 3,
     "url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80"},
    {"id": 2, "name": "Item 2", "price": 15.50, "stock": 6,
     "url": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400&q=80"},
    {"id": 3, "name": "Item 3", "price": 8.75, "stock": 2,
     "url": "https://images.unsplash.com/photo-1533055640609-24b498dfd74c?w=400&q=80"},
    {"id": 4, "name": "Item 4", "price": 12.00, "stock": 7,
     "url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&q=80"},
    {"id": 5, "name": "Item 5", "price": 20.00, "stock": 2,
     "url": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400&q=80"},
    {"id": 6, "name": "Item 6", "price": 5.50, "stock": 6,
     "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80"},
    {"id": 7, "name": "Item 7", "price": 18.25, "stock": 4,
     "url": "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=400&q=80"},
    {"id": 8, "name": "Item 8", "price": 22.00, "stock": 6,
     "url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&q=80"},
    {"id": 9, "name": "Item 9", "price": 14.75, "stock": 9,
     "url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80"},
    {"id": 10, "name": "neckless", "price": 9.99, "stock": 1,
     "url": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&q=80"},
]


def setup_and_ingest():
    try:
        if not client.collections.exists(COLLECTION_NAME):
            print(f"📦 Creating collection '{COLLECTION_NAME}'...")
            client.collections.create(
                name=COLLECTION_NAME,
                vectorizer_config=wc.Configure.Vectorizer.none(),
                properties=[
                    wc.Property(name="itemID", data_type=wc.DataType.INT),
                    wc.Property(name="itemName", data_type=wc.DataType.TEXT),
                    wc.Property(name="price", data_type=wc.DataType.NUMBER),
                    wc.Property(name="stockAvailable", data_type=wc.DataType.INT),
                    wc.Property(name="imageUrl", data_type=wc.DataType.TEXT),
                    wc.Property(name="content", data_type=wc.DataType.TEXT),
                ]
            )
            print(f"✅ Collection created.")
        else:
            print(f"ℹ️ Collection '{COLLECTION_NAME}' already exists.")

        collection = client.collections.get(COLLECTION_NAME)

        print(f"🚀 Starting ingestion of {len(items_data)} items...")
        for item in items_data:
            content_text = f"Product: {item['name']}. Price: {item['price']} dollars. Stock: {item['stock']}."

            # יצירת ה-Embedding דרך OpenAI
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=content_text
            )
            vector = response.data[0].embedding

            # הכנסה ל-Weaviate
            collection.data.insert(
                properties={
                    "itemID": item["id"],
                    "itemName": item["name"],
                    "price": float(item["price"]),
                    "stockAvailable": item["stock"],
                    "imageUrl": item["url"],
                    "content": content_text,
                },
                vector=vector,
                uuid=str(uuid.uuid4())
            )
            print(f"🔹 Ingested: {item['name']}")

        print("\n✨ Done! Database is ready.")

    except Exception as e:
        print(f"🔴 An error occurred: {e}")


if __name__ == "__main__":
    try:
        setup_and_ingest()
    finally:
        client.close()
        print("🔌 Connection closed.")