from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AIDDLevel(BaseModel):
    id: str
    label: str
    rank: int


class AxisScore(BaseModel):
    level: str
    rank: int
    confident: bool = True
    evidence: str
    details: Optional[Dict[str, Any]] = None


class AxesScores(BaseModel):
    taille: AxisScore
    harness: AxisScore
    intervention: AxisScore
    parallele: AxisScore


class ProgressionPlan(BaseModel):
    next_level: Optional[AIDDLevel] = None
    limiting_axis: str
    steps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    profile_id: str
    role: Optional[str] = None
    stack: List[str] = Field(default_factory=list)
    level: AIDDLevel
    axes: AxesScores
    limiting_axis: str
    confident: bool = True
    warnings: List[str] = Field(default_factory=list)
    progression: ProgressionPlan
    data_sources: List[str] = Field(default_factory=list)


class EvaluationRequest(BaseModel):
    profile_path: Optional[str] = None
    repo_url: Optional[str] = None
