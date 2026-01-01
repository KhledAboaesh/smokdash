from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QLabel, QFrame, QDoubleSpinBox
from components.style_engine import Colors, StyleEngine
from PySide6.QtCore import Qt
import qtawesome as qta

class OpenShiftDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("فتح وردية جديدة")
        self.setFixedWidth(400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.container = QFrame()
        self.container.setObjectName("dialogContainer")
        main_layout.addWidget(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header = QLabel("بدء وردية مبيعات جديدة")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)
        
        info = QLabel("يرجى إدخال المبلغ النقدي المتوفر في الدرج الآن:")
        info.setObjectName("subtitleLabel")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        form = QFormLayout()
        form.setSpacing(15)
        
        self.cash_input = QDoubleSpinBox()
        self.cash_input.setMaximum(999999.99)
        self.cash_input.setPrefix("LYD ")
        self.cash_input.setFixedHeight(45)
        
        form.addRow("المبلغ الافتتاحي:", self.cash_input)
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        self.open_btn = QPushButton(" فتح الوردية")
        self.open_btn.setIcon(qta.icon("fa5s.clock", color="#062C21"))
        self.open_btn.setObjectName("posButton")
        self.open_btn.setFixedHeight(45)
        self.open_btn.clicked.connect(self.accept)
        
        btns.addWidget(self.open_btn)
        layout.addLayout(btns)
        
        StyleEngine.apply_shadow(self.container)

    def get_start_cash(self):
        return self.cash_input.value()

class CloseShiftDialog(QDialog):
    def __init__(self, shift_data, report, parent=None):
        super().__init__(parent)
        self.shift_data = shift_data
        self.report = report
        self.setWindowTitle("إغلاق الوردية")
        self.setFixedWidth(450)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.container = QFrame()
        self.container.setObjectName("dialogContainer")
        main_layout.addWidget(self.container)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        header = QLabel("إغلاق الوردية وتقرير Z")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)
        
        # Summary Grid
        summary = QFrame()
        summary.setObjectName("statsCard")
        sl = QFormLayout(summary)
        sl.setContentsMargins(15, 15, 15, 15)
        sl.setSpacing(10)
        
        start_cash = self.shift_data.get('start_cash', 0)
        total_sales = self.report.get('total', 0)
        cash_sales = self.report.get('cash', 0)
        expected_cash = start_cash + cash_sales
        
        sl.addRow("المبلغ الافتتاحي:", QLabel(f"{start_cash:.2f} LYD"))
        sl.addRow("إجمالي المبيعات:", QLabel(f"{total_sales:.2f} LYD"))
        sl.addRow("المبيعات النقدية:", QLabel(f"{cash_sales:.2f} LYD"))
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: #D4AF37;")
        sl.addRow(line)
        
        expected_lbl = QLabel(f"{expected_cash:.2f} LYD")
        expected_lbl.setStyleSheet("font-weight: bold; color: #D4AF37; font-size: 16px;")
        sl.addRow("النقد المتوقع في الدرج:", expected_lbl)
        
        layout.addWidget(summary)
        
        # Final Cash Input
        layout.addWidget(QLabel("إدخال النقد الفعلي عند الإغلاق:"))
        self.final_cash = QDoubleSpinBox()
        self.final_cash.setMaximum(999999.99)
        self.final_cash.setPrefix("LYD ")
        self.final_cash.setFixedHeight(45)
        self.final_cash.setValue(expected_cash)
        layout.addWidget(self.final_cash)
        
        self.notes = QLineEdit()
        self.notes.setPlaceholderText("ملاحظات إضافية...")
        layout.addWidget(self.notes)
        
        btns = QHBoxLayout()
        self.close_btn = QPushButton(" تأكيد وإغلاق الوردية")
        self.close_btn.setIcon(qta.icon("fa5s.lock", color="#062C21"))
        self.close_btn.setObjectName("dangerButton")
        self.close_btn.setFixedHeight(45)
        self.close_btn.clicked.connect(self.accept)
        
        btns.addWidget(self.close_btn)
        layout.addLayout(btns)
        
        StyleEngine.apply_shadow(self.container)

    def get_data(self):
        return self.final_cash.value(), self.notes.text()
