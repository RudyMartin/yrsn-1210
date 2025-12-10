"""Pydantic models for REST API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# Request Models
class QueryRequest(BaseModel):
    """Request to submit a query."""
    text: str = Field(..., description="Query text")
    constraints: List[str] = Field(default_factory=list, description="Optional constraints")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")


class ContextRequest(BaseModel):
    """Request to add a context."""
    content: str = Field(..., description="Context content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")


# Response Models
class ContextResponse(BaseModel):
    """Context response model."""
    id: str
    content: str
    relevance_score: Optional[float] = None
    superfluous_score: Optional[float] = None
    noise_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    @classmethod
    def from_domain(cls, context_block) -> 'ContextResponse':
        """Create from domain model."""
        return cls(
            id=context_block.id,
            content=context_block.content,
            relevance_score=context_block.relevance_score,
            superfluous_score=context_block.superfluous_score,
            noise_score=context_block.noise_score,
            metadata=context_block.metadata,
            created_at=context_block.created_at
        )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "content": "Example context content",
                "relevance_score": 0.85,
                "superfluous_score": 0.10,
                "noise_score": 0.05,
                "metadata": {},
                "created_at": "2025-12-01T12:00:00"
            }
        }


class QueryResponse(BaseModel):
    """Query submission response."""
    query_id: str
    status: str = "submitted"
    message: str = "Query submitted successfully"


class QueryResultResponse(BaseModel):
    """Query result response."""
    query_id: str
    contexts: List[ContextResponse]
    total_candidates: int
    processing_time_ms: float
    decomposition_stats: Dict[str, float] = Field(default_factory=dict)

    @classmethod
    def from_domain(cls, query_result) -> 'QueryResultResponse':
        """Create from domain model."""
        return cls(
            query_id=query_result.query_id,
            contexts=[ContextResponse.from_domain(ctx) for ctx in query_result.contexts],
            total_candidates=query_result.total_candidates,
            processing_time_ms=query_result.processing_time_ms,
            decomposition_stats=query_result.decomposition_stats
        )

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "550e8400-e29b-41d4-a716-446655440000",
                "contexts": [],
                "total_candidates": 10,
                "processing_time_ms": 45.2,
                "decomposition_stats": {
                    "avg_relevance": 0.75,
                    "avg_noise": 0.10
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    status_code: int


