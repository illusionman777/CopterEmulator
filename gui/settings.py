from pyquaternion import Quaternion
from logger import CopterState
from . import main_window
import json_serializer
import os
import numpy as py


class Settings:
    def __init__(self):
        self.current_copter = 'None'
        self.log_file = 'None'
        self.graphics_enabled = True
        self.view3d_enabled = True
        self.ground_collision = True
        self.ground_level = 0.
        self.dest_pos = py.array([0., 0., 0.])
        self.dest_q = Quaternion()
        self.dt = 0.1
        self.log_enabled = True
        self.log_inf = True
        self.log_time = 1
        self.real_time_syncr = True
        self.controller_freq = 1
        self.vert_syncr = True
        self.hover_mod_on_start = False
        self.start_state = CopterState()
        return

    def save(self):
        json_serializer.writefile(main_window.__settings_path__, self)
        return

    @staticmethod
    def load():
        return json_serializer.readfile(main_window.__settings_path__)

    @property
    def current_copter(self):
        return self._current_copter

    @current_copter.setter
    def current_copter(self, value):
        self._current_copter = value
        if os.path.isfile(self._current_copter):
            copter = json_serializer.readfile(self._current_copter)
            self.start_state = CopterState(copter)
            self.log_file = main_window.__logs_dir__ + copter.name + '_log.log'
            for i in range(copter.num_of_engines):
                self.start_state.engines_state[i].rotation_dir = copter.engines[i].rotation_dir
        return
