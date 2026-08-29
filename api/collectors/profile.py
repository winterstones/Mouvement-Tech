import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class MissingMandatoryProfileDataError(ValueError):
    """Raised when mandatory files (profile.json or git-activity.json) are missing."""
    pass


class ProfileCollector:
    """Loads and normalizes profile data from a local directory."""

    @staticmethod
    def load_profile(profile_path: str | Path) -> Dict[str, Any]:
        path = Path(profile_path)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Le dossier de profil n'existe pas : {path}")

        profile_json_path = path / "profile.json"
        git_activity_path = path / "git-activity.json"

        if not profile_json_path.exists():
            raise MissingMandatoryProfileDataError(
                f"Fichier obligatoire manquant dans '{path.name}' : profile.json"
            )
        if not git_activity_path.exists():
            raise MissingMandatoryProfileDataError(
                f"Fichier obligatoire manquant dans '{path.name}' : git-activity.json"
            )

        with open(profile_json_path, "r", encoding="utf-8") as f:
            profile_info = json.load(f)

        with open(git_activity_path, "r", encoding="utf-8") as f:
            git_activity = json.load(f)

        profile_id = profile_info.get("profile_id", path.name)
        available_sources = ["profile.json", "git-activity.json"]

        pull_requests = None
        pr_path = path / "pull-requests.json"
        if pr_path.exists():
            with open(pr_path, "r", encoding="utf-8") as f:
                pull_requests = json.load(f)
            available_sources.append("pull-requests.json")

        sonar_measures = None
        sonar_path = path / "sonar-measures.json"
        if sonar_path.exists():
            with open(sonar_path, "r", encoding="utf-8") as f:
                sonar_measures = json.load(f)
            available_sources.append("sonar-measures.json")

        declaratif = None
        dec_path = path / "declaratif.md"
        if dec_path.exists():
            with open(dec_path, "r", encoding="utf-8") as f:
                declaratif = f.read()
            available_sources.append("declaratif.md")

        session = None
        sess_path = path / "session.md"
        if sess_path.exists():
            with open(sess_path, "r", encoding="utf-8") as f:
                session = f.read()
            available_sources.append("session.md")

        repo_context_files = {}
        repo_ctx_dir = path / "repo-context"
        if repo_ctx_dir.exists() and repo_ctx_dir.is_dir():
            available_sources.append("repo-context/")
            for root, _, files in os.walk(repo_ctx_dir):
                for file in files:
                    file_full_path = Path(root) / file
                    rel_path = file_full_path.relative_to(repo_ctx_dir).as_posix()
                    try:
                        with open(file_full_path, "r", encoding="utf-8") as f:
                            repo_context_files[rel_path] = f.read()
                    except Exception:
                        repo_context_files[rel_path] = "<binary or unreadable>"

        code_files = []
        code_dir = path / "code"
        if code_dir.exists() and code_dir.is_dir():
            available_sources.append("code/")
            for root, _, files in os.walk(code_dir):
                for file in files:
                    code_files.append((Path(root) / file).relative_to(code_dir).as_posix())

        return {
            "profile_id": profile_id,
            "profile_info": profile_info,
            "git_activity": git_activity,
            "pull_requests": pull_requests,
            "sonar_measures": sonar_measures,
            "declaratif": declaratif,
            "session": session,
            "repo_context_files": repo_context_files,
            "code_files": code_files,
            "available_sources": available_sources,
        }
