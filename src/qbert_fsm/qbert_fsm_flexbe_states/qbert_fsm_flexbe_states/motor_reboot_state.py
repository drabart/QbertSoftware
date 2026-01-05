#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import Motor

class MotorRebootState(EventState):
    """
    State implementing target velocity movement

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- motor               Motor which should be moved
    -- topic               Topic for setting the motor's velocity

    Outputs
    <= done                Successfully set the velocity
    <= failed              Failed for some reason
    """

    def __init__(self, motor, topic="/reboot_motor"):
        super().__init__(outcomes=['done', 'failed'],
                         input_keys=[],
                         output_keys=[])
        
        self._topic = topic
        self._motor = motor

        ProxyServiceCaller.initialize(MotorRebootState._node)

        self._client = ProxyServiceCaller({self._topic: Motor},
                                            wait_duration=0.0)

    def execute(self, userdata):
        motor_goal = Motor.Request()
        motor_goal.motor = self._motor

        result = self._client.call(self._topic, motor_goal)

        if not result.success:
            return 'failed'
        
        return 'done'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass
