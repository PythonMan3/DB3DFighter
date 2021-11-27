from OpenGL.GL import *
from OpenGL.GLU import *
import glm
import numpy as np
import gl_util
from PIL import Image

# キューブ
cube_sp = None
cube_vao = None
cube_map_texture = None
FRONT = "data/image/negz.jpg"
BACK = "data/image/posz.jpg"
TOP = "data/image/posy.jpg"
BOTTOM = "data/image/negy.jpg"
LEFT = "data/image/negx.jpg"
RIGHT = "data/image/posx.jpg"
# 床
floor_sp = None
floor_vao = None
floor_texture = None
FLOOR = "data/image/floor.jpg"
view_mat = glm.mat4()
proj_mat = glm.mat4()

class CStage:
    def __init__(self):
        pass
        
    def draw(self, world):
        draw(world)
        
cube_vertex_shader_src="""
#version 330 core

layout(location = 1) in vec3 vp;
uniform mat4 MVP;
out vec3 texcoords;

void main () {
	texcoords = vp;
	gl_Position = MVP * vec4(vp, 1.0);
}
""".strip()

cube_fragment_shader_src="""
#version 330 core

in vec3 texcoords;
uniform samplerCube cube_texture;
out vec4 frag_colour;

void main () {
	frag_colour = texture(cube_texture, texcoords);
}
""".strip()

floor_vertex_shader_src="""
#version 330 core

layout(location = 2) in vec3 pos;
layout(location = 3) in vec2 texCoord;
out vec2 outTexCoord;
uniform mat4 MVP;

void main () {
    outTexCoord = texCoord;
    gl_Position = MVP * vec4(pos, 1.0);
}
""".strip()

floor_fragment_shader_src="""
#version 330 core

in vec2 outTexCoord;
uniform sampler2D texture0;
out vec4 frag_color;

void main () {
    frag_color = texture(texture0, outTexCoord);
}
""".strip()

def set_view_matrix(view):
    global view_mat
    view_mat = view

def set_projection_matrix(proj):
    global proj_mat
    proj_mat = proj

def make_floor():
    size = 10.0
    points = [
        -size, 0.0, -size,  -size, 0.0, size,  size, 0.0, size,
        size, 0.0, size,  size, 0.0, -size,  -size, 0.0, -size
    ]
    tex_coords = [
        0.0, 0.0,  0.0, 1.0,  1.0, 1.0,
        1.0, 1.0,  1.0, 0.0,  0.0, 0.0
    ]
    vbo = gl_util.create_vbo(points)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glEnableVertexAttribArray(2)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    texCoord_vbo = gl_util.create_vbo(tex_coords)
    glEnableVertexAttribArray(3)
    glBindBuffer(GL_ARRAY_BUFFER, texCoord_vbo)
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 0, None)
    return vao

def make_big_cube():
    size = 30.0
    points = [
        -size, size, -size, -size, -size, -size, size, -size, -size,
        size, -size, -size, size, size, -size, -size, size, -size,

        -size, -size, size, -size, -size, -size, -size, size, -size,
        -size, size, -size, -size, size, size, -size, -size, size,

        size, -size, -size, size, -size, size, size, size, size,
        size, size, size, size, size, -size, size, -size, -size,

        -size, -size, size, -size, size, size, size, size, size,
        size, size, size, size, -size, size, -size, -size, size,

        -size, size, -size, size, size, -size, size, size, size,
        size, size, size, -size, size, size, -size, size, -size,

        -size, -size, -size, -size, -size, size, size, -size, -size,
        size, -size, -size, -size, -size, size, size, -size, size
    ]
    vbo = gl_util.create_vbo(points)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    return vao

def load_cube_map_side(texture, side_target, file_name):
    glBindTexture(GL_TEXTURE_CUBE_MAP, texture)

    img = Image.open(file_name)
    width, height = img.size
    image_data = img.tobytes()
    format = GL_RGBA
    if img.mode == "RGB":
        format = GL_RGB

    glTexImage2D( side_target, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, image_data )
    return True

def create_cube_map(front, back, top, bottom, left, right):
    #// generate a cube-map texture to hold all the sides
    glActiveTexture( GL_TEXTURE0 )
    tex_cube = glGenTextures(1)

    #// load each image and copy into a side of the cube-map texture
    load_cube_map_side( tex_cube, GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, front );
    load_cube_map_side( tex_cube, GL_TEXTURE_CUBE_MAP_POSITIVE_Z, back );
    load_cube_map_side( tex_cube, GL_TEXTURE_CUBE_MAP_POSITIVE_Y, top );
    load_cube_map_side( tex_cube, GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, bottom );
    load_cube_map_side( tex_cube, GL_TEXTURE_CUBE_MAP_NEGATIVE_X, left );
    load_cube_map_side( tex_cube, GL_TEXTURE_CUBE_MAP_POSITIVE_X, right );
    #// format cube map texture
    glTexParameteri( GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
    glTexParameteri( GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
    glTexParameteri( GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE );
    glTexParameteri( GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE );
    glTexParameteri( GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE );
    return tex_cube

def init():
    global cube_vao, cube_map_texture, cube_sp
    global floor_vao, floor_texture, floor_sp
    # キューブ
    cube_vao = make_big_cube()
    cube_map_texture = create_cube_map( FRONT, BACK, TOP, BOTTOM, LEFT, RIGHT )
    cube_sp = gl_util.create_program( cube_vertex_shader_src, cube_fragment_shader_src )
    # 床
    floor_vao = make_floor()
    floor_texture = gl_util.create_texture(FLOOR)
    floor_sp = gl_util.create_program(floor_vertex_shader_src, floor_fragment_shader_src)

def draw(world):
    # キューブ
    glDepthMask(GL_FALSE)
    glUseProgram(cube_sp)
    M = glm.translate(glm.mat4(), glm.vec3(0.0, 2.0, 0.0))
    V = view_mat
    P = proj_mat
    MVP = np.array(P * V * M, dtype=np.float32)
    MVP_loc = glGetUniformLocation(cube_sp, "MVP")
    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cube_map_texture)
    glBindVertexArray(cube_vao)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glDepthMask(GL_TRUE)
    # 床
    glEnable(GL_TEXTURE_2D)
    glUseProgram(floor_sp)
    glBindVertexArray(floor_vao)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, floor_texture)
    tex_loc = glGetUniformLocation(floor_sp, "texture0")
    glUniform1i(tex_loc, 1)
    M = world
    V = view_mat
    P = proj_mat
    MVP = np.array(P * V * M, dtype=np.float32)
    MVP_loc = glGetUniformLocation(floor_sp, "MVP")
    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glDisable(GL_TEXTURE_2D)
    glBindVertexArray(0)
    glUseProgram(0)
