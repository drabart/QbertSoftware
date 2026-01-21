#!/usr/bin/env python

from rclpy.duration import Duration

from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyActionClient, ProxyServiceCaller

from qbert_msgs.srv import MotorSetup
from qbert_msgs.action import MoveToPos

class MotorMoveToPosState(EventState):
    """
    State implementing moving a id to a desired position.

    Shouldn't be using multiple actions for one robot at once.

    Elements defined here for UI
    Parameters
    -- timeout             Maximum time allowed (seconds)
    -- id               Motor which should be moved
    -- action_topic        Topic on which the action is called
    -- setup_topic          Topic for drive state setup

    Outputs
    <= move_complete       Move completed
    <= failed              Failed for some reason.
    <= canceled            User canceled before completion.
    <= timeout             The action has timed out.

    User data
    ># position  float     Desired position of movement (id rotations) (Input)
    #> duration  float     Amount time taken to complete rotation (seconds) (Output)

    """

    def __init__(self, id, timeout = 10.0,
                 action_topic="/odesc/move_to_pos", 
                 setup_topic="/odesc/setup"):
        super().__init__(outcomes=['move_complete', 'failed', 'canceled', 'timeout'],
                         input_keys=['position'],
                         output_keys=['duration'])

        self._timeout = Duration(seconds=timeout)
        self._timeout_sec = timeout
        self._topic = action_topic
        self._setup_topic = setup_topic
        self._id = id

        ProxyActionClient.initialize(MotorMoveToPosState._node)

        self._client = ProxyActionClient({self._topic: MoveToPos},
                                         wait_duration=0.0)
        
        ProxyServiceCaller.initialize(MotorMoveToPosState._node)

        self._setup_client = ProxyServiceCaller(
            {self._setup_topic: MotorSetup},
            wait_duration=0.0,
        )

        self._error = False
        self._return = None
        self._start_time = None

    def execute(self, userdata):
        if self._error:
            return 'failed'

        if self._return is not None:
            return self._return

        if self._client.has_result(self._topic):
            _ = self._client.get_result(self._topic)
            userdata.duration = self._node.get_clock().now() - self._start_time
            Logger.loginfo('Move complete')
            self._return = 'move_complete'
            return self._return

        if self._node.get_clock().now().nanoseconds - self._start_time.nanoseconds > self._timeout.nanoseconds:
            self._return = 'timeout'
            return 'timeout'

        return None

    def on_enter(self, userdata):
        self._error = False
        self._return = None

        if 'position' not in userdata:
            self._error = True
            Logger.logwarn("MoveMotorToPosState requires userdata.position key!")
            return

        self._start_time = self._node.get_clock().now()

        goal = MoveToPos.Goal()
        goal.id = self._id

        if isinstance(userdata.position, (float, int)):
            goal.target_position = userdata.position
        else:
            self._error = True
            Logger.logwarn("Input is %s. Expects an int or a float.", type(userdata.position).__name__)
            return
        
        request = MotorSetup.Request()
        request.id = self._id
        request.mode = MotorSetup.Request.MODE_POSITION
        
        self._setup_client.call(self._setup_topic, request)

        try:
            self._client.send_goal(self._topic, goal, wait_duration=self._timeout_sec)
        except Exception as exc:
            Logger.logwarn(f"Failed to send the MoveToPos command:\n  {type(exc)} - {exc}")
            self._error = True

    def on_exit(self, userdata):
        if not self._client.has_result(self._topic):
            self._client.cancel(self._topic)
            Logger.loginfo('Cancelled active action goal.')
