from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QComboBox
from PySide6.QtCore import Qt

def create_settings_page(main_window):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignTop)
    layout.setContentsMargins(20, 20, 20, 20)
    header = QLabel("Application Settings")
    header.setObjectName("welcomeLabel")
    layout.addWidget(header)
    # Language Section
    lang_group = QFrame()
    lang_group.setObjectName("statsCard")
    lang_layout = QVBoxLayout(lang_group)
    lang_header = QLabel(main_window.lang.get_text("language"))
    lang_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #58a6ff;")
    
    lang_combo = QComboBox()
    lang_combo.addItem("العربية", "ar")
    lang_combo.addItem("English", "en")
    
    # Set current index based on current language
    current_lang = main_window.lang.current_language
    index = lang_combo.findData(current_lang)
    if index >= 0:
        lang_combo.setCurrentIndex(index)
        
    lang_combo.currentIndexChanged.connect(lambda i: main_window.change_language(lang_combo.itemData(i)))
    
    lang_layout.addWidget(lang_header)
    lang_layout.addWidget(lang_combo)
    layout.addWidget(lang_group)

    # Backup Section
    backup_group = QFrame()
    backup_group.setObjectName("statsCard")
    backup_layout = QVBoxLayout(backup_group)
    backup_header = QLabel(main_window.lang.get_text("backup"))
    backup_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #58a6ff;")
    
    create_backup_btn = QPushButton(main_window.lang.get_text("create_backup"))
    create_backup_btn.setObjectName("posButton")
    create_backup_btn.clicked.connect(main_window.create_manual_backup)
    
    backup_layout.addWidget(backup_header)
    backup_layout.addWidget(create_backup_btn)
    layout.addWidget(backup_group)

    # Update Section
    update_group = QFrame()
    update_group.setObjectName("statsCard")
    update_layout = QVBoxLayout(update_group)
    update_header = QLabel(main_window.lang.get_text("check_updates"))
    update_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #58a6ff;")
    check_update_btn = QPushButton(main_window.lang.get_text("check_updates"))
    check_update_btn.setObjectName("posButton")
    check_update_btn.clicked.connect(main_window.check_for_updates_action)
    update_layout.addWidget(update_header)
    update_layout.addWidget(check_update_btn)
    layout.addWidget(update_group)
    
    return page
