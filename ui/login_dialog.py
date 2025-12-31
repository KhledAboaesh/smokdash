from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QFrame, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from components.style_engine import Colors, StyleEngine

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_data = None
        self.setWindowTitle("تسجيل الدخول - SmokeDash")
        self.setFixedWidth(500)
        self.setFixedHeight(600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Main Premium Card
        self.card = QFrame()
        self.card.setObjectName("loginCard")
        self.card.setStyleSheet(f"""
            QFrame#loginCard {{
                background-color: {Colors.SECONDARY_BG};
                border: 2px solid {Colors.ACCENT};
                border-radius: 10px;
            }}
            QLabel#titleLabel {{
                font-size: 32px;
                font-weight: 900;
                color: {Colors.ACCENT};
                letter-spacing: 0px;
            }}
            QLineEdit {{
                background-color: {Colors.BACKGROUND};
                border: 1px solid {Colors.ACCENT};
                border-radius: 0px;
                padding: 5px;
                color: {Colors.TEXT_PRIMARY};
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Colors.TEXT_PRIMARY};
            }}
            QPushButton#loginBtn {{
                background-color: {Colors.ACCENT};
                color: {Colors.BACKGROUND};
                border-radius: 0px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton#loginBtn:hover {{
                background-color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(10)
        
        # Header Section
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        from components.utils import resource_path
        self.logo_pix = QLabel()
        logo_pix = QPixmap(resource_path("logo.png"))
        self.logo_pix.setPixmap(logo_pix.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_pix.setAlignment(Qt.AlignCenter)
        
        self.logo_lbl = QLabel("SMOKEDASH V3.00")
        self.logo_lbl.setObjectName("titleLabel")
        self.logo_lbl.setAlignment(Qt.AlignCenter)
        
        self.sub_lbl = QLabel("نظام الإدارة المتميز - الإصدار الثالث")
        self.sub_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 16px; margin-bottom: 0px;")
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.logo_pix)
        header_layout.addWidget(self.logo_lbl)
        header_layout.addWidget(self.sub_lbl)
        card_layout.addLayout(header_layout)
        
        # Form
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.username_input.setFixedHeight(55)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(55)
        
        self.login_btn = QPushButton("تسجيل الدخول")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setFixedHeight(60)
        self.login_btn.clicked.connect(self.check_login)
        
        card_layout.addWidget(QLabel("بيانات الدخول:"))
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.login_btn)
        
        # Footer
        footer_layout = QHBoxLayout()
        close_btn = QPushButton("إغلاق النظام")
        close_btn.setStyleSheet("background: transparent; color: #f85149; font-weight: bold; border: none;")
        close_btn.clicked.connect(self.reject)
        
        footer_layout.addStretch()
        footer_layout.addWidget(close_btn)
        footer_layout.addStretch()
        card_layout.addLayout(footer_layout)
        
        main_layout.addWidget(self.card)
        
        # Apply premium shadow
        StyleEngine.apply_shadow(self.card)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        users = self.db.get_users()
        
        user = next((u for u in users if u.get('username') == username and u.get('password') == password), None)
        if user:
            self.user_data = user
            self.accept()
        else:
            QMessageBox.warning(self, "خطأ", "بيانات الدخول غير صحيحة!")
