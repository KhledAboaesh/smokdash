from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Signal, Qt

class NumpadWidget(QWidget):
    digit_pressed = Signal(str)
    action_pressed = Signal(str) # 'enter', 'clear', 'backspace'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(10)
        
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 0), ('.', 3, 1), ('⌫', 3, 2),
            ('مسح', 4, 0, 1, 1), ('إدخال', 4, 1, 1, 2)
        ]
        
        for b in buttons:
            btn = QPushButton(b[0])
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setObjectName("numpadKey" if b[0] in '0123456789.' else "numpadAction")
            if len(b) == 5:
                layout.addWidget(btn, b[1], b[2], b[3], b[4])
            else:
                layout.addWidget(btn, b[1], b[2])
            
            if b[0] in '0123456789.':
                btn.clicked.connect(lambda ch=b[0]: self.digit_pressed.emit(ch))
            else:
                if b[0] == '⌫':
                    btn.clicked.connect(lambda: self.action_pressed.emit('backspace'))
                elif b[0] == 'مسح':
                    btn.clicked.connect(lambda: self.action_pressed.emit('clear'))
                elif b[0] == 'إدخال':
                    btn.clicked.connect(lambda: self.action_pressed.emit('enter'))
