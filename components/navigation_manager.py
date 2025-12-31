from PySide6.QtWidgets import QStackedWidget, QPushButton
from PySide6.QtCore import QSize, Qt
import qtawesome as qta
from components.style_engine import Colors

class NavigationManager:
    def __init__(self, main_window, stack_widget, sidebar_layout):
        self.main_window = main_window
        self.stack = stack_widget
        self.sidebar_layout = sidebar_layout
        self.nav_btns = {}
        self.btn_indices = {}
        self.current_index = -1

    def add_navigation(self, key, text, icon, page_index, role_required=None):
        if role_required and self.main_window.user_data['role'] != role_required and self.main_window.user_data['role'] != "admin":
            return
            
        btn = QPushButton(text)
        btn.setObjectName("sidebarBtn")
        btn.setIcon(qta.icon(icon, color=Colors.TEXT_SECONDARY))
        btn.setIconSize(QSize(20, 20))
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.switch_page(page_index))
        
        self.sidebar_layout.addWidget(btn)
        self.nav_btns[key] = btn
        self.btn_indices[btn] = page_index
        return btn

    def switch_page(self, index):
        if index == self.current_index:
            return
            
        self.stack.setCurrentIndex(index)
        self.current_index = index
        
        # Update button states
        for btn in self.nav_btns.values():
            btn.setChecked(self.btn_indices.get(btn) == index)
            # We could also use StyleEngine to apply transitions here
