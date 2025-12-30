from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from components.style_engine import Colors, StyleEngine

class BasePage(QWidget):
    def __init__(self, main_window, title="", subtitle=""):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # Header Section
        self.setup_header(title, subtitle)
        
        # Content Section (to be populated by subclasses)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.content_area)
        
    def setup_header(self, title, subtitle):
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("pageTitle")
        self.title_label.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {Colors.TEXT_PRIMARY};")
        
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_SECONDARY};")
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        
        self.layout.addWidget(header_widget)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)
