from pyrfidsim.helpers.geometry import Vec3
from pyrfidsim.objects.gobject import GObject
import numpy as np

from pyrfidsim.sim.dispatcher import Dispatcher


class Vehicle(GObject):
    def __init__(self):
        super().__init__()
        self.id = 0
        self.direction = np.array([1, 0, 0])
        self.speed = 50.0/3.0   # 60 kmph
        self.distance = 30  # meters
        self.initial_position = None
        self.__created_at__ = None

    @property
    def lifetime(self):
        return self.distance / self.speed

    @property
    def position(self):
        if self.__created_at__ is None:
            return self.initial_position
        else:
            now = Dispatcher.get_time()
            return self.initial_position + self.direction * (now - self.__created_at__) * self.speed

    def add_tag(self, tag):
        tag.owner = self

    def initialize(self):
        self.__created_at__ = Dispatcher.get_time()
        self.direction = Vec3.normalize(self.direction)
        for child in self.children:
            child.initialize()
