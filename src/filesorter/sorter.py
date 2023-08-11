"""
"""
import functools
import json
import os
import queue
import sys
import time

from pathlib import Path

import logger.config as config
import logger.logger as Logging

from logger.logger import logger, formatter, formatter_result

# print(__name__)
if      __name__ == "__main__"          \
    or  __name__ == "filesorter.sorter" \
    :
    import filesorter._argparser as argparser
    # Override default config
    if not config.SCRIPT:
        config.SCRIPT = __file__
        config.LOG_FILE_TRUNCATE = True
        config.PROFILING = True
        Logging.truncate()
        Logging.init()

if config.PROFILING:
    import cProfile

from filesorter._executors import registry, TASK_SENTINEL, RESULT_SENTINEL
from filesorter.filters import Filter, Filters
from filesorter.task import Task

SETTINGS_FILENAME = "settings.json"

# This file contains a filter's settings.
# Keyword "archive" will be used as subdirectory name for all files
# specified by "extensions" and for all files will be applied all of functions in
# "functions". That's all will be executed in executor - specified by "use",
# or in "mainthread" by default.
SETTINGS =  {
                "archives"  :   {
                    "extensions"    :   ["zip", "tar", "tgz", "gz", "7zip", "7z", "iso", "rar"],
                    "functions"     :   ["unpack", "copy"],
                    "use"           :   "processes"
                },

                "video"     :   {
                    "extensions"    :   ["avi", "mp4", "mov", "mkv"],
                    "functions"     :   ["copy"]
                },
                "audio"     :   {
                    "extensions"    :   ["wav", "mp3", "ogg", "amr"],
                    "functions"     :   ["copy"]
                },
                "documents" :   {
                    "extensions"    :   ["doc", "docx", "txt", "pdf", "xls", "xlsx", "ppt", "pptx", "rtf", "xml", "ini"],
                    "functions"     :   ["copy"]
                },
                "images"    :   {
                    "extensions"    :   ["jpeg", "png", "jpg", "svg"],
                    "functions"     :   ["copy"]
                },
                "software"  :   {
                    "extensions"    :   ["exe", "msi", "bat", "dll"],
                    "functions"     :   ["copy"]
                },
                "other"     :   {
                    "extensions"    :   [],
                    "functions"     :   ["copy"]
                }
            }

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


def sort_targets(args, executor, settings):
    # Make path list
    if isinstance(args.directories, str):
        pathes = args.directories.split()
    elif isinstance(args.directories, list):
        pathes = args.directories
    elif isinstance(args.directories, Path):
        pathes = list(args.directories.name)
    else:
        raise ValueError(f"{args.directories} value error.")
    
    # Remove duplicates
    pathes = list(dict.fromkeys(pathes))

    tasks = []
    for path in pathes:
        filters =   Filters(
                        args.destination,#path,
                        None,
                        args.keep_empty_dir,
                        args.normalize,
                        args.overwrite,
                        not args.dont_use_names,
                    )
        for name, setting in settings.items():
            filters +=  Filter(
                            filters,
                            name,#args.destination / name,
                            setting["extensions"],
                            setting["functions"],
                            setting["use"] if "use" in setting else ""
                        )
        if args.name:
            filters +=   Filter(
                            filters,#path,
                            args.name,
                            args.extensions,
                            args.functions,
                            args.ext_executor,
                        )
        task = Task(path, filters, executor)
        tasks.append(task)

    for task in tasks:
        executor.submit(task)
    # else:
    #     executor.submit(TASK_SENTINEL)
    return

def load_settings(path : Path):
    # Full path specified
    if path is not None and os.path.dirname(path) and not path.exists():
        raise LookupError(path, "not exists")
    # File name specified only, try script's directory
    elif path is not None and not os.path.dirname(path):
        path = Path(os.path.dirname(__file__)) / path
    # Not specified, try hardcoded
    elif path is None:
        path = Path(os.path.dirname(__file__)) / SETTINGS_FILENAME
    
    settings = None
    with open(path, 'r') as fd:
        settings = json.load(fd)
        if settings:
            logger.info(f"Loaded settings from {path}.")
            logger.debug(f"Settings: {settings}.")
        else:
            logger.warning(f"Settings' file {path} is empty.")
    return settings

def sort(args):
    profile = None
    if config.PROFILING:
        # profile = cProfile.Profile()
        # profile.enable()
        start = time.perf_counter()

    if args.settings:
        settings = load_settings(args.settings)
    else:
        settings = SETTINGS

    executor = registry[args.executor]()
    executor.start()

    sort_targets(args, executor, settings)
    executor.submit(TASK_SENTINEL)
    executor.join()
    executor.shutdown(True)

    for handler in logger.handlers:
        handler.setFormatter(formatter_result)
    # time.sleep(3)
    logger.info("<Result")
    results = executor.get_results(False)
    for result in executor.lresults:
        logger.info("\t" + str(result))
    # try:
    #     while result := executor.get_results(False):
    #         logger.info("\t" + str(result))
    # except Exception as e:
    #     pass
    logger.info(">")

    for handler in logger.handlers:
        handler.setFormatter(formatter)
    # print()

    if config.PROFILING:
        if  profile is not None:
            profile.disable()
            profile.print_stats(sort="cumtime")
        end = time.perf_counter()
        delta = end - start
        logger.info(f"Total execution time: {delta}")

if __name__ == "__main__":
    
    def main():
        args = argparser.parse(*sys.argv[1:])
        logger.setLevel(args.log_level)
        logger.info(f"Set verbose to - {args.verbose}.")
        logger.info(f"Got args: {args}.")
        sort(args)


    main()
