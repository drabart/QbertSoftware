#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import SetupDrive
from qbert_msgs.srv import Motor

class SetMotorStateState(EventState):
    """
    State implementing motor state setup.

    Parameters
    -- motor               Motor which should be moved
    -- desired_state       ['homing', 'inactive', 'position', 'velocity']
    -- homing_topic        Topic for homing the motor
    -- setup_topic         Topic for selecting the control type
    -- motor_arm_topic     Topic for arming the motor

    Outcomes
    <= state_set
    <= failed
    """

    MODE_MAP = {
        'inactive': 0,
        'position': 1,
        'velocity': 2,
    }

    def __init__(self, motor, desired_state,
        homing_topic="/home_motor",
        setup_topic="/setup_drive",
        motor_arm_topic="/motor_ready",
    ):
        super().__init__(
            outcomes=['state_set', 'failed'],
            input_keys=[],
            output_keys=[],
        )

        self._motor = motor
        self._desired_state = desired_state

        self._homing_topic = homing_topic
        self._setup_topic = setup_topic
        self._motor_arm_topic = motor_arm_topic

        ProxyServiceCaller.initialize(SetMotorStateState._node)

        self._homing_client = ProxyServiceCaller(
            {self._homing_topic: Motor},
            wait_duration=0.0,
        )
        self._state_client = ProxyServiceCaller(
            {self._setup_topic: SetupDrive},
            wait_duration=0.0,
        )
        self._motor_arm_client = ProxyServiceCaller(
            {self._motor_arm_topic: Motor},
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
        motor_req = Motor.Request()
        motor_req.motor = self._motor

        # --- HOMING ---
        if self._desired_state == 'homing':
            if not self._call_service(
                self._homing_client,
                self._homing_topic,
                motor_req,
                "Homing",
            ):
                return 'failed'

            return 'state_set'

        # --- OTHER MODES ---
        if self._desired_state not in self.MODE_MAP:
            Logger.logwarn(f"Unknown motor state: {self._desired_state}")
            return 'failed'

        # Arm motor first (position / velocity / inactive)
        if not self._call_service(
            self._motor_arm_client,
            self._motor_arm_topic,
            motor_req,
            "Motor arm",
        ):
            return 'failed'

        setup_req = SetupDrive.Request()
        setup_req.motor = self._motor
        setup_req.mode = self.MODE_MAP[self._desired_state]

        if not self._call_service(
            self._state_client,
            self._setup_topic,
            setup_req,
            "Setup drive",
        ):
            return 'failed'

        return 'state_set'

    def on_enter(self, userdata):
        pass

    def on_exit(self, userdata):
        pass

