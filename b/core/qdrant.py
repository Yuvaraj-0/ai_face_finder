from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

try:
    collections = client.get_collections()
    print("✅ Connected to Qdrant successfully!")
    print(collections)
except Exception as e:
    print("❌ Failed to connect to Qdrant")
    print(e)