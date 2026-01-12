#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import SetupDrive
from qbert_msgs.srv import Motor

class SetMotorStateState(EventState):
    """
    State implementing id state setup.

    Parameters
    -- id               Motor which should be moved
    -- desired_state       ['homing', 'inactive', 'position', 'velocity']
    -- homing_topic        Topic for homing the id
    -- setup_topic         Topic for selecting the control type
    -- id_arm_topic     Topic for arming the id

    Outcomes
    <= state_set
    <= failed
    """

    MODE_MAP = {
        'inactive': 0,
        'position': 1,
        'velocity': 2,
    }

    def __init__(self, id, desired_state,
        homing_topic="/odesc/home",
        setup_topic="/odesc/setup",
        id_arm_topic="/odesc/ready",
    ):
        super().__init__(
            outcomes=['state_set', 'failed'],
            input_keys=[],
            output_keys=[],
        )

        self._id = id
        self._desired_state = desired_state

        self._homing_topic = homing_topic
        self._setup_topic = setup_topic
        self._id_arm_topic = id_arm_topic

        ProxyServiceCaller.initialize(SetMotorStateState._node)

        self._homing_client = ProxyServiceCaller(
            {self._homing_topic: Motor},
            wait_duration=0.0,
        )
        self._state_client = ProxyServiceCaller(
            {self._setup_topic: SetupDrive},
            wait_duration=0.0,
        )
        self._id_arm_client = ProxyServiceCaller(
            {self._id_arm_topic: Motor},
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

        # --- HOMING ---
        if self._desired_state == 'homing':
            if not self._call_service(
                self._homing_client,
                self._homing_topic,
                id_req,
                "Homing",
            ):
                return 'failed'

            return 'state_set'

        # --- OTHER MODES ---
        if self._desired_state not in self.MODE_MAP:
            Logger.logwarn(f"Unknown id state: {self._desired_state}")
            return 'failed'

        setup_req = SetupDrive.Request()
        setup_req.id = self._id
        setup_req.mode = self.MODE_MAP[self._desired_state]

        if not self._call_service(
            self._state_client,
            self._setup_topic,
            setup_req,
            "Setup drive",
        ):
            Logger.logwarn(f"Failed setup drive")
            return 'failed'

        Logger.logwarn(f"Setup done successfully")
        return 'state_set'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass

