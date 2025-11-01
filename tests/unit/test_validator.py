"""Tests for ProjectValidator."""

import json
from pathlib import Path

import pytest

from gtd_mcp.config import ConfigManager
from gtd_mcp.validator import ProjectValidator


class TestProjectValidatorValidateArea:
    """Test ProjectValidator.validate_area()."""

    def test_valid_area_exact_case(self, tmp_path):
        """
        Test validating area with exact case match.

        Given: ProjectValidator with "Health" configured
        When: Calling validate_area("Health")
        Then: Returns (True, None)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_area("Health")

        # Then
        assert is_valid is True
        assert error_msg is None

    def test_valid_area_case_insensitive(self, tmp_path):
        """
        Test validating area with different case.

        Given: ProjectValidator with "Health" configured
        When: Calling validate_area("health")
        Then: Returns (True, None)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_area("health")

        # Then
        assert is_valid is True
        assert error_msg is None

    def test_invalid_area_returns_error(self, tmp_path):
        """
        Test validating non-existent area returns error.

        Given: ProjectValidator with only "Health" and "Career" configured
        When: Calling validate_area("Finance")
        Then: Returns (False, error message with valid areas)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"},
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_area("Finance")

        # Then
        assert is_valid is False
        assert error_msg is not None
        assert "Finance" in error_msg
        assert "Health" in error_msg
        assert "Career" in error_msg

    def test_multi_word_area_validation(self, tmp_path):
        """
        Test validating multi-word area name.

        Given: ProjectValidator with "Personal Growth Systems" configured
        When: Calling validate_area("personal growth systems")
        Then: Returns (True, None)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [
                {"name": "Personal Growth Systems", "kebab": "personal-growth-systems"}
            ],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_area("personal growth systems")

        # Then
        assert is_valid is True
        assert error_msg is None


class TestProjectValidatorCheckDuplicates:
    """Test ProjectValidator.check_duplicates()."""

    def test_no_duplicate_in_empty_repo(self, tmp_path):
        """
        Test checking duplicates in empty repository.

        Given: Empty execution system repository with no projects
        When: Calling check_duplicates("test-project")
        Then: Returns (False, None)
        """
        # Given
        repo_path = tmp_path / "gtd-repo"
        repo_path.mkdir()
        projects_path = repo_path / "docs" / "execution_system" / "10k-projects"
        for folder in ["active", "incubator", "completed", "descoped"]:
            (projects_path / folder).mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_duplicate, folder_name = validator.check_duplicates("test-project")

        # Then
        assert is_duplicate is False
        assert folder_name is None

    def test_detect_duplicate_in_active(self, tmp_path):
        """
        Test detecting duplicate in active folder.

        Given: Project "test-project.md" exists in active/health/
        When: Calling check_duplicates("test-project")
        Then: Returns (True, "active")
        """
        # Given
        repo_path = tmp_path / "gtd-repo"
        projects_path = repo_path / "docs" / "execution_system" / "10k-projects"
        active_health = projects_path / "active" / "health"
        active_health.mkdir(parents=True)
        (active_health / "test-project.md").write_text("# Test Project")

        for folder in ["incubator", "completed", "descoped"]:
            (projects_path / folder).mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_duplicate, folder_name = validator.check_duplicates("test-project")

        # Then
        assert is_duplicate is True
        assert folder_name == "active"

    def test_detect_duplicate_in_incubator(self, tmp_path):
        """
        Test detecting duplicate in incubator folder.

        Given: Project "test-project.md" exists in incubator/career/
        When: Calling check_duplicates("test-project")
        Then: Returns (True, "incubator")
        """
        # Given
        repo_path = tmp_path / "gtd-repo"
        projects_path = repo_path / "docs" / "execution_system" / "10k-projects"
        incubator_career = projects_path / "incubator" / "career"
        incubator_career.mkdir(parents=True)
        (incubator_career / "test-project.md").write_text("# Test Project")

        for folder in ["active", "completed", "descoped"]:
            (projects_path / folder).mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_duplicate, folder_name = validator.check_duplicates("test-project")

        # Then
        assert is_duplicate is True
        assert folder_name == "incubator"

    def test_detect_duplicate_in_completed(self, tmp_path):
        """
        Test detecting duplicate in completed folder.

        Given: Project "test-project.md" exists in completed/health/
        When: Calling check_duplicates("test-project")
        Then: Returns (True, "completed")
        """
        # Given
        repo_path = tmp_path / "gtd-repo"
        projects_path = repo_path / "docs" / "execution_system" / "10k-projects"
        completed_health = projects_path / "completed" / "health"
        completed_health.mkdir(parents=True)
        (completed_health / "test-project.md").write_text("# Test Project")

        for folder in ["active", "incubator", "descoped"]:
            (projects_path / folder).mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_duplicate, folder_name = validator.check_duplicates("test-project")

        # Then
        assert is_duplicate is True
        assert folder_name == "completed"

    def test_detect_duplicate_in_descoped(self, tmp_path):
        """
        Test detecting duplicate in descoped folder.

        Given: Project "test-project.md" exists in descoped/finance/
        When: Calling check_duplicates("test-project")
        Then: Returns (True, "descoped")
        """
        # Given
        repo_path = tmp_path / "gtd-repo"
        projects_path = repo_path / "docs" / "execution_system" / "10k-projects"
        descoped_finance = projects_path / "descoped" / "finance"
        descoped_finance.mkdir(parents=True)
        (descoped_finance / "test-project.md").write_text("# Test Project")

        for folder in ["active", "incubator", "completed"]:
            (projects_path / folder).mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Finance", "kebab": "finance"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_duplicate, folder_name = validator.check_duplicates("test-project")

        # Then
        assert is_duplicate is True
        assert folder_name == "descoped"

    def test_no_duplicate_different_filename(self, tmp_path):
        """
        Test no duplicate when filename is different.

        Given: Project "other-project.md" exists in active/health/
        When: Calling check_duplicates("test-project")
        Then: Returns (False, None)
        """
        # Given
        repo_path = tmp_path / "gtd-repo"
        projects_path = repo_path / "docs" / "execution_system" / "10k-projects"
        active_health = projects_path / "active" / "health"
        active_health.mkdir(parents=True)
        (active_health / "other-project.md").write_text("# Other Project")

        for folder in ["incubator", "completed", "descoped"]:
            (projects_path / folder).mkdir(parents=True)

        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_duplicate, folder_name = validator.check_duplicates("test-project")

        # Then
        assert is_duplicate is False
        assert folder_name is None


class TestProjectValidatorValidateDueDate:
    """Test ProjectValidator.validate_due_date()."""

    def test_valid_due_date(self, tmp_path):
        """
        Test validating correct YYYY-MM-DD format.

        Given: ProjectValidator instance
        When: Calling validate_due_date("2025-12-31")
        Then: Returns (True, None)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_due_date("2025-12-31")

        # Then
        assert is_valid is True
        assert error_msg is None

    def test_invalid_date_format_slashes(self, tmp_path):
        """
        Test rejecting YYYY/MM/DD format.

        Given: ProjectValidator instance
        When: Calling validate_due_date("2025/12/31")
        Then: Returns (False, error message)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_due_date("2025/12/31")

        # Then
        assert is_valid is False
        assert error_msg is not None
        assert "YYYY-MM-DD" in error_msg

    def test_invalid_date_format_american(self, tmp_path):
        """
        Test rejecting MM-DD-YYYY format.

        Given: ProjectValidator instance
        When: Calling validate_due_date("12-31-2025")
        Then: Returns (False, error message)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_due_date("12-31-2025")

        # Then
        assert is_valid is False
        assert error_msg is not None

    def test_empty_string_is_invalid(self, tmp_path):
        """
        Test rejecting empty string.

        Given: ProjectValidator instance
        When: Calling validate_due_date("")
        Then: Returns (False, error message)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_due_date("")

        # Then
        assert is_valid is False
        assert error_msg is not None

    def test_invalid_date_values(self, tmp_path):
        """
        Test rejecting invalid date values.

        Given: ProjectValidator instance
        When: Calling validate_due_date("2025-13-45")
        Then: Returns (False, error message)
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        validator = ProjectValidator(config)

        # When
        is_valid, error_msg = validator.validate_due_date("2025-13-45")

        # Then
        assert is_valid is False
        assert error_msg is not None
