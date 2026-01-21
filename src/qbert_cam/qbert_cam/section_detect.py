import rclpy
from rclpy.task import Future
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.action.server import ActionServer, ServerGoalHandle, GoalResponse, CancelResponse

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from qbert_msgs.action import SectionDetect

import cv2 as cv
import numpy as np
from threading import Lock


class SectionDetector(Node):
    def __init__(self):
        super().__init__("SectionDetector_Node")
        self._bridge = CvBridge()
        self._active_goal = None
        self._lock = Lock()

        self._color_img = None
        self._depth_img = None
        self._samples = 0

        self._min_dist = 100
        self._max_dist = 300

        self._display_image = None

        self.create_subscription(
            Image,
            "/camera/camera/color/image_raw",
            self._process_sample,
            qos_profile_sensor_data
        )

        self._action = ActionServer(
            self,
            SectionDetect,
            "/detect_section",
            execute_callback=self._execute_callback,
            cancel_callback=self._cancel_callback,
            goal_callback=self._goal_callback,
        )

        self.create_timer(0.03, self._show_img)

        self.get_logger().info("Section Detector Node initiated")

    def _show_img(self):
        if self._display_image is not None:
            cv.imshow("img", self._display_image)
            cv.waitKey(1)

    async def _execute_callback(self, goal_handle: ServerGoalHandle):
        with self._lock:
            self._active_goal = goal_handle
            self._samples = 0

        future = Future()
        self._execute_timer = self.create_timer(
            0.5,
            lambda: self._feedback(goal_handle, future)
        )

        try:
            result = await future
        except Exception:
            goal_handle.abort()
            with self._lock:
                self._active_goal = None
            return SectionDetect.Result(success=False)

        with self._lock:
            self._active_goal = None

        self._execute_timer.cancel()
        if future.cancelled():
            goal_handle.canceled()
            return SectionDetect.Result(success=False)

        goal_handle.succeed()
        return result

    def _feedback(self, goal_handle: ServerGoalHandle, future: Future):
        if goal_handle.is_cancel_requested:
            future.cancel()
            return
        with self._lock:
            samples = self._samples

        if samples < 10:
            return

        correct = False

        with self._lock:
            self._samples = 0

        if correct:
            future.set_result(SectionDetect.Result(success=True))
            return
        else:
            # publish feedback
            return

    def _cancel_callback(self, goal_handle: ServerGoalHandle):
        return CancelResponse.ACCEPT

    def _goal_callback(self, goal_handle: ServerGoalHandle):
        with self._lock:
            if self._active_goal:
                return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def _process_sample(self, color_img):
        with self._lock:
            if self._active_goal is None:
                return

        orig = self._bridge.imgmsg_to_cv2(color_img, desired_encoding='bgr8')
        cropped = orig[140:360, 270:430]

#       blurred = cv.GaussianBlur(cable_image, (3, 3), 0)
#       blurred = cv.bilateralFilter(cropped, 5, 75, 75)
#       grayscale = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)

#       lines = cv.Canny(grayscale, 150, 300)
#       lines_3c = cv.cvtColor(lines, cv.COLOR_GRAY2BGR)
#       grid = np.hstack((cropped, lines_3c))
        final = cropped

        self._display_image = final

        self.get_logger().info("processed sample")
        with self._lock:
            self._samples += 1


def main(args=None):
    rclpy.init(args=args)
    node = SectionDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv.destroyAllWindows()
        node.destroy_node()


if __name__ == "__main__":
    main()
