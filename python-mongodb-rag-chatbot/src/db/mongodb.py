from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import MONGODB_URI, MONGODB_DB, VECTOR_COLLECTION


class MongoDB:
    def __init__(self, uri: str = None, db_name: str = None):
        self._uri = uri or MONGODB_URI
        self._db_name = db_name or MONGODB_DB
        self.client = AsyncIOMotorClient(self._uri)
        self.db = self.client[self._db_name]

    def get_collection(self, name):
        return self.db[name]

    async def close(self):
        self.client.close()

    async def ensure_collection_exists(self, collection_name: str = None):
        """Check if collection exists, create it if not."""
        col_name = collection_name or VECTOR_COLLECTION
        existing_collections = await self.db.list_collection_names()
        
        if col_name not in existing_collections:
            # Create collection with vector search index if needed
            await self.db.create_collection(col_name)
            print(f"✓ Created collection: {col_name}")
        else:
            print(f"✓ Collection already exists: {col_name}")
        
        return self.db[col_name]

    async def ensure_database_exists(self):
        """Verify database exists by listing collections."""
        try:
            collections = await self.db.list_collection_names()
            print(f"✓ Database '{self._db_name}' is accessible with {len(collections)} collection(s)")
            return True
        except Exception as e:
            print(f"✗ Error accessing database: {e}")
            return False
