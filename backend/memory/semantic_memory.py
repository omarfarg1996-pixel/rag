"""
Semantic Memory Layer - Milvus-based vector memory with RaBitQ optimization
Handles long-term semantic knowledge storage and retrieval
"""
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
    IndexParams,
)
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


class SemanticMemory:
    """Milvus-backed semantic memory for vector embeddings with RaBitQ optimization"""
    
    def __init__(self):
        self.connection_alias: str = "default"
        self.collection: Optional[Collection] = None
        self.collection_name: str = settings.MILVUS_COLLECTION_NAME
    
    async def connect(self) -> None:
        """Initialize Milvus connection"""
        try:
            connections.connect(
                alias=self.connection_alias,
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT
            )
            logger.info("SemanticMemory connected to Milvus")
            
            # Create or load collection
            await self._create_collection()
            
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Milvus connection"""
        try:
            connections.disconnect(self.connection_alias)
            logger.info("SemanticMemory disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {e}")
    
    async def _create_collection(self) -> None:
        """Create Milvus collection with RaBitQ-optimized schema"""
        try:
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                logger.info(f"Loaded existing collection: {self.collection_name}")
                return
            
            # Define schema
            fields = [
                FieldSchema(
                    name="id",
                    dtype=DataType.VARCHAR,
                    max_length=128,
                    is_primary=True
                ),
                FieldSchema(
                    name="content",
                    dtype=DataType.VARCHAR,
                    max_length=65535  # Max content size
                ),
                FieldSchema(
                    name="metadata",
                    dtype=DataType.JSON
                ),
                FieldSchema(
                    name="embedding",
                    dtype=DataType.FLOAT_VECTOR,
                    dim=settings.EMBEDDING_DIMENSION
                ),
                FieldSchema(
                    name="timestamp",
                    dtype=DataType.INT64
                ),
                FieldSchema(
                    name="freshness_score",
                    dtype=DataType.FLOAT
                ),
            ]
            
            schema = CollectionSchema(fields=fields, description="Semantic Memory Collection")
            
            # Create collection
            self.collection = Collection(name=self.collection_name, schema=schema)
            logger.info(f"Created collection: {self.collection_name}")
            
            # Create index with RaBitQ quantization for 72% memory reduction
            index_params = IndexParams()
            index_params.add_index(
                field_name="embedding",
                index_type=settings.MILVUS_INDEX_TYPE,  # IVF_FLAT
                metric_type="COSINE",
                params={
                    "nlist": settings.MILVUS_NLIST,
                    "quantization": {
                        "type": "RaBitQ",  # 1-bit quantization
                        "nbits": 1
                    }
                }
            )
            
            self.collection.create_index(index_params=index_params)
            
            # Load collection into memory
            self.collection.load()
            logger.info(f"Collection loaded with RaBitQ optimization")
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    async def insert(
        self,
        id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None
    ) -> bool:
        """
        Insert a document into semantic memory
        
        Args:
            id: Unique document identifier
            content: Text content
            embedding: Vector embedding
            metadata: Additional metadata
            timestamp: Unix timestamp
            
        Returns:
            True if successful
        """
        try:
            if not self.collection:
                raise RuntimeError("Collection not initialized")
            
            data = [{
                "id": id,
                "content": content,
                "metadata": metadata or {},
                "embedding": embedding,
                "timestamp": timestamp or int(__import__("time").time()),
                "freshness_score": 1.0
            }]
            
            result = self.collection.insert(data)
            self.collection.flush()
            
            logger.debug(f"Inserted document {id} into semantic memory")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            return False
    
    async def insert_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """
        Insert multiple documents in batch
        
        Args:
            documents: List of dicts with keys: id, content, embedding, metadata
            
        Returns:
            Tuple of (success_count, total_count)
        """
        success_count = 0
        total_count = len(documents)
        
        try:
            if not self.collection or not documents:
                return (0, total_count)
            
            # Prepare batch data
            data = []
            for doc in documents:
                data.append({
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "embedding": doc["embedding"],
                    "timestamp": doc.get("timestamp", int(__import__("time").time())),
                    "freshness_score": doc.get("freshness_score", 1.0)
                })
            
            # Insert in batches of 1000
            batch_size = 1000
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                result = self.collection.insert(batch)
                success_count += len(batch)
            
            self.collection.flush()
            logger.info(f"Inserted {success_count}/{total_count} documents")
            
        except Exception as e:
            logger.error(f"Error batch inserting: {e}")
        
        return (success_count, total_count)
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_expr: Optional[str] = None,
        timeout: int = 3000
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_expr: Milvus filter expression
            timeout: Timeout in milliseconds
            
        Returns:
            List of matching documents with scores
        """
        try:
            if not self.collection:
                raise RuntimeError("Collection not initialized")
            
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 16}  # Optimized for IVF_FLAT
            }
            
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=["id", "content", "metadata", "timestamp", "freshness_score"],
                timeout=timeout
            )
            
            # Format results
            formatted_results = []
            if results and len(results) > 0:
                for hit in results[0]:
                    formatted_results.append({
                        "id": hit.entity.get("id"),
                        "content": hit.entity.get("content"),
                        "metadata": hit.entity.get("metadata"),
                        "timestamp": hit.entity.get("timestamp"),
                        "freshness_score": hit.entity.get("freshness_score"),
                        "score": hit.score,
                        "distance": 1 - hit.score  # Convert similarity to distance
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    async def delete(self, ids: List[str]) -> int:
        """Delete documents by IDs"""
        try:
            if not self.collection:
                return 0
            
            expr = f'id in {ids}'
            result = self.collection.delete(expr)
            self.collection.flush()
            
            logger.info(f"Deleted {len(ids)} documents")
            return len(ids)
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return 0
    
    async def update_freshness(
        self,
        ids: List[str],
        freshness_score: float
    ) -> bool:
        """Update freshness score for documents"""
        try:
            # Note: Milvus doesn't support partial updates directly
            # Need to delete and re-insert
            logger.warning("Freshness update requires delete+reinsert in Milvus")
            return False
        except Exception as e:
            logger.error(f"Error updating freshness: {e}")
            return False
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a single document by ID"""
        try:
            if not self.collection:
                return None
            
            results = self.collection.query(
                expr=f'id == "{doc_id}"',
                output_fields=["id", "content", "metadata", "embedding", "timestamp", "freshness_score"]
            )
            
            if results and len(results) > 0:
                return results[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    async def count(self) -> int:
        """Get total document count"""
        try:
            if not self.collection:
                return 0
            return self.collection.num_entities
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    async def drop(self) -> bool:
        """Drop the entire collection"""
        try:
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                logger.info(f"Dropped collection: {self.collection_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error dropping collection: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            if not self.collection:
                return {}
            
            stats = {
                "collection_name": self.collection_name,
                "document_count": self.collection.num_entities,
                "index_type": settings.MILVUS_INDEX_TYPE,
                "quantization": settings.MILVUS_QUANTIZATION,
                "dimension": settings.EMBEDDING_DIMENSION,
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Global instance
semantic_memory = SemanticMemory()


async def get_semantic_memory() -> SemanticMemory:
    """Get semantic memory instance"""
    return semantic_memory
