import numpy as py
import pyquaternion as quat


class PhysicalObject:
    def __init__(self):
        self.mass = 0.0
        self.inertia_moment = py.array([[0., 0., 0.],
                                         [0., 0., 0.],
                                         [0., 0., 0.]])
        self.pos_v = py.array([0., 0., 0.])
        self.rot_q = quat.Quaternion()
        self.vel_v = py.array([0., 0., 0.])
        self.rot_q_diff = quat.Quaternion([0., 0., 0., 0.])
        self.angular_vel_v = py.array([0., 0., 0.])
        self.acel_v = py.array([0., 0., 0.])
        self.angular_acel_v = py.array([0., 0., 0.])
        return
