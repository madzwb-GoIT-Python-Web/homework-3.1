import argparse
import logging

from pathlib import Path

_parser = None
_args    = None

def get_parser():
    # global _args
    # if _args is not None:
    #     return _args
    """Parse comand-line options"""

    parser = argparse.ArgumentParser(
        prog="sorter",
        description="Sort files by extension. \n\
        Can unpack supported by 'shutil' archives.",
        # formatter_class=argparse.RawTextHelpFormatter
        formatter_class=lambda prog: argparse.HelpFormatter("sorter",width=80),
        epilog = "Usage examples:\n\
    sorter.py -v -o ~/downloads ~/must_be_sorted -s settings.json           \n\
or  sorter.py -v -o ~/downloads ~/must_be_sorted -n images -e jpg bmp -f move"
    )  # ,exit_on_error=False
    parser.add_argument(
        "directories",
        help        = "Directories list to process,\n\
        if not specified will used current directory.",
        type        = Path,
        action      = "store",
        default     = Path().cwd(),
        # required    = False,
        nargs       = '*'
    )
    parser.add_argument(
        "-k", "--keep-empty-dir",
        help        = "Don't remove empty directories.",
        action      = "store_true",
        default     = False,
        required    = False
    )
    parser.add_argument(
        "-norm", "--normalize",
        help        = "Normalize file and directory\n\
        (for unpacking archives) names.",
        action      = "store_true",
        default     = False,
        required    = False
    )
    parser.add_argument(
        "-o", "--overwrite",
        help        = "Overwrite existing files and directories.",
        action      = "store_true",
        default     = False,
        required    = False
    )
    parser.add_argument(
        "-x", "--executor",
        type        = str.lower,
        help        = "Main executor.",
        choices     =   [
                            "mainthread",
                            "thread",
                            "process",
                            "threads",
                            "processes",
                            "threadpool",
                            "processpool"
                        ],
        metavar     = "executor",
        action      = "store",
        default     = "mainthread",
        required    = False,
        nargs='?'
    )
    parser.add_argument(
        "-v", "--verbose",
        type        = str.upper,
    #     help        = ("increase output verbosity.\n\
    # 0 - Only errors printout\n\
    # 1 - Add warnings\n\
    # 2 - Add destination directory creation\n\
    # 3 - Add all filesystem modification\n\
    # 4 - Add internal script structures"),
        choices     =   [
                            "CRITICAL",
                            "ERROR",
                            "WARNING",
                            "INFO",
                            "DEBUG",
                            "NOTSET"
                        ],
        # action="count",
        metavar     = "level",
        action      = "store",
        required    = False,
        default     = "notset",
        nargs       = '?'
    )
    parser.add_argument(
        "-d", "--destination",
        help        = "Destination directory.",
        type        = Path,
        metavar     = "destination",
        action      = "store",
        default     = Path().cwd(),
        # default     = None,
        required    = False
    )
    parser.add_argument(
        "--dont-use-names",
        help        = "Don't use filter name as destination subdirectory.\n\
        If not specified, but destination directory matches source,\n\
        will be set to 'True'.",
        # type        = bool,
        # metavar     = "dont_use_names",
        action      = "store_True",
        default     = False,
        # default     = None,
        required    = False
    )

    # group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "-s", "--settings",
        help        = "Specify path to settings(JSON) file.\n\
        If file name only specified, will search in \n\
        script's directory.",
        type        = Path,
        action      = "store",
        metavar     = "settings",
        default     = "settings.json",
        required    = False
    )
    filter_group = parser.add_argument_group(
        "Filter",
        "If filter with name are present in settings.json,\n\
        it will be overwrited."
    )
    filter_group.add_argument(
        "-n", "--name",
        help        = "Filter name. Will be used as subdirectory,\n\
        if --dont-use-names is specified and destiantion\n\
        directory not in source directory list.",
        type        = str,
        metavar     = "name",
        action      = "store",
        default     = "",#Path().cwd(),
        required    = False
    )
    filter_group.add_argument(
        "-e", "--extensions",
        help        = "File's extensions. Ex: 'jpg jpeg png bmp'.",
        metavar     = "extensions",
        action      = "store",
        default     = "*",
        required    = False,
        nargs       = '*'
    )
    filter_group.add_argument(
        "-f", "--functions",
        type        = str.lower,
        help        = "Functions' list(order sensitive).\n\
    A list of next functions:\n\
    copy, move, unpack, remove,\n\
    removechecked(check if archive already unpacked).\n\
    Ex: 'unpack move' - will unpack archive file\n\
    to destination directory and move it to the same.",
        metavar     = "functions",
        action      = "store",
        default     = "move",
        required    = False,
        choices     =    [
                            "copy",
                            "move",
                            "unpack",
                            "remove",
                            "removechecked"
                        ],
        nargs       = '*'
    )
    # executor_group = filter_group.add_argument_group("Executor")
    filter_group.add_argument(
        "-u", "--use",
        type        = str.lower,
        help        = "Individual executor.",
        choices     =   [
                            "mainthread",
                            "thread",
                            "process",
                            "threads",
                            "processes",
                            "threadpool",
                            "processpool"
                        ],
        metavar     = "use",
        dest        = "use",
        action      = "store",
        default     = "mainthread",
        required    = False,
        nargs       = '?'
    )
    filter_group.add_argument(
        "-m", "--max-workers",
        type        =  int,
        help        = "Max number of workers.",
        metavar     = "max_workers",
        dest        = "max_workers",
        action      = "store",
        default     = 0,
        # required    = False,
        nargs       = '?'
    )

    return parser

def get_args(*args):
    global _args, _parser
    if _parser is None:
        _parser = get_parser()
    __args = _parser.parse_args(args)
    # [source for source in args.directories if source == args.destination]
    if __args.dont_use_names:
        __args.dont_use_names = __args.destination not in __args.directories    \
                                    if  isinstance(__args.directories, list)    \
                                    else                                        \
                                __args.destination != __args.directories        \
                                    if  isinstance(__args.directories, Path)    \
                                    else                                        \
                                False#__args.dont_use_names
    
    __args.log_level = logging._nameToLevel[__args.verbose]
    return __args

def parse(*args):
    _args = get_args(*args)
    return _args
