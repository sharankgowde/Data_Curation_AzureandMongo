import asyncio
from typing import List
from openai import AzureOpenAI
from src.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_EMBEDDING_DEPLOYMENT,
)

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Create embeddings for a list of texts using Azure OpenAI Ada model.

    Uses a background thread to avoid blocking the event loop.
    """
    if not texts:
        return []

    def _create_embeddings():
        try:
            # Debug: print configuration
            print(f"🔍 Azure OpenAI Config:")
            print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
            print(f"   Deployment: {AZURE_EMBEDDING_DEPLOYMENT}")
            print(f"   API Version: {AZURE_OPENAI_API_VERSION}")
            print(f"   Texts to embed: {len(texts)}")
            
            resp = client.embeddings.create(
                input=texts,
                model=AZURE_EMBEDDING_DEPLOYMENT,
            )
            embeddings = [item.embedding for item in resp.data]
            print(f"✓ Successfully created {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            print(f"✗ Embedding error: {e}")
            raise

    embeddings = await asyncio.to_thread(_create_embeddings)
    return embeddings
