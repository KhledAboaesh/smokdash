from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QSize, QParallelAnimationGroup, Property, Qt
from PySide6.QtGui import QColor

class Colors:
    BACKGROUND = "#062C21"    # Deep Emerald
    SECONDARY_BG = "#0A3B2C"  # Lighter Emerald
    ACCENT = "#D4AF37"        # Royal Gold
    SUCCESS = "#3fb950"
    DANGER = "#f85149"
    TEXT_PRIMARY = "#FDFCF0"  # Pearl White
    TEXT_SECONDARY = "#C8C4A0" # Dim Pearl
    BORDER = "#D4AF37"        # Gold Border

class StyleEngine:
    @staticmethod
    def apply_shadow(widget, blur=15, offset=(0, 4), color=QColor(0, 0, 0, 100)):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(offset[0], offset[1])
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)
        return shadow

    @staticmethod
    def create_hover_anim(widget, start_color=QColor("#161b22"), end_color=QColor("#1f6feb")):
        # Note: Background color animation requires custom property or stylesheet manipulation
        pass

    @staticmethod
    def apply_fade_in(widget, duration=300):
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        anim = QPropertyAnimation(opacity_effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()
        return anim
