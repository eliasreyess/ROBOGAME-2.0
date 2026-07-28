import json

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from visualization_msgs.msg import Marker


class TagVisualizer(Node):

    def __init__(self):
        super().__init__("tag_visualizer")

        self.subscription = self.create_subscription(
            String,
            "/arena/tags",
            self.tag_callback,
            10
        )

        self.marker_pub = self.create_publisher(
            Marker,
            "/visualization_marker",
            10
        )

        self.get_logger().info(
            "AprilTag Gazebo visualizer started"
        )


    def tag_callback(self, msg):

        detections = json.loads(msg.data)

        for tag in detections:

            # Ignore arena corner tags if desired
            # if tag["id"] in [1,2,3,4]:
            #     continue

            marker = Marker()

            marker.header.frame_id = "arena"
            marker.header.stamp = self.get_clock().now().to_msg()

            marker.ns = "apriltags"
            marker.id = tag["id"]

            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD


            # Your coordinates are cm
            # Gazebo uses meters
            marker.pose.position.x = tag["x_cm"] /100
            marker.pose.position.y = tag["y_cm"] /100
            marker.pose.position.z = 0.02


            marker.pose.orientation.w = 1.0


            marker.scale.x = 0.05
            marker.scale.y = 0.05
            marker.scale.z = 0.02


            marker.color.a = 1.0
            marker.color.r = 1.0


            self.marker_pub.publish(marker)



def main(args=None):

    rclpy.init(args=args)

    node = TagVisualizer()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()