"""Area listing functionality."""

import json

from gtd_mcp.config import ConfigManager


class AreaLister:
    """Lists areas of focus."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize lister with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config

    def list_areas(self) -> str:
        """
        List all configured areas of focus.

        Returns:
            JSON string with areas list
        """
        areas = self._config.get_areas()
        return json.dumps({"areas": areas}, indent=2)
