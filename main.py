import sys
import os
import json
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QLineEdit, QFormLayout, QMessageBox, QDoubleSpinBox, QSpinBox,
                             QInputDialog, QScrollArea, QCheckBox, QProgressBar, QTabWidget, QDateEdit, QComboBox, QMenu)
from PySide6.QtCore import Qt, QSize, QTimer, QDate
from PySide6.QtGui import QColor, QPixmap, QAction
import qtawesome as qta
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtGui import QPainter

# Import all managers
from data_manager import DataManager
from backup_manager import BackupManager
from notification_manager import NotificationManager
from language_manager import LanguageManager
from invoice_manager import InvoiceManager
from user_manager import UserManager
from update_manager import UpdateManager
from ui.splash_screen import SplashScreen
from ui.login_dialog import LoginDialog
from ui.advanced_reports_dialog import AdvancedReportsDialog
from ui.reports_page import create_reports_page
from ui.settings_page import create_settings_page
from ui.dashboard_page import create_dashboard_page
from ui.pos_page import create_pos_page
from ui.inventory_page import create_inventory_page
from ui.customers_page import create_customers_page
from ui.product_dialog import ProductDialog
class MainWindow(QMainWindow):
    def __init__(self, user_data, db):
        super().__init__()
        self.user_data = user_data
        self.db = db
        self.settings = db.get_settings()

        # Initialize Managers
        self.backup_mgr = BackupManager()
        self.notification_mgr = NotificationManager(self.db)
        self.lang = LanguageManager()
        self.invoice_mgr = InvoiceManager(self.db)
        self.user_mgr = UserManager(self.db)
        self.update_mgr = UpdateManager()

        # Load saved language or default to 'ar'
        saved_lang = self.settings.get('language', 'ar')
        self.lang.set_language(saved_lang)

        self.active_shift = self.db.get_active_shift(self.user_data['username'])
        self.cart_items = []

        self.setWindowTitle(self.lang.get_text("app_title"))
        self.resize(1200, 800)
        
        try:
            with open("style.qss", "r", encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Warning: style.qss not found.")

        self.setup_ui()
        self.setup_timers()
        self.setup_language_menu()
        self.update_ui_texts()
        self.apply_permissions()
        
        # Initial data load
        self.refresh_dashboard()
        self.refresh_inventory()
        self.search_pos_products()

    def toggle_shift(self):
        if hasattr(self, 'active_shift') and self.active_shift:
            # Close Shift logic
            sales = self.db.get_sales()
            shift_sales = sum(s['total_amount'] for s in sales if s.get('shift_id') == self.active_shift['id'])
            total_expected = self.active_shift['start_cash'] + shift_sales
            
            msg = f"{self.lang.get_text('confirm_close')}\n\nإجمالي مبيعات الوردية: {shift_sales:.2f}\nالمبلغ المتوقع: {total_expected:.2f}"
            reply = QMessageBox.question(self, self.lang.get_text("close_shift"), msg, QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.close_shift(self.active_shift['id'], total_expected)
                self.active_shift = None
                QMessageBox.information(self, "تم", "تم إغلاق الوردية")
        else:
            # Open Shift logic
            val, ok = QInputDialog.getDouble(self, self.lang.get_text("open_shift"), "أدخل مبلغ العهدة الابتدائي:", 0, 0, 10000, 2)
            if ok:
                self.active_shift = self.db.open_shift(self.user_data['username'], val)
                QMessageBox.information(self, "تم", "تم فتح الوردية")
        
        self.refresh_dashboard()
        self.search_pos_products()

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
            self.search_pos_products()

    def edit_product_dialog(self, item):
        row = item.row()
        product_id = self.inventory_table.item(row, 0).text()
        product = self.db.get_product_by_id(product_id)
        
        if product:
            dialog = ProductDialog(self, product)
            result = dialog.exec()
            if result == QDialog.Accepted:
                data = dialog.get_data()
                self.db.update_product(product_id, data)
                self.refresh_inventory()
                self.refresh_dashboard()
                self.search_pos_products()
                QMessageBox.information(self, "تم", "تم التحديث")
            elif result == 2: # Deletion
                self.db.delete_product(product_id)
                self.refresh_inventory()
                self.refresh_dashboard()
                self.search_pos_products()
                QMessageBox.information(self, "تم", "تم الحذف")

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.logo_label = QLabel("SMOKEDASH")
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.logo_label)

        self.nav_btns = {}
        self.add_nav_button("dashboard", "fa5s.home", 0)
        self.add_nav_button("pos", "fa5s.shopping-cart", 1)
        self.add_nav_button("inventory", "fa5s.boxes", 2)
        self.add_nav_button("customers", "fa5s.users", 3)
        self.add_nav_button("reports", "fa5s.chart-bar", 4)
        self.sidebar_layout.addStretch()
        self.add_nav_button("settings", "fa5s.cog", 5)
        self.main_layout.addWidget(self.sidebar)

        # Content Stack
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        # Pages
        self.dashboard_page = create_dashboard_page(self)
        self.pos_page = create_pos_page(self)
        self.inventory_page = create_inventory_page(self)
        self.customers_page = create_customers_page(self)
        self.reports_page = create_reports_page(self)
        self.settings_page = create_settings_page(self)

        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.pos_page)
        self.content_stack.addWidget(self.inventory_page)
        self.content_stack.addWidget(self.customers_page)
        self.content_stack.addWidget(self.reports_page)
        self.content_stack.addWidget(self.settings_page)
        
        self.set_app_direction()

    def add_nav_button(self, key, icon, index):
        btn = QPushButton(self.lang.get_text(key))
        btn.setIcon(qta.icon(icon, color="#e0e0e0"))
        btn.setObjectName("navButton")
        btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(index))
        self.sidebar_layout.addWidget(btn)
        self.nav_btns[key] = btn
        return btn
    

    def show_advanced_reports(self):
        dialog = AdvancedReportsDialog(self.db, self)
        dialog.exec()

    def setup_timers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(300000) # Refresh every 5 minutes

    def refresh_data(self):
        # Global refresh of all UI components
        self.refresh_dashboard()
        self.refresh_inventory()
        self.refresh_customers()
        self.search_pos_products()
        
    def setup_language_menu(self):
        menubar = self.menuBar()
        lang_menu = menubar.addMenu(self.lang.get_text("language"))
        
        ar_action = QAction("العربية", self)
        ar_action.triggered.connect(lambda: self.change_language("ar"))
        lang_menu.addAction(ar_action)
        
        en_action = QAction("English", self)
        en_action.triggered.connect(lambda: self.change_language("en"))
        lang_menu.addAction(en_action)

    def change_language(self, lang_code):
        if self.lang.set_language(lang_code):
            self.update_ui_texts()
            self.set_app_direction()
            self.db.update_settings({"language": lang_code})

    def update_ui_texts(self):
        self.setWindowTitle(self.lang.get_text("app_title"))
        for key, btn in self.nav_btns.items():
            btn.setText(self.lang.get_text(key))
        # Additional logic to refresh page contents could go here

    def apply_permissions(self):
        role = self.user_data.get('role', 'cashier')
        permissions = self.user_mgr.get_role_permissions(role)
        
        if "view_reports" not in permissions:
            self.nav_btns['reports'].hide()
        if "manage_settings" not in permissions:
            self.nav_btns['settings'].hide()

    def set_app_direction(self):
        if self.lang.current_language == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

    def check_for_updates_action(self):
        if self.update_mgr.check_for_updates():
            QMessageBox.information(self, "Tحديث", "يوجد تحديث جديد متاح!")
        else:
            QMessageBox.information(self, "Tحديث", "أنت تستخدم أحدث إصدار.")

    def create_manual_backup(self):
        path = self.backup_mgr.backup()
        if path:
            QMessageBox.information(self, "نسخ احتياطي", f"تم إنشاء النسخة الاحتياطية بنجاح في:\n{path}")
        else:
            QMessageBox.critical(self, "خطأ", "فشل إنشاء النسخة الاحتياطية.")

    # POS Logic
    def search_pos_products(self):
        text = self.pos_search.text().lower()
        products = self.db.get_products()
        filtered = [p for p in products if text in p['name'].lower() or text in p.get('id', '').lower()]
        
        self.pos_products_table.setRowCount(0)
        for p in filtered:
            row = self.pos_products_table.rowCount()
            self.pos_products_table.insertRow(row)
            self.pos_products_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.pos_products_table.setItem(row, 1, QTableWidgetItem(f"{p['price']:.2f}"))
            self.pos_products_table.setItem(row, 2, QTableWidgetItem(str(p['stock'])))
            self.pos_products_table.item(row, 0).setData(Qt.UserRole, p['id'])

    def add_to_cart(self, item):
        row = item.row()
        product_id = self.pos_products_table.item(row, 0).data(Qt.UserRole)
        product = self.db.get_product_by_id(product_id)
        
        if product and product['stock'] > 0:
            quantity, ok = QInputDialog.getInt(self, "الكمية", "أدخل الكمية:", 1, 1, product['stock'])
            if ok:
                total = quantity * product['price']
                self.cart_items.append({
                    "product_id": product_id,
                    "name": product['name'],
                    "quantity": quantity,
                    "price": product['price'],
                    "total": total
                })
                self.update_cart_table()
        else:
            QMessageBox.warning(self, "خطأ", "الكمية غير متوفرة")

    def update_cart_table(self):
        self.cart_table.setRowCount(0)
        grand_total = 0
        for item in self.cart_items:
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{item['total']:.2f}"))
            grand_total += item['total']
        
        currency = self.settings.get('currency', 'LYD')
        self.pos_total_label.setText(f"الإجمالي: {grand_total:.2f} {currency}")

    def clear_cart(self):
        self.cart_items = []
        self.update_cart_table()

    def process_sale(self, method):
        if not self.cart_items:
            return
        
        if not hasattr(self, 'active_shift') or not self.active_shift:
            QMessageBox.warning(self, "خطأ", "يجب فتح وردية أولاً")
            return

        total = sum(item['total'] for item in self.cart_items)
        customer_id = None
        
        if method == "Debt":
            customers = self.db.get_customers()
            names = [c['name'] for c in customers]
            name, ok = QInputDialog.getItem(self, "اختيار عميل", "اختر العميل للدين:", names, 0, False)
            if ok:
                customer = next((c for c in customers if c['name'] == name), None)
                if customer: customer_id = customer['id']
            else: return

        self.db.add_sale(self.cart_items, total, method, self.active_shift['id'], customer_id)
        self.clear_cart()
        self.refresh_dashboard()
        self.search_pos_products()
        QMessageBox.information(self, "تم", "تمت عملية البيع بنجاح")

    # Data Refresh Methods
    def refresh_dashboard(self):
        sales = self.db.get_todays_sales()
        total_sales = sum(s['total_amount'] for s in sales)
        count = len(sales)
        products = self.db.get_products()
        total_stock = sum(p['stock'] for p in products)
        
        currency = self.settings.get('currency', 'LYD')
        self.card_sales.findChild(QLabel, "totalLabel").setText(f"{total_sales:.2f} {currency}")
        self.card_count.findChild(QLabel, "totalLabel").setText(str(count))
        self.card_stock.findChild(QLabel, "totalLabel").setText(str(total_stock))
        
        self.recent_table.setRowCount(0)
        for s in reversed(sales[-10:]):
            row = self.recent_table.rowCount()
            self.recent_table.insertRow(row)
            time_str = datetime.fromisoformat(s['timestamp']).strftime("%H:%M")
            self.recent_table.setItem(row, 0, QTableWidgetItem(time_str))
            self.recent_table.setItem(row, 1, QTableWidgetItem(f"{s['total_amount']:.2f}"))
            self.recent_table.setItem(row, 2, QTableWidgetItem(s['payment_method']))

        if hasattr(self, 'active_shift') and self.active_shift:
            self.shift_status_label.setText(f"حالة الوردية: مفتوحة ({self.user_data['username']})")
            self.shift_btn.setText("إغلاق الوردية")
        else:
            self.shift_status_label.setText("حالة الوردية: مغلقة")
            self.shift_btn.setText("فتح وردية جديدة")

    def refresh_inventory(self):
        products = self.db.get_products()
        self.inventory_table.setRowCount(0)
        for p in products:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            self.inventory_table.setItem(row, 0, QTableWidgetItem(p['id']))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(p['name']))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(p.get('brand', '-')))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(f"{p['price']:.2f}"))
            self.inventory_table.setItem(row, 4, QTableWidgetItem(str(p['stock'])))

    def refresh_customers(self):
        customers = self.db.get_customers()
        self.customers_table.setRowCount(0)
        for c in customers:
            row = self.customers_table.rowCount()
            self.customers_table.insertRow(row)
            self.customers_table.setItem(row, 0, QTableWidgetItem(c['name']))
            self.customers_table.setItem(row, 1, QTableWidgetItem(c['phone']))
            self.customers_table.setItem(row, 2, QTableWidgetItem(f"{c['debt']:.2f}"))
            self.customers_table.setItem(row, 3, QTableWidgetItem(c['created_at'][:10]))

    def add_customer_dialog(self):
        name, ok1 = QInputDialog.getText(self, "عميل جديد", "اسم العميل:")
        if ok1 and name:
            phone, ok2 = QInputDialog.getText(self, "عميل جديد", "رقم الهاتف:")
            if ok2:
                self.db.add_customer(name, phone)
                self.refresh_customers()

    def collect_debt_dialog(self):
        customers = self.db.get_customers()
        names = [c['name'] for c in customers if c['debt'] > 0]
        if not names:
            QMessageBox.information(self, "تنبيه", "لا يوجد عملاء لديهم ديون")
            return
        
        name, ok = QInputDialog.getItem(self, "تحصيل دين", "اختر العميل:", names, 0, False)
        if ok:
            customer = next((c for c in customers if c['name'] == name), None)
            amount, ok2 = QInputDialog.getDouble(self, "تحصيل دين", f"المبلغ المحصل (الدين الحالي: {customer['debt']:.2f}):", 0, 0, customer['debt'], 2)
            if ok2:
                self.db.update_customer_debt(customer['id'], -amount)
                self.refresh_customers()
                QMessageBox.information(self, "تم", "تم التحصيل بنجاح")

    def generate_last_invoice_pdf(self):
        sales = self.db.get_sales()
        if not sales:
            QMessageBox.warning(self, "خطأ", "لا توجد مبيعات")
            return
        last_sale = sales[-1]
        path = self.invoice_mgr.create_invoice(last_sale)
        if path:
            QMessageBox.information(self, "تم", f"تم إنشاء الفاتورة في:\n{path}")
        else:
            QMessageBox.critical(self, "خطأ", "فشل إنشاء الفاتورة")

    def closeEvent(self, event):
        # Optional: Auto-backup on close
        self.backup_mgr.backup()
        event.accept()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # عرض شاشة التحميل
    splash = SplashScreen()
    splash.show()
    
    splash.update_progress(10, "جاري تحميل قاعدة البيانات...")
    db = DataManager()
    
    splash.update_progress(30, "جاري تحميل الإعدادات...")
    # ... بقية عملية التحميل
    
    splash.update_progress(100, "جاهز!")
    splash.close()
    
    login = LoginDialog(db)
    if login.exec():
        window = MainWindow(login.user_data, db)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)