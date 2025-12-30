from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from components.stats_card import StatsCard
from components.style_engine import Colors

class DashboardPage(BasePage):
    def __init__(self, main_window):
        # Localize title/subtitle
        title = main_window.lang.get_text("dashboard")
        subtitle = "نظرة عامة على أداء المنظومة اليوم"
        super().__init__(main_window, title, subtitle)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        currency = self.main_window.settings.get('currency', 'LYD')
        
        self.card_sales = StatsCard("مبيعات اليوم", f"0.00 {currency}", "fa5s.chart-line", Colors.SUCCESS)
        self.card_transactions = StatsCard("عدد العمليات", "0", "fa5s.receipt", Colors.ACCENT)
        self.card_stock = StatsCard("إجمالي المخزون", "0", "fa5s.boxes", Colors.DANGER)
        
        stats_layout.addWidget(self.card_sales)
        stats_layout.addWidget(self.card_transactions)
        stats_layout.addWidget(self.card_stock)
        
        self.add_layout(stats_layout)
        
        # Bottom Content (Charts & Recent Sales - Placeholder for now)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Recent Sales Placeholder
        recent_frame = QFrame()
        recent_frame.setObjectName("statsCard")
        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.addWidget(QLabel("آخر العمليات"))
        recent_layout.addStretch()
        
        # Inventory Alerts Placeholder
        alerts_frame = QFrame()
        alerts_frame.setObjectName("statsCard")
        alerts_layout = QVBoxLayout(alerts_frame)
        alerts_layout.addWidget(QLabel("تنبيهات النواقص"))
        alerts_layout.addStretch()
        
        bottom_layout.addWidget(recent_frame, 2)
        bottom_layout.addWidget(alerts_frame, 1)
        
        self.add_layout(bottom_layout)
        self.layout.addStretch()

    def refresh(self):
        # Logic to update values from DB
        sales = self.main_window.db.get_todays_sales()
        total_sales = sum(s['total_amount'] for s in sales)
        count = len(sales)
        products = self.main_window.db.get_products()
        total_stock = sum(p['stock'] for p in products)
        
        currency = self.main_window.settings.get('currency', 'LYD')
        self.card_sales.update_value(f"{total_sales:.2f} {currency}")
        self.card_transactions.update_value(str(count))
        self.card_stock.update_value(str(total_stock))
