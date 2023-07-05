from __future__ import annotations

import shutil
# import sys

from abc import ABC, abstractmethod
from collections import UserDict, UserList
from pathlib import Path
from typing import Any, Callable, cast
# import os
# import sys
# import threading

import registry

from executors  import Executor
from logger     import logger

class IAction(ABC):
    
    @abstractmethod
    def __call__(self, *args, **kwargs): ...

class Task(IAction):
    
    def __init__(self, executor: Executor|None = None) -> None:
        super().__init__()
        self.executor: Executor|None = executor

class Action(IAction):

    translation = dict[int,str]|None

    @staticmethod
    def make_translation() -> dict[int, str]:
        """Create translation table from cyrillic to latin.
        Also replace all other character with symbol - '_' except digits"""
        translation_table = {}
        latin = (
                    "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j",
                    "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f",
                    "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu",
                    "ya", "je", "i", "ji", "g"
                )

        # Make cyrillic tuplet
        cyrillic_symbols = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
        cyrillic_list = []
        for c in cyrillic_symbols:
            cyrillic_list.append(c)

        cyrillic = tuple(cyrillic_list)

        # Fill tranlation table
        for c, l in zip(cyrillic, latin):
            translation_table[ord(c)] = l
            translation_table[ord(c.upper())] = l.upper()

        # From symbol [NULL] to '/'. See ASCI table for more details.
        for i in range(0, 48):
            translation_table[i] = '_'
        # From ':' to '@'. See ASCI table for more details.
        for i in range(58, 65):
            translation_table[i] = '_'
        # From symbol '[' to '`'. See ASCI table for more details.
        for i in range(91, 97):
            translation_table[i] = '_'
        # From symbol '{' to [DEL]. See ASCI table for more details.
        for i in range(123, 128):
            translation_table[i] = '_'
        return translation_table
    
    translation = make_translation()

    def __init__(self, path: Path, root: Path|None = None, destination: Path|None = None, normalize = False, overwrite = False):
        self.path       = path          # File to process
        self.root       = root          # Desctination root
        self.destination= destination   # Destination path
        self.normalize  = normalize
        self.overwrite  = overwrite

    def make_destination(self, split = True) -> Path:
        """Create destination path with normalization, if normalization is on."""
        file_name   = self.path.stem
        file_ext    = ''
        if split:
            file_ext    = self.path.suffix
        
        if self.normalize and Action.translation:
            file_name = file_name.translate(cast(dict, Action.translation))
        
        file_name += file_ext

        destination  = Path(self.root) / self.destination if self.root and self.destination else None
        if destination:
            if not destination.exists():
                destination.mkdir()
            return  destination / file_name
        raise Exception(f"Root path for destination:'{destination}' not defined.")
    
    def __str__(self) -> str:
        return f"<Action name='{self.__class__.__name__.replace('Action','')}' path='{str(self.path)}'>"

class CopyAction(Action):

    def __init__(self, path: Path, root: Path, destination: Path, normalize = False, overwrite = False):
        super().__init__(path, root, destination, normalize, overwrite)

    def __call__(self, *args, **kwargs) -> str|Exception:
        destination = self.make_destination()

        if destination:
            if self.overwrite or not destination.exists():
                shutil.copy2(self.path, destination)
                return str(self) + ". From:'" + str(self.path) + "' to:'" + str(destination) + "' done."
        raise Exception(str(self) + f". Destination:'{destination}' doesn't exist.")
        # return None

class MoveAction(Action):

    def __init__(self, path: Path, root: Path, destination: Path, normalize = False, overwrite = False):
        super().__init__(path, root, destination, normalize, overwrite)

    def __call__(self, *args, **kwargs) -> str|Exception:
        destination = self.make_destination()

        if destination:
            if self.overwrite or destination.exists():
                #file_size = self.path.stat().st_size
                shutil.move(self.path, destination)
                return str(self) + ". From:'" + str(self.path) + "' to:'" + str(destination) + "' done."
        raise Exception(str(self) + f". Destination:'{destination}' doesn't exist.")
        # return None

class RemoveAction(Action):

    def __init__(self, path: Path, root: Path|None = None, destination: Path|None = None, normalize = False, overwrite = False):
        super().__init__(path, root, destination, normalize, overwrite)

    def __call__(self, *args, **kwargs) -> str|Exception:
        if self.path.exists():
            self.path.unlink(True)
            return str(self) + ". Path:'" + str(self.path) + "' done."
        raise Exception(str(self) + f". Can't remove file:{self.path}")
        # return None

class RemoveCkeckedAction(Action):

    def __init__(self, path: Path, root: Path, destination: Path, normalize = False, overwrite = False):
        super().__init__(path, root, destination, normalize, overwrite)

    def __call__(self, *args, **kwargs) -> str|Exception:
        """Remove archive if it is unpacked."""
        destination = self.make_destination(False)
        if destination:
            if destination.exists():
                self.path.unlink()
                return str(self) + ". Path:'" + str(self.path) + "' done."
        raise Exception(str(self) + f". Destination:'{destination}' doesn't exist.")
        # return None

class UnpackAction(Action):

    def __init__(self, path: Path, root: Path, destination: Path, normalize = False, overwrite = False):
        super().__init__(path, root, destination, normalize, overwrite)

    def __call__(self, *args, **kwargs) -> str|Exception:
        destination = self.make_destination(False)
        if destination and not destination.exists():
            destination.mkdir()
        
        if destination:
            if self.overwrite or not any(destination.iterdir()):
                try:
                    shutil.unpack_archive(self.path, destination)
                    return str(self) + ". File:'" + str(self.path) + "' to:'" + str(destination) + "' done."
                except Exception as e: #shutil.ReadError as e:
                    destination.rmdir()
                    return e
        raise Exception(str(self) + f". Destination:'{destination}' doesn't exist.")
        # return None

class RemoveEmptyDirAction(Action):

    def __init__(self, path: Path, root: Path|None = None, destination: Path|None = None, normalize = False, overwrite = False):
        super().__init__(path, root, destination, normalize, overwrite)

    def __call__(self, *args, **kwargs) -> str|Exception:
        if self.path.exists() and not any(self.path.iterdir()):
            self.path.rmdir()
            return str(self) + ". Path:'" + str(self.path) + "' done."
        raise Exception(str(self) + f". Can't remove directory:{self.path}" if not any(self.path.iterdir()) else str(self) + f". Directory:{self.path} not empty.")
        # return None

class ActionSequence(IAction, UserList):

    def __init__(self, actions: list[Action]):
        super().__init__(actions)
        self.path = ",".join(str(action.path) for action in actions)

    def __str__(self) -> str:
        return f"<Action name='{self.__class__.__name__.replace('Action','')}' actions=({', '.join([str(action) for action in self])})"

    def __call__(self, *args, **kwargs) -> list[str]:
        results = []
        for action in self.data:
            result = ""
            try:
                result = action()
            except Exception as e:
                result = str(e)
            # if results:
            #     results += "\n"
            # results = results + str(result)
            results.append(result)
        return results

class ACTIONS(registry.REGISTRY):
    """Actions' Factory"""
    pass

ACTIONS.register("Action", __name__, globals(), IAction)
# logger.debug(f"Actions registered:{ACTIONS()}.")
registry = ACTIONS()
# registry.register("Action", __name__, globals(), IAction)
pass
