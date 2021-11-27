from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import image_renderer
import music

button_pressed = [False] * 3

class GameTitle:
    def __init__(self, window, screen_width=640, screen_height=480, music=None, key=None):
        self.window = window
        width = 750.0
        height = 200.0
        x = (screen_width - width) / 2.0
        y = 100.0
        self.logo = image_renderer.image_renderer(x, y, width, height, "data/image/Title_Logo.PNG", screen_width, screen_height)
        width = 300.0
        height = 50.0
        x = (screen_width - width) / 2.0
        y = 400.0
        self.menu = image_renderer.image_renderer(x, y, width, height, "data/image/Title_Menu.PNG", screen_width, screen_height)
        # VSメニュー初期化
        width = 150.0
        height = 50.0
        x = (screen_width - width) / 2.0
        y = 400
        self.vs_HUMANvsCPU = image_renderer.image_renderer(x, y, width, height, "data/image/Title_Menu_HUMANvsCPU.PNG", screen_width, screen_height)
        self.vs_CPUvsCPU = image_renderer.image_renderer(x, y, width, height, "data/image/Title_Menu_CPUvsCPU.PNG", screen_width, screen_height)
        self.vs_QUIT = image_renderer.image_renderer(x, y, width, height, "data/image/Title_Menu_QUIT.PNG", screen_width, screen_height)
        self.reset()
        self.music = music
        self.key = key
        
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
        self.key.check_key()
        space_pressed = self.key.space or (self.key.button[0] or self.key.button[1] or self.key.button[2])
        space_released = not self.key.space and not self.key.button[0] and not self.key.button[1] and not self.key.button[2]
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
        if self.key.up and not button_pressed[1]:
            button_pressed[1] = True
            if self.cpu_mode_index != -1:
                self.cpu_mode_index = (self.cpu_mode_index - 1) % len(self.cpu_modes)
                self.music.play_sound(music.CHANGE_MENU)
        elif not self.key.up and button_pressed[1]:
            button_pressed[1] = False
        if self.key.down and not button_pressed[2]:
            button_pressed[2] = True
            if self.cpu_mode_index != -1:
                self.cpu_mode_index = (self.cpu_mode_index + 1) % len(self.cpu_modes)
                self.music.play_sound(music.CHANGE_MENU)
        elif not self.key.down and button_pressed[2]:
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

