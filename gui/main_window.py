from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction, \
                            QMenuBar, QToolBar, QFileDialog, QMessageBox, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from .new_copter_dlg import NewCopterDLG
from .settings import Settings
from .copter_settings_widget import CopterSettingsWidget
from .sim_settings_tab_widget import SimSettingsTabWidget
from .graphics_widget import GraphicsWidget
from .copter3d_widget import Copter3DWidget

import sys
import os
import json_serializer
import physicalmodel as model

__icon_dir__ = os.path.dirname(os.path.realpath(__file__)) + \
                   os.path.sep + 'icons' + os.path.sep
__copter_dir__ = os.path.dirname(os.path.realpath(sys.argv[0])) + \
                 os.path.sep + 'copters' + os.path.sep
__logs_dir__ = os.path.dirname(os.path.realpath(sys.argv[0])) + \
               os.path.sep + 'logs' + os.path.sep
__settings_path__ = os.path.dirname(os.path.realpath(sys.argv[0])) + \
                    os.path.sep + 'settings.json'


class MainWindow(QMainWindow):

    main_menu = QMenuBar
    toolbar = QToolBar
    copter = model.Copter
    settings = Settings
    copter_settings = CopterSettingsWidget
    sim_settings = SimSettingsTabWidget
    simulation = GraphicsWidget

    def __init__(self):
        super(MainWindow, self).__init__()
        self._init_gui()
        return

    def _init_gui(self):
        self.setWindowTitle('Copter flight simulator')
        self._init_size()
        self._center_window()
        self.setWindowIcon(QIcon(__icon_dir__ + 'icon.png'))
        self._init_mainmenu()
        self._init_toolbar()
        try:
            self.settings = Settings.load()
        except FileNotFoundError:
            self.settings = Settings()
            self.settings.save()
        finally:
            if os.path.isfile(self.settings.current_copter):
                self.copter = json_serializer.readfile(self.settings.current_copter)
                self._init_copter_settings()
                save_as_act = self.findChild(QAction, "save_as_menu")
                save_as_act.setEnabled(True)
            else:
                self.copter_settings = None
                self.sim_settings = None
                self.simulation = None
                self._disable_toolbar()
            self.statusBar().showMessage('Ready')
            self.show()
        return

    def _init_size(self):
        desk_width = QDesktopWidget().availableGeometry().width()
        desk_height = QDesktopWidget().availableGeometry().height()
        window_width = desk_width // 1.5
        window_height = desk_height // 1.5
        self.resize(window_width, window_height)
        return

    def _center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        return

    def _init_mainmenu(self):
        self.main_menu = self.menuBar()
        file_menu = self.main_menu.addMenu('File')

        new_copter_act = QAction('New Copter...', self)
        new_copter_act.setObjectName("new_copter_menu")
        new_copter_act.setStatusTip('Create new Copter')
        new_copter_act.triggered.connect(self._new_copter)

        open_copter_act = QAction(QIcon(__icon_dir__ + 'openFile.png'),
                                  'Open...', self)
        open_copter_act.setObjectName("open_copter_menu")
        open_copter_act.setStatusTip('Open Copter')
        open_copter_act.triggered.connect(self._open_copter)

        save_act = QAction(QIcon(__icon_dir__ + 'saveCopter.png'),
                           'Save', self)
        save_act.setObjectName("save_act_menu")
        save_act.setStatusTip('Save copter changes')
        save_act.triggered.connect(self._save_copter)
        save_act.setEnabled(False)

        save_as_act = QAction(QIcon(__icon_dir__ + 'saveAs.png'),
                           'Save As...', self)
        save_as_act.setObjectName("save_as_menu")
        save_as_act.setStatusTip('Save current copter as JSON file')
        save_as_act.triggered.connect(self._save_copter_as)
        save_as_act.setEnabled(False)

        exit_act = QAction('Exit', self)
        exit_act.setObjectName("exit_menu")
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit application')
        exit_act.triggered.connect(self.close)

        file_menu.addAction(new_copter_act)
        file_menu.addAction(open_copter_act)
        file_menu.addAction(save_act)
        file_menu.addAction(save_as_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)
        return

    def _init_toolbar(self):
        new_copter_act = QAction(QIcon(__icon_dir__ + 'newCopter.png'),
                                 'New Copter', self)
        new_copter_act.setObjectName("new_copter_tlb")
        new_copter_act.setStatusTip('Create new copter')
        new_copter_act.triggered.connect(self._new_copter)

        edit_copter_act = QAction(QIcon(__icon_dir__ + 'editCopter.png'),
                                  'Edit Copter', self)
        edit_copter_act.setObjectName("edit_copter_tlb")
        edit_copter_act.setStatusTip('Edit current copter')
        edit_copter_act.triggered.connect(self._open_copter_settings)

        save_copter_act = QAction(QIcon(__icon_dir__ + 'saveCopter.png'),
                                  'Save Copter', self)
        save_copter_act.setObjectName("save_copter_tlb")
        save_copter_act.setStatusTip('Save current copter')
        save_copter_act.triggered.connect(self._save_copter)
        save_copter_act.setEnabled(False)

        delete_copter_act = QAction(QIcon(__icon_dir__ + 'deleteCopter.png'),
                                    'Delete Copter', self)
        delete_copter_act.setObjectName("delete_copter_tlb")
        delete_copter_act.setStatusTip('Delete current copter')
        delete_copter_act.triggered.connect(self._delete_copter)

        edit_sim_act = QAction(QIcon(__icon_dir__ + 'editSimulation.png'),
                               'Settings', self)
        edit_sim_act.setObjectName("edit_sim_tlb")
        edit_sim_act.setStatusTip('Edit simulation settings')
        edit_sim_act.triggered.connect(self._open_sim_settings)

        show_sim_act = QAction(QIcon(__icon_dir__ + 'simulationControl.png'),
                               'Simulation control', self)
        show_sim_act.setObjectName("show_sim_tlb")
        show_sim_act.setStatusTip('Show simulation process')
        show_sim_act.triggered.connect(self._open_simulation)

        self.toolbar = self.addToolBar('New copter')
        self.toolbar.addAction(new_copter_act)
        self.toolbar.addAction(edit_copter_act)
        self.toolbar.addAction(save_copter_act)
        self.toolbar.addAction(delete_copter_act)
        self.toolbar.addSeparator()
        self.toolbar.addAction(edit_sim_act)
        self.toolbar.addAction(show_sim_act)

        self.toolbar.setMovable(False)
        tb_iconsize = QSize(75, 75)
        self.toolbar.setIconSize(tb_iconsize)
        return

    def _init_copter_settings(self):
        if self.centralWidget():
            self.centralWidget().close()
            self.takeCentralWidget()
        if isinstance(self.simulation, GraphicsWidget):
            copter3d_w = self.simulation.findChildren(Copter3DWidget)[0]
            copter3d_w.cleanup_vbo()
        copter_settings_w = self.findChildren(CopterSettingsWidget)
        if copter_settings_w:
            for widget in copter_settings_w:
                widget.destroy()
        sim_settings_w = self.findChildren(SimSettingsTabWidget)
        if sim_settings_w:
            for widget in sim_settings_w:
                widget.destroy()
        simulation_w = self.findChildren(GraphicsWidget)
        if simulation_w:
            for widget in simulation_w:
                widget.destroy()
        self.copter_settings = CopterSettingsWidget(self)
        self.copter_settings.copter_changed.connect(self._copter_changed)
        self.copter_settings.widget_closed.connect(self._unsaved_changes)
        self.copter_settings.hide()
        self.sim_settings = SimSettingsTabWidget(self)
        self.sim_settings.hide()
        self.simulation = GraphicsWidget(self)
        self.simulation.simulation_started.connect(self._disable_actions)
        self.simulation.simulation_stopped.connect(self._enable_actions)
        self.simulation.hide()
        show_sim_tlb = self.findChild(QAction, "show_sim_tlb")
        show_sim_tlb.trigger()
        return

    def _disable_actions(self):
        file_menu = self.main_menu.findChildren(QMenu)[0]
        for action in file_menu.actions():
            if action.text() == 'File' or \
                    action.text() == 'Exit':
                continue
            else:
                action.setEnabled(False)
        for action in self.toolbar.actions():
            if action.text() == 'Simulation control' or \
                    action.objectName() == "start_act" or \
                    action.objectName() == "pause_act" or \
                    action.objectName() == "stop_act":
                continue
            else:
                action.setEnabled(False)
        return

    def _enable_actions(self):
        file_menu = self.main_menu.findChildren(QMenu)[0]
        for action in file_menu.actions():
            if action.text() == 'Save':
                continue
            else:
                action.setEnabled(True)
        for action in self.findChildren(QAction):
            if action.objectName() == "save_copter_tlb" or \
                    action.objectName() == "start_act" or \
                    action.objectName() == "pause_act" or \
                    action.objectName() == "stop_act" or \
                    action.text() == 'Save':
                continue
            else:
                action.setEnabled(True)
        return

    def _disable_toolbar(self):
        for action in self.toolbar.actions():
            if action.text() == 'New Copter':
                continue
            else:
                action.setEnabled(False)
        return

    def _enable_toolbar(self):
        for action in self.toolbar.actions():
            if not action.objectName() == "save_copter_tlb":
                action.setEnabled(True)
        return

    def _new_copter(self):
        if self.centralWidget():
            self.centralWidget().close()
            self.takeCentralWidget()
        dialog = NewCopterDLG()
        value = dialog.exec_()
        if value[0]:
            self.copter = model.Copter()
            [name,
             num_of_engines,
             symmetry,
             equal_engines] = value
            self.copter.name = name
            self.copter.num_of_engines = num_of_engines
            self.copter.symmetry = symmetry
            self.copter.equal_engines = equal_engines
            file_path = __copter_dir__ + self.copter.name + '.json'
            json_serializer.writefile(file_path, self.copter)
            self.settings.current_copter = file_path
            self.settings.hover_mod_on_start = False
            self.settings.save()
            self._init_copter_settings()
            self._enable_toolbar()
            save_as_act = self.findChild(QAction, "save_as_menu")
            if not save_as_act.isEnabled():
                save_as_act.setEnabled(True)
        return

    def _open_copter(self):
        dialog = QFileDialog()
        dialog.setNameFilters(["JSON files (*.json)", "All Files (*)"])
        dialog.selectNameFilter("JSON files (*.json)")
        dialog.setDirectory(os.path.dirname(__copter_dir__))
        _open = dialog.exec_()
        if _open:
            copter_file = dialog.selectedFiles()
            self.copter = json_serializer.readfile(copter_file[0])
            self.settings.current_copter = copter_file[0]
            self.settings.hover_mod_on_start = False
            self.settings.save()
            self._init_copter_settings()
            self._enable_toolbar()
            save_as_act = self.findChild(QAction, "save_as_menu")
            save_as_act.setEnabled(True)
        return

    def _save_copter(self):
        copter_file = __copter_dir__ + self.copter.name + '.json'
        json_serializer.writefile(copter_file, self.copter)
        save_btn = self.findChild(QAction, "save_copter_tlb")
        save_btn.setEnabled(False)
        save_menu = self.findChild(QAction, "save_act_menu")
        save_menu.setEnabled(False)
        copter3d_w = self.simulation.findChildren(Copter3DWidget)[0]
        copter3d_w.cleanup_vbo()
        copter3d_w.load_objects3d()
        return

    def _save_copter_as(self):
        dialog = QFileDialog()
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(["JSON files (*.json)", "All Files (*)"])
        dialog.selectNameFilter("JSON files (*.json)")
        dialog.setDefaultSuffix("*.json")
        dialog.setDirectory(os.path.dirname(__copter_dir__))
        save = dialog.exec_()
        if save:
            copter_file = dialog.selectedFiles()
            copter_name = copter_file[0].split("/")[-1]
            copter_name = copter_name.split(".")[0]
            if not self.copter.name == copter_name:
                rename_msg = "Rename current copter to '{}'?".format(copter_name)
                reply = QMessageBox.question(self, 'Message',
                                             rename_msg, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.copter.name = copter_name
                    self._init_copter_settings()
            json_serializer.writefile(copter_file[0], self.copter)
            self.settings.current_copter = copter_file[0]
            self.settings.save()
            self._open_copter_settings()
        return

    def _delete_copter(self):
        del_msg = "Are you sure you want to delete '{}'?".format(self.copter.name)
        reply = QMessageBox.question(self, 'Message',
                                     del_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            os.remove(self.settings.current_copter)
            self.copter = model.Copter
            self.settings.current_copter = 'None'
            self.copter_settings = None
            if self.centralWidget():
                self.takeCentralWidget()
                self.setCentralWidget(None)
            self._disable_toolbar()
            save_as_act = self.findChild(QAction, "save_as_menu")
            save_as_act.setEnabled(False)
        return

    def _open_copter_settings(self):
        if isinstance(self.centralWidget(), CopterSettingsWidget):
            return
        if self.centralWidget():
            self.centralWidget().close()
            self.takeCentralWidget()
        self.setCentralWidget(self.copter_settings)
        self.copter_settings.show()
        return

    def _open_sim_settings(self):
        if isinstance(self.centralWidget(), SimSettingsTabWidget):
            return
        if self.centralWidget():
            self.centralWidget().close()
            self.takeCentralWidget()
        self.setCentralWidget(self.sim_settings)
        self.sim_settings.show()
        return

    def _open_simulation(self):
        if isinstance(self.centralWidget(), GraphicsWidget):
            return
        if self.centralWidget():
            self.centralWidget().close()
            self.takeCentralWidget()
        self.setCentralWidget(self.simulation)
        self.simulation.show()
        return

    def _copter_changed(self):
        save_btn = self.findChild(QAction, "save_copter_tlb")
        save_menu = self.findChild(QAction, "save_act_menu")
        if not save_btn.isEnabled():
            save_btn.setEnabled(True)
            save_menu.setEnabled(True)
        return

    def _unsaved_changes(self):
        save_btn = self.findChild(QAction, "save_copter_tlb")
        if save_btn.isEnabled():
            save_msg = "You have unsaved changes in '{0}'.\n" \
                       "Leaving this window will reduce them.\n" \
                       "Save '{0}' now?".format(self.copter.name)
            reply = QMessageBox.question(self, 'Message',
                                         save_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self._save_copter()
            else:
                self.copter = json_serializer.readfile(self.settings.current_copter)
                self._init_copter_settings()
            save_btn = self.findChild(QAction, "save_copter_tlb")
            save_btn.setEnabled(False)
            save_menu = self.findChild(QAction, "save_act_menu")
            save_menu.setEnabled(False)
        return

    def closeEvent(self, *args, **kwargs):
        if not self.simulation:
            return
        if self.simulation.simulation_running:
            save_msg = "Simulation is running.\n" \
                       "Do you want to stop simulation and quit?"
            reply = QMessageBox.question(self, 'Message',
                                         save_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                args[0].ignore()
                return
            else:
                self.simulation.stop_simulation()
        if isinstance(self.simulation, GraphicsWidget):
            copter3d_w = self.simulation.findChildren(Copter3DWidget)[0]
            copter3d_w.cleanup_all()
        return
