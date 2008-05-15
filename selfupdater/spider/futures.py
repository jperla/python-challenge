import sys
from threading import *
import copy

class Future:
    def __init__(self, func, *args, **kwargs):
        # Constructor
        self.__excpt = None

        self.__done=0
        self.__result=None
        self.__status='working'

        self.__C=Condition()   # Notify on this Condition when result is ready

        # Run the actual function in a separate thread
        self.__T=Thread(target=self.wrapper, args=(func, (args, kwargs)))
        self.__T.setName("FutureThread")
        self.__T.start()

    def __repr__(self):
        return '<Future at '+hex(id(self))+':'+self.__status+'>'

    def __call__(self):
        self.__C.acquire()
        while self.__done==0:
            self.__C.wait()
        self.__C.release()

        #throw exception if there was one
        if self.__excpt is not None:
            raise self.__excpt[0], self.__excpt[1], self.__excpt[2]

        # We deepcopy __result to prevent accidental tampering with it.
        a=copy.deepcopy(self.__result)
        return a

    def wrapper(self, func, params):
        args, kwargs = params

        # Run the actual function, and let us housekeep around it
        self.__C.acquire()

        try:
            self.__result = func(*args, **kwargs)
        except:
            self.__result = "Exception raised within Future"
            self.__excpt = sys.exc_info()

        self.__done=1
        self.__status=`self.__result`
        self.__C.notify()
        self.__C.release()
