from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QMessageBox, QLabel, QFrame
import qtawesome as qta
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
        self.container.setObjectName("dialogContainer")
        
        main_layout.addWidget(self.container)
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30,30,30,30)
        
        header = QLabel(self.windowTitle())
        header.setObjectName("sectionHeader")
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
        save_btn = QPushButton(" حفظ العميل")
        save_btn.setIcon(qta.icon("fa5s.save", color="#062C21"))
        save_btn.setObjectName("posButton")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton(" إلغاء")
        cancel_btn.setIcon(qta.icon("fa5s.times", color="#C8C4A0"))
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedHeight(40)
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
