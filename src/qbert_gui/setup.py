from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'qbert_gui'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ("share/ament_index/resource_index/packages",
         ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),

        (os.path.join("share", package_name, "assets"), glob(package_name + "/assets/*")),
        (os.path.join("share", package_name, "ui"), glob(package_name + "/ui/*.ui")),
        (os.path.join("share", package_name, "themes"), glob(package_name + "/themes/*.qss")),
        (os.path.join("share", package_name, "i18n"), glob(package_name + "/i18n/*.qm")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bartosz-drabinski',
    maintainer_email='drabart@outlook.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'gui = qbert_gui.main:main'
        ],
    },
)
