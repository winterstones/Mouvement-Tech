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


class ActionTicket(BaseModel):
    ticket_id: str
    title: str
    axis: str
    priority: str = "High"  # Critical, High, Medium, Low
    estimated_effort: str = "1 jour"
    target_level: str
    definition_of_done: str
    status: str = "To Do"  # To Do, In Progress, Done


class VibeRiskMetrics(BaseModel):
    risk_score: int  # 0 to 100
    risk_level: str  # Faible, Modéré, Élevé, Critique
    rework_ratio: float  # e.g., 0.65
    context_coverage_detected: bool
    explanation: str


class ProgressionPlan(BaseModel):
    next_level: Optional[AIDDLevel] = None
    limiting_axis: str
    steps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    action_tickets: List[ActionTicket] = Field(default_factory=list)


class EvolutionPoint(BaseModel):
    timestamp: str  # e.g., "2026-06", "Sprint 38", "Mois M-2"
    sprint_label: str
    level_rank: int
    level_label: str
    ai_ratio: float
    corrective_rate: float
    summary: Optional[str] = None


class DeveloperEvolution(BaseModel):
    developer_id: str
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    starting_level_label: str
    current_level_label: str
    velocity_increase_percent: int
    progression_trend: str  # e.g. "Accélération soutenue", "Transition vers Green", "Stabilisation"
    history: List[EvolutionPoint] = Field(default_factory=list)


class CodeHealthMetrics(BaseModel):
    maintainability_score: int = 80  # 0 to 100
    archetype: str = "CLEAN_CRAFT_NO_AI"  # "CLEAN_CRAFT_NO_AI", "LEGACY_MANUAL_DEBT", "VIBE_CODING_DEBT", "CERTIFIED_AIDD"
    archetype_label: str = "Artisanat Sain (Non-IA)"
    archetype_badge_color: str = "bg-blue-50 text-blue-700 border-blue-200"
    technical_debt_index: int = 15  # 0 (clean) to 100 (extreme technical debt)
    spaghetti_index: Optional[int] = 15  # Backwards compatibility alias
    god_functions_count: int = 0
    test_coverage_density: float = 8.5
    duplication_ratio: float = 0.04
    explanation: str = "Code propre avec architecture modulaire."
    actionable_remediation: str = "Maintenir les bonnes pratiques."


class EvaluationResult(BaseModel):
    profile_id: str
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    stack: List[str] = Field(default_factory=list)
    level: AIDDLevel
    axes: AxesScores
    limiting_axis: str
    confident: bool = True
    warnings: List[str] = Field(default_factory=list)
    progression: ProgressionPlan
    vibe_risk: Optional[VibeRiskMetrics] = None
    code_health: Optional[CodeHealthMetrics] = None
    evolution_history: Optional[List[EvolutionPoint]] = None
    data_sources: List[str] = Field(default_factory=list)
    audited_repos: Optional[List[Dict[str, Any]]] = None


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
    team_vibe_risk_avg: int = 0
    team_maintainability_avg: int = 85
    team_technical_debt_avg: int = 15
    team_spaghetti_avg: Optional[int] = 15
    team_action_backlog: List[ActionTicket] = Field(default_factory=list)
    evolution_timeline: Optional[List[DeveloperEvolution]] = None
    contributors_breakdown: Optional[List[ContributorMetrics]] = None


class EvaluationRequest(BaseModel):
    profile_path: Optional[str] = None
    repo_url: Optional[str] = None


class TeamEvaluationRequest(BaseModel):
    profile_paths: Optional[List[str]] = None
    team_directory: Optional[str] = None
    repo_url: Optional[str] = None
