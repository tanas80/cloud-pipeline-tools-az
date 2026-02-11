# AI Instructions

## Language

All project documentation, specifications, and AI instructions must be maintained exclusively in English.

## Documentation style

Project documentation must be very compact:
- Do NOT duplicate command descriptions
- Do NOT duplicate command-line option descriptions  
- Do NOT duplicate data types
- Do NOT duplicate function call examples

These details are already in the code (argparse definitions, type hints, docstrings). Documentation should focus on high-level concepts, architecture, and usage patterns only.

## Code structure

- Core logic uses dependency injection (functions accept data providers as arguments)
- Tests inject mock/stub implementations instead of calling Azure CLI
- All Azure CLI interactions go through `az_cli.py` module
- JSON payloads are modeled with Pydantic `BaseModel` classes; prefer direct attribute access on models
- Filter criteria combine via OR logic when multiple are provided
- Age calculations use `lastModified` field from job data

## Dependency hygiene

- Keep dependencies in `requirements.txt` and `setup.py` in sync.

## CLI options formatting

When working on command-line options, follow the formatting rules in `cli-argparse-format.md`.
