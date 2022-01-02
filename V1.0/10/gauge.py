from OpenGL.GL import *
from OpenGL.GLU import *
import glm
import numpy as np
import gl_util

program = None
ibo4 = None
ibo5 = None
screen_height = 600

GAUGE_TIME = 30

face4 = [
    [0, 1, 2], [3, 2, 1],
    [4, 5, 6], [7, 6, 5],
    [8, 9, 10], [11, 10, 9],
    [12, 13, 14], [15, 14, 13]]
face5 = [
    [0, 1, 2], [3, 2, 1],
    [4, 5, 6], [7, 6, 5],
    [8, 9, 10], [11, 10, 9],
    [12, 13, 14], [15, 14, 13],
    [16, 17, 18], [19, 18, 17]]

class CGauge:
    def __init__(self, index, width, height):
        self.value = 0.0
        self.prev_value = 0.0
        self.vvalue = 0.0
        self.index = index
        self.wait = 0
        self.win_count = 0
        self.width = width
        self.height = height
        self.vertexs = []
        self.colors = []
        self.reset()
    def reset(self):
        self.value, self.prev_value = 0, 0
        self.vvalue = 1.0 / GAUGE_TIME
        self.wait = 0
    def damage(self, v):
        if self.value > 0 and self.vvalue <= 0:
            self.value -= v
            if self.value < 0: self.value = 0
            if self.value <= 1.0E-6: self.value = 0  # 誤差を考慮
            self.vvalue = (self.value - self.prev_value) / GAUGE_TIME
            self.wait = GAUGE_TIME
    def move(self):
        if self.wait > 0:
            self.wait -= 1
        else:
           if self.vvalue < 0:
               if self.prev_value > self.value:
                   self.prev_value += self.vvalue
               else:
                   self.prev_value = self.value
                   self.vvalue = 0
           else:
               if self.vvalue > 0:
                   if self.value < 1:
                       self.value += self.vvalue
                   else:
                       self.value = self.prev_value = 1
                       self.vvalue = 0
    def add_draw(self, x, y, dx, dy, color):
        vertex_arr = [
            [x, y, 0],
            [x+dx, y, 0],
            [x, y+dy, 0],
            [x+dx, y+dy, 0]]
        for i in range(len(vertex_arr)):
            v = vertex_arr[i]
            vertex_arr[i] = [v[0], screen_height - v[1], v[2]]
        self.vertexs.append(vertex_arr)
        color = (color[0]/255.0, color[1]/255.0, color[2]/255.0, color[3]/255.0)
        color_arr = [color, color, color, color]
        self.colors.append(color_arr)
    def draw(self):
        sw, sh = self.width, self.height
        x, y = sw * 0.44, sw * 0.04
        w, h = -sw * 0.4, sw * 0.02
        if self.index == 1:
            x = sw - x
            w =- w
        self.vertexs = []
        self.colors = []
        self.add_draw(x, y-h*0.05, w, h*0.05, (255, 255, 255, 100))
        self.add_draw(x, y+h, w, h*0.05, (255, 255, 255, 100))
        self.add_draw(x, y, w, h, (0, 0, 0, 150))
        if self.prev_value > self.value:
            self.add_draw(x+self.value*w, y, (self.prev_value-self.value)*w, h, (255, 0, 0, 150))
        self.add_draw(x, y, self.value*w, h, (0, 255, 0, 150))
        draw(self.vertexs, self.colors)
        
        #buf = "{} WINS".format(self.win_count)
        #CFont* f=Game->Font;
        #f->DrawText(buf, Index==0?x+w:x+w-f->GetTextW(buf), y-f->GetTextH()*1.1f, COL_WHITE, COL_BLACK);

vertex_shader_src="""
#version 400 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec4 diffuseColor;
out vec4 outDiffuseColor;
uniform mat4 MVP;

void main(void) {
    outDiffuseColor = diffuseColor;
    gl_Position = MVP * vec4(position, 1.0);
}
""".strip()

fragment_shader_src="""
#version 400 core

in vec4 outDiffuseColor;
out vec4 outFragmentColor;
uniform vec4 diffuseColor;

void main(void) {
    outFragmentColor = outDiffuseColor;
}
""".strip()

def init(width, height):
    global program, screen_height, ibo4, ibo5
    program = gl_util.create_program(vertex_shader_src, fragment_shader_src)
    ibo4 = gl_util.create_ibo(face4)
    ibo5 = gl_util.create_ibo(face5)
    # Projection
    P = glm.ortho(0.0, width, 0.0, height, 0.0, 2.0)
    MVP = np.array(P, dtype=np.float32)
    MVP_loc = glGetUniformLocation(program, "MVP")
    glUseProgram(program)
    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
    glUseProgram(0)
    screen_height = height

def move():
    pass

def draw(vertexs, colors):
    pos_vbo = gl_util.create_vbo(vertexs)
    color_vbo = gl_util.create_vbo(colors)
    glDisable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glUseProgram(program)
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, color_vbo)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
    if len(vertexs) == 4:
        ibo = ibo4
        num_vertex = 24
    else:
        ibo = ibo5
        num_vertex = 30
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    glDrawElements(GL_TRIANGLES, num_vertex, GL_UNSIGNED_INT, None)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glUseProgram(0)
    glEnable(GL_DEPTH_TEST)
