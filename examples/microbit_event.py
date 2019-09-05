from codelab_adapter_client.microbit import MicrobitNode
import time


class MyNode(MicrobitNode):
    def __init__(self):
        super().__init__()

    def when_button_a_is_pressed(self):
        self.logger.info("you press button A!")

    def microbit_event(self, data):
        self.logger.debug(data)
        if data["button_a"] == True:
            self.when_button_a_is_pressed()

    def run(self):
        # document: https://microbit-micropython.readthedocs.io/en/latest/
        while self._running:
            time.sleep(1)


if __name__ == "__main__":
    try:
        node = MyNode()
        node.receive_loop_as_thread()  # get microbit data
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.