"""
Reusable navigation bar component for PyQt.
"""

from PyQt6 import QtWidgets, QtCore, QtGui
from typing import List, Dict, Optional
from .router import Router
from .icon_utils import set_button_icon
import os


class Navbar(QtWidgets.QFrame):
    """
    Reusable navigation bar widget.
    
    Usage:
        navbar = Navbar(router, [
            {'name': 'home', 'icon': 'home.png', 'label': 'Home'},
            {'name': 'debug', 'icon': 'debug.png', 'label': 'Debug'},
            {'name': 'settings', 'icon': 'settings.png', 'label': 'Settings'},
        ])
    """
    
    def __init__(
        self,
        router: Router,
        routes: List[Dict[str, str]],
        parent: Optional[QtWidgets.QWidget] = None
    ):
        """
        Initialize navbar.
        
        Args:
            router: Router instance to use for navigation
            routes: List of route configs, each with 'name', 'icon', and 'label'
            parent: Parent widget
        """
        super().__init__(parent)
        self.router = router
        self.routes = routes
        self.buttons: Dict[str, QtWidgets.QPushButton] = {}
        
        # Connect to router's route change callback
        self.router.on_route_change = self._on_route_changed
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the navbar UI."""
        # Set minimum height for navbar (matching old navbar height)
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
        
        # Set object name for styling
        self.setObjectName("navbar")
        
        # Set a subtle background to distinguish the navbar
        # QFrame supports background-color and borders better than QWidget
        self.setStyleSheet("""
            #navbar {
                background-color: #F5F5F5;
                border-top: 1px solid #000000;
            }
        """)
        
        # Create horizontal layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create button for each route
        for route_config in self.routes:
            route_name = route_config['name']
            icon_path = route_config.get('icon', '')
            label = route_config.get('label', route_name.capitalize())
            
            button = QtWidgets.QPushButton()
            button.setObjectName(f"nav{route_name.capitalize()}Button")
            button.setMinimumHeight(80)
            button.setMaximumHeight(80)
            
            # Set icon if provided
            if icon_path:
                set_button_icon(button, icon_path, size=24, position="top")
                # Update text label if it was created by set_button_icon
                if hasattr(button, '_text_label'):
                    button._text_label.setText(label)
                else:
                    button.setText(label)
            else:
                button.setText(label)
            
            # Connect button to router
            button.clicked.connect(lambda checked, name=route_name: self.router.navigate(name))
            
            # Store button reference
            self.buttons[route_name] = button
            
            # Add to layout
            layout.addWidget(button)
        
        # Set default styling
        self._apply_default_styling()
        
        # Update active state based on current route
        current_route = self.router.get_current_route()
        if current_route:
            self._update_active_state(current_route)
    
    def _apply_default_styling(self):
        """Apply default styling to all buttons."""
        for button in self.buttons.values():
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: black;
                    font-size: 14px;
                }
                QPushButton:pressed {
                    background-color: #F0F0F0;
                }
            """)
    
    def _on_route_changed(self, route_name: str):
        """Called when router navigates to a new route."""
        self._update_active_state(route_name)
    
    def _update_active_state(self, active_route: str):
        """Update button styles to show active route."""
        from PyQt6 import QtGui
        
        # Reset all buttons to inactive style
        for route_name, button in self.buttons.items():
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: black;
                    font-size: 14px;
                }
                QPushButton:pressed {
                    background-color: #F0F0F0;
                }
            """)
            # Remove bold from text label if it exists
            if hasattr(button, '_text_label'):
                font = button._text_label.font()
                font.setBold(False)
                button._text_label.setFont(font)
        
        # Set active button style
        if active_route in self.buttons:
            button = self.buttons[active_route]
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #5C6BC0;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:pressed {
                    background-color: #F0F0F0;
                }
            """)
            # Set bold on text label if it exists
            if hasattr(button, '_text_label'):
                font = button._text_label.font()
                font.setBold(True)
                button._text_label.setFont(font)
    
    def retranslate(self):
        """Retranslate navbar labels (for i18n support)."""
        for route_config in self.routes:
            route_name = route_config['name']
            label = route_config.get('label', route_name.capitalize())
            
            if route_name in self.buttons:
                button = self.buttons[route_name]
                if hasattr(button, '_text_label'):
                    button._text_label.setText(label)
                else:
                    button.setText(label)
