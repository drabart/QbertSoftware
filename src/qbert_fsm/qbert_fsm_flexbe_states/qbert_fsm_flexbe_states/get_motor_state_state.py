#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import MotorState

class GetMotorStateState(EventState):
    """
    State implementing retrieving of a current motor state

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- motor               Motor which should be moved
    -- get_state_topic           Topic for setting the motor's velocity

    Outputs
    <= state_acquired        Successfully set the velocity
    <= failed              Failed for some reason

    Outputs
    #> current_state        Current state of the motor
    """

    def __init__(self, motor, get_state_topic="/get_motor_state"):
        super().__init__(outcomes=['state_acquired', 'failed'],
                         output_keys=['current_state'])
        
        self._get_state_topic = get_state_topic
        self._motor = motor

        ProxyServiceCaller.initialize(GetMotorStateState._node)

        self._client = ProxyServiceCaller({self._get_state_topic: MotorState},
                                            wait_duration=0.0)

    def execute(self, userdata):
        motor_goal = MotorState.Request()
        motor_goal.motor = self._motor

        result = self._client.call(self._vel_topic, motor_goal)

        if not result.exists:
            return 'failed'
        
        userdata.current_state = result.state
        return 'state_acquired'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass
