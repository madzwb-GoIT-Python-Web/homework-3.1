"""
"""

import json
import os
import sys
import time

from pathlib import Path


import logger.config as config
import logger.logger as Logging

from logger.logger import logger,formatter_result

config.SCRIPT = __file__
# print(__name__)
if      __name__ == "__main__"\
    or  __name__ == "filesorter.sorter"\
    :
    import filesorter._argparser as _argparser
    # Override default config
    config.LOG_FILE_TRUNCATE = True
    Logging.init()
    Logging.truncate()

if config.PROFILING:
    import cProfile

from filesorter._executors import registry
from filesorter.filters import Filter, Filters
from filesorter.task import Task



def sort_targets(path_to_target, executor, settings):
    # Make path list
    if isinstance(path_to_target, str):
        pathes = path_to_target.split()
    elif isinstance(path_to_target, list):
        pathes = path_to_target
    elif isinstance(path_to_target, Path):
        pathes = list(path_to_target.name)
    else:
        raise ValueError(f"{path_to_target} value error.")
    
    # Remove duplicates
    pathes = list(dict.fromkeys(pathes))

    for path in pathes:
        filters = Filters(path,_argparser.args.keep_empty_dir)
        for name, setting in settings.items():
            filters +=  Filter(
                            filters,
                            name,
                            setting["extensions"],
                            setting["functions"],
                            setting["use"] if "use" in setting else ""
                        )
        task = Task(path, filters, executor)
        executor.submit(task)
    return

def load_settings(path = None):
    if path is not None and not os.path.exists(path):
        raise LookupError(path, "not exists")
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "settings.json")
    with open(path, 'r') as settings:
        dir2ext = json.load(settings)
    return dir2ext

def main():
    
    profile = None
    if config.PROFILING:
        profile = cProfile.Profile()
        profile.enable()
        start = time.time()

    args = _argparser.parse_args()
    if args.settings:
        settings = load_settings(args.settings)
    else:
        settings = {
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

    executor = registry[_argparser.args.executor]()

    sort_targets(args.directories, executor, settings)
    executor.join()
    executor.shutdown(True)

    for handler in logger.handlers:
        handler.setFormatter(formatter_result)
    # time.sleep(3)
    logger.info("<Result")
    try:
        while result := executor.results.get_nowait():
            logger.info("\t" + str(result))
    except Exception as e:
        pass
    logger.info(">")

    print()

    if config.PROFILING and profile is not None:
        profile.disable()
        profile.print_stats(sort="cumtime")


if __name__ == "__main__":
    main()
