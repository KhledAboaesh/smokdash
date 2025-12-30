from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, QHeaderView, QPushButton
from PySide6.QtCore import Qt
import qtawesome as qta

def create_dashboard_page(main_window):
    print("Executing create_dashboard_page from ui/dashboard_page.py")
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(30, 30, 30, 30)
    
    shop_name = main_window.settings.get('shop_name', 'سموك داش')
    header = QLabel(f"{main_window.lang.get_text('welcome')}، {main_window.user_data['full_name']}")
    header.setObjectName("welcomeLabel")
    layout.addWidget(header)
    
    sub = QLabel(main_window.lang.get_text("dashboard_sub") if main_window.lang.get_text("dashboard_sub") != "{dashboard_sub}" else "متابعة أداء المحل اليوم")
    sub.setStyleSheet("color: #8b949e; font-size: 16px; margin-bottom: 25px;")
    layout.addWidget(sub)
    
    stats_layout = QHBoxLayout()
    stats_layout.setSpacing(25)
    currency = main_window.settings.get('currency', 'LYD')
    main_window.card_sales = create_stats_card(main_window.lang.get_text("sales_amount"), f"0.00 {currency}", "fa5s.money-bill-wave")
    main_window.card_count = create_stats_card(main_window.lang.get_text("transaction_count"), "0", "fa5s.receipt")
    main_window.card_stock = create_stats_card(main_window.lang.get_text("stock_count"), "0", "fa5s.box-open")
    
    stats_layout.addWidget(main_window.card_sales)
    stats_layout.addWidget(main_window.card_count)
    stats_layout.addWidget(main_window.card_stock)
    layout.addLayout(stats_layout)
    
    layout.addSpacing(40)
    recent_label = QLabel("آخر العمليات")
    recent_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
    layout.addWidget(recent_label)
    
    main_window.recent_table = QTableWidget(0, 3)
    main_window.recent_table.setHorizontalHeaderLabels(["الوقت", "المبلغ", "طريقة الدفع"])
    main_window.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    main_window.recent_table.setFixedHeight(250)
    layout.addWidget(main_window.recent_table)
    
    # Analytics Section
    layout.addSpacing(30)
    analytics_row = QHBoxLayout()
    
    # Weekly Sales Chart (Simple Bar Representation)
    main_window.chart_frame = QFrame()
    main_window.chart_frame.setObjectName("statsCard")
    chart_layout = QVBoxLayout(main_window.chart_frame)
    chart_title = QLabel("تحليل المبيعات الأسبوعي")
    chart_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #58a6ff;")
    chart_layout.addWidget(chart_title)
    
    main_window.bars_container = QHBoxLayout()
    main_window.bars_container.setSpacing(15)
    main_window.bars_container.setAlignment(Qt.AlignBottom)
    main_window.bars_container.setContentsMargins(10, 20, 10, 10)
    chart_layout.addLayout(main_window.bars_container)
    
    # Stock Alerts
    main_window.alerts_frame = QFrame()
    main_window.alerts_frame.setObjectName("statsCard")
    main_window.alerts_frame.setFixedWidth(300)
    alerts_layout = QVBoxLayout(main_window.alerts_frame)
    alerts_title = QLabel("تنبيهات المخزون")
    alerts_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #ff5252;")
    alerts_layout.addWidget(alerts_title)
    
    main_window.alerts_list = QVBoxLayout()
    alerts_layout.addLayout(main_window.alerts_list)
    alerts_layout.addStretch()
    
    analytics_row.addWidget(main_window.chart_frame, 2)
    analytics_row.addWidget(main_window.alerts_frame, 1)
    layout.addLayout(analytics_row)

    layout.addSpacing(30)
    main_window.shift_group = QFrame()
    main_window.shift_group.setObjectName("statsCard")
    shift_layout = QHBoxLayout(main_window.shift_group)
    main_window.shift_status_label = QLabel("حالة الوردية: مغلقة")
    main_window.shift_status_label.setStyleSheet("font-weight: bold; font-size: 16px;")
    main_window.shift_btn = QPushButton("فتح وردية جديدة")
    main_window.shift_btn.setObjectName("posButton")
    main_window.shift_btn.setFixedWidth(200)
    main_window.shift_btn.clicked.connect(main_window.toggle_shift)
    
    shift_layout.addWidget(main_window.shift_status_label)
    shift_layout.addStretch()
    shift_layout.addWidget(main_window.shift_btn)
    layout.addWidget(main_window.shift_group)
    
    layout.addStretch()
    return page

def create_stats_card(title, value, icon):
    card = QFrame()
    card.setObjectName("statsCard")
    card_layout = QVBoxLayout(card)
    icon_label = QLabel()
    icon_label.setPixmap(qta.icon(icon, color="#58a6ff").pixmap(40, 40))
    title_label = QLabel(title)
    title_label.setStyleSheet("color: #888888; font-size: 15px; font-weight: bold;")
    value_label = QLabel(value)
    value_label.setObjectName("totalLabel")
    card_layout.addWidget(icon_label)
    card_layout.addWidget(title_label)
    card_layout.addWidget(value_label)
    return card
