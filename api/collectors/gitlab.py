import os
import re
from typing import Dict, Any, Optional
import httpx


class GitLabCollector:
    """Collects repository context and merge requests from GitLab API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITLAB_TOKEN")
        self.headers = {}
        if self.token:
            self.headers["PRIVATE-TOKEN"] = self.token

    @staticmethod
    def parse_repo_url(url: str) -> Optional[str]:
        """Extracts project path or URL-encoded path from a GitLab URL."""
        match = re.search(r"gitlab\.com[/:]([\w.-]+/[\w.-]+?)(?:\.git|/)?$", url)
        if match:
            # GitLab requires URL-encoded project path, e.g. "group%2Fproject"
            return match.group(1).replace("/", "%2F")
        return None

    async def enrich_profile(self, repo_url: str) -> Dict[str, Any]:
        """Fetches repository context and MR activity from GitLab."""
        project_id = self.parse_repo_url(repo_url)
        if not project_id:
            return {"error": "Format d'URL GitLab invalide."}

        base_url = f"https://gitlab.com/api/v4/projects/{project_id}"
        enrichment: Dict[str, Any] = {
            "platform": "gitlab",
            "project_id": project_id,
            "context_files": {},
            "mrs": [],
            "is_accessible": False,
        }

        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            repo_res = await client.get(base_url)
            if repo_res.status_code != 200:
                return {
                    "error": f"Impossible d'accéder au projet GitLab ({repo_res.status_code}).",
                    "status_code": repo_res.status_code,
                }
            enrichment["is_accessible"] = True

            # Check tree for AGENTS.md, etc.
            tree_res = await client.get(f"{base_url}/repository/tree")
            if tree_res.status_code == 200:
                for item in tree_res.json():
                    name = item.get("name", "")
                    if name in ["AGENTS.md", "CLAUDE.md", ".cursorrules"]:
                        enrichment["context_files"][name] = item.get("path")

        return enrichment
