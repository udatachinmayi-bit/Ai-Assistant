"""ChromaDB-based long-term semantic memory store."""

from typing import List

import chromadb
from chromadb.types import Collection

from chinu.logging_system.logger import get_logger
from chinu.memory.vector_store.config import ChromaMemoryConfig
from chinu.memory.vector_store.models import MemoryRecord, SearchResult

logger = get_logger("chroma_memory")


class ChromaMemoryStore:
    """A memory store using ChromaDB for semantic storage and retrieval."""

    def __init__(self, config: ChromaMemoryConfig) -> None:
        """Initialize the ChromaMemoryStore.

        Args:
            config: Configuration for the ChromaDB client.
        """
        self.config = config
        self._client = self._create_client()
        self._collection = self._get_or_create_collection()

    def _create_client(self) -> chromadb.Client:
        """Create and return a ChromaDB client."""
        try:
            client = chromadb.HttpClient(host=self.config.host, port=self.config.port)
            logger.info("ChromaDB client created.", host=self.config.host, port=self.config.port)
            return client
        except Exception as e:
            logger.error("Failed to create ChromaDB client.", exc_info=True)
            raise

    def _get_or_create_collection(self) -> Collection:
        """Get or create the ChromaDB collection for memories."""
        try:
            collection = self._client.get_or_create_collection(
                name=self.config.collection_name
            )
            logger.info("ChromaDB collection loaded.", name=self.config.collection_name)
            return collection
        except Exception as e:
            logger.error("Failed to get or create ChromaDB collection.", exc_info=True)
            raise

    def add_memory(self, memory: MemoryRecord) -> None:
        """Add a new memory to the store.

        Args:
            memory: The MemoryRecord to add.
        """
        self._collection.add(
            ids=[memory.id],
            embeddings=[memory.embedding],
            documents=[memory.content],
            metadatas=[memory.metadata],
        )
        logger.debug("Added memory to store.", memory_id=memory.id)

    def search_memories(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[SearchResult]:
        """Search for memories similar to a query embedding.

        Args:
            query_embedding: The vector embedding of the search query.
            top_k: The number of similar memories to return.

        Returns:
            A list of SearchResult objects.
        """
        results = self._collection.query(
            query_embeddings=[query_embedding], n_results=top_k
        )
        search_results = []
        if results and results["ids"]:
            for i, doc_id in enumerate(results["ids"][0]):
                search_results.append(
                    SearchResult(
                        id=doc_id,
                        content=results["documents"][0][i],
                        score=results["distances"][0][i],
                        metadata=results["metadatas"][0][i],
                    )
                )
        return search_results

    def update_memory(self, memory: MemoryRecord) -> None:
        """Update an existing memory in the store.

        Args:
            memory: The MemoryRecord to update.
        """
        self._collection.update(
            ids=[memory.id],
            embeddings=[memory.embedding],
            documents=[memory.content],
            metadatas=[memory.metadata],
        )
        logger.debug("Updated memory in store.", memory_id=memory.id)

    def delete_memory(self, memory_id: str) -> None:
        """Delete a memory from the store by its ID.

        Args:
            memory_id: The unique identifier of the memory to delete.
        """
        self._collection.delete(ids=[memory_id])
        logger.debug("Deleted memory from store.", memory_id=memory_id)