#!/usr/bin/env python

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyServiceCaller

from qbert_msgs.srv import SetupDrive
from qbert_msgs.srv import Motor

class SetMotorStateState(EventState):
    """
    State implementing state setup

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- motor               Motor which should be moved
    -- desired_state       State to which motor should be set ['homing', 'inactive', 'position', 'velocity']
    -- homing_topic        Topic for homing the motor
    -- setup_topic         Topic for selecting the control type
    -- motor_arm_topic     Topic for arming the motor

    Outputs
    <= state_set           State has been set
    <= failed              Failed for some reason.
    """

    def __init__(self, motor, desired_state, homing_topic="/home_motor", setup_topic="/setup_drive", motor_arm_topic="/motor_ready"):
        # See example_state.py for basic explanations.
        super().__init__(outcomes=['move_complete', 'failed'],
                         input_keys=[],
                         output_keys=['failed'])
        
        self._homing_topic = homing_topic
        self._setup_topic = setup_topic
        self._motor_arm_topic = motor_arm_topic
        self._motor = motor
        self._desired_state = desired_state

        # Create the action client when building the behavior.
        # Using the proxy client provides asynchronous access to the result and status
        # and makes sure only one client is used, no matter how often this state is used in a behavior.
        ProxyServiceCaller.initialize(SetMotorStateState._node)

        self._homing_client = ProxyServiceCaller({self._homing_topic: Motor},
                                                wait_duration=0.0)
        self._state_client = ProxyServiceCaller({self._setup_topic: SetupDrive},
                                                wait_duration=0.0)
        self._motor_arm_client = ProxyServiceCaller({self._motor_arm_topic: Motor},
                                                wait_duration=0.0)

        # It may happen that the action client fails to send the action goal.
        self._error = False
        self._return = None  # Retain return value in case the outcome is blocked by operator

    def execute(self, userdata):
        # Check if the client failed to send the goal.
        if self._error:
            return 'failed'

        if self._return is not None:
            # Return prior outcome in case transition is blocked by autonomy level
            return self._return

        # Check if the action has been finished
        if self._client.has_result(self._topic):
            _ = self._client.get_result(self._topic)  # The delta result value is not useful here
            userdata.duration = self._node.get_clock().now() - self._start_time
            Logger.loginfo('Move complete')
            self._return = 'move_complete'
            return self._return

        # If the action has not yet finished, no outcome will be returned and the state stays active.
        return None

    def on_enter(self, userdata):
        # make sure to reset the error state since a previous state execution might have failed
        self._error = False
        self._return = None

        motor_goal = Motor.Goal()
        motor_goal.motor = self._motor

        match self._desired_state:
            case 'homing':
                try:
                    self._homing_client.send_goal(self._homing_topic, motor_goal, wait_duration=1.0)
                except Exception as exc:
                    Logger.logwarn(f"Failed to send:\n  {type(exc)} - {exc}")
                    self._error = True
            case 'inactive':
                goal = SetupDrive.Goal()
                goal.motor = self._motor
                goal.mode = 0
                try:
                    self._state_client.send_goal(self._state_client, goal, wait_duration=1.0)
                except Exception as exc:
                    Logger.logwarn(f"Failed to send:\n  {type(exc)} - {exc}")
                    self._error = True
            case 'position':
                goal = SetupDrive.Goal()
                goal.motor = self._motor
                goal.mode = 1
                try:
                    self._motor_arm_client.send_goal(self._motor_arm_topic, motor_goal, wait_duration=1.0)
                    self._state_client.send_goal(self._state_client, goal, wait_duration=1.0)
                except Exception as exc:
                    Logger.logwarn(f"Failed to send:\n  {type(exc)} - {exc}")
                    self._error = True
            case 'velocity':
                goal = SetupDrive.Goal()
                goal.motor = self._motor
                goal.mode = 2
                try:
                    self._motor_arm_client.send_goal(self._motor_arm_topic, motor_goal, wait_duration=1.0)
                    self._state_client.send_goal(self._state_client, goal, wait_duration=1.0)
                except Exception as exc:
                    Logger.logwarn(f"Failed to send:\n  {type(exc)} - {exc}")
                    self._error = True
            case _:
                self._error = True
                return

    def on_exit(self, userdata):
        pass
