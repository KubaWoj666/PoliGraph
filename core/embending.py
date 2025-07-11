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
    results = summarize_and_tag(text)
    short = results.get("summary")
    tags = results.get("tags")

    # 3. Embedding
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-large"
    )
    embedding = response.data[0].embedding

    # 4. Klient Qdrant
    qdrant = QdrantClient(env.str("QDRANT_URL"))

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


def embed_user_query(query):
    client = OpenAI(
        base_url=env.str("BASE_URL"),
        api_key=env.str("API_KEY"),
    )

    results = summarize_and_tag(query)
    tags = results.get("tags")

    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-large"
    )
    embedding = response.data[0].embedding

    qdrant = QdrantClient(env.str("QDRANT_URL"))

    filter_query = {
    "should": [
        {
            "key": "tags",
            "match": {"value": tag}
        } for tag in tags
        ]
    } if tags else None

    # Szukamy w bazie Qdrant
    results = qdrant.search(
        collection_name="transcript_test2",
        query_vector=embedding,
        limit=10,
        score_threshold=0.45,
        with_payload=True,
        query_filter=filter_query  # ważne: query_filter zamiast filter
    )

    for point in results:
        
        print(f"Score: {point.score:.4f} | ID: {point.id}")
        print(f"Text: {point.payload.get('text')[:150]}...")
        print()
        print(f"ID: {point.id}")
        print(f"Dopasowanie (score): {point.score:.3f}")
        print(f"Start time: {point.payload.get('start_time')}")
        print(f"Tekst: {point.payload.get('text')}")
        print(f"Streszczenie: {point.payload.get('summary')}")
        print(f"Tagi: {point.payload.get('tags')}")
        print(f"Źródło wideo: {point.payload.get('video_url')}")
        print("-" * 50)
