from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView

def create_inventory_page(main_window):
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
    add_btn.clicked.connect(main_window.add_product_dialog)
    header_row.addWidget(header)
    header_row.addStretch()
    header_row.addWidget(add_btn)
    layout.addLayout(header_row)
    
    main_window.inventory_table = QTableWidget(0, 5)
    main_window.inventory_table.setHorizontalHeaderLabels(["ID", "اسم الصنف", "الماركة", "السعر", "الكمية"])
    main_window.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    main_window.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
    main_window.inventory_table.itemDoubleClicked.connect(main_window.edit_product_dialog)
    layout.addWidget(main_window.inventory_table)
    return page
