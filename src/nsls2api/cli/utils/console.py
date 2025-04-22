from rich.console import Console
from rich.theme import Theme

# Define your custom theme
custom_theme = Theme(
    {
        "success": "bold green",
        "error": "bold red",
        "info": "cyan",
        "warning": "bold yellow",
        "highlight": "bold magenta",
    }
)

# Instantiate the console with the theme
console = Console(theme=custom_theme)


# Utility functions for printing
def success(message: str):
    console.print(message, style="success")


def error(message: str):
    console.print(message, style="error")


def info(message: str):
    console.print(message, style="info")


def warning(message: str):
    console.print(message, style="warning")


def highlight(message: str):
    console.print(message, style="highlight")
