# Complete Project - Implementation Tasks

## Phase 1: ProjectCompleter - Find Active Project

- [ ] Write test: test_finds_project_in_area_subdirectory
- [ ] Implement: `find_active_project()` basic search logic
- [ ] Write test: test_returns_none_for_nonexistent_project
- [ ] Implement: handle nonexistent project case
- [ ] Write test: test_returns_error_for_project_in_completed
- [ ] Implement: check completed folder and return error
- [ ] Write test: test_returns_error_for_project_in_incubator
- [ ] Implement: check incubator folder and return error
- [ ] Write test: test_handles_multiple_areas
- [ ] Implement: search across all area subdirectories
- [ ] Commit: "Add ProjectCompleter.find_active_project with folder validation"

## Phase 2: ProjectCompleter - Check 0k Blockers

- [ ] Write test: test_no_blockers_returns_empty_list
- [ ] Implement: `check_0k_blockers()` skeleton returning empty list
- [ ] Write test: test_finds_blocker_in_waiting
- [ ] Implement: parse @waiting.md for +{project} tags
- [ ] Write test: test_finds_blocker_in_incubating
- [ ] Implement: parse @incubating.md for +{project} tags
- [ ] Write test: test_finds_blocker_in_deferred
- [ ] Implement: parse @deferred.md for +{project} tags
- [ ] Write test: test_finds_blocker_in_context_file
- [ ] Implement: parse contexts/*.md files for +{project} tags
- [ ] Write test: test_finds_multiple_blockers_across_files
- [ ] Implement: aggregate blockers from all sources
- [ ] Write test: test_ignores_completed_items
- [ ] Implement: skip completed.md file
- [ ] Write test: test_ignores_checked_items
- [ ] Implement: only match `- [ ]` not `- [x]`
- [ ] Commit: "Add ProjectCompleter.check_0k_blockers with multi-file scanning"

## Phase 3: ProjectCompleter - Frontmatter Management

- [ ] Write test: test_parses_all_fields
- [ ] Implement: `parse_frontmatter()` basic YAML parsing
- [ ] Write test: test_handles_missing_optional_fields
- [ ] Implement: handle optional fields (due, started)
- [ ] Write test: test_preserves_field_order
- [ ] Implement: preserve field order in parsed dict
- [ ] Write test: test_adds_completed_with_todays_date
- [ ] Implement: `add_completed_date()` to add completed field
- [ ] Write test: test_preserves_all_existing_fields
- [ ] Implement: preserve all fields when adding completed
- [ ] Write test: test_maintains_field_order_with_due
- [ ] Implement: correct field order with due present
- [ ] Write test: test_maintains_field_order_without_due
- [ ] Implement: correct field order without due
- [ ] Write test: test_generates_valid_yaml_with_all_fields
- [ ] Implement: `generate_frontmatter_yaml()` to create YAML string
- [ ] Write test: test_maintains_correct_field_order
- [ ] Implement: ensure correct field order in output
- [ ] Write test: test_formats_dates_as_strings
- [ ] Implement: ensure dates are strings not date objects
- [ ] Commit: "Add ProjectCompleter frontmatter parsing and generation"

## Phase 4: ProjectCompleter - Complete Project

- [ ] Write test: test_successfully_completes_project_with_no_blockers
- [ ] Implement: `complete_project()` basic flow
- [ ] Write test: test_creates_completed_subdirectory_if_missing
- [ ] Implement: create completed/{area}/ directory
- [ ] Write test: test_preserves_file_content_and_frontmatter
- [ ] Implement: read full file, update frontmatter, write
- [ ] Write test: test_deletes_from_active_after_write
- [ ] Implement: delete active file after successful write
- [ ] Write test: test_returns_error_for_nonexistent_project
- [ ] Implement: error handling for missing project
- [ ] Write test: test_returns_error_with_blocking_items
- [ ] Implement: error handling for 0k blockers
- [ ] Commit: "Add ProjectCompleter.complete_project with atomic file operations"

## Phase 5: MCP Server Integration

- [ ] Write test: test_success_returns_formatted_message
- [ ] Implement: `complete_project_handler()` success case
- [ ] Write test: test_error_for_missing_title_parameter
- [ ] Implement: parameter validation
- [ ] Write test: test_error_for_project_not_found
- [ ] Implement: not found error handling
- [ ] Write test: test_error_lists_blocking_items
- [ ] Implement: format blocking items in error message
- [ ] Update: Add complete_project to server.py list_tools()
- [ ] Update: Add complete_project to server.py call_tool()
- [ ] Commit: "Add complete_project MCP tool to server"

## Phase 6: Integration Testing & Documentation

- [ ] Run: Full test suite to verify all 90+ tests pass
- [ ] Manual test: Complete a real project with no blockers
- [ ] Manual test: Try to complete project with blocking items
- [ ] Manual test: Try to complete nonexistent project
- [ ] Update: tasks.md with completion checkmarks
- [ ] Commit: "Complete project completion feature implementation"
- [ ] Push: All commits to remote
