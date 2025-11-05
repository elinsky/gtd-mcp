"""project completion functionality."""

import re
import yaml
from pathlib import Path
from datetime import date

from execution_system_mcp.config import ConfigManager


class ProjectCompleter:
    """Handles completing projects."""

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

    def parse_frontmatter(self, file_path: Path) -> dict:
        """
        Parse YAML frontmatter from a project file.

        Args:
            file_path: Path to project markdown file

        Returns:
            Dict with frontmatter fields (preserves insertion order)
        """
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract frontmatter between --- markers
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Invalid frontmatter format")

        yaml_content = parts[1]
        frontmatter = yaml.safe_load(yaml_content)

        # Convert date objects to strings
        for key, value in frontmatter.items():
            if isinstance(value, date):
                frontmatter[key] = str(value)

        return frontmatter

    def add_completed_date(self, frontmatter: dict) -> dict:
        """
        Add completed date to frontmatter dict.

        Maintains field order: area, title, type, created, started,
        last_reviewed, due (if present), completed.

        Args:
            frontmatter: Existing frontmatter dict

        Returns:
            New dict with completed date added
        """
        result = {}
        completed_value = str(date.today())

        # Build in correct order
        for key in ["area", "title", "type", "created", "started", "last_reviewed", "due"]:
            if key in frontmatter:
                result[key] = frontmatter[key]

        # Add completed at the end
        result["completed"] = completed_value

        return result

    def generate_frontmatter_yaml(self, frontmatter: dict) -> str:
        """
        Generate YAML frontmatter string from dict.

        Args:
            frontmatter: Frontmatter dict

        Returns:
            YAML frontmatter string with --- delimiters
        """
        lines = ["---"]
        for key, value in frontmatter.items():
            lines.append(f"{key}: {value}")
        lines.append("---")
        return "\n".join(lines) + "\n"

    def complete_project(self, title: str) -> str:
        """
        Complete a project.

        Validates no open 0k items exist, then moves project from active/
        to completed/ folder with completed date added to frontmatter.

        Args:
            title: Project title

        Returns:
            Success or error message
        """
        # Find active project
        project_path, area_or_error = self.find_active_project(title)
        if project_path is None:
            return f"✗ Error: {area_or_error}"

        area_kebab = area_or_error
        project_kebab = project_path.stem

        # Check for 0k blockers
        blockers = self.check_0k_blockers(project_kebab)
        if blockers:
            error_lines = [f"✗ Cannot complete project '{title}' - {len(blockers)} open item(s) at 0k horizon:", ""]

            # Group by file
            by_file = {}
            for blocker in blockers:
                file = blocker["file"]
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(blocker["line"])

            for file, lines in by_file.items():
                file_display = file.replace("@", "").replace(".md", "").replace("contexts/", "").title()
                error_lines.append(f"{file_display} ({file}):")
                for line in lines:
                    # Extract just the description part
                    parts = line.split(" ", 3)
                    if len(parts) >= 4:
                        desc = parts[3].split(" +")[0]
                        error_lines.append(f"  • {desc}")
                error_lines.append("")

            error_lines.append("Complete or remove these items before completing the project.")
            return "\n".join(error_lines)

        # Parse existing frontmatter
        frontmatter = self.parse_frontmatter(project_path)

        # Add completed date
        frontmatter = self.add_completed_date(frontmatter)

        # Read project body (everything after frontmatter)
        with open(project_path, 'r') as f:
            content = f.read()
        parts = content.split("---", 2)
        body = parts[2] if len(parts) >= 3 else ""

        # Generate new frontmatter
        new_frontmatter = self.generate_frontmatter_yaml(frontmatter)

        # Create completed directory if needed
        repo_path = Path(self._config.get_repo_path())
        completed_base = repo_path / "docs" / "execution_system" / "10k-projects" / "completed"
        completed_area_dir = completed_base / area_kebab
        completed_area_dir.mkdir(parents=True, exist_ok=True)

        # Write to completed folder
        completed_path = completed_area_dir / project_path.name
        with open(completed_path, 'w') as f:
            f.write(new_frontmatter + body)

        # Delete from active folder
        project_path.unlink()

        return f"✓ Successfully completed project '{title}'\n  Moved from: {project_path}\n  Moved to: {completed_path}\n  Completed: {date.today()}"
