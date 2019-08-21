from codelab_adapter_client import HANode
import subprocess

class Neverland(HANode):
    def __init__(self):
        super().__init__()

    def open_my_book(self):
        subprocess.call("open /Applications/iBooks.app/", shell=True)

    def open_door(self):
        print("The door is opened")
        self.open_my_book()

    def close_door(self):
        print("The door is closed")

    def neverland_event(self, entity, action):
        print(entity, action)

    def run(self):
        self.receive_loop()


neverland = Neverland()
neverland.run()
