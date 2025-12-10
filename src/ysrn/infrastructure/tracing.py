"""OpenTelemetry distributed tracing."""

from typing import Optional, Callable, Any
from functools import wraps
import functools

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = None
    FastAPIInstrumentor = None


_tracer: Optional[Any] = None
_tracer_provider: Optional[Any] = None


def initialize_tracing(
    service_name: str = "ysrn",
    jaeger_endpoint: Optional[str] = None,
    enabled: bool = True
) -> None:
    """Initialize OpenTelemetry tracing."""
    global _tracer, _tracer_provider
    
    if not OPENTELEMETRY_AVAILABLE or not enabled:
        return
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "0.1.0"
    })
    
    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)
    
    # Add span processor
    if jaeger_endpoint:
        # Export to Jaeger
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_endpoint.split(":")[0] if ":" in jaeger_endpoint else jaeger_endpoint,
            agent_port=int(jaeger_endpoint.split(":")[1]) if ":" in jaeger_endpoint else 6831,
        )
        _tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    else:
        # Console exporter for development
        console_exporter = ConsoleSpanExporter()
        _tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(_tracer_provider)
    
    # Get tracer
    _tracer = trace.get_tracer(service_name)


def get_tracer():
    """Get the global tracer instance."""
    if not OPENTELEMETRY_AVAILABLE or _tracer is None:
        # Return a no-op tracer
        class NoOpTracer:
            def start_span(self, *args, **kwargs):
                return NoOpSpan()
        class NoOpSpan:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def set_attribute(self, *args, **kwargs):
                pass
            def set_status(self, *args, **kwargs):
                pass
        return NoOpTracer()
    return _tracer


def trace_function(name: Optional[str] = None):
    """Decorator to trace function execution."""
    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"
        
        if not OPENTELEMETRY_AVAILABLE:
            return func
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        if hasattr(func, '__code__') and 'async' in str(func.__code__.co_flags):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def instrument_fastapi(app):
    """Instrument FastAPI application with OpenTelemetry."""
    if OPENTELEMETRY_AVAILABLE and FastAPIInstrumentor:
        FastAPIInstrumentor.instrument_app(app)
    return app


