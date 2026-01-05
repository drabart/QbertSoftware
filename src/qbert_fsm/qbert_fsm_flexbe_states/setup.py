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
            # 'example_action_state = qbert_fsm_flexbe_states.example_action_state',
            # 'example_state = qbert_fsm_flexbe_states.example_state',
            'motor_clear_errors_state = qbert_fsm_flexbe_states.motor_clear_errors_state',
            'motor_reboot_state = qbert_fsm_flexbe_states.motor_reboot_state',
            'move_motor_to_pos_state = qbert_fsm_flexbe_states.move_motor_to_pos_state',
            'set_motor_state_state = qbert_fsm_flexbe_states.set_motor_state_state',
            'set_motor_vel_state = qbert_fsm_flexbe_states.set_motor_vel_state',
        ],
    },
)
