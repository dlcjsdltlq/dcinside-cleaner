from ..proxy_checker import ProxyChecker
from .utils import resource_path
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import json

proxies_check_form = uic.loadUiType(resource_path('./resources/ui/ui_proxies_check_window.ui'))[0]
logo_ico = resource_path('./resources/icon/logo_icon.ico')

PROXY_AVAILABLE_DELAY = 0.6

class ProxyCheckWindow(QtWidgets.QDialog, proxies_check_form):
    available_proxy_list_signal  = QtCore.pyqtSignal(list)

    def __init__(self, proxy_list):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(logo_ico))

        self.check_thread : ProxyThread

        self.proxy_list = proxy_list
        self.proxy_count = len(proxy_list)

        self.available_list = []
        self.checkbox_list = []

        self.proxy_checker = ProxyChecker()
        self.proxy_checker.setCheckURL('https://www.dcinside.com/')

        self.btn_save_proxies.setEnabled(False)
        self.btn_save_proxies.clicked.connect(self.exportProxyList)
        
        self.btn_remove_excluded.setEnabled(False)
        self.btn_remove_excluded.clicked.connect(self.removeExcludedRows)

        self.btn_retest.setEnabled(False)
        self.btn_retest.clicked.connect(self.retest)

        self.initProxyTable()

        self.runThread()

    def closeEvent(self, event):
        if self.check_thread:
            self.check_thread.stop()

        event.accept()

    def initProxyTable(self):
        table_labels = ['사용', 'IP', '포트', '지연', '사용가능여부']
        self.proxy_table.setColumnCount(len(table_labels)) # ip port delay available
        self.proxy_table.setHorizontalHeaderLabels(table_labels)
        self.proxy_table.setRowCount(self.proxy_count)
        self.proxy_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        for idx, proxy in enumerate(self.proxy_list):
            cell_widget = QtWidgets.QWidget()
            checkbox = QtWidgets.QCheckBox()
            layout = QtWidgets.QHBoxLayout(cell_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(QtCore.Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            cell_widget.setLayout(layout)
            self.proxy_table.setCellWidget(idx, 0, cell_widget)
            self.checkbox_list.append(checkbox)

            proxy = proxy.split(':')
            self.proxy_table.setItem(idx, 1, QtWidgets.QTableWidgetItem(proxy[0]))
            self.proxy_table.setItem(idx, 2, QtWidgets.QTableWidgetItem(proxy[1]))
            self.proxy_table.setItem(idx, 3, QtWidgets.QTableWidgetItem('-'))
            self.proxy_table.setItem(idx, 4, QtWidgets.QTableWidgetItem('-'))

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
            self.proxy_table.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(round(delay, 1)) + 'sec'))
            self.checkbox_list[idx].setChecked(True)

        item = QtWidgets.QTableWidgetItem(status and '✓' or '✗')
        color = status and (0, 255, 0) or (255, 0, 0)
        item.setForeground(QtGui.QBrush(QtGui.QColor(*color)))
        self.proxy_table.setItem(idx, 4, item)
        index = self.proxy_table.model().index(idx, 0)
        self.proxy_table.scrollTo(index)

    @QtCore.pyqtSlot(bool)
    def completeCheck(self):
        self.available_proxy_list_signal.emit(self.available_list)
        self.btn_save_proxies.setEnabled(True)
        self.btn_remove_excluded.setEnabled(True)
        self.btn_retest.setEnabled(True)

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

    def removeExcludedRows(self):
        new_checkbox_list = []
        new_proxy_list = []
        deleted = 0
        for i, checkbox in enumerate(self.checkbox_list):
            if not checkbox.isChecked():
                self.proxy_table.removeRow(i - deleted)
                deleted += 1
                continue
            new_checkbox_list.append(checkbox)
            new_proxy_list.append(self.proxy_list[i])

        self.checkbox_list = new_checkbox_list
        self.proxy_list = new_proxy_list
        self.available_list = new_proxy_list
        self.available_proxy_list_signal.emit(self.available_list)

    def retest(self):
        self.available_list = []
        for i, checkbox in enumerate(self.checkbox_list):
            self.proxy_table.setItem(i, 3, QtWidgets.QTableWidgetItem('-'))
            self.proxy_table.setItem(i, 4, QtWidgets.QTableWidgetItem('-'))
            checkbox.setChecked(False)
            
        self.btn_save_proxies.setEnabled(False)
        self.btn_remove_excluded.setEnabled(False)
        self.btn_retest.setEnabled(False)

        self.runThread()
        




class ProxyThread(QtCore.QThread):
    proxy_info_signal = QtCore.pyqtSignal(list)
    check_complete_signal = QtCore.pyqtSignal(bool)

    def __init__(self, proxy_list):
        super().__init__()
        self.proxy_list = proxy_list
        self.proxy_checker = ProxyChecker()
        self.proxy_checker.setCheckURL('https://www.dcinside.com/')
        self.working = False

    def run(self):
        self.working = True
        for idx, proxy in enumerate(self.proxy_list):
            if not self.working: return
            status, delay = self.proxy_checker.checkProxy({ 'http': proxy, 'https': proxy }, PROXY_AVAILABLE_DELAY)
            self.proxy_info_signal.emit([idx, status, delay, proxy])

        self.check_complete_signal.emit(True)

    def stop(self):
        self.working = False
        self.quit()
        self.wait(5000)