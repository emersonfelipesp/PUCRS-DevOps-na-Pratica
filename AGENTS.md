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

Native server telemetry uses FastAPI standard 0.143.0. This educational application has no default collector. Preserve the `create_app(telemetry=...)` factory, existing Prometheus middleware and JSON logging, and the module-level application entry point. Privacy processors must sanitize selected caller SDK providers even when environment endpoints are empty; only automatic proxy-provider replacement depends on export configuration. Keep actual protobuf subprocess probes and the 90% coverage gate, including subprocess coverage. Normal tests disable ambient SDK export.

The factory copies caller telemetry configuration and disables native auto-configuration, tracing, metrics, and logs when `OTEL_SDK_DISABLED=true`. Preserve caller provider identities and ownership. Selected existing providers receive privacy processors independently of signal controls; implicit provider creation requires SDK, signal, auto-configuration, exporter, and endpoint eligibility. The SDK-disabled subprocess probes use active explicit and global caller providers for all three signals and exercise success, validation, errors, and repeated lifespans. Early caller logger exporters require caller-managed ordering; the probes observe disabled-phase early export separately from later privacy export.

The project declares `tool.uv.managed=false` because requirements.txt and requirements-dev.txt own its dependency installation. Create the virtual environment and install those declared requirements before invoking uv-based verification; do not synchronize an empty project dependency list over the tested environment.

Native FastAPI automatic setup is opt-in through `FASTAPI_OTEL_AUTO_CONFIGURE=true`.
An explicit caller `auto_configure` dictionary value takes precedence. Endpoint
values alone do not enable automatic setup. SDK disabling copies and disables
all four native controls while preserving selected caller privacy and ownership.
