import math
import numpy as py
import pyquaternion as quat
from . import physicalobject as p_obj
from . import engine


class Copter:
    def __init__(self):
        self.name = 'Unnamed'
        self.fuselage = p_obj.PhysicalObject()
        self.aero_square = 0.
        self.drag_coef = py.array([0., 0., 0.])
        self.moment_coef = py.array([0., 0., 0.])
        self._num_of_engines = 4
        self.engines = list()
        self._distance_fus_engine_mc = list()
        self._height_fus_engine_mc = list()
        self.fus_engine_q = list()
        self._angle_fus_engine = list()
        self.symmetry = False
        self._equal_engines = False
        self._vector_fus_engine_mc = list()
        for i in range(self._num_of_engines):
            self.engines.append(engine.Engine())
            self._distance_fus_engine_mc.append(0.)
            self._height_fus_engine_mc.append(0.)
            self.fus_engine_q.append(quat.Quaternion())
            self._angle_fus_engine.append(0.)
            self._vector_fus_engine_mc.append(py.array([0., 0., 0.]))
        return

    @property
    def equal_engines(self):
        return self._equal_engines

    @equal_engines.setter
    def equal_engines(self, value):
        if value:
            for i in range(self.num_of_engines):
                if i % 2:
                    self.engines[i].rotation_dir = 'clockwise'
                    self.engines[i].blade_dir = 'clockwise'
        self._equal_engines = value
        return

    @property
    def distance_fus_engine_mc(self):
        return self._distance_fus_engine_mc

    @distance_fus_engine_mc.setter
    def distance_fus_engine_mc(self, value):
        if not isinstance(value, list):
            raise TypeError("Distance from fuselage mc to engine mc must be a list")

        if not len(value) == self._num_of_engines:
            raise TypeError("Distance from fuselage mc to engine mc"
                            "must be a list with {} elements".format(self._num_of_engines))

        self._distance_fus_engine_mc = value
        for i in range(self.num_of_engines):
            vector = self.vector_fus_engine_mc[i]
            if self.symmetry:
                angle = 2 * math.pi / self.num_of_engines
                angle = angle / 2 + angle * i
                vector = py.array([self._distance_fus_engine_mc[i] * math.cos(angle),
                                   self._distance_fus_engine_mc[i] * math.sin(angle),
                                   vector[2]])
            else:
                vector = py.array([self._distance_fus_engine_mc[i] * math.cos(self.angle_fus_engine[i]),
                                   self._distance_fus_engine_mc[i] * math.sin(self.angle_fus_engine[i]),
                                   vector[2]])
            self._vector_fus_engine_mc[i] = vector
        return

    @property
    def height_fus_engine_mc(self):
        return self._height_fus_engine_mc

    @height_fus_engine_mc.setter
    def height_fus_engine_mc(self, value):
        if not isinstance(value, list):
            raise TypeError("Distance from fuselage mc to engine mc must be a list")

        if not len(value) == self._num_of_engines:
            raise TypeError("Height from fuselage mc to engine mc"
                            "must be a list with {} elements".format(self._num_of_engines))

        self._height_fus_engine_mc = value
        for i in range(self.num_of_engines):
            vector = self.vector_fus_engine_mc[i]
            vector = py.array([vector[0],
                               vector[1],
                               self._height_fus_engine_mc[i]])
            self._vector_fus_engine_mc[i] = vector
        return

    @property
    def angle_fus_engine(self):
        return self._angle_fus_engine

    @angle_fus_engine.setter
    def angle_fus_engine(self, value):
        if not isinstance(value, list):
            raise TypeError("Angle from fuselage to engine must be a list")

        if not len(value) == self._num_of_engines:
            raise TypeError("Angle from fuselage to engine"
                            "must be a list with {} elements".format(self._num_of_engines))

        self._angle_fus_engine = value
        if self.symmetry:
            return
        for i in range(self.num_of_engines):
            vector = self.vector_fus_engine_mc[i]
            vector = py.array([self._distance_fus_engine_mc[i] * math.cos(value[i]),
                               self._distance_fus_engine_mc[i] * math.sin(value[i]),
                               vector[2]])
            self._vector_fus_engine_mc[i] = vector
        return

    @property
    def vector_fus_engine_mc(self):
        return self._vector_fus_engine_mc

    @property
    def num_of_engines(self):
        return self._num_of_engines

    @num_of_engines.setter
    def num_of_engines(self, value):
        if self._num_of_engines == value:
            return
        self._num_of_engines = value
        self.engines = list()
        self._distance_fus_engine_mc = list()
        self._height_fus_engine_mc = list()
        self.fus_engine_q = list()
        self._angle_fus_engine = list()
        self._vector_fus_engine_mc = list()
        for i in range(self._num_of_engines):
            self.engines.append(engine.Engine())
            self._distance_fus_engine_mc.append(0.)
            self._height_fus_engine_mc.append(0.)
            self.fus_engine_q.append(quat.Quaternion())
            self.angle_fus_engine.append(0.)
            self._vector_fus_engine_mc.append(py.array([0., 0., 0.]))
        return
