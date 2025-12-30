from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QSize, QParallelAnimationGroup, Property, Qt
from PySide6.QtGui import QColor

class Colors:
    BACKGROUND = "#0d1117"
    SECONDARY_BG = "#161b22"
    ACCENT = "#58a6ff"
    SUCCESS = "#238636"
    DANGER = "#ff6b6b"
    TEXT_PRIMARY = "#f0f6fc"
    TEXT_SECONDARY = "#8b949e"
    BORDER = "#30363d"

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
