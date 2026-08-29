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


class ContributorMetrics(BaseModel):
    author: str
    email: Optional[str] = None
    total_commits: int
    ai_coauthored_commits: int
    ai_coauthored_ratio: float
    estimated_level: AIDDLevel
    sample_messages: List[str] = Field(default_factory=list)


class TeamEvaluationResult(BaseModel):
    team_name: str = "Équipe Technique"
    team_size: int
    average_rank: float
    average_level_label: str
    level_distribution: Dict[str, int]
    members: List[EvaluationResult]
    team_bottleneck_axis: str
    team_recommendations: List[str] = Field(default_factory=list)
    contributors_breakdown: Optional[List[ContributorMetrics]] = None


class EvaluationRequest(BaseModel):
    profile_path: Optional[str] = None
    repo_url: Optional[str] = None


class TeamEvaluationRequest(BaseModel):
    profile_paths: Optional[List[str]] = None
    team_directory: Optional[str] = None
    repo_url: Optional[str] = None
