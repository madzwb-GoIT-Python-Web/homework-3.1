from __future__ import annotations

import logging
import multiprocessing
import os
import config

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
