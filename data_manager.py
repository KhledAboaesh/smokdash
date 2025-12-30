import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.products_file = os.path.join(self.data_dir, "products.json")
        self.sales_file = os.path.join(self.data_dir, "sales.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        
        self._initialize_files()

    def _initialize_files(self):
        if not os.path.exists(self.products_file):
            self._save_json(self.products_file, [])
        if not os.path.exists(self.sales_file):
            self._save_json(self.sales_file, [])
        if not os.path.exists(self.settings_file):
            self._save_json(self.settings_file, {"theme": "dark", "currency": "LYD", "shop_name": "SmokeDash"})

    def get_settings(self):
        return self._load_json(self.settings_file, dict)

    def save_settings(self, settings_data):
        self._save_json(self.settings_file, settings_data)
        return settings_data

    def _load_json(self, file_path, default_type=list):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_type()

    def _save_json(self, file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Products Management
    def get_products(self):
        return self._load_json(self.products_file, list)

    def add_product(self, product_data):
        products = self.get_products()
        product_data['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
        products.append(product_data)
        self._save_json(self.products_file, products)
        return product_data

    def update_product_stock(self, product_id, quantity_change):
        products = self.get_products()
        for p in products:
            if p['id'] == product_id:
                p['stock'] = p.get('stock', 0) + quantity_change
                break
        self._save_json(self.products_file, products)

    # Sales Management
    def add_sale(self, items, total_amount, payment_method):
        sales = self._load_json(self.sales_file)
        sale_data = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "items": items,
            "total_amount": total_amount,
            "payment_method": payment_method
        }
        sales.append(sale_data)
        self._save_json(self.sales_file, sales)
        
        # Update stock for each item
        for item in items:
            self.update_product_stock(item['product_id'], -item['quantity'])
            
        return sale_data

    def get_sales(self):
        return self._load_json(self.sales_file)
