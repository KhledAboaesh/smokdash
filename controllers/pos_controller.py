from controllers.base_controller import BaseController
from datetime import datetime

class POSController(BaseController):
    def __init__(self, db, main_window=None):
        super().__init__(db, main_window)
        self.cart_items = []

    def search_products(self, query):
        text = query.lower()
        products = self.db.get_products()
        return [p for p in products if text in p['name'].lower() or text in p.get('id', '').lower()]

    def add_to_cart(self, product_id):
        product = self.db.get_product_by_id(product_id)
        if not product or product['stock'] <= 0:
            return False, "الكمية غير متوفرة"

        existing = next((i for i in self.cart_items if i['product_id'] == product_id), None)
        if existing:
            if existing['quantity'] < product['stock']:
                existing['quantity'] += 1
                existing['total'] = existing['quantity'] * existing['price']
                return True, "تم الكرار"
            else:
                return False, "تم الوصول للحد الأقصى للمخزون"
        else:
            self.cart_items.append({
                "product_id": product_id,
                "name": product['name'],
                "quantity": 1,
                "price": product['price'],
                "total": product['price']
            })
            return True, "تمت الإضافة"

    def clear_cart(self):
        self.cart_items = []

    def get_cart_total(self):
        return sum(item['total'] for item in self.cart_items)

    def process_sale(self, method, shift_id, customer_id=None):
        if not self.cart_items:
            return False, "السلة فارغة", None
        
        total = self.get_cart_total()
        try:
            sale = self.db.add_sale(self.cart_items, total, method, shift_id, customer_id)
            self.clear_cart()
            return True, "تمت العملية بنجاح", sale
        except Exception as e:
            return False, f"فشل في إتمام البيع: {str(e)}", None
