from dotenv import load_dotenv
import os
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

load_dotenv()


def setup_sentry_and_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    init_sentry()
    logging.info("Logging and Sentry set up")


""" Sentry setup to monitor errors in the live app. https://donnamagi.sentry.io/ """


def init_sentry():
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

    functions_to_trace = [
        {
            "qualified_name": "app.services.background_tasks.process_articles.process_articles"
        },
        {
            "qualified_name": "app.services.background_tasks.store_all_recents.update_scores"
        },
    ]

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        enable_tracing=True,
        functions_to_trace=functions_to_trace,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        integrations=[sentry_logging],
    )
