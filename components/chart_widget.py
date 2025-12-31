from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont
from PySide6.QtCore import Qt

class SalesChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {} # {label: value}
        self.bar_color = QColor("#58a6ff")
        self.text_color = QColor("#8b949e")
        self.bg_color = QColor("#0d1117")

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dimensions
        w = self.width()
        h = self.height()
        padding = 40
        
        # Draw Background (Optional, transparent usually better for integration)
        # painter.fillRect(0, 0, w, h, self.bg_color)
        
        if not self.data:
            painter.setPen(QPen(self.text_color))
            painter.drawText(self.rect(), Qt.AlignCenter, "لا توجد بيانات للعرض")
            return

        # Calculate Scales
        max_val = max(self.data.values()) if self.data else 1
        count = len(self.data)
        bar_width = (w - 2 * padding) / count * 0.6
        spacing = (w - 2 * padding) / count * 0.4
        
        # Draw Bars
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.bar_color))
        
        keys = list(self.data.keys())
        # Provide only last 7 or so if too many? For now show all passed.
        
        step_x = (w - 2 * padding) / count
        
        for i, (key, val) in enumerate(self.data.items()):
            bar_h = (val / max_val) * (h - 2 * padding)
            x = padding + i * step_x + spacing / 2
            y = h - padding - bar_h
            
            # Draw Bar
            painter.drawRoundedRect(x, y, bar_width, bar_h, 4, 4)
            
            # Draw Label (Date)
            painter.setPen(QPen(self.text_color))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            
            # Rotate text if needed or just show short date
            label = key[5:] if len(key) >= 10 else key # Show MM-DD
            painter.drawText(int(x), int(h - padding + 15), int(bar_width), 20, Qt.AlignCenter, label)
            
            # Draw Value on top
            painter.drawText(int(x), int(y - 20), int(bar_width), 20, Qt.AlignCenter, f"{int(val)}")

        # Draw Axis Lines
        painter.setPen(QPen(QColor("#30363d"), 1))
        painter.drawLine(padding, h - padding, w - padding, h - padding) # X Axis
        painter.drawLine(padding, padding, padding, h - padding) # Y Axis
