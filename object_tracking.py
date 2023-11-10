import math
from typing import List, Any


class LocationInTime:
    def __init__(self, frame_num, center_point=None, bounding_box=None):
        if center_point is None and bounding_box is None:
            raise ValueError("Either center_point or bounding_box must be provided.")

        self.frame_num = frame_num
        self.center_point = center_point if center_point is not None else self.calculate_center_from_bbox(bounding_box)
        self.bounding_box = bounding_box

    @staticmethod
    def calculate_center_from_bbox(bounding_box):
        if bounding_box is None:
            return None
        (x2, y2, w2, h2) = bounding_box
        cx2 = int((x2 + x2 + w2) / 2)
        cy2 = int((y2 + y2 + h2) / 2)
        return cx2, cy2

    def __str__(self):
        return f"Frame: {self.frame_num}, Center Point: {self.center_point}, Bounding Box: {self.bounding_box}"


class TrackedObject:
    locations: list[LocationInTime]

    def __init__(self, obj_id, obj_class):
        self.obj_class = obj_class
        self.obj_id = obj_id
        self.start_frame = None
        self.end_frame = None
        self.locations = []

    def add_location(self, location_in_time):
        if isinstance(location_in_time, LocationInTime):
            self.locations.append(location_in_time)
        else:
            raise ValueError("The provided location must be an instance of LocationInTime.")

    def __str__(self):
        return f"Car ID: {self.obj_id}\nLocations: {self.locations}"


class ObjectTracker:
    tracked_object_list: list[TrackedObject]

    def __init__(self):
        # Initialize count
        self.count = 0
        self.track_id = 0
        self.tracked_object_list = []

    def add_object_to_object_list(self, tr_object):
        if isinstance(tr_object, TrackedObject):
            self.tracked_object_list.append(tr_object)
        else:
            raise ValueError("The provided location must be an instance of Tracked_object.")

    def track(self, detected_objects, frame_num):

        (class_ids, scores, boxes) = detected_objects
        if isinstance(boxes, tuple):
            boxes = []
        else:
            # Handle the case when boxes is empty
            boxes = boxes.tolist()

        # frame count
        self.count += 1

        # on the first frame we initialize tracking of all the objects on the frame
        if self.count == 1:
            for i in range(len(boxes)):
                location = LocationInTime(frame_num, bounding_box=boxes[i])
                car = TrackedObject(self.track_id, class_ids[i])
                car.start_frame = frame_num
                self.track_id += 1
                car.add_location(location)
                self.add_object_to_object_list(car)

        else:
            # we copy the list because we can't change the list whill we are iterating through it,
            # so we will iterate through the copy
            # tracking_objects_copy = self.tracking_objects.copy()
            tracked_object_list_new = []
            forRange = len(self.tracked_object_list)
            for i in range(forRange):
                # calculate center points of the boxes
                (cx1, cy1) = self.tracked_object_list[i].locations[-1].center_point
                object_exists = False
                for j in range(len(boxes)):
                    # calculate center points of the boxes
                    (x2, y2, w2, h2) = boxes[j]
                    cx2 = int((x2 + x2 + w2) / 2)
                    cy2 = int((y2 + y2 + h2) / 2)

                    # use the center points to calculate the distance between objects
                    distance = math.hypot(cx1 - cx2, cy1 - cy2)

                    # Update IDs position
                    if (distance < 50) and (self.tracked_object_list[i].end_frame is None):
                        location = LocationInTime(frame_num, bounding_box=boxes[j])
                        self.tracked_object_list[i].add_location(location)
                        object_exists = True
                        boxes.pop(j)
                        break

                # add the tracked_object to the list
                if object_exists:
                    tracked_object_list_new.append(self.tracked_object_list[i])
                elif self.tracked_object_list[i].end_frame is None:
                    self.tracked_object_list[i].end_frame = frame_num
                    tracked_object_list_new.append(self.tracked_object_list[i])

            self.tracked_object_list = tracked_object_list_new

            # Add new IDs found
            for b in range(len(boxes)):
                location = LocationInTime(frame_num, bounding_box=boxes[b])
                car = TrackedObject(self.track_id, class_ids[b])
                self.track_id += 1
                car.start_frame = frame_num
                car.add_location(location)
                self.add_object_to_object_list(car)

        return self.tracked_object_list


class TrashTracker:
    tracked_object_list: list[TrackedObject]

    def __init__(self):
        # Initialize count
        self.count = 0
        self.track_id = 0
        self.tracked_object_list = []

    def add_object_to_object_list(self, tr_object):
        if isinstance(tr_object, TrackedObject):
            self.tracked_object_list.append(tr_object)
        else:
            raise ValueError("The provided location must be an instance of Tracked_object.")

    def track(self, detected_objects, frame_num):
        """
        :param: detected_objects: a list of (x,y) coordinates that refer to the center position
        of the object we want to track
        :return: the return will be a dictionary of all the objects that were successfully tracked
        along with the prior positions of this object
        """

        # frame count
        self.count += 1

        # on the first frame we initialize tracking of all the objects on the frame
        if self.count == 1:
            for i in range(len(detected_objects)):
                location = LocationInTime(frame_num, center_point=detected_objects[i])
                trash = TrackedObject(self.track_id, 0)
                self.track_id += 1
                trash.start_frame = frame_num
                trash.add_location(location)
                self.add_object_to_object_list(trash)

        else:
            # we copy the list because we can't change the list whill we are iterating through it,
            # so we will iterate through the copy
            tracked_object_list_new = []
            forRange = len(self.tracked_object_list)
            for i in range(forRange):
                # calculate center points of the boxes
                (cx1, cy1) = self.tracked_object_list[i].locations[-1].center_point
                object_exists = False
                for j in range(len(detected_objects)):
                    # calculate center points of the boxes
                    (cx2, cy2) = detected_objects[j]

                    # use the center points to calculate the distance between objects
                    distance = math.hypot(cx1 - cx2, cy1 - cy2)

                    # Update IDs position
                    if (distance < 50) and (self.tracked_object_list[i].end_frame is None):
                        location = LocationInTime(frame_num, center_point=detected_objects[j])
                        self.tracked_object_list[i].add_location(location)
                        object_exists = True
                        detected_objects.pop(j)
                        break

                # Remove IDs lost
                if object_exists:
                    tracked_object_list_new.append(self.tracked_object_list[i])
                elif self.tracked_object_list[i].end_frame is None:
                    self.tracked_object_list[i].end_frame = frame_num
                    tracked_object_list_new.append(self.tracked_object_list[i])
            self.tracked_object_list = tracked_object_list_new

            # Add new IDs found
            for b in range(len(detected_objects)):
                location = LocationInTime(frame_num, center_point=detected_objects[b])
                trash = TrackedObject(self.track_id, 0)
                self.track_id += 1
                trash.start_frame = frame_num
                trash.add_location(location)
                self.add_object_to_object_list(trash)

        return self.tracked_object_list
