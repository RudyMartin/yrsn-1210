"""Configuration management for YSRN application."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class Environment(str, Enum):
    """Application environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    type: str = "in_memory"  # in_memory, file, chromadb
    path: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    collection_name: str = "ysrn_contexts"


@dataclass
class EncoderConfig:
    """Encoder configuration."""
    type: str = "simple"  # simple, sentence_transformers, openai
    model_name: str = "all-MiniLM-L6-v2"
    device: str = "cpu"
    api_key: Optional[str] = None
    organization: Optional[str] = None


@dataclass
class EventBusConfig:
    """Event bus configuration."""
    type: str = "in_memory"  # in_memory, redis, kafka
    host: Optional[str] = None
    port: Optional[int] = None
    topic: str = "ysrn_events"


@dataclass
class ObservabilityConfig:
    """Observability configuration."""
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    log_level: str = "INFO"
    prometheus_port: int = 9090
    jaeger_endpoint: Optional[str] = None


@dataclass
class YSRNConfig:
    """Main YSRN application configuration."""
    environment: Environment = Environment.DEVELOPMENT
    app_name: str = "YSRN"
    version: str = "0.1.0"
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    encoder: EncoderConfig = field(default_factory=EncoderConfig)
    event_bus: EventBusConfig = field(default_factory=EventBusConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    
    # Feature flags
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Secrets (loaded from environment or secrets file)
    secrets: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> 'YSRNConfig':
        """Load configuration from environment variables."""
        env = os.getenv("YSRN_ENV", "development")
        
        config = cls(
            environment=Environment(env.lower()),
            app_name=os.getenv("YSRN_APP_NAME", "YSRN"),
            version=os.getenv("YSRN_VERSION", "0.1.0")
        )
        
        # Database config
        config.database = DatabaseConfig(
            type=os.getenv("YSRN_DB_TYPE", "in_memory"),
            path=os.getenv("YSRN_DB_PATH"),
            host=os.getenv("YSRN_DB_HOST"),
            port=int(os.getenv("YSRN_DB_PORT", "0")) or None,
            collection_name=os.getenv("YSRN_DB_COLLECTION", "ysrn_contexts")
        )
        
        # Encoder config
        config.encoder = EncoderConfig(
            type=os.getenv("YSRN_ENCODER_TYPE", "simple"),
            model_name=os.getenv("YSRN_ENCODER_MODEL", "all-MiniLM-L6-v2"),
            device=os.getenv("YSRN_ENCODER_DEVICE", "cpu"),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("YSRN_ENCODER_API_KEY"),
            organization=os.getenv("OPENAI_ORGANIZATION")
        )
        
        # Event bus config
        config.event_bus = EventBusConfig(
            type=os.getenv("YSRN_EVENT_BUS_TYPE", "in_memory"),
            host=os.getenv("YSRN_EVENT_BUS_HOST"),
            port=int(os.getenv("YSRN_EVENT_BUS_PORT", "0")) or None,
            topic=os.getenv("YSRN_EVENT_BUS_TOPIC", "ysrn_events")
        )
        
        # Observability config
        config.observability = ObservabilityConfig(
            metrics_enabled=os.getenv("YSRN_METRICS_ENABLED", "true").lower() == "true",
            tracing_enabled=os.getenv("YSRN_TRACING_ENABLED", "true").lower() == "true",
            log_level=os.getenv("YSRN_LOG_LEVEL", "INFO"),
            prometheus_port=int(os.getenv("YSRN_PROMETHEUS_PORT", "9090")),
            jaeger_endpoint=os.getenv("JAEGER_ENDPOINT")
        )
        
        # Feature flags
        feature_flags_str = os.getenv("YSRN_FEATURE_FLAGS", "{}")
        try:
            config.feature_flags = json.loads(feature_flags_str)
        except:
            config.feature_flags = {}
        
        # Load secrets from environment
        config.secrets = {
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "database_password": os.getenv("YSRN_DB_PASSWORD", ""),
        }
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'YSRNConfig':
        """Load configuration from JSON file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        config = cls(
            environment=Environment(data.get("environment", "development")),
            app_name=data.get("app_name", "YSRN"),
            version=data.get("version", "0.1.0")
        )
        
        # Load nested configs
        if "database" in data:
            config.database = DatabaseConfig(**data["database"])
        if "encoder" in data:
            config.encoder = EncoderConfig(**data["encoder"])
        if "event_bus" in data:
            config.event_bus = EventBusConfig(**data["event_bus"])
        if "observability" in data:
            config.observability = ObservabilityConfig(**data["observability"])
        if "feature_flags" in data:
            config.feature_flags = data["feature_flags"]
        if "secrets" in data:
            config.secrets = data["secrets"]
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excluding secrets)."""
        return {
            "environment": self.environment.value,
            "app_name": self.app_name,
            "version": self.version,
            "database": {
                "type": self.database.type,
                "path": self.database.path,
                "host": self.database.host,
                "port": self.database.port,
                "collection_name": self.database.collection_name,
            },
            "encoder": {
                "type": self.encoder.type,
                "model_name": self.encoder.model_name,
                "device": self.encoder.device,
                "api_key": "***" if self.encoder.api_key else None,
                "organization": self.encoder.organization,
            },
            "event_bus": {
                "type": self.event_bus.type,
                "host": self.event_bus.host,
                "port": self.event_bus.port,
                "topic": self.event_bus.topic,
            },
            "observability": {
                "metrics_enabled": self.observability.metrics_enabled,
                "tracing_enabled": self.observability.tracing_enabled,
                "log_level": self.observability.log_level,
                "prometheus_port": self.observability.prometheus_port,
                "jaeger_endpoint": self.observability.jaeger_endpoint,
            },
            "feature_flags": self.feature_flags,
        }
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature flag is enabled."""
        return self.feature_flags.get(feature, False)
    
    def get_secret(self, key: str, default: str = "") -> str:
        """Get a secret value."""
        return self.secrets.get(key, default)


# Global config instance
_config: Optional[YSRNConfig] = None


def get_config() -> YSRNConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        # Try to load from file first, then fall back to environment
        config_file = os.getenv("YSRN_CONFIG_FILE")
        if config_file and Path(config_file).exists():
            _config = YSRNConfig.from_file(config_file)
        else:
            _config = YSRNConfig.from_env()
    return _config


def set_config(config: YSRNConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


