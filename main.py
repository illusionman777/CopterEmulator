import sys
from CopterEmulator.gui import main_window
from PyQt5.QtWidgets import QApplication

sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = exception_hook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = main_window.MainWindow()
    app.exec_()
