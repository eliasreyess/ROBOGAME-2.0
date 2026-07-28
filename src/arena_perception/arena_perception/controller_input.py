import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class Ps4TeleopNode(Node):

    def __init__(self):
        super().__init__("ps4_teleop_node")

        self.declare_parameter("linear_axis", 1)
        self.declare_parameter("angular_axis", 3)
        self.declare_parameter("max_linear_speed", 0.5)
        self.declare_parameter("max_angular_speed", 1.5)
        self.declare_parameter("deadzone", 0.05)

        self.linear_axis = self.get_parameter("linear_axis").value
        self.angular_axis = self.get_parameter("angular_axis").value
        self.max_linear_speed = self.get_parameter("max_linear_speed").value
        self.max_angular_speed = self.get_parameter("max_angular_speed").value
        self.deadzone = self.get_parameter("deadzone").value

        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.subscription = self.create_subscription(
            Joy, "/joy", self.joy_callback, 10
        )

        self.get_logger().info("PS4 teleop node started")

    def apply_deadzone(self, value):
        return value if abs(value) > self.deadzone else 0.0

    def joy_callback(self, msg: Joy):
        linear = self.apply_deadzone(msg.axes[self.linear_axis])
        angular = self.apply_deadzone(msg.axes[self.angular_axis])

        twist = Twist()
        twist.linear.x = linear * self.max_linear_speed
        twist.angular.z = angular * self.max_angular_speed

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = Ps4TeleopNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
