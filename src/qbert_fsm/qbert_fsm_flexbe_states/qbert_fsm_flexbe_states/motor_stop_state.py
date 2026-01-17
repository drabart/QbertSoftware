#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import MotorSetup

class MotorStopState(EventState):
    """
    State stopping the motor

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- id               Motor which should be moved
    -- setup_topic         Topic for motor setup

    Outputs
    <= motor_stopped        Successfully stopped
    <= failed              Failed for some reason
    """

    def __init__(self, id,
                 setup_topic="/odesc/setup"):
        super().__init__(outcomes=['motor_stopped', 'failed'],
                         input_keys=[],
                         output_keys=[])
        
        self._id = id
        self._setup_topic = setup_topic

        ProxyServiceCaller.initialize(MotorStopState._node)

        self._setup_client = ProxyServiceCaller(
            {self._setup_topic: MotorSetup},
            wait_duration=0.0
        )

    def execute(self, userdata):
        request = MotorSetup.Request()
        request.id = self._id
        request.mode = MotorSetup.Request.MODE_IDLE

        result = self._setup_client.call(self._setup_topic, request)

        if not result.success:
            return 'failed'
        
        return 'motor_stopped'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass
