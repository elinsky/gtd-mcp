"""MCP server for GTD project creation."""

import json
import os
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from gtd_mcp.action_lister import ActionLister
from gtd_mcp.completer import ProjectCompleter
from gtd_mcp.config import ConfigManager
from gtd_mcp.creator import ProjectCreator
from gtd_mcp.lister import ProjectLister
from gtd_mcp.validator import ProjectValidator


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
        params: Tool parameters (folder, group_by, filter_area, filter_has_due)
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

        # List projects
        result = lister.list_projects(
            folder=folder,
            group_by=group_by,
            filter_area=filter_area,
            filter_has_due=filter_has_due
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


async def main():
    """Run the MCP server."""
    server = Server("gtd-mcp")

    # Get config path from environment or use default
    config_path = os.environ.get("GTD_MCP_CONFIG")
    if not config_path:
        config_path = str(Path.home() / ".config" / "gtd-mcp" / "config.json")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="create_project",
                description="Create a new GTD project file with YAML frontmatter and structured markdown template",
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
                description="List all active GTD projects grouped by area of focus with due dates and type indicators",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="complete_project",
                description="Complete an active GTD project by moving it to the completed folder after validating all 0k work is done",
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
                description="List GTD projects with flexible filtering and grouping options. Returns JSON with project metadata including title, area, type, folder, due date, and filename.",
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
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="list_actions",
                description="List GTD next actions with flexible filtering and grouping options. Returns JSON with action metadata including text, date, context, project, due date, defer date, and state.",
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
        else:
            raise ValueError(f"Unknown tool: {name}")

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
