import argparse as ap

from ndmanager.manager import ndm_init


def main():
    parser = ap.ArgumentParser(
        prog="ndm",
        description="Manage your nuclear data libraries",
    )
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize ndmanager")
    init_parser.add_argument(
        "--force", "-f", help="Force re-initialization", action="store_true"
    )
    init_parser.set_defaults(func=ndm_init)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
