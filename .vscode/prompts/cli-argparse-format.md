# CLI argparse 

## Formatting

When editing CLI options, format each `parser.add_argument` block as:

- First line: `parser.add_argument(`
- Second line: option name, `type`, `default`, `action` (as applicable)
- Last line: `help=...)`

Example:
```python
    parser.add_argument(
        "--task-age", type=parseDuration, default=None,
        help="delete jobs with matching task-id-pattern older than specified time")
```

Keep the block compact and avoid repeating option details elsewhere.

## Sync with CliOptions

Keep command-line options and the `CliOptions` dataclass in sync:
- Every CLI option must map to a `CliOptions` field.
- Every `CliOptions` field should be parsed from CLI options.