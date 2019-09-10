'''
makey makey作为输入: 接触、水果

pgzrun x.py
'''


def on_key_down():
    if keyboard.space:
        print("space")
        beep = tone.create('E3', 0.5)
        beep.play()

    if keyboard.b:
        print("b")