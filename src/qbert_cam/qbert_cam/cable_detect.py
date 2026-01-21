import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.action import ActionServer, CancelResponse
from rclpy.action.server import ServerGoalHandle, GoalResponse
from rclpy.task import Future

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from qbert_msgs.action import CableDetect

import numpy as np
import cv2 as cv

from threading import Lock


class CableDetector(Node):
    def __init__(self):
        super().__init__("CableDetector_Node")

        self._bridge = CvBridge()
        self._active_goal = None
        self._min_dist = 100
        self._max_dist = 300
        self._lock = Lock()
        self._detected = False
        self._display_img = None

        self.create_subscription(
            Image,
            "/camera/camera/depth/image_rect_raw",
            self._process_frame,
            qos_profile_sensor_data
        )

        self._action = ActionServer(
            self,
            CableDetect,
            "/detect_cable",
            execute_callback=self._execute_callback,
            cancel_callback=self._cancel_callback,
            goal_callback=self._goal_callback,
        )

        self.create_timer(
            0.05,
            self._show_img
        )
        self.get_logger().info("Cable Detector Node initiated")

    def _show_img(self):
        if self._display_img is not None:
            cv.imshow("img", self._display_img)
            cv.waitKey(1)

    def _goal_callback(self, goal_handle: ServerGoalHandle):
        with self._lock:
            if self._active_goal is not None:
                return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle: ServerGoalHandle):
        return CancelResponse.ACCEPT

    async def _execute_callback(self, goal_handle: ServerGoalHandle):
        with self._lock:
            self._active_goal = goal_handle
            self._detected = False

        future = Future()
        self._execute_timer = self.create_timer(
            0.05,
            lambda: self._feedback(goal_handle, future)
        )

        try:
            result = await future
        except Exception:
            goal_handle.abort()
            with self._lock:
                self._active_goal = None
            return CableDetect.Result(success=False)

        with self._lock:
            self._active_goal = None

        self._execute_timer.cancel()
        if future.cancelled():
            goal_handle.canceled()
            return CableDetect.Result(success=False)

        goal_handle.succeed()
        return result

    def _feedback(self, goal_handle: ServerGoalHandle, future: Future):
        if goal_handle.is_cancel_requested:
            future.cancel()
            return
        with self._lock:
            detected = self._detected

        if detected:
            future.set_result(CableDetect.Result(success=True))
            return

        goal_handle.publish_feedback(CableDetect.Feedback())

    def _process_frame(self, img_msg: Image):
        with self._lock:
            if self._active_goal is None:
                return

        orig = self._bridge.imgmsg_to_cv2(img_msg)
        image = orig[150:290, 415:475]

        mask = (image >= self._min_dist) & (image <= self._max_dist)
        scaled = np.zeros_like(image, dtype=np.uint8)

        scaled[mask] = np.clip(
            (image[mask]-self._min_dist) * 255 / (self._max_dist-self._min_dist),
            0,
            255
        )
        scaled[~mask] = 0
        final = cv.erode(scaled, cv.getStructuringElement(cv.MORPH_RECT, (9, 9)))

        self._display_img = final
        detected = np.any(final)

        if detected:
            with self._lock:
                self._detected = True


def main(args=None):
    rclpy.init(args=args)
    node = CableDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv.destroyAllWindows()
        node.destroy_node()


if __name__ == "__main__":
    main()
