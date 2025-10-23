"""Validation logic for GTD project creation."""

from gtd_mcp.config import ConfigManager


class ProjectValidator:
    """Validates project creation parameters."""

    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize validator with configuration.

        Args:
            config: ConfigManager instance with loaded configuration
        """
        self._config = config

    def validate_area(self, area: str) -> tuple[bool, str | None]:
        """
        Validate area parameter against configured areas.

        Args:
            area: Area name to validate (case-insensitive)

        Returns:
            Tuple of (is_valid, error_message)
            - If valid: (True, None)
            - If invalid: (False, error message with list of valid areas)
        """
        # Check if area exists (case-insensitive)
        area_kebab = self._config.find_area_kebab(area)

        if area_kebab is not None:
            return (True, None)

        # Build error message with list of valid areas
        valid_areas = [area_dict["name"] for area_dict in self._config.get_areas()]
        valid_areas_str = ", ".join(valid_areas)
        error_msg = f"Invalid area '{area}'. Valid areas: {valid_areas_str}"

        return (False, error_msg)
