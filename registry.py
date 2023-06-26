
from __future__ import annotations

import inspect
import sys

from collections import UserDict
from typing import Any, Callable, cast, Type


"""Return dict of classes by restrictions."""
def register(
        name    : str           = "",
        module  : str           = __name__,
        env     : dict[Any, Any]= globals(),
        base    : type|None     = None,
        filters : list[str]     = ["__builtins__"]
    ) -> dict[str, Callable]\
    :
    result = {}
    attributes = dir(sys.modules[module])
    # _globals = globals()
    for attribute in attributes:
        if attribute not in env:
            continue

        if attribute in filters:
            continue

        if not name or name in attribute:

            _type = env[attribute]
            if base is None:
                base = object

            if          callable(_type)             \
                and     issubclass(_type, base)     \
                and not inspect.isabstract(_type)   \
                :
                # print(attribute,"\t",_type)
                key = attribute.replace(name,"")
                if key:
                    result[key.lower()] = _type
    return result



class REGISTRY(UserDict):

    attribute   : str           = "alias"
    _instance   : REGISTRY|None = None
    _initialized: bool          = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:# not hasattr(cls, '_instance'):
            cls._instance       = super().__new__(cls, *args, **kwargs)
            cls._initialized    = False
        return cls._instance

    def __init__(self, *args, **kwargs):
        if self._initialized:
            return
        self._initialized = True
        super().__init__(*args, **kwargs)
    
    @classmethod
    def register(
            cls,
            name    : str           = "",
            module  : str           = __name__,
            env     : dict[Any, Any]= globals(),
            base    : type|None     = None,
            filters : list[str]     = ["__builtins__"]
        ):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        if cls._instance is not None and not cls._initialized:
            cls._instance.__init__()
        if base is not None:
            cls._base = base

        data = register(name, module, env, base, filters)
        for key, value in data.items():
            setattr(value, cls.attribute, key)
            # v.alias = k
        cls._instance.update(data)
    
    def __call__(self, *args: Any, **kwargs: Any) -> dict|object:
        if args and args[0]:
            key = args[0]
            return self[key]
        else:
            return REGISTRY._instance

    def __getitem__(self, key:  str):
        return super().__getitem__(key)
    
    def __setitem__(self, key: str, cls: type|Callable|None = None):
        if cls is None:
            if super().__contains__(key):
                super().__delitem__(key)
            else:
                raise KeyError(f"In dict:'{super(UserDict,self).__repr__()}', key:'{key}' not found.")
        elif cls is not None:
            if  not inspect.isabstract(cls)                 \
                and issubclass(cast(type, cls), self._base) \
                and callable(cls)                           \
                :
                setattr(cls, self.attribute, key)
                super().__setitem__(key,cls)
            elif inspect.isabstract(cls):
                raise TypeError(f"Class:'{cls}' is abstract class.")
            elif not issubclass(cast(type, cls), self._base):
                raise TypeError(f"Class:'{cls}' is not a subclass of {self._base.__name__}.")
            elif not callable(cls):
                raise TypeError(f"Class:'{cls}' is not callable.")
