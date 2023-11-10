import numpy as np
import cv2


def darken_rectangle(image, boxes):

    darkened_image = image

    # Create a mask with the same dimensions as the image
    mask = np.zeros_like(image)

    for box in boxes:
        (x, y, w, h) = box

        # so that only the pixels inside the area of interest get processed in the future
        mask[y-h:y+2*h, x-w:x+2*w] = 255

    for box in boxes:
        (x, y, w, h) = box

        # but we don't need the areas where the object is located
        mask[y:y+h, x:x+w] = 0

    # Apply the mask to the image using bitwise AND operation
    darkened_image = cv2.bitwise_and(image, mask)

    return darkened_image


def calculate_contour_center(contour):
    M = cv2.moments(contour)

    # Calculate centroid coordinates
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    return [cx, cy]


def discard_unwanted_objects(contours, tracked_objects, min_area):
    """
    :param contours:
    :param tracked_objects:
    :param min_area:
    :return:  function returns a list of contours that are relevant to our cause.
    it discards all the contours that are directly tuching any of the recognised objects, and it also discards
    all the contours that are too small to be of meaning
    """
    # define list with all the potential trash objects
    relevant_objects = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # we dont want to check every pixel of the contour to see if it tuches any boundingBoxes of the detected objects
        # so we get the bounding rectangle of the contour and then check for any tuches
        if area > min_area:
            x, y, width, height = cv2.boundingRect(cnt)
            contour_rect = (x+1, y+1, x + width, y + height)
            enlarged_rect = (
                contour_rect[0] - 2,  # Shift left by 1 pixel
                contour_rect[1] - 2,  # Shift up by 1 pixel
                contour_rect[2] + 4,  # Increase width by 2 pixels
                contour_rect[3] + 4  # Increase height by 2 pixels
            )
            intersects = False
            for obj in tracked_objects:
                obj_box = obj.locations[-1].bounding_box
                obj_rect = (obj_box[0], obj_box[1], obj_box[0] + obj_box[2], obj_box[1] + obj_box[3])
                # it checks if the contour_rect and obj_rect are touching
                if (enlarged_rect[2] > obj_rect[0] and enlarged_rect[0] < obj_rect[2] and
                        enlarged_rect[3] > obj_rect[1] and enlarged_rect[1] < obj_rect[3]):
                    intersects = True
                    break
            if not intersects:
                center = calculate_contour_center(cnt)
                relevant_objects.append(center)
    return relevant_objects


def detect_littering(track_trash, tracked_cars):
    # in this two lists we wil store all the trash and car objects that has been detected by the tracker and are
    # no longer being tracked. this means that the event had happened, and we can now check for littering
    trash_track_completed = []
    car_track_completed = []



