# Tasks: GTD Project Creation

**Feature:** [GTD Project Creation](requirements.md)
**Status:** In Development

## 1. Project Setup and Configuration (TDD Cycle)

### Task: Create Project Structure and Dependencies

*   [x] **Description:** Initialize the Python MCP server project structure with necessary directories and install dependencies.
    *   Create `src/gtd_mcp/` directory structure
    *   Create `pyproject.toml` with dependencies: `mcp`, `pyyaml`, `pytest`, `pytest-mock`
    *   Create `README.md` with basic setup instructions
*   **Location:** `/gtd-mcp/`
*   **Expected Outcome:** Project structure exists with installable package
*   **Dependencies:** None

### Task: Write Unit Tests for ConfigManager

*   [ ] **Description:** Create unit tests for `ConfigManager` class covering:
    *   Loading valid configuration file successfully
    *   Failing gracefully on missing configuration file
    *   Failing gracefully on invalid JSON format
    *   Failing gracefully on missing required fields
    *   Case-insensitive area name lookup
    *   Returning None for non-existent area names
*   **Location:** `tests/unit/test_config.py`
*   **Expected Outcome:** Tests fail because `ConfigManager` does not exist yet
*   **Dependencies:** Task 1.1

### Task: Implement ConfigManager

*   [ ] **Description:** Implement `ConfigManager` class with methods:
    *   `__init__(config_path: str | None = None)`
    *   `get_repo_path() -> str`
    *   `get_areas() -> list[dict[str, str]]`
    *   `find_area_kebab(area_name: str) -> str | None`
*   **Location:** `src/gtd_mcp/config.py`
*   **Expected Outcome:** All tests from Task 1.2 pass
*   **Dependencies:** Task 1.2

### Task: Commit ConfigManager Implementation

*   [ ] **Description:** Commit the ConfigManager implementation with tests
*   **Commit Message:** `feat: implement ConfigManager for loading GTD repo configuration`
*   **Dependencies:** Task 1.3

## 2. Validation Logic (TDD Cycle)

### Task: Write Unit Tests for ProjectValidator Area Validation

*   [ ] **Description:** Create unit tests for `ProjectValidator.validate_area()` covering:
    *   Valid area names (exact case match)
    *   Valid area names (case-insensitive: "health", "Health", "HEALTH")
    *   Invalid area names with error message listing valid areas
*   **Location:** `tests/unit/test_validator.py`
*   **Expected Outcome:** Tests fail because `ProjectValidator` does not exist yet
*   **Dependencies:** Task 1.3

### Task: Implement ProjectValidator Area Validation

*   [ ] **Description:** Implement `ProjectValidator` class with `validate_area()` method
*   **Location:** `src/gtd_mcp/validator.py`
*   **Expected Outcome:** All tests from Task 2.1 pass
*   **Dependencies:** Task 2.1

### Task: Commit Area Validation

*   [ ] **Description:** Commit area validation implementation
*   **Commit Message:** `feat: implement area validation with case-insensitive matching`
*   **Dependencies:** Task 2.2

### Task: Write Unit Tests for Duplicate Detection

*   [ ] **Description:** Create unit tests for `ProjectValidator.check_duplicates()` covering:
    *   Detect duplicate in `active/` folder
    *   Detect duplicate in `incubator/` folder
    *   Detect duplicate in `completed/` folder
    *   Detect duplicate in `descoped/` folder
    *   Allow creation when no duplicates exist
*   **Location:** `tests/unit/test_validator.py`
*   **Expected Outcome:** Tests fail because `check_duplicates()` does not exist yet
*   **Dependencies:** Task 2.3

### Task: Implement Duplicate Detection

*   [ ] **Description:** Implement `ProjectValidator.check_duplicates()` method with filesystem scanning
    *   Add TODO comment: "Future optimization - maintain an in-memory index of existing projects"
*   **Location:** `src/gtd_mcp/validator.py`
*   **Expected Outcome:** All tests from Task 2.4 pass
*   **Dependencies:** Task 2.4

### Task: Commit Duplicate Detection

*   [ ] **Description:** Commit duplicate detection implementation
*   **Commit Message:** `feat: implement duplicate detection across all project folders`
*   **Dependencies:** Task 2.5

### Task: Write Unit Tests for Due Date Validation

*   [ ] **Description:** Create unit tests for `ProjectValidator.validate_due_date()` covering:
    *   Valid YYYY-MM-DD format
    *   Invalid formats (YYYY/MM/DD, MM-DD-YYYY, etc.)
    *   None/empty values
*   **Location:** `tests/unit/test_validator.py`
*   **Expected Outcome:** Tests fail because `validate_due_date()` does not exist yet
*   **Dependencies:** Task 2.6

### Task: Implement Due Date Validation

*   [ ] **Description:** Implement `ProjectValidator.validate_due_date()` method
*   **Location:** `src/gtd_mcp/validator.py`
*   **Expected Outcome:** All tests from Task 2.7 pass
*   **Dependencies:** Task 2.7

### Task: Commit Due Date Validation

*   [ ] **Description:** Commit due date validation implementation
*   **Commit Message:** `feat: implement due date validation for YYYY-MM-DD format`
*   **Dependencies:** Task 2.8

## 3. Template Generation (TDD Cycle)

### Task: Write Unit Tests for Standard Template

*   [ ] **Description:** Create unit tests for `TemplateEngine.generate_standard()` verifying:
    *   Title is included in markdown
    *   Sections: "1. PURPOSE - Why This Matters", "2. VISION/OUTCOME - What Success Looks Like", "Ideas Parking Lot"
*   **Location:** `tests/unit/test_templates.py`
*   **Expected Outcome:** Tests fail because `TemplateEngine` does not exist yet
*   **Dependencies:** Task 2.9

### Task: Implement Standard Template

*   [ ] **Description:** Implement `TemplateEngine.generate_standard()` method
*   **Location:** `src/gtd_mcp/templates.py`
*   **Expected Outcome:** All tests from Task 3.1 pass
*   **Dependencies:** Task 3.1

### Task: Commit Standard Template

*   [ ] **Description:** Commit standard template implementation
*   **Commit Message:** `feat: implement standard project template with GTD structure`
*   **Dependencies:** Task 3.2

### Task: Write Unit Tests for Habit Template

*   [ ] **Description:** Create unit tests for `TemplateEngine.generate_habit()` verifying:
    *   Status "Active" when folder is "active"
    *   Status "Incubating" when folder is "incubator"
    *   Sections: "1. PURPOSE", "2. VISION/OUTCOME", "3. APPROACH", "Next Actions"
*   **Location:** `tests/unit/test_templates.py`
*   **Expected Outcome:** Tests fail because `generate_habit()` does not exist yet
*   **Dependencies:** Task 3.3

### Task: Implement Habit Template

*   [ ] **Description:** Implement `TemplateEngine.generate_habit()` method
*   **Location:** `src/gtd_mcp/templates.py`
*   **Expected Outcome:** All tests from Task 3.4 pass
*   **Dependencies:** Task 3.4

### Task: Commit Habit Template

*   [ ] **Description:** Commit habit template implementation
*   **Commit Message:** `feat: implement habit project template with status field`
*   **Dependencies:** Task 3.5

### Task: Write Unit Tests for Coordination Template

*   [ ] **Description:** Create unit tests for `TemplateEngine.generate_coordination()` verifying:
    *   Sections: "1. PURPOSE", "2. PRINCIPLES", "3. VISION/OUTCOME", "Supporting Resources", "Ideas to Consider"
*   **Location:** `tests/unit/test_templates.py`
*   **Expected Outcome:** Tests fail because `generate_coordination()` does not exist yet
*   **Dependencies:** Task 3.6

### Task: Implement Coordination Template

*   [ ] **Description:** Implement `TemplateEngine.generate_coordination()` method
*   **Location:** `src/gtd_mcp/templates.py`
*   **Expected Outcome:** All tests from Task 3.7 pass
*   **Dependencies:** Task 3.7

### Task: Commit Coordination Template

*   [ ] **Description:** Commit coordination template implementation
*   **Commit Message:** `feat: implement coordination project template with principles section`
*   **Dependencies:** Task 3.8

## 4. Project Creation Logic (TDD Cycle)

### Task: Write Unit Tests for Kebab-Case Conversion

*   [ ] **Description:** Create unit tests for `ProjectCreator.to_kebab_case()` covering:
    *   "My Test Project!" → "my-test-project"
    *   "Order Pokémon Cards" → "order-pokemon-cards"
    *   Edge cases with numbers, multiple spaces, special characters
*   **Location:** `tests/unit/test_creator.py`
*   **Expected Outcome:** Tests fail because `ProjectCreator` does not exist yet
*   **Dependencies:** Task 3.9

### Task: Implement Kebab-Case Conversion

*   [ ] **Description:** Implement `ProjectCreator.to_kebab_case()` method
*   **Location:** `src/gtd_mcp/creator.py`
*   **Expected Outcome:** All tests from Task 4.1 pass
*   **Dependencies:** Task 4.1

### Task: Commit Kebab-Case Conversion

*   [ ] **Description:** Commit kebab-case conversion implementation
*   **Commit Message:** `feat: implement kebab-case conversion for project filenames`
*   **Dependencies:** Task 4.2

### Task: Write Unit Tests for YAML Frontmatter Generation

*   [ ] **Description:** Create unit tests for `ProjectCreator.generate_frontmatter()` covering:
    *   All required fields present (area, title, type, created, last_reviewed)
    *   `started` field included when folder is "active"
    *   `started` field excluded when folder is "incubator"
    *   `due` field included when provided
    *   `due` field excluded when not provided
    *   Valid YAML format
*   **Location:** `tests/unit/test_creator.py`
*   **Expected Outcome:** Tests fail because `generate_frontmatter()` does not exist yet
*   **Dependencies:** Task 4.3

### Task: Implement YAML Frontmatter Generation

*   [ ] **Description:** Implement `ProjectCreator.generate_frontmatter()` method with conditional field logic
*   **Location:** `src/gtd_mcp/creator.py`
*   **Expected Outcome:** All tests from Task 4.4 pass
*   **Dependencies:** Task 4.4

### Task: Commit YAML Frontmatter Generation

*   [ ] **Description:** Commit frontmatter generation implementation
*   **Commit Message:** `feat: implement YAML frontmatter generation with conditional fields`
*   **Dependencies:** Task 4.5

### Task: Write Unit Tests for Project File Creation

*   [ ] **Description:** Create unit tests for `ProjectCreator.create_project()` covering:
    *   Correct file path construction
    *   Directory creation with `parents=True, exist_ok=True`
    *   File content includes frontmatter + template
    *   Returns absolute file path
*   **Location:** `tests/unit/test_creator.py`
*   **Expected Outcome:** Tests fail because `create_project()` does not exist yet
*   **Dependencies:** Task 4.6

### Task: Implement Project File Creation

*   [ ] **Description:** Implement `ProjectCreator.create_project()` method
    *   Use mocked filesystem for tests
    *   Create directories as needed
    *   Write complete file content
*   **Location:** `src/gtd_mcp/creator.py`
*   **Expected Outcome:** All tests from Task 4.7 pass
*   **Dependencies:** Task 4.7

### Task: Commit Project File Creation

*   [ ] **Description:** Commit project creation implementation
*   **Commit Message:** `feat: implement project file creation with directory handling`
*   **Dependencies:** Task 4.8

## 5. MCP Server Integration (TDD Cycle)

### Task: Write Unit Tests for MCP Tool Registration

*   [ ] **Description:** Create unit tests for MCP server verifying:
    *   `create_project` tool is registered with correct schema
    *   Tool accepts all required parameters
    *   Tool accepts optional `due` parameter
*   **Location:** `tests/unit/test_server.py`
*   **Expected Outcome:** Tests fail because MCP server does not exist yet
*   **Dependencies:** Task 4.9

### Task: Implement MCP Server Tool Registration

*   [ ] **Description:** Implement MCP server with `create_project` tool registration using `mcp` SDK
*   **Location:** `src/gtd_mcp/server.py`
*   **Expected Outcome:** All tests from Task 5.1 pass
*   **Dependencies:** Task 5.1

### Task: Commit MCP Server Tool Registration

*   [ ] **Description:** Commit MCP server tool registration
*   **Commit Message:** `feat: implement MCP server with create_project tool registration`
*   **Dependencies:** Task 5.2

### Task: Write Unit Tests for MCP Tool Handler

*   [ ] **Description:** Create unit tests for `create_project` tool handler covering:
    *   Success case with valid parameters
    *   Error handling for validation failures
    *   Error handling for filesystem failures
    *   Correct success message format with file path
*   **Location:** `tests/unit/test_server.py`
*   **Expected Outcome:** Tests fail because tool handler does not exist yet
*   **Dependencies:** Task 5.3

### Task: Implement MCP Tool Handler

*   [ ] **Description:** Implement `create_project` tool handler that orchestrates:
    *   Configuration loading
    *   Validation (area, duplicates, due date)
    *   Template generation
    *   Project creation
    *   Success/error message formatting
*   **Location:** `src/gtd_mcp/server.py`
*   **Expected Outcome:** All tests from Task 5.4 pass
*   **Dependencies:** Task 5.4

### Task: Commit MCP Tool Handler

*   [ ] **Description:** Commit MCP tool handler implementation
*   **Commit Message:** `feat: implement create_project tool handler with validation and error handling`
*   **Dependencies:** Task 5.5

## 6. Integration Testing and Documentation

### Task: Write Integration Tests

*   [ ] **Description:** Create end-to-end integration tests using temporary filesystem:
    *   Create project in active/health
    *   Create project in incubator/career
    *   Verify duplicate detection works across folders
    *   Verify area validation with real config
*   **Location:** `tests/integration/test_end_to_end.py`
*   **Expected Outcome:** Integration tests pass with real filesystem operations (using tmp_path)
*   **Dependencies:** Task 5.6

### Task: Commit Integration Tests

*   [ ] **Description:** Commit integration tests
*   **Commit Message:** `test: add end-to-end integration tests for project creation`
*   **Dependencies:** Task 6.1

### Task: Create Example Configuration File

*   [ ] **Description:** Create example configuration file with:
    *   Placeholder GTD repo path
    *   All 11 areas with kebab-case mappings
    *   Comments explaining each field
*   **Location:** `config.example.json`
*   **Expected Outcome:** Users can copy and modify this config
*   **Dependencies:** Task 6.2

### Task: Update README with Setup Instructions

*   [ ] **Description:** Update README.md with:
    *   Installation instructions
    *   Configuration setup
    *   Claude Desktop integration steps
    *   Usage examples
*   **Location:** `README.md`
*   **Expected Outcome:** Complete setup documentation
*   **Dependencies:** Task 6.3

### Task: Commit Documentation

*   [ ] **Description:** Commit example config and README updates
*   **Commit Message:** `docs: add setup instructions and example configuration`
*   **Dependencies:** Task 6.4

## 7. Manual Testing and Deployment

### Task: Manual Testing with Claude Desktop

*   [ ] **Description:** Test MCP server integration with Claude Desktop:
    *   Install MCP server locally
    *   Configure Claude Desktop to use the server
    *   Create test projects via Claude
    *   Verify file creation in correct locations
    *   Test error cases (invalid area, duplicates)
*   **Expected Outcome:** All manual tests pass
*   **Dependencies:** Task 6.5

### Task: Final Cleanup and Release

*   [ ] **Description:** Final review and cleanup:
    *   Review all code for TODOs
    *   Verify test coverage
    *   Update version number
    *   Tag release
*   **Expected Outcome:** Ready for production use
*   **Dependencies:** Task 7.1
