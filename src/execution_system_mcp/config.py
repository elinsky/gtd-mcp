"""Configuration management for Execution System MCP server."""

import json
from pathlib import Path


class ConfigManager:
    """Manages Execution System MCP server configuration."""

    def __init__(self, config_path: str | None = None) -> None:
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file. If None, uses default location.

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file has invalid JSON
            ValueError: If config is missing required fields or has invalid values
        """
        if config_path is None:
            config_path = str(Path.home() / ".config" / "execution-system-mcp" / "config.json")

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, "r") as f:
            self._config = json.load(f)

        self._validate_config()

    def _validate_config(self) -> None:
        """
        Validate configuration has required fields.

        Raises:
            ValueError: If configuration is invalid
        """
        if "execution_system_repo_path" not in self._config:
            raise ValueError("Configuration missing required field: execution_system_repo_path")

        if "areas" not in self._config:
            raise ValueError("Configuration missing required field: areas")

        if not self._config["areas"]:
            raise ValueError("Configuration error: areas must be non-empty")

    def get_repo_path(self) -> str:
        """
        Get execution system repository path from configuration.

        Returns:
            Absolute path to execution system repository
        """
        return self._config["execution_system_repo_path"]

    def get_areas(self) -> list[dict[str, str]]:
        """
        Get list of configured areas of focus.

        Returns:
            List of area dictionaries with 'name' and 'kebab' keys
        """
        return self._config["areas"]

    def find_area_kebab(self, area_name: str) -> str | None:
        """
        Find kebab-case mapping for area name (case-insensitive).

        Args:
            area_name: Area name to look up (case-insensitive)

        Returns:
            Kebab-case area name if found, None otherwise
        """
        area_name_lower = area_name.lower()

        for area in self._config["areas"]:
            if area["name"].lower() == area_name_lower:
                return area["kebab"]

        return None
