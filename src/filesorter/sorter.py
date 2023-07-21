"""
"""

from __future__ import annotations

import sys
import time

from pathlib import Path


import filesorter.config as config

from filesorter.logger import init, logger, formatter_result as formatter
if "__main__" == __name__:
    import filesorter._argparser as _argparser

    config.SCRIPT = __file__
    init()

if config.PROFILING:
    import cProfile

from filesorter._executors import registry
from filesorter.filters import Filter, Filters
from filesorter.task import Task



def sort_targets(path_to_target, executor):#, tasks: multiprocessing.JoinableQueue[actions.IAction]|queue.Queue[actions.IAction], results, create):
    # Make path list
    # tasks      = tasks     if tasks    else executor.tasks
    # results    = results   if results  else executor.results
    # create     = create    if create   else executor.create

    if isinstance(path_to_target, str):
        pathes = path_to_target.split()
    elif isinstance(path_to_target, list):
        pathes = path_to_target
    else:
        raise ValueError(f"{path_to_target} value error.")
    
    # Remove duplicates
    pathes = list(dict.fromkeys(pathes))

    for path in pathes:
        filters = Filters(path)
        filters += Filter(Path("archives"),  ["zip", "tar", "tgz", "gz", "7zip", "7z", "iso", "rar"] ,                           ["unpack", "copy"],    "processes")
        filters += Filter(Path("audios"),    ["wav", "mp3", "ogg", "amr"],                                                       ["copy"])
        filters += Filter(Path("images"),    ["jpeg", "png", "jpg", "svg"],                                                      ["copy"])
        filters += Filter(Path("videos"),    ["avi", "mp4", "mov", "mkv"],                                                       ["copy"])
        filters += Filter(Path("documents"), ["doc", "docx", "txt", "pdf", "xls", "xlsx", "ppt", "pptx", "rtf", "xml", "ini"],   ["copy"])
        filters += Filter(Path("softwares"), ["exe", "msi", "bat", "dll", "apk"],                                                ["copy"])
        filters += Filter(Path("other"),     [""],                                                                               ["copy"])
        
        task = Task(path, filters, executor)#, tasks, results, create)
        executor.submit(task)#, executor.tasks, executor.results, executor.create)
    # print(f"Results size: {executor.results.qsize()}.")
    return

def main():
    _argparser.parse_args()
    profile = None
    if config.PROFILING:
        profile = cProfile.Profile()
        profile.enable()
        start = time.time()
    
    executor = registry[_argparser.args.executor]()

    sort_targets("D:/edu/test", executor)
    executor.join()
    executor.shutdown(True)

    for handler in logger.handlers:
        handler.setFormatter(formatter)
    logger.info("<Result")
    try:
        while result := executor.results.get_nowait():
            logger.info("\t" + result)
    except Exception as e:
        pass
    logger.info(">")

    print()

    if config.PROFILING and profile is not None:
        profile.disable()
        profile.print_stats(sort="cumtime")


if __name__ == "__main__":
    main()
    
    #     # multiprocessing.freeze_support()
    #     # executor = executors.registry["processes"]

    #     # manager = executors.ProcessesManager()
    #     # proxy = None
    #     # proxy = executors.ProcessesExecutorProxy
    #     # # proxy = executors.Proxy(executors.ProcessesExecutor)
    #     # # manager.register("Queue", executors.Queue)
    #     # manager.register("ProcessesExecutor", executors.ProcessesExecutor, proxy)
    #     # manager.start()

    #     # executor.results = executor.manager.Queue()
    #     # executor.workers = executor.manager.list()
    #     # executor.futures = executor.manager.list()

    # # executor = executors.registry["mainthread"]()
    # # executor = executors.registry["thread"]()
    # # executor = executors.registry["threads"]()
    # # executor = executors.registry["threadpool"]()
    # # executor = executors.registry["processpool"]()
    # executor = executors.registry["processes"]()
    # # executor.init(4)
    # # tasks       = executor.tasks
    # # results     = executor.results
    # # create      = executor.create


    #     # current = threading.current_thread()
    #     # main = threading.main_thread()
    #     # executor = manager.ProcessesExecutor()
    #     # executor = executors.ProcessesExecutor()

    #     # tasks = manager.Queue()
    #     # results = manager.Queue()
    #     # create = manager.Event()
    #     # executor.tasks = tasks
    #     # executor.results = results
    #     # executor.create = create
    #     # executor.set_tasks(tasks)
    #     # executor.set_results(results)
        
    #     # print(executor.tasks())
    # # sort_targets(executor, "D:/work")
    # sort_targets("D:/edu/test", executor)#, tasks, results, create)
    # # manager.join()
    # executor.join()
    # executor.shutdown(True)

    # for handler in logger.handlers:
    #     handler.setFormatter(formatter)
    # logger.info("<Result")
    # try:
    #     while result := executor.results.get_nowait():
    #         logger.info("\t" + result)
    # except Exception as e:
    #     pass
    # logger.info(">")

    # print()

    # if config.PROFILING:
    #     profile.disable()
    #     profile.print_stats(sort="cumtime")
