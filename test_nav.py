import sys
from PySide6.QtWidgets import QApplication

# Test navigation
app = QApplication(sys.argv)

# Import after QApplication
from main import *
from data_manager import DataManager

db = DataManager()

# Create a test user
test_user = {
    'id': 1,
    'username': 'admin',
    'role': 'admin',
    'permissions': ['dashboard', 'pos', 'inventory', 'customers', 'users', 'reports', 'settings', 'invoices']
}

print("Creating MainWindow...")
window = MainWindow(test_user, db)

print(f"Content stack widget count: {window.content_stack.count()}")
print(f"Current page index: {window.content_stack.currentIndex()}")
print(f"Navigation buttons: {list(window.nav_manager.nav_btns.keys())}")
print(f"Button indices: {window.nav_manager.btn_indices}")

# Test switching
print("\nTesting page switch to index 1 (POS)...")
window.nav_manager.switch_page(1)
print(f"After switch - Current index: {window.content_stack.currentIndex()}")

print("\nNavigation test completed successfully!")
sys.exit(0)
