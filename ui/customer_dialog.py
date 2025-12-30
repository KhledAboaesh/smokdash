from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QMessageBox, QLabel, QFrame
from PySide6.QtCore import Qt
from components.style_engine import Colors, StyleEngine

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer_data=None):
        super().__init__(parent)
        self.customer_data = customer_data
        self.is_edit_mode = customer_data is not None
        
        self.setWindowTitle("تعديل بيانات العميل" if self.is_edit_mode else "إضافة عميل جديد")
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
            QLineEdit {{
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
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        form.addRow("اسم العميل:", self.name_input)
        form.addRow("رقم الهاتف:", self.phone_input)
        form.addRow("العنوان:", self.address_input)
        
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
        if self.customer_data:
            self.name_input.setText(self.customer_data.get('name', ''))
            self.phone_input.setText(self.customer_data.get('phone', ''))
            self.address_input.setText(self.customer_data.get('address', ''))

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "phone": self.phone_input.text(),
            "address": self.address_input.text()
        }
