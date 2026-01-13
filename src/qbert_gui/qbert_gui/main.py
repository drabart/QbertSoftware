import os, sys
import rclpy
from pathlib import Path
from rclpy.node import Node
from std_msgs.msg import Bool, String, Float64, Empty
from PyQt6 import QtWidgets, uic, QtCore
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from ament_index_python.packages import get_package_share_directory

class RosWorker(QObject):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        rclpy.init()
        self.node = Node("pyqt_ros_node")
        self.publishers = {}

        self.get_publisher("/gui_home", Empty)
        self.get_publisher("/gui_start", Empty)
        self.get_publisher("/gui_cancel", Empty)

    def get_publisher(self, topic, msg_type):
        if topic not in self.publishers:
            self.publishers[topic] = self.node.create_publisher(
                msg_type, topic, 10
            )
        return self.publishers[topic]
    
    @pyqtSlot(str)
    def publish_empty(self, topic):
        msg = Empty()
        self.get_publisher(topic, Empty).publish(msg)
    
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
    def publish_string(self, topic, value):
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

SHARE_DIR = Path(get_package_share_directory("qbert_gui"))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_ros_worker()

        self.home.homingButton.clicked.connect(lambda: self.ros_worker.publish_empty("/gui_home"))
        self.home.startButton.clicked.connect(lambda: self.ros_worker.publish_empty("/gui_start"))
        self.home.stopButton.clicked.connect(lambda: self.ros_worker.publish_empty("/gui_cancel"))


    def load_ui(self):
        self.setWindowTitle("Multi Screen App")

        self.load_language(SHARE_DIR / "i18n" / "nl.qm")

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = uic.loadUi(SHARE_DIR / "ui" / "home.ui")
        self.settings = uic.loadUi(SHARE_DIR / "ui" / "settings.ui")
        self.debug = uic.loadUi(SHARE_DIR / "ui" / "debug.ui")

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.settings)
        self.stack.addWidget(self.debug)

        self.home.settingsButton.clicked.connect(self.go_settings)
        self.settings.backButton.clicked.connect(self.go_home)
        self.settings.debugButton.clicked.connect(self.go_debug)
        self.debug.backButton.clicked.connect(self.go_settings)

        self.load_theme(SHARE_DIR / "themes" / "dark.qss")

    def setup_ros_worker(self): 
        self.ros_thread = QThread(self) 
        self.ros_worker = RosWorker() 

        self.ros_worker.moveToThread(self.ros_thread) 
        self.ros_thread.started.connect(self.ros_worker.spin) 

        self.ros_thread.start()

    def load_theme(self, path):
        with open(SHARE_DIR / "themes" / "common.qss", "r") as f:
            common_style = f.read()

        with open(path, "r") as f:
            theme_style = f.read()

        app.setStyleSheet(common_style + "\n" + theme_style)

    # Navigation
    def go_home(self):
        self.stack.setCurrentIndex(0)

    def go_settings(self):
        self.stack.setCurrentIndex(1)

    def go_debug(self):
        self.stack.setCurrentIndex(2)

    def load_language(self, path):
        if not hasattr(self, "translator"):
            self.translator = QtCore.QTranslator()

        if self.translator.load(str(path)):
            QtWidgets.QApplication.instance().installTranslator(self.translator)
        else:
            print("Failed to load:", path)


def main():
    global app

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(400, 300)
    w.show()
    exit_code = app.exec()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
    