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
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_behaviors.cable_detect_yup_sm import cable_detect_yupSM
from qbert_fsm_flexbe_behaviors.perform_gui_offset_sm import PerformGUIOffsetSM
from qbert_fsm_flexbe_behaviors.request_gui_confirm_sm import RequestGUIConfirmSM
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
        self.add_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/FindCableEnd/Request GUI Confirm', node)
        self.add_behavior(cable_detect_yupSM, 'Unstrand/MoveMotors/FindCableEnd/cable_detect_yup', node)
        self.add_behavior(PerformGUIOffsetSM, 'Unstrand/MoveMotors/FindSection/Perform GUI Offset', node)
        self.add_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/FindSection/Request GUI Confirm', node)
        self.add_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/MoveBackToHome/Request GUI Confirm', node)
        self.add_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/MoveToNext/Request GUI Confirm', node)
        self.add_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/SplitCable/Request GUI Confirm', node)
        self.add_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/SplitCable/Request GUI Confirm_2', node)

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
        _state_machine.userdata.user_progress = 0

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

        # x:1051 y:497, x:651 y:427
        _sm_splitcable_1 = OperatableStateMachine(outcomes=['finished', 'failed'],
                                                  input_keys=['progress'],
                                                  output_keys=['progress'])

        with _sm_splitcable_1:
            # x:227 y:46
            OperatableStateMachine.add('UpdateProgress',
                                       CalculationState(calculation=lambda x: x + 5),
                                       transitions={'done': 'Request GUI Confirm'  # 263 132 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'progress',
                                                  'output_value': 'progress'})

            # x:1001 y:349
            OperatableStateMachine.add('PistonExtend',
                                       PistonMoveToPosState(id=ESP_ID,
                                                            timeout=10.0,
                                                            action_topic='/esp/move_to_pos'),
                                       transitions={'move_complete': 'finished'  # 1034 434 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 834 398 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 834 398 -1 -1 -1 -1
                                                    , 'timeout': 'finished'  # 1034 434 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'piston', 'duration': 'duration'})

            # x:310 y:383
            OperatableStateMachine.add('PistonRetract',
                                       PistonMoveToPosState(id=ESP_ID,
                                                            timeout=10.0,
                                                            action_topic='/esp/move_to_pos'),
                                       transitions={'move_complete': 'UpdateProgress2'  # 646 237 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 550 429 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 550 429 -1 -1 -1 -1
                                                    , 'timeout': 'UpdateProgress2'  # 646 237 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'piston', 'duration': 'duration'})

            # x:1011 y:244
            OperatableStateMachine.add('PistonsExtended',
                                       UserdataState(data=100.0),
                                       transitions={'done': 'PistonExtend'  # 1052 321 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'piston'})

            # x:315 y:274
            OperatableStateMachine.add('PistonsRetracted',
                                       UserdataState(data=0.0),
                                       transitions={'done': 'PistonRetract'  # 362 361 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'piston'})

            # x:287 y:144
            OperatableStateMachine.add('Request GUI Confirm',
                                       self.use_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/SplitCable/Request GUI Confirm',
                                                         parameters={'confirm_string': "Pistons will drive axe into cable"}),
                                       transitions={'finished': 'PistonsRetracted'  # 363 236 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 553 310 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

            # x:965 y:116
            OperatableStateMachine.add('Request GUI Confirm_2',
                                       self.use_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/SplitCable/Request GUI Confirm_2',
                                                         parameters={'confirm_string': "Pistons will take axe out from the cable"}),
                                       transitions={'finished': 'PistonsExtended'  # 1050 209 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 819 294 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

            # x:848 y:50
            OperatableStateMachine.add('UpdateProgress2',
                                       CalculationState(calculation=lambda x: x + 5),
                                       transitions={'done': 'Request GUI Confirm_2'  # 992 104 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'progress',
                                                  'output_value': 'progress'})

        # x:165 y:559, x:637 y:240
        _sm_movetonext_2 = OperatableStateMachine(outcomes=['finished', 'failed'],
                                                  input_keys=['rotation_motor_position', 'progress'],
                                                  output_keys=['rotation_motor_position', 'progress'])

        with _sm_movetonext_2:
            # x:109 y:63
            OperatableStateMachine.add('UpdateProgress',
                                       CalculationState(calculation=lambda x: x + 5),
                                       transitions={'done': 'Request GUI Confirm'  # 155 151 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'progress',
                                                  'output_value': 'progress'})

            # x:258 y:329
            OperatableStateMachine.add('CalculateNext',
                                       CalculationState(calculation=lambda x: (x + self.degrees_to_rotations(60.0)) % self.degrees_to_rotations(360.0)),
                                       transitions={'done': 'MoveToNext'  # 359 481 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'rotation_motor_position',
                                                  'output_value': 'rotation_motor_position'})

            # x:375 y:520
            OperatableStateMachine.add('MoveToNext',
                                       MotorMoveToPosState(id=ROTATION_MOTOR,
                                                           timeout=40.0,
                                                           action_topic='/odesc/move_to_pos',
                                                           setup_topic='/odesc/setup'),
                                       transitions={'move_complete': 'finished'  # 293 546 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 584 344 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 584 344 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 584 344 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'rotation_motor_position',
                                                  'duration': 'duration'})

            # x:198 y:151
            OperatableStateMachine.add('Request GUI Confirm',
                                       self.use_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/MoveToNext/Request GUI Confirm',
                                                         parameters={'confirm_string': "Robot will move to the next section"}),
                                       transitions={'finished': 'CalculateNext'  # 238 285 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 533 200 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

        # x:1043 y:216, x:130 y:400
        _sm_movebacktohome_3 = OperatableStateMachine(outcomes=['finished', 'failed'],
                                                      input_keys=['progress'])

        with _sm_movebacktohome_3:
            # x:126 y:52
            OperatableStateMachine.add('SetProgress',
                                       UserdataState(data=100.0),
                                       transitions={'done': 'Request GUI Confirm'  # 232 116 -1 -1 232 139
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'progress'})

            # x:483 y:182
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=3),
                                       transitions={'done': 'SetHomePosition'  # 618 182 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:841 y:184
            OperatableStateMachine.add('MoveToHome',
                                       MotorMoveToPosState(id=GANTRY_MOTOR,
                                                           timeout=60.0,
                                                           action_topic='/odesc/move_to_pos',
                                                           setup_topic='/odesc/setup'),
                                       transitions={'move_complete': 'finished'  # 1009 175 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 492 315 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 492 315 -1 -1 -1 -1
                                                    , 'timeout': 'failed'  # 492 315 -1 -1 -1 -1
                                                    },
                                       autonomy={'move_complete': Autonomy.Off,
                                                 'failed': Autonomy.Off,
                                                 'canceled': Autonomy.Off,
                                                 'timeout': Autonomy.Off},
                                       remapping={'position': 'gantry_position',
                                                  'duration': 'duration'})

            # x:141 y:140
            OperatableStateMachine.add('Request GUI Confirm',
                                       self.use_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/MoveBackToHome/Request GUI Confirm',
                                                         parameters={'confirm_string': "Robot will back to the homed position"}),
                                       transitions={'finished': 'Ungrip'  # 350 208 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 133 254 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

            # x:652 y:192
            OperatableStateMachine.add('SetHomePosition',
                                       UserdataState(data=0.0),
                                       transitions={'done': 'MoveToHome'  # 810 192 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'gantry_position'})

            # x:291 y:232
            OperatableStateMachine.add('Ungrip',
                                       GripperExtendState(id=ESP_ID,
                                                          extended=False,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'Delay'  # 442 201 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 162 343 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

        # x:152 y:543, x:626 y:296
        _sm_findsection_4 = OperatableStateMachine(outcomes=['finished', 'failed'],
                                                   input_keys=['progress'],
                                                   output_keys=['progress'])

        with _sm_findsection_4:
            # x:132 y:75
            OperatableStateMachine.add('UpdateProgress',
                                       CalculationState(calculation=lambda x: x + 10),
                                       transitions={'done': 'Request GUI Confirm'  # 194 155 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'progress',
                                                  'output_value': 'progress'})

            # x:209 y:294
            OperatableStateMachine.add('MockFindSection',
                                       LogState(text="TODO: Cable find section here",
                                                severity=2),
                                       transitions={'done': 'Perform GUI Offset'  # 268 360 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:178 y:376
            OperatableStateMachine.add('Perform GUI Offset',
                                       self.use_behavior(PerformGUIOffsetSM, 'Unstrand/MoveMotors/FindSection/Perform GUI Offset',
                                                         parameters={'motor_id': ROTATION_MOTOR}),
                                       transitions={'finished': 'finished'  # 219 518 218 435 -1 -1
                                                    , 'failed': 'failed'  # 497 320 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:149 y:189
            OperatableStateMachine.add('Request GUI Confirm',
                                       self.use_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/FindSection/Request GUI Confirm',
                                                         parameters={'confirm_string': "Robot will start looking for the section split"}),
                                       transitions={'finished': 'MockFindSection'  # 243 266 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 501 249 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

        # x:872 y:140, x:591 y:625
        _sm_findcableend_5 = OperatableStateMachine(outcomes=['finished', 'failed'],
                                                    input_keys=['progress'],
                                                    output_keys=['progress'])

        with _sm_findcableend_5:
            # x:141 y:73
            OperatableStateMachine.add('UpdateProgress',
                                       CalculationState(calculation=lambda x: x + 10),
                                       transitions={'done': 'Request GUI Confirm'  # 159 146 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'progress',
                                                  'output_value': 'progress'})

            # x:647 y:95
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=3),
                                       transitions={'done': 'finished'  # 795 101 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:575 y:246
            OperatableStateMachine.add('Grip',
                                       GripperExtendState(id=ESP_ID,
                                                          extended=True,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'Delay'  # 651 183 -1 -1 681 148
                                                    , 'failed': 'failed'  # 620 472 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:242 y:423
            OperatableStateMachine.add('Perform GUI Offset',
                                       self.use_behavior(PerformGUIOffsetSM, 'Unstrand/MoveMotors/FindCableEnd/Perform GUI Offset',
                                                         parameters={'motor_id': GANTRY_MOTOR}),
                                       transitions={'finished': 'Grip'  # 465 384 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 488 547 337 482 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:183 y:160
            OperatableStateMachine.add('Request GUI Confirm',
                                       self.use_behavior(RequestGUIConfirmSM, 'Unstrand/MoveMotors/FindCableEnd/Request GUI Confirm',
                                                         parameters={'confirm_string': "Robot will start finding the cable end"}),
                                       transitions={'finished': 'cable_detect_yup'  # 205 259 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 191 560 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

            # x:227 y:288
            OperatableStateMachine.add('cable_detect_yup',
                                       self.use_behavior(cable_detect_yupSM, 'Unstrand/MoveMotors/FindCableEnd/cable_detect_yup'),
                                       transitions={'finished': 'Perform GUI Offset'  # 299 414 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 499 486 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

        # x:1282 y:490, x:379 y:721
        _sm_movemotors_6 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_movemotors_6:
            # x:36 y:110
            OperatableStateMachine.add('SetProgress',
                                       UserdataState(data=0.0),
                                       transitions={'done': 'FindCableEnd'  # 152 98 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'progress'})

            # x:163 y:123
            OperatableStateMachine.add('FindCableEnd',
                                       _sm_findcableend_5,
                                       transitions={'finished': 'FindSection'  # 307 100 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 298 462 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

            # x:324 y:122
            OperatableStateMachine.add('FindSection',
                                       _sm_findsection_4,
                                       transitions={'finished': 'GetRotation'  # 471 144 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 360 453 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

            # x:511 y:121
            OperatableStateMachine.add('GetRotation',
                                       MotorGetStateState(motor=ROTATION_MOTOR,
                                                          get_state_topic='/odesc/get_state'),
                                       transitions={'state_acquired': 'LoopStart'  # 666 99 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 390 485 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'rotation_motor_position',
                                                  'motor_error': 'motor_error'})

            # x:848 y:122
            OperatableStateMachine.add('LoopCheckEnd',
                                       CheckConditionState(predicate=lambda x: x == 0),
                                       transitions={'true': 'MoveBackToHome'  # 1019 119 -1 -1 -1 -1
                                                    , 'false': 'SplitCable'  # 945 218 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'loop_it'})

            # x:692 y:262
            OperatableStateMachine.add('LoopIterate',
                                       CalculationState(calculation=lambda x: x - 1),
                                       transitions={'done': 'LoopCheckEnd'  # 781 199 757 261 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'loop_it',
                                                  'output_value': 'loop_it'})

            # x:695 y:114
            OperatableStateMachine.add('LoopStart',
                                       UserdataState(data=6),
                                       transitions={'done': 'LoopCheckEnd'  # 812 116 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'loop_it'})

            # x:1076 y:108
            OperatableStateMachine.add('MoveBackToHome',
                                       _sm_movebacktohome_3,
                                       transitions={'finished': 'finished'  # 1266 324 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 1002 664 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

            # x:789 y:409
            OperatableStateMachine.add('MoveToNext',
                                       _sm_movetonext_2,
                                       transitions={'finished': 'LoopIterate'  # 759 372 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 589 590 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'rotation_motor_position': 'rotation_motor_position',
                                                  'progress': 'progress'})

            # x:928 y:277
            OperatableStateMachine.add('SplitCable',
                                       _sm_splitcable_1,
                                       transitions={'finished': 'MoveToNext'  # 948 387 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 1009 590 1012 336 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit},
                                       remapping={'progress': 'progress'})

        # x:30 y:400, x:130 y:400, x:556 y:388, x:653 y:391, x:454 y:471, x:226 y:384
        _sm_unstrand_7 = ConcurrencyContainer(outcomes=['finished', 'failed'],
                                              conditions=[('failed', [('WaitCancel', 'finished')]),
                                                          ('failed', [('WaitCancel', 'failed')]),
                                                          ('finished', [('MoveMotors', 'finished')]),
                                                          ('failed', [('MoveMotors', 'failed')])
                                                          ])

        with _sm_unstrand_7:
            # x:523 y:137
            OperatableStateMachine.add('MoveMotors',
                                       _sm_movemotors_6,
                                       transitions={'finished': 'finished', 'failed': 'failed'},
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:127 y:136
            OperatableStateMachine.add('WaitCancel',
                                       _sm_waitcancel_0,
                                       transitions={'finished': 'failed', 'failed': 'failed'},
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

        # x:1295 y:260, x:167 y:490
        _sm_homing_8 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_homing_8:
            # x:70 y:79
            OperatableStateMachine.add('WaitForGUI',
                                       SubscriberState(topic='/gui/home',
                                                       msg_type=Empty,
                                                       blocking=True,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'Grip'  # 191 82 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 117 321 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'message'})

            # x:353 y:168
            OperatableStateMachine.add('Delay1',
                                       WaitState(wait_time=1),
                                       transitions={'done': 'PistonExtended'  # 465 165 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:869 y:164
            OperatableStateMachine.add('Delay2',
                                       WaitState(wait_time=2),
                                       transitions={'done': 'HomeGantry'  # 979 172 -1 -1 1016 149
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:228 y:83
            OperatableStateMachine.add('Grip',
                                       GripperExtendState(id=ESP_ID,
                                                          extended=True,
                                                          gripper_topic='/esp/gripper_state'),
                                       transitions={'gripper_moved': 'Delay1'  # 303 165 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 202 317 -1 -1 -1 -1
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
                                                    , 'timeout': 'failed'  # 679 334 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 679 334 -1 -1 -1 -1
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
                                                    , 'timeout': 'failed'  # 584 329 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 584 329 -1 -1 -1 -1
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
                                                            timeout=5.0,
                                                            action_topic='/esp/move_to_pos'),
                                       transitions={'move_complete': 'Ungrip'  # 764 39 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 386 327 -1 -1 -1 -1
                                                    , 'canceled': 'failed'  # 386 327 -1 -1 -1 -1
                                                    , 'timeout': 'Ungrip'  # 764 39 -1 -1 -1 -1
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
                                       transitions={'gripper_moved': 'Delay2'  # 823 157 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 477 364 -1 -1 -1 -1
                                                    },
                                       autonomy={'gripper_moved': Autonomy.Off,
                                                 'failed': Autonomy.Off})

        with _state_machine:
            # x:118 y:143
            OperatableStateMachine.add('Homing',
                                       _sm_homing_8,
                                       transitions={'finished': 'WaitForGUI'  # 308 158 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 135 320 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:616 y:147
            OperatableStateMachine.add('Unstrand',
                                       _sm_unstrand_7,
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
