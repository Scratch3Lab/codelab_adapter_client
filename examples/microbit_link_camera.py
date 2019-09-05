import cv2

import time
from loguru import logger
from codelab_adapter_client import AdapterNode

content = 0


class EIMNode(AdapterNode):
    def __init__(self):
        super().__init__()
        self.EXTENSION_ID = "eim"

    def extension_message_handle(self, topic, payload):
        global content
        # self.logger.info(f'the message payload from scratch: {payload}')
        content = payload["content"]
        # print(content)


node = EIMNode()
node.receive_loop_as_thread()


def show_webcam(mirror=False):
    global content
    scale = 10
    cam = cv2.VideoCapture(0)
    while True:
        ret_val, image = cam.read()
        if mirror:
            image = cv2.flip(image, 1)

        #get the webcam size
        height, width, channels = image.shape

        #prepare the crop
        centerX, centerY = int(height / 2), int(width / 2)
        radiusX, radiusY = int(scale * height / 100), int(scale * width / 100)

        minX, maxX = centerX - radiusX, centerX + radiusX
        minY, maxY = centerY - radiusY, centerY + radiusY

        cropped = image[minX:maxX, minY:maxY]
        resized_cropped = cv2.resize(cropped, (width, height))

        cv2.imshow('my webcam', resized_cropped)

        #add + or - 5 % to zoom
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break  # esc to quit
        if key == ord("a"):
            if scale < 48:
                scale += 2  # +2

        if key == ord("b"):
            if scale >= 10:
                scale -= 2  # +2

        print("content:", content)
        if scale == "A":
            print("A")
        else:
            scale = 10 + 40/100*int(content)

    cv2.destroyAllWindows()


show_webcam()