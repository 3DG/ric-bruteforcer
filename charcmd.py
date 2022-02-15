from __future__ import annotations

from typing import Literal
import os
import math
import numpy as np
import json
import random
import time
import re
from io import BytesIO
from PIL import Image
from os import urandom as _urandom
config = {}
conf = open("./config.txt").readlines()
print(conf)
for line in conf:
      if "=" in line:
        line = line.strip().split("=")
        config[line[0]] = line[1]
os.system("echo RIC Seed Bruteforcer")
COLOR_NAMES: dict[str, tuple[int, int]] = {
    "maroon": (2, 1), # Not actually a word in the game
    "gold":   (6, 2), # Not actually a word in the game
    "red":    (2, 2),
    "orange": (2, 3),
    "yellow": (2, 4),
    "lime":   (5, 3),
    "green":  (5, 2),
    "cyan":   (1, 4),
    "blue":   (1, 3),
    "purple": (3, 1),
    "pink":   (4, 1),
    "rosy":   (4, 2),
    "grey":   (0, 1),
    "gray":   (0, 1), # alias
    "black":  (0, 4),
    "silver": (0, 2),
    "white":  (0, 3),
    "brown":  (6, 1),
}

class Random(random.Random):
      def seed(self, a=None):
          if a is None:
              try:
                # Seed with enough bytes to span the 19937 bit
                # state space for the Mersenne Twister
                a = int.from_bytes(_urandom(8), 'big')
              except NotImplementedError:
                import time
                a = int(time.time() * 256)%(2**64) # use fractional seconds
          self._current_seed = a
          super().seed(a)
      def get_seed(self):
          return self._current_seed
  
def recolor(sprite: Image.Image, color: str, palette: np.ndarray) -> Image.Image:
    '''Apply rgb color'''
    r,g,b = palette[COLOR_NAMES[color][::-1]]
    arr = np.asarray(sprite, dtype='float64')
    arr[..., 0] *= r / 256
    arr[..., 1] *= g / 256
    arr[..., 2] *= b / 256
    return Image.fromarray(arr.astype('uint8'))
  
def blacken(sprite: Image.Image, palette) -> np.ndarray:
    '''Apply black (convenience)'''
    return recolor(np.array(sprite.convert('RGBA')),'black',palette)
  
def paste(src: Image.Image, dst: Image.Image, loc:tuple(int,int), snap: int = 0):
    src.paste(dst,
              tuple([int(x-(s/2)) for x,s in zip(loc,dst.size)]) if snap == 0 else 
              (int(loc[0]-(dst.width/2)),min(loc[1],24-dst.height)) if snap == 1 else
              (int(loc[0]-(dst.width/2)),loc[1]-dst.height),
              dst.convert('RGBA'))
    return src
    
def generate_image(ears,legs,eyes,mouth,color,variant,typ,rand):
    with Image.open(f'./data/generator/sprites/{typ}_{variant}.png') as im:
      palette = np.array(Image.open(f"./data/palettes/default.png").convert("RGB"))
      with open('./data/generator/spritedata.json') as f:
        spritedata = json.loads(f.read())
        
      if legs != 0:
        positions = spritedata[typ][variant][('1leg' if legs == 1 else f'{legs}legs')] 
        for leg in positions:
          with Image.open(f'./data/generator/sprites/parts/legs/{rand.randint(1,5)}.png') as i:
            im = paste(im,i,leg,1)
      if ears != 0:
        positions = spritedata[typ][variant][('1ear' if ears == 1 else '2ears')] 
        for ear in positions:
          with Image.open(f'./data/generator/sprites/parts/ears/{rand.randint(1,4)}.png') as i:
            im = paste(im,i,ear,2)
      if eyes != 0:
        with Image.open(f'./data/generator/sprites/parts/eyes/{eyes}.png') as i:
          im = paste(im,blacken(i,palette),spritedata[typ][variant]['eyes'][0])
      if mouth:
        try:
          with Image.open(f'./data/generator/sprites/parts/mouth.png') as i:
            im = paste(im,blacken(i,palette),spritedata[typ][variant]['mouth'][0])
        except:
          pass
          
      #Recolor after generation
      im = recolor(np.array(im),color,palette)
      
      #Send generated sprite
      btio = BytesIO()
      im.resize((192,192),Image.NEAREST).save(btio,'png')
      btio.seek(0)
      return btio
def character(seed: str = None):
    '''Generates a random character. (These are bad but I'm not a good spriter lol)'''
    rand = Random()
    rand.seed(seed)
    ears = rand.choice([0,0,0,1,2,2,2,2])
    legs = rand.choice([0,0,1,2,2,2,3,4,4,4])
    eyes = rand.choice([0,0,1,2,2,2,2,2,3,4,5,6])
    mouth = rand.random() > 0.75
    color = rand.choice(['pink','red','maroon','yellow','orange','gold','brown','lime','green','cyan','blue','purple','white','silver','grey'])
    variant = rand.choice(['smooth','fuzzy','fluffy','polygonal','skinny','belt'])
    typ = rand.choice(['long','tall','curved','round'])
    a = rand.choice(['b','c','d','f','g','h','j','k','l','m','p','q','r','s','t','v','w','x','y','z','sh','ch','th','ph','cr','gr','tr','br','dr','pr','bl','sl','pl','cl','gl','fl','sk','sp','st','sn','sm','sw'])
    b = rand.choice(['a','e','i','o','u','ei','oi','ea','ou','ai','au','bu'])
    c = rand.choice(['b','c','d','f','g','h','j','k','l','m','p','q','r','s','t','v','w','x','y','z','sh','ch','ck','th','ph','sk','sp','st'])
    name = rand.choice([a+b+a+b,a+b,a+b+c,b+c,a+c+b,a+c+b+a+c+b,b+c+b+c,a+b+c+a+b+c,b+a]).title()
    if (name == config["name"] if "name" in config else True) and (color == config["color"] if "color" in config else True) and (variant == config["variant"] if "variant" in config else True) and (typ == config["type"] if "type" in config else True) and (mouth == (config["mouth"]=="True") if "mouth" in config else True) and (eyes == int(config["eyes"]) if "eyes" in config else True) and (legs == int(config["legs"]) if "legs" in config else True) and (ears == int(config["ears"]) if "ears" in config else True):
        if "saveImg" in config and config["saveImg"] == "True":
          b = generate_image(ears,legs,eyes,mouth,color,variant,typ,rand)
          img = Image.open(b)
          img.save(f"./img/{seed}.png")
        return True
    return False
seeds = []
nameent = config["name"] if "name" in config else "any"
colorent = config["color"] if "color" in config else "any"
variantent = config["variant"] if "variant" in config else "any"
typeent = config["type"] if "type" in config else "any"
eyesEnt = config["eyes"] if "eyes" in config else "any"
earsEnt = config["ears"] if "ears" in config else "any"
mouthEnt = config["mouth"] if "mouth" in config else False
legsEnt = config["legs"] if "legs" in config else "any"
startFrom = config["startFrom"] if "startFrom" in config else 0
b = math.floor(int(startFrom)/1000)-1 if "startFrom" in config else -1
for i in range((int(startFrom) if "startFrom" in config else 0), (int(config["searchThrough"]) if "searchThrough" in config and config["searchThrough"] != "inf" else 999999999999999999999999)+1):
    keke = character(i)
    if i%1000 == 0:
        b+=1
        os.system("cls")
        print("RIC Bruteforcer")
        print(f'Searching for: \"{nameent}\", {colorent}, {variantent}, {typeent} body with {eyesEnt} eyes, {earsEnt} ears'+(", a mouth, " if mouthEnt == True else ", ")+f'and {legsEnt} legs')
        if b >= 1000000:
            print(f'Searched {b/1000000}b+ seeds')
        elif b >= 1000:
            print(f'Searched {b/1000}m+ seeds')
        else:
            print(f'Searched {b}k+ seeds')
        print("Seeds found:")
        print(str(seeds))
    if keke == True:
        seeds.append(i)
