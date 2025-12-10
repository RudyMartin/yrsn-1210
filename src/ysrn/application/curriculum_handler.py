"""Curriculum handler - Use case for curriculum learning."""

from typing import List, Optional
from ..domain.model.curriculum import CurriculumStage, LearningProgress
from ..domain.model.constraint import Constraint, ConstraintSet
from ..ports.secondary.persistence_port import PersistencePort


class CurriculumHandler:
    """Handles curriculum learning use cases."""
    
    def __init__(self, persistence: PersistencePort):
        self.persistence = persistence
        
        # Default curriculum stages
        self.stages = [
            CurriculumStage(
                stage_number=1,
                name="Basic",
                description="Basic constraints only",
                active_constraints=["basic"],
                difficulty_level=0.2
            ),
            CurriculumStage(
                stage_number=2,
                name="Intermediate",
                description="Add moderate constraints",
                active_constraints=["basic", "moderate"],
                difficulty_level=0.5
            ),
            CurriculumStage(
                stage_number=3,
                name="Advanced",
                description="All constraints active",
                active_constraints=["basic", "moderate", "advanced"],
                difficulty_level=0.8
            ),
        ]
        
        # Load or initialize progress
        self.progress: Optional[LearningProgress] = None
        self._load_progress()
    
    def _load_progress(self) -> None:
        """Load learning progress from persistence."""
        # Try to load from checkpoint
        # For now, initialize fresh
        if self.progress is None:
            self.progress = LearningProgress(current_stage=1)
    
    async def get_current_stage(self) -> int:
        """Get current curriculum stage number."""
        if self.progress is None:
            return 1
        return self.progress.current_stage
    
    async def get_stage_info(self) -> CurriculumStage:
        """Get current stage information."""
        stage_num = await self.get_current_stage()
        # Find stage or return first
        for stage in self.stages:
            if stage.stage_number == stage_num:
                return stage
        return self.stages[0]
    
    async def evaluate_progression(self,
                                   accuracy: float,
                                   solve_time: float) -> str:
        """
        Evaluate learning progress and potentially advance stage.
        
        Returns:
            Status message indicating action taken
        """
        if self.progress is None:
            self.progress = LearningProgress(current_stage=1)
        
        # Add result
        self.progress.add_result(accuracy, solve_time)
        
        # Check if should advance
        current_stage_num = self.progress.current_stage
        max_stage = len(self.stages)
        
        if current_stage_num < max_stage:
            if self.progress.should_advance():
                # Advance to next stage
                self.progress.current_stage += 1
                await self._save_progress()
                return f"Advanced to stage {self.progress.current_stage}"
        
        await self._save_progress()
        return f"Remaining at stage {current_stage_num}"
    
    async def get_active_constraints(self) -> List[str]:
        """Get currently active constraint types for current stage."""
        stage = await self.get_stage_info()
        return stage.active_constraints
    
    async def reset_curriculum(self) -> None:
        """Reset curriculum to initial stage."""
        self.progress = LearningProgress(current_stage=1)
        await self._save_progress()
    
    async def _save_progress(self) -> None:
        """Save progress to persistence."""
        if self.progress:
            state = {
                'current_stage': self.progress.current_stage,
                'accuracy_history': self.progress.accuracy_history,
                'solve_time_history': self.progress.solve_time_history,
                'last_updated': self.progress.last_updated.isoformat()
            }
            await self.persistence.save_checkpoint(state)


