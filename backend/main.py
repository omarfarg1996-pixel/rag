"""
Super RAG - Main FastAPI Application
Cognitive Operating System with Hybrid Memory Intelligence
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import logging
import time
import uuid
from typing import Dict, Any, Optional

from .core.config import settings, get_settings
from .memory.working_memory import get_working_memory, WorkingMemory
from .memory.semantic_memory import get_semantic_memory, SemanticMemory

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - initialize and cleanup resources"""
    # Startup
    logger.info("Starting Super RAG Cognitive Operating System...")
    
    try:
        # Initialize memory layers
        working_mem = await get_working_memory()
        await working_mem.connect()
        
        semantic_mem = await get_semantic_memory()
        await semantic_mem.connect()
        
        logger.info("All memory layers initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize memory layers: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Super RAG...")
    
    try:
        working_mem = await get_working_memory()
        await working_mem.disconnect()
        
        semantic_mem = await get_semantic_memory()
        await semantic_mem.disconnect()
        
        logger.info("All memory layers disconnected")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cognitive Operating System with Hybrid Memory Intelligence",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Health Check
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": int(time.time())
    }


# System Status
@app.get("/api/v1/status")
async def system_status(
    working_mem: WorkingMemory = Depends(get_working_memory),
    semantic_mem: SemanticMemory = Depends(get_semantic_memory)
):
    """Get system status and memory statistics"""
    try:
        redis_info = await working_mem.get_memory_info()
        milvus_stats = await semantic_mem.get_stats()
        
        return {
            "status": "operational",
            "memory_layers": {
                "working_memory": {
                    "type": "Redis",
                    "status": "connected",
                    "stats": redis_info
                },
                "semantic_memory": {
                    "type": "Milvus",
                    "status": "connected",
                    "stats": milvus_stats
                }
            },
            "configuration": {
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "embedding_model": settings.EMBEDDING_MODEL,
                "search_top_k": settings.SEARCH_TOP_K,
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Chat Query Endpoint
@app.post("/api/v1/chat")
async def chat_query(
    request: Dict[str, Any],
    working_mem: WorkingMemory = Depends(get_working_memory)
):
    """
    Process a chat query with hybrid memory retrieval
    
    Request body:
    {
        "query": "user question",
        "session_id": "optional-session-id",
        "depth": "shallow" | "deep",
        "sources": ["memory", "web", "both"]
    }
    """
    query = request.get("query")
    session_id = request.get("session_id", str(uuid.uuid4()))
    depth = request.get("depth", "shallow")
    sources = request.get("sources", ["memory"])
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        start_time = time.time()
        
        # Save user message to conversation history
        await working_mem.add_to_conversation(
            session_id=session_id,
            role="user",
            content=query
        )
        
        # TODO: Implement full query processing pipeline
        # For now, return a placeholder response
        response_text = f"Received query: {query}\n\nFull RAG pipeline coming soon..."
        
        # Save assistant response
        await working_mem.add_to_conversation(
            session_id=session_id,
            role="assistant",
            content=response_text
        )
        
        process_time = time.time() - start_time
        
        return {
            "answer": response_text,
            "session_id": session_id,
            "sources": [],
            "confidence": 1.0,
            "process_time_ms": int(process_time * 1000),
            "request_id": request.state.request_id
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Streaming Chat Endpoint
@app.post("/api/v1/chat/stream")
async def chat_query_stream(
    request: Dict[str, Any],
    working_mem: WorkingMemory = Depends(get_working_memory)
):
    """Stream chat response using Server-Sent Events"""
    
    async def generate():
        yield f"data: {{\"type\": \"start\"}}\n\n"
        
        # Simulate streaming response
        chunks = [
            "This is a streaming response.",
            " Full RAG pipeline coming soon...",
            " Stay tuned!"
        ]
        
        for chunk in chunks:
            yield f"data: {{\"type\": \"chunk\", \"content\": \"{chunk}\"}}\n\n"
            await asyncio.sleep(0.1)
        
        yield f"data: {{\"type\": \"end\"}}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


# Document Upload Endpoint
@app.post("/api/v1/documents/upload")
async def upload_document(
    request: Request,
    working_mem: WorkingMemory = Depends(get_working_memory),
    semantic_mem: SemanticMemory = Depends(get_semantic_memory)
):
    """Upload and index a document"""
    try:
        form = await request.form()
        file = form.get("file")
        metadata_str = form.get("metadata", "{}")
        
        if not file:
            raise HTTPException(status_code=400, detail="File is required")
        
        # TODO: Implement document processing pipeline
        return {
            "status": "success",
            "message": "Document upload pipeline coming soon...",
            "filename": file.filename if hasattr(file, 'filename') else "unknown"
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Memory Management Endpoints
@app.get("/api/v1/memory/stats")
async def memory_stats(
    working_mem: WorkingMemory = Depends(get_working_memory),
    semantic_mem: SemanticMemory = Depends(get_semantic_memory)
):
    """Get detailed memory statistics"""
    try:
        redis_stats = await working_mem.get_memory_info()
        milvus_stats = await semantic_mem.get_stats()
        
        return {
            "working_memory": redis_stats,
            "semantic_memory": milvus_stats
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/memory/cache/clear")
async def clear_cache(
    working_mem: WorkingMemory = Depends(get_working_memory)
):
    """Clear semantic cache"""
    try:
        # Clear cache keys
        cache_keys = await working_mem.scan_keys("cache:*")
        if cache_keys:
            await working_mem.delete(*cache_keys)
        
        return {
            "status": "success",
            "keys_cleared": len(cache_keys)
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# n8n Webhook Integration
@app.post("/api/v1/webhook/n8n/query")
async def n8n_webhook_query(request: Dict[str, Any]):
    """n8n webhook for query processing"""
    query = request.get("query")
    context = request.get("context", {})
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # TODO: Implement full query processing
    return {
        "answer": f"Processed query via n8n: {query}",
        "sources": [],
        "confidence": 0.95
    }


@app.get("/api/v1/webhook/n8n/health")
async def n8n_webhook_health():
    """n8n webhook health check"""
    return {"status": "healthy"}


# Prometheus Metrics Endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=2
    )
