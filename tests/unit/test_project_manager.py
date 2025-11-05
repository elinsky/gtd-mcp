"""Tests for ProjectManager (Phase 2 tools)."""

import json
from datetime import date
from pathlib import Path

import pytest

from execution_system_mcp.config import ConfigManager
from execution_system_mcp.project_manager import ProjectManager


class TestProjectManagerActivateProject:
    """Test ProjectManager.activate_project()."""

    def test_activate_project_success(self, tmp_path):
        """
        Test successfully activating an incubator project.

        Given: Project in incubator folder
        When: Calling activate_project()
        Then: Moves to active folder and adds started date
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        incubator_dir = projects_base / "incubator" / "health"
        incubator_dir.mkdir(parents=True)

        project_file = incubator_dir / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
type: standard
created: 2025-01-01
last_reviewed: 2025-01-01
---
# Test Project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.activate_project("Test Project")

        # Then
        assert "Successfully activated" in result

        # Check file moved
        active_file = projects_base / "active" / "health" / "test-project.md"
        assert active_file.exists()
        assert not project_file.exists()

        # Check started date added
        content = active_file.read_text()
        assert f"started: {date.today().isoformat()}" in content

    def test_activate_project_not_in_incubator(self, tmp_path):
        """
        Test error when project not in incubator.

        Given: Project in active folder
        When: Calling activate_project()
        Then: Returns error message
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "test-project.md").write_text("""---
area: Health
title: Test Project
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.activate_project("Test Project")

        # Then
        assert "Error" in result
        assert "not found in incubator" in result


class TestProjectManagerMoveToIncubator:
    """Test ProjectManager.move_project_to_incubator()."""

    def test_move_to_incubator_success(self, tmp_path):
        """
        Test successfully moving active project to incubator.

        Given: Active project with no 0k actions
        When: Calling move_project_to_incubator()
        Then: Moves to incubator and removes started date
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        project_file = active_dir / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
type: standard
created: 2025-01-01
started: 2025-01-15
last_reviewed: 2025-01-01
---
# Test Project
""")

        # Create empty actions directory (no blockers)
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("---\ntitle: Macbook\n---\n")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.move_project_to_incubator("Test Project")

        # Then
        assert "Successfully moved" in result

        # Check file moved
        incubator_file = projects_base / "incubator" / "health" / "test-project.md"
        assert incubator_file.exists()
        assert not project_file.exists()

        # Check started date removed
        content = incubator_file.read_text()
        assert "started:" not in content

    def test_move_to_incubator_with_blockers(self, tmp_path):
        """
        Test error when project has 0k actions.

        Given: Active project with next actions
        When: Calling move_project_to_incubator()
        Then: Returns error with blocking items
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "test-project.md").write_text("""---
area: Health
title: Test Project
type: standard
---
""")

        # Create action that blocks
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
---

- [ ] 2025-10-30 Do something @macbook +test-project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.move_project_to_incubator("Test Project")

        # Then
        assert "Error" in result
        assert "has incomplete 0k actions" in result


class TestProjectManagerDescopeProject:
    """Test ProjectManager.descope_project()."""

    def test_descope_project_success(self, tmp_path):
        """
        Test successfully descoping a project.

        Given: Project with no 0k actions
        When: Calling descope_project()
        Then: Moves to descoped folder and adds descoped date
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        project_file = active_dir / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
type: standard
created: 2025-01-01
started: 2025-01-15
last_reviewed: 2025-01-01
---
# Test Project
""")

        # Create empty actions directory
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("---\ntitle: Macbook\n---\n")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.descope_project("Test Project")

        # Then
        assert "Successfully descoped" in result

        # Check file moved
        descoped_file = projects_base / "descoped" / "health" / "test-project.md"
        assert descoped_file.exists()
        assert not project_file.exists()

        # Check descoped date added and started removed
        content = descoped_file.read_text()
        assert f"descoped: {date.today().isoformat()}" in content
        assert "started:" not in content

    def test_descope_creates_folder(self, tmp_path):
        """
        Test that descope creates descoped folder if needed.

        Given: No descoped folder exists
        When: Calling descope_project()
        Then: Creates descoped/{area}/ folder
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        incubator_dir = projects_base / "incubator" / "health"
        incubator_dir.mkdir(parents=True)

        (incubator_dir / "test-project.md").write_text("""---
area: Health
title: Test Project
type: standard
---
""")

        # Create empty actions directory
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("---\ntitle: Macbook\n---\n")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.descope_project("Test Project")

        # Then
        assert "Successfully descoped" in result
        descoped_dir = projects_base / "descoped" / "health"
        assert descoped_dir.exists()


class TestProjectManagerUpdateDueDate:
    """Test ProjectManager.update_project_due_date()."""

    def test_add_due_date(self, tmp_path):
        """
        Test adding a due date to a project.

        Given: Project without due date
        When: Calling update_project_due_date()
        Then: Adds due date to YAML frontmatter
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        project_file = active_dir / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
type: standard
created: 2025-01-01
started: 2025-01-15
last_reviewed: 2025-01-01
---
# Test Project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.update_project_due_date("Test Project", "2025-12-31")

        # Then
        assert "Successfully updated due date" in result
        content = project_file.read_text()
        assert "due: 2025-12-31" in content

    def test_remove_due_date(self, tmp_path):
        """
        Test removing a due date from a project.

        Given: Project with due date
        When: Calling update_project_due_date(None)
        Then: Removes due date from YAML
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        project_file = active_dir / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
type: standard
created: 2025-01-01
started: 2025-01-15
last_reviewed: 2025-01-01
due: 2025-12-31
---
# Test Project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.update_project_due_date("Test Project", None)

        # Then
        assert "Successfully removed due date" in result
        content = project_file.read_text()
        assert "due:" not in content


class TestProjectManagerUpdateArea:
    """Test ProjectManager.update_project_area()."""

    def test_update_area_moves_file(self, tmp_path):
        """
        Test updating project area moves file to new folder.

        Given: Project in Health area
        When: Calling update_project_area("Career")
        Then: Moves file to career folder and updates YAML
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_health_dir = projects_base / "active" / "health"
        active_health_dir.mkdir(parents=True)

        active_career_dir = projects_base / "active" / "career"
        active_career_dir.mkdir(parents=True)

        project_file = active_health_dir / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
type: standard
created: 2025-01-01
started: 2025-01-15
last_reviewed: 2025-01-01
---
# Test Project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"}
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.update_project_area("Test Project", "Career")

        # Then
        assert "Successfully updated area" in result

        # Check file moved
        new_file = active_career_dir / "test-project.md"
        assert new_file.exists()
        assert not project_file.exists()

        # Check area updated
        content = new_file.read_text()
        assert "area: Career" in content


class TestProjectManagerUpdateType:
    """Test ProjectManager.update_project_type()."""

    def test_update_type(self, tmp_path):
        """
        Test updating project type.

        Given: Standard project
        When: Calling update_project_type("habit")
        Then: Updates type in YAML
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        project_file = active_dir / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
type: standard
created: 2025-01-01
started: 2025-01-15
last_reviewed: 2025-01-01
---
# Test Project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.update_project_type("Test Project", "habit")

        # Then
        assert "Successfully updated type" in result
        content = project_file.read_text()
        assert "type: habit" in content


class TestProjectManagerUpdateReviewDates:
    """Test ProjectManager.update_review_dates()."""

    def test_update_all_active_projects(self, tmp_path):
        """
        Test updating review dates for all active projects.

        Given: Multiple active projects
        When: Calling update_review_dates(target_type="projects", filter_folder="active")
        Then: Updates last_reviewed for all active projects
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "project-1.md").write_text("""---
area: Health
title: Project 1
type: standard
last_reviewed: 2025-01-01
---
""")
        (active_dir / "project-2.md").write_text("""---
area: Health
title: Project 2
type: standard
last_reviewed: 2025-01-01
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.update_review_dates(target_type="projects", filter_folder="active")

        # Then
        assert "Successfully updated review dates" in result
        assert "2 items" in result

        # Check both files updated
        today = date.today().isoformat()
        assert f"last_reviewed: {today}" in (active_dir / "project-1.md").read_text()
        assert f"last_reviewed: {today}" in (active_dir / "project-2.md").read_text()

    def test_update_specific_action_lists(self, tmp_path):
        """
        Test updating review dates for specific action lists.

        Given: Multiple action list files
        When: Calling update_review_dates with filter_names
        Then: Updates only specified files
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-01-01
---
""")
        (contexts_dir / "@phone.md").write_text("""---
title: Phone
last_reviewed: 2025-01-01
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.update_review_dates(
            target_type="actions",
            filter_names=["@macbook"]
        )

        # Then
        assert "Successfully updated review dates" in result
        assert "1 item" in result

        # Check only @macbook updated
        today = date.today().isoformat()
        assert f"last_reviewed: {today}" in (contexts_dir / "@macbook.md").read_text()
        assert "last_reviewed: 2025-01-01" in (contexts_dir / "@phone.md").read_text()

    def test_update_by_area(self, tmp_path):
        """
        Test updating review dates filtered by area.

        Given: Projects in multiple areas
        When: Calling update_review_dates with filter_area
        Then: Updates only projects in specified area
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        active_health_dir = projects_base / "active" / "health"
        active_health_dir.mkdir(parents=True)
        (active_health_dir / "health-project.md").write_text("""---
area: Health
title: Health Project
type: standard
last_reviewed: 2025-01-01
---
""")

        active_career_dir = projects_base / "active" / "career"
        active_career_dir.mkdir(parents=True)
        (active_career_dir / "career-project.md").write_text("""---
area: Career
title: Career Project
type: standard
last_reviewed: 2025-01-01
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"}
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        manager = ProjectManager(config)

        # When
        result = manager.update_review_dates(
            target_type="projects",
            filter_area="Health"
        )

        # Then
        assert "Successfully updated review dates" in result

        # Check only Health updated
        today = date.today().isoformat()
        assert f"last_reviewed: {today}" in (active_health_dir / "health-project.md").read_text()
        assert "last_reviewed: 2025-01-01" in (active_career_dir / "career-project.md").read_text()
