import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QLineEdit, QFormLayout, QMessageBox, QDoubleSpinBox, QSpinBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
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
        self.name_input.setPlaceholderText("أدخل اسم الصنف (مثل: مالبورو أحمر)...")
        
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("أدخل اسم الماركة (مثل: Philip Morris)...")
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(9999.99)
        self.price_input.setMinimum(0.01)
        currency = self.parent().settings.get('currency', 'LYD') if self.parent() else 'LYD'
        self.price_input.setSuffix(f" {currency}")
        
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(100000)
        self.stock_input.setValue(10)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("امسح الباركود أو أدخله يدوياً...")
        
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
        self.settings = self.db.get_settings()
        self.setup_ui()
        self.load_styles()
        self.refresh_inventory()
        self.refresh_dashboard()
        self.search_pos_products() # Show all products initially

    def setup_ui(self):
        shop_name = self.settings.get('shop_name', 'SmokeDash')
        self.setWindowTitle(f"{shop_name} - منظومة إدارة محل سجائر")
        self.resize(1150, 800)
        self.setLayoutDirection(Qt.RightToLeft)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()

        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        # Pages
        self.dashboard_page = self.create_dashboard()
        self.pos_page = self.create_pos()
        self.inventory_page = self.create_inventory()
        self.reports_page = self.create_reports()
        self.settings_page = self.create_settings()

        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.pos_page)
        self.content_stack.addWidget(self.inventory_page)
        self.content_stack.addWidget(self.reports_page)
        self.content_stack.addWidget(self.settings_page)

    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 30, 10, 30)
        self.sidebar_layout.setSpacing(10)

        shop_name = self.settings.get('shop_name', 'SMOKEDASH')
        logo_label = QLabel(shop_name.upper())
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(logo_label)

        self.nav_btns = []
        self.create_nav_btn("لوحة التحكم", "fa5s.home", 0)
        self.create_nav_btn("نقطة البيع (POS)", "fa5s.shopping-cart", 1)
        self.create_nav_btn("إدارة المخزون", "fa5s.boxes", 2)
        self.create_nav_btn("التقارير", "fa5s.chart-bar", 3)
        self.sidebar_layout.addStretch()
        self.create_nav_btn("الإعدادات", "fa5s.cog", 4)
        
        self.main_layout.addWidget(self.sidebar)

    def create_nav_btn(self, text, icon_name, index):
        btn = QPushButton(text)
        btn.setIcon(qta.icon(icon_name, color="#e0e0e0"))
        btn.setIconSize(QSize(20, 20))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(50)
        btn.setStyleSheet("text-align: right; padding-right: 20px; font-size: 15px; border: none;")
        if index != -1:
            btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(index))
        self.sidebar_layout.addWidget(btn)
        self.nav_btns.append(btn)
        return btn

    def create_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        shop_name = self.settings.get('shop_name', 'سموك داش')
        header = QLabel(f"أهلاً بك في {shop_name}")
        header.setObjectName("welcomeLabel")
        layout.addWidget(header)
        
        sub = QLabel("متابعة سريعة لأداء المحل اليوم")
        sub.setStyleSheet("color: #8b949e; font-size: 16px; margin-bottom: 25px;")
        layout.addWidget(sub)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(25)
        currency = self.settings.get('currency', 'LYD')
        self.card_sales = self.create_stats_card("مبيعات اليوم", f"0.00 {currency}", "fa5s.money-bill-wave")
        self.card_count = self.create_stats_card("عدد العمليات", "0", "fa5s.receipt")
        self.card_stock = self.create_stats_card("الأصناف المتوفرة", "0", "fa5s.box-open")
        
        stats_layout.addWidget(self.card_sales)
        stats_layout.addWidget(self.card_count)
        stats_layout.addWidget(self.card_stock)
        layout.addLayout(stats_layout)
        
        layout.addSpacing(40)
        recent_label = QLabel("آخر العمليات")
        recent_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        layout.addWidget(recent_label)
        
        self.recent_table = QTableWidget(0, 3)
        self.recent_table.setHorizontalHeaderLabels(["الوقت", "المبلغ", "طريقة الدفع"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setFixedHeight(300)
        layout.addWidget(self.recent_table)
        
        layout.addStretch()
        return page

    def create_stats_card(self, title, value, icon):
        card = QFrame()
        card.setObjectName("statsCard")
        card_layout = QVBoxLayout(card)
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color="#58a6ff").pixmap(40, 40))
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888888; font-size: 15px; font-weight: bold;")
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
        layout.setSpacing(20)
        
        cart_panel = QFrame()
        cart_panel.setFixedWidth(420)
        cart_panel.setObjectName("sidebar") # Reuse sidebar glass style
        cart_layout = QVBoxLayout(cart_panel)
        cart_layout.setContentsMargins(20, 20, 20, 20)
        
        cart_label = QLabel("سلة المشتريات")
        cart_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00bcd4;")
        cart_layout.addWidget(cart_label)
        
        self.cart_table = QTableWidget(0, 3)
        self.cart_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "الإجمالي"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        cart_layout.addWidget(self.cart_table)
        
        total_frame = QFrame()
        total_frame.setObjectName("totalFrame")
        total_layout = QVBoxLayout(total_frame)
        currency = self.settings.get('currency', 'LYD')
        self.pos_total_label = QLabel(f"الإجمالي: 0.00 {currency}")
        self.pos_total_label.setObjectName("posTotalLabel")
        self.pos_total_label.setAlignment(Qt.AlignCenter)
        total_layout.addWidget(self.pos_total_label)
        cart_layout.addWidget(total_frame)
        
        pay_layout = QHBoxLayout()
        
        self.pay_cash_btn = QPushButton("كاش (نقد)")
        self.pay_cash_btn.setObjectName("posButton")
        self.pay_cash_btn.setFixedHeight(60)
        self.pay_cash_btn.clicked.connect(lambda: self.process_sale("Cash"))
        
        self.pay_card_btn = QPushButton("بطاقة مصرفية")
        self.pay_card_btn.setObjectName("inventoryButton") # Use secondary color
        self.pay_card_btn.setFixedHeight(60)
        self.pay_card_btn.clicked.connect(lambda: self.process_sale("Card"))
        
        pay_layout.addWidget(self.pay_cash_btn)
        pay_layout.addWidget(self.pay_card_btn)
        cart_layout.addLayout(pay_layout)
        
        clear_btn = QPushButton("تفريغ السلة")
        clear_btn.setFixedHeight(40)
        clear_btn.clicked.connect(self.clear_cart)
        cart_layout.addWidget(clear_btn)
        
        layout.addWidget(cart_panel)
        
        products_panel = QFrame()
        products_layout = QVBoxLayout(products_panel)
        self.pos_search = QLineEdit()
        self.pos_search.setPlaceholderText("🔍  ابحث عن صنف أو امسح الباركود...")
        self.pos_search.setFixedHeight(55)
        self.pos_search.textChanged.connect(self.search_pos_products)
        products_layout.addWidget(self.pos_search)
        
        self.pos_products_table = QTableWidget(0, 3)
        self.pos_products_table.setHorizontalHeaderLabels(["الاسم", "السعر", "المتوفر"])
        self.pos_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pos_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pos_products_table.itemDoubleClicked.connect(self.add_to_cart)
        products_layout.addWidget(self.pos_products_table)
        
        layout.addWidget(products_panel)
        self.cart_items = []
        return page

    def create_inventory(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        header_row = QHBoxLayout()
        header = QLabel("إدارة المخزون")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        add_btn = QPushButton(" + إضافة صنف جديد")
        add_btn.setObjectName("inventoryButton")
        add_btn.setFixedWidth(180)
        add_btn.setFixedHeight(45)
        add_btn.clicked.connect(self.add_product_dialog)
        header_row.addWidget(header)
        header_row.addStretch()
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)
        
        self.inventory_table = QTableWidget(0, 5)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "اسم الصنف", "الماركة", "السعر", "الكمية"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.inventory_table)
        return page

    def create_reports(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        header = QLabel("تقارير المبيعات")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        layout.addWidget(header)
        self.sales_report_table = QTableWidget(0, 4)
        self.sales_report_table.setHorizontalHeaderLabels(["رقم العملية", "الوقت", "المبلغ الإجمالي", "طريقة الدفع"])
        self.sales_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.sales_report_table)
        refresh_btn = QPushButton("تحديث البيانات")
        refresh_btn.setFixedWidth(150)
        refresh_btn.clicked.connect(self.refresh_reports)
        layout.addWidget(refresh_btn)
        return page

    def create_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        header = QLabel("إعدادات المنظومة")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        layout.addWidget(header)
        form = QFormLayout()
        self.shop_name_input = QLineEdit()
        self.shop_name_input.setPlaceholderText("أدخل اسم متجرك ليظهر في واجهة البرنامج...")
        self.currency_input = QLineEdit()
        self.currency_input.setPlaceholderText("أدخل رمز العملة المعتمد في متجرك (مثال: LYD)...")
        form.addRow("اسم المحل:", self.shop_name_input)
        form.addRow("العملة المستخدمة:", self.currency_input)
        
        # Load current settings into inputs
        self.shop_name_input.setText(self.settings.get('shop_name', 'SmokeDash'))
        self.currency_input.setText(self.settings.get('currency', 'LYD'))
        
        layout.addLayout(form)
        save_settings_btn = QPushButton("حفظ الإعدادات")
        save_settings_btn.setObjectName("posButton")
        save_settings_btn.setFixedWidth(200)
        save_settings_btn.clicked.connect(self.save_settings_action)
        layout.addWidget(save_settings_btn)
        layout.addStretch()
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
                currency = self.settings.get('currency', 'LYD')
                self.pos_products_table.setItem(row, 1, QTableWidgetItem(f"{p['price']:.2f} {currency}"))
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
            existing = next((item for item in self.cart_items if item['product_id'] == product_id), None)
            if existing:
                if existing['quantity'] >= product['stock']:
                    QMessageBox.warning(self, "خطأ", "لا توجد كمية كافية!")
                    return
                existing['quantity'] += 1
            else:
                self.cart_items.append({"product_id": product_id, "name": product['name'], "quantity": 1, "price": product['price']})
            self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(0)
        total = 0
        currency = self.settings.get('currency', 'LYD')
        for item in self.cart_items:
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)
            item_total = item['quantity'] * item['price']
            total += item_total
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{item_total:.2f} {currency}"))
        self.pos_total_label.setText(f"الإجمالي: {total:.2f} {currency}")

    def clear_cart(self):
        self.cart_items = []
        self.update_cart_display()

    def process_sale(self, payment_method="Cash"):
        if not self.cart_items:
            QMessageBox.warning(self, "خطأ", "السلة فارغة!")
            return
        total = sum(item['quantity'] * item['price'] for item in self.cart_items)
        currency = self.settings.get('currency', 'LYD')
        method_ar = "نقدًا" if payment_method == "Cash" else "بطاقة"
        reply = QMessageBox.question(self, "تأكيد البيع", f"هل تريد إتمام عملية البيع ({method_ar}) بمبلغ {total:.2f} {currency}؟", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.add_sale(self.cart_items, total, payment_method)
            self.clear_cart()
            self.refresh_inventory()
            self.refresh_dashboard()
            self.refresh_reports()
            self.search_pos_products()
            QMessageBox.information(self, "تم", f"تمت عملية البيع ({method_ar}) بنجاح وتحديث المخزون.")

    def add_product_dialog(self):
        dialog = ProductDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "خطأ", "يجب إدخال اسم الصنف")
                return
            self.db.add_product(data)
            self.refresh_inventory()
            self.refresh_dashboard()

    def refresh_inventory(self):
        products = self.db.get_products()
        self.inventory_table.setRowCount(0)
        for p in products:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            self.inventory_table.setItem(row, 0, QTableWidgetItem(p.get('id', '')))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(p.get('name', '')))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(p.get('brand', '')))
            currency = self.settings.get('currency', 'LYD')
            self.inventory_table.setItem(row, 3, QTableWidgetItem(f"{p.get('price', 0):.2f} {currency}"))
            stock_item = QTableWidgetItem(str(p.get('stock', 0)))
            if p.get('stock', 0) < 10: stock_item.setForeground(QColor("#ff5252"))
            self.inventory_table.setItem(row, 4, stock_item)

    def refresh_dashboard(self):
        products = self.db.get_products()
        sales = self.db.get_sales()
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = sum(s['total_amount'] for s in sales if s['timestamp'].startswith(today))
        today_count = sum(1 for s in sales if s['timestamp'].startswith(today))
        self.card_stock.findChild(QLabel, "totalLabel").setText(str(len(products)))
        currency = self.settings.get('currency', 'LYD')
        self.card_sales.findChild(QLabel, "totalLabel").setText(f"{today_sales:.2f} {currency}")
        self.card_count.findChild(QLabel, "totalLabel").setText(str(today_count))
        self.recent_table.setRowCount(0)
        for s in reversed(sales[-5:]):
            row = self.recent_table.rowCount()
            self.recent_table.insertRow(row)
            time_str = datetime.fromisoformat(s['timestamp']).strftime("%H:%M:%S")
            self.recent_table.setItem(row, 0, QTableWidgetItem(time_str))
            currency = self.settings.get('currency', 'LYD')
            self.recent_table.setItem(row, 1, QTableWidgetItem(f"{s['total_amount']:.2f} {currency}"))
            method_ar = "نقدًا" if s['payment_method'] == "Cash" else "بطاقة"
            self.recent_table.setItem(row, 2, QTableWidgetItem(method_ar))

    def refresh_reports(self):
        sales = self.db.get_sales()
        self.sales_report_table.setRowCount(0)
        for s in reversed(sales):
            row = self.sales_report_table.rowCount()
            self.sales_report_table.insertRow(row)
            self.sales_report_table.setItem(row, 0, QTableWidgetItem(s['id']))
            time_str = datetime.fromisoformat(s['timestamp']).strftime("%Y-%m-%d %H:%M")
            self.sales_report_table.setItem(row, 1, QTableWidgetItem(time_str))
            currency = self.settings.get('currency', 'LYD')
            self.sales_report_table.setItem(row, 2, QTableWidgetItem(f"{s['total_amount']:.2f} {currency}"))
            method_ar = "نقدًا" if s['payment_method'] == "Cash" else "بطاقة"
            self.sales_report_table.setItem(row, 3, QTableWidgetItem(method_ar))

    def save_settings_action(self):
        new_settings = {
            "shop_name": self.shop_name_input.text(),
            "currency": self.currency_input.text(),
            "theme": self.settings.get('theme', 'dark')
        }
        self.db.save_settings(new_settings)
        self.settings = new_settings
        QMessageBox.information(self, "تم", "تم حفظ الإعدادات بنجاح. سيتم تطبيق التغييرات على بعض العناصر فوراً، وللعناصر الأخرى يرجى إعادة تشغيل البرنامج.")
        # Apply some changes immediately
        self.setWindowTitle(f"{new_settings['shop_name']} - منظومة إدارة محل سجائر")
        self.sidebar.findChild(QLabel, "logoLabel").setText(new_settings['shop_name'].upper())
        self.refresh_dashboard()
        self.refresh_inventory()
        self.refresh_reports()
        self.search_pos_products()
        self.update_cart_display()

    def load_styles(self):
        if os.path.exists("style.qss"):
            with open("style.qss", "r") as f:
                self.setStyleSheet(f.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
