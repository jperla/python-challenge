import time
class Waiter(object):
    def __init__(self, variance=.5, short=.5, medium=5, long=50):
        self._variance = variance
        self._short = short
        self._medium = medium
        self._long = long

    def wait_short_time(self):
        time.sleep(self._short)
        
    def wait_medium_time(self):
        time.sleep(self._medium)

    def wait_long_time(self):
        time.sleep(self._long)
