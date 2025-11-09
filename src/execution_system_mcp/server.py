"""MCP server for project creation."""

import json
import os
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from execution_system_mcp.action_lister import ActionLister
from execution_system_mcp.action_manager import ActionManager
from execution_system_mcp.area_lister import AreaLister
from execution_system_mcp.auditor import Auditor
from execution_system_mcp.completer import ProjectCompleter
from execution_system_mcp.config import ConfigManager
from execution_system_mcp.creator import ProjectCreator
from execution_system_mcp.goal_lister import GoalLister
from execution_system_mcp.lister import ProjectLister
from execution_system_mcp.project_manager import ProjectManager
from execution_system_mcp.searcher import Searcher
from execution_system_mcp.validator import ProjectValidator


def create_project_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle create_project tool invocation.

    Args:
        params: Tool parameters (title, area, type, folder, due?)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        # Load configuration
        config = ConfigManager(config_path)

        # Extract parameters
        title = params.get("title")
        area = params.get("area")
        project_type = params.get("type")
        folder = params.get("folder")
        due = params.get("due")

        # Validate required parameters
        if not all([title, area, project_type, folder]):
            return "Error: Missing required parameter (title, area, type, or folder)"

        # Initialize validator and creator
        validator = ProjectValidator(config)
        creator = ProjectCreator(config)

        # Validate area
        is_valid, error_msg = validator.validate_area(area)
        if not is_valid:
            return f"Error: {error_msg}"

        # Check for duplicates
        filename = creator.to_kebab_case(title)
        is_duplicate, duplicate_folder = validator.check_duplicates(filename)
        if is_duplicate:
            return f"Error: Project '{title}' already exists in {duplicate_folder}/ as {filename}.md"

        # Validate due date if provided
        if due:
            is_valid, error_msg = validator.validate_due_date(due)
            if not is_valid:
                return f"Error: {error_msg}"

        # Create project
        file_path = creator.create_project(title, area, project_type, folder, due)

        return f"✓ Successfully created project '{title}' at {file_path}"

    except Exception as e:
        return f"Error: {str(e)}"


def list_active_projects_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle list_active_projects tool invocation.

    Args:
        params: Tool parameters (currently none)
        config_path: Optional path to config file (for testing)

    Returns:
        Formatted list of active projects grouped by area
    """
    try:
        # Load configuration
        config = ConfigManager(config_path)

        # Initialize lister
        lister = ProjectLister(config)

        # List active projects
        return lister.list_active_projects()

    except Exception as e:
        return f"Error: {str(e)}"


def list_projects_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle list_projects tool invocation.

    Args:
        params: Tool parameters (folder, group_by, filter_area, filter_has_due, completed_date_preset, filter_completed_start, filter_completed_end)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with projects grouped according to parameters
    """
    try:
        # Load configuration
        config = ConfigManager(config_path)

        # Initialize lister
        lister = ProjectLister(config)

        # Extract parameters with defaults
        folder = params.get("folder", "active")
        group_by = params.get("group_by", "area")
        filter_area = params.get("filter_area")
        filter_has_due = params.get("filter_has_due")
        completed_date_preset = params.get("completed_date_preset")
        filter_completed_start = params.get("filter_completed_start")
        filter_completed_end = params.get("filter_completed_end")

        # List projects
        result = lister.list_projects(
            folder=folder,
            group_by=group_by,
            filter_area=filter_area,
            filter_has_due=filter_has_due,
            completed_date_preset=completed_date_preset,
            filter_completed_start=filter_completed_start,
            filter_completed_end=filter_completed_end
        )

        # Return as JSON string
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def complete_project_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle complete_project tool invocation.

    Args:
        params: Tool parameters (title)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        # Load configuration
        config = ConfigManager(config_path)

        # Extract parameters
        title = params.get("title")

        # Validate required parameters
        if not title:
            return "Error: Missing required parameter (title)"

        # Initialize completer
        completer = ProjectCompleter(config)

        # Complete project
        return completer.complete_project(title)

    except Exception as e:
        return f"Error: {str(e)}"


def list_actions_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle list_actions tool invocation.

    Args:
        params: Tool parameters (group_by, include_states, filter_project, filter_context)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with actions grouped according to parameters
    """
    try:
        # Load configuration
        config = ConfigManager(config_path)

        # Initialize lister
        lister = ActionLister(config)

        # Extract parameters with defaults
        group_by = params.get("group_by", "project")
        include_states = params.get("include_states")
        filter_project = params.get("filter_project")
        filter_context = params.get("filter_context")

        # List actions
        result = lister.list_actions(
            group_by=group_by,
            include_states=include_states,
            filter_project=filter_project,
            filter_context=filter_context
        )

        # Return as JSON string
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def activate_project_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle activate_project tool invocation.

    Args:
        params: Tool parameters (title)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ProjectManager(config)
        title = params.get("title")

        if not title:
            return "Error: Missing required parameter (title)"

        return manager.activate_project(title)

    except Exception as e:
        return f"Error: {str(e)}"


def move_project_to_incubator_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle move_project_to_incubator tool invocation.

    Args:
        params: Tool parameters (title)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ProjectManager(config)
        title = params.get("title")

        if not title:
            return "Error: Missing required parameter (title)"

        return manager.move_project_to_incubator(title)

    except Exception as e:
        return f"Error: {str(e)}"


def descope_project_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle descope_project tool invocation.

    Args:
        params: Tool parameters (title)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ProjectManager(config)
        title = params.get("title")

        if not title:
            return "Error: Missing required parameter (title)"

        return manager.descope_project(title)

    except Exception as e:
        return f"Error: {str(e)}"


def update_project_due_date_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle update_project_due_date tool invocation.

    Args:
        params: Tool parameters (title, due_date)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ProjectManager(config)
        title = params.get("title")
        due_date = params.get("due_date")

        if not title:
            return "Error: Missing required parameter (title)"

        return manager.update_project_due_date(title, due_date)

    except Exception as e:
        return f"Error: {str(e)}"


def update_project_area_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle update_project_area tool invocation.

    Args:
        params: Tool parameters (title, new_area)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ProjectManager(config)
        title = params.get("title")
        new_area = params.get("new_area")

        if not title or not new_area:
            return "Error: Missing required parameters (title, new_area)"

        return manager.update_project_area(title, new_area)

    except Exception as e:
        return f"Error: {str(e)}"


def update_project_type_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle update_project_type tool invocation.

    Args:
        params: Tool parameters (title, project_type)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ProjectManager(config)
        title = params.get("title")
        project_type = params.get("project_type")

        if not title or not project_type:
            return "Error: Missing required parameters (title, project_type)"

        return manager.update_project_type(title, project_type)

    except Exception as e:
        return f"Error: {str(e)}"


def update_review_dates_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle update_review_dates tool invocation.

    Args:
        params: Tool parameters (target_type, filter_folder, filter_area, filter_names)
        config_path: Optional path to config file (for testing)

    Returns:
        Success message with count
    """
    try:
        config = ConfigManager(config_path)
        manager = ProjectManager(config)

        target_type = params.get("target_type", "projects")
        filter_folder = params.get("filter_folder")
        filter_area = params.get("filter_area")
        filter_names = params.get("filter_names")

        return manager.update_review_dates(
            target_type=target_type,
            filter_folder=filter_folder,
            filter_area=filter_area,
            filter_names=filter_names
        )

    except Exception as e:
        return f"Error: {str(e)}"


def audit_projects_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle audit_projects tool invocation.

    Args:
        params: Tool parameters (none)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with validation issues
    """
    try:
        config = ConfigManager(config_path)
        auditor = Auditor(config)
        result = auditor.audit_projects()
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def audit_orphan_projects_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle audit_orphan_projects tool invocation.

    Args:
        params: Tool parameters (none)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with orphan projects
    """
    try:
        config = ConfigManager(config_path)
        auditor = Auditor(config)
        result = auditor.audit_orphan_projects()
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def audit_orphan_actions_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle audit_orphan_actions tool invocation.

    Args:
        params: Tool parameters (none)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with orphan actions
    """
    try:
        config = ConfigManager(config_path)
        auditor = Auditor(config)
        result = auditor.audit_orphan_actions()
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def audit_action_files_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle audit_action_files tool invocation.

    Args:
        params: Tool parameters (none)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with action file validation issues
    """
    try:
        config = ConfigManager(config_path)
        auditor = Auditor(config)
        result = auditor.audit_action_files()
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def list_projects_needing_review_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle list_projects_needing_review tool invocation.

    Args:
        params: Tool parameters (days_threshold)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with projects needing review
    """
    try:
        config = ConfigManager(config_path)
        auditor = Auditor(config)
        days_threshold = params.get("days_threshold", 7)
        result = auditor.list_projects_needing_review(days_threshold)
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def list_actions_needing_review_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle list_actions_needing_review tool invocation.

    Args:
        params: Tool parameters (days_threshold)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with action files needing review
    """
    try:
        config = ConfigManager(config_path)
        auditor = Auditor(config)
        days_threshold = params.get("days_threshold", 7)
        result = auditor.list_actions_needing_review(days_threshold)
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def search_projects_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle search_projects tool invocation.

    Args:
        params: Tool parameters (query, folder, filter_area)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with matching projects
    """
    try:
        config = ConfigManager(config_path)
        searcher = Searcher(config)

        query = params.get("query")
        if not query:
            return json.dumps({"error": "Missing required parameter (query)"}, indent=2)

        folder = params.get("folder", "all")
        filter_area = params.get("filter_area")

        result = searcher.search_projects(
            query=query,
            folder=folder,
            filter_area=filter_area
        )
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def search_actions_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle search_actions tool invocation.

    Args:
        params: Tool parameters (query, include_states, filter_project, filter_context)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with matching actions
    """
    try:
        config = ConfigManager(config_path)
        searcher = Searcher(config)

        query = params.get("query")
        if not query:
            return json.dumps({"error": "Missing required parameter (query)"}, indent=2)

        include_states = params.get("include_states")
        filter_project = params.get("filter_project")
        filter_context = params.get("filter_context")

        result = searcher.search_actions(
            query=query,
            include_states=include_states,
            filter_project=filter_project,
            filter_context=filter_context
        )
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def list_areas_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle list_areas tool invocation.

    Args:
        params: Tool parameters (none)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with list of areas
    """
    try:
        config = ConfigManager(config_path)
        lister = AreaLister(config)
        return lister.list_areas()

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def add_action_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle add_action tool invocation.

    Args:
        params: Tool parameters (text, context, project?, due?, defer?, action_date?)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ActionManager(config)

        text = params.get("text")
        context = params.get("context")

        if not text or not context:
            return "Error: Missing required parameters (text, context)"

        return manager.add_action(
            text=text,
            context=context,
            project=params.get("project"),
            due=params.get("due"),
            defer=params.get("defer"),
            action_date=params.get("action_date")
        )

    except Exception as e:
        return f"Error: {str(e)}"


def add_to_waiting_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle add_to_waiting tool invocation.

    Args:
        params: Tool parameters (text, project, due?, defer?, action_date?)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ActionManager(config)

        text = params.get("text")
        project = params.get("project")

        if not text:
            return "Error: Missing required parameter (text)"

        if not project:
            return "Error: Missing required parameter (project)"

        return manager.add_to_waiting(
            text=text,
            project=project,
            due=params.get("due"),
            defer=params.get("defer"),
            action_date=params.get("action_date")
        )

    except Exception as e:
        return f"Error: {str(e)}"


def add_to_deferred_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle add_to_deferred tool invocation.

    Args:
        params: Tool parameters (text, project, defer?, action_date?)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ActionManager(config)

        text = params.get("text")
        project = params.get("project")

        if not text:
            return "Error: Missing required parameter (text)"

        if not project:
            return "Error: Missing required parameter (project)"

        return manager.add_to_deferred(
            text=text,
            project=project,
            defer=params.get("defer"),
            action_date=params.get("action_date")
        )

    except Exception as e:
        return f"Error: {str(e)}"


def add_to_incubating_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle add_to_incubating tool invocation.

    Args:
        params: Tool parameters (text, project?, action_date?)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ActionManager(config)

        text = params.get("text")
        if not text:
            return "Error: Missing required parameter (text)"

        return manager.add_to_incubating(
            text=text,
            project=params.get("project"),
            action_date=params.get("action_date")
        )

    except Exception as e:
        return f"Error: {str(e)}"


def complete_action_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle complete_action tool invocation.

    Args:
        params: Tool parameters (file_path, line_number, completion_date?)
        config_path: Optional path to config file (for testing)

    Returns:
        Success or error message
    """
    try:
        config = ConfigManager(config_path)
        manager = ActionManager(config)

        file_path = params.get("file_path")
        line_number = params.get("line_number")

        if not file_path or line_number is None:
            return "Error: Missing required parameters (file_path, line_number)"

        return manager.complete_action(
            file_path=file_path,
            line_number=line_number,
            completion_date=params.get("completion_date")
        )

    except Exception as e:
        return f"Error: {str(e)}"


def list_goals_handler(params: dict, config_path: str | None = None) -> str:
    """
    Handle list_goals tool invocation.

    Args:
        params: Tool parameters (none)
        config_path: Optional path to config file (for testing)

    Returns:
        JSON string with goals grouped by folder
    """
    try:
        config = ConfigManager(config_path)
        lister = GoalLister(config)
        return lister.list_goals()

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def main():
    """Run the MCP server."""
    server = Server("execution-system-mcp")

    # Get config path from environment or use default
    config_path = os.environ.get("EXECUTION_SYSTEM_MCP_CONFIG")
    if not config_path:
        config_path = str(Path.home() / ".config" / "execution-system-mcp" / "config.json")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="create_project",
                description="Create a new project file with YAML frontmatter and structured markdown template",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title (will be converted to kebab-case for filename)"
                        },
                        "area": {
                            "type": "string",
                            "description": "Area of focus (must match configured areas, case-insensitive)"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["standard", "coordination", "habit"],
                            "description": "Project type determining the template structure"
                        },
                        "folder": {
                            "type": "string",
                            "enum": ["active", "incubator"],
                            "description": "Target folder (active projects include 'started' date)"
                        },
                        "due": {
                            "type": "string",
                            "description": "Optional due date in ISO format YYYY-MM-DD",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["title", "area", "type", "folder"]
                }
            ),
            Tool(
                name="list_active_projects",
                description="List all active projects grouped by area of focus with due dates and type indicators",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="complete_project",
                description="Complete an active project by moving it to the completed folder after validating all 0k work is done",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title (exact match, case-sensitive)"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="list_projects",
                description="List projects with flexible filtering and grouping options. Returns JSON with project metadata including title, area, type, folder, due date, completed date, started date, created date, and filename.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "folder": {
                            "type": "string",
                            "enum": ["active", "incubator", "completed", "all"],
                            "description": "Which folder(s) to list projects from (default: active)"
                        },
                        "group_by": {
                            "type": "string",
                            "enum": ["area", "due_date", "flat"],
                            "description": "How to group projects: 'area' groups by area of focus, 'due_date' groups by urgency (Overdue/This Week/Later/No Due Date), 'flat' returns all projects in one group sorted by title (default: area)"
                        },
                        "filter_area": {
                            "type": "string",
                            "description": "Optional: filter to show only projects from a specific area (case-insensitive)"
                        },
                        "filter_has_due": {
                            "type": "boolean",
                            "description": "Optional: filter to show only projects with due dates (true) or without due dates (false)"
                        },
                        "completed_date_preset": {
                            "type": "string",
                            "enum": ["last_week", "last_month", "week_to_date", "month_to_date", "quarter_to_date", "year_to_date"],
                            "description": "Optional: filter completed projects by preset date range (week starts Sunday)"
                        },
                        "filter_completed_start": {
                            "type": "string",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                            "description": "Optional: custom start date for completed projects filter (YYYY-MM-DD), requires filter_completed_end"
                        },
                        "filter_completed_end": {
                            "type": "string",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                            "description": "Optional: custom end date for completed projects filter (YYYY-MM-DD), requires filter_completed_start"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="list_actions",
                description="List next actions with flexible filtering and grouping options. Returns JSON with action metadata including text, date, context, project, due date, defer date, and state.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "group_by": {
                            "type": "string",
                            "enum": ["project", "context", "flat"],
                            "description": "How to group actions: 'project' groups by project folder (active/incubator), then project, then state (next/waiting/deferred/incubating); 'context' groups by context (@macbook, @phone, @waiting, etc.); 'flat' returns ungrouped list (default: project)"
                        },
                        "include_states": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["next", "waiting", "deferred", "incubating"]
                            },
                            "description": "Which action states to include (default: all states)"
                        },
                        "filter_project": {
                            "type": "string",
                            "description": "Optional: filter to show only actions for a specific project (use kebab-case filename)"
                        },
                        "filter_context": {
                            "type": "string",
                            "description": "Optional: filter to show only actions for a specific context (e.g., '@macbook', '@phone')"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="activate_project",
                description="Move a project from incubator to active folder. Adds 'started' date to project YAML. No validation for existing actions required - you activate first, then add actions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title (exact match, case-sensitive)"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="move_project_to_incubator",
                description="Move a project from active to incubator folder. Removes 'started' date from project YAML. Validates that project has NO incomplete 0k actions (next, waiting, deferred, or incubating) - all actions must be complete or removed first.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title (exact match, case-sensitive)"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="descope_project",
                description="Move a project to descoped folder (archives project as out-of-scope). Adds 'descoped' date and removes 'started' date. Validates that project has NO incomplete 0k actions - all actions must be complete or removed first. Creates descoped/{area}/ folder if needed.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title (exact match, case-sensitive)"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="update_project_due_date",
                description="Update or remove a project's due date in YAML frontmatter.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title (exact match, case-sensitive)"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "ISO date string (YYYY-MM-DD) or null to remove due date",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="update_project_area",
                description="Update a project's area of focus. Moves the project file to the new area's folder and updates YAML frontmatter. Area must match configured areas (case-insensitive).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title (exact match, case-sensitive)"
                        },
                        "new_area": {
                            "type": "string",
                            "description": "New area name (must match configured areas, case-insensitive)"
                        }
                    },
                    "required": ["title", "new_area"]
                }
            ),
            Tool(
                name="update_project_type",
                description="Update a project's type in YAML frontmatter. Types: standard (regular project), habit (recurring practice), coordination (multi-stakeholder coordination).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Project title (exact match, case-sensitive)"
                        },
                        "project_type": {
                            "type": "string",
                            "enum": ["standard", "habit", "coordination"],
                            "description": "New project type"
                        }
                    },
                    "required": ["title", "project_type"]
                }
            ),
            Tool(
                name="update_review_dates",
                description="Bulk update 'last_reviewed' dates for projects and/or action lists. Useful during weekly review to mark items as reviewed. Supports flexible filtering by folder, area, or specific names.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target_type": {
                            "type": "string",
                            "enum": ["projects", "actions", "all"],
                            "description": "What to update: 'projects' (project files), 'actions' (action list files), or 'all' (both) (default: projects)"
                        },
                        "filter_folder": {
                            "type": "string",
                            "enum": ["active", "incubator", "all"],
                            "description": "For projects: which folder(s) to update (default: all folders)"
                        },
                        "filter_area": {
                            "type": "string",
                            "description": "For projects: update only projects in specific area (case-insensitive)"
                        },
                        "filter_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific project titles or action list names to update (e.g., ['Project Name'] or ['@macbook', '@waiting'])"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="audit_projects",
                description="Validate all project files for data quality issues. Checks: required fields (area, title, last_reviewed), valid areas (match configured areas), valid types (standard/habit/coordination), valid date formats (YYYY-MM-DD). Returns JSON with list of validation issues.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="audit_orphan_projects",
                description="Find projects without any associated next actions. Only checks standard projects (excludes habit and coordination types). Returns JSON with list of orphan projects including file path.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="audit_orphan_actions",
                description="Find next actions that reference non-existent projects or use invalid contexts. Validates: project tags (+project) exist as project files, context tags (@context) match existing context files. Returns JSON with list of orphan actions.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="audit_action_files",
                description="Validate all action list files (next.md, @waiting.md, etc.) for data quality issues. Checks: required YAML fields (title, last_reviewed). Returns JSON with list of validation issues.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="list_projects_needing_review",
                description="Find projects that haven't been reviewed recently. A project needs review if 'last_reviewed' is >= threshold days ago (inclusive) or missing. Default threshold: 7 days. Returns JSON with projects grouped by area.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days_threshold": {
                            "type": "integer",
                            "description": "Number of days since last review (inclusive) to flag for review (default: 7)"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="list_actions_needing_review",
                description="Find action list files (@macbook.md, @waiting.md, etc.) that haven't been reviewed recently. An action file needs review if 'last_reviewed' is >= threshold days ago (inclusive) or missing. Default threshold: 7 days. Returns JSON with action files needing review.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days_threshold": {
                            "type": "integer",
                            "description": "Number of days since last review (inclusive) to flag for review (default: 7)"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="search_projects",
                description="Search for projects by text in title or content. Case-insensitive search. Returns JSON with matching projects including title, area, folder, filename, match location (title/content), and snippet showing match context.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Text to search for (case-insensitive)"
                        },
                        "folder": {
                            "type": "string",
                            "enum": ["active", "incubator", "completed", "all"],
                            "description": "Which folder(s) to search (default: all)"
                        },
                        "filter_area": {
                            "type": "string",
                            "description": "Optional: filter to show only projects from a specific area (case-insensitive)"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="search_actions",
                description="Search for actions by text in action content. Case-insensitive search. Returns JSON with matching actions including action text, state, context, project tag, file, and full line.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Text to search for (case-insensitive)"
                        },
                        "include_states": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["next", "waiting", "deferred", "incubating"]
                            },
                            "description": "Which action states to include (default: all states)"
                        },
                        "filter_project": {
                            "type": "string",
                            "description": "Optional: filter to show only actions for a specific project (use kebab-case filename)"
                        },
                        "filter_context": {
                            "type": "string",
                            "description": "Optional: filter to show only actions for a specific context (e.g., '@macbook', '@phone')"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="list_areas",
                description="List all configured areas of focus from config. Returns JSON with area names and kebab-case identifiers.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="add_action",
                description="Add a next action to a context list file. Validates that project exists if +project tag is provided. Action is added to top of context file with creation date.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Action text (without @context or +project tags)"
                        },
                        "context": {
                            "type": "string",
                            "description": "Context tag (e.g., '@macbook', '@phone', '@home')"
                        },
                        "project": {
                            "type": "string",
                            "description": "Optional project filename in kebab-case (e.g., 'ml-refresh'). Will be validated against existing projects."
                        },
                        "due": {
                            "type": "string",
                            "description": "Optional due date in ISO format YYYY-MM-DD",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "defer": {
                            "type": "string",
                            "description": "Optional defer date in ISO format YYYY-MM-DD",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "action_date": {
                            "type": "string",
                            "description": "Optional creation date in ISO format YYYY-MM-DD (defaults to today)",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["text", "context"]
                }
            ),
            Tool(
                name="add_to_waiting",
                description="Add an item to the @waiting.md list. Use for things waiting on others or external events. Requires a project to be specified.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Action text (without @waiting tag)"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project filename in kebab-case (required)"
                        },
                        "due": {
                            "type": "string",
                            "description": "Optional due date in ISO format YYYY-MM-DD",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "defer": {
                            "type": "string",
                            "description": "Optional defer date in ISO format YYYY-MM-DD",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "action_date": {
                            "type": "string",
                            "description": "Optional creation date in ISO format YYYY-MM-DD (defaults to today)",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["text", "project"]
                }
            ),
            Tool(
                name="add_to_deferred",
                description="Add an item to the @deferred.md list. Use for actions that cannot be done now but will be actionable at a specific future date. Requires a project to be specified.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Action text (without @deferred tag)"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project filename in kebab-case (required)"
                        },
                        "defer": {
                            "type": "string",
                            "description": "Defer date in ISO format YYYY-MM-DD - when this becomes actionable",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "action_date": {
                            "type": "string",
                            "description": "Optional creation date in ISO format YYYY-MM-DD (defaults to today)",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["text", "project"]
                }
            ),
            Tool(
                name="add_to_incubating",
                description="Add an item to the @incubating.md list. Use for ideas that might become projects or actions but need more thought.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Action or idea text (without @incubating tag)"
                        },
                        "project": {
                            "type": "string",
                            "description": "Optional project filename in kebab-case"
                        },
                        "action_date": {
                            "type": "string",
                            "description": "Optional creation date in ISO format YYYY-MM-DD (defaults to today)",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="complete_action",
                description="Complete an action by line number. Marks action as complete, moves to completed.md, removes from source file.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Relative path to action file (e.g., 'contexts/@macbook.md' or '@waiting.md')"
                        },
                        "line_number": {
                            "type": "integer",
                            "description": "Line number of action to complete (1-indexed as shown in editors)"
                        },
                        "completion_date": {
                            "type": "string",
                            "description": "Optional completion date in ISO format YYYY-MM-DD (defaults to today)",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["file_path", "line_number"]
                }
            ),
            Tool(
                name="list_goals",
                description="List all goals (30k level) grouped by folder. Only returns files with type: goal in YAML frontmatter. Returns JSON with active and incubator goals.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        if name == "create_project":
            result = create_project_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "list_active_projects":
            result = list_active_projects_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "list_projects":
            result = list_projects_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "list_actions":
            result = list_actions_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "complete_project":
            result = complete_project_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "activate_project":
            result = activate_project_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "move_project_to_incubator":
            result = move_project_to_incubator_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "descope_project":
            result = descope_project_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "update_project_due_date":
            result = update_project_due_date_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "update_project_area":
            result = update_project_area_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "update_project_type":
            result = update_project_type_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "update_review_dates":
            result = update_review_dates_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "audit_projects":
            result = audit_projects_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "audit_orphan_projects":
            result = audit_orphan_projects_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "audit_orphan_actions":
            result = audit_orphan_actions_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "audit_action_files":
            result = audit_action_files_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "list_projects_needing_review":
            result = list_projects_needing_review_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "list_actions_needing_review":
            result = list_actions_needing_review_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "search_projects":
            result = search_projects_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "search_actions":
            result = search_actions_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "list_areas":
            result = list_areas_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "add_action":
            result = add_action_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "add_to_waiting":
            result = add_to_waiting_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "add_to_deferred":
            result = add_to_deferred_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "add_to_incubating":
            result = add_to_incubating_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "complete_action":
            result = complete_action_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        elif name == "list_goals":
            result = list_goals_handler(arguments, config_path)
            return [TextContent(type="text", text=result)]
        else:
            raise ValueError(f"Unknown tool: {name}")

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
