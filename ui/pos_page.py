from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QTableWidget, QFrame, QLabel, QPushButton, QHeaderView, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt

def create_pos_page(main_window):
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
    
    main_window.cart_table = QTableWidget(0, 3)
    main_window.cart_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "الإجمالي"])
    main_window.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    cart_layout.addWidget(main_window.cart_table)
    
    total_frame = QFrame()
    total_frame.setObjectName("totalFrame")
    total_layout = QVBoxLayout(total_frame)
    currency = main_window.settings.get('currency', 'LYD')
    main_window.pos_total_label = QLabel(f"الإجمالي: 0.00 {currency}")
    main_window.pos_total_label.setObjectName("posTotalLabel")
    main_window.pos_total_label.setAlignment(Qt.AlignCenter)
    total_layout.addWidget(main_window.pos_total_label)
    cart_layout.addWidget(total_frame)
    
    pay_layout = QHBoxLayout()
    
    main_window.pay_cash_btn = QPushButton("كاش (نقد)")
    main_window.pay_cash_btn.setObjectName("posButton")
    main_window.pay_cash_btn.setFixedHeight(60)
    main_window.pay_cash_btn.clicked.connect(lambda: main_window.process_sale("Cash"))
    
    main_window.pay_card_btn = QPushButton("بطاقة مصرفية")
    main_window.pay_card_btn.setObjectName("inventoryButton") # Use secondary color
    main_window.pay_card_btn.setFixedHeight(60)
    main_window.pay_card_btn.clicked.connect(lambda: main_window.process_sale("Card"))

    main_window.pay_debt_btn = QPushButton("آجل (دين)")
    main_window.pay_debt_btn.setStyleSheet("background-color: #ff5252; color: white; border: none; font-weight: bold; border-radius: 12px;")
    main_window.pay_debt_btn.setFixedHeight(60)
    main_window.pay_debt_btn.clicked.connect(lambda: main_window.process_sale("Debt"))
    
    pay_layout.addWidget(main_window.pay_cash_btn)
    pay_layout.addWidget(main_window.pay_card_btn)
    pay_layout.addWidget(main_window.pay_debt_btn)
    cart_layout.addLayout(pay_layout)
    
    clear_btn = QPushButton("تفريغ السلة")
    clear_btn.setFixedHeight(40)
    clear_btn.clicked.connect(main_window.clear_cart)
    cart_layout.addWidget(clear_btn)
    
    layout.addWidget(cart_panel)
    
    products_panel = QFrame()
    products_layout = QVBoxLayout(products_panel)
    main_window.pos_search = QLineEdit()
    main_window.pos_search.setPlaceholderText("🔍  ابحث عن صنف أو امسح الباركود...")
    main_window.pos_search.setFixedHeight(55)
    main_window.pos_search.textChanged.connect(main_window.search_pos_products)
    products_layout.addWidget(main_window.pos_search)
    
    main_window.pos_products_table = QTableWidget(0, 3)
    main_window.pos_products_table.setHorizontalHeaderLabels(["الاسم", "السعر", "المتوفر"])
    main_window.pos_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    main_window.pos_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
    main_window.pos_products_table.itemDoubleClicked.connect(main_window.add_to_cart)
    products_layout.addWidget(main_window.pos_products_table)
    
    layout.addWidget(products_panel)
    main_window.cart_items = []
    return page
