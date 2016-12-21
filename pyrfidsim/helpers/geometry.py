import numpy as np


class Vec3:
    @staticmethod
    def length(r):
        if isinstance(r, np.ndarray):
            return (r**2).sum()**0.5
        else:
            return (r[0]**2 + r[1]**2 + r[2]**2)**0.5

    @staticmethod
    def normalize(r):
        if isinstance(r, np.ndarray):
            return r / Vec3.length(r)
        else:
            l = Vec3.length(r)
            return np.array([r[0]/l, r[1]/l, r[2]/l])

    @staticmethod
    def distance(r0, r1):
        r0 = np.array(r0) if not isinstance(r0, np.ndarray) else r0
        r1 = np.array(r1) if not isinstance(r1, np.ndarray) else r1
        return Vec3.length(r0 - r1)

    @staticmethod
    def get_in_axes(r, x_axis, y_axis, z_axis):
        r = np.array(r) if not isinstance(r, np.ndarray) else r
        x_axis = np.array(x_axis) if not isinstance(x_axis, np.ndarray) else x_axis
        y_axis = np.array(y_axis) if not isinstance(y_axis, np.ndarray) else y_axis
        z_axis = np.array(z_axis) if not isinstance(z_axis, np.ndarray) else z_axis
        x_axis = Vec3.normalize(x_axis)
        y_axis = Vec3.normalize(y_axis)
        z_axis = Vec3.normalize(z_axis)
        return r[0]*x_axis + r[1]*y_axis + r[2]*z_axis

    @staticmethod
    def mul_scalar(r0, r1):
        r0 = np.array(r0) if not isinstance(r0, np.ndarray) else r0
        r1 = np.array(r1) if not isinstance(r1, np.ndarray) else r1
        return (r0 * r1).sum()

    @staticmethod
    def get_angle(r0, r1):
        r0 = np.array(r0) if not isinstance(r0, np.ndarray) else r0
        r1 = np.array(r1) if not isinstance(r1, np.ndarray) else r1
        return np.arccos(Vec3.mul_scalar(r0, r1) / (Vec3.length(r0) * Vec3.length(r1)))
