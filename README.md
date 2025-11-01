# GTD MCP Server

MCP (Model Context Protocol) server for managing a complete GTD (Getting Things Done) system with projects, actions, and goals.

## Features

### Project Management (10k Projects)
- **Create projects** with YAML frontmatter and templates (standard, coordination, habit)
- **List projects** with flexible filtering and grouping
- **Search projects** by text in title or content
- **Complete projects** with validation for incomplete actions
- **Manage project lifecycle**: activate, move to incubator, descope
- **Update project metadata**: due dates, areas, types, review dates
- **Audit tools**: validate data quality, find orphan projects/actions, identify items needing review

### Action Management (0k Next Actions)
- **Add actions** to context files (@macbook, @phone, etc.) with project validation
- **Add to special lists**: @waiting, @deferred, @incubating
- **Complete actions** by line number with automatic move to completed.md
- **List actions** with flexible filtering by context, project, and state
- **Search actions** by text with state and context filters

### Goal Management (30k Goals)
- **List goals** from active and incubator folders
- Automatic filtering by `type: goal` in YAML frontmatter
- Support for nested goal directories with supporting materials

### Area Management (20k Areas)
- **List areas** of focus from configuration

All tools include:
- Comprehensive validation and error handling
- Support for todo.txt format with dates, contexts, projects, due/defer dates
- JSON output for programmatic access
- Area validation against configured areas of focus

## Installation

```bash
# Clone the repository
git clone https://github.com/elinsky/gtd-mcp.git
cd gtd-mcp

# Install dependencies
pip install -e ".[dev]"
```

## Configuration

Create a configuration file at `~/.config/gtd-mcp/config.json`:

```json
{
  "gtd_repo_path": "/absolute/path/to/your/gtd-repo",
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

The MCP server integrates with Claude Desktop. Once configured, you can manage your GTD system by asking Claude:

### Project Examples
- "Create a new project titled 'Learn Python' in the Learning area as a standard project in active folder"
- "List all active projects in the Health area"
- "Complete the project 'Learn Python'"
- "Search for projects about machine learning"

### Action Examples
- "Add action 'Buy groceries' to @errands context for project meal-planning"
- "Add 'Wait for package delivery' to @waiting with defer date 2025-11-15"
- "Complete the action on line 7 of contexts/@macbook.md"
- "List all actions for the ml-refresh project"

### Goal Examples
- "List all active goals"
- "Show me goals in the incubator"

### Area Examples
- "List all my areas of focus"

Claude will use the appropriate MCP tools to interact with your GTD system.

## Available Tools

### Project Tools
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

### Action Tools
- `add_action` - Add next action to context file with project validation
- `add_to_waiting` - Add item to @waiting list
- `add_to_deferred` - Add item to @deferred list
- `add_to_incubating` - Add item to @incubating list
- `complete_action` - Complete action by line number
- `list_actions` - List actions with flexible filtering and grouping
- `search_actions` - Search actions by text with filters

### Goal Tools
- `list_goals` - List goals from active and incubator folders

### Area Tools
- `list_areas` - List all configured areas of focus

### Audit Tools
- `audit_projects` - Validate project data quality
- `audit_orphan_projects` - Find projects without actions
- `audit_orphan_actions` - Find actions with invalid projects/contexts
- `audit_action_files` - Validate action file data quality
- `list_projects_needing_review` - Find projects not reviewed recently
- `list_actions_needing_review` - Find action files not reviewed recently

## Project Structure

```
gtd-mcp/
├── src/
│   └── gtd_mcp/
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
