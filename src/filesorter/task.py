from __future__ import annotations

from pathlib import Path

import actions
import executors

from filters import Filters
from logger import logger



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

        self.rmdir_actions: list[actions.Action] = []
        self.filters: Filters = filters

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
            raise   RuntimeError(
                        f"executor is not specified."
                    )
        
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
