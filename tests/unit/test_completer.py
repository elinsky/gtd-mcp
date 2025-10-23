"""Tests for ProjectCompleter class."""

import pytest
from pathlib import Path
from datetime import date
from gtd_mcp.completer import ProjectCompleter
from gtd_mcp.config import ConfigManager


class TestProjectCompleterFindActiveProject:
    """Tests for ProjectCompleter.find_active_project method."""

    def test_finds_project_in_area_subdirectory(self, tmp_path):
        """
        Given a project file exists in active/health/
        When find_active_project is called with the title
        Then the project path and area are returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [
                {"name": "Health", "kebab": "health"}
            ]
        }""" % str(tmp_path))

        active_health = tmp_path / "docs/execution_system/10k-projects/active/health"
        active_health.mkdir(parents=True)
        project_file = active_health / "upgrade-anbernic-sd-cards.md"
        project_file.write_text("""---
area: Health
title: Upgrade Anbernic SD Cards
type: standard
created: 2025-10-20
started: 2025-10-20
last_reviewed: 2025-10-20
---

# Content
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.find_active_project("Upgrade Anbernic SD Cards")

        # Then
        assert result == (project_file, "health")

    def test_returns_none_for_nonexistent_project(self, tmp_path):
        """
        Given no project file exists with the title
        When find_active_project is called
        Then None and error message are returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [
                {"name": "Health", "kebab": "health"}
            ]
        }""" % str(tmp_path))

        active_health = tmp_path / "docs/execution_system/10k-projects/active/health"
        active_health.mkdir(parents=True)

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.find_active_project("Nonexistent Project")

        # Then
        assert result[0] is None
        assert "not found" in result[1].lower()

    def test_returns_error_for_project_in_completed(self, tmp_path):
        """
        Given a project file exists in completed/health/
        When find_active_project is called
        Then None and error message are returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [
                {"name": "Health", "kebab": "health"}
            ]
        }""" % str(tmp_path))

        completed_health = tmp_path / "docs/execution_system/10k-projects/completed/health"
        completed_health.mkdir(parents=True)
        project_file = completed_health / "old-project.md"
        project_file.write_text("""---
area: Health
title: Old Project
---
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.find_active_project("Old Project")

        # Then
        assert result[0] is None
        assert "already completed" in result[1].lower() or "not active" in result[1].lower()

    def test_returns_error_for_project_in_incubator(self, tmp_path):
        """
        Given a project file exists in incubator/health/
        When find_active_project is called
        Then None and error message are returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [
                {"name": "Health", "kebab": "health"}
            ]
        }""" % str(tmp_path))

        incubator_health = tmp_path / "docs/execution_system/10k-projects/incubator/health"
        incubator_health.mkdir(parents=True)
        project_file = incubator_health / "future-project.md"
        project_file.write_text("""---
area: Health
title: Future Project
---
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.find_active_project("Future Project")

        # Then
        assert result[0] is None
        assert "not active" in result[1].lower() or "incubating" in result[1].lower()

    def test_handles_multiple_areas(self, tmp_path):
        """
        Given projects exist in multiple area subdirectories
        When find_active_project is called with a title
        Then the correct project is found in its area
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"}
            ]
        }""" % str(tmp_path))

        active_health = tmp_path / "docs/execution_system/10k-projects/active/health"
        active_health.mkdir(parents=True)
        health_project = active_health / "health-project.md"
        health_project.write_text("""---
area: Health
title: Health Project
---
""")

        active_career = tmp_path / "docs/execution_system/10k-projects/active/career"
        active_career.mkdir(parents=True)
        career_project = active_career / "career-project.md"
        career_project.write_text("""---
area: Career
title: Career Project
---
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.find_active_project("Career Project")

        # Then
        assert result == (career_project, "career")
