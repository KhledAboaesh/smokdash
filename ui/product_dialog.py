from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox, QHBoxLayout, QPushButton, QMessageBox, QLabel, QFrame
import qtawesome as qta
from PySide6.QtCore import Qt
from components.style_engine import Colors, StyleEngine

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.is_edit_mode = product_data is not None
        
        # Window attributes
        self.setWindowTitle("تعديل الصنف" if self.is_edit_mode else "إضافة صنف جديد")
        self.setFixedWidth(450)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_product_data()

    def setup_ui(self):
        # Container with custom border and shadow
        self.container = QFrame()
        self.container.setObjectName("dialogContainer")
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container)
        
        content_layout = QVBoxLayout(self.container)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Header
        header_lbl = QLabel(self.windowTitle())
        header_lbl.setObjectName("sectionHeader")
        content_layout.addWidget(header_lbl)
        
        # Form
        form = QFormLayout()
        form.setSpacing(15)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم المنتج...")
        
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("الماركة/الشركة المصنعة...")
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(99999.99)
        self.price_input.setSuffix(" LYD")
        
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(100000)

        self.min_stock_input = QSpinBox()
        self.min_stock_input.setMaximum(100000)
        self.min_stock_input.setValue(10)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("الباركود العالمي...")
        
        form.addRow("اسم الصنف:", self.name_input)
        form.addRow("الماركة:", self.brand_input)
        form.addRow("سعر البيع:", self.price_input)
        form.addRow("الكمية بالمخزن:", self.stock_input)
        form.addRow("حد التنبيه (الأدنى):", self.min_stock_input)
        form.addRow("كود الباركود:", self.barcode_input)
        
        content_layout.addLayout(form)
        
        # Actions
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(10)
        
        save_btn = QPushButton(" حفظ الصنف")
        save_btn.setIcon(qta.icon("fa5s.save", color="#062C21"))
        save_btn.setObjectName("posButton")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton(" إلغاء")
        cancel_btn.setIcon(qta.icon("fa5s.times", color="#C8C4A0"))
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedHeight(40)
        cancel_btn.clicked.connect(self.reject)
        
        if self.is_edit_mode:
            self.delete_btn = QPushButton(" حذف المنتج")
            self.delete_btn.setIcon(qta.icon("fa5s.trash-alt", color="#FDFCF0"))
            self.delete_btn.setObjectName("dangerButton")
            self.delete_btn.setFixedHeight(40)
            self.delete_btn.clicked.connect(self.delete_product)
            btns_layout.addWidget(self.delete_btn)
            
        btns_layout.addStretch()
        btns_layout.addWidget(cancel_btn)
        btns_layout.addWidget(save_btn)
        
        content_layout.addLayout(btns_layout)
        
        StyleEngine.apply_shadow(self.container)

    def load_product_data(self):
        if self.product_data:
            self.name_input.setText(self.product_data.get('name', ''))
            self.brand_input.setText(self.product_data.get('brand', ''))
            self.price_input.setValue(self.product_data.get('price', 0))
            self.stock_input.setValue(self.product_data.get('stock', 0))
            self.min_stock_input.setValue(self.product_data.get('min_stock', 10))
            self.barcode_input.setText(self.product_data.get('barcode', ''))

    def delete_product(self):
        reply = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا المنتج نهائياً؟", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.done(2)

    def get_data(self):
        data = {
            "name": self.name_input.text(),
            "brand": self.brand_input.text(),
            "price": self.price_input.value(),
            "stock": self.stock_input.value(),
            "min_stock": self.min_stock_input.value(),
            "barcode": self.barcode_input.text()
        }
        if self.is_edit_mode and self.product_data:
            data['id'] = self.product_data['id']
        return data
