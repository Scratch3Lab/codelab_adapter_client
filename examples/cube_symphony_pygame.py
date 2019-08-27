'''
pip install pygame python-sonic
  
instal sonic pi
'''
import pygame
from codelab_adapter_client import HANode
import time

pygame.init()
pygame.mixer.init()
pygame.display.set_mode()
pygame.display.set_caption('cube symphony')

hand_clap = pygame.mixer.Sound("src/Hand Clap.wav")
cowbell = pygame.mixer.Sound("src/Large Cowbell.wav")


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
                hand_clap.play()

    def run(self):
        self.receive_loop()


neverland = Neverland()

try:
    neverland.run()
except KeyboardInterrupt:
    neverland.terminate()
'''
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); #sys.exit() if sys is imported
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                hand_clap.play()
            if event.key == pygame.K_cc:
                cowbell.play()
'''