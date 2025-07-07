from uuid import uuid4
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from qdrant_client import QdrantClient
from openai import OpenAI
from .summarize_and_tag import summarize_and_tag
from environs import Env

env = Env()
env.read_env()



def embed_and_store_transcript_fragment(fragment, video_id, video_ulr, block_index):
    """Embeduje pojedynczy fragment, zapisuje do kolekcji przypisanej do video_id"""
    print("start embending")
    start_time = fragment.get("start")
    text = fragment.get("text")
    print("TEXT", text)

    # 1. Klient do embeddingów
    client = OpenAI(
        base_url=env.str("BASE_URL"),
        api_key=env.str("API_KEY"),
    )

    # 2. Streszczenie i tagi
    result = summarize_and_tag(text)
    short = result.get("summary")
    tags = result.get("tags")

    # 3. Embedding
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    embedding = response.data[0].embedding

    # 4. Klient Qdrant
    qdrant = QdrantClient("http://localhost:6333")

    # # 5. Nazwa kolekcji = np. "video__{video_id}"
    # collection_name = f"video__{video_id}"

    # 6. Tworzenie kolekcji (jeśli nie istnieje)
    if "transcript_test2" not in [col.name for col in qdrant.get_collections().collections]:
        qdrant.create_collection(
            collection_name="transcript_test2",
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )

    # 7. Zapis punktu z embeddingiem i metadanymi
    qdrant.upsert(
        collection_name="transcript_test2",
        points=[
            PointStruct(
                id=str(uuid4()),  # unikalne UUID
                vector=embedding,
                payload={
                    "start_time": start_time,
                    "text": text,
                    "summary": short,
                    "tags": tags,
                    "video_id": video_id,
                    "video_url": video_ulr,
                    "block_index": block_index
                }
            )
        ]
    )
