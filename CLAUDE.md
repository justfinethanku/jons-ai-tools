## Response Guidelines
- Keep all responses concise - default to bullet points
- always think about what you are going to do before doing it.
- always make a plan first before doing things
- Only modify code that needs changing
- Skip explanations unless I ask "why" or "explain"
- When planning: think internally, output minimal summary
- Never modify: secrets.toml, .env, .streamlit/secrets.toml

## Custom Commands
When I say these phrases, execute the corresponding scripts:
- "wrap it up" or "wrap session" → run `python HOUSEKEEPING/wrap_up.py`
- "update context" → run `python HOUSEKEEPING/update_context.py`
- "status check" or "what's the status" → run `python HOUSEKEEPING/project_status.py`
- "document this" → run `python HOUSEKEEPING/document_changes.py`