'''
pip install replit-play codelab_adapter_client
'''

import play
import time
from codelab_adapter_client import HANode

# cat = play.new_text('=^.^=', font_size=70)
cat = play.new_text('click to turn off the light!', font_size=70)


class Neverland(HANode):
    def __init__(self):
        super().__init__()


neverland = Neverland()

num = 1


@cat.when_clicked
def win_function():
    global num
    cat.show()

    if num % 2 == 0:
        neverland.call_service(service="turn_on")
        cat.words = 'click to turn off the light!'
    else:
        neverland.call_service(service="turn_off")
        cat.words = 'click to turn on the light!'
    num = num + 1  # num +=  1


play.start_program()