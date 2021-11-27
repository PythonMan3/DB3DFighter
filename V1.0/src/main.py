from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import sys
import model
import versus

gameVersus = None
is_finish = False

def init(window, width, height):
    global gameVersus
    # ゲームオブジェクトの初期化
    gameVersus = versus.DB3DFighterVersus(window, width, height, True)
    gameVersus.init()

def update(window, width, height):
    global is_finish
    # ゲームオブジェクト更新
    gameVersus.move()
    if gameVersus.is_quit():
        is_finish = True

def draw():
    glClearColor(0, 0.8, 0.8, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    # ゲームオブジェクト描画
    gameVersus.draw()
    
    glDisable(GL_DEPTH_TEST)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
REFRESH_SEC = model.ANIM_TIME_STEP
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
        tmp= "DB 3D Fighter: FPS: {:.2f}".format(fps)
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

    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "DB 3D Fighter", None, None)
    if not window:
        glfw.terminate()
        print('Failed to create window')
        return

    glfw.make_context_current(window)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    init(window, SCREEN_WIDTH, SCREEN_HEIGHT)

    glClearColor(0, 0, 0, 1)
    while not glfw.window_should_close(window):
        update_fps(window)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        update(window, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw()
        if is_finish:
            break

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
