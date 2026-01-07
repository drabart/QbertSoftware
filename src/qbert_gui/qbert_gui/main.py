import os, sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String, Float64
from PyQt6.QtCore import QObject, pyqtSignal, QtWidgets, uic, QtCore, QThread, pyqtSlot

class RosWorker(QObject):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        rclpy.init()
        self.node = Node("pyqt_ros_node")
        self.publishers = {}

    def get_publisher(self, topic, msg_type):
        if topic not in self.publishers:
            self.publishers[topic] = self.node.create_publisher(
                msg_type, topic, 10
            )
        return self.publishers[topic]
    
    @pyqtSlot(str, bool)
    def publish_bool(self, topic, value):
        msg = Bool()
        msg.data = value
        self.get_publisher(topic, Bool).publish(msg)

    @pyqtSlot(str, float)
    def publish_float(self, topic, value):
        msg = Float64()
        msg.data = value
        self.get_publisher(topic, Float64).publish(msg)

    @pyqtSlot(str, str)
    def publish_float(self, topic, value):
        msg = String()
        msg.data = value
        self.get_publisher(topic, String).publish(msg)

    def callback(self, msg):
        self.message_received.emit(msg.data)

    def spin(self):
        rclpy.spin(self.node)

    def shutdown(self):
        self.node.destroy_node()
        rclpy.shutdown()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_ros_worker()

    def load_ui(self):
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

    def setup_ros_worker(self):
        ros_thread = QThread()
        ros_worker = RosWorker()

        ros_worker.moveToThread(ros_thread)
        ros_thread.started.connect(ros_worker.spin)

        ros_thread.start()

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
    exit_code = app.exec()
    sys.exit(exit_code)
