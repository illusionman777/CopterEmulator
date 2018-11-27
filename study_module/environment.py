import c_emulator
from .logger_process import logger_process
from pyquaternion import Quaternion
import json_serializer
import copy
import multiprocessing
import random
import math
import os
import sys
import numpy as np

__settings_file__ = os.path.dirname(os.path.realpath(sys.argv[0])) + \
                    os.path.sep + 'settings.json'
__logs_dir__ = os.path.dirname(os.path.realpath(sys.argv[0])) + \
               os.path.sep + 'logs' + os.path.sep


class Environment:
    def __init__(self):
        self.settings = None
        self.copter = None
        self.emulator = None
        self.state = None
        self.logger_proc = None
        self.max_pos = None
        self.max_vel = None
        self.max_angular_vel = None
        self.max_engine_vel = None
        self.max_time = None
        self.prev_shaping = None
        self.controller_period = 1.0
        self.logger_out, self.logger_in = multiprocessing.Pipe(duplex=False)

        self.reset(0, log_enabled=False)
        return

    def reset(self, num_of_simulation, log_enabled=True, max_pos=5.0, max_vel=10.0,
              max_angular_vel=5.0, max_engine_vel=50.0, max_time=3600.0):
        self.max_pos = max_pos
        self.max_vel = max_vel
        self.max_angular_vel = max_angular_vel
        self.max_engine_vel = max_engine_vel
        self.max_time = max_time
        if self.logger_proc:
            if self.logger_proc.is_alive():
                self.logger_in.send("stop")
                self.logger_proc.join()
            self.logger_in.close()
            self.logger_out, self.logger_in = multiprocessing.Pipe(duplex=False)
        self.settings = json_serializer.readfile(__settings_file__)
        self.controller_period = 1.0 / self.settings.controller_freq
        self.copter = json_serializer.readfile(self.settings.current_copter)
        self.settings.log_file = __logs_dir__ + self.copter.name + '_{0}.log'.format(num_of_simulation)
        self.settings.log_enabled = log_enabled

        self._random_start_state()

        for i in range(3):
            self.copter.fuselage.pos_v[i] = self.settings.start_state.fuselage_state.pos_v[i]
            self.copter.fuselage.rot_q[i] = self.settings.start_state.fuselage_state.rot_q[i]
            self.copter.fuselage.vel_v[i] = self.settings.start_state.fuselage_state.velocity_v[i]
            self.copter.fuselage.angular_vel_v[i] = self.settings.start_state.fuselage_state.angular_vel_v[i]
        self.copter.fuselage.rot_q[3] = self.settings.start_state.fuselage_state.rot_q[3]
        for i in range(self.copter.num_of_engines):
            self.copter.engines[i].rot_q[0] = self.settings.start_state.engines_state[i].rot_q[0]
            self.copter.engines[i].rot_q[3] = self.settings.start_state.engines_state[i].rot_q[3]
            self.copter.engines[i].angular_vel_v[2] = self.settings.start_state.engines_state[i].angular_vel_v[2]
            if self.copter.engines[i].rotation_dir == "clockwise":
                self.copter.engines[i].angular_vel_v[2] = -self.copter.engines[i].angular_vel_v[2]
            self.copter.engines[i].current_pwm = self.settings.start_state.engines_state[i].current_pwm
            self.settings.start_state.engines_state[i].current_pow = self.copter.engines[i].current_pow
        emulator_tmp = c_emulator.cEmulator(self.copter, 1e-8)
        t_end = 2.0 * 1e-8
        pwm = list()
        for i in range(self.copter.num_of_engines):
            pwm.append(self.settings.start_state.engines_state[i].current_pwm)
        state_tmp = copy.deepcopy(self.settings.start_state)
        emulator_tmp.calculate_state(pwm, t_end, state_tmp)
        for i in range(3):
            self.settings.start_state.fuselage_state.acel_v[i] = state_tmp.fuselage_state.acel_v[i]
            self.settings.start_state.fuselage_state.angular_acel_v[i] = state_tmp.fuselage_state.angular_acel_v[i]
            self.copter.fuselage.acel_v[i] = state_tmp.fuselage_state.acel_v[i]
            self.copter.fuselage.angular_acel_v[i] = state_tmp.fuselage_state.angular_acel_v[i]

        self.emulator = c_emulator.cEmulator(self.copter, self.settings.dt)
        self.state = copy.deepcopy(self.settings.start_state)
        self.state.to_list()
        self.logger_proc = multiprocessing.Process(
            target=logger_process,
            args=(
                self.copter, self.settings, self.logger_out,
            )
        )
        if self.settings.log_enabled:
            self.logger_proc.start()
            self.logger_in.send(self.state)
        return

    def _random_start_state(self):
        random.seed()
        for i in range(3):
            self.settings.start_state.fuselage_state.pos_v[i] = 2 * (random.random() - 0.5) * self.max_pos + \
                                                                self.settings.dest_pos[i]
            self.settings.start_state.fuselage_state.rot_q[i] = random.random()
            self.settings.start_state.fuselage_state.velocity_v[i] = 2 * (random.random() - 0.5) * self.max_vel
            self.settings.start_state.fuselage_state.angular_vel_v[i] = 2 * (random.random() - 0.5) * \
                                                                        self.max_angular_vel
        if self.settings.start_state.fuselage_state.pos_v[2] < self.settings.ground_level + 1.0:
            self.settings.start_state.fuselage_state.pos_v[2] = random.random() * \
                                                                (self.settings.ground_level + self.max_pos + 1.0)
        self.settings.start_state.fuselage_state.rot_q[3] = random.random()
        self.settings.start_state.fuselage_state.rot_q /= math.sqrt(
            self.settings.start_state.fuselage_state.rot_q[0] ** 2 +
            self.settings.start_state.fuselage_state.rot_q[1] ** 2 +
            self.settings.start_state.fuselage_state.rot_q[2] ** 2 +
            self.settings.start_state.fuselage_state.rot_q[3] ** 2
        )
        for i in range(self.copter.num_of_engines):
            self.settings.start_state.engines_state[i].rot_q[0] = random.random()
            self.settings.start_state.engines_state[i].rot_q[3] = random.random()
            self.settings.start_state.engines_state[i].rot_q /= math.sqrt(
                self.settings.start_state.engines_state[i].rot_q[0] ** 2 +
                self.settings.start_state.engines_state[i].rot_q[1] ** 2 +
                self.settings.start_state.engines_state[i].rot_q[2] ** 2 +
                self.settings.start_state.engines_state[i].rot_q[3] ** 2
            )
            self.settings.start_state.engines_state[i].angular_vel_v[2] = random.random() * self.max_engine_vel
            if self.copter.engines[i].rotation_dir == "clockwise":
                self.settings.start_state.engines_state[i].angular_vel_v[2] *= -1
            self.settings.start_state.engines_state[i].current_pwm = random.randint(0, self.copter.engines[i].max_pwm)
        return

    def step(self, pwm):
        end_time = self.state.t + self.controller_period
        self.emulator.calculate_state(pwm, end_time, self.state)
        if self.settings.log_enabled:
            self.logger_in.send(self.state)

        quat_cur = Quaternion(self.state.fuselage_state.rot_q)
        quat_relative = quat_cur.conjugate * self.settings.dest_q
        g = quat_cur.rotation_matrix * np.array([0.0, 0.0, -9.8062])
        g = g[:, 2]
        acel_from_sensor = np.array(self.state.fuselage_state.angular_vel_v) + g
        observation = [
            self.state.fuselage_state.pos_v[0] - self.settings.dest_pos[0],
            self.state.fuselage_state.pos_v[1] - self.settings.dest_pos[1],
            self.state.fuselage_state.pos_v[2] - self.settings.dest_pos[2],
            quat_relative[0],
            quat_relative[1],
            quat_relative[2],
            quat_relative[3],
            self.state.fuselage_state.velocity_v[0],
            self.state.fuselage_state.velocity_v[1],
            self.state.fuselage_state.velocity_v[2],
            self.state.fuselage_state.angular_vel_v[0],
            self.state.fuselage_state.angular_vel_v[1],
            self.state.fuselage_state.angular_vel_v[2],
            acel_from_sensor[0],
            acel_from_sensor[1],
            acel_from_sensor[2],
            self.state.fuselage_state.angular_acel_v[0],
            self.state.fuselage_state.angular_acel_v[1],
            self.state.fuselage_state.angular_acel_v[2],
        ]

        reward = 0.0
        shaping = \
            -200 * np.sqrt(observation[0] * observation[0] +
                           observation[1] * observation[1] +
                           observation[2] * observation[2]) \
            - 100 * (1 - abs(observation[3]) +
                     abs(observation[4]) +
                     abs(observation[5]) +
                     abs(observation[6])) \
            - 100 * np.sqrt(observation[7] * observation[7] +
                            observation[8] * observation[8] +
                            observation[9] * observation[9]) \
            - 100 * np.sqrt(observation[10] * observation[10] +
                            observation[11] * observation[11] +
                            observation[12] * observation[12])
        if self.prev_shaping is not None:
            reward = shaping - self.prev_shaping
        self.prev_shaping = shaping
        done = False
        if self.state.fuselage_state.pos_v[2] < self.settings.ground_level:
            done = True
        if self.state.t > self.max_time:
            done = True
        return [observation, reward, done]

    def __del__(self):
        if not self.logger_proc:
            return
        if self.logger_proc.is_alive():
            self.logger_in.send("stop")
            self.logger_proc.join()
            self.logger_in.close()
        return
