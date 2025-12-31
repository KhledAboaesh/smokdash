import json
import os
from datetime import datetime

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.max_cache_size = 100
    
    def get(self, key):
        """الحصول على بيانات من الذاكرة المؤقتة"""
        if key in self.cache:
            return self.cache[key]
        return None
    
    def set(self, key, value):
        """تخزين بيانات في الذاكرة المؤقتة"""
        if len(self.cache) >= self.max_cache_size:
            # إزالة أقدم عنصر
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "value": value,
            "timestamp": datetime.now()
        }
    
    def clear(self):
        """مسح الذاكرة المؤقتة"""
        self.cache.clear()

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.cache = CacheManager()
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.products_file = os.path.join(self.data_dir, "products.json")
        self.sales_file = os.path.join(self.data_dir, "sales.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.shifts_file = os.path.join(self.data_dir, "shifts.json")
        self.customers_file = os.path.join(self.data_dir, "customers.json")
        
        self._initialize_files()

    def _initialize_files(self):
        if not os.path.exists(self.products_file):
            self._save_json(self.products_file, [])
        if not os.path.exists(self.sales_file):
            self._save_json(self.sales_file, [])
        if not os.path.exists(self.settings_file):
            self._save_json(self.settings_file, {"theme": "dark", "currency": "LYD", "shop_name": "SmokeDash", "language": "ar"})
        if not os.path.exists(self.users_file):
            self._save_json(self.users_file, [
                {"username": "admin", "password": "123", "role": "admin", "full_name": "مدير النظام"},
                {"username": "cashier", "password": "123", "role": "cashier", "full_name": "موظف مبيعات"}
            ])
        if not os.path.exists(self.shifts_file):
            self._save_json(self.shifts_file, [])
        if not os.path.exists(self.customers_file):
            self._save_json(self.customers_file, [])

    def _load_json(self, file_path, default_type=list):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, default_type):
                    return data
                return default_type()
        except (FileNotFoundError, json.JSONDecodeError):
            return default_type()

    def _save_json(self, file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    # Settings
    def get_settings(self, use_cache=True):
        if use_cache:
            cached = self.cache.get("settings")
            if cached: return cached["value"]
        settings = self._load_json(self.settings_file, dict)
        if use_cache: self.cache.set("settings", settings)
        return settings

    def save_settings(self, settings_data):
        self._save_json(self.settings_file, settings_data)
        self.cache.set("settings", settings_data)
        return settings_data

    # Products
    def get_products(self, use_cache=True):
        if use_cache:
            cached = self.cache.get("products")
            if cached: return cached["value"]
        products = self._load_json(self.products_file, list)
        if use_cache: self.cache.set("products", products)
        return products

    def add_product(self, product_data):
        products = self.get_products(use_cache=False)
        product_data['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
        products.append(product_data)
        self._save_json(self.products_file, products)
        self.cache.set("products", products)
        return product_data

    def delete_product(self, product_id):
        products = self.get_products(use_cache=False)
        products = [p for p in products if p['id'] != product_id]
        self._save_json(self.products_file, products)
        self.cache.set("products", products)
        return True

    def update_product(self, product_id, updated_data):
        products = self.get_products(use_cache=False)
        for i, p in enumerate(products):
            if p['id'] == product_id:
                products[i].update(updated_data)
                products[i]['id'] = product_id
                break
        self._save_json(self.products_file, products)
        self.cache.set("products", products)

    def get_product_by_id(self, product_id):
        products = self.get_products()
        return next((p for p in products if p['id'] == product_id), None)

    def update_product_stock(self, product_id, quantity_change):
        products = self.get_products(use_cache=False)
        for p in products:
            if p['id'] == product_id:
                p['stock'] = p.get('stock', 0) + quantity_change
                break
        self._save_json(self.products_file, products)
        self.cache.set("products", products)

    # Sales
    def get_sales(self, use_cache=True):
        if use_cache:
            cached = self.cache.get("sales")
            if cached: return cached["value"]
        sales = self._load_json(self.sales_file, list)
        if use_cache: self.cache.set("sales", sales)
        return sales

    def add_sale(self, items, total_amount, payment_method, shift_id=None, customer_id=None):
        sales = self.get_sales(use_cache=False)
        
        # Generate Unique Invoice Number (INV-YYYY-NNNN)
        today = datetime.now()
        year_prefix = f"INV-{today.year}-"
        last_num = 0
        for s in sales:
            inv_no = s.get('invoice_number', '')
            if inv_no.startswith(year_prefix):
                try:
                    num = int(inv_no.split('-')[-1])
                    if num > last_num: last_num = num
                except: continue
        
        invoice_number = f"{year_prefix}{last_num + 1:04d}"
        
        sale_data = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"), # Added microseconds for higher uniqueness
            "invoice_number": invoice_number,
            "timestamp": datetime.now().isoformat(),
            "items": items,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "shift_id": shift_id,
            "customer_id": customer_id
        }
        sales.append(sale_data)
        self._save_json(self.sales_file, sales)
        self.cache.set("sales", sales)
        
        # Update Stocks
        for item in items:
            self.update_product_stock(item['product_id'], -item['quantity'])
            
        # Update Customer Debt
        if payment_method == 'Debt' and customer_id:
            self.update_customer_debt(customer_id, total_amount)
            
        return sale_data

    def delete_sale(self, sale_id):
        """Removes a sale, restores stock, and adjusts debt if applicable."""
        sales = self.get_sales(use_cache=False)
        sale_to_delete = next((s for s in sales if s['id'] == sale_id or s.get('invoice_number') == sale_id), None)
        
        if not sale_to_delete:
            return False, "الفاتورة غير موجودة"
            
        # 1. Restore Stock
        for item in sale_to_delete.get('items', []):
            self.update_product_stock(item['product_id'], item['quantity'])
            
        # 2. Revert Customer Debt
        if sale_to_delete.get('payment_method') == 'Debt' and sale_to_delete.get('customer_id'):
            self.update_customer_debt(sale_to_delete['customer_id'], -sale_to_delete['total_amount'])
            
        # 3. Remove Sale
        sales = [s for s in sales if s['id'] != sale_to_delete['id']]
        self._save_json(self.sales_file, sales)
        self.cache.set("sales", sales)
        return True, "تم حذف الفاتورة وإرجاع الكميات للمخزون"

    # Users
    def get_users(self, use_cache=True):
        if use_cache:
            cached = self.cache.get("users")
            if cached: return cached["value"]
        users = self._load_json(self.users_file, list)
        if use_cache: self.cache.set("users", users)
        return users

    def add_user(self, user_data):
        users = self.get_users(use_cache=False)
        if any(u['username'] == user_data['username'] for u in users):
            return None
        users.append(user_data)
        self._save_json(self.users_file, users)
        self.cache.set("users", users)
        return user_data

    def update_user_password(self, username, new_password):
        users = self.get_users(use_cache=False)
        for u in users:
            if u['username'] == username:
                u['password'] = new_password
                break
        self._save_json(self.users_file, users)
        self.cache.set("users", users)

    # Shifts
    def get_shifts(self, use_cache=True):
        if use_cache:
            cached = self.cache.get("shifts")
            if cached: return cached["value"]
        shifts = self._load_json(self.shifts_file, list)
        if use_cache: self.cache.set("shifts", shifts)
        return shifts

    def get_active_shift(self, username):
        shifts = self.get_shifts()
        return next((s for s in shifts if s['username'] == username and s['status'] == 'open'), None)

    def open_shift(self, username, start_cash):
        shifts = self.get_shifts(use_cache=False)
        shift_id = datetime.now().strftime("SHFT%Y%m%d%H%M%S")
        new_shift = {
            "id": shift_id,
            "username": username,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "start_cash": start_cash,
            "end_cash": 0,
            "status": "open"
        }
        shifts.append(new_shift)
        self._save_json(self.shifts_file, shifts)
        self.cache.set("shifts", shifts)
        return new_shift

    def close_shift(self, shift_id, end_cash):
        shifts = self.get_shifts(use_cache=False)
        for s in shifts:
            if s['id'] == shift_id:
                s['end_time'] = datetime.now().isoformat()
                s['end_cash'] = end_cash
                s['status'] = 'closed'
                break
        self._save_json(self.shifts_file, shifts)
        self.cache.set("shifts", shifts)

    # Customers
    def get_customers(self, use_cache=True):
        if use_cache:
            cached = self.cache.get("customers")
            if cached: return cached["value"]
        customers = self._load_json(self.customers_file, list)
        if use_cache: self.cache.set("customers", customers)
        return customers

    def add_customer(self, data):
        customers = self.get_customers(use_cache=False)
        new_customer = {
            "id": datetime.now().strftime("CUST%Y%m%d%H%M%S"),
            "name": data.get('name', 'N/A'),
            "phone": data.get('phone', ''),
            "address": data.get('address', ''),
            "debt": 0.0,
            "created_at": datetime.now().isoformat()
        }
        customers.append(new_customer)
        self._save_json(self.customers_file, customers)
        self.cache.set("customers", customers)
        return new_customer

    def update_customer(self, customer_id, data):
        customers = self.get_customers(use_cache=False)
        for c in customers:
            if c['id'] == customer_id:
                c.update(data)
                break
        self._save_json(self.customers_file, customers)
        self.cache.set("customers", customers)

    def update_customer_debt(self, customer_id, amount_change):
        customers = self.get_customers(use_cache=False)
        for c in customers:
            if c['id'] == customer_id:
                c['debt'] += amount_change
                break
        self._save_json(self.customers_file, customers)
        self.cache.set("customers", customers)

    # General purpose methods from original file - kept for compatibility
    def get_sales_by_date_range(self, start_date, end_date):
        sales = self.get_sales()
        filtered = []
        for s in sales:
            sale_date = datetime.fromisoformat(s['timestamp']).date()
            if start_date <= sale_date <= end_date:
                filtered.append(s)
        return filtered
    
    def get_todays_sales(self):
        sales = self.get_sales()
        today = datetime.now().strftime("%Y-%m-%d")
        return [s for s in sales if s['timestamp'].startswith(today)]