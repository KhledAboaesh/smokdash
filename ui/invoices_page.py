from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QHeaderView, QTableWidgetItem, QFrame, QLineEdit, QMenu, QMessageBox, QDialog)
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from components.style_engine import Colors
from components.stats_card import StatsCard
from datetime import datetime


class InvoicesPage(BasePage):
    def __init__(self, main_window):
        title = "الفواتير"
        subtitle = "إدارة وسجل الفواتير السابقة"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()
        
    def setup_ui(self):
        # Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        currency = self.main_window.settings.get('currency', 'LYD')
        
        self.stat_count = StatsCard("عدد الفواتير (الكلي)", "0", "fa5s.file-invoice", Colors.ACCENT)
        self.stat_total = StatsCard("إجمالي المبيعات (الكلية)", f"0.00 {currency}", "fa5s.money-bill-wave", Colors.SUCCESS)
        
        stats_layout.addWidget(self.stat_count)
        stats_layout.addWidget(self.stat_total)
        stats_layout.addStretch()
        
        self.add_layout(stats_layout)
        
        # Search & Filter
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث برقم الفاتورة أو اسم العميل...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.ACCENT};
                border-radius: 0px;
                padding: 10px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Colors.TEXT_PRIMARY};
            }}
        """)
        self.search_input.textChanged.connect(self.filter_invoices)
        
        top_layout.addWidget(self.search_input)
        
        self.layout.addLayout(top_layout)
        
        # Table Panel
        table_panel = QFrame()
        table_panel.setObjectName("statsCard")
        # Global Styles for Menu and Table
        table_panel.setStyleSheet(f"""
            QFrame#statsCard {{
                background-color: {Colors.SECONDARY_BG};
                border: 2px solid {Colors.ACCENT};
                border-radius: 0px;
            }}
            QMenu {{
                background-color: {Colors.SECONDARY_BG};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.ACCENT};
            }}
            QMenu::item {{
                padding: 8px 25px;
            }}
            QMenu::item:selected {{
                background-color: {Colors.ACCENT};
                color: {Colors.BACKGROUND};
            }}
        """)
        panel_layout = QVBoxLayout(table_panel)
        
        headers = ["رقم الفاتورة", "التاريخ", "العميل", "القيمة", "طريقة الدفع"]
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                gridline-color: {Colors.ACCENT};
                color: {Colors.TEXT_PRIMARY};
                border: none;
            }}
            QHeaderView::section {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.ACCENT};
                padding: 12px;
                border: 1px solid {Colors.ACCENT};
                font-weight: bold;
            }}
            QTableWidget::item:selected {{
                background-color: {Colors.ACCENT};
                color: {Colors.BACKGROUND};
            }}
        """)
        
        # Context Menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        panel_layout.addWidget(self.table)
        self.layout.addWidget(table_panel)
        
    def show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item: return
        
        row = item.row()
        # Retrieve Invoice Number from UserRole to avoid string parsing issues
        inv_id = str(self.table.item(row, 0).data(Qt.UserRole))
        
        menu = QMenu(self)
        print_action = menu.addAction("طباعة الفاتورة 🖨️")
        delete_action = menu.addAction("حذف الفاتورة 🗑️")
        
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        if action == print_action:
            self.reprint_invoice(inv_id)
        elif action == delete_action:
            self.confirm_delete_invoice(inv_id)

    def confirm_delete_invoice(self, inv_id):
        reply = QMessageBox.question(self, "تأكيد الحذف", 
                                   f"هل أنت متأكد من حذف الفاتورة رقم {inv_id}؟\nسيتم إرجاع المنتجات للمخزون وتعديل حساب العميل.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, msg = self.main_window.db.delete_sale(inv_id)
            if success:
                QMessageBox.information(self, "تم", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "خطأ", msg)


    def reprint_invoice(self, inv_id):
        try:
            # Find sale data
            sales = self.main_window.db.get_sales()
            sale = next((s for s in sales if str(s.get('invoice_number')) == inv_id), None)
            
            if sale:
                pdf = self.main_window.invoice_mgr.generate_pdf_invoice(sale, self.main_window.settings)
                if pdf:
                    self.main_window.invoice_mgr.print_invoice(pdf)
                    QMessageBox.information(self, "تم", "تم إرسال الفاتورة للطباعة")
                else:
                    QMessageBox.warning(self, "فشل", "فشل إنشاء ملف PDF للفاتورة")
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الفاتورة")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الطباعة:\n{str(e)}")

    def refresh(self):
        sales = self.main_window.db.get_sales()
        # Sort by date desc
        sales.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Update Stats
        count = len(sales)
        total = sum(s['total_amount'] for s in sales)
        currency = self.main_window.settings.get('currency', 'LYD')
        
        self.stat_count.update_value(str(count))
        self.stat_total.update_value(f"{total:.2f} {currency}")
        
        self.all_sales = sales # Store for filtering
        self.populate_table(sales)

    def populate_table(self, sales_list):
        self.table.setRowCount(0)
        for s in sales_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            inv_num = str(s.get('invoice_number', 'N/A'))
            
            # Helper cells
            item_id = QTableWidgetItem(inv_num)
            item_id.setData(Qt.UserRole, inv_num) # STORE DATA HERE
            self.table.setItem(row, 0, item_id)
            
            ts = s['timestamp'].replace('T', ' ').split('.')[0]
            self.table.setItem(row, 1, QTableWidgetItem(ts))
            
            cust_name = "زبون عام"
            if s.get('customer_id'):
                cust = next((c for c in self.main_window.db.get_customers() if c['id'] == s['customer_id']), None)
                if cust: cust_name = cust['name']
            
            self.table.setItem(row, 2, QTableWidgetItem(cust_name))
            
            amount_item = QTableWidgetItem(f"{s['total_amount']:.2f}")
            amount_item.setForeground(Qt.green) # Make price green
            self.table.setItem(row, 3, amount_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(s.get('payment_method', 'N/A')))

    def filter_invoices(self):
        query = self.search_input.text().lower()
        if not hasattr(self, 'all_sales'): return
        
        if not query:
            self.populate_table(self.all_sales)
            return
            
        filtered = []
        for s in self.all_sales:
            inv_no = str(s.get('invoice_number', '')).lower()
            cust_name = ""
            if s.get('customer_id'):
                cust = next((c for c in self.main_window.db.get_customers() if c['id'] == s['customer_id']), None)
                if cust: cust_name = cust['name'].lower()
                
            if query in inv_no or query in cust_name:
                filtered.append(s)
        
        self.populate_table(filtered)
