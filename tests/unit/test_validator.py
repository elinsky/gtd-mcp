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
            "gtd_repo_path": "/path/to/repo",
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
            "gtd_repo_path": "/path/to/repo",
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
            "gtd_repo_path": "/path/to/repo",
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
            "gtd_repo_path": "/path/to/repo",
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
