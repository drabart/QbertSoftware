import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String, Float64, Empty
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

class RosWorker(QObject):
    position_adjust_message_received = pyqtSignal()
    confirm_request_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        rclpy.init()
        self.node = Node("pyqt_ros_node")
        self.publishers = {}

        self.node.create_subscription(
            Empty,
            "/gui/request_position_adjust",
            self.position_adjust_callback,
            10
        )
        self.node.create_subscription(
            String,
            "/gui/request_confirm",
            self.request_confirm_callback,
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

    def request_confirm_callback(self, msg):
        self.confirm_request_received.emit(msg.data)

    def position_adjust_callback(self, msg):
        self.position_adjust_message_received.emit()

    def spin(self):
        rclpy.spin(self.node)

    def shutdown(self):
        self.node.destroy_node()
        rclpy.shutdown()
        