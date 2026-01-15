#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import Motor
from qbert_msgs.srv import MotorGetState

class MotorHomeState(EventState):
    """
    State homing the motor

    Parameters
    -- id               Motor which should be moved
    -- timeout          Max expected homing time (-1 for no timeout)
    -- delay            Delay between state get
    -- homing_topic     Topic for homing the id
    -- get_state_topic  Topic for getting state

    Outcomes
    <= homed            Set state successfully
    <= timeout          Homing timed out
    <= failed           Setting failed
    """

    def __init__(self, id, timeout = -1, delay = 0.2,
                 homing_topic="/odesc/home",
                 get_state_topic="/odesc/get_state"):
        super().__init__(
            outcomes=['state_set', 'timeout', 'failed'],
            input_keys=[],
            output_keys=[],
        )

        self._id = id
        self._timeout = timeout
        self._delay = delay
        self._homing_topic = homing_topic
        self._get_state_topic = get_state_topic

        ProxyServiceCaller.initialize(MotorHomeState._node)

        self._homing_client = ProxyServiceCaller(
            {self._homing_topic: Motor},
            wait_duration=0.0,
        )
        self._get_state_client = ProxyServiceCaller(
            {self._get_state_topic: MotorGetState},
            wait_duration=0.0
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

    def on_enter(self, userdata):
        self._homing_sent = False
        self._start_time = self._node.get_clock().now()
        self._last_check = self._start_time

    def execute(self, userdata):
        now = self._node.get_clock().now()

        # send homing request once
        if not self._homing_sent:
            req = Motor.Request()
            req.id = self._id

            if not self._call_service(
                self._homing_client,
                self._homing_topic,
                req,
                "Homing",
            ):
                return 'failed'

            self._homing_sent = True
            self._last_check = now
            return None

        # timeout check
        if self._timeout > 0:
            elapsed = (now - self._start_time).nanoseconds * 1e-9
            if elapsed >= self._timeout:
                return 'timeout'

        # delay between state polls
        since_last = (now - self._last_check).nanoseconds * 1e-9
        if since_last < self._delay:
            return None

        self._last_check = now

        # query state
        state_req = MotorGetState.Request()
        state_req.id = self._id

        result = self._get_state_client.call(self._get_state_topic, state_req)

        if not result.exists:
            return 'failed'

        if result.state == 1:
            return 'state_set'

        return None

    def on_exit(self, userdata):
        pass

