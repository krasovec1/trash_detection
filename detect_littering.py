from kalmanfilter import KalmanFilter


def MatchMaker(tracker, trashTracker):
    """
    this function iterates through the list of objects that we are currently tracking and checks for any potential matches
    a potential match is if a trash_object and a car_object were at ny point in time both present on the screen
    :param tracker:
    :param trashTracker:
    :return:
    """
    trash_index_to_remove = []
    car_index_to_remove = []
    identified_offences = []
    for i in range(len(trashTracker.tracked_object_list)):
        tracked_trash = trashTracker.tracked_object_list[i]
        offenceFound = False

        if (tracked_trash.start_frame is not None) and (tracked_trash.end_frame is not None):
            wtf = (tracked_trash.end_frame - tracked_trash.start_frame)
            if (tracked_trash.end_frame - tracked_trash.start_frame) > 4:

                for j in range(len(tracker.tracked_object_list)):
                    tracked_car = tracker.tracked_object_list[j]
                    offenceFound = check_compatibility(tracked_trash, tracked_car)

                    if offenceFound:
                        offenceFound = identifie_litering(tracked_trash, tracked_car)

                        if offenceFound:
                            identified_offences.append([tracked_trash, tracked_car])
            trash_index_to_remove.append(i)

    # Remove Trash elements in reverse order to avoid index issues
    for index in sorted(trash_index_to_remove, reverse=True):
        del trashTracker.tracked_object_list[index]

    for j in range(len(tracker.tracked_object_list)):
        tracked_car = tracker.tracked_object_list[j]
        matchFound = False

        if (tracked_car.start_frame is not None) and (tracked_car.end_frame is not None):

            for i in range(len(trashTracker.tracked_object_list)):
                tracked_trash = trashTracker.tracked_object_list[i]
                matchFound = check_compatibility(tracked_trash, tracked_car)

            if not matchFound:
                car_index_to_remove.append(j)

    # Remove Car elements in reverse order to avoid index issues
    for index in sorted(car_index_to_remove, reverse=True):
        del tracker.tracked_object_list[index]

    return identified_offences


def check_compatibility(trash, car):

    if car.end_frame is not None:
        if (trash.start_frame > car.start_frame) and (trash.start_frame < car.end_frame):
            return True
        else:
            return False
    elif trash.start_frame > car.start_frame:
        return True
    else:
        return False


def is_point_inside_box(point, box):
    # point is a tuple (x, y) representing the point coordinates
    # box is a tuple (x, y, w, h) representing the bounding box

    x, y = point
    box_x, box_y, box_w, box_h = box

    if box_x <= x <= (box_x + box_w) and box_y <= y <= (box_y + box_h):
        return True
    else:
        return False


def identifie_litering(trash, car):
    kf = KalmanFilter()
    predictdPoint = []
    TrashFrameNum = 0
    # here we add all the nown locations of the trash obect to the kalman filter
    # preditedPoint is the point of origen for the trash object.
    for location in reversed(trash.locations):
        predictdPoint = kf.predict(location.center_point[0], location.center_point[1])
        TrashFrameNum = location.frame_num

    for location in car.locations:
        if location.frame_num == (TrashFrameNum - 1):
           if is_point_inside_box(predictdPoint, location.bounding_box):
               return True

    return False






