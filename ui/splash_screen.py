from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import qtawesome as qta

class SplashScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # شعار التطبيق
        logo_label = QLabel()
        logo_pixmap = qta.icon("fa5s.smoking", color="#58a6ff").pixmap(128, 128)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # اسم التطبيق
        name_label = QLabel("SMOKEDASH")
        name_label.setObjectName("logoLabel")
        name_label.setAlignment(Qt.AlignCenter)
        
        # مؤشر التحميل
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(300)
        
        # رسالة التحميل
        self.status_label = QLabel("جاري التحميل...")
        self.status_label.setStyleSheet("color: #8b949e;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(logo_label)
        layout.addWidget(name_label)
        layout.addSpacing(30)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        self.setFixedSize(500, 400)
    
    def update_progress(self, value, message):
        """تحديث شاشة التحميل"""
        from PySide6.QtWidgets import QApplication
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        QApplication.processEvents()
