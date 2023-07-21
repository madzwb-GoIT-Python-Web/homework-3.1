import sys

import executors.executors as executors
import registrator.registrator as registrator



class EXECUTERS(registrator.REGISTRATOR):
    pass

EXECUTERS.register("Executor", "executors.executors", vars(sys.modules["executors.executors"]), executors.IExecutor)
registry = EXECUTERS()

