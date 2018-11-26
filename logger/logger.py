from .copter_state import CopterState
from pyquaternion import Quaternion
import json
import numpy
import json_serializer
import os
import sys

__logs_dir__ = os.path.dirname(os.path.realpath(sys.argv[0])) + \
               os.path.sep + 'logs' + os.path.sep


class Logger:
    def __init__(self, copter, settings):
        self.settings = settings
        self.copter = copter
        self.copter_state = CopterState(copter)
        self.log_inf = settings.log_inf
        self.log_file = settings.log_file
        header = [
            copter.name,
            copter.num_of_engines,
            settings.current_copter,
            settings.dest_pos.tolist(),
            settings.dest_q.elements.tolist(),
            settings.ground_level
        ]
        self.header_json = json.dumps(header)
        if self.log_inf:
            self.log_file = open(self.log_file, 'w+')
            self.log_file.write(self.header_json + '\n')
        else:
            self.start_time = 0.0
            self.log_time = settings.log_time
            self.log_file_tmp = open(__logs_dir__ + "log.tmp", 'w+')
            self.log_file_tmp1 = open(__logs_dir__ + "log1.tmp", 'w+')
            self.file_dict = {
                self.log_file_tmp: self.log_file_tmp1,
                self.log_file_tmp1: self.log_file_tmp
            }
            self.log_time = settings.log_time
            self.active_file = self.log_file_tmp
        return

    def write_log(self):
        log_state = [
            self.copter_state.t,
            self.copter_state.fuselage_state.pos_v,
            self.copter_state.fuselage_state.velocity_v,
            self.copter_state.fuselage_state.acel_v,
            self.copter_state.fuselage_state.rot_q,
            self.copter_state.fuselage_state.angular_vel_v,
            self.copter_state.fuselage_state.angular_acel_v
        ]
        i = 0
        for engine_state in self.copter_state.engines_state:
            log_state.append([
                engine_state.rot_q[0],
                engine_state.rot_q[3],
                engine_state.current_pwm,
                engine_state.current_pow,
                engine_state.angular_vel_v[2]
            ])
            i += 1
        log_state_json = json.dumps(log_state)
        if self.log_inf:
            self.log_file.write(log_state_json + '\n')
        else:
            if self.copter_state.t - self.start_time > self.log_time:
                self.active_file = self.file_dict[self.active_file]
                self.start_time = self.copter_state.t
                self.active_file.seek(0, 0)
            self.active_file.write(log_state_json + '\n')
        return

    def compose_log_file(self):
        if self.log_inf:
            self.log_file.close()
            return
        self.log_file = open(self.log_file, 'w+')
        self.log_file.write(self.header_json + '\n')
        first_file = self.file_dict[self.active_file]
        first_file.seek(0, 0)
        write_log = False
        start_time = self.copter_state.t - self.log_time
        for line in first_file:
            current_state = json.loads(line)
            if current_state[0] >= start_time:
                write_log = True
            if write_log:
                self.log_file.write(line)
        first_file.close()
        self.active_file.seek(0, 0)
        for line in self.active_file:
            self.log_file.write(line)
        self.active_file.close()
        self.log_file.close()
        return

    @staticmethod
    def load_log(log_name, window):
        log_file = open(log_name, 'r')
        header = log_file.readline()
        header = json.loads(header)
        window.copter_name = header[0]
        window.num_of_engines = header[1]
        current_copter = header[2]
        window.settings.current_copter = current_copter
        window.copter = json_serializer.readfile(current_copter)
        window.dest_pos = numpy.array(header[3])
        window.dest_q = Quaternion(header[4])
        window.settings.ground_level = header[5]
        info_start = log_file.tell()
        num_of_states = 0
        for line in log_file:
            num_of_states += 1
        states = numpy.ndarray([7 + header[1], num_of_states], dtype=object)
        log_file.seek(info_start, 0)
        state_counter = 0
        for line in log_file:
            state_list = json.loads(line)
            states[0, state_counter] = state_list[0]
            states[1, state_counter] = state_list[1]
            states[2, state_counter] = state_list[2]
            states[3, state_counter] = state_list[3]
            states[4, state_counter] = state_list[4]
            states[5, state_counter] = state_list[5]
            states[6, state_counter] = state_list[6]
            counter = 7
            for i in range(header[1]):
                states[counter, state_counter] = state_list[counter]
                counter += 1
            state_counter += 1
        log_file.close()
        return states
