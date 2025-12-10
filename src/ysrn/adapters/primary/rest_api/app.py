"""FastAPI application factory and dependency injection."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .routes import query, context, health, curriculum
from ysrn.application.query_handler import QueryHandler
from ysrn.application.context_handler import ContextHandler
from ysrn.application.curriculum_handler import CurriculumHandler
from ysrn.domain.service.ysrn_engine import YSRNEngine
from ysrn.domain.service.gated_retrieval import GatedContextRetriever
from ysrn.adapters.secondary.encoder.simple_encoder_adapter import SimpleEncoderAdapter
from ysrn.adapters.secondary.persistence.in_memory_adapter import InMemoryPersistenceAdapter
from ysrn.adapters.secondary.event_bus.in_memory_event_bus import InMemoryEventBusAdapter


# Global application state (singleton pattern)
_app: Optional[FastAPI] = None
_query_handler: Optional[QueryHandler] = None
_context_handler: Optional[ContextHandler] = None
_curriculum_handler: Optional[CurriculumHandler] = None


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Sets up dependency injection for all handlers and services.
    """
    global _app, _query_handler, _context_handler, _curriculum_handler
    
    if _app is not None:
        return _app
    
    # Create FastAPI app
    app = FastAPI(
        title="YSRN API",
        description="YSRN (Y=R+S+N) Context Retrieval API using Hexagonal Architecture",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize adapters (secondary ports)
    encoder = SimpleEncoderAdapter(output_dim=512)
    persistence = InMemoryPersistenceAdapter()
    event_bus = InMemoryEventBusAdapter()
    
    # Initialize domain services
    ysrn_engine = YSRNEngine(
        relevance_threshold=0.3,
        noise_threshold=0.1,
        num_components=64
    )
    retriever = GatedContextRetriever(
        num_heads=8,
        head_dim=64,
        gate_init_bias=-2.0
    )
    
    # Initialize application handlers
    _query_handler = QueryHandler(
        ysrn_engine=ysrn_engine,
        retriever=retriever,
        encoder=encoder,
        persistence=persistence,
        event_bus=event_bus
    )
    
    _context_handler = ContextHandler(
        encoder=encoder,
        persistence=persistence
    )
    
    _curriculum_handler = CurriculumHandler(
        persistence=persistence
    )
    
    # Register routes
    app.include_router(health.router)
    app.include_router(query.router)
    app.include_router(context.router)
    app.include_router(curriculum.router)
    
    _app = app
    return app


def get_app() -> FastAPI:
    """Get the FastAPI application instance."""
    if _app is None:
        return create_app()
    return _app


def get_query_handler() -> QueryHandler:
    """Get the query handler instance."""
    if _query_handler is None:
        create_app()  # Initialize if not already done
    return _query_handler


def get_context_handler() -> ContextHandler:
    """Get the context handler instance."""
    if _context_handler is None:
        create_app()  # Initialize if not already done
    return _context_handler


def get_curriculum_handler() -> CurriculumHandler:
    """Get the curriculum handler instance."""
    if _curriculum_handler is None:
        create_app()  # Initialize if not already done
    return _curriculum_handler

