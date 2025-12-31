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
        # 1. Branding Section (Shop Name & Logo)
        branding_group = QFrame()
        branding_group.setObjectName("statsCard")
        branding_layout = QVBoxLayout(branding_group)
        branding_layout.setContentsMargins(30, 30, 30, 30)
        branding_layout.setSpacing(15)
        
        branding_header = QLabel("إعدادات الهوية (اسم المحل والشعار)")
        branding_header.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {Colors.ACCENT}; border-bottom: 1px solid {Colors.ACCENT}; padding-bottom: 5px; margin-bottom: 0px;")
        
        # Shop Name
        self.shop_name_input = QLineEdit()
        self.shop_name_input.setPlaceholderText("اسم المحل (يظهر في الفاتورة)...")
        self.shop_name_input.setText(self.main_window.settings.get('shop_name', 'SmokeDash'))
        self.shop_name_input.textChanged.connect(self.save_branding)
        
        # Logo Select
        logo_layout = QHBoxLayout()
        self.logo_path_lbl = QLabel(self.main_window.settings.get('logo_path', 'لا يوجد شعار محدد'))
        self.logo_path_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        self.logo_path_lbl.setWordWrap(True)
        
        logo_btn = QPushButton("اختر الشعار")
        logo_btn.setFixedSize(120, 35)
        logo_btn.clicked.connect(self.select_logo)
        
        logo_layout.addWidget(logo_btn)
        logo_layout.addWidget(self.logo_path_lbl)
        
        self.show_logo_chk = QCheckBox("عرض الشعار في الفاتورة المطبوعة")
        self.show_logo_chk.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: bold;")
        self.show_logo_chk.setChecked(self.main_window.settings.get('show_logo', True))
        self.show_logo_chk.toggled.connect(self.save_branding)
        
        branding_layout.addWidget(branding_header)
        branding_layout.addWidget(QLabel("اسم المحل:"))
        branding_layout.addWidget(self.shop_name_input)
        branding_layout.addSpacing(10)
        branding_layout.addLayout(logo_layout)
        branding_layout.addWidget(self.show_logo_chk)
        
        self.add_widget(branding_group)

        # 2. Language & Internationalization
        lang_group = QFrame()
        lang_group.setObjectName("statsCard")
        lang_layout = QVBoxLayout(lang_group)
        lang_layout.setContentsMargins(30, 30, 30, 30)
        lang_layout.setSpacing(15)
        
        lang_header = QLabel(self.main_window.lang.get_text("language"))
        lang_header.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {Colors.ACCENT}; border-bottom: 1px solid {Colors.ACCENT}; padding-bottom: 5px; margin-bottom:0px;")
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("العربية", "ar")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setFixedHeight(40)
        
        current_lang = self.main_window.lang.current_language
        index = self.lang_combo.findData(current_lang)
        if index >= 0: self.lang_combo.setCurrentIndex(index)
        
        self.lang_combo.currentIndexChanged.connect(lambda i: self.main_window.change_language(self.lang_combo.itemData(i)))
        
        lang_layout.addWidget(lang_header)
        lang_layout.addWidget(self.lang_combo)
        self.add_widget(lang_group)

        # 3. Printing Configuration
        print_group = QFrame()
        print_group.setObjectName("statsCard")
        print_layout = QVBoxLayout(print_group)
        print_layout.setContentsMargins(30, 30, 30, 30)
        print_layout.setSpacing(15)
        
        print_header = QLabel("إعدادات الطابعة والتشغيل")
        print_header.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {Colors.ACCENT}; border-bottom: 1px solid {Colors.ACCENT}; padding-bottom: 5px; margin-bottom: 0px;")
        
        self.auto_print_chk = QCheckBox("تفعيل الطباعة التلقائية (مباشرة بعد عملية البيع)")
        self.auto_print_chk.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; font-weight: bold;")
        self.auto_print_chk.setChecked(self.main_window.settings.get('auto_print', False))
        self.auto_print_chk.toggled.connect(self.update_auto_print_setting)
        
        print_layout.addWidget(print_header)
        print_layout.addWidget(self.auto_print_chk)
        self.add_widget(print_group)
        
        # 4. Backup & Maintenance
        maint_layout = QHBoxLayout()
        maint_layout.setSpacing(20)
        
        # Backup
        backup_group = QFrame()
        backup_group.setObjectName("statsCard")
        bl = QVBoxLayout(backup_group)
        bl.setContentsMargins(30, 30, 30, 30)
        bl.setSpacing(15)
        
        bl.addWidget(QLabel("النسخ الاحتياطي", styleSheet=f"font-size: 20px; font-weight: 800; color: {Colors.ACCENT}; border-bottom: 1px solid {Colors.ACCENT}; padding-bottom: 5px;"))
        self.backup_btn = QPushButton("إنشاء نسخة احتياطية الآن")
        self.backup_btn.setObjectName("posButton")
        self.backup_btn.setFixedHeight(50)
        self.backup_btn.clicked.connect(self.main_window.create_manual_backup)
        bl.addWidget(self.backup_btn)
        
        # Update
        update_group = QFrame()
        update_group.setObjectName("statsCard")
        ul = QVBoxLayout(update_group)
        ul.setContentsMargins(30, 30, 30, 30)
        ul.setSpacing(15)
        
        ul.addWidget(QLabel("تحديثات النظام", styleSheet=f"font-size: 20px; font-weight: 800; color: {Colors.ACCENT}; border-bottom: 1px solid {Colors.ACCENT}; padding-bottom: 5px;"))
        self.update_btn = QPushButton("التحقق من الإصدار الجديد")
        self.update_btn.setObjectName("inventoryButton")
        self.update_btn.setFixedHeight(50)
        self.update_btn.clicked.connect(self.main_window.check_for_updates_action)
        ul.addWidget(self.update_btn)
        
        maint_layout.addWidget(backup_group)
        maint_layout.addWidget(update_group)
        self.add_layout(maint_layout)
        
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
