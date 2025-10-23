"""Project listing functionality."""

from datetime import date, datetime
from pathlib import Path

from gtd_mcp.config import ConfigManager


class ProjectLister:
    """Lists and formats GTD projects."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize lister with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config

    @staticmethod
    def parse_yaml_frontmatter(file_path: Path) -> dict:
        """
        Parse YAML frontmatter from project file.

        Args:
            file_path: Path to project markdown file

        Returns:
            Dict with area, title, type, due fields
        """
        # Read first 10 lines (YAML frontmatter section)
        with open(file_path, 'r') as f:
            lines = [f.readline() for _ in range(10)]

        result = {
            "area": None,
            "title": None,
            "type": "standard",  # Default
            "due": None
        }

        # Parse YAML fields
        for line in lines:
            line = line.strip()
            if line.startswith("area:"):
                result["area"] = line.split(":", 1)[1].strip()
            elif line.startswith("title:"):
                result["title"] = line.split(":", 1)[1].strip()
            elif line.startswith("type:"):
                result["type"] = line.split(":", 1)[1].strip()
            elif line.startswith("due:"):
                result["due"] = line.split(":", 1)[1].strip()

        # Use filename as title if not provided
        if not result["title"]:
            result["title"] = file_path.stem  # filename without .md

        return result

    @staticmethod
    def format_due_date(due_date: str | None) -> str:
        """
        Format due date with days remaining/overdue.

        Args:
            due_date: ISO date string (YYYY-MM-DD) or None

        Returns:
            Formatted string like " (2025-12-31 - 45d)" or "" if no due date
        """
        if not due_date:
            return ""

        try:
            due = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            return f" ({due_date})"  # Invalid format, just show the date

        today = date.today()
        days_diff = (due - today).days

        if days_diff < 0:
            # Overdue
            days_over = abs(days_diff)
            return f" ({due_date} - OVERDUE {days_over}d)"
        elif days_diff == 0:
            # Due today
            return f" ({due_date} - TODAY!)"
        else:
            # Future date
            return f" ({due_date} - {days_diff}d)"

    def list_active_projects(self) -> str:
        """
        List all active projects grouped by area.

        Returns:
            Formatted string with projects grouped by area
        """
        repo_path = Path(self._config.get_repo_path())
        active_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active"

        if not active_path.exists():
            return "No active projects directory found"

        # Collect all projects with their metadata
        projects = []
        for area_dict in self._config.get_areas():
            area_name = area_dict["name"]
            area_kebab = area_dict["kebab"]
            area_dir = active_path / area_kebab

            if not area_dir.exists():
                continue

            # Find all .md files in this area
            for project_file in area_dir.glob("*.md"):
                metadata = self.parse_yaml_frontmatter(project_file)
                projects.append({
                    "area": area_name,
                    "title": metadata["title"],
                    "type": metadata["type"],
                    "due": metadata["due"]
                })

        if not projects:
            return "No active projects found"

        # Sort by area alphabetically
        projects.sort(key=lambda p: p["area"])

        # Format output
        lines = ["Active Projects by Area:", ""]
        current_area = None

        for project in projects:
            # Print area header when it changes
            if project["area"] != current_area:
                if current_area is not None:
                    lines.append("")  # Blank line between areas
                lines.append(f"{project['area']}:")
                current_area = project["area"]

            # Format project line
            title = project["title"]
            type_indicator = ""
            if project["type"] == "habit":
                type_indicator = " [habit]"
            elif project["type"] == "coordination":
                type_indicator = " [coordination]"

            due_display = self.format_due_date(project["due"])

            lines.append(f"  • {title}{type_indicator}{due_display}")

        return "\n".join(lines)
