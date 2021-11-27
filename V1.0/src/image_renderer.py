from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import numpy as np
import glm
from PIL import Image
import gl_util

vertex = [
    -0.5, -0.5, 0.0,  # 頂点 0
    0.5,  -0.5, 0.0,  # 頂点 1
    0.5,  0.5,  0.0,  # 頂点 2
    -0.5, 0.5,  0.0]  # 頂点 3

face = [
    0, 1, 2,
    2, 3, 0]

tex_coords = [
    0.0, 1.0,  # 頂点 0
    1.0, 1.0,  # 頂点 1
    1.0, 0.0,  # 頂点 2
    0.0, 0.0]  # 頂点 3

vertex_shader_src="""
#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoord;
out vec2 outTexCoord;
uniform mat4 MVP;

void main(void) {
    outTexCoord = texCoord;
    gl_Position = MVP * vec4(position, 1.0);
}
""".strip()

fragment_shader_src="""
#version 330 core

in vec2 outTexCoord;
out vec4 outFragmentColor;
uniform sampler2D textureUnit;

void main(void) {
    outFragmentColor = texture(textureUnit, outTexCoord);
}
""".strip()

class image_renderer:
    def __init__(self, x, y, img_width, img_height, img_file, screen_width=640, screen_height=480, texture=None):
        self.img_file = img_file
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.img_width = img_width
        self.img_height = img_height
        self.program = None
        self.pos_vbo = None
        self.texture = texture
        self.tex_coord_vbo = None
        self.ibo = None
        self.img = None
        self.sampler_loc = -1
        self.init_data()
        
    def get_texture(self):
        return self.texture
        
    def init_data(self):
        # create texture
        if not self.texture:
            self.texture = gl_util.create_texture(self.img_file)
        ###self.img = Image.open(self.img_file)
        # create program and vbo and ibo
        self.program = gl_util.create_program(vertex_shader_src, fragment_shader_src)
        img_w, img_h = self.img_width, self.img_height
        x, y = 0.0, 0.0
        vertex[0:3]  = x,         y - img_h, 0.0  # 頂点 0
        vertex[3:6]  = x + img_w, y - img_h, 0.0  # 頂点 1
        vertex[6:9]  = x + img_w, y,         0.0  # 頂点 2
        vertex[9:12] = x,         y,         0.0  # 頂点 3
        self.pos_vbo = gl_util.create_vbo(vertex)
        self.tex_coord_vbo = gl_util.create_vbo(tex_coords)
        self.ibo = gl_util.create_ibo(face)
        self.sampler_loc = glGetUniformLocation(self.program, "textureUnit")
        # set uniform for projection
        M = glm.translate(glm.mat4(), glm.vec3(0.0, self.screen_height, 0.0))
        V = glm.lookAt(glm.vec3(0.0, 0.0, 1.0),
            glm.vec3(0.0, 0.0, 0.0),
            glm.vec3(0.0, 1.0, 0.0))
        P = glm.ortho(0.0, self.screen_width, 0.0, self.screen_height, 0.0, 2.0)
        MVP = P * V * M
        MVP = np.array(MVP, dtype=np.float32)
        MVP_loc = glGetUniformLocation(self.program, "MVP")
        glUseProgram(self.program)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
        glUseProgram(0)
        
    def convert_screen_to_global_coord(self, x, y, height):
        return (x, height - y)
        
    def get_pos(self):
        return (self.x, self.y)
        
    def set_pos(self, x, y):
        self.x = x
        self.y = y
        
    def draw(self):
        # set uniform for projection
        x, y = self.x, self.y
        gx, gy = self.convert_screen_to_global_coord(x, y, self.screen_height)
        M = glm.translate(glm.mat4(), glm.vec3(gx, gy, 0.0))
        V = glm.lookAt(glm.vec3(0.0, 0.0, 1.0),
            glm.vec3(0.0, 0.0, 0.0),
            glm.vec3(0.0, 1.0, 0.0))
        P = glm.ortho(0.0, self.screen_width, 0.0, self.screen_height, 0.0, 2.0)
        MVP = P * V * M
        MVP = np.array(MVP, dtype=np.float32)
        MVP_loc = glGetUniformLocation(self.program, "MVP")
        glUseProgram(self.program)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
        # draw image
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glUniform1i(self.sampler_loc, 0)
        # 頂点属性を設定
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.pos_vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, self.tex_coord_vbo)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        # 図形を描画
        num_vertex = len(face)
        glDrawElements(GL_TRIANGLES, num_vertex, GL_UNSIGNED_INT, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glUseProgram(0)
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
