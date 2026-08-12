from setuptools import find_packages, setup

package_name = 'arena_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gmucradl',
    maintainer_email='your_email@example.com',
    description='AprilTag detection for the ROBOGAME arena',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'apriltag_node = arena_perception.apriltag_node:main',
            'camera_test = arena_perception.camera_test:main',
            'gazebo_viz_node = arena_perception.gazebo_viz_node:main',
            'controller_input = arena_perception.controller_input:main',
            'autonomy_node = arena_perception.autonomy_node:main',
        ],
    },
)
