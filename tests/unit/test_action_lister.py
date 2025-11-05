"""Tests for ActionLister."""

import json
from pathlib import Path

import pytest

from execution_system_mcp.action_lister import ActionLister
from execution_system_mcp.config import ConfigManager


class TestActionListerParseAction:
    """Test ActionLister action line parsing."""

    def test_parse_complete_action(self):
        """
        Test parsing action with all metadata.

        Given: Action line with date, text, context, project, and due date
        When: Calling parse_action()
        Then: Returns dict with all fields extracted
        """
        # Given
        line = "- [ ] 2025-10-30 Update financial statements @macbook +help-dad due:2025-10-31"

        # When
        result = ActionLister.parse_action(line, "next")

        # Then
        assert result["text"] == "Update financial statements"
        assert result["date"] == "2025-10-30"
        assert result["context"] == "@macbook"
        assert result["project"] == "help-dad"
        assert result["due"] == "2025-10-31"
        assert result["defer"] is None
        assert result["state"] == "next"

    def test_parse_action_with_defer(self):
        """
        Test parsing deferred action with defer date.

        Given: Action line with defer date
        When: Calling parse_action()
        Then: Returns dict with defer date extracted
        """
        # Given
        line = "- [ ] 2025-10-29 Email recruiter @phone +job-search defer:2025-11-01 due:2025-11-05"

        # When
        result = ActionLister.parse_action(line, "deferred")

        # Then
        assert result["text"] == "Email recruiter"
        assert result["defer"] == "2025-11-01"
        assert result["due"] == "2025-11-05"
        assert result["state"] == "deferred"

    def test_parse_action_without_project(self):
        """
        Test parsing action without project tag.

        Given: Action line without +project tag
        When: Calling parse_action()
        Then: Returns dict with project as None
        """
        # Given
        line = "- [ ] 2025-10-30 Buy groceries @errands"

        # When
        result = ActionLister.parse_action(line, "next")

        # Then
        assert result["text"] == "Buy groceries"
        assert result["project"] is None

    def test_parse_action_with_url(self):
        """
        Test parsing action with URL.

        Given: Action line with URL at end
        When: Calling parse_action()
        Then: Returns dict with URL preserved in text
        """
        # Given
        line = "- [ ] 2025-10-26 Track package @waiting +receive-goods https://www.ups.com/track?trackNums=123"

        # When
        result = ActionLister.parse_action(line, "waiting")

        # Then
        assert result["text"] == "Track package https://www.ups.com/track?trackNums=123"
        assert result["state"] == "waiting"


class TestActionListerListActions:
    """Test ActionLister.list_actions() with JSON output and flexible filtering."""

    def test_list_actions_grouped_by_project_default(self, tmp_path):
        """
        Test listing actions grouped by project (default behavior).

        Given: Actions in multiple context files with different projects
        When: Calling list_actions()
        Then: Returns JSON grouped by project folder, then project, then state
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        # Create macbook context with actions
        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Research ML resources @macbook +ml-refresh
- [ ] 2025-10-30 Complete homework @macbook +dbt-skills
""")

        # Create waiting file
        (actions_base / "@waiting.md").write_text("""---
title: Waiting For
last_reviewed: 2025-10-22
---

- [ ] 2025-10-29 Recruiter to respond @waiting +job-search
""")

        # Set up projects
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "career"
        active_dir.mkdir(parents=True)
        (active_dir / "ml-refresh.md").write_text("""---
area: Career
title: ML Refresh
type: standard
---
""")
        (active_dir / "job-search.md").write_text("""---
area: Career
title: Job Search
type: standard
---
""")

        incubator_dir = projects_base / "incubator" / "health"
        incubator_dir.mkdir(parents=True)
        (incubator_dir / "dbt-skills.md").write_text("""---
area: Health
title: DBT Skills
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [
                {"name": "Career", "kebab": "career"},
                {"name": "Health", "kebab": "health"},
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ActionLister(config)

        # When
        result = lister.list_actions()

        # Then
        assert "groups" in result

        # Should have Active and Incubator project groups
        active_group = next(g for g in result["groups"] if g["group_name"] == "Active Projects")
        incubator_group = next(g for g in result["groups"] if g["group_name"] == "Incubator Projects")

        # Check Active projects
        ml_project = next(p for p in active_group["projects"] if p["project_name"] == "ML Refresh")
        assert ml_project["project_filename"] == "ml-refresh"
        assert len(ml_project["states"]) == 1
        assert ml_project["states"][0]["state"] == "next"
        assert len(ml_project["states"][0]["actions"]) == 1
        assert ml_project["states"][0]["actions"][0]["text"] == "Research ML resources"

    def test_list_actions_grouped_by_context(self, tmp_path):
        """
        Test listing actions grouped by context.

        Given: Actions in multiple context files
        When: Calling list_actions(group_by="context")
        Then: Returns JSON grouped by context
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Research ML @macbook +ml-refresh
- [ ] 2025-10-30 Complete homework @macbook +dbt-skills
""")

        (contexts_dir / "@phone.md").write_text("""---
title: Phone
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Call recruiter @phone +job-search
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ActionLister(config)

        # When
        result = lister.list_actions(group_by="context")

        # Then
        assert len(result["groups"]) == 2

        macbook_group = next(g for g in result["groups"] if g["group_name"] == "@macbook")
        assert len(macbook_group["actions"]) == 2
        assert macbook_group["actions"][0]["text"] == "Research ML"

        phone_group = next(g for g in result["groups"] if g["group_name"] == "@phone")
        assert len(phone_group["actions"]) == 1

    def test_filter_by_project(self, tmp_path):
        """
        Test filtering actions by specific project.

        Given: Actions for multiple projects
        When: Calling list_actions(filter_project="ml-refresh")
        Then: Returns only actions for that project
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Research ML @macbook +ml-refresh
- [ ] 2025-10-30 Complete homework @macbook +dbt-skills
""")

        # Set up project
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "career"
        active_dir.mkdir(parents=True)
        (active_dir / "ml-refresh.md").write_text("""---
area: Career
title: ML Refresh
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ActionLister(config)

        # When
        result = lister.list_actions(filter_project="ml-refresh")

        # Then
        active_group = result["groups"][0]
        assert len(active_group["projects"]) == 1
        assert active_group["projects"][0]["project_filename"] == "ml-refresh"
        assert len(active_group["projects"][0]["states"][0]["actions"]) == 1

    def test_filter_by_context(self, tmp_path):
        """
        Test filtering actions by specific context.

        Given: Actions in multiple contexts
        When: Calling list_actions(filter_context="@phone")
        Then: Returns only actions for that context
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Research ML @macbook +ml-refresh
""")

        (contexts_dir / "@phone.md").write_text("""---
title: Phone
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Call recruiter @phone +job-search
""")

        # Set up projects
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "career"
        active_dir.mkdir(parents=True)
        (active_dir / "job-search.md").write_text("""---
area: Career
title: Job Search
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ActionLister(config)

        # When
        result = lister.list_actions(filter_context="@phone", group_by="context")

        # Then
        assert len(result["groups"]) == 1
        assert result["groups"][0]["group_name"] == "@phone"
        assert len(result["groups"][0]["actions"]) == 1

    def test_flat_grouping(self, tmp_path):
        """
        Test flat grouping returns simple list.

        Given: Actions in multiple contexts and projects
        When: Calling list_actions(group_by="flat")
        Then: Returns single group with all actions
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Task A @macbook +project-a
- [ ] 2025-10-30 Task B @macbook +project-b
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ActionLister(config)

        # When
        result = lister.list_actions(group_by="flat")

        # Then
        assert len(result["groups"]) == 1
        assert result["groups"][0]["group_name"] == "All Actions"
        assert len(result["groups"][0]["actions"]) == 2

    def test_include_all_states_by_default(self, tmp_path):
        """
        Test that all action states are included by default.

        Given: Actions in next, waiting, deferred, incubating states
        When: Calling list_actions()
        Then: Returns actions from all states
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Next action @macbook +project-a
""")

        (actions_base / "@waiting.md").write_text("""---
title: Waiting
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Waiting action @waiting +project-a
""")

        (actions_base / "@deferred.md").write_text("""---
title: Deferred
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Deferred action @deferred +project-a defer:2025-11-01
""")

        (actions_base / "@incubating.md").write_text("""---
title: Incubating
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Incubating action @incubating +project-a
""")

        # Set up project
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "career"
        active_dir.mkdir(parents=True)
        (active_dir / "project-a.md").write_text("""---
area: Career
title: Project A
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ActionLister(config)

        # When
        result = lister.list_actions()

        # Then
        project = result["groups"][0]["projects"][0]
        state_names = {s["state"] for s in project["states"]}
        assert state_names == {"next", "waiting", "deferred", "incubating"}

    def test_filter_by_states(self, tmp_path):
        """
        Test filtering by specific action states.

        Given: Actions in multiple states
        When: Calling list_actions(include_states=["next", "waiting"])
        Then: Returns only actions in those states
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_base = repo_path / "docs" / "execution_system" / "00k-next-actions"
        contexts_dir = actions_base / "contexts"
        contexts_dir.mkdir(parents=True)

        (contexts_dir / "@macbook.md").write_text("""---
title: Macbook
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Next action @macbook +project-a
""")

        (actions_base / "@waiting.md").write_text("""---
title: Waiting
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Waiting action @waiting +project-a
""")

        (actions_base / "@deferred.md").write_text("""---
title: Deferred
last_reviewed: 2025-10-22
---

- [ ] 2025-10-30 Deferred action @deferred +project-a defer:2025-11-01
""")

        # Set up project
        projects_base = repo_path / "docs" / "execution_system" / "10k-projects"
        active_dir = projects_base / "active" / "career"
        active_dir.mkdir(parents=True)
        (active_dir / "project-a.md").write_text("""---
area: Career
title: Project A
type: standard
---
""")

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        lister = ActionLister(config)

        # When
        result = lister.list_actions(include_states=["next", "waiting"])

        # Then
        project = result["groups"][0]["projects"][0]
        state_names = {s["state"] for s in project["states"]}
        assert state_names == {"next", "waiting"}
        assert "deferred" not in state_names
