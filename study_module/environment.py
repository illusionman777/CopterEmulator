import CopterEmulator
from CopterEmulator import c_emulator
from .logger_process import logger_process
from pyquaternion import Quaternion
import CopterEmulator.json_serializer as json_serializer
import copy
import multiprocessing
import random
import math
import os
import numpy as np

__settings_file__ = os.path.dirname(CopterEmulator.__path__[0]) + \
                    os.path.sep + 'CopterEmulator' + \
                    os.path.sep + 'settings.json'
__logs_dir__ = os.path.dirname(CopterEmulator.__path__[0]) + \
               os.path.sep + 'CopterEmulator' + \
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
        # self.func_prev = 0.0
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
            self.settings.start_state.fuselage_state.rot_q[i] = 2 * (random.random() - 0.5)
            self.settings.start_state.fuselage_state.velocity_v[i] = 2 * (random.random() - 0.5) * self.max_vel
            self.settings.start_state.fuselage_state.angular_vel_v[i] = 2 * (random.random() - 0.5) * \
                                                                        self.max_angular_vel
        if self.settings.start_state.fuselage_state.pos_v[2] < self.settings.ground_level + 1.0:
            self.settings.start_state.fuselage_state.pos_v[2] = random.random() * \
                                                                (self.settings.ground_level + self.max_pos + 1.0)
        self.settings.start_state.fuselage_state.rot_q[3] = random.random()
        quat_norm = math.sqrt(
            self.settings.start_state.fuselage_state.rot_q[0] ** 2 +
            self.settings.start_state.fuselage_state.rot_q[1] ** 2 +
            self.settings.start_state.fuselage_state.rot_q[2] ** 2 +
            self.settings.start_state.fuselage_state.rot_q[3] ** 2
        )
        if quat_norm > 1e-10:
            self.settings.start_state.fuselage_state.rot_q /= quat_norm
        else:
            self.settings.start_state.fuselage_state.rot_q = [1.0, 0.0, 0.0, 0.0]
        engine_angular_vel = random.random() * self.max_engine_vel
        for i in range(self.copter.num_of_engines):
            self.settings.start_state.engines_state[i].rot_q[0] = 2 * (random.random() - 0.5)
            self.settings.start_state.engines_state[i].rot_q[3] = 2 * (random.random() - 0.5)
            quat_norm = math.sqrt(
                self.settings.start_state.engines_state[i].rot_q[0] ** 2 +
                self.settings.start_state.engines_state[i].rot_q[1] ** 2 +
                self.settings.start_state.engines_state[i].rot_q[2] ** 2 +
                self.settings.start_state.engines_state[i].rot_q[3] ** 2
            )
            if quat_norm > 1e-10:
                self.settings.start_state.engines_state[i].rot_q /= quat_norm
            else:
                self.settings.start_state.engines_state[i].rot_q = [1.0, 0.0, 0.0, 0.0]
            self.settings.start_state.engines_state[i].angular_vel_v[2] = engine_angular_vel
            self.settings.start_state.engines_state[i].current_pwm = random.randint(0, self.copter.engines[i].max_pwm)
        return

    def step(self, pwm):
        end_time = self.state.t + self.controller_period
        self.emulator.calculate_state(pwm, end_time, self.state)
        if self.settings.log_enabled:
            self.logger_in.send(self.state)

        quat_cur = Quaternion(self.state.fuselage_state.rot_q)
        quat_relative = quat_cur.conjugate * self.settings.dest_q
        rot_matrix = quat_cur.rotation_matrix
        g = np.dot(rot_matrix, np.array([0.0, 0.0, -9.8062]))
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
            -7 * np.sqrt(observation[0] * observation[0] +
                         observation[1] * observation[1] +
                         observation[2] * observation[2]) \
            - 1 * (1 - abs(observation[3]) + math.sqrt(1 - observation[3] * observation[3])) \
            - 0.5 * np.sqrt(observation[7] * observation[7] +
                            observation[8] * observation[8] +
                            observation[9] * observation[9]) \
            - 1.7 * np.sqrt(observation[10] * observation[10] +
                            observation[11] * observation[11] +
                            observation[12] * observation[12])
        reward = shaping / 10
        '''
        if self.prev_shaping is not None:
            reward = shaping - self.prev_shaping
        self.prev_shaping = shaping
        '''

        done = False
        if np.sqrt(observation[0] * observation[0] + observation[1] * observation[1]
                   + observation[2] * observation[2]) < 0.01:
            reward += 10

        if self.state.fuselage_state.pos_v[2] < self.settings.ground_level:
            done = True
            reward -= 50

        if self.state.t > self.max_time:
            done = True
            reward += 5

        kp = 6.0
        kd = 30.0

        pid_controller = 450
        pwm_force = [0.0, 0.0, 0.0, 0.0]
        pwm_force[0] = pid_controller
        pwm_force[1] = pid_controller
        pwm_force[2] = pid_controller
        pwm_force[3] = pid_controller

        func_cur = (1 - abs(quat_relative[0]) + math.sqrt(1 - quat_relative[0] * quat_relative[0]))
        axis = np.array([
            quat_relative[1],
            quat_relative[2],
            quat_relative[3]
        ])
        if np.linalg.norm(axis) > 1e-14:
            axis /= np.linalg.norm(axis)
        moment = np.array([
            axis[0] / self.copter.engines[0].blade_coef_alpha / abs(self.copter.vector_fus_engine_mc[0][0]),
            axis[1] / self.copter.engines[0].blade_coef_alpha / abs(self.copter.vector_fus_engine_mc[0][1]),
            axis[2] / self.copter.engines[0].blade_coef_beta / self.copter.engines[0].blade_diameter
        ])

        angular_vel = np.array(self.state.fuselage_state.angular_vel_v)
        angular_vel = np.dot(self.settings.dest_q.conjugate.rotation_matrix, angular_vel)
        moment *= kp * func_cur
        moment -= kd * angular_vel

        pwm_current = [0.0, 0.0, 0.0, 0.0]
        pwm_current[0] = round(moment[0] - moment[1] - moment[2] + pid_controller)
        pwm_current[1] = round(moment[0] + moment[1] + moment[2] + pid_controller)
        pwm_current[2] = round(-moment[0] + moment[1] - moment[2] + pid_controller)
        pwm_current[3] = round(-moment[0] - moment[1] + moment[2] + pid_controller)

        for i in range(len(pwm_current)):
            if pwm_current[i] > self.copter.engines[i].max_pwm:
                pwm_current[i] = self.copter.engines[i].max_pwm
            if pwm_current[i] < 0:
                pwm_current[i] = 0

        return [observation, pwm_current, reward, done]

    def __del__(self):
        if not self.logger_proc:
            return
        if self.logger_proc.is_alive():
            self.logger_in.send("stop")
            self.logger_proc.join()
            self.logger_in.close()
        return
