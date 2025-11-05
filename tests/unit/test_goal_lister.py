"""Tests for GoalLister."""

import json
from pathlib import Path

import pytest

from execution_system_mcp.config import ConfigManager
from execution_system_mcp.goal_lister import GoalLister


class TestGoalListerListGoals:
    """Test GoalLister list_goals functionality."""

    def test_lists_goals_from_active_and_incubator(self, tmp_path):
        """
        Test listing goals from both active and incubator folders.

        Given: Goals in active and incubator folders
        When: Calling list_goals()
        Then: Returns JSON with goals grouped by folder
        """
        # Given
        repo_path = tmp_path / "repo"
        goals_base = repo_path / "docs" / "execution_system" / "30k-goals"

        # Active goal
        active_dir = goals_base / "active" / "health"
        active_dir.mkdir(parents=True)
        (active_dir / "fitness-goal.md").write_text("""---
area: Health
title: Get Fit
type: goal
started: 2025-01-01
---
# Get Fit
""")

        # Incubator goal
        incubator_dir = goals_base / "incubator"
        incubator_dir.mkdir(parents=True)
        (incubator_dir / "learn-spanish.md").write_text("""---
area: Learning
title: Learn Spanish
type: goal
---
# Learn Spanish
""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "execution_system_repo_path": str(repo_path),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Learning", "kebab": "learning"}
            ]
        }))

        config = ConfigManager(str(config_file))
        lister = GoalLister(config)

        # When
        result = lister.list_goals()

        # Then
        parsed = json.loads(result)
        assert "active" in parsed
        assert "incubator" in parsed
        assert len(parsed["active"]) == 1
        assert len(parsed["incubator"]) == 1

        active_goal = parsed["active"][0]
        assert active_goal["title"] == "Get Fit"
        assert active_goal["area"] == "Health"
        assert active_goal["filename"] == "fitness-goal.md"

        incubator_goal = parsed["incubator"][0]
        assert incubator_goal["title"] == "Learn Spanish"
        assert incubator_goal["area"] == "Learning"

    def test_filters_by_type_goal(self, tmp_path):
        """
        Test that only files with type: goal are included.

        Given: Goal file and supporting material file in same directory
        When: Calling list_goals()
        Then: Only returns file with type: goal
        """
        # Given
        repo_path = tmp_path / "repo"
        active_dir = repo_path / "docs" / "execution_system" / "30k-goals" / "active" / "health"
        active_dir.mkdir(parents=True)

        # Goal file
        (active_dir / "new-job.md").write_text("""---
area: Career
title: New Job Goal
type: goal
---
# New Job
""")

        # Supporting material (no type: goal)
        (active_dir / "role-criteria.md").write_text("""---
title: Role Criteria
---
# Role Criteria
Just supporting material
""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}]
        }))

        config = ConfigManager(str(config_file))
        lister = GoalLister(config)

        # When
        result = lister.list_goals()

        # Then
        parsed = json.loads(result)
        assert len(parsed["active"]) == 1
        assert parsed["active"][0]["title"] == "New Job Goal"

    def test_handles_nested_goal_directories(self, tmp_path):
        """
        Test finding goals in nested subdirectories.

        Given: Goal in nested folder structure (active/area/goal-folder/goal.md)
        When: Calling list_goals()
        Then: Finds goal and includes folder path
        """
        # Given
        repo_path = tmp_path / "repo"
        nested_dir = repo_path / "docs" / "execution_system" / "30k-goals" / "active" / "career" / "new-job"
        nested_dir.mkdir(parents=True)

        (nested_dir / "new-job.md").write_text("""---
area: Career
title: Find New Job
type: goal
started: 2025-10-01
---
# Find New Job
""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}]
        }))

        config = ConfigManager(str(config_file))
        lister = GoalLister(config)

        # When
        result = lister.list_goals()

        # Then
        parsed = json.loads(result)
        assert len(parsed["active"]) == 1
        goal = parsed["active"][0]
        assert goal["title"] == "Find New Job"
        assert "new-job/new-job.md" in goal["file_path"] or goal["filename"] == "new-job.md"

    def test_returns_empty_when_no_goals(self, tmp_path):
        """
        Test listing when no goals exist.

        Given: Goals directories exist but are empty
        When: Calling list_goals()
        Then: Returns empty lists for each folder
        """
        # Given
        repo_path = tmp_path / "repo"
        goals_base = repo_path / "docs" / "execution_system" / "30k-goals"
        (goals_base / "active").mkdir(parents=True)
        (goals_base / "incubator").mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        config = ConfigManager(str(config_file))
        lister = GoalLister(config)

        # When
        result = lister.list_goals()

        # Then
        parsed = json.loads(result)
        assert parsed["active"] == []
        assert parsed["incubator"] == []

    def test_includes_started_date_for_active_goals(self, tmp_path):
        """
        Test that started date is included for active goals.

        Given: Active goal with started date
        When: Calling list_goals()
        Then: Returned goal includes started date
        """
        # Given
        repo_path = tmp_path / "repo"
        active_dir = repo_path / "docs" / "execution_system" / "30k-goals" / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "goal.md").write_text("""---
area: Health
title: Health Goal
type: goal
started: 2025-09-15
---
# Health Goal
""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        config = ConfigManager(str(config_file))
        lister = GoalLister(config)

        # When
        result = lister.list_goals()

        # Then
        parsed = json.loads(result)
        goal = parsed["active"][0]
        assert goal["started"] == "2025-09-15"
