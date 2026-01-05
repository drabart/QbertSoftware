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
from qbert_fsm_flexbe_states.move_motor_to_pos_state import MoveMotorToPosState

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
        # x:763 y:123, x:1288 y:690
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
        _state_machine.userdata.position = 0.0
        _state_machine.userdata.iterations = 0

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        with _state_machine:
            # x:224 y:49
            OperatableStateMachine.add('custom_move',
                                       CalculationState(calculation=lambda x: -1000.0),
                                       transitions={'done': 'move-'  # 397 62 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'position',
                                                  'output_value': 'position'})

            # x:161 y:341
            OperatableStateMachine.add('Iter++',
                                       CalculationState(calculation=lambda x: x + 1),
                                       transitions={'done': 'SetDesiredPos'  # 312 395 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'iterations',
                                                  'output_value': 'iterations'})

            # x:166 y:196
            OperatableStateMachine.add('Loop',
                                       CheckConditionState(predicate=lambda x: x < 10),
                                       transitions={'true': 'Iter++'  # 198 298 -1 -1 -1 -1
                                                    , 'false': 'finished'  # 516 165 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'iterations'})

            # x:371 y:511
            OperatableStateMachine.add('Move',
                                       MoveMotorToPosState(timeout=200,
                                                           motor=1,
                                                           action_topic='/move_to_pos'),
                                       transitions={'move_complete': 'SetDesiredPos2'  # 700 502 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 964 615 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 964 615 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 964 615 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'position', 'duration': 'duration'})

            # x:1031 y:275
            OperatableStateMachine.add('Move2',
                                       MoveMotorToPosState(timeout=200,
                                                           motor=1,
                                                           action_topic='/move_to_pos'),
                                       transitions={'move_complete': 'Loop'  # 608 251 1030 282 -1 -1
                                                    , 'failed': 'failed'  # 1236 521 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 1236 521 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 1236 521 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'position', 'duration': 'duration'})

            # x:360 y:387
            OperatableStateMachine.add('SetDesiredPos',
                                       CalculationState(calculation=lambda x: 1800.0),
                                       transitions={'done': 'Move'  # 413 482 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'position',
                                                  'output_value': 'position'})

            # x:793 y:331
            OperatableStateMachine.add('SetDesiredPos2',
                                       CalculationState(calculation=lambda x: 0.0),
                                       transitions={'done': 'Move2'  # 962 327 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'position',
                                                  'output_value': 'position'})

            # x:467 y:21
            OperatableStateMachine.add('move-',
                                       MoveMotorToPosState(timeout=1000,
                                                           motor=1,
                                                           action_topic='/move_to_pos'),
                                       transitions={'move_complete': 'finished'  # 670 100 -1 -1 -1 -1
                                                    , 'failed': 'finished'  # 670 100 -1 -1 -1 -1
                                                    , 'canceled': 'finished'  # 670 100 -1 -1 -1 -1
                                                    , 'timeout': 'finished'  # 670 100 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'position', 'duration': 'duration'})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
