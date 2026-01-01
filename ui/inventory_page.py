from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView, QTableWidgetItem
import qtawesome as qta
from ui.base_page import BasePage
from components.style_engine import Colors

class InventoryPage(BasePage):
    def __init__(self, main_window):
        title = main_window.lang.get_text("inventory")
        subtitle = "إدارة المنتجات، المخزون، والأسعار"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()

    def setup_ui(self):
        # Actions Row
        actions_layout = QHBoxLayout()
        self.add_btn = QPushButton(" + إضافة صنف جديد")
        self.add_btn.setIcon(qta.icon("fa5s.plus-circle", color="#062C21"))
        self.add_btn.setObjectName("inventoryButton")
        self.add_btn.setFixedWidth(200)
        self.add_btn.clicked.connect(self.main_window.add_product_dialog)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.add_btn)
        self.add_layout(actions_layout)
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "اسم الصنف", "الماركة", "السعر", "الكمية"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(self.main_window.edit_product_dialog)
        self.add_widget(self.table)

    def refresh(self):
        products = self.main_window.db.get_products()
        self.table.setRowCount(0)
        for p in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(p['id']))
            self.table.setItem(row, 1, QTableWidgetItem(p['name']))
            self.table.setItem(row, 2, QTableWidgetItem(p.get('brand', '-')))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p['price']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(p['stock'])))
