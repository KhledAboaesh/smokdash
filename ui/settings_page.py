from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QComboBox, QCheckBox, QLineEdit, QFileDialog
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
        
        lang_group = QFrame()
        lang_group.setObjectName("statsCard")
        lang_layout = QVBoxLayout(lang_group)
        lang_layout.setContentsMargins(20, 20, 20, 20)
        
        # Branding Section
        branding_group = QFrame()
        branding_group.setObjectName("statsCard")
        branding_layout = QVBoxLayout(branding_group)
        branding_layout.setContentsMargins(20, 20, 20, 20)
        
        branding_header = QLabel("إعدادات الهوية (اسم المحل والشعار)")
        branding_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT}; margin-bottom: 10px;")
        
        # Shop Name
        self.shop_name_input = QLineEdit()
        self.shop_name_input.setPlaceholderText("اسم المحل (يظهر في الفاتورة)...")
        self.shop_name_input.setText(self.main_window.settings.get('shop_name', 'SmokeDash'))
        self.shop_name_input.textChanged.connect(self.save_branding)
        
        # Logo
        logo_layout = QHBoxLayout()
        self.logo_path_lbl = QLabel(self.main_window.settings.get('logo_path', 'لا يوجد شعار محدد'))
        self.logo_path_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        
        logo_btn = QPushButton("اختر الشعار")
        logo_btn.setFixedSize(100, 30)
        logo_btn.clicked.connect(self.select_logo)
        
        logo_layout.addWidget(logo_btn)
        
        self.show_logo_chk = QCheckBox("عرض الشعار في الفاتورة")
        self.show_logo_chk.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        self.show_logo_chk.setChecked(self.main_window.settings.get('show_logo', True))
        self.show_logo_chk.toggled.connect(self.save_branding)
        
        branding_layout.addWidget(branding_header)
        branding_layout.addWidget(QLabel("اسم المحل:"))
        branding_layout.addWidget(self.shop_name_input)
        branding_layout.addLayout(logo_layout)
        branding_layout.addWidget(self.show_logo_chk)
        
        self.add_widget(branding_group)
        
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

        # Printing Configuration
        print_group = QFrame()
        print_group.setObjectName("statsCard")
        print_layout = QVBoxLayout(print_group)
        print_layout.setContentsMargins(20, 20, 20, 20)
        
        print_header = QLabel("إعدادات الطباعة")
        print_header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.ACCENT}; margin-bottom: 10px;")
        
        self.auto_print_chk = QCheckBox("تفعيل الطباعة التلقائية للفواتير")
        self.auto_print_chk.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px;")
        
        # Load setting
        self.auto_print_chk.setChecked(self.main_window.settings.get('auto_print', False))
        self.auto_print_chk.toggled.connect(self.update_auto_print_setting)
        
        print_layout.addWidget(print_header)
        print_layout.addWidget(self.auto_print_chk)
        self.add_widget(print_group)
        
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

    def save_branding(self):
        self.main_window.settings['shop_name'] = self.shop_name_input.text()
        self.main_window.settings['show_logo'] = self.show_logo_chk.isChecked()
        self.main_window.db.save_settings(self.main_window.settings)

    def select_logo(self):
        fname, _ = QFileDialog.getOpenFileName(self, "اختر الشعار", "", "Images (*.png *.jpg *.jpeg)")
        if fname:
            self.main_window.settings['logo_path'] = fname
            self.logo_path_lbl.setText(fname)
            self.main_window.db.save_settings(self.main_window.settings)

    def update_auto_print_setting(self, checked):
        self.main_window.settings['auto_print'] = checked
        self.main_window.db.save_settings(self.main_window.settings)

    def refresh(self):
        pass
