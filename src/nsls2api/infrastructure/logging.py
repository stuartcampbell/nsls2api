import logging
import nsls2api

# Grab the uvicorn logger so we can generate logs to the application log
logger = logging.getLogger(f"uvicorn.error.{nsls2api.__name__}")


