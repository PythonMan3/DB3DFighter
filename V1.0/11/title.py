from OpenGL.GL import *
from OpenGL.GLU import *
import image_renderer

class GameTitle:
    def __init__(self, screen_width=640, screen_height=480):
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
        
    def draw(self, system_time):
        glClearColor(0.99, 0.99, 0.99, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.logo.draw()
        time = system_time % 1.0
        if time >= 0.3:
            self.menu.draw()
