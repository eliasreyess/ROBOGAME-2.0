import json

import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class AprilTagNode(Node):

    def __init__(self):
        super().__init__("apriltag_node")

        self.publisher = self.create_publisher(
            String,
            "/arena/tags",
            10
        )

        self.camera = cv2.VideoCapture(0, cv2.CAP_V4L2)

        self.camera.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"MJPG")
        )
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        self.camera.set(cv2.CAP_PROP_FPS, 30)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open /dev/video0")

        self.tag_dictionary = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_APRILTAG_25h9
        )

        self.detector_parameters = (
            cv2.aruco.DetectorParameters_create()
        )

        self.detector_parameters.cornerRefinementMethod = (
            cv2.aruco.CORNER_REFINE_APRILTAG
        )

        self.detector_parameters.adaptiveThreshWinSizeMin = 3
        self.detector_parameters.adaptiveThreshWinSizeMax = 53
        self.detector_parameters.adaptiveThreshWinSizeStep = 4
        self.detector_parameters.minMarkerPerimeterRate = 0.02

        self.timer = self.create_timer(
            1.0 / 30.0,
            self.process_frame
        )

        self.get_logger().info(
            "AprilTag arena-perception node started"
        )

    def process_frame(self):
        success, frame = self.camera.read()

        if not success:
            self.get_logger().warning(
                "Failed to read a camera frame"
            )
            return

        grayscale = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        corners, tag_ids, rejected = cv2.aruco.detectMarkers(
            grayscale,
            self.tag_dictionary,
            parameters=self.detector_parameters
        )

        detections = []

        if tag_ids is not None:
            cv2.aruco.drawDetectedMarkers(
                frame,
                corners,
                tag_ids
            )

            for tag_corners, tag_id in zip(
                corners,
                tag_ids.flatten()
            ):
                points = tag_corners[0]

                center_x = int(points[:, 0].mean())
                center_y = int(points[:, 1].mean())

                detection = {
                    "id": int(tag_id),
                    "x": center_x,
                    "y": center_y
                }

                detections.append(detection)

                cv2.circle(
                    frame,
                    (center_x, center_y),
                    6,
                    (0, 0, 255),
                    -1
                )

                cv2.putText(
                    frame,
                    f"ID {tag_id}: ({center_x}, {center_y})",
                    (center_x + 10, center_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        message = String()
        message.data = json.dumps(detections)
        self.publisher.publish(message)

        cv2.imshow(
            "ROBOGAME Arena AprilTags",
            frame
        )

        cv2.waitKey(1)

    def close(self):
        self.camera.release()
        cv2.destroyAllWindows()


def main(args=None):
    rclpy.init(args=args)

    node = AprilTagNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()