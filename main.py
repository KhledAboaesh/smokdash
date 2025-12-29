import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QLineEdit, QFormLayout, QMessageBox, QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QColor
import qtawesome as qta

from data_manager import DataManager

class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة صنف جديد")
        self.setFixedWidth(400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(9999.99)
        self.price_input.setSuffix(" LYD")
        
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(100000)
        
        self.barcode_input = QLineEdit()
        
        form.addRow("اسم الصنف:", self.name_input)
        form.addRow("الماركة:", self.brand_input)
        form.addRow("سعر البيع:", self.price_input)
        form.addRow("الكمية الأولية:", self.stock_input)
        form.addRow("الباركود:", self.barcode_input)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        save_btn.clicked.connect(self.accept)
        save_btn.setObjectName("posButton")
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "brand": self.brand_input.text(),
            "price": self.price_input.value(),
            "stock": self.stock_input.value(),
            "barcode": self.barcode_input.text()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DataManager()
        self.setup_ui()
        self.load_styles()
        self.refresh_inventory()

    def setup_ui(self):
        self.setWindowTitle("SmokeDash - منظومة إدارة محل سجائر")
        self.resize(1100, 750)
        self.setLayoutDirection(Qt.RightToLeft)

        # Main Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.setup_sidebar()

        # Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        # Pages
        self.dashboard_page = self.create_dashboard()
        self.pos_page = self.create_pos()
        self.inventory_page = self.create_inventory()

        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.pos_page)
        self.content_stack.addWidget(self.inventory_page)

    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 30, 10, 30)
        self.sidebar_layout.setSpacing(15)

        # Logo / Title
        logo_label = QLabel("SMOKEDASH")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00bcd4; margin-bottom: 30px;")
        logo_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(logo_label)

        # Navigation Buttons
        self.nav_btns = []
        
        btn_dash = self.create_nav_btn("لوحة التحكم", "fa5s.home", 0)
        btn_pos = self.create_nav_btn("نقطة البيع (POS)", "fa5s.shopping-cart", 1)
        btn_inventory = self.create_nav_btn("المخزون", "fa5s.boxes", 2)
        btn_reports = self.create_nav_btn("التقارير", "fa5s.chart-bar", 3)
        
        self.sidebar_layout.addStretch()
        
        btn_settings = self.create_nav_btn("الإعدادات", "fa5s.cog", -1)
        
        self.main_layout.addWidget(self.sidebar)

    def create_nav_btn(self, text, icon_name, index):
        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon_name, color="#e0e0e0"))
        btn.setIconSize(QSize(20, 20))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(45)
        btn.setStyleSheet("text-align: right; padding-right: 20px; font-size: 15px;")
        
        if index != -1:
            btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(index))
        
        self.sidebar_layout.addWidget(btn)
        self.nav_btns.append(btn)
        return btn

    def create_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("نظرة عامة على المحل")
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(header)
        
        # Stats Cards
        stats_layout = QHBoxLayout()
        
        self.card_sales = self.create_stats_card("مبيعات اليوم", "0.00 LYD", "fa5s.money-bill-wave")
        self.card_count = self.create_stats_card("عدد العمليات", "0", "fa5s.receipt")
        self.card_stock = self.create_stats_card("الأصناف المتوفرة", "0", "fa5s.box-open")
        
        stats_layout.addWidget(self.card_sales)
        stats_layout.addWidget(self.card_count)
        stats_layout.addWidget(self.card_stock)
        layout.addLayout(stats_layout)
        layout.addStretch()
        
        return page

    def create_stats_card(self, title, value, icon):
        card = QFrame()
        card.setObjectName("statsCard")
        card_layout = QVBoxLayout(card)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color="#00bcd4").pixmap(30, 30))
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888888; font-size: 14px;")
        
        value_label = QLabel(value)
        value_label.setObjectName("totalLabel")
        
        card_layout.addWidget(icon_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        return card

    def create_pos(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left Side: Cart and Payment
        cart_panel = QFrame()
        cart_panel.setFixedWidth(400)
        cart_layout = QVBoxLayout(cart_panel)
        
        cart_label = QLabel("سلة المشتريات")
        cart_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        cart_layout.addWidget(cart_label)
        
        self.cart_table = QTableWidget(0, 3)
        self.cart_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "الإجمالي"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        cart_layout.addWidget(self.cart_table)
        
        # Total
        self.pos_total_label = QLabel("الإجمالي: 0.00 LYD")
        self.pos_total_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00bcd4; margin: 10px 0;")
        cart_layout.addWidget(self.pos_total_label)
        
        pay_btn = QPushButton("إتمام البيع (دفع)")
        pay_btn.setObjectName("posButton")
        pay_btn.setFixedHeight(50)
        pay_btn.clicked.connect(self.process_sale)
        cart_layout.addWidget(pay_btn)
        
        clear_btn = QPushButton("تفريغ السلة")
        clear_btn.clicked.connect(self.clear_cart)
        cart_layout.addWidget(clear_btn)
        
        layout.addWidget(cart_panel)
        
        # Right Side: Product Search and Selection
        products_panel = QFrame()
        products_layout = QVBoxLayout(products_panel)
        
        search_layout = QHBoxLayout()
        self.pos_search = QLineEdit()
        self.pos_search.setPlaceholderText("بحث عن منتج (الاسم أو الباركود)...")
        self.pos_search.textChanged.connect(self.search_pos_products)
        search_layout.addWidget(self.pos_search)
        products_layout.addLayout(search_layout)
        
        # Products List for POS
        self.pos_products_table = QTableWidget(0, 3)
        self.pos_products_table.setHorizontalHeaderLabels(["الاسم", "السعر", "الكمية المتاحة"])
        self.pos_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pos_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pos_products_table.itemDoubleClicked.connect(self.add_to_cart)
        products_layout.addWidget(self.pos_products_table)
        
        layout.addWidget(products_panel)
        
        self.cart_items = []
        return page

    def search_pos_products(self):
        query = self.pos_search.text().lower()
        products = self.db.get_products()
        self.pos_products_table.setRowCount(0)
        for p in products:
            if query in p['name'].lower() or query in p.get('barcode', ''):
                row = self.pos_products_table.rowCount()
                self.pos_products_table.insertRow(row)
                self.pos_products_table.setItem(row, 0, QTableWidgetItem(p['name']))
                self.pos_products_table.item(row, 0).setData(Qt.UserRole, p['id'])
                self.pos_products_table.setItem(row, 1, QTableWidgetItem(f"{p['price']:.2f} LYD"))
                self.pos_products_table.setItem(row, 2, QTableWidgetItem(str(p['stock'])))

    def add_to_cart(self, item):
        row = item.row()
        product_id = self.pos_products_table.item(row, 0).data(Qt.UserRole)
        products = self.db.get_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if product:
            if product['stock'] <= 0:
                QMessageBox.warning(self, "خطأ", "هذا الصنف غير متوفر في المخزون!")
                return
                
            # Check if already in cart
            existing = next((item for item in self.cart_items if item['product_id'] == product_id), None)
            if existing:
                if existing['quantity'] >= product['stock']:
                    QMessageBox.warning(self, "خطأ", "لا توجد كمية كافية!")
                    return
                existing['quantity'] += 1
            else:
                self.cart_items.append({
                    "product_id": product_id,
                    "name": product['name'],
                    "quantity": 1,
                    "price": product['price']
                })
            self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(0)
        total = 0
        for item in self.cart_items:
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)
            item_total = item['quantity'] * item['price']
            total += item_total
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{item_total:.2f} LYD"))
            
        self.pos_total_label.setText(f"الإجمالي: {total:.2f} LYD")

    def clear_cart(self):
        self.cart_items = []
        self.update_cart_display()

    def process_sale(self):
        if not self.cart_items:
            QMessageBox.warning(self, "خطأ", "السلة فارغة!")
            return
            
        total = sum(item['quantity'] * item['price'] for item in self.cart_items)
        reply = QMessageBox.question(self, "تأكيد البيع", f"هل تريد إتمام عملية البيع بمبلغ {total:.2f} LYD؟", 
                                     QMessageBox.Yes | QMessageBox.No)
                                     
        if reply == QMessageBox.Yes:
            self.db.add_sale(self.cart_items, total, "Cash")
            self.clear_cart()
            self.refresh_inventory()
            self.search_pos_products()
            QMessageBox.information(self, "تم", "تمت عملية البيع بنجاح وتحديث المخزون.")

    def create_inventory(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header_row = QHBoxLayout()
        header = QLabel("إدارة المخزون")
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        
        add_btn = QPushButton("إضافة منتج")
        add_btn.setObjectName("inventoryButton")
        add_btn.setFixedWidth(120)
        add_btn.clicked.connect(self.add_product_dialog)
        
        header_row.addWidget(header)
        header_row.addStretch()
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)
        
        # Table
        self.inventory_table = QTableWidget(0, 5)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "اسم الصنف", "الماركة", "السعر", "الكمية"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.inventory_table)
        
        return page

    def add_product_dialog(self):
        dialog = ProductDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "خطأ", "يجب إدخال اسم الصنف")
                return
            self.db.add_product(data)
            self.refresh_inventory()

    def refresh_inventory(self):
        products = self.db.get_products()
        self.inventory_table.setRowCount(0)
        for p in products:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            self.inventory_table.setItem(row, 0, QTableWidgetItem(p.get('id', '')))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(p.get('name', '')))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(p.get('brand', '')))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(f"{p.get('price', 0):.2f} LYD"))
            stock_item = QTableWidgetItem(str(p.get('stock', 0)))
            if p.get('stock', 0) < 10:
                stock_item.setForeground(QColor("#ff5252"))
            self.inventory_table.setItem(row, 4, stock_item)
            
        # Update Dashboard stats
        self.card_stock.findChild(QLabel, "totalLabel").setText(str(len(products)))

    def load_styles(self):
        if os.path.exists("style.qss"):
            with open("style.qss", "r") as f:
                self.setStyleSheet(f.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
