#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import MoveWithVel

class SetMotorVelState(EventState):
    """
    State implementing target velocity movement

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- id               Motor which should be moved
    -- target_velocity     Velocity to be achieved
    -- vel_topic           Topic for setting the id's velocity

    Outputs
    <= velocity_set        Successfully set the velocity
    <= failed              Failed for some reason
    """

    def __init__(self, id, target_velocity=5.0, vel_topic="/odesc/move_with_velocity"):
        super().__init__(outcomes=['velocity_set', 'failed'],
                         input_keys=[],
                         output_keys=[])
        
        self._vel_topic = vel_topic
        self._id = id
        self._target_velocity = target_velocity

        ProxyServiceCaller.initialize(SetMotorVelState._node)

        self._client = ProxyServiceCaller({self._vel_topic: MoveWithVel},
                                            wait_duration=0.0)

    def execute(self, userdata):
        id_goal = MoveWithVel.Request()
        id_goal.id = self._id
        id_goal.vel = self._target_velocity

        result = self._client.call(self._vel_topic, id_goal)

        if not result.success:
            return 'failed'
        
        return 'velocity_set'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass
