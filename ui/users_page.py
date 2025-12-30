from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView, QInputDialog, QMessageBox, QFrame, QFormLayout, QLineEdit, QComboBox
from PySide6.QtCore import Qt

def create_users_page(main_window):
    page = QWidget()
    page_layout = QHBoxLayout(page)
    page_layout.setContentsMargins(0, 0, 0, 0)
    page_layout.setSpacing(0)
    
    # Left Content (Table)
    table_widget = QWidget()
    table_layout = QVBoxLayout(table_widget)
    table_layout.setContentsMargins(30, 30, 30, 30)
    
    header_row = QHBoxLayout()
    header = QLabel(main_window.lang.get_text("users"))
    header.setObjectName("welcomeLabel")
    
    sub_header = QLabel("تحكم في صلاحيات الوصول وإعدادات حسابات الموظفين")
    sub_header.setStyleSheet("color: #8b949e; font-size: 14px; margin-top: -10px; margin-bottom: 20px;")
    
    add_user_btn = QPushButton(" + إضافة موظف جديد")
    add_user_btn.setObjectName("inventoryButton")
    add_user_btn.setFixedWidth(200)
    add_user_btn.clicked.connect(main_window.add_user_dialog)
    
    header_row.addWidget(header)
    header_row.addStretch()
    header_row.addWidget(add_user_btn)
    table_layout.addLayout(header_row)
    table_layout.addWidget(sub_header)
    
    main_window.users_table = QTableWidget(0, 4)
    main_window.users_table.setHorizontalHeaderLabels(["اسم المستخدم", "الاسم الكامل", "رقم الهاتف", "الدور"])
    main_window.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    main_window.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
    main_window.users_table.setSelectionBehavior(QTableWidget.SelectRows)
    main_window.users_table.setAlternatingRowColors(True)
    main_window.users_table.itemDoubleClicked.connect(main_window.open_user_drawer)
    table_layout.addWidget(main_window.users_table)
    
    page_layout.addWidget(table_widget)
    
    # Right Content (Side Drawer)
    main_window.user_drawer = QFrame()
    main_window.user_drawer.setObjectName("userDrawer")
    main_window.user_drawer.setFixedWidth(350)
    main_window.user_drawer.hide()
    
    drawer_layout = QVBoxLayout(main_window.user_drawer)
    drawer_layout.setContentsMargins(20, 20, 20, 20)
    
    drawer_title = QLabel("تعديل بيانات الموظف")
    drawer_title.setObjectName("drawerTitle")
    drawer_layout.addWidget(drawer_title)
    
    
    form = QFormLayout()
    main_window.edit_u_name = QLineEdit()
    main_window.edit_u_name.setReadOnly(True)
    main_window.edit_u_fullname = QLineEdit()
    main_window.edit_u_phone = QLineEdit()
    main_window.edit_u_role = QComboBox()
    main_window.edit_u_role.addItems(["admin", "manager", "cashier"])
    
    form.addRow("اسم المستخدم:", main_window.edit_u_name)
    form.addRow("الاسم الكامل:", main_window.edit_u_fullname)
    form.addRow("رقم الهاتف:", main_window.edit_u_phone)
    form.addRow("الدور:", main_window.edit_u_role)
    drawer_layout.addLayout(form)
    
    drawer_layout.addSpacing(20)
    save_btn = QPushButton("حفظ التغييرات")
    save_btn.setObjectName("posButton")
    save_btn.clicked.connect(main_window.save_user_drawer)
    
    cancel_btn = QPushButton("إلغاء")
    cancel_btn.clicked.connect(lambda: main_window.user_drawer.hide())
    
    drawer_layout.addWidget(save_btn)
    drawer_layout.addWidget(cancel_btn)
    drawer_layout.addStretch()
    
    page_layout.addWidget(main_window.user_drawer)
    
    main_window.refresh_users()
    return page
