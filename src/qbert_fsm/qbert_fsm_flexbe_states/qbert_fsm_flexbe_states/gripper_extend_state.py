#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import GripperState

class GripperExtendState(EventState):
    """
    State for extending and retracting the gripper

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- id               Motor which should be moved
    -- extended         Whether the gripper should be extended or retracted
    -- gripper_topic         Topic for motor setup

    Outputs
    <= gripper_moved        Successfully stopped
    <= failed              Failed for some reason
    """

    def __init__(self, id,
                 extended=False,
                 gripper_topic="/esp/gripper_state"):
        super().__init__(outcomes=['gripper_moved', 'failed'],
                         input_keys=[],
                         output_keys=[])
        
        self._id = id
        self._extended = extended
        self._gripper_topic = gripper_topic

        ProxyServiceCaller.initialize(GripperExtendState._node)

        self._setup_client = ProxyServiceCaller(
            {self._gripper_topic: GripperState},
            wait_duration=0.0
        )

    def execute(self, userdata):
        request = GripperState.Request()
        request.id = self._id
        request.state = self._extended

        result = self._setup_client.call(self._gripper_topic, request)

        if not result.success:
            return 'failed'
        
        return 'gripper_moved'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass
