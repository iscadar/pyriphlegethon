from PIL import Image, ImageFilter, ImageEnhance
from os.path import exists
from datetime import datetime
import random as rnd
import glob
import pygame
import pygame_gui
import pickle

#initialising the game
pygame.init()
X = 600
Y = 600
pygame.display.set_caption('Pyriphlegethon')
window_surface = pygame.display.set_mode((X, Y))
background = pygame.Surface((X, Y))
background.fill(pygame.Color('#000000'))
manager = pygame_gui.UIManager((X, Y))
bg = pygame.image.load("GUI/PYR.png")

feed_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (100, 50)),
                                            text='FEED',
                                            manager=manager)

clock = pygame.time.Clock()
is_running = True

#initialising the image processing
image_list = []
filename_list = []
#both .jpg and .png work but super hacky, make a better load/save/os manipulation thing
imgtype = ['.png', '.jpg']

#add checks for files so thing doesn't crash
for it in imgtype:
    for filename in glob.glob('INIMG/*' + it): 
        im=Image.open(filename)
        
        image_list.append(im)
        rm_dir = filename.replace("INIMG\\", "")
        filename_list.append(rm_dir) # file/filename processing

#genome/parameters for the phonemes
genome = {
    'sns_shift' : rnd.randint(2, 32),
    'gauss_radius' : rnd.randint(2, 20),
    'erode_cycles' : rnd.randint(1, 15),
    'dilate_cycles' : rnd.randint(1, 15),
    'color_enh' : rnd.uniform(0.0, 5.0),
    'contrast_enh' : rnd.uniform(0.0, 5.0),
    'bright_enh' : rnd.uniform(0.0, 5.0),
    'sharp_enh' : rnd.uniform(0.0, 5.0)
}

#phonemes from ImageFilter and ImageEnhance module
def split_n_shift(image):
    shift = genome['sns_shift']
    
    red, green, blue = image.split()

    zeroed_red = red.point(lambda _: 0)
    zeroed_blue = blue.point(lambda _: 0)
    zeroed_green = green.point(lambda _: 0)

    zeroed_blue.paste(blue, (rnd.randint(-red.width//shift, red.width//shift), rnd.randint(-red.height//shift, red.height//shift)))
    zeroed_green.paste(green, (rnd.randint(-red.width//shift, red.width//shift), rnd.randint(-red.height//shift, red.height//shift)))

    image = Image.merge("RGB", (red, zeroed_green, zeroed_blue))
    return image
def filt_box(image):
    radius = 5
    image = image.filter(ImageFilter.BoxBlur(radius))
    return image
def filt_gauss(image):
    radius = genome['gauss_radius']
    image = image.filter(ImageFilter.GaussianBlur(radius))
    return image
def filt_sharp(image):
    image = image.filter(ImageFilter.SHARPEN)
    return image
def filt_smooth(image):
    image = image.filter(ImageFilter.SMOOTH)
    return image
def filt_edges(image):
    image = image.filter(ImageFilter.FIND_EDGES)
    return image
def filt_enhance(image):
    image = image.filter(ImageFilter.EDGE_ENHANCE)
    return image
def filt_emboss(image):
    image = image.filter(ImageFilter.EMBOSS)
    return image
def filt_erode(image):
    cycles = genome['erode_cycles']
    for _ in range(cycles):
        image = image.filter(ImageFilter.MinFilter(3))
    return image
def filt_dilate(image):
    cycles = genome['dilate_cycles']
    for _ in range(cycles):
        image = image.filter(ImageFilter.MaxFilter(3))
    return image
def filt_contour(image):
    image = image.filter(ImageFilter.CONTOUR)
    return image
def enhance_color(image):
    enhancer = ImageEnhance.Color(image).enhance(genome['color_enh'])
    return image
def enhance_contrast(image):
    enhancer = ImageEnhance.Contrast(image).enhance(genome['contrast_enh'])
    return image
def enhance_bright(image):
    enhancer = ImageEnhance.Brightness(image).enhance(genome['bright_enh'])
    return image
def enhance_sharp(image):
    enhancer = ImageEnhance.Sharpness(image).enhance(genome['sharp_enh'])
    return image

#add a way to select from subsets of phonemes for each of multiple verbs
phonemes = {
  # 1 : filt_box, #might remove because of gauss blur and/or enhance sharp
  2 : filt_gauss,
  # 3 : filt_sharp, #might be obsolete because of enhance sharp
  4 : filt_smooth, #might be obsolete because of enhance sharp
  5 : filt_edges,
  6 : filt_enhance,
  # 7 : filt_emboss,
  8 : filt_erode,
  9 : filt_dilate,
  # 10 : filt_contour,
  11 : split_n_shift,
  12 : enhance_color,
  13 : enhance_contrast,
  14 : enhance_bright,
  15 : enhance_sharp
}

#saving and loading functions
def save():
    saveGame = open('SAVES/savegame.dat', 'wb')
    saveValues = (life, datetime.now())
    pickle.dump(saveValues, saveGame)
    saveGame.close()
def load():
    loadGame = open('SAVES/savegame.dat', 'rb')
    loadValues = pickle.load(loadGame)
    life = loadValues[0]
    last = loadValues[1]
    # location = loadValues[2]
    loadGame.close()
    return life, last

#load game here/set life
if exists('SAVES/savegame.dat'):
    life, last = load()
    life -= (datetime.now()-last).total_seconds()*.001
else:
    life = 100 #PYR's lifeforce

while is_running:
    time_delta = clock.tick(60)/1000.0
    life -= time_delta*.02
    if life > 100:
        life = 100
    elif life < 0:
        life = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save()
            #save game here
            is_running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == feed_button:
                pick_img = rnd.randint(0, len(image_list)-1)

                with image_list[pick_img] as img:
                    img.load()

                # truncated permutation of dictionary keys list/allows for varying dictionaries
                verb = rnd.sample(list(phonemes.keys()), rnd.randint(1, len(phonemes)//2))
                
                pverb = ''
                for i in verb:
                    img = phonemes[i](img)
                    pverb = pverb + str(i)
                                
                # save output image
                sv_file = filename_list[pick_img]
                clean_filename = sv_file.replace(sv_file[-4:-1], '_' + pverb + sv_file[-4:-1])
                img.save('OUTIMG/'+ clean_filename)

                life += 5
                print('Pyriphlegethon has fed!')

        manager.process_events(event)
    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    window_surface.blit(bg, (0, 0))
    font = pygame.font.Font(None, 18)
    text = font.render('Life: ' + str(round(life, 1)), True, (255, 255, 255))
    textRect = text.get_rect()
    textRect.center = (510, 50)
    window_surface.blit(text, textRect)
    manager.draw_ui(window_surface)
    pygame.display.update()