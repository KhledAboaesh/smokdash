# notification_manager.py
from datetime import datetime, timedelta
from PySide6.QtCore import QTimer

class NotificationManager:
    def __init__(self, db):
        self.db = db
        self.notifications = []
    
    def check_stock_alerts(self):
        """التحقق من تنبيهات المخزون"""
        products = self.db.get_products()
        alerts = []
        
        for product in products:
            stock = product.get('stock', 0)
            if stock < 5:
                alerts.append({
                    "type": "stock_low",
                    "product": product['name'],
                    "stock": stock,
                    "message": f"المخزون منخفض: {product['name']} ({stock} فقط)",
                    "priority": "high" if stock == 0 else "medium"
                })
        
        return alerts
    
    def check_expiry_alerts(self):
        """التحقق من منتجات على وشك الانتهاء"""
        # يمكن إضافة تاريخ انتهاء للمنتجات في المستقبل
        return []
    
    def check_debt_alerts(self):
        """التحقق من الديون المتأخرة"""
        customers = self.db.get_customers()
        alerts = []
        
        for customer in customers:
            if customer['debt'] > 1000:  # إذا تجاوز الدين 1000
                alerts.append({
                    "type": "debt_high",
                    "customer": customer['name'],
                    "debt": customer['debt'],
                    "message": f"دين مرتفع: {customer['name']} ({customer['debt']:.2f})",
                    "priority": "high"
                })
        
        return alerts
    
    def get_all_alerts(self):
        """الحصول على جميع التنبيهات"""
        alerts = []
        alerts.extend(self.check_stock_alerts())
        alerts.extend(self.check_expiry_alerts())
        alerts.extend(self.check_debt_alerts())
        
        # ترتيب حسب الأولوية
        priority_order = {"high": 0, "medium": 1, "low": 2}
        alerts.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return alerts
