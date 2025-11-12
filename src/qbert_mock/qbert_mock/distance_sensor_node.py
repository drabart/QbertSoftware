#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import urdf_parser_py.urdf as urdf

from sensor_msgs.msg import JointState
from qbert_msgs.msg import DistanceSensor

class DistanceSensorMock(Node):
    joints = {}

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.robot = None

        self.declare_parameter(
            'distance_sensor_joints', ['']
        )

        distance_sensor_joints = self.get_parameter('distance_sensor_joints').get_parameter_value().string_array_value
        for name in distance_sensor_joints:
            self.joints[name] = {"position": 0.0}

        self.start_joint_state_subscription()

        self.distance_pub = self.create_publisher(DistanceSensor, 'distance_sensor', 10)
        self.timer = self.create_timer(0.2, self.publish_distance_sensors)

        self.get_logger().info('Distance sensors initialized')

    def start_joint_state_subscription(self):
        self.subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            10)
        self.subscription  # prevent unused variable warning

    def publish_distance_sensors(self):
        for (name, joint) in self.joints.items():
            self.get_logger().debug('position: "%s: %f"' % (name, joint["position"]))

            switch_msg = DistanceSensor()
            switch_msg.sensor_id = name
            switch_msg.distance = joint["position"]

            self.distance_pub.publish(switch_msg)

    def joint_state_callback(self, msg):
        # self.get_logger().info(f'{self.joints}')
        for name, position in zip(msg.name, msg.position):
            if name in self.joints:

                self.joints[name]['position'] = position
                

def main(args=None):
    rclpy.init(args=args)
    node = DistanceSensorMock()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
