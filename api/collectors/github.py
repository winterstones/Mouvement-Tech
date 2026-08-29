import os
import re
from typing import Dict, Any, Optional, List
import statistics
import httpx


class GitHubCollector:
    """Collects repository context, pull requests, and activity metrics from GitHub API to build full profile evaluations."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Mouvement-Tech-AIDD-Engine"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    @staticmethod
    def parse_repo_url(url: str) -> Optional[tuple[str, str]]:
        """Extracts (owner, repo) from a GitHub URL."""
        clean_url = url.strip().rstrip("/")
        match = re.search(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?$", clean_url)
        if match:
            return match.group(1), match.group(2)
        return None

    async def enrich_profile(self, repo_url: str) -> Dict[str, Any]:
        """Fetches repository context, metadata, and activity from GitHub to enrich an existing profile."""
        parsed = self.parse_repo_url(repo_url)
        if not parsed:
            return {
                "platform": "github",
                "error": f"Format d'URL GitHub invalide : {repo_url}",
                "is_accessible": False,
            }

        owner, repo = parsed
        base_url = f"https://api.github.com/repos/{owner}/{repo}"

        enrichment: Dict[str, Any] = {
            "platform": "github",
            "owner": owner,
            "repo": repo,
            "is_accessible": False,
            "context_files": {},
            "pull_requests_count": 0,
            "has_workflows": False,
        }

        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            repo_res = await client.get(base_url)
            if repo_res.status_code != 200:
                msg = f"Impossible d'accéder au dépôt GitHub '{owner}/{repo}' (HTTP {repo_res.status_code})."
                if repo_res.status_code == 404:
                    msg += " Le dépôt est introuvable ou privé."
                elif repo_res.status_code == 403:
                    msg += " Limite de requêtes GitHub atteinte. Configurez un GITHUB_TOKEN."
                enrichment["error"] = msg
                return enrichment

            enrichment["is_accessible"] = True
            repo_meta = repo_res.json()
            enrichment["description"] = repo_meta.get("description") or ""
            enrichment["language"] = repo_meta.get("language") or "Code"
            enrichment["default_branch"] = repo_meta.get("default_branch", "main")
            enrichment["stars"] = repo_meta.get("stargazers_count", 0)

            # Check Root Files & Context Files
            contents_res = await client.get(f"{base_url}/contents")
            if contents_res.status_code == 200:
                root_files = contents_res.json()
                for item in root_files:
                    name = item.get("name", "")
                    if name.upper() in ["AGENTS.MD", "CLAUDE.MD", ".CURSORRULES", "PROMPT.MD"]:
                        download_url = item.get("download_url")
                        if download_url:
                            try:
                                f_res = await client.get(download_url)
                                if f_res.status_code == 200:
                                    enrichment["context_files"][name] = f_res.text[:3000]
                            except Exception:
                                enrichment["context_files"][name] = "Content available"

            # Check PRs
            pulls_res = await client.get(f"{base_url}/pulls?state=closed&per_page=10")
            if pulls_res.status_code == 200:
                enrichment["pull_requests_count"] = len(pulls_res.json())

            # Check Workflows
            wf_res = await client.get(f"{base_url}/contents/.github/workflows")
            enrichment["has_workflows"] = (wf_res.status_code == 200 and len(wf_res.json()) > 0)

        return enrichment

    async def fetch_full_profile_from_repo(self, repo_url: str) -> Dict[str, Any]:
        """Queries GitHub API to synthesize a complete profile_data dict for direct scoring."""
        parsed = self.parse_repo_url(repo_url)
        if not parsed:
            raise ValueError(f"Format d'URL GitHub invalide : {repo_url}")

        owner, repo = parsed
        base_url = f"https://api.github.com/repos/{owner}/{repo}"

        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            # 1. Fetch Repository Metadata
            repo_res = await client.get(base_url)
            if repo_res.status_code != 200:
                msg = f"Impossible d'accéder au dépôt GitHub '{owner}/{repo}' (HTTP {repo_res.status_code})."
                if repo_res.status_code == 404:
                    msg += " Le dépôt est introuvable ou privé."
                elif repo_res.status_code == 403:
                    msg += " Limite de requêtes GitHub atteinte. Configurez un GITHUB_TOKEN."
                raise ValueError(msg)

            repo_meta = repo_res.json()
            main_language = repo_meta.get("language") or "Code"
            description = repo_meta.get("description") or ""

            # 2. Check Root Files & Context Files (AGENTS.md, CLAUDE.md, .cursorrules, .worktreeinclude, etc.)
            contents_res = await client.get(f"{base_url}/contents")
            root_files = contents_res.json() if contents_res.status_code == 200 else []

            repo_context_files: Dict[str, str] = {}
            agents_md = False
            rules_count = 0
            skills_count = 0
            hooks_count = 0
            agents_count = 0
            has_auto_loops = False
            last_updated = None

            for item in root_files:
                name = item.get("name", "")
                if name.upper() in ["AGENTS.MD", "CLAUDE.MD", ".CURSORRULES", "PROMPT.MD", ".WORKTREEINCLUDE"]:
                    agents_md = True
                    download_url = item.get("download_url")
                    if download_url:
                        try:
                            f_res = await client.get(download_url)
                            if f_res.status_code == 200:
                                repo_context_files[name] = f_res.text[:3000]
                        except Exception:
                            repo_context_files[name] = "Content available"

                if name.upper() == ".CURSORRULES":
                    rules_count += 2
                if name.upper() == ".WORKTREEINCLUDE":
                    skills_count += 1

                if name in [".cursor", ".claude"]:
                    sub_res = await client.get(f"{base_url}/contents/{name}")
                    if sub_res.status_code == 200:
                        sub_items = [si.get("name") for si in sub_res.json()]
                        if "skills" in sub_items:
                            skills_count += 3
                        if "rules" in sub_items:
                            rules_count += 3
                        if "agents" in sub_items:
                            agents_count += 2

                if name == "scripts":
                    sub_res = await client.get(f"{base_url}/contents/{name}")
                    if sub_res.status_code == 200:
                        sub_items = [si.get("name") for si in sub_res.json()]
                        if any("loop" in s.lower() or "fix" in s.lower() for s in sub_items):
                            has_auto_loops = True
                            hooks_count += 2
                        if any("worktree" in s.lower() for s in sub_items):
                            skills_count += 2

                if name == "docs":
                    sub_res = await client.get(f"{base_url}/contents/{name}")
                    if sub_res.status_code == 200:
                        sub_items = [si.get("name") for si in sub_res.json()]
                        if "knowledge" in sub_items or "context" in sub_items or "specs" in sub_items:
                            rules_count += 2

            # 3. Pull Requests analysis
            pulls_res = await client.get(f"{base_url}/pulls?state=closed&per_page=30")
            prs_data = pulls_res.json() if pulls_res.status_code == 200 else []

            size_dist = {"xs": 0, "s": 0, "m": 0, "l": 0, "xl": 0}
            lines_changed_list = []
            correction_commits_list = []
            merged_without_human_edit = 0

            # Sample the most recent closed PRs
            for pr in prs_data[:15]:
                pr_num = pr.get("number")
                pr_detail_res = await client.get(f"{base_url}/pulls/{pr_num}")
                if pr_detail_res.status_code == 200:
                    pr_detail = pr_detail_res.json()
                    additions = pr_detail.get("additions", 0)
                    deletions = pr_detail.get("deletions", 0)
                    total_lines = additions + deletions
                    lines_changed_list.append(total_lines)

                    commits_cnt = pr_detail.get("commits", 1)
                    corrections = max(0, commits_cnt - 1)
                    correction_commits_list.append(corrections)
                    if commits_cnt == 1:
                        merged_without_human_edit += 1

                    if total_lines < 30:
                        size_dist["xs"] += 1
                    elif total_lines < 150:
                        size_dist["s"] += 1
                    elif total_lines < 500:
                        size_dist["m"] += 1
                    elif total_lines < 1200:
                        size_dist["l"] += 1
                    else:
                        size_dist["xl"] += 1

            # 4. Fetch commits
            commits_res = await client.get(f"{base_url}/commits?per_page=30")
            commits_data = commits_res.json() if commits_res.status_code == 200 else []

            # If no or few PRs (direct branch work), sample commit sizes
            if len(lines_changed_list) < 2 and len(commits_data) > 0:
                for c in commits_data[:10]:
                    sha = c.get("sha")
                    c_detail_res = await client.get(f"{base_url}/commits/{sha}")
                    if c_detail_res.status_code == 200:
                        c_detail = c_detail_res.json()
                        stats = c_detail.get("stats", {})
                        c_lines = stats.get("total", 0)
                        if c_lines > 0:
                            lines_changed_list.append(c_lines)
                            if c_lines < 30:
                                size_dist["xs"] += 1
                            elif c_lines < 150:
                                size_dist["s"] += 1
                            elif c_lines < 500:
                                size_dist["m"] += 1
                            elif c_lines < 1200:
                                size_dist["l"] += 1
                            else:
                                size_dist["xl"] += 1

                fix_commits = sum(1 for c in commits_data if any(kw in c.get("commit", {}).get("message", "").lower() for kw in ["fix", "corr", "bug", "patch"]))
                median_corrections = 0 if fix_commits <= 1 else 1
                merged_without_human_edit = len(lines_changed_list)
            else:
                median_corrections = statistics.median(correction_commits_list) if correction_commits_list else 1

            total_prs = max(1, len(lines_changed_list))
            median_lines = statistics.median(lines_changed_list) if lines_changed_list else 150

            # 5. Check Parallelism (Branches)
            branches_res = await client.get(f"{base_url}/branches?per_page=30")
            branches = branches_res.json() if branches_res.status_code == 200 else []
            active_branches_count = max(1, len(branches))

            # 6. Check AI Co-authorship in recent commits
            ai_commits_count = 0
            for c in commits_data:
                msg = c.get("commit", {}).get("message", "")
                if any(x in msg.lower() for x in ["co-authored-by: claude", "co-authored-by: antigravity", "co-authored-by: copilot", "co-authored-by: ai"]):
                    ai_commits_count += 1

            ai_ratio = round(ai_commits_count / len(commits_data), 2) if commits_data else 0.0

            # 7. Check GitHub Actions Workflows
            wf_res = await client.get(f"{base_url}/contents/.github/workflows")
            has_workflows = wf_res.status_code == 200 and len(wf_res.json()) > 0
            if has_workflows:
                has_auto_loops = True
                hooks_count += 2

            # Synthesize git_activity
            git_activity = {
                "pull_requests": {
                    "total": total_prs,
                    "size_distribution": size_dist,
                    "median_lines_changed": int(median_lines),
                    "median_correction_commits_after_open": int(median_corrections),
                    "merged_without_human_edit_after_open": merged_without_human_edit,
                    "reverted": 0,
                },
                "commits": {
                    "total": len(commits_data),
                    "ai_coauthored_ratio": ai_ratio,
                },
                "context_files": {
                    "agents_md": agents_md,
                    "rules_count": rules_count,
                    "skills_count": skills_count,
                    "hooks_count": hooks_count,
                    "agents_count": agents_count,
                    "has_auto_loops": has_auto_loops,
                    "last_updated": last_updated,
                },
                "parallelism": {
                    "max_concurrent_branches": active_branches_count,
                    "median_concurrent_branches": min(3, max(1, active_branches_count // 2)) if active_branches_count >= 3 else 1,
                },
                "ci": {
                    "failure_rate": 0.05 if has_workflows else 0.15,
                },
                "assistant_usage": {
                    "declared_tools": ["github-ai-integration"] if agents_md else [],
                    "sessions_per_week": 10 if agents_md else 2,
                }
            }

            profile_info = {
                "profile_id": f"{owner}/{repo}",
                "role": f"Dépôt GitHub ({owner}/{repo})",
                "stack": [main_language] + ([description] if description else []),
                "experience_years": 5,
                "team_size": 1,
            }

            return {
                "profile_id": f"{owner}/{repo}",
                "profile_info": profile_info,
                "git_activity": git_activity,
                "repo_context_files": repo_context_files,
                "declaratif": f"Dépôt GitHub public {owner}/{repo}. Description: {description}",
                "session": None,
                "available_sources": ["github-api-live", "github-contents", "github-pulls", "github-commits"],
            }
