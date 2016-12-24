import numpy as np
from pyrfidsim.helpers.geometry import Vec3


class GObject:
    def __init__(self):
        self.__owner__ = None
        self.__position__ = np.array([0, 0, 0])
        self.__x_axis__ = np.array([1, 0, 0])
        self.__y_axis__ = np.array([0, 1, 0])
        self.__z_axis__ = np.array([0, 0, 1])
        self.children = []

    def destroy(self):
        for child in self.children:
            child.destroy()

    def initialize(self):
        for child in self.children:
            child.initialize()

    @property
    def owner(self):
        return self.__owner__

    @owner.setter
    def owner(self, value):
        if self.__owner__ != value:
            if self.__owner__ is not None:
                self.__owner__.del_child(self)
            self.__owner__ = value
            if self.__owner__ is not None:
                self.__owner__.add_child(self)

    @property
    def position(self):
        if self.owner is None:
            return self.__position__
        else:
            return self.owner.position + Vec3.get_in_axes(
                self.__position__, self.owner.x_axis, self.owner.y_axis, self.owner.z_axis)

    @position.setter
    def position(self, value):
        self.__position__ = value

    @property
    def x_axis(self):
        if self.owner is None:
            return self.__x_axis__
        else:
            return Vec3.get_in_axes(self.__x_axis__, self.owner.x_axis, self.owner.y_axis, self.owner.z_axis)

    @x_axis.setter
    def x_axis(self, value):
        self.__x_axis__ = Vec3.normalize(value)

    @property
    def y_axis(self):
        if self.owner is None:
            return self.__y_axis__
        else:
            return Vec3.get_in_axes(self.__y_axis__, self.owner.x_axis, self.owner.y_axis, self.owner.z_axis)

    @y_axis.setter
    def y_axis(self, value):
        self.__y_axis__ = Vec3.normalize(value)

    @property
    def z_axis(self):
        if self.owner is None:
            return self.__z_axis__
        else:
            return Vec3.get_in_axes(self.__z_axis__, self.owner.x_axis, self.owner.y_axis, self.owner.z_axis)

    @z_axis.setter
    def z_axis(self, value):
        self.__z_axis__ = Vec3.normalize(value)

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)

    def del_child(self, child):
        if child in self.children:
            self.children.remove(child)
