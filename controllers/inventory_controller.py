from controllers.base_controller import BaseController

class InventoryController(BaseController):
    def __init__(self, db, main_window=None):
        super().__init__(db, main_window)

    def get_all_products(self):
        return self.db.get_products()

    def add_product(self, data):
        if not data.get('name'):
            return False, "يجب إدخال اسم المنتج"
        try:
            self.db.add_product(data)
            return True, "تمت إضافة المنتج بنجاح"
        except Exception as e:
            return False, f"خطأ أثناء الإضافة: {str(e)}"

    def update_product(self, product_id, data):
        try:
            self.db.update_product(product_id, data)
            return True, "تم تحديث البيانات بنجاح"
        except Exception as e:
            return False, f"خطأ أثناء التحديث: {str(e)}"

    def delete_product(self, product_id):
        try:
            self.db.delete_product(product_id)
            return True, "تم حذف المنتج بنجاح"
        except Exception as e:
            return False, f"خطأ أثناء الحذف: {str(e)}"

    def get_low_stock_alerts(self, threshold=5):
        products = self.db.get_products()
        return [p for p in products if p['stock'] <= threshold]
