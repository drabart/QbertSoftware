#!/usr/bin/env python

from rclpy.duration import Duration

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyActionClient

from qbert_msgs.action import CableDetect


class DetectCableState(EventState):
    """
    State implementing detection of cable

    Elements defined here for UI
    Parameters
    -- timout           Maximum time allowed (seconds)
    -- action_topic     Topic on which the action is called

    Outputs
    <= success          Cable was detected
    <= canceled         User canceled before completion
    <= timeout          The action ahs timed out
    """

    def __init__(self, timeout=-1.0, action_topic="/detect_cable"):
        super().__init__(
            outcomes=['success', 'canceled', 'timeout'],
        )
        self._timeout = Duration(seconds=timeout)
        self._timeout_sec = timeout
        self._topic = action_topic

        ProxyActionClient.initialize(DetectCableState._node)
        self._client = ProxyActionClient(
            {self._topic: CableDetect},
            wait_duration=0.0,
        )

        self._return = None
        self._start_time = None

    def execute(self, userdata):
        if self._return:
            return self._return

        now = self._node.get_clock().now()

        if self._client.has_result(self._topic):
            _ = self._client.get_result(self._topic)
            Logger.loginfo('Cable detected')
            self._return = 'success'
            return self._return

        if self._timeout_sec > 0:
            if (now - self._start_time).nanoseconds * 1e-9 >= self._timeout.nanoseconds:
                self._return = 'timeout'
                return 'timeout'

        return None

    def on_enter(self, userdata):
        self._return = None
        self._start_time = self._node.get_clock().now()
        goal = CableDetect.Goal()

        try:
            self._client.send_goal(self._topic, goal, wait_duration=self._timeout_sec)
        except Exception as e:
            Logger.logwarn(f"Failed to send CableDetect command:\n {type(e)} - {e}")

    def on_exit(self, userdata):
        if not self._client.has_result(self._topic):
            self._client.cancel(self._topic)
            Logger.loginfo("Cancelled active action goal")
