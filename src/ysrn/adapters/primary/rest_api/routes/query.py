"""Query endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..models import QueryRequest, QueryResponse, QueryResultResponse, ErrorResponse
from ysrn.application.query_handler import QueryHandler


router = APIRouter(prefix="/api/v1/query", tags=["query"])


def get_query_handler() -> QueryHandler:
    """Dependency to get query handler."""
    # This will be injected by the app factory
    from ..app import get_query_handler as _get_handler
    return _get_handler()


@router.post("", response_model=QueryResponse, status_code=202)
async def submit_query(
    request: QueryRequest,
    handler: QueryHandler = Depends(get_query_handler)
):
    """
    Submit a new query for context retrieval.
    
    Returns a query_id that can be used to retrieve results.
    """
    try:
        query_id = await handler.submit_query(
            text=request.text,
            constraints=request.constraints
        )
        return QueryResponse(
            query_id=query_id,
            status="submitted",
            message="Query submitted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit query: {str(e)}"
        )


@router.get("/{query_id}", response_model=QueryResultResponse)
async def get_query_result(
    query_id: str,
    timeout: float = 30.0,
    handler: QueryHandler = Depends(get_query_handler)
):
    """
    Get the result of a query.
    
    - **query_id**: The ID returned from submitting a query
    - **timeout**: Maximum time to wait for result (seconds)
    """
    try:
        result = await handler.get_result(query_id, timeout=timeout)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Query {query_id} not found or not yet completed"
            )
        return QueryResultResponse.from_domain(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get query result: {str(e)}"
        )


@router.post("/{query_id}/stream")
async def stream_query_results(
    query_id: str,
    handler: QueryHandler = Depends(get_query_handler)
):
    """
    Stream incremental results for a query.
    
    This endpoint would use Server-Sent Events (SSE) for streaming.
    For now, returns a placeholder.
    """
    # TODO: Implement SSE streaming
    raise HTTPException(
        status_code=501,
        detail="Streaming not yet implemented"
    )

