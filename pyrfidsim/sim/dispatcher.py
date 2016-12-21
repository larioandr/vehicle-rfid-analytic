from pyrfidsim.sim.pqueue import PQueue


class Dispatcher:
    class __Dispatcher:
        def __init__(self):
            self.__queue__ = PQueue()
            self.__time__ = 0
            self.__index__ = 0
            self.__max_time__ = -1

        def schedule(self, sender, event, dt):
            index = self.__queue__.put(self.__time__ + dt, (sender, sender, event))
            return index

        def send(self, sender, target, event, dt=0):
            index = self.__queue__.put(self.__time__ + dt, (sender, target, event))
            return index

        def cancel(self, index):
            if index is not None:
                self.__queue__.drop(index)

        def remove_entity(self, entity):
            self.__queue__.drop_all_by(lambda e: e[0] == entity or e[1] == entity)

        def run(self):
            while not self.__queue__.empty() and (self.__max_time__ <= 0 or self.__time__ <= self.__max_time__):
                self.__time__, index, (sender, target, event) = self.__queue__.get()
                # print("{0}: event #{1}: {2}".format(self.__time__, index, event))
                target.handle_event(sender, event)

        def get_time(self):
            return self.__time__

        def get_max_time(self):
            return self.__max_time__

        def set_max_time(self, value):
            self.__max_time__ = value

    instance = None

    def __init__(self, max_time=-1):
        if not Dispatcher.instance:
            Dispatcher.instance = Dispatcher.__Dispatcher()
            Dispatcher.instance.max_time = max_time

    @staticmethod
    def schedule(target, event, dt):
        return Dispatcher.instance.schedule(target, event, dt)

    @staticmethod
    def cancel(index):
        Dispatcher.instance.cancel(index)

    @staticmethod
    def remove_entity(entity):
        Dispatcher.instance.remove_entity(entity)

    @staticmethod
    def run():
        Dispatcher.instance.run()

    @staticmethod
    def get_time():
        return Dispatcher.instance.get_time()

    @staticmethod
    def get_max_time():
        return Dispatcher.instance.get_max_time()

