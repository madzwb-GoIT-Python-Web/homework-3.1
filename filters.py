from collections import UserDict
from copy import deepcopy
from pathlib import Path

import actions
# import executors



class Filter:

    def __init__(self, destination: Path, extensions: str|list, functions: str|list, use: str = "", normalize: bool = True, overwrite: bool = True):

        self.root:Path|None = None          #   Root directory. Sets with adding Filter to Task.
        self.destination    = destination   #   Destination directory.
        self.normalize      = normalize     #   Normalize files' names.
        self.overwrite      = overwrite     #   Overwrite files in destination directory.
        self.use            = use           #   Executor
        self._actions       = []            #   List of functions' objects.

        if isinstance(extensions, str):
            self.extensions = extensions.lower().split()
        else:
            self.extensions = list(map(lambda x: x.lower(),extensions))
        
        if isinstance(functions, str):
            self.functions = functions.lower().split()
        else:
            self.functions = list(map(lambda x: x.lower(),functions))

        #   Fill list with callable actions.
        for function in self.functions:
            action = actions.registry[function]#getattr(self, "_" + name)
            self._actions.append(action)
        

    def __call__(self, path: Path) -> actions.IAction:
        """Generate actions' list."""
        result = []
        for action in self._actions:
            # Create action's instance
            _action = action(path, self.root, self.destination, self.normalize, self.overwrite)
            result.append(_action)
        if len(result) > 1:
            result = actions.ActionSequence(result)
        else:
            result = result[0]
        return result


class Filters(UserDict):

    def __init__(self, path: Path|str|None = None, filter: Filter|None = None, keep_empty_dir: bool = False):
        super().__init__()
        self._root = None
        self.keep_empty_dir = keep_empty_dir
        if isinstance(path, str):
            if not len(path):
                path = Path().cwd()
            else:
                path = Path(path)
        if path and path.exists():
            self._root    = path
        else:   #   Before running protection
            raise FileExistsError(f"Path: '{path}' doesn't exists.")
        
        # self._filters       = {}    #   Destination path to Filter mapping ex. {"archives": Filter()}.
        self._ext2filter    = {}    #   File extension to Filter mapping ex. {"zip": Filter()}.
        if filter and self._root:
            self.data[filter.destination] = filter
            filter.root = self._root
            for ext in filter.extensions:
                self._ext2filter[ext] = filter
    

    @property
    def filters(self) -> dict[Path, Filter]:
        filters = deepcopy(self.data)
        for _filter in filters.values():
            _filter.root = None
        return filters


    @filters.setter
    def filters(self,filters: dict[Path, Filter]):
        self.data = deepcopy(filters)
        self._ext2filter = {}
        for _filter in self.data.values():
            _filter.root = self._root
            for ext in _filter.extensions:
                self._ext2filter[ext] = _filter

    @property
    def root(self) -> Path|None:
        return self._root
    
    @root.setter
    def root(self, path: Path):
        self._root = path
        for _filter in self.data.values():
            _filter.root = self._root

    def __iadd__(self, _filter: Filter):
        """Add filter."""
        self.data[_filter.destination] = _filter
        _filter.root = self._root
        for ext in _filter.extensions:
            self._ext2filter[ext] = _filter
        return self


    def __isub__(self, _filter: Filter):
        """Remove filter."""
        _filter.root = None
        self.data.pop(_filter.destination)
        for ext in _filter.extensions:
            self._ext2filter.pop(ext)
        return self

    def __call__(self, name: Path) -> Filter: #list[actions.IAction]:
        """"""
        ext = name.suffix.replace('.', '').lower()  #   Get file's extension
        #   Find filter by extension
        if len(self._ext2filter) == 1 and '*' in self._ext2filter:
            filter_ = self._ext2filter['*']
        elif not ext in self._ext2filter and Path("other") in self.data:  #   If file extension not found in filters' list and present Filter("other")
            filter_ = self.data[Path("other")]
        else:
            filter_ = self._ext2filter[ext]
        
        # actions = []
        # if filter_: #   Filter found
        #     # actions = [action for action in filter_(name)]
        #     actions = filter_(name)
        # return actions
        return filter_

    # def _file_processing(self, pathname: Path):

    #     ext = pathname.suffix.replace('.', '').lower()  #   Get file extesion
    #     #   Find filter by extension
    #     if len(self._ext2filter) == 1 and '*' in self._ext2filter:
    #         filter_ = self._ext2filter['*']
    #     elif not ext in self._ext2filter and "other" in self._filters:  #   If file extesions not found in filters' list and present Filter("other")
    #         filter_ = self._filters["other"]
    #     else:
    #         filter_ = self._ext2filter[ext]
        
    #     if filter_: #   Filter found
    #         generator = filter_(pathname)    #   Create every filter.
    #         while True:
    #             try:
    #                 action = next(generator)    #   Call filter to create action
    #                 if isinstance(action, Exception):
    #                     self._status.put(action)    #   Store all exceptions for filter functions' call
    #                     continue
    #             except StopIteration:
    #                 break
