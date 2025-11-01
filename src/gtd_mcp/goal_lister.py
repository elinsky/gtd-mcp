"""Goal listing functionality."""

import json
from pathlib import Path

from gtd_mcp.config import ConfigManager


class GoalLister:
    """Lists GTD goals."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize lister with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config

    def _parse_yaml_frontmatter(self, file_path: Path) -> dict:
        """
        Parse YAML frontmatter from a goal file.

        Args:
            file_path: Path to goal file

        Returns:
            Dictionary with YAML fields
        """
        with open(file_path, 'r') as f:
            lines = f.readlines()

        in_yaml = False
        yaml_lines = []

        for line in lines:
            if line.strip() == '---':
                if not in_yaml:
                    in_yaml = True
                else:
                    break
            elif in_yaml:
                yaml_lines.append(line)

        # Parse YAML manually (simple key: value format)
        yaml_data = {}
        for line in yaml_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                yaml_data[key.strip()] = value.strip()

        return yaml_data

    def _find_goal_files(self, folder: str) -> list[dict]:
        """
        Find all goal files in a folder (active or incubator).

        Args:
            folder: Folder name ("active" or "incubator")

        Returns:
            List of goal dictionaries
        """
        repo_path = Path(self._config.get_repo_path())
        goals_base = repo_path / "docs" / "execution_system" / "30k-goals" / folder

        if not goals_base.exists():
            return []

        goals = []

        # Recursively find all .md files
        for md_file in goals_base.rglob("*.md"):
            # Skip _goals-summary.md
            if md_file.name == "_goals-summary.md":
                continue

            # Parse YAML frontmatter
            yaml_data = self._parse_yaml_frontmatter(md_file)

            # Only include files with type: goal
            if yaml_data.get("type") != "goal":
                continue

            # Build goal dictionary
            goal = {
                "title": yaml_data.get("title", ""),
                "area": yaml_data.get("area", ""),
                "filename": md_file.name,
                "file_path": str(md_file.relative_to(goals_base))
            }

            # Include started date if present
            if "started" in yaml_data:
                goal["started"] = yaml_data["started"]

            goals.append(goal)

        return goals

    def list_goals(self) -> str:
        """
        List all goals grouped by folder (active/incubator).

        Returns:
            JSON string with goals grouped by folder
        """
        active_goals = self._find_goal_files("active")
        incubator_goals = self._find_goal_files("incubator")

        result = {
            "active": active_goals,
            "incubator": incubator_goals
        }

        return json.dumps(result, indent=2)
