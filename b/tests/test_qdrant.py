
from uuid import uuid4

from core.qdrant import client
from qdrant_client.models import PointStruct


print("Testing Qdrant connection...")

# Check collection
collection = client.get_collection("faces")

print("Collection:", collection)
print("Points:", collection.points_count)


# Test vector
vector = [0.0] * 512

point = PointStruct(
    id=str(uuid4()),
    vector=vector,
    payload={
        "image_id": "test-image",
        "event_id": "test-event",
        "photographer_id": "test-photographer",
    },
)

print("Uploading test point...")

client.upsert(
    collection_name="faces",
    points=[point],
    wait=True,
)

print("SUCCESS: Test vector uploaded to Qdrant")

