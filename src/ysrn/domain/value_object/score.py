"""Score value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RelevanceScore:
    """Relevance score with confidence."""
    value: float  # [0, 1]
    confidence: float  # [0, 1]
    
    def __post_init__(self):
        if not 0 <= self.value <= 1:
            object.__setattr__(self, 'value', max(0, min(1, self.value)))
        if not 0 <= self.confidence <= 1:
            object.__setattr__(self, 'confidence', max(0, min(1, self.confidence)))


@dataclass(frozen=True)
class QualityScore:
    """Signal quality score."""
    value: float  # R / (S + N)
    signal_to_noise: float
    relevance_ratio: float


