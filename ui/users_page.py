from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView, QTableWidgetItem, QFrame, QFormLayout, QLineEdit, QComboBox
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from components.style_engine import Colors

class UserPermissionsPage(BasePage):
    def __init__(self, main_window):
        title = main_window.lang.get_text("users")
        subtitle = "إدارة صلاحيات الوصول وحسابات الموظفين"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()

    def setup_ui(self):
        main_h_layout = QHBoxLayout()
        main_h_layout.setSpacing(20)
        
        # Left: Users Table
        table_panel = QFrame()
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        actions_layout = QHBoxLayout()
        self.add_btn = QPushButton(" + إضافة موظف")
        self.add_btn.setObjectName("inventoryButton")
        self.add_btn.setFixedWidth(180)
        self.add_btn.clicked.connect(self.main_window.add_user_dialog)
        actions_layout.addStretch()
        actions_layout.addWidget(self.add_btn)
        table_layout.addLayout(actions_layout)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["اسم المستخدم", "الاسم الكامل", "الهاتف", "الدور"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(self.main_window.open_user_drawer)
        table_layout.addWidget(self.table)
        
        main_h_layout.addWidget(table_panel, 2)
        
        # Right: Side Drawer (Properties)
        self.drawer = QFrame()
        self.drawer.setObjectName("statsCard")
        self.drawer.setFixedWidth(320)
        self.drawer.hide()
        
        drawer_layout = QVBoxLayout(self.drawer)
        drawer_layout.setContentsMargins(20, 20, 20, 20)
        drawer_layout.setSpacing(15)
        
        drawer_title = QLabel("تعديل البيانات")
        drawer_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Colors.ACCENT}; margin-bottom: 10px;")
        drawer_layout.addWidget(drawer_title)
        
        self.form = QFormLayout()
        self.form.setSpacing(12)
        self.edit_name = QLineEdit()
        self.edit_name.setReadOnly(True)
        self.edit_fullname = QLineEdit()
        self.edit_phone = QLineEdit()
        self.edit_role = QComboBox()
        self.edit_role.addItems(["admin", "manager", "cashier"])
        
        self.form.addRow("اسم المستخدم:", self.edit_name)
        self.form.addRow("الاسم الكامل:", self.edit_fullname)
        self.form.addRow("رقم الهاتف:", self.edit_phone)
        self.form.addRow("الدور:", self.edit_role)
        drawer_layout.addLayout(self.form)
        
        save_btn = QPushButton("حفظ التغييرات")
        save_btn.setObjectName("posButton")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self.main_window.save_user_drawer)
        drawer_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.drawer.hide)
        drawer_layout.addWidget(cancel_btn)
        drawer_layout.addStretch()
        
        main_h_layout.addWidget(self.drawer)
        self.add_layout(main_h_layout)

    def refresh(self):
        users = self.main_window.db.get_users()
        self.table.setRowCount(0)
        for u in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(u['username']))
            self.table.setItem(row, 1, QTableWidgetItem(u.get('full_name', '-')))
            self.table.setItem(row, 2, QTableWidgetItem(u.get('phone', '-')))
            self.table.setItem(row, 3, QTableWidgetItem(u.get('role', 'cashier')))
