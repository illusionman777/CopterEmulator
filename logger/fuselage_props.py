import numpy


class FuselageProps:
    def __init__(self):
        self.pos_v = numpy.array([0., 0., 0.])
        self.velocity_v = numpy.array([0., 0., 0.])
        self.acel_v = numpy.array([0., 0., 0.])
        self.rot_q = numpy.array([1., 0., 0., 0.])
        self.angular_vel_v = numpy.array([0., 0., 0.])
        self.angular_acel_v = numpy.array([0., 0., 0.])
        return
