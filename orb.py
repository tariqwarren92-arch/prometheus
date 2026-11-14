from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QPen
from PySide6.QtWidgets import QWidget

class IntelligenceOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0
        self.setMinimumSize(210, 210)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(32)

    def tick(self):
        self.phase = (self.phase + 2) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height())
        cx, cy = self.width()/2, self.height()/2
        r = side * .31
        glow = QRadialGradient(cx, cy, r*1.9)
        glow.setColorAt(0, QColor(0, 220, 255, 90))
        glow.setColorAt(.55, QColor(110, 70, 255, 28))
        glow.setColorAt(1, QColor(5, 10, 25, 0))
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(glow)
        p.drawEllipse(int(cx-r*1.9), int(cy-r*1.9), int(r*3.8), int(r*3.8))
        for i in range(3):
            rr = r*(.78+i*.2)
            p.setPen(QPen(QColor(0, 220, 255, 130-i*30), 1.2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(int(cx-rr), int(cy-rr), int(rr*2), int(rr*2))
        p.save(); p.translate(cx, cy); p.rotate(self.phase)
        p.setPen(QPen(QColor(145, 115, 255, 190), 2))
        p.drawEllipse(int(-r*.62), int(-r*.62), int(r*1.24), int(r*1.24))
        p.drawLine(int(-r*.95), 0, int(r*.95), 0)
        p.restore()
        core = QRadialGradient(cx-r*.15, cy-r*.18, r*.9)
        core.setColorAt(0, QColor(235,255,255,245))
        core.setColorAt(.25, QColor(0,205,255,225))
        core.setColorAt(1, QColor(60,55,170,170))
        p.setPen(QPen(QColor(120,245,255,180), 1)); p.setBrush(core)
        p.drawEllipse(int(cx-r*.43), int(cy-r*.43), int(r*.86), int(r*.86))
