from PyQt5.QtWidgets import QTabWidget, QWidget, QToolBar, \
    QAction, QVBoxLayout, QSizePolicy, \
    QLabel, QGridLayout, QScrollArea, QFileDialog
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize, pyqtSignal
from CopterEmulator.simulation import SimulationServer
from . import main_window, log_window
from .plot_widget import PlotWidget
from .settings import Settings
from .copter3d_widget import Copter3DWidget
import CopterEmulator.physicalmodel as model
import pyqtgraph as pg
import CopterEmulator.graphics as graphics
import os
import multiprocessing


class GraphicsWidget(QWidget):
    start_act = QAction
    pause_act = QAction
    stop_act = QAction
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()
    settings = Settings
    copter = model.Copter

    def __init__(self, window):
        super(GraphicsWidget, self).__init__(window)
        self.settings = window.settings
        self.copter = window.copter
        self.simulation_running = False
        self.simulation_paused = False
        self.server = None
        self.plot_pen = pg.mkPen('k', width=4)
        self._init_ui()
        return

    def _init_ui(self):
        widget_box = QVBoxLayout(self)
        graphics_tbr = QTabWidget(self)
        view3d_tab = Copter3DWidget(self)
        view3d_tab.setObjectName("view3d_tab")
        graphics_tbr.addTab(view3d_tab, "3D view")

        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('background', 'w')

        pos_tab = PlotWidget(graphics_tbr)
        pos_tab.setObjectName("pos_tab")
        name_lbl = pos_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Position plot")
        name_lbl.show()
        self._init_plot(pos_tab)
        graphics_tbr.addTab(pos_tab, "Position plots")

        rot_q_tab = PlotWidget(graphics_tbr)
        rot_q_tab.setObjectName("rot_q_tab")
        name_lbl = rot_q_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Angular position plot")
        name_lbl.show()
        self._init_plot(rot_q_tab)
        graphics_tbr.addTab(rot_q_tab, "Angular position plots")

        vel_tab = PlotWidget(graphics_tbr)
        vel_tab.setObjectName("vel_tab")
        name_lbl = vel_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Velocity plot")
        name_lbl.show()
        plot_mode_w = vel_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_plot(vel_tab)
        graphics_tbr.addTab(vel_tab, "Velocity plots")

        ang_vel_tab = PlotWidget(graphics_tbr)
        ang_vel_tab.setObjectName("ang_vel_tab")
        name_lbl = ang_vel_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Angular velocity plot")
        name_lbl.show()
        plot_mode_w = ang_vel_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_plot(ang_vel_tab)
        graphics_tbr.addTab(ang_vel_tab, "Angular velocity plots")

        acel_tab = PlotWidget(graphics_tbr)
        acel_tab.setObjectName("acel_tab")
        name_lbl = acel_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Acceleration plot")
        name_lbl.show()
        plot_mode_w = acel_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_plot(acel_tab)
        graphics_tbr.addTab(acel_tab, "Acceleration plots")

        ang_acel_tab = PlotWidget(graphics_tbr)
        ang_acel_tab.setObjectName("ang_acel_tab")
        name_lbl = ang_acel_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Angular acceleration plot")
        name_lbl.show()
        plot_mode_w = ang_acel_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_plot(ang_acel_tab)
        graphics_tbr.addTab(ang_acel_tab, "Angular acceleration plots")

        engine_pwm_tab = PlotWidget(graphics_tbr)
        engine_pwm_tab.setObjectName("engine_pwm_tab")
        name_lbl = engine_pwm_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Engines PWM plot")
        name_lbl.show()
        plot_mode_w = engine_pwm_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_engines_plot(engine_pwm_tab)
        graphics_tbr.addTab(engine_pwm_tab, "Engines PWM plots")

        engine_pow_tab = PlotWidget(graphics_tbr)
        engine_pow_tab.setObjectName("engine_pow_tab")
        name_lbl = engine_pow_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Engines power plot")
        name_lbl.show()
        plot_mode_w = engine_pow_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_engines_plot(engine_pow_tab)
        graphics_tbr.addTab(engine_pow_tab, "Engines power plots")

        engine_ang_v_tab = PlotWidget(graphics_tbr)
        engine_ang_v_tab.setObjectName("engine_ang_v_tab")
        name_lbl = engine_ang_v_tab.findChild(QLabel, "name_lbl")
        name_lbl.setText("Engines angular velocity plot")
        name_lbl.show()
        plot_mode_w = engine_ang_v_tab.findChild(QWidget, "plot_mode_w")
        plot_mode_w.hide()
        self._init_engines_plot(engine_ang_v_tab)
        graphics_tbr.addTab(engine_ang_v_tab, "Engines angular velocity plots")

        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        control_tlbr = QToolBar(self)
        control_tlbr.setMovable(False)
        tblr_font = QFont("Times", 16)
        control_tlbr.setFont(tblr_font)

        open_log_act = QAction("Load log file", self)
        open_log_act.setObjectName("open_log_act")
        open_log_act.setStatusTip("Draw plots from log file")
        open_log_act.triggered.connect(self._open_log)
        spacer_w = QWidget()
        spacer_w.setFixedSize(150, 50)
        control_tlbr.addWidget(spacer_w)
        control_tlbr.addWidget(left_spacer)

        self.start_act = QAction(QIcon(main_window.__icon_dir__ + 'startIcon.png'),
                                 "Start simulation", self)
        self.start_act.setObjectName("start_act")
        self.start_act.setStatusTip("Start simulation")
        self.start_act.triggered.connect(self._start_simulation)
        control_tlbr.addAction(self.start_act)
        control_tlbr.addSeparator()

        self.pause_act = QAction(QIcon(main_window.__icon_dir__ + 'pauseIcon.png'),
                                 "Pause simulation", self)
        self.pause_act.setObjectName("pause_act")
        self.pause_act.setStatusTip("Pause simulation")
        self.pause_act.triggered.connect(self._pause_simulation)
        self.pause_act.setEnabled(False)
        control_tlbr.addAction(self.pause_act)
        control_tlbr.addSeparator()

        self.stop_act = QAction(QIcon(main_window.__icon_dir__ + 'stopIcon.png'),
                                "Stop simulation", self)
        self.stop_act.setObjectName("stop_act")
        self.stop_act.setStatusTip("Stop simulation")
        self.stop_act.triggered.connect(self.stop_simulation)
        self.stop_act.setEnabled(False)
        control_tlbr.addAction(self.stop_act)
        control_tlbr.addWidget(right_spacer)

        control_tlbr.addSeparator()
        control_tlbr.addAction(open_log_act)
        open_log_w = control_tlbr.widgetForAction(open_log_act)
        open_log_w.setFixedSize(150, 50)

        tb_iconsize = QSize(50, 50)
        control_tlbr.setIconSize(tb_iconsize)

        widget_box.addWidget(graphics_tbr)
        widget_box.addWidget(control_tlbr)
        self.setLayout(widget_box)
        return

    def _init_plot(self, tab):
        tab_name = tab.objectName()
        if tab_name == "rot_q_tab":
            w_plot = pg.PlotWidget(parent=tab.plot_w)
            # w_plot.setLimits(xMin=0, xMax=610)
            # w_plot.setXRange(0, 610)
            w_plot.setMouseEnabled(x=False, y=False)
            w_axis = w_plot.getPlotItem()
            w_axis.setLabel("left", text="W")
            w_axis.setLabel("bottom", text="t", units="s")
            w_axis.showGrid(x=True, y=True)
            w_axis.plot([0], [0], pen=self.plot_pen)
            w_axis.curves[0].setData([], [])

        x_plot = pg.PlotWidget(parent=tab.plot_w)
        # x_plot.setLimits(xMin=0, xMax=610)
        # x_plot.setXRange(0, 550)
        x_plot.setMouseEnabled(x=False, y=False)
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
        # y_plot.setLimits(xMin=0, xMax=610)
        # y_plot.setXRange(0, 610)
        y_plot.setMouseEnabled(x=False, y=False)
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
        # z_plot.setLimits(xMin=0, xMax=610)
        # z_plot.setXRange(0, 610)
        z_plot.setMouseEnabled(x=False, y=False)
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
        for i in range(self.copter.num_of_engines):
            engine_plot = pg.PlotWidget(parent=tab.plot_w)
            # engine_plot.setLimits(xMin=0, xMax=610)
            # engine_plot.setXRange(0, 610)
            engine_plot.setMouseEnabled(x=False, y=False)
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

    def _open_log(self):
        dialog = QFileDialog()
        dialog.setNameFilters(["LOG files (*.log)", "All Files (*)"])
        dialog.selectNameFilter("LOG files (*.log)")
        dialog.setDirectory(os.path.dirname(main_window.__logs_dir__))
        _open = dialog.exec_()
        if _open:
            log_file = dialog.selectedFiles()
            log_name = str(log_file[0])
            proc = multiprocessing.Process(target=log_window.LogWindow.new_window, args=(log_name,))
            proc.start()
        return

    def _start_simulation(self):
        self.simulation_running = True
        self.start_act.setEnabled(False)
        self.pause_act.setEnabled(True)
        self.stop_act.setEnabled(True)
        if self.simulation_paused:
            self.server.resume_simulation()
            self.simulation_paused = False
            return
        open_log_act = self.findChild(QAction, "open_log_act")
        open_log_act.setEnabled(False)
        self.simulation_started.emit()
        plotter = graphics.Plotter(self)
        widget_3d = self.findChildren(Copter3DWidget)[0]
        self.server = SimulationServer(self.copter, self.settings, widget_3d, plotter, self)
        self.server.start_simulation()
        return

    def _pause_simulation(self):
        self.pause_act.setEnabled(False)
        self.start_act.setEnabled(True)
        self.simulation_paused = True
        self.server.pause_simulation()
        return

    def stop_simulation(self):
        self.simulation_stopped.emit()
        self.stop_act.setEnabled(False)
        self.start_act.setEnabled(True)
        self.pause_act.setEnabled(False)
        open_log_act = self.findChild(QAction, "open_log_act")
        open_log_act.setEnabled(True)
        self.simulation_running = False
        self.simulation_paused = False
        self.server.stop_simulation()
        self.server = None
        return
