from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox, QHBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.is_edit_mode = product_data is not None
        
        if self.is_edit_mode:
            self.setWindowTitle("تعديل الصنف")
        else:
            self.setWindowTitle("إضافة صنف جديد")
            
        self.setFixedWidth(400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_product_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم الصنف (مثل: مالبورو أحمر)...")
        
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("أدخل اسم الماركة (مثل: Philip Morris)...")
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(9999.99)
        self.price_input.setMinimum(0.01)
        # Assuming parent has a settings attribute with currency
        currency = self.parent().settings.get('currency', 'LYD') if (self.parent() and hasattr(self.parent(), 'settings')) else 'LYD'
        self.price_input.setSuffix(f" {currency}")
        
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(100000)
        self.stock_input.setValue(10)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("الباركود...")
        
        form.addRow("اسم الصنف:", self.name_input)
        form.addRow("الماركة:", self.brand_input)
        form.addRow("سعر البيع:", self.price_input)
        form.addRow("الكمية:", self.stock_input)
        form.addRow("الباركود:", self.barcode_input)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        save_text = "حفظ التعديلات" if self.is_edit_mode else "حفظ"
        save_btn = QPushButton(save_text)
        save_btn.clicked.connect(self.accept)
        save_btn.setObjectName("posButton")
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        
        if self.is_edit_mode:
            delete_btn = QPushButton("حذف")
            delete_btn.setStyleSheet("background-color: #da3633; color: white; border-radius: 6px; padding: 8px;")
            delete_btn.clicked.connect(self.delete_product)
            btns.addWidget(delete_btn)
        
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def load_product_data(self):
        if self.product_data:
            self.name_input.setText(self.product_data.get('name', ''))
            self.brand_input.setText(self.product_data.get('brand', ''))
            self.price_input.setValue(self.product_data.get('price', 0))
            self.stock_input.setValue(self.product_data.get('stock', 0))
            self.barcode_input.setText(self.product_data.get('barcode', ''))

    def delete_product(self):
        reply = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا المنتج؟", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.done(2)

    def get_data(self):
        data = {
            "name": self.name_input.text(),
            "brand": self.brand_input.text(),
            "price": self.price_input.value(),
            "stock": self.stock_input.value(),
            "barcode": self.barcode_input.text()
        }
        if self.is_edit_mode and self.product_data:
            data['id'] = self.product_data['id']
        return data
