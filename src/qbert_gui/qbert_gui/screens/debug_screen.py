"""Debug Screen."""

from core.base_screen import BaseScreen
from core.icon_utils import set_button_icon


class DebugScreen(BaseScreen):
    """Debug screen."""
    
    def __init__(self, parent=None):
        super().__init__("debug.ui", parent)
    
    def setup_ui(self):
        """Setup UI connections."""
        pass
    
    def retranslate_ui(self):
        """Retranslate UI elements."""
        pass
