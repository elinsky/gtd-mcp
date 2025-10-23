"""MCP server for GTD project creation."""

import os
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

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
        else:
            raise ValueError(f"Unknown tool: {name}")

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
