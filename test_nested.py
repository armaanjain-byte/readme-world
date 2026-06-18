import json
from state import initialize_state, save_state
from generate_world import generate_svg

state = initialize_state()
state['weather'] = 'clear'
state['pet']['mood'] = 'happy'
save_state(state)
generate_svg()

with open('generated/world.svg') as f:
    text = f.read()
    print('cat_happy exists:', 'cat_happy' in text)
    if 'cat_happy' in text:
        block = text.split('id="cat_happy"')[1].split('</g>')[0]
        print('nested svg exists:', '<svg' in block)
    else:
        print('nested svg exists: N/A')
