from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import sys
import time
import random
import os
last_time = time.time()

MENU = 0             #initial vari
JERSEY_SELECTION = 1
DIFFICULTY_SELECTION = 2  
nam_inpt = 3
plyrs = 4
gm_ovr = 5

current_state = MENU

window_side = 1920
window_Tall = 1080


key_states = {}  #movementt

power_meter = {
    'value': 0.0,
    'max_power': 2.0,
    'charging': False,
    'charge_rate': 3.0,
    'show_meter': False,
    'last_shot_power': 0.0,
    'last_shot_time': 0,
    'show_last_power': False
}

class Game:
    def __init__(self):
        self.score = 0
        self.game_time = 0
        self.total_game_time = 240  
        self.is_plyrs = True
        self.gm_ovr = False
        self.ball_pos = [0, 0.3, 0]
        self.ball_vel = [0, 0, 0]
        self.player_has_ball = False
        self.last_goal_time = -5
        self.goal_message = ""
        self.goal_message_time = 0
        self.winner = None
        self.selected_jersey = "brazil"  
        self.player_nam = "YOU"  
        self.team_scores = {"blue": 0, "red": 0, "yellow": 0, "green": 0}
        self.winner_team = None
        self.difficulty = "easy"  #ARU: difficulty modes     


game = Game()

whole_field = 20.0     #field dim
gl_side = 3.0
gl_tall = 2.0
gl_line = whole_field / 2 

player = {                       #Self player
    'pos': [0, 0, 0],
    'rot': 0,
    'speed': 0.15,
    'sp_speed': 0.15,  #ARU
    'team': 'yellow',
    'jrsy_num': 10
}

gl_plane = whole_field / 2 - 0.5    #goal pos and collis
goalies = {
    'nrth': {
        'pos': [0, 0, -gl_plane],
        'dir': 1, 
        'anim': 0, 
        'team': 'blue',
        'collision_box': {'x': 0, 'z': -gl_plane, 'width': gl_side, 'height': gl_tall, 'depth': 0.5}
    },
    'est': {
        'pos': [gl_plane, 0, 0],
        'dir': 1, 
        'anim': 30, 
        'team': 'red',
        'collision_box': {'x': gl_plane, 'z': 0, 'width': 0.5, 'height': gl_tall, 'depth': gl_side}
    },
    'suth': {
        'pos': [0, 0, gl_plane],
        'dir': 1, 
        'anim': 60, 
        'team': 'yellow',
        'collision_box': {'x': 0, 'z': gl_plane, 'width': gl_side, 'height': gl_tall, 'depth': 0.5}
    },
    'wst': {
        'pos': [-gl_plane, 0, 0],
        'dir': 1, 
        'anim': 90, 
        'team': 'green',
        'collision_box': {'x': -gl_plane, 'z': 0, 'width': 0.5, 'height': gl_tall, 'depth': gl_side}
    }
}

cam_mode = "PLAYER"  
cam_height = 3.0
cam_dist = 5.0

menu_selection = 0  
jersey_selection = 0  
difficulty_selection = 0         # easy(0), hard(1)
gm_ovr_selection = 0       # restart(0), quit(1)

nam_inpt = ""
nam_cursor_pos = 0
max_nam_LENGTH = 15

ball_owner = None  # possesion of rthe vall

ai_plyrs = [
    {"pos": [ 4,0,4],"rot":180, "speed": 0.01, "nam":"Bot-1", "team":"red"},
    {"pos": [-4,0,4],"rot":180, "speed": 0.01, "nam":"Bot-2", "team":"green"},
    {"pos": [ 0,0,-6],"rot":0, "speed": 0.01, "nam":"Bot-3", "team":"blue"},
]

win_SCORE = 3
last_shooter_team = None


pick_cooldwn = 0.8   #sec    #Ball pickup
KNOCKBACK_DIST  = 2
last_pickup_block = {"human": 0.0, 0: 0.0, 1: 0.0, 2: 0.0}

push_cooldwn = 0.35  # sec #Push (while holding ball)
push_rnge = 1.35
push_dist = 1.2
lst_push_time = 0.0
                                                        
superpower = {               #ARU Superpower - random spawn after each goal
    'active': False,         
    'type': None,            #freeze/speed
    'pos': [0, 0, 0],       
    'spawn_time': 0,        
    'lifetime': 3.0,         #sec
    'effect_active': False,  
    'effect_time': 0,       
    'effect_duration': 5.0,  
    'rotation': 0,           
    'last_type': None        #toggle
}


def spawn_superpower(): #ARU:Randomly spawn
    global superpower
    
    if random.random() < 0.90:
        superpower['active'] = True
         
        if superpower['last_type'] == 'freeze':  #toggle freeze and speed
            superpower['type'] = 'speed'
        elif superpower['last_type'] == 'speed':
            superpower['type'] = 'freeze'
        else:   #none
            superpower['type'] = random.choice(['freeze', 'speed'])
        
        superpower['last_type'] = superpower['type']
        
        
        field_halved = whole_field / 2 - 3  #Random position to spawn
        superpower['pos'] = [
            random.uniform(-field_halved, field_halved),
            0.5,  #HeightFixed
            random.uniform(-field_halved, field_halved)
        ]
        superpower['spawn_time'] = time.time()
        superpower['rotation'] = 0
    else:
        superpower['active'] = False
        #no change last power for toggle

def init():
    glClearColor(0.1, 0.2, 0.3, 1.0)  # Dark blue background
    glEnable(GL_DEPTH_TEST)
    

def set_cam():
    if cam_mode == "OVERHEAD":
    
        glLoadIdentity()

        gluLookAt(0, 18, 0,
                  0, 0, 0,
                  0, 0, 1)
        glRotatef(180, 0, 1, 0)

    elif cam_mode == "PLAYER":
        angle_rad = math.radians(player['rot'])
        offset_x = math.sin(angle_rad) * cam_dist
        offset_z = math.cos(angle_rad) * cam_dist
        
        cam_x = player['pos'][0] - offset_x
        cam_y = cam_height
        cam_z = player['pos'][2] - offset_z 
        glLoadIdentity()
        gluLookAt(0, 5, whole_field/2 + 5,
                  0, 2, 0,
                  0, 1, 0)


def art_square_field():
    field_halved = whole_field / 2

    #1st
    glColor3f(0.8, 0.6, 0.5)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-field_halved-6, 0, -field_halved-6)
    glVertex3f(field_halved+6, 0, -field_halved-6)
    glVertex3f(field_halved+6, 0, field_halved+6)
    glVertex3f(-field_halved-6, 0, field_halved+6)
    glEnd()
    #2nd
    glColor3f(0.9, 0.6, 0.5)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-field_halved-13, 0, -field_halved-13)
    glVertex3f(field_halved+13, 0, -field_halved-13)
    glVertex3f(field_halved+13, 0, field_halved+13)
    glVertex3f(-field_halved-13, 0, field_halved+13)
    glEnd()
   
    glColor3f(0.2, 0.6, 0.2) # grass base
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-field_halved, 0, -field_halved)
    glVertex3f(field_halved, 0, -field_halved)
    glVertex3f(field_halved, 0, field_halved)
    glVertex3f(-field_halved, 0, field_halved)
    glEnd()
    
            # grass stripes
    stripe_width = 1.0
    for i in range(int(whole_field / stripe_width)):
        x_start = -field_halved + i * stripe_width
        
        if i % 2 == 0:
            glColor3f(0.15, 0.55, 0.15)
        else:
            glColor3f(0.25, 0.65, 0.25)
        
        glBegin(GL_QUADS)
        glVertex3f(x_start, 0.01, -field_halved)
        glVertex3f(x_start + stripe_width, 0.01, -field_halved)
        glVertex3f(x_start + stripe_width, 0.01, field_halved)
        glVertex3f(x_start, 0.01, field_halved)
        glEnd()
    
    
    glColor3f(1.0, 1.0, 1.0) #lines of the field
    glLineWidth(3.0)
    
    # Outer boundary
    glBegin(GL_LINE_LOOP)
    glVertex3f(-field_halved, 0.02, -field_halved)
    glVertex3f(field_halved, 0.02, -field_halved)
    glVertex3f(field_halved, 0.02, field_halved)
    glVertex3f(-field_halved, 0.02, field_halved)
    glEnd()
    
    # center lines 
    glBegin(GL_LINES)
    glVertex3f(-field_halved, 0.02, 0)
    glVertex3f(field_halved, 0.02, 0)
    glVertex3f(0, 0.02, -field_halved)
    glVertex3f(0, 0.02, field_halved)
    glEnd()
    
    
    glBegin(GL_LINE_LOOP)  # Center circle
    for i in range(32):
        angle = 2.0 * math.pi * i / 32
        x = 2.0 * math.cos(angle)
        z = 2.0 * math.sin(angle)
        glVertex3f(x, 0.02, z)
    glEnd()
    
    # Center dot
    glPointSize(9.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0.03, 0)
    glEnd()
    
    
def art_simple_goal(side, color):
    field_halved = whole_field / 2
    
    if side == "nrth":
        x, z = 0, -field_halved
        rotation = 0
    elif side == "est":
        x, z = field_halved, 0
        rotation = 270
    elif side == "suth":
        x, z = 0, field_halved
        rotation = 180
    else:  
        x, z = -field_halved, 0
        rotation = 90
    
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)
    

    glColor3f(color[0], color[1], color[2]) #post color

    # Left goal post (vertical)
    glPushMatrix()
    glTranslatef(-gl_side/2, gl_tall, 0)  # Center at half height
    glRotatef(90, 1, 0, 0)  # Make vertical
    glutSolidCylinder(0.05, gl_tall, 16, 4)  # Same as cuboid width 0.1 -> radius 0.05
    glPopMatrix()

    # Right goal post (vertical)  
    glPushMatrix()
    glTranslatef(gl_side/2 - 0.1, gl_tall, 0)  # Adjusted position like original
    glRotatef(90, 1, 0, 0)  # Make vertical
    glutSolidCylinder(0.05, gl_tall, 16, 4)
    glPopMatrix()

    # Crossbar (horizontal)
    glPushMatrix()
    glTranslatef(-1.55, gl_tall, 0)  # Same offset as original
    glRotatef(90, 0, 1, 0) # No rotation needed - cylinder is horizontal along X-axis by default
    glutSolidCylinder(0.05, gl_side, 16, 4)  # Same as cuboid depth 0.1 -> radius 0.05
    glPopMatrix()
      
    glPopMatrix()

def art_goal_box(side):
    field_halved = whole_field / 2
    box_size = 4.0
    

    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    
    if side == "nrth":
        glBegin(GL_LINE_LOOP)
        glVertex3f(-box_size/2, 0.02, -field_halved)
        glVertex3f(box_size/2, 0.02, -field_halved)
        glVertex3f(box_size/2, 0.02, -field_halved + 2.0)
        glVertex3f(-box_size/2, 0.02, -field_halved + 2.0)
        glEnd()
    elif side == "est":
        glBegin(GL_LINE_LOOP)
        glVertex3f(field_halved - 2.0, 0.02, -box_size/2)
        glVertex3f(field_halved, 0.02, -box_size/2)
        glVertex3f(field_halved, 0.02, box_size/2)
        glVertex3f(field_halved - 2.0, 0.02, box_size/2)
        glEnd()
    elif side == "suth":
        glBegin(GL_LINE_LOOP)
        glVertex3f(-box_size/2, 0.02, field_halved - 2.0)
        glVertex3f(box_size/2, 0.02, field_halved - 2.0)
        glVertex3f(box_size/2, 0.02, field_halved)
        glVertex3f(-box_size/2, 0.02, field_halved)
        glEnd()
    else:  # wst
        glBegin(GL_LINE_LOOP)
        glVertex3f(-field_halved, 0.02, -box_size/2)
        glVertex3f(-field_halved + 2.0, 0.02, -box_size/2)
        glVertex3f(-field_halved + 2.0, 0.02, box_size/2)
        glVertex3f(-field_halved, 0.02, box_size/2)
        glEnd()
    
def art_head():
    # Back cuboid (black)
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, -0.03)
    glScalef(0.15, 0.2, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Front cuboid (skin color)
    glColor3f(0.9, 0.8, 0.7)
    glPushMatrix()
    glTranslatef(0, 0, 0.03)
    glScalef(0.15, 0.2, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()

def art_goalkeeper(side, color):
    goalie = goalies[side]
    
    anim_speed = 1.0 if game.difficulty == "hard" else 0.5 #ARU
    if superpower['effect_active'] and superpower['type'] == 'freeze':#ARU
        anim_speed = 0
    
    goalie['anim'] += goalie['dir'] * anim_speed
    if goalie['anim'] >= 60:
        goalie['anim'] = 60
        goalie['dir'] = -1
    elif goalie['anim'] <= -60:
        goalie['anim'] = -60
        goalie['dir'] = 1
    
    # Calculate goalkeeper position
    if side == "nrth":

        x = goalie['pos'][0] + math.sin(goalie['anim'] * 0.05) * 2.0
        z = goalie['pos'][2]
        rotation = 0
    elif side == "est":
        x = goalie['pos'][0]
        z = goalie['pos'][2] + math.sin(goalie['anim'] * 0.05) * 2.0
        rotation = 270
    elif side == "suth":
        x = goalie['pos'][0] + math.sin(goalie['anim'] * 0.05) * 2.0
        z = goalie['pos'][2]
        rotation = 180
    else:  # wst
        x = goalie['pos'][0]
        z = goalie['pos'][2] + math.sin(goalie['anim'] * 0.05) * 2.0
        rotation = 90
    
    
    if side == "nrth" or side == "suth":  # Update collision box position
        goalie['collision_box']['x'] = x
    else:
        goalie['collision_box']['z'] = z
    
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)
    
    
    glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7) # Goalkeeper body
    
    # Torso
    glPushMatrix()
    glTranslatef(0, 0.9, 0)
    glScalef(0.3, 0.6, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # head 
    glPushMatrix()
    glTranslatef(0, 1.3, 0)
    art_head()
    glPopMatrix()
    
    # arms
    glColor3f(0.667, 0.455, 0.290)
    
    # right arm
    glPushMatrix()
    glTranslatef(0.4, 1.0, 0)
    glRotatef(45, 0, 0, 1)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # left arm
    glPushMatrix()
    glTranslatef(-0.4, 1.0, 0)
    glRotatef(-45, 0, 0, 1)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()
    

    glColor3f(0.9, 0.8, 0.7)
    
    # right leg
    glPushMatrix()
    glTranslatef(0.1, 0.3, 0)
    glScalef(0.1, 0.5, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # left leg
    glPushMatrix()
    glTranslatef(-0.1, 0.3, 0)
    glScalef(0.1, 0.5, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()

count=0

def art_stadium():
    global count
    base = whole_field + 3.0
    hight_step = 0.6
    dpth_step = 0.8
    lyrs = 6

    for i in range(lyrs):
        h = i * hight_step
        offset = i * dpth_step                             

        glBegin(GL_QUADS)   #Top
        glColor3f(1.0, 0.97, 0.75)
        glVertex3f(-base - offset, h, -base - offset)
        glVertex3f( base + offset, h, -base - offset)
        glVertex3f( base + offset, h + hight_step, -base - offset)
        glVertex3f(-base - offset, h + hight_step, -base - offset)
        glEnd()

        glBegin(GL_QUADS)  #Bottm
        glColor3f(0.6, 0.8, 1.0)
        glVertex3f(-base - offset, h, base + offset)
        glVertex3f( base + offset, h, base + offset)
        glVertex3f( base + offset, h + hight_step, base + offset)
        glVertex3f(-base - offset, h + hight_step, base + offset)
        glEnd()

        glBegin(GL_QUADS)  #Left
        glColor3f(0.7, 1.0, 0.85)
        glVertex3f(-base - offset, h, -base - offset)
        glVertex3f(-base - offset, h,  base + offset)
        glVertex3f(-base - offset, h + hight_step,  base + offset)
        glVertex3f(-base - offset, h + hight_step, -base - offset)
        glEnd()

        glBegin(GL_QUADS) #rigjt
        glColor3f(1.0, 0.75, 0.75)
        glVertex3f(base + offset, h, -base - offset)
        glVertex3f(base + offset, h,  base + offset)
        glVertex3f(base + offset, h + hight_step,  base + offset)
        glVertex3f(base + offset, h + hight_step, -base - offset)
        glEnd()
        

#hi
def art_stadium_lights():
    pole_height = 15.0
    pole_radius = 0.4  

    head_size = 2.5      # square light
    tilt_angle = 280    
    d = whole_field + 6.0

    positions = [
        (-d, 0, -d),  # left
        ( d, 0, -d),  # right
        (-d, 0,  d),  # Botleft
        ( d, 0,  d),  # Botright
    ]

    glColor3f(0.3, 0.3, 0.3)  
    
    glPushMatrix()  #left
    glTranslatef(positions[0][0], positions[0][1] + pole_height/2, positions[0][2])  
    glRotatef(90, 1, 0, 0)  
    glutSolidCylinder(pole_radius, pole_height, 16, 1)  # radius, height, slices, stacks
    glPopMatrix()
        
    glPushMatrix() #right
    glTranslatef(positions[1][0], positions[1][1] + pole_height/2, positions[1][2])
    glRotatef(90, 1, 0, 0)
    glutSolidCylinder(pole_radius, pole_height, 16, 1)
    glPopMatrix()
    
    glPushMatrix()   #Botleft
    glTranslatef(positions[2][0], positions[2][1] + pole_height/2, positions[2][2])
    glRotatef(90, 1, 0, 0)
    glutSolidCylinder(pole_radius, pole_height, 16, 1)
    glPopMatrix()
    
    glPushMatrix()  #Botright
    glTranslatef(positions[3][0], positions[3][1] + pole_height/2, positions[3][2])
    glRotatef(90, 1, 0, 0)
    glutSolidCylinder(pole_radius, pole_height, 16, 1)
    glPopMatrix()
    
    #LIGHT head QUad
    glColor3f(1.0, 1.0, 0.95)  
    
    # Top-left
    glPushMatrix()
    head_offset_y = 2.6
    glTranslatef(positions[0][0], positions[0][1] + 7.5 + head_offset_y, positions[0][2])
    glRotatef(tilt_angle, 1, 0, 0)   
    glBegin(GL_QUADS)
    glVertex3f(-head_size, 0, -head_size)
    glVertex3f( head_size, 0, -head_size)
    glVertex3f( head_size, 0,  head_size)
    glVertex3f(-head_size, 0,  head_size)
    glEnd()
    glPopMatrix()
    
    # Top-right
    glPushMatrix()
    glTranslatef(positions[1][0], positions[1][1] + 7.5 + head_offset_y, positions[1][2])
    glRotatef(tilt_angle, 1, 0, 0)
    glBegin(GL_QUADS)
    glVertex3f(-head_size, 0, -head_size)
    glVertex3f( head_size, 0, -head_size)
    glVertex3f( head_size, 0,  head_size)
    glVertex3f(-head_size, 0,  head_size)
    glEnd()
    glPopMatrix()
    
    # Bottom-left
    glPushMatrix()
    glTranslatef(positions[2][0], positions[2][1] + 7.5 + head_offset_y, positions[2][2])
    glRotatef(tilt_angle, 1, 0, 0)
    glBegin(GL_QUADS)
    glVertex3f(-head_size, 0, -head_size)
    glVertex3f( head_size, 0, -head_size)
    glVertex3f( head_size, 0,  head_size)
    glVertex3f(-head_size, 0,  head_size)
    glEnd()
    glPopMatrix()
    
    # Bottom-right
    glPushMatrix()
    glTranslatef(positions[3][0], positions[3][1] + 7.5 + head_offset_y, positions[3][2])
    glRotatef(tilt_angle, 1, 0, 0)
    glBegin(GL_QUADS)
    glVertex3f(-head_size, 0, -head_size)
    glVertex3f( head_size, 0, -head_size)
    glVertex3f( head_size, 0,  head_size)
    glVertex3f(-head_size, 0,  head_size)
    glEnd()
    glPopMatrix()

def art_stand():
    
    pole_height = 15.0
    pole_radius = 0.4
    head_size = 2.5
    tilt_angle = 280
    d = whole_field + 6.0

    positions = [(-d, 0, -d)]

    glColor3f(0.3, 0.3, 0.3) 

    # Pole 1
    glPushMatrix()
    glTranslatef(positions[0][0]+21.5, positions[0][1] + pole_height/2, positions[0][2])
    glRotatef(90, 1, 0, 0)
    glutSolidCylinder(pole_radius, pole_height, 16, 1)
    glPopMatrix()
    
    # Pole 2
    glPushMatrix()
    glTranslatef(positions[0][0]+30, positions[0][1] + pole_height/2, positions[0][2])
    glRotatef(90, 1, 0, 0)
    glutSolidCylinder(pole_radius, pole_height, 16, 1)
    glPopMatrix()

    # Light head
    glPushMatrix()
    head_offset_y = 2.6
    glTranslatef(positions[0][0]+25.7, positions[0][1] + 7.5 + head_offset_y, positions[0][2])
    #hell
    lines = [
        ("BLUE",   game.team_scores["blue"]),
        ("RED",    game.team_scores["red"]),
        ("YELLOW", game.team_scores["yellow"]),
        ("GREEN",  game.team_scores["green"]),
    ]

    for k, (nam, val) in enumerate(lines):
        if k == 0:
            glColor3f(0.0, 0.1, 0.4)  # Blue
            glRasterPos2f(-7, 0.5)
            txt = f"{nam}: {val}"
            for ch in txt:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        elif k == 1:
            glColor3f(1.0, 0, 0)  # Red
            glRasterPos2f(-7, -1.2)
            txt = f"{nam}: {val}"
            for ch in txt:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        elif k == 2:
            glColor3f(1.0, 1.0, 0)  # Yellow
            glRasterPos2f(1.8, 0.5)
            txt = f"{nam}: {val}"
            for ch in txt:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        else:  # k == 3
            glColor3f(0, 1.0, 0)  # Green
            glRasterPos2f(1.8, -1.2)
            txt = f"{nam}: {val}"
            for ch in txt:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
    #hell
    glRotatef(-90, 1, 0, 0)
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.5 , 0.5)
    glVertex3f(-head_size-6, 1, -head_size)
    glVertex3f( head_size+6, 1, -head_size)
    glVertex3f( head_size+6, 1,  head_size)
    glVertex3f(-head_size-6, 1,  head_size)
    glEnd()
    glPopMatrix()
    
    


def art_player():
    global ball_owner
    glPushMatrix()
    glTranslatef(player['pos'][0], 0, player['pos'][2])
    glRotatef(player['rot'], 0, 1, 0)
    
    if game.selected_jersey == "brazil":
        body_color = (1.0, 0.8, 0.0)  

    # Body (torso)
    glColor3f(*body_color)
    glPushMatrix()
    glTranslatef(0, 0.8, 0)
    glScalef(0.25, 0.5, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(0, 1.1, 0)
    art_head()
    glPopMatrix()
    
    # Arms 
    glColor3f(0.776, 0.525, 0.259)
    
    # Right arm
    glPushMatrix()
    glTranslatef(0.2, 0.9, 0)
    if ball_owner == ("human", None):
        glRotatef(90, 1, 0, 0)   
    glScalef(0.07, 0.3, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Left arm
    glPushMatrix()
    glTranslatef(-0.2, 0.9, 0)
    if ball_owner == ("human", None):
        glRotatef(90, 1, 0, 0)   
    glScalef(0.07, 0.3, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glColor3f(0.776, 0.525, 0.259)
    
    # Right leg
    glPushMatrix()
    glTranslatef(0.08, 0.25, 0)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Left leg
    glPushMatrix()
    glTranslatef(-0.08, 0.25, 0)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()
    

    glColor3f(1.0, 1.0, 1.0)
    
    glColor3f(1.0, 1.0, 0.0)
    glRasterPos3f(-0.05 * len(game.player_nam), 1.5, 0.1)
    for ch in game.player_nam:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))
    
    glPopMatrix()

def art_ball():
    glPushMatrix()
    glTranslatef(game.ball_pos[0], game.ball_pos[1], game.ball_pos[2])
    
    vel_mag = math.sqrt(game.ball_vel[0]**2 + game.ball_vel[1]**2 + game.ball_vel[2]**2) # rotate based on velocity
    rotation = game.game_time * vel_mag * 30
    
    glRotatef(rotation, 1, 0, 0)
    glColor3f(1.0, 1.0, 1.0)
    glutSolidSphere(0.2, 16, 16)
    
   
    glColor3f(0.0, 0.0, 0.0)   #patches 
    for i in range(6):
        angle = 2.0 * math.pi * i / 6
        patch_x = 0.15 * math.cos(angle)
        patch_z = 0.15 * math.sin(angle)
        
        glPushMatrix()
        glTranslatef(patch_x, 0, patch_z)
        glutSolidSphere(0.08, 8, 8)
        glPopMatrix()
    
    glPopMatrix()

            #GK and ball collision check
def check_goalkeeper_collision():    
    EXTRA_W = 0.5  
    EXTRA_D = 0.5
    EXTRA_H = 0.25    
    for side, goalie in goalies.items():    #side=nrth/est/suth/wst
        box = goalie['collision_box']
        
                                #check collision with goalkeeper's collision box
        if (abs(game.ball_pos[0] - box['x']) < (box['width']/2 + EXTRA_W) and
            abs(game.ball_pos[2] - box['z']) < (box['depth']/2 + EXTRA_D) and
            game.ball_pos[1] < box['height'] + EXTRA_H):
            
            
            if side == "nrth" or side == "suth": #GK save and push ball
                #push in x direction
                game.ball_vel[0] = -game.ball_vel[0] * 0.8
                #also added with some random deflection
                game.ball_vel[0] += random.uniform(-0.3, 0.3)
            else:
                #push in z direction
                game.ball_vel[2] = -game.ball_vel[2] * 0.8
                #also added with some random deflection
                game.ball_vel[2] += random.uniform(-0.3, 0.3)
            
                     #also some y axis push
            game.ball_vel[1] = abs(game.ball_vel[1]) * 0.5 + 0.2
            
            return True
    
    return False

def check_goal():
    global last_shooter_team,ball_owner
    if last_shooter_team==None:
        return False

    field_halved = gl_plane

    shooter = last_shooter_team
    goal_team = None
    
    #nrth goal
    if (game.ball_pos[2] <= -field_halved and
        abs(game.ball_pos[0]) <= gl_side/2 and
        game.ball_pos[1] <= gl_tall):
        goal_team = "blue"

    #est goal
    elif (game.ball_pos[0] >= field_halved and
          abs(game.ball_pos[2]) <= gl_side/2 and
          game.ball_pos[1] <= gl_tall):
        goal_team = "red"

    # suth goal
    elif (game.ball_pos[2] >= field_halved and
          abs(game.ball_pos[0]) <= gl_side/2 and
          game.ball_pos[1] <= gl_tall):
        goal_team = "yellow"

    # wst goal
    elif (game.ball_pos[0] <= -field_halved and
          abs(game.ball_pos[2]) <= gl_side/2 and
          game.ball_pos[1] <= gl_tall):
        goal_team = "green"
        
    else:
        return False  #not inside any goal
    #no point for own goal
    if goal_team.lower() == shooter.lower():
        game.goal_message = f"OWN GOAL! {shooter.upper()} hit their own net!"
        game.goal_message_time = game.game_time
        reset_round_positions()
        last_shooter_team = None
        return True
    

    if check_goalkeeper_collision():
        return False
    
    scoring_team = last_shooter_team
    if scoring_team == None:
        return False
    
    game.team_scores[shooter] += 1
    game.goal_message = f"GOAL! {shooter.upper()} SCORES!"
    game.goal_message_time = game.game_time

    #check win
    if game.team_scores[shooter] >= win_SCORE:
        game.winner_team = shooter
        game.gm_ovr = True
        game.is_plyrs = False
        global current_state  #ARU menu/play/game over
        current_state = gm_ovr  #ARU
        return True

#kickoff reset
    reset_round_positions()
    last_shooter_team = None
    return True    


def art_menu():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_side, 0, window_Tall)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
   
    glColor3f(0.0, 0.1, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(window_side, 0)
    glVertex2f(window_side, window_Tall)
    glVertex2f(0, window_Tall)
    glEnd()
    
   
    glColor3f(1.0, 1.0, 0.0) #title
    glRasterPos2f(window_side/2 - 136, window_Tall - 190)
    title = "Lessgo..! Hand_Soccer..!"
    for ch in title:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    
    start_color = (0.0, 1.0, 0.0) if menu_selection == 0 else (0.5, 0.5, 0.5)
    quit_color = (1.0, 0.0, 0.0) if menu_selection == 1 else (0.5, 0.5, 0.5)
    
    glColor3f(*start_color) # start but
    glRasterPos2f(window_side/2 - 50, window_Tall/2 + 50)
    start_text = "START GAME"
    for ch in start_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
 
    glColor3f(*quit_color) #quit but
    glRasterPos2f(window_side/2 - 30, window_Tall/2 - 50)
    quit_text = "QUIT"
    for ch in quit_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    # Selection indicator
    glColor3f(1.0, 1.0, 0.0)
    glRasterPos2f(window_side/2 - 80, window_Tall/2 + 50 if menu_selection == 0 else window_Tall/2 - 50)
    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('>'))
     
    
def art_difficulty_selection(): #ARU difficulty selection
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDisable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_side, 0, window_Tall)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(0.0, 0.1, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(window_side, 0)
    glVertex2f(window_side, window_Tall)
    glVertex2f(0, window_Tall)
    glEnd()
    

    glColor3f(1.0, 1.0, 0.0)
    glRasterPos2f(window_side/2 - 120, window_Tall - 100)
    title = "SELECT DIFFICULTY"
    for ch in title:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
    
        #Easy option
    if difficulty_selection == 0:
        glColor3f(0.0, 1.0, 0.0)  #selected
    else:
        glColor3f(0.7, 0.7, 0.7)  
    
    #Easy box
    glBegin(GL_LINE_LOOP)
    glVertex2f(window_side/2 - 200, window_Tall/2 + 100)
    glVertex2f(window_side/2 - 50, window_Tall/2 + 100)
    glVertex2f(window_side/2 - 50, window_Tall/2 - 100)
    glVertex2f(window_side/2 - 200, window_Tall/2 - 100)
    glEnd()
    
     #Easy text
    glRasterPos2f(window_side/2 - 170, window_Tall/2 + 150)
    easy_text = "EASY"
    for ch in easy_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    #Easy description
    if difficulty_selection == 0:
        glColor3f(0.2, 0.8, 0.2)  # Green
    else:
        glColor3f(0.5, 0.5, 0.5)  # Gray
    glBegin(GL_QUADS)
    glVertex2f(window_side/2 - 180, window_Tall/2 + 80)
    glVertex2f(window_side/2 - 70, window_Tall/2 + 80)
    glVertex2f(window_side/2 - 70, window_Tall/2 - 80)
    glVertex2f(window_side/2 - 180, window_Tall/2 - 80)
    glEnd()
    
    #Easy details
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(window_side/2 - 170, window_Tall/2 + 30)
    for ch in "Normal":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glRasterPos2f(window_side/2 - 170, window_Tall/2 + 10)
    for ch in "AI Speed":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glRasterPos2f(window_side/2 - 170, window_Tall/2 - 20)
    for ch in "Normal":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glRasterPos2f(window_side/2 - 170, window_Tall/2 - 40)
    for ch in "Goalkeeper":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glRasterPos2f(window_side/2 - 170, window_Tall/2 - 60)
    for ch in "Speed":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    
    #Hard option
    if difficulty_selection == 1:
        glColor3f(0.0, 1.0, 0.0)  #selected
    else:
        glColor3f(0.7, 0.7, 0.7) 
    
    #Hard box
    glBegin(GL_LINE_LOOP)
    glVertex2f(window_side/2 + 50, window_Tall/2 + 100)
    glVertex2f(window_side/2 + 200, window_Tall/2 + 100)
    glVertex2f(window_side/2 + 200, window_Tall/2 - 100)
    glVertex2f(window_side/2 + 50, window_Tall/2 - 100)
    glEnd()
    
    #Hard text
    glRasterPos2f(window_side/2 + 100, window_Tall/2 + 150)
    hard_text = "HARD"
    for ch in hard_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    #Hard description
    if difficulty_selection == 1:
        glColor3f(1.0, 0.2, 0.2)  # Red
    else:
        glColor3f(0.5, 0.5, 0.5)  # Gray
    glBegin(GL_QUADS)
    glVertex2f(window_side/2 + 70, window_Tall/2 + 80)
    glVertex2f(window_side/2 + 180, window_Tall/2 + 80)
    glVertex2f(window_side/2 + 180, window_Tall/2 - 80)
    glVertex2f(window_side/2 + 70, window_Tall/2 - 80)
    glEnd()
    
    #Hard details
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(window_side/2 + 85, window_Tall/2 + 30)
    for ch in "Fast":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glRasterPos2f(window_side/2 + 85, window_Tall/2 + 10)
    for ch in "AI Speed":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glRasterPos2f(window_side/2 + 85, window_Tall/2 - 20)
    for ch in "Fast":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glRasterPos2f(window_side/2 + 85, window_Tall/2 - 40)
    for ch in "Goalkeeper":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glRasterPos2f(window_side/2 + 85, window_Tall/2 - 60)
    for ch in "Speed":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    
    #Selection indicator
    glColor3f(1.0, 1.0, 0.0)
    if difficulty_selection == 0:
        glRasterPos2f(window_side/2 - 220, window_Tall/2)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('>'))
    else:
        glRasterPos2f(window_side/2 + 210, window_Tall/2)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('<'))

   
    glColor3f(0.0, 1.0, 0.0)
    glRasterPos2f(window_side/2 - 20, 80)
    ok_text = "OK"
    for ch in ok_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    glEnable(GL_DEPTH_TEST)
    

def art_nam_inpt():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_side, 0, window_Tall)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Dark background
    glColor3f(0.0, 0.1, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(window_side, 0)
    glVertex2f(window_side, window_Tall)
    glVertex2f(0, window_Tall)
    glEnd()
    
    # Title
    glColor3f(1.0, 1.0, 0.0)
    glRasterPos2f(window_side/2 - 110, window_Tall - 400)
    title = "ENTER YOUR NAME"
    for ch in title:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
    
            #input box
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(window_side/2 - 200, window_Tall/2 + 30)
    glVertex2f(window_side/2 + 200, window_Tall/2 + 30)
    glVertex2f(window_side/2 + 200, window_Tall/2 - 30)
    glVertex2f(window_side/2 - 200, window_Tall/2 - 30)
    glEnd()
    
    # Current nam
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(window_side/2 - 190, window_Tall/2)
    display_nam = nam_inpt
    if len(display_nam) == 0:
        display_nam = "Hello, YOU"
    
    for ch in display_nam:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
 
    if time.time() % 1.0 < 0.5:  # blinking cursor
        glColor3f(1.0, 1.0, 0.0)
        cursor_x = window_side/2 - 190 + len(display_nam) * 10
        glRasterPos2f(cursor_x, window_Tall/2)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('|'))
    
    
    glColor3f(0.0, 1.0, 0.0)
    glRasterPos2f(window_side/2 - 90, 400)
    ok_text = "ENTER to Start Game"
    for ch in ok_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    # Re-enable 3D features
    glEnable(GL_DEPTH_TEST)
    

def art_hud():
   
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_side, 0, window_Tall)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    
    time_left = max(0, game.total_game_time - game.game_time) # Time remaining
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    
    glColor3f(1.0, 1.0, 0.0)  # Yellow for timer
    glRasterPos2f(window_side/2 - 50, window_Tall - 40)
    time_text = f"TIME: {minutes:02d}:{seconds:02d}"
    for ch in time_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    art_stand()
    
    #ARU: Display active superpower
    if superpower['effect_active']:
        if superpower['type'] == 'freeze':
            glColor3f(0.2, 0.5, 1.0)
            effect_text = "FREEZE ACTIVE!"
        else:
            glColor3f(1.0, 0.8, 0.0)
            effect_text = "SPEED BOOST!"
        
        glRasterPos2f(window_side/2 - 100, window_Tall - 80)
        for ch in effect_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
            #Goal message for 2sec
    if game.game_time - game.goal_message_time < 2.0 and game.goal_message:
        glColor3f(0.0, 1.0, 0.0)  # Green
        glRasterPos2f(window_side/2 - 80, window_Tall/2 + 50)
        for ch in game.goal_message:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
    
            #Pause indicator
    if not game.is_plyrs and not game.gm_ovr:
        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(window_side/2 - 30, window_Tall/2)
        pause_text = "GAME PAUSED"
        for ch in pause_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
    
        #ARU: Game over screen, team stats
    if game.gm_ovr:  
        glColor4f(0.0, 0.0, 0.0, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(window_side, 0)
        glVertex2f(window_side, window_Tall)
        glVertex2f(0, window_Tall)
        glEnd()
        
        #Title
        glColor3f(1.0, 0.85, 0.0)
        glRasterPos2f(window_side/2 - 120, window_Tall - 80)
        gm_ovr_text = "MATCH FINISHED!"
        for ch in gm_ovr_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        
        #winner
        if game.winner_team:
            winner_nam = game.winner_team.upper()
            glColor3f(0.0, 1.0, 0.0)
            glRasterPos2f(window_side/2 - 100, window_Tall - 130)
            winner_text = f" WINNER: {winner_nam} TEAM!"
            for ch in winner_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
         #Stats box background
        stats_y = window_Tall/2 + 100
        glColor3f(0.15, 0.2, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(window_side/2 - 300, stats_y)
        glVertex2f(window_side/2 + 300, stats_y)
        glVertex2f(window_side/2 + 300, stats_y - 280)
        glVertex2f(window_side/2 - 300, stats_y - 280)
        glEnd()
        
        #Stats box border
        glColor3f(1.0, 1.0, 0.0)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(window_side/2 - 300, stats_y)
        glVertex2f(window_side/2 + 300, stats_y)
        glVertex2f(window_side/2 + 300, stats_y - 280)
        glVertex2f(window_side/2 - 300, stats_y - 280)
        glEnd()
        
        #Stats header
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(window_side/2 - 80, stats_y - 30)
        header_text = "MATCH STATISTICS"
        for ch in header_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        #Team stats
        teams_data = [
            ("BLUE", game.team_scores["blue"], (0.0, 0.545, 0.545)),
            ("RED", game.team_scores["red"], (1.0, 0.2, 0.2)),
            ("YELLOW", game.team_scores["yellow"], (1.0, 1.0, 0.2)),
            ("GREEN", game.team_scores["green"], (0.2, 1.0, 0.2))
        ]
        
        start_y = stats_y - 70
        for i, (team_nam, score, color) in enumerate(teams_data):
            y_pos = start_y - (i * 50)
            
            #Team color indicator
            glColor3f(*color)
            glBegin(GL_QUADS)
            glVertex2f(window_side/2 - 270, y_pos + 15)
            glVertex2f(window_side/2 - 240, y_pos + 15)
            glVertex2f(window_side/2 - 240, y_pos - 15)
            glVertex2f(window_side/2 - 270, y_pos - 15)
            glEnd()
            
            #Team name
            glColor3f(1.0, 1.0, 1.0)
            glRasterPos2f(window_side/2 - 220, y_pos - 5)
            for ch in team_nam:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
            
            #Score
            glRasterPos2f(window_side/2 + 50, y_pos - 5)
            score_text = f"Goals: {score}"
            for ch in score_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
            
            #winner crown
            if game.winner_team and team_nam.lower() == game.winner_team.lower():
                glColor3f(1.0, 0.85, 0.0)
                glRasterPos2f(window_side/2 + 180, y_pos - 5)
                crown_text = "<< WINNER"
                for ch in crown_text:
                    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        #Difficulty & time info
        glColor3f(0.7, 0.7, 0.7)
        glRasterPos2f(window_side/2 - 270, stats_y - 250)
        diff_text = f"Difficulty: {game.difficulty.upper()}"
        for ch in diff_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
        
        glRasterPos2f(window_side/2 + 80, stats_y - 250)
        time_text = f"Match Duration: {int(game.total_game_time // 60)}:{int(game.total_game_time % 60):02d}"
        for ch in time_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
        
        #Restart
        button_y = 150
        restart_color = (0.0, 0.8, 0.0) if gm_ovr_selection == 0 else (0.3, 0.5, 0.3)
        glColor3f(*restart_color)
        glBegin(GL_QUADS)
        glVertex2f(window_side/2 - 180, button_y + 30)
        glVertex2f(window_side/2 - 20, button_y + 30)
        glVertex2f(window_side/2 - 20, button_y - 30)
        glVertex2f(window_side/2 - 180, button_y - 30)
        glEnd()
        
        #Restart border
        glColor3f(1.0, 1.0, 1.0) if gm_ovr_selection == 0 else glColor3f(0.5, 0.5, 0.5)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(window_side/2 - 180, button_y + 30)
        glVertex2f(window_side/2 - 20, button_y + 30)
        glVertex2f(window_side/2 - 20, button_y - 30)
        glVertex2f(window_side/2 - 180, button_y - 30)
        glEnd()
        
        #Restart  text
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(window_side/2 - 145, button_y - 5)
        restart_text = "RESTART"
        for ch in restart_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        #Quit
        quit_color = (0.8, 0.0, 0.0) if gm_ovr_selection == 1 else (0.5, 0.3, 0.3)
        glColor3f(*quit_color)
        glBegin(GL_QUADS)
        glVertex2f(window_side/2 + 20, button_y + 30)
        glVertex2f(window_side/2 + 180, button_y + 30)
        glVertex2f(window_side/2 + 180, button_y - 30)
        glVertex2f(window_side/2 + 20, button_y - 30)
        glEnd()
        
        #Quit border
        glColor3f(1.0, 1.0, 1.0) if gm_ovr_selection == 1 else glColor3f(0.5, 0.5, 0.5)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(window_side/2 + 20, button_y + 30)
        glVertex2f(window_side/2 + 180, button_y + 30)
        glVertex2f(window_side/2 + 180, button_y - 30)
        glVertex2f(window_side/2 + 20, button_y - 30)
        glEnd()
        
        #Quit text
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(window_side/2 + 75, button_y - 5)
        quit_text = "QUIT"
        for ch in quit_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(window_side/2 - 150, 80)
        instructions = "Use LEFT/RIGHT arrows to select, ENTER to confirm"
        for ch in instructions:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
  
    
    #power meter
    if current_state == plyrs and game.player_has_ball:
        pass


def art_superpower():   #ARU
    if not superpower['active']:
        return
    
    glPushMatrix()
    glTranslatef(superpower['pos'][0], superpower['pos'][1], superpower['pos'][2])
    glRotatef(superpower['rotation'], 0, 1, 0)
    
    #art by type
    if superpower['type'] == 'freeze':
        glColor3f(0.3, 0.6, 1.0)
        glutSolidSphere(0.15, 16, 16)
        
        for i in range(6):
            angle = i * 60
            x = 0.12 * math.cos(math.radians(angle))
            z = 0.12 * math.sin(math.radians(angle))
            glPushMatrix()
            glTranslatef(x, 0, z)
            glutSolidSphere(0.06, 12, 12)
            glPopMatrix()
    else:  #speed
        glColor3f(1.0, 0.85, 0.2)
        glutSolidSphere(0.12, 16, 16)
        for i in range(4):
            angle = i * 90 + superpower['rotation']
            x = 0.15 * math.cos(math.radians(angle))
            z = 0.15 * math.sin(math.radians(angle))
            glPushMatrix()
            glTranslatef(x, 0, z)
            glColor3f(1.0, 0.95, 0.5)
            glutSolidSphere(0.05, 12, 12)
            glPopMatrix()
    
    glPopMatrix()
    
    #rotating
    
    pulse = math.sin(time.time() * 5) * 0.2 + 0.8
    if superpower['type'] == 'freeze':
        glColor4f(0.2, 0.5, 1.0, pulse)
    else:
        glColor4f(1.0, 0.8, 0.0, pulse)
    
    glPushMatrix()
    glTranslatef(superpower['pos'][0], 0.05, superpower['pos'][2])
    glRotatef(90, 1, 0, 0)
    glutSolidTorus(0.03, 0.3, 8, 16)
    glPopMatrix()
   


def art_ai_player(ai, idx):
    global ball_owner
    glPushMatrix()
    glTranslatef(ai["pos"][0], 0, ai["pos"][2])
    glRotatef(ai["rot"], 0, 1, 0)

    #jersey color
    t = ai["team"].lower().strip()

    if t == "red":
        body_color = (1.0, 0.2, 0.2)
    elif t == "green":
        body_color = (0.2, 1.0, 0.2)
    elif t == "yellow":
        body_color = (1.0, 1.0, 0.2)
    elif t == "blue":
        body_color = (0.0, 0.545, 0.545)

    glColor3f(*body_color)
    glPushMatrix()
    glTranslatef(0, 0.8, 0)    #for lifting slightly
    glScalef(0.25, 0.5, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 1.1, 0)
    art_head()
    glPopMatrix()

    # Arms
    glColor3f(0.776, 0.525, 0.259)

    #Right arm
    glPushMatrix()
    glTranslatef(0.2, 0.9, 0)
    if ball_owner == ("ai", idx):    
        glRotatef(90, 1, 0, 0)   #rotate
    glScalef(0.07, 0.3, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()

    #Left arm
    glPushMatrix()
    glTranslatef(-0.2, 0.9, 0)
    if ball_owner == ("ai", idx):    
        glRotatef(90, 1, 0, 0)   #rotate
    glScalef(0.07, 0.3, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()

    #Legs
    glColor3f(0.776, 0.525, 0.259)
    glPushMatrix()
    glTranslatef(0.08, 0.25, 0)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.08, 0.25, 0)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()

    #nam label

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos3f(-0.05 * len(ai["nam"]), 1.5, 0.1)   
    for ch in ai["nam"]:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))
 
    glPopMatrix()


def ball_movement():
    global current_state  
    if not game.is_plyrs or game.gm_ovr:
        return
    
    # Update game time
    game.game_time += 1/60.0
    
    # Check if game time is up
    if game.game_time >= game.total_game_time:
        game.gm_ovr = True
        game.is_plyrs = False
        current_state = gm_ovr  
        return
    
    # Ball physics
    gravity = -0.098
    friction = 0.99
    bounce_damping = 0.7
    
    # Apply gravity
    game.ball_vel[1] += gravity
    
    # Apply friction
    game.ball_vel[0] *= friction
    game.ball_vel[2] *= friction
    
    # Update position
    game.ball_pos[0] += game.ball_vel[0]
    game.ball_pos[1] += game.ball_vel[1]
    game.ball_pos[2] += game.ball_vel[2]
    
    # Ground collision
    if game.ball_pos[1] < 0.2:
        game.ball_pos[1] = 0.2
        game.ball_vel[1] = -game.ball_vel[1] * bounce_damping
    
    # Boundary collision (walls)
    field_halved = whole_field / 2-0.5
    # X wall collision(Bounce)
    if abs(game.ball_pos[0]) > field_halved:
        in_goal_mouth = (abs(game.ball_pos[2]) <= gl_side/2 and game.ball_pos[1] <= gl_tall)
        if not in_goal_mouth:
            game.ball_pos[0] = field_halved if game.ball_pos[0] > 0 else -field_halved
            game.ball_vel[0] = -game.ball_vel[0] * 0.8

    # Z wall collision(bounce)
    if abs(game.ball_pos[2]) > field_halved:
        in_goal_mouth = (abs(game.ball_pos[0]) <= gl_side/2 and game.ball_pos[1] <= gl_tall)
        if not in_goal_mouth:
            game.ball_pos[2] = field_halved if game.ball_pos[2] > 0 else -field_halved
            game.ball_vel[2] = -game.ball_vel[2] * 0.8
    
    # Check goalkeeper collision
    check_goalkeeper_collision()
    
    # Check for goals
    check_goal()
    
    # Check ball possession
    if ball_owner is not None:
        owner_type, owner_idx = ball_owner

        if owner_type == "human":
            game.ball_pos = hand_attach_position(player["pos"], player["rot"])
        else:
            ai = ai_plyrs[owner_idx]
            game.ball_pos = hand_attach_position(ai["pos"], ai["rot"])

        #Ball is carried
        game.ball_vel = [0, 0, 0]
        game.player_has_ball = (owner_type == "human")
    else:
        #Nobody owns ball
        dx = player['pos'][0] - game.ball_pos[0]
        dz = player['pos'][2] - game.ball_pos[2]
        dist = math.sqrt(dx*dx + dz*dz)
        game.player_has_ball = (dist < 1.0 and game.ball_pos[1] < 0.8)
    
    # Update power meter charging
    if power_meter['charging'] and game.player_has_ball and game.is_plyrs:
        power_meter['value'] += power_meter['charge_rate'] / 60
        if power_meter['value'] > power_meter['max_power']:
            power_meter['value'] = power_meter['max_power']


def try_steal_ball_human():
    global ball_owner

    #only steal if AI owns ball
    if ball_owner is None:
        return
    owner_type, owner_idx = ball_owner
    if owner_type != "ai":
        return

    ai = ai_plyrs[owner_idx]

    dx = ai["pos"][0] - player["pos"][0]
    dz = ai["pos"][2] - player["pos"][2]
    dist = math.sqrt(dx*dx + dz*dz)

    #ball steal dist
    if dist < 2.25:
        #check if facing ball
        if not is_ball_in_front(player["pos"], player["rot"], ai["pos"], min_dot=0.0):
            return
        # STEAL
        knockback_loser(ai["pos"], player["pos"], dist=KNOCKBACK_DIST)
        block_entity_pickup(owner_idx)     #stop same AI from instant pickup
        ball_owner = ("human", None)
        game.player_has_ball = True
        game.ball_vel = [0, 0, 0]    #velocity
        game.ball_pos = hand_attach_position(player["pos"], player["rot"])

#only use when human has ball by pri 
def push_ai_forward_backward(direction):    #direction=1(forward),-1(backward)
    global lst_push_time

    # must be holding the ball
    if ball_owner != ("human", None):
        return

    # cooldown    
    now = time.time()
    if (now - lst_push_time) < push_cooldwn:
        return

    px, pz = player["pos"][0], player["pos"][2]
    fx, fz = forward_vector_y(player["rot"])  # my face direction 

    best_i = None
    best_d = 1e9

    i = 0
    while i < len(ai_plyrs):
        ai = ai_plyrs[i]

        ax, az = ai["pos"][0], ai["pos"][2]
        dx = ax - px
        dz = az - pz
        d = math.sqrt(dx*dx + dz*dz)

        if d > push_rnge:
            i += 1
            continue

        #direction check using dot
        if d < 1e-6:
            i += 1
            continue

        nx, nz = dx / d, dz / d  #direction of ai player
        dot = nx * fx + nz * fz

        # forward push needs dot >= threshold, backward push needs dot <= -threshold
        if direction == 1:
            if dot < 0.2:
                i += 1
                continue
        else:  # direction == -1
            if dot > -0.2:
                i += 1
                continue

        if d < best_d:
            best_d = d
            best_i = i

        i += 1

    if best_i is None:
        return

    # push the target AI away from player
    knockback_loser(ai_plyrs[best_i]["pos"], player["pos"], dist=push_dist)

    # avoid instant re-collision feel
    lst_push_time = now


def update_superpower():# ARU: Handle power time & collision
    global superpower
    
    if not superpower['active']:
        return  
    current_time = time.time()
    
    #3sec
    if current_time - superpower['spawn_time'] > superpower['lifetime']:
        superpower['active'] = False
        return
    
    #Rotate
    superpower['rotation'] += 3
    
    #Check collision
    dx = player['pos'][0] - superpower['pos'][0]
    dz = player['pos'][2] - superpower['pos'][2]
    dist = math.sqrt(dx*dx + dz*dz)
    
    if dist < 0.8:
        #Active effect
        superpower['effect_active'] = True
        superpower['effect_time'] = current_time
        superpower['active'] = False 

def update_superpower_effects():
    pass

def update_ai_plyrs():
    global ball_owner
    if not game.is_plyrs or game.gm_ovr:
        return

    #ARU:AI speed by difficulty
    ai_speed = 0.1 if game.difficulty == "hard" else 0.01   
    #ARU:Apply freeze on Ai
    if superpower['effect_active'] and superpower['type'] == 'freeze':
        return 

    field_halved = whole_field / 2 - 2
    goals = [
        {"side":"nrth", "pos": (0, -gl_line), "team":"blue"},
        {"side":"est",  "pos": (gl_line, 0),  "team":"red"},
        {"side":"suth", "pos": (0, gl_line),  "team":"yellow"},
        {"side":"wst",  "pos": (-gl_line, 0), "team":"green"},
    ]  

    i = 0
    while i < len(ai_plyrs):
        ai = ai_plyrs[i]
        ai_team = ai["team"].lower().strip()

        # If AI has ball, go for goal
        if ball_owner == ("ai", i):
            # choose nearest goal
            best = None
            best_d = 1e9
            for g in goals:
                if g["team"].lower().strip() == ai_team:
                    continue   # skip own goal

                gx, gz = g["pos"]
                dx = gx - ai["pos"][0]
                dz = gz - ai["pos"][2]
                d = dx*dx + dz*dz

                if d < best_d:
                    best_d = d
                    best = (gx, gz)

            tx, tz = best
            vx = tx - ai["pos"][0]
            vz = tz - ai["pos"][2]
            dist = math.sqrt(vx*vx + vz*vz)

            if dist > 0.05:
                vx /= dist     #unit length
                vz /= dist
                ai["pos"][0] += vx * ai_speed  #move x dir
                ai["pos"][2] += vz * ai_speed  #move z dir
                #atan2=0-> faces forward. #90=right, #-90=left #180=back
                ai["rot"] = math.degrees(math.atan2(vx, vz))    #rotate   #atan2 is for skipping vz=0

            # If close to post, just shoot
            if dist < 3.0:
                shoot_ball_ai(i, power=1.25)

            i += 1
            continue  

          #otherwise just follow ball
        if ball_owner == ("human", None):
            tx, tz = player["pos"][0], player["pos"][2]
        else:
            tx, tz = game.ball_pos[0], game.ball_pos[2]

        vx = tx - ai["pos"][0]
        vz = tz - ai["pos"][2]
        dist = math.sqrt(vx*vx + vz*vz)

        if dist > 0.05:
            vx /= dist    #unit length
            vz /= dist
            ai["pos"][0] += vx * ai_speed   #move x dir
            ai["pos"][2] += vz * ai_speed    #move z dir
            ai["rot"] = math.degrees(math.atan2(vx, vz))    #rotate

          #keep inside field
        ai["pos"][0] = max(-field_halved, min(field_halved, ai["pos"][0]))
        ai["pos"][2] = max(-field_halved, min(field_halved, ai["pos"][2]))
        separate_ai(i, min_sep=1.1, push=0.04)    #keep dist from other

        i += 1

def separate_ai(i, min_sep=1.0, push=0.03):
    ax, az = ai_plyrs[i]["pos"][0], ai_plyrs[i]["pos"][2]

    j = 0
    while j < len(ai_plyrs):
        if j == i:
            j += 1
            continue

        other = ai_plyrs[j]
        bx = other["pos"][0]
        bz = other["pos"][2]
        dx = ax - bx
        dz = az - bz
        d = math.sqrt(dx*dx + dz*dz)

        if d < 1e-6:
            #random small nudge
            dx = random.uniform(-1, 1)
            dz = random.uniform(-1, 1)
            d = math.sqrt(dx*dx + dz*dz)

        if d < min_sep:
            # push away
            dx /= d
            dz /= d
            ai_plyrs[i]["pos"][0] += dx * push
            ai_plyrs[i]["pos"][2] += dz * push

        j += 1

def separate_player_from_ai(min_sep=1.0, push=0.06):
    px, pz = player["pos"][0], player["pos"][2]
    for ai in ai_plyrs:
        ax, az = ai["pos"][0], ai["pos"][2]
        dx = px - ax
        dz = pz - az
        d = math.sqrt(dx*dx + dz*dz)

        if d < 1e-6:
            dx = random.uniform(-1, 1)
            dz = random.uniform(-1, 1)
            d = math.sqrt(dx*dx + dz*dz)

        if d < min_sep:
            dx /= d
            dz /= d

            player["pos"][0] += dx * push
            player["pos"][2] += dz * push
            ai["pos"][0] -= dx * push
            ai["pos"][2] -= dz * push


def shoot_ball_ai(i, power=1.2):
    global ball_owner,last_shooter_team
    ai = ai_plyrs[i]

    last_shooter_team = ai["team"].lower().strip()
    ball_owner = None  #release ownership

    angle_x = math.sin(math.radians(ai['rot']))
    angle_z = math.cos(math.radians(ai['rot']))

    game.ball_vel[0] = angle_x * power
    game.ball_vel[1] = 0.25 + (power * 0.08)
    game.ball_vel[2] = angle_z * power

def try_steal_ball_ai(i):
    global ball_owner

    if ball_owner is None:
        return

    owner_type, owner_idx = ball_owner

    #check if it is him
    if owner_type == "ai" and owner_idx == i:
        return

    ai = ai_plyrs[i]

    if owner_type == "human":
        target_pos = player["pos"]
        target_key = "human"
    else:
        target_pos = ai_plyrs[owner_idx]["pos"]
        target_key = owner_idx

    dx = target_pos[0] - ai["pos"][0]
    dz = target_pos[2] - ai["pos"][2]
    dist = math.sqrt(dx*dx + dz*dz)

    #steal dist
    if dist < 1.25:
        #if AI is in front of ball,then steal
        if not is_ball_in_front(ai["pos"], ai["rot"], target_pos, min_dot=0.0):
            return

        #Knockback & steal
        knockback_loser(target_pos, ai["pos"], dist=KNOCKBACK_DIST)
        block_entity_pickup(target_key)
        ball_owner = ("ai", i)
        game.player_has_ball = False
        game.ball_vel = [0, 0, 0]
        game.ball_pos = hand_attach_position(ai["pos"], ai["rot"])
        


#Forward direction in xz plane
def forward_vector_y(rot_deg):   
    ang = math.radians(rot_deg)
    fx = math.sin(ang)
    fz = math.cos(ang)
    return fx, fz

#check if ball is front
def is_ball_in_front(entity_pos, entity_rot,ball_pos, min_dot=0.35):    #min_dot=cos(70)=0.34
    vx = ball_pos[0] - entity_pos[0]
    vz = ball_pos[2] - entity_pos[2]
    dist = math.sqrt(vx*vx + vz*vz)
    if dist < 1e-6:
        return True

    vx=vx/dist
    vz=vz/ dist

    fx, fz = forward_vector_y(entity_rot)
    dot = vx*fx + vz*fz
    return dot >= min_dot

#Hand position
def hand_attach_position(entity_pos, entity_rot):
    fx, fz = forward_vector_y(entity_rot)

    x = entity_pos[0] + fx * 0.45
    y = 1.0
    z = entity_pos[2] + fz * 0.45
    return [x, y, z]

def try_pickup_ball_human():
    global ball_owner    
    if ball_owner is not None:
        return
    
    if not can_entity_pickup("human"):
        return

    # close+low enough+in front
    dx = game.ball_pos[0] - player["pos"][0]
    dz = game.ball_pos[2] - player["pos"][2]
    dist = math.sqrt(dx*dx + dz*dz)

    if dist < 0.9 and game.ball_pos[1] < 0.8 and is_ball_in_front(player["pos"], player["rot"], game.ball_pos):
        ball_owner = ("human", None)
        game.player_has_ball = True
        game.ball_vel = [0, 0, 0]
        game.ball_pos = hand_attach_position(player["pos"], player["rot"])

def try_pickup_ball_ai(i):
    global ball_owner
    if ball_owner is not None:
        return
    if not can_entity_pickup(i):
        return

    ai = ai_plyrs[i]
    dx = game.ball_pos[0] - ai["pos"][0]
    dz = game.ball_pos[2] - ai["pos"][2]
    dist = math.sqrt(dx*dx + dz*dz)

    if dist < 1.35 and game.ball_pos[1] < 0.95 and is_ball_in_front(ai["pos"], ai["rot"], game.ball_pos):
        ball_owner = ("ai", i)
        game.ball_vel = [0, 0, 0]
        game.ball_pos = hand_attach_position(ai["pos"], ai["rot"])

#entity_key:human or ai index(0/1/2)
def can_entity_pickup(entity_key):
    return (time.time() - last_pickup_block[entity_key]) >= pick_cooldwn

def block_entity_pickup(entity_key):
    last_pickup_block[entity_key] = time.time()

def knockback_loser(loser_pos, winner_pos, dist=1.0):
    dx = loser_pos[0] - winner_pos[0]
    dz = loser_pos[2] - winner_pos[2]
    d = math.sqrt(dx*dx + dz*dz)
    if d < 1e-6:
        dx = random.uniform(-1, 1)
        dz = random.uniform(-1, 1)
        d = math.sqrt(dx*dx + dz*dz)

    dx /= d
    dz /= d
    loser_pos[0] += dx * dist
    loser_pos[2] += dz * dist

        
def reset_round_positions(): #after goal it will reset positions
    global ball_owner

    half = whole_field / 2 - 2.5

    #ball to middle
    ball_owner = None
    game.ball_pos = [0, 0.5, 0]
    game.ball_vel = [0, 0, 0]
    game.player_has_ball = False
    
    #ARU:Reset superpower 
    superpower['effect_active'] = False
    spawn_superpower()

    #player spawn location
    if player["team"] == "blue":
        player["pos"] = [0, 0, -half]
        player["rot"] = 0          #face toward center
    else:  # yellow
        player["pos"] = [0, 0, half]
        player["rot"] = 180        #face toward center

    # AI spawns
    for ai in ai_plyrs:
        if ai["team"] == "red":
            ai["pos"] = [half, 0, 0]
            ai["rot"] = 270
        elif ai["team"] == "green":
            ai["pos"] = [-half, 0, 0]
            ai["rot"] = 90
        else:  # yellow AI 
            if player["team"] == "yellow":
                ai["pos"] = [0, 0, -half]
                ai["rot"] = 0
            else:
                ai["pos"] = [0, 0, half]
                ai["rot"] = 180

    #Reset power meter
    power_meter['value'] = 0.0
    power_meter['charging'] = False


def reset_ball():
    global last_shooter_team
    last_shooter_team = None
    reset_round_positions()

def restart_game():
    global game, player, current_state, nam_inpt, power_meter, difficulty_selection, gm_ovr_selection 
    game = Game()
    player = {
        'pos': [0, 0, 0],
        'rot': 0,
        'speed': 0.03,
        'team': 'yellow',
        'jrsy_num': 10
    }
    nam_inpt = ""
    difficulty_selection = 0  # ARU
    gm_ovr_selection = 0 
    power_meter = {
        'value': 0.0,
        'max_power': 2.0,
        'charging': False,
        'charge_rate': 3.0,
        'show_meter': False,
        'last_shot_power': 0.0,
        'last_shot_time': 0,
        'show_last_power': False
    }
    current_state = MENU

#ARU: restart game  same settings
def restart_game_keep_settings():
    global game, player, current_state, last_shooter_team, ball_owner, power_meter, gm_ovr_selection

    saved_jersey = game.selected_jersey
    saved_nam = game.player_nam
    saved_difficulty = game.difficulty
    saved_team = player['team']
    
    game = Game()
    game.selected_jersey = saved_jersey
    game.player_nam = saved_nam
    game.difficulty = saved_difficulty
    
    player['pos'] = [0, 0, 0]
    player['rot'] = 0
    player['team'] = saved_team
    
    last_shooter_team = None
    ball_owner = None
    gm_ovr_selection = 0  
    
    power_meter = {
        'value': 0.0,
        'max_power': 2.0,
        'charging': False,
        'charge_rate': 3.0,
        'show_meter': False,
        'last_shot_power': 0.0,
        'last_shot_time': 0,
        'show_last_power': False
    }
    
    reset_round_positions()
    spawn_superpower()

    current_state = plyrs
    game.is_plyrs = True

def process_player_movement():
    if not game.is_plyrs or game.gm_ovr:
        return
    
    # Simple arrow key movement (up/down/left/right relative to field)
    if key_states.get(GLUT_KEY_UP):
        player['pos'][2] -= player['speed']
        player['rot'] = 180
    if key_states.get(GLUT_KEY_DOWN):
        player['pos'][2] += player['speed']
        player['rot'] = 0
    if key_states.get(GLUT_KEY_LEFT):
        player['pos'][0] -= player['speed']
        player['rot'] = 270
    if key_states.get(GLUT_KEY_RIGHT):
        player['pos'][0] += player['speed']
        player['rot'] = 90
    
       # Diagonal 
    if key_states.get(GLUT_KEY_UP, False) and key_states.get(GLUT_KEY_LEFT, False):
        player['rot'] = 315
    if key_states.get(GLUT_KEY_UP, False) and key_states.get(GLUT_KEY_RIGHT, False):
        player['rot'] = 45
    if key_states.get(GLUT_KEY_DOWN, False) and key_states.get(GLUT_KEY_LEFT, False):
        player['rot'] = 225
    if key_states.get(GLUT_KEY_DOWN, False) and key_states.get(GLUT_KEY_RIGHT, False):
        player['rot'] = 135
    
       # Keep player in bounds
    field_halved = whole_field / 2 - 2
    player['pos'][0] = max(-field_halved, min(field_halved, player['pos'][0]))
    player['pos'][2] = max(-field_halved, min(field_halved, player['pos'][2]))

def shoot_ball(power):#shoot with given power
    
    global ball_owner,last_shooter_team
    last_shooter_team = player["team"].lower().strip()
    ball_owner = None
    angle_x = math.sin(math.radians(player['rot']))
    angle_z = math.cos(math.radians(player['rot']))
    
    # Apply power to velocity
    game.ball_vel[0] = angle_x * power
    game.ball_vel[1] = 0.3 + (power * 0.1)  # More lift with more power
    game.ball_vel[2] = angle_z * power
    
    game.player_has_ball = False
    power_meter['charging'] = False
    
    # Store last shot power for display
    power_meter['last_shot_power'] = power
    power_meter['last_shot_time'] = time.time()
    power_meter['show_last_power'] = True
    
    # Reset power meter
    power_meter['value'] = 0.0

def display():
    if current_state == MENU:
        art_menu()
    elif current_state == DIFFICULTY_SELECTION: 
        art_difficulty_selection()
    elif current_state == nam_inpt:
        art_nam_inpt()
    elif current_state == plyrs:
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, window_side/window_Tall, 0.1, 100.0)
        
       
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        set_cam()     
        
        art_stadium()
        art_stadium_lights()
        art_stand()
       
        art_square_field()
        art_simple_goal("nrth", (0.0, 0.545, 0.545))  # Blue goal
        art_goal_box("nrth")
        art_simple_goal("est", (1.0, 0.2, 0.2))   # Red goal
        art_goal_box("est")
        art_simple_goal("suth", (1.0, 1.0, 0.2))  # Yellow goal
        art_goal_box("suth")
        art_simple_goal("wst", (0.2, 1.0, 0.2))   # Green goal
        art_goal_box("wst")
        art_goalkeeper("nrth", (0.0, 0.545, 0.545))  # Cyan
        art_goalkeeper("est", (1.0, 0.2, 0.2))   # Red
        art_goalkeeper("suth", (1.0, 1.0, 0.2))  # Yellow
        art_goalkeeper("wst", (0.2, 1.0, 0.2))   # Green
        
        art_player()
        art_ball()
        art_superpower()
        art_hud()

        #AI plyrs
        for i, ai in enumerate(ai_plyrs):
            art_ai_player(ai, i)
    elif current_state == gm_ovr:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, window_side/window_Tall, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        set_cam()
        
        art_stadium()
        art_stadium_lights()
        art_stand()

        art_square_field()
        
        art_simple_goal("nrth", (0.0, 0.545, 0.545))  
        art_goal_box("nrth")
        art_simple_goal("est", (1.0, 0.2, 0.2))  
        art_goal_box("est")
        art_simple_goal("suth", (1.0, 1.0, 0.2))  
        art_goal_box("suth")
        art_simple_goal("wst", (0.2, 1.0, 0.2))   
        art_goal_box("wst")
        

        art_goalkeeper("nrth", (0.0, 0.545, 0.545))  # Blue
        art_goalkeeper("est", (1.0, 0.2, 0.2))   # Red
        art_goalkeeper("suth", (1.0, 1.0, 0.2))  # Yellow
        art_goalkeeper("wst", (0.2, 1.0, 0.2))   # Green
        

        art_player()
        art_ball()
        
        #art AI plyrs
        for i, ai in enumerate(ai_plyrs):
            art_ai_player(ai, i)
      
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_side, 0, window_Tall)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor4f(0.0, 0.0, 0.0, 0.85)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(window_side, 0)
        glVertex2f(window_side, window_Tall)
        glVertex2f(0, window_Tall)
        glEnd()
        
        #ARU: Display "MATCH FINISHED!"
        glColor3f(1.0, 0.85, 0.0)
        glRasterPos2f(window_side/2 - 120, window_Tall - 80)
        gm_ovr_text = "MATCH FINISHED!"
        for ch in gm_ovr_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))
        
        #ARU: Display winner
        if game.winner_team:
            winner_nam = game.winner_team.upper()
            glColor3f(0.0, 1.0, 0.0)
            glRasterPos2f(window_side/2 - 100, window_Tall - 130)
            winner_text = f"winNER: {winner_nam} TEAM!"
            for ch in winner_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        #ARU:art stats box
        stats_y = window_Tall/2 + 100
        glColor3f(0.15, 0.2, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(window_side/2 - 300, stats_y)
        glVertex2f(window_side/2 + 300, stats_y)
        glVertex2f(window_side/2 + 300, stats_y - 280)
        glVertex2f(window_side/2 - 300, stats_y - 280)
        glEnd()
        
        glColor3f(1.0, 1.0, 0.0)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(window_side/2 - 300, stats_y)
        glVertex2f(window_side/2 + 300, stats_y)
        glVertex2f(window_side/2 + 300, stats_y - 280)
        glVertex2f(window_side/2 - 300, stats_y - 280)
        glEnd()
        
        # ARU:Display "MATCH STATISTICS" header
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(window_side/2 - 80, stats_y - 30)
        header_text = "MATCH STATISTICS"
        for ch in header_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        #ARU: Display all 4 teams
        teams_data = [
            ("BLUE", game.team_scores["blue"], (0.0, 0.545, 0.545)),
            ("RED", game.team_scores["red"], (1.0, 0.2, 0.2)),
            ("YELLOW", game.team_scores["yellow"], (1.0, 1.0, 0.2)),
            ("GREEN", game.team_scores["green"], (0.2, 1.0, 0.2))
        ]
        
        start_y = stats_y - 70
        for i, (team_nam, score, color) in enumerate(teams_data):
            y_pos = start_y - (i * 50)
            

            glColor3f(*color)
            glBegin(GL_QUADS)
            glVertex2f(window_side/2 - 270, y_pos + 15)
            glVertex2f(window_side/2 - 240, y_pos + 15)
            glVertex2f(window_side/2 - 240, y_pos - 15)
            glVertex2f(window_side/2 - 270, y_pos - 15)
            glEnd()
            

            glColor3f(1.0, 1.0, 1.0)
            glRasterPos2f(window_side/2 - 220, y_pos - 5)
            for ch in team_nam:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
            
            # Score
            glRasterPos2f(window_side/2 + 50, y_pos - 5)
            score_text = f"Goals: {score}"
            for ch in score_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
            
            #ARU: Show <<<winNER
            if game.winner_team and team_nam.lower() == game.winner_team.lower():
                glColor3f(1.0, 0.85, 0.0)
                glRasterPos2f(window_side/2 + 180, y_pos - 5)
                crown_text = "<< WINNER"
                for ch in crown_text:
                    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        #ARU: Display difficulty level & duration
        glColor3f(0.7, 0.7, 0.7)
        glRasterPos2f(window_side/2 - 270, stats_y - 250)
        diff_text = f"Difficulty: {game.difficulty.upper()}"
        for ch in diff_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
        
        glRasterPos2f(window_side/2 + 80, stats_y - 250)
        time_text = f"Match Duration: {int(game.total_game_time // 60)}:{int(game.total_game_time % 60):02d}"
        for ch in time_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
        
        # Restart button
        button_y = 150
        restart_color = (0.0, 0.8, 0.0) if gm_ovr_selection == 0 else (0.3, 0.5, 0.3)
        glColor3f(*restart_color)
        glBegin(GL_QUADS)
        glVertex2f(window_side/2 - 180, button_y + 30)
        glVertex2f(window_side/2 - 20, button_y + 30)
        glVertex2f(window_side/2 - 20, button_y - 30)
        glVertex2f(window_side/2 - 180, button_y - 30)
        glEnd()
        
        # Restart button border
        glColor3f(1.0, 1.0, 1.0) if gm_ovr_selection == 0 else glColor3f(0.5, 0.5, 0.5)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(window_side/2 - 180, button_y + 30)
        glVertex2f(window_side/2 - 20, button_y + 30)
        glVertex2f(window_side/2 - 20, button_y - 30)
        glVertex2f(window_side/2 - 180, button_y - 30)
        glEnd()
        
        # Restart button text
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(window_side/2 - 145, button_y - 5)
        restart_text = "RESTART"
        for ch in restart_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        # Quit button
        quit_color = (0.8, 0.0, 0.0) if gm_ovr_selection == 1 else (0.5, 0.3, 0.3)
        glColor3f(*quit_color)
        glBegin(GL_QUADS)
        glVertex2f(window_side/2 + 20, button_y + 30)
        glVertex2f(window_side/2 + 180, button_y + 30)
        glVertex2f(window_side/2 + 180, button_y - 30)
        glVertex2f(window_side/2 + 20, button_y - 30)
        glEnd()
        
        # Quit button border
        glColor3f(1.0, 1.0, 1.0) if gm_ovr_selection == 1 else glColor3f(0.5, 0.5, 0.5)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(window_side/2 + 20, button_y + 30)
        glVertex2f(window_side/2 + 180, button_y + 30)
        glVertex2f(window_side/2 + 180, button_y - 30)
        glVertex2f(window_side/2 + 20, button_y - 30)
        glEnd()
        
        # Quit button text
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(window_side/2 + 75, button_y - 5)
        quit_text = "QUIT"
        for ch in quit_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        
        # Instructions
        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(window_side/2 - 150, 80)
        instructions = "Use LEFT/RIGHT arrows to select, ENTER to confirm"
        for ch in instructions:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

    
    glutSwapBuffers()

def reshape(width, height):  #for window
    global window_side, window_Tall
    window_side = width
    window_Tall = height
    glViewport(0, 0, width, height)

def keyboard(key, x, y):
    global cam_mode, current_state, game, nam_inpt,last_shooter_team
    if isinstance(key, bytes):
        key_char = key.decode('utf-8')
    else:
        return  # Not a regular key
    
    # Handle different states
    if current_state == MENU:
        if key_char == '\r': 
            if menu_selection == 0:  # Start Game
                current_state = JERSEY_SELECTION
            elif menu_selection == 1:  # Quit
                os._exit(0)
        elif key_char == '\x1b':  
            os._exit(0) 
    
    elif current_state == JERSEY_SELECTION:
        if key_char == '\r':  # ENTER key
            current_state = DIFFICULTY_SELECTION  # ARU:to difficulty selection
        
        elif key_char == '\x1b':  # ESC key - go back to menu
            current_state = MENU
    
    #ARU: Handle difficulty screen
    elif current_state == DIFFICULTY_SELECTION:
        if key_char == '\r':  
            if difficulty_selection == 0:
                game.difficulty = "easy"
            else:
                game.difficulty = "hard"
            current_state = nam_inpt
        
        elif key_char == '\x1b':  
            current_state = JERSEY_SELECTION
    
    elif current_state == nam_inpt:
        if key_char == '\r':  # ENTER key
            if nam_inpt.strip():
                game.player_nam = nam_inpt.strip()
            else:
                game.player_nam = "YOU"
            
            # Set selected jersey and start game

            game.selected_jersey = "brazil"
            player['team'] = 'yellow'

            
            current_state = plyrs
            game.is_plyrs = True
            last_shooter_team = None
            reset_round_positions()
            spawn_superpower() 

        
        elif key_char == '\x1b':  #ESC key  go back  difficulty selection
            current_state = DIFFICULTY_SELECTION  #ARU: navigate back to difficulty
        
        elif key_char == '\x08':  #BACKSPACE key
            if nam_inpt:
                nam_inpt = nam_inpt[:-1]
        
        elif len(key_char) == 1 and key_char.isprintable() and len(nam_inpt) < max_nam_LENGTH:
            nam_inpt += key_char
    
    elif current_state == plyrs or current_state == gm_ovr: 
        # ARU:game over screen actions FIRST (restart/quit)
        if current_state == gm_ovr:
            if key_char == '\r':  # ENTER key
                if gm_ovr_selection == 0:  # ARU:Restart w same settings
                    restart_game_keep_settings()
                else:  #ARU: Quit close game 
                    print("Quitting game...")
                    os._exit(0)   
            elif key_char == '\x1b':
                print("Quitting game (ESC)...") 
                os._exit(0)   
        
        # Game controls (only during plyrs)
        elif current_state == plyrs:
            if key_char == 'c':
                modes = ["PLAYER","OVERHEAD"]
                current_idx = modes.index(cam_mode)
                cam_mode = modes[(current_idx + 1) % len(modes)]
            
            # Pause game by pri
            elif key_char == 'p':
                game.is_plyrs = not game.is_plyrs
            
            # PUSH while holding ball (W forward, S backward)
            elif (key_char == 'w' or key_char == 'W') and ball_owner == ("human", None):
                push_ai_forward_backward(direction=1)

            elif (key_char == 's' or key_char == 'S') and ball_owner == ("human", None):
                push_ai_forward_backward(direction=-1)
            
            # Start charging shot when space is pressed
            elif key_char == ' ' and game.player_has_ball and game.is_plyrs and not game.gm_ovr:
                if not power_meter['charging']:
                    power_meter['charging'] = True
                    power_meter['value'] = 0.1  # Start with minimal power
            
            # Reset ball
            elif key_char == 'r':
                reset_ball()
            
            # Quit to menu
            elif key_char == '\x1b':  # ESC
                current_state = MENU
                
    
    glutPostRedisplay()

def keyboard_up(key, x, y):  # for key relase
    global power_meter, game
    
    if isinstance(key, bytes):
        key_char = key.decode('utf-8')
    else:
        return
    
    # Handle space key release for shooting
    if key_char == ' ' and current_state == plyrs and game.player_has_ball and game.is_plyrs and not game.gm_ovr:
        if power_meter['charging']:
            # current power
            shoot_ball(power_meter['value'])
            
            power_meter['charging'] = False
    
    glutPostRedisplay()

def special_keys(key, x, y):
    global menu_selection, jersey_selection, difficulty_selection, current_state 
    if current_state == MENU:
        
        if key == GLUT_KEY_UP:
            menu_selection = max(0, menu_selection - 1)
        elif key == GLUT_KEY_DOWN:
            menu_selection = min(1, menu_selection + 1)
    elif current_state == JERSEY_SELECTION:
        if key == GLUT_KEY_LEFT:
            jersey_selection = 0
        elif key == GLUT_KEY_RIGHT:
            jersey_selection = 1
    
    #ARU:choose difficulty  
    elif current_state == DIFFICULTY_SELECTION:
        if key == GLUT_KEY_LEFT:
            difficulty_selection = 0
        elif key == GLUT_KEY_RIGHT:
            difficulty_selection = 1
    
    elif current_state == plyrs or current_state == gm_ovr: #for player
        
        if key == GLUT_KEY_UP:
            key_states[GLUT_KEY_UP] = True
        elif key == GLUT_KEY_DOWN:
            key_states[GLUT_KEY_DOWN] = True
        elif key == GLUT_KEY_LEFT:
            if current_state == gm_ovr:  #ARU:navigate game over button
                global gm_ovr_selection
                gm_ovr_selection = 0
            else:
                key_states[GLUT_KEY_LEFT] = True
        elif key == GLUT_KEY_RIGHT:
            if current_state == gm_ovr: 
                gm_ovr_selection = 1
            else:
                key_states[GLUT_KEY_RIGHT] = True
    
    glutPostRedisplay()

def special_up(key, x, y):
   
    if current_state == plyrs or current_state == gm_ovr:
        if key == GLUT_KEY_UP:
            key_states[GLUT_KEY_UP] = False
        elif key == GLUT_KEY_DOWN:
            key_states[GLUT_KEY_DOWN] = False
        elif key == GLUT_KEY_LEFT:
            key_states[GLUT_KEY_LEFT] = False
        elif key == GLUT_KEY_RIGHT:
            key_states[GLUT_KEY_RIGHT] = False
    
    glutPostRedisplay()

def idle():
    global last_time
    current_time = time.time()
    delta = current_time - last_time

    if delta >= 0.016:
        update()
        last_time = current_time

    glutPostRedisplay()

def update(value): #updategame state
    if current_state == plyrs or current_state == gm_ovr:
        #ARU: Apply speed superpower
        if superpower['effect_active'] and superpower['type'] == 'speed':
            player['speed'] = player['sp_speed'] * 2.0
        else:
            player['speed'] = player['sp_speed']
        
        process_player_movement()
        update_superpower()  
        update_superpower_effects()  
        update_ai_plyrs()

        separate_player_from_ai(min_sep=1.1, push=0.06) 
        for i in range(len(ai_plyrs)):
            separate_ai(i, min_sep=1.1, push=0.04)

        ball_movement()

        try_pickup_ball_human()
        try_steal_ball_human()

        for i in range(len(ai_plyrs)):
            try_pickup_ball_ai(i)
            try_steal_ball_ai(i)

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_side, window_Tall)
    glutCreateWindow(b"Single Player Football - Score Goals!")
    
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)  
    glutSpecialFunc(special_keys)
    glutSpecialUpFunc(special_up)
    glutTimerFunc(16, update, 0)
    
    print("=" * 70)
    print("FOOTBALL CHALLENGE - SINGLE PLAYER")
    print("=" * 70)
    print("\nGAME FLOW:")
    print("1. Start at Main Menu")
    print("2. Select Jersey (Argentina Blue or Brazil Yellow)")
    print("3. Enter Your nam")
    print("4. Play the Game!")
    print("\nGAME FEATURES:")
    print("- Single player only (YOU vs 4 goalkeepers)")
    print("- 4-minute timed match")
    print("- 4 Goals with colored posts (Blue, Red, Yellow, Green)")
    print("- 4 Goalkeepers with collision detection")
    print("- Score by shooting past goalkeepers")
    print("- Jersey number on your BACK shows which way you're facing")
    print("- NEW: Stadium stands around the field (45° tilted)")
    print("- NEW: Power meter for shooting - HOLD SPACE to charge!")
    print("\nHOW TO PLAY:")
    print("- Move with Arrow Keys")
    print("- Look at the number on your BACK to know your direction")
    print("- Get close to ball to pick it up")
    print("- HOLD SPACE to charge power, RELEASE to shoot")
    print("- Ball must pass goal line WITHOUT hitting goalkeeper")
    print("\nCONTROLS:")
    print("- Arrow Keys: Move (number on back shows direction)")
    print("- SPACE: Hold to charge shot power, release to shoot")
    print("- C: Change cam view (Player, Overhead, Goal)")
    print("- P: Pause/Resume game")
    print("- R: Reset ball (during game) / Restart (after game)")
    print("- ESC: Quit to menu")
    print("\nPOWER METER:")
    print("- Bottom right of screen shows shot power")
    print("- Green (low power) -> Yellow (medium) -> Red (high)")
    print("- After shooting, yellow line shows exact power used")
    print("\nOBJECTIVE:")
    print("Score as many goals as possible in 4 minutes!")
    print("Shoot past any of the 4 goalkeepers to score.")
    
    glutMainLoop()

if __name__ == "__main__":

    main()