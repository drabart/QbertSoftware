"""
Main application entry point.
"""

import sys
import os
from PyQt6 import QtWidgets, QtCore
from core import TranslationManager, Router, Navbar
from screens import HomeScreen, SettingsScreen, DebugScreen


class MainWindow(QtWidgets.QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qbert Software")
        
        # Translation
        self.translation_manager = TranslationManager()
        
        # Setup UI with router
        self.stack = QtWidgets.QStackedWidget()
        
        # Create router
        self.router = Router(self.stack)
        
        # Create screens
        self.home_screen = HomeScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.debug_screen = DebugScreen(self)
        
        # Register routes with router
        self.router.register('home', self.home_screen)
        self.router.register('settings', self.settings_screen)
        self.router.register('debug', self.debug_screen)
        
        # Create navbar
        navbar_routes = [
            {'name': 'home', 'icon': 'home.png', 'label': 'Home'},
            {'name': 'debug', 'icon': 'debug.png', 'label': 'Debug'},
            {'name': 'settings', 'icon': 'settings.png', 'label': 'Settings'},
        ]
        self.navbar = Navbar(self.router, navbar_routes, self)
        
        # Create main container with stack and navbar
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add stack (takes most space)
        main_layout.addWidget(self.stack, 1)
        
        # Add navbar at bottom
        main_layout.addWidget(self.navbar, 0)
        
        self.setCentralWidget(main_widget)
        
        # Navigate to initial screen
        self.router.navigate('home')
        
        # Setup language selector if present
        if hasattr(self.settings_screen, 'languageComboBox'):
            self._setup_language_selector()
        
        # Load theme and language
        self._load_theme("themes/dark.qss")
        self.translation_manager.set_language("en")
        
        # Set window size
        self.resize(1280, 600)
        # self.showFullScreen()  # Uncomment for fullscreen/touchscreen
    
    def _setup_language_selector(self):
        """Setup language selection combo box."""
        combo = self.settings_screen.languageComboBox
        combo.clear()
        for lang_code in self.translation_manager.get_available_languages():
            lang_name = self.translation_manager.get_language_name(lang_code)
            combo.addItem(lang_name, lang_code)
        
        # Set current language
        current_lang = self.translation_manager.current_language
        index = combo.findData(current_lang)
        if index >= 0:
            combo.setCurrentIndex(index)
        
        combo.currentIndexChanged.connect(self._on_language_changed)
    
    def _on_language_changed(self, index):
        """Handle language change."""
        combo = self.settings_screen.languageComboBox
        lang_code = combo.itemData(index)
        if lang_code:
            self.translation_manager.set_language(lang_code)
    
    def _load_theme(self, theme_file: str):
        """Load a theme from QSS file."""
        theme_path = os.path.join("themes", theme_file)
        common_path = os.path.join("themes", "common.qss")
        
        style = ""
        if os.path.exists(common_path):
            with open(common_path, 'r') as f:
                style += f.read() + "\n"
        if os.path.exists(theme_path):
            with open(theme_path, 'r') as f:
                style += f.read()
        
        if style:
            self.setStyleSheet(style)


def main():
    """Application entry point."""
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Qbert Software")
    app.setOrganizationName("Qbert")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
