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
from ui.users_page import create_users_page
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
        self.setup_statusbar()
        self.setup_toolbar()
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
        self.sidebar_layout.setContentsMargins(0, 10, 0, 10)
        self.sidebar_layout.setSpacing(5)
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
        self.add_nav_button("users", "fa5s.user-shield", 5)
        self.sidebar_layout.addStretch()
        self.add_nav_button("settings", "fa5s.cog", 6)
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
        self.users_page = create_users_page(self)
        self.settings_page = create_settings_page(self)

        self.content_stack.addWidget(self.wrap_in_scroll(self.dashboard_page))
        self.content_stack.addWidget(self.wrap_in_scroll(self.pos_page))
        self.content_stack.addWidget(self.wrap_in_scroll(self.inventory_page))
        self.content_stack.addWidget(self.wrap_in_scroll(self.customers_page))
        self.content_stack.addWidget(self.wrap_in_scroll(self.reports_page))
        self.content_stack.addWidget(self.wrap_in_scroll(self.users_page))
        self.content_stack.addWidget(self.wrap_in_scroll(self.settings_page))
        
        self.set_app_direction()

    def setup_toolbar(self):
        self.toolbar = QToolBar("ERP Toolbar")
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        # Quick Actions
        self.new_sale_act = QAction(qta.icon("fa5s.plus-circle", color="#238636"), self.lang.get_text("pos"), self)
        self.new_sale_act.triggered.connect(lambda: self.switch_page(1))
        
        self.search_act = QAction(qta.icon("fa5s.search", color="#58a6ff"), self.lang.get_text("search"), self)
        
        self.backup_act = QAction(qta.icon("fa5s.database", color="#8b949e"), self.lang.get_text("quick_backup"), self)
        self.backup_act.triggered.connect(self.db_backup_quick)
        
        self.toolbar.addAction(self.new_sale_act)
        self.toolbar.addAction(self.search_act)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.backup_act)

    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # User Info
        self.status_user = QLabel(f"👤 {self.user_data['full_name']} ({self.user_data['role']})")
        self.status_user.setStyleSheet("margin-left: 20px; font-weight: bold; color: #58a6ff;")
        
        # DB Status
        self.status_db = QLabel(f"🔌 {self.lang.get_text('db_status')}: {self.lang.get_text('db_connected')}")
        self.status_db.setStyleSheet("margin-left: 20px; color: #238636;")
        
        # Time
        self.status_time = QLabel()
        self.status_time.setStyleSheet("margin-right: 20px; color: #8b949e;")
        
        self.statusbar.addWidget(self.status_user)
        self.statusbar.addWidget(self.status_db)
        self.statusbar.addPermanentWidget(self.status_time)
        
        # Timer for clock
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_status_time)
        self.clock_timer.start(1000)
        self.update_status_time()

    def update_status_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_time.setText(now)

    def db_backup_quick(self):
        filename = self.backup_mgr.create_backup()
        if filename:
            QMessageBox.information(self, "نجاح", f"تم إنشاء نسخة احتياطية سريعة:\n{filename}")

    def wrap_in_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        # Ensure scroll area transparent background if needed
        scroll.setStyleSheet("background: transparent; border: none;")
        return scroll

    def add_nav_button(self, key, icon, index):
        btn = QPushButton(self.lang.get_text(key))
        btn.setObjectName("sidebarBtn")
        btn.setIcon(qta.icon(icon, color="#8b949e"))
        btn.setIconSize(QSize(20, 20))
        btn.clicked.connect(lambda: self.switch_page(index))
        self.sidebar_layout.addWidget(btn)
        self.nav_btns[key] = btn
        return btn

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        # Update active state for buttons
        for i, btn in enumerate(self.nav_btns.values()):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    

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
            self.db.save_settings({"language": lang_code})

    def update_ui_texts(self):
        self.setWindowTitle(self.lang.get_text("app_title"))
        for key, btn in self.nav_btns.items():
            btn.setText(self.lang.get_text(key))
            
        # Toolbar & Statusbar
        if hasattr(self, 'new_sale_act'):
            self.new_sale_act.setText(self.lang.get_text("pos"))
            self.search_act.setText(self.lang.get_text("search"))
            self.backup_act.setText(self.lang.get_text("quick_backup"))
            
        if hasattr(self, 'status_db'):
            self.status_db.setText(f"🔌 {self.lang.get_text('db_status')}: {self.lang.get_text('db_connected')}")
            
        # Refresh current page texts if needed
        # (Dashboard uses main_window.lang directly so it will update on next refresh)
        # Additional logic to refresh page contents could go here

    def apply_permissions(self):
        role = self.user_data.get('role', 'cashier')
        permissions = self.user_mgr.get_role_permissions(role)
        
        if "view_reports" not in permissions:
            self.nav_btns['reports'].hide()
        if "manage_settings" not in permissions:
            self.nav_btns['settings'].hide()
        if "manage_users" not in permissions:
            self.nav_btns['users'].hide()

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
            # Automatic increment instead of prompt
            existing_item = next((i for i in self.cart_items if i['product_id'] == product_id), None)
            if existing_item:
                if existing_item['quantity'] < product['stock']:
                    existing_item['quantity'] += 1
                    existing_item['total'] = existing_item['quantity'] * existing_item['price']
                else:
                    QMessageBox.warning(self, "خطأ", "تم الوصول للحد الأقصى للمخزون")
            else:
                self.cart_items.append({
                    "product_id": product_id,
                    "name": product['name'],
                    "quantity": 1,
                    "price": product['price'],
                    "total": product['price']
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
        self.refresh_customers()
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

        # Refresh Charts (Last 7 Days)
        self.refresh_weekly_chart()
        self.refresh_stock_alerts()

    def refresh_weekly_chart(self):
        # Clear existing bars
        while self.bars_container.count():
            item = self.bars_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        sales = self.db.get_sales()
        days_data = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            days_data[date] = 0
            
        for s in sales:
            date_str = s['timestamp'][:10]
            if date_str in days_data:
                days_data[date_str] += s['total_amount']
        
        max_val = max(days_data.values()) if any(days_data.values()) else 100
        
        for date in sorted(days_data.keys()):
            val = days_data[date]
            height = int((val / max_val) * 150) if val > 0 else 5
            
            bar_frame = QVBoxLayout()
            bar = QFrame()
            bar.setFixedWidth(30)
            bar.setFixedHeight(height)
            bar.setStyleSheet(f"background-color: {'#58a6ff' if date != datetime.now().strftime('%Y-%m-%d') else '#238636'}; border-radius: 4px;")
            
            label_val = QLabel(f"{val:.0f}")
            label_val.setStyleSheet("font-size: 10px; color: #8b949e;")
            label_val.setAlignment(Qt.AlignCenter)
            
            label_day = QLabel(date[8:])
            label_day.setStyleSheet("font-size: 10px; color: #8b949e;")
            label_day.setAlignment(Qt.AlignCenter)
            
            bar_frame.addWidget(label_val)
            bar_frame.addWidget(bar)
            bar_frame.addWidget(label_day)
            self.bars_container.addLayout(bar_frame)

    def refresh_stock_alerts(self):
        # Clear alerts
        while self.alerts_list.count():
            item = self.alerts_list.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        products = self.db.get_products()
        low_stock = [p for p in products if p['stock'] <= 5]
        
        if not low_stock:
            lbl = QLabel("جميع الأصناف متوفرة")
            lbl.setStyleSheet("color: #238636; font-style: italic;")
            self.alerts_list.addWidget(lbl)
        else:
            for p in low_stock[:5]:
                lbl = QLabel(f"⚠️ {p['name']}: {p['stock']} علبة")
                lbl.setStyleSheet("color: #ff5252; padding: 5px;")
                self.alerts_list.addWidget(lbl)

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

    def refresh_users(self):
        users = self.db.get_users()
        self.users_table.setRowCount(0)
        for u in users:
            row = self.users_table.rowCount()
            self.users_table.insertRow(row)
            self.users_table.setItem(row, 0, QTableWidgetItem(u['username']))
            self.users_table.setItem(row, 1, QTableWidgetItem(u.get('full_name', '-')))
            self.users_table.setItem(row, 2, QTableWidgetItem(u.get('phone', '-')))
            self.users_table.setItem(row, 3, QTableWidgetItem(u.get('role', 'cashier')))

    def add_user_dialog(self):
        user, ok = QInputDialog.getText(self, "موظف جديد", "اسم المستخدم:")
        if ok and user:
            pwd, ok2 = QInputDialog.getText(self, "موظف جديد", "كلمة المرور:")
            if ok2:
                fullname, ok3 = QInputDialog.getText(self, "موظف جديد", "الاسم الكامل:")
                if ok3:
                    phone, ok4 = QInputDialog.getText(self, "موظف جديد", "رقم الهاتف:")
                    if ok4:
                        roles = ["admin", "manager", "cashier"]
                        role, ok5 = QInputDialog.getItem(self, "موظف جديد", "الدور:", roles, 2, False)
                        if ok5:
                            self.db.add_user({"username": user, "password": pwd, "full_name": fullname, "phone": phone, "role": role})
                            self.refresh_users()

    def open_user_drawer(self, item):
        row = item.row()
        username = self.users_table.item(row, 0).text()
        user = next((u for u in self.db.get_users() if u['username'] == username), None)
        
        if user:
            self.edit_u_name.setText(user['username'])
            self.edit_u_fullname.setText(user.get('full_name', ''))
            self.edit_u_phone.setText(user.get('phone', ''))
            self.edit_u_role.setCurrentText(user.get('role', 'cashier'))
            self.user_drawer.show()

    def save_user_drawer(self):
        username = self.edit_u_name.text()
        if username == "admin":
            QMessageBox.warning(self, "خطأ", "لا يمكن تعديل المدير العام")
            self.user_drawer.hide()
            return

        fullname = self.edit_u_fullname.text()
        phone = self.edit_u_phone.text()
        role = self.edit_u_role.currentText()
        
        users = self.db.get_users()
        for u in users:
            if u['username'] == username:
                u['full_name'] = fullname
                u['phone'] = phone
                u['role'] = role
                break
        
        self.db._save_json(self.db.users_file, users)
        self.refresh_users()
        self.user_drawer.hide()
        QMessageBox.information(self, "تم", "تم تحديث بيانات الموظف")

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