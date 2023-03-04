from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import QPolygonF, QPen, QBrush, QPainter, QColor, QFont, QPainter
from PyQt5.QtWidgets import QWidget
import math

def getSerialInt():
    import serial
    a = 0
    with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as serial:
            a = int(serial.readline())
    return a

class Speedometer(QWidget):
    def __init__(self, min_value, max_value, parent=None):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value
        self.range_angle = 300
        self.min_angle = 0
        self.max_angle = self.min_angle + self.range_angle
        self.bg_color = QColor(255, 255, 255)
        self.scale_color = QColor(0, 0, 0)
        self.needle_color = QColor(255, 0, 0)
        self.font_size = 20
        self.font = QFont('Arial', self.font_size)
        self.pen_width = 2
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update2)
        self.timer.start(100)

    def update2(self):
        self.setValue(getSerialInt())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), self.bg_color)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(min(self.width(), self.height()) / 200.0, min(self.width(), self.height()) / 200.0)
        self.drawScale(painter)
        self.drawValue(painter)

    def drawScale(self, painter):
        painter.save()
        painter.setPen(QPen(self.scale_color, self.pen_width))
        font = self.font
        font.setPointSize(int(self.font_size * 0.15))
        painter.setFont(font)
        step = 20
        angle_step = self.range_angle / ((self.max_value - self.min_value) / step)
        start_angle = self.min_angle
        painter.rotate(-90)
        for i in range(int((self.max_value - self.min_value) / step) + 1):
            x1 = 62 * math.cos(math.radians(start_angle + i * angle_step))
            y1 = 62 * math.sin(math.radians(start_angle + i * angle_step))
            x2 = 72 * math.cos(math.radians(start_angle + i * angle_step))
            y2 = 72 * math.sin(math.radians(start_angle + i * angle_step))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            if i < int((self.max_value - self.min_value) / step):
                painter.save()
                painter.translate(80 * math.cos(math.radians(start_angle + (i + 0.5) * angle_step)),
                                80 * math.sin(math.radians(start_angle + (i + 0.5) * angle_step)))
                painter.rotate(start_angle + (i + 0.5) * angle_step + 90)
                painter.drawText(QPointF(-8, 0), str(i * step + self.min_value))
                painter.restore()
        painter.restore()


    def drawValue(self, painter):
        painter.save()
        painter.setPen(QPen(self.needle_color, self.pen_width))
        painter.setBrush(QBrush(self.needle_color))
        value_angle = self.min_angle + (self.value - self.min_value) * self.range_angle / (self.max_value - self.min_value)
        painter.rotate(value_angle)
        painter.drawPolygon(QPolygonF([QPointF(0, 0), QPointF(2, -55), QPointF(-2, -55)]))
        painter.restore()

        # Draw text
        font = QFont('Arial', int(self.font_size * 0.8))
        painter.setFont(font)
        text = str(self.value)
        text_rect = painter.boundingRect(QRectF(), Qt.AlignCenter, text)
        

        x = -text_rect.width() / 2
        y = 25
        painter.setPen(QPen(self.needle_color))
        background_rect = QRectF(text_rect.x(), text_rect.y() + y-7, text_rect.width(), y-font.pixelSize())  # create new rectangle for background
        painter.fillRect(background_rect, QColor('black'))
        painter.setPen(QPen(Qt.white))
        painter.drawText(QPointF(x, y), text)

    def setValue(self, value):
        self.value = value
        self.update()
from PyQt5.QtWidgets import QApplication, QMainWindow

app = QApplication([])
main_window = QMainWindow()
speedometer = Speedometer(0, 860)
main_window.setCentralWidget(speedometer)
main_window.showNormal()
# main_window.showFullScreen()
app.exec_()