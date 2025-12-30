from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QDateEdit, QSpinBox, QComboBox, QFrame, QTableWidgetItem)
from PySide6.QtCore import QDate, Qt
from components.style_engine import Colors, StyleEngine

class AdvancedReportsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("التقارير المتقدمة والتحليلات")
        self.setMinimumSize(1000, 750)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header Area
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {Colors.SIDEBAR}; border-bottom: 1px solid {Colors.BORDER};")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        title_lbl = QLabel("تحليلات الأداء والتقارير")
        title_lbl.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {Colors.ACCENT};")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: transparent; font-size: 24px; color: #8b949e;")
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        main_layout.addWidget(header_frame)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background-color: {Colors.BACKGROUND}; }}
            QTabBar::tab {{
                background: transparent;
                color: #8b949e;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                color: {Colors.ACCENT};
                border-bottom: 2px solid {Colors.ACCENT};
            }}
        """)
        
        self.daily_tab = self.create_daily_sales_tab()
        self.top_products_tab = self.create_top_products_tab()
        
        self.tabs.addTab(self.daily_tab, "المبيعات اليومية")
        self.tabs.addTab(self.top_products_tab, "الأصناف الأكثر طلباً")
        
        main_layout.addWidget(self.tabs)
        
        # Actions Footer
        footer = QFrame()
        footer.setStyleSheet(f"background-color: {Colors.SIDEBAR}; border-top: 1px solid {Colors.BORDER};")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        
        export_btn = QPushButton("تصدير إلى Excel")
        export_btn.setObjectName("posButton")
        export_btn.setFixedHeight(40)
        
        footer_layout.addWidget(export_btn)
        footer_layout.addStretch()
        main_layout.addWidget(footer)

    def create_daily_sales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Filter Bar
        filters = QFrame()
        filters.setObjectName("statsCard")
        fl = QHBoxLayout(filters)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        
        refresh_btn = QPushButton("تطبيق الفلتر")
        refresh_btn.setObjectName("inventoryButton")
        refresh_btn.clicked.connect(self.refresh_daily_sales)
        
        fl.addWidget(QLabel("من:"))
        fl.addWidget(self.start_date)
        fl.addWidget(QLabel("إلى:"))
        fl.addWidget(self.end_date)
        fl.addStretch()
        fl.addWidget(refresh_btn)
        
        layout.addWidget(filters)
        
        # Content Split (Table + Placeholder for chart)
        content = QHBoxLayout()
        self.daily_table = QTableWidget(0, 3)
        self.daily_table.setHorizontalHeaderLabels(["التاريخ", "العمليات", "الإجمالي"])
        content.addWidget(self.daily_table, 1)
        
        chart_mock = QFrame()
        chart_mock.setObjectName("statsCard")
        chart_mock.setStyleSheet("background-color: rgba(88, 166, 255, 0.05);")
        chart_mock_layout = QVBoxLayout(chart_mock)
        chart_mock_layout.addWidget(QLabel("مساحة الرسم البياني للمبيعات"), 0, Qt.AlignCenter)
        content.addWidget(chart_mock, 1)
        
        layout.addLayout(content)
        self.refresh_daily_sales()
        return tab

    def create_top_products_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)
        
        self.top_table = QTableWidget(0, 4)
        self.top_table.setHorizontalHeaderLabels(["الصنف", "الكمية المباعة", "الإيرادات", "النسبة"])
        layout.addWidget(self.top_table)
        
        self.refresh_top_products()
        return tab

    def refresh_daily_sales(self):
        # Implementation of data aggregation logic
        sales = self.db.get_sales_by_date_range(self.start_date.date().toPython(), self.end_date.date().toPython())
        stats = {}
        for s in sales:
            d = s['timestamp'].split('T')[0]
            if d not in stats: stats[d] = {'count': 0, 'total': 0.0}
            stats[d]['count'] += 1
            stats[d]['total'] += s['total_amount']
            
        self.daily_table.setRowCount(0)
        for d, data in sorted(stats.items(), reverse=True):
            row = self.daily_table.rowCount()
            self.daily_table.insertRow(row)
            self.daily_table.setItem(row, 0, QTableWidgetItem(d))
            self.daily_table.setItem(row, 1, QTableWidgetItem(str(data['count'])))
            self.daily_table.setItem(row, 2, QTableWidgetItem(f"{data['total']:.2f}"))

    def refresh_top_products(self):
        sales = self.db.get_sales()
        prod_stats = {}
        for s in sales:
            for item in s['items']:
                pid = item['product_id']
                if pid not in prod_stats: prod_stats[pid] = {'name': item['name'], 'qty': 0, 'rev': 0.0}
                prod_stats[pid]['qty'] += item['quantity']
                prod_stats[pid]['rev'] += item['total']
        
        sorted_stats = sorted(prod_stats.values(), key=lambda x: x['rev'], reverse=True)
        total_rev = sum(p['rev'] for p in sorted_stats)
        
        self.top_table.setRowCount(0)
        for p in sorted_stats[:20]:
            row = self.top_table.rowCount()
            self.top_table.insertRow(row)
            self.top_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.top_table.setItem(row, 1, QTableWidgetItem(str(p['qty'])))
            self.top_table.setItem(row, 2, QTableWidgetItem(f"{p['rev']:.2f}"))
            perc = (p['rev'] / total_rev * 100) if total_rev > 0 else 0
            self.top_table.setItem(row, 3, QTableWidgetItem(f"{perc:.1f}%"))
