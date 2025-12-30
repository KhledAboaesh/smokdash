from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QComboBox
from PySide6.QtCore import Qt
from ui.base_page import BasePage
from components.style_engine import Colors

class SettingsPage(BasePage):
    def __init__(self, main_window):
        title = main_window.lang.get_text("settings")
        subtitle = "تخصيص الخيارات، اللغة، وإدارة النظام"
        super().__init__(main_window, title, subtitle)
        self.setup_ui()

    def setup_ui(self):
        # Language Section
        lang_group = QFrame()
        lang_group.setObjectName("statsCard")
        lang_layout = QVBoxLayout(lang_group)
        lang_layout.setContentsMargins(20, 20, 20, 20)
        
        lang_header = QLabel(self.main_window.lang.get_text("language"))
        lang_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT}; margin-bottom: 10px;")
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("العربية", "ar")
        self.lang_combo.addItem("English", "en")
        
        current_lang = self.main_window.lang.current_language
        index = self.lang_combo.findData(current_lang)
        if index >= 0: self.lang_combo.setCurrentIndex(index)
        
        self.lang_combo.currentIndexChanged.connect(lambda i: self.main_window.change_language(self.lang_combo.itemData(i)))
        
        lang_layout.addWidget(lang_header)
        lang_layout.addWidget(self.lang_combo)
        self.add_widget(lang_group)
        
        # Backup & Update Section Row
        backup_layout = QHBoxLayout()
        backup_layout.setSpacing(20)
        
        # Backup Section
        backup_group = QFrame()
        backup_group.setObjectName("statsCard")
        bl = QVBoxLayout(backup_group)
        bl.setContentsMargins(20, 20, 20, 20)
        
        backup_header = QLabel("النسخ الاحتياطي")
        backup_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        self.backup_btn = QPushButton("إنشاء نسخة احتياطية يدوية")
        self.backup_btn.setObjectName("posButton")
        self.backup_btn.setFixedHeight(40)
        self.backup_btn.clicked.connect(self.main_window.create_manual_backup)
        
        bl.addWidget(backup_header)
        bl.addWidget(self.backup_btn)
        
        # Update Section
        update_group = QFrame()
        update_group.setObjectName("statsCard")
        ul = QVBoxLayout(update_group)
        ul.setContentsMargins(20, 20, 20, 20)
        
        update_header = QLabel("تحديثات النظام")
        update_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT};")
        self.update_btn = QPushButton("التحقق من وجود تحديثات")
        self.update_btn.setObjectName("inventoryButton")
        self.update_btn.setFixedHeight(40)
        self.update_btn.clicked.connect(self.main_window.check_for_updates_action)
        
        ul.addWidget(update_header)
        ul.addWidget(self.update_btn)
        
        backup_layout.addWidget(backup_group)
        backup_layout.addWidget(update_group)
        self.add_layout(backup_layout)
        
        self.layout.addStretch()

    def refresh(self):
        pass
