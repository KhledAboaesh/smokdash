import sys
import os
import json
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QStatusBar, QToolBar, QMessageBox, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QLineEdit, QFormLayout, QDoubleSpinBox, QSpinBox,
                             QInputDialog, QCheckBox, QProgressBar, QTabWidget, QDateEdit, QComboBox, QMenu)
from PySide6.QtCore import Qt, QSize, QTimer, QDate
from PySide6.QtGui import QColor, QPixmap, QAction
import qtawesome as qta
from components.utils import resource_path

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
from ui.customers_page import CustomersPage
from ui.users_page import UserPermissionsPage
from ui.reports_page import ReportsPage
from ui.settings_page import SettingsPage
from ui.invoices_page import InvoicesPage
from ui.product_dialog import ProductDialog
from ui.customer_dialog import CustomerDialog
from ui.user_dialog import UserDialog
from ui.splash_screen import SplashScreen
from ui.login_dialog import LoginDialog
from ui.shift_dialogs import OpenShiftDialog, CloseShiftDialog

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
        self.setWindowIcon(QPixmap(resource_path("logo.png")))
        self.resize(1200, 800)
        
        # 3. Core UI Shell
        self.active_shift = self.db.get_active_shift(self.user_data['username'])
        
        # Initialize Controllers
        self.pos_ctrl = POSController(self.db, self)
        self.inventory_ctrl = InventoryController(self.db, self)
        self.cart_items = self.pos_ctrl.cart_items # Link for compatibility
        
        self.setup_ui_shell()
        
        # 4. Routing & Pages
        self.nav_manager = NavigationManager(self, self.content_stack, self.nav_buttons_layout)
        start_idx = self.initialize_pages()
        
        # 5. Global Features
        self.setup_statusbar()
        self.setup_toolbar()
        self.setup_timers()
        
        # 6. Localization
        self.set_app_direction()
        
        # Initial Data load
        self.refresh_data()
        
        # 7. Shift Enforcement
        QTimer.singleShot(100, self.force_shift_check)
        
        # Start
        self.nav_manager.switch_page(start_idx)

    def setup_managers(self):
        self.backup_mgr = BackupManager()
        self.notification_mgr = NotificationManager(self.db)
        self.lang = LanguageManager()
        self.invoice_mgr = InvoiceManager(self.db)
        self.user_mgr = UserManager(self.db)
        self.update_mgr = UpdateManager()
        
        saved_lang = self.settings.get('language', 'ar')
        self.lang.set_language(saved_lang)


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
        
        # Brand Logo at Top
        self.logo_img = QLabel()
        # Initial pixmap, scaling will be handled by resizeEvent
        self.logo_img.setPixmap(QPixmap(resource_path("logo.png"))) 
        self.logo_img.setAlignment(Qt.AlignCenter)
        self.logo_img.setContentsMargins(0, 20, 0, 10)
        self.sidebar_layout.addWidget(self.logo_img)
        
        self.logo_text = QLabel("SMOKEDASH V3.0")
        self.logo_text.setObjectName("logoLabel")
        self.logo_text.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.logo_text)
        self.sidebar_layout.addSpacing(10)
        
        # Shift Status Label in Sidebar
        self.shift_status_widget = QFrame()
        self.shift_status_widget.setObjectName("statsCard")
        self.shift_status_widget.setFixedHeight(80)
        ss_layout = QVBoxLayout(self.shift_status_widget)
        
        self.shift_lbl = QLabel("الوردية: مغلقة 🔴")
        self.shift_lbl.setStyleSheet("font-weight: bold; color: #FDFCF0;")
        self.shift_lbl.setAlignment(Qt.AlignCenter)
        ss_layout.addWidget(self.shift_lbl)
        
        self.shift_btn = QPushButton("فتح الوردية")
        self.shift_btn.setObjectName("posButton")
        self.shift_btn.setFixedHeight(30)
        self.shift_btn.clicked.connect(self.toggle_shift)
        ss_layout.addWidget(self.shift_btn)
        
        self.sidebar_layout.addWidget(self.shift_status_widget)
        self.sidebar_layout.addSpacing(10)
        
        # Add scroll area for navigation buttons
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setFrameShape(QFrame.NoFrame)
        
        nav_container = QWidget()
        self.nav_buttons_layout = QVBoxLayout(nav_container)
        self.nav_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_buttons_layout.setSpacing(2)
        
        nav_scroll.setWidget(nav_container)
        self.sidebar_layout.addWidget(nav_scroll, 1) # Give it stretch to fill space
        
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
        self.invoices_page = InvoicesPage(self)
        
        # Determine Permissions
        perms = self.user_data.get('permissions', [])
        role = self.user_data.get('role', 'cashier')
        
        # Legacy/Default Fallback
        if not perms:
            if role == 'admin':
                perms = ['dashboard', 'pos', 'inventory', 'customers', 'users', 'reports', 'settings', 'invoices']
            else:
                 # Default for cashier/others
                perms = ['pos', 'customers', 'invoices']
        
        # Register Pages & Navigation if permitted
        self.available_pages = []
        
        def add_page(key, page_widget, label, icon, index_id):
            if key in perms:
                self.content_stack.addWidget(page_widget)
                self.nav_manager.add_navigation(key, label, icon, index_id)
                self.available_pages.append(index_id)
        
        # Add all to stack first to keep indices consistent (0=Dash, 1=POS, etc)
        self.content_stack.addWidget(self.dashboard_page) # 0
        self.content_stack.addWidget(self.pos_page)       # 1
        self.content_stack.addWidget(self.inventory_page) # 2
        self.content_stack.addWidget(self.customers_page) # 3
        self.content_stack.addWidget(self.users_page)     # 4
        self.content_stack.addWidget(self.reports_page)   # 5
        self.content_stack.addWidget(self.settings_page)  # 6
        self.content_stack.addWidget(self.invoices_page)  # 7
        
        # Register Nav Buttons conditionally
        # Updated icons for visual hierarchy
        if 'dashboard' in perms: self.nav_manager.add_navigation("dashboard", self.lang.get_text("dashboard"), "fa5s.chart-line", 0)
        if 'pos' in perms: self.nav_manager.add_navigation("pos", self.lang.get_text("pos"), "fa5s.shopping-cart", 1)
        if 'invoices' in perms: self.nav_manager.add_navigation("invoices", "الفواتير", "fa5s.file-invoice", 7)
        if 'inventory' in perms: self.nav_manager.add_navigation("inventory", self.lang.get_text("inventory"), "fa5s.boxes", 2)
        if 'customers' in perms: self.nav_manager.add_navigation("customers", self.lang.get_text("customers"), "fa5s.users", 3)
        if 'users' in perms: self.nav_manager.add_navigation("users", self.lang.get_text("users"), "fa5s.user-shield", 4)
        if 'reports' in perms: self.nav_manager.add_navigation("reports", self.lang.get_text("reports"), "fa5s.chart-bar", 5)
        if 'settings' in perms: self.nav_manager.add_navigation("settings", self.lang.get_text("settings"), "fa5s.cog", 6)

        # Determine start page
        start_index = 0
        priority_order = ['dashboard', 'pos', 'invoices', 'inventory', 'customers', 'users', 'reports', 'settings']
        page_indices = {'dashboard':0, 'pos':1, 'inventory':2, 'customers':3, 'users':4, 'reports':5, 'settings':6, 'invoices':7}
        
        for p in priority_order:
            if p in perms:
                start_index = page_indices[p]
                break
        
        return start_index

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
        if method == "دين":
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

        if not self.active_shift:
            QMessageBox.warning(self, "تنبيه", "يجب فتح وردية أولاً للقيام بالمبيعات!")
            self.toggle_shift()
            return
            
        shift_id = self.active_shift['id']
        success, msg, sale_data = self.pos_ctrl.process_sale(method, shift_id, customer_id)
        
        if success:
            self.update_cart_ui()
            self.refresh_data()
            self.search_pos_products()
            
            # Auto-Print Logic
            if self.settings.get('auto_print', False) and sale_data:
                path = self.invoice_mgr.generate_pdf_invoice(sale_data, self.settings)
                if path:
                    self.invoice_mgr.print_invoice(path)
                    msg += "\n(تمت الطباعة تلقائياً)"
            
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
        if hasattr(self, 'invoices_page'): self.invoices_page.refresh()
        self.update_shift_ui()

    def update_shift_ui(self):
        self.active_shift = self.db.get_active_shift(self.user_data['username'])
        if self.active_shift:
            self.shift_lbl.setText("الوردية: نشطة 🟢")
            self.shift_btn.setText("إغلاق الوردية")
            self.shift_btn.setObjectName("dangerButton")
        else:
            self.shift_lbl.setText("الوردية: مغلقة 🔴")
            self.shift_btn.setText("فتح الوردية")
            self.shift_btn.setObjectName("posButton")
        self.shift_btn.style().unpolish(self.shift_btn)
        self.shift_btn.style().polish(self.shift_btn)

    def force_shift_check(self):
        if not self.active_shift:
            self.toggle_shift()

    def toggle_shift(self):
        if self.active_shift:
            # Close Shift
            report = self.db.get_shift_report(self.active_shift['id'])
            dialog = CloseShiftDialog(self.active_shift, report, self)
            if dialog.exec():
                cash, notes = dialog.get_data()
                self.db.close_shift(self.active_shift['id'], cash, notes)
                self.active_shift = None
                QMessageBox.information(self, "تم", "تم إغلاق الوردية بنجاح.")
                self.refresh_data()
        else:
            # Open Shift
            dialog = OpenShiftDialog(self)
            if dialog.exec():
                cash = dialog.get_start_cash()
                self.active_shift = self.db.open_shift(self.user_data['username'], cash)
                QMessageBox.information(self, "تم", "تم فتح وردية جديدة.")
                self.refresh_data()

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
        path = self.invoice_mgr.generate_pdf_invoice(sales[-1], self.settings)
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Dynamic Logo Resizing
        if hasattr(self, 'logo_img'):
            sidebar_w = self.sidebar.width()
            target_w = int(sidebar_w * 0.7) # Logo takes 70% of sidebar width
            logo_pix = QPixmap(resource_path("logo.png"))
            if not logo_pix.isNull():
                self.logo_img.setPixmap(logo_pix.scaled(
                    target_w, target_w, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                ))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply Global Styles to the App
    try:
        style_path = resource_path("style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding='utf-8') as f:
                app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Error loading style: {e}")

    db = DataManager()
    login = LoginDialog(db)
    if login.exec():
        window = MainWindow(login.user_data, db)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)