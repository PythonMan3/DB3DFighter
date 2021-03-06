from OpenGL.GL import *
from OpenGL.GLU import *
import glfw
import glm
import numpy as np
from h5_reader import H5Reader
import gl_util
from trackball import Trackball
import fitview
import sys

tb = None
aspect_ratio = 1.0
reader = None
program = None
tex_loc = -1
has_tex_loc = -1
diffuse_color_loc = -1
file_name = 'DB_ALL_models.h5'
bone_matrices_locations = []
anim_time = 0.0
previous_seconds = 0.0
curr_anim_idx = 0
button_pressed = False

vertex_shader_src="""
#version 400 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 textureCoord;
layout(location = 3) in ivec4 bone_id;
layout(location = 4) in vec4 bone_weight;
out vec3 outPosition;
out vec3 outNormal;
out vec2 outTextureCoord;
uniform mat4 P, MV;
// a deformation matrix for each bone (max number of bones is 200)
uniform mat4 bone_matrices[200];

void main(void) {
    outTextureCoord = textureCoord;
    mat4 transform = bone_matrices[bone_id[0]] * bone_weight[0];
    transform     += bone_matrices[bone_id[1]] * bone_weight[1];
    transform     += bone_matrices[bone_id[2]] * bone_weight[2];
    transform     += bone_matrices[bone_id[3]] * bone_weight[3];
    vec4 pos = transform * vec4(position, 1.0);
    outPosition = (MV * pos).xyz;
    outNormal = normalize(MV * transform * vec4(normal, 0.0)).xyz;
    gl_Position = P * MV * pos;
}
""".strip()

fragment_shader_src="""
#version 400 core

in vec3 outPosition;
in vec3 outNormal;
in vec2 outTextureCoord;
out vec4 outFragmentColor;
uniform sampler2D texture0;
uniform int hasTexture;
uniform vec4 diffuseColor;
uniform mat4 MV;
uniform vec3 lightPosition;
uniform vec3 eyePosition;

void main(void) {
    vec3 lightVec = normalize(lightPosition - outPosition);
    vec3 eyeVec = normalize(eyePosition - outPosition);
    vec3 halfLE = normalize(lightVec + eyeVec);
    float diffuse  = max(dot(outNormal, lightVec), 0.0);
    float specular = pow(clamp(dot(outNormal, halfLE), 0.0, 1.0), 50.0);
    vec4 diffuseVec = vec4(vec3(diffuse), 1.0);    // diffuse
    vec4 specularVec = vec4(vec3(specular), 0.0);  // specular
    vec4 ambientVec = vec4(0.1, 0.1, 0.1, 0.0);    // ambient
    vec4 diffColor = diffuseColor;
    if (bool(hasTexture)) {
        diffColor = texture(texture0, outTextureCoord);
    }
    outFragmentColor = diffColor * diffuseVec + specularVec + diffColor * ambientVec;
}
""".strip()

def init(window, width, height):
    global reader, program, tex_loc, has_tex_loc, diffuse_color_loc, aspect_ratio, tb, bone_matrices_locations
    program = gl_util.create_program(vertex_shader_src, fragment_shader_src)
    tex_loc = glGetUniformLocation(program, "texture0")
    has_tex_loc = glGetUniformLocation(program, "hasTexture")
    diffuse_color_loc = glGetUniformLocation(program, "diffuseColor")
    aspect_ratio = width / height
    # reader
    reader = H5Reader(file_name)
    reader.read_mesh("goku-ssj")
    select_anim(0)
    # bone matrix
    glUseProgram(program)
    num_max_bone = 0
    for mat in reader.model.materials:
        num_max_bone = max(num_max_bone, len(mat.node_indexs))
    if num_max_bone == 0:
        raise RuntimeError('The max number of bones is 0.')
    elif num_max_bone > 200:
        raise RuntimeError('The max number of bones is over 200.')
    for i in range(num_max_bone):
        name = "bone_matrices[{}]".format(i)
        loc = glGetUniformLocation(program, name)
        bone_matrices_locations.append(loc)
        m = np.array(glm.mat4(), dtype=np.float32)
        glUniformMatrix4fv(loc, 1, GL_FALSE, m)
    # ???????????????????????????????????????BoundBox?????????
    ##reader.calc_animate_vertexs()
    # Projection
    center_xyz, radius = reader.model.bound_box.get_sphere()
    M = glm.translate(glm.mat4(), glm.vec3(-center_xyz[0], -center_xyz[1], -center_xyz[2]))
    diameter = radius * 2.0
    z_pos = diameter * 2.0
    eye_pos = [0.0, 0.0, z_pos]
    V = glm.lookAt(glm.vec3(eye_pos),
        glm.vec3(0.0, 0.0, 0.0),
        glm.vec3(0.0, 1.0, 0.0))
    P = fitview.fit_by_sphere(V * M, reader.model.bound_box, aspect_ratio)
    glUseProgram(program)
    P_loc = glGetUniformLocation(program, "P")
    glUniformMatrix4fv(P_loc, 1, GL_FALSE, P)
    glUseProgram(0)
    # ?????????????????????????????????
    tb = Trackball()
    tb.region(width, height)

def update(window, width, height):
    global button_pressed
    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_1) == glfw.PRESS and not tb.is_rotating():
        x, y = glfw.get_cursor_pos(window)
        tb.start(x, y)
    elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_1) == glfw.RELEASE:
        tb.stop()
    x, y = glfw.get_cursor_pos(window)
    tb.motion(x, y)
    # ?????????????????????????????????
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS and not button_pressed: # ???????????????????????????????????????
        next_anim_idx = (curr_anim_idx + 1) % len(reader.model.animations)
        select_anim(next_anim_idx)
        button_pressed = True
    elif glfw.get_key(window, glfw.KEY_SPACE) == glfw.RELEASE and button_pressed:
        button_pressed = False

def select_anim(anim_idx):
    global curr_anim_idx
    curr_anim_idx = anim_idx
    for idx, anim in enumerate(reader.model.animations):
        if idx == anim_idx:
            anim.weight = 1.0
            anim.time = 0.0
        else:
            anim.weight = 0.0

def draw():
    global anim_time, previous_seconds
    
    glClearColor(0, 0.8, 0.8, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    # calculate time
    current_seconds = glfw.get_time()
    elapsed_seconds = current_seconds - previous_seconds
    previous_seconds = current_seconds
    
    # update animation timer and loop
    curr_anim = reader.model.get_animation(curr_anim_idx)
    ticks_per_second = 1.0
    if curr_anim.ticks_per_second != 0.0:
        ticks_per_second = curr_anim.ticks_per_second
    #print(ticks_per_second)
    anim_time += elapsed_seconds * ticks_per_second
    anim_duration = curr_anim.duration
    if anim_time >= anim_duration:
        anim_time = anim_duration - anim_time
    #print(anim_time)
    
    # ModelView
    glUseProgram(program)
    center_xyz, radius = reader.model.bound_box.get_sphere()
    T = glm.translate(glm.mat4(), glm.vec3(-center_xyz[0], -center_xyz[1], -center_xyz[2]))
    mdl_rot = tb.get()
    R = glm.mat4(mdl_rot)  # ?????????????????????????????????????????????
    M = R * T
    diameter = radius * 2.0
    x_pos = diameter
    y_pos = diameter
    z_pos = diameter * 2.0
    eye_pos = [0.0, 0.0, z_pos]
    V = glm.lookAt(glm.vec3(eye_pos),
        glm.vec3(0.0, 0.0, 0.0),
        glm.vec3(0.0, 1.0, 0.0))
    MV = np.array(V * M, dtype=np.float32)
    MV_loc = glGetUniformLocation(program, "MV")
    glUniformMatrix4fv(MV_loc, 1, GL_FALSE, MV)
    # lightPosition
    light_pos = [x_pos, y_pos, z_pos]
    light_pos_arr = np.array(light_pos, dtype=np.float32)
    light_pos_loc = glGetUniformLocation(program, "lightPosition")
    glUniform3fv(light_pos_loc, 1, light_pos_arr)
    # eyePosition
    eye_pos_arr = np.array(eye_pos, dtype=np.float32)
    eye_pos_loc = glGetUniformLocation(program, "eyePosition")
    glUniform3fv(eye_pos_loc, 1, eye_pos_arr)
    # bone_matrices
    curr_anim.time = anim_time
    world = glm.mat4(1.0)
    reader.model.animate_node(world)
    # draw mesh
    for mat in reader.model.materials:
        glBindVertexArray(mat.vao)
        glEnableVertexAttribArray(0)
        if mat.has_normal:
            glEnableVertexAttribArray(1)
        if mat.has_uv:
            glEnableVertexAttribArray(2)
        if mat.vbo_bone_id:
            glEnableVertexAttribArray(3)
        if mat.vbo_bone_weight:
            glEnableVertexAttribArray(4)
        # texture
        has_texture = 0
        if mat.has_uv and mat.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, mat.texture)
            glUniform1i(tex_loc, 0)
            has_texture = 1
        glUniform1i(has_tex_loc, has_texture)
        glUniform4fv(diffuse_color_loc, 1, mat.diffuse_color)
        # update bone matricies
        num_bone = len(mat.node_indexs)
        skin_mat = reader.model.get_skinning_matrix(mat)
        glUniformMatrix4fv(bone_matrices_locations[0], num_bone, GL_FALSE, skin_mat)
        # draw call
        num_face_vertex = mat.num_face * 3
        glDrawElements(GL_TRIANGLES, num_face_vertex, mat.idx_type, None)
        if mat.has_normal:
            glDisableVertexAttribArray(1)
        if mat.has_uv:
            glDisableVertexAttribArray(2)
            glDisable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
        if mat.vbo_bone_id:
            glDisableVertexAttribArray(3)
        if mat.vbo_bone_weight:
            glDisableVertexAttribArray(4)
    glBindVertexArray(0)
    glDisable(GL_DEPTH_TEST)
    glUseProgram(0)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

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

    while not glfw.window_should_close(window):
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        update(window, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw()

        glfw.swap_buffers(window)

        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
