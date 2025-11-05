"""Tests for AreaLister."""

import json
from pathlib import Path

import pytest

from execution_system_mcp.area_lister import AreaLister
from execution_system_mcp.config import ConfigManager


class TestAreaListerListAreas:
    """Test AreaLister list_areas functionality."""

    def test_returns_all_configured_areas(self, tmp_path):
        """
        Test listing all areas from config.

        Given: Config with multiple areas
        When: Calling list_areas()
        Then: Returns JSON with all areas and kebab names
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "execution_system_repo_path": str(tmp_path / "repo"),
            "areas": [
                {"name": "Health", "kebab": "health"},
                {"name": "Career", "kebab": "career"},
                {"name": "Mission", "kebab": "mission"}
            ]
        }))

        config = ConfigManager(str(config_file))
        lister = AreaLister(config)

        # When
        result = lister.list_areas()

        # Then
        parsed = json.loads(result)
        assert len(parsed["areas"]) == 3
        assert parsed["areas"][0] == {"name": "Health", "kebab": "health"}
        assert parsed["areas"][1] == {"name": "Career", "kebab": "career"}
        assert parsed["areas"][2] == {"name": "Mission", "kebab": "mission"}

    def test_returns_single_area(self, tmp_path):
        """
        Test listing when config has single area.

        Given: Config with one area
        When: Calling list_areas()
        Then: Returns JSON with single area
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "execution_system_repo_path": str(tmp_path / "repo"),
            "areas": [
                {"name": "Health", "kebab": "health"}
            ]
        }))

        config = ConfigManager(str(config_file))
        lister = AreaLister(config)

        # When
        result = lister.list_areas()

        # Then
        parsed = json.loads(result)
        assert len(parsed["areas"]) == 1
        assert parsed["areas"][0] == {"name": "Health", "kebab": "health"}

    def test_preserves_area_order(self, tmp_path):
        """
        Test that area order from config is preserved.

        Given: Config with areas in specific order
        When: Calling list_areas()
        Then: Returns areas in same order
        """
        # Given
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "execution_system_repo_path": str(tmp_path / "repo"),
            "areas": [
                {"name": "Zebra", "kebab": "zebra"},
                {"name": "Apple", "kebab": "apple"},
                {"name": "Banana", "kebab": "banana"}
            ]
        }))

        config = ConfigManager(str(config_file))
        lister = AreaLister(config)

        # When
        result = lister.list_areas()

        # Then
        parsed = json.loads(result)
        assert parsed["areas"][0]["name"] == "Zebra"
        assert parsed["areas"][1]["name"] == "Apple"
        assert parsed["areas"][2]["name"] == "Banana"
