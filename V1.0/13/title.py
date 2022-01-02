from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import image_renderer
import music

button_pressed = [False] * 3

class GameTitle:
    def __init__(self, window, screen_width=640, screen_height=480, music=None):
        self.window = window
        width = 750.0
        height = 200.0
        x = (screen_width - width) / 2.0
        y = 100.0
        self.logo = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Title_Logo.PNG", screen_width, screen_height)
        width = 300.0
        height = 50.0
        x = (screen_width - width) / 2.0
        y = 400.0
        self.menu = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Title_Menu.PNG", screen_width, screen_height)
        # VSメニュー初期化
        width = 150.0
        height = 50.0
        x = (screen_width - width) / 2.0
        y = 400
        self.vs_HUMANvsCPU = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Title_Menu_HUMANvsCPU.PNG", screen_width, screen_height)
        self.vs_CPUvsCPU = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Title_Menu_CPUvsCPU.PNG", screen_width, screen_height)
        self.vs_QUIT = image_renderer.image_renderer(x, y, width, height, "../src/data/image/Title_Menu_QUIT.PNG", screen_width, screen_height)
        self.reset()
        self.music = music
        
    def reset(self):
        self.cpu_modes = [1, 3, 99]
        self.cpu_mode_index = -1
        self.cpu_mode = 0 # 1: 人間vsCPU, 3: CPUvsCPU
        self.is_finished = False
        self.is_quited = False
        
    def is_quit(self):
        return self.is_quited
        
    def is_finish(self):
        return self.is_finished
        
    def get_cpu_mode(self):
        return self.cpu_modes[self.cpu_mode_index]
        
    def move(self):
        ## Space Press
        space_pressed = glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if state.buttons[glfw.GAMEPAD_BUTTON_X] or \
                state.buttons[glfw.GAMEPAD_BUTTON_A] or \
                state.buttons[glfw.GAMEPAD_BUTTON_B]:
                space_pressed = True
        ## Space Release
        space_released = False
        joystick_button_released = False
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if not state.buttons[glfw.GAMEPAD_BUTTON_X] and \
                not state.buttons[glfw.GAMEPAD_BUTTON_A] and \
                not state.buttons[glfw.GAMEPAD_BUTTON_B]:
                joystick_button_released = True
        else:
            joystick_button_released = True
        keyboard_space_released = glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.RELEASE
        if joystick_button_released and keyboard_space_released:
            space_released = True
        ## Up Press
        up_pressed = glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if state.buttons[glfw.GAMEPAD_BUTTON_DPAD_UP]:
                up_pressed = True
        ## Up Release
        up_released = False
        joystic_up_released = False
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if not state.buttons[glfw.GAMEPAD_BUTTON_DPAD_UP]:
                joystic_up_released = True
        else:
            joystic_up_released = True
        if glfw.get_key(self.window, glfw.KEY_UP) == glfw.RELEASE and joystic_up_released:
            up_released = True
        ## Down Press
        down_pressed = glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if state.buttons[glfw.GAMEPAD_BUTTON_DPAD_DOWN]:
                down_pressed = True
        ## Down Release
        down_released = False
        joystic_down_released = False
        if glfw.joystick_is_gamepad(glfw.JOYSTICK_1):
            state = glfw.get_gamepad_state(glfw.JOYSTICK_1)
            if not state.buttons[glfw.GAMEPAD_BUTTON_DPAD_DOWN]:
                joystic_down_released = True
        else:
            joystic_down_released = True
        if glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.RELEASE and joystic_down_released:
            down_released = True
        # ボタン押下時の処理
        if space_pressed and not button_pressed[0]:
            button_pressed[0] = True
            if self.cpu_mode_index == -1:
                self.music.play_sound(music.SELECT_MENU)
                self.cpu_mode_index = 0
            else:
                if self.get_cpu_mode() == 99:
                    self.is_quited = True
                self.is_finished = True
                self.music.play_sound(music.SELECT_ITEM)
        elif space_released and button_pressed[0]:
            button_pressed[0] = False
        if up_pressed and not button_pressed[1]:
            button_pressed[1] = True
            if self.cpu_mode_index != -1:
                self.cpu_mode_index = (self.cpu_mode_index - 1) % len(self.cpu_modes)
                self.music.play_sound(music.CHANGE_MENU)
        elif up_released and button_pressed[1]:
            button_pressed[1] = False
        if down_pressed and not button_pressed[2]:
            button_pressed[2] = True
            if self.cpu_mode_index != -1:
                self.cpu_mode_index = (self.cpu_mode_index + 1) % len(self.cpu_modes)
                self.music.play_sound(music.CHANGE_MENU)
        elif down_released and button_pressed[2]:
            button_pressed[2] = False
        
    def draw(self, system_time):
        glClearColor(0.99, 0.99, 0.99, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.logo.draw()
        time = system_time % 1.0
        if self.cpu_mode_index == -1:
            if time >= 0.3:
                self.menu.draw()
        elif self.get_cpu_mode() == 1:
            self.vs_HUMANvsCPU.draw()
        elif self.get_cpu_mode() == 3:
            self.vs_CPUvsCPU.draw()
        elif self.get_cpu_mode() == 99:
            self.vs_QUIT.draw()

