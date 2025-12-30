from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QDateEdit, QSpinBox, QComboBox)
from PySide6.QtCore import QDate

class AdvancedReportsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("تقارير متقدمة")
        self.setMinimumSize(900, 700)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # تبويبات للتقارير المختلفة
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # تقرير المبيعات اليومية
        self.daily_sales_tab = self.create_daily_sales_tab()
        self.tabs.addTab(self.daily_sales_tab, "المبيعات اليومية")
        self.refresh_daily_sales() # Add this
        
        # تقرير المنتجات الأكثر مبيعاً
        self.top_products_tab = self.create_top_products_tab()
        self.tabs.addTab(self.top_products_tab, "المنتجات الأكثر مبيعاً")
        self.refresh_top_products() # Add this
        
        # تقرير طرق الدفع
        self.payment_methods_tab = self.create_payment_methods_tab()
        self.tabs.addTab(self.payment_methods_tab, "طرق الدفع")
        
        layout.addWidget(self.tabs)
        
        # أزرار التحكم
        btn_layout = QHBoxLayout()
        export_btn = QPushButton("تصدير التقرير")
        export_btn.setObjectName("posButton")
        export_btn.clicked.connect(self.export_report)
        
        print_btn = QPushButton("طباعة")
        print_btn.clicked.connect(self.print_report)
        
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(print_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def create_daily_sales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # اختيار نطاق تاريخي
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("من:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("إلى:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_daily_sales)
        date_layout.addWidget(refresh_btn)
        
        layout.addLayout(date_layout)
        
        # جدول المبيعات اليومية
        self.daily_sales_table = QTableWidget()
        self.daily_sales_table.setColumnCount(3)
        self.daily_sales_table.setHorizontalHeaderLabels(["التاريخ", "عدد العمليات", "إجمالي المبيعات"])
        layout.addWidget(self.daily_sales_table)
        
        # مخطط بياني
        self.chart_widget = QWidget()
        layout.addWidget(self.chart_widget)
        
        return tab
    
    def refresh_daily_sales(self):
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()
        
        # جلب البيانات من قاعدة البيانات
        sales = self.db.get_sales_by_date_range(start_date, end_date)
        
        # معالجة البيانات وعرضها
        daily_stats = {}
        for sale in sales:
            sale_date = QDate.fromString(sale['timestamp'].split('T')[0], "yyyy-MM-dd") # Assuming timestamp is ISO format
            if sale_date not in daily_stats:
                daily_stats[sale_date] = {'count': 0, 'total': 0.0}
            daily_stats[sale_date]['count'] += 1
            daily_stats[sale_date]['total'] += sale['total_amount']

        self.daily_sales_table.setRowCount(len(daily_stats))
        row = 0
        for date, stats in sorted(daily_stats.items(), key=lambda x: x[0]):
            self.daily_sales_table.setItem(row, 0, QTableWidgetItem(date.toString("yyyy-MM-dd")))
            self.daily_sales_table.setItem(row, 1, QTableWidgetItem(str(stats['count'])))
            self.daily_sales_table.setItem(row, 2, QTableWidgetItem(f"{stats['total']:.2f}"))
            row += 1
        
        # تحديث الجدول
        self.daily_sales_table.setRowCount(0)
        
        # تحديث المخطط
        self.update_chart(sales)
    
    def update_chart(self, sales_data):
        """تحديث المخطط البياني"""
        # تنفيذ عرض مخطط بياني باستخدام QtCharts أو مكتبة خارجية
        pass
    
    def create_top_products_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # إعدادات التقرير
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("عدد المنتجات:"))
        self.top_count = QSpinBox()
        self.top_count.setRange(5, 50)
        self.top_count.setValue(10)
        settings_layout.addWidget(self.top_count)
        
        settings_layout.addWidget(QLabel("الفترة:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["أسبوع", "شهر", "ربع سنة", "سنة"])
        settings_layout.addWidget(self.period_combo)
        
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_top_products)
        settings_layout.addWidget(refresh_btn)
        
        layout.addLayout(settings_layout)
        
        # جدول المنتجات الأكثر مبيعاً
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels(["المنتج", "الكمية المباعة", "الإيرادات", "النسبة"])
        layout.addWidget(self.top_products_table)
        
        return tab
    
    def refresh_top_products(self):
        top_count = self.top_count.value()
        period = self.period_combo.currentText() # Will use this later for filtering

        sales = self.db.get_sales()
        product_stats = {}

        for sale in sales:
            for item in sale['items']:
                product_id = item['product_id']
                product_name = item['name']
                quantity = item['quantity']
                price = item['price']
                
                if product_id not in product_stats:
                    product_stats[product_id] = {'name': product_name, 'quantity_sold': 0, 'revenue': 0.0}
                
                product_stats[product_id]['quantity_sold'] += quantity
                product_stats[product_id]['revenue'] += quantity * price
        
        # Sort by revenue for "top products"
        sorted_products = sorted(product_stats.values(), key=lambda x: x['revenue'], reverse=True)
        
        self.top_products_table.setRowCount(min(top_count, len(sorted_products)))
        
        total_revenue_all_products = sum(p['revenue'] for p in sorted_products)

        row = 0
        for product in sorted_products[:top_count]:
            self.top_products_table.setItem(row, 0, QTableWidgetItem(product['name']))
            self.top_products_table.setItem(row, 1, QTableWidgetItem(str(product['quantity_sold'])))
            self.top_products_table.setItem(row, 2, QTableWidgetItem(f"{product['revenue']:.2f}"))
            
            percentage = (product['revenue'] / total_revenue_all_products * 100) if total_revenue_all_products > 0 else 0
            self.top_products_table.setItem(row, 3, QTableWidgetItem(f"{percentage:.2f}%"))
            row += 1
    
    def create_payment_methods_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # مخطط دائري لطرق الدفع
        self.payment_chart_widget = QWidget()
        layout.addWidget(self.payment_chart_widget)
        
        # جدول تفصيلي
        self.payment_table = QTableWidget()
        self.payment_table.setColumnCount(3)
        self.payment_table.setHorizontalHeaderLabels(["طريقة الدفع", "عدد العمليات", "القيمة الإجمالية"])
        layout.addWidget(self.payment_table)
        
        # تحديث البيانات
        self.refresh_payment_methods()
        
        return tab
    
    def refresh_payment_methods(self):
        """تحديث بيانات طرق الدفع"""
        sales = self.db.get_sales()
        
        # تجميع البيانات حسب طريقة الدفع
        payment_stats = {}
        for sale in sales:
            method = sale['payment_method']
            if method not in payment_stats:
                payment_stats[method] = {
                    'count': 0,
                    'total': 0
                }
            payment_stats[method]['count'] += 1
            payment_stats[method]['total'] += sale['total_amount']
        
        # تحديث الجدول
        self.payment_table.setRowCount(len(payment_stats))
        
        row = 0
        for method, stats in payment_stats.items():
            method_name = {
                'Cash': 'نقداً',
                'Card': 'بطاقة',
                'Debt': 'آجل'
            }.get(method, method)
            
            self.payment_table.setItem(row, 0, QTableWidgetItem(method_name))
            self.payment_table.setItem(row, 1, QTableWidgetItem(str(stats['count'])))
            self.payment_table.setItem(row, 2, QTableWidgetItem(f"{stats['total']:.2f}"))
            row += 1
    
    def export_report(self):
        """تصدير التقرير الحالي"""
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:
            self.export_daily_sales()
        elif current_tab == 1:
            self.export_top_products()
        elif current_tab == 2:
            self.export_payment_methods()
    
    def export_daily_sales(self):
        """تصدير تقرير المبيعات اليومية"""
        # تنفيذ التصدير إلى Excel
        pass

    def export_top_products(self):
        pass

    def export_payment_methods(self):
        pass
    
    def print_report(self):
        """طباعة التقرير"""
        # تنفيذ الطباعة
        pass

    def on_tab_changed(self, index):
        if index == 0: # Daily Sales tab
            self.refresh_daily_sales()
        elif index == 1: # Top Products tab
            self.refresh_top_products()
        elif index == 2: # Payment Methods tab
            self.refresh_payment_methods()
