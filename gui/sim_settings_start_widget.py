from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, \
                            QLineEdit, QVBoxLayout, \
                            QScrollArea, QCheckBox, QMessageBox, QGroupBox
from PyQt5.QtGui import QFont, QDoubleValidator, QPalette, QColor, QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal
from .settings import Settings
from math import cos, sin, pi, sqrt, acos
import CopterEmulator.physicalmodel as model
import numpy

_g = 9.8062


class SimSettingsStartWidget(QWidget):
    settings = Settings
    copter = model.Copter
    settings_changed = pyqtSignal()

    def __init__(self, tab_wadget):
        super(SimSettingsStartWidget, self).__init__(tab_wadget)
        widget_font = QFont("Times", 10)
        self.setFont(widget_font)
        self.settings = tab_wadget.settings
        self.copter = tab_wadget.copter
        self._init_ui()
        self._set_ui()
        return

    def _init_ui(self):
        name_lbl = QLabel(self)
        name_lbl.setText("Simulation start settings")
        name_lbl.setObjectName("name_lbl")
        name_font = QFont("Times", 14, QFont.Bold)
        name_lbl.setFont(name_font)
        name_lbl.setAlignment(Qt.AlignCenter)

        hover_mode_lbl = QLabel(self)
        hover_mode_lbl.setText("Hover mode on start")
        hover_mode_lbl.setObjectName("hover_mode_lbl")
        hover_mode_chbx = QCheckBox(self)
        hover_mode_chbx.setObjectName("hover_mode_chbx")

        start_pos_lbl = QLabel(self)
        start_pos_lbl.setText("Copter start position, [m]:")
        start_pos_lbl.setObjectName("start_pos_lbl")

        for i in range(3):
            start_pos_line = QLineEdit(self)
            start_pos_line.setObjectName("start_pos_line_{}".format(i))

        start_q_lbl = QLabel(self)
        start_q_lbl.setText("Copter start angular position:")
        start_q_lbl.setObjectName("start_q_lbl")

        for i in range(4):
            start_q_line = QLineEdit(self)
            start_q_line.setObjectName("start_q_line_{}".format(i))

        start_vel_lbl = QLabel(self)
        start_vel_lbl.setText("Copter start velocity, [m/s]:")
        start_vel_lbl.setObjectName("start_vel_lbl")

        for i in range(3):
            start_vel_line = QLineEdit(self)
            start_vel_line.setObjectName("start_vel_line_{}".format(i))

        start_angular_vel_lbl = QLabel(self)
        start_angular_vel_lbl.setText("Copter start angular velocity, [rpm]:")
        start_angular_vel_lbl.setObjectName("start_angular_vel_lbl")

        for i in range(3):
            start_angular_vel_line = QLineEdit(self)
            start_angular_vel_line.setObjectName("start_angular_vel_line_{}".format(i))

        for i in range(self.copter.num_of_engines):
            engine_start_a_lbl = QLabel(self)
            engine_start_a_lbl.setText("Start angle, [deg]:")
            engine_start_a_lbl.setObjectName("engine_start_a_lbl_{}".format(i))
            engine_start_a_line = QLineEdit(self)
            engine_start_a_line.setObjectName("engine_start_a_line_{}".format(i))

            engine_start_a_v_lbl = QLabel(self)
            engine_start_a_v_lbl.setText("Start angular velocity, [rpm]:")
            engine_start_a_v_lbl.setObjectName("engine_start_a_v_lbl_{}".format(i))
            engine_start_a_v_line = QLineEdit(self)
            engine_start_a_v_line.setObjectName("engine_start_a_v_line_{}".format(i))

            engine_start_pwm_lbl = QLabel(self)
            engine_start_pwm_lbl.setText("Start PWM:")
            engine_start_pwm_lbl.setObjectName("engine_start_pwm_lbl_{}".format(i))
            engine_start_pwm_line = QLineEdit(self)
            engine_start_pwm_line.setObjectName("engine_start_pwm_line_{}".format(i))

        self._connect_ui()
        return

    def _set_ui(self):
        main_box = QVBoxLayout(self)
        name_lbl = self.findChild(QLabel, "name_lbl")

        text_scr = QScrollArea(self)
        color = QColor(255, 255, 255)
        palette = QPalette(color)
        text_scr.setPalette(palette)
        text_w = QWidget(self)
        text_grid = QGridLayout(text_w)
        grid_row = 0

        hover_mode_lbl = self.findChild(QLabel, "hover_mode_lbl")
        hover_mode_chbx = self.findChild(QCheckBox, "hover_mode_chbx")
        hover_mode_chbx.setChecked(False)
        if self.settings.hover_mod_on_start:
            hover_mode_chbx.toggle()

        fuselage_grbx = QGroupBox(text_w)
        fuselage_grbx.setTitle("Fuselage start settings")
        fuselage_grid = QGridLayout(fuselage_grbx)
        fus_grid_row = 0

        start_pos_lbl = self.findChild(QLabel, "start_pos_lbl")
        start_pos_w = QWidget(text_w)
        start_pos_grid = QGridLayout(start_pos_w)

        for i in range(3):
            start_pos_line = self.findChild(QLineEdit, "start_pos_line_{}".format(i))
            start_pos_line.setText(str(self.settings.start_state.fuselage_state.pos_v[i]))
            start_pos_grid.addWidget(start_pos_line, i, 0)

        start_q_lbl = self.findChild(QLabel, "start_q_lbl")
        start_q_w = QWidget(text_w)
        start_q_grid = QGridLayout(start_q_w)

        for i in range(4):
            start_q_line = self.findChild(QLineEdit, "start_q_line_{}".format(i))
            start_q_line.setText(str(self.settings.start_state.fuselage_state.rot_q[i]))
            start_q_grid.addWidget(start_q_line, i, 0)

        start_vel_lbl = self.findChild(QLabel, "start_vel_lbl")
        start_vel_w = QWidget(text_w)
        start_vel_grid = QGridLayout(start_vel_w)

        for i in range(3):
            start_vel_line = self.findChild(QLineEdit, "start_vel_line_{}".format(i))
            start_vel_line.setText(str(self.settings.start_state.fuselage_state.velocity_v[i]))
            start_vel_grid.addWidget(start_vel_line, i, 0)

        start_angular_vel_lbl = self.findChild(QLabel, "start_angular_vel_lbl")
        start_angular_vel_w = QWidget(text_w)
        start_angular_vel_grid = QGridLayout(start_angular_vel_w)

        for i in range(3):
            start_angular_vel_line = self.findChild(QLineEdit, "start_angular_vel_line_{}".format(i))
            start_angular_vel_line.setText(str(self.settings.start_state.fuselage_state.angular_vel_v[i]))
            start_angular_vel_grid.addWidget(start_angular_vel_line, i, 0)

        fuselage_grid.addWidget(start_pos_lbl, fus_grid_row, 0, 1, 2)
        fuselage_grid.addWidget(start_pos_w, fus_grid_row, 2)
        fus_grid_row += 1

        fuselage_grid.addWidget(start_q_lbl, fus_grid_row, 0, 1, 2)
        fuselage_grid.addWidget(start_q_w, fus_grid_row, 2)
        fus_grid_row += 1

        fuselage_grid.addWidget(start_vel_lbl, fus_grid_row, 0, 1, 2)
        fuselage_grid.addWidget(start_vel_w, fus_grid_row, 2)
        fus_grid_row += 1

        fuselage_grid.addWidget(start_angular_vel_lbl, fus_grid_row, 0, 1, 2)
        fuselage_grid.addWidget(start_angular_vel_w, fus_grid_row, 2)
        fus_grid_row += 1

        text_grid.addWidget(hover_mode_lbl, grid_row, 0)
        text_grid.addWidget(hover_mode_chbx, grid_row, 1)
        grid_row += 1
        text_grid.addWidget(fuselage_grbx, grid_row, 0, 4, 3)

        for i in range(self.copter.num_of_engines):
            engine_grbx = QGroupBox(text_w)
            engine_grbx.setTitle("Engine {} start settings".format(i + 1))
            engine_grid = QGridLayout(engine_grbx)
            eng_grid_row = 0

            engine_start_a_lbl = self.findChild(QLabel, "engine_start_a_lbl_{}".format(i))
            engine_start_a_line = self.findChild(QLineEdit, "engine_start_a_line_{}".format(i))
            angle = 2 * acos(self.settings.start_state.engines_state[i].rot_q[0]) * 180 / pi
            if self.copter.engines[i].rotation_dir == "clockwise":
                angle = -angle
            engine_start_a_line.setText(str(angle))

            engine_start_a_v_lbl = self.findChild(QLabel, "engine_start_a_v_lbl_{}".format(i))
            engine_start_a_v_line = self.findChild(QLineEdit, "engine_start_a_v_line_{}".format(i))
            angular_velocity = self.settings.start_state.engines_state[i].angular_vel_v[2] * 2 * pi * 60
            engine_start_a_v_line.setText(str(angular_velocity))

            engine_start_pwm_lbl = self.findChild(QLabel, "engine_start_pwm_lbl_{}".format(i))
            engine_start_pwm_line = self.findChild(QLineEdit, "engine_start_pwm_line_{}".format(i))
            engine_start_pwm_line.setText(str(self.settings.start_state.engines_state[i].current_pwm))

            engine_grid.addWidget(engine_start_a_lbl, eng_grid_row, 0, 1, 2)
            engine_grid.addWidget(engine_start_a_line, eng_grid_row, 2)
            eng_grid_row += 1
            engine_grid.addWidget(engine_start_a_v_lbl, eng_grid_row, 0, 1, 2)
            engine_grid.addWidget(engine_start_a_v_line, eng_grid_row, 2)
            eng_grid_row += 1
            engine_grid.addWidget(engine_start_pwm_lbl, eng_grid_row, 0, 1, 2)
            engine_grid.addWidget(engine_start_pwm_line, eng_grid_row, 2)
            eng_grid_row += 1

            grid_row_tmp = grid_row + i % 4
            grid_column = 3 + i // 4
            text_grid.addWidget(engine_grbx, grid_row_tmp, grid_column)

        grid_row += 4
        stretch_box_v = QVBoxLayout(self)
        stretch_box_v.addStretch(1)
        text_grid.addItem(stretch_box_v, grid_row, 0)

        text_scr.setWidgetResizable(False)
        text_scr.setWidget(text_w)

        main_box.addWidget(name_lbl)
        main_box.addWidget(text_scr)

        self.setLayout(main_box)
        return

    def _connect_ui(self):
        double_valid = QDoubleValidator()
        for line_edit in self.findChildren(QLineEdit):
            line_name = line_edit.objectName()
            if line_name.startswith("engine_start_pwm_line"):
                int_valid = QIntValidator()
                int_valid.setBottom(0)
                line_edit.setValidator(int_valid)
            else:
                line_edit.setValidator(double_valid)
            line_edit.textEdited.connect(self._change_settings)

        hover_mode_chbx = self.findChild(QCheckBox, "hover_mode_chbx")
        hover_mode_chbx.toggled.connect(self._set_hover_mode)
        return

    def _change_settings(self):
        sender_w = self.sender()
        input_valid = sender_w.validator()
        if input_valid:
            valid = input_valid.validate(sender_w.text(), 0)
            if valid[0] == 2 and isinstance(input_valid, QDoubleValidator):
                sender_value = float(sender_w.text())
            elif valid[0] == 2 and isinstance(input_valid, QIntValidator):
                sender_value = int(sender_w.text())
            else:
                return
        else:
            sender_value = sender_w.text()
        sender_name = sender_w.objectName()

        if sender_name.startswith("start_pos_line"):
            i = int(sender_name[-1])
            self.settings.start_state.fuselage_state.pos_v[i] = sender_value
            if self.settings.hover_mod_on_start and i == 2:
                hover_mode_chbx = self.findChild(QCheckBox, "hover_mode_chbx")
                hover_mode_chbx.toggle()
        elif sender_name.startswith("start_q_line"):
            i = int(sender_name[-1])
            self.settings.start_state.fuselage_state.rot_q[i] = sender_value
        elif sender_name.startswith("start_vel_line"):
            i = int(sender_name[-1])
            self.settings.start_state.fuselage_state.velocity_v[i] = sender_value
        elif sender_name.startswith("start_angular_vel_line"):
            i = int(sender_name[-1])
            self.settings.start_state.fuselage_state.angular_vel_v[i] = sender_value / 60 / (2 * pi)
        elif sender_name.startswith("engine_start_a_line"):
            i = int(sender_name[-1])
            angle = sender_value / 180 * pi / 2
            if self.copter.engines[i].rotation_dir == "clockwise":
                angle = -angle
            self.settings.start_state.engines_state[i].rot_q[0] = cos(angle)
            self.settings.start_state.engines_state[i].rot_q[3] = sin(angle)
        elif sender_name.startswith("engine_start_a_v_line"):
            i = int(sender_name[-1])
            vector_tmp = numpy.array([0, 0, sender_value / 60 / (2 * pi)])
            self.settings.start_state.engines_state[i].angular_vel_v = vector_tmp
        elif sender_name.startswith("engine_start_pwm_line"):
            i = int(sender_name[-1])
            self.settings.start_state.engines_state[i].current_pwm = sender_value

        self.settings_changed.emit()
        return

    def _set_hover_mode(self):
        sender = self.sender()
        if sender.isChecked():
            if not self.copter.symmetry or not self.copter.equal_engines:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Cannot set the hover mode!")
                msg.setInformativeText("This mode works only on symmetric copter with equal engines.")
                msg.setWindowTitle("Critical error!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(self._uncheck_hover_mode)
                msg.exec_()
                return
            self.settings.hover_mod_on_start = True
            copter_mass = self.copter.fuselage.mass
            for i in range(self.copter.num_of_engines):
                copter_mass += self.copter.engines[i].mass
            engine_force = copter_mass * _g / self.copter.num_of_engines
            for i in range(self.copter.num_of_engines):
                if self.copter.engines[i].blade_diameter == 0:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Cannot set the hover mode!")
                    msg.setInformativeText("Engine {} blade diameter is 0".format(i))
                    msg.setWindowTitle("Critical error!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.buttonClicked.connect(self._uncheck_hover_mode)
                    msg.exec_()
                    return
                engine_a_v = sqrt(engine_force / (2 * pi *
                                                  self.copter.engines[i].blade_coef_alpha *
                                                  self._pho_air() *
                                                  self.copter.engines[i].blade_diameter *
                                                  self.copter.engines[i].blade_diameter *
                                                  self.copter.engines[i].blade_diameter *
                                                  self.copter.engines[i].blade_diameter))
                engine_moment = 2 * pi * self.copter.engines[i].blade_coef_beta * \
                                self._pho_air() * \
                                engine_a_v * engine_a_v * \
                                self.copter.engines[i].blade_diameter * \
                                self.copter.engines[i].blade_diameter * \
                                self.copter.engines[i].blade_diameter * \
                                self.copter.engines[i].blade_diameter * \
                                self.copter.engines[i].blade_diameter
                engine_power = engine_a_v * engine_moment
                if engine_power > self.copter.engines[i].max_power:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Cannot set the hover mode!")
                    msg.setInformativeText("Engine {} has not enough power\n"
                                           "to produce needed aerodynamic force".format(i))
                    msg.setWindowTitle("Critical error!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.buttonClicked.connect(self._uncheck_hover_mode)
                    msg.exec_()
                    return
                self.settings.start_state.engines_state[i].angular_vel_v = numpy.array([0, 0, engine_a_v])
                engine_a_v = engine_a_v * 2 * pi * 60
                engine_pwm = sqrt(engine_power / self.copter.engines[i].max_power) * \
                             self.copter.engines[i].max_pwm
                engine_pwm = int(round(engine_pwm))
                self.settings.start_state.engines_state[i].current_pwm = engine_pwm
                engine_start_a_v_line = self.findChild(QLineEdit, "engine_start_a_v_line_{}".format(i))
                engine_start_pwm_line = self.findChild(QLineEdit, "engine_start_pwm_line_{}".format(i))
                engine_start_a_v_line.setText(str(engine_a_v))
                engine_start_pwm_line.setText(str(engine_pwm))
                engine_start_a_v_line.setReadOnly(True)
                engine_start_pwm_line.setReadOnly(True)
        else:
            self.settings.hover_mod_on_start = False
            for i in range(self.copter.num_of_engines):
                engine_start_a_v_line = self.findChild(QLineEdit, "engine_start_a_v_line_{}".format(i))
                engine_start_pwm_line = self.findChild(QLineEdit, "engine_start_pwm_line_{}".format(i))
                engine_start_a_v_line.setReadOnly(False)
                engine_start_pwm_line.setReadOnly(False)
        self.settings_changed.emit()
        return

    def _pho_air(self):
        _pho_air0 = 1.225
        return _pho_air0 * (20000 - self.settings.start_state.fuselage_state.pos_v[2]) / \
               (20000 + self.settings.start_state.fuselage_state.pos_v[2])

    def _uncheck_hover_mode(self):
        hover_mode_chbx = self.findChild(QCheckBox, "hover_mode_chbx")
        hover_mode_chbx.setChecked(False)
        self.settings.hover_mod_on_start = False
        return
