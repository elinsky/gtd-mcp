"""Tests for TemplateEngine."""

import pytest

from execution_system_mcp.templates import TemplateEngine


class TestTemplateEngineGenerateStandard:
    """Test TemplateEngine.generate_standard()."""

    def test_includes_title(self):
        """
        Test standard template includes title.

        Given: Title "Test Project"
        When: Calling generate_standard("Test Project")
        Then: Returns markdown with "# Test Project"
        """
        # Given
        title = "Test Project"

        # When
        result = TemplateEngine.generate_standard(title)

        # Then
        assert "# Test Project" in result

    def test_includes_purpose_section(self):
        """
        Test standard template includes PURPOSE section.

        Given: Title "Test Project"
        When: Calling generate_standard("Test Project")
        Then: Returns markdown with "## 1. PURPOSE - Why This Matters"
        """
        # Given
        title = "Test Project"

        # When
        result = TemplateEngine.generate_standard(title)

        # Then
        assert "## 1. PURPOSE - Why This Matters" in result

    def test_includes_vision_section(self):
        """
        Test standard template includes VISION/OUTCOME section.

        Given: Title "Test Project"
        When: Calling generate_standard("Test Project")
        Then: Returns markdown with "## 2. VISION/OUTCOME - What Success Looks Like"
        """
        # Given
        title = "Test Project"

        # When
        result = TemplateEngine.generate_standard(title)

        # Then
        assert "## 2. VISION/OUTCOME - What Success Looks Like" in result

    def test_includes_ideas_section(self):
        """
        Test standard template includes Ideas Parking Lot section.

        Given: Title "Test Project"
        When: Calling generate_standard("Test Project")
        Then: Returns markdown with "## Ideas Parking Lot"
        """
        # Given
        title = "Test Project"

        # When
        result = TemplateEngine.generate_standard(title)

        # Then
        assert "## Ideas Parking Lot" in result


class TestTemplateEngineGenerateHabit:
    """Test TemplateEngine.generate_habit()."""

    def test_includes_title(self):
        """
        Test habit template includes title.

        Given: Title "Daily Exercise" and folder "active"
        When: Calling generate_habit("Daily Exercise", "active")
        Then: Returns markdown with "# Daily Exercise"
        """
        # Given
        title = "Daily Exercise"
        folder = "active"

        # When
        result = TemplateEngine.generate_habit(title, folder)

        # Then
        assert "# Daily Exercise" in result

    def test_active_folder_shows_active_status(self):
        """
        Test habit template shows "Active" status for active folder.

        Given: Title "Daily Exercise" and folder "active"
        When: Calling generate_habit("Daily Exercise", "active")
        Then: Returns markdown with "**Status:** Active"
        """
        # Given
        title = "Daily Exercise"
        folder = "active"

        # When
        result = TemplateEngine.generate_habit(title, folder)

        # Then
        assert "**Status:** Active" in result

    def test_incubator_folder_shows_incubating_status(self):
        """
        Test habit template shows "Incubating" status for incubator folder.

        Given: Title "Daily Exercise" and folder "incubator"
        When: Calling generate_habit("Daily Exercise", "incubator")
        Then: Returns markdown with "**Status:** Incubating"
        """
        # Given
        title = "Daily Exercise"
        folder = "incubator"

        # When
        result = TemplateEngine.generate_habit(title, folder)

        # Then
        assert "**Status:** Incubating" in result

    def test_includes_purpose_section(self):
        """
        Test habit template includes PURPOSE section.

        Given: Title and folder
        When: Calling generate_habit()
        Then: Returns markdown with "## 1. PURPOSE - Why This Matters"
        """
        # Given
        title = "Daily Exercise"
        folder = "active"

        # When
        result = TemplateEngine.generate_habit(title, folder)

        # Then
        assert "## 1. PURPOSE - Why This Matters" in result

    def test_includes_vision_section(self):
        """
        Test habit template includes VISION/OUTCOME section.

        Given: Title and folder
        When: Calling generate_habit()
        Then: Returns markdown with "## 2. VISION/OUTCOME - What Success Looks Like"
        """
        # Given
        title = "Daily Exercise"
        folder = "active"

        # When
        result = TemplateEngine.generate_habit(title, folder)

        # Then
        assert "## 2. VISION/OUTCOME - What Success Looks Like" in result

    def test_includes_approach_section(self):
        """
        Test habit template includes APPROACH section.

        Given: Title and folder
        When: Calling generate_habit()
        Then: Returns markdown with "## 3. APPROACH"
        """
        # Given
        title = "Daily Exercise"
        folder = "active"

        # When
        result = TemplateEngine.generate_habit(title, folder)

        # Then
        assert "## 3. APPROACH" in result

    def test_includes_next_actions_section(self):
        """
        Test habit template includes Next Actions section.

        Given: Title and folder
        When: Calling generate_habit()
        Then: Returns markdown with "## Next Actions"
        """
        # Given
        title = "Daily Exercise"
        folder = "active"

        # When
        result = TemplateEngine.generate_habit(title, folder)

        # Then
        assert "## Next Actions" in result


class TestTemplateEngineGenerateCoordination:
    """Test TemplateEngine.generate_coordination()."""

    def test_includes_title(self):
        """
        Test coordination template includes title.

        Given: Title "Q4 Planning"
        When: Calling generate_coordination("Q4 Planning")
        Then: Returns markdown with "# Q4 Planning"
        """
        # Given
        title = "Q4 Planning"

        # When
        result = TemplateEngine.generate_coordination(title)

        # Then
        assert "# Q4 Planning" in result

    def test_includes_purpose_section(self):
        """
        Test coordination template includes PURPOSE section.

        Given: Title "Q4 Planning"
        When: Calling generate_coordination("Q4 Planning")
        Then: Returns markdown with "## 1. PURPOSE - Why This Matters"
        """
        # Given
        title = "Q4 Planning"

        # When
        result = TemplateEngine.generate_coordination(title)

        # Then
        assert "## 1. PURPOSE - Why This Matters" in result

    def test_includes_principles_section(self):
        """
        Test coordination template includes PRINCIPLES section.

        Given: Title "Q4 Planning"
        When: Calling generate_coordination("Q4 Planning")
        Then: Returns markdown with "## 2. PRINCIPLES - Standards & Values"
        """
        # Given
        title = "Q4 Planning"

        # When
        result = TemplateEngine.generate_coordination(title)

        # Then
        assert "## 2. PRINCIPLES - Standards & Values" in result

    def test_includes_vision_section(self):
        """
        Test coordination template includes VISION/OUTCOME section.

        Given: Title "Q4 Planning"
        When: Calling generate_coordination("Q4 Planning")
        Then: Returns markdown with "## 3. VISION/OUTCOME - What Success Looks Like"
        """
        # Given
        title = "Q4 Planning"

        # When
        result = TemplateEngine.generate_coordination(title)

        # Then
        assert "## 3. VISION/OUTCOME - What Success Looks Like" in result

    def test_includes_supporting_resources_section(self):
        """
        Test coordination template includes Supporting Resources section.

        Given: Title "Q4 Planning"
        When: Calling generate_coordination("Q4 Planning")
        Then: Returns markdown with "## Supporting Resources"
        """
        # Given
        title = "Q4 Planning"

        # When
        result = TemplateEngine.generate_coordination(title)

        # Then
        assert "## Supporting Resources" in result

    def test_includes_ideas_section(self):
        """
        Test coordination template includes Ideas to Consider section.

        Given: Title "Q4 Planning"
        When: Calling generate_coordination("Q4 Planning")
        Then: Returns markdown with "## Ideas to Consider"
        """
        # Given
        title = "Q4 Planning"

        # When
        result = TemplateEngine.generate_coordination(title)

        # Then
        assert "## Ideas to Consider" in result
