"""Context classification service."""

from typing import List
from ..model.context import ContextBlock
from ..model.query import Query
from .ysrn_engine import YSRNEngine


class ContextClassifier:
    """Classifies contexts using YSRN decomposition."""
    
    def __init__(self, ysrn_engine: YSRNEngine):
        self.ysrn_engine = ysrn_engine
    
    def classify(self, context: ContextBlock, query: Query) -> ContextBlock:
        """Classify a single context."""
        return self.ysrn_engine.classify_context(context, query)
    
    def classify_batch(self, contexts: List[ContextBlock], query: Query) -> List[ContextBlock]:
        """Classify multiple contexts."""
        return self.ysrn_engine.batch_classify(contexts, query)


