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
from flexbe_states.log_key_state import LogKeyState
from flexbe_states.log_state import LogState
from flexbe_states.subscriber_state import SubscriberState
from flexbe_states.user_data_state import UserdataState
from flexbe_states.wait_state import WaitState
from qbert_fsm_flexbe_states.get_motor_state_state import GetMotorStateState
from qbert_fsm_flexbe_states.set_motor_state_state import SetMotorStateState
from qbert_fsm_flexbe_states.set_motor_vel_state import SetMotorVelState

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

        # Root state machine
        # x:1237 y:101, x:1199 y:651
        _state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
        _state_machine.userdata.gantry_position = 0.0
        _state_machine.userdata.rotation_position = 0.0

        # Additional creation code can be added inside the following tags
        # [MANUAL_CREATE]


        # [/MANUAL_CREATE]

        # x:892 y:332, x:130 y:400
        _sm_waitforstart_0 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_waitforstart_0:
            # x:305 y:111
            OperatableStateMachine.add('SubscribeGUIStart',
                                       SubscriberState(topic='/gui_start',
                                                       msg_type=Empty,
                                                       blocking=False,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'CheckMessageReceived'  # 473 151 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 220 282 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'start_message'})

            # x:522 y:134
            OperatableStateMachine.add('CheckMessageReceived',
                                       CheckConditionState(predicate=lambda x: x is not None),
                                       transitions={'true': 'Log'  # 630 201 -1 -1 -1 -1
                                                    , 'false': 'Delay'  # 561 274 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'start_message'})

            # x:400 y:315
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.2),
                                       transitions={'done': 'SubscribeGUIStart'  # 323 241 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:706 y:222
            OperatableStateMachine.add('Log',
                                       LogState(text="Received start command",
                                                severity=2),
                                       transitions={'done': 'finished'  # 831 298 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

        # x:864 y:141, x:679 y:505
        _sm_waitforhomingclicked_1 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_waitforhomingclicked_1:
            # x:149 y:104
            OperatableStateMachine.add('CheckHomingGUI',
                                       SubscriberState(topic="/gui_home",
                                                       msg_type=Empty,
                                                       blocking=False,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'MessageReceived'  # 320 96 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 475 343 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'homing_message'})

            # x:269 y:278
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'CheckHomingGUI'  # 189 245 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:636 y:93
            OperatableStateMachine.add('LogResponse',
                                       LogKeyState(text="Received message: {}",
                                                   severity=2),
                                       transitions={'done': 'finished'  # 813 129 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'homing_message'})

            # x:369 y:64
            OperatableStateMachine.add('MessageReceived',
                                       CheckConditionState(predicate=lambda x: x is not None),
                                       transitions={'true': 'LogResponse'  # 594 74 -1 -1 -1 -1
                                                    , 'false': 'Delay'  # 398 193 415 117 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'homing_message'})

        # x:942 y:184, x:933 y:428
        _sm_homerobot_2 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_homerobot_2:
            # x:191 y:172
            OperatableStateMachine.add('SetGantryIntoHomingState',
                                       SetMotorStateState(id=GANTRY_MOTOR,
                                                          desired_state='homing',
                                                          homing_topic='/odesc/home',
                                                          setup_topic='/odesc/setup',
                                                          id_arm_topic='/odesc/ready'),
                                       transitions={'state_set': 'Delay'  # 342 111 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 554 485 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:477 y:265
            OperatableStateMachine.add('CheckError',
                                       CheckConditionState(predicate=lambda x: x == AxisState.UNDEFINED),
                                       transitions={'true': 'failed'  # 802 393 -1 -1 -1 -1
                                                    , 'false': 'Delay'  # 450 225 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'motor_state'})

            # x:644 y:204
            OperatableStateMachine.add('CheckHomingComplete',
                                       CheckConditionState(predicate=lambda x: x == AxisState.IDLE),
                                       transitions={'true': 'finished'  # 864 204 -1 -1 -1 -1
                                                    , 'false': 'CheckError'  # 601 234 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'motor_state'})

            # x:398 y:75
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.2),
                                       transitions={'done': 'WaitForHoming'  # 457 63 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:587 y:49
            OperatableStateMachine.add('WaitForHoming',
                                       GetMotorStateState(motor=1,
                                                          get_state_topic='/get_motor_state'),
                                       transitions={'state_acquired': 'CheckHomingComplete'  # 670 160 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 826 265 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_state',
                                                  'motor_position': 'motor_position',
                                                  'motor_error': 'motor_error'})

        # x:219 y:456, x:665 y:484
        _sm_waitforcancel_3 = OperatableStateMachine(outcomes=['failed', 'cancelled'])

        with _sm_waitforcancel_3:
            # x:266 y:85
            OperatableStateMachine.add('SubscribeCancelled',
                                       SubscriberState(topic='/gui_cancel',
                                                       msg_type=Empty,
                                                       blocking=False,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'CheckCancelled'  # 457 175 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 231 306 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'cancel_message'})

            # x:479 y:207
            OperatableStateMachine.add('CheckCancelled',
                                       CheckConditionState(predicate=lambda x: x is not None),
                                       transitions={'true': 'cancelled'  # 569 379 -1 -1 -1 -1
                                                    , 'false': 'Delay'  # 444 277 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'cancel_message'})

            # x:296 y:254
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'SubscribeCancelled'  # 288 191 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

        # x:30 y:400, x:130 y:400
        _sm_splitcablewithaxe_4 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_splitcablewithaxe_4:
            # x:200 y:96
            OperatableStateMachine.add('MockDriveAxe',
                                       LogState(text="TODO: Driving axe into cable here",
                                                severity=2),
                                       transitions={'done': 'Delay'  # 235 188 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:213 y:208
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=2.0),
                                       transitions={'done': 'finished'  # 127 323 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

        # x:128 y:627, x:360 y:650
        _sm_rotatedisktoposition_5 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_rotatedisktoposition_5:
            # x:246 y:126
            OperatableStateMachine.add('MockRotateDisk',
                                       LogState(text="TODO: Rotate the disk into position",
                                                severity=2),
                                       transitions={'done': 'Delay'  # 205 326 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:139 y:412
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'finished'  # 134 542 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

        # x:918 y:492, x:130 y:400
        _sm_findsectionsplit_6 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_findsectionsplit_6:
            # x:107 y:117
            OperatableStateMachine.add('SetStateVel',
                                       SetMotorStateState(id=ROTATION_MOTOR,
                                                          desired_state='velocity',
                                                          homing_topic='/odesc/home',
                                                          setup_topic='/odesc/setup',
                                                          id_arm_topic='/odesc/ready'),
                                       transitions={'state_set': 'StartSearch'  # 296 133 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 120 280 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:507 y:463
            OperatableStateMachine.add('CheckCamera',
                                       CheckConditionState(predicate=lambda x: x),
                                       transitions={'true': 'ResetVelocity'  # 694 481 -1 -1 -1 -1
                                                    , 'false': 'Delay'  # 380 358 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'split_detected'})

            # x:569 y:250
            OperatableStateMachine.add('CheckMotor',
                                       CheckConditionState(predicate=lambda x: x == AxisState.CLOSED_LOOP_CONTROL),
                                       transitions={'true': 'MockGetCameraState'  # 715 268 -1 -1 -1 -1
                                                    , 'false': 'StopMotor'  # 481 412 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'motor_axis_state'})

            # x:236 y:250
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'StartSearch'  # 264 219 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:587 y:133
            OperatableStateMachine.add('GetState',
                                       GetMotorStateState(motor=ROTATION_MOTOR,
                                                          get_state_topic='/get_motor_state'),
                                       transitions={'state_acquired': 'CheckMotor'  # 630 230 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 360 291 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_acquired': Autonomy.Off,
                                                 'failed': Autonomy.Off},
                                       remapping={'motor_axis_state': 'motor_axis_state',
                                                  'motor_position': 'motor_position',
                                                  'motor_error': 'motor_error'})

            # x:743 y:261
            OperatableStateMachine.add('MockGetCameraState',
                                       LogState(text="TODO: load state from camera",
                                                severity=2),
                                       transitions={'done': 'MockSetCamera'  # 704 343 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:616 y:365
            OperatableStateMachine.add('MockSetCamera',
                                       UserdataState(data=True),
                                       transitions={'done': 'CheckCamera'  # 580 427 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'split_detected'})

            # x:731 y:473
            OperatableStateMachine.add('ResetVelocity',
                                       SetMotorVelState(id=ROTATION_MOTOR,
                                                        target_velocity=0.0,
                                                        vel_topic='/move_with_velocity'),
                                       transitions={'velocity_set': 'StopSearch'  # 789 432 -1 -1 -1 -1
                                                    , 'failed': 'StopMotor'  # 665 518 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:118 y:544
            OperatableStateMachine.add('ResetVelocity2',
                                       SetMotorVelState(id=ROTATION_MOTOR,
                                                        target_velocity=0.0,
                                                        vel_topic='/move_with_velocity'),
                                       transitions={'velocity_set': 'failed'  # 126 496 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 126 496 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:348 y:125
            OperatableStateMachine.add('StartSearch',
                                       SetMotorVelState(id=ROTATION_MOTOR,
                                                        target_velocity=5.0,
                                                        vel_topic='/move_with_velocity'),
                                       transitions={'velocity_set': 'GetState'  # 528 132 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 243 279 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:333 y:514
            OperatableStateMachine.add('StopMotor',
                                       SetMotorStateState(id=ROTATION_MOTOR,
                                                          desired_state='inactive',
                                                          homing_topic='/odesc/home',
                                                          setup_topic='/odesc/setup',
                                                          id_arm_topic='/odesc/ready'),
                                       transitions={'state_set': 'ResetVelocity2'  # 285 573 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 291 440 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:822 y:363
            OperatableStateMachine.add('StopSearch',
                                       SetMotorStateState(id=ROTATION_MOTOR,
                                                          desired_state='inactive',
                                                          homing_topic='/odesc/home',
                                                          setup_topic='/odesc/setup',
                                                          id_arm_topic='/odesc/ready'),
                                       transitions={'state_set': 'finished'  # 898 454 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 481 387 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

        # x:1222 y:159, x:130 y:400
        _sm_findcableend_7 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_findcableend_7:
            # x:196 y:107
            OperatableStateMachine.add('SetVelocityMode',
                                       SetMotorStateState(id=GANTRY_MOTOR,
                                                          desired_state='velocity',
                                                          homing_topic='/odesc/home',
                                                          setup_topic='/odesc/setup',
                                                          id_arm_topic='/odesc/ready'),
                                       transitions={'state_set': 'StartSearch'  # 345 96 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 165 283 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:908 y:97
            OperatableStateMachine.add('CheckCableEndFound',
                                       CheckConditionState(predicate=""),
                                       transitions={'true': 'StopSearch'  # 952 188 -1 -1 -1 -1
                                                    , 'false': 'GetPosition'  # 875 211 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'cable_end_message'})

            # x:556 y:395
            OperatableStateMachine.add('CheckPositionInBounds',
                                       CheckConditionState(predicate=lambda x: x > GANTRY_MIN and x < GANTRY_MAX),
                                       transitions={'true': 'Delay'  # 545 315 -1 -1 -1 -1
                                                    , 'false': 'StopMotor'  # 598 500 -1 -1 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'gantry_position'})

            # x:557 y:218
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=0.1),
                                       transitions={'done': 'SubscribeCameraFoundEnd'  # -1 -1 592 217 679 144
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:801 y:290
            OperatableStateMachine.add('GetPosition',
                                       LogState(text="TODO: Getting motor position here",
                                                severity=2),
                                       transitions={'done': 'SetMockPosition'  # 788 391 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:244 y:479
            OperatableStateMachine.add('NoCableFound',
                                       LogState(text="Couldn't find cable end",
                                                severity=2),
                                       transitions={'done': 'failed'  # 191 462 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:747 y:453
            OperatableStateMachine.add('SetMockPosition',
                                       UserdataState(data=0.0),
                                       transitions={'done': 'CheckPositionInBounds'  # 708 501 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'gantry_position'})

            # x:381 y:97
            OperatableStateMachine.add('StartSearch',
                                       SetMotorVelState(id=GANTRY_MOTOR,
                                                        target_velocity=5.0,
                                                        vel_topic='/move_with_velocity'),
                                       transitions={'velocity_set': 'SubscribeCameraFoundEnd',
                                                    'failed': 'failed'  # 260 272 -1 -1 -1 -1
                                                    },
                                       autonomy={'velocity_set': Autonomy.Off,
                                                 'failed': Autonomy.Off})

            # x:426 y:507
            OperatableStateMachine.add('StopMotor',
                                       SetMotorStateState(id=GANTRY_MOTOR,
                                                          desired_state='inactive',
                                                          homing_topic='/odesc/home',
                                                          setup_topic='/odesc/setup',
                                                          id_arm_topic='/odesc/ready'),
                                       transitions={'state_set': 'NoCableFound'  # 396 493 -1 -1 -1 -1
                                                    , 'failed': 'NoCableFound'  # 396 493 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:959 y:240
            OperatableStateMachine.add('StopSearch',
                                       SetMotorStateState(id=GANTRY_MOTOR,
                                                          desired_state='inactive',
                                                          homing_topic='/odesc/home',
                                                          setup_topic='/odesc/setup',
                                                          id_arm_topic='/odesc/ready'),
                                       transitions={'state_set': 'finished'  # 1145 207 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 549 360 -1 -1 -1 -1
                                                    },
                                       autonomy={'state_set': Autonomy.Off, 'failed': Autonomy.Off})

            # x:631 y:91
            OperatableStateMachine.add('SubscribeCameraFoundEnd',
                                       SubscriberState(topic='/camera_found_end',
                                                       msg_type=Empty,
                                                       blocking=False,
                                                       clear=False,
                                                       qos=QOS_DEFAULT),
                                       transitions={'received': 'CheckCableEndFound'  # 843 81 -1 -1 -1 -1
                                                    , 'unavailable': 'failed'  # 384 267 -1 -1 -1 -1
                                                    },
                                       autonomy={'received': Autonomy.Off,
                                                 'unavailable': Autonomy.Off},
                                       remapping={'message': 'cable_end_message'})

        # x:605 y:602, x:247 y:640
        _sm_cableunstranding_8 = OperatableStateMachine(outcomes=['finished', 'failed'])

        with _sm_cableunstranding_8:
            # x:77 y:99
            OperatableStateMachine.add('Delay',
                                       WaitState(wait_time=1.0),
                                       transitions={'done': 'FindCableEnd'  # 195 98 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:224 y:124
            OperatableStateMachine.add('FindCableEnd',
                                       _sm_findcableend_7,
                                       transitions={'finished': 'MockGripper'  # 316 91 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 239 433 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:464 y:182
            OperatableStateMachine.add('FindSectionSplit',
                                       _sm_findsectionsplit_6,
                                       transitions={'finished': 'SetSectionCount'  # 519 338 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 361 441 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:737 y:366
            OperatableStateMachine.add('Loop',
                                       CheckConditionState(predicate=lambda x: x < 6),
                                       transitions={'true': 'RotateDiskToPosition'  # 819 303 805 365 -1 -1
                                                    , 'false': 'finished'  # 711 478 794 419 -1 -1
                                                    },
                                       autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
                                       remapping={'input_value': 'unstranded_sections'})

            # x:346 y:59
            OperatableStateMachine.add('MockGripper',
                                       LogState(text="4 pistons grip the cable",
                                                severity=2),
                                       transitions={'done': 'FindSectionSplit'  # 438 130 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:832 y:193
            OperatableStateMachine.add('RotateDiskToPosition',
                                       _sm_rotatedisktoposition_5,
                                       transitions={'finished': 'SplitCableWithAxe'  # 1026 220 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 547 444 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:570 y:366
            OperatableStateMachine.add('SetSectionCount',
                                       UserdataState(data=0),
                                       transitions={'done': 'Loop'  # 706 393 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'data': 'unstranded_sections'})

            # x:1096 y:227
            OperatableStateMachine.add('SplitCableWithAxe',
                                       _sm_splitcablewithaxe_4,
                                       transitions={'finished': 'UnstandedSectionsInc'  # 1160 377 -1 -1 -1 -1
                                                    , 'failed': 'failed'  # 674 454 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:981 y:430
            OperatableStateMachine.add('UnstandedSectionsInc',
                                       CalculationState(calculation=lambda x: x + 1),
                                       transitions={'done': 'Loop'  # 910 408 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off},
                                       remapping={'input_value': 'unstranded_sections',
                                                  'output_value': 'unstranded_sections'})

        # x:120 y:480, x:586 y:471, x:433 y:527, x:107 y:542, x:431 y:479, x:429 y:577, x:582 y:530
        _sm_dounstranding_9 = ConcurrencyContainer(outcomes=['finished', 'cancelled', 'failed'],
                                                   conditions=[('finished', [('CableUnstranding', 'finished')]),
                                                               ('failed', [('CableUnstranding', 'failed')]),
                                                               ('failed', [('WaitForCancel', 'failed')]),
                                                               ('cancelled', [('WaitForCancel', 'cancelled')])
                                                               ])

        with _sm_dounstranding_9:
            # x:231 y:91
            OperatableStateMachine.add('CableUnstranding',
                                       _sm_cableunstranding_8,
                                       transitions={'finished': 'finished', 'failed': 'failed'},
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:548 y:84
            OperatableStateMachine.add('WaitForCancel',
                                       _sm_waitforcancel_3,
                                       transitions={'failed': 'failed', 'cancelled': 'cancelled'},
                                       autonomy={'failed': Autonomy.Inherit,
                                                 'cancelled': Autonomy.Inherit})

        with _state_machine:
            # x:110 y:55
            OperatableStateMachine.add('WaitForHomingClicked',
                                       _sm_waitforhomingclicked_1,
                                       transitions={'finished': 'HomeRobot'  # 297 50 -1 -1 -1 -1
                                                    , 'failed': 'LogError'  # 386 398 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:788 y:71
            OperatableStateMachine.add('DoUnstranding',
                                       _sm_dounstranding_9,
                                       transitions={'finished': 'LogMachineDone'  # 985 96 -1 -1 -1 -1
                                                    , 'cancelled': 'LogCancelled'  # 951 237 -1 -1 -1 -1
                                                    , 'failed': 'LogError'  # 659 391 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'cancelled': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:315 y:61
            OperatableStateMachine.add('HomeRobot',
                                       _sm_homerobot_2,
                                       transitions={'finished': 'WaitForStart'  # 498 66 -1 -1 -1 -1
                                                    , 'failed': 'LogError'  # 477 384 364 120 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

            # x:958 y:337
            OperatableStateMachine.add('LogCancelled',
                                       LogState(text="Process was cancelled",
                                                severity=2),
                                       transitions={'done': 'finished'  # 1131 236 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:488 y:619
            OperatableStateMachine.add('LogError',
                                       LogState(text="Error occured",
                                                severity=2),
                                       transitions={'done': 'failed'  # 904 632 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:1031 y:76
            OperatableStateMachine.add('LogMachineDone',
                                       LogState(text="State machine finished",
                                                severity=2),
                                       transitions={'done': 'finished'  # 1187 94 -1 -1 -1 -1
                                                    },
                                       autonomy={'done': Autonomy.Off})

            # x:554 y:65
            OperatableStateMachine.add('WaitForStart',
                                       _sm_waitforstart_0,
                                       transitions={'finished': 'DoUnstranding'  # 740 52 -1 -1 -1 -1
                                                    , 'failed': 'LogError'  # 531 376 -1 -1 -1 -1
                                                    },
                                       autonomy={'finished': Autonomy.Inherit,
                                                 'failed': Autonomy.Inherit})

        return _state_machine

    # Private functions can be added inside the following tags
    # [MANUAL_FUNC]


    # [/MANUAL_FUNC]
