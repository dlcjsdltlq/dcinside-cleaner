from ..dcinside_cleaner import Cleaner
from PyQt5 import QtCore

class CleanerThread(QtCore.QThread):
    event_signal = QtCore.pyqtSignal(dict)

    def __init__(self, captcha_signal):
        super().__init__()
        self.cleaner : Cleaner
        self.captcha_signal = captcha_signal
        self.del_list = []
        self.p_type = ''

        self.captcha_flag = False

        self.captcha_signal.connect(self.checkCaptcha)

    def setCleaner(self, cleaner):
        self.cleaner = cleaner

    def setDelInfo(self, l, p_type):
        self.del_list = l
        self.p_type = p_type

    def checkCaptcha(self, i):
        self.captcha_flag = False
    
    def deleteEvent(self, event):
        self.event_signal.emit(event)
        if event['type'] == 'captcha':
            while self.captcha_flag: pass

    def run(self):
        for gno in self.del_list:
            self.event_signal.emit({ 'type': 'pages', 'data': self.cleaner.getPages(gno, self.p_type) })
            for i in self.cleaner.getAllPosts(gno, self.p_type):
                if i == 'ipblocked':
                    return self.event_signal.emit({ 'type': 'ipblocked' })
                self.event_signal.emit({ 'type': 'page_update' })
            
            self.event_signal.emit({ 'type': 'posts', 'data': len(self.cleaner.post_list) })
            for i in self.cleaner.deletePosts(self.p_type):
                if i == 'ipblocked':
                    return self.event_signal.emit({ 'type': 'ipblocked' })
                if i == 'captcha':
                    self.event_signal.emit({ 'type': 'captcha' })
                    self.captcha_flag = True
                    while self.captcha_flag: pass
                self.event_signal.emit({ 'type': 'post_update' })
        self.event_signal.emit({ 'type': 'complete' })