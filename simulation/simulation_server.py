from .controller_process import controller_process
from .emulator_process import emulator_process
from .logger_process import logger_process
from .graphics_thread import graphics_thread
from .stop_signal import stop_signal
from physicalmodel import Copter
import multiprocessing
import threading
import json_serializer
import c_emulator
import copy

__settings_file__ = 'settings.json'


class SimulationServer:
    def __init__(self, copter, settings, widget_3d, plotter, graphics_widget):
        self.graphics_widget = graphics_widget
        if not settings:
            self.settings = json_serializer.readfile(__settings_file__)
            self.settings.graphics_enabled = False
        else:
            self.settings = settings
        if not isinstance(copter, Copter):
            self.copter = json_serializer.readfile(self.settings.current_copter)
        else:
            self.copter = copter

        self._set_start_state_to_copter()

        self.stop_event = multiprocessing.Event()
        self.running_event = multiprocessing.Event()
        self.graphics_event = multiprocessing.Event()
        self.em_stopped_event = multiprocessing.Event()
        self.contr_stopped_event = multiprocessing.Event()
        emulator_out, emulator_in = multiprocessing.Pipe(duplex=False)
        controller_out, controller_in = multiprocessing.Pipe(duplex=False)
        logger_out, logger_in = multiprocessing.Pipe(duplex=False)
        graphics_out, graphics_in = multiprocessing.Pipe(duplex=False)
        self.emulator_in = emulator_in
        self.controller_in = controller_in
        self.logger_in = logger_in
        self.controller_proc = multiprocessing.Process(
            target=controller_process,
            args=(copter, settings, controller_out, emulator_in,
                  self.stop_event, self.running_event,
                  self.em_stopped_event, self.contr_stopped_event, )
        )
        self.emulator_proc = multiprocessing.Process(
            target=emulator_process,
            args=(copter, settings, emulator_out, controller_in, logger_in, graphics_in,
                  self.stop_event, self.running_event, self.graphics_event,
                  self.em_stopped_event, self.contr_stopped_event, )
        )
        self.logger_proc = multiprocessing.Process(
            target=logger_process,
            args=(copter, settings, logger_out, self.stop_event, self.running_event, self.em_stopped_event, )
        )
        if self.settings.graphics_enabled:
            self.update_event = multiprocessing.Event()
            widget_3d.update_event = self.update_event
            self.graphics_thread = threading.Thread(
                target=graphics_thread,
                args=(widget_3d, plotter, settings, graphics_out,
                      self.stop_event, self.running_event, self.graphics_event,
                      self.update_event, self.em_stopped_event, )
            )
        self.stop_signal = threading.Thread(
            target=stop_signal,
            args=(self, self.stop_event, )
        )
        self.simulation_running = False
        self.simulation_paused = False
        return

    def _set_start_state_to_copter(self):
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
        emulator_c = c_emulator.cEmulator(self.copter, 1e-8)
        t_end = 2.0 * 1e-8
        pwm = list()
        for i in range(self.copter.num_of_engines):
            pwm.append(self.settings.start_state.engines_state[i].current_pwm)
        state_tmp = copy.deepcopy(self.settings.start_state)
        emulator_c.calculate_state(pwm, t_end, state_tmp)
        for i in range(3):
            self.settings.start_state.fuselage_state.acel_v[i] = state_tmp.fuselage_state.acel_v[i]
            self.settings.start_state.fuselage_state.angular_acel_v[i] = state_tmp.fuselage_state.angular_acel_v[i]
        return

    def start_simulation(self):
        self.stop_event.clear()
        self.running_event.set()
        self.graphics_event.set()
        self.em_stopped_event.clear()
        self.contr_stopped_event.clear()
        self.controller_proc.start()
        self.emulator_proc.start()
        if self.settings.log_enabled:
            self.logger_proc.start()
        if self.settings.graphics_enabled:
            self.update_event.clear()
            self.graphics_thread.start()
        self.stop_signal.start()
        self.settings.start_state.to_list()
        # self.logger_in.send(self.settings.start_state)
        self.emulator_in.send(self.settings.start_state)
        self.controller_in.send(self.settings.start_state)
        self.settings.start_state.to_array()
        self.simulation_running = True
        return

    def pause_simulation(self):
        if self.simulation_paused:
            return
        self.running_event.clear()
        self.simulation_paused = True
        return

    def resume_simulation(self):
        if not self.simulation_paused:
            return
        self.running_event.set()
        self.simulation_paused = False
        return

    def stop_simulation(self):
        self.simulation_running = False
        self.stop_event.set()
        if self.settings.graphics_enabled:
            self.update_event.set()
        self.resume_simulation()
        self.controller_proc.join()
        self.emulator_proc.join()
        if self.settings.log_enabled:
            self.logger_proc.join()
        if self.settings.graphics_enabled:
            self.graphics_thread.join()
        return
