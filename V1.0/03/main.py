from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
from trackball import Trackball
import sys
import model
import versus

tb = None
gameVersus = None

def init(window, width, height):
    global tb, gameVersus
    # トラックボールの初期化
    tb = Trackball()
    tb.region(width, height)
    # ゲームオブジェクトの初期化
    gameVersus = versus.DB3DFighterVersus(window, width, height, False)
    gameVersus.init()

def update(window, width, height):
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_1) == glfw.PRESS and not tb.is_rotating():
        x, y = glfw.get_cursor_pos(window)
        tb.start(x, y)
    elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_1) == glfw.RELEASE:
        tb.stop()
    x, y = glfw.get_cursor_pos(window)
    tb.motion(x, y)
    # ゲームオブジェクト更新
    gameVersus.move()

def draw():
    glClearColor(0, 0.8, 0.8, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    # ゲームオブジェクト描画
    mdl_rot = tb.get()
    gameVersus.draw(mdl_rot)
    
    glDisable(GL_DEPTH_TEST)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
REFRESH_SEC = 1.0 / FPS
previous_seconds = 0.0
previous_seconds_ = 0.0
frame_count = 0

def update_fps(window):
    global previous_seconds, frame_count
    current_seconds = glfw.get_time()
    elapsed_seconds = current_seconds - previous_seconds
    if elapsed_seconds > 0.25:
        previous_seconds = current_seconds
        fps = frame_count / elapsed_seconds
        tmp= "PyOpenGL Sample: FPS: {:.2f}".format(fps)
        glfw.set_window_title (window, tmp)
        frame_count = 0
    frame_count += 1

def wait_for_refresh_timing():
    global previous_seconds_
    while True:
        current_seconds = glfw.get_time()
        elapsed_seconds = current_seconds - previous_seconds_
        if elapsed_seconds >= REFRESH_SEC:
            previous_seconds_ = current_seconds
            break

def main():
    if not glfw.init():
        return

    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "PyOpenGL Sample", None, None)
    if not window:
        glfw.terminate()
        print('Failed to create window')
        return

    glfw.make_context_current(window)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    init(window, SCREEN_WIDTH, SCREEN_HEIGHT)

    glClearColor(0, 0, 0, 1)
    while not glfw.window_should_close(window):
        update_fps(window)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        update(window, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw()

        glfw.swap_buffers(window)
        glfw.poll_events()
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, 1)
            
        # 60 FPSを保つ
        wait_for_refresh_timing()

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
