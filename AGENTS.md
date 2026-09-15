# Repository Agent Guide

Use Python 3.11 or 3.12 for development and validation. Install the exact development dependency set from `requirements-dev.txt` before running repository gates.

Run the complete local gate after dependency or Python changes:

```bash
ruff check .
ruff format --check .
pytest
bandit -r app -ll
pip-audit -r requirements-dev.txt --strict
```

The pytest configuration in `pyproject.toml` enforces at least 90% application coverage. Preserve exact dependency pins so local, CI, and container environments resolve the same versions.

Do not run the deployment or infrastructure apply commands during routine validation. Docker builds and read-only Terraform and Ansible validation are allowed when required by the change.
