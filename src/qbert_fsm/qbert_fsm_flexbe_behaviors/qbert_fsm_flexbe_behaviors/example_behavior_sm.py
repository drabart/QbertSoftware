#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2015 Philipp Schillinger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

"""
Define Example Behavior.

This is a simple example for a behavior.

Created on Fri Aug 21 2015
@author: Philipp Schillinger
"""


from flexbe_core import Autonomy
from flexbe_core import Behavior
from flexbe_core import ConcurrencyContainer
from flexbe_core import Logger
from flexbe_core import OperatableStateMachine
from flexbe_core import PriorityContainer
from flexbe_core import initialize_flexbe_core
from flexbe_states.log_state import LogState
from flexbe_states.user_data_state import UserdataState
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_states.motor_clear_errors_state import MotorClearErrorsState
from qbert_fsm_flexbe_states.motor_home_state import MotorHomeState
from qbert_fsm_flexbe_states.motor_set_vel_state import MotorSetVelState
from qbert_fsm_flexbe_states.motor_stop_state import MotorStopState
from qbert_fsm_flexbe_states.move_move_to_pos_state import MotorMoveToPosState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
from std_msgs.msg import Bool, String, Float64, Empty
from flexbe_core.proxy.qos import QOS_DEFAULT
# [/MANUAL_IMPORT]


class ExampleBehaviorSM(Behavior):
    """
    Define Example Behavior.

    This is a simple example for a behavior.
    """

    def __init__(self, node):
        super().__init__()
        self.name = 'Example Behavior'

        # parameters of this behavior
        self.add_parameter('waiting_time', 3)

        # Initialize ROS node information
        initialize_flexbe_core(node)

        # references to used behaviors

        # Additional initialization code can be added inside the following tags
        # [MANUAL_INIT]


        # [/MANUAL_INIT]

        # Behavior comments:

    def create(self):
        """Create state machine."""
        # Private variables
        log_msg = "Hello World!"

        # Root state machine
        # x:30 y:400, x:130 y:400
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
        _state_machine.userdata.position = 0.0
        _state_machine.userdata.iterations = 0

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        with _state_machine:
            # x:366 y:174
            OperatableStateMachine.add('home',
                                       MotorHomeState(id=1,
                                                      timeout=-1,
                                                      delay=0.2,
                                                      homing_topic='/odesc/home',
                                                      get_state_topic='/odesc/get_state'),
                                       transitions={'state_set': 'finished'  # 204 308 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 252 310 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 252 310 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off,
                                                 'timeout': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:59 y:74
            OperatableStateMachine.add('clear',
                                       MotorClearErrorsState(id=1,
                                                             topic='/odesc/clear_error'),
                                       transitions={'done': 'delay2'  # 246 126 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 108 286 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

            # x:571 y:105
            OperatableStateMachine.add('delay',
                                       WaitState(wait_time=30),
                                       transitions={'done': 'stop'  # 706 131 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:227 y:152
            OperatableStateMachine.add('delay2',
                                       WaitState(wait_time=0.2),
                                       transitions={'done': 'home'  # 348 187 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:679 y:244
            OperatableStateMachine.add('move',
                                       MotorMoveToPosState(id=1,
                                                           timeout=40.0,
                                                           action_topic='/odesc/move_to_pos',
                                                           setup_topic='/odesc/setup'),
                                       transitions={'move_complete': 'finished'  # 617 641 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 409 369 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 409 369 -1 -1 -1 -1
                                                    , 'timeout': 'timeout'  # 789 386 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'position', 'duration': 'duration'})

            # x:526 y:358
            OperatableStateMachine.add('set_pos',
                                       UserdataState(data=-500.0),
                                       transitions={'done': 'move'  # 658 353 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'position'})

            # x:375 y:60
            OperatableStateMachine.add('start',
                                       MotorSetVelState(id=1,
                                                        target_velocity=-5.0,
                                                        vel_topic='/odesc/move_with_velocity',
                                                        setup_topic='/odesc/setup'),
                                       transitions={'velocity_set': 'delay'  # 544 75 -1 -1 -1 -1
                                                    , 'failed': 'failed'},
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:746 y:136
            OperatableStateMachine.add('stop',
                                       MotorStopState(id=1,
                                                      setup_topic='/odesc/setup'),
                                       transitions={'motor_stopped': 'finished'  # 394 298 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 444 293 -1 -1 -1 -1
                                                    },
                                       autonomy={'motor_stopped': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:793 y:458
            OperatableStateMachine.add('timeout',
                                       LogState(text='Move timed out',
                                                severity=2),
                                       transitions={'done': 'failed'  # 465 453 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
