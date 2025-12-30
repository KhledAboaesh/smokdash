from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_data = None
        self.setWindowTitle("تسجيل الدخول - SmokeDash")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        login_btn = QPushButton("دخول")
        login_btn.clicked.connect(self.check_login)
        
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        users = self.db.get_users()
        
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            self.user_data = user
            self.accept()
        else:
            QMessageBox.warning(self, "خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة!")
