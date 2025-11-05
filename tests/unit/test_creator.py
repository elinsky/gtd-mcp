"""Tests for ProjectCreator."""

import json
from datetime import date
from pathlib import Path

import pytest
import yaml

from execution_system_mcp.config import ConfigManager
from execution_system_mcp.creator import ProjectCreator


class TestProjectCreatorToKebabCase:
    """Test ProjectCreator.to_kebab_case()."""

    def test_basic_conversion(self):
        """
        Test basic string to kebab-case.

        Given: String "My Test Project"
        When: Calling to_kebab_case("My Test Project")
        Then: Returns "my-test-project"
        """
        # Given
        text = "My Test Project"

        # When
        result = ProjectCreator.to_kebab_case(text)

        # Then
        assert result == "my-test-project"

    def test_removes_special_characters(self):
        """
        Test removing special characters.

        Given: String "My Test Project!"
        When: Calling to_kebab_case("My Test Project!")
        Then: Returns "my-test-project"
        """
        # Given
        text = "My Test Project!"

        # When
        result = ProjectCreator.to_kebab_case(text)

        # Then
        assert result == "my-test-project"

    def test_handles_unicode(self):
        """
        Test handling unicode characters.

        Given: String "Order Pokémon Cards"
        When: Calling to_kebab_case("Order Pokémon Cards")
        Then: Returns "order-pokemon-cards"
        """
        # Given
        text = "Order Pokémon Cards"

        # When
        result = ProjectCreator.to_kebab_case(text)

        # Then
        assert result == "order-pokemon-cards"

    def test_handles_multiple_spaces(self):
        """
        Test handling multiple consecutive spaces.

        Given: String "Multiple   Spaces   Here"
        When: Calling to_kebab_case("Multiple   Spaces   Here")
        Then: Returns "multiple-spaces-here"
        """
        # Given
        text = "Multiple   Spaces   Here"

        # When
        result = ProjectCreator.to_kebab_case(text)

        # Then
        assert result == "multiple-spaces-here"

    def test_preserves_numbers(self):
        """
        Test preserving numbers in output.

        Given: String "Project 2024 Q4"
        When: Calling to_kebab_case("Project 2024 Q4")
        Then: Returns "project-2024-q4"
        """
        # Given
        text = "Project 2024 Q4"

        # When
        result = ProjectCreator.to_kebab_case(text)

        # Then
        assert result == "project-2024-q4"


class TestProjectCreatorGenerateFrontmatter:
    """Test ProjectCreator.generate_frontmatter()."""

    def test_includes_all_required_fields(self, tmp_path):
        """
        Test frontmatter includes all required fields.

        Given: ProjectCreator with config
        When: Calling generate_frontmatter()
        Then: Frontmatter includes area, title, type, created, last_reviewed
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(tmp_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        creator = ProjectCreator(config)

        # When
        result = creator.generate_frontmatter(
            area="Health",
            title="Test Project",
            project_type="standard",
            folder="active"
        )

        # Then
        frontmatter = yaml.safe_load(result.strip("---\n"))
        assert frontmatter["area"] == "Health"
        assert frontmatter["title"] == "Test Project"
        assert frontmatter["type"] == "standard"
        assert "created" in frontmatter
        assert "last_reviewed" in frontmatter

    def test_includes_started_for_active_folder(self, tmp_path):
        """
        Test frontmatter includes started field for active folder.

        Given: ProjectCreator with config
        When: Calling generate_frontmatter() with folder="active"
        Then: Frontmatter includes started field
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(tmp_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        creator = ProjectCreator(config)

        # When
        result = creator.generate_frontmatter(
            area="Health",
            title="Test Project",
            project_type="standard",
            folder="active"
        )

        # Then
        frontmatter = yaml.safe_load(result.strip("---\n"))
        assert "started" in frontmatter

    def test_excludes_started_for_incubator_folder(self, tmp_path):
        """
        Test frontmatter excludes started field for incubator folder.

        Given: ProjectCreator with config
        When: Calling generate_frontmatter() with folder="incubator"
        Then: Frontmatter does not include started field
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(tmp_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        creator = ProjectCreator(config)

        # When
        result = creator.generate_frontmatter(
            area="Health",
            title="Test Project",
            project_type="standard",
            folder="incubator"
        )

        # Then
        frontmatter = yaml.safe_load(result.strip("---\n"))
        assert "started" not in frontmatter

    def test_includes_due_when_provided(self, tmp_path):
        """
        Test frontmatter includes due field when provided.

        Given: ProjectCreator with config
        When: Calling generate_frontmatter() with due="2025-12-31"
        Then: Frontmatter includes due: 2025-12-31
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(tmp_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        creator = ProjectCreator(config)

        # When
        result = creator.generate_frontmatter(
            area="Health",
            title="Test Project",
            project_type="standard",
            folder="active",
            due="2025-12-31"
        )

        # Then
        frontmatter = yaml.safe_load(result.strip("---\n"))
        assert str(frontmatter["due"]) == "2025-12-31"

    def test_excludes_due_when_not_provided(self, tmp_path):
        """
        Test frontmatter excludes due field when not provided.

        Given: ProjectCreator with config
        When: Calling generate_frontmatter() without due parameter
        Then: Frontmatter does not include due field
        """
        # Given
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(tmp_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        creator = ProjectCreator(config)

        # When
        result = creator.generate_frontmatter(
            area="Health",
            title="Test Project",
            project_type="standard",
            folder="active"
        )

        # Then
        frontmatter = yaml.safe_load(result.strip("---\n"))
        assert "due" not in frontmatter


class TestProjectCreatorCreateProject:
    """Test ProjectCreator.create_project()."""

    def test_creates_file_in_correct_location(self, tmp_path):
        """
        Test project file created in correct location.

        Given: ProjectCreator with config
        When: Calling create_project()
        Then: File created at {repo}/docs/execution_system/10k-projects/{folder}/{area}/{filename}.md
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        creator = ProjectCreator(config)

        # When
        result_path = creator.create_project(
            title="Test Project",
            area="Health",
            project_type="standard",
            folder="active"
        )

        # Then
        expected_path = repo_path / "docs" / "execution_system" / "10k-projects" / "active" / "health" / "test-project.md"
        assert Path(result_path) == expected_path
        assert expected_path.exists()

    def test_creates_directories_if_missing(self, tmp_path):
        """
        Test creates area directory if it doesn't exist.

        Given: ProjectCreator with config and non-existent area directory
        When: Calling create_project()
        Then: Area directory is created
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Career", "kebab": "career"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        creator = ProjectCreator(config)

        # When
        result_path = creator.create_project(
            title="New Job Search",
            area="Career",
            project_type="standard",
            folder="active"
        )

        # Then
        assert Path(result_path).parent.exists()
        assert Path(result_path).exists()

    def test_file_includes_frontmatter_and_template(self, tmp_path):
        """
        Test created file includes both frontmatter and template.

        Given: ProjectCreator with config
        When: Calling create_project()
        Then: File content includes YAML frontmatter and markdown template
        """
        # Given
        repo_path = tmp_path / "repo"
        config_file = tmp_path / "config.json"
        config_data = {
            "execution_system_repo_path": str(repo_path),
            "areas": [{"name": "Health", "kebab": "health"}],
        }
        config_file.write_text(json.dumps(config_data))
        config = ConfigManager(str(config_file))
        creator = ProjectCreator(config)

        # When
        result_path = creator.create_project(
            title="Test Project",
            area="Health",
            project_type="standard",
            folder="active"
        )

        # Then
        content = Path(result_path).read_text()
        assert content.startswith("---\n")
        assert "# Test Project" in content
        assert "## 1. PURPOSE - Why This Matters" in content
