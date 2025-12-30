from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from components.style_engine import Colors

class ReportsPage(BasePage):
    def __init__(self, main_window):
        title = main_window.lang.get_text("reports")
        subtitle = "تقارير المبيعات، الفواتير، والتحليلات المتقدمة"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()

    def setup_ui(self):
        # Invoicing Group
        invoice_group = QFrame()
        invoice_group.setObjectName("statsCard")
        invoice_layout = QVBoxLayout(invoice_group)
        invoice_layout.setContentsMargins(20, 20, 20, 20)
        
        invoice_header = QLabel("إدارة الفواتير")
        invoice_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        
        self.gen_invoice_btn = QPushButton("إصدار فاتورة لآخر عملية بيع (PDF)")
        self.gen_invoice_btn.setObjectName("posButton")
        self.gen_invoice_btn.setFixedHeight(45)
        self.gen_invoice_btn.clicked.connect(self.main_window.generate_last_invoice_pdf)
        
        invoice_layout.addWidget(invoice_header)
        invoice_layout.addWidget(self.gen_invoice_btn)
        self.add_widget(invoice_group)
        
        # Advanced Reports Group
        adv_reports_group = QFrame()
        adv_reports_group.setObjectName("statsCard")
        adv_reports_layout = QVBoxLayout(adv_reports_group)
        adv_reports_layout.setContentsMargins(20, 20, 20, 20)
        
        adv_header = QLabel("التحليلات المتقدمة")
        adv_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        
        self.show_adv_btn = QPushButton("عرض التقارير والرسوم البيانية المحسنة")
        self.show_adv_btn.setObjectName("inventoryButton")
        self.show_adv_btn.setFixedHeight(45)
        self.show_adv_btn.clicked.connect(self.main_window.show_advanced_reports)
        
        adv_reports_layout.addWidget(adv_header)
        adv_reports_layout.addWidget(self.show_adv_btn)
        self.add_widget(adv_reports_group)
        
        self.layout.addStretch()

    def refresh(self):
        pass
