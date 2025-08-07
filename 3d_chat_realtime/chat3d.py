import io, logging, os, sys, textwrap, time
from threading import Thread

import requests
from raylib import *
from texttopng import render


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('main').setLevel(logging.INFO)

LN = logging.NOTSET
LD = logging.DEBUG
LI = logging.INFO
LW = logging.WARNING
LE = logging.ERROR
LC = logging.CRITICAL
LICONS = {LN:'ℹ', LD:'🇩', LI:'ℹ️', LW:'⚠', LE:'🆘', LC:'👾'}

def log(lvl=LN, msgs=[], *args, **kwargs):
    s = f'{LICONS[lvl]}::{__name__}.{sys._getframe().f_back.f_code.co_name}'
    for m in msgs:
        s += f'::{m}'
        if hasattr(m, '__traceback__'):
            s += f'🇱🇮🇳🇪{m.__traceback__.tb_lineno}'
    logging.log(lvl, s, *args, **kwargs)

global HTTP_CHAT_URL, HTTP_TIMEOUT, CHAT_REQUEST_DURATION, CHAT_LENGTH_WRAP_MESSAGE
HTTP_CHAT_URL = 'https://studio.rutube.ru/api/chat/{YOUR-CHAT-ID}/'
HTTP_TIMEOUT = 20
CHAT_REQUEST_DURATION = 10
CHAT_LENGTH_WRAP_MESSAGE = 15
config_file_path = f'{os.getcwd()}//config.json'
log(LD, ['🎂CONFIG_FILE_PATH🎂', config_file_path])
def config_read():
    global HTTP_CHAT_URL, HTTP_TIMEOUT, CHAT_REQUEST_DURATION
    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = eval(config_file.read())
            #log(LD, ['🎂CONFIG🎂', config])
            HTTP_CHAT_URL = config.get('HTTP_CHAT_URL', HTTP_CHAT_URL)
            HTTP_TIMEOUT = config.get('HTTP_TIMEOUT', HTTP_TIMEOUT)
            CHAT_REQUEST_DURATION = config.get('CHAT_REQUEST_DURATION', CHAT_REQUEST_DURATION)
            CHAT_LENGTH_WRAP_MESSAGE = config.get('CHAT_LENGTH_WRAP_MESSAGE', CHAT_LENGTH_WRAP_MESSAGE)
config_read()

def api_chat_get(last_value = ''):
    global HTTP_CHAT_URL, HTTP_TIMEOUT, CHAT_REQUEST_DURATION, CHAT_LENGTH_WRAP_MESSAGE
    config_read()
    data = last_value
    session = requests.Session()
    try:
        response = session.get(HTTP_CHAT_URL, timeout=HTTP_TIMEOUT)
    except requests.exceptions.ConnectTimeout as e:
        log(LW, [HTTP_CHAT_URL, e])
    except Exception as e:
        log(LE, [HTTP_CHAT_URL, e])
    else:
        #log(LD, ['🎂RESPONSE🎂', response.status_code])
        #log(LD, ['🎂RESPONSE.HEADERS🎂', response.headers])
        #log(LD, ['🎂SESSION.COOKIES🎂', session.cookies])
        #log(LD, ['🎂SESSION.HEADERS🎂', session.headers])
        if response.status_code == 200:
            res = response.json()
            if res:
                results = res.get('results', [])
                if len(results):
                    payload = results[0].get('payload', {})
                    if 'text' in payload:
                        data = payload.get('text', '')
                        if len(data) > 5:
                            data = textwrap.fill(data, CHAT_LENGTH_WRAP_MESSAGE)
        else:
            log(LW, ['🎂RESPONSE.CONTENT🎂', response.content, HTTP_CHAT_URL])
    return data


global run, current_time_as_str
run = True
current_time_as_str = ''
def set_time():
    global run, current_time_as_str
    has_colon = True
    message = api_chat_get()
    chat_request_step_skip = 0
    while run:
        if chat_request_step_skip > CHAT_REQUEST_DURATION:
            message = api_chat_get(message)
            chat_request_step_skip = 0
        if message:
            if has_colon:
                current_time_as_str = time.strftime('%H:%M:%S') + f'\n{message}'
            else:
                current_time_as_str = time.strftime('%H %M %S') + f'\n{message}'
        else:
            if has_colon:
                current_time_as_str = time.strftime('%H:%M:%S')
            else:
                current_time_as_str = time.strftime('%H %M %S')
        has_colon = not has_colon
        time.sleep(1)
        chat_request_step_skip += 1

timer = Thread(target=set_time)
timer.start()

screenWidth = GetScreenWidth()
screenHeight = GetScreenHeight()

InitWindow(screenWidth, screenHeight, b"realtime 3d timer")

camera = ffi.new("struct Camera3D *", [[ 46.0, 44.0, 46.0 ], [ 0.0, 0.0, 0.0 ], [ 0.0, 45.0, 0.0 ], 100.0, CAMERA_ORTHOGRAPHIC])#CAMERA_PERSPECTIVE

mapPosition = [ -16.0, 0.0, -8.0 ]
texture = LoadTexture(b"cubicmap_atlas.png")

def generate_cubicmap_model(text = 'hello world !!!'):
    image_data = io.BytesIO()
    render(text, image_data)
    buf = image_data.getvalue()
    buf_size = len(buf)
    sys.stdout.write(f'\n⚠{buf_size}⚠ :: {buf}\n')
    image = LoadImageFromMemory(b'.png', buf, buf_size)

    cubicmap = LoadTextureFromImage(image)

    mesh = GenMeshCubicmap(image, [ 1.0, 1.0, 1.0 ])
    model = LoadModelFromMesh(mesh)

    model.materials[0].maps[MATERIAL_MAP_ALBEDO ].texture = texture

    UnloadImage(image)
    return cubicmap, model

cubicmap, model = generate_cubicmap_model('START TEXT')

SetTargetFPS(60)

last_time_as_str = current_time_as_str
movement = [0.0, 0.0, 0.0]
rotation = [0.0, 0.0, 0.0]

# Main game loop
while not WindowShouldClose(): # Detect window close button or ESC key

    if last_time_as_str != current_time_as_str:
        last_time_as_str = current_time_as_str
        UnloadTexture(cubicmap)
        UnloadModel(model)
        cubicmap, model = generate_cubicmap_model(last_time_as_str)

    #UpdateCamera(camera, CAMERA_THIRD_PERSON)#CAMERA_ORBITAL
    UpdateCameraPro(camera, movement, rotation, 0.0)

    BeginDrawing()

    ClearBackground(RAYWHITE)

    BeginMode3D(camera[0])

    DrawModel(model, mapPosition, 1.0, WHITE)

    EndMode3D()

    DrawTextureEx(cubicmap, [ screenWidth - cubicmap.width*4 - 20, 20 ], 0.0, 4.0, WHITE)
    DrawRectangleLines(screenWidth - cubicmap.width*4 - 20, 20, cubicmap.width*4, cubicmap.height*4, GREEN)

    DrawFPS(10, 10)

    EndDrawing()

run = False
timer.join()

UnloadTexture(cubicmap)
UnloadTexture(texture)
UnloadModel(model)

CloseWindow()
