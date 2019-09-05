from codelab_adapter_client.microbit import MicrobitNode


class MyNode(MicrobitNode):
    def __init__(self):
        super().__init__()

    def run(self):
        # document: https://microbit-micropython.readthedocs.io/en/latest/
        content = "a"
        py_code = f"display.scroll('{content}', wait=False, loop=False)"
        self.send_command(py_code)


if __name__ == "__main__":
    try:
        node = MyNode()
        # node.receive_loop_as_thread() # get microbit data
        node.run()
    except KeyboardInterrupt:
        node.terminate()  # Clean up before exiting.