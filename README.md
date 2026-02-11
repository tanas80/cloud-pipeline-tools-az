# Azure Batch Cleanup

Small Python CLI tool to delete Azure Batch jobs that are not completed and match user-defined filters. The core logic is implemented as pure functions with injected data providers, so tests can substitute Azure CLI calls.

## Prerequisites

- Azure CLI installed and authenticated for Batch operations.
- Batch account configuration provided via Azure CLI defaults or the `AZURE_BATCH_*` environment variables.

## Quick start

1) Copy `.env.example` to `.env` and fill the Azure Batch variables.
2) Install dev dependencies and run tests with pytest.
3) Run the CLI and choose filters.

## Notes

- Filters combine with OR logic.
- Age is calculated using `lastModified`.
- Task-based filters require a task age and only match when all tasks satisfy the pattern/workdir checks.
- `--dry-run` lists candidates and exits.
- The CLI prompts before deletion unless `--yes` is provided.
- JSON payloads are parsed into Pydantic `BaseModel` types; use direct attribute access on models.

## Tests

Tests live in `tests/` and are designed to run without Azure.
