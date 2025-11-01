"""Action management functionality."""

from datetime import date
from pathlib import Path

from gtd_mcp.config import ConfigManager


class ActionManager:
    """Manages GTD next actions."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize manager with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config

    def _find_project_file(self, project_filename: str) -> Path | None:
        """
        Find project file across all folders and areas.

        Args:
            project_filename: Project filename in kebab-case (without .md)

        Returns:
            Path to project file if found, None otherwise
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        # Search in active, incubator, completed
        for folder in ["active", "incubator", "completed"]:
            folder_path = projects_base / folder
            if not folder_path.exists():
                continue

            # Search in all area subdirectories
            for area_dict in self._config.get_areas():
                area_kebab = area_dict["kebab"]
                area_dir = folder_path / area_kebab

                if not area_dir.exists():
                    continue

                project_file = area_dir / f"{project_filename}.md"
                if project_file.exists():
                    return project_file

        return None

    def _get_context_file_path(self, context: str) -> Path:
        """
        Get path to context file.

        Args:
            context: Context tag (e.g., "@macbook")

        Returns:
            Path to context file
        """
        repo_path = Path(self._config.get_repo_path())
        contexts_dir = repo_path / "docs" / "execution_system" / "00k-next-actions" / "contexts"
        return contexts_dir / f"{context}.md"

    def add_action(
        self,
        text: str,
        context: str,
        project: str | None = None,
        due: str | None = None,
        defer: str | None = None,
        action_date: str | None = None
    ) -> str:
        """
        Add a next action to a context file.

        Args:
            text: Action text
            context: Context tag (e.g., "@macbook")
            project: Optional project filename in kebab-case
            due: Optional due date (YYYY-MM-DD)
            defer: Optional defer date (YYYY-MM-DD)
            action_date: Optional creation date (YYYY-MM-DD), defaults to today

        Returns:
            Success or error message
        """
        # Validate project exists if provided
        if project:
            project_file = self._find_project_file(project)
            if not project_file:
                return f"Error: Project '{project}' does not exist in any folder"

        # Get context file path
        context_file = self._get_context_file_path(context)

        if not context_file.exists():
            return f"Error: Context file {context}.md does not exist"

        # Read existing file
        with open(context_file, 'r') as f:
            lines = f.readlines()

        # Find end of YAML frontmatter
        yaml_end_idx = 0
        in_yaml = False
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_yaml:
                    in_yaml = True
                else:
                    yaml_end_idx = i + 1
                    break

        # Build action line
        action_date_str = action_date if action_date else date.today().strftime("%Y-%m-%d")
        action_parts = [f"- [ ] {action_date_str} {text} {context}"]

        if project:
            action_parts.append(f"+{project}")

        if due:
            action_parts.append(f"due:{due}")

        if defer:
            action_parts.append(f"defer:{defer}")

        action_line = " ".join(action_parts) + "\n"

        # Insert action at top of file (after YAML)
        # Add empty line after YAML if not present
        if yaml_end_idx < len(lines) and lines[yaml_end_idx].strip() != "":
            lines.insert(yaml_end_idx, "\n")
            yaml_end_idx += 1

        lines.insert(yaml_end_idx, action_line)

        # Write back to file
        with open(context_file, 'w') as f:
            f.writelines(lines)

        return f"✓ Successfully added action to {context}.md"
