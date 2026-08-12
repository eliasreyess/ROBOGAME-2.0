import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Point, Twist
from nav_msgs.msg import Odometry


class AutonomyNode(Node):

    def __init__(self):
        super().__init__("autonomy_node")

        self.cmd_publisher = self.create_publisher(
            Twist,
            "/robot_1/cmd_vel",
            10
        )

        self.odom_subscription = self.create_subscription(
            Odometry,
            "/model/robot_1/odometry",
            self.odom_callback,
            10
        )

        self.goal_subscription = self.create_subscription(
            Point,
            "/robot_1/goal",
            self.goal_callback,
            10
        )


        #variable definitions for the robot command 
        
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0


        #these are overwriten when read from the message
        self.goal_x = 0.0
        self.goal_y = 0.0

        self.have_odometry = False
        self.goal_active = False

        self.distance_tolerance = 0.05
        self.heading_tolerance = 0.10


        #these are for tunning the robot movement.
        #for now these work well.
        self.max_linear_speed = 0.25
        self.max_angular_speed = 1.0

        self.distance_gain = 0.6
        self.heading_gain = 1.5

        # Run the controller at 20 Hz
        self.timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info(
            "Autonomy node started. Waiting for odometry and a goal."
        )

    def odom_callback(self, message):
        position = message.pose.pose.position
        orientation = message.pose.pose.orientation

        self.x = position.x
        self.y = position.y

        # Convert quaternion into yaw angle
        sin_yaw = 2.0 * (
            orientation.w * orientation.z
            + orientation.x * orientation.y
        )

        cos_yaw = 1.0 - 2.0 * (
            orientation.y ** 2
            + orientation.z ** 2
        )

        self.yaw = math.atan2(sin_yaw, cos_yaw)
        self.have_odometry = True

    def goal_callback(self, message):
        self.goal_x = message.x
        self.goal_y = message.y
        self.goal_active = True

        self.get_logger().info(
            f"New goal: x={self.goal_x:.2f}, y={self.goal_y:.2f}"
        )

    @staticmethod
    def normalize_angle(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    @staticmethod
    def clamp(value, minimum, maximum):
        return max(minimum, min(value, maximum))

    def control_loop(self):
        if not self.have_odometry or not self.goal_active:
            return

        delta_x = self.goal_x - self.x
        delta_y = self.goal_y - self.y

        distance = math.hypot(delta_x, delta_y)
        desired_heading = math.atan2(delta_y, delta_x)

        heading_error = self.normalize_angle(
            desired_heading - self.yaw
        )

        command = Twist()

        if distance <= self.distance_tolerance:
            self.goal_active = False
            self.cmd_publisher.publish(command)

            self.get_logger().info(
                f"Goal reached: x={self.x:.2f}, y={self.y:.2f}"
            )
            return

        command.angular.z = self.clamp(
            self.heading_gain * heading_error,
            -self.max_angular_speed,
            self.max_angular_speed
        )

        # First rotate toward the goal, then drive forward
        if abs(heading_error) > self.heading_tolerance:
            command.linear.x = 0.0
        else:
            command.linear.x = self.clamp(
                self.distance_gain * distance,
                0.0,
                self.max_linear_speed
            )

        self.cmd_publisher.publish(command)

    def stop_robot(self):
        self.cmd_publisher.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = AutonomyNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
