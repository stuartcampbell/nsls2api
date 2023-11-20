from nsls2api import __app_name__
from nsls2api.cli import cli


def main():
    cli.app(prog=__app_name__)


if __name__ == "__main__":
    main()
