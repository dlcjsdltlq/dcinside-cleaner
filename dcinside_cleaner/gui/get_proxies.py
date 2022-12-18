from .utils import resource_path
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import ipaddress

proxies_input_form = uic.loadUiType(resource_path('./resources/ui/ui_proxies_input_window.ui'))[0]
logo_ico = resource_path('./resources/icon/logo_icon.ico')

class ProxyInputWindow(QtWidgets.QDialog, proxies_input_form):
    proxy_list_signal = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(logo_ico))

        self.btn_complete.clicked.connect(self.getProxyList)

    def getProxyList(self):
        text = self.proxies_input.toPlainText()
        raw_list = text.split('\n')
        valid_proxy_list = []
        for raw_proxy in raw_list:
            proxy = []
            try:
                proxy = raw_proxy.split(':') # proxy -> [ip, port]
                ipaddress.ip_address(proxy[0])
            except:
                continue
            
            valid_proxy_list.append(raw_proxy)

        self.proxy_list_signal.emit(valid_proxy_list)
        self.close()