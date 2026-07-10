import os
import json
import time
import math
from typing import List, Dict, Any, Optional
import logging
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from app.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "user_memories"


class MemoryManager:
    """Manages the Identity Core (permanent facts) and Temporal RAG (Qdrant)."""

    def __init__(self):
        # Load embedding model locally
        logger.info("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformer: {e}")
            self.model = None

        # Load Qdrant Client
        logger.info(f"Connecting to Qdrant at {settings.QDRANT_URL}...")
        try:
            self.qdrant = QdrantClient(
                url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
            )
            # Create collection if it doesn't exist
            if self.model:
                self._init_collection()
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            self.qdrant = None

        # Load Identity Core
        self.identity_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "identity_core.json",
        )
        self.identity_data = self._load_identity_core()

    def _load_identity_core(self) -> Dict[str, Any]:
        """Loads factual profile from identity_core.json."""
        if os.path.exists(self.identity_path):
            try:
                with open(self.identity_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading identity_core.json: {e}")
        return {}

    def _init_collection(self):
        """Initializes Qdrant collection if not already existing."""
        if not self.qdrant:
            return
        try:
            collections = self.qdrant.get_collections().collections
            collection_names = [c.name for c in collections]
            if COLLECTION_NAME not in collection_names:
                logger.info(f"Creating Qdrant collection '{COLLECTION_NAME}'...")
                self.qdrant.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {e}")

    def get_identity_fact(self, query: str) -> Optional[str]:
        """Looks up a fact in Identity Core. Matches keys or facts list."""
        if not self.identity_data:
            return None

        query_lower = query.lower()
        # Direct key lookup
        for key, val in self.identity_data.items():
            if key.lower() in query_lower and isinstance(val, str) and val:
                return f"{key}: {val}"

        # Sub-facts dict lookup
        facts = self.identity_data.get("facts", {})
        for key, val in facts.items():
            if key.lower() in query_lower and val:
                return f"{key}: {val}"

        return None

    def add_memory(self, text: str, timestamp: float, sender: str, platform: str):
        """Helper to add a single memory to Qdrant."""
        if not self.qdrant or not self.model:
            logger.warning("Qdrant or embedding model not active. Cannot add memory.")
            return

        try:
            vector = self.model.encode(text).tolist()
            point_id = int(time.time() * 1000) % 1000000000  # Unique integer ID
            self.qdrant.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "text": text,
                            "timestamp": timestamp,
                            "sender": sender,
                            "platform": platform,
                        },
                    )
                ],
            )
            logger.info("Added memory to Qdrant collection.")
        except Exception as e:
            logger.error(f"Error writing to Qdrant: {e}")

    def search_memories(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Semantic search with custom temporal time-decay scoring (30-day half-life)."""
        if not self.qdrant or not self.model:
            logger.warning("Qdrant or embedding model not active. Returning empty search results.")
            return []

        try:
            vector = self.model.encode(query).tolist()
            # Fetch more results to perform time-decay reranking in python
            raw_results = self.qdrant.search(
                collection_name=COLLECTION_NAME,
                query_vector=vector,
                limit=top_k * 4,
            )

            reranked_results = []
            now = time.time()
            # Half-life of 30 days in seconds
            half_life = 30 * 24 * 3600
            lambda_val = math.log(2) / half_life

            for hit in raw_results:
                payload = hit.payload
                text = payload.get("text", "")
                timestamp = payload.get("timestamp", now)

                # Compute exponential decay
                age_seconds = max(0.0, now - timestamp)
                decay_factor = math.exp(-lambda_val * age_seconds)

                # Adjusted Score = Semantic similarity * decay factor
                adjusted_score = hit.score * decay_factor

                reranked_results.append(
                    {
                        "text": text,
                        "timestamp": timestamp,
                        "original_score": hit.score,
                        "score": adjusted_score,
                        "platform": payload.get("platform", "unknown"),
                        "sender": payload.get("sender", "unknown"),
                    }
                )

            # Sort by new adjusted score descending
            reranked_results.sort(key=lambda x: x["score"], reverse=True)
            return reranked_results[:top_k]

        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}")
            return []

    def ingest_chat_history(self, file_path: str):
        """Parses chat exports and bulk upserts to Qdrant."""
        if not os.path.exists(file_path):
            logger.error(f"Chat export file {file_path} not found.")
            return

        logger.info(f"Ingesting chat history from {file_path}...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Process in chunks to prevent large memory load
            points = []
            now = time.time()

            for idx, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 10:
                    continue

                # Quick embedding generation (simplistic parsing: one line = one memory)
                vector = self.model.encode(line).tolist()
                points.append(
                    PointStruct(
                        id=idx,
                        vector=vector,
                        payload={
                            "text": line,
                            "timestamp": now
                            - (idx * 3600),  # Synthesize older memories
                            "sender": "historical_user",
                            "platform": "chat_export",
                        },
                    )
                )

                if len(points) >= 100:
                    self.qdrant.upsert(
                        collection_name=COLLECTION_NAME, points=points
                    )
                    points = []

            if points:
                self.qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

            logger.info("Successfully ingested chat history.")
        except Exception as e:
            logger.error(f"Error during chat ingestion: {e}")


# Singleton instance of memory manager
memory_manager = MemoryManager()
