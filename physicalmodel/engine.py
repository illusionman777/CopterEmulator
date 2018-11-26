from . import physicalobject as p_obj
import numpy as py


class Engine(p_obj.PhysicalObject):
    def __init__(self):
        super(Engine, self).__init__()
        self.max_power = 1.
        self.max_drive_moment = 0.
        self.max_pwm = 1
        self.blade_diameter = 0.
        self.blade_coef_alpha = 0.8
        self.blade_coef_beta = 1.0
        self.rotation_dir = "counterclockwise"
        self.blade_dir = "counterclockwise"
        self.blade_air_force = py.array([0., 0., 0.])
        self.blade_air_moment = py.array([0., 0., 0.])
        self.drive_moment = py.array([0., 0., 0.])

        self._current_pwm = 0.
        self._current_power = 0.
        return

    @property
    def current_pwm(self):
        return self._current_pwm

    @current_pwm.setter
    def current_pwm(self, value):
        self._current_pwm = value
        self._current_power = self._current_pwm * self._current_pwm / \
                              (self.max_pwm * self.max_pwm) * self.max_power
        return

    @property
    def current_pow(self):
        return self._current_power
