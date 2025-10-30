"""Tests for Auditor (Phase 3 tools)."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from gtd_mcp.auditor import Auditor
from gtd_mcp.config import ConfigManager


class TestAuditorAuditProjects:
    """Test Auditor.audit_projects()."""

    def test_valid_project_no_issues(self, tmp_path):
        """
        Test project with all valid fields.

        Given: Project with all required fields and valid values
        When: Calling audit_projects()
        Then: Returns no issues
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
created: 2025-01-01
last_reviewed: 2025-01-15
---
# Test Project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_projects()

        # Then
        assert len(result["issues"]) == 0

    def test_missing_required_fields(self, tmp_path):
        """
        Test project missing required fields.

        Given: Project missing title and last_reviewed
        When: Calling audit_projects()
        Then: Returns issues for missing fields
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "incomplete-project.md").write_text("""---
area: Health
type: standard
created: 2025-01-01
---
# Project without title
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_projects()

        # Then
        assert len(result["issues"]) == 1
        issue = result["issues"][0]
        assert "incomplete-project.md" in issue["file"]
        assert "title" in issue["missing_fields"]
        assert "last_reviewed" in issue["missing_fields"]

    def test_invalid_area(self, tmp_path):
        """
        Test project with invalid area.

        Given: Project with area not in configured areas
        When: Calling audit_projects()
        Then: Returns issue for invalid area
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "bad-area.md").write_text("""---
area: InvalidArea
title: Bad Area Project
type: standard
created: 2025-01-01
last_reviewed: 2025-01-01
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_projects()

        # Then
        assert len(result["issues"]) == 1
        issue = result["issues"][0]
        invalid_field = next(f for f in issue["invalid_fields"] if f["field"] == "area")
        assert invalid_field["value"] == "InvalidArea"
        assert "not in configured areas" in invalid_field["reason"]

    def test_invalid_project_type(self, tmp_path):
        """
        Test project with invalid type.

        Given: Project with type not in [standard, habit, coordination]
        When: Calling audit_projects()
        Then: Returns issue for invalid type
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "bad-type.md").write_text("""---
area: Health
title: Bad Type Project
type: invalid_type
created: 2025-01-01
last_reviewed: 2025-01-01
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_projects()

        # Then
        assert len(result["issues"]) == 1
        issue = result["issues"][0]
        invalid_field = next(f for f in issue["invalid_fields"] if f["field"] == "type")
        assert invalid_field["value"] == "invalid_type"
        assert "must be one of" in invalid_field["reason"]

    def test_invalid_date_format(self, tmp_path):
        """
        Test project with invalid date format.

        Given: Project with created date in wrong format
        When: Calling audit_projects()
        Then: Returns issue for invalid date
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "bad-date.md").write_text("""---
area: Health
title: Bad Date Project
type: standard
created: 01/15/2025
last_reviewed: 2025-01-01
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_projects()

        # Then
        assert len(result["issues"]) == 1
        issue = result["issues"][0]
        invalid_field = next(f for f in issue["invalid_fields"] if f["field"] == "created")
        assert "invalid date format" in invalid_field["reason"].lower()


class TestAuditorAuditOrphanProjects:
    """Test Auditor.audit_orphan_projects()."""

    def test_no_orphans_with_actions(self, tmp_path):
        """
        Test project with actions is not orphaned.

        Given: Standard project with next action
        When: Calling audit_orphan_projects()
        Then: Returns no orphans
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "with-actions.md").write_text("""---
area: Health
title: Project With Actions
type: standard
---
""")

        # Create action
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
---

- [ ] 2025-10-30 Do something @macbook +with-actions
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_orphan_projects()

        # Then
        assert len(result["orphan_projects"]) == 0

    def test_orphan_standard_project(self, tmp_path):
        """
        Test standard project without actions is orphaned.

        Given: Standard project with no actions
        When: Calling audit_orphan_projects()
        Then: Returns project as orphan
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "orphan.md").write_text("""---
area: Health
title: Orphan Project
type: standard
---
""")

        # Empty actions directory
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("---\ntitle: Macbook\n---\n")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_orphan_projects()

        # Then
        assert len(result["orphan_projects"]) == 1
        assert result["orphan_projects"][0]["title"] == "Orphan Project"

    def test_habits_not_orphaned(self, tmp_path):
        """
        Test habit projects are excluded from orphan check.

        Given: Habit project with no actions
        When: Calling audit_orphan_projects()
        Then: Not reported as orphan
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "habit.md").write_text("""---
area: Health
title: Habit Project
type: habit
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_orphan_projects()

        # Then
        assert len(result["orphan_projects"]) == 0


class TestAuditorAuditOrphanActions:
    """Test Auditor.audit_orphan_actions()."""

    def test_valid_actions_no_orphans(self, tmp_path):
        """
        Test actions with valid project tags.

        Given: Actions with project tags that exist
        When: Calling audit_orphan_actions()
        Then: Returns no orphans
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "valid-project.md").write_text("""---
area: Health
title: Valid Project
type: standard
---
""")

        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
---

- [ ] 2025-10-30 Do something @macbook +valid-project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_orphan_actions()

        # Then
        assert len(result["orphan_actions"]) == 0
        assert len(result["invalid_contexts"]) == 0

    def test_orphan_action_invalid_project(self, tmp_path):
        """
        Test action with nonexistent project tag.

        Given: Action with project tag that doesn't exist
        When: Calling audit_orphan_actions()
        Then: Returns orphan action
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
---

- [ ] 2025-10-30 Do something @macbook +nonexistent-project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_orphan_actions()

        # Then
        assert len(result["orphan_actions"]) == 1
        assert result["orphan_actions"][0]["project_tag"] == "nonexistent-project"

    def test_invalid_context(self, tmp_path):
        """
        Test action with invalid context.

        Given: Action with context that doesn't have a file
        When: Calling audit_orphan_actions()
        Then: Returns invalid context
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "project.md").write_text("""---
area: Health
title: Project
type: standard
---
""")

        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)
        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
---

- [ ] 2025-10-30 Do something @invalidcontext +project
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_orphan_actions()

        # Then
        assert len(result["invalid_contexts"]) == 1
        assert result["invalid_contexts"][0]["context"] == "@invalidcontext"


class TestAuditorAuditActionFiles:
    """Test Auditor.audit_action_files()."""

    def test_valid_action_file(self, tmp_path):
        """
        Test action file with all required fields.

        Given: Action file with title and last_reviewed
        When: Calling audit_action_files()
        Then: Returns no issues
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-01-15
---

- [ ] 2025-10-30 Action here @macbook
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_action_files()

        # Then
        assert len(result["issues"]) == 0

    def test_missing_required_fields(self, tmp_path):
        """
        Test action file missing required fields.

        Given: Action file missing last_reviewed
        When: Calling audit_action_files()
        Then: Returns issue
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
---

- [ ] 2025-10-30 Action here @macbook
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.audit_action_files()

        # Then
        assert len(result["issues"]) == 1
        assert "last_reviewed" in result["issues"][0]["missing_fields"]


class TestAuditorListProjectsNeedingReview:
    """Test Auditor.list_projects_needing_review()."""

    def test_recent_project_not_needing_review(self, tmp_path):
        """
        Test recently reviewed project not returned.

        Given: Project reviewed 3 days ago
        When: Calling list_projects_needing_review()
        Then: Not in results
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        recent_date = (date.today() - timedelta(days=3)).isoformat()
        (active_dir / "recent.md").write_text(f"""---
area: Health
title: Recent Project
type: standard
last_reviewed: {recent_date}
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.list_projects_needing_review()

        # Then
        assert len(result["projects_needing_review"]) == 0

    def test_old_project_needs_review(self, tmp_path):
        """
        Test project reviewed 10 days ago needs review.

        Given: Project reviewed 10 days ago
        When: Calling list_projects_needing_review()
        Then: In results with days_since_review = 10
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        old_date = (date.today() - timedelta(days=10)).isoformat()
        (active_dir / "old.md").write_text(f"""---
area: Health
title: Old Project
type: standard
last_reviewed: {old_date}
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.list_projects_needing_review()

        # Then
        assert len(result["projects_needing_review"]) == 1
        assert result["projects_needing_review"][0]["days_since_review"] == 10

    def test_exactly_7_days_needs_review(self, tmp_path):
        """
        Test project reviewed exactly 7 days ago needs review.

        Given: Project reviewed 7 days ago (inclusive)
        When: Calling list_projects_needing_review()
        Then: In results
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
        (active_dir / "seven.md").write_text(f"""---
area: Health
title: Seven Days Project
type: standard
last_reviewed: {seven_days_ago}
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.list_projects_needing_review()

        # Then
        assert len(result["projects_needing_review"]) == 1
        assert result["projects_needing_review"][0]["days_since_review"] == 7

    def test_missing_last_reviewed_needs_review(self, tmp_path):
        """
        Test project without last_reviewed needs review.

        Given: Project with no last_reviewed field
        When: Calling list_projects_needing_review()
        Then: In results with null last_reviewed
        """
        # Given
        repo_path = tmp_path / "repo"
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "health"
        active_dir.mkdir(parents=True)

        (active_dir / "never.md").write_text("""---
area: Health
title: Never Reviewed
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.list_projects_needing_review()

        # Then
        assert len(result["projects_needing_review"]) == 1
        assert result["projects_needing_review"][0]["last_reviewed"] is None


class TestAuditorListActionsNeedingReview:
    """Test Auditor.list_actions_needing_review()."""

    def test_recent_action_file_not_needing_review(self, tmp_path):
        """
        Test recently reviewed action file not returned.

        Given: Action file reviewed 3 days ago
        When: Calling list_actions_needing_review()
        Then: Not in results
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        recent_date = (date.today() - timedelta(days=3)).isoformat()
        (contexts_dir / "@macbook.md").write_text(f"""---
title: Macbook
last_reviewed: {recent_date}
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.list_actions_needing_review()

        # Then
        assert len(result["actions_needing_review"]) == 0

    def test_old_action_file_needs_review(self, tmp_path):
        """
        Test action file reviewed 12 days ago needs review.

        Given: Action file reviewed 12 days ago
        When: Calling list_actions_needing_review()
        Then: In results with days_since_review = 12
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        old_date = (date.today() - timedelta(days=12)).isoformat()
        (contexts_dir / "@phone.md").write_text(f"""---
title: Phone
last_reviewed: {old_date}
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        auditor = Auditor(config)

        # When
        result = auditor.list_actions_needing_review()

        # Then
        assert len(result["actions_needing_review"]) == 1
        assert result["actions_needing_review"][0]["days_since_review"] == 12
