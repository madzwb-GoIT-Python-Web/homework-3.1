import sys

import executors.iexecutor as iexecutor
import registrator.registrator as registrator

from executors.executor import TASK_SENTINEL, RESULT_SENTINEL



class EXECUTERS(registrator.REGISTRATOR):
    pass

EXECUTERS.register("Executor", "executors", vars(sys.modules["executors"]), iexecutor.IExecutor)
registry = EXECUTERS()
pass
