import cv2


camera = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Select MJPG before requesting resolution and frame rate
camera.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG")
)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
camera.set(cv2.CAP_PROP_FPS, 30)

if not camera.isOpened():
    raise RuntimeError("Could not open /dev/video0")


actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
actual_fps = camera.get(cv2.CAP_PROP_FPS)

print(f"Camera resolution: {actual_width}x{actual_height}")
print(f"Camera frame rate: {actual_fps}")

if not camera.isOpened():
    raise RuntimeError("Could not open /dev/video0")


# Use the AprilTag 36h11 family
tag_dictionary = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_APRILTAG_25h9
)

detector_parameters = cv2.aruco.DetectorParameters_create()


print("AprilTag detector started")
print("Press Q to close the window")


while True:
    success, frame = camera.read()

    if not success:
        print("Failed to read a camera frame")
        break

    # AprilTag detection works on a grayscale image
    grayscale = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    corners, tag_ids, rejected = cv2.aruco.detectMarkers(
        grayscale,
        tag_dictionary,
        parameters=detector_parameters
    )

    if tag_ids is not None:

        # Draw tag boundaries and IDs
        cv2.aruco.drawDetectedMarkers(
            frame,
            corners,
            tag_ids
        )

        for tag_corners, tag_id in zip(corners, tag_ids.flatten()):
            points = tag_corners[0]

            center_x = int(points[:, 0].mean())
            center_y = int(points[:, 1].mean())

            # Draw the calculated center
            cv2.circle(
                frame,
                (center_x, center_y),
                6,
                (0, 0, 255),
                -1
            )

            cv2.putText(
                frame,
                f"ID: {tag_id} ({center_x}, {center_y})",
                (center_x + 10, center_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            print(
                f"Tag {tag_id}: "
                f"x={center_x}, y={center_y}"
            )

    cv2.imshow("ROBOGAME Arena AprilTags", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()