#!/usr/bin/env python
from setuptools import setup

package_name = 'qbert_fsm_flexbe_behaviors'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='phil',
    maintainer_email='philsplus@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cable_detect_sm = qbert_fsm_flexbe_behaviors.cable_detect_yup_sm',
            'example_behavior_sm = qbert_fsm_flexbe_behaviors.example_behavior_sm',
            'qbert_state_machine_sm = qbert_fsm_flexbe_behaviors.qbert_state_machine_sm',
        ],
    },
)
