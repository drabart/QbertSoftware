"""
Minimal router for PyQt navigation.
Similar to NextJS router but simplified - no history tracking.
"""

from PyQt6 import QtWidgets
from typing import Dict, Optional, Callable


class Router:
    """
    Simple router for managing screen navigation.
    
    Usage:
        router = Router(stacked_widget)
        router.register('home', HomeScreen(parent))
        router.register('settings', SettingsScreen(parent))
        router.navigate('home')
    """
    
    def __init__(self, stacked_widget: QtWidgets.QStackedWidget):
        """
        Initialize router with a QStackedWidget.
        
        Args:
            stacked_widget: QStackedWidget that will hold the screens
        """
        self.stack = stacked_widget
        self.routes: Dict[str, int] = {}  # route_name -> stack_index
        self.current_route: Optional[str] = None
        self.on_route_change: Optional[Callable[[str], None]] = None
    
    def register(self, route_name: str, screen: QtWidgets.QWidget) -> None:
        """
        Register a screen with a route name.
        
        Args:
            route_name: Unique name for the route (e.g., 'home', 'settings')
            screen: QWidget instance to display for this route
        """
        if route_name in self.routes:
            raise ValueError(f"Route '{route_name}' is already registered")
        
        index = self.stack.addWidget(screen)
        self.routes[route_name] = index
    
    def navigate(self, route_name: str) -> None:
        """
        Navigate to a route.
        
        Args:
            route_name: Name of the route to navigate to
        """
        if route_name not in self.routes:
            raise ValueError(f"Route '{route_name}' is not registered")
        
        index = self.routes[route_name]
        self.stack.setCurrentIndex(index)
        
        previous_route = self.current_route
        self.current_route = route_name
        
        # Call optional callback if route changed
        if self.on_route_change and previous_route != route_name:
            self.on_route_change(route_name)
    
    def get_current_route(self) -> Optional[str]:
        """Get the name of the currently active route."""
        return self.current_route
