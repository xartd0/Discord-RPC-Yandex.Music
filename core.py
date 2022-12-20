import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from threading import Thread
from threading import Timer
from pypresence import Presence
import time

client_id = "948644686178967573"

RPC = Presence(client_id=client_id)
RPC.connect()

left_sec = ''

class WebEnginePage(QWebEnginePage):

    def createWindow(self, _type):
        page = WebEnginePage(self)
        page.urlChanged.connect(self.on_url_changed)
        return page

    @pyqtSlot(QUrl)
    def on_url_changed(self, url):
        page = self.sender()
        self.setUrl(url)
        page.deleteLater()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        global media_url
        super(MainWindow, self).__init__(*args, **kwargs)
        self.browser = QWebEngineView()
        page = WebEnginePage(self.browser)
        self.browser.setPage(page)
        self.browser.load(QUrl('https://music.yandex.ru/'))
        self.setCentralWidget(self.browser)
        self.browser.loadFinished.connect(self.onLoadFinished)

    def injectjs(self, code, dist):
        self.browser.page().runJavaScript(code, dist)

    def check(self):
        self.injectjs("externalAPI.getCurrentTrack()", self.get_yandex_data)
        self.injectjs("externalAPI.getProgress();", self.get_seconds_data)

    def get_seconds_data(self, data):
        try:
            global left_sec
            self.data=data
            dur = int(self.data['duration'])
            pos = int(self.data['position'])
            left_sec = time.strftime("%M:%S", time.gmtime(dur - pos))
        except:
            print( 'externalAPI is not defined' )

    def get_yandex_data(self, data):
        global left_sec
        self.data=data
        if self.data is not None:
            if self.data['album']['title'] != self.data['title']:
                RPC.update(
                    large_image='https://' + self.data['cover'].replace(r'%%', '400x400'),
                    details=f"{self.data['album']['title']} | {self.data['artists'][0]['title']}" ,
                    state=f"{self.data['title']} | {left_sec}",
                    buttons=[{"label": "🎶 Слушать", "url": 'https://music.yandex.ru/' + self.data['link']}])
            else:
                RPC.update(
                    large_image='https://' + self.data['cover'].replace(r'%%', '400x400'),
                    details=f"{self.data['artists'][0]['title']}" ,
                    state=f"{self.data['title']} | {left_sec}",
                    buttons=[{"label": "🎶 Слушать", "url": 'https://music.yandex.ru/' + self.data['link']}])

    def onLoadFinished(self, ok):
        if ok:
            setInterval(1.0, self.check)

def setInterval(timer, task):
    isStop = task()
    if not isStop:
        Timer(timer, setInterval, [timer, task]).start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.setWindowTitle('Yandex Music')
    w.show()
    sys.exit(app.exec_())  
