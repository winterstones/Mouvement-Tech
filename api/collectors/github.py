import os
import re
from typing import Dict, Any, Optional
import httpx


class GitHubCollector:
    """Collects repository context, pull requests, and activity metrics from GitHub API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    @staticmethod
    def parse_repo_url(url: str) -> Optional[tuple[str, str]]:
        """Extracts (owner, repo) from a GitHub URL."""
        match = re.search(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git|/)?$", url)
        if match:
            return match.group(1), match.group(2)
        return None

    async def enrich_profile(self, repo_url: str) -> Dict[str, Any]:
        """Fetches repository context and PR activity from GitHub."""
        parsed = self.parse_repo_url(repo_url)
        if not parsed:
            return {"error": "Format d'URL GitHub invalide."}

        owner, repo = parsed
        base_url = f"https://api.github.com/repos/{owner}/{repo}"

        enrichment: Dict[str, Any] = {
            "platform": "github",
            "repo": f"{owner}/{repo}",
            "context_files": {},
            "prs": [],
            "workflows": [],
            "is_accessible": False,
        }

        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            # 1. Test repository accessibility
            repo_res = await client.get(base_url)
            if repo_res.status_code != 200:
                return {
                    "error": f"Impossible d'accéder au dépôt ({repo_res.status_code}). Vérifiez la visibilité ou GITHUB_TOKEN.",
                    "status_code": repo_res.status_code,
                }
            enrichment["is_accessible"] = True

            # 2. Check root context files (AGENTS.md, CLAUDE.md, .cursorrules)
            contents_res = await client.get(f"{base_url}/contents")
            if contents_res.status_code == 200:
                root_files = contents_res.json()
                for item in root_files:
                    name = item.get("name", "")
                    if name in ["AGENTS.md", "CLAUDE.md", ".cursorrules", "PROMPT.md"]:
                        enrichment["context_files"][name] = item.get("download_url")

            # 3. Check GitHub Actions workflows for automated loops or agents
            workflows_res = await client.get(f"{base_url}/contents/.github/workflows")
            if workflows_res.status_code == 200:
                wf_files = workflows_res.json()
                for wf in wf_files:
                    enrichment["workflows"].append(wf.get("name", ""))

            # 4. Fetch recent closed PRs
            pulls_res = await client.get(f"{base_url}/pulls?state=closed&per_page=30")
            if pulls_res.status_code == 200:
                prs_data = pulls_res.json()
                for pr in prs_data:
                    enrichment["prs"].append({
                        "number": pr.get("number"),
                        "title": pr.get("title"),
                        "created_at": pr.get("created_at"),
                        "merged_at": pr.get("merged_at"),
                        "user": pr.get("user", {}).get("login"),
                    })

        return enrichment
