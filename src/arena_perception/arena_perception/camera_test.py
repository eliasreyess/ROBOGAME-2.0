import cv2
import rclpy
from rclpy.node import Node


class CameraTest(Node):

    def __init__(self):
        super().__init__('camera_test')

        # Open camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            self.get_logger().error("Could not open camera")
            return

        # Camera settings
        self.cap.set(cv2.CAP_PROP_FOURCC,
                     cv2.VideoWriter_fourcc(*'MJPG'))

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.get_logger().info("Camera started")

        # 30 Hz timer
        self.timer = self.create_timer(1/30, self.camera_loop)


    def camera_loop(self):

        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warning("No frame received")
            return

        # Print frame info
        height, width, _ = frame.shape
        self.get_logger().info(
            f"Frame received: {width}x{height}"
        )

        # Show image
        cv2.imshow("Camera Feed", frame)

        # Required for OpenCV window
        cv2.waitKey(1)


    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = CameraTest()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()