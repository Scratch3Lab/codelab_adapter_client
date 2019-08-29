'''
pip install python-sonic
  
instal sonic pi
'''
import pygame
from codelab_adapter_client import HANode
from time import sleep

from psonic import play, run  # work with sonic pi


def sonicpi_sample_wav(wav_file):
    wav_file_dir = "~/mylab/codelabclub/lab/codelab_adapter_client/examples/src"
    return f'sample "{wav_file_dir}/{wav_file}"'

def test_run():
    return '''
define :foo do
  play 50
  sleep 1
  play 55
  sleep 0.5
end

foo

sleep 1

2.times do
  foo
end
    '''

cowbell = sonicpi_sample_wav("Large Cowbell.wav")
hand_clap = sonicpi_sample_wav("Large Cowbell.wav")

# sample "~/mylab/codelabclub/lab/codelab_adapter_client/examples/src/Large Cowbell.wav"
# set midi  todo  with sonic


class Neverland(HANode):
    def __init__(self):
        super().__init__()
        self.beat = 1/4

    def neverland_event(self, entity, action, entity_id):
        '''
        entity_id 
        '''
        print(entity, action, entity_id)
        if entity == "cube":
            if action == "slide":
                run(cowbell) 
                # run(test_run())
            if action == "rotate_left":
                # play (60, attack=0.5, decay=1, sustain_level=0.4, sustain=2, release=0.5)
                # attack 淡入时间，中间持续时间，release淡出时间
                # play是非阻塞的
                play(70,sustain=0.25) # 响度 amp=2/0.5， 方向 pan=-1/1/0
                sleep(self.beat)
                play(72,sustain=0.25)

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