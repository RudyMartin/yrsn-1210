"""Context endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..models import ContextRequest, ContextResponse, ErrorResponse
from ysrn.application.context_handler import ContextHandler


router = APIRouter(prefix="/api/v1/context", tags=["context"])


def get_context_handler() -> ContextHandler:
    """Dependency to get context handler."""
    from ..app import get_context_handler as _get_handler
    return _get_handler()


@router.post("", response_model=ContextResponse, status_code=201)
async def add_context(
    request: ContextRequest,
    handler: ContextHandler = Depends(get_context_handler)
):
    """
    Add a new context block to the system.
    
    The context will be encoded and stored for retrieval.
    """
    try:
        context = await handler.add_context(
            content=request.content,
            metadata=request.metadata
        )
        return ContextResponse.from_domain(context)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add context: {str(e)}"
        )


@router.get("/{context_id}", response_model=ContextResponse)
async def get_context(
    context_id: str,
    handler: ContextHandler = Depends(get_context_handler)
):
    """
    Get a context block by ID.
    
    - **context_id**: The unique identifier of the context
    """
    try:
        context = await handler.get_context(context_id)
        if context is None:
            raise HTTPException(
                status_code=404,
                detail=f"Context {context_id} not found"
            )
        return ContextResponse.from_domain(context)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get context: {str(e)}"
        )

