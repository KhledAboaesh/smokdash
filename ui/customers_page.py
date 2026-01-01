from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QHeaderView, QTableWidgetItem
import qtawesome as qta
from ui.base_page import BasePage
from components.style_engine import Colors

class CustomersPage(BasePage):
    def __init__(self, main_window):
        title = main_window.lang.get_text("customers")
        subtitle = "إدارة علاقات العملاء، الديون، والمستحقات"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()

    def setup_ui(self):
        # Actions Row
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        self.add_btn = QPushButton(" إضافة عميل جديد")
        self.add_btn.setIcon(qta.icon("fa5s.user-plus", color="#062C21"))
        self.add_btn.setObjectName("inventoryButton")
        self.add_btn.setFixedWidth(180)
        self.add_btn.clicked.connect(self.main_window.add_customer_dialog)
        
        self.debt_btn = QPushButton(" تحصيل دين")
        self.debt_btn.setIcon(qta.icon("fa5s.money-bill-wave", color="#062C21"))
        self.debt_btn.setObjectName("posButton") 
        self.debt_btn.setFixedWidth(180)
        self.debt_btn.clicked.connect(self.main_window.collect_debt_dialog)
        
        actions_layout.addStretch()
        actions_layout.addWidget(self.debt_btn)
        actions_layout.addWidget(self.add_btn)
        self.add_layout(actions_layout)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["الاسم", "رقم الهاتف", "الدين الحالي", "تاريخ الانضمام"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.add_widget(self.table)

    def refresh(self):
        customers = self.main_window.db.get_customers()
        self.table.setRowCount(0)
        for c in customers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(c['name']))
            self.table.setItem(row, 1, QTableWidgetItem(c['phone']))
            self.table.setItem(row, 2, QTableWidgetItem(f"{c['debt']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(c['created_at'][:10]))
