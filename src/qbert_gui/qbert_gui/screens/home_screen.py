"""Home Screen."""

import os
from PyQt6 import QtWidgets, QtCore
from qbert_gui.core.base_screen import BaseScreen
from qbert_gui.core.ros_worker import RosWorker
from qbert_gui.core.icon_utils import set_button_icon
from qbert_gui.core.shared_resource import get_from_shared
from qbert_gui.popups.offset_popup import PositionAdjustDialog
from qbert_gui.popups.continue_action_popup import ConfirmContinueDialog
from qbert_gui.popups.move_confirm_popup import ConfirmStartDialog
from PyQt6.QtWidgets import QMessageBox
from datetime import datetime
from playsound3 import playsound

class HomeScreen(BaseScreen):
    """Home screen with main controls."""
    
    def __init__(self, ros_worker: RosWorker, parent=None):
        super().__init__("home.ui", parent)
        self.ros_worker = ros_worker
        self.ros_worker.position_adjust_received.connect(self._position_adjust_callback)
        self.ros_worker.confirm_received.connect(self._confirm_request_callback)
        self.ros_worker.log_received.connect(self._log_request_callback)
        self.ros_worker.progress_received.connect(self._progress_request_callback)

        self.is_running = False  # Track robot state
    
    def setup_ui(self):
        """Setup UI connections."""
        # Connect control button (toggles between start/stop)
        if hasattr(self, 'controlButton'):
            self.controlButton.clicked.connect(self._handle_control_button)
            # Add PNG icon to control button (play icon initially)
            set_button_icon(self.controlButton, "play.png", size=24, position="top")
        
        if hasattr(self, 'homingButton'):
            self.homingButton.clicked.connect(lambda: self._show_start_movement_confirmation(self._handle_homing))
    
    def _handle_control_button(self):
        """Handle control button click - toggles between start and stop."""
        if not self.is_running:
            # Show confirmation modal before starting
            self._show_start_movement_confirmation(self._handle_start)
        else:
            # Immediately stop
            self._handle_stop()
    
    def _show_start_movement_confirmation(self, confirm_function):
        """Show confirmation modal before starting the robot."""
        
        if ConfirmStartDialog(self).exec() == QMessageBox.StandardButton.Yes:
            playsound(get_from_shared(os.path.join("assets", "beep.mp3")))
            confirm_function()

    def _position_adjust_callback(self):
        dlg = PositionAdjustDialog(self.ros_worker, self)

        dlg.exec()

    def _confirm_request_callback(self, text):
        dlg = ConfirmContinueDialog(text, self)

        response = dlg.exec()

        if response == QMessageBox.StandardButton.Yes:
            playsound(get_from_shared(os.path.join("assets", "beep.mp3")))
            self.ros_worker.publish_bool('/gui/confirm', True)
        else:
            self.ros_worker.publish_bool('/gui/confirm', False)

    def _log_request_callback(self, text):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logText.append(f"[{ts}] {text}")

    def _progress_request_callback(self, text):
        self.progressBar.setValue(int(float(text)))

    def _handle_start(self):
        """Handle start command - send start command to robot."""
        self.ros_worker.publish_empty("/gui/start")
        
        # Update UI to show stop button
        self.is_running = True
        self._update_control_button_state()
    
    def _handle_stop(self):
        """Handle stop command - immediately stop the robot."""
        
        # Update UI to show start button
        self.is_running = False
        self._update_control_button_state()
    
    def _handle_homing(self):
        """Handle homing command - implement your logic here."""
        self.ros_worker.publish_empty("/gui/home")

    def _update_control_button_state(self):
        """Update control button appearance based on robot state."""
        if not hasattr(self, 'controlButton'):
            return
        
        button = self.controlButton
        
        if self.is_running:
            # Show stop button (red)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #FF4040;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:pressed {
                    background-color: #E03030;
                    color: black;
                }
            """)
            # Update icon and text without recreating layout
            self._update_button_icon_text(button, "pause.png", self.tr("Stop"))
        else:
            # Show start button (green)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #28E87C;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:pressed {
                    background-color: #20D06C;
                    color: black;
                }
            """)
            # Update icon and text without recreating layout
            self._update_button_icon_text(button, "play.png", self.tr("Start"))

    def _update_button_icon_text(self, button, icon_path, text):
        """
        Update button icon and text without recreating the layout.
        Assumes the button already has a layout with icon and text labels.
        """
        import os
        from PyQt6 import QtGui, QtCore
        
        # If path is relative, assume it's in assets/
        if not os.path.isabs(icon_path):
            icon_path = os.path.join("assets", icon_path)
        
        # Update icon if icon label exists
        if hasattr(button, '_icon_label') and os.path.exists(icon_path):
            pixmap = QtGui.QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(24, 24, 
                                         QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                         QtCore.Qt.TransformationMode.SmoothTransformation)
            button._icon_label.setPixmap(scaled_pixmap)
        
        # Update text if text label exists
        if hasattr(button, '_text_label'):
            button._text_label.setText(text)
        else:
            # Fallback if layout doesn't exist yet
            button.setText(text)
    
    def retranslate_ui(self):
        """Retranslate UI elements."""
        if hasattr(self, 'controlButton'):
            self._update_control_button_state()
        if hasattr(self, 'homingButton'):
            self.homingButton.setText(self.tr("Homing"))
