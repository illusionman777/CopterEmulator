from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout,\
                            QHBoxLayout, QSizePolicy, QCheckBox, QScrollArea
from PyQt5.QtGui import QFont, QColor, QPalette, QPaintEvent, QWheelEvent
from PyQt5.QtCore import Qt, pyqtSignal


class PlotWidget(QWidget):
    plot_w = QWidget
    plot_mode = str
    plot_enabled = bool
    redraw = bool
    plot_mode_changed = pyqtSignal()
    plot_visible = pyqtSignal()

    def __init__(self, widget):
        super(PlotWidget, self).__init__(widget)
        self._init_ui()
        self.plot_enabled = True
        self.redraw = False
        self.plot_mode = 'Absolute value'
        return

    def _init_ui(self):
        name_lbl = QLabel(self)
        name_lbl.setObjectName("name_lbl")
        name_font = QFont("Times", 14, QFont.Bold)
        name_lbl.setFont(name_font)
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.hide()

        plot_enabled_lbl = QLabel(self)
        plot_enabled_lbl.setText("Enable plot:")
        plot_enabled_lbl.setObjectName("plot_enabled_lbl")
        plot_enabled_chbx = QCheckBox(self)
        plot_enabled_chbx.setObjectName("plot_enabled_chbx")
        plot_enabled_w = QWidget(self)
        plot_enabled_w.setObjectName("plot_enabled_w")
        plot_enabled_box = QHBoxLayout(plot_enabled_w)
        plot_enabled_box.addWidget(plot_enabled_lbl)
        plot_enabled_box.addWidget(plot_enabled_chbx)
        plot_enabled_box.addStretch(1)
        plot_enabled_w.setLayout(plot_enabled_box)

        plot_mode_lbl = QLabel(self)
        plot_mode_lbl.setText("Plot values mode:")
        plot_mode_lbl.setObjectName("plot_mode_lbl")
        plot_mode_cmbx = QComboBox(self)
        plot_mode_cmbx.setObjectName("plot_mode_cmbx")
        plot_mode_cmbx.addItem("Absolute value")
        plot_mode_cmbx.addItem("Value relative to destination")

        plot_mode_w = QWidget(self)
        plot_mode_w.setObjectName("plot_mode_w")
        plot_mode_box = QHBoxLayout(plot_mode_w)
        plot_mode_box.addWidget(plot_mode_lbl)
        plot_mode_box.addWidget(plot_mode_cmbx)
        plot_mode_box.addStretch(1)
        plot_mode_w.setLayout(plot_mode_box)

        scroll_w = QScrollArea(self)
        color = QColor(255, 255, 255)
        palette = QPalette(color)
        scroll_w.setPalette(palette)
        scroll_w.setObjectName("scroll_w")
        self.plot_w = QWidget(scroll_w)
        self.plot_w.installEventFilter(self)
        self.plot_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_w.setWidgetResizable(False)
        scroll_w.viewport().installEventFilter(self)

        main_box = QVBoxLayout(self)
        main_box.addWidget(name_lbl)
        main_box.addWidget(plot_enabled_w)
        main_box.addWidget(plot_mode_w)
        main_box.addWidget(scroll_w)
        self.setLayout(main_box)

        plot_enabled_chbx.stateChanged.connect(self._enable_plot)
        plot_mode_cmbx.currentIndexChanged.connect(self._change_plot_mode)

        plot_enabled_chbx.setChecked(True)
        plot_mode_cmbx.setCurrentText("Absolute value")
        return

    def _enable_plot(self):
        sender = self.sender()
        plot_mode_cmbx = self.findChild(QComboBox, "plot_mode_cmbx")
        if sender.isChecked():
            self.plot_w.setEnabled(True)
            plot_mode_cmbx.setEnabled(True)
            self.plot_enabled = True
        else:
            self.plot_w.setEnabled(False)
            plot_mode_cmbx.setEnabled(False)
            self.plot_enabled = False
        return

    def _change_plot_mode(self):
        sender = self.sender()
        if sender.currentIndex() == 0:
            self.plot_mode = "Absolute value"
        else:
            self.plot_mode = "Value relative to destination"
        self.redraw = True
        self.plot_mode_changed.emit()
        return

    def eventFilter(self, QObject, QEvent):
        scroll_w = self.findChild(QScrollArea, "scroll_w")
        if QObject == scroll_w.viewport() and isinstance(QEvent, QWheelEvent):
            return False
        if QObject == self.plot_w and isinstance(QEvent, QPaintEvent):
            self.plot_w.setFixedWidth(scroll_w.width() - 20)
            if scroll_w.height() > self.plot_w.minimumHeight():
                self.plot_w.setFixedHeight(scroll_w.height())
        return False

    def showEvent(self, *args, **kwargs):
        self.plot_visible.emit()
        return
