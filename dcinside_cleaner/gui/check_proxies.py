from ..proxy_checker import ProxyChecker
from .utils import resource_path
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import json

proxies_check_form = uic.loadUiType(resource_path('./resources/ui/ui_proxies_check_window.ui'))[0]

PROXY_AVAILABLE_DELAY = 1

class ProxyCheckWindow(QtWidgets.QDialog, proxies_check_form):
    available_proxy_list_signal  = QtCore.pyqtSignal(list)

    def __init__(self, proxy_list):
        super().__init__()
        self.setupUi(self)

        self.check_thread : ProxyThread

        self.proxy_list = proxy_list
        self.proxy_count = len(proxy_list)

        self.available_list = []

        self.proxy_checker = ProxyChecker()
        self.proxy_checker.setCheckURL('https://www.dcinside.com/')

        self.btn_save_proxies.setEnabled(False)
        self.btn_save_proxies.clicked.connect(self.exportProxyList)

        self.quit = QtWidgets.QAction('Quit', self)
        self.quit.triggered.connect(self.handleQuit)

        self.initProxyTable()

        self.runThread()

    def handleQuit(self, event):
        if self.check_thread:
            self.check_thread.quit()

        event.accept()

    def initProxyTable(self):
        table_labels = ['IP', '포트', '딜레이', '사용가능여부']
        self.proxy_table.setColumnCount(len(table_labels)) # ip port delay available
        self.proxy_table.setHorizontalHeaderLabels(table_labels)
        self.proxy_table.setRowCount(self.proxy_count)
        self.proxy_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        for idx, proxy in enumerate(self.proxy_list):
            proxy = proxy.split(':')
            self.proxy_table.setItem(idx, 0, QtWidgets.QTableWidgetItem(proxy[0]))
            self.proxy_table.setItem(idx, 1, QtWidgets.QTableWidgetItem(proxy[1]))
            self.proxy_table.setItem(idx, 2, QtWidgets.QTableWidgetItem('-'))
            self.proxy_table.setItem(idx, 3, QtWidgets.QTableWidgetItem('-'))

    def runThread(self):
        self.check_thread = ProxyThread(self.proxy_list)
        self.check_thread.proxy_info_signal.connect(self.checkProxy)
        self.check_thread.check_complete_signal.connect(self.completeCheck)
        self.check_thread.start()

    @QtCore.pyqtSlot(list)
    def checkProxy(self, result):
        idx, status, delay, proxy = result

        if status:
            self.available_list.append(proxy)
            self.proxy_table.setItem(idx, 2, QtWidgets.QTableWidgetItem(str(round(delay, 1)) + 'sec'))

        item = QtWidgets.QTableWidgetItem(status and '✓' or '✗')
        color = status and (0, 255, 0) or (255, 0, 0)
        item.setForeground(QtGui.QBrush(QtGui.QColor(*color)))
        self.proxy_table.setItem(idx, 3, item)
        index = self.proxy_table.model().index(idx, 0)
        self.proxy_table.scrollTo(index)

    @QtCore.pyqtSlot(bool)
    def completeCheck(self):
        self.available_proxy_list_signal.emit(self.available_list)
        self.btn_save_proxies.setEnabled(True)

    def exportProxyList(self):
        time = str(datetime.today())
        export_content = {
            "title": "dcinside_cleaner_proxy_list",
            "create_date": time,
            "data": self.available_list
        }

        export_content_json = json.dumps(export_content)
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', f'./dcinside_cleaner_proxy_list.json', 'JSON files (*.json)')

        try:
            with open(name[0], 'w') as file:
                file.write(export_content_json)
            QtWidgets.QMessageBox.information(self, '저장 완료', '파일 저장이 완료되었습니다.')
        except: pass



class ProxyThread(QtCore.QThread):
    proxy_info_signal = QtCore.pyqtSignal(list)
    check_complete_signal = QtCore.pyqtSignal(bool)

    def __init__(self, proxy_list):
        super().__init__()
        self.proxy_list = proxy_list
        self.proxy_checker = ProxyChecker()
        self.proxy_checker.setCheckURL('https://www.dcinside.com/')

    def run(self):
        for idx, proxy in enumerate(self.proxy_list):
            status, delay = self.proxy_checker.checkProxy({ 'http': proxy, 'https': proxy }, PROXY_AVAILABLE_DELAY)
            print('proxy', proxy, 'status', status, 'delay', delay)
            self.proxy_info_signal.emit([idx, status, delay, proxy])

        self.check_complete_signal.emit(True)
            