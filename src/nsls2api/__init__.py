from .version import get_version

# Ensure logging is configured on package import.
from nsls2api.infrastructure import logging

__app_name__ = "nsls2api"
__version__ = get_version()
