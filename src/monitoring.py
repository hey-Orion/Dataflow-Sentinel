import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def init_monitoring() -> None:
    dsn = os.getenv("SENTRY_DSN")

    # Skip Sentry during tests or if no DSN is set
    if not dsn or os.getenv("ENV") == "TESTING":
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("ENV", "development"),
        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            )
        ],
        traces_sample_rate=1.0,
        attach_stacktrace=True,
    )


def set_run_context(run_id: str) -> None:
    sentry_sdk.set_tag("run_id", run_id)
    sentry_sdk.add_breadcrumb(
        category="pipeline",
        message=f"Starting pipeline execution for run_id: {run_id}",
        level="info",
    )