"""Tests for ProjectLister."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from execution_system_mcp.config import ConfigManager
from execution_system_mcp.lister import ProjectLister


def get_week_start(d: date) -> date:
    """Get the Sunday of the week containing the given date."""
    return d - timedelta(days=d.weekday() + 1 if d.weekday() != 6 else 0)


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
            "execution_system_repo_path": str(repo_path),
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
            "execution_system_repo_path": str(repo_path),
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


class TestProjectListerListProjects:
    """Test ProjectLister.list_projects() with JSON output and flexible filtering."""

    def test_list_all_active_projects_grouped_by_area(self, tmp_path):
        """
        Test listing active projects grouped by area (default behavior).

        Given: Active projects in multiple areas
        When: Calling list_projects()
        Then: Returns JSON with projects grouped by area
        """
        # Given
        repo_path = tmp_path / "repo"
        active_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active"

        health_dir = active_path / "health"
        health_dir.mkdir(parents=True)
        (health_dir / "morning-routine.md").write_text("""---
area: Health
title: Morning Routine
type: habit
---
""")

        career_dir = active_path / "career"
        career_dir.mkdir(parents=True)
        (career_dir / "job-search.md").write_text("""---
area: Career
title: Job Search
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"},
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_projects()

        # Then
        assert "groups" in result
        assert len(result["groups"]) == 2

        # Find Career group
        career_group = next(g for g in result["groups"] if g["group_name"] == "Career")
        assert len(career_group["projects"]) == 1
        assert career_group["projects"][0]["title"] == "Job Search"
        assert career_group["projects"][0]["type"] == "standard"
        assert career_group["projects"][0]["folder"] == "active"

        # Find Health group
        health_group = next(g for g in result["groups"] if g["group_name"] == "Health")
        assert len(health_group["projects"]) == 1
        assert health_group["projects"][0]["title"] == "Morning Routine"
        assert health_group["projects"][0]["type"] == "habit"

    def test_list_incubator_projects(self, tmp_path):
        """
        Test listing incubator projects only.

        Given: Projects in active and incubator folders
        When: Calling list_projects(folder="incubator")
        Then: Returns only incubator projects
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        # Create active project
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)
        (active_dir / "active-project.md").write_text("""---
area: Health
title: Active Project
type: standard
---
""")

        # Create incubator project
        incubator_dir = projects_base / "incubator" / "health"
        incubator_dir.mkdir(parents=True)
        (incubator_dir / "incubator-project.md").write_text("""---
area: Health
title: Incubator Project
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
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(folder="incubator")

        # Then
        assert len(result["groups"]) == 1
        assert result["groups"][0]["projects"][0]["title"] == "Incubator Project"
        assert result["groups"][0]["projects"][0]["folder"] == "incubator"

    def test_list_all_folders(self, tmp_path):
        """
        Test listing projects from all folders.

        Given: Projects in active, incubator, and completed
        When: Calling list_projects(folder="all")
        Then: Returns projects from all folders
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"

        for folder in ["active", "incubator", "completed"]:
            folder_dir = projects_base / folder / "health"
            folder_dir.mkdir(parents=True)
            (folder_dir / f"{folder}-project.md").write_text(f"""---
area: Health
title: {folder.capitalize()} Project
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
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(folder="all")

        # Then
        all_projects = result["groups"][0]["projects"]
        assert len(all_projects) == 3
        folders = {p["folder"] for p in all_projects}
        assert folders == {"active", "incubator", "completed"}

    def test_filter_by_area(self, tmp_path):
        """
        Test filtering projects by specific area.

        Given: Projects in multiple areas
        When: Calling list_projects(filter_area="Health")
        Then: Returns only Health area projects
        """
        # Given
        repo_path = tmp_path / "repo"
        active_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active"

        health_dir = active_path / "health"
        health_dir.mkdir(parents=True)
        (health_dir / "health-project.md").write_text("""---
area: Health
title: Health Project
type: standard
---
""")

        career_dir = active_path / "career"
        career_dir.mkdir(parents=True)
        (career_dir / "career-project.md").write_text("""---
area: Career
title: Career Project
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"},
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(filter_area="Health")

        # Then
        assert len(result["groups"]) == 1
        assert result["groups"][0]["group_name"] == "Health"
        assert result["groups"][0]["projects"][0]["title"] == "Health Project"

    def test_filter_by_has_due(self, tmp_path):
        """
        Test filtering projects that have due dates.

        Given: Mix of projects with and without due dates
        When: Calling list_projects(filter_has_due=True)
        Then: Returns only projects with due dates
        """
        # Given
        repo_path = tmp_path / "repo"
        active_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active"

        health_dir = active_path / "health"
        health_dir.mkdir(parents=True)
        (health_dir / "with-due.md").write_text("""---
area: Health
title: With Due Date
type: standard
due: 2025-12-31
---
""")
        (health_dir / "without-due.md").write_text("""---
area: Health
title: Without Due Date
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
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(filter_has_due=True)

        # Then
        all_projects = result["groups"][0]["projects"]
        assert len(all_projects) == 1
        assert all_projects[0]["title"] == "With Due Date"
        assert all_projects[0]["due"] == "2025-12-31"

    def test_group_by_due_date(self, tmp_path):
        """
        Test grouping projects by due date.

        Given: Projects with various due dates
        When: Calling list_projects(group_by="due_date")
        Then: Returns projects sorted by due date
        """
        # Given
        repo_path = tmp_path / "repo"
        active_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active"

        health_dir = active_path / "health"
        health_dir.mkdir(parents=True)

        overdue_date = (date.today() - timedelta(days=5)).isoformat()
        soon_date = (date.today() + timedelta(days=3)).isoformat()
        later_date = (date.today() + timedelta(days=30)).isoformat()

        (health_dir / "overdue.md").write_text(f"""---
area: Health
title: Overdue Project
type: standard
due: {overdue_date}
---
""")
        (health_dir / "soon.md").write_text(f"""---
area: Health
title: Soon Project
type: standard
due: {soon_date}
---
""")
        (health_dir / "later.md").write_text(f"""---
area: Health
title: Later Project
type: standard
due: {later_date}
---
""")
        (health_dir / "no-due.md").write_text("""---
area: Health
title: No Due Project
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
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(group_by="due_date")

        # Then
        # Should have groups for: Overdue, This Week, Later, No Due Date
        assert len(result["groups"]) == 4

        overdue_group = next(g for g in result["groups"] if g["group_name"] == "Overdue")
        assert len(overdue_group["projects"]) == 1
        assert overdue_group["projects"][0]["title"] == "Overdue Project"

        this_week_group = next(g for g in result["groups"] if g["group_name"] == "This Week")
        assert len(this_week_group["projects"]) == 1
        assert this_week_group["projects"][0]["title"] == "Soon Project"

    def test_flat_grouping(self, tmp_path):
        """
        Test flat grouping (no grouping).

        Given: Projects in multiple areas
        When: Calling list_projects(group_by="flat")
        Then: Returns all projects in single group sorted by title
        """
        # Given
        repo_path = tmp_path / "repo"
        active_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active"

        health_dir = active_path / "health"
        health_dir.mkdir(parents=True)
        (health_dir / "zebra.md").write_text("""---
area: Health
title: Zebra Project
type: standard
---
""")

        career_dir = active_path / "career"
        career_dir.mkdir(parents=True)
        (career_dir / "alpha.md").write_text("""---
area: Career
title: Alpha Project
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"},
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(group_by="flat")

        # Then
        assert len(result["groups"]) == 1
        assert result["groups"][0]["group_name"] == "All Projects"
        projects = result["groups"][0]["projects"]
        assert len(projects) == 2
        # Should be sorted by title
        assert projects[0]["title"] == "Alpha Project"
        assert projects[1]["title"] == "Zebra Project"


class TestProjectListerDateFields:
    """Test parsing and returning date fields (completed, started, created)."""

    def test_parse_completed_date(self, tmp_path):
        """
        Test parsing completed date from YAML.

        Given: Completed project file with completed date
        When: Calling parse_yaml_frontmatter()
        Then: Returns dict with completed field
        """
        # Given
        project_file = tmp_path / "completed-project.md"
        project_file.write_text("""---
area: Health
title: Completed Project
type: standard
created: 2025-01-01
started: 2025-01-15
completed: 2025-10-31
---
""")

        # When
        result = ProjectLister.parse_yaml_frontmatter(project_file)

        # Then
        assert result["completed"] == "2025-10-31"
        assert result["started"] == "2025-01-15"
        assert result["created"] == "2025-01-01"

    def test_parse_without_date_fields(self, tmp_path):
        """
        Test parsing when date fields are missing.

        Given: Project file without completed/started/created
        When: Calling parse_yaml_frontmatter()
        Then: Returns dict with None for missing date fields
        """
        # Given
        project_file = tmp_path / "project.md"
        project_file.write_text("""---
area: Health
title: Simple Project
type: standard
---
""")

        # When
        result = ProjectLister.parse_yaml_frontmatter(project_file)

        # Then
        assert result["completed"] is None
        assert result["started"] is None
        assert result["created"] is None

    def test_list_projects_includes_date_fields(self, tmp_path):
        """
        Test that list_projects includes date fields in output.

        Given: Completed projects with date fields
        When: Calling list_projects(folder="completed")
        Then: Returns projects with completed, started, created fields
        """
        # Given
        repo_path = tmp_path / "repo"
        completed_path = repo_path / "docs" / "execution_system" / "10k-projects" / "completed"

        health_dir = completed_path / "health"
        health_dir.mkdir(parents=True)
        (health_dir / "project1.md").write_text("""---
area: Health
title: Completed Project 1
type: standard
created: 2025-01-01
started: 2025-01-15
completed: 2025-10-31
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(folder="completed")

        # Then
        project = result["groups"][0]["projects"][0]
        assert project["completed"] == "2025-10-31"
        assert project["started"] == "2025-01-15"
        assert project["created"] == "2025-01-01"


class TestProjectListerCompletedDateFiltering:
    """Test filtering completed projects by date ranges."""

    def test_filter_completed_last_week(self, tmp_path):
        """
        Test filtering projects completed last week.

        Given: Completed projects from various weeks
        When: Calling list_projects(completed_date_preset="last_week")
        Then: Returns only projects completed last Sunday-Saturday
        """
        # Given
        repo_path = tmp_path / "repo"
        completed_path = repo_path / "docs" / "execution_system" / "10k-projects" / "completed"
        health_dir = completed_path / "health"
        health_dir.mkdir(parents=True)

        today = date.today()
        # Get last week's Sunday and Saturday
        this_week_start = get_week_start(today)
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = this_week_start - timedelta(days=1)

        # Project completed last week (should be included)
        (health_dir / "last-week.md").write_text(f"""---
area: Health
title: Last Week Project
type: standard
completed: {last_week_start + timedelta(days=2)}
---
""")

        # Project completed this week (should NOT be included)
        (health_dir / "this-week.md").write_text(f"""---
area: Health
title: This Week Project
type: standard
completed: {today}
---
""")

        # Project completed two weeks ago (should NOT be included)
        (health_dir / "two-weeks.md").write_text(f"""---
area: Health
title: Two Weeks Project
type: standard
completed: {last_week_start - timedelta(days=8)}
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(folder="completed", completed_date_preset="last_week")

        # Then
        projects = result["groups"][0]["projects"]
        assert len(projects) == 1
        assert projects[0]["title"] == "Last Week Project"

    def test_filter_completed_last_month(self, tmp_path):
        """
        Test filtering projects completed last month.

        Given: Completed projects from various months
        When: Calling list_projects(completed_date_preset="last_month")
        Then: Returns only projects completed in previous calendar month
        """
        # Given
        repo_path = tmp_path / "repo"
        completed_path = repo_path / "docs" / "execution_system" / "10k-projects" / "completed"
        health_dir = completed_path / "health"
        health_dir.mkdir(parents=True)

        today = date.today()
        # Get last month's first and last day
        first_of_this_month = today.replace(day=1)
        last_month_last = first_of_this_month - timedelta(days=1)
        last_month_first = last_month_last.replace(day=1)

        # Project completed last month (should be included)
        (health_dir / "last-month.md").write_text(f"""---
area: Health
title: Last Month Project
type: standard
completed: {last_month_first + timedelta(days=10)}
---
""")

        # Project completed this month (should NOT be included)
        (health_dir / "this-month.md").write_text(f"""---
area: Health
title: This Month Project
type: standard
completed: {today}
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(folder="completed", completed_date_preset="last_month")

        # Then
        projects = result["groups"][0]["projects"]
        assert len(projects) == 1
        assert projects[0]["title"] == "Last Month Project"

    def test_filter_completed_week_to_date(self, tmp_path):
        """
        Test filtering projects completed week-to-date.

        Given: Completed projects from various times
        When: Calling list_projects(completed_date_preset="week_to_date")
        Then: Returns projects completed from Sunday through today (inclusive)
        """
        # Given
        repo_path = tmp_path / "repo"
        completed_path = repo_path / "docs" / "execution_system" / "10k-projects" / "completed"
        health_dir = completed_path / "health"
        health_dir.mkdir(parents=True)

        today = date.today()
        this_week_start = get_week_start(today)

        # Project completed this week (should be included)
        # Use a date that's guaranteed to be between week_start and today
        days_into_week = (today - this_week_start).days
        if days_into_week >= 1:
            this_week_date = this_week_start + timedelta(days=1)
        else:
            # Today is Sunday, use today
            this_week_date = today

        (health_dir / "this-week.md").write_text(f"""---
area: Health
title: This Week Project
type: standard
completed: {this_week_date}
---
""")

        # Project completed today (should be included)
        (health_dir / "today.md").write_text(f"""---
area: Health
title: Today Project
type: standard
completed: {today}
---
""")

        # Project completed last week (should NOT be included)
        (health_dir / "last-week.md").write_text(f"""---
area: Health
title: Last Week Project
type: standard
completed: {this_week_start - timedelta(days=1)}
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When
        result = lister.list_projects(folder="completed", completed_date_preset="week_to_date")

        # Then
        projects = result["groups"][0]["projects"]
        assert len(projects) == 2
        titles = {p["title"] for p in projects}
        assert titles == {"This Week Project", "Today Project"}

    def test_filter_completed_custom_range(self, tmp_path):
        """
        Test filtering projects with custom date range.

        Given: Completed projects from various dates
        When: Calling list_projects(filter_completed_start, filter_completed_end)
        Then: Returns only projects completed within the range
        """
        # Given
        repo_path = tmp_path / "repo"
        completed_path = repo_path / "docs" / "execution_system" / "10k-projects" / "completed"
        health_dir = completed_path / "health"
        health_dir.mkdir(parents=True)

        # Projects with different completion dates
        (health_dir / "before.md").write_text("""---
area: Health
title: Before Range
type: standard
completed: 2025-09-30
---
""")
        (health_dir / "in-range-1.md").write_text("""---
area: Health
title: In Range 1
type: standard
completed: 2025-10-01
---
""")
        (health_dir / "in-range-2.md").write_text("""---
area: Health
title: In Range 2
type: standard
completed: 2025-10-15
---
""")
        (health_dir / "in-range-3.md").write_text("""---
area: Health
title: In Range 3
type: standard
completed: 2025-10-31
---
""")
        (health_dir / "after.md").write_text("""---
area: Health
title: After Range
type: standard
completed: 2025-11-01
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ProjectLister(config)

        # When - filter for October 2025
        result = lister.list_projects(
            folder="completed",
            filter_completed_start="2025-10-01",
            filter_completed_end="2025-10-31"
        )

        # Then
        projects = result["groups"][0]["projects"]
        assert len(projects) == 3
        titles = {p["title"] for p in projects}
        assert titles == {"In Range 1", "In Range 2", "In Range 3"}
