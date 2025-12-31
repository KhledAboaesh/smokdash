# language_manager.py
import json
import os
from components.utils import resource_path

class LanguageManager:
    def __init__(self):
        self.languages = {}
        self.current_language = "ar"
        self.load_languages()
    
    def load_languages(self):
        """تحميل ملفات اللغة"""
        lang_dir = resource_path("languages")
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
            
            # إنشاء ملف اللغة العربية الافتراضي
            self.create_arabic_language_file()
            self.create_english_language_file()
        
        # تحميل جميع ملفات اللغة
        for file in os.listdir(lang_dir):
            if file.endswith('.json'):
                lang_code = file.replace('.json', '')
                with open(os.path.join(lang_dir, file), 'r', encoding='utf-8') as f:
                    self.languages[lang_code] = json.load(f)
    
    def create_arabic_language_file(self):
        """إنشاء ملف اللغة العربية"""
        arabic_translations = {
            "app_title": "سموك داش - منظومة إدارة محل سجائر",
            "login": "تسجيل الدخول",
            "username": "اسم المستخدم",
            "password": "كلمة المرور",
            "dashboard": "لوحة التحكم",
            "pos": "نقطة البيع",
            "inventory": "المخزون",
            "customers": "العملاء",
            "reports": "التقارير",
            "settings": "الإعدادات",
            "logout": "تسجيل الخروج",
            "users": "الموظفين",
            "welcome": "أهلاً بك",
            "sales_amount": "مبيعات اليوم",
            "transaction_count": "إجمالي العمليات",
            "inventory_value": "قيمة المخزون",
            "low_stock": "نواقص المخزون",
            "add_product": "إضافة صنف",
            "edit_product": "تعديل صنف",
            "delete_product": "حذف صنف",
            "save": "حفظ",
            "cancel": "إلغاء",
            "search": "بحث...",
            "language": "اللغة",
            "arabic": "العربية",
            "english": "الإنجليزية",
            "backup": "النسخ الاحتياطي",
            "create_backup": "إنشاء نسخة احتياطية",
            "restore_backup": "استعادة نسخة احتياطية",
            "check_updates": "التحقق من التحديثات",
            "shift_status": "حالة الوردية",
            "open_shift": "فتح وردية",
            "close_shift": "إغلاق الوردية",
            "confirm_close": "هل أنت متأكد من إغلاق الوردية؟",
            "dashboard_sub": "متابعة أداء المحل اليوم",
            "stock_count": "الأصناف المتوفرة",
            "db_status": "قاعدة البيانات",
            "quick_backup": "نسخ احتياطي سريع",
            "pos_cash": "نقداً",
            "pos_card": "بطاقة",
            "pos_debt": "دين",
            "recent_sales": "آخر العمليات",
            "stock_alerts": "تنبيهات نواقص المخزون",
            "financial_summary": "الملخص المالي",
            "total_revenue": "إجمالي المبيعات",
            "total_debt": "إجمالي الديون",
            "collect_debt": "تحصيل دين",
            "add_customer": "إضافة عميل",
            "edit_customer": "تعديل بيانات عميل",
            "full_name": "الاسم الكامل",
            "phone": "رقم الهاتف",
            "role": "الدور الوظيفي",
            "password_show": "كلمة المرور"
        }
        
        with open(resource_path("languages/ar.json"), 'w', encoding='utf-8') as f:
            json.dump(arabic_translations, f, ensure_ascii=False, indent=2)
    
    def create_english_language_file(self):
        """إنشاء ملف اللغة الإنجليزية"""
        english_translations = {
            "app_title": "SmokeDash - Cigarette Shop Management System",
            "login": "Login",
            "username": "Username",
            "password": "Password",
            "dashboard": "Dashboard",
            "pos": "Point of Sale",
            "inventory": "Inventory",
            "customers": "Customers",
            "reports": "Reports",
            "settings": "Settings",
            "logout": "Logout",
            "users": "Staff",
            "welcome": "Welcome",
            "sales_amount": "Sales Today",
            "transaction_count": "Transactions",
            "inventory_value": "Inventory Value",
            "low_stock": "Low Stock Items",
            "add_product": "Add Product",
            "edit_product": "Edit Product",
            "delete_product": "Delete Product",
            "save": "Save",
            "cancel": "Cancel",
            "search": "Search...",
            "language": "Language",
            "arabic": "Arabic",
            "english": "English",
            "backup": "Backup",
            "create_backup": "Create Backup",
            "restore_backup": "Restore Backup",
            "check_updates": "Check for Updates",
            "shift_status": "Shift Status",
            "open_shift": "Open Shift",
            "close_shift": "Close Shift",
            "confirm_close": "Are you sure you want to close the shift?",
            "dashboard_sub": "Daily shop performance tracking",
            "stock_count": "Available Items",
            "db_status": "Database Status",
            "quick_backup": "Quick Backup",
            "pos_cash": "Cash",
            "pos_card": "Card",
            "pos_debt": "Debt",
            "recent_sales": "Recent Transactions",
            "stock_alerts": "Stock Alerts",
            "financial_summary": "Financial Summary",
            "total_revenue": "Total Revenue",
            "total_debt": "Total Debt",
            "collect_debt": "Collect Debt",
            "add_customer": "Add Customer",
            "edit_customer": "Edit Customer",
            "full_name": "Full Name",
            "phone": "Phone",
            "role": "Role",
            "password_show": "Password"
        }
        
        with open(resource_path("languages/en.json"), 'w', encoding='utf-8') as f:
            json.dump(english_translations, f, ensure_ascii=False, indent=2)
    
    def get_text(self, key, lang=None):
        """الحصول على النص المترجم"""
        if lang is None:
            lang = self.current_language
        
        if lang in self.languages and key in self.languages[lang]:
            return self.languages[lang][key]
        
        # إذا لم يتم العثور على الترجمة، إرجاع المفتاح نفسه
        return key
    
    def set_language(self, lang_code):
        """تغيير اللغة الحالية"""
        if lang_code in self.languages:
            self.current_language = lang_code
            return True
        return False
    
    def get_available_languages(self):
        """الحصول على اللغات المتاحة"""
        return list(self.languages.keys())
