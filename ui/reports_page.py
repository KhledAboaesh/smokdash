from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
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
        # Top Section: Financial Summary
        summary_panel = QFrame()
        summary_panel.setObjectName("statsCard")
        sl = QHBoxLayout(summary_panel)
        sl.setContentsMargins(30, 30, 30, 30)
        
        self.total_revenue_lbl = QLabel(f"{self.main_window.lang.get_text('total_revenue')}: 0.00 LYD")
        self.total_debt_lbl = QLabel(f"{self.main_window.lang.get_text('total_debt')}: 0.00 LYD")
        
        for lbl in [self.total_revenue_lbl, self.total_debt_lbl]:
            lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Colors.TEXT_PRIMARY};")
            sl.addWidget(lbl)
            sl.addStretch()
            
        self.add_widget(summary_panel)
        
        # Middle Section: Quick Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(20)
        
        # Invoicing Group
        invoice_group = QFrame()
        invoice_group.setObjectName("statsCard")
        invoice_layout = QVBoxLayout(invoice_group)
        invoice_layout.setContentsMargins(25, 25, 25, 25)
        
        invoice_header = QLabel(self.main_window.lang.get_text("reports") + " - " + self.main_window.lang.get_text("pos"))
        invoice_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        
        self.gen_invoice_btn = QPushButton("إصدار فاتورة لآخر عملية بيع (PDF)")
        self.gen_invoice_btn.setObjectName("posButton")
        self.gen_invoice_btn.setFixedHeight(45)
        self.gen_invoice_btn.clicked.connect(self.main_window.generate_last_invoice_pdf)
        
        invoice_layout.addWidget(invoice_header)
        invoice_layout.addWidget(self.gen_invoice_btn)
        actions_layout.addWidget(invoice_group, 1)
        
        # Advanced Reports Group
        adv_reports_group = QFrame()
        adv_reports_group.setObjectName("statsCard")
        adv_reports_layout = QVBoxLayout(adv_reports_group)
        adv_reports_layout.setContentsMargins(25, 25, 25, 25)
        
        adv_header = QLabel(self.main_window.lang.get_text("financial_summary"))
        adv_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        
        self.show_adv_btn = QPushButton("عرض التقارير والرسوم البيانية المحسنة")
        self.show_adv_btn.setObjectName("inventoryButton")
        self.show_adv_btn.setFixedHeight(45)
        self.show_adv_btn.clicked.connect(self.main_window.show_advanced_reports)
        
        adv_reports_layout.addWidget(adv_header)
        adv_reports_layout.addWidget(self.show_adv_btn)
        actions_layout.addWidget(adv_reports_group, 1)
        
        self.add_layout(actions_layout)
        
        # Bottom Section: Top Products Summary (Compact)
        self.top_summary_table = QTableWidget(0, 2)
        self.top_summary_table.setHorizontalHeaderLabels([
            self.main_window.lang.get_text("top_selling"),
            self.main_window.lang.get_text("revenue")
        ])
        self.top_summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_summary_table.setFixedHeight(200)
        self.top_summary_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.add_widget(self.top_summary_table)
        self.layout.addStretch()

    def refresh(self):
        sales = self.main_window.db.get_sales()
        total_rev = sum(s['total_amount'] for s in sales)
        
        customers = self.main_window.db.get_customers()
        total_debt = sum(c['debt'] for c in customers)
        
        currency = self.main_window.settings.get('currency', 'LYD')
        
        self.total_revenue_lbl.setText(f"{self.main_window.lang.get_text('total_revenue')}: {total_rev:.2f} {currency}")
        self.total_debt_lbl.setText(f"{self.main_window.lang.get_text('total_debt')}: {total_debt:.2f} {currency}")
        
        # Top 5 products
        prod_stats = {}
        for s in sales:
            for item in s['items']:
                pid = item['product_id']
                if pid not in prod_stats: prod_stats[pid] = {'name': item['name'], 'rev': 0.0}
                prod_stats[pid]['rev'] += item['total']
        
        sorted_stats = sorted(prod_stats.values(), key=lambda x: x['rev'], reverse=True)
        self.top_summary_table.setRowCount(0)
        for p in sorted_stats[:5]:
            row = self.top_summary_table.rowCount()
            self.top_summary_table.insertRow(row)
            self.top_summary_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.top_summary_table.setItem(row, 1, QTableWidgetItem(f"{p['rev']:.2f}"))
