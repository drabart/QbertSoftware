"""
Reusable navigation bar component for PyQt.
"""

from PyQt6 import QtWidgets
from typing import List, Dict, Optional
from .router import Router
from .icon_utils import set_button_icon


class Navbar(QtWidgets.QFrame):
    def __init__(
        self,
        router: Router,
        routes: List[Dict[str, str]],
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        self.router = router
        self.routes = routes
        self.buttons: Dict[str, QtWidgets.QPushButton] = {}

        self.setProperty("type", "navbar")
        self.setFixedHeight(80)

        self.router.on_route_change = self._on_route_changed
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for route in self.routes:
            name = route["name"]
            label = route.get("label", name.capitalize())
            icon = route.get("icon")

            button = QtWidgets.QPushButton()
            button.setProperty("type", "navbar")
            button.setProperty("active", False)
            button.setFixedHeight(80)

            if icon:
                set_button_icon(button, icon, size=24, position="top")
                if hasattr(button, "_text_label"):
                    button._text_label.setText(label)
                    button._text_label.setProperty("type", "navbar")
                else:
                    button.setText(label)
            else:
                button.setText(label)

            button.clicked.connect(
                lambda _, r=name: self.router.navigate(r)
            )

            self.buttons[name] = button
            layout.addWidget(button)

        current = self.router.get_current_route()
        if current:
            self._update_active_state(current)

    def _on_route_changed(self, route_name: str):
        self._update_active_state(route_name)

    def _update_active_state(self, active_route: str):
        for name, button in self.buttons.items():
            is_active = name == active_route
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

            if hasattr(button, "_text_label"):
                font = button._text_label.font()
                font.setBold(is_active)
                button._text_label.setFont(font)

    def retranslate(self):
        for route in self.routes:
            name = route["name"]
            label = route.get("label", name.capitalize())
            button = self.buttons.get(name)

            if button:
                if hasattr(button, "_text_label"):
                    button._text_label.setText(label)
                else:
                    button.setText(label)
