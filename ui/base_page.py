from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
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
        
        # Main Box Frame (シガレットボックスのシミュレーション)
        self.main_frame = QFrame()
        self.main_frame.setObjectName("statsCard") # Uses the gold-bordered frame style
        self.main_frame_layout = QVBoxLayout(self.main_frame)
        self.main_frame_layout.setContentsMargins(20, 20, 20, 20)
        
        # Content Section with Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("mainScroll")
        
        self.content_area = QWidget()
        self.content_area.setObjectName("contentContainer")
        self.content_area.setObjectName("contentArea")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        
        self.scroll.setWidget(self.content_area)
        self.main_frame_layout.addWidget(self.scroll)
        
        self.layout.addWidget(self.main_frame)
        
    def setup_header(self, title, subtitle):
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("pageTitle")
        self.title_label.setObjectName("pageTitle")
        
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("subtitleLabel")
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        
        self.layout.addWidget(header_widget)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)
