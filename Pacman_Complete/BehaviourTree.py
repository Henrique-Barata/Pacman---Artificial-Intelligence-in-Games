__author__ = 'LuisMoniz'


import random
import time
from threading import Thread

from multiprocessing import Process

class Atomic():
    """
    Abstract implementation of an atomic action
    """
    def __init__(self, func):
        self.func = func

    def run(self):
        #print(self.func.__name__)
        return self.func()


class Task(object):
    """ Abstract Task implementation
    """

    def __init__(self):
        super(Task,self).__init__()

    def __init__(self,*children):
        self._children = []
        for child in children:
            self._children.append(child)

    def run(self):
        pass

class Selector(Task):
    """   Selector Implementation   """

    def run(self):
        for c in self._children:
            if c.run() :
                return True
        return False


class RandomSelector(Selector):
    """   Random Implementation   """

    def run(self):
        while True:
            if random.choice(self._children).run():
                return True
        return False



class NonDeterministicSelector(Selector):
    """   NonDeterministicSelector Implementation   """

    def run(self):
        shuffled = random.shuffle(self._children)
        for c in shuffled :
            if c.run() :
                return True
        return False



class Sequence(Task):
    """   Sequence Implementation   """

    def run(self):
        for c in self._children :
            if not c.run() :
                return False
        return True


class NonDeterministicSequence(Task):
    """   NonDeterministicSequence Implementation   """

    def run(self):
        shuffled = random.shuffle(self._children)
        for c in shuffled :
            if not c.run() :
                return False
        return True


class Decorator(Task):

    def __init__(self,child):
        super(Decorator,self).__init__(self)
        self._child = child



class Limit(Decorator):
    """ Counter Decorator Implementation
    """
    def __init__(self,limit,child):
        super(Limit,self).__init__(child)
        self._runLimit = limit


    def run(self):
        if self._runLimit > 0:
            self._runLimit -= 1
            return self._child.run()
        return False

class UntilFail(Decorator):
    """ UntilFail Decorator Implementation
    """

    def run(self):
        while self._child.run():
            pass
        return True

class Wait(Decorator):
    """ Wait implementation
    """
    def __init__(self,duration,child):
        super(Wait,self).__init__(child)
        self._duration = duration

    def run(self):
        time.sleep(self._duration)
        return self._child.run()

class Inverter(Decorator):
    """ Inverter implementation
    """
    def __init__(self,child):
        super(Inverter,self).__init__(child)


    def run(self):
         return not self._child.run()


class Parallel(Task):

    def run(self):
        plist = []
        for child in self._children:
            plist.append(Process(target=child.run))
        for p in plist:
            p.start()
        for p in plist:
            p.join()

    def doit(self,task):
        task.run()
        time.sleep(1.0)
