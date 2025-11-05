# Execution System MCP Server

An AI-native execution system powered by Claude and the Model Context Protocol.

## Why This Exists

Traditional productivity tools force you to context-switch between thinking and doing. You stop your work, open an app, navigate through menus, fill out forms, and then return to what you were doing. This friction means you often don't capture things at all, or you create incomplete entries that need cleanup later.

This MCP server eliminates that friction. You stay in conversation with Claude while working, and your execution system updates naturally:

- **Working on code?** "Add action: refactor the auth module @macbook +api-redesign due:2025-11-15"
- **In a meeting?** "Add to waiting: Sarah's feedback on the proposal"
- **Reviewing your week?** "List all actions for the ml-refresh project"
- **Planning?** "Show me all Health projects that haven't been reviewed in 7 days"

No app switching. No form filling. Just natural language that keeps you in flow while maintaining a rigorous execution system.

## Features

The server implements the horizons of focus model through the Model Context Protocol:

### 0k - Next Actions (Ground Level)
- **Add actions** to context files (@macbook, @phone, @errands) with automatic project validation
- **Add to special lists**: @waiting (for others), @deferred (specific future date), @incubating (someday/maybe)
- **Complete actions** by line number with automatic archival to completed.md
- **List actions** with flexible filtering by context, project, and state
- **Search actions** by text with state and context filters
- Full support for todo.txt format with creation dates, contexts, projects, due/defer dates

### 10k - Projects (Current Initiatives)
- **Create projects** with YAML frontmatter and three templates (standard, coordination, habit)
- **List projects** with flexible filtering and grouping by area, due date, or flat
- **Search projects** by text in title or content
- **Complete projects** with validation that all actions are done
- **Manage lifecycle**: activate from incubator, move back to incubator, descope
- **Update metadata**: due dates, areas, types, review dates (bulk updates supported)
- **Audit tools**: validate data quality, find orphan projects/actions, identify items needing review

### 20k - Areas of Focus (Responsibilities)
- **List areas** of focus from configuration
- Automatic area validation across all projects and goals

### 30k - Goals (1-2 Year Objectives)
- **List goals** from active and incubator folders
- Automatic filtering by `type: goal` in YAML frontmatter
- Support for nested goal directories with supporting materials

All tools include comprehensive validation, error handling, and JSON output for programmatic access.

## Installation

```bash
# Clone the repository
git clone https://github.com/elinsky/execution-system-mcp.git
cd execution-system-mcp

# Install dependencies
pip install -e ".[dev]"
```

## Configuration

Create a configuration file at `~/.config/execution-system-mcp/config.json`:

```json
{
  "execution_system_repo_path": "/absolute/path/to/your/execution-system-repo",
  "areas": [
    {"name": "Health", "kebab": "health"},
    {"name": "Learning", "kebab": "learning"},
    {"name": "Career", "kebab": "career"},
    {"name": "Mission", "kebab": "mission"},
    {"name": "Personal Growth Systems", "kebab": "personal-growth-systems"},
    {"name": "Social Relationships", "kebab": "social-relationships"},
    {"name": "Romance", "kebab": "romance"},
    {"name": "Emotional Health", "kebab": "emotional-health"},
    {"name": "Finance", "kebab": "finance"},
    {"name": "Character and Values", "kebab": "character-and-values"},
    {"name": "Hobbies and Recreation", "kebab": "hobbies-and-recreation"}
  ]
}
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py
```

## Usage

The MCP server integrates with Claude Desktop. Once configured, you can manage your execution system by asking Claude:

### 0k - Action Examples
- "Add action 'Buy groceries' to @errands context for project meal-planning"
- "Add 'Wait for package delivery' to @waiting with defer date 2025-11-15"
- "Complete the action on line 7 of contexts/@macbook.md"
- "List all actions for the ml-refresh project"

### 10k - Project Examples
- "Create a new project titled 'Learn Python' in the Learning area as a standard project in active folder"
- "List all active projects in the Health area"
- "Complete the project 'Learn Python'"
- "Search for projects about machine learning"

### 20k - Area Examples
- "List all my areas of focus"

### 30k - Goal Examples
- "List all active goals"
- "Show me goals in the incubator"

Claude will use the appropriate MCP tools to interact with your execution system.

## Available Tools

### 0k - Action Tools
- `add_action` - Add next action to context file with project validation
- `add_to_waiting` - Add item to @waiting list
- `add_to_deferred` - Add item to @deferred list
- `add_to_incubating` - Add item to @incubating list
- `complete_action` - Complete action by line number
- `list_actions` - List actions with flexible filtering and grouping
- `search_actions` - Search actions by text with filters

### 10k - Project Tools
- `create_project` - Create new project with YAML frontmatter and template
- `list_active_projects` - List all active projects grouped by area
- `list_projects` - List projects with flexible filtering (folder, area, due date)
- `complete_project` - Complete project with validation for incomplete actions
- `activate_project` - Move project from incubator to active
- `move_project_to_incubator` - Move project from active to incubator
- `descope_project` - Move project to descoped folder
- `update_project_due_date` - Add or remove project due date
- `update_project_area` - Change project's area of focus
- `update_project_type` - Change project type (standard/coordination/habit)
- `update_review_dates` - Bulk update last_reviewed dates
- `search_projects` - Search projects by text with filters

### 20k - Area Tools
- `list_areas` - List all configured areas of focus

### 30k - Goal Tools
- `list_goals` - List goals from active and incubator folders

### Audit & Health Check Tools
- `audit_projects` - Validate project data quality
- `audit_orphan_projects` - Find projects without actions
- `audit_orphan_actions` - Find actions with invalid projects/contexts
- `audit_action_files` - Validate action file data quality
- `list_projects_needing_review` - Find projects not reviewed recently
- `list_actions_needing_review` - Find action files not reviewed recently

## Project Structure

```
execution-system-mcp/
├── src/
│   └── execution_system_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server with all tool handlers
│       ├── config.py          # Configuration manager
│       ├── creator.py         # Project creation
│       ├── lister.py          # Project listing
│       ├── completer.py       # Project completion
│       ├── validator.py       # Validation logic
│       ├── templates.py       # Project templates
│       ├── project_manager.py # Project lifecycle management
│       ├── action_manager.py  # Action creation and completion
│       ├── action_lister.py   # Action listing
│       ├── goal_lister.py     # Goal listing
│       ├── area_lister.py     # Area listing
│       ├── searcher.py        # Search functionality
│       └── auditor.py         # Data quality audits
├── tests/
│   └── unit/                  # 185 comprehensive unit tests
├── pyproject.toml
└── README.md
```

## License

MIT
