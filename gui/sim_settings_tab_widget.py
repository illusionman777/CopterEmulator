from PyQt5.QtWidgets import QWidget, QToolBar, QHBoxLayout, QAction
from PyQt5.Qt import Qt, QFont
from PyQt5.QtGui import QColor, QPalette
from .settings import Settings
from .sim_settings_widget import SimSettingsWidget
from .sim_settings_start_widget import SimSettingsStartWidget
from .copter3d_widget import Copter3DWidget

import CopterEmulator.physicalmodel as model


class SimSettingsTabWidget(QWidget):
    main_widget = QWidget
    current_action = QAction
    copter = model.copter
    settings = Settings
    settings_changed = bool

    def __init__(self, window):
        super(SimSettingsTabWidget, self).__init__(window)
        self.copter = window.copter
        self.settings = window.settings
        self.settings_changed = False
        self._init_ui()
        return

    def _init_ui(self):
        color = QColor(255, 255, 255)
        palette = QPalette(color)

        main_box = QHBoxLayout(self)
        settings_tlbr = QToolBar(self)
        settings_tlbr.setOrientation(Qt.Vertical)
        tblr_font = QFont("Times", 14)
        settings_tlbr.setFont(tblr_font)

        simulation_act = QAction("Simulation settings", self)
        simulation_act.setObjectName("simulation_act")
        simulation_act.setCheckable(True)
        simulation_act.setChecked(True)
        simulation_act.triggered.connect(self._show_widget)
        settings_tlbr.addAction(simulation_act)
        simulation_tab = SimSettingsWidget(self)
        simulation_tab.setObjectName("simulation_tab")
        simulation_tab.setPalette(palette)
        simulation_tab.setAutoFillBackground(True)
        simulation_tab.settings_changed.connect(self._settings_changed)
        self.current_action = simulation_act
        self.main_widget = simulation_tab

        copter_act = QAction("Start settings", self)
        copter_act.setObjectName("start_act")
        copter_act.setCheckable(True)
        copter_act.setChecked(False)
        copter_act.triggered.connect(self._show_widget)
        settings_tlbr.addAction(copter_act)
        copter_tab = SimSettingsStartWidget(self)
        copter_tab.setObjectName("start_tab")
        copter_tab.setPalette(palette)
        copter_tab.setAutoFillBackground(True)
        copter_tab.settings_changed.connect(self._settings_changed)
        copter_tab.hide()

        save_act = QAction("Save settings", self)
        save_act.setObjectName("save_act")
        save_act.setEnabled(False)
        save_act.triggered.connect(self._save_settings)
        settings_tlbr.addAction(save_act)

        main_box.addWidget(settings_tlbr)
        main_box.addWidget(simulation_tab)
        main_box.addWidget(copter_tab)
        for action in settings_tlbr.actions():
            widget = settings_tlbr.widgetForAction(action)
            widget.setFixedWidth(200)
        self.setLayout(main_box)
        return

    def _show_widget(self):
        sender = self.sender()
        if not sender.isChecked():
            sender.setChecked(True)
            return
        else:
            self.current_action.setChecked(False)
            self.current_action = sender
            self.main_widget.hide()
            sender_name = sender.objectName()
            if sender_name == "simulation_act":
                widget = self.findChild(SimSettingsWidget, "simulation_tab")
            elif sender_name == "start_act":
                widget = self.findChild(SimSettingsStartWidget, "start_tab")
            widget.show()
            self.main_widget = widget
        return

    def _settings_changed(self):
        if not self.settings_changed:
            self.settings_changed = True
            save_act = self.findChild(QAction, 'save_act')
            save_act.setEnabled(True)
        return

    def _save_settings(self):
        self.settings.save()
        save_act = self.findChild(QAction, 'save_act')
        save_act.setEnabled(False)
        main_window = self.parentWidget()
        copter3d_w = main_window.simulation.findChildren(Copter3DWidget)[0]
        copter3d_w.set_settings()
        self.settings_changed = False
        return

    def closeEvent(self, *args, **kwargs):
        if self.isVisible() and self.settings_changed:
            self._save_settings()
        return
