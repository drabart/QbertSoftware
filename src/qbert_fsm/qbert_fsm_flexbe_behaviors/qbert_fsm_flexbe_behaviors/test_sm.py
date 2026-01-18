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
Define Test.

test behavior

Created on Sun Jan 18 2026
@author: Bartosz Drabinski
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
from flexbe_states.publisher_string_state import PublisherStringState
from flexbe_states.user_data_state import UserdataState
from flexbe_states.wait_state import WaitState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]


# [/MANUAL_IMPORT]


class TestSM(Behavior):
    """
    Define Test.

    test behavior
    """

    def __init__(self, node):
        super().__init__()
        self.name = 'Test'

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
        # Root state machine
        # x:837 y:358, x:130 y:400
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        with _state_machine:
            # x:135 y:151
            OperatableStateMachine.add('LogMessage',
                                       UserdataState(data="Hello"),
                                       transitions={'done': 'ProgressValue'  # 246 143 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'value'})

            # x:616 y:350
            OperatableStateMachine.add('CheckFinished',
                                       CheckConditionState(predicate=lambda x: int(x) >= 100),
                                       transitions={'true': 'finished'  # 768 351 -1 -1 -1 -1
                                                    , 'false': 'Delay'  # 642 458 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'progress'})

            # x:608 y:499
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=1),
                                       transitions={'done': 'UpdateProgress'  # 527 484 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:452 y:168
            OperatableStateMachine.add('Log',
                                       PublisherStringState(topic='/gui/request/log'),
                                       transitions={'done': 'Progress'  # 611 174 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'value': 'value'})

            # x:681 y:159
            OperatableStateMachine.add('Progress',
                                       PublisherStringState(topic='/gui/request/progress'),
                                       transitions={'done': 'CheckFinished'  # 682 268 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'value': 'progress'})

            # x:278 y:143
            OperatableStateMachine.add('ProgressValue',
                                       UserdataState(data="0"),
                                       transitions={'done': 'Log'  # 411 170 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'progress'})

            # x:369 y:409
            OperatableStateMachine.add('UpdateProgress',
                                       CalculationState(calculation=lambda x: str(int(x) + 10)),
                                       transitions={'done': 'Log'  # 413 337 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'progress',
                                                  'output_value': 'progress'})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
