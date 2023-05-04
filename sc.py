import sys
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QApplication, QMainWindow

class ScreenCapture(QMainWindow):
    def __init__(self):
        super().__init__()

        self.start_pos = None
        self.end_pos = None
        self.tmp_img_file = '.latest.screenshot.png'

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), QApplication.primaryScreen().size().height())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.rect = None
    
        self.flag = True
        self.right_mouse_pressed = False
        self.image_hash = None
        self.show()

    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        if event.button() == Qt.MouseButton.RightButton:
            self.right_mouse_pressed = True

    def mouseReleaseEvent(self, event):
        if self.right_mouse_pressed and self.rect:
            if self.flag: 
                screen = QApplication.primaryScreen()
                pixmap = screen.grabWindow(0, self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height())
                pixmap.save(self.tmp_img_file)
                self.flag = False

            self.close()

    def paintEvent(self,event):
        if self.rect and self.right_mouse_pressed and self.flag:
            qp = QPainter(self)
            qp.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine))
            qp.setBrush(Qt.GlobalColor.transparent)
            qp.drawRect(self.rect)

    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            self.rect = QRect(self.start_pos, event.pos())
            self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sc = ScreenCapture()
    sys.exit(app.exec())