"""Audit and health check functionality for Phase 3."""

import re
from datetime import date, datetime
from pathlib import Path

from gtd_mcp.config import ConfigManager


class Auditor:
    """Audits execution system for data quality and health."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize auditor with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config

    def _parse_frontmatter(self, file_path: Path) -> dict:
        """Parse YAML frontmatter from file."""
        frontmatter = {}
        with open(file_path, 'r') as f:
            lines = f.readlines()

        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
                continue

            if in_frontmatter and ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def _validate_date_format(self, date_string: str) -> bool:
        """Validate date is in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def audit_projects(self) -> dict:
        """
        Audit all projects for YAML completeness and validity.

        Checks:
        - Required fields: area, title, type, created, last_reviewed
        - Area matches configured areas
        - Type is one of: standard, habit, coordination
        - All date fields are valid YYYY-MM-DD format

        Returns:
            Dict with structure:
            {
                "issues": [
                    {
                        "file": "path/to/project.md",
                        "missing_fields": ["last_reviewed"],
                        "invalid_fields": [
                            {"field": "area", "value": "X", "reason": "not in configured areas"}
                        ]
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        required_fields = ["area", "title", "type", "created", "last_reviewed"]
        date_fields = ["created", "last_reviewed", "started", "due", "completed", "descoped"]
        valid_types = ["standard", "habit", "coordination"]
        valid_areas = [a["name"].lower() for a in self._config.get_areas()]

        issues = []

        # Scan all project folders
        for folder in ["active", "incubator", "completed", "descoped"]:
            folder_path = projects_base / folder
            if not folder_path.exists():
                continue

            for area_dir in folder_path.iterdir():
                if not area_dir.is_dir():
                    continue

                for project_file in area_dir.glob("*.md"):
                    frontmatter = self._parse_frontmatter(project_file)

                    missing_fields = []
                    invalid_fields = []

                    # Check required fields
                    for field in required_fields:
                        if field not in frontmatter or not frontmatter[field]:
                            missing_fields.append(field)

                    # Validate area
                    if "area" in frontmatter:
                        if frontmatter["area"].lower() not in valid_areas:
                            invalid_fields.append({
                                "field": "area",
                                "value": frontmatter["area"],
                                "reason": f"not in configured areas: {', '.join([a['name'] for a in self._config.get_areas()])}"
                            })

                    # Validate type
                    if "type" in frontmatter:
                        if frontmatter["type"] not in valid_types:
                            invalid_fields.append({
                                "field": "type",
                                "value": frontmatter["type"],
                                "reason": f"must be one of: {', '.join(valid_types)}"
                            })

                    # Validate date formats
                    for date_field in date_fields:
                        if date_field in frontmatter and frontmatter[date_field]:
                            if not self._validate_date_format(frontmatter[date_field]):
                                invalid_fields.append({
                                    "field": date_field,
                                    "value": frontmatter[date_field],
                                    "reason": "invalid date format (must be YYYY-MM-DD)"
                                })

                    # Add issue if any problems found
                    if missing_fields or invalid_fields:
                        issues.append({
                            "file": str(project_file),
                            "missing_fields": missing_fields,
                            "invalid_fields": invalid_fields
                        })

        return {"issues": issues}

    def audit_orphan_projects(self) -> dict:
        """
        Find projects without any actions.

        Excludes habit and coordination type projects (they don't need actions).

        Returns:
            Dict with structure:
            {
                "orphan_projects": [
                    {
                        "title": "Project Name",
                        "folder": "active",
                        "area": "Health",
                        "filename": "project-name"
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

        # Collect all action project tags
        action_project_tags = set()

        # Scan context files
        contexts_dir = actions_base / "contexts"
        if contexts_dir.exists():
            for context_file in contexts_dir.glob("*.md"):
                with open(context_file, 'r') as f:
                    for line in f:
                        if line.strip().startswith("- [ ]"):
                            match = re.search(r'\+(\S+)', line)
                            if match:
                                action_project_tags.add(match.group(1))

        # Scan special state files
        for state_file in ["@waiting.md", "@deferred.md", "@incubating.md"]:
            state_path = actions_base / state_file
            if state_path.exists():
                with open(state_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith("- [ ]"):
                            match = re.search(r'\+(\S+)', line)
                            if match:
                                action_project_tags.add(match.group(1))

        # Find projects without actions
        orphan_projects = []

        for folder in ["active", "incubator"]:
            folder_path = projects_base / folder
            if not folder_path.exists():
                continue

            for area_dir in folder_path.iterdir():
                if not area_dir.is_dir():
                    continue

                for project_file in area_dir.glob("*.md"):
                    frontmatter = self._parse_frontmatter(project_file)

                    # Skip habits and coordination
                    project_type = frontmatter.get("type", "")
                    if project_type in ["habit", "coordination"]:
                        continue

                    # Check if project has actions
                    if project_file.stem not in action_project_tags:
                        orphan_projects.append({
                            "title": frontmatter.get("title", project_file.stem),
                            "folder": folder,
                            "area": frontmatter.get("area", ""),
                            "filename": project_file.stem
                        })

        return {"orphan_projects": orphan_projects}

    def audit_orphan_actions(self) -> dict:
        """
        Find actions with invalid project tags or contexts.

        Validates:
        - Project tags match existing project filenames
        - Contexts match existing context files

        Returns:
            Dict with structure:
            {
                "orphan_actions": [
                    {
                        "action_text": "Do something",
                        "project_tag": "nonexistent",
                        "file": "@macbook.md",
                        "line": "- [ ] 2025-10-30 Do something @macbook +nonexistent"
                    }
                ],
                "invalid_contexts": [
                    {
                        "action_text": "Do something",
                        "context": "@invalid",
                        "file": "@macbook.md",
                        "line": "..."
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

        # Collect all project filenames
        all_project_filenames = set()
        for folder in ["active", "incubator", "completed", "descoped"]:
            folder_path = projects_base / folder
            if not folder_path.exists():
                continue

            for area_dir in folder_path.iterdir():
                if not area_dir.is_dir():
                    continue

                for project_file in area_dir.glob("*.md"):
                    all_project_filenames.add(project_file.stem)

        # Collect all valid contexts
        valid_contexts = set()
        contexts_dir = actions_base / "contexts"
        if contexts_dir.exists():
            for context_file in contexts_dir.glob("*.md"):
                # Context files are named like @macbook.md, stem gives @macbook
                valid_contexts.add(context_file.stem)

        # Add special contexts
        for special in ["@waiting", "@deferred", "@incubating"]:
            special_path = actions_base / f"{special}.md"
            if special_path.exists():
                valid_contexts.add(special)

        # Scan actions for orphans
        orphan_actions = []
        invalid_contexts = []

        # Helper to process action file
        def process_action_file(file_path: Path):
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line.startswith("- [ ]"):
                        continue

                    # Extract project tag
                    project_match = re.search(r'\+(\S+)', line)
                    if project_match:
                        project_tag = project_match.group(1)
                        if project_tag not in all_project_filenames:
                            # Extract action text (simplified)
                            text_match = re.match(r'- \[ \] (?:\d{4}-\d{2}-\d{2} )?(.+?)(?:@|\+|due:|defer:|https?://|$)', line)
                            action_text = text_match.group(1).strip() if text_match else "..."

                            orphan_actions.append({
                                "action_text": action_text,
                                "project_tag": project_tag,
                                "file": file_path.name,
                                "line": line
                            })

                    # Extract context
                    context_match = re.search(r'@(\S+)', line)
                    if context_match:
                        context = f"@{context_match.group(1)}"
                        if context not in valid_contexts:
                            # Extract action text
                            text_match = re.match(r'- \[ \] (?:\d{4}-\d{2}-\d{2} )?(.+?)(?:@|\+|due:|defer:|https?://|$)', line)
                            action_text = text_match.group(1).strip() if text_match else "..."

                            invalid_contexts.append({
                                "action_text": action_text,
                                "context": context,
                                "file": file_path.name,
                                "line": line
                            })

        # Process context files
        if contexts_dir.exists():
            for context_file in contexts_dir.glob("*.md"):
                process_action_file(context_file)

        # Process special state files
        for state_file in ["@waiting.md", "@deferred.md", "@incubating.md"]:
            state_path = actions_base / state_file
            if state_path.exists():
                process_action_file(state_path)

        return {
            "orphan_actions": orphan_actions,
            "invalid_contexts": invalid_contexts
        }

    def audit_action_files(self) -> dict:
        """
        Audit action files for YAML completeness.

        Checks required fields: title, last_reviewed

        Returns:
            Dict with structure:
            {
                "issues": [
                    {
                        "file": "@macbook.md",
                        "missing_fields": ["last_reviewed"]
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

        required_fields = ["title", "last_reviewed"]
        issues = []

        # Helper to check action file
        def check_action_file(file_path: Path):
            frontmatter = self._parse_frontmatter(file_path)

            missing_fields = []
            for field in required_fields:
                if field not in frontmatter or not frontmatter[field]:
                    missing_fields.append(field)

            if missing_fields:
                issues.append({
                    "file": file_path.name,
                    "missing_fields": missing_fields
                })

        # Check context files
        contexts_dir = actions_base / "contexts"
        if contexts_dir.exists():
            for context_file in contexts_dir.glob("*.md"):
                check_action_file(context_file)

        # Check special state files
        for state_file in ["@waiting.md", "@deferred.md", "@incubating.md"]:
            state_path = actions_base / state_file
            if state_path.exists():
                check_action_file(state_path)

        return {"issues": issues}

    def list_projects_needing_review(self, days_threshold: int = 7) -> dict:
        """
        Find projects not reviewed recently.

        Args:
            days_threshold: Days since review to consider needing review (default: 7, inclusive)

        Returns:
            Dict with structure:
            {
                "projects_needing_review": [
                    {
                        "title": "Project Name",
                        "folder": "active",
                        "area": "Health",
                        "last_reviewed": "2025-01-01",
                        "days_since_review": 15
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        today = date.today()

        projects_needing_review = []

        for folder in ["active", "incubator", "completed"]:
            folder_path = projects_base / folder
            if not folder_path.exists():
                continue

            for area_dir in folder_path.iterdir():
                if not area_dir.is_dir():
                    continue

                for project_file in area_dir.glob("*.md"):
                    frontmatter = self._parse_frontmatter(project_file)

                    last_reviewed = frontmatter.get("last_reviewed")

                    if not last_reviewed:
                        # Missing last_reviewed - definitely needs review
                        projects_needing_review.append({
                            "title": frontmatter.get("title", project_file.stem),
                            "folder": folder,
                            "area": frontmatter.get("area", ""),
                            "filename": project_file.stem,
                            "last_reviewed": None,
                            "days_since_review": None
                        })
                    else:
                        try:
                            review_date = datetime.strptime(last_reviewed, "%Y-%m-%d").date()
                            days_diff = (today - review_date).days

                            if days_diff >= days_threshold:
                                projects_needing_review.append({
                                    "title": frontmatter.get("title", project_file.stem),
                                    "folder": folder,
                                    "area": frontmatter.get("area", ""),
                                    "filename": project_file.stem,
                                    "last_reviewed": last_reviewed,
                                    "days_since_review": days_diff
                                })
                        except ValueError:
                            # Invalid date format - treat as needs review
                            projects_needing_review.append({
                                "title": frontmatter.get("title", project_file.stem),
                                "folder": folder,
                                "area": frontmatter.get("area", ""),
                                "filename": project_file.stem,
                                "last_reviewed": last_reviewed,
                                "days_since_review": None
                            })

        # Sort by days_since_review descending (None last)
        projects_needing_review.sort(key=lambda p: (p["days_since_review"] is None, -(p["days_since_review"] or 0)))

        return {"projects_needing_review": projects_needing_review}

    def list_actions_needing_review(self, days_threshold: int = 7) -> dict:
        """
        Find action lists not reviewed recently.

        Args:
            days_threshold: Days since review to consider needing review (default: 7, inclusive)

        Returns:
            Dict with structure:
            {
                "actions_needing_review": [
                    {
                        "file": "@macbook.md",
                        "last_reviewed": "2025-01-01",
                        "days_since_review": 12
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        today = date.today()

        actions_needing_review = []

        # Helper to check action file
        def check_action_file(file_path: Path):
            frontmatter = self._parse_frontmatter(file_path)
            last_reviewed = frontmatter.get("last_reviewed")

            if not last_reviewed:
                # Missing last_reviewed
                actions_needing_review.append({
                    "file": file_path.name,
                    "last_reviewed": None,
                    "days_since_review": None
                })
            else:
                try:
                    review_date = datetime.strptime(last_reviewed, "%Y-%m-%d").date()
                    days_diff = (today - review_date).days

                    if days_diff >= days_threshold:
                        actions_needing_review.append({
                            "file": file_path.name,
                            "last_reviewed": last_reviewed,
                            "days_since_review": days_diff
                        })
                except ValueError:
                    # Invalid date format
                    actions_needing_review.append({
                        "file": file_path.name,
                        "last_reviewed": last_reviewed,
                        "days_since_review": None
                    })

        # Check context files
        contexts_dir = actions_base / "contexts"
        if contexts_dir.exists():
            for context_file in contexts_dir.glob("*.md"):
                check_action_file(context_file)

        # Check special state files
        for state_file in ["@waiting.md", "@deferred.md", "@incubating.md"]:
            state_path = actions_base / state_file
            if state_path.exists():
                check_action_file(state_path)

        # Sort by days_since_review descending (None last)
        actions_needing_review.sort(key=lambda a: (a["days_since_review"] is None, -(a["days_since_review"] or 0)))

        return {"actions_needing_review": actions_needing_review}
