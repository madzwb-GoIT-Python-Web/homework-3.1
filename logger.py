import logging
import sys

log_file = "sorter.log"
debugger = 1#sys.gettrace() if hasattr(sys, "gettrace") else False
logger = logging.getLogger()
stream_handler  = logging.StreamHandler()
file_handler    = logging.FileHandler(log_file)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
level = logging.DEBUG# if debugger else logging.INFO
logger.setLevel(level)
# logger.debug()
