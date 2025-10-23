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


class TestProjectCompleterCheck0kBlockers:
    """Tests for ProjectCompleter.check_0k_blockers method."""

    def test_no_blockers_returns_empty_list(self, tmp_path):
        """
        Given no 0k files contain the project tag
        When check_0k_blockers is called
        Then an empty list is returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [{"name": "Health", "kebab": "health"}]
        }""" % str(tmp_path))

        next_actions_dir = tmp_path / "docs/execution_system/00k-next-actions"
        next_actions_dir.mkdir(parents=True)

        waiting_file = next_actions_dir / "@waiting.md"
        waiting_file.write_text("""---
title: Waiting For
---

- [ ] 2025-10-22 Someone to do something +other-project
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.check_0k_blockers("my-project")

        # Then
        assert result == []

    def test_finds_blocker_in_waiting(self, tmp_path):
        """
        Given @waiting.md contains an open item with the project tag
        When check_0k_blockers is called
        Then a list with the blocking item is returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [{"name": "Health", "kebab": "health"}]
        }""" % str(tmp_path))

        next_actions_dir = tmp_path / "docs/execution_system/00k-next-actions"
        next_actions_dir.mkdir(parents=True)

        waiting_file = next_actions_dir / "@waiting.md"
        waiting_file.write_text("""---
title: Waiting For
---

- [ ] 2025-10-22 Tina to receive Amazon package +my-project
- [ ] 2025-10-21 Something else +other-project
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.check_0k_blockers("my-project")

        # Then
        assert len(result) == 1
        assert result[0]["file"] == "@waiting.md"
        assert "Tina to receive Amazon package" in result[0]["line"]

    def test_finds_blocker_in_incubating(self, tmp_path):
        """
        Given @incubating.md contains an open item with the project tag
        When check_0k_blockers is called
        Then a list with the blocking item is returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [{"name": "Health", "kebab": "health"}]
        }""" % str(tmp_path))

        next_actions_dir = tmp_path / "docs/execution_system/00k-next-actions"
        next_actions_dir.mkdir(parents=True)

        incubating_file = next_actions_dir / "@incubating.md"
        incubating_file.write_text("""---
title: Incubating
---

- [ ] 2025-09-12 Text Samarth to get coffee +my-project
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.check_0k_blockers("my-project")

        # Then
        assert len(result) == 1
        assert result[0]["file"] == "@incubating.md"
        assert "Text Samarth" in result[0]["line"]

    def test_finds_blocker_in_deferred(self, tmp_path):
        """
        Given @deferred.md contains an open item with the project tag
        When check_0k_blockers is called
        Then a list with the blocking item is returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [{"name": "Health", "kebab": "health"}]
        }""" % str(tmp_path))

        next_actions_dir = tmp_path / "docs/execution_system/00k-next-actions"
        next_actions_dir.mkdir(parents=True)

        deferred_file = next_actions_dir / "@deferred.md"
        deferred_file.write_text("""---
title: Deferred
---

- [ ] 2025-10-23 Pick up dry cleaning +my-project defer:2025-10-28
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.check_0k_blockers("my-project")

        # Then
        assert len(result) == 1
        assert result[0]["file"] == "@deferred.md"
        assert "Pick up dry cleaning" in result[0]["line"]

    def test_finds_blocker_in_context_file(self, tmp_path):
        """
        Given a contexts/*.md file contains an open item with the project tag
        When check_0k_blockers is called
        Then a list with the blocking item is returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [{"name": "Health", "kebab": "health"}]
        }""" % str(tmp_path))

        contexts_dir = tmp_path / "docs/execution_system/00k-next-actions/contexts"
        contexts_dir.mkdir(parents=True)

        personal_file = contexts_dir / "personal.md"
        personal_file.write_text("""---
title: Personal Context
---

- [ ] 2025-10-20 Do the thing @home +my-project
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.check_0k_blockers("my-project")

        # Then
        assert len(result) == 1
        assert result[0]["file"] == "contexts/personal.md"
        assert "Do the thing" in result[0]["line"]

    def test_finds_multiple_blockers_across_files(self, tmp_path):
        """
        Given multiple 0k files contain open items with the project tag
        When check_0k_blockers is called
        Then a list with all blocking items is returned
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [{"name": "Health", "kebab": "health"}]
        }""" % str(tmp_path))

        next_actions_dir = tmp_path / "docs/execution_system/00k-next-actions"
        next_actions_dir.mkdir(parents=True)

        waiting_file = next_actions_dir / "@waiting.md"
        waiting_file.write_text("""---
title: Waiting For
---

- [ ] 2025-10-22 Wait for thing +my-project
""")

        deferred_file = next_actions_dir / "@deferred.md"
        deferred_file.write_text("""---
title: Deferred
---

- [ ] 2025-10-23 Deferred task +my-project
""")

        contexts_dir = next_actions_dir / "contexts"
        contexts_dir.mkdir(parents=True)
        personal_file = contexts_dir / "personal.md"
        personal_file.write_text("""---
title: Personal
---

- [ ] 2025-10-20 Next action +my-project
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.check_0k_blockers("my-project")

        # Then
        assert len(result) == 3

    def test_ignores_completed_items(self, tmp_path):
        """
        Given completed.md contains items with the project tag
        When check_0k_blockers is called
        Then those items are not included in the result
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [{"name": "Health", "kebab": "health"}]
        }""" % str(tmp_path))

        next_actions_dir = tmp_path / "docs/execution_system/00k-next-actions"
        next_actions_dir.mkdir(parents=True)

        completed_file = next_actions_dir / "completed.md"
        completed_file.write_text("""---
title: Completed
---

- [ ] 2025-10-20 Completed task +my-project
- [x] 2025-10-19 Another completed task +my-project
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.check_0k_blockers("my-project")

        # Then
        assert result == []

    def test_ignores_checked_items(self, tmp_path):
        """
        Given @waiting.md contains a checked item with the project tag
        When check_0k_blockers is called
        Then the checked item is not included in the result
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("""{
            "gtd_repo_path": "%s",
            "areas": [{"name": "Health", "kebab": "health"}]
        }""" % str(tmp_path))

        next_actions_dir = tmp_path / "docs/execution_system/00k-next-actions"
        next_actions_dir.mkdir(parents=True)

        waiting_file = next_actions_dir / "@waiting.md"
        waiting_file.write_text("""---
title: Waiting For
---

- [x] 2025-10-22 Done waiting +my-project
- [ ] 2025-10-21 Still waiting +other-project
""")

        config = ConfigManager(str(config_file))
        completer = ProjectCompleter(config)

        # When
        result = completer.check_0k_blockers("my-project")

        # Then
        assert result == []
