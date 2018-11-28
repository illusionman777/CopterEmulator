from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, \
    QLineEdit, QHBoxLayout, \
    QVBoxLayout, QScrollArea
from PyQt5.QtGui import QFont, QDoubleValidator, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from . import main_window
from math import pi, pow, sqrt, sin, cos, tan, acos, fabs
import numpy
import CopterEmulator.physicalmodel as model


class FuselageWidget(QWidget):
    copter = model.Copter
    copter_changed = pyqtSignal()

    def __init__(self, tab_widget):
        super(FuselageWidget, self).__init__(tab_widget)
        widget_font = QFont("Times", 10)
        self.setFont(widget_font)
        self.copter = tab_widget.copter
        self._init_ui()
        self._set_ui()
        return

    def _init_ui(self):
        name_lbl = QLabel(self)
        name_lbl.setText(self.copter.name)
        name_lbl.setObjectName("name_lbl")
        name_font = QFont("Times", 20, QFont.Bold)
        name_lbl.setFont(name_font)
        name_lbl.setAlignment(Qt.AlignCenter)

        descr_lbl = QLabel(self)
        descr_lbl.setText("Copter with {} engines".format(
            self.copter.num_of_engines))
        descr_lbl.setObjectName("descr_lbl")
        descr_lbl.setAlignment(Qt.AlignCenter)

        settings_lbl = QLabel(self)
        settings_lbl.setText("Fuselage settings")
        settings_lbl.setObjectName("settings_lbl")
        settings_font = QFont("Times", 12, QFont.Bold)
        settings_lbl.setFont(settings_font)
        settings_lbl.setAlignment(Qt.AlignCenter)

        vx_lbl = QLabel(self)
        vx_lbl.setText("Maximum horizontal speed\n"
                       "Vx, [m/s]:")
        vx_lbl.setObjectName("vx_lbl")
        vx_line = QLineEdit(self)
        vx_line.setObjectName("vx_line")

        vy_lbl = QLabel(self)
        vy_lbl.setText("Maximum vertical speed\n"
                       "Vy, [m/s]:")
        vy_lbl.setObjectName("vy_lbl")
        vy_line = QLineEdit(self)
        vy_line.setObjectName("vy_line")

        mass_lbl = QLabel(self)
        mass_lbl.setText("Fuselage mass\n"
                         "m, [kg]:")
        mass_lbl.setObjectName("mass_lbl")
        mass_line = QLineEdit(self)
        mass_line.setObjectName("mass_line")

        in_moment_lbl = QLabel(self)
        in_moment_lbl.setText("Fuselage moment of inertia around mass center\n"
                              "Ic, [kg*m^2]:")
        in_moment_lbl.setObjectName("in_moment_lbl")

        for i in range(3):
            for j in range(3):
                in_moment_line = QLineEdit(self)
                in_moment_line.setObjectName("in_moment_line_{0}{1}".format(i, j))

        square_lbl = QLabel(self)
        square_lbl.setText("Aerodynamic fuselage square\n"
                           "S, [m^2]:")
        square_lbl.setObjectName("square_lbl")
        square_line = QLineEdit(self)
        square_line.setObjectName("square_line")

        drag_coef_lbl = QLabel(self)
        drag_coef_lbl.setText("Aerodynamic drag coefficient\n"
                              "Cd:")
        drag_coef_lbl.setObjectName("drag_coef_lbl")

        m_coef_lbl = QLabel(self)
        m_coef_lbl.setText("Aerodynamic moment coefficient\n"
                           "Cm:")
        m_coef_lbl.setObjectName("m_coef_lbl")

        for i in range(3):
            drag_coef_line = QLineEdit(self)
            drag_coef_line.setObjectName("drag_coef_line_{}".format(i))

            m_coef_line = QLineEdit(self)
            m_coef_line.setObjectName("m_coef_line_{}".format(i))

        dist_mc_lbl = QLabel(self)
        dist_mc_lbl.setText("Distance between fuselage and engines mass center's\n"
                            "L, [m]:")
        dist_mc_lbl.setObjectName("dist_mc_lbl")

        height_mc_lbl = QLabel(self)
        height_mc_lbl.setText("Height between fuselage and engines mass center's\n"
                              "H, [m]:")
        height_mc_lbl.setObjectName("height_mc_lbl")

        if self.copter.symmetry:
            dist_mc_line = QLineEdit(self)
            dist_mc_line.setObjectName("dist_mc_line")

            height_mc_line = QLineEdit(self)
            height_mc_line.setObjectName("height_mc_line")
        else:
            for i in range(self.copter.num_of_engines):
                engine_lbl = QLabel(self)
                engine_lbl.setText("Engine {}".format(i + 1))
                engine_font = QFont("Times", 10, QFont.Bold)
                engine_lbl.setFont(engine_font)
                engine_lbl.setObjectName("engine_lbl_{}".format(i))
                engine_lbl.setAlignment(Qt.AlignCenter)

                dist_mc_line = QLineEdit(self)
                dist_mc_line.setObjectName("dist_mc_line_{}".format(i))

                height_mc_line = QLineEdit(self)
                height_mc_line.setObjectName("height_mc_line_{}".format(i))

        if not self.copter.symmetry:
            angle_fus_eng_lbl = QLabel(self)
            angle_fus_eng_lbl.setText("Angle between fuselage X axis"
                                      "and line from it's to engine's mass center\n"
                                      "Alpha, [deg]:")
            angle_fus_eng_lbl.setObjectName("angle_fus_eng_lbl")
            for i in range(self.copter.num_of_engines):
                angle_fus_eng_line = QLineEdit(self)
                angle_fus_eng_line.setObjectName("angle_fus_eng_line_{}".format(i))

            fus_eng_q_lbl = QLabel(self)
            fus_eng_q_lbl.setText("Quaternion between fuselage coordinate axis"
                                  "and engine coordinate axis\n"
                                  "Lambda:")
            fus_eng_q_lbl.setObjectName("fus_eng_q_lbl")
            for i in range(self.copter.num_of_engines):
                for j in range(4):
                    fus_eng_q_line = QLineEdit(self)
                    fus_eng_q_line.setObjectName("fus_eng_q_line_{0}{1}".format(i, j))

        self._connect_line_edit()
        return

    def _set_ui(self):
        main_box = QVBoxLayout(self)
        name_lbl = self.findChild(QLabel, "name_lbl")
        descr_lbl = self.findChild(QLabel, "descr_lbl")

        settings_box = QHBoxLayout(self)
        text_scr = QScrollArea(self)
        color = QColor(255, 255, 255)
        palette = QPalette(color)
        text_scr.setPalette(palette)
        text_w = QWidget(self)
        text_grid = QGridLayout(text_w)

        grid_row = 0
        if self.copter.symmetry:
            grid_column_num = 1
        else:
            grid_column_num = self.copter.num_of_engines

        settings_lbl = self.findChild(QLabel, "settings_lbl")

        vx_lbl = self.findChild(QLabel, "vx_lbl")
        vx_line = self.findChild(QLineEdit, "vx_line")
        vx_line.setEnabled(False)
        vy_lbl = self.findChild(QLabel, "vy_lbl")
        vy_line = self.findChild(QLineEdit, "vy_line")
        vy_line.setEnabled(False)
        self._calc_maximum_speed()

        v_widget = QWidget(text_w)
        v_grid = QGridLayout(v_widget)
        v_grid.addWidget(vx_lbl, 0, 0, 1, 1)
        v_grid.addWidget(vy_lbl, 0, 1, 1, 1)
        v_grid.addWidget(vx_line, 1, 0, 1, 1)
        v_grid.addWidget(vy_line, 1, 1, 1, 1)

        mass_lbl = self.findChild(QLabel, "mass_lbl")
        mass_line = self.findChild(QLineEdit, "mass_line")
        mass_line.setText(str(self.copter.fuselage.mass))
        in_moment_lbl = self.findChild(QLabel, "in_moment_lbl")

        in_moment_w = QWidget(text_w)
        in_moment_grid = QGridLayout(in_moment_w)

        for i in range(3):
            for j in range(3):
                in_moment_line = self.findChild(QLineEdit, "in_moment_line_{0}{1}".format(i, j))
                in_moment_line.setText(str(self.copter.fuselage.inertia_moment[j, i]))
                in_moment_grid.addWidget(in_moment_line, i, j)

        square_lbl = self.findChild(QLabel, "square_lbl")
        square_line = self.findChild(QLineEdit, "square_line")
        square_line.setText(str(self.copter.aero_square))

        drag_coef_lbl = self.findChild(QLabel, "drag_coef_lbl")
        drag_coef_w = QWidget(text_w)
        drag_coef_grid = QGridLayout(drag_coef_w)
        m_coef_lbl = self.findChild(QLabel, "m_coef_lbl")
        m_coef_w = QWidget(text_w)
        m_coef_grid = QGridLayout(m_coef_w)

        for i in range(3):
            drag_coef_line = self.findChild(QLineEdit, "drag_coef_line_{}".format(i))
            drag_coef_line.setText(str(self.copter.drag_coef[i]))
            drag_coef_grid.addWidget(drag_coef_line, i, 0)
            m_coef_line = self.findChild(QLineEdit, "m_coef_line_{}".format(i))
            m_coef_line.setText(str(self.copter.moment_coef[i]))
            m_coef_grid.addWidget(m_coef_line, i, 0)

        text_grid.addWidget(settings_lbl, grid_row, 0, 1, min([grid_column_num, 6]))
        grid_row += 1
        text_grid.addWidget(v_widget, grid_row, 0, 1, min([grid_column_num, 6]))
        grid_row += 1
        text_grid.addWidget(mass_lbl, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 1
        text_grid.addWidget(mass_line, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 1
        text_grid.addWidget(in_moment_lbl, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 1
        text_grid.addWidget(in_moment_w, grid_row, 0, 3, min([grid_column_num, 3]))
        grid_row += 3
        text_grid.addWidget(square_lbl, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 1
        text_grid.addWidget(square_line, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 1
        text_grid.addWidget(drag_coef_lbl, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 1
        text_grid.addWidget(drag_coef_w, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 3
        text_grid.addWidget(m_coef_lbl, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 1
        text_grid.addWidget(m_coef_w, grid_row, 0, 1, min([grid_column_num, 3]))
        grid_row += 3

        dist_mc_lbl = self.findChild(QLabel, "dist_mc_lbl")
        height_mc_lbl = self.findChild(QLabel, "height_mc_lbl")

        stretch_box_v = QVBoxLayout(self)
        stretch_box_v.addStretch(1)

        if self.copter.symmetry:
            dist_mc_line = self.findChild(QLineEdit, "dist_mc_line")
            dist_mc_line.setText(str(self.copter.distance_fus_engine_mc[0]))
            height_mc_line = self.findChild(QLineEdit, "height_mc_line")
            height_mc_line.setText(str(self.copter.height_fus_engine_mc[0]))

            text_grid.addWidget(dist_mc_lbl, grid_row, 0, 1, grid_column_num)
            grid_row += 1
            text_grid.addWidget(dist_mc_line, grid_row, 0, 1, grid_column_num)
            grid_row += 1
            text_grid.addWidget(height_mc_lbl, grid_row, 0, 1, grid_column_num)
            grid_row += 1
            text_grid.addWidget(height_mc_line, grid_row, 0, 1, grid_column_num)
            grid_row += 1
            text_grid.addItem(stretch_box_v, grid_row, 0, 1, grid_column_num)
        else:
            angle_fus_eng_lbl = self.findChild(QLabel, "angle_fus_eng_lbl")
            fus_eng_q_lbl = self.findChild(QLabel, "fus_eng_q_lbl")
            text_grid.addWidget(dist_mc_lbl, grid_row + 1, 0, 1, grid_column_num)
            text_grid.addWidget(height_mc_lbl, grid_row + 3, 0, 1, grid_column_num)
            text_grid.addWidget(angle_fus_eng_lbl, grid_row + 5, 0, 1, grid_column_num)
            text_grid.addWidget(fus_eng_q_lbl, grid_row + 7, 0, 1, grid_column_num)
            text_grid.addItem(stretch_box_v, grid_row + 9, 0, 1, grid_column_num)

            for i in range(self.copter.num_of_engines):
                grid_row_tmp = grid_row
                fus_eng_q_w = QWidget(text_w)
                fus_eng_q_grid = QGridLayout(fus_eng_q_w)
                fus_eng_q_grid.setVerticalSpacing(0)
                engine_name_lbl = self.findChild(QLabel, "engine_lbl_{}".format(i))
                dist_mc_line = self.findChild(QLineEdit, "dist_mc_line_{}".format(i))
                dist_mc_line.setText(str(self.copter.distance_fus_engine_mc[i]))
                height_mc_line = self.findChild(QLineEdit, "height_mc_line_{}".format(i))
                height_mc_line.setText(str(self.copter.height_fus_engine_mc[i]))
                angle_fus_eng_line = self.findChild(QLineEdit, "angle_fus_eng_line_{}".format(i))
                angle_fus_eng_line.setText(str(self.copter.angle_fus_engine[i] * pi / 180))
                for j in range(4):
                    fus_eng_q_line = self.findChild(QLineEdit, "fus_eng_q_line_{0}{1}".format(i, j))
                    fus_eng_q_tmp = self.copter.fus_engine_q[i]
                    fus_eng_q_line.setText(str(fus_eng_q_tmp[j]))
                    fus_eng_q_grid.addWidget(fus_eng_q_line, j, 0)

                text_grid.addWidget(engine_name_lbl, grid_row_tmp, i, 1, 1)
                grid_row_tmp += 2
                text_grid.addWidget(dist_mc_line, grid_row_tmp, i, 1, 1)
                grid_row_tmp += 2
                text_grid.addWidget(height_mc_line, grid_row_tmp, i, 1, 1)
                grid_row_tmp += 2
                text_grid.addWidget(angle_fus_eng_line, grid_row_tmp, i, 1, 1)
                grid_row_tmp += 2
                text_grid.addWidget(fus_eng_q_w, grid_row_tmp, i, 1, 1)

        text_scr.setWidgetResizable(False)
        text_scr.setWidget(text_w)

        copter_pic = QPixmap(main_window.__icon_dir__ + "copterBlueprint.png")
        copter_lbl = QLabel()
        copter_lbl.setPixmap(copter_pic)

        settings_box.addWidget(text_scr)
        settings_box.addWidget(copter_lbl)

        main_box.addWidget(name_lbl)
        main_box.addWidget(descr_lbl)
        main_box.addLayout(settings_box)

        self.setLayout(main_box)
        return

    def _connect_line_edit(self):
        double_valid = QDoubleValidator()
        for line_edit in self.findChildren(QLineEdit):
            line_name = line_edit.objectName()
            if line_name == "mass_line" or \
                    line_name.startswith("drag_coef"):
                mass_valid = QDoubleValidator()
                mass_valid.setBottom(0.)
                line_edit.setValidator(mass_valid)
            else:
                line_edit.setValidator(double_valid)
            if line_name.startswith("in_moment"):
                i = int(line_name[-2])
                j = int(line_name[-1])
                if i == j:
                    in_moment_valid = QDoubleValidator()
                    in_moment_valid.setBottom(0.)
                    line_edit.setValidator(in_moment_valid)
                line_edit.textEdited.connect(self._change_in_moment)
            else:
                line_edit.textEdited.connect(self._change_copter)
        return

    def _change_in_moment(self):
        sender_line = self.sender()
        sender_name = sender_line.objectName()
        i = int(sender_name[-2])
        j = int(sender_name[-1])
        in_moment_equal = self.findChild(QLineEdit, "in_moment_line_{0}{1}".format(j, i))
        in_moment_equal.setText(sender_line.text())
        try:
            self.copter.fuselage.inertia_moment[j, i] = float(sender_line.text())
            self.copter.fuselage.inertia_moment[i, j] = float(in_moment_equal.text())
        except ValueError:
            self.copter.fuselage.inertia_moment[j, i] = 0.
            self.copter.fuselage.inertia_moment[i, j] = 0.
        self.copter_changed.emit()
        return

    def _change_copter(self):
        sender_line = self.sender()
        input_valid = sender_line.validator()
        valid = input_valid.validate(sender_line.text(), 0)
        if not valid[0] == 2:
            return
        sender_name = sender_line.objectName()
        sender_value = float(sender_line.text())

        if sender_name == "mass_line":
            self.copter.fuselage.mass = sender_value
        elif sender_name == "square_line":
            self.copter.aero_square = sender_value
        elif sender_name.startswith("drag_coef_line_"):
            i = int(sender_name.replace("drag_coef_line_", ""))
            self.copter.drag_coef[i] = sender_value
        elif sender_name.startswith("m_coef_line_"):
            i = int(sender_name.replace("m_coef_line_", ""))
            self.copter.moment_coef[i] = sender_value
        elif sender_name == "dist_mc_line":
            dist_mc_tmp = self.copter.distance_fus_engine_mc
            for i in range(len(dist_mc_tmp)):
                dist_mc_tmp[i] = sender_value
            self.copter.distance_fus_engine_mc = dist_mc_tmp
        elif sender_name == "height_mc_line":
            height_mc_tmp = self.copter.height_fus_engine_mc
            for i in range(len(height_mc_tmp)):
                height_mc_tmp[i] = sender_value
            self.copter.height_fus_engine_mc = height_mc_tmp
        elif sender_name.startswith("dist_mc_line_"):
            dist_mc_tmp = self.copter.distance_fus_engine_mc
            i = int(sender_name.replace("dist_mc_line_", ""))
            dist_mc_tmp[i] = sender_value
            self.copter.distance_fus_engine_mc = dist_mc_tmp
        elif sender_name.startswith("height_mc_line_"):
            height_mc_tmp = self.copter.height_fus_engine_mc
            i = int(sender_name.replace("height_mc_line_", ""))
            height_mc_tmp[i] = sender_value
            self.copter.height_fus_engine_mc = height_mc_tmp
        elif sender_name.startswith("angle_fus_eng_line_"):
            angle_fus_eng_tmp = self.copter.angle_fus_engine
            i = int(sender_name.replace("angle_fus_eng_line_", ""))
            angle_fus_eng_tmp[i] = sender_value / 180 * pi
            self.copter.angle_fus_engine = angle_fus_eng_tmp
        elif sender_name.startswith("fus_eng_q_line_"):
            sender_name_tmp = sender_name.replace("angle_fus_eng_line_", "")
            i = int(sender_name_tmp[:-1])
            j = int(sender_name_tmp[-1])
            fus_eng_q_tmp = self.copter.fus_engine_q[i]
            fus_eng_q_tmp[j] = sender_value
            self.copter.fus_engine_q[i] = fus_eng_q_tmp

        self._calc_maximum_speed()
        self.copter_changed.emit()
        return

    def _calc_maximum_speed(self):
        vx_line = self.findChild(QLineEdit, "vx_line")
        vy_line = self.findChild(QLineEdit, "vy_line")
        g = 9.8062

        if fabs(self.copter.aero_square) < 1e-10 or \
                fabs(self.copter.drag_coef[0]) < 1e-10 or \
                fabs(self.copter.drag_coef[1]) < 1e-10 or \
                fabs(self.copter.drag_coef[2]) < 1e-10:
            vx_line.setText("0.0")
            vy_line.setText("0.0")
            return

        engines_max_force = 0.0
        copter_mass = self.copter.fuselage.mass
        for engine in self.copter.engines:
            if engine.blade_diameter < 1e-10:
                vx_line.setText("0.0")
                vy_line.setText("0.0")
                return
            omega_max = engine.max_power / 2 / pi / engine.blade_coef_beta / 1.225 / \
                        engine.blade_diameter / engine.blade_diameter / engine.blade_diameter / \
                        engine.blade_diameter / engine.blade_diameter
            omega_max = pow(omega_max, 1 / 3)
            max_force = 2 * pi * engine.blade_coef_alpha * 1.225 * engine.blade_diameter * \
                        engine.blade_diameter * engine.blade_diameter * engine.blade_diameter * \
                        omega_max * omega_max
            engines_max_force += max_force
            copter_mass += engine.mass
        vy_max = 2 * (engines_max_force - copter_mass * g) / \
                 (self.copter.drag_coef[2] * 1.225 * self.copter.aero_square)
        if vy_max < 0:
            vx_line.setText("0.0")
            vy_line.setText("0.0")
            return
        vy_max = sqrt(vy_max)

        cx = min(self.copter.drag_coef[0], self.copter.drag_coef[1])
        cy = self.copter.drag_coef[2]

        alpha_max = acos(copter_mass * g / engines_max_force)
        if alpha_max < 1e-10:
            vx_line.setText("0.0")
            vy_line.setText(str(vy_max))
            return

        vx_max = 2 * copter_mass * g / 1.225 * self.copter.aero_square * \
                 self._find_min(cx, cy, alpha_max)
        vx_max = sqrt(vx_max)
        vx_line.setText(str(vx_max))
        vy_line.setText(str(vy_max))
        return

    def _find_min(self, cx, cy, alpha_max):
        f = lambda alpha: -tan(alpha) / (cx * cos(alpha) + cy * sin(alpha))
        diff = pi / 2 - alpha_max
        eps = diff / 1e6
        diff_step = diff / 1e6
        alpha_left = 0
        alpha_right = alpha_max
        alpha_cur = (0 + alpha_max) / 2
        alpha_w = alpha_cur
        alpha_v = alpha_cur
        f_cur = f(alpha_cur)
        f_w = f_cur
        f_v = f_cur
        df_cur = (f(alpha_cur + diff_step) - f(alpha_cur - diff_step)) / 2 / diff_step
        df_w = df_cur
        df_v = df_cur

        counter = 0
        u1 = 0
        u2 = 0
        search = True
        alpha_res = 0
        while search:
            u1_flag = False
            u2_flag = False
            if not fabs(alpha_cur - alpha_w) < 1e-6 and not fabs(df_cur - df_w) < 1e-6:
                u1 = alpha_w - df_w * (alpha_w - alpha_cur) / (df_w - df_cur)
                if alpha_left + eps <= u1 <= alpha_right - eps and fabs(u1 - alpha_cur) < diff / 2:
                    u1_flag = True
            if not fabs(alpha_cur - alpha_v) < 1e-6 and not fabs(df_cur - df_v) < 1e-6:
                u2 = alpha_v - df_v * (alpha_v - alpha_cur) / (df_v - df_cur)
                if alpha_left + eps <= u2 <= alpha_right - eps and fabs(u2 - alpha_cur) < diff / 2:
                    u2_flag = True
            if u1_flag or u2_flag:
                alpha_u = u1 * (u1_flag and not u2_flag) + u2 * (not u1_flag and u2_flag) + \
                          u1 * (u1_flag and u2_flag) * (fabs(u1 - alpha_cur) <= fabs(u2 - alpha_cur)) + \
                          u2 * (u1_flag and u2_flag) * (fabs(u1 - alpha_cur) > fabs(u2 - alpha_cur))
            else:
                if df_cur > 0:
                    alpha_u = (alpha_left + alpha_cur) / 2
                else:
                    alpha_u = (alpha_cur + alpha_right) / 2
            if fabs(alpha_u - alpha_cur) < eps or counter > 1000:
                alpha_res = alpha_u * (fabs(alpha_u) > 1e-10) + \
                            (alpha_cur + numpy.sign(alpha_u - alpha_cur) * eps) * (fabs(alpha_u) < 1e-10)
                search = False
            diff = fabs(alpha_cur - alpha_u)
            f_u = f(alpha_u)
            df_u = (f(alpha_u + diff_step) - f(alpha_u - diff_step)) / 2 / diff_step
            if f_u <= f_cur:
                if alpha_u >= alpha_cur:
                    alpha_left = alpha_cur
                else:
                    alpha_right = alpha_cur
                alpha_v = alpha_w
                alpha_w = alpha_cur
                alpha_cur = alpha_u
                f_v = f_w
                f_cur = f_u
                df_v = df_w
                df_w = df_cur
                df_cur = df_u
            else:
                if alpha_u >= alpha_cur:
                    alpha_right = alpha_u
                else:
                    alpha_left = alpha_u
                if f_u <= f_w or fabs(alpha_w - alpha_cur) < 1e-10:
                    alpha_v = alpha_w
                    alpha_w = alpha_u
                    f_v = f_w
                    f_w = f_u
                    df_v = df_w
                    df_w = df_u
                else:
                    if f_u <= f_v or \
                            fabs(alpha_v - alpha_cur) < 1e-10 or \
                            fabs(alpha_w - alpha_w) < 1e-10:
                        alpha_v = alpha_u
                        f_v = f_u
                        df_v = df_u
            counter += 1
        result = -f(alpha_res)
        # print(alpha_res / pi * 180)
        # print(alpha_max / pi * 180)
        return result
