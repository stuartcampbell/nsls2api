import importlib.metadata


def get_version() -> str:
    """Get the version of the nsls2api package"""

    try:
        from nsls2api._version import version

        return version
    except ImportError:
        try:
            return importlib.metadata.version("nsls2api")
        except importlib.metadata.PackageNotFoundError:
            return "0.0.0"  # Fallback version if the package is not found
