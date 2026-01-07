import sys
from PyQt6 import QtWidgets, uic, QtCore
import os

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi Screen App")

        # self.load_language(os.path.join(os.getcwd(), "i18n/nl.ts"))
        self.load_language(os.path.join("i18n", "nl.qm"))

        # Stacked layout for screens
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        # Load screens from XML (.ui)
        self.home = uic.loadUi("ui/home.ui")
        self.settings = uic.loadUi("ui/settings.ui")
        self.debug = uic.loadUi("ui/debug.ui")

        # Add to stack
        self.stack.addWidget(self.home)      # index 0
        self.stack.addWidget(self.settings)  # index 1
        self.stack.addWidget(self.debug)     # index 2

        # Connect navigation buttons
        self.home.settingsButton.clicked.connect(self.go_settings)

        self.settings.backButton.clicked.connect(self.go_home)
        self.settings.debugButton.clicked.connect(self.go_debug)

        self.debug.backButton.clicked.connect(self.go_settings)

        # Load default theme and language
        self.load_theme("themes/dark.qss")

    # Navigation
    def go_home(self):
        self.stack.setCurrentIndex(0)

    def go_settings(self):
        self.stack.setCurrentIndex(1)

    def go_debug(self):
        self.stack.setCurrentIndex(2)

    # Theme loading
    def load_theme(self, path):
        with open("themes/common.qss") as f:
            common_style = f.read()

        with open(path, "r") as f:
            theme_style = f.read()

        app.setStyleSheet(common_style + "\n" + theme_style)

    # Language loading
    def load_language(self, path):
        if not hasattr(self, "translator"):
            self.translator = QtCore.QTranslator()

        if self.translator.load(path):
            QtWidgets.QApplication.instance().installTranslator(self.translator)
        else:
            print("Failed to load:", path)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(400, 300)
    w.show()
    sys.exit(app.exec())
