"""Settings Screen."""

from core.base_screen import BaseScreen
from core.icon_utils import set_button_icon


class SettingsScreen(BaseScreen):
    """Settings screen."""
    
    def __init__(self, parent=None):
        super().__init__("settings.ui", parent)
    
    def setup_ui(self):
        """Setup UI connections."""
        pass
    
    def retranslate_ui(self):
        """Retranslate UI elements."""
        pass
