#!/usr/bin/env python3
"""
Engineering Calculator with PyOpenGL and GLUT
sudo apt install freeglut3-dev
python -m venv venv
. venv/bin/activate
pip install PyOpenGL PyOpenGL_accelerate
python calc.py
"""

import os
os.environ['PYOPENGL_NO_CONTEXT_CHECK'] = '1'

import sys
import math
import threading

from OpenGL import contextdata
_original_getContext = contextdata.getContext
def _safe_getContext(context=None):
    try:
        return _original_getContext(context)
    except Exception:
        dummy = threading.current_thread().__dict__.get('_dummy_gl_context')
        if dummy is None:
            dummy = type('DummyContext', (), {})()
            threading.current_thread()._dummy_gl_context = dummy
        return dummy
contextdata.getContext = _safe_getContext

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

WIDTH, HEIGHT = 800, 400
DISPLAY_HEIGHT = 100
BUTTON_START_Y = DISPLAY_HEIGHT + 45
BUTTON_WIDTH = 85
BUTTON_HEIGHT = 50
COLS = 8

buttons_def = [
    ('7', 'append', '7'), ('8', 'append', '8'), ('9', 'append', '9'), ('/', 'append', '/'),
    ('sin', 'append', 'sin('), ('asin', 'append', 'asin('), ('pi', 'append', 'pi'), ('C', 'clear', None),
    ('4', 'append', '4'), ('5', 'append', '5'), ('6', 'append', '6'), ('*', 'append', '*'),
    ('cos', 'append', 'cos('), ('acos', 'append', 'acos('), ('e', 'append', 'e'), ('<=', 'backspace', None),
    ('1', 'append', '1'), ('2', 'append', '2'), ('3', 'append', '3'), ('-', 'append', '-'),
    ('tan', 'append', 'tan('), ('atan', 'append', 'atan('), ('sqrt', 'append', 'sqrt('), ('^', 'append', '^'),
    ('0', 'append', '0'), ('.', 'append', '.'), ('=', 'equals', None), ('+', 'append', '+'),
    ('(', 'append', '('), (')', 'append', ')'), ('log10', 'append', 'log10('), ('ln', 'append', 'ln('),
    ('exp', 'append', 'exp('), ('Ans', 'ans', None), ('g', 'append', 'g'), ('c', 'append', 'c')
]

expression = ""
last_result = "0.0"
last_answer = 0.0

safe_dict = {name: getattr(math, name) for name in dir(math) if not name.startswith('_')}
safe_dict.update({
    'g': 9.80665,
    'c': 299792458.0,
    'ans': last_answer,
    'ln': math.log,
    'log': math.log10,
    '__builtins__': None
})

def evaluate_expression(expr):
    if not expr.strip():
        return None, "Empty expression"
    try:
        eval_expr = expr.replace('^', '**')
        safe_dict['ans'] = last_answer
        result = eval(eval_expr, safe_dict)
        return result, None
    except Exception as e:
        return None, str(e)

def add_to_expression(text):
    global expression
    expression += text

def clear_expression():
    global expression, last_result
    expression = ""
    last_result = "0.0"

def backspace():
    global expression
    expression = expression[:-1]

def compute_result():
    global expression, last_result, last_answer
    value, error = evaluate_expression(expression)
    if error is None:
        formatted = f"{value:.10g}".rstrip('.') if isinstance(value, float) else str(value)
        last_result = formatted
        last_answer = value
        #expression = last_result
    else:
        last_result = f"Error: {error}"
        #expression = ""

def handle_button_action(label, action_type, action_data):
    if action_type == 'append':
        add_to_expression(action_data)
    elif action_type == 'clear':
        clear_expression()
    elif action_type == 'backspace':
        backspace()
    elif action_type == 'equals':
        compute_result()
    elif action_type == 'ans':
        add_to_expression('ans')

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(0,0,0)):
    glColor3f(*color)
    glRasterPos2i(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_rect(x, y, w, h, fill_color, border_color=(0,0,0)):
    glColor3f(*fill_color)
    glBegin(GL_QUADS)
    glVertex2i(x, y); glVertex2i(x+w, y); glVertex2i(x+w, y+h); glVertex2i(x, y+h)
    glEnd()
    glColor3f(*border_color)
    glBegin(GL_LINE_LOOP)
    glVertex2i(x, y); glVertex2i(x+w, y); glVertex2i(x+w, y+h); glVertex2i(x, y+h)
    glEnd()

def draw_display():
    draw_rect(10, HEIGHT - DISPLAY_HEIGHT + 10, WIDTH - 20, DISPLAY_HEIGHT - 20, (0.95,0.95,0.95), (0.3,0.3,0.3))
    expr_display = expression if len(expression) <= 40 else "..." + expression[-37:]
    draw_text(20, HEIGHT - DISPLAY_HEIGHT + 55, f"Expr: {expr_display}", GLUT_BITMAP_HELVETICA_18, (0.2,0.2,0.8))
    result_display = last_result if len(last_result) <= 40 else "..." + last_result[-37:]
    draw_text(20, HEIGHT - DISPLAY_HEIGHT + 25, f"= {result_display}", GLUT_BITMAP_HELVETICA_18, (0,0,0))

def draw_buttons():
    for idx, (label, action_type, _) in enumerate(buttons_def):
        row, col = divmod(idx, COLS)
        x = 20 + col * (BUTTON_WIDTH + 10)
        y = HEIGHT - BUTTON_START_Y - row * (BUTTON_HEIGHT + 10)
        if action_type == 'equals':
            fill = (0.3, 0.7, 0.3)
        elif action_type in ('clear', 'backspace'):
            fill = (0.9, 0.5, 0.4)
        elif label in ('sin','cos','tan','asin','acos','atan','sqrt','log10','ln','exp','pi','e','g','c'):
            fill = (0.5, 0.7, 0.9)
        elif label == 'Ans':
            fill = (0.8, 0.8, 0.5)
        else:
            fill = (0.9, 0.9, 0.9)
        draw_rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, fill, (0.2,0.2,0.2))
        text_x = x + BUTTON_WIDTH//2 - len(label)*4
        text_y = y + BUTTON_HEIGHT//2 - 6
        draw_text(text_x, text_y, label, GLUT_BITMAP_HELVETICA_18, (0,0,0))

def init_gl():
    glClearColor(0.85, 0.85, 0.85, 1.0)

def display():
    if not hasattr(display, "gl_initialized"):
        init_gl()
        display.gl_initialized = True
    glClear(GL_COLOR_BUFFER_BIT)
    draw_display()
    draw_buttons()
    glutSwapBuffers()

def reshape(w, h):
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def mouse(button, state, x, y):
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return
    gl_y = HEIGHT - y
    for idx, (label, action_type, action_data) in enumerate(buttons_def):
        row, col = divmod(idx, COLS)
        btn_x = 20 + col * (BUTTON_WIDTH + 10)
        btn_y = HEIGHT - BUTTON_START_Y - row * (BUTTON_HEIGHT + 10)
        if btn_x <= x <= btn_x + BUTTON_WIDTH and btn_y <= gl_y <= btn_y + BUTTON_HEIGHT:
            handle_button_action(label, action_type, action_data)
            glutPostRedisplay()
            return

def keyboard(key, x, y):
    if isinstance(key, bytes):
        key = key.decode('utf-8')
    if key in ('\r', '\n'):
        compute_result()
    elif key in ('\x08', '\x7f'):
        backspace()
    elif key == '\x1b':
        clear_expression()
    elif key in '0123456789+-*/().^':
        add_to_expression(key)
    elif key == '=':
        compute_result()
    elif key.lower() == 'c':
        clear_expression()
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Engineering Calculator")
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == "__main__":
    main()
