#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import Motor

class MotorHomeState(EventState):
    """
    State homing the motor

    Parameters
    -- id               Motor which should be moved
    -- homing_topic     Topic for homing the id

    Outcomes
    <= homed            Set state successfully
    <= failed           Setting failed
    """

    def __init__(self, id, homing_topic="/odesc/home"):
        super().__init__(
            outcomes=['state_set', 'failed'],
            input_keys=[],
            output_keys=[],
        )

        self._id = id
        self._homing_topic = homing_topic

        ProxyServiceCaller.initialize(MotorHomeState._node)

        self._homing_client = ProxyServiceCaller(
            {self._homing_topic: Motor},
            wait_duration=0.0,
        )

    def _call_service(self, client, topic, request, name):
        """Helper to call a service and check its result."""
        try:
            response = client.call(topic, request)
        except Exception as exc:
            Logger.logwarn(f"{name} service call failed: {type(exc)} - {exc}")
            return None

        if not response.success:
            Logger.logwarn(f"{name} service reported failure")
            return None

        return response

    def execute(self, userdata):
        id_req = Motor.Request()
        id_req.id = self._id

        if not self._call_service(
            self._homing_client,
            self._homing_topic,
            id_req,
            "Homing",
        ):
            return 'failed'

        return 'state_set'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass

