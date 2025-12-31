from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
from PySide6.QtCore import Qt, QSize
import qtawesome as qta
from ui.base_page import BasePage
from components.style_engine import Colors, StyleEngine

class POSPage(BasePage):
    def __init__(self, main_window):
        title = main_window.lang.get_text("pos")
        subtitle = "نظام البيع السريع وإدارة الفواتير"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()

    def setup_ui(self):
        main_h_layout = QHBoxLayout()
        main_h_layout.setSpacing(20)
        
        # --- LEFT: Product Selection ---
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search Bar
        search_box = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث عن صنف (اسم أو كود)...")
        self.search_input.textChanged.connect(self.main_window.search_pos_products)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon("fa5s.search", color=Colors.TEXT_SECONDARY).pixmap(16, 16))
        search_box.addWidget(icon_label)
        search_box.addWidget(self.search_input)
        left_layout.addLayout(search_box)
        
        # Product Table
        self.products_table = QTableWidget(0, 3)
        self.products_table.setHorizontalHeaderLabels(["الصنف", "السعر", "المخزون"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.itemDoubleClicked.connect(self.main_window.add_to_cart)
        left_layout.addWidget(self.products_table)
        
        main_h_layout.addWidget(left_panel, 2)
        
        # --- RIGHT: Cart & Checkout ---
        right_panel = QFrame()
        right_panel.setObjectName("statsCard") # Reusing card style for cart container
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("سلة المشتريات"))
        
        self.cart_table = QTableWidget(0, 3)
        self.cart_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "الإجمالي"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.cart_table)
        
        # Totals Area
        self.total_label = QLabel("الإجمالي: 0.00 LYD")
        self.total_label.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {Colors.ACCENT}; margin-top: 10px;")
        right_layout.addWidget(self.total_label)
        
        # Actions
        btn_box = QHBoxLayout()
        self.pay_btn = QPushButton(self.main_window.lang.get_text("pos_cash"))
        self.pay_btn.setObjectName("posButton")
        self.pay_btn.clicked.connect(lambda: self.main_window.process_sale("نقداً"))
        
        self.card_btn = QPushButton(self.main_window.lang.get_text("pos_card"))
        self.card_btn.setObjectName("posButton")
        self.card_btn.clicked.connect(lambda: self.main_window.process_sale("بطاقة"))
        
        self.debt_btn = QPushButton(self.main_window.lang.get_text("pos_debt"))
        self.debt_btn.setObjectName("inventoryButton")
        self.debt_btn.clicked.connect(lambda: self.main_window.process_sale("دين"))
        
        self.clear_btn = QPushButton("إفراغ")
        self.clear_btn.setStyleSheet(f"background-color: transparent; color: {Colors.DANGER}; border: 1px solid {Colors.DANGER}; padding: 8px;")
        self.clear_btn.clicked.connect(self.main_window.clear_cart)
        
        btn_box.addWidget(self.pay_btn)
        btn_box.addWidget(self.card_btn)
        btn_box.addWidget(self.debt_btn)
        btn_box.addWidget(self.clear_btn)
        right_layout.addLayout(btn_box)
        
        main_h_layout.addWidget(right_panel, 1)
        
        self.add_layout(main_h_layout)

    def refresh(self):
        # We'll call the search method which populates the table
        pass
