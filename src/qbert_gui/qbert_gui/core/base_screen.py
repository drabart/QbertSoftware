"""
Base screen class that all screens should inherit from.
"""

from PyQt6 import QtWidgets, QtCore
from qbert_gui.core.shared_resource import get_from_shared
import os


class BaseScreen(QtWidgets.QWidget):
    """Base class for all application screens."""
    
    def __init__(self, ui_file: str, parent=None):
        """
        Initialize the screen.
        
        Args:
            ui_file: Path to the .ui file (relative to ui/ directory)
            parent: Parent widget
        """
        super().__init__(parent)
        self._load_ui(ui_file)
        self.setup_ui()
    
    def _load_ui(self, ui_file: str):
        """Load the UI file."""
        from PyQt6 import uic
        ui_path = get_from_shared(os.path.join("ui", ui_file))
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"UI file not found: {ui_path}")
        uic.loadUi(ui_path, self)
    
    def setup_ui(self):
        """Override this method to setup UI connections."""
        pass
    
    def changeEvent(self, event: QtCore.QEvent):
        """Handle language change events."""
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
    
    def retranslate_ui(self):
        """Override this method to retranslate UI elements."""
        pass
