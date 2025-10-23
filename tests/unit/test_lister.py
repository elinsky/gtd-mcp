"""Tests for ProjectLister."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from gtd_mcp.config import ConfigManager
from gtd_mcp.lister import ProjectLister


class TestProjectListerParseYaml:
    """Test ProjectLister YAML frontmatter parsing."""

    def test_parse_all_fields(self, tmp_path):
        """
        Test parsing all YAML fields from project file.

        Given: Project file with all YAML fields
        When: Calling parse_yaml_frontmatter()
        Then: Returns dict with area, title, type, due
        """
        # Given
        project_file = tmp_path / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
type: standard
created: 2025-01-01
started: 2025-01-01
last_reviewed: 2025-01-01
due: 2025-12-31
---
# Test Project
""")

        # When
        result = ProjectLister.parse_yaml_frontmatter(project_file)

        # Then
        assert result["area"] == "Health"
        assert result["title"] == "Test Project"
        assert result["type"] == "standard"
        assert result["due"] == "2025-12-31"

    def test_parse_without_due(self, tmp_path):
        """
        Test parsing without due date.

        Given: Project file without due field
        When: Calling parse_yaml_frontmatter()
        Then: Returns dict with due as None
        """
        # Given
        project_file = tmp_path / "test-project.md"
        project_file.write_text("""---
area: Career
title: No Due Date Project
type: habit
---
# No Due Date Project
""")

        # When
        result = ProjectLister.parse_yaml_frontmatter(project_file)

        # Then
        assert result["area"] == "Career"
        assert result["title"] == "No Due Date Project"
        assert result["type"] == "habit"
        assert result["due"] is None

    def test_parse_without_title(self, tmp_path):
        """
        Test parsing without title uses filename.

        Given: Project file without title field
        When: Calling parse_yaml_frontmatter()
        Then: Returns filename (without .md) as title
        """
        # Given
        project_file = tmp_path / "my-test-project.md"
        project_file.write_text("""---
area: Mission
type: coordination
---
# Project without title in YAML
""")

        # When
        result = ProjectLister.parse_yaml_frontmatter(project_file)

        # Then
        assert result["title"] == "my-test-project"
        assert result["area"] == "Mission"
        assert result["type"] == "coordination"


class TestProjectListerFormatDueDate:
    """Test ProjectLister due date formatting."""

    def test_no_due_date(self):
        """
        Test formatting when no due date.

        Given: due_date is None
        When: Calling format_due_date(None)
        Then: Returns empty string
        """
        # Given
        due_date = None

        # When
        result = ProjectLister.format_due_date(due_date)

        # Then
        assert result == ""

    def test_overdue_date(self):
        """
        Test formatting overdue date.

        Given: due_date is 5 days in the past
        When: Calling format_due_date()
        Then: Returns formatted string with OVERDUE and days
        """
        # Given
        due_date = (date.today() - timedelta(days=5)).isoformat()

        # When
        result = ProjectLister.format_due_date(due_date)

        # Then
        assert "OVERDUE" in result
        assert "5d" in result
        assert due_date in result

    def test_today_date(self):
        """
        Test formatting date due today.

        Given: due_date is today
        When: Calling format_due_date()
        Then: Returns formatted string with TODAY!
        """
        # Given
        due_date = date.today().isoformat()

        # When
        result = ProjectLister.format_due_date(due_date)

        # Then
        assert "TODAY!" in result
        assert due_date in result

    def test_upcoming_within_7_days(self):
        """
        Test formatting date within 7 days.

        Given: due_date is 3 days from now
        When: Calling format_due_date()
        Then: Returns formatted string with days remaining
        """
        # Given
        due_date = (date.today() + timedelta(days=3)).isoformat()

        # When
        result = ProjectLister.format_due_date(due_date)

        # Then
        assert "3d" in result
        assert due_date in result
        assert "OVERDUE" not in result

    def test_upcoming_beyond_7_days(self):
        """
        Test formatting date beyond 7 days.

        Given: due_date is 30 days from now
        When: Calling format_due_date()
        Then: Returns formatted string with days remaining
        """
        # Given
        due_date = (date.today() + timedelta(days=30)).isoformat()

        # When
        result = ProjectLister.format_due_date(due_date)

        # Then
        assert "30d" in result
        assert due_date in result


class TestProjectListerListActiveProjects:
    """Test ProjectLister.list_active_projects()."""

    def test_lists_projects_grouped_by_area(self, tmp_path):
        """
        Test listing projects grouped by area.

        Given: Active projects in multiple areas
        When: Calling list_active_projects()
        Then: Returns formatted string grouped by area
        """
        # Given
        repo_path = tmp_path / "repo"
        active_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active"

        # Create health area projects
        health_dir = active_path / "health"
        health_dir.mkdir(parents=True)
        (health_dir / "morning-routine.md").write_text("""---
area: Health
title: Morning Routine
type: habit
---
# Morning Routine
""")
        (health_dir / "bulk-to-187.md").write_text(f"""---
area: Health
title: Bulk to 187lbs
type: standard
due: {(date.today() + timedelta(days=100)).isoformat()}
---
# Bulk to 187lbs
""")

        # Create career area project
        career_dir = active_path / "career"
        career_dir.mkdir(parents=True)
        (career_dir / "job-search.md").write_text("""---
area: Career
title: Job Search
type: coordination
---
# Job Search
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"},
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_active_projects()

        # Then
        assert "Career:" in result
        assert "Job Search" in result
        assert "[coordination]" in result

        assert "Health:" in result
        assert "Morning Routine" in result
        assert "[habit]" in result
        assert "Bulk to 187lbs" in result
        assert "100d" in result  # Days until due

    def test_handles_empty_areas(self, tmp_path):
        """
        Test handling areas with no projects.

        Given: Some areas have no projects
        When: Calling list_active_projects()
        Then: Only shows areas with projects
        """
        # Given
        repo_path = tmp_path / "repo"
        active_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active"

        # Create only health project
        health_dir = active_path / "health"
        health_dir.mkdir(parents=True)
        (health_dir / "test.md").write_text("""---
area: Health
title: Test Project
type: standard
---
# Test
""")

        # Create empty career directory
        (active_path / "career").mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"},
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_active_projects()

        # Then
        assert "Health:" in result
        assert "Test Project" in result
        # Career should not appear since it's empty
        assert "Career:" not in result
