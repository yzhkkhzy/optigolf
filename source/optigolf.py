import pygame
import pymunk
import random
import colorsys
import sys
import math
import os
import time
import json
import ast
from pynput.mouse import Controller
from pygame._sdl2 import Window
mouse = Controller()

pygame.init()
fps = 60
clock = pygame.time.Clock()
width, height = 900, 800
window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
main = window.copy()
winder = Window.from_display_module()
space = pymunk.Space()

programIcon = pygame.image.load('assets/logo.png')
pygame.display.set_icon(programIcon)

logo = pygame.image.load('assets/yzhklogo.png')

werebumping = True
starttime = time.time()

pi = math.pi 

sounds = []
for i in range(15):
    sounds.append(pygame.mixer.Sound('assets/' + str(i) + '.wav'))
succsound = pygame.mixer.Sound('assets/' + "succ.wav")
bkgmusicsound = pygame.mixer.Sound('assets/' + "fina music.wav")
bkgmusicsound.play(loops = -1, fade_ms = 8000)
pew = pygame.mixer.Sound('assets/pew.wav')
pullback = pygame.mixer.Sound('assets/pullback.wav')
no = pygame.mixer.Sound('assets/no.wav')
ding = pygame.mixer.Sound('assets/ding.wav')
# bkgmusic.play()

pygame.font.init() 
font = pygame.font.SysFont('assets/Futura-Medium-01.ttf', 30)
bigfont = pygame.font.SysFont('assets/Futura-Medium-01.ttf', 100)
def rectdraw(surface, color, coords, sizes, corner = 0, border = 0):
    shape_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    pygame.draw.rect(shape_surf, color, (coords, sizes), border, corner)
    surface.blit(shape_surf, (0,0))
def hsbtorgb(rotation, trans = 255):
    # rotation is 0-1
    colo = colorsys.hsv_to_rgb(rotation % 1, 1, 1)
    r, g, b = colo
    r = r*255
    g = g*255
    b = b*255
    return (r,g,b, trans)
def rgbtohsb(color, trans = 255):
    # returns the rotation in [0], but also contains value and brightness
    rotation = colorsys.rgb_to_hsv(color[0], color[1], color[2])
    return rotation
def remap(old_val, old_min, old_max, new_min, new_max):
    if old_max - old_min == 0:
        p = old_max - old_min + .01
    else:
        p = old_max - old_min
    output = (new_max - new_min)*(old_val - old_min) / p + new_min
    return output
def textify(string, x, y, surface, color = None, rot = 0, big = False):
    if big:
        text = str(string)
        textimg = bigfont.render(text, True, (color))
        textimg = pygame.transform.rotate(textimg, rot)
        text_rect = textimg.get_rect(center=(x, y))
        surface.blit(textimg, text_rect)
    else:
        if color == None:
            text = str(string)
            textimg = font.render(text, True, (0,0,0))
            textimg = pygame.transform.rotate(textimg, rot)
            text_rect = textimg.get_rect(center=(x, y))
            surface.blit(textimg, text_rect)
        else:
            text = str(string)
            textimg = font.render(text, True, color)
            textimg = pygame.transform.rotate(textimg, rot)
            text_rect = textimg.get_rect(center=(x, y))
            surface.blit(textimg, text_rect)
    

def circledraw(surface, color, center, radius):
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)
class Prism():
    leftx = 0
    lefty = 0
    rightx = 0
    righty = 0
    w = 100
    surface = main
    def __init__(self, lx, ly, rx, ry):
        self.leftx = lx
        self.lefty = ly
        self.rightx = ry
        self.righty = ry
    def draw(self):
        pygame.draw.line(self.surface, (0,255,255), (self.leftx, self.lefty), (self.rightx, self.righty), 5)
class Button():
    def __init__(self, xx, yy, ww, hh):
        self.x = xx
        self.y = yy
        self.w = ww
        self.h = hh
        self.ison = False
    def draw(self):
        pygame.draw.rect(main, (255, 255,255), (self.x - self.w / 2 - 5 / 2 , self.y - self.h / 2, self.w  + 5, self.h + 5), 5)
        if self.ison:
            textify('x', self.x, self.y, main, (255, 255, 255))
    def check(self):
        if math.dist(pygame.mouse.get_pos(), (self.x, self.y)) < self.w + 10:
            return True
        else:
            return False
class menuButt(Button):
    def draw(self):
        pygame.draw.rect(main, (0,0,0), (self.x - self.w / 2 - 5 / 2 , self.y - self.h / 2, self.w  + 5, self.h + 5))
        textify('=', self.x, self.y, main, (255, 255, 255))
class resetButt(Button):
    def draw(self):
        pygame.draw.rect(main, (0,0,0), (self.x - self.w / 2 - 5 / 2 , self.y - self.h / 2, self.w  + 5, self.h + 5))
        textify('>', self.x, self.y, main, (255, 255, 255))
cbmode = Button(200, 150, 25, 25)
sfx = Button(200, 300, 25, 25)
bkgmusic = Button(200, 450, 25, 25)
menubutt = menuButt(20, 20, 25, 25)
reset = resetButt(width - 20, 20, 25, 25)
bkgmusic.ison = True
sfx.ison = True
prisms = []
colorblindnessmode = False
timesincelastsound = time.time()
def playballsound(ball, volume = .1):
    global timesincelastsound
    if ball.mag() > 3 and not(ball.isstuck) and sfx.ison:
        number = random.randint(0, 14)
        sounds[number].play()
        sounds[number].set_volume(volume)
        timesincelastsound = time.time()
class Ball():
    drawshakex = 0
    drawshakey = 0
    def __init__(self, x, y, xspeed, yspeed, radius, color):
        self.radius = 15
        mass = 1
        self.color=color
        self.body=pymunk.Body(mass)
        self.body.position=(x, y)
        self.body.velocity=(xspeed, yspeed)
        self.shape=pymunk.Circle(self.body, self.radius)
        self.shape.elasticity=1
        self.shape.density=1
        space.add(self.body, self.shape)
        self.iscolliding = True
        self.shape.collision_type = 1
        self.surface = main
        self.isingoal = False
        self.isinspecgoal = False
        self.specholein = specialHole(-500, -500, (255, 255, 255), 30, 't')
        self.body.velocity_func = self.customgravbong
        # experimental
        # self.shape.filter = pymunk.ShapeFilter(group = 3)
        self.isbeingslapshot = False
        self.isstuck = False
        self.stuckto = 0
        self.inmotion = False
        self.isinside = False
        self.lasttimeadded = time.time()
        self.frictioniness = .96
        self.shape.filter = pymunk.ShapeFilter(categories = 0b001, mask = 0b011)
    def slapshotprotocol(self):
        self.shape.filter = pymunk.ShapeFilter(categories = 0b001, mask = 0b001)
        # self.frictioniness = .8
    def draw(self):
        x=int(self.body.position.x)
        y=int(self.body.position.y)
        pygame.draw.circle(main, self.color, (x + self.drawshakex,y + self.drawshakey), self.radius)
        text = math.floor(rgbtohsb(self.color)[0] * 10)
        if colorblindnessmode:
            textify(text, self.body.position.x, self.body.position.y, self.surface, (0,0,0))  
    def friction(self):
        # adds friction
        if self.isstuck:
            self.body.velocity *= .92
        else:
            self.body.velocity *= .98
        
    def mag(self):
        # returns unnormalized magnitude i think
        return abs(self.body.velocity[0]) + abs(self.body.velocity[1])
    def check(self):
        nowrect = pygame.Rect(self.body.position.x - self.radius, self.body.position.y - self.radius, self.radius * 2, self.radius * 2)
        bigrect = pygame.Rect(self.body.position.x - self.radius * 4, self.body.position.y - self.radius* 4, self.radius * 8, self.radius * 8)

        # prism detection
        for prism in prisms:
            if nowrect.clipline((prism.leftx, prism.lefty), (prism.rightx, prism.righty)):
                self.iscolliding = True
                if self.color == (255, 255, 255):
                    self.color = hsbtorgb(random.randint(0, 100) / 100)
                addball(self, int(remap(self.mag(), 0, 1000, 2, 6)))
             
            # elif not(bigrect.clipline((prism.leftx, prism.lefty), (prism.rightx, prism.righty))):
            #     self.iscolliding = False
            #     prismonrn = 0

            
        # level detection
        if self.body.position.x + self.radius + self.radius /2 > width - level.outerlevelmargin:
            self.body.velocity = (self.body.velocity[0] * -1, self.body.velocity[1])
            if self.mag() > 3:
                playballsound(self, remap(self.mag(), 0, 500, 0, .1))
        if self.body.position.x - self.radius - self.radius / 2< level.outerlevelmargin:
            self.body.velocity = (self.body.velocity[0] * -1, self.body.velocity[1])
            if self.mag() > 3:
                playballsound(self, remap(self.mag(), 0, 500, 0, .1))
        if self.body.position.y + self.radius + self.radius /2 > height - level.outerlevelmargin:
            self.body.velocity = (self.body.velocity[0], self.body.velocity[1] * -1)
            if self.mag() > 3:
                playballsound(self, remap(self.mag(), 0, 500, 0, .1))
        if self.body.position.y - self.radius - self.radius / 2 < level.outerlevelmargin:
            self.body.velocity = (self.body.velocity[0], self.body.velocity[1] * -1)
            if self.mag() > 3:
                playballsound(self, remap(self.mag(), 0, 500, 0, .1))
        # hole detection
        if math.dist(self.body.position, (hole.x, hole.y)) < hole.radius + self.radius / 2:
            self.isingoal = True
        else:
            self.isingoal = False
        # special hole detection
        for specialhole in specialholes:
            if math.dist(self.body.position, (specialhole.x, specialhole.y)) < specialhole.radius - 10 + self.radius / 2:
                self.isinspecgoal = True
                self.specholein = specialhole
            # else:
        if math.dist(self.body.position, (self.specholein.x, self.specholein.y)) > self.specholein.radius + self.radius / 2:
            self.isinspecgoal = False
                
            #     self.isinspecgoal = False
        # stop detection
        if self.mag() > 1:
            self.inmotion = True
        if self.mag() < 1 and self.inmotion:
            self.stop()
            # print('were stoppng')
            self.inmotion = False
    def stop(self):
        if self.isbeingslapshot:
            self.shape.filter = pymunk.ShapeFilter(categories = 0b001, mask = 0b011)
            self.frictioniness = .96
        self.isbeingslapshot = False
        self.isstuck = False
        
    def checkclick(self):                                       #              ...margin of error 
        if math.dist(self.body.position, pygame.mouse.get_pos()) < self.radius * 1.5:
            self.isbeingslapshot = False
            self.isstuck = False
            return True
        else:
            return False
    def customgravbong(self, body, gravity, damping, dt):
        g = ((hole.x - self.body.position.x) * gravsucc, (hole.y - self.body.position.y) * gravsucc)
        
        # ga = ((self.stuckto[0].position.x - self.body.position.x) * gravsucc, (self.stuckto[0].position.y - self.body.position.y) * gravsucc)
        if self.isingoal:
            pymunk.Body.update_velocity(body, g, damping, dt)
        elif self.isstuck:
            # ga = ((self.stuckto[0].position.x - self.body.position.x) * gravsuccc, (self.stuckto[0].position.y - self.body.position.y) * gravsuccc)
            # pymunk.Body.update_velocity(body, ga, damping, dt)
            pass
        if self.isinspecgoal:
            gh = ((self.specholein.x - self.body.position.x) * gravsucc, (self.specholein.y - self.body.position.y) * gravsucc)
            pymunk.Body.update_velocity(body, gh, damping, dt)
        # elif self.isstuck:
        #     ga = ((self.stuckto[0].position.x - self.body.position.x) * gravsuccc, (self.stuckto[0].position.y - self.body.position.y) * gravsuccc)
        #     pymunk.Body.update_velocity(body, ga, damping, dt)
gravsucc = 25
gravsuccc = 50
lastballadded = time.time()
interval = .5
def addball(ball, number, color = None):
    if color == None:
        if ball.lasttimeadded + interval < time.time():
            for i in range(number):
                if len(balls) < maxballs:
                    balls.append(Ball(ball.body.position.x, ball.body.position.y, ball.body.velocity[0],  ball.body.velocity[1], 10, hsbtorgb(ball.mag() / 100 + (random.randint(-20, 20) / 8) % 10) ))
                else:
                    print('too many')
        ball.lasttimeadded = time.time()
    else:
        if ball.lasttimeadded + interval < time.time():
            for i in range(number):
                if len(balls) < maxballs:
                    balls.append(Ball(ball.body.position.x, ball.body.position.y, ball.body.velocity[0],  ball.body.velocity[1], 10, (color)))
                else:
                    # print('way too many')
                    pass
        ball.lasttimeadded = time.time()
maxwidth = 150
maxheight = 150
border = 5
texts = []
isdonevaluating = False
fileinfo = []
par = 0
class Levelmanager():
    currentlevel = 0
    levelstrings = []
    levelrn = 0
    text = ''
    starttimer = time.time()
    istiming = False
    targeting = 0
    def exportlevels(self):
        jasonstring = json.dumps(self.jason)
        # print(jasonstring)

        f = open('assets/levels.json', 'w')
        f.write(jasonstring)
        f.close()
    def check(self):
        global isevaluating
        global isdonevalutating
        global par
        if self.istiming and not(time.time() >  self.starttimer + 1.5):
            if hole.size > 3:
                hole.size -= 3

            for ball in balls:
                if ball.radius > .6:
                    ball.radius -= .6
        if self.istiming and time.time() > self.starttimer + .75:
            if self.currentlevel == 26:
                self.setuplevel(26)
            else:
                self.setuplevel(self.currentlevel + 1)
            
            isdonevaluating = False
            isevaluating = False
            self.istiming = False
            for ball in balls:
                ball.shape.filter = pymunk.ShapeFilter(mask = 0b011)
                gravsucc = 25
            hole.colur = 0
            hole.counter = 0
            hole.transness = 0

    def forward(self):
        for ball in balls:
            ball.shape.filter = pymunk.ShapeFilter(mask = 0b000)

        self.starttimer = time.time()
        self.istiming = True
        # succsound.play()
        # succsound.set_volume(.2)
        hole.haswritten = False


        
      
    
    def hotreload(self):
        self.loadlevels()
        self.setuplevel(self.currentlevel)
    def backward(self):
        self.setuplevel(self.currentlevel - 1)
        # self.currentlevel -= 1
    def loadlevels(self):
        file = open('assets/levels.json', 'r')
        self.text = file.read()
        self.jason = json.loads(self.text)
        file.close()
    def write(self, level, percent):
        # f = open('levelon.txt', 'r')

        # f.close()

        pass


    def setuplevel(self, levelnumber):
        numstring = str(levelnumber)
        global par

        par = 0
        if levelnumber == 26:
            # balls
            for ball in balls:
                space.remove(ball.body, ball.shape)
            balls.clear()
            balls.append(Ball(random.randint(75, width - 75), random.randint(75, height - 75), 0, 0, 10, (255, 255, 255)))
            balls[0].isinspecgoal = False

            # hole
            hole.x = random.randint(75, width - 75)
            hole.y = random.randint(75, height - 75)
            holecolor = hsbtorgb(random.randint(0, 100) / 100)
            hole.color = (holecolor[0], holecolor[1], holecolor[2], 100)
            hole.size = 50

            # walls
            for i in walls:
                space.remove(i[0], i[1])
            walls.clear()
            walla = random.randint(3, 15)
            
            for i in range(walla):
                circlelikelihood = random.randint(0, 10)
                if circlelikelihood > 5:
                    flip = True
                else:
                    flip = False    
                x = random.randint(75, width - 75)
                y = random.randint(75, height - 75)
                w = random.randint(50, 250)
                h = random.randint(50, 250)
                color = hsbtorgb(random.randint(0, 100) / 100)
                level.addwall(x, y, w, h, flip, color)
            
            texts.clear()
            specialholes.clear()
        elif levelnumber < len(self.jason) and levelnumber >= 0:
            
            j = self.jason[numstring]
            # name
            level.title = j['name']
            # balls
            for ball in balls:
                space.remove(ball.body, ball.shape)
            balls.clear()
            balls.append(Ball(width / 2, height / 2, 0, 0, 10, (255, 255, 255)))
            balls[0].body.position = (j['ballx'],j['bally'])
            balls[0].isinspecgoal = False
            
            # hole 
            if j['holeon'] == 'True':
                hole.x = j['holex']
                hole.y = j['holey']
                hole.color = ast.literal_eval(j['holecolor']) 
                hole.size = j['holesize']
            else:
                hole.x = -500
                hole.y = -500
                hole.color = (0,0,0)
            # prisms
            prisms.clear()
            prismas = j['prisms']
            for i in prismas:
                # print(prismas[str(i)])
                prisms.append(Prism(prismas[str(i)]['leftx'],prismas[str(i)]['lefty'],prismas[str(i)]['rightx'],prismas[str(i)]['righty'],))
            # walls
            for i in walls:
                # level.removewall(i)
                space.remove(i[0], i[1])
                # walls.remove(i)
            walls.clear()
            walla = j['walls']
            for i in walla:
                if walla[str(i)]['circley'] == 'True':
                    flip = True
                else:
                    flip = False

                level.addwall(walla[str(i)]['x'],walla[str(i)]['y'],walla[str(i)]['w'],walla[str(i)]['h'],flip,ast.literal_eval(walla[str(i)]['color']))
            # text
            texts.clear()
            t = j['text']
            for tit in range(len(t)):
                string = t[str(tit)]["string"]
                x = t[str(tit)]["x"]
                y = t[str(tit)]["y"]
                size = t[str(tit)]["size"]
                if size == 'True':
                    sizebool = True
                else:
                    sizebool = False
                texts.append((string, x, y, sizebool))
            # special holes :)
            specialholes.clear()
            s = j['special holes']
            for sis in range(len(s)):
                x = s[str(sis)]['x']
                y = s[str(sis)]['y']
                color = ast.literal_eval(s[str(sis)]['holecolor'])
                size = s[str(sis)]['holesize']
                target = s[str(sis)]['target']
                specialholes.append(specialHole(x, y, color, size, target))
                # print(specialholes[sis].target)       
                
        else:

            d = {str(levelnumber): {
                "name": "",
                "ballx": 450,
                "bally": 400,
                "holeon": "False",
                "holex": 500,
                "holey": 500,
                "holecolor": "(255, 0, 0, 100)",
                "holesize": 50,
                "prisms": {},
                "walls": {},
                "text": {},
                "special holes": {}}}

            self.jason.update(d)
            # print(self.jason)
            # ball
            # balls[0].body.position = (width/2, height/2)
            for ball in balls:
                space.remove(ball.body, ball.shape)
            balls.clear()
            balls.append(Ball(width / 2, height / 2, 0, 0, 10,(255, 255, 255)))
            balls[0].body.position = (width/2, height/2)
            # hole
            hole.x = -500
            hole.y = -500
            # prisms
            prisms.clear()
            # walls
            for i in walls:
                # level.removewall(i)
                space.remove(i[0], i[1])
                # walls.remove(i)
            walls.clear()
            level.addwall(-500, -500, 50, 50, True, (255, 255, 255))
            texts.clear()
            specialholes.clear()
        self.currentlevel = levelnumber
walls = []     
        
levelmanager = Levelmanager()
levelmanager.loadlevels()

isevaluating = False

# 0level
# 1ball details (ballx, bally)
# 2hole details (holex, holey, holecolor)
# 3([prism details])
# 4(wall details)
# 5name
# leveldetails = [(0, (510.2455940492768, 716.9732794978537), (172, 522, (0, 255, 0, 100), 66.2872536767062), [(325, 494, 325, 651), (229, 640, 370, 547)], [(279.5, 309.5, 135, 167, False, (255, 255, 255)), (335, 158, 150.41608956491322, 0, True, (255, 255, 255))], "''")]
leveldetails = [(0, (width / 2, height / 2), (-500, -500, (255, 255, 255, 100), 10), [(-500, -500, -500, -500)], [(-500, -500, 500, 500, False, (255, 255, 255))], "''"), (0, (510.2455940492768, 716.9732794978537), (172, 522, (0, 255, 0, 100), 66.2872536767062), [(325, 494, 325, 651), (229, 640, 370, 547)], [(279.5, 309.5, 135, 167, False, (255, 255, 255)), (335, 158, 150.41608956491322, 0, True, (255, 255, 255))], "''"), (0, (width / 2, height / 2), (-500, -500, (255, 255, 255, 100), 10), [(-500, -500, -500, -500)], [(-500, -500, 500, 500, False, (255, 255, 255))], "penis")]

class Level():
    currentlevel = 0
    shapes = []
    shapedimensions = []
    numberofshapes = 50
    shapedensity = 1/2
    circliness = 50
    outerlevelmargin = 40
    color = (255, 255, 255)
    title = ''
    def addwall(self, xx, yy, ww, hh, circley, coloor):
        ship = pymunk.Body(body_type = pymunk.Body.STATIC)
        x = xx
        y = yy
        w = ww
        h = hh
        color = coloor
        ship.position = (x,y)

        if circley:
            shipshape = pymunk.Circle(ship, (w))
        else:
            shipshape = pymunk.Poly.create_box(ship, (w, h))
        shipshape.elasticity = 1
        space.add(ship, shipshape)
        shipshape.collision_type = 2
        self.filter = pymunk.ShapeFilter(categories = 0b010, mask = 0b000)
        # self.shapes.append((ship, shipshape))
        walls.append((ship, shipshape, x, y, w, h, circley, color))
    def removewall(self, walltoremove):
        # try:
        space.remove(walls[walltoremove][0], walls[walltoremove][1])
        walls.remove(walls[walltoremove])
       

    def nextlevel(self):
        if (self.currentlevel + 1 < len(leveldetails)):
            level.currentlevel += 1
            print(level.currentlevel)
            level.reset()  
        else:
            print('nah we good')
    def randomizedim(self):
        for dim in range(self.numberofshapes):
            x = dim * 25 + random.randint(-300, 300)
            y = dim * 25 + random.randint(-250, 250)
            # dear god this is ugly
            for d in range(len(self.shapedimensions)):
                if math.dist((x,y), (self.shapedimensions[d][0], self.shapedimensions[d][1])) < self.numberofshapes / self.shapedensity:
                    x = -1000
                    y = -1000
                elif math.dist((x,y), (hole.x, hole.y)) < hole.radius:
                    x = -1000
                    y = -1000
            w = random.randint(20, maxwidth)
            h = random.randint(20, maxheight)
            circlechance = random.randint(0, 100)
            
            if circlechance > self.circliness: 
                self.shapedimensions.append((x,y,w,h, True))
            else:
                self.shapedimensions.append((x,y,w,h, False))
    def setlevel(self):
        if self.currentlevel < len(leveldetails):
            # title
            self.title = leveldetails[self.currentlevel][5]
            # ball
            balls[0].body.position = (leveldetails[self.currentlevel][1][0], leveldetails[self.currentlevel][1][1])

            # hole
            hole.x = leveldetails[self.currentlevel][2][0]
            hole.y = leveldetails[self.currentlevel][2][1]
            hole.color = leveldetails[self.currentlevel][2][2]
            hole.size = leveldetails[self.currentlevel][2][3]
            # prisms
            prismdimensions = leveldetails[self.currentlevel][3]
            for i in range(len(prismdimensions)):
                prisms.append(Prism())
            for g in range(len(prismdimensions)):
                prisms[g].leftx = prismdimensions[g][0]
                prisms[g].lefty = prismdimensions[g][1]
                prisms[g].rightx = prismdimensions[g][2]
                prisms[g].righty = prismdimensions[g][3]
            # walls
            self.shapedimensions = leveldetails[self.currentlevel][4]
            for i in range(len(self.shapedimensions)):
                ship = pymunk.Body(body_type = pymunk.Body.STATIC)
                x = self.shapedimensions[i][0]
                y = self.shapedimensions[i][1]
                w = self.shapedimensions[i][2]
                h = self.shapedimensions[i][3]
                color = self.shapedimensions[i][4]
                ship.position = (x,y)

                if self.shapedimensions[i][4]:
                    shipshape = pymunk.Circle(ship, (w))
                else:
                    shipshape = pymunk.Poly.create_box(ship, (w, h))
                shipshape.elasticity = 1
                space.add(ship, shipshape)
                shipshape.collision_type = 2
                # experimental
                self.filter = pymunk.ShapeFilter(categories = 0b010, mask = 0b000)
                self.shapes.append((ship, shipshape))
    def hardreset(self):
        prisms.clear()
        self.shapedimensions.clear()
        
        for thing in self.shapes:
            space.remove(thing[0], thing[1])
        self.shapes.clear()
        # print(self.shapes)
        # leveldetails = [(0, (width / 2, height / 2), (-500, -500, (255, 255, 255, 100), 10), [(-500, -500, -500, -500)], [(-500, -500, 500, 500, False, (255, 255, 255))], "''")]
        self.setlevel()
    def reset(self):
        for thing in self.shapes:
            space.remove(thing[0], thing[1])
        self.shapes.clear()
        self.shapedimensions.clear()

        global prisms
        global prismdetails
        # prisms = []
        # for ball in balls:
        #     space.remove(ball.body, ball.shape)
        # balls.clear()
        # balls.append(Ball(width / 2, height / 2, 0, 0, 10, (255, 255, 255)))
        global leveldetails
        # leveldetails = [(level.currentlevel,(balls[0].body.position.x, balls[0].body.position.y), (hole.x, hole.y, hole.color, hole.size), prismdetails, level.shapedimensions, '')]

        self.shapedimensions = leveldetails[self.currentlevel][4]
        for i in range(len(self.shapedimensions)):
            ship = pymunk.Body(body_type = pymunk.Body.STATIC)
            x = self.shapedimensions[i][0]
            y = self.shapedimensions[i][1]
            w = self.shapedimensions[i][2]
            h = self.shapedimensions[i][3]
            color = self.shapedimensions[i][4]
            ship.position = (x,y)

            if self.shapedimensions[i][4]:
                shipshape = pymunk.Circle(ship, (w))
            else:
                shipshape = pymunk.Poly.create_box(ship, (w, h))
            shipshape.elasticity = 1
            space.add(ship, shipshape)
            shipshape.collision_type = 2
            # experimental
            self.filter = pymunk.ShapeFilter(categories = 0b010, mask = 0b000)
            self.shapes.append((ship, shipshape))

        
        # global prismdetails
        # leveldetails = [(level.currentlevel,(balls[0].body.position.x, balls[0].body.position.y), (hole.x, hole.y, hole.color, hole.size), prismdetails, level.shapedimensions, '')]
        # self.setlevel()
    def solidify(self):
        global leveldetails
        # leveldetails.append(((len(leveldetails)),(balls[0].body.position.x, balls[0].body.position.y), (hole.x, hole.y, hole.color), prismdetails, level.shapedimensions, ''))
        print(str((level.currentlevel,(balls[0].body.position.x, balls[0].body.position.y), (hole.x, hole.y, hole.color, hole.size), prismdetails, level.shapedimensions, '\'\'' )))
    def draw(self):
        if len(walls) > 0:
            for wall in range(len(walls)):
                will = walls[wall]
                x = will[2]
                y = will[3]
                w = will[4]
                h = will[5]
                circ = will[6]
                colur = will[7]
                # white borders
                if circ:
                    pygame.draw.circle(main, colur, (x,y), w + border, 5)
                else:
                    pygame.draw.rect(main, colur, (x - w / 2 - border, y - h / 2 - border, w + border * 2, h + border * 2), 5)
                pygame.draw.rect(main, (255,255,255), (self.outerlevelmargin, self.outerlevelmargin, width - self.outerlevelmargin * 2, height - self.outerlevelmargin * 2), 5)
            for wall in range(len(walls)):
                will = walls[wall]
                x = will[2]
                y = will[3]
                w = will[4]
                h = will[5]
                circ = will[6]
                colur = will[7]  
                # black borders
                if circ:
                    pygame.draw.circle(main, (0,0,0), (x,y), w)
                else:
                    pygame.draw.rect(main, (0,0,0), (x - w / 2, y - h / 2, w, h))
                if debugging:
                    textify(wall, x, y, main, (255, 255, 255))
                pygame.draw.rect(main, (0,0,0), (0,0,width, height), self.outerlevelmargin)
                textify(self.title, width / 2, height - 10, main, (255,255,255))
                if debugging:
                    textify(wall, x, y, main, (255, 255, 255))
                if colorblindnessmode:
                    textify(math.floor(rgbtohsb(colur)[0] * 10), x, y, main, (255, 255, 255))
        else:
            pygame.draw.rect(main, (255,255,255), (self.outerlevelmargin, self.outerlevelmargin, width - self.outerlevelmargin * 2, height - self.outerlevelmargin * 2), 5)
            pygame.draw.rect(main, (0,0,0), (0,0,width, height), self.outerlevelmargin)
            # textify(self.title, width / 2, height - 10, main, (255,255,255))
        menubutt.draw()
        reset.draw()
    def drawr(self):
        # white borders
        for i in range(len(self.shapes)):
            x = self.shapedimensions[i][0]
            y = self.shapedimensions[i][1]
            w = self.shapedimensions[i][2]
            h = self.shapedimensions[i][3]
            color = self.shapedimensions[i][5]
            if self.shapedimensions[i][4]:
                pygame.draw.circle(main, color, (x,y), w + border)
            else:
                pygame.draw.rect(main, color, (x - w / 2 - border, y - h / 2 - border, w + border * 2, h + border * 2))
        
        pygame.draw.rect(main, (255,255,255), (self.outerlevelmargin, self.outerlevelmargin, width - self.outerlevelmargin * 2, height - self.outerlevelmargin * 2), 10)
        # black boxes  
        for i in range(len(self.shapes)):
            x = self.shapedimensions[i][0]
            y = self.shapedimensions[i][1]
            w = self.shapedimensions[i][2]
            h = self.shapedimensions[i][3]
            if self.shapedimensions[i][4]:
                pygame.draw.circle(main, (0,0,0), (x,y), w)
            else:
                pygame.draw.rect(main, (0,0,0), (x - w / 2, y - h / 2, w, h))
        pygame.draw.rect(main, (0,0,0), (0,0,width, height), self.outerlevelmargin)
        textify(self.title, width / 2, height - 10, main, (255,255,255))
        
class Hole():
    # dont call me a hole! ur the hole
    x = width / 2
    y = height /2
    radius = 100
    size = radius
    iscounting = False
    countingfrom = 0
    color = (255, 0 ,0, 150)
    fullness = 0
    howfull = 0
    isshaking = False
    startedshaking = 0
    isspecial = False
    transness = 0
    timr = time.time()
    colur = 0
    haswritten = False
    counter = 0
    def aberrationcheck(self):
        ballsingoal = []
        for ball in balls:
            if ball.isingoal:
                if not(ball.color == (255, 255, 255)):
                    ballsingoal.append(ball)
        
        if time.time() > self.timr + .01:
            if self.transness < 150:
                self.transness += 1 
            self.timr = time.time()

        if (self.counter < len(ballsingoal)):
            self.colur += rgbtohsb(ballsingoal[self.counter].color)[0]
            self.counter += 1
            
                
            
        newcolor = hsbtorgb(self.colur / (self.counter + 0.01))
        
        rectdraw(main, (newcolor[0], newcolor[1], newcolor[2], self.transness), (0,0), (width, height))
        level.draw()
        distance = abs(((self.colur / (self.counter + 0.01)) - rgbtohsb(hole.color)[0]))

        distancepercent = distance * 100
        
    
        rectdraw(main, (0,0,0), (width / 2 - 150, height / 2 - 75), (300, 150), corner = 10)
        rectdraw(main, (255, 255, 255), (width / 2 - 150, height / 2 - 75), (300, 150), corner = 10, border = 5)
        textify('chromatic aberration: ' + str(math.floor(distancepercent) )+ '%', width / 2, height / 2 - 50, main, (255, 255, 255))
        textify('par: ' + str(par), width / 2, height / 2, main, (255, 255, 255))
        if distancepercent < 10 and par < 25:
            textify('nice :D', width / 2, height / 2 + 50, main, (255, 255, 255))
        else:
            textify('~terrible~', width / 2, height / 2 + 50, main, (255, 255, 255))
            
        

    def nextcheck(self):
        if hole.fullness > hole.howfull / fullnessratio and hole.iscounting:
            
            global isevaluating
            
            isevaluating = True
            hole.iscounting = False
            if sfx.ison:
                ding.play()
                ding.set_volume(.1)
        else:
            hole.isshaking = True
            if sfx.ison and levelmanager.currentlevel > 10:
                no.play()
                no.set_volume(.1)
            hole.startedshaking = time.time()
    def draw(self):
        if self.isshaking:
            offsetx = random.randint(-3,2)
            offsety = random.randint(-3,2)
            circledraw(main, self.color, (self.x + offsetx, self.y + offsety), self.size)
            if colorblindnessmode and not(self.isspecial):
                textify(math.floor(rgbtohsb(self.color)[0] * 10), self.x, self.y, main, (255, 255, 255))
            if time.time() > self.startedshaking + .1 and self.isshaking:
                self.isshaking = False
        else:
            offsetx = random.randint(-3,2)
            offsety = random.randint(-3,2)
            circledraw(main, self.color, (self.x, self.y), self.size)
            if colorblindnessmode and not(self.isspecial):
                textify(math.floor(rgbtohsb(self.color)[0] * 10), self.x, self.y, main, (255, 255, 255))
    def check(self):
        self.fullness = 0
        self.howfull = self.size**2 * pi
        for ball in balls:
            if ball.isingoal:
                self.fullness += pi * ball.radius**2
        self.finishcheck()

    def finishcheck(self):
        if self.fullness > self.howfull / fullnessratio and not(self.iscounting):
            self.iscounting = True
            self.countingfrom = time.time()
            # print('commence counting!')
class specialHole(Hole):
    target = 0
    def __init__(self, xx, yy, ccolor, ssize, tt):
        self.x = xx
        self.y = yy
        self.color = ccolor
        self.size = ssize
        self.target = tt
        self.isspecial = True
    def check(self):
        pass
    def nextcheck(self):
        # levelmanager.specforward(self.target)
        for ball in balls:
            if ball.isinspecgoal and ball.specholein == self:
                levelmanager.setuplevel((self.target))
                print(self.target)
                ball.isinspecgoal = False
        
     
    

specialholes = []
hole = Hole()
fullnessratio = 2

maxballs = 200
balls = []
balls.append(Ball(width / 2, height / 2, 0, 0, 10, (255, 255, 255)))

level = Level()

bgcolor = (0,0,0)
sticking = False

# functions that call back when balls collide heehee
def ballscolliding(arbiter, space, data):
    for ball in balls:
        # cant believe this works haha
        if ball.shape == arbiter.shapes[0]:
            ball1 = ball
        elif ball.shape == arbiter.shapes[1]:
            ball2 = ball
    if ball1.color == (255, 255, 255):
        ball1.color = ball2.color
        ball2.color = (255, 255, 255)
        
    elif ball2.color == (255, 255, 255):
        ball2.color = ball1.color
        ball1.color = (255, 255, 255)
    else:
        b1color = rgbtohsb(ball1.color)[0]
        b2color = rgbtohsb(ball2.color)[0]

        if b1color >= b2color:
            smallestcolor = b2color
            largestcolor = b1color
        else:
            smallestcolor = b1color
            largestcolor = b2color
        if abs((largestcolor - smallestcolor)) < .5:
            b = (largestcolor + smallestcolor) / 2
            # print('1bigger 2')
        else:
            b = (largestcolor + smallestcolor + 1) / 2
            # print('2bigger1')
        # b = (largestcolor + smallestcolor + 1) / 2
        ballnewcolor = hsbtorgb(b)
        
        # ballnewcolor = hsbtorgb((b1color + b2color) / 2)
        # ballnewcolor = hsbtorgb((b1color + b2color) / 2)
        # if ball1.lasttimeadded + 2 < time.time() and not(ball1.isingoal) and not(ball2.isingoal):
        if not(ball1.isingoal) and not(ball2.isingoal) and ball1.lasttimeadded + 2 < time.time() and not(ball1.isinspecgoal) and not(ball2.isinspecgoal):
            ball1.color = ballnewcolor 
            ball2.color = ballnewcolor
            playballsound(ball1, remap(ball1.mag(), 0, 500, 0, .1))
            
def ballstothewalls(arbiter, space, data):
    global nicetext
    for ball in balls:
        if ball.shape == arbiter.shapes[0] or ball.shape == arbiter.shapes[1]:
            ball1 = ball
    for wall in range(len(walls)):
        if walls[wall][1] == arbiter.shapes[0] or walls[wall][1] == arbiter.shapes[1]:
            wall1 = walls[wall]
            colur = walls[wall][7]
    playballsound(ball1, remap(ball1.mag(), 0, 500, 0, .1))
    if ball1.mag() > 1500:
        if levelmanager.currentlevel > 3:
            if colur == (255, 255, 255):
                addball(ball1, int(remap(ball1.mag(), 0, 1000, 2, 5)))

            else:
                addball(ball1, int(remap(ball1.mag(), 0, 1000, 2, 5)), color = colur)
        if levelmanager.currentlevel == 4:
            nicetext = True
        ball1.slapshotprotocol()
        ball1.isstuck = True
        ball1.stuckto = wall1
        return False
    else: 
        return True
handler = space.add_collision_handler(1,1)
handler.separate = ballscolliding

handler2 = space.add_collision_handler(1,2)
handler2.begin = ballstothewalls

ballbeingclicked = 0
randomish = 0

transness = 100
nicetext = False

debugging = False

# expeirmetnal
editmode = ''

prismdetails = []
currentprism = 0
lastmousepos = (0,0)
red = 255
green = 255
blue = 255

levelmanager.setuplevel(0)
helptext1 = False
ht1 = False
while True:
    

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if menubutt.check():
                levelmanager.setuplevel(0)
            if reset.check():
                levelmanager.setuplevel(levelmanager.currentlevel)    
            
            if levelmanager.currentlevel == 1:
                if cbmode.check():
                    cbmode.ison = not(cbmode.ison)
                    if cbmode.ison:
                        colorblindnessmode = True
                    else:
                        colorblindnessmode = False
                if sfx.check():
                    sfx.ison = not(sfx.ison)
                if bkgmusic.check():
                    bkgmusicwason = bkgmusic.ison
                    bkgmusic.ison = not(bkgmusic.ison)
                    if bkgmusic.ison:
                        bkgmusicsound.play(loops = -1, fade_ms = 8000)
                    else:
                        bkgmusicsound.stop()
            if levelmanager.currentlevel == 0:
                helptext1 = True

                   
            lastmousepos = pygame.mouse.get_pos()
            if editmode == "prism":
                # prisms.append(Prism(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[0], 0, 0))
                prisms[currentprism].leftx = pygame.mouse.get_pos()[0]
                prisms[currentprism].lefty = pygame.mouse.get_pos()[1]
                prisms[currentprism].rightx = pygame.mouse.get_pos()[0]
                prisms[currentprism].righty = pygame.mouse.get_pos()[1]
            else:
                for ball in balls:
                    if ball.checkclick():
                        sticking = True
                        par += 1
                        if sfx.ison:
                            pullback.play(fade_ms=10)
                            pullback.set_volume(.2)
                        xlaststickpos = mouse.position[0]
                        ylaststickpos = mouse.position[1]
                        ballbeingclicked = ball
        if event.type == pygame.MOUSEBUTTONUP:
            pullback.stop()
            helptext1 = False
            if editmode == 'hole':
                hole.x = lastmousepos[0]
                hole.y = lastmousepos[1]
                hole.color = (red, green, blue, transness)
                hole.size = math.dist(pygame.mouse.get_pos(), lastmousepos)
                levelmanager.jason[str(levelmanager.currentlevel)]['holeon'] = 'True'
                levelmanager.jason[str(levelmanager.currentlevel)]['holex'] = hole.x
                levelmanager.jason[str(levelmanager.currentlevel)]['holey'] = hole.y
                levelmanager.jason[str(levelmanager.currentlevel)]['holecolor'] = str(hole.color)
                levelmanager.jason[str(levelmanager.currentlevel)]['holesize'] = hole.size
            if editmode == 'prism':
                prisms[currentprism].rightx = pygame.mouse.get_pos()[0]
                prisms[currentprism].righty = pygame.mouse.get_pos()[1]
                newprisms = {str(len(prisms)): {'leftx': prisms[currentprism].leftx, 'lefty': prisms[currentprism].lefty, 'rightx': prisms[currentprism].rightx, 'righty': prisms[currentprism].righty}}
                levelmanager.jason[str(levelmanager.currentlevel)]['prisms'].update(newprisms)
                currentprism += 1
            if editmode == 'wall':
                w = abs(pygame.mouse.get_pos()[0] - lastmousepos[0])
                h = abs(pygame.mouse.get_pos()[1] - lastmousepos[1])

                xx = {str(len(walls)): {'x': pygame.mouse.get_pos()[0] - w / 2, 'y': pygame.mouse.get_pos()[1] - h / 2, 'w': w, 'h': h, 'circley': str(False), 'color': str((red, green, blue))}}
    
                levelmanager.jason[str(levelmanager.currentlevel)]['walls'].update(xx)
                
                level.addwall(pygame.mouse.get_pos()[0] - w / 2, pygame.mouse.get_pos()[1] - h / 2, w, h, False, (red, green, blue))
            if editmode == 'ballwall':
                xx = {str(len(walls)): {'x': lastmousepos[0], 'y': lastmousepos[1], 'w': math.dist(lastmousepos, pygame.mouse.get_pos()), 'h': 0, 'circley': str(True), 'color': str((red, green, blue))}}
    
                levelmanager.jason[str(levelmanager.currentlevel)]['walls'].update(xx)
                
                level.addwall(lastmousepos[0], lastmousepos[1], math.dist(lastmousepos, pygame.mouse.get_pos()), 100, True, (red, green, blue))

            if editmode == 'ball':
                balls[0].body.position = pygame.mouse.get_pos()
                levelmanager.jason[str(levelmanager.currentlevel)]['ballx'] = balls[0].body.position[0]
                levelmanager.jason[str(levelmanager.currentlevel)]['bally'] = balls[0].body.position[1]
                # balls.clear()
                
                
            elif sticking:
                if sfx.ison:
                    pew.play()
                    pew.set_volume(.05)
                xsign = 1
                ysign = 1
                xnextspeed = (xlaststickpos - mouse.position[0]) * 5
                ynextspeed = (ylaststickpos - mouse.position[1]) * 5
                if math.dist((xlaststickpos, ylaststickpos), mouse.position) / 10 < balls[0].radius * 2:
                    ballbeingclicked.body.velocity = (xnextspeed, ynextspeed)
                else:
                    if xnextspeed < 0:
                        xsign = -1
                    if ynextspeed < 0:
                        ysign = -1
                    if abs(xlaststickpos -  mouse.position[0]) > ballbeingclicked.radius * 2:
                        xspeed = ballbeingclicked.radius * 125 * xsign
                        ballbeingclicked.body.velocity = (xspeed, ballbeingclicked.body.velocity[1])
                    if abs(ylaststickpos - mouse.position[1]) > ballbeingclicked.radius * 2:
                        yspeed = ballbeingclicked.radius * 125 * ysign
                        ballbeingclicked.body.velocity = (ballbeingclicked.body.velocity[0], yspeed)
                sticking = False
            lastmousepos = (0,0)
            randomish = 0
            red = 255
            blue = 255
            green = 255
        if event.type == pygame.KEYDOWN:
            # if event.key == pygame.K_m:
            #     levelmanager.setuplevel(levelmanager.currentlevel + 1)
            # if event.key == pygame.K_d:
            #     debugging = not(debugging)
            # if event.key == pygame.K_f:
            #     levelmanager.hotreload()
            # if event.key == pygame.K_8:
            #     red = 0
            # if event.key == pygame.K_9:
            #     green = 0
            # if event.key == pygame.K_0:
            #     blue = 0
            if event.key == pygame.K_SPACE:
                if levelmanager.currentlevel == 11 and not(isevaluating):
                    ht1 = not(ht1)
                if isevaluating:
                    levelmanager.forward()
                    succsound.play()
                    succsound.set_volume(.2)

                hole.nextcheck()
                # global isdonevaluating
                
                for specialhole in specialholes:
                    specialhole.nextcheck()
            # if event.key == pygame.K_q:
            #     levelmanager.backward()
            # if event.key == pygame.K_h:
            #     if not(editmode == 'hole'):
            #         editmode = 'hole'
            # if event.key == pygame.K_b:
            #     if not(editmode == 'ball'):
            #         editmode = 'ball'
            # if event.key == pygame.K_p:
            #     if not(editmode == 'prism'):
            #         editmode = 'prism'
            #         prisms.append(Prism(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]))
            #         # prismdetails.append(prisms[currentprism])
            # if event.key == pygame.K_w:
            #     if not(editmode == 'wall'):
            #         editmode = 'wall'
            # if event.key == pygame.K_e:
            #     if not(editmode == 'ballwall'):
            #         editmode = 'ballwall'
            # if event.key == pygame.K_RETURN:
            #     levelmanager.exportlevels()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_1:
                red = 255
            if event.key == pygame.K_2:
                green = 255
            if event.key == pygame.K_3:
                blue = 255
            editmode = ''           
        if event.type == pygame.VIDEORESIZE:
            width = pygame.display.get_surface().get_size()[0]
            height = pygame.display.get_surface().get_size()[1]
        if event.type == pygame.QUIT:
            pygame.quit()
            # for wall in walls:
            #     level.removewall(wall)
            sys.exit()

    if time.time() < starttime + 1:
        main.blit(logo, (0,0,width, height))
    else:
        main.fill(bgcolor)
        if isevaluating:
            level.draw()
            for ball in balls:
                if ball.isingoal:
                    ball.draw()
                ball.check()
                ball.friction()
            hole.draw()
            hole.aberrationcheck()
            levelmanager.check()
        else:
            for prism in prisms:
                prism.draw()
            level.draw()
            levelmanager.check()
            if levelmanager.currentlevel ==  1:
                cbmode.draw()
                sfx.draw()
                bkgmusic.draw()
                
                
            for ball in balls:
                ball.draw()
                ball.friction()
                ball.check()
            for text in texts:
                textify(text[0], int(text[1]), int(text[2]), main, (255, 255, 255), rot = 0, big = bool(text[3]))
            for specialhole in specialholes:
                specialhole.draw()
                specialhole.check()
            hole.draw()
            hole.check()
        if editmode == 'hole' and not(lastmousepos == (0,0)):
            pygame.draw.circle(main, (red, green, blue), lastmousepos, math.dist(lastmousepos, pygame.mouse.get_pos()), 5)
        if editmode == 'wall' and not(lastmousepos == (0,0)):
            pygame.draw.rect(main, (red, green, blue), (lastmousepos[0], lastmousepos[1], abs(pygame.mouse.get_pos()[0] - lastmousepos[0]), abs(pygame.mouse.get_pos()[1] - lastmousepos[1])), 5)
        if editmode == 'ballwall' and not(lastmousepos == (0,0)):
            pygame.draw.circle(main, (red, green, blue), lastmousepos, math.dist(lastmousepos, pygame.mouse.get_pos()), 5)
        if debugging:
            textify((str(red), str(green), str(blue)), 100, 100, main, (255, 255, 255))
            textify(levelmanager.currentlevel, 100, 200, main, (255, 255, 255))
        # draw stick and stuff
        if sticking:
            xnextspeed = (xlaststickpos - mouse.position[0]) / 10
            ynextspeed = (ylaststickpos - mouse.position[1]) / 10
            if math.dist((xlaststickpos, ylaststickpos), mouse.position) / 2 < ballbeingclicked.radius * 8:
                pygame.draw.circle(main, (0,255,0), (ballbeingclicked.body.position), math.dist(ballbeingclicked.body.position, (mouse.position[0] - winder.position[0], mouse.position[1] - winder.position[1])), 5)
                randomish = 0
                ballbeingclicked.drawshake = 0
            else:
                ballbeingclicked.isbeingslapshot = True
                pygame.draw.circle(main, (255,0,0), (ballbeingclicked.body.position), ballbeingclicked.radius * 16 + ( math.dist((ballbeingclicked.body.position), mouse.position) / 25 + randomish), 5)
                ballbeingclicked.drawshakex = random.randint(-3, 2)
                ballbeingclicked.drawshakey = random.randint(-3, 2)
                randomish += random.randint(-1,1)
        if levelmanager.currentlevel == 0 and helptext1:
            textify('- click here', balls[0].body.position.x + 75, balls[0].body.position.y, main, (255, 255, 255))

        if levelmanager.currentlevel == 0 and balls[0].isinspecgoal:
            textify('press space to start', 450, 400, main, (255, 255, 255))
        if levelmanager.currentlevel == 2 and balls[0].isinspecgoal:
            textify('press space to continue', 450, 350, main, (255, 255, 255))
        if nicetext and levelmanager.currentlevel == 4:
            textify('nice!', 450, 400, main, (255, 255, 255))
        if levelmanager.currentlevel == 10:
            textify('- home', menubutt.x + 45, menubutt.y, main, (255, 255, 255))
        if levelmanager.currentlevel == 10:
            textify('reset -', reset.x - 45, reset.y, main, (255, 255, 255))
        if levelmanager.currentlevel == 11 and ht1 and not(isevaluating):
            textify('you need to make enough light to move forward', width / 2, height / 2, main, (255, 255, 255))
    # print(pygame.mouse.get_pos())
    # screenshake here
    window.blit(main, (0,0))
    pygame.display.flip()
    clock.tick(fps)
    space.step(1/fps)