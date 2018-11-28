from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QTabWidget, QWidget, \
                            QVBoxLayout, QLabel, QGridLayout, QScrollArea, \
                            QApplication, QSizePolicy, QAction, QToolBar
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from CopterEmulator.logger import Logger, CopterState
from pyquaternion import Quaternion
import CopterEmulator.gui as gui
from .plot_widget import PlotWidget
import os
import pyqtgraph as pg
import numpy as py
import sys
import time
import threading

__icon_dir__ = os.path.dirname(os.path.realpath(__file__)) + \
                   os.path.sep + 'icons' + os.path.sep


class LogWindow(QMainWindow):
    copter_name = str
    num_of_engines = int
    dest_pos = py.array
    dest_q = Quaternion

    def __init__(self, log_name):
        super(LogWindow, self).__init__()
        self.video_paused = False
        self.video_running = False
        self.stop_event = threading.Event()
        self.running_event = threading.Event()
        self.video_thread = None
        self.plot_pen = pg.mkPen('k', width=4)
        self._init_size()
        self._center_window()
        self.setWindowIcon(QIcon(__icon_dir__ + 'icon.png'))
        widget_tmp = QWidget(self)
        self.setCentralWidget(widget_tmp)
        self.setWindowTitle("Loading .log file...")
        self.show()
        self.copter_name = None
        self.num_of_engines = None
        self.copter = None
        self.dest_pos = None
        self.dest_q = None
        self.settings = gui.Settings()
        self.log_data = Logger.load_log(log_name, self)
        self.start_index = 0
        self.end_index = self.log_data.shape[1] - 1
        self.settings.dest_pos = self.dest_pos
        self.settings.dest_q = self.dest_q
        self.current_state = CopterState(self.copter)
        self.setWindowTitle("Initialize ui...")
        self._init_ui()
        self.view_boxes = []
        plot_widgets = self.findChildren(pg.PlotWidget)
        for plot_widget in plot_widgets:
            plot_item = plot_widget.getPlotItem()
            self.view_boxes.append(plot_item.getViewBox())
        self.setWindowTitle("Plotting data...")
        self._plot()
        self.setWindowTitle("'{0}' copter log".format(self.copter_name))
        status_bar = self.statusBar()
        file_lbl = QLabel(status_bar)
        file_lbl.setText(log_name)
        status_bar.addPermanentWidget(file_lbl, 1)
        return

    def _init_ui(self):
        main_widget = QWidget(self)
        widget_box = QVBoxLayout(main_widget)
        graphics_tbr = QTabWidget(main_widget)

        copter_lbl = QLabel(main_widget)
        copter_lbl.setText(self.copter_name)
        copter_lbl.setObjectName("copter_lbl")
        name_font = QFont("Times", 20, QFont.Bold)
        copter_lbl.setFont(name_font)
        copter_lbl.setAlignment(Qt.AlignCenter)

        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('background', 'w')

        view3d_tab = gui.Copter3DWidget(self)
        view3d_tab.setObjectName("view3d_tab")
        graphics_tbr.addTab(view3d_tab, "3D view")

        pos_tab = PlotWidget(graphics_tbr)
        pos_tab.setObjectName("pos_tab")
        pos_tab.plot_mode_changed.connect(self._change_pos_mode)
        name_lbl = pos_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Position plot")
        name_lbl.show()
        plot_enabled_w = pos_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        self._init_plot(pos_tab)
        self.pos_curves = self._init_curves(pos_tab)
        graphics_tbr.addTab(pos_tab, "Position plots")

        rot_q_tab = PlotWidget(graphics_tbr)
        rot_q_tab.setObjectName("rot_q_tab")
        rot_q_tab.plot_mode_changed.connect(self._change_rot_mode)
        name_lbl = rot_q_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Angular position plot")
        name_lbl.show()
        plot_enabled_w = rot_q_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        self._init_plot(rot_q_tab)
        self.rot_q_curves = self._init_curves(rot_q_tab)
        graphics_tbr.addTab(rot_q_tab, "Angular position plots")

        vel_tab = PlotWidget(graphics_tbr)
        vel_tab.setObjectName("vel_tab")
        name_lbl = vel_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Velocity plot")
        name_lbl.show()
        plot_enabled_w = vel_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        plot_mode_w = vel_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_plot(vel_tab)
        self.vel_curves = self._init_curves(vel_tab)
        graphics_tbr.addTab(vel_tab, "Velocity plots")

        ang_vel_tab = PlotWidget(graphics_tbr)
        ang_vel_tab.setObjectName("ang_vel_tab")
        name_lbl = ang_vel_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Angular velocity plot")
        name_lbl.show()
        plot_enabled_w = ang_vel_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        plot_mode_w = ang_vel_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_plot(ang_vel_tab)
        self.ang_vel_curves = self._init_curves(ang_vel_tab)
        graphics_tbr.addTab(ang_vel_tab, "Angular velocity plots")

        acel_tab = PlotWidget(graphics_tbr)
        acel_tab.setObjectName("acel_tab")
        name_lbl = acel_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Acceleration plot")
        name_lbl.show()
        plot_enabled_w = acel_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        plot_mode_w = acel_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_plot(acel_tab)
        self.acel_curves = self._init_curves(acel_tab)
        graphics_tbr.addTab(acel_tab, "Acceleration plots")

        ang_acel_tab = PlotWidget(graphics_tbr)
        ang_acel_tab.setObjectName("ang_acel_tab")
        name_lbl = ang_acel_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Angular acceleration plot")
        name_lbl.show()
        plot_enabled_w = ang_acel_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        plot_mode_w = ang_acel_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_plot(ang_acel_tab)
        self.ang_acel_curves = self._init_curves(ang_acel_tab)
        graphics_tbr.addTab(ang_acel_tab, "Angular acceleration plots")

        engine_pwm_tab = PlotWidget(graphics_tbr)
        engine_pwm_tab.setObjectName("engine_pwm_tab")
        name_lbl = engine_pwm_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Engines PWM plot")
        name_lbl.show()
        plot_enabled_w = engine_pwm_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        plot_mode_w = engine_pwm_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_engines_plot(engine_pwm_tab)
        self.pwm_curves = self._init_curves(engine_pwm_tab)
        graphics_tbr.addTab(engine_pwm_tab, "Engines PWM plots")

        engine_pow_tab = PlotWidget(graphics_tbr)
        engine_pow_tab.setObjectName("engine_pow_tab")
        name_lbl = engine_pow_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Engines power plot")
        name_lbl.show()
        plot_enabled_w = engine_pow_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        plot_mode_w = engine_pow_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_engines_plot(engine_pow_tab)
        self.pow_curves = self._init_curves(engine_pow_tab)
        graphics_tbr.addTab(engine_pow_tab, "Engines power plots")

        engine_ang_v_tab = PlotWidget(graphics_tbr)
        engine_ang_v_tab.setObjectName("engine_ang_v_tab")
        name_lbl = engine_ang_v_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Engines angular velocity plot")
        name_lbl.show()
        plot_enabled_w = engine_ang_v_tab.findChild(QWidget, "plot_enabled_w")
        plot_enabled_w.hide()
        plot_mode_w = engine_ang_v_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_engines_plot(engine_ang_v_tab)
        self.eng_ang_v_curves = self._init_curves(engine_ang_v_tab)
        graphics_tbr.addTab(engine_ang_v_tab, "Engines angular velocity plots")

        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        control_tlbr = QToolBar(self)
        control_tlbr.setMovable(False)
        control_tlbr.addWidget(left_spacer)

        self.start_act = QAction(QIcon(__icon_dir__ + 'startIcon.png'),
                                 "Start simulation", self)
        self.start_act.setObjectName("start_act")
        self.start_act.setStatusTip("Start simulation")
        self.start_act.triggered.connect(self._start_video)
        control_tlbr.addAction(self.start_act)
        control_tlbr.addSeparator()

        self.pause_act = QAction(QIcon(__icon_dir__ + 'pauseIcon.png'),
                                 "Pause simulation", self)
        self.pause_act.setObjectName("pause_act")
        self.pause_act.setStatusTip("Pause simulation")
        self.pause_act.triggered.connect(self._pause_video)
        self.pause_act.setEnabled(False)
        control_tlbr.addAction(self.pause_act)
        control_tlbr.addSeparator()

        self.stop_act = QAction(QIcon(__icon_dir__ + 'stopIcon.png'),
                                "Stop simulation", self)
        self.stop_act.setObjectName("stop_act")
        self.stop_act.setStatusTip("Stop simulation")
        self.stop_act.triggered.connect(self.stop_video)
        self.stop_act.setEnabled(False)
        control_tlbr.addAction(self.stop_act)
        control_tlbr.addWidget(right_spacer)

        tb_iconsize = QSize(50, 50)
        control_tlbr.setIconSize(tb_iconsize)

        slider = gui.QRangeSlider()
        slider.setObjectName('slider')
        slider.setFixedHeight(25)
        slider.setMin(int(self.log_data[0, 0]))
        slider.setMax(int(self.log_data[0, -1]) + 1)
        slider.setEnd(int(self.log_data[0, -1]) + 1)
        slider.setStart(int(self.log_data[0, 0]))
        slider.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #666);')
        slider.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        slider.setStyleSheet("""
        QRangeSlider > QSplitter::handle {
            background: #000000;
        }
        QRangeSlider > QSplitter::handle:vertical {
            height: 4px;
        }
        QRangeSlider > QSplitter::handle:pressed {
            background: #7D7D7D;
        }
        """)
        slider.tail.setTextColor(210)
        slider.handle.setTextColor(0)
        slider.head.setTextColor(210)
        slider.startValueChanged.connect(self._change_start_index)
        slider.endValueChanged.connect(self._change_end_index)

        widget_box.addWidget(copter_lbl)
        widget_box.addWidget(graphics_tbr)
        widget_box.addWidget(slider)
        widget_box.addWidget(control_tlbr)
        main_widget.setLayout(widget_box)

        self.setCentralWidget(main_widget)
        return

    def _init_size(self):
        desk_width = QDesktopWidget().availableGeometry().width()
        desk_height = QDesktopWidget().availableGeometry().height()
        window_width = desk_width // 2.0
        window_height = desk_height // 2.0
        self.resize(window_width, window_height)
        return

    def _center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        return

    def _init_plot(self, tab):
        tab_name = tab.objectName()
        if tab_name == "rot_q_tab":
            w_plot = pg.PlotWidget(parent=tab.plot_w)
            w_axis = w_plot.getPlotItem()
            w_axis.setLabel("left", text="W")
            w_axis.setLabel("bottom", text="t", units="s")
            w_axis.showGrid(x=True, y=True)
            w_axis.plot([0], [0], pen=self.plot_pen)
            w_axis.curves[0].setData([], [])

        x_plot = pg.PlotWidget(parent=tab.plot_w)
        x_axis = x_plot.getPlotItem()
        if tab_name == "rot_q_tab":
            x_axis.setLabel("left", text="X")
        elif tab_name == "pos_tab":
            x_axis.setLabel("left", text="X", units="m")
        elif tab_name == "vel_tab":
            x_axis.setLabel("left", text="X", units="m/s")
        elif tab_name == "ang_vel_tab":
            x_axis.setLabel("left", text="X", units="rad/s")
        elif tab_name == "acel_tab":
            x_axis.setLabel("left", text="X", units="m/s^2")
        elif tab_name == "ang_acel_tab":
            x_axis.setLabel("left", text="X", units="rad/s^2")
        x_axis.setLabel("bottom", text="t", units="s")
        x_axis.showGrid(x=True, y=True)
        x_axis.plot([0], [0], pen=self.plot_pen)
        x_axis.curves[0].setData([], [])
        y_plot = pg.PlotWidget(parent=tab.plot_w)
        y_axis = y_plot.getPlotItem()
        if tab_name == "rot_q_tab":
            y_axis.setLabel("left", text="Y")
        elif tab_name == "pos_tab":
            y_axis.setLabel("left", text="Y", units="m")
        elif tab_name == "vel_tab":
            y_axis.setLabel("left", text="Y", units="m/s")
        elif tab_name == "ang_vel_tab":
            y_axis.setLabel("left", text="Y", units="rad/s")
        elif tab_name == "acel_tab":
            y_axis.setLabel("left", text="Y", units="m/s^2")
        elif tab_name == "ang_acel_tab":
            y_axis.setLabel("left", text="Y", units="rad/s^2")
        y_axis.setLabel("bottom", text="t", units="s")
        y_axis.showGrid(x=True, y=True)
        y_axis.plot([0], [0], pen=self.plot_pen)
        y_axis.curves[0].setData([], [])
        z_plot = pg.PlotWidget(parent=tab.plot_w)
        z_axis = z_plot.getPlotItem()
        if tab_name == "rot_q_tab":
            z_axis.setLabel("left", text="Z")
        elif tab_name == "pos_tab":
            z_axis.setLabel("left", text="Z", units="m")
        elif tab_name == "vel_tab":
            z_axis.setLabel("left", text="Z", units="m/s")
        elif tab_name == "ang_vel_tab":
            z_axis.setLabel("left", text="Z", units="rad/s")
        elif tab_name == "acel_tab":
            z_axis.setLabel("left", text="Z", units="m/s^2")
        elif tab_name == "ang_acel_tab":
            z_axis.setLabel("left", text="Z", units="rad/s^2")
        z_axis.setLabel("bottom", text="t", units="s")
        z_axis.showGrid(x=True, y=True)
        z_axis.plot([0], [0], pen=self.plot_pen)
        z_axis.curves[0].setData([], [])

        if tab_name == "rot_q_tab":
            plot_grid = QGridLayout(tab.plot_w)
            plot_grid.addWidget(w_plot, 0, 0)
            plot_grid.addWidget(x_plot, 0, 1)
            plot_grid.addWidget(y_plot, 1, 0)
            plot_grid.addWidget(z_plot, 1, 1)
        else:
            plot_box = QVBoxLayout(tab.plot_w)
            plot_box.addWidget(x_plot)
            plot_box.addWidget(y_plot)
            plot_box.addWidget(z_plot)

        scroll_w = tab.findChild(QScrollArea, "scroll_w")
        scroll_w.setWidget(tab.plot_w)
        if tab_name == "rot_q_tab":
            tab.plot_w.setLayout(plot_grid)
            tab.plot_w.setMinimumHeight(2 * 256)
        else:
            tab.plot_w.setLayout(plot_box)
            tab.plot_w.setMinimumHeight(3 * 256)
        return

    def _init_engines_plot(self, tab):
        tab_name = tab.objectName()
        plot_grid = QGridLayout(tab.plot_w)
        for i in range(self.num_of_engines):
            engine_plot = pg.PlotWidget(parent=tab.plot_w)
            engine_plot.setLimits(xMin=0, xMax=610)
            engine_axis = engine_plot.getPlotItem()
            if tab_name == "engine_pwm_tab":
                engine_axis.setLabel("left", text="PWM")
            elif tab_name == "engine_pow_tab":
                engine_axis.setLabel("left", text="N", units="Wt")
            elif tab_name == "engine_ang_v_tab":
                engine_axis.setLabel("left", text="Omega", units="rad/s")
            engine_axis.setLabel("bottom", text="t", units="s")
            engine_axis.setTitle("Engine {}".format(i + 1))
            engine_axis.showGrid(x=True, y=True)
            engine_axis.plot([0], [0], pen=self.plot_pen)
            engine_axis.curves[0].setData([], [])
            plot_grid.addWidget(engine_plot, i // 2, i % 2)
        scroll_w = tab.findChild(QScrollArea, "scroll_w")
        scroll_w.setWidget(tab.plot_w)
        tab.plot_w.setLayout(plot_grid)
        tab.plot_w.setMinimumHeight(plot_grid.rowCount() * 256)
        return

    def _plot(self):
        num_of_states = self.log_data.shape[1]

        self.t = py.ndarray([num_of_states])
        self.pos_v = py.ndarray([3, num_of_states])
        velocity_v = py.ndarray([3, num_of_states])
        acel_v = py.ndarray([3, num_of_states])
        self.rot_q = py.ndarray([4, num_of_states])
        angular_vel_v = py.ndarray([3, num_of_states])
        angular_acel_v = py.ndarray([3, num_of_states])
        engine_rot_q0 = py.ndarray([self.num_of_engines, num_of_states])
        engine_rot_q3 = py.ndarray([self.num_of_engines, num_of_states])
        current_pwm = py.ndarray([self.num_of_engines, num_of_states])
        current_pow = py.ndarray([self.num_of_engines, num_of_states])
        engine_angular_vel_v = py.ndarray([self.num_of_engines, num_of_states])
        for i in range(num_of_states):
            self.t[i] = self.log_data[0, i]
            self.pos_v[:, i] = py.array(self.log_data[1, i]).transpose()
            velocity_v[:, i] = py.array(self.log_data[2, i]).transpose()
            acel_v[:, i] = py.array(self.log_data[3, i]).transpose()
            self.rot_q[:, i] = py.array(self.log_data[4, i])
            angular_vel_v[:, i] = py.array(self.log_data[5, i]).transpose()
            angular_acel_v[:, i] = py.array(self.log_data[6, i]).transpose()
            for j in range(self.num_of_engines):
                engine_rot_q0[j, i] = self.log_data[7 + j, i][0]
                engine_rot_q3[j, i] = self.log_data[7 + j, i][1]
                current_pwm[j, i] = self.log_data[7 + j, i][2]
                current_pow[j, i] = self.log_data[7 + j, i][3]
                engine_angular_vel_v[j, i] = self.log_data[7 + j, i][4]
        for view_box in self.view_boxes:
            view_box.state['limits']['xLimits'][0] = self.t[0]
            view_box.state['limits']['xLimits'][1] = self.t[-1] + 10
        for i in range(3):
            self.pos_curves[i].setData(self.t, self.pos_v[i])
            self.vel_curves[i].setData(self.t, velocity_v[i])
            self.ang_vel_curves[i].setData(self.t, angular_vel_v[i])
            self.acel_curves[i].setData(self.t, acel_v[i])
            self.ang_acel_curves[i].setData(self.t, angular_acel_v[i])
        for i in range(4):
            self.rot_q_curves[i].setData(self.t, self.rot_q[i])
        for i in range(self.num_of_engines):
            self.pwm_curves[i].setData(self.t, current_pwm[i])
            self.pow_curves[i].setData(self.t, current_pow[i])
            self.eng_ang_v_curves[i].setData(self.t, engine_angular_vel_v[i])
        self.settings.start_state.t = self.t[0]
        self.settings.start_state.fuselage_state.pos_v = self.pos_v[:, 0]
        self.settings.start_state.fuselage_state.rot_q = self.rot_q[:, 0]
        self.settings.start_state.fuselage_state.velocity_v = velocity_v[:, 0]
        self.settings.start_state.fuselage_state.angular_vel_v = angular_vel_v[:, 0]
        self.settings.start_state.fuselage_state.acel_v = acel_v[:, 0]
        for i in range(self.num_of_engines):
            self.settings.start_state.engines_state[i].current_pwm = current_pwm[i, 0]
            self.settings.start_state.engines_state[i].rot_q[0] = engine_rot_q0[i, 0]
            self.settings.start_state.engines_state[i].rot_q[3] = engine_rot_q3[i, 0]
        return

    @staticmethod
    def _init_curves(tab):
        plots = tab.findChildren(pg.PlotWidget)
        curves = list()
        for plot in plots:
            plot_item = plot.getPlotItem()
            curves.append(plot_item.curves[0])
        return curves

    @staticmethod
    def new_window(log_name):
        app = QApplication(sys.argv)
        ex = LogWindow(log_name)
        app.exec_()
        return

    def _change_pos_mode(self):
        pos_tab = self.findChild(PlotWidget, "pos_tab")
        if pos_tab.plot_mode == 'Absolute value':
            for j in range(3):
                self.pos_curves[j].setData(self.t, self.pos_v[j])
        else:
            for j in range(3):
                self.pos_curves[j].setData(self.t, self.pos_v[j] - self.dest_pos[j])
        return

    def _change_rot_mode(self):
        rot_q_tab = self.findChild(PlotWidget, "rot_q_tab")
        if rot_q_tab.plot_mode == 'Absolute value':
            for j in range(4):
                self.rot_q_curves[j].setData(self.t, self.rot_q[j])
        else:
            for j in range(4):
                self.rot_q_curves[j].setData(self.t, self.rot_q[j] - self.dest_q[j])
        return

    def _start_video(self):
        self.start_act.setEnabled(False)
        self.pause_act.setEnabled(True)
        self.stop_act.setEnabled(True)
        slider = self.findChild(gui.QRangeSlider, 'slider')
        slider.setEnabled(False)
        self.video_running = True
        self.running_event.set()
        if self.video_paused:
            self.video_paused = False
            return
        self.stop_event.clear()
        self.video_thread = threading.Thread(
            target=self._video_thread,
            args=(self, self.running_event, self.stop_event, )
        )
        self.video_thread.start()
        return

    def _pause_video(self):
        self.pause_act.setEnabled(False)
        self.start_act.setEnabled(True)
        self.video_paused = True
        self.running_event.clear()
        return

    def stop_video(self):
        self.stop_act.setEnabled(False)
        self.start_act.setEnabled(True)
        self.pause_act.setEnabled(False)
        slider = self.findChild(gui.QRangeSlider, 'slider')
        slider.setEnabled(True)
        self.video_running = False
        self.video_paused = False
        self.stop_event.set()
        self.running_event.set()
        if not threading.current_thread() == self.video_thread:
            self.video_thread.join()
        self.video_thread = None
        return

    def closeEvent(self, *args, **kwargs):
        if self.video_running:
            self.stop_video()
        copter3d_w = self.findChildren(gui.Copter3DWidget)[0]
        copter3d_w.cleanup_all()
        return

    def _change_start_index(self):
        slider = self.sender()
        start_time = slider.start()
        self.start_index = self._find_index(start_time, 'start')
        self.draw_frame(self.start_index)
        return

    def _change_end_index(self):
        slider = self.sender()
        end_time = slider.end()
        self.end_index = self._find_index(end_time, 'end')
        return

    def _find_index(self, value, mode):
        left_index = 0
        right_index = self.log_data.shape[1] - 1
        if self.t[left_index] >= value and mode == 'start':
            return left_index
        if self.t[right_index] <= value and mode == 'end':
            return right_index
        index_cur = int((left_index + right_index) / 2)
        searching = True
        counter = 0
        while searching:
            if mode == 'start':
                if self.t[index_cur] >= value > self.t[index_cur - 1]:
                    searching = False
                    continue
            elif mode == 'end':
                if self.t[index_cur] <= value < self.t[index_cur + 1]:
                    searching = False
                    continue
            if counter > self.log_data.shape[1]:
                searching = False
                continue
            if self.t[index_cur] <= value:
                left_index = index_cur
            else:
                right_index = index_cur
            index_cur = int(round((left_index + right_index) / 2))
            counter += 1
        return index_cur

    def draw_frame(self, index):
        self.current_state.t = self.log_data[0, index]
        self.current_state.fuselage_state.pos_v = self.log_data[1, index]
        self.current_state.fuselage_state.velocity_v = self.log_data[2, index]
        self.current_state.fuselage_state.acel_v = self.log_data[3, index]
        self.current_state.fuselage_state.rot_q = self.log_data[4, index]
        self.current_state.fuselage_state.angular_vel_v = self.log_data[5, index]
        for i in range(self.num_of_engines):
            self.current_state.engines_state[i].rot_q[0] = self.log_data[7 + i, index][0]
            self.current_state.engines_state[i].rot_q[3] = self.log_data[7 + i, index][1]
            self.current_state.engines_state[i].current_pwm = self.log_data[7 + i, index][2]
        self.current_state.to_array()
        copter3d_w = self.findChildren(gui.Copter3DWidget)[0]
        copter3d_w.state = self.current_state
        copter3d_w.update()
        return

    @staticmethod
    def _video_thread(log_window, running_event, stop_event):
        fps = 60
        frame_time = 1 / fps
        index_cur = log_window.start_index
        while index_cur <= log_window.end_index:
            if not running_event.is_set():
                running_event.wait()
            if stop_event.is_set():
                break
            start_time = time.time()
            log_window.draw_frame(index_cur)
            index_cur += 1
            sleep_time = frame_time - (time.time() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
        log_window.stop_video()
        return
