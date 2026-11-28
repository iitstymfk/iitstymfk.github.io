"""Builds game models into ../models/*.glb. Add new model functions below and list them in MODELS."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from blender_kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(OUT, exist_ok=True)

def ammo_crate():
    wood = mat('wood', (.35, .22, .1), .85)
    metal = mat('metal', (.18, .2, .18), .4, .8)
    stripe = mat('stripe', (.8, .65, .1), .6)
    box('body', (.7, .45, .4), (0, 0, .2), wood, bevel=.015)
    for x in (-.22, .22):
        box('band', (.05, .47, .42), (x, 0, .2), metal)
    box('lid', (.72, .47, .04), (0, 0, .42), metal, bevel=.01)
    box('label', (.3, .01, .12), (0, -.226, .22), stripe)
    cyl('handle', .015, .26, (0, 0, .46), metal, rot=(0, 1.5708, 0), verts=10)

MODELS = {'ammo_crate': ammo_crate}

if __name__ == '__main__':
    only = sys.argv[1:] or MODELS.keys()
    for n in only:
        reset(); MODELS[n]()
        join_all(n); export(os.path.join(OUT, n + '.glb'))
        preview(os.path.join('/tmp', n + '.png'))
