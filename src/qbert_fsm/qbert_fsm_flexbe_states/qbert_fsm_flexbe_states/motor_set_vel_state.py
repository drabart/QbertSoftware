#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import MotorSetup
from qbert_msgs.srv import MoveWithVel

class MotorSetVelState(EventState):
    """
    State implementing target velocity movement

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- id               Motor which should be moved
    -- target_velocity     Velocity to be achieved
    -- vel_topic           Topic for setting the id's velocity
    -- setup_topic         Topic for motor setup

    Outputs
    <= velocity_set        Successfully set the velocity
    <= failed              Failed for some reason
    """

    def __init__(self, id, target_velocity=5.0, 
                 vel_topic="/odesc/move_with_velocity",
                 setup_topic="/odesc/setup"):
        super().__init__(outcomes=['velocity_set', 'failed'],
                         input_keys=[],
                         output_keys=[])
        
        self._id = id
        self._target_velocity = target_velocity
        
        self._vel_topic = vel_topic
        self._setup_topic = setup_topic

        ProxyServiceCaller.initialize(MotorSetVelState._node)

        self._client = ProxyServiceCaller(
            {self._vel_topic: MoveWithVel},
            wait_duration=0.0
        )
        self._setup_client = ProxyServiceCaller(
            {self._setup_topic: MotorSetup},
            wait_duration=0.0
        )

    def execute(self, userdata):
        request = MotorSetup.Request()
        request.id = self._id
        request.mode = MotorSetup.Request.MODE_VELOCITY

        result = self._setup_client.call(self._setup_topic, request)

        if not result.success:
            return 'failed'

        request = MoveWithVel.Request()
        request.id = self._id
        request.vel = self._target_velocity

        result = self._client.call(self._vel_topic, request)

        if not result.success:
            return 'failed'
        
        return 'velocity_set'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass
