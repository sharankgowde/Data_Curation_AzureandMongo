from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from src.utils.pdf_utils import extract_text_from_pdf_bytes, chunk_text
from src.embed.embeddings import embed_texts
from src.db.mongodb import MongoDB
from src.core.config import VECTOR_COLLECTION
from src.similaritycheck import check_pdf_duplicate
import asyncio

router = APIRouter()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    similarity_threshold: float = Query(0.85, ge=0.0, le=1.0, description="Threshold for duplicate detection (0-1)")
):
    """Upload a PDF, extract text, chunk it, embed chunks, and store in MongoDB.
    
    Args:
        file: PDF file to upload
        similarity_threshold: Cosine similarity threshold for detecting duplicates (default 0.85)
    
    Returns:
        JSON with insertion status, filename, total chunks, and duplicate detection results
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    db = MongoDB()
    
    # Verify database and collection exist
    db_exists = await db.ensure_database_exists()
    if not db_exists:
        raise HTTPException(status_code=500, detail="Failed to connect to MongoDB database")
    
    collection = await db.ensure_collection_exists(VECTOR_COLLECTION)

    content = await file.read()
    try:
        text = extract_text_from_pdf_bytes(content)
    except Exception as e:
        await db.close()
        raise HTTPException(status_code=500, detail=f"Failed to extract PDF text: {e}")

    chunks = chunk_text(text)
    if not chunks:
        await db.close()
        return JSONResponse({"inserted": 0, "detail": "No text extracted from PDF"})

    # embed chunks in batches to avoid sending too large a request
    BATCH_SIZE = 50
    embeddings: List[List[float]] = []
    try:
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            batch_embeddings = await embed_texts(batch)
            embeddings.extend(batch_embeddings)
    except Exception as e:
        await db.close()
        raise HTTPException(status_code=500, detail=f"Failed to create embeddings: {e}")

    # Check for duplicate PDF using cosine similarity
    is_duplicate, similar_filename, max_similarity = await check_pdf_duplicate(
        collection,
        embeddings,
        file.filename,
        similarity_threshold=similarity_threshold
    )
    
    if is_duplicate:
        await db.close()
        return JSONResponse(
            status_code=409,
            content={
                "error": "PDF appears to be a duplicate",
                "similar_to": similar_filename,
                "similarity_score": round(max_similarity, 4),
                "threshold_used": similarity_threshold,
                "message": f"This PDF is {round(max_similarity * 100, 2)}% similar to '{similar_filename}'"
            }
        )

    # Prepare documents for MongoDB
    docs = []
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        docs.append(
            {
                "text": chunk,
                "embedding": emb,
                "metadata": {
                    "filename": file.filename,
                    "chunk_index": idx,
                },
            }
        )

    try:
        result = await collection.insert_many(docs)
        inserted = len(result.inserted_ids)
    except Exception as e:
        await db.close()
        raise HTTPException(status_code=500, detail=f"Failed to insert embeddings into MongoDB: {e}")
    finally:
        await db.close()

    return {
        "inserted": inserted,
        "filename": file.filename,
        "total_chunks": len(chunks),
        "duplicate_check": {
            "is_duplicate": False,
            "max_similarity": round(max_similarity, 4),
            "threshold_used": similarity_threshold
        }
    }
