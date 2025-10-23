"""GTD project completion functionality."""

import re
import yaml
from pathlib import Path
from datetime import date

from gtd_mcp.config import ConfigManager


class ProjectCompleter:
    """Handles completing GTD projects."""

    def __init__(self, config: ConfigManager):
        """
        Initialize ProjectCompleter.

        Args:
            config: ConfigManager instance
        """
        self._config = config

    def find_active_project(self, title: str) -> tuple[Path | None, str]:
        """
        Find an active project by title.

        Searches all area subdirectories in the active folder for a project
        with the given title in its YAML frontmatter. Also checks if the
        project exists in other folders (completed, incubator, descoped).

        Args:
            title: Project title (exact match)

        Returns:
            Tuple of (project_path, area_kebab) if found in active,
            or (None, error_message) if not found or not active
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        # Search all area subdirectories in active folder
        active_base = projects_base / "active"
        if active_base.exists():
            for area_dir in active_base.iterdir():
                if not area_dir.is_dir():
                    continue

                for project_file in area_dir.glob("*.md"):
                    # Parse frontmatter to check title
                    try:
                        with open(project_file, 'r') as f:
                            lines = [f.readline() for _ in range(20)]

                        # Simple YAML frontmatter parsing
                        in_frontmatter = False
                        project_title = None
                        for line in lines:
                            line = line.strip()
                            if line == "---":
                                if in_frontmatter:
                                    break
                                in_frontmatter = True
                                continue
                            if in_frontmatter and line.startswith("title:"):
                                project_title = line.split(":", 1)[1].strip()
                                break

                        if project_title == title:
                            return (project_file, area_dir.name)

                    except Exception:
                        continue

        # Check if project exists in other folders
        for folder in ["completed", "incubator", "descoped"]:
            folder_base = projects_base / folder
            if not folder_base.exists():
                continue

            for area_dir in folder_base.iterdir():
                if not area_dir.is_dir():
                    continue

                for project_file in area_dir.glob("*.md"):
                    try:
                        with open(project_file, 'r') as f:
                            lines = [f.readline() for _ in range(20)]

                        in_frontmatter = False
                        project_title = None
                        for line in lines:
                            line = line.strip()
                            if line == "---":
                                if in_frontmatter:
                                    break
                                in_frontmatter = True
                                continue
                            if in_frontmatter and line.startswith("title:"):
                                project_title = line.split(":", 1)[1].strip()
                                break

                        if project_title == title:
                            if folder == "completed":
                                return (None, f"Project '{title}' is already completed")
                            else:
                                return (None, f"Project '{title}' is not active (found in {folder})")

                    except Exception:
                        continue

        return (None, f"Project '{title}' not found in active folder")

    def check_0k_blockers(self, project_kebab: str) -> list[dict]:
        """
        Check for open 0k horizon items tagged with the project.

        Scans @waiting.md, @incubating.md, @deferred.md, and contexts/*.md
        for unchecked items (- [ ]) containing +{project_kebab}. Ignores
        completed.md file and checked items (- [x]).

        Args:
            project_kebab: Project identifier in kebab-case

        Returns:
            List of dicts with keys "file" and "line" for each blocking item
        """
        repo_path = Path(self._config.get_repo_path())
        next_actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

        blockers = []
        project_tag = f"+{project_kebab}"

        # Files to check (excluding completed.md)
        files_to_check = []

        # Add @ files
        for filename in ["@waiting.md", "@incubating.md", "@deferred.md"]:
            file_path = next_actions_base / filename
            if file_path.exists():
                files_to_check.append((filename, file_path))

        # Add context files
        contexts_dir = next_actions_base / "contexts"
        if contexts_dir.exists():
            for context_file in contexts_dir.glob("*.md"):
                relative_name = f"contexts/{context_file.name}"
                files_to_check.append((relative_name, context_file))

        # Scan each file for unchecked items with project tag
        for filename, file_path in files_to_check:
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        # Only match unchecked items
                        if line.strip().startswith("- [ ]") and project_tag in line:
                            blockers.append({
                                "file": filename,
                                "line": line.strip()
                            })
            except Exception:
                continue

        return blockers
