"""Action management functionality."""

from datetime import date
from pathlib import Path

from gtd_mcp.config import ConfigManager


class ActionManager:
    """Manages next actions."""

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
            context: Context tag (e.g., "@macbook", "@waiting")

        Returns:
            Path to context file
        """
        repo_path = Path(self._config.get_repo_path())
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

        # Special state files are in the base actions directory
        if context in ["@waiting", "@deferred", "@incubating"]:
            return actions_base / f"{context}.md"

        # Regular context files are in contexts subdirectory
        contexts_dir = actions_base / "contexts"
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

    def add_to_waiting(
        self,
        text: str,
        project: str | None = None,
        due: str | None = None,
        defer: str | None = None,
        action_date: str | None = None
    ) -> str:
        """
        Add an item to @waiting list.

        Args:
            text: Action text
            project: Optional project filename in kebab-case
            due: Optional due date (YYYY-MM-DD)
            defer: Optional defer date (YYYY-MM-DD)
            action_date: Optional creation date (YYYY-MM-DD), defaults to today

        Returns:
            Success or error message
        """
        result = self.add_action(
            text=text,
            context="@waiting",
            project=project,
            due=due,
            defer=defer,
            action_date=action_date
        )
        return result.replace("action to", "to")

    def add_to_deferred(
        self,
        text: str,
        project: str | None = None,
        defer: str | None = None,
        action_date: str | None = None
    ) -> str:
        """
        Add an item to @deferred list.

        Args:
            text: Action text
            project: Optional project filename in kebab-case
            defer: Optional defer date (YYYY-MM-DD)
            action_date: Optional creation date (YYYY-MM-DD), defaults to today

        Returns:
            Success or error message
        """
        return self.add_action(
            text=text,
            context="@deferred",
            project=project,
            defer=defer,
            action_date=action_date
        ).replace("action to @deferred.md", "to @deferred.md")

    def add_to_incubating(
        self,
        text: str,
        project: str | None = None,
        action_date: str | None = None
    ) -> str:
        """
        Add an item to @incubating list.

        Args:
            text: Action text
            project: Optional project filename in kebab-case
            action_date: Optional creation date (YYYY-MM-DD), defaults to today

        Returns:
            Success or error message
        """
        return self.add_action(
            text=text,
            context="@incubating",
            project=project,
            action_date=action_date
        ).replace("action to @incubating.md", "to @incubating.md")

    def complete_action(
        self,
        file_path: str,
        line_number: int,
        completion_date: str | None = None
    ) -> str:
        """
        Complete an action by marking it done and moving to completed.md.

        Args:
            file_path: Relative path to action file (e.g., "contexts/@macbook.md" or "@waiting.md")
            line_number: Line number of action to complete (1-indexed as shown in editors)
            completion_date: Optional completion date (YYYY-MM-DD), defaults to today

        Returns:
            Success or error message
        """
        repo_path = Path(self._config.get_repo_path())
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

        # Resolve file path
        if file_path.startswith("@"):
            # Special state file in base directory
            source_file = actions_base / file_path
        elif file_path.startswith("contexts/"):
            # Context file in contexts subdirectory
            source_file = actions_base / file_path
        else:
            return f"Error: Invalid file path '{file_path}'. Must start with '@' or 'contexts/'"

        if not source_file.exists():
            return f"Error: File {file_path} does not exist"

        # Read source file
        with open(source_file, 'r') as f:
            lines = f.readlines()

        # Validate line number (convert from 1-indexed to 0-indexed)
        line_idx = line_number - 1
        if line_idx < 0 or line_idx >= len(lines):
            return f"Error: Line number {line_number} is out of range"

        action_line = lines[line_idx]

        # Validate it's an incomplete action
        if not action_line.strip().startswith("- [ ]"):
            return f"Error: Line {line_number} is not an incomplete action"

        # Extract action text (everything after "- [ ] ")
        action_text = action_line.strip()[6:]  # Remove "- [ ] "

        # Build completed action line
        completion_date_str = completion_date if completion_date else date.today().strftime("%Y-%m-%d")
        completed_line = f"- [x] {completion_date_str} {action_text}\n"

        # Get completed file path
        completed_file = actions_base / "completed.md"

        # Read completed file
        with open(completed_file, 'r') as f:
            completed_lines = f.readlines()

        # Find end of YAML frontmatter in completed file
        yaml_end_idx = 0
        in_yaml = False
        for i, line in enumerate(completed_lines):
            if line.strip() == '---':
                if not in_yaml:
                    in_yaml = True
                else:
                    yaml_end_idx = i + 1
                    break

        # Add empty line after YAML if not present
        if yaml_end_idx < len(completed_lines) and completed_lines[yaml_end_idx].strip() != "":
            completed_lines.insert(yaml_end_idx, "\n")
            yaml_end_idx += 1

        # Insert completed action at top of completed file
        completed_lines.insert(yaml_end_idx, completed_line)

        # Write updated completed file
        with open(completed_file, 'w') as f:
            f.writelines(completed_lines)

        # Remove action from source file
        lines.pop(line_idx)

        # Write updated source file
        with open(source_file, 'w') as f:
            f.writelines(lines)

        return f"✓ Successfully completed action from {file_path}"
