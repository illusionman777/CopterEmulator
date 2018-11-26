from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, \
                            QLineEdit, QVBoxLayout, QFileDialog, \
                            QScrollArea, QCheckBox, QPushButton
from PyQt5.QtGui import QFont, QDoubleValidator, QPalette, QColor, QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal
from .settings import Settings
from . import main_window
import os


class SimSettingsWidget(QWidget):
    settings = Settings
    settings_changed = pyqtSignal()

    def __init__(self, tab_wadget):
        super(SimSettingsWidget, self).__init__(tab_wadget)
        widget_font = QFont("Times", 10)
        self.setFont(widget_font)
        self.settings = tab_wadget.settings
        self._init_ui()
        self._set_ui()
        return

    def _init_ui(self):
        name_lbl = QLabel(self)
        name_lbl.setText("Simulation settings")
        name_lbl.setObjectName("name_lbl")
        name_font = QFont("Times", 14, QFont.Bold)
        name_lbl.setFont(name_font)
        name_lbl.setAlignment(Qt.AlignCenter)

        contr_freq_lbl = QLabel(self)
        contr_freq_lbl.setText("Controller work frequency, [Hz]:")
        contr_freq_lbl.setObjectName("contr_freq_lbl")
        contr_freq_line = QLineEdit(self)
        contr_freq_line.setObjectName("contr_freq_line")

        dt_lbl = QLabel(self)
        dt_lbl.setText("Time step, dt [s]:")
        dt_lbl.setObjectName("dt_lbl")
        dt_line = QLineEdit(self)
        dt_line.setObjectName("dt_line")

        graph_enabled_lbl = QLabel(self)
        graph_enabled_lbl.setText("Enable graphics and visualization")
        graph_enabled_lbl.setObjectName("graph_enabled_lbl")
        graph_enabled_chbx = QCheckBox(self)
        graph_enabled_chbx.setObjectName("graph_enabled_chbx")

        view3d_enabled_lbl = QLabel(self)
        view3d_enabled_lbl.setText("        Enable 3D graphics")
        view3d_enabled_lbl.setObjectName("view3d_enabled_lbl")
        view3d_enabled_chbx = QCheckBox(self)
        view3d_enabled_chbx.setObjectName("view3d_enabled_chbx")

        vert_syncr_lbl = QLabel(self)
        vert_syncr_lbl.setText("        Vertical synchronization")
        vert_syncr_lbl.setObjectName("vert_syncr_lbl")
        vert_syncr_chbx = QCheckBox(self)
        vert_syncr_chbx.setObjectName("vert_syncr_chbx")

        ground_collision_lbl = QLabel(self)
        ground_collision_lbl.setText("Ground collision. Stop the simulation at collision")
        ground_collision_lbl.setObjectName("ground_collision_lbl")
        ground_collision_chbx = QCheckBox(self)
        ground_collision_chbx.setObjectName("ground_collision_chbx")

        ground_level_lbl = QLabel(self)
        ground_level_lbl.setText("        Ground level Z, [m]:")
        ground_level_lbl.setObjectName("ground_level_lbl")
        ground_level_line = QLineEdit(self)
        ground_level_line.setObjectName("ground_level_line")

        real_time_syncr_lbl = QLabel(self)
        real_time_syncr_lbl.setText("Run simulation in real-time mode")
        real_time_syncr_lbl.setObjectName("real_time_syncr_lbl")
        real_time_syncr_chbx = QCheckBox(self)
        real_time_syncr_chbx.setObjectName("real_time_syncr_chbx")

        log_enabled_lbl = QLabel(self)
        log_enabled_lbl.setText("Write log of copter position")
        log_enabled_lbl.setObjectName("log_enabled_lbl")
        log_enabled_chbx = QCheckBox(self)
        log_enabled_chbx.setObjectName("log_enabled_chbx")

        log_inf_lbl = QLabel(self)
        log_inf_lbl.setText("        Write log during all simulation time")
        log_inf_lbl.setObjectName("log_inf_lbl")
        log_inf_chbx = QCheckBox(self)
        log_inf_chbx.setObjectName("log_inf_chbx")

        log_time_lbl = QLabel(self)
        log_time_lbl.setText("        Maximum log duration, [s]:")
        log_time_lbl.setObjectName("log_time_lbl")
        log_time_lbl.setToolTip("When the set time is exceeded\n"
                                "log will delete first recording\n"
                                "and add new one")
        log_time_line = QLineEdit(self)
        log_time_line.setObjectName("log_time_line")
        log_time_line.setToolTip("Time format: HH:MM:SS")

        log_file_lbl = QLabel(self)
        log_file_lbl.setText("        Current log file:")
        log_file_lbl.setObjectName("log_file_lbl")
        log_file_line = QLineEdit(self)
        log_file_line.setObjectName("log_file_line")
        log_file_line.setReadOnly(True)
        log_file_btn = QPushButton(self)
        log_file_btn.setObjectName("log_file_btn")
        log_file_btn.setText("Change")
        log_file_btn.clicked.connect(self._new_log_file)

        dest_pos_lbl = QLabel(self)
        dest_pos_lbl.setText("Copter destination position, [m]:")
        dest_pos_lbl.setObjectName("dest_pos_lbl")

        for i in range(3):
            dest_pos_line = QLineEdit(self)
            dest_pos_line.setObjectName("dest_pos_line_{}".format(i))

        dest_q_lbl = QLabel(self)
        dest_q_lbl.setText("Copter destination rotation quaternion:")
        dest_q_lbl.setObjectName("dest_q_lbl")

        for i in range(4):
            dest_q_line = QLineEdit(self)
            dest_q_line.setObjectName("dest_q_line_{}".format(i))

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

        contr_freq_lbl = self.findChild(QLabel, "contr_freq_lbl")
        contr_freq_line = self.findChild(QLineEdit, "contr_freq_line")
        contr_freq_line.setText(str(self.settings.controller_freq))

        dt_lbl = self.findChild(QLabel, "dt_lbl")
        dt_line = self.findChild(QLineEdit, "dt_line")
        dt_line.setText(str(self.settings.dt))

        graph_enabled_lbl = self.findChild(QLabel, "graph_enabled_lbl")
        graph_enabled_chbx = self.findChild(QCheckBox, "graph_enabled_chbx")
        graph_enabled_chbx.setChecked(self.settings.graphics_enabled)

        view3d_enabled_lbl = self.findChild(QLabel, "view3d_enabled_lbl")
        view3d_enabled_chbx = self.findChild(QCheckBox, "view3d_enabled_chbx")
        view3d_enabled_chbx.setChecked(self.settings.view3d_enabled)

        vert_syncr_lbl = self.findChild(QLabel, "vert_syncr_lbl")
        vert_syncr_chbx = self.findChild(QCheckBox, "vert_syncr_chbx")
        vert_syncr_chbx.setChecked(self.settings.vert_syncr)
        if not self.settings.graphics_enabled:
            view3d_enabled_chbx.setEnabled(False)
            vert_syncr_chbx.setEnabled(False)

        ground_collision_lbl = self.findChild(QLabel, "ground_collision_lbl")
        ground_collision_chbx = self.findChild(QCheckBox, "ground_collision_chbx")
        ground_collision_chbx.setChecked(self.settings.ground_collision)

        ground_level_lbl = self.findChild(QLabel, "ground_level_lbl")
        ground_level_line = self.findChild(QLineEdit, "ground_level_line")
        ground_level_line.setText(str(self.settings.ground_level))

        real_time_syncr_lbl = self.findChild(QLabel, "real_time_syncr_lbl")
        real_time_syncr_chbx = self.findChild(QCheckBox, "real_time_syncr_chbx")
        real_time_syncr_chbx.setChecked(self.settings.real_time_syncr)

        log_enabled_lbl = self.findChild(QLabel, "log_enabled_lbl")
        log_enabled_chbx = self.findChild(QCheckBox, "log_enabled_chbx")
        log_enabled_chbx.setChecked(self.settings.log_enabled)

        log_inf_lbl = self.findChild(QLabel, "log_inf_lbl")
        log_inf_chbx = self.findChild(QCheckBox, "log_inf_chbx")
        log_inf_chbx.setChecked(self.settings.log_inf)

        log_time_lbl = self.findChild(QLabel, "log_time_lbl")
        log_time_line = self.findChild(QLineEdit, "log_time_line")
        hours = str(self.settings.log_time // 3600)
        minutes = str((self.settings.log_time % 3600) // 60)
        seconds = str((self.settings.log_time % 3600) % 60)
        if len(hours) == 1:
            hours = "0" + hours
        if len(minutes) == 1:
            minutes = "0" + minutes
        if len(seconds) == 1:
            seconds = "0" + seconds
        log_time_line.setText(str(hours) + ":" + str(minutes) + ":" + str(seconds))
        if not self.settings.log_enabled:
            log_inf_chbx.setEnabled(False)
            log_time_line.setEnabled(False)

        log_file_lbl = self.findChild(QLabel, "log_file_lbl")
        log_file_line = self.findChild(QLineEdit, "log_file_line")
        log_file_line.setText(str(self.settings.log_file))
        log_file_btn = self.findChild(QPushButton, "log_file_btn")

        dest_pos_lbl = self.findChild(QLabel, "dest_pos_lbl")
        vector_w = QWidget(text_w)
        vector_grid = QGridLayout(vector_w)

        for i in range(3):
            dest_pos_line = self.findChild(QLineEdit, "dest_pos_line_{}".format(i))
            dest_pos_line.setText(str(self.settings.dest_pos[i]))
            vector_grid.addWidget(dest_pos_line, i, 0)

        dest_q_lbl = self.findChild(QLabel, "dest_q_lbl")
        quaternion_w = QWidget(text_w)
        quaternion_grid = QGridLayout(quaternion_w)

        for i in range(4):
            dest_q_line = self.findChild(QLineEdit, "dest_q_line_{}".format(i))
            dest_q_line.setText(str(self.settings.dest_q[i]))
            quaternion_grid.addWidget(dest_q_line, i, 0)

        text_grid.addWidget(contr_freq_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(contr_freq_line, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(dt_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(dt_line, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(graph_enabled_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(graph_enabled_chbx, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(view3d_enabled_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(view3d_enabled_chbx, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(vert_syncr_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(vert_syncr_chbx, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(ground_collision_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(ground_collision_chbx, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(ground_level_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(ground_level_line, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(real_time_syncr_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(real_time_syncr_chbx, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(log_enabled_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(log_enabled_chbx, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(log_inf_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(log_inf_chbx, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(log_time_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(log_time_line, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(log_file_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(log_file_btn, grid_row, 2, 2, 1)
        grid_row += 1
        text_grid.addWidget(log_file_line, grid_row, 0, 1, 2)
        grid_row += 1
        text_grid.addWidget(dest_pos_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(vector_w, grid_row, 2)
        grid_row += 1
        text_grid.addWidget(dest_q_lbl, grid_row, 0, 1, 2)
        text_grid.addWidget(quaternion_w, grid_row, 2)
        grid_row += 1
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
            if line_name == "log_time_line":
                line_edit.setInputMask("99:99:99;_")
            elif line_name == "contr_freq_line":
                int_valid = QIntValidator()
                int_valid.setBottom(1)
                line_edit.setValidator(int_valid)
            elif line_name == "dt_line":
                valid = QDoubleValidator()
                valid.setBottom(0.)
                line_edit.setValidator(valid)
            else:
                line_edit.setValidator(double_valid)
            line_edit.textEdited.connect(self._change_settings)

        for check_box in self.findChildren(QCheckBox):
            check_box.stateChanged.connect(self._change_settings)
        return

    def _new_log_file(self):
        dialog = QFileDialog()
        dialog.setNameFilters(["JSON files (*.json)", "All Files (*)"])
        dialog.selectNameFilter("JSON files (*.json)")
        dialog.setDirectory(os.path.dirname(main_window.__logs_dir__))
        _open = dialog.exec_()
        if _open:
            copter_file = dialog.selectedFiles()
            self.settings.log_file = str(copter_file[0])
            log_file_line = self.findChild(QLineEdit, "log_file_line")
            log_file_line.setText(self.settings.log_file)
            self.settings_changed.emit()
        return

    def _change_settings(self):
        sender_w = self.sender()
        if isinstance(sender_w, QCheckBox):
            sender_value = sender_w.isChecked()
        else:
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

        if sender_name == "contr_freq_line":
            self.settings.controller_freq = sender_value
        elif sender_name == "dt_line":
            self.settings.dt = sender_value
        elif sender_name == "graph_enabled_chbx":
            self.settings.graphics_enabled = sender_value
            view3d_enabled_chbx = self.findChild(QCheckBox, "view3d_enabled_chbx")
            vert_syncr_chbx = self.findChild(QCheckBox, "vert_syncr_chbx")
            if sender_value:
                view3d_enabled_chbx.setEnabled(True)
                vert_syncr_chbx.setEnabled(True)
            else:
                view3d_enabled_chbx.setEnabled(False)
                vert_syncr_chbx.setEnabled(False)
        elif sender_name == "view3d_enabled_chbx":
            self.settings.view3d_enabled = sender_value
        elif sender_name == "vert_syncr_chbx":
            self.settings.vert_syncr = sender_value
        elif sender_name == "ground_collision_chbx":
            self.settings.ground_collision = sender_value
            ground_level_line = self.findChild(QLineEdit, "ground_level_line")
            if sender_value:
                ground_level_line.setEnabled(True)
            else:
                ground_level_line.setEnabled(False)
        elif sender_name == "ground_level_line":
            self.settings.ground_level = sender_value
        elif sender_name == "real_time_syncr_chbx":
            self.settings.real_time_syncr = sender_value
        elif sender_name == "log_enabled_chbx":
            self.settings.log_enabled = sender_value
            log_inf_chbx = self.findChild(QCheckBox, "log_inf_chbx")
            log_time_line = self.findChild(QLineEdit, "log_time_line")
            if sender_value and log_inf_chbx.isChecked():
                log_inf_chbx.setEnabled(True)
            elif sender_value:
                log_inf_chbx.setEnabled(True)
                log_time_line.setEnabled(True)
            else:
                log_inf_chbx.setEnabled(False)
                log_time_line.setEnabled(False)
        elif sender_name == "log_inf_chbx":
            self.settings.log_inf = sender_value
            log_time_line = self.findChild(QLineEdit, "log_time_line")
            if sender_value:
                log_time_line.setEnabled(False)
            else:
                log_time_line.setEnabled(True)
        elif sender_name == "log_time_line":
            sender_value = sender_value.split(":")
            try:
                hours = int(sender_value[0])
                minutes = int(sender_value[1])
                seconds = int(sender_value[2])
            except ValueError:
                hours = 0
                minutes = 0
                seconds = 0
            self.settings.log_time = 3600 * hours + \
                                     60 * minutes + \
                                     seconds
        elif sender_name.startswith("dest_pos_line_"):
            i = int(sender_name.replace("dest_pos_line_", ""))
            self.settings.dest_pos[i] = sender_value
        elif sender_name.startswith("dest_q_line_"):
            i = int(sender_name.replace("dest_q_line_", ""))
            self.settings.dest_q[i] = sender_value

        self.settings_changed.emit()
        return
