from collections import UserList
from pathlib import Path

from executors import Executor, TASK_SENTINEL

import filesorter.actions as actions
from filesorter._executors import registry
from filesorter.filters import Filters
from logger.logger import logger
from executors import Logging

class Queue(UserList):

    def put_nowait(self, item):
        self.append(item)
    def get_nowait(self):
        return self.pop(0)

class Task(actions.Task):

    def __init__(
            self,
            path    :   Path|str,
            filters :   Filters,
            executor:   Executor|None = None
        ):
        super().__init__(executor)
        self.path = Path(path)
        self.actions: list[actions.IAction|TASK_SENTINEL] = []
        if self.executor is not None and self.executor.results is not None:
            self.results = self.executor.results
        else:
            self.results = Queue()
        # self.files_actions: list[actions.IAction] = []
        self.filters: Filters = filters

    def __str__(self):
        return f"<Task name='Directory traverse' path='{str(self.path)}'>"


    def get_executor_from_registry(self, use: str):
        executor = None
        try:
            creator = registry[use]
        except KeyError as ex:
            creator = None
        if creator is not None:
            executor = creator()
            if executor is not None:
                logger.debug(
                    f"{Logging.info(str(self))}. "
                    f"Created child executor({type(executor)})."
                )
        return executor

    # if present use field, create child executor
    def _executor(self, use: str):
        executor = None
        if use and self.executor is not None:
            if use == self.executor.alias:
                return self.executor
            elif use in self.executor.childs:
                return self.executor.childs[use]
            else:
                executor = self.get_executor_from_registry(use)
                if executor is not None:
                    self.executor.childs[use] = executor
                    executor.parent = self.executor
                    executor.start()
                    logger.debug(
                        f"{Logging.info(str(self))}. "
                        f"Start child executor({type(executor)})."
                    )
        # elif not use and self.executor is not None:
        #     executor = self.executor
        #     logger.warning(
        #         f"{Logging.info(str(self))}. "
        #         f"Executor(name='{use}') not found. "
        #         f"Fallback to parent executor({type(executor)})."
        #     )
        #     return executor
        elif use and self.executor is None:
            executor = self.get_executor_from_registry(use)
            if executor is not None:
                executor.start()
                logger.debug(
                    f"{Logging.info(str(self))}. "
                    f"Start child executor({type(executor)})."
                )
                # self.executor = executor
        return executor

    def _process_file(self, path):
        _filter = self.filters(path)
        action = _filter(path)
        executor = self._executor(_filter.use)
        if executor is not None:
            executor.submit(action)
            if self.executor is None: # For ProcessPool self.executor is None, wait for child
                executor.submit(TASK_SENTINEL)
                executor.join()
                executor.shutdown(False)
                results = executor.get_results()
                Executor.process_results(self.results, executor.lresults)
        else:
            self.actions.insert(0, action)

    def _process_dir(self, path):
        pass

    #   Get path entity type
    def _path_type(self, path):
        try:
            is_dir  = path.is_dir()
            is_file = path.is_file()
        except Exception as e:
            self.results.put_nowait(str(e))
            # if self.executor is not None and self.executor.results is not None:
            #     self.executor.results.put_nowait(str(e))
            raise e
        return is_dir, is_file

    def __call__(self, path = None, *args, **kwargs):
        path = self.path if path is None else path
        if self.executor is None and self.results is None:
            self.results = Queue()
        #     raise   RuntimeError(
        #                 f"executor is not specified."
        #             )
        
        is_dir  = False
        is_file = False
        if path:
            # Get path entity type
            is_dir, is_file = self._path_type(path)
            if is_file: 
                self._process_file(path)

            elif is_dir:
                for p in path.iterdir():
                    #   Get path entity type
                    is_dir, is_file = self._path_type(p)
                    
                    if is_dir: # Process dir
                        #  Exclude destination directories
                        #  aka [archives, videos, audios, etc.].
                        if Path(p.name) in self.filters:
                            continue
                        if p.name in self.filters:
                            continue
                        #   Remove empty dirs
                        if not self.filters.keep_empty_dir:
                            self.actions.insert(0, actions.RemoveEmptyDirAction(p))

                        if self.executor is None:
                            results, action = self.__call__(p) # Going to recusion
                            Executor.process_results(self.results, results)
                            if action is not None and id(self.actions) != id(action):
                                self.actions.extend(action)
                        elif self.executor.iworkers.value <= 1:
                            results = self.__call__(p) # Going to recusion
                            Executor.process_results(self.results, results)
                        else:
                            filters_list = self.filters.filters
                            filters = Filters(
                                self.filters.root,
                                None,
                                self.filters.keep_empty_dir,
                                self.filters.normalize,
                                self.filters.overwrite,
                            )
                            filters.filters = filters_list
                            task = Task(p, filters)
                            self.executor.submit(task)

                    elif is_file: # Process files
                        self._process_file(p)
                    else:
                        continue

        
        # If exceptions is been and execution is in Main Thread, raise it all as Queue object
        # and threading.current_thread() == threading.main_thread() \
        # if  not self._status.empty() \
        #     and path == self.filters.root:
        #     raise Exception(self._status)

        # Remove empty directories
        if self.executor is not None:
            if self.actions:
                self.executor.submit(actions.ActionSequence(self.actions))
        
            self.executor.submit(TASK_SENTINEL)
            return self.executor.results#, None
        else:
            # self.actions.append(TASK_SENTINEL)
            return self.results, self.actions
