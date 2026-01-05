#!/usr/bin/env python

from rclpy.duration import Duration

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyActionClient

from qbert_msgs.action import MoveToPos

class MoveMotorToPosState(EventState):
    """
    State implementing moving a motor to a desired position.

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- timeout             Maximum time allowed (seconds)
    -- motor               Motor which should be moved
    -- action_topic        Topic on which the action is called

    Outputs
    <= move_complete       Move completed
    <= failed              Failed for some reason.
    <= canceled            User canceled before completion.
    <= timeout             The action has timed out.

    User data
    ># position  float     Desired position of movement (motor rotations) (Input)
    #> duration  float     Amount time taken to complete rotation (seconds) (Output)

    """

    def __init__(self, timeout, motor, action_topic="/move_to_pos", service_topic="/setup_drive"):
        # See example_state.py for basic explanations.
        super().__init__(outcomes=['move_complete', 'failed', 'canceled', 'timeout'],
                         input_keys=['position'],
                         output_keys=['duration'])

        self._timeout = Duration(seconds=timeout)
        self._timeout_sec = timeout
        self._topic = action_topic
        self._motor = motor

        # Create the action client when building the behavior.
        # Using the proxy client provides asynchronous access to the result and status
        # and makes sure only one client is used, no matter how often this state is used in a behavior.
        ProxyActionClient.initialize(MoveMotorToPosState._node)

        self._client = ProxyActionClient({self._topic: MoveToPos},
                                         wait_duration=0.0)

        # It may happen that the action client fails to send the action goal.
        self._error = False
        self._return = None  # Retain return value in case the outcome is blocked by operator
        self._start_time = None

    def execute(self, userdata):
        # While this state is active, check if the action has been finished and evaluate the result.

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

        if self._node.get_clock().now().nanoseconds - self._start_time.nanoseconds > self._timeout.nanoseconds:
            # Checking for timeout after we check for goal response
            self._return = 'timeout'
            return 'timeout'

        # If the action has not yet finished, no outcome will be returned and the state stays active.
        return None

    def on_enter(self, userdata):

        # make sure to reset the error state since a previous state execution might have failed
        self._error = False
        self._return = None

        if 'position' not in userdata:
            self._error = True
            Logger.logwarn("MoveMotorToPosState requires userdata.position key!")
            return

        # Recording the start time to set rotation duration output
        self._start_time = self._node.get_clock().now()

        goal = MoveToPos.Goal()
        goal.motor = self._motor

        if isinstance(userdata.position, (float, int)):
            goal.target_position = userdata.position
        else:
            self._error = True
            Logger.logwarn("Input is %s. Expects an int or a float.", type(userdata.position).__name__)
            return

        # Send the goal.
        try:
            self._client.send_goal(self._topic, goal, wait_duration=self._timeout_sec)
        except Exception as exc:  # pylint: disable=W0703
            # Since a state failure not necessarily causes a behavior failure,
            # it is recommended to only print warnings, not errors.
            # Using a linebreak before appending the error log enables the operator to collapse details in the GUI.
            Logger.logwarn(f"Failed to send the MoveToPos command:\n  {type(exc)} - {exc}")
            self._error = True

    def on_exit(self, userdata):
        # Make sure that the action is not running when leaving this state.
        # A situation where the action would still be active is for example when the operator manually triggers an outcome.

        if not self._client.has_result(self._topic):
            self._client.cancel(self._topic)
            Logger.loginfo('Cancelled active action goal.')
