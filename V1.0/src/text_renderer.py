from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import numpy as np
import glm
from PIL import Image, ImageDraw, ImageFont
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

class text_renderer:
    def __init__(self, text, font_size=24, text_color=(255, 255, 255, 255), bk_color=(0, 0, 0, 0), width=640, height=480):
        self.text = text
        self.x = 0.0
        self.y = 0.0
        self.width = width
        self.height = height
        self.font = ImageFont.truetype("msgothic.ttc", font_size, encoding="utf-8")
        self.text_color = text_color
        self.bk_color = bk_color
        self.program = None
        self.pos_vbo = None
        self.tex_coord_vbo = None
        self.ibo = None
        self.img = None
        self.texture = None
        self.sampler_loc = -1
        self.init_data()
        
    def init_data(self):
        # create texture
        self.img = create_text_image(self.text, self.font, self.text_color, self.bk_color)
        self.texture = create_texture(self.img)
        # create program and vbo and ibo
        self.program = gl_util.create_program(vertex_shader_src, fragment_shader_src)
        img_w, img_h = self.img.size
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
        M = glm.translate(glm.mat4(), glm.vec3(0.0, self.height, 0.0))
        V = glm.lookAt(glm.vec3(0.0, 0.0, 1.0),
            glm.vec3(0.0, 0.0, 0.0),
            glm.vec3(0.0, 1.0, 0.0))
        P = glm.ortho(0.0, self.width, 0.0, self.height, 0.0, 2.0)
        MVP = P * V * M
        MVP = np.array(MVP, dtype=np.float32)
        MVP_loc = glGetUniformLocation(self.program, "MVP")
        glUseProgram(self.program)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
        glUseProgram(0)
        
    def set_text(self, text):
        self.text = text
        new_img = create_text_image(self.text, self.font, self.text_color, self.bk_color)
        new_width, new_height = new_img.size
        width, height = self.img.size
        self.img = new_img
        if new_width == width and new_height == height:
            glBindTexture(GL_TEXTURE_2D, self.texture)
            textureData = self.img.tobytes()
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, new_width, new_height, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            glDeleteTextures(1, [self.texture])
            self.texture = create_texture(self.img)
            # テクスチャを貼り付ける板のサイズを更新
            img_w, img_h = new_img.size
            x, y = 0.0, 0.0
            vertex[0:3]  = x,         y - img_h, 0.0  # 頂点 0
            vertex[3:6]  = x + img_w, y - img_h, 0.0  # 頂点 1
            vertex[6:9]  = x + img_w, y,         0.0  # 頂点 2
            vertex[9:12] = x,         y,         0.0  # 頂点 3
            pos = np.array(vertex, dtype=np.float32)
            glBindBuffer(GL_ARRAY_BUFFER, self.pos_vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, pos.nbytes, pos)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
        
    def convert_screen_to_global_coord(self, x, y, height):
        return (x, height - y)
        
    def draw_text(self, x, y):
        # set uniform for projection
        gx, gy = self.convert_screen_to_global_coord(x, y, self.height)
        M = glm.translate(glm.mat4(), glm.vec3(gx, gy, 0.0))
        V = glm.lookAt(glm.vec3(0.0, 0.0, 1.0),
            glm.vec3(0.0, 0.0, 0.0),
            glm.vec3(0.0, 1.0, 0.0))
        P = glm.ortho(0.0, self.width, 0.0, self.height, 0.0, 2.0)
        MVP = P * V * M
        MVP = np.array(MVP, dtype=np.float32)
        MVP_loc = glGetUniformLocation(self.program, "MVP")
        glUseProgram(self.program)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
        # draw text
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

def create_text_image(text, font, text_color, bk_color):
    # create image
    img = Image.new("RGBA", (1024, 256), bk_color)
    draw = ImageDraw.Draw(img)
    # draw text
    width = 0
    height = 0
    for line in text.splitlines():
        draw.text((0, height), line, font=font, fill=text_color)
        w, h = draw.textsize(line, font)
        _, _, w, h = draw.textbbox((0, 0), line, font)
        width = max(w, width)
        height += h
    # trim extra margin of right and bottom
    return img.crop((0, 0, width, height))

def create_texture(img):
    width, height = img.size
    textureData = img.tobytes()
    # テクスチャを作成してバインド
    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glBindTexture(GL_TEXTURE_2D, texture)
    # WRAP_S は横方向にテクスチャをどのように延長するか
    # WRAP_T は縦方向にテクスチャをどのように延長するか
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # _MAG_FILTER は拡大時のフィルタの種類
    # _MIN_FILTER は縮小時のフィルタの種類
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    # データの転送
    format = GL_RGBA
    if img.mode == "RGB":
        format = GL_RGB
    glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, textureData)
    return texture
