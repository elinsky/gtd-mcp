"""Tests for MCP server."""

import json
from pathlib import Path

import pytest

from execution_system_mcp.server import create_project_handler


class TestCreateProjectHandler:
    """Test create_project tool handler."""

    def test_success_creates_project_file(self, tmp_path):
        """
        Test successful project creation.

        Given: Valid project parameters
        When: Calling create_project_handler()
        Then: Project file is created and success message returned
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))

        params = {
            "title": "Test Project",
            "area": "Health",
            "type": "standard",
            "folder": "active"
        }

        # When
        result = create_project_handler(params, str(config_file))

        # Then
        assert "success" in result.lower() or "created" in result.lower()
        assert "test-project.md" in result

        # Verify file exists
        project_file = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / "health" / "test-project.md"
        assert project_file.exists()

    def test_invalid_area_returns_error(self, tmp_path):
        """
        Test invalid area returns error message.

        Given: Invalid area parameter
        When: Calling create_project_handler()
        Then: Error message with list of valid areas returned
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))

        params = {
            "title": "Test Project",
            "area": "InvalidArea",
            "type": "standard",
            "folder": "active"
        }

        # When
        result = create_project_handler(params, str(config_file))

        # Then
        assert "error" in result.lower() or "invalid" in result.lower()
        assert "Health" in result

    def test_duplicate_project_returns_error(self, tmp_path):
        """
        Test duplicate project returns error message.

        Given: Project with same name already exists
        When: Calling create_project_handler()
        Then: Error message indicating duplicate returned
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))

        # Create existing project
        existing_project = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / "health" / "test-project.md"
        existing_project.parent.mkdir(parents=True)
        existing_project.write_text("# Existing Project")

        params = {
            "title": "Test Project",
            "area": "Health",
            "type": "standard",
            "folder": "active"
        }

        # When
        result = create_project_handler(params, str(config_file))

        # Then
        assert "error" in result.lower() or "exists" in result.lower() or "duplicate" in result.lower()

    def test_invalid_due_date_returns_error(self, tmp_path):
        """
        Test invalid due date returns error message.

        Given: Invalid due date format
        When: Calling create_project_handler()
        Then: Error message about date format returned
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))

        params = {
            "title": "Test Project",
            "area": "Health",
            "type": "standard",
            "folder": "active",
            "due": "12-31-2025"  # Invalid format
        }

        # When
        result = create_project_handler(params, str(config_file))

        # Then
        assert "error" in result.lower() or "invalid" in result.lower()
        assert "date" in result.lower()

    def test_success_with_due_date(self, tmp_path):
        """
        Test successful project creation with due date.

        Given: Valid project parameters including due date
        When: Calling create_project_handler()
        Then: Project file created with due date in frontmatter
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))

        params = {
            "title": "Test Project",
            "area": "Health",
            "type": "standard",
            "folder": "active",
            "due": "2025-12-31"
        }

        # When
        result = create_project_handler(params, str(config_file))

        # Then
        assert "success" in result.lower() or "created" in result.lower()

        # Verify due date in file
        project_file = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / "health" / "test-project.md"
        content = project_file.read_text()
        assert "due: 2025-12-31" in content
