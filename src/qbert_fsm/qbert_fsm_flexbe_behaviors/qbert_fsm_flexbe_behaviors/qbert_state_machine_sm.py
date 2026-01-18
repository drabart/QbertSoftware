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
from flexbe_states.calculation_state import CalculationState
from flexbe_states.check_condition_state import CheckConditionState
from flexbe_states.log_state import LogState
from flexbe_states.subscriber_state import SubscriberState
from flexbe_states.user_data_state import UserdataState
from qbert_fsm_flexbe_behaviors.perform_gui_offset_sm import PerformGUIOffsetSM
from qbert_fsm_flexbe_states.gripper_extend_state import GripperExtendState
from qbert_fsm_flexbe_states.motor_get_state_state import MotorGetStateState
from qbert_fsm_flexbe_states.motor_home_state import MotorHomeState
from qbert_fsm_flexbe_states.motor_move_to_pos_state import MotorMoveToPosState
from qbert_fsm_flexbe_states.piston_move_to_pos_state import PistonMoveToPosState

# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
from std_msgs.msg import Bool, String, Float64, Empty
from flexbe_core.proxy.qos import QOS_DEFAULT
from odrive.enums import AxisState
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
        self.add_behavior(PerformGUIOffsetSM, 'Unstrand/MoveMotors/FindCableEnd/Perform GUI Offset', node)
        self.add_behavior(PerformGUIOffsetSM, 'Unstrand/MoveMotors/FindSection/Perform GUI Offset', node)

        # Additional initialization code can be added inside the following tags
        # [MANUAL_INIT]


        # [/MANUAL_INIT]

        # Behavior comments:

    def create(self):
        """Create state machine."""
        # Private variables
        GANTRY_MOTOR = 1
        ROTATION_MOTOR = 0
        GANTRY_MIN = 100
        GANTRY_MAX = 1500
        ESP_ID = 63

        # Root state machine
        # x:859 y:155, x:130 y:400
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
        _state_machine.userdata.gantry_position = 0.0
        _state_machine.userdata.rotation_position = 0.0

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        # x:30 y:400, x:130 y:400
        _sm_waitcancel_0 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_waitcancel_0:
            # x:80 y:171
            OperatableStateMachine.add('WaitForCancel',
                                       SubscriberState(topic='/gui/cancel',
                                                       msg_type=Empty,
                                                       blocking=True,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'finished'  # 59 308 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 121 324 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'message'})

        # x:1052 y:144, x:429 y:348
        _sm_splitcable_1 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_splitcable_1:
            # x:142 y:117
            OperatableStateMachine.add('PistonsRetracted',
                                       UserdataState(data=0.0),
                                       transitions={'done': 'PistonRetract'  # 288 119 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'piston'})

            # x:783 y:111
            OperatableStateMachine.add('PistonExtend',
                                       PistonMoveToPosState(id=ESP_ID,
                                                            timeout=10.0,
                                                            action_topic='/esp/move_to_pos'),
                                       transitions={'move_complete': 'finished'  # 960 130 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 614 260 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 614 260 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 614 260 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'piston', 'duration': 'duration'})

            # x:323 y:115
            OperatableStateMachine.add('PistonRetract',
                                       PistonMoveToPosState(id=ESP_ID,
                                                            timeout=10.0,
                                                            action_topic='/esp/move_to_pos'),
                                       transitions={'move_complete': 'PistonsExtended'  # 509 124 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 362 247 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 362 247 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 362 247 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'piston', 'duration': 'duration'})

            # x:575 y:113
            OperatableStateMachine.add('PistonsExtended',
                                       UserdataState(data=100.0),
                                       transitions={'done': 'PistonExtend'  # 731 122 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'piston'})

        # x:59 y:432, x:169 y:430
        _sm_findsection_2 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_findsection_2:
            # x:99 y:103
            OperatableStateMachine.add('MockFindSection',
                                       LogState(text="TODO: Cable find section here",
                                                severity=2),
                                       transitions={'done': 'SelectRotationMotor'  # 151 171 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:61 y:291
            OperatableStateMachine.add('Perform GUI Offset',
                                       self.use_behavior(PerformGUIOffsetSM, 'Unstrand/MoveMotors/FindSection/Perform GUI Offset'),
                                       transitions={'finished': 'finished'  # 60 400 101 350 -1 -1
                                                    , 'failed': 'failed'  # 138 388 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'motor_id': 'motor_id'})

            # x:100 y:196
            OperatableStateMachine.add('SelectRotationMotor',
                                       UserdataState(data=ROTATION_MOTOR),
                                       transitions={'done': 'Perform GUI Offset'  # 132 262 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'motor_id'})

        # x:60 y:524, x:192 y:508
        _sm_findcableend_3 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_findcableend_3:
            # x:78 y:81
            OperatableStateMachine.add('MockFindEnd',
                                       LogState(text="TODO: Find cable end here",
                                                severity=2),
                                       transitions={'done': 'SelectGantryMotor'  # 136 161 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:48 y:357
            OperatableStateMachine.add('Perform GUI Offset',
                                       self.use_behavior(PerformGUIOffsetSM, 'Unstrand/MoveMotors/FindCableEnd/Perform GUI Offset'),
                                       transitions={'finished': 'finished'  # 91 475 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 149 450 143 416 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'motor_id': 'motor_id'})

            # x:79 y:207
            OperatableStateMachine.add('SelectGantryMotor',
                                       UserdataState(data=GANTRY_MOTOR),
                                       transitions={'done': 'Perform GUI Offset'  # 124 290 111 260 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'motor_id'})

        # x:1303 y:197, x:379 y:721
        _sm_movemotors_4 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_movemotors_4:
            # x:25 y:133
            OperatableStateMachine.add('FindCableEnd',
                                       _sm_findcableend_3,
                                       transitions={'finished': 'Grip'  # 156 116 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 245 466 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:868 y:489
            OperatableStateMachine.add('CalculateNewRotation',
                                       CalculationState(calculation=lambda x: x + self.degrees_to_rotations(60.0)),
                                       transitions={'done': 'MoveToNext'  # 773 496 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'rotation_motor_position',
                                                  'output_value': 'rotation_motor_position'})

            # x:330 y:124
            OperatableStateMachine.add('FindSection',
                                       _sm_findsection_2,
                                       transitions={'finished': 'GetRotation'  # 473 121 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 362 455 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:511 y:121
            OperatableStateMachine.add('GetRotation',
                                       MotorGetStateState(motor=ROTATION_MOTOR,
                                                          get_state_topic='/odesc/get_state'),
                                       transitions={'state_acquired': 'LoopStart'  # 664 93 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 390 485 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'rotation_motor_position',
                                                  'motor_error': 'motor_error'})

            # x:176 y:128
            OperatableStateMachine.add('Grip',
                                       GripperExtendState(id=ESP_ID,
                                                          extended=True,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'FindSection'  # 316 105 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 337 504 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:848 y:122
            OperatableStateMachine.add('LoopCheckEnd',
                                       CheckConditionState(predicate=lambda x: x == 0),
                                       transitions={'true': 'Ungrip'  # 1045 130 -1 -1 -1 -1
                                                    , 'false': 'SplitCable'  # 885 211 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'loop_it'})

            # x:589 y:281
            OperatableStateMachine.add('LoopIterate',
                                       CalculationState(calculation=lambda x: x - 1),
                                       transitions={'done': 'LoopCheckEnd'  # 737 210 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'loop_it',
                                                  'output_value': 'loop_it'})

            # x:695 y:114
            OperatableStateMachine.add('LoopStart',
                                       UserdataState(data=3),
                                       transitions={'done': 'LoopCheckEnd'  # 812 116 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'loop_it'})

            # x:555 y:494
            OperatableStateMachine.add('MoveToNext',
                                       MotorMoveToPosState(id=ROTATION_MOTOR,
                                                           timeout=10.0,
                                                           action_topic='/odesc/move_to_pos',
                                                           setup_topic='/odesc/setup'),
                                       transitions={'move_complete': 'LoopIterate'  # 646 402 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 490 616 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 490 616 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 490 616 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'rotation_motor_position',
                                                  'duration': 'duration'})

            # x:928 y:277
            OperatableStateMachine.add('SplitCable',
                                       _sm_splitcable_1,
                                       transitions={'finished': 'CalculateNewRotation'  # 888 430 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 664 680 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:1078 y:131
            OperatableStateMachine.add('Ungrip',
                                       GripperExtendState(id=ESP_ID,
                                                          extended=False,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'finished'  # 1272 164 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 1026 657 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

        # x:30 y:400, x:130 y:400, x:556 y:388, x:653 y:391, x:454 y:471, x:226 y:384
        _sm_unstrand_5 = ConcurrencyContainer(outcomes=['finished', 'failed'],
                                              conditions=[('failed', [('WaitCancel', 'finished')]),
                                                          ('failed', [('WaitCancel', 'failed')]),
                                                          ('finished', [('MoveMotors', 'finished')]),
                                                          ('failed', [('MoveMotors', 'failed')])
                                                          ])

        with _sm_unstrand_5:
            # x:523 y:137
            OperatableStateMachine.add('MoveMotors',
                                       _sm_movemotors_4,
                                       transitions={'finished': 'finished', 'failed': 'failed'},
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:127 y:136
            OperatableStateMachine.add('WaitCancel',
                                       _sm_waitcancel_0,
                                       transitions={'finished': 'failed', 'failed': 'failed'},
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

        # x:1295 y:260, x:130 y:400
        _sm_homing_6 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_homing_6:
            # x:70 y:79
            OperatableStateMachine.add('WaitForGUI',
                                       SubscriberState(topic='/gui/home',
                                                       msg_type=Empty,
                                                       blocking=True,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'Grip'  # 191 82 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 99 268 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'message'})

            # x:228 y:83
            OperatableStateMachine.add('Grip',
                                       GripperExtendState(id=ESP_ID,
                                                          extended=True,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'PistonExtended'  # 412 72 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 186 265 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:1169 y:100
            OperatableStateMachine.add('HomeDisk',
                                       MotorHomeState(id=ROTATION_MOTOR,
                                                      timeout=-1,
                                                      delay=0.2,
                                                      homing_topic='/odesc/home',
                                                      get_state_topic='/odesc/get_state'),
                                       transitions={'state_set': 'finished'  # 1269 189 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 661 280 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 661 280 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off,
                                                 'timeout': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:956 y:96
            OperatableStateMachine.add('HomeGantry',
                                       MotorHomeState(id=GANTRY_MOTOR,
                                                      timeout=-1,
                                                      delay=0.2,
                                                      homing_topic='/odesc/home',
                                                      get_state_topic='/odesc/get_state'),
                                       transitions={'state_set': 'HomeDisk'  # 1138 96 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 567 276 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 567 276 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off,
                                                 'timeout': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:442 y:83
            OperatableStateMachine.add('PistonExtended',
                                       UserdataState(data=100.0),
                                       transitions={'done': 'PistonMove'  # 569 81 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'piston'})

            # x:598 y:80
            OperatableStateMachine.add('PistonMove',
                                       PistonMoveToPosState(id=ESP_ID,
                                                            timeout=10.0,
                                                            action_topic='/esp/move_to_pos'),
                                       transitions={'move_complete': 'Ungrip'  # 751 56 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 368 273 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 368 273 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 368 273 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'piston', 'duration': 'duration'})

            # x:778 y:81
            OperatableStateMachine.add('Ungrip',
                                       GripperExtendState(id=ESP_ID,
                                                          extended=False,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'HomeGantry'  # 952 68 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 459 302 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

        with _state_machine:
            # x:118 y:143
            OperatableStateMachine.add('Homing',
                                       _sm_homing_6,
                                       transitions={'finished': 'WaitForGUI'  # 308 158 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 135 320 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:616 y:147
            OperatableStateMachine.add('Unstrand',
                                       _sm_unstrand_5,
                                       transitions={'finished': 'finished'  # 766 167 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 385 296 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:378 y:127
            OperatableStateMachine.add('WaitForGUI',
                                       SubscriberState(topic='/gui/start',
                                                       msg_type=Empty,
                                                       blocking=True,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'Unstrand'  # 552 155 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 258 283 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'message'})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]
    @staticmethod
    def degrees_to_rotations(x: float):
        return x / 360.0 * 270.833

    @staticmethod
    def millimeters_to_rotations(x: float):
        return x * 2.0



    # [/MANUAL_FUNC]
