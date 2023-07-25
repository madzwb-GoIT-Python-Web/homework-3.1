from pathlib import Path

from executors import Executor

import filesorter.actions as actions
from filesorter._executors import registry
from filesorter.filters import Filters
from logger.logger import logger
from executors import Logging



class Task(actions.Task):

    def __init__(
            self,
            path    :   Path|str,
            filters :   Filters,
            executor:   Executor|None = None
        ):
        super().__init__(executor)
        self.path = Path(path)
        self.rmdir_actions: list[actions.Action] = []
        self.filters: Filters = filters

    def __str__(self):
        return f"<Task name='Directory traverse' path='{str(self.path)}'>"

    # if present use field create child executor
    def _executor(self, use: str):
        executor = None
        if use and self.executor:
            if use not in self.executor.childs:
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
                        self.executor.childs[use] = executor
                        executor.parent = self.executor
                        executor.start()
            else:
                executor = self.executor.childs[use]
            if executor is None:
                executor = self.executor
                logger.warning(
                    f"{Logging.info(str(self))}. "
                    f"Executor(name='{use}') not found. "
                    f"Fallback to parent executor({type(executor)})."
                )
        elif self.executor is not None:
            executor = self.executor
        return executor

    def _process_file(self, path):
        _filter = self.filters(path)
        action = _filter(path)
        executor = self._executor(_filter.use)
        if executor is not None:
            executor.submit(action)
            # executor.submit(None)

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
        path = self.path if path is None else path
        if self.executor is None:
            raise   RuntimeError(
                        f"executor is not specified."
                    )
        
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
                            self.rmdir_actions.insert(0, actions.RemoveEmptyDirAction(p))
                        if self.executor.iworkers.value <= 1:
                            results = self.__call__(p) # Going to recusion
                            self.executor.process_results(results)
                        else:
                            filters_list = self.filters.filters
                            filters = Filters(self.filters.root)
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
        if self.rmdir_actions:
            rmdir_actions = actions.ActionSequence(self.rmdir_actions)
            self.executor.submit(rmdir_actions)
        
        self.executor.submit(None)
        return self.executor.results
