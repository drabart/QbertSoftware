#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2026 Lucas
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
Define cable_detect_yup.

Detects if cable detected

Created on Sat Jan 17 2026
@author: Lucas
"""


from flexbe_core import Autonomy
from flexbe_core import Behavior
from flexbe_core import ConcurrencyContainer
from flexbe_core import Logger
from flexbe_core import OperatableStateMachine
from flexbe_core import PriorityContainer
from flexbe_core import initialize_flexbe_core
from flexbe_states.check_condition_state import CheckConditionState
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_states.detect_cable_state import DetectCableState
from qbert_fsm_flexbe_states.motor_get_state_state import MotorGetStateState
from qbert_fsm_flexbe_states.motor_set_vel_state import MotorSetVelState
from qbert_fsm_flexbe_states.motor_stop_state import MotorStopState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]


# [/MANUAL_IMPORT]


class cable_detect_yupSM(Behavior):
    """
    Define cable_detect_yup.

    Detects if cable detected
    """

    def __init__(self, node):
        super().__init__()
        self.name = 'cable_detect_yup'

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
        # x:342 y:627, x:318 y:381
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        # x:498 y:406, x:130 y:400
        _sm_toofar_0 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_toofar_0:
            # x:113 y:74
            OperatableStateMachine.add('GetPos',
                                       MotorGetStateState(motor=1,
                                                          get_state_topic='/odesc/get_state'),
                                       transitions={'state_acquired': 'TooFar'  # 367 94 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 144 280 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'motor_position',
                                                  'motor_error': 'motor_error'})

            # x:455 y:67
            OperatableStateMachine.add('TooFar',
                                       CheckConditionState(predicate=lambda x: x > 1000),
                                       transitions={'true': 'finished'  # 476 258 -1 -1 -1 -1
                                                    , 'false': 'Wait'  # 401 161 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'motor_position'})

            # x:301 y:173
            OperatableStateMachine.add('Wait',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'GetPos'  # 252 157 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

        # x:612 y:189, x:171 y:72, x:460 y:73, x:290 y:395, x:430 y:400, x:629 y:362, x:630 y:400
        _sm_detectcable_1 = ConcurrencyContainer(outcomes=['finished', 'failed'],
                                                 conditions=[('failed', [('TooFar', 'finished')]),
                                                             ('failed', [('TooFar', 'failed')]),
                                                             ('failed', [('DetectCable', 'timeout')]),
                                                             ('failed', [('DetectCable', 'canceled')]),
                                                             ('finished', [('DetectCable', 'success')])
                                                             ])

        with _sm_detectcable_1:
            # x:234 y:172
            OperatableStateMachine.add('DetectCable',
                                       DetectCableState(timeout=-1.0,
                                                        action_topic='/detect_cable'),
                                       transitions={'success': 'finished',
                                                    'canceled': 'failed',
                                                    'timeout': 'failed'},
                                       autonomy={'success': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off})

            # x:270 y:60
            OperatableStateMachine.add('TooFar',
                                       _sm_toofar_0,
                                       transitions={'finished': 'failed', 'failed': 'failed'},
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

        with _state_machine:
            # x:244 y:158
            OperatableStateMachine.add('StartMove',
                                       MotorSetVelState(id=1,
                                                        target_velocity=-20.0,
                                                        vel_topic='/odesc/move_with_velocity',
                                                        setup_topic='/odesc/setup'),
                                       transitions={'velocity_set': 'DetectCable'  # 408 136 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 324 321 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:441 y:152
            OperatableStateMachine.add('DetectCable',
                                       _sm_detectcable_1,
                                       transitions={'finished': 'StopGood'  # 572 346 525 211 -1 -1
                                                    , 'failed': 'StopBad'  # 616 206 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:647 y:253
            OperatableStateMachine.add('StopBad',
                                       MotorStopState(id=1,
                                                      setup_topic='/odesc/setup'),
                                       transitions={'motor_stopped': 'failed'  # 466 319 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 466 319 -1 -1 -1 -1
                                                    },
                                       autonomy={'motor_stopped': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:585 y:463
            OperatableStateMachine.add('StopGood',
                                       MotorStopState(id=1,
                                                      setup_topic='/odesc/setup'),
                                       transitions={'motor_stopped': 'finished'  # 470 574 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 453 443 -1 -1 -1 -1
                                                    },
                                       autonomy={'motor_stopped': Autonomy.Off,
                                                 'failed': Autonomy.Off})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
