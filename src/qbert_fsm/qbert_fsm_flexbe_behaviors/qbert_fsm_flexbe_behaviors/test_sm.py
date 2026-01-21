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
from flexbe_states.log_key_state import LogKeyState
from flexbe_states.user_data_state import UserdataState
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_behaviors.perform_gui_offset_sm import PerformGUIOffsetSM
from qbert_fsm_flexbe_behaviors.request_gui_confirm_sm import RequestGUIConfirmSM
from qbert_fsm_flexbe_states.gripper_extend_state import GripperExtendState
from qbert_fsm_flexbe_states.motor_clear_errors_state import MotorClearErrorsState
from qbert_fsm_flexbe_states.motor_get_state_state import MotorGetStateState
from qbert_fsm_flexbe_states.motor_home_state import MotorHomeState
from qbert_fsm_flexbe_states.motor_set_vel_state import MotorSetVelState
from qbert_fsm_flexbe_states.motor_stop_state import MotorStopState
from qbert_fsm_flexbe_states.piston_move_to_pos_state import PistonMoveToPosState

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
        self.add_behavior(PerformGUIOffsetSM, 'Perform GUI Offset', node)
        self.add_behavior(RequestGUIConfirmSM, 'Request GUI Confirm', node)

        # Additional initialization code can be added inside the following tags
        # [MANUAL_INIT]


        # [/MANUAL_INIT]

        # Behavior comments:

    def create(self):
        """Create state machine."""
        # Root state machine
        # x:1025 y:94, x:130 y:400
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        with _state_machine:
            # x:167 y:120
            OperatableStateMachine.add('clear2',
                                       MotorClearErrorsState(id=0,
                                                             topic='/odesc/clear_error'),
                                       transitions={'done': 'vel2'  # 284 231 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 154 285 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

            # x:1021 y:604
            OperatableStateMachine.add('GetPos',
                                       MotorGetStateState(motor=1,
                                                          get_state_topic='/odesc/get_state'),
                                       transitions={'state_acquired': 'LogExi'  # 1073 543 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 580 560 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'motor_position',
                                                  'motor_error': 'motor_error'})

            # x:291 y:681
            OperatableStateMachine.add('Grip',
                                       GripperExtendState(id=63,
                                                          extended=True,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'finished'  # 727 400 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 214 561 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:1011 y:461
            OperatableStateMachine.add('LogExi',
                                       LogKeyState(text="state {}",
                                                   severity=2),
                                       transitions={'done': 'LogPos'  # 1082 396 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'motor_axis_state'})

            # x:1050 y:287
            OperatableStateMachine.add('LogPos',
                                       LogKeyState(text="Motor pos {}",
                                                   severity=2),
                                       transitions={'done': 'finished'  # 1045 193 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'motor_position'})

            # x:674 y:338
            OperatableStateMachine.add('Perform GUI Offset',
                                       self.use_behavior(PerformGUIOffsetSM, 'Perform GUI Offset',
                                                         parameters={'motor_id': 1}),
                                       transitions={'finished': 'finished'  # 941 231 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 406 392 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:677 y:527
            OperatableStateMachine.add('Request GUI Confirm',
                                       self.use_behavior(RequestGUIConfirmSM, 'Request GUI Confirm',
                                                         parameters={'confirm_string': "Please confirm that the robot is ready to perform the next move"}),
                                       transitions={'finished': 'finished'  # 943 327 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 409 487 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

            # x:766 y:643
            OperatableStateMachine.add('Ungrip',
                                       GripperExtendState(id=63,
                                                          extended=False,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'finished'  # 935 385 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 451 541 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:76 y:22
            OperatableStateMachine.add('clear',
                                       MotorClearErrorsState(id=1,
                                                             topic='/odesc/clear_error'),
                                       transitions={'done': 'vel'  # 259 53 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 126 250 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

            # x:560 y:44
            OperatableStateMachine.add('delay',
                                       WaitState(wait_time=5),
                                       transitions={'done': 'stop'  # 720 62 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:589 y:674
            OperatableStateMachine.add('delay2',
                                       WaitState(wait_time=5),
                                       transitions={'done': 'Ungrip'  # 722 688 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:520 y:329
            OperatableStateMachine.add('delay3',
                                       WaitState(wait_time=1),
                                       transitions={'done': 'vel3'  # 641 329 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:621 y:146
            OperatableStateMachine.add('delay4',
                                       WaitState(wait_time=8),
                                       transitions={'done': 'stop2'  # 753 169 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:392 y:106
            OperatableStateMachine.add('home',
                                       MotorHomeState(id=0,
                                                      timeout=-1,
                                                      delay=0.2,
                                                      homing_topic='/odesc/home',
                                                      get_state_topic='/odesc/get_state'),
                                       transitions={'state_set': 'finished'  # 779 116 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 263 278 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 263 278 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off,
                                                 'timeout': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:717 y:448
            OperatableStateMachine.add('piston',
                                       PistonMoveToPosState(id=63,
                                                            timeout=10.0,
                                                            action_topic='/esp/move_to_pos'),
                                       transitions={'move_complete': 'finished'  # 888 321 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 429 433 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 429 433 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 429 433 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'piston', 'duration': 'duration'})

            # x:438 y:464
            OperatableStateMachine.add('pistonSet',
                                       UserdataState(data=0.0),
                                       transitions={'done': 'piston'  # 642 516 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'piston'})

            # x:293 y:546
            OperatableStateMachine.add('progress',
                                       UserdataState(data=25.0),
                                       transitions={'done': 'Request GUI Confirm'  # 536 569 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'progress'})

            # x:775 y:28
            OperatableStateMachine.add('stop',
                                       MotorStopState(id=1,
                                                      setup_topic='/odesc/setup'),
                                       transitions={'motor_stopped': 'finished'  # 969 79 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 456 235 -1 -1 -1 -1
                                                    },
                                       autonomy={'motor_stopped': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:798 y:145
            OperatableStateMachine.add('stop2',
                                       MotorStopState(id=0,
                                                      setup_topic='/odesc/setup'),
                                       transitions={'motor_stopped': 'finished'  # 952 128 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 470 295 -1 -1 -1 -1
                                                    },
                                       autonomy={'motor_stopped': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:295 y:40
            OperatableStateMachine.add('vel',
                                       MotorSetVelState(id=1,
                                                        target_velocity=-30.0,
                                                        vel_topic='/odesc/move_with_velocity',
                                                        setup_topic='/odesc/setup'),
                                       transitions={'velocity_set': 'delay'  # 479 63 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 214 240 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:306 y:263
            OperatableStateMachine.add('vel2',
                                       MotorSetVelState(id=0,
                                                        target_velocity=4.0,
                                                        vel_topic='/odesc/move_with_velocity',
                                                        setup_topic='/odesc/setup'),
                                       transitions={'velocity_set': 'delay3'  # 451 352 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 224 352 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:611 y:235
            OperatableStateMachine.add('vel3',
                                       MotorSetVelState(id=0,
                                                        target_velocity=8.0,
                                                        vel_topic='/odesc/move_with_velocity',
                                                        setup_topic='/odesc/setup'),
                                       transitions={'velocity_set': 'delay4'  # 676 218 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 374 338 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
