"""project and action search functionality."""

import re
from pathlib import Path
from typing import Literal

from gtd_mcp.config import ConfigManager


class Searcher:
    """
    Search functionality for projects and actions.

    Provides text-based search across project files and action lists
    with various filtering options.
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize Searcher with configuration.

        Args:
            config: ConfigManager instance
        """
        self._config = config

    def _parse_frontmatter(self, file_path: Path) -> dict:
        """
        Parse YAML frontmatter from a file.

        Args:
            file_path: Path to file with frontmatter

        Returns:
            Dict of frontmatter key-value pairs
        """
        frontmatter = {}
        with open(file_path, 'r') as f:
            lines = f.readlines()

        in_frontmatter = False
        for line in lines[:10]:  # Only check first 10 lines
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def search_projects(
        self,
        query: str,
        folder: Literal["active", "incubator", "completed", "all"] = "all",
        filter_area: str | None = None
    ) -> dict:
        """
        Search for projects by text in title or content.

        Args:
            query: Text to search for (case-insensitive)
            folder: Which folder(s) to search (default: all)
            filter_area: Optional area filter (case-insensitive)

        Returns:
            Dict with structure:
            {
                "matches": [
                    {
                        "title": "Project Title",
                        "area": "Health",
                        "folder": "active",
                        "filename": "project-name",
                        "match_location": "title" or "content",
                        "snippet": "...text around match..." (for content matches)
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        # Determine which folders to search
        if folder == "all":
            folders = ["active", "incubator", "completed", "descoped"]
        else:
            folders = [folder]

        # Normalize area filter
        area_kebab = None
        if filter_area:
            area_kebab = self._config.find_area_kebab(filter_area)

        matches = []
        query_lower = query.lower()

        for folder_name in folders:
            folder_path = projects_base / folder_name
            if not folder_path.exists():
                continue

            for area_dir in folder_path.iterdir():
                if not area_dir.is_dir():
                    continue

                # Apply area filter
                if area_kebab and area_dir.name != area_kebab:
                    continue

                for project_file in area_dir.glob("*.md"):
                    frontmatter = self._parse_frontmatter(project_file)
                    title = frontmatter.get("title", project_file.stem)
                    area = frontmatter.get("area", "")

                    # Track if we found match in title to avoid duplicates
                    found_in_title = False

                    # Search in title
                    if query_lower in title.lower():
                        matches.append({
                            "title": title,
                            "area": area,
                            "folder": folder_name,
                            "filename": project_file.stem,
                            "match_location": "title",
                            "snippet": title
                        })
                        found_in_title = True

                    # Search in content (skip if already found in title)
                    if not found_in_title:
                        with open(project_file, 'r') as f:
                            content = f.read()

                        # Skip frontmatter when searching content
                        content_without_frontmatter = content
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                content_without_frontmatter = parts[2]

                        if query_lower in content_without_frontmatter.lower():
                            # Find matching line for snippet
                            lines = content_without_frontmatter.split('\n')
                            for line in lines:
                                if query_lower in line.lower():
                                    snippet = line.strip()[:100]  # First 100 chars
                                    matches.append({
                                        "title": title,
                                        "area": area,
                                        "folder": folder_name,
                                        "filename": project_file.stem,
                                        "match_location": "content",
                                        "snippet": snippet
                                    })
                                    break  # Only include first match per file

        return {"matches": matches}

    def search_actions(
        self,
        query: str,
        include_states: list[str] | None = None,
        filter_project: str | None = None,
        filter_context: str | None = None
    ) -> dict:
        """
        Search for actions by text in action content.

        Args:
            query: Text to search for (case-insensitive)
            include_states: Which states to include (default: all)
            filter_project: Optional project filter (kebab-case filename)
            filter_context: Optional context filter (e.g., '@macbook')

        Returns:
            Dict with structure:
            {
                "matches": [
                    {
                        "action_text": "Do something",
                        "state": "next",
                        "context": "@macbook",
                        "project": "project-name",
                        "file": "@macbook.md",
                        "line": "- [ ] 2025-10-30 Do something @macbook +project"
                    }
                ]
            }
        """
        repo_path = Path(self._config.get_repo_path())
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

        # Default to all states
        if include_states is None:
            include_states = ["next", "waiting", "deferred", "incubating"]

        matches = []
        query_lower = query.lower()

        # Map states to file sections
        state_sections = {
            "next": "## Next",
            "waiting": "## Waiting",
            "deferred": "## Deferred",
            "incubating": "## Incubating"
        }

        # Helper to process action file
        def process_action_file(file_path: Path):
            with open(file_path, 'r') as f:
                lines = f.readlines()

            current_state = None
            for line in lines:
                # Check for state headers
                line_stripped = line.strip()
                for state, header in state_sections.items():
                    if line_stripped == header:
                        current_state = state
                        break

                # Skip if not in an included state
                if current_state not in include_states:
                    continue

                # Parse action lines
                if not line_stripped.startswith("- [ ]"):
                    continue

                # Check if query matches
                if query_lower not in line_stripped.lower():
                    continue

                # Extract metadata
                project_match = re.search(r'\+(\S+)', line_stripped)
                project = project_match.group(1) if project_match else None

                context_match = re.search(r'@(\S+)', line_stripped)
                context = f"@{context_match.group(1)}" if context_match else None

                # Apply filters
                if filter_project and project != filter_project:
                    continue
                if filter_context and context != filter_context:
                    continue

                # Extract action text
                text_match = re.match(
                    r'- \[ \] (?:\d{4}-\d{2}-\d{2} )?(.+?)(?:@|\+|due:|defer:|https?://|$)',
                    line_stripped
                )
                action_text = text_match.group(1).strip() if text_match else "..."

                matches.append({
                    "action_text": action_text,
                    "state": current_state,
                    "context": context,
                    "project": project,
                    "file": file_path.name,
                    "line": line_stripped
                })

        # Process context files
        contexts_dir = actions_base / "contexts"
        if contexts_dir.exists():
            for context_file in contexts_dir.glob("*.md"):
                process_action_file(context_file)

        # Process special state files
        for state in include_states:
            if state in ["waiting", "deferred", "incubating"]:
                state_file = actions_base / f"@{state}.md"
                if state_file.exists():
                    process_action_file(state_file)

        return {"matches": matches}
