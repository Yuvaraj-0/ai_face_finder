from uuid import uuid4

from qdrant_client.models import (
    PointStruct,
    Distance,
    VectorParams,
    PayloadSchemaType,
    Filter,
    FieldCondition,
    MatchValue,
)

from core.qdrant import client


COLLECTION_NAME = "faces"


class QdrantService:

    @staticmethod
    def create_collection():

        if not client.collection_exists(COLLECTION_NAME):

            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=512,
                    distance=Distance.COSINE,
                ),
            )

            print("✅ Qdrant collection created")

        else:
            print("✅ Qdrant collection already exists")

        # Ensure event_id payload index exists
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="event_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        print("✅ event_id payload index created")

    @staticmethod
    def save_embedding(
        image_id: str,
        event_id: str,
        photographer_id: str,
        embedding: list[float],
    ):

        point = PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload={
                "image_id": image_id,
                "event_id": event_id,
                "photographer_id": photographer_id,
            },
        )

        client.upsert(
            collection_name=COLLECTION_NAME,
            wait=True,
            points=[point],
        )

        print("✅ Embedding saved to Qdrant")

    @staticmethod
    def search(embedding, event_id):

        print("=" * 60)
        print("QDRANT SEARCH DEBUG")
        print("Collection:", COLLECTION_NAME)
        print("Event ID:", event_id)
        print("Embedding length:", len(embedding))

        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            limit=20,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="event_id",
                        match=MatchValue(value=event_id)
                    )
                ]
            ),
        )

        print("Qdrant points returned:", len(results.points))

        for point in results.points:
            print("--------------------------------")
            print("Point ID:", point.id)
            print("Image ID:", point.payload.get("image_id"))
            print("Event ID:", point.payload.get("event_id"))
            print("Photographer ID:", point.payload.get("photographer_id"))
            print("Score:", point.score)

        print("=" * 60)

        return results

qdrant_service = QdrantService()