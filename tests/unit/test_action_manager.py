"""Tests for ActionManager."""

import json
from datetime import date
from pathlib import Path

import pytest

from gtd_mcp.action_manager import ActionManager
from gtd_mcp.config import ConfigManager


class TestActionManagerAddAction:
    """Test ActionManager add_action functionality."""

    def test_adds_action_to_context_file(self, tmp_path):
        """
        Test adding action to context file.

        Given: Context file exists with YAML header
        When: Adding action with text, context, project
        Then: Action is added to top of file with today's date
        """
        # Given
        repo_path = tmp_path / "repo"
        contexts_dir = repo_path / "docs" / "execution_system" / "00k-next-actions" / "contexts"
        contexts_dir.mkdir(parents=True)

        macbook_file = contexts_dir / "@macbook.md"
        macbook_file.write_text("""---
title: Macbook
last_reviewed: 2025-10-20
---

- [ ] 2025-10-20 Existing action @macbook +existing-project
""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        # Create a dummy project so validation passes
        projects_dir = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / "health"
        projects_dir.mkdir(parents=True)
        project_file = projects_dir / "test-project.md"
        project_file.write_text("""---
area: Health
title: Test Project
---
""")

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_action(
            text="New action to add",
            context="@macbook",
            project="test-project"
        )

        # Then
        assert "✓ Successfully added action" in result
        content = macbook_file.read_text()
        lines = content.strip().split('\n')

        # Check action is added after YAML header
        today = date.today().strftime("%Y-%m-%d")
        expected_action = f"- [ ] {today} New action to add @macbook +test-project"
        assert expected_action in content
        # Should be added at top (after YAML)
        assert lines[4] == expected_action

    def test_adds_action_with_due_date(self, tmp_path):
        """
        Test adding action with due date.

        Given: Context file exists
        When: Adding action with due date
        Then: Action includes due:YYYY-MM-DD tag
        """
        # Given
        repo_path = tmp_path / "repo"
        contexts_dir = repo_path / "docs" / "execution_system" / "00k-next-actions" / "contexts"
        contexts_dir.mkdir(parents=True)

        macbook_file = contexts_dir / "@macbook.md"
        macbook_file.write_text("""---
title: Macbook
last_reviewed: 2025-10-20
---

""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_action(
            text="Action with deadline",
            context="@macbook",
            due="2025-12-31"
        )

        # Then
        assert "✓ Successfully added action" in result
        content = macbook_file.read_text()
        assert "due:2025-12-31" in content

    def test_adds_action_with_custom_date(self, tmp_path):
        """
        Test adding action with custom creation date.

        Given: Context file exists
        When: Adding action with specific date
        Then: Action uses provided date instead of today
        """
        # Given
        repo_path = tmp_path / "repo"
        contexts_dir = repo_path / "docs" / "execution_system" / "00k-next-actions" / "contexts"
        contexts_dir.mkdir(parents=True)

        macbook_file = contexts_dir / "@macbook.md"
        macbook_file.write_text("""---
title: Macbook
last_reviewed: 2025-10-20
---

""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_action(
            text="Action from past",
            context="@macbook",
            action_date="2025-09-15"
        )

        # Then
        content = macbook_file.read_text()
        assert "- [ ] 2025-09-15 Action from past @macbook" in content

    def test_validates_project_exists(self, tmp_path):
        """
        Test project validation when adding action.

        Given: Project does not exist
        When: Adding action with +project tag
        Then: Returns error about invalid project
        """
        # Given
        repo_path = tmp_path / "repo"
        contexts_dir = repo_path / "docs" / "execution_system" / "00k-next-actions" / "contexts"
        contexts_dir.mkdir(parents=True)

        macbook_file = contexts_dir / "@macbook.md"
        macbook_file.write_text("""---
title: Macbook
last_reviewed: 2025-10-20
---

""")

        # Create projects dir but no project file
        projects_dir = repo_path / "docs" / "execution_system" / "10k-projects" / "active"
        projects_dir.mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_action(
            text="Action for nonexistent project",
            context="@macbook",
            project="nonexistent-project"
        )

        # Then
        assert "Error" in result
        assert "Project 'nonexistent-project' does not exist" in result

    def test_returns_error_for_invalid_context(self, tmp_path):
        """
        Test error when context file doesn't exist.

        Given: Context file does not exist
        When: Adding action to that context
        Then: Returns error about missing context
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_action(
            text="Action for missing context",
            context="@nonexistent"
        )

        # Then
        assert "Error" in result
        assert "Context file" in result
        assert "@nonexistent.md" in result

    def test_action_without_project_tag(self, tmp_path):
        """
        Test adding action without project tag.

        Given: Context file exists
        When: Adding action without project parameter
        Then: Action added successfully without +project tag
        """
        # Given
        repo_path = tmp_path / "repo"
        contexts_dir = repo_path / "docs" / "execution_system" / "00k-next-actions" / "contexts"
        contexts_dir.mkdir(parents=True)

        phone_file = contexts_dir / "@phone.md"
        phone_file.write_text("""---
title: Phone
last_reviewed: 2025-10-20
---

""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_action(
            text="Call dentist",
            context="@phone"
        )

        # Then
        assert "✓ Successfully added action" in result
        content = phone_file.read_text()
        assert "Call dentist @phone" in content
        assert "+" not in content  # No project tag


class TestActionManagerAddToWaiting:
    """Test ActionManager add_to_waiting functionality."""

    def test_adds_to_waiting_file(self, tmp_path):
        """
        Test adding item to @waiting file.

        Given: @waiting.md exists
        When: Adding item with add_to_waiting
        Then: Item added to top of file with @waiting context
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_dir = repo_path / "docs" / "execution_system" / "00k-next-actions"
        actions_dir.mkdir(parents=True)

        waiting_file = actions_dir / "@waiting.md"
        waiting_file.write_text("""---
title: Waiting For
last_reviewed: 2025-10-20
---

- [ ] 2025-10-20 Existing waiting item @waiting +existing-project
""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        # Create dummy project for validation
        projects_dir = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / "health"
        projects_dir.mkdir(parents=True)
        (projects_dir / "receive-package.md").write_text("---\narea: Health\n---\n")

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_to_waiting(
            text="Wait for package delivery",
            project="receive-package"
        )

        # Then
        assert "✓ Successfully added to @waiting.md" in result
        content = waiting_file.read_text()
        today = date.today().strftime("%Y-%m-%d")
        expected = f"- [ ] {today} Wait for package delivery @waiting +receive-package"
        assert expected in content

    def test_adds_to_waiting_with_defer(self, tmp_path):
        """
        Test adding to waiting with defer date.

        Given: @waiting.md exists
        When: Adding item with defer date
        Then: Item includes defer:YYYY-MM-DD tag
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_dir = repo_path / "docs" / "execution_system" / "00k-next-actions"
        actions_dir.mkdir(parents=True)

        waiting_file = actions_dir / "@waiting.md"
        waiting_file.write_text("""---
title: Waiting For
last_reviewed: 2025-10-20
---

""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_to_waiting(
            text="Wait for delayed shipment",
            defer="2025-12-01"
        )

        # Then
        content = waiting_file.read_text()
        assert "defer:2025-12-01" in content


class TestActionManagerAddToDeferred:
    """Test ActionManager add_to_deferred functionality."""

    def test_adds_to_deferred_file(self, tmp_path):
        """
        Test adding item to @deferred file.

        Given: @deferred.md exists
        When: Adding item with add_to_deferred
        Then: Item added to top of file with @deferred context
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_dir = repo_path / "docs" / "execution_system" / "00k-next-actions"
        actions_dir.mkdir(parents=True)

        deferred_file = actions_dir / "@deferred.md"
        deferred_file.write_text("""---
title: Deferred
last_reviewed: 2025-10-20
---

""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        # Create dummy project for validation
        projects_dir = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / "health"
        projects_dir.mkdir(parents=True)
        (projects_dir / "future-project.md").write_text("---\narea: Health\n---\n")

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_to_deferred(
            text="Action for later",
            defer="2025-11-15",
            project="future-project"
        )

        # Then
        assert "✓ Successfully added to @deferred.md" in result
        content = deferred_file.read_text()
        today = date.today().strftime("%Y-%m-%d")
        assert f"- [ ] {today} Action for later @deferred +future-project defer:2025-11-15" in content


class TestActionManagerAddToIncubating:
    """Test ActionManager add_to_incubating functionality."""

    def test_adds_to_incubating_file(self, tmp_path):
        """
        Test adding item to @incubating file.

        Given: @incubating.md exists
        When: Adding item with add_to_incubating
        Then: Item added to top of file with @incubating context
        """
        # Given
        repo_path = tmp_path / "repo"
        actions_dir = repo_path / "docs" / "execution_system" / "00k-next-actions"
        actions_dir.mkdir(parents=True)

        incubating_file = actions_dir / "@incubating.md"
        incubating_file.write_text("""---
title: Incubating
last_reviewed: 2025-10-20
---

""")

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "gtd_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}]
        }))

        # Create dummy project for validation
        projects_dir = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / "health"
        projects_dir.mkdir(parents=True)
        (projects_dir / "experimental-idea.md").write_text("---\narea: Health\n---\n")

        config = ConfigManager(str(config_file))
        manager = ActionManager(config)

        # When
        result = manager.add_to_incubating(
            text="Maybe someday explore this",
            project="experimental-idea"
        )

        # Then
        assert "✓ Successfully added to @incubating.md" in result
        content = incubating_file.read_text()
        today = date.today().strftime("%Y-%m-%d")
        assert f"- [ ] {today} Maybe someday explore this @incubating +experimental-idea" in content
