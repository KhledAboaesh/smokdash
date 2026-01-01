from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from ui.base_page import BasePage
from components.stats_card import StatsCard
from components.style_engine import Colors

class DashboardPage(BasePage):
    def __init__(self, main_window):
        title = main_window.lang.get_text("dashboard")
        subtitle = "نظرة عامة على أداء المنظومة اليوم"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()
        
    def setup_ui(self):
        # Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        currency = self.main_window.settings.get('currency', 'LYD')
        
        self.card_sales = StatsCard(self.main_window.lang.get_text("sales_amount"), f"0.00 {currency}", "fa5s.chart-line", Colors.SUCCESS)
        self.card_transactions = StatsCard(self.main_window.lang.get_text("transaction_count"), "0", "fa5s.receipt", Colors.ACCENT)
        self.card_stock = StatsCard(self.main_window.lang.get_text("inventory_value"), "0", "fa5s.boxes", Colors.DANGER)
        
        stats_layout.addWidget(self.card_sales)
        stats_layout.addWidget(self.card_transactions)
        stats_layout.addWidget(self.card_stock)
        self.add_layout(stats_layout)
        
        # Middle Section (Recent Sales & Alerts)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Recent Sales
        recent_panel = QFrame()
        recent_panel.setObjectName("statsCard")
        rl = QVBoxLayout(recent_panel)
        rl.setContentsMargins(20, 20, 20, 20)
        
        rh = QLabel(self.main_window.lang.get_text("recent_sales"))
        rh.setObjectName("sectionHeader")
        rl.addWidget(rh)
        
        self.recent_table = QTableWidget(0, 3)
        self.recent_table.setHorizontalHeaderLabels([
            self.main_window.lang.get_text("time"),
            self.main_window.lang.get_text("total"),
            self.main_window.lang.get_text("payment_method")
        ])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setFixedHeight(250)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        rl.addWidget(self.recent_table)
        
        # Stock Alerts
        alerts_panel = QFrame()
        alerts_panel.setObjectName("statsCard")
        al = QVBoxLayout(alerts_panel)
        al.setContentsMargins(20, 20, 20, 20)
        
        ah = QLabel(self.main_window.lang.get_text("stock_alerts"))
        ah.setObjectName("sectionHeader")
        al.addWidget(ah)
        
        self.alerts_table = QTableWidget(0, 2)
        self.alerts_table.setHorizontalHeaderLabels([
            self.main_window.lang.get_text("item"),
            self.main_window.lang.get_text("remaining_stock")
        ])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.setFixedHeight(250)
        self.alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        al.addWidget(self.alerts_table)
        
        content_layout.addWidget(recent_panel, 2)
        content_layout.addWidget(alerts_panel, 1)
        
        self.add_layout(content_layout)
        self.layout.addStretch()

    def refresh(self):
        # Update Stats Cards
        sales = self.main_window.db.get_todays_sales()
        total_sales = sum(s['total_amount'] for s in sales)
        count = len(sales)
        products = self.main_window.db.get_products()
        total_stock = sum(p['stock'] for p in products)
        
        currency = self.main_window.settings.get('currency', 'LYD')
        self.card_sales.update_value(f"{total_sales:.2f} {currency}")
        self.card_transactions.update_value(str(count))
        self.card_stock.update_value(str(total_stock))
        
        # Update Recent Sales Table
        self.recent_table.setRowCount(0)
        for s in list(reversed(sales))[:5]:
            row = self.recent_table.rowCount()
            self.recent_table.insertRow(row)
            self.recent_table.setItem(row, 0, QTableWidgetItem(s['timestamp'].split('T')[1].split('.')[0]))
            self.recent_table.setItem(row, 1, QTableWidgetItem(f"{s['total_amount']:.2f}"))
            self.recent_table.setItem(row, 2, QTableWidgetItem(s['payment_method']))
            
        # Update Alerts Table
        low_stock = [p for p in products if p['stock'] <= p.get('min_stock', 10)]
        self.alerts_table.setRowCount(0)
        for p in low_stock[:10]:
            row = self.alerts_table.rowCount()
            self.alerts_table.insertRow(row)
            self.alerts_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.alerts_table.setItem(row, 1, QTableWidgetItem(str(p['stock'])))
            min_val = p.get('min_stock', 10)
            color_hex = Colors.DANGER if p['stock'] <= (min_val // 2) else Colors.TEXT_PRIMARY
            self.alerts_table.item(row, 1).setForeground(QBrush(QColor(color_hex)))
