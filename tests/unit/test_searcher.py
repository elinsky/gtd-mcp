"""Tests for project and action search functionality."""

import json
from pathlib import Path

import pytest

from execution_system_mcp.config import ConfigManager
from execution_system_mcp.searcher import Searcher


class TestSearcherSearchProjects:
    """Tests for searching projects by text."""

    def test_search_in_project_title(self, tmp_path):
        """
        Test searching finds matches in project titles.

        Given: Projects with various titles
        When: Searching for text that appears in title
        Then: Returns matching projects with title highlighted
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "exercise-routine.md").write_text("""---
area: Health
title: Daily Exercise Routine
type: standard
last_reviewed: 2025-10-30
---

# Daily Exercise Routine

Some content here.
""")

        (active_dir / "meditation.md").write_text("""---
area: Health
title: Meditation Practice
type: habit
last_reviewed: 2025-10-30
---

# Meditation Practice

Daily meditation routine.
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_projects("exercise")

        # Then
        assert len(result["matches"]) == 1
        match = result["matches"][0]
        assert match["title"] == "Daily Exercise Routine"
        assert match["filename"] == "exercise-routine"
        assert match["folder"] == "active"
        assert "title" in match["match_location"]

    def test_search_in_project_content(self, tmp_path):
        """
        Test searching finds matches in project content.

        Given: Projects with various content
        When: Searching for text that appears in content
        Then: Returns matching projects with content snippet
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "mission"
        active_dir.mkdir(parents=True)

        (active_dir / "project-a.md").write_text("""---
area: Mission
title: Project A
type: standard
last_reviewed: 2025-10-30
---

# Project A

This project involves building a Python web application.
""")

        (active_dir / "project-b.md").write_text("""---
area: Mission
title: Project B
type: standard
last_reviewed: 2025-10-30
---

# Project B

This is about JavaScript development.
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Mission", "kebab": "mission"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_projects("python")

        # Then
        assert len(result["matches"]) == 1
        match = result["matches"][0]
        assert match["title"] == "Project A"
        assert "content" in match["match_location"]
        assert "Python" in match["snippet"]

    def test_search_case_insensitive(self, tmp_path):
        """
        Test searching is case-insensitive.

        Given: Project with mixed case text
        When: Searching with different case
        Then: Returns match regardless of case
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "yoga.md").write_text("""---
area: Health
title: YOGA Practice
type: standard
last_reviewed: 2025-10-30
---

Content with YoGa mentioned.
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_projects("yoga")

        # Then
        assert len(result["matches"]) == 1  # Title (content skipped to avoid duplicates)
        assert result["matches"][0]["match_location"] == "title"

    def test_filter_by_folder(self, tmp_path):
        """
        Test filtering search results by folder.

        Given: Projects in different folders with same search term
        When: Searching with folder filter
        Then: Returns only matches from specified folder
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)
        (active_dir / "active-project.md").write_text("""---
area: Health
title: Active Fitness
type: standard
last_reviewed: 2025-10-30
---

Fitness content.
""")

        incubator_dir = projects_base / "incubator" / "health"
        incubator_dir.mkdir(parents=True)
        (incubator_dir / "incubator-project.md").write_text("""---
area: Health
title: Future Fitness
type: standard
last_reviewed: 2025-10-30
---

Fitness ideas.
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_projects("fitness", folder="active")

        # Then
        assert len(result["matches"]) == 1
        assert result["matches"][0]["title"] == "Active Fitness"

    def test_filter_by_area(self, tmp_path):
        """
        Test filtering search results by area.

        Given: Projects in different areas with same search term
        When: Searching with area filter
        Then: Returns only matches from specified area
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        health_dir = projects_base / "active" / "health"
        health_dir.mkdir(parents=True)
        (health_dir / "health-project.md").write_text("""---
area: Health
title: Health Goals
type: standard
last_reviewed: 2025-10-30
---

Content about goals.
""")

        mission_dir = projects_base / "active" / "mission"
        mission_dir.mkdir(parents=True)
        (mission_dir / "mission-project.md").write_text("""---
area: Mission
title: Mission Goals
type: standard
last_reviewed: 2025-10-30
---

Content about goals.
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Mission", "kebab": "mission"}
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_projects("goals", filter_area="health")

        # Then
        assert len(result["matches"]) == 1
        assert result["matches"][0]["area"] == "Health"

    def test_no_matches_returns_empty(self, tmp_path):
        """
        Test searching with no matches returns empty list.

        Given: Projects without search term
        When: Searching for non-existent term
        Then: Returns empty matches list
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "project.md").write_text("""---
area: Health
title: Some Project
type: standard
last_reviewed: 2025-10-30
---

Content here.
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_projects("nonexistent")

        # Then
        assert len(result["matches"]) == 0


class TestSearcherSearchActions:
    """Tests for searching actions by text."""

    def test_search_in_action_text(self, tmp_path):
        """
        Test searching finds matches in action text.

        Given: Actions with various text
        When: Searching for text that appears in action
        Then: Returns matching actions
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-30
---

## Next
- [ ] 2025-10-30 Write Python tests @macbook +project-a
- [ ] 2025-10-30 Review JavaScript code @macbook +project-b
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_actions("python")

        # Then
        assert len(result["matches"]) == 1
        match = result["matches"][0]
        assert "Python" in match["action_text"]
        assert match["state"] == "next"
        assert match["file"] == "@macbook.md"

    def test_search_case_insensitive_actions(self, tmp_path):
        """
        Test action searching is case-insensitive.

        Given: Action with mixed case text
        When: Searching with different case
        Then: Returns match regardless of case
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@phone.md").write_text("""---
title: Phone
last_reviewed: 2025-10-30
---

## Next
- [ ] 2025-10-30 Call DOCTOR about appointment @phone
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_actions("doctor")

        # Then
        assert len(result["matches"]) == 1

    def test_filter_actions_by_state(self, tmp_path):
        """
        Test filtering action search by state.

        Given: Actions in different states with same search term
        When: Searching with state filter
        Then: Returns only matches from specified states
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-30
---

## Next
- [ ] 2025-10-30 Review code @macbook +project-a

## Waiting
- [ ] 2025-10-30 Review feedback from team @waiting @macbook +project-a
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_actions("review", include_states=["next"])

        # Then
        assert len(result["matches"]) == 1
        assert result["matches"][0]["state"] == "next"

    def test_filter_actions_by_project(self, tmp_path):
        """
        Test filtering action search by project.

        Given: Actions for different projects with same search term
        When: Searching with project filter
        Then: Returns only matches for specified project
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-30
---

## Next
- [ ] 2025-10-30 Write tests @macbook +project-a
- [ ] 2025-10-30 Write tests @macbook +project-b
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_actions("tests", filter_project="project-a")

        # Then
        assert len(result["matches"]) == 1
        assert result["matches"][0]["project"] == "project-a"

    def test_filter_actions_by_context(self, tmp_path):
        """
        Test filtering action search by context.

        Given: Actions in different contexts with same search term
        When: Searching with context filter
        Then: Returns only matches for specified context
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-30
---

## Next
- [ ] 2025-10-30 Email client @macbook +project-a
""")

        (contexts_dir / "@phone.md").write_text("""---
title: Phone
last_reviewed: 2025-10-30
---

## Next
- [ ] 2025-10-30 Email office @phone +project-a
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_actions("email", filter_context="@phone")

        # Then
        assert len(result["matches"]) == 1
        assert result["matches"][0]["context"] == "@phone"

    def test_no_action_matches_returns_empty(self, tmp_path):
        """
        Test searching actions with no matches returns empty list.

        Given: Actions without search term
        When: Searching for non-existent term
        Then: Returns empty matches list
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-30
---

## Next
- [ ] 2025-10-30 Do something @macbook +project-a
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        searcher = Searcher(config)

        # When
        result = searcher.search_actions("nonexistent")

        # Then
        assert len(result["matches"]) == 0
