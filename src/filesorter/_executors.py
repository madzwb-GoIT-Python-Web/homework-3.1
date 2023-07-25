import sys

import executors.iexecutor as iexecutor
import registrator.registrator as registrator



class EXECUTERS(registrator.REGISTRATOR):
    pass

EXECUTERS.register("Executor", "executors", vars(sys.modules["executors"]), iexecutor.IExecutor)
registry = EXECUTERS()
pass
