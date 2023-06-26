"""
    TODO: logging

    USAGE:
        class Filter(
                destiantion:    -   string,
                extensions:     -   "space separated string" | [list of strings],
                functions:      -   "space separated string" | [list of strings]
            )
        class Task(
            path:   - Path to sort
        )
        For example see function main()

        All excpetions store in Task's deque attribute - _status
        In threaded mode no exception raised, except in construction methods
"""

from __future__ import annotations

import cProfile
import multiprocessing
# import os
import sys
import threading
import time

from pathlib import Path
# from concurrent.futures import Future
# from collections import UserDict
# from copy import deepcopy

import actions
if "__main__" == __name__:
    import arg_parser
import executors

from logger import logger
from filters import Filter, Filters
# from typing import Any, Callable, cast, Type


EXECUTORS: dict[str, executors.Executor] = {}

class Task(actions.Task):

    def __init__(
            self,
            path: Path|str,
            filters: Filters,
            executor:executors.Executor|None = None
        ):
        super().__init__(executor)
        self.path = Path(path)
        
        # self.executor: executors.Executor|None = None
        # self.tasks      = tasks     if tasks    else executor.tasks
        # self.results    = results   if results  else executor.results
        # self.create     = create    if create   else executor.create

        self.rmdir_actions: list[actions.Action]  = []
        self.filters: Filters        = filters

    def __str__(self):
        return f"<Task name='Directory traverse' path='{str(self.path)}'>"

    def _executor(self, use: str):
        executor = None
        if use and self.executor:
            if use not in self.executor.childs:
                executor = executors.EXECUTORS()[use]()
                logger.debug(
                    f"{executor.debug_info('Task')}. Task({str(self)}). "
                    f"Created child executor({type(executor)})."
                )
                self.executor.childs[use] = executor
                executor.parent = self.executor
            else:
                executor = self.executor.childs[use]
            if executor is None:
                executor = self.executor
                logger.warning(
                    f"{executor.debug_info()}. Task({str(self)}). "
                    f"Executor(name='{use}') not found. "
                    f"Fallback to parent executor({type(executor)})."
                )
        elif self.executor:
            executor = self.executor
        return executor

    def _process_file(self, path):#, executor, tasks, results, create):
        _filter = self.filters(path)
        action = _filter(path)
        executor = self._executor(_filter.use)
        if executor is not None:
            executor.submit(action)

    def _process_dir(self, path):
        pass

    #   Get path entity type
    def _path_type(self, path):
        try:
            is_dir  = path.is_dir()
            is_file = path.is_file()
        except Exception as e:
            if self.executor is not None and self.executor.results is not None:
                self.executor.results.put_nowait(str(e))
            raise e
        return is_dir, is_file

    def __call__(self, path = None, *args, **kwargs):
        path = self.path if not path else path
        # tasks   = self.tasks    if not tasks    else tasks
        # results = self.results  if not results  else results
        # create  = self.create   if not create   else create
        # executor = executors.EXECUTORS()["processes"]
        if self.executor is None:
            return None
        
        is_dir = False
        is_file = False
        if self.path:
            # Get path entity type
            is_dir, is_file = self._path_type(self.path)
            if is_file: 
                self._process_file(self.path)#, tasks, results, create)

            elif is_dir:
                for path in self.path.iterdir():
                    #   Get path entity type
                    is_dir, is_file = self._path_type(path)
                    
                    if is_dir: # Process dir
                        #  Exclude destination directories
                        #  aka [archives, videos, audios, etc.].
                        if Path(path.name) in self.filters:
                            continue
                        #   Remove empty dirs
                        if not self.filters.keep_empty_dir:# and path.exists() and not any(path.iterdir()):
                            self.rmdir_actions.insert(0, actions.RemoveEmptyDirAction(path))
                        
                            # (\
                            #         threading.current_thread()  == threading.main_thread()  \
                            #     or  self.executor.max_workers   == 1                        \
                            # )\
                            # and not multiprocessing.parent_process()\
                        # if      self.executor.in_main_process   \
                        #     and self.executor.in_main_thread    \
                        if self.executor.in_main:
                            results = self.__call__(path) # Going to recusion
                            self.executor.process_results(results)
                        else:
                            filters_list = self.filters.filters
                            filters = Filters(self.filters.root)
                            filters.filters = filters_list
                            task = Task(path, filters)#, executor)#, tasks, results, create)
                            self.executor.submit(task)#, tasks, results, create)

                    elif is_file: # Process files
                        self._process_file(path)#, executor, tasks, results, create)
                    else:
                        continue

        
        # If exceptions is been and execution is in Main Thread, raise it all as Queue object
        # and threading.current_thread() == threading.main_thread() \
        # if  not self._status.empty() \
        #     and path == self.filters.root:
        #     raise Exception(self._status)

        # Remove empty directories
        if self.rmdir_actions:
            rmdir_actions = actions.ActionSequence(self.rmdir_actions)
            # print(rmdir_actions.path, flush = True)
            self.executor.submit(rmdir_actions)#, tasks, results, create)
        
        self.executor.submit(None)#, executor, tasks, results, create)
        # if self.executor.results:
        #     lresults = []
        #     while True:
        #         try:
        #             result = self.executor.results.get_nowait()
        #             if result:
        #                 lresults.append(result)
        #         except Exception as e:
        #             break
        #     if lresults:
        #         return ", ".join(lresults)
        return self.executor.results


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
        filters += Filter(Path("archives"),  ["zip", "tar", "tgz", "gz", "7zip", "7z", "iso", "rar"] ,                           ["unpack", "copy"],    "process")
        filters += Filter(Path("audios"),    ["wav", "mp3", "ogg", "amr"],                                                       ["copy"])
        filters += Filter(Path("images"),    ["jpeg", "png", "jpg", "svg"],                                                      ["copy"])
        filters += Filter(Path("videos"),    ["avi", "mp4", "mov", "mkv"],                                                       ["copy"])
        filters += Filter(Path("documents"), ["doc", "docx", "txt", "pdf", "xls", "xlsx", "ppt", "pptx", "rtf", "xml", "ini"],   ["copy"])
        filters += Filter(Path("softwares"), ["exe", "msi", "bat", "dll", "apk"],                                                ["copy"])
        filters += Filter(Path("other"),     [""],                                                                               ["copy"])
        
        task = Task(path, filters, executor)#, executor)#, tasks, results, create)
        executor.submit(task)#, executor.tasks, executor.results, executor.create)
    # print(f"Results size: {executor.results.qsize()}.")
    return

# def main():
#     # executor = executors.registry["mainthread"]
#     # executor = executors.registry["thread"]
#     # executor = executors.registry["threads"]
#     # executor = executors.registry["threadpool"]
#     # executor = executors.registry["processpool"]
#     # executor = executors.registry["processes"]
#     # print(id(executor))

#     # sort_targets(executor, "D:/work")
#     sort_targets("D:/edu/test", executor)#, tasks, results, create)
#     # manager.join()
#     executor.join()
#     executor.shutdown(True)


if __name__ == "__main__":

    # executor = executors.registry["processes"]
    # print(id(executor))

    # process = multiprocessing.Process(target=main)
    # process.start()
    # process.join()

    profile = cProfile.Profile()
    profile.enable()

    if sys.getprofile():
        start = time.time()

        # multiprocessing.freeze_support()
        # executor = executors.registry["processes"]

        # manager = executors.ProcessesManager()
        # proxy = None
        # proxy = executors.ProcessesExecutorProxy
        # # proxy = executors.Proxy(executors.ProcessesExecutor)
        # # manager.register("Queue", executors.Queue)
        # manager.register("ProcessesExecutor", executors.ProcessesExecutor, proxy)
        # manager.start()

        # executor.results = executor.manager.Queue()
        # executor.workers = executor.manager.list()
        # executor.futures = executor.manager.list()

    # executor = executors.registry["mainthread"]()
    # executor = executors.registry["thread"]()
    # executor = executors.registry["threads"]()
    # executor = executors.registry["threadpool"]()
    # executor = executors.registry["processpool"]()
    executor = executors.registry["processes"]()
    # executor.init(4)
    # tasks       = executor.tasks
    # results     = executor.results
    # create      = executor.create


        # current = threading.current_thread()
        # main = threading.main_thread()
        # executor = manager.ProcessesExecutor()
        # executor = executors.ProcessesExecutor()

        # tasks = manager.Queue()
        # results = manager.Queue()
        # create = manager.Event()
        # executor.tasks = tasks
        # executor.results = results
        # executor.create = create
        # executor.set_tasks(tasks)
        # executor.set_results(results)
        
        # print(executor.tasks())
    # sort_targets(executor, "D:/work")
    sort_targets("D:/edu/test", executor)#, tasks, results, create)
    # manager.join()
    print("Join")
    executor.join()
    print("Shutdowning")
    executor.shutdown(True)

    try:
        while result := executor.results.get_nowait():
            print(result, flush = True)
    except Exception as e:
        pass
    print()

    profile.disable()
    profile.print_stats(sort="cumtime")