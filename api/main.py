import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.models import (
    EvaluationRequest,
    EvaluationResult,
    TeamEvaluationRequest,
    TeamEvaluationResult,
    ContributorMetrics,
    AIDDLevel,
)
from api.collectors.profile import ProfileCollector, MissingMandatoryProfileDataError
from api.collectors.github import GitHubCollector
from api.collectors.gitlab import GitLabCollector
from api.scorer.algo import QuantitativeScorer
from api.scorer.llm import LLMQualitativeJudge
from api.scorer.fusion import EvaluationEngine
from api.scorer.team import TeamEngine
from api.scorer.thresholds import LEVELS, AXES_CRITERIA

load_dotenv()

app = FastAPI(
    title="Mouvement-Tech — Moteur d'évaluation AIDD",
    description="API REST d'analyse et de positionnement individuel et d'équipe sur le référentiel AI-Driven Development (AIDD).",
    version="1.0.0",
)

# Enable CORS for local web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Reference profiles path
BASE_DIR = Path(__file__).resolve().parent.parent
SUJET_PROFILES_DIR = BASE_DIR.parent / "laivel-up-sujet" / "profiles"


@app.get("/")
async def root():
    return {
        "app": "Mouvement-Tech",
        "description": "Moteur d'évaluation AIDD (AI-Driven Development) Individuel & Équipe",
        "version": "1.0.0",
        "endpoints": {
            "evaluate_custom": "POST /evaluate (avec profile_path et/ou repo_url)",
            "evaluate_repo_live": "GET /evaluate/live?repo_url=https://github.com/...",
            "evaluate_reference": "GET /evaluate/{profile_id} (ex: perceval, bohort, leodagan, arthur)",
            "team_dashboard": "GET /team (évalue toute l'équipe pour le CTO)",
            "team_contributors": "GET /team/contributors?repo_url=https://github.com/...",
            "levels_grid": "GET /levels",
            "docs": "/docs",
        },
    }


@app.get("/levels")
async def get_levels():
    """Returns the official AIDD levels and axes criteria."""
    return {
        "levels": list(LEVELS.values()),
        "criteria": AXES_CRITERIA,
    }


@app.get("/team", response_model=TeamEvaluationResult)
async def evaluate_reference_team(
    repo_url: Optional[str] = Query(None, description="URL d'un dépôt GitHub partagé pour extraire l'équipe réelle"),
):
    """Evaluates all developers of a project or the benchmark reference team, returning a complete CTO Team Report."""
    if repo_url and "github.com" in repo_url:
        gh = GitHubCollector()
        try:
            members_results = await gh.fetch_team_from_repo(repo_url)
            contributors = await gh.analyze_repo_contributors(repo_url)
            parsed = gh.parse_repo_url(repo_url)
            team_title = f"Équipe Projet ({parsed[0]}/{parsed[1]})" if parsed else "Équipe Projet"
            return TeamEngine.evaluate_team(
                members=members_results,
                team_name=team_title,
                contributors_breakdown=contributors,
            )
        except Exception as e:
            # If repo fails (e.g. rate limit), fallback gracefully
            pass

    member_ids = ["perceval", "bohort", "leodagan", "arthur"]
    members_results: List[EvaluationResult] = []

    for mid in member_ids:
        path = SUJET_PROFILES_DIR / mid
        if path.exists() and path.is_dir():
            res = await _run_evaluation(path)
            members_results.append(res)

    return TeamEngine.evaluate_team(
        members=members_results,
        team_name="Équipe Démonstration (4 Profils)",
        contributors_breakdown=None,
    )


@app.get("/team/contributors", response_model=List[ContributorMetrics])
async def analyze_repo_contributors(
    repo_url: str = Query(..., description="URL GitHub du dépôt à analyser"),
):
    """Analyzes all individual developers contributing to a GitHub repository and computes their AI co-authorship ratio."""
    if "github.com" not in repo_url:
        raise HTTPException(
            status_code=400,
            detail="Seuls les dépôts GitHub sont pris en charge pour l'analyse des contributeurs.",
        )
    gh = GitHubCollector()
    return await gh.analyze_repo_contributors(repo_url)


@app.get("/evaluate/developer", response_model=EvaluationResult)
async def evaluate_developer_profile(
    username: str = Query(..., description="Nom d'utilisateur ou URL de profil GitHub (ex: 'torvalds' ou 'https://github.com/username')"),
):
    """Audits a developer's cross-repository GitHub activity, measuring AI co-authorship and AIDD maturity level."""
    try:
        gh = GitHubCollector()
        return await gh.fetch_developer_profile(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du développeur : {str(e)}")


@app.get("/evaluate/live", response_model=EvaluationResult)
async def evaluate_live_repo(
    repo_url: str = Query(..., description="URL publique d'un dépôt GitHub à évaluer en direct"),
):
    """Evaluates a live public GitHub repository directly from GitHub API."""
    if "github.com" not in repo_url:
        raise HTTPException(
            status_code=400,
            detail="Seuls les dépôts GitHub (https://github.com/owner/repo) sont pris en charge pour l'évaluation en direct.",
        )

    try:
        gh = GitHubCollector()
        profile_data = await gh.fetch_full_profile_from_repo(repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse GitHub : {str(e)}")

    quantitative_scores = QuantitativeScorer.score_all(profile_data)
    llm_judge = LLMQualitativeJudge()
    llm_insights = await llm_judge.analyze(profile_data)
    result = EvaluationEngine.evaluate(profile_data, quantitative_scores, llm_insights)
    return result


@app.get("/evaluate/{profile_id}", response_model=EvaluationResult)
async def evaluate_reference_profile(
    profile_id: str,
    repo_url: Optional[str] = Query(None, description="URL GitHub ou GitLab optionnelle pour enrichissement"),
):
    """Evaluates a reference profile by its ID (perceval, bohort, leodagan, arthur)."""
    profile_path = SUJET_PROFILES_DIR / profile_id
    if not profile_path.exists() or not profile_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail=f"Profil de référence '{profile_id}' introuvable. Disponibles : perceval, bohort, leodagan, arthur.",
        )

    return await _run_evaluation(profile_path, repo_url)


@app.post("/evaluate", response_model=EvaluationResult)
async def evaluate_profile(request: EvaluationRequest):
    """Evaluates a profile given its local folder path and/or public repository URL."""
    if not request.profile_path and not request.repo_url:
        raise HTTPException(
            status_code=400,
            detail="Au moins un paramètre ('profile_path' ou 'repo_url') est requis pour lancer une évaluation.",
        )

    if request.repo_url and not request.profile_path:
        return await evaluate_live_repo(request.repo_url)

    profile_path = Path(request.profile_path)
    if not profile_path.exists() or not profile_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail=f"Dossier de profil introuvable : {request.profile_path}",
        )

    return await _run_evaluation(profile_path, request.repo_url)


async def _run_evaluation(profile_path: Path, repo_url: Optional[str] = None) -> EvaluationResult:
    try:
        # 1. Load profile data
        profile_data = ProfileCollector.load_profile(profile_path)
    except MissingMandatoryProfileDataError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture du profil : {str(e)}")

    # 2. Optional online repository enrichment
    if repo_url:
        if "github.com" in repo_url:
            gh = GitHubCollector()
            enrichment = await gh.enrich_profile(repo_url)
            profile_data["github_enrichment"] = enrichment
            profile_data["available_sources"].append("github-api")
        elif "gitlab.com" in repo_url:
            gl = GitLabCollector()
            enrichment = await gl.enrich_profile(repo_url)
            profile_data["gitlab_enrichment"] = enrichment
            profile_data["available_sources"].append("gitlab-api")

    # 3. Compute quantitative axis scores
    quantitative_scores = QuantitativeScorer.score_all(profile_data)

    # 4. Optional qualitative textual analysis (Gemini / Heuristic)
    llm_judge = LLMQualitativeJudge()
    llm_insights = await llm_judge.analyze(profile_data)

    # 5. Consolidation and progression plan
    result = EvaluationEngine.evaluate(profile_data, quantitative_scores, llm_insights)
    return result
