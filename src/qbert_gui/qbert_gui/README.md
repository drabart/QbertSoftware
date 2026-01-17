# Qbert GUI - Simple PyQt6 Architecture

Simple, modular GUI architecture for PyQt6 running on Rock 4D SBC touchscreen.

## Structure

```
gui/
├── core/
│   ├── base_screen.py          # Base class for screens
│   └── translation_manager.py   # Handles i18n (English/Dutch)
├── screens/                     # Screen implementations
│   ├── home_screen.py
│   ├── settings_screen.py
│   └── debug_screen.py
├── ui/                          # Qt Designer UI files
├── i18n/                        # Translation files (.ts, .qm)
├── themes/                      # QSS style sheets
└── main.py                      # Application entry point
```

## Key Components

### BaseScreen (`core/base_screen.py`)

Simple base class that:
- Loads UI files
- Provides `display_robot_log()` for showing robot messages
- Handles translation retranslation

### TranslationManager (`core/translation_manager.py`)

Simple translation manager:
- Loads `.qm` files
- Switches languages
- Supports English and Dutch

### MainWindow (`main.py`)

Main application:
- Manages screens with QStackedWidget
- Connects buttons directly to handler methods
- Handles navigation between screens
- Displays robot logs

## Adding a New Screen

1. **Create UI file** in Qt Designer → `ui/my_screen.ui`

2. **Create screen class**:
   ```python
   # screens/my_screen.py
   from core.base_screen import BaseScreen
   
   class MyScreen(BaseScreen):
       def __init__(self, parent=None):
           super().__init__("my_screen.ui", parent)
       
       def setup_ui(self):
           pass  # Connect widgets if needed
   ```

3. **Add to main.py**:
   ```python
   from screens.my_screen import MyScreen
   
   # In __init__:
   self.my_screen = MyScreen(self)
   self.screens['my_screen'] = self.stack.addWidget(self.my_screen)
   
   # Add navigation:
   self.some_button.clicked.connect(lambda: self.navigate('my_screen'))
   ```

## Adding Button Commands

Connect buttons directly to handler methods in `main.py`:

```python
# In _connect_commands():
if hasattr(self.home_screen, 'myButton'):
    self.home_screen.myButton.clicked.connect(self.handle_my_command)

# Add handler method:
def handle_my_command(self):
    # Your logic here
    pass
```

## Displaying Robot Logs

When receiving log messages from the robot:

```python
# From external code (CAN, serial, etc.):
window.display_robot_log("Robot status: Ready", "home")
```

The log appears in the `logText` QTextEdit widget in the specified screen.

## Internationalization

1. **Mark strings** in UI files with `tr("Text")`

2. **Extract strings**:
   ```bash
   ./scripts/extract_text.sh
   ```

3. **Translate** in `i18n/nl.ts`

4. **Compile**:
   ```bash
   ./scripts/generate_localization.sh
   ```

## Running

```bash
cd test_software/gui
python main.py
```

## That's It!

The architecture is intentionally simple:
- Screens load UI files
- Buttons connect directly to methods
- Navigation uses QStackedWidget
- Translation is handled automatically
- Robot logs are displayed directly

No complex managers or abstractions - just what you need.
