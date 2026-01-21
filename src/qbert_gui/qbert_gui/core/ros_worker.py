import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String, Float64, Empty
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

class RosWorker(QObject):
    position_adjust_received = pyqtSignal()
    confirm_received = pyqtSignal(str)
    log_received = pyqtSignal(str)
    progress_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        rclpy.init()
        self.node = Node("pyqt_ros_node")
        self.publishers = {}

        self.node.create_subscription(
            Empty,
            "/gui/request/position_adjust",
            self.position_adjust_callback,
            10
        )
        self.node.create_subscription(
            String,
            "/gui/request/confirm",
            self.confirm_callback,
            10
        )
        self.node.create_subscription(
            String,
            "/gui/request/log",
            self.log_callback,
            10
        )
        self.node.create_subscription(
            String,
            "/gui/request/progress",
            self.progress_callback,
            10
        )

        self.get_publisher("/gui/home", Empty)
        self.get_publisher("/gui/start", Empty)
        self.get_publisher("/gui/cancel", Empty)

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

    def position_adjust_callback(self, msg):
        print("Position adjust received")
        self.position_adjust_received.emit()

    def confirm_callback(self, msg):
        print(f"Confirm received {msg.data}")
        self.confirm_received.emit(msg.data)

    def log_callback(self, msg):
        print(f"Log received {msg.data}")
        self.log_received.emit(msg.data)

    def progress_callback(self, msg):
        print(f"Progress received {msg.data}")
        self.progress_received.emit(msg.data)

    def spin(self):
        rclpy.spin(self.node)

    def shutdown(self):
        self.node.destroy_node()
        rclpy.shutdown()
        