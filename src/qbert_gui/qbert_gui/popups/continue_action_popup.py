from PyQt6.QtWidgets import QMessageBox

class ConfirmContinueDialog(QMessageBox):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)

        self.move(300, 100)

        self.setIcon(QMessageBox.Icon.Warning)
        self.setWindowTitle(self.tr("Confirm Continue"))
        self.setText(self.tr("Warning: Performing next action"))
        self.setInformativeText(
            self.tr(
                text
            )
        )
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.setDefaultButton(QMessageBox.StandardButton.No)
