from __future__ import annotations
from collections import UserDict
from copy import deepcopy
from pathlib import Path

import filesorter.actions as actions



class Filter:

    def __init__(
            self,
            parent      : Filters|None,
            name        : str,
            extensions  : str|list[str],
            functions   : str|list[str],
            use         : str = ""
        ):
        self.parent :Filters|None   = parent
        self.root   :Path|None      = None  #   Root directory. Sets with adding Filter to Task.
        self.name           = name          #   Destination directory.
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
            _action =   action(
                            path,
                            self.root,
                            self.name,
                            self.parent.normalize if self.parent is not None else False,
                            self.parent.overwrite if self.parent is not None else False,
                            self.parent.use_names if self.parent is not None else True
                        )
            result.append(_action)
        if len(result) > 1:
            result = actions.ActionSequence(result)
        else:
            result = result[0]
        return result


class Filters(UserDict):

    def __init__(
            self,
            path            : Path|str|None = None,
            filter          : Filter|None = None,
            keep_empty_dir  : bool = False,
            normalize       : bool = False,
            overwrite       : bool = False,
            use_names       : bool = True
        ):
        super().__init__()
        self._root = None
        self.keep_empty_dir = keep_empty_dir
        self.normalize      = normalize     #   Normalize files' names.
        self.overwrite      = overwrite     #   Overwrite files in destination directory.
        self.use_names      = use_names

        if isinstance(path, str):
            # if not len(path):
            #     path = Path().cwd()
            # else:
            path = Path(path)
        # if path and not path.exists():
        #     path.mkdir()
        self._root    = path
        # else:   #   Before running protection
        #     raise FileExistsError(f"Path: '{path}' doesn't exists.")
        
        # self._filters       = {}  #   Destination path to Filter mapping ex. {"archives": Filter()}.
        self._ext2filter    = {}    #   File extension to Filter mapping ex. {"zip": Filter()}.
        if filter and self._root:
            self.data[filter.name] = filter
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
            _filter.root    = self._root
            _filter.parent  = self
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
        # name = str(_filter.name)
        if _filter.name in self.data:
            extensions = self.data[str(_filter.name)].extensions
            _filter.extensions.extend(extensions)
            _filter.extensions = [*set(extensions)]

            functions = self.data[str(_filter.name)].functions
            _filter.functions.extend(functions)
            _filter.functions = [*set(functions)]

        self.data[_filter.name] = _filter
        _filter.root    = self._root
        _filter.parent  = self
        for ext in _filter.extensions:
            self._ext2filter[ext] = _filter
        return self


    def __isub__(self, _filter: Filter):
        """Remove filter."""
        _filter.root    = None
        _filter.parent  = None
        self.data.pop(_filter.name)
        for ext in _filter.extensions:
            self._ext2filter.pop(ext)
        return self

    def __call__(self, name: Path) -> Filter: #list[actions.IAction]:
        """"""
        ext = name.suffix.replace('.', '').lower()  #   Get file's extension
        # Find filter by extension
        if len(self._ext2filter) == 1 and '*' in self._ext2filter:
            filter_ = self._ext2filter['*']
        # If file extension not found in filters' list and present Filter("other")
        elif not ext in self._ext2filter and Path("other") in self.data:
            filter_ = self.data[Path("other")]
        elif not ext in self._ext2filter and "other" in self.data:
            filter_ = self.data["other"]
        else:
            filter_ = self._ext2filter[ext]
        
        # actions = []
        # if filter_: #   Filter found
        #     # actions = [action for action in filter_(name)]
        #     actions = filter_(name)
        # return actions
        return filter_
