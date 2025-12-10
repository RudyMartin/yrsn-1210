"""Prometheus metrics collection."""

from typing import Optional, Any
from functools import wraps
import time

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Any
    Histogram = Any
    Gauge = Any


# Metrics
_query_counter: Optional[Any] = None
_query_duration: Optional[Any] = None
_context_counter: Optional[Any] = None
_embedding_counter: Optional[Any] = None
_active_queries: Optional[Any] = None
_context_storage_size: Optional[Any] = None


def initialize_metrics() -> None:
    """Initialize Prometheus metrics."""
    global _query_counter, _query_duration, _context_counter
    global _embedding_counter, _active_queries, _context_storage_size
    
    if not PROMETHEUS_AVAILABLE:
        return
    
    _query_counter = Counter(
        'ysrn_queries_total',
        'Total number of queries processed',
        ['status']  # success, error
    )
    
    _query_duration = Histogram(
        'ysrn_query_duration_seconds',
        'Query processing duration in seconds',
        ['stage']  # encoding, retrieval, classification
    )
    
    _context_counter = Counter(
        'ysrn_contexts_total',
        'Total number of contexts processed',
        ['operation']  # added, retrieved, classified
    )
    
    _embedding_counter = Counter(
        'ysrn_embeddings_total',
        'Total number of embeddings generated',
        ['type']  # context, query
    )
    
    _active_queries = Gauge(
        'ysrn_active_queries',
        'Number of currently active queries'
    )
    
    _context_storage_size = Gauge(
        'ysrn_context_storage_size',
        'Total number of contexts in storage'
    )


def record_query(status: str = "success") -> None:
    """Record a query metric."""
    if _query_counter:
        _query_counter.labels(status=status).inc()


def record_query_duration(stage: str, duration: float) -> None:
    """Record query processing duration."""
    if _query_duration:
        _query_duration.labels(stage=stage).observe(duration)


def record_context(operation: str) -> None:
    """Record a context operation."""
    if _context_counter:
        _context_counter.labels(operation=operation).inc()


def record_embedding(embedding_type: str) -> None:
    """Record an embedding generation."""
    if _embedding_counter:
        _embedding_counter.labels(type=embedding_type).inc()


def set_active_queries(count: int) -> None:
    """Set the number of active queries."""
    if _active_queries:
        _active_queries.set(count)


def set_context_storage_size(count: int) -> None:
    """Set the context storage size."""
    if _context_storage_size:
        _context_storage_size.set(count)


def get_metrics() -> bytes:
    """Get Prometheus metrics in text format."""
    if not PROMETHEUS_AVAILABLE:
        return b"# Prometheus client not available\n"
    return generate_latest(REGISTRY)


def metrics_middleware(func):
    """Decorator to automatically record metrics for async functions."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            record_query("success")
            return result
        except Exception as e:
            record_query("error")
            raise
        finally:
            duration = time.time() - start_time
            record_query_duration("total", duration)
    return wrapper

