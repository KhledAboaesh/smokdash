from PySide6.QtCore import QObject, Signal

class BaseController(QObject):
    """
    Base class for all business logic controllers.
    Ensures consistent access to the database and signals.
    """
    error_occurred = Signal(str)
    operation_success = Signal(str)

    def __init__(self, db, main_window=None):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.settings = db.get_settings()

    def refresh_settings(self):
        self.settings = self.db.get_settings()
