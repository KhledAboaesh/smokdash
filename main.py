import sys
import os
import json
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QLineEdit, QFormLayout, QMessageBox, QDoubleSpinBox, QSpinBox,
                             QInputDialog, QScrollArea, QCheckBox, QProgressBar, QTabWidget, QDateEdit, QComboBox, QMenu,
                             QToolBar, QStatusBar)
from PySide6.QtCore import Qt, QSize, QTimer, QDate
from PySide6.QtGui import QColor, QPixmap, QAction
import qtawesome as qta

# Import Managers
from data_manager import DataManager
from backup_manager import BackupManager
from notification_manager import NotificationManager
from language_manager import LanguageManager
from invoice_manager import InvoiceManager
from user_manager import UserManager
from update_manager import UpdateManager

# Import Controllers
from controllers.pos_controller import POSController
from controllers.inventory_controller import InventoryController

# Import Components & Base
from components.style_engine import Colors, StyleEngine
from components.navigation_manager import NavigationManager
from ui.base_page import BasePage
from ui.dashboard_page import DashboardPage
from ui.pos_page import POSPage
from ui.inventory_page import InventoryPage
from ui.customers_page import CustomersPage
from ui.users_page import UserPermissionsPage
from ui.reports_page import ReportsPage
from ui.settings_page import SettingsPage
from ui.product_dialog import ProductDialog
from ui.customer_dialog import CustomerDialog
from ui.user_dialog import UserDialog
from ui.splash_screen import SplashScreen
from ui.login_dialog import LoginDialog

class MainWindow(QMainWindow):
    def __init__(self, user_data, db):
        super().__init__()
        self.user_data = user_data
        self.db = db
        self.settings = db.get_settings()
        
        # 1. Initialize Managers
        self.setup_managers()
        
        # 2. Window Config
        self.setWindowTitle(self.lang.get_text("app_title"))
        self.resize(1200, 800)
        self.set_app_styling()
        
        # 3. Core UI Shell
        self.active_shift = self.db.get_active_shift(self.user_data['username'])
        
        # Initialize Controllers
        self.pos_ctrl = POSController(self.db, self)
        self.inventory_ctrl = InventoryController(self.db, self)
        self.cart_items = self.pos_ctrl.cart_items # Link for compatibility
        
        self.setup_ui_shell()
        
        # 4. Routing & Pages
        self.nav_manager = NavigationManager(self, self.content_stack, self.sidebar_layout)
        self.initialize_pages()
        
        # 5. Global Features
        self.setup_statusbar()
        self.setup_toolbar()
        self.setup_timers()
        
        # 6. Localization
        self.set_app_direction()
        
        # Initial Data load
        self.refresh_data()
        
        # Start
        self.nav_manager.switch_page(0)

    def setup_managers(self):
        self.backup_mgr = BackupManager()
        self.notification_mgr = NotificationManager(self.db)
        self.lang = LanguageManager()
        self.invoice_mgr = InvoiceManager(self.db)
        self.user_mgr = UserManager(self.db)
        self.update_mgr = UpdateManager()
        
        saved_lang = self.settings.get('language', 'ar')
        self.lang.set_language(saved_lang)

    def set_app_styling(self):
        try:
            with open("style.qss", "r", encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except:
            pass

    def setup_ui_shell(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        
        self.logo = QLabel("SMOKEDASH 2.0")
        self.logo.setObjectName("logoLabel")
        self.logo.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.logo)
        self.sidebar_layout.addSpacing(20)
        
        self.main_layout.addWidget(self.sidebar)
        
        # Content Area
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

    def initialize_pages(self):
        self.dashboard_page = DashboardPage(self)
        self.pos_page = POSPage(self)
        self.inventory_page = InventoryPage(self)
        self.customers_page = CustomersPage(self)
        self.users_page = UserPermissionsPage(self)
        self.reports_page = ReportsPage(self)
        self.settings_page = SettingsPage(self)
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.pos_page)
        self.content_stack.addWidget(self.inventory_page)
        self.content_stack.addWidget(self.customers_page)
        self.content_stack.addWidget(self.users_page)
        self.content_stack.addWidget(self.reports_page)
        self.content_stack.addWidget(self.settings_page)
        
        self.nav_manager.add_navigation("dashboard", self.lang.get_text("dashboard"), "fa5s.chart-line", 0)
        self.nav_manager.add_navigation("pos", self.lang.get_text("pos"), "fa5s.shopping-cart", 1)
        self.nav_manager.add_navigation("inventory", self.lang.get_text("inventory"), "fa5s.boxes", 2)
        self.nav_manager.add_navigation("customers", self.lang.get_text("customers"), "fa5s.users", 3)
        self.nav_manager.add_navigation("users", self.lang.get_text("users"), "fa5s.user-shield", 4)
        self.nav_manager.add_navigation("reports", self.lang.get_text("reports"), "fa5s.file-invoice", 5)
        self.nav_manager.add_navigation("settings", self.lang.get_text("settings"), "fa5s.cog", 6)

    # --- POS Logic ---
    def search_pos_products(self):
        text = self.pos_page.search_input.text()
        filtered = self.pos_ctrl.search_products(text)
        
        tbl = self.pos_page.products_table
        tbl.setRowCount(0)
        for p in filtered:
            row = tbl.rowCount()
            tbl.insertRow(row)
            tbl.setItem(row, 0, QTableWidgetItem(p['name']))
            tbl.setItem(row, 1, QTableWidgetItem(f"{p['price']:.2f}"))
            tbl.setItem(row, 2, QTableWidgetItem(str(p['stock'])))
            tbl.item(row, 0).setData(Qt.UserRole, p['id'])

    def add_to_cart(self, item):
        row = item.row()
        product_id = self.pos_page.products_table.item(row, 0).data(Qt.UserRole)
        success, msg = self.pos_ctrl.add_to_cart(product_id)
        
        if success:
            self.update_cart_ui()
        else:
            QMessageBox.warning(self, "خطأ", msg)

    def update_cart_ui(self):
        tbl = self.pos_page.cart_table
        tbl.setRowCount(0)
        cart_items = self.pos_ctrl.cart_items
        for item in cart_items:
            row = tbl.rowCount()
            tbl.insertRow(row)
            tbl.setItem(row, 0, QTableWidgetItem(item['name']))
            tbl.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            tbl.setItem(row, 2, QTableWidgetItem(f"{item['total']:.2f}"))
        
        currency = self.settings.get('currency', 'LYD')
        self.pos_page.total_label.setText(f"الإجمالي: {self.pos_ctrl.get_cart_total():.2f} {currency}")

    def clear_cart(self):
        self.pos_ctrl.clear_cart()
        self.update_cart_ui()

    def process_sale(self, method):
        customer_id = None
        if method == "Debt":
            # Select customer for debt
            from PySide6.QtWidgets import QInputDialog
            customers = self.db.get_customers()
            names = [c['name'] for c in customers]
            if not names:
                QMessageBox.warning(self, "خطأ", "يجب إضافة عملاء أولاً لإجراء مبيعات آجلة.")
                return
            name, ok = QInputDialog.getItem(self, "اختيار عميل", "اختر العميل المعني بالدين:", names, 0, False)
            if not ok: return
            customer = next(c for c in customers if c['name'] == name)
            customer_id = customer['id']

        shift_id = self.active_shift['id'] if self.active_shift else "manual"
        success, msg = self.pos_ctrl.process_sale(method, shift_id, customer_id)
        
        if success:
            self.update_cart_ui()
            self.refresh_data()
            self.search_pos_products()
            QMessageBox.information(self, "تم", msg)
        else:
            QMessageBox.warning(self, "خطأ", msg)

    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.status_user = QLabel(f"👤 {self.user_data['full_name']} ({self.user_data['role']})")
        self.status_user.setStyleSheet(f"margin-left: 20px; color: {Colors.ACCENT}; font-weight: bold;")
        self.statusbar.addWidget(self.status_user)

    def setup_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(22, 22))
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        backup_act = QAction(qta.icon("fa5s.database", color=Colors.TEXT_SECONDARY), "نسخة احتياطية", self)
        backup_act.triggered.connect(self.db_backup_quick)
        self.toolbar.addAction(backup_act)

    def db_backup_quick(self):
        filename = self.backup_mgr.create_backup()
        if filename:
            QMessageBox.information(self, "نجاح", f"تم إنشاء نسخة احتياطية سريعة:\n{filename}")

    def setup_timers(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(300000)

    def refresh_data(self):
        if hasattr(self, 'dashboard_page'): self.dashboard_page.refresh()
        if hasattr(self, 'pos_page'): self.search_pos_products()
        if hasattr(self, 'inventory_page'): self.inventory_page.refresh()
        if hasattr(self, 'customers_page'): self.customers_page.refresh()
        if hasattr(self, 'users_page'): self.users_page.refresh()
        if hasattr(self, 'reports_page'): self.reports_page.refresh()

    # --- User Permissions Logic ---
    def add_user_dialog(self):
        dialog = UserDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.db.add_user(data)
            self.refresh_data()
            QMessageBox.information(self, "تم", "تمت إضافة الموظف بنجاح")

    def open_user_drawer(self, item):
        row = item.row()
        username = self.users_page.table.item(row, 0).text()
        user = next((u for u in self.db.get_users() if u['username'] == username), None)
        if user:
            self.users_page.edit_name.setText(user['username'])
            self.users_page.edit_fullname.setText(user.get('full_name', ''))
            self.users_page.edit_phone.setText(user.get('phone', ''))
            self.users_page.edit_role.setCurrentText(user.get('role', 'cashier'))
            if hasattr(self.users_page, 'edit_pwd'):
                self.users_page.edit_pwd.setText(user.get('password', ''))
            self.users_page.drawer.show()

    def save_user_drawer(self):
        username = self.users_page.edit_name.text()
        if username == "admin":
            QMessageBox.warning(self, "تنبيه", "لا يمكن تعديل المدير العام")
            return
        
        data = {
            "full_name": self.users_page.edit_fullname.text(),
            "phone": self.users_page.edit_phone.text(),
            "role": self.users_page.edit_role.currentText()
        }
        if hasattr(self.users_page, 'edit_pwd'):
            data["password"] = self.users_page.edit_pwd.text()
        
        users = self.db.get_users()
        for u in users:
            if u['username'] == username:
                u.update(data)
                break
        self.db._save_json(self.db.users_file, users)
        self.refresh_data()
        self.users_page.drawer.hide()
        QMessageBox.information(self, "تم", "تم تحديث البيانات")

    # --- Reports Logic ---
    def generate_last_invoice_pdf(self):
        sales = self.db.get_sales()
        if not sales:
            QMessageBox.warning(self, self.lang.get_text("reports"), "لا يوجد عمليات بيع سابقة لإصدار فاتورة.")
            return
        path = self.invoice_mgr.create_invoice(sales[-1])
        if path: QMessageBox.information(self, "تم", f"تم حفظ الفاتورة في:\n{path}")

    def show_advanced_reports(self):
        from ui.advanced_reports_dialog import AdvancedReportsDialog
        dialog = AdvancedReportsDialog(self.db, self)
        dialog.exec()

    # --- Settings Logic ---
    def change_language(self, lang_code):
        if self.lang.set_language(lang_code):
            self.db.save_settings({"language": lang_code})
            QMessageBox.information(self, "تنبيه", "يرجى إعادة تشغيل التطبيق لتطبيق اللغة الجديدة بالكامل.")

    def create_manual_backup(self):
        path = self.backup_mgr.backup()
        if path: QMessageBox.information(self, "نجاح", f"تم إنشاء النسخة الاحتياطية:\n{path}")

    def check_for_updates_action(self):
        if self.update_mgr.check_for_updates():
            QMessageBox.information(self, "تحديث", "يوجد تحديث متاح!")
        else:
            QMessageBox.information(self, "تحديث", "أنت تستخدم أحدث إصدار.")

    # --- Inventory Logic ---
    def add_product_dialog(self):
        dialog = ProductDialog(self)
        if dialog.exec():
            success, msg = self.inventory_ctrl.add_product(dialog.get_data())
            if success:
                self.refresh_data()
                QMessageBox.information(self, "تم", msg)
            else:
                QMessageBox.warning(self, "خطأ", msg)

    def edit_product_dialog(self, item):
        row = item.row()
        product_id = self.inventory_page.table.item(row, 0).text()
        product = self.db.get_product_by_id(product_id)
        if product:
            dialog = ProductDialog(self, product)
            res = dialog.exec()
            success, msg = False, ""
            if res == QDialog.Accepted:
                success, msg = self.inventory_ctrl.update_product(product_id, dialog.get_data())
            elif res == 2: # Delete
                success, msg = self.inventory_ctrl.delete_product(product_id)
            
            if success:
                self.refresh_data()
                QMessageBox.information(self, "تم", msg)
            elif msg:
                QMessageBox.warning(self, "خطأ", msg)

    # --- CRM Logic ---
    def add_customer_dialog(self):
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.db.add_customer(dialog.get_data())
            self.refresh_data()
            QMessageBox.information(self, "تم", "تمت إضافة العميل بنجاح")

    def edit_customer_dialog(self, item):
        row = item.row()
        customer_id = self.customers_page.table.item(row, 0).text()
        customer = next((c for c in self.db.get_customers() if c['id'] == customer_id), None)
        if customer:
            dialog = CustomerDialog(self, customer)
            if dialog.exec():
                self.db.update_customer(customer_id, dialog.get_data())
                self.refresh_data()
                QMessageBox.information(self, "تم", "تم تحديث بيانات العميل")

    def collect_debt_dialog(self):
        customers = [c for c in self.db.get_customers() if c['debt'] > 0]
        if not customers:
            QMessageBox.information(self, self.lang.get_text("reports"), "لا يوجد ديون مستحقة!")
            return
        
        names = [c['name'] for c in customers]
        name, ok = QInputDialog.getItem(self, self.lang.get_text("collect_debt"), "اختر العميل:", names, 0, False)
        if ok:
            customer = next(c for c in customers if c['name'] == name)
            amount, ok2 = QInputDialog.getDouble(self, self.lang.get_text("collect_debt"), 
                                                 f"المبلغ المستلم (الدين الحالي: {customer['debt']:.2f}):", 
                                                 0, 0, customer['debt'], 2)
            if ok2:
                self.db.update_customer_debt(customer['id'], -amount)
                self.refresh_data()
                QMessageBox.information(self, "تم", "تم تحصيل المبلغ وتحديث سجل العميل بنجاح")

    def set_app_direction(self):
        direction = Qt.RightToLeft if self.lang.current_language == "ar" else Qt.LeftToRight
        self.setLayoutDirection(direction)

    def closeEvent(self, event):
        self.backup_mgr.backup()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = DataManager()
    login = LoginDialog(db)
    if login.exec():
        window = MainWindow(login.user_data, db)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)