from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, \
                            QLineEdit, QHBoxLayout, \
                            QVBoxLayout, QScrollArea, QComboBox
from PyQt5.QtGui import QFont, QDoubleValidator, QPixmap, \
                        QPalette, QColor, QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal
from . import main_window

import physicalmodel as model
import copy


class EngineWidget(QWidget):
    copter = model.Copter
    engine = model.Engine
    copter_changed = pyqtSignal()

    def __init__(self, tab_widget, *args):
        super(EngineWidget, self).__init__(tab_widget)
        widget_font = QFont("Times", 10)
        self.setFont(widget_font)
        self.copter = tab_widget.copter
        if args:
            self.engine = self.copter.engines[args[0]]
            self._init_ui(args[0])
        else:
            self.engine = self.copter.engines[0]
            self._init_ui()
        self._set_ui()
        return

    def _init_ui(self, *args):
        name_lbl = QLabel(self)
        if args:
            name_lbl.setText("Engine {}".format(args[0] + 1))
        else:
            name_lbl.setText("Engines")
        name_lbl.setObjectName("name_lbl")
        name_font = QFont("Times", 14, QFont.Bold)
        name_lbl.setFont(name_font)
        name_lbl.setAlignment(Qt.AlignCenter)

        settings_lbl = QLabel(self)
        settings_lbl.setText(name_lbl.text() + " settings")
        settings_lbl.setObjectName("settings_lbl")
        settings_font = QFont("Times", 12, QFont.Bold)
        settings_lbl.setFont(settings_font)
        settings_lbl.setAlignment(Qt.AlignCenter)

        mass_lbl = QLabel(self)
        mass_lbl.setText("Engine mass\n"
                         "m, [kg]:")
        mass_lbl.setObjectName("mass_lbl")
        mass_line = QLineEdit(self)
        mass_line.setObjectName("mass_line")

        in_moment_lbl = QLabel(self)
        in_moment_lbl.setText("Engine moment of inertia around mass center\n"
                              "Ic, [kg*m^2]:")
        in_moment_lbl.setObjectName("in_moment_lbl")

        for i in range(3):
            for j in range(3):
                in_moment_line = QLineEdit(self)
                in_moment_line.setObjectName("in_moment_line_{0}{1}".format(i, j))

        if not self.copter.equal_engines:
            rot_dir_lbl = QLabel(self)
            rot_dir_lbl.setText("Engine direction of rotation:")
            rot_dir_lbl.setObjectName("rot_dir_lbl")
            rot_dir_cmbx = QComboBox(self)
            rot_dir_cmbx.setObjectName("rot_dir_cmbx")
            rot_dir_cmbx.addItem("clockwise")
            rot_dir_cmbx.addItem("counterclockwise")
            rot_dir_cmbx.activated[str].connect(self._set_rot_dir)

            blade_dir_lbl = QLabel(self)
            blade_dir_lbl.setText("Blade direction of rotation:")
            blade_dir_lbl.setObjectName("blade_dir_lbl")
            blade_dir_cmbx = QComboBox(self)
            blade_dir_cmbx.setObjectName("blade_dir_cmbx")
            blade_dir_cmbx.addItem("clockwise")
            blade_dir_cmbx.addItem("counterclockwise")
            blade_dir_cmbx.activated[str].connect(self._set_blade_dir)

        max_power_lbl = QLabel(self)
        max_power_lbl.setText("Engine maximum power\n"
                              "N, [Wt]:")
        max_power_lbl.setObjectName("max_power_lbl")
        max_power_line = QLineEdit(self)
        max_power_line.setObjectName("max_power_line")

        max_dr_moment_lbl = QLabel(self)
        max_dr_moment_lbl.setText("Engine hold moment\n"
                                  "M, [N*m]:")
        max_dr_moment_lbl.setObjectName("max_dr_moment_lbl")
        max_dr_moment_line = QLineEdit(self)
        max_dr_moment_line.setObjectName("max_dr_moment_line")

        max_pwm_lbl = QLabel(self)
        max_pwm_lbl.setText("Maximum PWM number")
        max_pwm_lbl.setObjectName("max_pwm_lbl")
        max_pwm_line = QLineEdit(self)
        max_pwm_line.setObjectName("max_pwm_line")

        blade_diameter_lbl = QLabel(self)
        blade_diameter_lbl.setText("Engine's blade diameter\n"
                                   "D, [m]:")
        blade_diameter_lbl.setObjectName("blade_diameter_lbl")
        blade_diameter_line = QLineEdit(self)
        blade_diameter_line.setObjectName("blade_diameter_line")

        blade_coef_a_lbl = QLabel(self)
        blade_coef_a_lbl.setText("Blade's Alpha coefficient")
        blade_coef_a_lbl.setObjectName("blade_coef_a_lbl")
        blade_coef_a_line = QLineEdit(self)
        blade_coef_a_line.setObjectName("blade_coef_a_line")

        blade_coef_b_lbl = QLabel(self)
        blade_coef_b_lbl.setText("Blade's Beta coefficient")
        blade_coef_b_lbl.setObjectName("blade_coef_b_lbl")
        blade_coef_b_line = QLineEdit(self)
        blade_coef_b_line.setObjectName("blade_coef_b_line")

        self._connect_line_edit()
        return

    def _set_ui(self):
        main_box = QVBoxLayout(self)
        name_lbl = self.findChild(QLabel, "name_lbl")

        settings_box = QHBoxLayout(self)
        text_scr = QScrollArea(self)
        color = QColor(255, 255, 255)
        palette = QPalette(color)
        text_scr.setPalette(palette)
        text_w = QWidget(self)
        text_grid = QGridLayout(text_w)

        grid_row = 0
        if self.copter.equal_engines:
            grid_column_num = 1
        else:
            grid_column_num = 2

        settings_lbl = self.findChild(QLabel, "settings_lbl")
        mass_lbl = self.findChild(QLabel, "mass_lbl")
        mass_line = self.findChild(QLineEdit, "mass_line")
        mass_line.setText(str(self.engine.mass))
        in_moment_lbl = self.findChild(QLabel, "in_moment_lbl")

        in_moment_w = QWidget(text_w)
        in_moment_grid = QGridLayout(in_moment_w)

        for i in range(3):
            for j in range(3):
                in_moment_line = self.findChild(QLineEdit, "in_moment_line_{0}{1}".format(i, j))
                in_moment_line.setText(str(self.engine.inertia_moment[j, i]))
                in_moment_grid.addWidget(in_moment_line, i, j)

        text_grid.addWidget(settings_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(mass_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(mass_line, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(in_moment_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(in_moment_w, grid_row, 0, 3, grid_column_num)
        grid_row += 3

        if not self.copter.equal_engines:
            rot_dir_lbl = self.findChild(QLabel, "rot_dir_lbl")
            rot_dir_cmbx = self.findChild(QComboBox, "rot_dir_cmbx")
            rot_dir_cmbx.setCurrentText(self.engine.rotation_dir)
            text_grid.addWidget(rot_dir_lbl, grid_row, 0, 1, 1)
            text_grid.addWidget(rot_dir_cmbx, grid_row, 1, 1, 1)
            grid_row += 1

            blade_dir_lbl = self.findChild(QLabel, "blade_dir_lbl")
            blade_dir_cmbx = self.findChild(QComboBox, "blade_dir_cmbx")
            blade_dir_cmbx.setCurrentText(self.engine.blade_dir)
            text_grid.addWidget(blade_dir_lbl, grid_row, 0, 1, 1)
            text_grid.addWidget(blade_dir_cmbx, grid_row, 1, 1, 1)
            grid_row += 1

        max_power_lbl = self.findChild(QLabel, "max_power_lbl")
        max_power_line = self.findChild(QLineEdit, "max_power_line")
        max_power_line.setText(str(self.engine.max_power))

        max_dr_moment_lbl = self.findChild(QLabel, "max_dr_moment_lbl")
        max_dr_moment_line = self.findChild(QLineEdit, "max_dr_moment_line")
        max_dr_moment_line.setText(str(self.engine.max_drive_moment))

        max_pwm_lbl = self.findChild(QLabel, "max_pwm_lbl")
        max_pwm_line = self.findChild(QLineEdit, "max_pwm_line")
        max_pwm_line.setText(str(self.engine.max_pwm))

        blade_diameter_lbl = self.findChild(QLabel, "blade_diameter_lbl")
        blade_diameter_line = self.findChild(QLineEdit, "blade_diameter_line")
        blade_diameter_line.setText(str(self.engine.blade_diameter))

        blade_coef_a_lbl = self.findChild(QLabel, "blade_coef_a_lbl")
        blade_coef_a_line = self.findChild(QLineEdit, "blade_coef_a_line")
        blade_coef_a_line.setText(str(self.engine.blade_coef_alpha))

        blade_coef_b_lbl = self.findChild(QLabel, "blade_coef_b_lbl")
        blade_coef_b_line = self.findChild(QLineEdit, "blade_coef_b_line")
        blade_coef_b_line.setText(str(self.engine.blade_coef_beta))

        stretch_box_v = QVBoxLayout(self)
        stretch_box_v.addStretch(1)

        text_grid.addWidget(max_power_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(max_power_line, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(max_dr_moment_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(max_dr_moment_line, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(max_pwm_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(max_pwm_line, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(blade_diameter_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(blade_diameter_line, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(blade_coef_a_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(blade_coef_a_line, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(blade_coef_b_lbl, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addWidget(blade_coef_b_line, grid_row, 0, 1, grid_column_num)
        grid_row += 1
        text_grid.addItem(stretch_box_v)

        text_scr.setWidgetResizable(False)
        text_scr.setWidget(text_w)

        copter_pic = QPixmap(main_window.__icon_dir__ + "copterBlueprint.png")
        copter_lbl = QLabel()
        copter_lbl.setPixmap(copter_pic)

        settings_box.addWidget(text_scr)
        settings_box.addWidget(copter_lbl)

        main_box.addWidget(name_lbl)
        main_box.addLayout(settings_box)

        self.setLayout(main_box)
        return

    def _connect_line_edit(self):
        double_valid = QDoubleValidator()
        double_valid.setBottom(0.)
        for line_edit in self.findChildren(QLineEdit):
            line_name = line_edit.objectName()
            if line_name == "max_pwm_lbl":
                int_valid = QIntValidator()
                int_valid.setBottom(1)
                line_edit.setValidator(int_valid)
            else:
                line_edit.setValidator(double_valid)
            if line_name.startswith("in_moment"):
                i = int(line_name[-2])
                j = int(line_name[-1])
                in_moment_valid = QDoubleValidator()
                if i == j:
                    in_moment_valid.setBottom(0.)
                    line_edit.setValidator(in_moment_valid)
                else:
                    line_edit.setValidator(in_moment_valid)
                line_edit.textEdited.connect(self._change_in_moment)
            else:
                line_edit.textEdited.connect(self._change_engine)
        return

    def _change_in_moment(self):
        sender_line = self.sender()
        sender_name = sender_line.objectName()
        try:
            sender_value = float(sender_line.text())
        except ValueError:
            sender_value = 0.
        i = int(sender_name[-2])
        j = int(sender_name[-1])
        in_moment_equal = self.findChild(QLineEdit, "in_moment_line_{0}{1}".format(j, i))
        in_moment_equal.setText(sender_line.text())
        if self.copter.equal_engines:
            for engine in self.copter.engines:
                engine.inertia_moment[j, i] = sender_value
                engine.inertia_moment[i, j] = sender_value
        else:
            self.engine.inertia_moment[j, i] = sender_value
            self.engine.inertia_moment[i, j] = sender_value

        self.copter_changed.emit()
        return

    def _change_engine(self):
        sender_line = self.sender()
        input_valid = sender_line.validator()
        valid = input_valid.validate(sender_line.text(), 0)
        if valid[0] == 2 and isinstance(input_valid, QDoubleValidator):
            sender_value = float(sender_line.text())
        elif valid[0] == 2 and isinstance(input_valid, QIntValidator):
            sender_value = int(sender_line.text())
        else:
            return
        sender_name = sender_line.objectName()

        if sender_name == "mass_line":
            self.engine.mass = sender_value
        elif sender_name == "max_power_line":
            self.engine.max_power = sender_value
        elif sender_name == "max_dr_moment_line":
            self.engine.max_drive_moment = sender_value
        elif sender_name == "max_pwm_line":
            self.engine.max_pwm = sender_value
        elif sender_name == "blade_diameter_line":
            self.engine.blade_diameter = sender_value
        elif sender_name == "blade_coef_a_lbl":
            self.engine.blade_coef_alpha = sender_value
        elif sender_name == "blade_coef_b_lbl":
            self.engine.blade_coef_beta = sender_value

        if self.copter.equal_engines:
            for i in range(len(self.copter.engines)):
                self.copter.engines[i] = copy.deepcopy(self.engine)
                if i % 2:
                    self.copter.engines[i].rotation_dir = "clockwise"
                    self.copter.engines[i].blade_dir = "clockwise"

        self.copter_changed.emit()
        return

    def _set_rot_dir(self, text):
        if not self.engine.rotation_dir == text:
            self.engine.rotation_dir = text
            self.copter_changed.emit()
        return

    def _set_blade_dir(self, text):
        if not self.engine.blade_dir == text:
            self.engine.blade_dir = text
            self.copter_changed.emit()
        return
