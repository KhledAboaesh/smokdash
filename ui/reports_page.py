from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt

def create_reports_page(main_window):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignTop)
    layout.setContentsMargins(20, 20, 20, 20)
    main_window.reports_header = QLabel(main_window.lang.get_text("reports"))
    main_window.reports_header.setObjectName("welcomeLabel")
    layout.addWidget(main_window.reports_header)
    
    # Invoicing
    invoice_group = QFrame()
    invoice_group.setObjectName("statsCard")
    invoice_layout = QVBoxLayout(invoice_group)
    main_window.invoice_header = QLabel("Generate Invoice")
    main_window.invoice_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #58a6ff;")
    main_window.generate_invoice_btn = QPushButton("Generate PDF for Last Sale")
    main_window.generate_invoice_btn.setObjectName("posButton")
    main_window.generate_invoice_btn.clicked.connect(main_window.generate_last_invoice_pdf)
    invoice_layout.addWidget(main_window.invoice_header)
    invoice_layout.addWidget(main_window.generate_invoice_btn)
    layout.addWidget(invoice_group)

    # Advanced Reports
    adv_reports_group = QFrame()
    adv_reports_group.setObjectName("statsCard")
    adv_reports_layout = QVBoxLayout(adv_reports_group)
    adv_reports_header = QLabel("Advanced Analytics")
    adv_reports_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #58a6ff;")
    adv_reports_btn = QPushButton("Show Advanced Reports")
    adv_reports_btn.setObjectName("inventoryButton")
    adv_reports_btn.clicked.connect(main_window.show_advanced_reports)
    adv_reports_layout.addWidget(adv_reports_header)
    adv_reports_layout.addWidget(adv_reports_btn)
    layout.addWidget(adv_reports_group)

    return page
