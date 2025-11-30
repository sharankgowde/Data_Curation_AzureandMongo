import numpy as np
from typing import List, Tuple, Optional
from motor.motor_asyncio import AsyncIOMotorCollection


async def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.
    
    Returns a value between 0 and 1, where 1 is identical.
    """
    arr1 = np.array(vec1)
    arr2 = np.array(vec2)
    
    dot_product = np.dot(arr1, arr2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return float(similarity)


async def check_pdf_duplicate(
    collection: AsyncIOMotorCollection,
    pdf_embeddings: List[List[float]],
    filename: str,
    similarity_threshold: float = 0.85
) -> Tuple[bool, Optional[str], float]:
    """Check if a PDF already exists by comparing embeddings.
    
    Args:
        collection: MongoDB collection with existing embeddings
        pdf_embeddings: List of embeddings from the new PDF
        filename: Name of the file being uploaded
        similarity_threshold: Threshold (0-1) for considering documents as duplicates
    
    Returns:
        Tuple of (is_duplicate, existing_filename, max_similarity_score)
    """
    if not pdf_embeddings:
        return False, None, 0.0
    
    # Get all existing embeddings from the collection
    existing_docs = await collection.find({}, {"embedding": 1, "metadata.filename": 1}).to_list(None)
    
    if not existing_docs:
        return False, None, 0.0
    
    # Compare each new embedding with all existing embeddings
    max_similarity = 0.0
    most_similar_filename = None
    
    for new_emb in pdf_embeddings:
        for existing_doc in existing_docs:
            if "embedding" in existing_doc:
                existing_emb = existing_doc["embedding"]
                similarity = await cosine_similarity(new_emb, existing_emb)
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    existing_metadata = existing_doc.get("metadata", {})
                    most_similar_filename = existing_metadata.get("filename", "unknown")
                
                # Early exit if we find a very high match
                if similarity > similarity_threshold:
                    return True, most_similar_filename, similarity
    
    # Check if max similarity exceeds threshold
    is_duplicate = max_similarity > similarity_threshold
    return is_duplicate, most_similar_filename, max_similarity


async def get_similarity_stats(
    collection: AsyncIOMotorCollection,
    embedding: List[float],
    top_k: int = 5
) -> List[dict]:
    """Get the top-k most similar documents to a given embedding.
    
    Args:
        collection: MongoDB collection with embeddings
        embedding: Query embedding vector
        top_k: Number of similar documents to return
    
    Returns:
        List of documents with similarity scores, sorted by similarity descending
    """
    existing_docs = await collection.find({}, {"text": 1, "embedding": 1, "metadata": 1}).to_list(None)
    
    similarities = []
    for doc in existing_docs:
        if "embedding" in doc:
            similarity = await cosine_similarity(embedding, doc["embedding"])
            similarities.append({
                "filename": doc.get("metadata", {}).get("filename", "unknown"),
                "chunk_index": doc.get("metadata", {}).get("chunk_index", 0),
                "text": doc.get("text", "")[:100],  # First 100 chars
                "similarity": similarity
            })
    
    # Sort by similarity descending and return top k
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities[:top_k]
