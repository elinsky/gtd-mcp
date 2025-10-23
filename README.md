# GTD MCP Server

MCP (Model Context Protocol) server for creating GTD projects with proper structure, validation, and templates.

## Features

- Create GTD projects via Claude Desktop
- YAML frontmatter generation with conditional fields
- Three project templates: standard, coordination, habit
- Area validation against configured areas of focus
- Duplicate detection across all project folders
- Kebab-case filename conversion

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

The MCP server integrates with Claude Desktop. Once configured, you can create projects by asking Claude:

> "Create a new project titled 'Learn Python' in the Learning area as a standard project in active folder"

Claude will use the `create_project` tool to generate the project file with proper structure.

## Project Structure

```
gtd-mcp/
├── src/
│   └── gtd_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server
│       ├── config.py          # Configuration manager
│       ├── validator.py       # Validation logic
│       ├── templates.py       # Template engine
│       └── creator.py         # Project creator
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   └── features/
│       └── project-creation/
├── pyproject.toml
└── README.md
```

## License

MIT
