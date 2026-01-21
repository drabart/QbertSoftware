from setuptools import find_packages, setup
import glob

package_name = 'qbert_cam'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + "/launch", glob.glob('launch/*.launch.py')),
    ],
    install_requires=[
        'setuptools'
        'numpy',
        'opencv-python',
    ],
    zip_safe=True,
    maintainer='lucas',
    maintainer_email='L.B.paul@student.tudelft.nl',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'cable_detector_node = qbert_cam.cable_detect:main',
            'section_detector_node = qbert_cam.section_detect:main',
        ],
    },
)
