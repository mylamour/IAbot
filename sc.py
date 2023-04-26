import sys
import cv2
import time
import tempfile
import numpy as np
from mss import mss
from core import brain
from ocr import OCR
from prompts import Prompt
from markdown import markdown
from PyQt6.QtCore import Qt, QPoint, QRect, QRunnable, QObject, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextBrowser

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(str)

class OCRWorker(QRunnable):
    def __init__(self, img_path):
        super().__init__()
        self.signals = WorkerSignals()
        self.img_path = img_path

    @pyqtSlot()
    def run(self):
        try:
            ocr = OCR()
            res = "".join(ocr.ocr_img(self.img_path))
            conversation = []
            conversation.append(Prompt.screenshot.value)
            conversation.append({
                "role": "user",
                "content": res
            })
            result = brain(conversation)
            self.signals.finished.emit()
            self.signals.result.emit(result)
            # time.sleep(2)  #  for debug
            # self.signals.result.emit('1233')
        except Exception as e:
            self.signals.error.emit(str(e))

class ScreenCapture(QMainWindow):
    def __init__(self, imgfile):
        super().__init__()
        self.threadpool = QThreadPool()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), QApplication.primaryScreen().size().height())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.start_pos = None
        self.end_pos = None
        self.img_file = imgfile
    
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setWindowTitle('正在分析中-请稍后')
        self.text_browser.setGeometry(1, 1, 1, 1)  #  hidden first, show when you get the result
        self.text_browser.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        self.end_pos = None

    def mouseReleaseEvent(self, event):
        self.end_pos = event.pos()
        self.takeScreenshot()
        self.text_browser.show()

    def setTextBrowser(self, result):
        self.text_browser.setGeometry(QApplication.primaryScreen().size().width()-400, 0, 400, QApplication.primaryScreen().size().height())
        new_x = QApplication.primaryScreen().size().width() - 400
        new_y = 0
        self.text_browser.move(new_x, new_y)
        self.text_browser.setWindowTitle('分析结果如下')
        self.text_browser.setHtml(markdown(result))
        # self.text_browser.show()

    def takeScreenshot(self):
        screen_pixmap = QApplication.primaryScreen().grabWindow(0)
        selected_pixmap = QPixmap(self.end_pos.x() - self.start_pos.x(), self.end_pos.y() - self.start_pos.y())
        selected_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(selected_pixmap)
        painter.drawPixmap(QPoint(0, 0), screen_pixmap, QRect(self.start_pos, self.end_pos))
        selected_pixmap.save(self.img_file)
        worker.signals.result.connect(self.setTextBrowser)
        worker.signals.error.connect(self.mouseReleaseEvent) # if error, screenshot again
        self.threadpool.start(worker)
        painter.end() # if not , will error QPaintDevice: Cannot destroy paint device that is being painted
        self.close()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.MouseButton.LeftButton:
            self.end_pos = event.pos()
            self.update()

    def paintEvent(self, event):
        if not self.start_pos and not self.end_pos:
            return
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRect(self.start_pos.x(), self.start_pos.y(), self.end_pos.x() - self.start_pos.x(), self.end_pos.y() - self.start_pos.y())
class ScreenRecord():
    def __init__(self) -> None:
        screen_size = (width, height) = (1920, 1080)  # Change this to your screen resolution  
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  
        out = cv2.VideoWriter('screen_recording.mp4', fourcc, 30.0, screen_size)  
        recording_time_limit = 10  # Record for 10 seconds  
        start_time = time.time()  
        with mss() as sct:  
            monitor = {'top': 0, 'left': 0, 'width': width, 'height': height}  
            while True:  
                img = np.array(sct.grab(monitor))  
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  
                out.write(frame)  
                if (time.time() - start_time) > recording_time_limit:  
                    break
        out.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with tempfile.NamedTemporaryFile(prefix="ai_bot_", suffix=".png") as temp_file:
        screencapture = ScreenCapture(temp_file.name)
        screencapture.show()
        worker = OCRWorker(temp_file.name) # it put it into takeScreenshot , it wont work , because temp file was deleted after with context.
    sys.exit(app.exec())