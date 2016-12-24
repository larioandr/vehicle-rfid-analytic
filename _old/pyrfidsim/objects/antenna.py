from pyrfidsim.helpers.geometry import Vec3
from pyrfidsim.objects.gobject import GObject


class Antenna(GObject):
    def __init__(self, owner=None, index=0, radiation_pattern=None, gain=0, position=(0, 0, 0), orientation=(1, 0, 0)):
        super().__init__()
        self.owner = owner
        self.index = index
        self.radiation_pattern = radiation_pattern
        self.gain = gain
        self.position = position
        self.__orientation__ = Vec3.normalize(orientation)

    @property
    def orientation(self):
        return Vec3.get_in_axes(self.__orientation__, self.owner.x_axis, self.owner.y_axis, self.owner.z_axis)

    @orientation.setter
    def orientation(self, value):
        self.__orientation__ = Vec3.normalize(value)
