from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QFrame
from PySide6.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_data = None
        self.setWindowTitle("تسجيل الدخول - SmokeDash")
        self.setFixedWidth(450)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        main_layout = QVBoxLayout(self)
        
        # Login Card
        self.card = QFrame()
        self.card.setObjectName("loginCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setSpacing(15)
        
        # Logo/Title
        self.logo = QLabel("SMOKEDASH")
        self.logo.setObjectName("loginTitle")
        self.logo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.logo)
        
        self.subtitle = QLabel("المحترف لإدارة مبيعات السجائر")
        self.subtitle.setStyleSheet("color: #8b949e; font-size: 14px; margin-bottom: 20px;")
        self.subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.subtitle)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.username_input.setFixedHeight(50)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(50)
        
        self.login_btn = QPushButton("تسجيل الدخول")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setFixedHeight(55)
        self.login_btn.clicked.connect(self.check_login)
        
        # Close Button
        self.close_btn = QPushButton("إغلاق")
        self.close_btn.setStyleSheet("background: transparent; border: none; color: #8b949e; font-size: 12px;")
        self.close_btn.clicked.connect(self.reject)
        
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.login_btn)
        card_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(self.card)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        users = self.db.get_users()
        
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            self.user_data = user
            self.accept()
        else:
            QMessageBox.warning(self, "خطأ", "بيانات الدخول غير صحيحة!")
