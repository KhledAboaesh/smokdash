from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
import qtawesome as qta
from components.style_engine import Colors, StyleEngine

class StatsCard(QFrame):
    def __init__(self, title, value, icon, icon_color=Colors.ACCENT):
        super().__init__()
        self.setObjectName("statsCard")
        self.setMinimumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header (Icon + Title)
        header = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color=icon_color).pixmap(24, 24))
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 14px; font-weight: 600;")
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 28px; font-weight: 800; margin-top: 10px;")
        layout.addWidget(self.value_label)
        
        # Apply shadow
        StyleEngine.apply_shadow(self)

    def update_value(self, new_value):
        self.value_label.setText(new_value)
