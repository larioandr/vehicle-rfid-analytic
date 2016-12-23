from pyrfidsim.sim.dispatcher import Dispatcher


class Env:
    @staticmethod
    def log(entity, message):
        print("{0:.9f} [{1}] {2}".format(Dispatcher.get_time(), entity, message))