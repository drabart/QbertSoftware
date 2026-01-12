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
    -- id               Motor which should be moved
    -- topic               Topic for setting the id's velocity

    Outputs
    <= done                Successfully set the velocity
    <= failed              Failed for some reason
    """

    def __init__(self, id, topic="/odesc/reboot"):
        super().__init__(outcomes=['done', 'failed'],
                         input_keys=[],
                         output_keys=[])
        
        self._topic = topic
        self._id = id

        ProxyServiceCaller.initialize(MotorRebootState._node)

        self._client = ProxyServiceCaller({self._topic: Motor},
                                            wait_duration=0.0)

    def execute(self, userdata):
        id_goal = Motor.Request()
        id_goal.id = self._id

        result = self._client.call(self._topic, id_goal)

        if not result.success:
            return 'failed'
        
        return 'done'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass
