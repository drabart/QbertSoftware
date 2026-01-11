"""
Simple utility for loading PNG icons.
"""

from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtWidgets import QPushButton, QLabel, QVBoxLayout
import os


def set_button_icon(button: QPushButton, icon_path: str, size: int = 24, position: str = "top"):
    """
    Set a PNG icon on a button. For "top" position, creates a custom layout with icon above text.
    
    Args:
        button: QPushButton to set icon on
        icon_path: Path to PNG file (relative to assets/ or absolute)
        size: Icon size in pixels
        position: Icon position - "top" (icon above text) or "left" (icon left of text)
    """
    # If path is relative, assume it's in assets/
    if not os.path.isabs(icon_path):
        icon_path = os.path.join("assets", icon_path)
    
    if not os.path.exists(icon_path):
        print(f"Warning: Icon file not found: {icon_path}")
        return
    
    if position == "top":
        # For stacked (icon above text), create a vertical layout inside the button
        button_text = button.text()
        
        # Clear button text - we'll add it back in the layout
        button.setText("")
        
        # Create vertical layout for the button
        layout = QVBoxLayout(button)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Create icon label
        icon_label = QLabel()
        pixmap = QtGui.QPixmap(icon_path)
        scaled_pixmap = pixmap.scaled(size, size, 
                                     QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                     QtCore.Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        # Create text label
        text_label = QLabel(button_text)
        text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("background: transparent; border: none;")
        
        # Copy font from button to text label
        font = button.font()
        text_label.setFont(font)
        
        # Add to layout
        layout.addWidget(icon_label, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # Store references for later access (e.g., retranslation)
        button._icon_label = icon_label
        button._text_label = text_label
        
    else:
        # For "left" position, use standard QPushButton icon
        icon = QtGui.QIcon(icon_path)
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(size, size))
