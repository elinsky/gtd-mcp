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
