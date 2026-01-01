from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QSizePolicy, QGridLayout
from PySide6.QtCore import Qt, QSize
import qtawesome as qta
from ui.base_page import BasePage
from components.style_engine import Colors, StyleEngine
from components.numpad_widget import NumpadWidget

class POSPage(BasePage):
    def __init__(self, main_window):
        title = main_window.lang.get_text("pos")
        subtitle = "نظام البيع السريع وإدارة الفواتير"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()

    def setup_ui(self):
        main_h_layout = QHBoxLayout()
        main_h_layout.setSpacing(15)
        
        # --- COLUMN 1: Product Selection (Largest) ---
        col1 = QFrame()
        col1_layout = QVBoxLayout(col1)
        col1_layout.setContentsMargins(0, 0, 0, 0)
        
        search_box = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔎 بحث عن صنف...")
        self.search_input.textChanged.connect(self.main_window.search_pos_products)
        search_box.addWidget(self.search_input)
        col1_layout.addLayout(search_box)
        
        self.products_table = QTableWidget(0, 3)
        self.products_table.setHorizontalHeaderLabels(["الصنف", "السعر", "المخزون"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.itemDoubleClicked.connect(self.main_window.add_to_cart)
        col1_layout.addWidget(self.products_table)
        
        main_h_layout.addWidget(col1, 3)
        
        # --- COLUMN 2: Cart (Middle) ---
        col2 = QFrame()
        col2.setObjectName("statsCard")
        col2_layout = QVBoxLayout(col2)
        
        cart_header = QLabel("🛒 سلة المشتريات")
        cart_header.setObjectName("sectionHeader")
        col2_layout.addWidget(cart_header)
        
        self.cart_table = QTableWidget(0, 3)
        self.cart_table.setHorizontalHeaderLabels(["الصنف", "الكمية", "الإجمالي"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        col2_layout.addWidget(self.cart_table)
        
        self.total_label = QLabel("الإجمالي: 0.00 LYD")
        self.total_label.setObjectName("totalLabel")
        self.total_label.setAlignment(Qt.AlignCenter)
        col2_layout.addWidget(self.total_label)
        
        main_h_layout.addWidget(col2, 2)
        
        # --- COLUMN 3: Payment & Numpad (Compact Right) ---
        col3 = QFrame()
        col3.setObjectName("statsCard")
        col3.setMaximumWidth(400) # Prepend extreme growth
        col3_layout = QVBoxLayout(col3)
        
        pay_header = QLabel("💳 إتمام العملية")
        pay_header.setObjectName("sectionHeader")
        col3_layout.addWidget(pay_header)
        
        # Payment Buttons (Grid)
        pay_grid = QGridLayout()
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
        self.clear_btn.setObjectName("dangerButton")
        self.clear_btn.clicked.connect(self.main_window.clear_cart)
        
        pay_grid.addWidget(self.pay_btn, 0, 0)
        pay_grid.addWidget(self.card_btn, 0, 1)
        pay_grid.addWidget(self.debt_btn, 1, 0)
        pay_grid.addWidget(self.clear_btn, 1, 1)
        col3_layout.addLayout(pay_grid)
        
        col3_layout.addSpacing(10)
        
        # Compact Numpad
        self.numpad = NumpadWidget()
        self.numpad.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.numpad.digit_pressed.connect(self._on_numpad_digit)
        self.numpad.action_pressed.connect(self._on_numpad_action)
        col3_layout.addWidget(self.numpad)
        
        main_h_layout.addWidget(col3, 2)
        
        self.add_layout(main_h_layout)

    def refresh(self):
        # We'll call the search method which populates the table
        pass

    def _on_numpad_digit(self, digit):
        # If search input has focus, type there
        if self.search_input.hasFocus():
            self.search_input.insert(digit)
        else:
            # Otherwise assume quantity or general input (can be expanded)
            self.search_input.setFocus()
            self.search_input.insert(digit)

    def _on_numpad_action(self, action):
        if action == 'clear':
            self.search_input.clear()
        elif action == 'backspace':
            self.search_input.backspace()
        elif action == 'enter':
            # Trigger search or add if only one product
            # For now, let's keep it simple: if there's a selected item in products table, add it
            items = self.products_table.selectedItems()
            if items:
                self.main_window.add_to_cart(items[0])
            else:
                self.main_window.search_pos_products()
