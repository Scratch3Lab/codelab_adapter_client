'''
pip install codelab_adapter_client opencv-python

# ref: https://gpiozero.readthedocs.io/en/stable/recipes.html#button-controlled-camera
'''
from codelab_adapter_client import HANode
from datetime import datetime
import cv2

cap = cv2.VideoCapture(0)  


class Neverland(HANode):
    def __init__(self):
        super().__init__()

    def capture(self):
        timestamp = datetime.now().isoformat()
        ret, frame = cap.read()
        cv2.imwrite(f"/tmp/{timestamp}.jpg", frame)

    def when_open_door(self):
        print("The door is opened")
        self.capture()

    def run(self):
        self.receive_loop()


neverland = Neverland()
neverland.run()
