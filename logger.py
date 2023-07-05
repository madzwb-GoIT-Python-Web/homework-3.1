from __future__ import annotations

import logging
import multiprocessing
import os
import config

# import inspect

# def _get_caller(frame):
#     cls_name = None
#     fun_name = None
#     caller   = None
#     if frame:
#         qualname = frame.f_code.co_qualname
#         names = qualname.split(".")
#         length = len(names)

#         cls_name = names[length - 2] if length >= 2 else names[length - 1]
#         fun_name = names[-1]
#         caller   = list(frame.f_locals.values())[0] if len(frame.f_locals) else None
#     return cls_name, fun_name, caller

# frame = inspect.currentframe()
# print(_get_caller(frame))
# while frame := frame.f_back:
#     print(_get_caller(frame))
# print()

if config.LOG_MULTI:
    logger = multiprocessing.get_logger()
else:
    logger = logging.getLogger()

formatter = logging.Formatter("%(asctime)s [%(levelname)-8s] - %(message)s")
formatter_result = logging.Formatter("%(message)s")
formatter.default_msec_format = '%s.%03d'

def init():
    if config.LOG_TO_TERMINAL:
        stream_handler  = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if config.LOG_TO_FILE and config.SCRIPT:
        # if hasattr(sys.modules["__main__"], "__file__"):
        #     main_file = str(sys.modules["__main__"].__file__)
        # else:
        #     main_file = sys.argv[0]
        # print(f"argv: {sys.argv}")
        filename = os.path.dirname(config.SCRIPT)
        filename += "/"
        filename += os.path.splitext(os.path.basename(config.SCRIPT))[0]
        filename += ".log"
        file_handler =  logging.FileHandler(filename)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    level = logging.DEBUG if config.DEBUG else logging.INFO
    logger.setLevel(level)
