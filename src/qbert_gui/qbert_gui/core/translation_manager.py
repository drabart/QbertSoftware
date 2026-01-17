"""
Simple translation manager for handling language switching.
"""

from PyQt6 import QtCore, QtWidgets
import os


class TranslationManager:
    """Manages application translations."""
    
    def __init__(self, i18n_dir: str = "i18n", default_language: str = "en"):
        self.i18n_dir = i18n_dir
        self.current_language = default_language
        self.translators = []
    
    def set_language(self, language_code: str) -> bool:
        """Switch to a different language."""
        app = QtWidgets.QApplication.instance()
        
        # Remove existing translators
        for translator in self.translators:
            app.removeTranslator(translator)
        self.translators.clear()
        
        # Load new translator
        translator = QtCore.QTranslator()
        qm_file = os.path.join(self.i18n_dir, f"{language_code}.qm")
        
        if translator.load(qm_file):
            app.installTranslator(translator)
            self.translators.append(translator)
            self.current_language = language_code
            app.sendEvent(app, QtCore.QEvent(QtCore.QEvent.Type.LanguageChange))
            return True
        return False
    
    def get_available_languages(self):
        """Get list of available language codes."""
        languages = []
        if os.path.exists(self.i18n_dir):
            for filename in os.listdir(self.i18n_dir):
                if filename.endswith('.qm'):
                    languages.append(filename[:-3])
        return sorted(languages)
    
    def get_language_name(self, code: str) -> str:
        """Get display name for a language code."""
        names = {'en': 'English', 'nl': 'Nederlands'}
        return names.get(code, code.upper())
