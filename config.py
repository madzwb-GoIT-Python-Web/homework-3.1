import sys

SCRIPT  = ""
TEST    = False
LOGGING = False

DEBUG = True\
            if hasattr(sys, "gettrace") and sys.gettrace()\
            else\
        False
if LOGGING:
    LOG_MULTI = False
    if TEST:
        LOG_TO_TERMINAL = False
    else:
        LOG_TO_TERMINAL = True
    LOG_TO_FILE     = True
else:
    LOG_MULTI       = False
    LOG_TO_TERMINAL = False
    LOG_TO_FILE     = False

PROFILING = True

FIELDS  =   [
                "SCRIPT",
                "DEBUG",
                "TEST",
                "LOG_MULTI",
                "LOG_TO_TERMINAL",
                "LOG_TO_FILE",
                "PROFILING",
            ]
