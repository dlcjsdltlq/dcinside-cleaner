from PyQt5 import QtWidgets, QtCore, QtGui, uic
from ..dcinside_cleaner import Cleaner
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

main_form = uic.loadUiType(resource_path('./ui_main_window.ui'))[0]

class MainWindow(QtWidgets.QMainWindow, main_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

def execute():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()