#!/usr/bin/env python

'''
This is an attempt to rewrite the "Test your memory" game.
Started coding at 3/2/2009 and finished at 4/27/2009

"Test your memory" is a simple game for all kids.

I am using midi sounds here so osX users (as always) must have
"Timidity" and "Freepats" installed to actually play.
'''

#-------------------Imports-------------------
import pygame
from pygame.locals import *
from os import path
from random import randint, shuffle

#-------------------Constants-------------------
VERSION = '0.2.1'
SIZE = (300,325)
_FONT = 'VeraSe.ttf'
data_folder = 'mem_data'
FIRST_TIME = 1

#-------------------Colors-------------------
YELLOW = (255,255,0)
GOLD = (255,215,0)

BLACK = (0,0,0)
WHITE = (255,255,255)
FLORAL_WHITE = (255,250,240)

RED = (255,0,0)
MEDIUM_VIOLET_RED = (199,21,133)
PALE_VIOLET_RED = (219,112,147)

GREEN = (0,255,0)
YELLOW_GREEN = (154,205,50)

BLUE = (0,0,255)
AQUAMARINE = (127,255,212)
MIDNIGHT_BLUE = (25,25,112)
SKY_BLUE = (135,206,235)
TURQUOISE = (64,224,208)

PURPLE = (160,32,240)
MAGENTA = (255,0,255)

SADDLE_BROWN = (139,69,19)
PERU = (205,133,63)

ORANGE = (255,165,0)
SALMON = (250,128,114)

#-------------------Global functions-------------------
def load_sound(name):
    pygame.mixer.music.load(path.join(data_folder, name))

def display_some_text(text,size,p,b,orientation):
    font = pygame.font.Font(path.join(data_folder,_FONT), size)
    t = font.render(text, 1, BLACK)
    trect = t.get_rect()
    if orientation == 0:
        trect.left = p[0]
        trect.top = p[1]
    elif orientation == 1:
        trect.centerx = p[0]
        trect.centery = p[1]
    elif orientation == 2:
        trect.right = p[0]
        trect.top = p[1]
    b.blit(t, trect)

#-------------------Classes-------------------
class square:
    def __init__(self,index,x,y,width,height,color,soundfile,background):
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.index = index
        self.color = color
        self.soundfile = soundfile
        self.background = background
        self.status = 0 # flag that represents whether the square is clicked or not
        self.is_dirty = 1 # flag that represents whether the square needs to be drawn
    def press(self):
        load_sound(self.soundfile)
        pygame.mixer.music.play()
        self.image.fill(WHITE)
        self.status = 1
        self.is_dirty = 1
    def unpress(self):
        self.image.fill(self.color)
        self.status = 0
        self.is_dirty = 1
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)
    def update(self):
        if self.is_dirty:
            self.background.blit(self.image,self.rect)
            self.is_dirty = 0

class radio_button:
    def __init__(self,background,text,topleft):
        self.background = background
        self.image2 = pygame.Surface((180, 30)).convert()
        self.image2.fill(FLORAL_WHITE)
        display_some_text(text, 18, (20,4), self.image2,0)
        self.image = self.image2
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        if text == 'Beginner':
            self.is_clicked = 1
        else:
            self.is_clicked = 0
        self.is_dirty = 1
    def draw_a_square(self,filled):
        self.background.lock()
        pygame.draw.rect(self.image2, FLORAL_WHITE, (0,7,15,15))
        if filled:
            f = 0
        else:
            f = 1
        pygame.draw.rect(self.image2, BLACK, (0,7,15,15), f)
        self.background.unlock()
    def update(self):
        if self.is_dirty:
            if self.is_clicked:
                self.draw_a_square(1)
            elif not self.is_clicked:
                self.draw_a_square(0)
            self.background.blit(self.image,self.rect)
            self.is_dirty = 0
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)

class radio_button_holder:
    def __init__(self,choices,place,background):
        self.place = place
        self.background = background
        self.a = radio_button(background,choices[0],[self.place[0],self.place[1]])
        self.b = radio_button(background,choices[1],[self.place[0],self.place[1] + 40])
        self.c = radio_button(background,choices[2],[self.place[0],self.place[1] + 80])
        self.var = 0
    def update(self):
        if self.a.is_clicked and self.a.is_dirty:
            self.b.is_clicked = 0
            self.b.is_dirty = 1
            self.c.is_clicked = 0
            self.c.is_dirty = 1
            self.var = 0
        elif self.b.is_clicked and self.b.is_dirty:
            self.a.is_clicked = 0
            self.a.is_dirty = 1
            self.c.is_clicked = 0
            self.c.is_dirty = 1
            self.var = 1
        elif self.c.is_clicked and self.c.is_dirty:
            self.a.is_clicked = 0
            self.a.is_dirty = 1
            self.b.is_clicked = 0
            self.b.is_dirty = 1
            self.var = 2
        self.a.update()
        self.b.update()
        self.c.update()

class simple_button:
    def __init__(self,x,y,title,background,small=0):
        self.background = background
        if small:
            self.image = pygame.Surface([80,30])
        else:
            self.image = pygame.Surface([120,30])
        self.image.fill(FLORAL_WHITE)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.status = 0
        # Draw the border
        pygame.draw.rect(self.image,BLACK,(0,0,self.rect.width,self.rect.height),1)
        # Draw some shadow lines
        background.lock()
        pygame.draw.line(background,BLACK,(x+1,y+self.rect.height),\
                         (x+self.rect.width-1,y+self.rect.height)) #horizontal
        pygame.draw.line(background,BLACK,(x+self.rect.width,y+1),\
                         (x+self.rect.width,y+self.rect.height)) #vertical
        background.unlock()
        # Display some text
        display_some_text(title,14,(self.rect.width/2,self.rect.height/2),self.image,1)
        self.is_dirty = 1
    def press(self):
        self.rect.inflate_ip(-2,-2)
        self.status = 1
        self.is_dirty = 1
    def unpress(self):
        self.rect.inflate_ip(2,2)
        self.status = 0
        self.is_dirty = 1
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)
    def update(self):
        if self.is_dirty:
            self.background.blit(self.image,self.rect)
            self.is_dirty = 0

#-------------------Game functions-------------------
def welcome(background):
    if not pygame.mixer.music.get_busy(): 
        musicfile = path.join(data_folder,'SchumannOp15No01.mid')
        pygame.mixer.music.load(musicfile)
        pygame.mixer.music.play(-1)

    background.fill(FLORAL_WHITE)
    a = radio_button_holder(['Beginner','Advanced','Expert'],[100,100],background)
    b = simple_button(90,250,'Ok',background)
    display_some_text('Select your level',22,(150,50),background,1)
    group = (a.a,a.b,a.c)
    a.update()
    b.update()
    pygame.display.update()

    r = 1
    run = 1
    esc = 0
    while run:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                esc = 1
                r = 0
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for x in group:
                    if x.is_focused(event.pos[0],event.pos[1]) and not x.is_clicked:
                        x.is_clicked = 1
                        x.is_dirty = 1
                if b.is_focused(event.pos[0],event.pos[1]):
                    b.press()
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if b.status:
                    b.unpress()
                    r = 0
            a.update()
            b.update()
            pygame.display.update()
        if r == 0:
            run = 0


    if esc:
        return -1
    else:
        pygame.mixer.music.stop()
        background.fill(FLORAL_WHITE)
        display_some_text('Follow the randomly',20,(150,100),background,1)
        display_some_text('created pattern',20,(150,150),background,1)
        pygame.display.update()
        _delay(1300)
        return a.var

def play(level,background):

    # make the squares
    squares = []
    colors = []
    playing_colors = [YELLOW,GOLD,BLACK,RED,MEDIUM_VIOLET_RED,PALE_VIOLET_RED,GREEN,\
                      YELLOW_GREEN,BLUE,AQUAMARINE,MIDNIGHT_BLUE,SKY_BLUE,TURQUOISE,\
                      PURPLE,MAGENTA,SADDLE_BROWN,PERU,ORANGE,SALMON]

    life_messages = ['no lives left...','watch it...','oops... try again']

    if level == 0:
        _colors = 4
        _times = 10
        _lives = 3
    elif level == 1:
        _colors = 8
        _times = 15
        _lives = 2
    elif level == 2:
        _colors = 12
        _times = 20
        _lives = 1

    for x in range(_colors):
        shuffle(playing_colors)
        colors.append(playing_colors.pop())

    if level == 0:
        for index,x,y,width,height,color,soundfile in [(0,0,0,150,150,colors[0],'do.mid'),\
                                                 (1,150,0,150,150,colors[1],'re.mid'),\
                                                 (2,0,150,150,150,colors[2],'mi.mid'),\
                                                 (3,150,150,150,150,colors[3],'fa.mid')]:
            squares.append(square(index,x,y,width,height,color,soundfile,background))
    elif level == 1:
        for index,x,y,width,height,color,soundfile in [(0,0,0,75,150,colors[0],'do.mid'),\
                                                 (1,75,0,75,150,colors[1],'re.mid'),\
                                                 (2,150,0,75,150,colors[2],'mi.mid'),\
                                                 (3,225,0,75,150,colors[3],'fa.mid'),\
                                                 (4,0,150,75,150,colors[4],'sol.mid'),\
                                                 (5,75,150,75,150,colors[5],'la.mid'),\
                                                 (6,150,150,75,150,colors[6],'si.mid'),\
                                                 (7,225,150,75,150,colors[7],'upper_do.mid')]:
            squares.append(square(index,x,y,width,height,color,soundfile,background))
    elif level == 2:
        for index,x,y,width,height,color,soundfile in [(0,0,0,75,100,colors[0],'do.mid'),\
                                                 (1,75,0,75,100,colors[1],'do#.mid'),\
                                                 (2,150,0,75,100,colors[2],'re.mid'),\
                                                 (3,225,0,75,100,colors[3],'re#.mid'),\
                                                 (4,0,100,75,100,colors[4],'mi.mid'),\
                                                 (5,75,100,75,100,colors[5],'fa.mid'),\
                                                 (6,150,100,75,100,colors[6],'fa#.mid'),\
                                                 (7,225,100,75,100,colors[7],'sol.mid'),\
                                                 (8,0,200,75,100,colors[8],'sol#.mid'),\
                                                 (9,75,200,75,100,colors[9],'la.mid'),\
                                                 (10,150,200,75,100,colors[10],'la#.mid'),\
                                                 (11,225,200,75,100,colors[11],'si.mid')]:
            squares.append(square(index,x,y,width,height,color,soundfile,background))

    # make the cpu_list
    cpu_list = []
    for x in range(_times):
        cpu_list.append(randint(1,_colors) - 1)

    # declare some control variables
    esc = 0
    count = 1
    life_has_been_taken = 0
    r = 1
    player_has_won = 0

    # draw the squares & write some text
    for s in squares:
        s.update()
    display_some_text('score:',14,[0,305],background,0)
    display_some_text('lives:',14,[90,305],background,0)
    _print(str(count-1) + '/' + str(_times),background,(45,305,40,20),0)
    _print(str(_lives),background,(132,305,15,20),0)
    pygame.display.update()
    _delay(500)

    # let's play
    while r:

        # cpu plays
        if not life_has_been_taken:
            for x in range(count):
                _delay(200)
                squares[cpu_list[x]].press()
                squares[cpu_list[x]].update()
                pygame.display.update()
                _delay(200)
                squares[cpu_list[x]].unpress()
                squares[cpu_list[x]].update()
                pygame.display.update()

        # clear events - very important
        pygame.event.clear()

        # player plays
        r2 = 1
        run = 1
        pcount = 0
        player_list = []
        while run:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    esc = 1
                    run = 0
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    for s in squares:
                        if s.is_focused(event.pos[0],event.pos[1]):
                            s.press()
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    for s in squares:
                        if s.status:
                            s.unpress()
                            player_list.append(s.index)
                            pcount += 1
                            if pcount == count:
                                r2 = 0
            for s in squares:
                s.update()
            pygame.display.update()
            if r2 == 0:
                run = 0

        # let's check
        if esc:
            break
        if cpu_list[:count] != player_list:
            if _lives > 0:
                _lives -= 1
                life_has_been_taken = 1
                _print(life_messages[_lives],background,(300,305,150,20),2)
            elif _lives == 0:
                r = 0
        elif cpu_list[:count] == player_list:
            count += 1
            if count > _times:
                player_has_won = 1
                r = 0
            if life_has_been_taken:
                life_has_been_taken = 0
                _print('OK',background,(300,305,150,20),2)
            elif not life_has_been_taken:
                _print('',background,(150,305,150,20),0)

        # print some messages
        _delay(500)
        _print(str(count-1) + '/' + str(_times),background,(45,305,40,20),0)
        _print(str(_lives),background,(132,305,15,20),0)
        pygame.display.update()
        _delay(500)
        
        # clear events - very important
        pygame.event.clear()

    if esc:
        return -1

    return player_has_won

def after_play(player_has_won,level,background):
    musicfile = path.join(data_folder,'SchumannOp15No01.mid')
    pygame.mixer.music.load(musicfile)
    pygame.mixer.music.play(-1)

    background.fill(FLORAL_WHITE)

    if player_has_won and level in [0,1]:
        _status = 1
        display_some_text("That's great !!!",20,(150,100),background,1)
        display_some_text('Go to next level now...',20,(150,150),background,1)

        b = simple_button(90,250,'Ok',background)
        b.update()
        pygame.display.update()

        run = 1
        esc = 0
        while run:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    esc = 1
                    run = 0
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if b.is_focused(event.pos[0],event.pos[1]):
                        b.press()
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    if b.status:
                        b.unpress()
                        run = 0
                b.update()
                pygame.display.update()

        level += 1

    else:
        _status = 2
        if player_has_won:
            display_some_text('You are a memory',20,(150,100),background,1)
            display_some_text('expert now !!!',20,(150,150),background,1)
        else:
            display_some_text('Better luck next time...',20,(150,125),background,1)

        b1 = simple_button(47,250,'Play',background,1)
        b2 = simple_button(174,250,'Credits',background,1)
        group = (b1,b2)
        for x in group:
            x.update()
        pygame.display.update()

        run = 1
        esc = 0
        choice = 0
        while run:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    esc = 1
                    run = 0
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    for x in group:
                        if x.is_focused(event.pos[0],event.pos[1]):
                            x.press()
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    if b1.status:
                        b1.unpress()
                        choice = 3
                        run = 0
                    if b2.status:
                        b2.unpress()
                        choice = 4
                        run = 0
                for x in group:
                    x.update()
                pygame.display.update()

    if esc:
        return 0

    if _status == 1:
        return level
    elif _status == 2:
        return choice

def _credits(background):
    pygame.mixer.music.stop()
    musicfile = path.join(data_folder,'SchumannOp15No03.mid')
    pygame.mixer.music.load(musicfile)
    pygame.mixer.music.play(-1)

    background.fill(FLORAL_WHITE)
    b1 = simple_button(174,250,'Next',background,1)
    b2 = simple_button(47,250,'Ok',background,1)
    group = (b1,b2)
    for x in group:
        x.update()

    text_file = path.join(data_folder,'Info.txt')
    in_file = open(text_file,'r')
    opened_file = in_file.readlines()
    in_file.close()
    y = 0
    text = ''
    o = opened_file[0]
    for x in o:
        if x == '^':
            display_some_text(text,14,(150,55+y),background,1)
            y += 20
            text = ''
        else:
            text += x

    pygame.display.update()

    line = 1
    run = 1
    esc = 0
    signal = 0
    y = 0
    text = ''

    while run:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                esc = 1
                run = 0
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for x in group:
                    if x.is_focused(event.pos[0],event.pos[1]):
                        x.press()
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if b1.status:
                    b1.unpress()
                    background.fill(FLORAL_WHITE,(0,0,300,240))
                    o = opened_file[line]
                    for x in o:
                        if x == '^':
                            display_some_text(text,14,(150,55+y),background,1)
                            y += 20
                            text = ''
                        else:
                            text += x
                    o = opened_file[line+1]
                    if o == '%\n':
                        line = 0
                    else:
                        line += 1
                    text = ''
                    y = 0
                if b2.status:
                    b2.unpress()
                    signal = 1
                    run = 0
            for x in group:
                x.update()
            pygame.display.update()

    pygame.mixer.music.stop()

    if esc:
        return 0
    return signal

def _delay(t):
    while pygame.time.delay(t) < t:
        pass

def _print(text,background,fillrect,x):
    if x == 2:
        _fillrect = (fillrect[0]-150,fillrect[1],fillrect[2],fillrect[3])
        background.fill(FLORAL_WHITE,_fillrect)
    else:
        background.fill(FLORAL_WHITE,fillrect)
    display_some_text(text,14,(fillrect[0],fillrect[1]),background,x)

def main():
    pygame.init()
    background = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('Test your memory v' + VERSION)
    background.fill(FLORAL_WHITE)

    run = 1
    while run:
        level = welcome(background)
        if level == -1:
            run = 0
        elif level in [0,1,2]:
            run2 = 1
            while run2:
                result = play(level,background)
                if result == -1:
                    run = 0
                    run2 = 0
                elif result in [0,1]:
                    run3 = 1
                    while run3:
                        decision = after_play(result,level,background)
                        if decision == 0:
                            run = 0
                            run2 = 0
                            run3 = 0
                        elif decision in [1,2]:
                            level = decision
                            run3 = 0
                        elif decision == 3:
                            run2 = 0
                            run3 = 0
                        elif decision == 4:
                            run4 = 1
                            while run4:
                                _info = _credits(background)
                                if _info == 0:
                                    run = 0
                                    run2 = 0
                                    run3 = 0
                                    run4 = 0
                                elif _info == 1:
                                    run2 = 0
                                    run3 = 0
                                    run4 = 0
    pygame.quit()

if __name__ == "__main__": main()
