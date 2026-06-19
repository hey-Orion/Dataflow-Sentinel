# DATAFLOW-SENTINEL

Production-Inspired DataOps Pipeline with Freshness Monitoring & CI Alerting

---

## Overview

**DATAFLOW-SENTINEL** > A production-inspired DataOps pipeline that ingests financial market data, validates schema integrity, promotes datasets through a Medallion Architecture, and enforces freshness monitoring via CI-based alerting.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Airflow](https://img.shields.io/badge/Orchestrator-Apache_Airflow-orange)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-success)
![Docker](https://img.shields.io/badge/Containerized-Docker-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Modern pipelines often *run* but silently degrade — schemas drift, data becomes stale, and failures go unnoticed.

This system is designed to:

* Detect failures early
* Prevent silent data corruption
* Enforce schema validation
* Guarantee safe re-runs (idempotency)
* Surface freshness violations via CI alerts

The focus is not just moving data — but protecting its integrity.

---

## Why This Project Matters

Most beginner pipelines demonstrate ingestion.

This project demonstrates:

* Validation-first data promotion
* Deterministic orchestration
* Idempotent re-execution
* Structured logging for traceability
* CI-driven monitoring and alerting
* Environment parity (Local ↔ Docker ↔ CI)
* **Production-grade orchestration with Apache Airflow and Github Actions**

It simulates a production-grade DataOps project in a compact, readable system.

---

## Architecture

### System Architecture

![Pipeline Architecture](docs/images/pipeline-architecture.png)

### Medallion Data Model

![Medallion Architecture](docs/images/medallion-architecture.webp)


The pipeline follows a **Medallion Architecture**:

**Bronze → Silver → Gold**

**Bronze**
Immutable raw market data from Yahoo Finance

**Silver**
Schema-enforced and validated datasets

**Gold**
Analytics-ready aggregates and freshness monitoring artifacts

Execution is orchestrated via `src/pipeline.py` and runs identically across:

* Local environment
* Docker container
* GitHub Actions (scheduled CI runs)
* Apache Airflow, which executes the pipeline as a Directed Acyclic Graph (DAG).

📄 Detailed architecture: `docs/ARCHITECTURE.md`

---

## Reliability Guarantees

The system is intentionally designed to fail loudly.

* Safe re-runs (idempotent writes and controlled promotion)
* Validation gates prevent downstream corruption
* Structured logs for debugging and auditability
* Freshness tracking via `data/gold/freshness.json`
* CI alerts on failure
* Retries and task-level failure alerts

No silent degradation.

---

## Project Structure

![Project Structure](docs/images/project-structure.png)


```
src/        Core pipeline logic (ingestion, validation, storage, metrics)
data/       Bronze / Silver / Gold
tests/      Pytest-based unit & integration tests
config/     Runtime / assets configuration (assets.yaml)
logs/       Structured execution logs
docs/       Architecture & operational runbook
```

The structure enforces strict separation of concerns and stage isolation.

---

## Pipeline Flow

1. **Ingestion**

   * Pulls market data via `yfinance`
   * Writes immutable datasets to Bronze

2. **Validation**

   * Enforces schema with Pydantic
   * Blocks invalid datasets

3. **Promotion**

   * Bronze → Silver → Gold
   * Centralized storage abstraction controls writes

4. **Metrics**

   * Computes aggregates
   * Calculates freshness indicators

5. **Monitoring**

   * Writes `freshness.json`
   * Triggers CI-based email alerts when needed


### Gold Layer Output Example (freshness Artifact)

![Gold Files](docs/images/gold-freshness.png)

---

## How to Run

### Installation

```bash
pip install -r requirements.txt
```

### Local

```bash
make run
```

Uses environment variables defined in `.env`.

---

### Airflow (Orchestration)

This is the recommended way to run the pipeline in a production-like environment.

1. Start airflow with docker
   ```bash
   make up
   ```

2. Access the UI: Open http://localhost:8080 and log in.

3. Trigger the DAG:
   · Via UI: Click the play button next to sentinel_dag.
   · Via CLI:
     ```bash
     make trigger
     ```
4. Monitor execution: Track task statuses, logs, and retries directly in the UI.

![airflow dashboard](docs/images/airflow-ui-dag-list.png)

The DAG appears in the Airflow UI, ready for manual or scheduled triggers.

---

### Docker

```bash
make docker_run
```

![Docker Run](docs/images/docker-container.png)

Runs the pipeline in a containerized environment with local PostgreSQL.

---

### CI (GitHub Actions)

* Scheduled daily runs
* Manual workflow dispatch
* Executes tests before pipeline
* Sends email notifications on success or failure

![GitHub CI](docs/images/github-ci.png)

---

### Configuration

**Assets**

Defined in:

```
config/assets.yaml
```

This decouples runtime symbols (e.g., ticker symbols, file paths) from pipeline logic.

---

### Environment Variables

Multiple environment files are provided for different contexts:

# File Purpose
* .env Base defaults (used in local runs)
* .env.airflow Overrides for Airflow execution
* .env.docker Overrides for Docker‑compose runs

Sensitive values (like SENTRY_DSN) should never be committed; instead, use GitHub Secrets.

---

### Testing

* Built with **pytest**
* Tests mirror the `src/` structure
* Covers ingestion, validation, storage and metrics
* Enforced in CI to prevent regressions

Run tests locally:

```bash
pytest tests/
```

---

### Observability

* Structured logs in `logs/`
* Data freshness tracking in `data/gold/freshness.json`
* CI email alerts on failure
* Airflow UI for real‑time task monitoring and runs

Operational response guide:

📄 `docs/RUNBOOK.md`

---

## Error Monitoring (Sentry)

The pipeline integrates **Sentry** for real-time error tracking and release monitoring.

![Sentry Dashboard](docs/images/sentry-dashboard.png)

While CI alerts notify on workflow failures, Sentry captures:

* Unhandled runtime exceptions
* Full stack traces with context
* Commit-level release tracking

This ensures that failures inside the pipeline are visible even outside CI logs.

### How It Works

* `src/monitoring.py` initializes Sentry at application startup
* DSN is injected via environment variables
* GitHub Actions attaches the current commit SHA as the release version
* Errors are automatically reported on uncaught exceptions

Monitoring is isolated from business logic to maintain clean architecture separation.

### Environment Variables

```
SENTRY_DSN=
ENV=development
SENTRY_RELEASE=

```

Sentry is optional in local development and activates only when `SENTRY_DSN` is provided.

---

## Tech Stack

**Language**

* Python

**Core Libraries**

* pandas
* Pydantic
* yfinance
* SQLAlchemy
* python-dotenv

**Orchestration**

* Apache Airflow
* GitHub Actions

**Infrastructure**

* PostgreSQL (Local & Neon)
* Docker & Docker Compose
* pytest
* Sentry
* Makefile
* Git & GitHub
* yaml 

---

## Design Principles

* Deterministic execution
* Idempotent re-runs
* Validation-first promotion
* Configuration over hard-coded values
* Reproducible environments
* Fail fast, fail visibly

---

## Limitations

* No real-time ingestion
* No dashboard UI
* Limited anomaly detection beyond freshness
* Optimized for clarity and reliability over scale

---

## Future Improvements

* Replace simulated ingestion with additional external APIs
* Add anomaly-based monitoring
* Integrate observability dashboards (Grafana)
* Expand alert channels (Slack / Discord)

---

## Final Note

This project prioritizes reliability, validation, and operational discipline over scale.
It is intentionally designed to reflect how real-world data systems fail —
and how they should be protected.

---

## License

MIT License
