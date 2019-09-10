'''
pip install pgzero

pgzrun x.py

doc: https://pygame-zero.readthedocs.io/en/stable/index.html
'''
from codelab_adapter_client import HANode
import time

'''
hand_clap = pygame.mixer.Sound("src/Hand Clap.wav")
cowbell = pygame.mixer.Sound("src/Large Cowbell.wav")
'''

beep = tone.create('A3', 0.5) # pgzero 内建对象
    

class Neverland(HANode):
    def __init__(self):
        super().__init__()

    def neverland_event(self, entity, action, entity_id):
        '''
        entity_id 
        '''
        print(entity, action, entity_id)
        if entity == "cube":
            if action == "slide":
                beep.play()

    def run(self):
        self.receive_loop()


neverland = Neverland()

try:
    neverland.run()
except KeyboardInterrupt:
    neverland.terminate()
