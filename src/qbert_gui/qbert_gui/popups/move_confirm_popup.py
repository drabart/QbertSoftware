from PyQt6.QtWidgets import QMessageBox

class ConfirmStartDialog(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setIcon(QMessageBox.Icon.Warning)
        self.setWindowTitle(self.tr("Confirm Start"))
        self.setText(self.tr("Warning: Moving the Robot"))
        self.setInformativeText(
            self.tr(
                "The action you selected will cause the robot to move.\n\n"
                "Make sure the robot is ready to be started."
            )
        )
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.setDefaultButton(QMessageBox.StandardButton.No)
