"""Project listing functionality."""

from datetime import date, datetime
from pathlib import Path
from typing import Literal

from gtd_mcp.config import ConfigManager


class ProjectLister:
    """Lists and formats projects."""

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

    def list_projects(
        self,
        folder: Literal["active", "incubator", "completed", "all"] = "active",
        group_by: Literal["area", "due_date", "flat"] = "area",
        filter_area: str | None = None,
        filter_has_due: bool | None = None,
    ) -> dict:
        """
        List projects with flexible filtering and grouping.

        Args:
            folder: Which folder(s) to list from (default: "active")
            group_by: How to group projects (default: "area")
            filter_area: Optional area filter (case-insensitive)
            filter_has_due: Optional filter for projects with due dates

        Returns:
            Dict with structure:
            {
                "groups": [
                    {
                        "group_name": "Health",
                        "projects": [
                            {
                                "title": "Morning Routine",
                                "area": "Health",
                                "type": "habit",
                                "folder": "active",
                                "due": "2025-12-31",
                                "filename": "morning-routine"
                            }
                        ]
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        # Determine which folders to scan
        folders_to_scan = []
        if folder == "all":
            folders_to_scan = ["active", "incubator", "completed"]
        else:
            folders_to_scan = [folder]

        # Collect all projects
        all_projects = []
        for folder_name in folders_to_scan:
            folder_path = projects_base / folder_name
            if not folder_path.exists():
                continue

            for area_dict in self._config.get_areas():
                area_name = area_dict["name"]
                area_kebab = area_dict["kebab"]
                area_dir = folder_path / area_kebab

                if not area_dir.exists():
                    continue

                for project_file in area_dir.glob("*.md"):
                    metadata = self.parse_yaml_frontmatter(project_file)

                    project_data = {
                        "title": metadata["title"],
                        "area": area_name,
                        "type": metadata["type"],
                        "folder": folder_name,
                        "due": metadata["due"],
                        "filename": project_file.stem,
                    }
                    all_projects.append(project_data)

        # Apply filters
        if filter_area:
            all_projects = [
                p for p in all_projects
                if p["area"].lower() == filter_area.lower()
            ]

        if filter_has_due is not None:
            if filter_has_due:
                all_projects = [p for p in all_projects if p["due"] is not None]
            else:
                all_projects = [p for p in all_projects if p["due"] is None]

        # Group and sort
        if group_by == "area":
            return self._group_by_area(all_projects)
        elif group_by == "due_date":
            return self._group_by_due_date(all_projects)
        else:  # flat
            return self._group_flat(all_projects)

    def _group_by_area(self, projects: list[dict]) -> dict:
        """Group projects by area."""
        # Sort by area name
        projects.sort(key=lambda p: p["area"])

        groups = []
        current_area = None
        current_group = None

        for project in projects:
            if project["area"] != current_area:
                if current_group is not None:
                    groups.append(current_group)
                current_area = project["area"]
                current_group = {
                    "group_name": current_area,
                    "projects": []
                }
            current_group["projects"].append(project)

        if current_group is not None:
            groups.append(current_group)

        return {"groups": groups}

    def _group_by_due_date(self, projects: list[dict]) -> dict:
        """Group projects by due date categories."""
        today = date.today()

        overdue = []
        this_week = []
        later = []
        no_due = []

        for project in projects:
            if project["due"] is None:
                no_due.append(project)
            else:
                try:
                    due = datetime.strptime(project["due"], "%Y-%m-%d").date()
                    days_diff = (due - today).days

                    if days_diff < 0:
                        overdue.append(project)
                    elif days_diff <= 7:
                        this_week.append(project)
                    else:
                        later.append(project)
                except ValueError:
                    no_due.append(project)

        # Sort each category by due date
        for category in [overdue, this_week, later]:
            category.sort(key=lambda p: p["due"] if p["due"] else "")

        # Build groups
        groups = []
        if overdue:
            groups.append({"group_name": "Overdue", "projects": overdue})
        if this_week:
            groups.append({"group_name": "This Week", "projects": this_week})
        if later:
            groups.append({"group_name": "Later", "projects": later})
        if no_due:
            no_due.sort(key=lambda p: p["title"])
            groups.append({"group_name": "No Due Date", "projects": no_due})

        return {"groups": groups}

    def _group_flat(self, projects: list[dict]) -> dict:
        """Return all projects in a single group, sorted by title."""
        projects.sort(key=lambda p: p["title"])
        return {
            "groups": [
                {
                    "group_name": "All Projects",
                    "projects": projects
                }
            ]
        }
