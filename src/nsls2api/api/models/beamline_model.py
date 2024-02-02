# This is for response models relating to the beamline api endpoints.

from enum import Enum


class AssetDirectoryGranularity(Enum):
    """
    Represents the granularity options for asset directory YYYY/MM/DD/HH tree structure.
    The value specifies the most granular level to create directories for.
    """

    year = "year"
    month = "month"
    day = "day"
    hour = "hour"
