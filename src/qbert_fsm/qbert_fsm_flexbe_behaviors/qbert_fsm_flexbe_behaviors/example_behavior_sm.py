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
from flexbe_states.calculation_state import CalculationState
from flexbe_states.check_condition_state import CheckConditionState
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_states.move_motor_to_pos_state import MoveMotorToPosState
from qbert_fsm_flexbe_states.set_motor_state_state import SetMotorStateState
from qbert_fsm_flexbe_states.set_motor_vel_state import SetMotorVelState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]


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
        # x:1215 y:373, x:1288 y:690
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
        _state_machine.userdata.position = 0.0
        _state_machine.userdata.iterations = 0

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        with _state_machine:
            # x:202 y:354
            OperatableStateMachine.add('home',
                                       SetMotorStateState(motor=1,
                                                          desired_state='homing',
                                                          homing_topic='/odesc/home_motor',
                                                          setup_topic='/odesc/setup_drive',
                                                          motor_arm_topic='/odesc/motor_ready'),
                                       transitions={'state_set': 'finished'  # 777 388 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 815 550 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:71 y:680
            OperatableStateMachine.add('Iter++',
                                       CalculationState(calculation=lambda x: x + 1),
                                       transitions={'done': 'SetDesiredPos'  # 221 662 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'iterations',
                                                  'output_value': 'iterations'})

            # x:62 y:560
            OperatableStateMachine.add('Loop',
                                       CheckConditionState(predicate=lambda x: x < 10),
                                       transitions={'true': 'Iter++'  # 10 644 -1 -1 -1 -1
                                                    , 'false': 'finished'  # 738 481 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'iterations'})

            # x:471 y:670
            OperatableStateMachine.add('Move',
                                       MoveMotorToPosState(motor=1,
                                                           timeout=200,
                                                           action_topic='/odesc/move_to_pos'),
                                       transitions={'move_complete': 'SetDesiredPos2'  # 699 667 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 999 682 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 999 682 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 999 682 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'position', 'duration': 'duration'})

            # x:1025 y:563
            OperatableStateMachine.add('Move2',
                                       MoveMotorToPosState(motor=1,
                                                           timeout=200,
                                                           action_topic='/odesc/move_to_pos'),
                                       transitions={'move_complete': 'Loop'  # 554 562 1024 570 -1 -1
                                                    , 'failed': 'failed'  # 1235 638 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 1235 638 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 1235 638 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'position', 'duration': 'duration'})

            # x:269 y:661
            OperatableStateMachine.add('SetDesiredPos',
                                       CalculationState(calculation=lambda x: 1800.0),
                                       transitions={'done': 'Move'  # 416 690 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'position',
                                                  'output_value': 'position'})

            # x:763 y:619
            OperatableStateMachine.add('SetDesiredPos2',
                                       CalculationState(calculation=lambda x: 0.0),
                                       transitions={'done': 'Move2'  # 949 615 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'position',
                                                  'output_value': 'position'})

            # x:475 y:111
            OperatableStateMachine.add('custom_move',
                                       CalculationState(calculation=lambda x: -1000.0),
                                       transitions={'done': 'move-'  # 668 114 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'position',
                                                  'output_value': 'position'})

            # x:793 y:313
            OperatableStateMachine.add('ina',
                                       SetMotorStateState(motor=1,
                                                          desired_state='inactive',
                                                          homing_topic='/odesc/home_motor',
                                                          setup_topic='/odesc/setup_drive',
                                                          motor_arm_topic='/odesc/motor_ready'),
                                       transitions={'state_set': 'finished'  # 1076 368 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 1112 523 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:746 y:127
            OperatableStateMachine.add('move-',
                                       MoveMotorToPosState(motor=1,
                                                           timeout=1000,
                                                           action_topic='/odesc/move_to_pos'),
                                       transitions={'move_complete': 'finished'  # 1068 318 -1 -1 -1 -1
                                                    , 'failed': 'finished'  # 1068 318 -1 -1 -1 -1
                                                    , 'canceled': 'finished'  # 1068 318 -1 -1 -1 -1
                                                    , 'timeout': 'finished'  # 1068 318 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'position', 'duration': 'duration'})

            # x:136 y:233
            OperatableStateMachine.add('set_state',
                                       SetMotorStateState(motor=1,
                                                          desired_state='velocity',
                                                          homing_topic='/odesc/home_motor',
                                                          setup_topic='/odesc/setup_drive',
                                                          motor_arm_topic='/odesc/motor_ready'),
                                       transitions={'state_set': 'vel'  # 343 261 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 784 482 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:392 y:220
            OperatableStateMachine.add('vel',
                                       SetMotorVelState(motor=1,
                                                        target_velocity=-15.0,
                                                        vel_topic='/odesc/move_with_velocity'),
                                       transitions={'velocity_set': 'wait'  # 573 257 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 908 476 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:797 y:237
            OperatableStateMachine.add('vel2',
                                       SetMotorVelState(motor=1,
                                                        target_velocity=0.0,
                                                        vel_topic='/odesc/move_with_velocity'),
                                       transitions={'velocity_set': 'finished'  # 1067 333 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 1104 492 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:599 y:251
            OperatableStateMachine.add('wait',
                                       WaitState(wait_time=10),
                                       transitions={'done': 'ina'  # 749 321 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
