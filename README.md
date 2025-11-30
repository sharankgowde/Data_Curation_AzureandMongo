# PDF RAG Chatbot - MongoDB & Azure OpenAI

A production-ready **Retrieval-Augmented Generation (RAG)** chatbot application that processes PDF documents, extracts text, generates embeddings using Azure OpenAI, stores them in MongoDB, and detects duplicate PDFs using cosine similarity.


<img width="692" height="286" alt="image" src="https://github.com/user-attachments/assets/b42badae-e968-4a91-9a19-c81b11f45c93" />




## 🚀 Features

- **PDF Upload & Processing**: Upload PDF files and automatically extract text
- **Smart Chunking**: Intelligent text chunking with configurable overlap for better context preservation
- **Azure OpenAI Embeddings**: Generate Ada embeddings using Azure OpenAI's embedding model
- **MongoDB Storage**: Store embeddings and metadata in MongoDB Atlas with vector search support
- **Duplicate Detection**: Detect duplicate PDFs using cosine similarity (configurable threshold)
- **Async FastAPI Server**: High-performance async API with auto-reload support
- **Swagger UI**: Interactive API documentation and testing interface
- **Docker Ready**: Includes Dockerfile for containerized deployment

## 📋 Prerequisites

- **Python 3.8+**
- **MongoDB Atlas** account with vector search enabled
- **Azure OpenAI** resource with text-embedding-ada-002 deployment
- **Git** (optional, for cloning the repository)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd python-mongodb-rag-chatbot
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with your credentials:

```dotenv
# MongoDB Atlas
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=<AppName>
MONGODB_DB=pdf_rag_db
VECTOR_COLLECTION=pdf_embeddings

# Azure OpenAI
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_ENDPOINT=https://<resource-name>.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

**Important**: Never commit `.env` file to version control. It's already in `.gitignore`.

## 📁 Project Structure

```
python-mongodb-rag-chatbot/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app initialization
│   │   └── routes_ingest.py     # PDF upload endpoint
│   ├── core/
│   │   └── config.py            # Configuration loader from .env
│   ├── db/
│   │   └── mongodb.py           # MongoDB async wrapper (Motor)
│   ├── embed/
│   │   └── embeddings.py        # Azure OpenAI embedding logic
│   ├── similaritycheck/
│   │   ├── __init__.py
│   │   └── similarity.py        # Cosine similarity & duplicate detection
│   ├── utils/
│   │   └── pdf_utils.py         # PDF extraction & chunking
│   └── storage/
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (git-ignored)
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
└── test_azure_connection.py      # Azure OpenAI connection tester
```

## ▶️ Running the Application

### Start the Server

```powershell
# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Start the server
python -m uvicorn src.api.main:app --reload --port 8000
```

The server will start on **http://localhost:8000**

### Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Expand `/ingest/upload` endpoint
3. Click "Try it out"
4. Click "Choose File" and select a PDF
5. Optionally adjust `similarity_threshold` (0-1, default: 0.85)
6. Click "Execute"

### Using cURL

```bash
curl -X POST -F "file=@path/to/your/file.pdf" \
  http://localhost:8000/ingest/upload
```

### Using Python Requests

```python
import requests

url = "http://localhost:8000/ingest/upload"
files = {"file": open("path/to/file.pdf", "rb")}
params = {"similarity_threshold": 0.85}

response = requests.post(url, files=files, params=params)
print(response.json())
```

## 📤 API Endpoints

### POST `/ingest/upload`

Upload a PDF for processing.

**Query Parameters:**
- `similarity_threshold` (float, optional): Similarity threshold for duplicate detection (0-1, default: 0.85)

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response (Success):**
```json
{
  "inserted": 125,
  "filename": "document.pdf",
  "total_chunks": 125,
  "duplicate_check": {
    "is_duplicate": false,
    "max_similarity": 0.42,
    "threshold_used": 0.85
  }
}
```

**Response (Duplicate Detected):**
```json
{
  "error": "PDF appears to be a duplicate",
  "similar_to": "existing_document.pdf",
  "similarity_score": 0.91,
  "threshold_used": 0.85,
  "message": "This PDF is 91% similar to 'existing_document.pdf'"
}
```

**Response (No Text):**
```json
{
  "inserted": 0,
  "detail": "No text extracted from PDF"
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## 🔍 Duplicate Detection

The system uses **cosine similarity** to detect duplicate PDFs:

- **Algorithm**: Compares embeddings of new PDF chunks against all existing embeddings
- **Threshold**: Default 0.85 (85% similarity) - adjustable per request
- **Result**: Returns highest similarity score found
- **Action**: Rejects upload if similarity exceeds threshold (HTTP 409)

### Adjusting Threshold

```bash
# Stricter (more likely to accept similar docs)
curl -X POST -F "file=@file.pdf" \
  "http://localhost:8000/ingest/upload?similarity_threshold=0.95"

# Looser (more likely to reject similar docs)
curl -X POST -F "file=@file.pdf" \
  "http://localhost:8000/ingest/upload?similarity_threshold=0.70"
```

## 🐛 Troubleshooting

### Azure OpenAI Authentication Error (401)

**Error:**
```
Error code: 401 - Access denied due to invalid subscription key or wrong API endpoint
```

**Solutions:**
1. Verify API key in `.env` is correct and not expired
2. Check endpoint format: `https://<resource-name>.openai.azure.com/`
3. Ensure deployment name `text-embedding-ada-002` exists in Azure OpenAI
4. Verify IP/network access to Azure resource
5. Run test script: `.\.venv\Scripts\python.exe test_azure_connection.py`

### MongoDB Connection Error

**Error:**
```
Failed to connect to MongoDB database
```

**Solutions:**
1. Verify `MONGODB_URI` in `.env` is correct
2. Check username and password in URI
3. Ensure IP is whitelisted in MongoDB Atlas network access
4. Verify cluster name and region in URI

### No Text Extracted from PDF

**Cause**: PDF contains only images or is encrypted

**Solutions:**
1. Verify PDF has selectable text (not scanned images)
2. Check PDF is not password-protected
3. Try extracting text manually to verify PDF is valid

## 📦 Dependencies

See `requirements.txt` for full list:

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **motor** - Async MongoDB driver
- **openai** - Azure OpenAI SDK
- **pymupdf** - PDF text extraction
- **numpy** - Vector operations for similarity
- **python-dotenv** - Environment variable loader
- **python-multipart** - Form data support

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t pdf-rag-chatbot .

# Run container
docker run -p 8000:8000 \
  -e MONGODB_URI=<uri> \
  -e AZURE_OPENAI_API_KEY=<key> \
  -e AZURE_OPENAI_ENDPOINT=<endpoint> \
  pdf-rag-chatbot
```

### Production Considerations

1. Use proper secrets management (Azure Key Vault, AWS Secrets Manager)
2. Enable HTTPS/TLS
3. Add authentication/authorization
4. Implement rate limiting
5. Add request logging and monitoring
6. Use production-grade MongoDB Atlas tier
7. Enable Vector Search indexes on MongoDB
8. Configure auto-scaling for API pods

## 📊 Data Flow

```
PDF Upload
    ↓
PDF Text Extraction (PyMuPDF)
    ↓
Text Chunking (1000 chars, 200 char overlap)
    ↓
Duplicate Detection (Cosine Similarity)
    ├─→ Duplicate Found → HTTP 409 Conflict
    └─→ No Duplicate → Continue
    ↓
Generate Embeddings (Azure OpenAI Ada)
    ↓
Store in MongoDB (pdf_embeddings collection)
    └─→ document: { text, embedding, metadata }
    ↓
HTTP 200 Success Response
```

## 🔐 Security

- ✅ `.env` added to `.gitignore` - credentials never committed
- ✅ API key masking in logs
- ⚠️ Consider adding API authentication
- ⚠️ Consider implementing rate limiting
- ⚠️ Consider HTTPS in production

## 📝 Configuration Details

### Text Chunking
- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters (for context preservation)
- **Adjustable in**: `src/utils/pdf_utils.py` → `chunk_text()`

### Embedding Model
- **Model**: text-embedding-ada-002
- **Dimension**: 1536
- **Provider**: Azure OpenAI
- **Cost**: Pay-per-token

### Similarity Threshold
- **Default**: 0.85
- **Range**: 0.0 - 1.0
- **Adjustable per**: Request parameter

## 📚 API Examples

### Example 1: Upload PDF with Default Settings
```bash
curl -X POST -F "file=@research.pdf" http://localhost:8000/ingest/upload
```

### Example 2: Upload with Custom Similarity Threshold
```bash
curl -X POST -F "file=@research.pdf" \
  "http://localhost:8000/ingest/upload?similarity_threshold=0.90"
```

### Example 3: Python Script
```python
import requests
import json

def upload_pdf(filepath, threshold=0.85):
    with open(filepath, 'rb') as f:
        files = {'file': f}
        params = {'similarity_threshold': threshold}
        response = requests.post(
            'http://localhost:8000/ingest/upload',
            files=files,
            params=params
        )
    return response.json()

result = upload_pdf('document.pdf', threshold=0.80)
print(json.dumps(result, indent=2))
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 💡 Future Enhancements

- [ ] Add vector search queries for RAG
- [ ] Implement chat interface
- [ ] Add LLM response generation
- [ ] Support multiple document types (docx, txt, etc.)
- [ ] Batch PDF processing
- [ ] Admin dashboard for document management
- [ ] User authentication and document ownership
- [ ] Async job queue for large files
- [ ] WebSocket support for real-time updates
- [ ] Semantic search capabilities

## 📞 Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review logs in server terminal
3. Run `test_azure_connection.py` to diagnose Azure issues
4. Open an issue in the repository

---

**Last Updated**: December 1, 2025  
**Version**: 1.0.0
