import os
import re
from typing import Dict, Any, Optional, List
import statistics
import httpx
from api.models import ContributorMetrics
from api.scorer.thresholds import RANK_TO_LEVEL


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

    @staticmethod
    def parse_username(url_or_name: str) -> str:
        """Extracts clean username from a GitHub URL or username string."""
        clean = url_or_name.strip().rstrip("/")
        match = re.search(r"github\.com[/:]([\w.-]+)$", clean)
        if match:
            return match.group(1)
        return clean.lstrip("@")

    async def fetch_developer_profile(self, username_or_url: str) -> Any:
        """Audits a developer's multi-project GitHub presence, scanning repositories and commits for AIDD maturity."""
        from api.scorer.algo import QuantitativeScorer
        from api.scorer.fusion import EvaluationEngine

        username = self.parse_username(username_or_url)
        base_url = f"https://api.github.com/users/{username}"

        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            user_res = await client.get(base_url)
            if user_res.status_code != 200:
                raise ValueError(f"Profil développeur GitHub '@{username}' introuvable (HTTP {user_res.status_code}).")

            user_meta = user_res.json()
            name = user_meta.get("name") or username
            bio = user_meta.get("bio") or ""

            # Fetch top recent repos
            repos_res = await client.get(f"{base_url}/repos?sort=pushed&per_page=6")
            repos_data = repos_res.json() if repos_res.status_code == 200 else []

            total_commits = 0
            ai_commits = 0
            languages = set()
            has_agents_md = False
            rules_count = 0
            skills_count = 0
            lines_changed_list = []
            size_dist = {"xs": 0, "s": 0, "m": 0, "l": 0, "xl": 0}

            for r in repos_data[:4]:
                r_name = r.get("name")
                r_owner = (r.get("owner") or {}).get("login") or username
                lang = r.get("language")
                if lang:
                    languages.add(lang)

                # Check root context files in repo
                c_res = await client.get(f"https://api.github.com/repos/{r_owner}/{r_name}/contents")
                if c_res.status_code == 200:
                    r_files = [item.get("name", "").upper() for item in c_res.json()]
                    if any(f in r_files for f in ["AGENTS.MD", "CLAUDE.MD", ".CURSORRULES", ".AIDER.CONF.YML"]):
                        has_agents_md = True
                        rules_count += 2
                        skills_count += 2

                # Check commits by author
                commits_res = await client.get(f"https://api.github.com/repos/{r_owner}/{r_name}/commits?author={username}&per_page=20")
                if commits_res.status_code == 200:
                    c_list = commits_res.json()
                    for c in c_list:
                        total_commits += 1
                        msg = c.get("commit", {}).get("message", "")
                        if any(x in msg.lower() for x in ["co-authored-by: claude", "co-authored-by: antigravity", "co-authored-by: copilot", "co-authored-by: ai"]):
                            ai_commits += 1

            ai_ratio = round(ai_commits / total_commits, 2) if total_commits > 0 else 0.0

            # Estimate PR & commit delivery size
            if ai_ratio >= 0.70:
                size_dist = {"xs": 0, "s": 1, "m": 3, "l": 4, "xl": 2}
                median_lines = 550
                median_corrections = 0
            elif ai_ratio >= 0.20:
                size_dist = {"xs": 1, "s": 3, "m": 4, "l": 2, "xl": 0}
                median_lines = 280
                median_corrections = 0
            elif ai_ratio > 0.0:
                size_dist = {"xs": 2, "s": 4, "m": 1, "l": 0, "xl": 0}
                median_lines = 80
                median_corrections = 1
            else:
                size_dist = {"xs": 4, "s": 3, "m": 0, "l": 0, "xl": 0}
                median_lines = 30
                median_corrections = 2

            concurrent_tracks = min(4, max(1, len(repos_data)))

            git_activity = {
                "pull_requests": {
                    "total": max(1, total_commits // 3),
                    "size_distribution": size_dist,
                    "median_lines_changed": median_lines,
                    "median_correction_commits_after_open": median_corrections,
                    "merged_without_human_edit_after_open": max(0, (total_commits // 3) - median_corrections),
                    "reverted": 0,
                },
                "commits": {
                    "total": max(total_commits, 1),
                    "ai_coauthored_ratio": ai_ratio,
                },
                "context_files": {
                    "agents_md": has_agents_md,
                    "rules_count": rules_count,
                    "skills_count": skills_count,
                    "hooks_count": 2 if has_agents_md else 0,
                    "agents_count": 2 if has_agents_md else 0,
                    "has_auto_loops": False,
                    "last_updated": None,
                },
                "parallelism": {
                    "max_concurrent_branches": concurrent_tracks,
                    "median_concurrent_branches": min(3, max(1, concurrent_tracks // 2)),
                },
                "ci": {
                    "failure_rate": 0.08 if has_agents_md else 0.15,
                },
                "assistant_usage": {
                    "declared_tools": ["github-developer-audit"] if has_agents_md else [],
                    "sessions_per_week": 8 if has_agents_md else 2,
                },
            }

            profile_data = {
                "profile_id": username,
                "profile_info": {
                    "role": f"Développeur GitHub ({name})",
                    "stack": list(languages) if languages else ["Polyvalent"],
                    "experience_years": 4,
                    "team_size": 1,
                },
                "git_activity": git_activity,
                "repo_context_files": {"AGENTS.md": "Available across repos"} if has_agents_md else {},
                "declaratif": f"Profil GitHub @{username}. {bio}. {len(repos_data)} dépôts analysés, {total_commits} commits ({int(ai_ratio*100)}% co-signés IA).",
                "session": None,
                "available_sources": ["github-api-developer", "github-multi-repos"],
            }

            scores = QuantitativeScorer.score_all(profile_data)
            return EvaluationEngine.evaluate(profile_data, scores)

    async def enrich_profile(self, repo_url: str) -> Dict[str, Any]:
        """Fetches repository context and PR activity from GitHub to enrich an existing profile."""
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
            repo_res = await client.get(base_url)
            if repo_res.status_code != 200:
                return {
                    "error": f"Impossible d'accéder au dépôt ({repo_res.status_code}).",
                    "status_code": repo_res.status_code,
                }
            enrichment["is_accessible"] = True

            contents_res = await client.get(f"{base_url}/contents")
            if contents_res.status_code == 200:
                root_files = contents_res.json()
                for item in root_files:
                    name = item.get("name", "")
                    if name.upper() in ["AGENTS.MD", "CLAUDE.MD", ".CURSORRULES", "PROMPT.MD"]:
                        enrichment["context_files"][name] = item.get("download_url")

        return enrichment

    async def analyze_repo_contributors(self, repo_url: str) -> List[ContributorMetrics]:
        """Analyzes individual developer contributions and calculates AI co-authorship ratios per contributor."""
        parsed = self.parse_repo_url(repo_url)
        if not parsed:
            return []

        owner, repo = parsed
        base_url = f"https://api.github.com/repos/{owner}/{repo}"

        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            commits_res = await client.get(f"{base_url}/commits?per_page=100")
            if commits_res.status_code != 200:
                return []

            commits_data = commits_res.json()
            authors_data: Dict[str, Dict[str, Any]] = {}

            for c in commits_data:
                author_login = (c.get("author") or {}).get("login")
                author_name = (c.get("commit", {}).get("author") or {}).get("name", "Anonyme")
                email = (c.get("commit", {}).get("author") or {}).get("email")
                key = author_login or author_name

                if key not in authors_data:
                    authors_data[key] = {
                        "author": key,
                        "email": email,
                        "total_commits": 0,
                        "ai_coauthored_commits": 0,
                        "sample_messages": [],
                    }

                msg = c.get("commit", {}).get("message", "")
                authors_data[key]["total_commits"] += 1
                if len(authors_data[key]["sample_messages"]) < 3:
                    authors_data[key]["sample_messages"].append(msg.split("\n")[0])

                if any(x in msg.lower() for x in ["co-authored-by: claude", "co-authored-by: antigravity", "co-authored-by: copilot", "co-authored-by: ai"]):
                    authors_data[key]["ai_coauthored_commits"] += 1

            results: List[ContributorMetrics] = []
            for k, val in authors_data.items():
                total = val["total_commits"]
                ai_cnt = val["ai_coauthored_commits"]
                ratio = round(ai_cnt / total, 2) if total > 0 else 0.0

                # Inferred level based on empirical AI collaboration
                if ratio >= 0.85:
                    est_level = RANK_TO_LEVEL[4]  # Copper / Green
                elif ratio >= 0.50:
                    est_level = RANK_TO_LEVEL[3]  # Green
                elif ratio >= 0.20:
                    est_level = RANK_TO_LEVEL[2]  # Blue
                elif ratio > 0.0:
                    est_level = RANK_TO_LEVEL[1]  # Red
                else:
                    est_level = RANK_TO_LEVEL[0]  # White

                results.append(
                    ContributorMetrics(
                        author=val["author"],
                        email=val["email"],
                        total_commits=total,
                        ai_coauthored_commits=ai_cnt,
                        ai_coauthored_ratio=ratio,
                        estimated_level=est_level,
                        sample_messages=val["sample_messages"],
                    )
                )

            # Sort by total commits descending
            results.sort(key=lambda x: x.total_commits, reverse=True)
            return results

    async def fetch_team_from_repo(self, repo_url: str) -> List[Any]:
        """Synthesizes a list of individual EvaluationResult objects for each real contributor of the project."""
        from api.scorer.algo import QuantitativeScorer
        from api.scorer.fusion import EvaluationEngine

        # 1. Base project profile (Harness, Parallelism, Context Files)
        project_profile = await self.fetch_full_profile_from_repo(repo_url)
        contributors = await self.analyze_repo_contributors(repo_url)

        if not contributors:
            # Fallback on the project as a single member
            scores = QuantitativeScorer.score_all(project_profile)
            return [EvaluationEngine.evaluate(project_profile, scores)]

        members: List[Any] = []
        for c in contributors:
            # Clone git_activity and customize for contributor
            dev_git_act = dict(project_profile.get("git_activity", {}))
            dev_git_act["commits"] = {
                "total": c.total_commits,
                "ai_coauthored_ratio": c.ai_coauthored_ratio,
            }

            dev_prs = dict(dev_git_act.get("pull_requests", {}))
            
            # Individualize size and corrections based on developer's empirical AI collaboration
            if c.ai_coauthored_ratio >= 0.80:  # Copper / Silver contributor
                dev_prs["size_distribution"] = {"xs": 0, "s": 1, "m": 3, "l": 4, "xl": 2}
                dev_prs["median_lines_changed"] = 650
                dev_prs["total"] = 10
                dev_prs["median_correction_commits_after_open"] = 0
                dev_prs["merged_without_human_edit_after_open"] = 10
            elif c.ai_coauthored_ratio >= 0.25:  # Green / Blue contributor (e.g. lead maintainer)
                dev_prs["size_distribution"] = {"xs": 1, "s": 2, "m": 4, "l": 3, "xl": 0}
                dev_prs["median_lines_changed"] = 320
                dev_prs["total"] = 10
                dev_prs["median_correction_commits_after_open"] = 0
                dev_prs["merged_without_human_edit_after_open"] = 9
            elif c.ai_coauthored_ratio > 0.0:  # Red contributor
                dev_prs["size_distribution"] = {"xs": 2, "s": 4, "m": 1, "l": 0, "xl": 0}
                dev_prs["median_lines_changed"] = 60
                dev_prs["total"] = 7
                dev_prs["median_correction_commits_after_open"] = 1
                dev_prs["merged_without_human_edit_after_open"] = 5
            else:  # White contributor (0% AI detected)
                dev_prs["size_distribution"] = {"xs": 4, "s": 4, "m": 0, "l": 0, "xl": 0}
                dev_prs["median_lines_changed"] = 25
                dev_prs["total"] = 8
                dev_prs["median_correction_commits_after_open"] = 2
                dev_prs["merged_without_human_edit_after_open"] = 3

            dev_git_act["pull_requests"] = dev_prs

            # Individualize context & assistant usage
            dev_context = dict(dev_git_act.get("context_files", {}))
            if c.ai_coauthored_ratio == 0.0:
                dev_context = {
                    "agents_md": False,
                    "rules_count": 0,
                    "skills_count": 0,
                    "hooks_count": 0,
                    "agents_count": 0,
                    "has_auto_loops": False,
                    "last_updated": None,
                }
                dev_git_act["assistant_usage"] = {"declared_tools": [], "sessions_per_week": 0}
            dev_git_act["context_files"] = dev_context

            dev_profile_data = {
                "profile_id": c.author,
                "profile_info": {
                    "role": f"Contributeur ({project_profile['profile_id']})",
                    "stack": project_profile["profile_info"].get("stack", []),
                    "experience_years": 3,
                    "team_size": len(contributors),
                },
                "git_activity": dev_git_act,
                "repo_context_files": project_profile.get("repo_context_files", {}) if c.ai_coauthored_ratio > 0 else {},
                "declaratif": f"Contributeur du projet {project_profile['profile_id']} avec {c.total_commits} commits ({int(c.ai_coauthored_ratio*100)}% assistés par IA).",
                "session": None,
                "available_sources": ["github-api-contributor", "github-contents"],
            }

            scores = QuantitativeScorer.score_all(dev_profile_data)
            eval_res = EvaluationEngine.evaluate(dev_profile_data, scores)
            members.append(eval_res)

        return members

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

            # 2. Check Root Files & Context Files (AGENTS.md, CLAUDE.md, etc.)
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
                name_upper = name.upper()
                if name_upper in ["AGENTS.MD", "CLAUDE.MD", ".CURSORRULES", "PROMPT.MD", ".WORKTREEINCLUDE", "CONVENTIONS.MD", ".AIDER.CONF.YML"] or name.startswith(".aider"):
                    agents_md = True
                    download_url = item.get("download_url")
                    if download_url:
                        try:
                            f_res = await client.get(download_url)
                            if f_res.status_code == 200:
                                repo_context_files[name] = f_res.text[:3000]
                        except Exception:
                            repo_context_files[name] = "Content available"

                if name_upper == ".CURSORRULES" or name.startswith(".aider"):
                    rules_count += 2
                    skills_count += 2
                if name_upper == ".WORKTREEINCLUDE":
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

                if name in ["benchmark", "benchmarks"]:
                    has_auto_loops = True
                    hooks_count += 2
                    skills_count += 1

                if name == "scripts":
                    sub_res = await client.get(f"{base_url}/contents/{name}")
                    if sub_res.status_code == 200:
                        sub_items = [si.get("name") for si in sub_res.json()]
                        if any("loop" in s.lower() or "fix" in s.lower() for s in sub_items):
                            has_auto_loops = True
                            hooks_count += 2
                        if any("worktree" in s.lower() for s in sub_items):
                            skills_count += 2

                if name in ["docs", "prompts", "queries"]:
                    sub_res = await client.get(f"{base_url}/contents/{name}")
                    if sub_res.status_code == 200:
                        sub_items = [si.get("name") for si in sub_res.json()]
                        if "knowledge" in sub_items or "context" in sub_items or "specs" in sub_items:
                            rules_count += 2
                        if any(s.endswith(".md") or s.endswith(".scm") or s.endswith(".txt") for s in sub_items):
                            skills_count += 1

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

            # 5. Check Parallelism (Branches & Active Tracks)
            branches_res = await client.get(f"{base_url}/branches?per_page=30")
            branches = branches_res.json() if branches_res.status_code == 200 else []
            active_branches_count = max(1, len(branches))

            # 6. Check AI Co-authorship in recent commits
            ai_commits_count = 0
            ai_sample_lines = []
            active_authors = set()
            for c in commits_data:
                msg = c.get("commit", {}).get("message", "")
                author_email = c.get("commit", {}).get("author", {}).get("email")
                if author_email:
                    active_authors.add(author_email)

                if any(x in msg.lower() for x in ["co-authored-by: claude", "co-authored-by: antigravity", "co-authored-by: copilot", "co-authored-by: ai"]):
                    ai_commits_count += 1
                    sha = c.get("sha")
                    if len(ai_sample_lines) < 6 and sha:
                        try:
                            c_detail_res = await client.get(f"{base_url}/commits/{sha}")
                            if c_detail_res.status_code == 200:
                                c_lines = c_detail_res.json().get("stats", {}).get("total", 0)
                                if c_lines > 0:
                                    ai_sample_lines.append(c_lines)
                        except Exception:
                            pass

            ai_ratio = round(ai_commits_count / len(commits_data), 2) if commits_data else 0.0

            # If substantial AI commits were found, incorporate them in delivery sizes
            if ai_sample_lines:
                for l_cnt in ai_sample_lines:
                    lines_changed_list.append(l_cnt)
                    if l_cnt < 30:
                        size_dist["xs"] += 1
                    elif l_cnt < 150:
                        size_dist["s"] += 1
                    elif l_cnt < 500:
                        size_dist["m"] += 1
                    elif l_cnt < 1200:
                        size_dist["l"] += 1
                    else:
                        size_dist["xl"] += 1
                median_lines = statistics.median(lines_changed_list)
                total_prs = len(lines_changed_list)

            # Reflect active parallel tracks if multiple concurrent active developers
            if len(active_authors) >= 5:
                active_branches_count = max(active_branches_count, min(6, len(active_authors) // 2 + 1))

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
