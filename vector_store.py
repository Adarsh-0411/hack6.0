import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from urllib.parse import urlparse
import os

class DocumentVectorizer:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.db = chromadb.Client()
        self.store = self.db.create_collection("knowledge_store")
        self.encoder = SentenceTransformer(model_name)
        self.cache = {}

    def index_chunks(self, segments: List[Dict], additional_metadata: List[Dict] = None):
        texts = [s['text'] for s in segments]
        vectors = self.encoder.encode(texts, normalize_embeddings=True).tolist()
        metadata = [{"chunk_id": s['chunk_id']} for s in segments]
        if additional_metadata:
            for i, data in enumerate(additional_metadata):
                metadata[i].update(data)
        ids = [str(i) for i in range(len(segments))]
        self.store.add(documents=texts, embeddings=vectors, metadatas=metadata, ids=ids)

    def find_similar(self, query: str, top_k: int = 5, filters: dict = None) -> List[Dict]:
        cache_key = (query, top_k, frozenset(filters.items()) if filters else None)
        if cache_key in self.cache:
            return self.cache[cache_key]

        query_vector = self.encoder.encode([query], normalize_embeddings=True).tolist()
        result = self.store.query(query_embeddings=query_vector, n_results=top_k, where=filters) if filters else self.store.query(query_embeddings=query_vector, n_results=top_k)

        output = []
        for i in range(len(result['documents'][0])):
            output.append({
                "text": result['documents'][0][i],
                "relevance_score": 1 - result['distances'][0][i],
                "metadata": result['metadatas'][0][i],
                "id": result['ids'][0][i]
            })
        self.cache[cache_key] = output
        return output
