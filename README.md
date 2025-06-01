# AI Tools Suite

A modular toolkit for AI-powered content generation and prompt engineering, built with Streamlit using Gemini, 

## Overview

This project provides a suite of specialized tools for content creation and development assistance, featuring a unified client management system with Notion integration and structured logging throughout.

## Architecture

```
.
├── app.py                    # Main Streamlit application
├── frameworks/               # Core infrastructure
│   ├── database_manager.py   # Notion API integration
│   ├── unified_client_manager.py
│   ├── universal_framework.py
│   ├── refiner_framework.py
│   ├── logging_manager.py
│   └── shared_utils.py
├── tools/                    # Tool implementations
│   ├── social_copy_tool.py
│   ├── prompt_refiner.py
│   ├── coder_helper.py
│   └── context_gatherer.py
└── HOUSEKEEPING/            # Documentation and utilities
    ├── *.md                 # Project documentation
    ├── *.py                 # Utility scripts
    └── DOCS/                # Change logs
```

## Tools

### Copy Generator
Platform-specific content generation with customizable tone and style.
- Supports: Facebook, LinkedIn, TikTok, YouTube
- Features: Voice consistency, tone adjustment, platform optimization
- Special mode: Legacy Advisors for specialized financial content

### Prompt Refiner
Iterative prompt improvement through AI-assisted refinement.
- Real-time suggestions
- Version history with undo capability
- Meta-prompt optimization

### Coder Helper
Technical prompt optimization for development tasks.
- Code-focused refinements
- Technical language optimization

## Installation

```bash
# Clone repository
git clone <repository-url>
cd jons-ai-tools

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your API keys
```

## Configuration

Required API keys in `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-openai-key"
GOOGLE_API_KEY = "your-gemini-key"
NOTION_API_KEY = "your-notion-key"
NOTION_DATABASE_ID = "your-database-id"
```

## Usage

### Command Line
```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

### Desktop Icon (macOS)
Create a desktop icon for one-click access:

```bash
python3 create_desktop_icon.py
```

This creates `AI Tools.app` that you can drag to your Desktop. Double-clicking the icon will:
- Start the application automatically
- Open your browser to the correct URL
- Handle all setup (virtual environment, server startup)

See [DESKTOP_ICON.md](DESKTOP_ICON.md) for detailed setup instructions.

## Development

### Project Structure

- **frameworks/**: Core utilities and integrations
  - Retry logic with exponential backoff
  - Structured logging
  - Unified client management
  - Database operations

- **tools/**: Individual tool implementations
  - Each tool follows a consistent interface
  - Shared utilities in `context_gatherer.py`

- **HOUSEKEEPING/**: Project management
  - Custom commands via CLAUDE.md
  - Documentation and utility scripts

### Custom Commands

When using Claude Code, these commands are available:
- `wrap it up` - Session wrap-up
- `update context` - Update CONTEXT.md
- `status check` - Project status report
- `document this` - Generate documentation

### Testing

```bash
cd xfindandfixshit
pytest tests/ -v
```

## API Integration

### Notion Database
The system integrates with Notion for client data persistence:
- Client profiles
- Tool completion tracking
- Content samples
- Voice guidelines

### AI Models
- **Google Gemini 2.0 Flash**: Primary content generation
- **OpenAI GPT-4**: Fallback and specialized tasks

## Logging

Structured logging is implemented throughout:
```python
from frameworks.logging_manager import get_logger

logger = get_logger(__name__)
logger.log_operation_start("operation_name", **context)
logger.log_operation_success("operation_name", **results)
logger.log_operation_failure("operation_name", error_msg, **context)
```

## Contributing

1. Follow existing patterns in `shared_utils.py`
2. Use structured logging for all operations
3. Implement retry logic for external API calls
4. Add tests in `xfindandfixshit/tests/`

## License

[License information pending]