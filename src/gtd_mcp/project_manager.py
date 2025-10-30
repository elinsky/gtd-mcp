"""Project management functionality for Phase 2."""

import re
import shutil
from datetime import date
from pathlib import Path
from typing import Literal

from gtd_mcp.completer import ProjectCompleter
from gtd_mcp.config import ConfigManager


class ProjectManager:
    """Manages GTD project state transitions and updates."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize manager with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config
        self._completer = ProjectCompleter(config)

    def _find_project_file(self, title: str, expected_folder: str | None = None) -> tuple[Path | None, str | None]:
        """
        Find project file by title.

        Args:
            title: Project title (exact match, case-sensitive)
            expected_folder: If specified, only search this folder

        Returns:
            Tuple of (file_path, folder_name) or (None, None) if not found
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        folders_to_search = [expected_folder] if expected_folder else ["active", "incubator", "completed"]

        for folder in folders_to_search:
            folder_path = projects_base / folder
            if not folder_path.exists():
                continue

            for area_dict in self._config.get_areas():
                area_kebab = area_dict["kebab"]
                area_dir = folder_path / area_kebab

                if not area_dir.exists():
                    continue

                for project_file in area_dir.glob("*.md"):
                    # Check title in YAML
                    with open(project_file, 'r') as f:
                        for line in f.readlines()[:10]:
                            if line.strip().startswith("title:"):
                                file_title = line.split(":", 1)[1].strip()
                                if file_title == title:
                                    return (project_file, folder)

        return (None, None)

    def _parse_frontmatter(self, file_path: Path) -> dict:
        """Parse YAML frontmatter from project file."""
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

    def _update_frontmatter(self, file_path: Path, updates: dict, removals: list[str] | None = None) -> None:
        """
        Update YAML frontmatter fields.

        Args:
            file_path: Path to project file
            updates: Dict of field_name: value to add/update
            removals: List of field names to remove
        """
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Find frontmatter bounds
        frontmatter_start = None
        frontmatter_end = None
        for i, line in enumerate(lines):
            if line.strip() == "---":
                if frontmatter_start is None:
                    frontmatter_start = i
                else:
                    frontmatter_end = i
                    break

        if frontmatter_start is None or frontmatter_end is None:
            raise ValueError("Invalid YAML frontmatter")

        # Parse existing frontmatter
        frontmatter_lines = lines[frontmatter_start + 1:frontmatter_end]
        new_frontmatter = []

        # Process existing lines
        for line in frontmatter_lines:
            if ":" in line:
                key = line.split(":", 1)[0].strip()
                # Skip if in removals
                if removals and key in removals:
                    continue
                # Update if in updates
                if key in updates:
                    new_frontmatter.append(f"{key}: {updates[key]}\n")
                    del updates[key]  # Mark as processed
                else:
                    new_frontmatter.append(line)
            else:
                new_frontmatter.append(line)

        # Add any remaining updates (new fields)
        for key, value in updates.items():
            new_frontmatter.append(f"{key}: {value}\n")

        # Reconstruct file
        new_lines = (
            lines[:frontmatter_start + 1] +
            new_frontmatter +
            lines[frontmatter_end:]
        )

        with open(file_path, 'w') as f:
            f.writelines(new_lines)

    def activate_project(self, title: str) -> str:
        """
        Move project from incubator to active.

        Args:
            title: Project title (exact match)

        Returns:
            Success or error message
        """
        # Find project in incubator
        project_file, folder = self._find_project_file(title, expected_folder="incubator")

        if not project_file:
            return f"Error: Project '{title}' not found in incubator folder"

        # Get area from file path
        area_kebab = project_file.parent.name

        # Create target path
        repo_path = Path(self._config.get_repo_path())
        active_dir = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / area_kebab
        active_dir.mkdir(parents=True, exist_ok=True)

        target_file = active_dir / project_file.name

        # Move file
        shutil.move(str(project_file), str(target_file))

        # Add started date
        today = date.today().isoformat()
        self._update_frontmatter(target_file, {"started": today})

        return f"✓ Successfully activated project '{title}' (added started date: {today})"

    def move_project_to_incubator(self, title: str) -> str:
        """
        Move project from active to incubator.

        Args:
            title: Project title (exact match)

        Returns:
            Success or error message
        """
        # Find project in active
        project_file, folder = self._find_project_file(title, expected_folder="active")

        if not project_file:
            return f"Error: Project '{title}' not found in active folder"

        # Check for 0k blockers (any actions)
        project_filename = project_file.stem
        blockers = self._completer.check_0k_blockers(project_filename)

        if blockers:
            return f"Error: Project '{title}' has incomplete 0k actions. Must complete or remove all actions before moving to incubator. Found {len(blockers)} blocking items."

        # Get area from file path
        area_kebab = project_file.parent.name

        # Create target path
        repo_path = Path(self._config.get_repo_path())
        incubator_dir = repo_path / "docs" / "execution_system" / "10k-projects" / "incubator" / area_kebab
        incubator_dir.mkdir(parents=True, exist_ok=True)

        target_file = incubator_dir / project_file.name

        # Move file
        shutil.move(str(project_file), str(target_file))

        # Remove started date
        self._update_frontmatter(target_file, {}, removals=["started"])

        return f"✓ Successfully moved project '{title}' to incubator (removed started date)"

    def descope_project(self, title: str) -> str:
        """
        Move project to descoped folder.

        Args:
            title: Project title (exact match)

        Returns:
            Success or error message
        """
        # Find project in active or incubator
        project_file, folder = self._find_project_file(title)

        if not project_file or folder not in ["active", "incubator"]:
            return f"Error: Project '{title}' not found in active or incubator folders"

        # Check for 0k blockers (any actions)
        project_filename = project_file.stem
        blockers = self._completer.check_0k_blockers(project_filename)

        if blockers:
            return f"Error: Project '{title}' has incomplete 0k actions. Must complete or remove all actions before descoping. Found {len(blockers)} blocking items."

        # Get area from file path
        area_kebab = project_file.parent.name

        # Create target path
        repo_path = Path(self._config.get_repo_path())
        descoped_dir = repo_path / "docs" / "execution_system" / "10k-projects" / "descoped" / area_kebab
        descoped_dir.mkdir(parents=True, exist_ok=True)

        target_file = descoped_dir / project_file.name

        # Move file
        shutil.move(str(project_file), str(target_file))

        # Add descoped date and remove started
        today = date.today().isoformat()
        self._update_frontmatter(target_file, {"descoped": today}, removals=["started"])

        return f"✓ Successfully descoped project '{title}' (added descoped date: {today})"

    def update_project_due_date(self, title: str, due_date: str | None) -> str:
        """
        Update or remove project due date.

        Args:
            title: Project title (exact match)
            due_date: ISO date string (YYYY-MM-DD) or None to remove

        Returns:
            Success or error message
        """
        # Find project
        project_file, folder = self._find_project_file(title)

        if not project_file:
            return f"Error: Project '{title}' not found"

        # Validate date format if provided
        if due_date:
            try:
                # Just check format
                parts = due_date.split("-")
                if len(parts) != 3 or len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
                    raise ValueError("Invalid format")
            except:
                return f"Error: Invalid due date format. Use YYYY-MM-DD"

        # Update or remove
        if due_date:
            self._update_frontmatter(project_file, {"due": due_date})
            return f"✓ Successfully updated due date for '{title}' to {due_date}"
        else:
            self._update_frontmatter(project_file, {}, removals=["due"])
            return f"✓ Successfully removed due date from '{title}'"

    def update_project_area(self, title: str, new_area: str) -> str:
        """
        Update project area (moves file to new area folder).

        Args:
            title: Project title (exact match)
            new_area: New area name (must match configured areas)

        Returns:
            Success or error message
        """
        # Validate new area
        area_kebab = self._config.find_area_kebab(new_area)
        if not area_kebab:
            valid_areas = [a["name"] for a in self._config.get_areas()]
            return f"Error: Invalid area '{new_area}'. Valid areas: {', '.join(valid_areas)}"

        # Find project
        project_file, folder = self._find_project_file(title)

        if not project_file:
            return f"Error: Project '{title}' not found"

        # Create target directory
        repo_path = Path(self._config.get_repo_path())
        target_dir = repo_path / "docs" / "execution_system" / "10k-projects" / folder / area_kebab
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / project_file.name

        # Move file
        shutil.move(str(project_file), str(target_file))

        # Update area in YAML
        self._update_frontmatter(target_file, {"area": new_area})

        return f"✓ Successfully updated area for '{title}' to {new_area}"

    def update_project_type(self, title: str, project_type: Literal["standard", "habit", "coordination"]) -> str:
        """
        Update project type.

        Args:
            title: Project title (exact match)
            project_type: New project type

        Returns:
            Success or error message
        """
        # Find project
        project_file, folder = self._find_project_file(title)

        if not project_file:
            return f"Error: Project '{title}' not found"

        # Update type
        self._update_frontmatter(project_file, {"type": project_type})

        return f"✓ Successfully updated type for '{title}' to {project_type}"

    def update_review_dates(
        self,
        target_type: Literal["projects", "actions", "all"] = "projects",
        filter_folder: Literal["active", "incubator", "all"] | None = None,
        filter_area: str | None = None,
        filter_names: list[str] | None = None
    ) -> str:
        """
        Bulk update last_reviewed dates.

        Args:
            target_type: What to update (projects, actions, or all)
            filter_folder: For projects - which folder(s)
            filter_area: For projects - specific area
            filter_names: Specific project titles or action list names

        Returns:
            Success message with count
        """
        repo_path = Path(self._config.get_repo_path())
        today = date.today().isoformat()
        updated_count = 0

        # Update projects
        if target_type in ["projects", "all"]:
            projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

            # Determine folders to scan
            folders = []
            if filter_folder == "all" or filter_folder is None:
                folders = ["active", "incubator"]
            else:
                folders = [filter_folder]

            for folder in folders:
                folder_path = projects_base / folder
                if not folder_path.exists():
                    continue

                for area_dict in self._config.get_areas():
                    area_name = area_dict["name"]
                    area_kebab = area_dict["kebab"]

                    # Skip if filtering by area and this isn't it
                    if filter_area and area_name.lower() != filter_area.lower():
                        continue

                    area_dir = folder_path / area_kebab
                    if not area_dir.exists():
                        continue

                    for project_file in area_dir.glob("*.md"):
                        # If filter_names specified, check title
                        if filter_names:
                            with open(project_file, 'r') as f:
                                content = f.read()
                                title = None
                                for line in content.split('\n')[:10]:
                                    if line.strip().startswith("title:"):
                                        title = line.split(":", 1)[1].strip()
                                        break

                                if title not in filter_names:
                                    continue

                        # Update review date
                        self._update_frontmatter(project_file, {"last_reviewed": today})
                        updated_count += 1

        # Update action lists
        if target_type in ["actions", "all"]:
            actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

            # Get all action list files
            action_files = []

            # Context files
            contexts_dir = actions_base / "contexts"
            if contexts_dir.exists():
                action_files.extend(contexts_dir.glob("*.md"))

            # Special state files
            for special_file in ["@waiting.md", "@deferred.md", "@incubating.md"]:
                special_path = actions_base / special_file
                if special_path.exists():
                    action_files.append(special_path)

            for action_file in action_files:
                # If filter_names specified, check filename
                if filter_names:
                    # Handle both with and without @ prefix
                    filename_variants = [action_file.stem, f"@{action_file.stem}"]
                    if not any(variant in filter_names for variant in filename_variants):
                        continue

                # Update review date
                self._update_frontmatter(action_file, {"last_reviewed": today})
                updated_count += 1

        item_word = "item" if updated_count == 1 else "items"
        return f"✓ Successfully updated review dates for {updated_count} {item_word} to {today}"
