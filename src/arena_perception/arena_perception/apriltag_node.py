import json

import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import numpy as np


class AprilTagNode(Node):

    def __init__(self):
        super().__init__("apriltag_node")

        self.publisher = self.create_publisher(
            String,
            "/arena/tags",
            10
        )

        self.camera = cv2.VideoCapture(0, cv2.CAP_V4L2)

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
            1.0 / 30,
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

        # Stores the center position of each AprilTag
        tag_centers = {}


        if tag_ids is not None:     # this test prevents the program from crasshing when no tags are detected

            cv2.aruco.drawDetectedMarkers(
                frame,
                corners,
                tag_ids
            )

            resize_parameter = 40.0   # adjusting this parameeter will change the arena size (blue line)
            # positive values will make the arena larger, negative values will make the arena smaller


            for tag_corners, tag_id in zip( corners, tag_ids.flatten()):  # corners and tag_id 
                                                                            # are two separate lists, so we need to flatten tag_ids to match the shape of corners

                    points = tag_corners[0]
                    #print(tag_id, points )   #debug                       
                    center_x = int(points[:, 0].mean() )
                    center_y = int(points[:, 1].mean() )

                    
                    #we use the centers of the corner tags to define an arena boundary
                    #we then resize the arena boundary by a certain amount.
                    #this is done via using the resize_parameter variable. the math is done bellow

                    if tag_id == 1:

                        # Save tag center for arena boundary
                        tag_centers[int(tag_id)] = ( center_x + resize_parameter, center_y + resize_parameter )

                    if tag_id == 2:
                        tag_centers[int(tag_id)] = ( center_x + resize_parameter, center_y - resize_parameter )
                    elif  tag_id == 3:
                        tag_centers[int(tag_id)] = ( center_x - resize_parameter, center_y - resize_parameter )
                    elif  tag_id == 4:
                        tag_centers[int(tag_id)] = ( center_x - resize_parameter, center_y + resize_parameter )


                    detection = {   "id": int(tag_id), "x": center_x, "y": center_y }


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
                        (0, 255, 255),
                        2
                    )


        ########################################################
        # Draw arena rectangle using AprilTags 1,2,3,4

        #fyi tag id 1 , 2, 3, 4 are reserved for the arena corners 

        arena_corners=[]
       

        if all(tag in tag_centers for tag in [1, 2, 3, 4]):

            arena_corners = np.array(
                [
                    tag_centers[1],   # Top left
                    tag_centers[2],   # Top right
                    tag_centers[3],   # Bottom right
                    tag_centers[4]    # Bottom left
                ],
                dtype=np.int32
            )


            cv2.polylines(
                frame,
                [arena_corners],
                True,
                (255, 0, 0),
                3
            )



            #debug 

        #print(tag_centers)
        #if tag_centers is not None and len(tag_centers) == 4:   # is not none to avoid crashing 
            

            
            #print(tag_centers[0]);
            #print(tag_centers[1]);
            #print(tag_centers[2]);
            #print(tag_centers[3]);


        ####### MATRIX TRANSFORMATION into real world coordinates (cm)


          #tag 1 corresponds to bottom right 
          #tag 2 corresponds to top right
          #tag 3 corresponds to top left
          #tag 4 corresponds to bottom left
        if all(tag in tag_centers for tag in [1, 2, 3, 4]):
            src_points = np.float32([
                tag_centers[1],  # Bottom right
                tag_centers[2],  # Top right
                tag_centers[3],  # Top left
                tag_centers[4]   # Bottom left
            ])  


                                                            
            #these are the real world coordinates of the arena corners in cm. 
            # The arena is 112cm x 112cm, so the corners are defined as follows:
            dst_points = np.float32([
                [112, 112],   # Bottom right in cm      
                
                [112, 0],     # Top right in cm
                [0, 0],       # Top left in cm
                [0, 112]      # Bottom left in cm
            ])

            
            # Compute the perspective transformation matrix
            #our src points are the tag centers for the boundary tags (1,2,3,4) after they have been modified by
            #the resize param. 
            #the dst points are the "true" real life measured coordinates 
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)

            for d in detections:
                point = np.array([[[d["x"], d["y"]]]], dtype=np.float32)
                cm_point = cv2.perspectiveTransform(point, matrix)
                d["x_cm"] = float(cm_point[0][0][0])
                d["y_cm"] = float(cm_point[0][0][1])
###### get back here!!!!!!
# continue sentence. we are publishing the xy values in cm, however 
# we need to fix the issue that prevents the node from running if its ocluded
# this happens because the code crashes if a polygon cannot be drawn due to being obstructed. 



        






        


        ########################################################
        # Publish AprilTag data
        ########################################################

        message = String()
        message.data = json.dumps(detections)

        #message.data = json.dumps(arena_corners.tolist())  # Convert numpy array to list for JSON serialization

        self.publisher.publish(message)


        cv2.imshow(
            "ROBOGAME Arena AprilTags",
            frame
        )

        cv2.waitKey(3)



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