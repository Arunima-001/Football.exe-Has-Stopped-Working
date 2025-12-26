from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import sys
import time
import random
from collections import defaultdict

MENU = 0
JERSEY_SELECTION = 1
PLAYER_NAME_INPUT = 2
PLAYING = 3
GAME_OVER = 4

current_state = MENU


WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

key_states = defaultdict(bool)


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
        self.is_playing = True
        self.game_over = False
        self.ball_pos = [0, 0.3, 0]
        self.ball_vel = [0, 0, 0]
        self.player_has_ball = False
        self.last_goal_time = -5
        self.goal_message = ""
        self.goal_message_time = 0
        self.winner = None
        self.selected_jersey = "argentina"  
        self.player_name = "YOU"  

game = Game()


FIELD_SIZE = 20.0
GOAL_WIDTH = 3.0
GOAL_HEIGHT = 2.0
GOAL_DEPTH = 1.5
GOAL_LINE = FIELD_SIZE / 2  

STADIUM_SIZE = 35.0
STAND_HEIGHT = 5.0
STAND_DEPTH = 5.0
NUM_STAND_SEGMENTS = 20

player = {
    'pos': [0, 0, 0],
    'rot': 0,
    'speed': 0.15,
    'team': 'blue',
    'jersey_number': 10
}

goalies = {
    'north': {
        'pos': [0, 0, -GOAL_LINE],
        'dir': 1,
        'anim': 0,
        'team': 'blue',
        'collision_box': {'x': 0, 'z': -GOAL_LINE, 'width': GOAL_WIDTH, 'height': GOAL_HEIGHT, 'depth': 0.5}
    },
    'east': {
        'pos': [GOAL_LINE, 0, 0],
        'dir': 1,
        'anim': 30,
        'team': 'red',
        'collision_box': {'x': GOAL_LINE, 'z': 0, 'width': 0.5, 'height': GOAL_HEIGHT, 'depth': GOAL_WIDTH}
    },
    'south': {
        'pos': [0, 0, GOAL_LINE],
        'dir': 1,
        'anim': 60,
        'team': 'yellow',
        'collision_box': {'x': 0, 'z': GOAL_LINE, 'width': GOAL_WIDTH, 'height': GOAL_HEIGHT, 'depth': 0.5}
    },
    'west': {
        'pos': [-GOAL_LINE, 0, 0],
        'dir': 1,
        'anim': 90,
        'team': 'green',
        'collision_box': {'x': -GOAL_LINE, 'z': 0, 'width': 0.5, 'height': GOAL_HEIGHT, 'depth': GOAL_WIDTH}
    }
}

camera_mode = "PLAYER"  
camera_height = 3.0
camera_distance = 5.0


menu_selection = 0  
jersey_selection = 0  

player_name_input = ""
name_cursor_pos = 0
MAX_NAME_LENGTH = 15

ball_owner = None  


ai_players = [
    {"pos": [ 4,0,4],  "rot":180, "speed": 0.01, "name":"AI-1", "team":"red"},
    {"pos": [-4,0,4],  "rot":180, "speed": 0.01, "name":"AI-2", "team":"green"},
    {"pos": [ 0,0,-6], "rot":0,   "speed": 0.01, "name":"AI-3", "team":"yellow"},
]


PICKUP_COOLDOWN = 0.8  
KNOCKBACK_DIST  = 2
last_pickup_block = {"human": 0.0, 0: 0.0, 1: 0.0, 2: 0.0}


PUSH_COOLDOWN = 1.0
last_push_time = 0.0

PUSH_RANGE = 2.2
PUSH_DIST  = 2.4


BALL_PUSH_POWER = 1.35
BALL_PUSH_LIFT  = 0.12

BALL_HIT_RADIUS   = 0.75
BALL_PUSH_AI_DIST = 1.8

debug_push_msg = ""
debug_push_msg_time = 0.0


push_anim = {
    "active": False,
    "type": None,        
    "start_time": 0.0,
    "duration": 0.18      
}

def init():
    """Initialize OpenGL"""
    glClearColor(0.1, 0.2, 0.3, 1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 20.0, 0.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


def set_camera():
    """Set camera position based on mode"""
    if camera_mode == "OVERHEAD":
        glLoadIdentity()
        gluLookAt(0, 15, 0,
                  0, 0, 0,
                  0, 0, 1)
    elif camera_mode == "PLAYER":
       
        glLoadIdentity()
        gluLookAt(0, 5, FIELD_SIZE/2 + 5,
                  0, 2, 0,
                  0, 1, 0)

def draw_cuboid(x, y, z, width, height, depth):
    """Draw a 3D cuboid"""
    glPushMatrix()
    glTranslatef(x, y, z)

    half_w = width / 2
    half_h = height / 2
    half_d = depth / 2

    glBegin(GL_QUADS)

    
    glNormal3f(0, 0, 1)
    glVertex3f(-half_w, -half_h, half_d)
    glVertex3f( half_w, -half_h, half_d)
    glVertex3f( half_w,  half_h, half_d)
    glVertex3f(-half_w,  half_h, half_d)

    
    glNormal3f(0, 0, -1)
    glVertex3f(-half_w, -half_h, -half_d)
    glVertex3f(-half_w,  half_h, -half_d)
    glVertex3f( half_w,  half_h, -half_d)
    glVertex3f( half_w, -half_h, -half_d)

   
    glNormal3f(0, 1, 0)
    glVertex3f(-half_w, half_h, -half_d)
    glVertex3f(-half_w, half_h,  half_d)
    glVertex3f( half_w, half_h,  half_d)
    glVertex3f( half_w, half_h, -half_d)

   
    glNormal3f(0, -1, 0)
    glVertex3f(-half_w, -half_h, -half_d)
    glVertex3f( half_w, -half_h, -half_d)
    glVertex3f( half_w, -half_h,  half_d)
    glVertex3f(-half_w, -half_h,  half_d)

    
    glNormal3f(1, 0, 0)
    glVertex3f(half_w, -half_h, -half_d)
    glVertex3f(half_w,  half_h, -half_d)
    glVertex3f(half_w,  half_h,  half_d)
    glVertex3f(half_w, -half_h,  half_d)

    
    glNormal3f(-1, 0, 0)
    glVertex3f(-half_w, -half_h, -half_d)
    glVertex3f(-half_w, -half_h,  half_d)
    glVertex3f(-half_w,  half_h,  half_d)
    glVertex3f(-half_w,  half_h, -half_d)

    glEnd()
    glPopMatrix()


def draw_head():
    
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, -0.03)
    glScalef(0.15, 0.2, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.9, 0.8, 0.7)
    glPushMatrix()
    glTranslatef(0, 0, 0.03)
    glScalef(0.15, 0.2, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_square_field():
   
    half_size = FIELD_SIZE / 2

    glColor3f(0.2, 0.6, 0.2)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-half_size, 0, -half_size)
    glVertex3f( half_size, 0, -half_size)
    glVertex3f( half_size, 0,  half_size)
    glVertex3f(-half_size, 0,  half_size)
    glEnd()

    stripe_width = 1.0
    for i in range(int(FIELD_SIZE / stripe_width)):
        x_start = -half_size + i * stripe_width

        if i % 2 == 0:
            glColor3f(0.15, 0.55, 0.15)
        else:
            glColor3f(0.25, 0.65, 0.25)

        glBegin(GL_QUADS)
        glVertex3f(x_start, 0.01, -half_size)
        glVertex3f(x_start + stripe_width, 0.01, -half_size)
        glVertex3f(x_start + stripe_width, 0.01, half_size)
        glVertex3f(x_start, 0.01, half_size)
        glEnd()

    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(3.0)

    glBegin(GL_LINE_LOOP)
    glVertex3f(-half_size, 0.02, -half_size)
    glVertex3f( half_size, 0.02, -half_size)
    glVertex3f( half_size, 0.02,  half_size)
    glVertex3f(-half_size, 0.02,  half_size)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-half_size, 0.02, 0)
    glVertex3f( half_size, 0.02, 0)
    glVertex3f(0, 0.02, -half_size)
    glVertex3f(0, 0.02,  half_size)
    glEnd()

    glBegin(GL_LINE_LOOP)
    for i in range(32):
        angle = 2.0 * math.pi * i / 32
        x = 2.0 * math.cos(angle)
        z = 2.0 * math.sin(angle)
        glVertex3f(x, 0.02, z)
    glEnd()

    glPointSize(8.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0.03, 0)
    glEnd()


    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(4.0)

    glBegin(GL_LINES)
    glVertex3f(-GOAL_WIDTH/2, 0.03, -GOAL_LINE)
    glVertex3f( GOAL_WIDTH/2, 0.03, -GOAL_LINE)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(GOAL_LINE, 0.03, -GOAL_WIDTH/2)
    glVertex3f(GOAL_LINE, 0.03,  GOAL_WIDTH/2)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-GOAL_WIDTH/2, 0.03, GOAL_LINE)
    glVertex3f( GOAL_WIDTH/2, 0.03, GOAL_LINE)
    glEnd()

    glBegin(GL_LINES)
    glVertex3f(-GOAL_LINE, 0.03, -GOAL_WIDTH/2)
    glVertex3f(-GOAL_LINE, 0.03,  GOAL_WIDTH/2)
    glEnd()

    glEnable(GL_LIGHTING)


def draw_simple_goal(side, color):

    half_size = FIELD_SIZE / 2

    if side == "north":
        x, z = 0, -half_size
        rotation = 0
    elif side == "east":
        x, z = half_size, 0
        rotation = 270
    elif side == "south":
        x, z = 0, half_size
        rotation = 180
    else:
        x, z = -half_size, 0
        rotation = 90

    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)

    glColor3f(color[0], color[1], color[2])

    draw_cuboid(-GOAL_WIDTH/2, GOAL_HEIGHT/2, 0, 0.1, GOAL_HEIGHT, 0.1)
    draw_cuboid(GOAL_WIDTH/2 - 0.1, GOAL_HEIGHT/2, 0, 0.1, GOAL_HEIGHT, 0.1)
    draw_cuboid(-0.055, GOAL_HEIGHT, 0, GOAL_WIDTH, 0.1, 0.1)

    glPopMatrix()


def draw_goal_box(side):

    half_size = FIELD_SIZE / 2
    box_size = 4.0

    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)

    if side == "north":
        glBegin(GL_LINE_LOOP)
        glVertex3f(-box_size/2, 0.02, -half_size)
        glVertex3f( box_size/2, 0.02, -half_size)
        glVertex3f( box_size/2, 0.02, -half_size + 2.0)
        glVertex3f(-box_size/2, 0.02, -half_size + 2.0)
        glEnd()
    elif side == "east":
        glBegin(GL_LINE_LOOP)
        glVertex3f(half_size - 2.0, 0.02, -box_size/2)
        glVertex3f(half_size,       0.02, -box_size/2)
        glVertex3f(half_size,       0.02,  box_size/2)
        glVertex3f(half_size - 2.0, 0.02,  box_size/2)
        glEnd()
    elif side == "south":
        glBegin(GL_LINE_LOOP)
        glVertex3f(-box_size/2, 0.02, half_size - 2.0)
        glVertex3f( box_size/2, 0.02, half_size - 2.0)
        glVertex3f( box_size/2, 0.02, half_size)
        glVertex3f(-box_size/2, 0.02, half_size)
        glEnd()
    else:
        glBegin(GL_LINE_LOOP)
        glVertex3f(-half_size,      0.02, -box_size/2)
        glVertex3f(-half_size + 2.0,0.02, -box_size/2)
        glVertex3f(-half_size + 2.0,0.02,  box_size/2)
        glVertex3f(-half_size,      0.02,  box_size/2)
        glEnd()

    glEnable(GL_LIGHTING)


def draw_stadium_stands():
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glColor3f(0.25, 0.25, 0.25)

    half = FIELD_SIZE/2 + 2.5
    for k in range(4):
        glPushMatrix()
        if k == 0:
            glTranslatef(0, 0.0, -half-2.0)
            w, d = STADIUM_SIZE, 2.0
        elif k == 1:
            glTranslatef(half+2.0, 0.0, 0)
            w, d = 2.0, STADIUM_SIZE
        elif k == 2:
            glTranslatef(0, 0.0, half+2.0)
            w, d = STADIUM_SIZE, 2.0
        else:
            glTranslatef(-half-2.0, 0.0, 0)
            w, d = 2.0, STADIUM_SIZE

        steps = 6
        for s in range(steps):
            glPushMatrix()
            glTranslatef(0, s*0.45, 0)
            glScalef(w, 0.4, d + s*0.8)
            glutSolidCube(1.0)
            glPopMatrix()

        glPopMatrix()

    glEnable(GL_LIGHTING)
    glPopMatrix()

def draw_goalkeeper(side, color):
    """Draw a goalkeeper with left-right animation"""
    goalie = goalies[side]

    goalie['anim'] += goalie['dir'] * 0.5
    if goalie['anim'] >= 60:
        goalie['anim'] = 60
        goalie['dir'] = -1
    elif goalie['anim'] <= -60:
        goalie['anim'] = -60
        goalie['dir'] = 1

    if side == "north":
        x = goalie['pos'][0] + math.sin(goalie['anim'] * 0.05) * 2.0
        z = goalie['pos'][2]
        rotation = 0
    elif side == "east":
        x = goalie['pos'][0]
        z = goalie['pos'][2] + math.sin(goalie['anim'] * 0.05) * 2.0
        rotation = 270
    elif side == "south":
        x = goalie['pos'][0] + math.sin(goalie['anim'] * 0.05) * 2.0
        z = goalie['pos'][2]
        rotation = 180
    else:
        x = goalie['pos'][0]
        z = goalie['pos'][2] + math.sin(goalie['anim'] * 0.05) * 2.0
        rotation = 90

    if side == "north" or side == "south":
        goalie['collision_box']['x'] = x
    else:
        goalie['collision_box']['z'] = z

    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)

    glColor3f(color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)

    glPushMatrix()
    glTranslatef(0, 0.9, 0)
    glScalef(0.3, 0.6, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 1.3, 0)
    draw_head()
    glPopMatrix()

    glColor3f(0.667, 0.455, 0.290)

    glPushMatrix()
    glTranslatef(0.4, 1.0, 0)
    glRotatef(45, 0, 0, 1)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.4, 1.0, 0)
    glRotatef(-45, 0, 0, 1)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.9, 0.8, 0.7)

    glPushMatrix()
    glTranslatef(0.1, 0.3, 0)
    glScalef(0.1, 0.5, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.1, 0.3, 0)
    glScalef(0.1, 0.5, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos3f(-0.02, 1.1, -0.15)
    for ch in "1":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    glEnable(GL_LIGHTING)

    glPopMatrix()


def start_push_anim(anim_type):
    push_anim["active"] = True
    push_anim["type"] = anim_type
    push_anim["start_time"] = time.time()

def push_anim_amount():

    if not push_anim["active"]:
        return 0.0
    t = time.time() - push_anim["start_time"]
    if t >= push_anim["duration"]:
        push_anim["active"] = False
        return 0.0
    x = t / push_anim["duration"]
    return math.sin(math.pi * x)


def draw_player():
    global ball_owner
    glPushMatrix()
    glTranslatef(player['pos'][0], 0, player['pos'][2])
    glRotatef(player['rot'], 0, 1, 0)

    anim_amt = push_anim_amount()
    anim_type = push_anim["type"]

    if game.selected_jersey == "argentina":
        body_color = (0.2, 0.6, 1.0)
    else:
        body_color = (1.0, 0.8, 0.0)

    glColor3f(*body_color)
    glPushMatrix()
    glTranslatef(0, 0.8, 0)
    glScalef(0.25, 0.5, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 1.1, 0)
    draw_head()
    glPopMatrix()

    glColor3f(0.776, 0.525, 0.259)

    glPushMatrix()
    glTranslatef(0.2, 0.9, 0)

    if ball_owner == ("human", None):
        glRotatef(90, 1, 0, 0)

    if anim_amt > 0 and (anim_type in ("L", "F")):
        glRotatef(-65 * anim_amt, 1, 0, 0)

    glScalef(0.07, 0.3, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()


    glPushMatrix()
    glTranslatef(-0.2, 0.9, 0)

    if ball_owner == ("human", None):
        glRotatef(90, 1, 0, 0)

    if anim_amt > 0 and (anim_type in ("J", "F")):
        glRotatef(-65 * anim_amt, 1, 0, 0)

    glScalef(0.07, 0.3, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.776, 0.525, 0.259)

    glPushMatrix()
    glTranslatef(0.08, 0.25, 0)
    if anim_amt > 0 and (anim_type in ("I", "F")):
        glRotatef(-70 * anim_amt, 1, 0, 0)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.08, 0.25, 0)
    if anim_amt > 0 and (anim_type in ("K", "F")):
        glRotatef(-70 * anim_amt, 1, 0, 0)
    glScalef(0.08, 0.4, 0.08)
    glutSolidCube(1.0)
    glPopMatrix()

    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos3f(-0.03, 1.1, -0.12)
    for ch in str(player['jersey_number']):
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

    glColor3f(1.0, 1.0, 0.0)
    glRasterPos3f(-0.05 * len(game.player_name), 1.5, 0.1)
    for ch in game.player_name:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))
    glEnable(GL_LIGHTING)

    glPopMatrix()


def draw_ai_player(ai, idx):
    global ball_owner
    glPushMatrix()
    glTranslatef(ai["pos"][0], 0, ai["pos"][2])
    glRotatef(ai["rot"], 0, 1, 0)

    if ai["team"] == "red":
        body_color = (1.0, 0.2, 0.2)
    elif ai["team"] == "green":
        body_color = (0.2, 1.0, 0.2)
    else:
        body_color = (1.0, 1.0, 0.2)

    glColor3f(*body_color)
    glPushMatrix()
    glTranslatef(0, 0.8, 0)
    glScalef(0.25, 0.5, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 1.1, 0)
    draw_head()
    glPopMatrix()

    glColor3f(0.776, 0.525, 0.259)

    glPushMatrix()
    glTranslatef(0.2, 0.9, 0)
    if ball_owner == ("ai", idx):
        glRotatef(90, 1, 0, 0)
    glScalef(0.07, 0.3, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.2, 0.9, 0)
    if ball_owner == ("ai", idx):
        glRotatef(90, 1, 0, 0)
    glScalef(0.07, 0.3, 0.07)
    glutSolidCube(1.0)
    glPopMatrix()

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

    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos3f(-0.05 * len(ai["name"]), 1.5, 0.1)
    for ch in ai["name"]:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))
    glEnable(GL_LIGHTING)

    glPopMatrix()


def draw_ball():
    glPushMatrix()
    glTranslatef(game.ball_pos[0], game.ball_pos[1], game.ball_pos[2])

    vel_mag = math.sqrt(game.ball_vel[0]**2 + game.ball_vel[1]**2 + game.ball_vel[2]**2)
    rotation = game.game_time * vel_mag * 30
    glRotatef(rotation, 1, 0, 0)

    glColor3f(1.0, 1.0, 1.0)
    glutSolidSphere(0.2, 16, 16)

    glColor3f(0.0, 0.0, 0.0)
    for i in range(6):
        angle = 2.0 * math.pi * i / 6
        patch_x = 0.15 * math.cos(angle)
        patch_z = 0.15 * math.sin(angle)
        glPushMatrix()
        glTranslatef(patch_x, 0, patch_z)
        glutSolidSphere(0.08, 8, 8)
        glPopMatrix()

    glPopMatrix()

def draw_power_meter():

    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    meter_width = 200
    meter_height = 25
    meter_x = WINDOW_WIDTH - meter_width - 20
    meter_y = 40

    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(meter_x, meter_y)
    glVertex2f(meter_x + meter_width, meter_y)
    glVertex2f(meter_x + meter_width, meter_y + meter_height)
    glVertex2f(meter_x, meter_y + meter_height)
    glEnd()

    power_percentage = power_meter['value'] / power_meter['max_power']
    fill_width = meter_width * power_percentage

    if power_percentage < 0.5:
        r = 2.0 * power_percentage
        g = 1.0
        b = 0.0
    else:
        r = 1.0
        g = 2.0 * (1.0 - power_percentage)
        b = 0.0

    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(meter_x, meter_y)
    glVertex2f(meter_x + fill_width, meter_y)
    glVertex2f(meter_x + fill_width, meter_y + meter_height)
    glVertex2f(meter_x, meter_y + meter_height)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(meter_x, meter_y)
    glVertex2f(meter_x + meter_width, meter_y)
    glVertex2f(meter_x + meter_width, meter_y + meter_height)
    glVertex2f(meter_x, meter_y + meter_height)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(meter_x, meter_y + meter_height + 5)
    label = "SHOT POWER:"
    for ch in label:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

    power_text = f"{power_percentage*100:.0f}%"
    glColor3f(1.0, 1.0, 0.0)
    text_width = len(power_text) * 8
    glRasterPos2f(meter_x + meter_width/2 - text_width/2, meter_y + meter_height/2 - 4)
    for ch in power_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

    if power_meter['show_last_power'] and time.time() - power_meter['last_shot_time'] < 2.0:
        last_power_y = meter_y + meter_height + 25
        last_power_x = meter_x + (power_meter['last_shot_power'] / power_meter['max_power']) * meter_width
        glColor3f(1.0, 1.0, 0.0)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex2f(last_power_x, meter_y + meter_height)
        glVertex2f(last_power_x, last_power_y)
        glEnd()

        glRasterPos2f(last_power_x - 20, last_power_y + 5)
        last_power_text = f"{power_meter['last_shot_power']:.1f}"
        for ch in last_power_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

    if power_meter['charging']:
        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(meter_x, meter_y - 20)
        charge_text = "HOLD SPACE to charge power, RELEASE to shoot"
        for ch in charge_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)


def draw_hud():
    """Draw heads-up display during game"""
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    time_left = max(0, game.total_game_time - game.game_time)
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)

    glColor3f(1.0, 1.0, 0.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 50, WINDOW_HEIGHT - 40)
    time_text = f"TIME: {minutes:02d}:{seconds:02d}"
    for ch in time_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(0.2, 0.6, 1.0)
    glRasterPos2f(50, WINDOW_HEIGHT - 40)
    score_text = f"SCORE: {game.score}"
    for ch in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(0.8, 0.8, 0.8)
    glRasterPos2f(20, 60)
    controls = "Arrow Keys: Move | SPACE: Charge+Shoot | F: Push | I/K/J/L: Direction Push | C: Camera | P: Pause | R: Reset Ball"
    for ch in controls:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

    if game.selected_jersey == "argentina":
        team_color = (0.2, 0.6, 1.0)
        team_name = "Argentina (Blue)"
    else:
        team_color = (1.0, 0.8, 0.0)
        team_name = "Brazil (Yellow)"

    glColor3f(*team_color)
    glRasterPos2f(20, 40)
    player_text = f"Player: {game.player_name} - Team: {team_name} - #{player['jersey_number']}"
    for ch in player_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

    glRasterPos2f(20, 20)
    camera_text = f"CAMERA: {camera_mode} (C to change)"
    for ch in camera_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

    if game.player_has_ball:
        glColor3f(0.0, 1.0, 0.0)
        glRasterPos2f(WINDOW_WIDTH/2 - 50, 40)
        ball_text = "YOU HAVE THE BALL! (HOLD SPACE to charge shot)"
        for ch in ball_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    if game.game_time - game.goal_message_time < 2.0 and game.goal_message:
        glColor3f(0.0, 1.0, 0.0)
        glRasterPos2f(WINDOW_WIDTH/2 - 80, WINDOW_HEIGHT/2 + 50)
        for ch in game.goal_message:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    if not game.is_playing and not game.game_over:
        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(WINDOW_WIDTH/2 - 30, WINDOW_HEIGHT/2)
        pause_text = "GAME PAUSED"
        for ch in pause_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    if game.game_over:
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()

        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(WINDOW_WIDTH/2 - 80, WINDOW_HEIGHT/2 + 50)
        game_over_text = "GAME OVER!"
        for ch in game_over_text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

        glColor3f(0.2, 0.6, 1.0)
        glRasterPos2f(WINDOW_WIDTH/2 - 60, WINDOW_HEIGHT/2)
        score_text = f"FINAL SCORE: {game.score}"
        for ch in score_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

        performance = ""
        color = (1.0, 1.0, 1.0)

        if game.score >= 10:
            performance = "EXCELLENT! You're a football star!"
            color = (1.0, 1.0, 0.0)
        elif game.score >= 5:
            performance = "GOOD JOB! Keep practicing!"
            color = (0.0, 1.0, 0.0)
        elif game.score >= 2:
            performance = "NOT BAD! Try again!"
            color = (0.8, 0.8, 0.8)
        else:
            performance = "KEEP PRACTICING!"
            color = (0.5, 0.5, 0.5)

        glColor3f(*color)
        glRasterPos2f(WINDOW_WIDTH/2 - 120, WINDOW_HEIGHT/2 - 50)
        for ch in performance:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(WINDOW_WIDTH/2 - 100, 50)
        restart_text = "Press R to Restart Game | ESC to Quit"
        for ch in restart_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


    if debug_push_msg and (time.time() - debug_push_msg_time) < 1.2:
        glColor3f(1.0, 1.0, 0.0)
        glRasterPos2f(WINDOW_WIDTH/2 - 140, 110)
        for ch in debug_push_msg:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

    if current_state == PLAYING and game.player_has_ball:
        draw_power_meter()

def check_goalkeeper_collision():
    for side, goalie in goalies.items():
        box = goalie['collision_box']

        if (abs(game.ball_pos[0] - box['x']) < box['width']/2 and
            abs(game.ball_pos[2] - box['z']) < box['depth']/2 and
            game.ball_pos[1] < box['height']):

            if side == "north" or side == "south":
                game.ball_vel[0] = -game.ball_vel[0] * 0.8
                game.ball_vel[0] += random.uniform(-0.3, 0.3)
            else:
                game.ball_vel[2] = -game.ball_vel[2] * 0.8
                game.ball_vel[2] += random.uniform(-0.3, 0.3)

            game.ball_vel[1] = abs(game.ball_vel[1]) * 0.5 + 0.2
            return True

    return False


def check_goal():
    if (game.ball_pos[2] < -GOAL_LINE + 0.2 and
        abs(game.ball_pos[0]) < GOAL_WIDTH/2 and
        game.ball_pos[1] < GOAL_HEIGHT):

        if not check_goalkeeper_collision():
            if game.game_time - game.last_goal_time > 2:
                game.score += 1
                game.last_goal_time = game.game_time
                game.goal_message = "GOAL! +1 Point"
                game.goal_message_time = game.game_time
                reset_ball()
                return True

    elif (game.ball_pos[0] > GOAL_LINE - 0.2 and
          abs(game.ball_pos[2]) < GOAL_WIDTH/2 and
          game.ball_pos[1] < GOAL_HEIGHT):

        if not check_goalkeeper_collision():
            if game.game_time - game.last_goal_time > 2:
                game.score += 1
                game.last_goal_time = game.game_time
                game.goal_message = "GOAL! +1 Point"
                game.goal_message_time = game.game_time
                reset_ball()
                return True

    elif (game.ball_pos[2] > GOAL_LINE - 0.2 and
          abs(game.ball_pos[0]) < GOAL_WIDTH/2 and
          game.ball_pos[1] < GOAL_HEIGHT):

        if not check_goalkeeper_collision():
            if game.game_time - game.last_goal_time > 2:
                game.score += 1
                game.last_goal_time = game.game_time
                game.goal_message = "GOAL! +1 Point"
                game.goal_message_time = game.game_time
                reset_ball()
                return True

    elif (game.ball_pos[0] < -GOAL_LINE + 0.2 and
          abs(game.ball_pos[2]) < GOAL_WIDTH/2 and
          game.ball_pos[1] < GOAL_HEIGHT):

        if not check_goalkeeper_collision():
            if game.game_time - game.last_goal_time > 2:
                game.score += 1
                game.last_goal_time = game.game_time
                game.goal_message = "GOAL! +1 Point"
                game.goal_message_time = game.game_time
                reset_ball()
                return True

    return False

def can_push():
    return (time.time() - last_push_time) >= PUSH_COOLDOWN

def mark_push():
    global last_push_time
    last_push_time = time.time()

def set_debug_push(text):
    global debug_push_msg, debug_push_msg_time
    debug_push_msg = text
    debug_push_msg_time = time.time()
    print("[PUSH]", text)

def normalize2(x, z):
    d = math.sqrt(x*x + z*z)
    if d < 1e-6:
        return 0.0, 0.0
    return x/d, z/d

def left_from_forward(fx, fz):
    return -fz, fx

def clamp_pos_in_field(pos, margin=2.0):
    half = FIELD_SIZE/2 - margin
    pos[0] = max(-half, min(half, pos[0]))
    pos[2] = max(-half, min(half, pos[2]))

def shove_ai(ai_idx, dirx, dirz, dist):
    ai_players[ai_idx]["pos"][0] += dirx * dist
    ai_players[ai_idx]["pos"][2] += dirz * dist
    clamp_pos_in_field(ai_players[ai_idx]["pos"])

def pick_ai_in_direction(dirx, dirz, max_range=PUSH_RANGE, min_dot=0.25):
    best_i = None
    best_dist = 1e9
    for i, ai in enumerate(ai_players):
        dx = ai["pos"][0] - player["pos"][0]
        dz = ai["pos"][2] - player["pos"][2]
        dist = math.sqrt(dx*dx + dz*dz)
        if dist > max_range:
            continue
        ux, uz = normalize2(dx, dz)
        dot = ux*dirx + uz*dirz
        if dot >= min_dot and dist < best_dist:
            best_dist = dist
            best_i = i
    return best_i

def push_player_F():
    if current_state != PLAYING or (not game.is_playing) or game.game_over:
        return

    if not can_push():
        set_debug_push("Cooldown... wait 1 sec")
        return

    fx, fz = forward_vector_y(player["rot"])

    best_i = None
    best_dist = 9999.0

    for i, ai in enumerate(ai_players):
        dx = ai["pos"][0] - player["pos"][0]
        dz = ai["pos"][2] - player["pos"][2]
        dist = math.sqrt(dx*dx + dz*dz)

        if dist <= PUSH_RANGE:
            ux, uz = normalize2(dx, dz)
            dot = ux*fx + uz*fz
            if dot > -0.15:
                if dist < best_dist:
                    best_dist = dist
                    best_i = i

    if best_i is None:
        set_debug_push("No target to push")
        return

    dx = ai_players[best_i]["pos"][0] - player["pos"][0]
    dz = ai_players[best_i]["pos"][2] - player["pos"][2]
    dirx, dirz = normalize2(dx, dz)

    shove_ai(best_i, dirx, dirz, PUSH_DIST)
    block_entity_pickup(best_i)

    start_push_anim("F") 
    mark_push()
    set_debug_push(f"Pushed {ai_players[best_i]['name']}")

def push_player_dir(key_name):
    if current_state != PLAYING or (not game.is_playing) or game.game_over:
        return

    if not can_push():
        set_debug_push("Cooldown... wait 1 sec")
        return

    fx, fz = forward_vector_y(player["rot"])
    lx, lz = left_from_forward(fx, fz)
    rx, rz = -lx, -lz 

    if key_name == "I":
        dirx, dirz = normalize2(fx + 0.6*rx, fz + 0.6*rz)
        anim = "I"
    elif key_name == "K":
        dirx, dirz = normalize2(-fx + 0.6*lx, -fz + 0.6*lz)
        anim = "K"
    elif key_name == "J":
        dirx, dirz = normalize2(lx, lz)
        anim = "J"
    else:
        dirx, dirz = normalize2(rx, rz)
        anim = "L"

    target = pick_ai_in_direction(dirx, dirz, max_range=PUSH_RANGE, min_dot=0.15)

    if target is None:
        best_dist = 1e9
        for i, ai in enumerate(ai_players):
            dx = ai["pos"][0] - player["pos"][0]
            dz = ai["pos"][2] - player["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            if dist <= PUSH_RANGE and dist < best_dist:
                best_dist = dist
                target = i

    if target is None:
        set_debug_push("No target to push")
        return

    shove_ai(target, dirx, dirz, PUSH_DIST)
    block_entity_pickup(target)

    start_push_anim(anim)
    mark_push()
    set_debug_push(f"Directional push ({anim}) -> {ai_players[target]['name']}")

def forward_vector_y(rot_deg):
    ang = math.radians(rot_deg)
    fx = math.sin(ang)
    fz = math.cos(ang)
    return fx, fz

def is_ball_in_front(entity_pos, entity_rot, ball_pos, min_dot=0.35):
    vx = ball_pos[0] - entity_pos[0]
    vz = ball_pos[2] - entity_pos[2]
    dist = math.sqrt(vx*vx + vz*vz)
    if dist < 1e-6:
        return True

    vx /= dist
    vz /= dist

    fx, fz = forward_vector_y(entity_rot)
    dot = vx*fx + vz*fz
    return dot >= min_dot

def hand_attach_position(entity_pos, entity_rot):
    fx, fz = forward_vector_y(entity_rot)
    x = entity_pos[0] + fx * 0.45
    y = 1.0
    z = entity_pos[2] + fz * 0.45
    return [x, y, z]

def can_entity_pickup(entity_key):
    return (time.time() - last_pickup_block[entity_key]) >= PICKUP_COOLDOWN

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

def try_pickup_ball_human():
    global ball_owner
    if ball_owner is not None:
        return
    if not can_entity_pickup("human"):
        return

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

    ai = ai_players[i]
    dx = game.ball_pos[0] - ai["pos"][0]
    dz = game.ball_pos[2] - ai["pos"][2]
    dist = math.sqrt(dx*dx + dz*dz)

    if dist < 1.35 and game.ball_pos[1] < 0.95 and is_ball_in_front(ai["pos"], ai["rot"], game.ball_pos):
        ball_owner = ("ai", i)
        game.ball_vel = [0, 0, 0]
        game.ball_pos = hand_attach_position(ai["pos"], ai["rot"])

def try_steal_ball_human():
    global ball_owner

    if ball_owner is None:
        return
    owner_type, owner_idx = ball_owner
    if owner_type != "ai":
        return

    ai = ai_players[owner_idx]
    dx = ai["pos"][0] - player["pos"][0]
    dz = ai["pos"][2] - player["pos"][2]
    dist = math.sqrt(dx*dx + dz*dz)

    if dist < 2.25:
        if not is_ball_in_front(player["pos"], player["rot"], ai["pos"], min_dot=0.0):
            return
        knockback_loser(ai["pos"], player["pos"], dist=KNOCKBACK_DIST)
        block_entity_pickup(owner_idx)
        ball_owner = ("human", None)
        game.player_has_ball = True
        game.ball_vel = [0, 0, 0]
        game.ball_pos = hand_attach_position(player["pos"], player["rot"])

def shoot_ball_ai(i, power=1.2):
    global ball_owner
    ai = ai_players[i]
    ball_owner = None

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
    if owner_type == "ai" and owner_idx == i:
        return

    ai = ai_players[i]

    if owner_type == "human":
        target_pos = player["pos"]
        target_key = "human"
    else:
        target_pos = ai_players[owner_idx]["pos"]
        target_key = owner_idx

    dx = target_pos[0] - ai["pos"][0]
    dz = target_pos[2] - ai["pos"][2]
    dist = math.sqrt(dx*dx + dz*dz)

    if dist < 1.25:
        if not is_ball_in_front(ai["pos"], ai["rot"], target_pos, min_dot=0.0):
            return

        knockback_loser(target_pos, ai["pos"], dist=KNOCKBACK_DIST)
        block_entity_pickup(target_key)
        ball_owner = ("ai", i)
        game.player_has_ball = False
        game.ball_vel = [0, 0, 0]
        game.ball_pos = hand_attach_position(ai["pos"], ai["rot"])

def separate_ai(i, min_sep=1.0, push=0.03):
    ax, az = ai_players[i]["pos"][0], ai_players[i]["pos"][2]
    for j, other in enumerate(ai_players):
        if j == i:
            continue
        bx, bz = other["pos"][0], other["pos"][2]
        dx = ax - bx
        dz = az - bz
        d = math.sqrt(dx*dx + dz*dz)
        if d < 1e-6:
            dx = random.uniform(-1, 1)
            dz = random.uniform(-1, 1)
            d = math.sqrt(dx*dx + dz*dz)
        if d < min_sep:
            dx /= d
            dz /= d
            ai_players[i]["pos"][0] += dx * push
            ai_players[i]["pos"][2] += dz * push

def separate_player_from_ai(min_sep=1.0, push=0.06):
    px, pz = player["pos"][0], player["pos"][2]
    for ai in ai_players:
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

def update_ai_players():
    global ball_owner
    if not game.is_playing or game.game_over:
        return

    half_size = FIELD_SIZE / 2 - 2

    goals = [
        {"side":"north", "pos": (0, -GOAL_LINE), "team":"blue"},
        {"side":"east",  "pos": (GOAL_LINE, 0),  "team":"red"},
        {"side":"south", "pos": (0, GOAL_LINE),  "team":"yellow"},
        {"side":"west",  "pos": (-GOAL_LINE, 0), "team":"green"},
    ]

    for i, ai in enumerate(ai_players):
        if ball_owner == ("ai", i):
            best = None
            best_d = 1e9
            for g in goals:
                if g["team"] == ai["team"]:
                    continue
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
                vx /= dist
                vz /= dist
                ai["pos"][0] += vx * ai["speed"]
                ai["pos"][2] += vz * ai["speed"]
                ai["rot"] = math.degrees(math.atan2(vx, vz))

            if dist < 3.0:
                shoot_ball_ai(i, power=1.25)

            continue

        if ball_owner == ("human", None):
            tx, tz = player["pos"][0], player["pos"][2]
        else:
            tx, tz = game.ball_pos[0], game.ball_pos[2]

        vx = tx - ai["pos"][0]
        vz = tz - ai["pos"][2]
        dist = math.sqrt(vx*vx + vz*vz)

        if dist > 0.05:
            vx /= dist
            vz /= dist
            ai["pos"][0] += vx * ai["speed"]
            ai["pos"][2] += vz * ai["speed"]
            ai["rot"] = math.degrees(math.atan2(vx, vz))

        ai["pos"][0] = max(-half_size, min(half_size, ai["pos"][0]))
        ai["pos"][2] = max(-half_size, min(half_size, ai["pos"][2]))
        separate_ai(i, min_sep=1.1, push=0.04)

def update_physics():
    if not game.is_playing or game.game_over:
        return

    game.game_time += 1/60.0

    if game.game_time >= game.total_game_time:
        game.game_over = True
        game.is_playing = False
        return

    gravity = -0.098
    friction = 0.99
    bounce_damping = 0.7

    game.ball_vel[1] += gravity
    game.ball_vel[0] *= friction
    game.ball_vel[2] *= friction

    game.ball_pos[0] += game.ball_vel[0]
    game.ball_pos[1] += game.ball_vel[1]
    game.ball_pos[2] += game.ball_vel[2]

    if game.ball_pos[1] < 0.2:
        game.ball_pos[1] = 0.2
        game.ball_vel[1] = -game.ball_vel[1] * bounce_damping

    half_size = FIELD_SIZE / 2 - 0.5
    if abs(game.ball_pos[0]) > half_size:
        game.ball_pos[0] = half_size if game.ball_pos[0] > 0 else -half_size
        game.ball_vel[0] = -game.ball_vel[0] * 0.8

    if abs(game.ball_pos[2]) > half_size:
        game.ball_pos[2] = half_size if game.ball_pos[2] > 0 else -half_size
        game.ball_vel[2] = -game.ball_vel[2] * 0.8

    check_goalkeeper_collision()
    check_goal()

    if ball_owner is not None:
        owner_type, owner_idx = ball_owner
        if owner_type == "human":
            game.ball_pos = hand_attach_position(player["pos"], player["rot"])
        else:
            ai = ai_players[owner_idx]
            game.ball_pos = hand_attach_position(ai["pos"], ai["rot"])

        game.ball_vel = [0, 0, 0]
        game.player_has_ball = (owner_type == "human")

        if ball_owner == ("human", None):
            fx, fz = forward_vector_y(player["rot"])
            for i, ai in enumerate(ai_players):
                dx = ai["pos"][0] - player["pos"][0]
                dz = ai["pos"][2] - player["pos"][2]
                dist = math.sqrt(dx*dx + dz*dz)
                if dist < 0.95:
                    ux, uz = normalize2(dx, dz)
                    if (ux*fx + uz*fz) > 0.1:
                        shove_ai(i, fx, fz, 0.9)
                        block_entity_pickup(i)
                        break
    else:
        dx = player['pos'][0] - game.ball_pos[0]
        dz = player['pos'][2] - game.ball_pos[2]
        dist = math.sqrt(dx*dx + dz*dz)
        game.player_has_ball = (dist < 1.0 and game.ball_pos[1] < 0.8)

        vx, vz = game.ball_vel[0], game.ball_vel[2]
        sp = math.sqrt(vx*vx + vz*vz)
        if sp > 0.05 and game.ball_pos[1] < 1.2:
            dirx, dirz = normalize2(vx, vz)
            for i, ai in enumerate(ai_players):
                adx = ai["pos"][0] - game.ball_pos[0]
                adz = ai["pos"][2] - game.ball_pos[2]
                d = math.sqrt(adx*adx + adz*adz)
                if d < BALL_HIT_RADIUS:
                    shove_ai(i, dirx, dirz, BALL_PUSH_AI_DIST)
                    block_entity_pickup(i)
                    game.ball_vel[0] *= 0.65
                    game.ball_vel[2] *= 0.65
                    set_debug_push(f"Ball pushed {ai['name']}")
                    break

    if power_meter['charging'] and game.player_has_ball and game.is_playing:
        power_meter['value'] += power_meter['charge_rate'] / 60
        if power_meter['value'] > power_meter['max_power']:
            power_meter['value'] = power_meter['max_power']

def reset_ball():
    global ball_owner
    ball_owner = None
    game.ball_pos = [0, 0.5, 0]
    game.ball_vel = [0, 0, 0]
    game.player_has_ball = False
    power_meter['value'] = 0.0
    power_meter['charging'] = False

def restart_game():

    global game, player, current_state, player_name_input, power_meter, ball_owner
    game = Game()
    player = {
        'pos': [0, 0, 0],
        'rot': 0,
        'speed': 0.15,
        'team': 'blue',
        'jersey_number': 10
    }
    player_name_input = ""
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
    ball_owner = None
    current_state = MENU

def process_player_movement():
    if not game.is_playing or game.game_over:
        return

    if key_states[GLUT_KEY_UP]:
        player['pos'][2] -= player['speed']
        player['rot'] = 180
    if key_states[GLUT_KEY_DOWN]:
        player['pos'][2] += player['speed']
        player['rot'] = 0
    if key_states[GLUT_KEY_LEFT]:
        player['pos'][0] -= player['speed']
        player['rot'] = 270
    if key_states[GLUT_KEY_RIGHT]:
        player['pos'][0] += player['speed']
        player['rot'] = 90

    if key_states[GLUT_KEY_UP] and key_states[GLUT_KEY_LEFT]:
        player['rot'] = 315
    if key_states[GLUT_KEY_UP] and key_states[GLUT_KEY_RIGHT]:
        player['rot'] = 45
    if key_states[GLUT_KEY_DOWN] and key_states[GLUT_KEY_LEFT]:
        player['rot'] = 225
    if key_states[GLUT_KEY_DOWN] and key_states[GLUT_KEY_RIGHT]:
        player['rot'] = 135

    half_size = FIELD_SIZE / 2 - 2
    player['pos'][0] = max(-half_size, min(half_size, player['pos'][0]))
    player['pos'][2] = max(-half_size, min(half_size, player['pos'][2]))

def shoot_ball(power):
    global ball_owner
    ball_owner = None

    angle_x = math.sin(math.radians(player['rot']))
    angle_z = math.cos(math.radians(player['rot']))

    game.ball_vel[0] = angle_x * power
    game.ball_vel[1] = 0.3 + (power * 0.1)
    game.ball_vel[2] = angle_z * power

    game.player_has_ball = False
    power_meter['charging'] = False

    power_meter['last_shot_power'] = power
    power_meter['last_shot_time'] = time.time()
    power_meter['show_last_power'] = True
    power_meter['value'] = 0.0


def draw_menu():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(0.0, 0.1, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()

    glColor3f(1.0, 1.0, 0.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 150, WINDOW_HEIGHT - 150)
    title = "FOOTBALL CHALLENGE"
    for ch in title:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 200, WINDOW_HEIGHT - 200)
    subtitle = "Single Player - Score Against 4 Goalkeepers!"
    for ch in subtitle:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    start_color = (0.0, 1.0, 0.0) if menu_selection == 0 else (0.5, 0.5, 0.5)
    quit_color  = (1.0, 0.0, 0.0) if menu_selection == 1 else (0.5, 0.5, 0.5)

    glColor3f(*start_color)
    glRasterPos2f(WINDOW_WIDTH/2 - 50, WINDOW_HEIGHT/2 + 50)
    for ch in "START GAME":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(*quit_color)
    glRasterPos2f(WINDOW_WIDTH/2 - 30, WINDOW_HEIGHT/2 - 50)
    for ch in "QUIT":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(1.0, 1.0, 0.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 80, WINDOW_HEIGHT/2 + 50 if menu_selection == 0 else WINDOW_HEIGHT/2 - 50)
    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('>'))

    glColor3f(0.8, 0.8, 0.8)
    glRasterPos2f(50, 100)
    instructions = "Use UP/DOWN to navigate, ENTER to select"
    for ch in instructions:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def draw_jersey_selection():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(0.0, 0.1, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()

    glColor3f(1.0, 1.0, 0.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 120, WINDOW_HEIGHT - 100)
    for ch in "SELECT YOUR JERSEY":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    glColor3f(0.0, 1.0, 0.0) if jersey_selection == 0 else glColor3f(0.7, 0.7, 0.7)
    glBegin(GL_LINE_LOOP)
    glVertex2f(WINDOW_WIDTH/2 - 200, WINDOW_HEIGHT/2 + 100)
    glVertex2f(WINDOW_WIDTH/2 - 50,  WINDOW_HEIGHT/2 + 100)
    glVertex2f(WINDOW_WIDTH/2 - 50,  WINDOW_HEIGHT/2 - 100)
    glVertex2f(WINDOW_WIDTH/2 - 200, WINDOW_HEIGHT/2 - 100)
    glEnd()

    glRasterPos2f(WINDOW_WIDTH/2 - 180, WINDOW_HEIGHT/2 + 150)
    for ch in "HOME":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(0.2, 0.6, 1.0)
    glBegin(GL_QUADS)
    glVertex2f(WINDOW_WIDTH/2 - 180, WINDOW_HEIGHT/2 + 80)
    glVertex2f(WINDOW_WIDTH/2 - 70,  WINDOW_HEIGHT/2 + 80)
    glVertex2f(WINDOW_WIDTH/2 - 70,  WINDOW_HEIGHT/2 - 80)
    glVertex2f(WINDOW_WIDTH/2 - 180, WINDOW_HEIGHT/2 - 80)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 125, WINDOW_HEIGHT/2)
    for ch in "10":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(0.0, 1.0, 0.0) if jersey_selection == 1 else glColor3f(0.7, 0.7, 0.7)
    glBegin(GL_LINE_LOOP)
    glVertex2f(WINDOW_WIDTH/2 + 50,  WINDOW_HEIGHT/2 + 100)
    glVertex2f(WINDOW_WIDTH/2 + 200, WINDOW_HEIGHT/2 + 100)
    glVertex2f(WINDOW_WIDTH/2 + 200, WINDOW_HEIGHT/2 - 100)
    glVertex2f(WINDOW_WIDTH/2 + 50,  WINDOW_HEIGHT/2 - 100)
    glEnd()

    glRasterPos2f(WINDOW_WIDTH/2 + 90, WINDOW_HEIGHT/2 + 150)
    for ch in "AWAY":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(1.0, 0.8, 0.0)
    glBegin(GL_QUADS)
    glVertex2f(WINDOW_WIDTH/2 + 70,  WINDOW_HEIGHT/2 + 80)
    glVertex2f(WINDOW_WIDTH/2 + 180, WINDOW_HEIGHT/2 + 80)
    glVertex2f(WINDOW_WIDTH/2 + 180, WINDOW_HEIGHT/2 - 80)
    glVertex2f(WINDOW_WIDTH/2 + 70,  WINDOW_HEIGHT/2 - 80)
    glEnd()

    glColor3f(0.0, 0.0, 0.0)
    glRasterPos2f(WINDOW_WIDTH/2 + 125, WINDOW_HEIGHT/2)
    for ch in "10":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(1.0, 1.0, 0.0)
    if jersey_selection == 0:
        glRasterPos2f(WINDOW_WIDTH/2 - 220, WINDOW_HEIGHT/2)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('>'))
    else:
        glRasterPos2f(WINDOW_WIDTH/2 + 210, WINDOW_HEIGHT/2)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('<'))

    glColor3f(0.8, 0.8, 0.8)
    glRasterPos2f(WINDOW_WIDTH/2 - 150, 150)
    instructions = "Use LEFT/RIGHT to choose, ENTER to confirm, ESC to go back"
    for ch in instructions:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def draw_player_name_input():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(0.0, 0.1, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()

    glColor3f(1.0, 1.0, 0.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 150, WINDOW_HEIGHT - 150)
    for ch in "ENTER YOUR NAME":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 200, WINDOW_HEIGHT - 200)
    instruction = "This name will appear above your player in the game"
    for ch in instruction:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(WINDOW_WIDTH/2 - 200, WINDOW_HEIGHT/2 + 30)
    glVertex2f(WINDOW_WIDTH/2 + 200, WINDOW_HEIGHT/2 + 30)
    glVertex2f(WINDOW_WIDTH/2 + 200, WINDOW_HEIGHT/2 - 30)
    glVertex2f(WINDOW_WIDTH/2 - 200, WINDOW_HEIGHT/2 - 30)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(WINDOW_WIDTH/2 - 190, WINDOW_HEIGHT/2)
    display_name = player_name_input if len(player_name_input) > 0 else "Type your name..."
    for ch in display_name:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    if time.time() % 1.0 < 0.5:
        glColor3f(1.0, 1.0, 0.0)
        cursor_x = WINDOW_WIDTH/2 - 190 + len(display_name) * 10
        glRasterPos2f(cursor_x, WINDOW_HEIGHT/2)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('|'))

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def display():
    if current_state == MENU:
        draw_menu()

    elif current_state == JERSEY_SELECTION:
        draw_jersey_selection()

    elif current_state == PLAYER_NAME_INPUT:
        draw_player_name_input()

    elif current_state == PLAYING:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        set_camera()

        draw_square_field()

        draw_simple_goal("north", (0.0, 0.545, 0.545))
        draw_goal_box("north")
        draw_simple_goal("east", (1.0, 0.2, 0.2))
        draw_goal_box("east")
        draw_simple_goal("south", (1.0, 1.0, 0.2))
        draw_goal_box("south")
        draw_simple_goal("west", (0.2, 1.0, 0.2))
        draw_goal_box("west")

        draw_goalkeeper("north", (0.0, 0.545, 0.545))
        draw_goalkeeper("east", (1.0, 0.2, 0.2))
        draw_goalkeeper("south", (1.0, 1.0, 0.2))
        draw_goalkeeper("west", (0.2, 1.0, 0.2))

        draw_player()
        draw_ball()

        for i, ai in enumerate(ai_players):
            draw_ai_player(ai, i)

        draw_hud()

    elif current_state == GAME_OVER:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        set_camera()

        draw_stadium_stands()
        draw_square_field()

        draw_simple_goal("north", (0.0, 0.545, 0.545))
        draw_goal_box("north")
        draw_simple_goal("east", (1.0, 0.2, 0.2))
        draw_goal_box("east")
        draw_simple_goal("south", (1.0, 1.0, 0.2))
        draw_goal_box("south")
        draw_simple_goal("west", (0.2, 1.0, 0.2))
        draw_goal_box("west")

        draw_goalkeeper("north", (0.0, 0.545, 0.545))
        draw_goalkeeper("east", (1.0, 0.2, 0.2))
        draw_goalkeeper("south", (1.0, 1.0, 0.2))
        draw_goalkeeper("west", (0.2, 1.0, 0.2))

        draw_player()
        draw_ball()
        for i, ai in enumerate(ai_players):
            draw_ai_player(ai, i)
        draw_hud()

    glutSwapBuffers()

def reshape(width, height):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH = width
    WINDOW_HEIGHT = height
    glViewport(0, 0, width, height)

def keyboard(key, x, y):
    global camera_mode, current_state, game, player_name_input

    if isinstance(key, bytes):
        key_char = key.decode('utf-8')
    else:
        return

    if current_state == MENU:
        if key_char == '\r':
            if menu_selection == 0:
                current_state = JERSEY_SELECTION
            else:
                glutLeaveMainLoop()
        elif key_char == '\x1b':
            glutLeaveMainLoop()

    elif current_state == JERSEY_SELECTION:
        if key_char == '\r':
            current_state = PLAYER_NAME_INPUT
        elif key_char == '\x1b':
            current_state = MENU

    elif current_state == PLAYER_NAME_INPUT:
        if key_char == '\r':
            game.player_name = player_name_input.strip() if player_name_input.strip() else "YOU"

            if jersey_selection == 0:
                game.selected_jersey = "argentina"
                player['team'] = 'blue'
            else:
                game.selected_jersey = "brazil"
                player['team'] = 'yellow'

            current_state = PLAYING
            game.is_playing = True

        elif key_char == '\x1b':
            current_state = JERSEY_SELECTION

        elif key_char == '\x08':
            if player_name_input:
                player_name_input = player_name_input[:-1]

        elif len(key_char) == 1 and key_char.isprintable() and len(player_name_input) < MAX_NAME_LENGTH:
            player_name_input += key_char

    elif current_state == PLAYING or current_state == GAME_OVER:
        if key_char.lower() == 'c':
            modes = ["PLAYER","OVERHEAD"]
            current_idx = modes.index(camera_mode)
            camera_mode = modes[(current_idx + 1) % len(modes)]

        elif key_char.lower() == 'p' and current_state == PLAYING:
            game.is_playing = not game.is_playing

        elif key_char == ' ' and game.player_has_ball and game.is_playing and not game.game_over:
            if not power_meter['charging']:
                power_meter['charging'] = True
                power_meter['value'] = 0.1
        elif key_char.lower() == 'f':
            push_player_F()
        elif key_char.lower() == 'i':
            push_player_dir("I")
        elif key_char.lower() == 'k':
            push_player_dir("K")
        elif key_char.lower() == 'j':
            push_player_dir("J")
        elif key_char.lower() == 'l':
            push_player_dir("L")

        elif key_char.lower() == 'r':
            if current_state == GAME_OVER:
                restart_game()
            else:
                reset_ball()

        elif key_char == '\x1b':
            current_state = MENU

    glutPostRedisplay()

def keyboard_up(key, x, y):
    global power_meter, game

    if isinstance(key, bytes):
        key_char = key.decode('utf-8')
    else:
        return

    if key_char == ' ' and current_state == PLAYING and game.player_has_ball and game.is_playing and not game.game_over:
        if power_meter['charging']:
            shoot_ball(power_meter['value'])
            power_meter['charging'] = False

    glutPostRedisplay()


def special_keys(key, x, y):
    global menu_selection, jersey_selection, current_state

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

    elif current_state == PLAYING or current_state == GAME_OVER:
        if key == GLUT_KEY_UP:
            key_states[GLUT_KEY_UP] = True
        elif key == GLUT_KEY_DOWN:
            key_states[GLUT_KEY_DOWN] = True
        elif key == GLUT_KEY_LEFT:
            key_states[GLUT_KEY_LEFT] = True
        elif key == GLUT_KEY_RIGHT:
            key_states[GLUT_KEY_RIGHT] = True

    glutPostRedisplay()


def special_up(key, x, y):
    if current_state == PLAYING or current_state == GAME_OVER:
        if key == GLUT_KEY_UP:
            key_states[GLUT_KEY_UP] = False
        elif key == GLUT_KEY_DOWN:
            key_states[GLUT_KEY_DOWN] = False
        elif key == GLUT_KEY_LEFT:
            key_states[GLUT_KEY_LEFT] = False
        elif key == GLUT_KEY_RIGHT:
            key_states[GLUT_KEY_RIGHT] = False

    glutPostRedisplay()

def update(value):
    if current_state == PLAYING or current_state == GAME_OVER:
        process_player_movement()
        update_ai_players()

        separate_player_from_ai(min_sep=1.1, push=0.06)
        for i in range(len(ai_players)):
            separate_ai(i, min_sep=1.1, push=0.04)

        update_physics()

        try_pickup_ball_human()
        try_steal_ball_human()

        for i in range(len(ai_players)):
            try_pickup_ball_ai(i)
            try_steal_ball_ai(i)

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
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
    print("\nCONTROLS:")
    print("- Arrow Keys: Move")
    print("- SPACE: Hold to charge shot power, release to shoot")
    print("- F: Push another player (1 sec cooldown)")
    print("- I/K/J/L: Directional Push (Forward/Backward/Left/Right) with limb animation")
    print("- C: Change camera view (Player/Overhead)")
    print("- P: Pause/Resume game")
    print("- R: Reset ball / Restart after game over")
    print("- ESC: Quit to menu")
    glutMainLoop()

if __name__ == "__main__":
    main()