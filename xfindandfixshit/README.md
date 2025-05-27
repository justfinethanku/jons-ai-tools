# xfindandfixshit Package

This package contains all testing, debugging, and development utilities for the AI Tools project.

## Structure

```
xfindandfixshit/
├── tests/                 # All production tests
│   ├── unit/             # Unit tests for individual modules
│   ├── integration/      # Integration tests across modules  
│   └── functional/       # End-to-end functional tests
├── debug/                # Debug scripts and utilities
│   ├── general/          # General debugging tools
│   ├── frameworks/       # Framework-specific debug scripts
│   ├── tools/           # Tool-specific debug scripts
├── fixtures/            # Test fixtures and mock data
├── legacy/             # Archived/obsolete tests and scripts
└── pytest.ini         # Pytest configuration

```

## Usage

### Running Tests
```bash
# From project root
cd xfindandfixshit
pytest tests/

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/functional/
```

### Debug Scripts
```bash
# Run debug scripts from project root
python -m xfindandfixshit.debug.general.test_token_direct
```

## Guidelines

- **ALL** new tests go in `tests/` subdirectories
- **ALL** debug scripts go in `debug/` subdirectories organized by component
- Use `fixtures/` for shared test data and mocks
- Archive obsolete code in `legacy/` instead of deleting
- Update this README when adding new debug script categories

## Test Categories

- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test interaction between multiple components
- **Functional Tests**: Test complete workflows end-to-end