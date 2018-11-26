from .array_shift import array_shift
from gui.plot_widget import PlotWidget
from logger import CopterState
import pyqtgraph as pg
import numpy as py


class Plotter:
    def __init__(self, widget):
        self.copter = widget.copter
        self.settings = widget.settings
        self.copter_state = CopterState(self.copter)
        '''self.view_boxes = []
        plot_widgets = widget.findChildren(pg.PlotWidget)
        for plot_widget in plot_widgets:
            plot_item = plot_widget.getPlotItem()
            self.view_boxes.append(plot_item.getViewBox())'''
        self.num_of_dots = 500
        self.current_dot = 0
        self.t = py.zeros([self.num_of_dots])

        self.pos_tab = widget.findChild(PlotWidget, "pos_tab")
        self.pos_tab.plot_visible.connect(self._update_plot)
        self.pos_curves = self._init_curves(self.pos_tab)
        self.pos_values = py.zeros([3, self.num_of_dots])

        self.rot_q_tab = widget.findChild(PlotWidget, "rot_q_tab")
        self.rot_q_tab.plot_visible.connect(self._update_plot)
        self.rot_q_curves = self._init_curves(self.rot_q_tab)
        self.rot_q_values = py.zeros([4, self.num_of_dots])

        self.vel_tab = widget.findChild(PlotWidget, "vel_tab")
        self.vel_tab.plot_visible.connect(self._update_plot)
        self.vel_curves = self._init_curves(self.vel_tab)
        self.vel_values = py.zeros([3, self.num_of_dots])

        self.ang_vel_tab = widget.findChild(PlotWidget, "ang_vel_tab")
        self.ang_vel_tab.plot_visible.connect(self._update_plot)
        self.ang_vel_curves = self._init_curves(self.ang_vel_tab)
        self.ang_vel_values = py.zeros([3, self.num_of_dots])

        self.acel_tab = widget.findChild(PlotWidget, "acel_tab")
        self.acel_tab.plot_visible.connect(self._update_plot)
        self.acel_curves = self._init_curves(self.acel_tab)
        self.acel_values = py.zeros([3, self.num_of_dots])

        self.ang_acel_tab = widget.findChild(PlotWidget, "ang_acel_tab")
        self.ang_acel_tab.plot_visible.connect(self._update_plot)
        self.ang_acel_curves = self._init_curves(self.ang_acel_tab)
        self.ang_acel_values = py.zeros([3, self.num_of_dots])

        self.engine_pwm_tab = widget.findChild(PlotWidget, "engine_pwm_tab")
        self.engine_pwm_tab.plot_visible.connect(self._update_plot)
        self.engine_pwm_curves = self._init_curves(self.engine_pwm_tab)
        self.engine_pwm_values = py.zeros([self.copter.num_of_engines, self.num_of_dots])

        self.engine_pow_tab = widget.findChild(PlotWidget, "engine_pow_tab")
        self.engine_pow_tab.plot_visible.connect(self._update_plot)
        self.engine_pow_curves = self._init_curves(self.engine_pow_tab)
        self.engine_pow_values = py.zeros([self.copter.num_of_engines, self.num_of_dots])

        self.engine_ang_v_tab = widget.findChild(PlotWidget, "engine_ang_v_tab")
        self.engine_ang_v_tab.plot_visible.connect(self._update_plot)
        self.engine_ang_v_curves = self._init_curves(self.engine_ang_v_tab)
        self.engine_ang_v_values = py.zeros([self.copter.num_of_engines, self.num_of_dots])
        '''for view_box in self.view_boxes:
            view_box.state['limits']['xLimits'][0] = self.settings.start_state.t
            view_box.state['limits']['xLimits'][1] = self.settings.start_state.t + self.settings.dt * self.num_of_dots'''
        return

    @staticmethod
    def _init_curves(tab):
        plots = tab.findChildren(pg.PlotWidget)
        curves = list()
        for plot in plots:
            plot_item = plot.getPlotItem()
            curves.append(plot_item.curves[0])
        return curves

    def _plot_part(self):
        slice_limit = self.current_dot + 1
        self.t[self.current_dot] = self.copter_state.t
        '''for view_box in self.view_boxes:
            view_box.state['limits']['xLimits'][0] = self.t[0]
            view_box.state['limits']['xLimits'][1] = self.t[self.current_dot] + 10'''
        if self.pos_tab.plot_enabled:
            if self.pos_tab.plot_mode == "Absolute value" and not self.pos_tab.redraw:
                self.pos_values[:, self.current_dot] = self.copter_state.fuselage_state.pos_v
            else:
                pos_v = py.ndarray([3])
                for i in range(3):
                    pos_v[i] = self.copter_state.fuselage_state.pos_v[i] - self.settings.dest_pos[i]
                self.pos_values[:, self.current_dot] = pos_v
        if self.rot_q_tab.plot_enabled:
            if self.rot_q_tab.plot_mode == "Absolute value" and not self.rot_q_tab.redraw:
                self.rot_q_values[:, self.current_dot] = self.copter_state.fuselage_state.rot_q
            else:
                rot_q = py.ndarray([4])
                for i in range(4):
                    rot_q[i] = self.copter_state.fuselage_state.rot_q[i] - self.settings.dest_q[i]
                self.rot_q_values[:, self.current_dot] = rot_q
        if self.vel_tab.plot_enabled:
            self.vel_values[:, self.current_dot] = self.copter_state.fuselage_state.velocity_v
        if self.ang_vel_tab.plot_enabled:
            self.ang_vel_values[:, self.current_dot] = self.copter_state.fuselage_state.angular_vel_v
        if self.acel_tab.plot_enabled:
            self.acel_values[:, self.current_dot] = self.copter_state.fuselage_state.acel_v
        if self.ang_acel_tab.plot_enabled:
            self.ang_acel_values[:, self.current_dot] = self.copter_state.fuselage_state.angular_acel_v[:]
        current_pwm = py.ndarray([self.copter.num_of_engines])
        current_pow = py.ndarray([self.copter.num_of_engines])
        engines_ang_v_values = py.ndarray([self.copter.num_of_engines])
        for i in range(self.copter.num_of_engines):
            current_pwm[i] = self.copter_state.engines_state[i].current_pwm
            current_pow[i] = self.copter_state.engines_state[i].current_pow
            engines_ang_v_values[i] = self.copter_state.engines_state[i].angular_vel_v[2]
        if self.engine_pwm_tab.plot_enabled:
            self.engine_pwm_values[:, self.current_dot] = current_pwm
        if self.engine_pow_tab.plot_enabled:
            self.engine_pow_values[:, self.current_dot] = current_pow
        if self.engine_ang_v_tab.plot_enabled:
            self.engine_ang_v_values[:, self.current_dot] = engines_ang_v_values
        for i in range(3):
            if self.pos_tab.redraw and self.pos_tab.plot_mode == "Absolute value":
                self.pos_values[i, :slice_limit] = self.pos_values[i, :slice_limit] + \
                                                        self.settings.dest_pos[i]
            elif self.pos_tab.redraw:
                self.pos_values[i, :slice_limit] = self.pos_values[i, :slice_limit] - \
                                                        self.settings.dest_pos[i]
        self.pos_tab.redraw = False
        for i in range(4):
            if self.rot_q_tab.redraw and self.rot_q_tab.plot_mode == "Absolute value":
                self.rot_q_values[i, :slice_limit] = self.rot_q_values[i, :slice_limit] + \
                                                          self.settings.dest_q[i]
            elif self.rot_q_tab.redraw:
                self.rot_q_values[i, :slice_limit] = self.rot_q_values[i, :slice_limit] - \
                                                          self.settings.dest_q[i]
        self.rot_q_tab.redraw = False
        self.current_dot += 1
        self._update_plot()
        return

    def plot(self):
        if self.current_dot < self.num_of_dots:
            self._plot_part()
            return

        self.t[:-1] = self.t[1:]
        self.t[-1] = self.copter_state.t
        if self.pos_tab.plot_enabled:
            if self.pos_tab.plot_mode == "Absolute value" and not self.pos_tab.redraw:
                self.pos_values = array_shift(self.pos_values, self.copter_state.fuselage_state.pos_v)
            else:
                pos_v = py.ndarray([3])
                for i in range(3):
                    pos_v[i] = self.copter_state.fuselage_state.pos_v[i] - self.settings.dest_pos[i]
                self.pos_values = array_shift(self.pos_values, pos_v)
        if self.rot_q_tab.plot_enabled:
            if self.rot_q_tab.plot_mode == "Absolute value" and not self.rot_q_tab.redraw:
                self.rot_q_values = array_shift(self.rot_q_values, self.copter_state.fuselage_state.rot_q)
            else:
                rot_q = py.ndarray([4])
                for i in range(4):
                    rot_q[i] = self.copter_state.fuselage_state.rot_q[i] - self.settings.dest_q[i]
                self.rot_q_values = array_shift(self.rot_q_values, rot_q)
        if self.vel_tab.plot_enabled:
            self.vel_values = array_shift(self.vel_values, self.copter_state.fuselage_state.velocity_v)
        if self.ang_vel_tab.plot_enabled:
            self.ang_vel_values = array_shift(self.ang_vel_values, self.copter_state.fuselage_state.angular_vel_v)
        if self.acel_tab.plot_enabled:
            self.acel_values = array_shift(self.acel_values, self.copter_state.fuselage_state.acel_v)
        if self.ang_acel_tab.plot_enabled:
            self.ang_acel_values = array_shift(self.ang_acel_values, self.copter_state.fuselage_state.angular_acel_v)
        current_pwm = py.ndarray([self.copter.num_of_engines])
        current_pow = py.ndarray([self.copter.num_of_engines])
        engines_ang_v_values = py.ndarray([self.copter.num_of_engines])
        for i in range(self.copter.num_of_engines):
            current_pwm[i] = self.copter_state.engines_state[i].current_pwm
            current_pow[i] = self.copter_state.engines_state[i].current_pow
            engines_ang_v_values[i] = self.copter_state.engines_state[i].angular_vel_v[2]
        if self.engine_pwm_tab.plot_enabled:
            self.engine_pwm_values = array_shift(self.engine_pwm_values, current_pwm)
        if self.engine_pow_tab.plot_enabled:
            self.engine_pow_values = array_shift(self.engine_pow_values, current_pow)
        if self.engine_ang_v_tab.plot_enabled:
            self.engine_ang_v_values = array_shift(self.engine_ang_v_values, engines_ang_v_values)
        '''for view_box in self.view_boxes:
            view_box.state['limits']['xLimits'][0] = self.t[0]
            view_box.state['limits']['xLimits'][1] = self.t[-1] + 10'''
        for i in range(3):
            if self.pos_tab.redraw and self.pos_tab.plot_mode == "Absolute value":
                self.pos_values[i] = self.pos_values[i] + \
                                     self.settings.dest_pos[i]
            elif self.pos_tab.redraw:
                self.pos_values[i] = self.pos_values[i] - \
                                     self.settings.dest_pos[i]
        self.pos_tab.redraw = False
        for i in range(4):
            if self.rot_q_tab.redraw and self.rot_q_tab.plot_mode == "Absolute value":
                self.rot_q_values[i] = self.rot_q_values[i] + \
                                       self.settings.dest_q[i]
            elif self.rot_q_tab.redraw:
                self.rot_q_values[i] = self.rot_q_values[i] - \
                                       self.settings.dest_q[i]
        self.rot_q_tab.redraw = False
        self._update_plot()
        return

    def _update_plot(self):
        if self.current_dot < self.num_of_dots:
            self._update_plot_part()
            return
        if self.pos_tab.isVisible():
            for i in range(3):
                self.pos_curves[i].setData(self.t, self.pos_values[i])
                self.pos_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        if self.rot_q_tab.isVisible():
            for i in range(4):
                self.rot_q_curves[i].setData(self.t, self.rot_q_values[i])
                self.rot_q_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        if self.vel_tab.isVisible():
            for i in range(3):
                self.vel_curves[i].setData(self.t, self.vel_values[i])
                self.vel_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        if self.ang_vel_tab.isVisible():
            for i in range(3):
                self.ang_vel_curves[i].setData(self.t, self.ang_vel_values[i])
                self.ang_vel_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        if self.acel_tab.isVisible():
            for i in range(3):
                self.acel_curves[i].setData(self.t, self.acel_values[i])
                self.acel_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        if self.ang_acel_tab.isVisible():
            for i in range(3):
                self.ang_acel_curves[i].setData(self.t, self.ang_acel_values[i])
                self.ang_acel_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        if self.engine_pwm_tab.isVisible():
            for i in range(self.copter.num_of_engines):
                self.engine_pwm_curves[i].setData(self.t, self.engine_pwm_values[i])
                self.engine_pwm_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        if self.engine_pow_tab.isVisible():
            for i in range(self.copter.num_of_engines):
                self.engine_pow_curves[i].setData(self.t, self.engine_pow_values[i])
                self.engine_pow_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        if self.engine_ang_v_tab.isVisible():
            for i in range(self.copter.num_of_engines):
                self.engine_ang_v_curves[i].setData(self.t, self.engine_ang_v_values[i])
                self.engine_ang_v_curves[i].setDownsampling(ds=1, auto=True, method='subsample')
        return

    def _update_plot_part(self):
        slice_limit = self.current_dot
        if self.pos_tab.isVisible():
            for i in range(3):
                self.pos_curves[i].setData(
                    self.t[:slice_limit],
                    self.pos_values[i, :slice_limit]
                )
        if self.vel_tab.isVisible():
            for i in range(3):
                self.vel_curves[i].setData(
                    self.t[:slice_limit],
                    self.vel_values[i, :slice_limit]
                )
        if self.ang_vel_tab.isVisible():
            for i in range(3):
                self.ang_vel_curves[i].setData(
                    self.t[:slice_limit],
                    self.ang_vel_values[i, :slice_limit]
                )
        if self.acel_tab.isVisible():
            for i in range(3):
                self.acel_curves[i].setData(
                    self.t[:slice_limit],
                    self.acel_values[i, :slice_limit]
                )
        if self.ang_acel_tab.isVisible():
            for i in range(3):
                self.ang_acel_curves[i].setData(
                    self.t[:slice_limit],
                    self.ang_acel_values[i, :slice_limit]
                )
        if self.rot_q_tab.isVisible():
            for i in range(4):
                self.rot_q_curves[i].setData(
                    self.t[:slice_limit],
                    self.rot_q_values[i, :slice_limit]
                )
        if self.engine_pwm_tab.isVisible():
            for i in range(self.copter.num_of_engines):
                self.engine_pwm_curves[i].setData(
                    self.t[:slice_limit],
                    self.engine_pwm_values[i, :slice_limit]
                )
        if self.engine_pow_tab.isVisible():
            for i in range(self.copter.num_of_engines):
                self.engine_pow_curves[i].setData(
                    self.t[:slice_limit],
                    self.engine_pow_values[i, :slice_limit]
                )
        if self.engine_ang_v_tab.isVisible():
            for i in range(self.copter.num_of_engines):
                self.engine_ang_v_curves[i].setData(
                    self.t[:slice_limit],
                    self.engine_ang_v_values[i, :slice_limit]
                )
        return
