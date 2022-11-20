from .cleaner_thread import CleanerThread
from ..dcinside_cleaner import Cleaner
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

main_form = uic.loadUiType(resource_path('ui_main_window.ui'))[0]

class MainWindow(QtWidgets.QMainWindow, main_form):
    p_type_dict = { 'p': 'posting', 'c': 'comment' }
    captcha_signal = QtCore.pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.id = ''
        self.pw = ''
        self.g_list = []

        self.progress_cur = 0
        self.progress_max = 0

        self.cleaner_thread = CleanerThread(self.captcha_signal)
        self.cleaner = Cleaner(self.cleaner_thread)
        self.cleaner_thread.setCleaner(self.cleaner)

        self.cleaner_thread.event_signal.connect(self.deleteEvent)

        self.input_pw.returnPressed.connect(self.login)
        self.btn_login.clicked.connect(self.login)

        self.btn_get_posting.clicked.connect(lambda: self.getGallList('p'))
        self.btn_get_comment.clicked.connect(lambda: self.getGallList('c'))

        self.btn_start.clicked.connect(self.delete)

    @QtCore.pyqtSlot(dict)
    def deleteEvent(self, event):
        if event['type'] == 'pages':
            self.log('글 목록 가져오는 중...')
            self.progress_cur = 0
            self.progress_max = event['data']
            self.progress_bar.setValue(0)

        if event['type'] == 'posts':
            self.log(f'글 개수는 {event["data"]}개 입니다')
            self.log('글 삭제하는 중...')
            self.progress_cur = 0
            self.progress_max = event['data']
            self.progress_bar.setValue(0)

        if event['type'] in ('page_update', 'post_update'):
            self.progress_cur += 1
            self.progress_bar.setValue(int((self.progress_cur / self.progress_max) * 100))

        if event['type'] == 'ipblocked':
            self.log('IP 차단 감지')
            QtWidgets.QMessageBox.warning(self, '차단 안내', 'IP가 차단되었습니다.')

        if event['type'] == 'captcha':
            self.log('캡차 감지')
            QtWidgets.QMessageBox.information(self, '캡차 안내', '캡차가 감지되었습니다.\n갤로그에 접속해 캡차를 해제한 후 확인을 눌러주세요.')
            self.captcha_signal.emit(True)

        if event['type'] == 'complete':
            self.log('삭제 완료')
            QtWidgets.QMessageBox.information(self, '완료', '삭제 작업이 완료되었습니다.')
            self.progress_cur = 0
            self.progress_max = 0
            self.progress_bar.setValue(0)
            self.group_box_gall.setEnabled(True)
            self.btn_start.setEnabled(True)
            self.combo_box_gall.clear()
            self.cleaner_thread.quit()
            self.g_list = []

    def log(self, text):
        self.box_log.append(text)
        self.statusBar().showMessage(text, 1500)

    def setCursorWait(self):
        QtGui.QGuiApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def restoreCursor(self):
        QtGui.QGuiApplication.restoreOverrideCursor()

    def login(self):
        self.id = self.input_id.text()
        self.pw = self.input_pw.text()
        self.log('로그인 중...')
        self.setCursorWait()
        res = self.cleaner.login(self.id, self.pw)
        self.restoreCursor()
        if res:
            self.log('로그인 성공')
            QtWidgets.QMessageBox.information(self, '로그인 안내', '로그인되었습니다')
            self.group_box_login.setEnabled(False)
        else:
            self.log('로그인 실패')
            QtWidgets.QMessageBox.warning(self, '로그인 안내', '로그인에 실패했습니다.')

    def getGallList(self, post_type):
        self.combo_box_gall.clear()
        self.g_list = []
        self.setCursorWait()
        self.p_type = self.p_type_dict[post_type]
        self.log('갤러리 목록 가져오는 중...')
        gall_list = self.cleaner.getGallList(self.p_type)
        idx = 0
        for gno in gall_list:
            self.g_list.append(gno)
            self.combo_box_gall.addItem(f'{idx + 1}. {gall_list[gno]}')
            idx += 1
        self.restoreCursor()

    def delete(self):
        if not self.g_list:
            return QtWidgets.QMessageBox.warning(self, '안내', '글 또는 댓글 목록을 불러온 후 삭제해 주세요.')
        elif self.checkbox_gall_all.isChecked():
            self.cleaner_thread.setDelInfo(self.g_list, self.p_type)
        else:
            idx = self.combo_box_gall.currentIndex()
            self.cleaner_thread.setDelInfo([self.g_list[idx]], self.p_type)
        self.group_box_gall.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.cleaner_thread.start()

def execute():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()