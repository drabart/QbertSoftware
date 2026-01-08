#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2026 Bartosz Drabinski
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
Define Qbert State Machine.

Main state machine for qbert cable splitting robot

Created on Thu Jan 08 2026
@author: Bartosz Drabinski
"""


from flexbe_core import Autonomy
from flexbe_core import Behavior
from flexbe_core import ConcurrencyContainer
from flexbe_core import Logger
from flexbe_core import OperatableStateMachine
from flexbe_core import PriorityContainer
from flexbe_core import initialize_flexbe_core
from flexbe_states.check_condition_state import CheckConditionState
from flexbe_states.log_key_state import LogKeyState
from flexbe_states.log_state import LogState
from flexbe_states.subscriber_state import SubscriberState
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_states.set_motor_state_state import SetMotorStateState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
from std_msgs.msg import Bool, String, Float64, Empty
from flexbe_core.proxy.qos import QOS_DEFAULT
# [/MANUAL_IMPORT]


class QbertStateMachineSM(Behavior):
    """
    Define Qbert State Machine.

    Main state machine for qbert cable splitting robot
    """

    def __init__(self, node):
        super().__init__()
        self.name = 'Qbert State Machine'

        # parameters of this behavior

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
        GANTRY_MOTOR = 1
        ROTATION_MOTOR = 0

        # Root state machine
        # x:891 y:96, x:896 y:196
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        # x:864 y:141, x:679 y:505
        _sm_wait_for_homing_0 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_wait_for_homing_0:
            # x:149 y:104
            OperatableStateMachine.add('CheckHomingGUI',
                                       SubscriberState(topic="/gui_home",
                                                       msg_type=Empty,
                                                       blocking=False,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'MessageReceived'  # 320 96 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 475 343 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'homing_message'})

            # x:269 y:278
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'CheckHomingGUI'  # 189 245 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:636 y:93
            OperatableStateMachine.add('LogResponse',
                                       LogKeyState(text="Received message: {}",
                                                   severity=2),
                                       transitions={'done': 'finished'  # 813 129 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'homing_message'})

            # x:369 y:64
            OperatableStateMachine.add('MessageReceived',
                                       CheckConditionState(predicate=lambda x: x is not None),
                                       transitions={'true': 'LogResponse'  # 594 74 -1 -1 -1 -1
                                                    , 'false': 'Delay'  # 398 193 415 117 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'homing_message'})

        # x:942 y:184, x:933 y:428
        _sm_homerobot_1 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_homerobot_1:
            # x:293 y:225
            OperatableStateMachine.add('SetGantryIntoHomingState',
                                       SetMotorStateState(motor=GANTRY_MOTOR,
                                                          desired_state='homing',
                                                          homing_topic='/home_motor',
                                                          setup_topic='/setup_drive',
                                                          motor_arm_topic='/motor_ready'),
                                       transitions={'state_set': 'finished'  # 696 224 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 691 348 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

        with _state_machine:
            # x:150 y:120
            OperatableStateMachine.add('Wait for Homing',
                                       _sm_wait_for_homing_0,
                                       transitions={'finished': 'HomeRobot'  # 365 131 -1 -1 -1 -1
                                                    , 'failed': 'LogError'  # 406 347 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:422 y:135
            OperatableStateMachine.add('HomeRobot',
                                       _sm_homerobot_1,
                                       transitions={'finished': 'LogMachineDone'  # 604 127 -1 -1 -1 -1
                                                    , 'failed': 'LogError'  # 496 342 471 194 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:501 y:493
            OperatableStateMachine.add('LogError',
                                       LogState(text="Error occured",
                                                severity=2),
                                       transitions={'done': 'failed'  # 732 369 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:687 y:109
            OperatableStateMachine.add('LogMachineDone',
                                       LogState(text="State machine finished",
                                                severity=2),
                                       transitions={'done': 'finished'  # 845 114 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
