#!/usr/bin/env python

from glob import glob
from setuptools import setup
from setuptools import find_packages

PACKAGE_NAME = 'qbert_fsm_flexbe_states'

setup(
    name=PACKAGE_NAME,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + PACKAGE_NAME]),
        ('share/' + PACKAGE_NAME, ['package.xml']),
        ('share/' + PACKAGE_NAME + "/tests", glob('tests/*.test')),
        ('share/' + PACKAGE_NAME + "/launch", glob('tests/*.launch.py')),
    ],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='TODO',
    maintainer_email='TODO@TODO.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'motor_clear_errors_state = qbert_fsm_flexbe_states.motor_clear_errors_state',
            'motor_get_state_state = qbert_fsm_flexbe_states.motor_get_state_state',
            'motor_stop_state = qbert_fsm_flexbe_states.motor_stop_state',
            'motor_home_state = qbert_fsm_flexbe_states.motor_home_state',
            'motor_move_to_pos_state = qbert_fsm_flexbe_states.motor_move_to_pos_state',
            'motor_set_vel_state = qbert_fsm_flexbe_states.motor_set_vel_state',
            'detect_cable_state = qbert_fsm_flexbe_states.detect_cable_state',
            'piston_move_to_pos_state = qbert_fsm_flexbe_states.piston_move_to_pos_state',
            'gripper_extend_state = qbert_fsm_flexbe_states.gripper_extend_state',
        ],
    },
)
