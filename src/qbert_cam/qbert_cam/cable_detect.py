import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.action import ActionServer, CancelResponse
from rclpy.action.server import ServerGoalHandle, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.task import Future

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from qbert_msgs.action import CableDetect

import numpy as np

from threading import Lock


class CableDetector(Node):
    def __init__(self):
        super().__init__("CableDetector_Node")

        self._bridge = CvBridge()
        self._cb_group = ReentrantCallbackGroup()
        self._active_goal = None
        self._future = None
        self._min_dist = 150
        self._max_dist = 300
        self._lock = Lock()
        self._shutdown = False

        self.create_subscription(
            Image,
            "/camera/camera/depth/image_rect_raw",
            self._process_frame,
            qos_profile_sensor_data,
            callback_group=self._cb_group
        )

        self._action = ActionServer(
            self,
            CableDetect,
            "/detect_cable",
            self._handle_goal,
            cancel_callback=self._cancel_callback,
            goal_callback=self._goal_callback,
            callback_group=self._cb_group
        )

        self.get_logger().info("Cable Detector Node initiated")

    def _goal_callback(self, goal_handle: ServerGoalHandle):
        with self._lock:
            if (self._active_goal):
                return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle: ServerGoalHandle):
        with self._lock:
            if self._future and not self._future.done():
                self._future.set_result(CableDetect.Result(success=False))

        return CancelResponse.ACCEPT

    async def _handle_goal(self, goal_handle: ServerGoalHandle):
        with self._lock:
            self._active_goal = goal_handle
            self._future = Future()

        self.get_logger().info("Started handling goal")

        result = await self._future
        if goal_handle.is_cancel_requested:
            goal_handle.canceled()
        elif goal_handle.is_active:
            goal_handle.succeed()

        with self._lock:
            self._future = None
            self._active_goal = None
        self.get_logger().info("Finished handling goal")

        return result

    def _process_frame(self, img_msg: Image):
        with self._lock:
            if not self._active_goal:
                return
            if not self._future or self._future.done():
                return
            goal = self._active_goal
            future = self._future

        image = self._bridge.imgmsg_to_cv2(img_msg)

        mask = (image >= self._min_dist) & (image <= self._max_dist)
        scaled = np.zeros_like(image, dtype=np.uint8)

        scaled[mask] = np.clip(
            (image[mask]-self._min_dist) * 255 / (self._max_dist-self._min_dist),
            0,
            255
        )
        detected = np.any(scaled[:, scaled.shape[1]//2:])

        goal.publish_feedback(CableDetect.Feedback())
        with self._lock:
            if detected and not future.done():
                future.set_result(CableDetect.Result(success=True))


def main(args=None):
    rclpy.init(args=args)
    node = CableDetector()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()


if __name__ == "__main__":
    main()
