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
Define Perform Gui Offset.

Behavior for performing gui correction of the autoposition

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
from flexbe_states.subscriber_state import SubscriberState
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_states.motor_get_state_state import MotorGetStateState
from qbert_fsm_flexbe_states.motor_home_state import MotorHomeState
from qbert_fsm_flexbe_states.motor_move_to_pos_state import MotorMoveToPosState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
from std_msgs.msg import Bool, String, Float64, Empty
from flexbe_core.proxy.qos import QOS_DEFAULT
# [/MANUAL_IMPORT]


class PerformGuiOffsetSM(Behavior):
    """
    Define Perform Gui Offset.

    Behavior for performing gui correction of the autoposition
    """

    def __init__(self, node):
        super().__init__()
        self.name = 'Perform Gui Offset'

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
        # x:30 y:400, x:130 y:400
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'], input_keys=['position', 'motor_id'])
        _state_machine.userdata.position = 0.0
        _state_machine.userdata.motor_id = 1

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        with _state_machine:
            # x:304 y:32
            OperatableStateMachine.add('Home',
                                       MotorHomeState(id=1,
                                                      timeout=-1,
                                                      delay=0.2,
                                                      homing_topic='/odesc/home',
                                                      get_state_topic='/odesc/get_state'),
                                       transitions={'state_set': 'getpos'  # 490 49 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 222 241 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 222 241 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off,
                                                 'timeout': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:370 y:139
            OperatableStateMachine.add('GetOffsetFinialized',
                                       SubscriberState(topic="/gui/offset_complete",
                                                       msg_type=Empty,
                                                       blocking=False,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'OffsetFinallizedReceived'  # 518 144 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 253 291 -1 -1 -1 -1
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
                                                    , 'unavailable': 'failed'  # 360 347 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'offset_message'})

            # x:199 y:159
            OperatableStateMachine.add('GetPosition0',
                                       MotorGetStateState(motor=_state_machine.userdata.motor_id,
                                                          get_state_topic='/odesc/get_state'),
                                       transitions={'state_acquired': 'GetOffsetFinialized'  # 368 177 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 169 299 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'position',
                                                  'motor_error': 'motor_error'})

            # x:205 y:264
            OperatableStateMachine.add('GetPosition1',
                                       MotorGetStateState(motor=1,
                                                          get_state_topic='/odesc/get_state'),
                                       transitions={'state_acquired': 'GetOffsetFinialized'  # 369 230 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 171 353 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'position',
                                                  'motor_error': 'motor_error'})

            # x:559 y:146
            OperatableStateMachine.add('OffsetFinallizedReceived',
                                       CheckConditionState(predicate=lambda x: x is not None),
                                       transitions={'true': 'finished'  # 297 311 -1 -1 -1 -1
                                                    , 'false': 'GetOffsetMessage'  # 625 234 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'offset_finalized_message'})

            # x:561 y:389
            OperatableStateMachine.add('OffsetReceived',
                                       CheckConditionState(predicate=lambda x: x is not None),
                                       transitions={'true': 'UpdatePosition'  # 631 474 -1 -1 -1 -1
                                                    , 'false': 'delay'  # 486 411 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'offset_message'})

            # x:26 y:216
            OperatableStateMachine.add('SelectMotor0',
                                       CheckConditionState(predicate=lambda x: x == 0),
                                       transitions={'true': 'GetPosition0'  # 167 200 -1 -1 -1 -1
                                                    , 'false': 'GetPosition1'  # 184 268 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'motor_id'})

            # x:710 y:571
            OperatableStateMachine.add('SelectMotor1',
                                       CheckConditionState(predicate=lambda x: x == 0),
                                       transitions={'true': 'SetOffsetPosition0'  # 711 682 743 624 -1 -1
                                                    , 'false': 'SetOffsetPosition1'  # 844 670 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'motor_id'})

            # x:590 y:709
            OperatableStateMachine.add('SetOffsetPosition0',
                                       MotorMoveToPosState(id=0,
                                                           timeout=10.0,
                                                           action_topic='/odesc/move_to_pos',
                                                           setup_topic='/odesc/setup'),
                                       transitions={'move_complete': 'delay'  # 495 612 -1 -1 409 428
                                                    , 'failed': 'failed'  # 365 600 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 365 600 -1 -1 -1 -1
                                                    , 'timeout': 'delay'  # 495 612 -1 -1 409 428
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'offset_position',
                                                  'duration': 'duration'})

            # x:793 y:713
            OperatableStateMachine.add('SetOffsetPosition1',
                                       MotorMoveToPosState(id=1,
                                                           timeout=10.0,
                                                           action_topic='/odesc/move_to_pos',
                                                           setup_topic='/odesc/setup'),
                                       transitions={'move_complete': 'delay'  # 606 598 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 466 586 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 466 586 -1 -1 -1 -1
                                                    , 'timeout': 'delay'  # 606 598 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'offset_position',
                                                  'duration': 'duration'})

            # x:69 y:88
            OperatableStateMachine.add('StartOffsetCalibration',
                                       PublisherEmptyState(topic='/gui/position_adjust'),
                                       transitions={'done': 'GetPosition0'  # 166 164 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:672 y:467
            OperatableStateMachine.add('UpdatePosition',
                                       FlexibleCalculationState(calculation=lambda x: x[0] + x[1].data,
                                                                input_keys=["position",
                                                                            "offset_message"]),
                                       transitions={'done': 'SelectMotor1'  # 758 541 -1 -1 739 570
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'position': 'position',
                                                  'offset_message': 'offset_message',
                                                  'output_value': 'offset_position'})

            # x:369 y:375
            OperatableStateMachine.add('delay',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'GetOffsetFinialized'  # 409 268 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:523 y:23
            OperatableStateMachine.add('getpos',
                                       MotorGetStateState(motor=1,
                                                          get_state_topic='/odesc/get_state'),
                                       transitions={'state_acquired': 'move'  # 734 64 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 329 231 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'motor_position',
                                                  'motor_error': 'motor_error'})

            # x:795 y:55
            OperatableStateMachine.add('move',
                                       MotorMoveToPosState(id=1,
                                                           timeout=10.0,
                                                           action_topic='/odesc/move_to_pos',
                                                           setup_topic='/odesc/setup'),
                                       transitions={'move_complete': 'finished'  # 421 244 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 470 255 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 471 254 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 471 250 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'motor_position',
                                                  'duration': 'duration'})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
