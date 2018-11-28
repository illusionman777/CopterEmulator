import numpy as py
import CopterEmulator.physicalmodel as model


class PlotCalculator:
    stop = bool
    copter = model.Copter
    num_of_dots = int
    current_dot = int
    t = py.array
    pos_values = py.array
    pos_redraw = bool
    pos_mode = str
    dest_pos = py.array
    rot_q_values = py.array
    rot_q_redraw = bool
    rot_q_mode = str
    dest_q = py.array
    vel_values = py.array
    ang_vel_values = py.array
    acel_values = py.array
    ang_acel_values = py.array
    engine_pwm_values = py.array
    engine_pow_values = py.array
    engine_ang_v_values = py.array

    def __init__(self, plotter):
        self.stop = False
        self.copter = plotter.copter
        self.num_of_dots = plotter.num_of_dots
        self.current_dot = 0
        self.pos_values = plotter.pos_values
        self.pos_redraw = plotter.pos_tab.redraw
        self.pos_mode = plotter.pos_tab.plot_mode
        self.dest_pos = plotter.settings.dest_pos
        self.rot_q_values = plotter.rot_q_values
        self.rot_q_redraw = plotter.rot_q_tab.redraw
        self.rot_q_mode = plotter.rot_q_tab.plot_mode
        self.dest_q = plotter.settings.dest_q
        self.vel_values = plotter.vel_values
        self.ang_vel_values = plotter.ang_vel_values
        self.acel_values = plotter.acel_values
        self.ang_acel_values = plotter.ang_acel_values
        self.engine_pwm_values = plotter.engine_pwm_values
        self.engine_pow_values = plotter.engine_pow_values
        self.engine_ang_v_values = plotter.engine_ang_v_values
        return

    def calculate(self):
        running = True
        while running:
            i = self.current_dot
            if i < self.num_of_dots:
                for j in range(3):
                    if self.pos_redraw and self.pos_mode == "Absolute value":
                        self.pos_values[j, :i] = self.pos_values[j, :i] + \
                                                       self.dest_pos[j]
                    elif self.pos_redraw:
                        self.pos_values[j, :i] = self.pos_values[j, :i] - \
                                                       self.dest_pos[j]
                    if self.pos_mode == "Absolute value":
                        self.pos_values[j, i] = self.copter.fuselage.pos_v[j]
                    else:
                        self.pos_values[j, i] = self.copter.fuselage.pos_v[j] - \
                                                      self.dest_pos[j]
                    self.vel_values[j, i] = self.copter.fuselage.vel_v[j]
                    self.ang_vel_values[j, i] = self.copter.fuselage.angular_vel_v[j]
                    self.acel_values[j, i] = self.copter.fuselage.acel_v[j]
                    self.ang_acel_values[j, i] = self.copter.fuselage.angular_acel_v[j]
                for j in range(4):
                    if self.rot_q_redraw and self.rot_q_mode == "Absolute value":
                        self.rot_q_values[j, :i] = self.rot_q_values[j, :i] + \
                                                         self.dest_q[j]
                    elif self.rot_q_redraw:
                        self.rot_q_values[j, :i] = self.rot_q_values[j, :i] - \
                                                         self.dest_q[j]
                    if self.rot_q_mode == "Absolute value":
                        self.rot_q_values[j, i] = self.copter.fuselage.rot_q[j]
                    else:
                        self.rot_q_values[j, i] = self.copter.fuselage.rot_q[j] - \
                                                        self.dest_q[j]
                for j in range(self.copter.num_of_engines):
                    self.engine_pwm_values[j, i] = self.copter.engines[j].current_pwm
                    self.engine_pow_values[j, i] = self.copter.engines[j].current_pow
                    ang_v = self.copter.engines[j].angular_vel_v
                    rot_q = self.copter.fuselage.rot_q * self.copter.fus_engine_q[j]
                    ang_v = ang_v.rdot(py.matrix(rot_q.rotation_matrix))
                    self.engine_ang_v_values[j, i] = ang_v[2]
                self.current_dot += 1
                if self.stop:
                    running = False
                continue

            for j in range(3):
                if self.pos_redraw and self.pos_mode == "Absolute value":
                    self.pos_values[j] = self.pos_values[j] + \
                                               self.settings.dest_pos[j]
                elif self.pos_redraw:
                    self.pos_values[j] = self.pos_values[j] - \
                                               self.settings.dest_pos[j]
                self.pos_values[j, :-1] = self.pos_values[j, 1:]
                if self.pos_mode == "Absolute value":
                    self.pos_values[j, -1] = self.copter.fuselage.pos_v[j]
                else:
                    self.pos_values[j, -1] = self.copter.fuselage.pos_v[j] - \
                                                   self.settings.dest_pos[j]
                self.vel_values[j, :-1] = self.vel_values[j, 1:]
                self.vel_values[j, -1] = self.copter.fuselage.vel_v[j]
                self.ang_vel_values[j, :-1] = self.ang_vel_values[j, 1:]
                self.ang_vel_values[j, -1] = self.copter.fuselage.angular_vel_v[j]
                self.acel_values[j, :-1] = self.acel_values[j, 1:]
                self.acel_values[j, -1] = self.copter.fuselage.acel_v[j]
                self.ang_acel_values[j, :-1] = self.ang_acel_values[j, 1:]
                self.ang_acel_values[j, -1] = self.copter.fuselage.angular_acel_v[j]
            for j in range(4):
                if self.rot_q_redraw and self.rot_q_mode == "Absolute value":
                    self.rot_q_values[j] = self.rot_q_values[j] + \
                                                 self.settings.dest_q[j]
                elif self.rot_q_redraw:
                    self.rot_q_values[j] = self.rot_q_values[j] - \
                                                 self.settings.dest_q[j]
                self.rot_q_values[j, :-1] = self.rot_q_values[j, 1:]
                if self.rot_q_mode == "Absolute value":
                    self.rot_q_values[j, -1] = self.copter.fuselage.rot_q[j]
                else:
                    self.rot_q_values[j, -1] = self.copter.fuselage.rot_q[j] - \
                                                     self.settings.dest_q[j]
            for j in range(self.copter.num_of_engines):
                self.engine_pwm_values[j, :-1] = self.engine_pwm_values[j, 1:]
                self.engine_pwm_values[j, i] = self.copter.engines[j].current_pwm
                self.engine_pow_values[j, :-1] = self.engine_pow_values[j, 1:]
                self.engine_pow_values[j, i] = self.copter.engines[j].current_pow
                self.engine_ang_v_values[j, :-1] = self.engine_ang_v_values[j, 1:]
                ang_v = self.copter.engines[j].angular_vel_v
                rot_q = self.copter.fuselage.rot_q * self.copter.fus_engine_q[j]
                ang_v = ang_v.rdot(rot_q.rotation_matrix)
                self.engine_ang_v_values[j, i] = ang_v[2]
            if self.stop:
                running = False
        return
