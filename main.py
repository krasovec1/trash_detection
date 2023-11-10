import cv2
import numpy as np
from object_detection import ObjectDetection
from detect_littering import MatchMaker
from object_tracking import *
import functions
import math

# Initialize Object Detection
od = ObjectDetection()

cap = cv2.VideoCapture("videos/00122.MTS")

# Initialize count
frame_num = 0

# initialize car tracking class
tracked_objects = ObjectTracker()

# initialize trash tracking class
tracked_trash = TrashTracker()

# Initialize movement detector
movement_detection = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=20)

# start reviewing the video
while True:
    ret, frame = cap.read()
    frame_num += 1
    if not ret:
        break
    if frame_num <= 150: # clip 00119 point of interest on frame 328
        mask = movement_detection.apply(frame)
        #cv2.imshow("mask", mask)
        continue

    # attach frame to the movement detection instance
    mask = movement_detection.apply(frame)

    # Detect objects on frame
    detected_objects = od.detect(frame)
    (class_ids, scores, boxes) = detected_objects

    # we don't need to perform movement detection inside the boxes where a specific object was detected,
    # so we make a mask that weill eliminate those areas
    mask = functions.darken_rectangle(mask, boxes)

    # start tracking
    tracked_cars = tracked_objects.track(detected_objects, frame_num)

    # Iterate over the dictionary
    for car in tracked_cars:
        object_id = car.obj_id
        (x, y, w, h) = car.locations[-1].bounding_box
        # Add a rectangle to the image
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # the next rectangle represents the area of interest
        cv2.rectangle(frame, (x-w, y-h), (x + 2*w, y + 2*h), (0, 255, 0), 2)

        # Add the object ID as text next to the circle
        cv2.putText(frame, str(object_id), (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # extract high visibility objects
    _, mask = cv2.threshold(mask, 250, 255, cv2.THRESH_BINARY)

    # find outlines of the highlighted areas
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # define list with all the potential trash objects
    relevant_objects = functions.discard_unwanted_objects(contours, tracked_cars, 20)

    track_trash = tracked_trash.track(relevant_objects, frame_num)

    car_ids = MatchMaker(tracked_objects, tracked_trash)
    if len(car_ids) > 0:
        print("found one")

    for trash in track_trash:
        (cX, cY) = trash.locations[-1].center_point
        cv2.circle(frame, (cX, cY), 4, (0, 255, 255), -1)

    # decision = functions.decide(track_trash, tracked_cars)

    # Display the grayscale difference image
    cv2.imshow("Grayscale Difference", frame)
    key = cv2.waitKey(0)
    if key == 27:
        break

    # Update the previous frame
    frame_previous = frame.copy()

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()
