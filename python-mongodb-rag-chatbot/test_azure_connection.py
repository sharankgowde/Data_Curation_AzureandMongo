"""Test Azure OpenAI connection"""
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials from environment
api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "").strip()
deployment = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "").strip()

print("=" * 60)
print("AZURE OPENAI CONNECTION TEST")
print("=" * 60)
print(f"\n📋 Configuration:")
print(f"   API Key: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else ''}")
print(f"   Endpoint: {endpoint}")
print(f"   API Version: {api_version}")
print(f"   Deployment: {deployment}")

# Validate configuration
if not api_key:
    print("\n❌ ERROR: AZURE_OPENAI_API_KEY is empty!")
    exit(1)
if not endpoint:
    print("\n❌ ERROR: AZURE_OPENAI_ENDPOINT is empty!")
    exit(1)
if not deployment:
    print("\n❌ ERROR: AZURE_EMBEDDING_DEPLOYMENT is empty!")
    exit(1)

print("\n✓ All configuration values are present")

# Test connection
print("\n🔄 Testing Azure OpenAI connection...")
try:
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
    )
    
    print("✓ Client created successfully")
    
    # Try to create a test embedding
    print("\n📝 Creating test embedding...")
    response = client.embeddings.create(
        input=["Test embedding"],
        model=deployment,
    )
    
    print(f"✓ Embedding created successfully!")
    print(f"   Embedding dimension: {len(response.data[0].embedding)}")
    print(f"   First 5 values: {response.data[0].embedding[:5]}")
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS: Azure OpenAI connection is working!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING TIPS:")
    print("=" * 60)
    print("1. Verify API key is correct and hasn't expired")
    print("2. Check endpoint format: https://<resource-name>.openai.azure.com/")
    print("3. Ensure deployment name exists in your Azure OpenAI resource")
    print("4. Verify API version is supported (2023-05-15 or later)")
    print("5. Check that your IP has network access to the resource")
    exit(1)
