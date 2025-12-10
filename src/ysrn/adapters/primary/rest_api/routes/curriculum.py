"""Curriculum endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from ysrn.application.curriculum_handler import CurriculumHandler


router = APIRouter(prefix="/api/v1/curriculum", tags=["curriculum"])


# Request/Response Models
class EvaluateProgressionRequest(BaseModel):
    """Request to evaluate curriculum progression."""
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Accuracy score (0.0 to 1.0)")
    solve_time: float = Field(..., ge=0.0, description="Solve time in seconds")


class StageResponse(BaseModel):
    """Current stage information."""
    stage_number: int
    name: str
    description: str
    active_constraints: List[str]
    difficulty_level: float


class ProgressionResponse(BaseModel):
    """Progression evaluation response."""
    message: str
    current_stage: int
    should_advance: bool


def get_curriculum_handler() -> CurriculumHandler:
    """Dependency to get curriculum handler."""
    from ..app import get_curriculum_handler as _get_handler
    return _get_handler()


@router.get("/stage", response_model=StageResponse)
async def get_current_stage(
    handler: CurriculumHandler = Depends(get_curriculum_handler)
):
    """
    Get current curriculum stage information.
    """
    try:
        stage = await handler.get_stage_info()
        return StageResponse(
            stage_number=stage.stage_number,
            name=stage.name,
            description=stage.description,
            active_constraints=stage.active_constraints,
            difficulty_level=stage.difficulty_level
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stage: {str(e)}"
        )


@router.post("/evaluate", response_model=ProgressionResponse)
async def evaluate_progression(
    request: EvaluateProgressionRequest,
    handler: CurriculumHandler = Depends(get_curriculum_handler)
):
    """
    Evaluate learning progress and potentially advance curriculum stage.
    """
    try:
        message = await handler.evaluate_progression(
            accuracy=request.accuracy,
            solve_time=request.solve_time
        )
        
        current_stage = await handler.get_current_stage()
        should_advance = "Advanced" in message
        
        return ProgressionResponse(
            message=message,
            current_stage=current_stage,
            should_advance=should_advance
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate progression: {str(e)}"
        )


@router.get("/constraints", response_model=List[str])
async def get_active_constraints(
    handler: CurriculumHandler = Depends(get_curriculum_handler)
):
    """
    Get currently active constraint types for the current stage.
    """
    try:
        constraints = await handler.get_active_constraints()
        return constraints
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get constraints: {str(e)}"
        )


@router.post("/reset")
async def reset_curriculum(
    handler: CurriculumHandler = Depends(get_curriculum_handler)
):
    """
    Reset curriculum to initial stage.
    """
    try:
        await handler.reset_curriculum()
        return {"message": "Curriculum reset to stage 1"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset curriculum: {str(e)}"
        )

