#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
import urdf_parser_py.urdf as urdf

from sensor_msgs.msg import JointState
from qbert_msgs.msg import LimitSwitch

class LimitSwitchMock(Node):
    joints = {}

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.robot = None

        self.declare_parameter('robot_description', '')
        self.declare_parameter(
            'limit_switch_joints', ['']
        )

        self.read_joint_limits()
        self.start_joint_state_subscription()

        self.limit_pub = self.create_publisher(LimitSwitch, 'limit_switch', 10)
        self.timer = self.create_timer(0.2, self.publish_limit_switches)

    def read_joint_limits(self):
        limit_switch_joints = self.get_parameter('limit_switch_joints').get_parameter_value().string_array_value

        robot_desc = self.get_parameter('robot_description').get_parameter_value().string_value
        if robot_desc:
            self.robot = urdf.URDF.from_xml_string(robot_desc)
            self.get_logger().info("Loaded URDF and joint limits:")
            for joint in self.robot.joints:
                if joint.limit and joint.name in limit_switch_joints:
                    lower = joint.limit.lower
                    upper = joint.limit.upper

                    # compute 99% thresholds, handling negative limits
                    lower_thresh = lower * 0.99 if lower >= 0 else lower * 1.01
                    upper_thresh = upper * 0.99 if upper >= 0 else upper * 1.01

                    self.joints[joint.name] = {
                        "lower": lower,
                        "upper": upper,
                        "lower_thresh": lower_thresh,
                        "upper_thresh": upper_thresh,
                        "position": 0.0,
                    }

                    self.get_logger().debug(
                        f'{joint.name}: lower={lower}, upper={upper}, '
                        f'lower_thresh={lower_thresh}, upper_thresh={upper_thresh}'
                    )
        else:
            self.get_logger().error("No urdf to load")

    def start_joint_state_subscription(self):
        self.subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            10)
        self.subscription  # prevent unused variable warning

    def publish_limit_switches(self):
        for (name, joint) in self.joints.items():
            if joint["position"] < joint["lower_thresh"]: 
                self.get_logger().debug('lower thresh: "%s: %f"' % (name, joint["position"]))

                switch_msg = LimitSwitch()
                switch_msg.sensor_id = f"lower_{name}"
                switch_msg.triggered = True

                self.limit_pub.publish(switch_msg)

            if joint["position"] > joint["upper_thresh"]:
                self.get_logger().debug('upper thresh: "%s: %f"' % (name, joint["position"]))

                switch_msg = LimitSwitch()
                switch_msg.sensor_id = f"upper_{name}"
                switch_msg.triggered = True

                self.limit_pub.publish(switch_msg)

    def joint_state_callback(self, msg):
        for name, position in zip(msg.name, msg.position):
            if name in self.joints:
                self.joints[name]['position'] = position
                

def main(args=None):
    rclpy.init(args=args)
    node = LimitSwitchMock()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
