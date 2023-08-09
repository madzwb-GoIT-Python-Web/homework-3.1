import importlib.util
import inspect
import functools
import logging
import unittest
import sys
import os

from abc import ABC, abstractmethod
from pathlib import Path
from unittest.mock import patch

import executors.config as config

from executors import Logging
from executors import logger

# print(__name__)

if "logger.config" in sys.modules:
    config.config.SCRIPT = __file__
    #   !!!ATTENTION!!!
    #   Fucking magic live here!!!
    if __name__ == "__main__":
        config.config.LOG_FILE_TRUNCATE = True
        Logging.truncate()
        Logging.init()
    if "test_sorter" in __name__:# == "test_sorter":
        config.config.DEBUG = True
        Logging.init()
else:
    stream_logger = logging.StreamHandler()
    stream_logger.setFormatter(Logging.formatter)
    logger.addHandler(stream_logger)

import filesorter._argparser as argparser  
import filesorter.sorter as sorter

data_path = ""
modspec = importlib.util.find_spec("filesorter")
if modspec is not None and modspec.origin is not None:
    data_path = os.path.dirname(modspec.origin)
logger.info(f"Using path to data:'{data_path}'")



def testing(function):
    @functools.wraps(function)
    def wrapper(self, *args, **kwds):
        # print('Calling decorated function')
        # stack = [stack for stack in inspect.stack() if stack.filename == __file__]
        self.setup(function.__name__)
        function(self, *args, **kwds)
        self.do(function.__name__)
        self.check(function.__name__)
    return wrapper



class ITestCase(ABC):

    @abstractmethod
    def setup   (self):  ...

    @abstractmethod
    def do     (self):   ...

    @abstractmethod
    def check   (self):  ...



class TestCase(unittest.TestCase,ITestCase):

    name    = None
    path    = "d:/edu/test/original"
    size    = 5305043333
    dest    = "d:/edu/test"
    opts    = []
    args    = None

    def setup(self, name):
        # stack = next(stack for stack in inspect.stack() if stack.filename == __file__)
        # stack = [stack for stack in inspect.stack() if stack.filename == __file__]
        logger.info(f"Testing '{self.name}.{name}' start.")#{__class__.__name__}.
        self.opts = [
                    # "--overwrite"   ,
                    # "--normalize"   ,
                    "--executor"    , self.name,
                    "--settings"    , os.path.join(data_path,"settings.json"),
                    "--destination" , str(Path(self.dest) / (self.name + "." + name)),
                    self.path,
                ]

    def do(self, name):
        sorter.sort(self.args)
        logger.info(f"Testing '{self.name}.{name}' end.")
    
    def check(self, name):
        self.assertNoLogs(logger,logging.ERROR)
        size = sum(file.stat().st_size for file in Path(f"{self.dest}/{self.name}.{name}").rglob('*'))
        self.assertEqual(self.size, size)
        logger.info(f"Testing '{self.name}.{name}' ok.")

    def call_without_decorator(self, method):
        function = method.__wrapped__
        function(self)

    def opt_exend(self, name):
        self.opts.extend(["--name"          , "archives"])
        self.opts.extend(["--extensions"    , "zip", "tar", "tgz", "gz", "7zip", "7z", "iso", "rar"])
        self.opts.extend(["--functions"     , "unpack", "copy"])
        self.opts.extend(["--use"           , name])

    def get_function_name(self):
        frame = inspect.currentframe()
        while                                       \
                (name:=frame.f_code.co_name)        \
            and not (                               \
                        name.startswith ("test_")   \
                    or  name.endswith   ("_test")   \
                )                                   \
            and (frame:=frame.f_back)               \
        :
            continue
        # print(name)
        name = name.replace("test_","")
        name = name.replace("_test","")
        return name



class TestCaseOverwrite(TestCase):

    def setup(self, name):
        super().setup(name)
        self.opts.append("--overwrite")
        self.size = [self.size, 5304456256, 5304456256, 5305043313, 5303097733]

    def check(self, name):
        self.assertNoLogs(logger,logging.ERROR)
        size = sum(file.stat().st_size for file in Path(f"{self.dest}/{self.name}.{name}").rglob('*'))
        self.assertIn(size, self.size)
        logger.info(f"Testing '{self.name}.{name}' ok.")



class TestCaseNormalize(TestCaseOverwrite):

    def setup(self, name):
        super().setup(name)
        self.opts.append("--normalize")



class Tests(TestCase):

    @testing
    def mainthread_test(self):
        name = self.get_function_name()
        self.opt_exend(name)
        self.args =  argparser.get_args(*self.opts)

    @testing
    def thread_test(self):
        name = self.get_function_name()
        self.opt_exend(name)
        self.args =  argparser.get_args(*self.opts)

    @testing
    def process_test(self):
        name = self.get_function_name()
        self.opt_exend(name)
        self.args =  argparser.get_args(*self.opts)

    @testing
    def threads_test(self):
        name = self.get_function_name()
        self.opt_exend(name)
        self.args =  argparser.get_args(*self.opts)

    @testing
    def processes_test(self):
        name = self.get_function_name()
        self.opt_exend(name)
        self.args =  argparser.get_args(*self.opts)

    @testing
    def threadpool_test(self):
        name = self.get_function_name()
        self.opt_exend(name)
        self.args =  argparser.get_args(*self.opts)

    @testing
    def processpool_test(self):
        name = self.get_function_name()
        self.opt_exend(name)
        self.args =  argparser.get_args(*self.opts)



class MainThread(Tests):

    name = "mainthread"

    @testing
    def test_mainthread(self):
        self.call_without_decorator(self.mainthread_test)

    @testing
    def test_thread(self):
        self.call_without_decorator(self.thread_test)

    @testing
    def test_process(self):
        self.call_without_decorator(self.process_test)

    @testing
    def test_threads(self):
        self.call_without_decorator(self.threads_test)

    @testing
    def test_processes(self):
        self.call_without_decorator(self.processes_test)

    @testing
    def test_threadpool(self):
        self.call_without_decorator(self.threadpool_test)

    @testing
    def test_processpool(self):
        self.call_without_decorator(self.processpool_test)



class ThreadPoolOverwrite(Tests, TestCaseOverwrite):

    name = "threadpool"

    @testing
    def test_processpool(self):
        self.call_without_decorator(self.processpool_test)



class ThreadPoolNormalize(Tests, TestCaseNormalize):

    name = "threadpool"

    @testing
    def test_processpool(self):
        self.call_without_decorator(self.processpool_test)



class ProcessPoolOverwrite(Tests, TestCaseOverwrite):

    name = "processpool"

    @testing
    def test_processpool(self):
        self.call_without_decorator(self.processpool_test)



class ProcessPoolNormalize(Tests, TestCaseNormalize):

    name = "processpool"

    @testing
    def test_processpool(self):
        self.call_without_decorator(self.processpool_test)



class Thread(MainThread):

    name = "thread"



class Process(MainThread):

    name = "process"



class Threads(MainThread):

    name = "threads"



class Processes(MainThread):

    name = "processes"



class ThreadPool(MainThread):

    name = "threadpool"



class ProcessPool(MainThread):

    name = "processpool"



if __name__ == "__main__":
    app = sys.argv[0]
    with patch("sys.argv", [app]):
        unittest.main()
