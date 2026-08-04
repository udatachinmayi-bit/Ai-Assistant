"""Configuration for the ChromaDB memory store."""

from pydantic import BaseModel, Field


class ChromaMemoryConfig(BaseModel):
    """Configuration for the ChromaDB memory store.

    Attributes:
        host: The host of the ChromaDB server.
        port: The port of the ChromaDB server.
        collection_name: The name of the collection to use for memories.
    """

    host: str = Field(default="localhost", description="The host of the ChromaDB server.")
    port: int = Field(default=8000, description="The port of the ChromaDB server.")
    collection_name: str = Field(
        default="chinu_long_term_memory",
        description="The name of the collection to use for memories.",
    )