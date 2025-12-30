from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QMessageBox, QLabel, QFrame, QComboBox
from PySide6.QtCore import Qt
from components.style_engine import Colors, StyleEngine

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit_mode = user_data is not None
        
        self.setWindowTitle("تعديل بيانات الموظف" if self.is_edit_mode else "إضافة موظف جديد")
        self.setFixedWidth(450)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.container = QFrame()
        self.container.setObjectName("statsCard")
        self.container.setStyleSheet(f"""
            QFrame#statsCard {{
                background-color: #161b22;
                border: 1px solid {Colors.ACCENT};
                border-radius: 12px;
            }}
            QLabel {{ color: {Colors.TEXT_SECONDARY}; font-weight: 600; }}
            QLineEdit, QComboBox {{
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px;
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        
        main_layout.addWidget(self.container)
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30,30,30,30)
        
        header = QLabel(self.windowTitle())
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Colors.ACCENT}; margin-bottom: 10px;")
        layout.addWidget(header)
        
        form = QFormLayout()
        form.setSpacing(15)
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("اترك فارغاً لعدم التغيير" if self.is_edit_mode else "كلمة المرور")
        self.fullname_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "manager", "cashier"])
        
        form.addRow("اسم المستخدم:", self.username_input)
        form.addRow("كلمة المرور:", self.password_input)
        form.addRow("الاسم الكامل:", self.fullname_input)
        form.addRow("رقم الهاتف:", self.phone_input)
        form.addRow("الدور الوظيفي:", self.role_combo)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.setObjectName("posButton")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet("background: transparent; color: #8b949e;")
        cancel_btn.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)
        
        StyleEngine.apply_shadow(self.container)

    def load_data(self):
        if self.user_data:
            self.username_input.setText(self.user_data.get('username', ''))
            self.username_input.setReadOnly(True)
            self.fullname_input.setText(self.user_data.get('full_name', ''))
            self.phone_input.setText(self.user_data.get('phone', ''))
            self.role_combo.setCurrentText(self.user_data.get('role', 'cashier'))

    def get_data(self):
        data = {
            "username": self.username_input.text(),
            "full_name": self.fullname_input.text(),
            "phone": self.phone_input.text(),
            "role": self.role_combo.currentText()
        }
        if self.password_input.text():
            data["password"] = self.password_input.text()
        return data
