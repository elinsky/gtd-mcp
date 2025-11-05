"""Tests for ConfigManager."""

import json
from pathlib import Path

import pytest

from execution_system_mcp.config import ConfigManager


class TestConfigManagerInit:
    """Test ConfigManager initialization."""

    def test_load_valid_config(self, tmp_path):
        """
        Test loading a valid configuration file.

        Given: Valid config file with repo path and areas
        When: Initializing ConfigManager
        Then: ConfigManager loads successfully
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

        # When
        config = ConfigManager(str(config_file))

        # Then
        assert config is not None

    def test_fail_on_missing_config(self):
        """
        Test failure when config file doesn't exist.

        Given: Path to non-existent config file
        When: Initializing ConfigManager
        Then: Raises FileNotFoundError
        """
        # Given
        config_path = "/nonexistent/config.json"

        # When/Then
        with pytest.raises(FileNotFoundError):
            ConfigManager(config_path)

    def test_fail_on_invalid_json(self, tmp_path):
        """
        Test failure when config file has invalid JSON.

        Given: Config file with malformed JSON
        When: Initializing ConfigManager
        Then: Raises JSONDecodeError
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text("{invalid json")

        # When/Then
        with pytest.raises(json.JSONDecodeError):
            ConfigManager(str(config_file))

    def test_fail_on_missing_execution_system_repo_path(self, tmp_path):
        """
        Test failure when execution_system_repo_path field is missing.

        Given: Config file without execution_system_repo_path field
        When: Initializing ConfigManager
        Then: Raises ValueError with 'execution_system_repo_path' message
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))

        # When/Then
        with pytest.raises(ValueError, match="execution_system_repo_path"):
            ConfigManager(str(config_file))

    def test_fail_on_missing_areas(self, tmp_path):
        """
        Test failure when areas field is missing.

        Given: Config file without areas field
        When: Initializing ConfigManager
        Then: Raises ValueError with 'areas' message
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
        }
        config_file.write_text(json.dumps(config_data))

        # When/Then
        with pytest.raises(ValueError, match="areas"):
            ConfigManager(str(config_file))

    def test_fail_on_empty_areas(self, tmp_path):
        """
        Test failure when areas array is empty.

        Given: Config file with empty areas array
        When: Initializing ConfigManager
        Then: Raises ValueError with 'non-empty' message
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [],
        }
        config_file.write_text(json.dumps(config_data))

        # When/Then
        with pytest.raises(ValueError, match="non-empty"):
            ConfigManager(str(config_file))


class TestConfigManagerGetRepoPath:
    """Test ConfigManager.get_repo_path()."""

    def test_returns_repo_path(self, tmp_path):
        """
        Test getting repository path from config.

        Given: ConfigManager with repo path "/path/to/repo"
        When: Calling get_repo_path()
        Then: Returns "/path/to/repo"
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))

        # When
        actual_path = config.get_repo_path()

        # Then
        assert actual_path == "/path/to/repo"


class TestConfigManagerGetAreas:
    """Test ConfigManager.get_areas()."""

    def test_returns_all_areas(self, tmp_path):
        """
        Test getting all areas from config.

        Given: ConfigManager with 2 areas defined
        When: Calling get_areas()
        Then: Returns list of 2 area dictionaries
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

        # When
        actual_areas = config.get_areas()

        # Then
        assert len(actual_areas) == 2
        assert actual_areas[0]["name"] == "Health"
        assert actual_areas[0]["kebab"] == "health"
        assert actual_areas[1]["name"] == "Career"
        assert actual_areas[1]["kebab"] == "career"


class TestConfigManagerFindAreaKebab:
    """Test ConfigManager.find_area_kebab()."""

    def test_exact_case_match(self, tmp_path):
        """
        Test finding area with exact case match.

        Given: ConfigManager with "Health" area
        When: Calling find_area_kebab("Health")
        Then: Returns "health" kebab value
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))

        # When
        actual_kebab = config.find_area_kebab("Health")

        # Then
        assert actual_kebab == "health"

    def test_lowercase_lookup(self, tmp_path):
        """
        Test finding area with lowercase name.

        Given: ConfigManager with "Health" area
        When: Calling find_area_kebab("health")
        Then: Returns "health" kebab value
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))

        # When
        actual_kebab = config.find_area_kebab("health")

        # Then
        assert actual_kebab == "health"

    def test_uppercase_lookup(self, tmp_path):
        """
        Test finding area with uppercase name.

        Given: ConfigManager with "Health" area
        When: Calling find_area_kebab("HEALTH")
        Then: Returns "health" kebab value
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))

        # When
        actual_kebab = config.find_area_kebab("HEALTH")

        # Then
        assert actual_kebab == "health"

    def test_multi_word_area_lookup(self, tmp_path):
        """
        Test finding multi-word area with case-insensitive match.

        Given: ConfigManager with "Personal Growth Systems" area
        When: Calling find_area_kebab("personal growth systems")
        Then: Returns "personal-growth-systems" kebab value
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

        # When
        actual_kebab = config.find_area_kebab("personal growth systems")

        # Then
        assert actual_kebab == "personal-growth-systems"

    def test_nonexistent_area_returns_none(self, tmp_path):
        """
        Test finding non-existent area returns None.

        Given: ConfigManager with "Health" area only
        When: Calling find_area_kebab("Career")
        Then: Returns None
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": "/path/to/repo",
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))

        # When
        actual_kebab = config.find_area_kebab("Career")

        # Then
        assert actual_kebab is None
