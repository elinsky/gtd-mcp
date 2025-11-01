"""Project file creation logic."""

import re
import unicodedata
from datetime import date
from pathlib import Path

from gtd_mcp.config import ConfigManager
from gtd_mcp.templates import TemplateEngine


class ProjectCreator:
    """Creates project files with frontmatter and templates."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize creator with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config

    @staticmethod
    def to_kebab_case(text: str) -> str:
        """
        Convert text to kebab-case.

        Args:
            text: Text to convert

        Returns:
            Kebab-case string (lowercase, hyphens, alphanumeric only)
        """
        # Normalize unicode characters (é -> e)
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')

        # Convert to lowercase
        text = text.lower()

        # Replace spaces and non-alphanumeric chars with hyphens
        text = re.sub(r'[^a-z0-9]+', '-', text)

        # Remove leading/trailing hyphens
        text = text.strip('-')

        # Replace multiple consecutive hyphens with single hyphen
        text = re.sub(r'-+', '-', text)

        return text

    def generate_frontmatter(
        self,
        area: str,
        title: str,
        project_type: str,
        folder: str,
        due: str | None = None
    ) -> str:
        """
        Generate YAML frontmatter.

        Args:
            area: Area of focus
            title: Project title
            project_type: Type of project
            folder: Target folder (active or incubator)
            due: Optional due date in YYYY-MM-DD format

        Returns:
            YAML frontmatter string with --- delimiters
        """
        today = date.today().isoformat()

        frontmatter = {
            "area": area,
            "title": title,
            "type": project_type,
            "created": today,
        }

        # Add started field for active projects
        if folder == "active":
            frontmatter["started"] = today

        frontmatter["last_reviewed"] = today

        # Add due field if provided
        if due:
            frontmatter["due"] = due

        # Build YAML string manually to control field order
        lines = ["---"]
        for key, value in frontmatter.items():
            lines.append(f"{key}: {value}")
        lines.append("---\n")

        return "\n".join(lines)

    def create_project(
        self,
        title: str,
        area: str,
        project_type: str,
        folder: str,
        due: str | None = None
    ) -> str:
        """
        Create project file with frontmatter and template.

        Args:
            title: Project title
            area: Area of focus
            project_type: Type of project (standard, habit, coordination)
            folder: Target folder (active or incubator)
            due: Optional due date in YYYY-MM-DD format

        Returns:
            Absolute path to created project file
        """
        # Generate filename
        filename = self.to_kebab_case(title) + ".md"

        # Get area kebab-case
        area_kebab = self._config.find_area_kebab(area)
        if not area_kebab:
            raise ValueError(f"Area '{area}' not found in configuration")

        # Construct file path
        repo_path = Path(self._config.get_repo_path())
        file_path = (
            repo_path / "docs" / "execution_system" / "10k-projects" /
            folder / area_kebab / filename
        )

        # Create directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate frontmatter
        frontmatter = self.generate_frontmatter(area, title, project_type, folder, due)

        # Generate template
        template = TemplateEngine.generate(project_type, title, folder)

        # Write file
        content = frontmatter + template
        file_path.write_text(content)

        return str(file_path.absolute())
