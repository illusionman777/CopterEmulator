from PyQt5.QtWidgets import QAction, QWidget, QToolBar, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from .fuselage_widget import FuselageWidget
from .engine_widget import EngineWidget

import physicalmodel as model


class CopterSettingsWidget(QWidget):
    copter = model.Copter
    main_widget = QWidget
    current_action = QAction
    copter_changed = pyqtSignal()
    widget_closed = pyqtSignal()

    def __init__(self, window):
        super(CopterSettingsWidget, self).__init__(window)
        self.copter = window.copter
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
        main_box.addWidget(settings_tlbr)
        fuselage_act = QAction("Fuselage", self)
        fuselage_act.setObjectName("fuselage_act")
        fuselage_act.setCheckable(True)
        fuselage_act.setChecked(True)
        fuselage_act.triggered.connect(self._show_widget)
        settings_tlbr.addAction(fuselage_act)
        fuselage_tab = FuselageWidget(self)
        fuselage_tab.setObjectName("fuselage_tab")
        fuselage_tab.setPalette(palette)
        fuselage_tab.setAutoFillBackground(True)
        fuselage_tab.copter_changed.connect(self._copter_changed)
        self.current_action = fuselage_act
        self.main_widget = fuselage_tab
        main_box.addWidget(fuselage_tab)
        if self.copter.equal_engines:
            engine_act = QAction("Engines", self)
            engine_act.setObjectName("engine_act")
            engine_act.setCheckable(True)
            engine_act.setChecked(False)
            engine_act.triggered.connect(self._show_widget)
            settings_tlbr.addAction(engine_act)
            engine_tab = EngineWidget(self)
            engine_tab.setObjectName("engine_tab")
            engine_tab.setPalette(palette)
            engine_tab.setAutoFillBackground(True)
            engine_tab.copter_changed.connect(self._copter_changed)
            main_box.addWidget(engine_tab)
            engine_tab.hide()
        else:
            for i in range(self.copter.num_of_engines):
                engine_act = QAction("Engine {}".format(i + 1), self)
                engine_act.setObjectName("engine_act_{}".format(i))
                engine_act.setCheckable(True)
                engine_act.setChecked(False)
                engine_act.triggered.connect(self._show_widget)
                settings_tlbr.addAction(engine_act)
                engine_tab = EngineWidget(self, i)
                engine_tab.setObjectName("engine_tab_{}".format(i))
                engine_tab.setPalette(palette)
                engine_tab.setAutoFillBackground(True)
                engine_tab.copter_changed.connect(self._copter_changed)
                main_box.addWidget(engine_tab)
                engine_tab.hide()
        for action in settings_tlbr.actions():
            widget = settings_tlbr.widgetForAction(action)
            widget.setFixedWidth(115)
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
            if sender_name == "fuselage_act":
                widget = self.findChild(FuselageWidget, "fuselage_tab")
            elif sender_name == "engine_act":
                widget = self.findChild(EngineWidget, "engine_tab")
            elif sender_name.startswith("engine_act_"):
                i = sender_name.replace("engine_act_", "")
                widget = self.findChild(EngineWidget, "engine_tab_" + i)
            widget.show()
            self.main_widget = widget
        return

    def _copter_changed(self):
        self.copter_changed.emit()
        return

    def closeEvent(self, *args, **kwargs):
        if self.isVisible():
            self.widget_closed.emit()
        return
