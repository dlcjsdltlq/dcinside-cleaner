from ..dcinside_cleaner import Cleaner
from PyQt5 import QtCore


class CleanerThread(QtCore.QThread):
    event_signal = QtCore.pyqtSignal(dict)

    def __init__(self, captcha_signal):
        super().__init__()
        self.cleaner: Cleaner
        self.captcha_signal = captcha_signal
        self.del_list = []
        self.p_type = ''
        self.del_all = False

        self.captcha_flag = False

        self.captcha_signal.connect(self.checkCaptcha)

    def setCleaner(self, cleaner):
        self.cleaner = cleaner

    def setDelInfo(self, del_list, p_type, del_all):
        self.del_list = del_list
        self.p_type = p_type
        self.del_all = del_all

        if del_all:
            del_list = []

    def checkCaptcha(self):
        self.captcha_flag = False

    def deleteEvent(self, event):
        self.event_signal.emit(event)
        if event['type'] == 'captcha':
            while self.captcha_flag:
                pass

    def delete(self, gno):
        self.event_signal.emit(
            {'type': 'pages', 'data': self.cleaner.getPageCount(gno, self.p_type)})
        for i in self.cleaner.aggregatePosts(gno, self.p_type):
            if i['data'] == 'ipblocked':
                return self.event_signal.emit({'type': 'ipblocked'})
            self.event_signal.emit({'type': 'page_update', 'data': i['data']})

        self.event_signal.emit(
            {'type': 'posts', 'data': len(self.cleaner.post_list)})
        for i in self.cleaner.deletePosts(self.p_type):
            if i['data'] == 'ipblocked':
                return self.event_signal.emit({'type': 'ipblocked'})
            elif i['data'] == 'captcha':
                self.event_signal.emit({'type': 'captcha'})
                self.captcha_flag = True
                while self.captcha_flag:
                    pass
                continue
            self.event_signal.emit({'type': 'post_update', 'data': i['data']})

    def run(self):
        if self.del_all:
            self.delete(None)

        for gno in self.del_list:
            self.delete(gno)    
        
        self.event_signal.emit({'type': 'complete'})
