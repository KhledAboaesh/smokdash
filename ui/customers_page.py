from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView
from PySide6.QtCore import Qt

def create_customers_page(main_window):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(30, 30, 30, 30)
    
    header_row = QHBoxLayout()
    header = QLabel("إدارة العملاء والديون")
    header.setObjectName("welcomeLabel")
    
    add_cust_btn = QPushButton(" + إضافة عميل جديد")
    add_cust_btn.setObjectName("inventoryButton")
    add_cust_btn.setFixedWidth(200)
    add_cust_btn.clicked.connect(main_window.add_customer_dialog)
    
    collect_btn = QPushButton("تحصيل مبلغ")
    collect_btn.setObjectName("posButton")
    collect_btn.setFixedWidth(150)
    collect_btn.clicked.connect(main_window.collect_debt_dialog)
    
    header_row.addWidget(header)
    header_row.addStretch()
    header_row.addWidget(collect_btn)
    header_row.addWidget(add_cust_btn)
    layout.addLayout(header_row)
    
    main_window.customers_table = QTableWidget(0, 4)
    main_window.customers_table.setHorizontalHeaderLabels(["الاسم", "رقم الهاتف", "إجمالي الدين", "تاريخ الانضمام"])
    main_window.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    layout.addWidget(main_window.customers_table)
    
    main_window.refresh_customers()
    return page
