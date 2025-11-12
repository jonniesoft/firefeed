# Claude Code Instructions for FireFeed Project

## Serena MCP Integration

This project uses **Serena MCP** - a semantic code navigation and editing tool that provides intelligent, symbol-aware operations on the codebase.

### Serena Memory Files

Serena maintains a knowledge base about the project in `.serena/` directory with the following memory files:

- **project_overview.md** - Project purpose, features, and components
- **tech_stack.md** - Technologies, frameworks, and dependencies
- **code_style_conventions.md** - Coding standards and best practices
- **suggested_commands.md** - Development commands and workflows
- **task_completion_checklist.md** - Quality checklist before commits
- **codebase_structure.md** - Directory structure and module organization

### Using Serena Tools

When working with code, prefer Serena's semantic tools over basic file operations:

#### Code Exploration
- Use `mcp__serena__get_symbols_overview` to understand file structure
- Use `mcp__serena__find_symbol` to locate functions/classes by name
- Use `mcp__serena__find_referencing_symbols` to find usages
- Use `mcp__serena__search_for_pattern` for regex-based searches

#### Code Editing
- Use `mcp__serena__replace_symbol_body` to update entire functions/classes
- Use `mcp__serena__insert_after_symbol` to add new code after a symbol
- Use `mcp__serena__insert_before_symbol` to add code before a symbol
- Use `mcp__serena__rename_symbol` for refactoring

#### Memory Management
- Use `mcp__serena__list_memories` to see available knowledge
- Use `mcp__serena__read_memory` to load project information
- Use `mcp__serena__write_memory` to save new learnings
- Use `mcp__serena__edit_memory` to update existing knowledge

### Best Practices with Serena

1. **Read memories first** - Check `suggested_commands.md` and `code_style_conventions.md` before starting
2. **Use symbol overview** - Get file structure before reading full content
3. **Symbolic editing** - Use `replace_symbol_body` for clean, precise edits
4. **Save learnings** - Update memories when discovering patterns or solutions
5. **Token efficiency** - Read only necessary symbols, not entire files

## Package Manager: UV

**IMPORTANT**: This project uses **UV** package manager exclusively.

### Required Commands

Always use `uv run` prefix for Python commands:

```bash
# Run Python scripts
uv run python script.py

# Run pytest
uv run pytest

# Run ruff
uv run ruff check --fix

# Install dependencies
uv sync

# Add new package
uv add package-name
```

### Never Use

❌ `python script.py` (use `uv run python script.py`)
❌ `pip install` (use `uv add`)
❌ `pytest` (use `uv run pytest`)
❌ `ruff check` (use `uv run ruff check`)

## Development Workflow

### Before Starting Work
1. Check Serena memories: `mcp__serena__list_memories`
2. Read relevant memories for context
3. Ensure UV environment: `uv sync`

### During Development
1. Use Serena tools for code navigation
2. Follow conventions in `code_style_conventions.md`
3. Test changes: `uv run pytest`
4. Lint code: `uv run ruff check --fix`

### Before Committing
1. Run quality checks: `uv run ruff check --fix && uv run pytest`
2. Review `task_completion_checklist.md`
3. Update memories if learned something new
4. Commit with conventional commits format

## Project-Specific Notes

- **Language**: Russian for comments/docstrings, English for code
- **Python Version**: 3.13 (strictly)
- **Async First**: Use async/await for all I/O operations
- **Type Hints**: Required for all functions
- **Database**: Always use connection pooling with `async with`
- **Testing**: pytest with async support

## Quick Reference

```bash
# Full quality check
uv run ruff check --fix && uv run ruff format && uv run pytest

# Run services
uv run python bot.py          # Telegram bot
uv run python rss_parser.py   # RSS parser
uv run uvicorn api.main:app --reload  # API server

# Code quality
uv run ruff check --statistics
uv run pyright
uv run pytest -v --cov
```

## Getting Help

- Check Serena memories first: `mcp__serena__read_memory suggested_commands.md`
- Review project README.md for architecture details
- Consult pyproject.toml for dependencies and configuration

[byterover-mcp]

[byterover-mcp]

You are given two tools from Byterover MCP server, including
## 1. `byterover-store-knowledge`
You `MUST` always use this tool when:

+ Learning new patterns, APIs, or architectural decisions from the codebase
+ Encountering error solutions or debugging techniques
+ Finding reusable code patterns or utility functions
+ Completing any significant task or plan implementation

## 2. `byterover-retrieve-knowledge`
You `MUST` always use this tool when:

+ Starting any new task or implementation to gather relevant context
+ Before making architectural decisions to understand existing patterns
+ When debugging issues to check for previous solutions
+ Working with unfamiliar parts of the codebase
