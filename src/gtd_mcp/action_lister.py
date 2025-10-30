"""Action listing functionality."""

import re
from pathlib import Path
from typing import Literal

from gtd_mcp.config import ConfigManager


class ActionLister:
    """Lists and formats GTD actions."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize lister with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config

    @staticmethod
    def parse_action(line: str, state: str) -> dict:
        """
        Parse action line from todo.txt format.

        Args:
            line: Action line like "- [ ] 2025-10-30 Text @context +project due:date"
            state: Action state (next, waiting, deferred, incubating)

        Returns:
            Dict with parsed action metadata
        """
        # Extract checkbox and remainder
        match = re.match(r'^- \[ \] (.+)$', line)
        if not match:
            return None

        remainder = match.group(1)

        # Extract date (YYYY-MM-DD at start)
        date_match = re.match(r'^(\d{4}-\d{2}-\d{2}) (.+)$', remainder)
        if date_match:
            date = date_match.group(1)
            remainder = date_match.group(2)
        else:
            date = None
            remainder = remainder

        # Extract context (@context)
        context_match = re.search(r'@(\S+)', remainder)
        context = f"@{context_match.group(1)}" if context_match else None

        # Extract project (+project)
        project_match = re.search(r'\+(\S+)', remainder)
        project = project_match.group(1) if project_match else None

        # Extract due date (due:YYYY-MM-DD)
        due_match = re.search(r'due:(\d{4}-\d{2}-\d{2})', remainder)
        due = due_match.group(1) if due_match else None

        # Extract defer date (defer:YYYY-MM-DD)
        defer_match = re.search(r'defer:(\d{4}-\d{2}-\d{2})', remainder)
        defer = defer_match.group(1) if defer_match else None

        # Clean text: remove date, context, project tags, due/defer tags
        # But keep URLs
        text = remainder
        if date:
            text = re.sub(r'^\d{4}-\d{2}-\d{2}\s+', '', text)
        text = re.sub(r'@\S+\s*', '', text)
        text = re.sub(r'\+\S+\s*', '', text)
        text = re.sub(r'due:\d{4}-\d{2}-\d{2}\s*', '', text)
        text = re.sub(r'defer:\d{4}-\d{2}-\d{2}\s*', '', text)
        text = text.strip()

        return {
            "text": text,
            "date": date,
            "context": context,
            "project": project,
            "due": due,
            "defer": defer,
            "state": state
        }

    def _collect_all_actions(self, include_states: list[str]) -> list[dict]:
        """
        Collect all actions from action files.

        Args:
            include_states: Which states to include (next, waiting, deferred, incubating)

        Returns:
            List of action dicts
        """
        repo_path = Path(self._config.get_repo_path())
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"

        all_actions = []

        # Collect from context files (next actions)
        if "next" in include_states:
            contexts_dir = actions_base / "contexts"
            if contexts_dir.exists():
                for context_file in contexts_dir.glob("*.md"):
                    if not context_file.is_file():
                        continue

                    with open(context_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("- [ ]"):
                                action = self.parse_action(line, "next")
                                if action:
                                    all_actions.append(action)

        # Collect from special state files
        state_files = {
            "waiting": "@waiting.md",
            "deferred": "@deferred.md",
            "incubating": "@incubating.md"
        }

        for state, filename in state_files.items():
            if state in include_states:
                state_file = actions_base / filename
                if state_file.exists():
                    with open(state_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("- [ ]"):
                                action = self.parse_action(line, state)
                                if action:
                                    all_actions.append(action)

        return all_actions

    def _get_project_info(self, project_filename: str) -> dict | None:
        """
        Get project metadata (title, folder, area).

        Args:
            project_filename: Project filename (kebab-case without .md)

        Returns:
            Dict with project info or None if not found
        """
        repo_path = Path(self._config.get_repo_path())
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        # Search in all folders
        for folder in ["active", "incubator", "completed"]:
            folder_path = projects_base / folder
            if not folder_path.exists():
                continue

            for area_dict in self._config.get_areas():
                area_name = area_dict["name"]
                area_kebab = area_dict["kebab"]
                area_dir = folder_path / area_kebab

                if not area_dir.exists():
                    continue

                project_file = area_dir / f"{project_filename}.md"
                if project_file.exists():
                    # Parse title from YAML
                    with open(project_file, 'r') as f:
                        for line in f.readlines()[:10]:
                            if line.strip().startswith("title:"):
                                title = line.split(":", 1)[1].strip()
                                return {
                                    "title": title,
                                    "folder": folder,
                                    "area": area_name,
                                    "filename": project_filename
                                }
                    # Fallback to filename if no title found
                    return {
                        "title": project_filename,
                        "folder": folder,
                        "area": area_name,
                        "filename": project_filename
                    }

        return None

    def list_actions(
        self,
        group_by: Literal["project", "context", "flat"] = "project",
        include_states: list[str] | None = None,
        filter_project: str | None = None,
        filter_context: str | None = None,
    ) -> dict:
        """
        List actions with flexible filtering and grouping.

        Args:
            group_by: How to group actions (default: "project")
            include_states: Which states to include (default: all)
            filter_project: Optional project filter (filename)
            filter_context: Optional context filter (e.g., "@macbook")

        Returns:
            Dict with grouped actions
        """
        # Default to all states
        if include_states is None:
            include_states = ["next", "waiting", "deferred", "incubating"]

        # Collect all actions
        all_actions = self._collect_all_actions(include_states)

        # Apply filters
        if filter_project:
            all_actions = [a for a in all_actions if a["project"] == filter_project]

        if filter_context:
            all_actions = [a for a in all_actions if a["context"] == filter_context]

        # Group according to mode
        if group_by == "project":
            return self._group_by_project(all_actions)
        elif group_by == "context":
            return self._group_by_context(all_actions)
        else:  # flat
            return self._group_flat(all_actions)

    def _group_by_project(self, actions: list[dict]) -> dict:
        """
        Group actions by project folder, then project, then state.

        Returns structure:
        {
            "groups": [
                {
                    "group_name": "Active Projects",
                    "projects": [
                        {
                            "project_name": "ML Refresh",
                            "project_filename": "ml-refresh",
                            "project_folder": "active",
                            "project_area": "Career",
                            "states": [
                                {
                                    "state": "next",
                                    "actions": [...]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """
        # Build project info for all actions
        projects_map = {}  # filename -> info
        for action in actions:
            if action["project"] and action["project"] not in projects_map:
                info = self._get_project_info(action["project"])
                if info:
                    projects_map[action["project"]] = info

        # Organize by folder -> project -> state
        folder_groups = {
            "active": [],
            "incubator": []
        }

        # Group actions by project and state
        for action in actions:
            project_filename = action["project"]
            if not project_filename or project_filename not in projects_map:
                continue

            project_info = projects_map[project_filename]
            folder = project_info["folder"]

            if folder not in ["active", "incubator"]:
                continue

            # Find or create project entry
            project_entry = None
            for p in folder_groups[folder]:
                if p["project_filename"] == project_filename:
                    project_entry = p
                    break

            if not project_entry:
                project_entry = {
                    "project_name": project_info["title"],
                    "project_filename": project_filename,
                    "project_folder": folder,
                    "project_area": project_info["area"],
                    "states": []
                }
                folder_groups[folder].append(project_entry)

            # Find or create state entry
            state_entry = None
            for s in project_entry["states"]:
                if s["state"] == action["state"]:
                    state_entry = s
                    break

            if not state_entry:
                state_entry = {
                    "state": action["state"],
                    "actions": []
                }
                project_entry["states"].append(state_entry)

            state_entry["actions"].append(action)

        # Sort projects alphabetically within each folder
        for folder in folder_groups.values():
            folder.sort(key=lambda p: p["project_name"])

        # Build final groups structure
        groups = []
        if folder_groups["active"]:
            groups.append({
                "group_name": "Active Projects",
                "projects": folder_groups["active"]
            })
        if folder_groups["incubator"]:
            groups.append({
                "group_name": "Incubator Projects",
                "projects": folder_groups["incubator"]
            })

        return {"groups": groups}

    def _group_by_context(self, actions: list[dict]) -> dict:
        """
        Group actions by context.

        Returns structure:
        {
            "groups": [
                {
                    "group_name": "@macbook",
                    "actions": [...]
                }
            ]
        }
        """
        # Organize by context
        context_map = {}

        for action in actions:
            context = action["context"]
            if not context:
                continue

            if context not in context_map:
                context_map[context] = []

            context_map[context].append(action)

        # Sort contexts alphabetically
        sorted_contexts = sorted(context_map.keys())

        groups = []
        for context in sorted_contexts:
            groups.append({
                "group_name": context,
                "actions": context_map[context]
            })

        return {"groups": groups}

    def _group_flat(self, actions: list[dict]) -> dict:
        """
        Return all actions in a single flat list.

        Returns structure:
        {
            "groups": [
                {
                    "group_name": "All Actions",
                    "actions": [...]
                }
            ]
        }
        """
        return {
            "groups": [
                {
                    "group_name": "All Actions",
                    "actions": actions
                }
            ]
        }
