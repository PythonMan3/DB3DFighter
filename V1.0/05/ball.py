from OpenGL.GL import *
from OpenGL.GLU import *
import glm
import numpy as np
from h5_reader import H5Reader
import gl_util

program = None
diffuse_color_loc = -1
view_mat = glm.mat4()
proj_mat = glm.mat4()

class CBall:
    def __init__(self, model_file, model_name):
        self.model_file = model_file
        self.model_name = model_name
        self.model = None
        self.color = (0.0, 0.0 ,0.0)
        self.init()
        
    def init(self):
        reader = H5Reader(self.model_file)
        reader.read_mesh(self.model_name)
        self.model = reader.model
        
    def set_color(self, color):
        self.color = color
        
    def draw(self, world):
        draw(self.model, self.color, world)
        
vertex_shader_src="""
#version 330 core

layout(location = 0) in vec3 position;
uniform mat4 MVP;

void main(void) {
    gl_Position = MVP * vec4(position, 1.0);
}
""".strip()

fragment_shader_src="""
#version 330 core

out vec4 outFragmentColor;
uniform vec4 diffuseColor;

void main(void) {
    outFragmentColor = diffuseColor;
}
""".strip()

def set_view_matrix(view):
    global view_mat
    view_mat = view

def set_projection_matrix(proj):
    global proj_mat
    proj_mat = proj

def init():
    global program, diffuse_color_loc
    program = gl_util.create_program(vertex_shader_src, fragment_shader_src)
    diffuse_color_loc = glGetUniformLocation(program, "diffuseColor")

def draw(model, color, world):
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # MVP
    glUseProgram(program)
    M = world
    V = view_mat
    P = proj_mat
    MVP = np.array(P * V * M, dtype=np.float32)
    MVP_loc = glGetUniformLocation(program, "MVP")
    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, MVP)
    # draw mesh
    for mat in model.materials:
        glBindVertexArray(mat.vao)
        glEnableVertexAttribArray(0)
        diffuse_color = np.array(color, dtype=np.float32)
        glUniform4fv(diffuse_color_loc, 1, diffuse_color)
        # draw call
        num_face_vertex = mat.num_face * 3
        glDrawElements(GL_TRIANGLES, num_face_vertex, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)
    glUseProgram(0)
