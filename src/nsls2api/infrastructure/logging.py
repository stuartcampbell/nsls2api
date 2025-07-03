import logging

import nsls2api
import logfire


class LogfireHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            # Get the logging level name (e.g., 'INFO' becomes 'info')
            level_method = record.levelname.lower()
            # Check if logfire has a method matching the level
            if hasattr(logfire, level_method):
                getattr(logfire, level_method)(msg)
            else:
                # Fallback to a default method or ignore
                logfire.log(msg)
        except Exception:
            self.handleError(record)


# Grab the uvicorn logger so we can generate logs to the application log
logger = logging.getLogger(f"uvicorn.error.{nsls2api.__name__}")

# Create and configure the LogfireHandler
logfire_handler = LogfireHandler()

# Add the handler to the logger
logger.addHandler(logfire_handler)