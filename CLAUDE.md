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

## CI scheduling and delivery boundary

CI runs on pushes to main, pull requests targeting main, and manual dispatch. Feature branch pushes do not start a second copy of the PR quality gate. Preserve all seven required checks, both Python versions, and every existing quality assertion. The workflow does not currently admit tag pushes; this scheduling correction does not add them.

A successful main push CI run starts the existing CD workflow, which publishes a container image and deploys to homologacao. A CI-only merge still has this effect because CD consumes workflow_run events, not changed paths. Do not merge this scheduling change until an explicit no-publication and no-deployment boundary is approved. Do not manually dispatch CD during validation.

GitHub main currently contains older application source than canonical Gitea main. Do not promote that application delta as part of an unreviewed scheduling-only synchronization. Preserve existing public history and use the reviewed deployment workflow for any later source promotion.

The image gate uses run-specific image and container names. It records and validates the container ID before starting it. Health checks and cleanup use only that ID. Docker assigns a loopback port for the unchanged smoke script. The health assertions, smoke assertions, and all seven quality checks remain mandatory. An absent or invalid creation response never permits cleanup by a guessed name. A failed create response can leave an unidentifiable partial resource; the job must fail and retain evidence rather than remove a foreign container.

Automatic CD publication requires the canonical repository, a successful push-origin CI completion on main, and a valid exact source SHA. PR-origin and manually dispatched CI completions do not authorize automatic publication. Direct manual CD dispatch remains available and uses its own event SHA. Both CD checkouts and the OCI revision use the same qualified SHA, with an explicit checkout identity assertion. This source correction does not authorize any publication or deployment. Temporary workflow suspension still requires separate completion-event and restoration evidence; terminal CI status alone does not acknowledge delivery of its completion notification.

## Provider-specific image build cache

The CI and CD image build steps keep their existing GitHub Actions cache import and export on github.com. On the canonical Gitea server, these two optional inputs are empty. The controlled PR run reached image import but failed while exporting to its unreachable GHA cache endpoint. This source correction removes that observed transport dependency without changing image build, health, smoke, source qualification, or publication assertions. It does not claim that every Gitea cache implementation is incompatible.

An uncached Gitea build can take longer and repeat dependency work. No benchmark or universal speed improvement is claimed. GitHub keeps the exact original cache-from and cache-to values. No local cache service, host networking change, privileged runner, retry, or ignored build failure is introduced. CD remains unexecuted and requires its separate publication and deployment admission.

## Image smoke network namespace

GitHub host runners retain the dynamic loopback-port path. Containerized Gitea jobs instead validate their own current hostname, immutable container ID, and exactly one existing user-defined local bridge. The workflow creates only its run-owned target on that existing network and invokes the unchanged smoke script through the target unique DNS name on port 8000. It does not attach the shared job to a new network, use host networking, inspect environment or credentials, or list other resources. Ambiguous identity, multiple networks, default bridge, unsupported driver, or a changed association causes refusal. Cleanup still uses only the recorded target ID.

This proposal changes transport addressing, not any of the eight smoke assertions. It adds no application dependency, helper image, service, or runner configuration. The Dockerfile and complete smoke script remain unchanged. Only a future admitted native image gate can prove actual network reachability.
