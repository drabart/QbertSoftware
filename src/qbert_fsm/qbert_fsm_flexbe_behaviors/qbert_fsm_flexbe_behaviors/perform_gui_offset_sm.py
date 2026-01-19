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
Define Perform GUI Offset.

Performs a motor offset

Created on Sat Jan 17 2026
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
from flexbe_states.flexible_calculation_state import FlexibleCalculationState
from flexbe_states.publisher_empty_state import PublisherEmptyState
from flexbe_states.publisher_string_state import PublisherStringState
from flexbe_states.subscriber_state import SubscriberState
from flexbe_states.user_data_state import UserdataState
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_states.motor_get_state_state import MotorGetStateState
from qbert_fsm_flexbe_states.motor_move_to_pos_state import MotorMoveToPosState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
from std_msgs.msg import Bool, String, Float64, Empty
from flexbe_core.proxy.qos import QOS_DEFAULT
# [/MANUAL_IMPORT]


class PerformGUIOffsetSM(Behavior):
    """
    Define Perform GUI Offset.

    Performs a motor offset
    """

    def __init__(self, node):
        super().__init__()
        self.name = 'Perform GUI Offset'

        # parameters of this behavior
        self.add_parameter('motor_id', 1)

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
        # x:1116 y:56, x:1215 y:22
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        with _state_machine:
            # x:69 y:88
            OperatableStateMachine.add('StartOffsetCalibration',
                                       PublisherEmptyState(topic='/gui/request/position_adjust'),
                                       transitions={'done': 'GetInitialPosition'  # 218 68 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:863 y:154
            OperatableStateMachine.add('AddOffsetValue',
                                       FlexibleCalculationState(calculation=lambda x: x[0] + str(x[1].data),
                                                                input_keys=["log_text",
                                                                            "offset_message"]),
                                       transitions={'done': 'PublishLog'  # 894 101 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'log_text': 'log_text',
                                                  'offset_message': 'offset_message',
                                                  'output_value': 'output_value'})

            # x:369 y:375
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'GetOffsetFinialized'  # 409 268 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:278 y:37
            OperatableStateMachine.add('GetInitialPosition',
                                       MotorGetStateState(motor=_state_machine.userdata.motor_id,
                                                          get_state_topic='/odesc/get_state'),
                                       transitions={'state_acquired': 'GetOffsetMessage'  # 498 176 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 633 33 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'position',
                                                  'motor_error': 'motor_error'})

            # x:370 y:139
            OperatableStateMachine.add('GetOffsetFinialized',
                                       SubscriberState(topic="/gui/offset_complete",
                                                       msg_type=Empty,
                                                       blocking=False,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'OffsetFinallizedReceived'  # 524 156 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 651 87 452 138 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'offset_finalized_message'})

            # x:571 y:272
            OperatableStateMachine.add('GetOffsetMessage',
                                       SubscriberState(topic="/gui/offset",
                                                       msg_type=Float64,
                                                       blocking=False,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'OffsetReceived'  # 617 355 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 1093 222 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'offset_message'})

            # x:559 y:146
            OperatableStateMachine.add('OffsetFinallizedReceived',
                                       CheckConditionState(predicate=lambda x: x is not None),
                                       transitions={'true': 'SetText'  # 723 123 -1 -1 -1 -1
                                                    , 'false': 'GetOffsetMessage'  # 625 234 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'offset_finalized_message'})

            # x:561 y:389
            OperatableStateMachine.add('OffsetReceived',
                                       CheckConditionState(predicate=lambda x: x is not None),
                                       transitions={'true': 'UpdatePosition'  # 631 474 -1 -1 -1 -1
                                                    , 'false': 'Delay'  # 486 411 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'offset_message'})

            # x:940 y:80
            OperatableStateMachine.add('PublishLog',
                                       PublisherStringState(topic='/gui/request/log'),
                                       transitions={'done': 'finished'  # 1080 80 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'value': 'log_text'})

            # x:483 y:560
            OperatableStateMachine.add('SetOffsetPosition',
                                       MotorMoveToPosState(id=_state_machine.userdata.motor_id,
                                                           timeout=10.0,
                                                           action_topic='/odesc/move_to_pos',
                                                           setup_topic='/odesc/setup'),
                                       transitions={'move_complete': 'Delay'  # 434 506 -1 -1 409 428
                                                    , 'failed': 'failed'  # 966 572 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 966 572 -1 -1 -1 -1
                                                    , 'timeout': 'Delay'  # 434 506 -1 -1 409 428
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'offset_position',
                                                  'duration': 'duration'})

            # x:738 y:156
            OperatableStateMachine.add('SetText',
                                       UserdataState(data="Finished offset with offset: "),
                                       transitions={'done': 'AddOffsetValue'  # 835 126 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'log_text'})

            # x:672 y:467
            OperatableStateMachine.add('UpdatePosition',
                                       FlexibleCalculationState(calculation=lambda x: x[0] + x[1].data,
                                                                input_keys=["position",
                                                                            "offset_message"]),
                                       transitions={'done': 'SetOffsetPosition'  # 645 540 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'position': 'position',
                                                  'offset_message': 'offset_message',
                                                  'output_value': 'offset_position'})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
