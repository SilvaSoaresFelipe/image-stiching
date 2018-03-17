import cv2


def get_frames(video_name):
    vidcap = cv2.VideoCapture(video_name)
    success, image = vidcap.read()
    count = 0
    success = True
    while success:
        success, image = vidcap.read()
        cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file
        if cv2.waitKey(10) == 27:                     # exit if Escape is hit
            break
        count += 1
