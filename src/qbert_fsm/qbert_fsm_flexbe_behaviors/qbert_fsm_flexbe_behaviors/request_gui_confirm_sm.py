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
Define Request GUI Confirm.

Blocks execution until the popup in GUI is resolved

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
from flexbe_states.check_condition_state import CheckConditionState
from flexbe_states.publisher_string_state import PublisherStringState
from flexbe_states.subscriber_state import SubscriberState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
from std_msgs.msg import Bool, String, Float64, Empty
from flexbe_core.proxy.qos import QOS_DEFAULT
# [/MANUAL_IMPORT]


class RequestGUIConfirmSM(Behavior):
    """
    Define Request GUI Confirm.

    Blocks execution until the popup in GUI is resolved
    """

    def __init__(self, node):
        super().__init__()
        self.name = 'Request GUI Confirm'

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
        # x:755 y:262, x:363 y:278
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'], input_keys=['confirm_string'])
        _state_machine.userdata.confirm_string = "Please confirm the machine is ready to perform the next action"

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        with _state_machine:
            # x:225 y:136
            OperatableStateMachine.add('RequestConfirm',
                                       PublisherStringState(topic='/gui/request_confirm'),
                                       transitions={'done': 'WaitForConfirm'  # 432 133 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'value': 'confirm_string'})

            # x:504 y:241
            OperatableStateMachine.add('CheckSuccess',
                                       CheckConditionState(predicate=lambda x: x.data == True),
                                       transitions={'true': 'finished'  # 684 256 -1 -1 -1 -1
                                                    , 'false': 'failed'  # 449 290 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'message'})

            # x:517 y:133
            OperatableStateMachine.add('WaitForConfirm',
                                       SubscriberState(topic='/gui/confirm',
                                                       msg_type=Bool,
                                                       blocking=True,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'CheckSuccess'  # 562 216 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 442 220 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'message'})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
