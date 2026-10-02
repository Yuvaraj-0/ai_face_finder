from core.qdrant import client

COLLECTION_NAME = "faces"

print("=" * 60)
print("QDRANT DATA")
print("=" * 60)

result = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=20,
    with_payload=True,
    with_vectors=False,
)

points, next_page = result

print("Number of points returned:", len(points))

for point in points:
    print("--------------------------------")
    print("Point ID:", point.id)
    print("Payload:", point.payload)

print("=" * 60)