from PyQt5.QtWidgets import QDialog, QSizePolicy, QGridLayout, \
    QLineEdit, QPushButton, QLabel, QCheckBox, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QIntValidator
from . import main_window

import os


class NewCopterDLG(QDialog):

    def __init__(self):
        super(NewCopterDLG, self).__init__()
        self.resize(100, 100)
        size_pol = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(size_pol)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setWindowIcon(QIcon(main_window.__icon_dir__ + 'newCopter.png'))
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        name_lbl = QLabel("Copter name")
        name_lbl.setObjectName("name_lbl")
        self.name_line = QLineEdit(self)
        self.name_line.setObjectName("name_line")
        self.name_line.textChanged.connect(self._activate_accept_b)

        numofeng_lbl = QLabel("Number of engines")
        numofeng_lbl.setObjectName("numofeng_lbl")
        self.numofeng_line = QLineEdit(self)
        self.numofeng_line.setObjectName("numofeng_line")
        numofeng_valid = QIntValidator()
        numofeng_valid.setBottom(4)
        self.numofeng_line.setValidator(numofeng_valid)
        self.numofeng_line.textChanged.connect(self._activate_accept_b)

        sym_check_lbl = QLabel("Symmetry construction")
        sym_check_lbl.setObjectName("sym_check_lbl")
        self.sym_check = QCheckBox()

        eng_check_lbl = QLabel("Engines equality")
        eng_check_lbl.setObjectName("eng_check_lbl")
        self.eng_check = QCheckBox()

        self.create = QPushButton(self)
        self.create.setObjectName("create_link")
        self.create.setEnabled(False)

        self.cancel = QPushButton(self)
        self.cancel.setObjectName("cancel_link")

        self.gridLayout.addWidget(name_lbl, 0, 0)
        self.gridLayout.addWidget(self.name_line, 0, 1, 1, 2)
        self.gridLayout.addWidget(numofeng_lbl, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.numofeng_line, 1, 2)
        self.gridLayout.addWidget(sym_check_lbl, 2, 0, 1, 2)
        self.gridLayout.addWidget(self.sym_check, 2, 2)
        self.gridLayout.addWidget(eng_check_lbl, 3, 0, 1, 2)
        self.gridLayout.addWidget(self.eng_check, 3, 2)
        self.gridLayout.addWidget(self.create, 4, 1)
        self.gridLayout.addWidget(self.cancel, 4, 2)

        self._retranslate_ui()
        self.cancel.clicked.connect(self.reject)
        self.create.clicked.connect(self._create_copter)
        self.returnName = None
        self.returnNum = None
        return

    def _activate_accept_b(self):
        num_of_eng_valid = self.numofeng_line.validator()
        valid = num_of_eng_valid.validate(self.numofeng_line.text(), 0)
        if self.name_line.text() and self.numofeng_line.text() and valid[0] == 2:
            self.create.setEnabled(True)
        else:
            self.create.setEnabled(False)
        return

    def _retranslate_ui(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Create copter"))
        self.create.setText(_translate("Dialog", "Create"))
        self.cancel.setText(_translate("Dialog", "Cancel"))
        return

    def _create_copter(self):
        if os.path.isfile(main_window.__copter_dir__ + self.name_line.text() + '.json'):
            overwrite_msg = "Copter with this name is already exist.\n" \
                            "Are you sure you want to overwrite it?"
            reply = QMessageBox.question(self, 'Message',
                                         overwrite_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        self.returnName = self.name_line.text()
        self.returnNum = int(self.numofeng_line.text())
        self.accept()
        return

    def exec_(self):
        super(NewCopterDLG, self).exec_()
        return self.returnName, self.returnNum, \
               self.sym_check.isChecked(), self.eng_check.isChecked()
