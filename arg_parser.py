import argparse
from pathlib import Path


def _parse_argmunets():
    """Parse comand-line options"""

    parser = argparse.ArgumentParser(
        description="Sort files by extension. Can unpack supported archives.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog = "Usage examples:\n\
            clean.py -v -o /usr/home/root/downloads /usr/home/root/must_be_sorted -s settings.json\n\
        or  clean.py -v -o /usr/home/root/downloads /usr/home/root/must_be_sorted -d images -e jpg bmp jpeg -f move"
    )  # ,exit_on_error=False
    parser.add_argument(
        "directories",
        help="Directories list to process, if not specified used current directory.",
        type = Path,
        action="store",
        nargs='*'
    )
    parser.add_argument(
        "-k", "--keep-empty-dir",
        help="Don't remove empty directories.",
        action="store_true",
        required=False
    )
    parser.add_argument(
        "-u", "--use-original-names",
        help="Don't normalize file and directory(for unpacking archives) names.",
        action="store_true",
        default=False,
        required=False
    )
    parser.add_argument(
        "-o", "--overwrite",
        help="Overwrite existing files and directories.",
        action="store_true",
        default=False,
        required=False
    )
    parser.add_argument(
        "-p", "--process",
        help=".",
        action="store_true",
        default=False,
        required=False
    )

    parser.add_argument(
        "-v", "--verbose",
        help = ("increase output verbosity.\n\
    0 - Only errors printout\n\
    1 - Add warnings\n\
    2 - Add destination directory creation\n\
    3 - Add all filesystem modification\n\
    4 - Add internal script structures"),
        action="count",
        default=0,
        required=False
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s", "--settings",
        help="Specify path to settings(JSON) file. Ex: settings.json",
        type = Path,
        metavar="settings.json",
        default="settings.json",
        required=False
    )
    group.add_argument(
        "-d", "--destination",
        help="Destination directory.",
        type = Path,
        metavar="destination",
        action="store",
        default=None,
        required=False
    )
    parser.add_argument(
        "-e", "--extensions",
        help="File's extensions. Ex: 'jpg jpeg png bmp'",
        metavar="extensions",
        action="store",
        default="*",
        required=False,
        nargs='*'
    )
    parser.add_argument(
        "-f", "--functions",
        help = "Functions' list(order sensitive).\n\
    A list of next functions:\n\
    copy, move, unpack, delete(check if archive already unpacked), remove.\n\
    Ex: 'unpack move' - will unpack archive file to destination directory\n\
    and move it to same path.",
        metavar="functions",
        action="store",
        default="move",
        required=False,
        nargs='*'
    )
    return parser.parse_args()