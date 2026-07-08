from qdrant_client.models import PayloadSchemaType
from uuid import uuid4
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client.models import (
    PointStruct,
    Distance,
    VectorParams,
)
from core.qdrant import client

COLLECTION_NAME = "faces"


class QdrantService:
    print(client.get_collections())

    
    from qdrant_client.models import (
    PointStruct,
    Distance,
    VectorParams,
    PayloadSchemaType,
)

    @staticmethod
    def create_collection():

        if not client.collection_exists(COLLECTION_NAME):

            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=512,
                    distance=Distance.COSINE
                )
            )

            print("✅ Qdrant collection created")

        else:
            print("✅ Qdrant collection already exists")

        # Always ensure the payload index exists
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
        embedding: list[float]
    ):

        point = PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload={
                "image_id": image_id,
                "event_id": event_id,
                "photographer_id": photographer_id
            }
        )

        client.upsert(
            collection_name=COLLECTION_NAME,
            wait=True,
            points=[point]
        )

        print("✅ Embedding saved to Qdrant")

    def search(self, embedding, event_id):


                return client.query_points(
                    collection_name="faces",
                    query=embedding,
                    limit=20,
                    query_filter=Filter(
                        must=[
                            FieldCondition(
                                key="event_id",
                                match=MatchValue(value=event_id)
                            )
                        ]
                    )
                )
qdrant_service = QdrantService()