from OpenGL.GL import *
import glfw
from PIL import Image
import numpy as np
import glm
import io

def create_program(vertex_shader_src, fragment_shader_src):
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_src)
    glCompileShader(vertex_shader)
    result = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if not result:
        err_str = glGetShaderInfoLog(vertex_shader).decode('utf-8')
        raise RuntimeError(err_str)
        glDeleteShader(vertex_shader)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_src)
    glCompileShader(fragment_shader)
    result = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if not result:
        err_str = glGetShaderInfoLog(fragment_shader).decode('utf-8')
        raise RuntimeError(err_str)
        glDeleteShader(fragment_shader)

    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glDeleteShader(vertex_shader)
    glAttachShader(program, fragment_shader)
    glDeleteShader(fragment_shader)
    glLinkProgram(program)
    result = glGetProgramiv(program, GL_LINK_STATUS)
    if not result:
        err_str = glGetProgramInfoLog(program).decode('utf-8')
        raise RuntimeError(err_str)

    return program

def create_vbo(vertex, nbytes=0):
    buffer_nbytes = 0
    if isinstance(vertex, bytes):
        buffer_nbytes = nbytes
    elif isinstance(vertex, np.ndarray):
        buffer_nbytes = vertex.nbytes
    elif isinstance(vertex, (list, tuple)):
        vertex = np.array(vertex, dtype=np.float32)
        buffer_nbytes = vertex.nbytes
    else:
        raise ValueError("argument type is not matched.")
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, buffer_nbytes, vertex, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo

def create_ibo(vert_index, nbytes=0):
    buffer_nbytes = 0
    if isinstance(vert_index, bytes):
        buffer_nbytes = nbytes
    elif isinstance(vert_index, np.ndarray):
        buffer_nbytes = vert_index.nbytes
    elif isinstance(vert_index, (list, tuple)):
        vert_index = np.array(vert_index, dtype=np.uint32)
        buffer_nbytes = vert_index.nbytes
    else:
        raise ValueError("argument type is not matched.")
    ibo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, buffer_nbytes, vert_index, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    return ibo

def create_texture(image_file_path, nbytes=0):
    img = None
    if isinstance(image_file_path, str):
        img = Image.open(image_file_path)
    elif isinstance(image_file_path, bytes):
        buffer = image_file_path
        img_bin = io.BytesIO(buffer)
        img = Image.open(img_bin)
    else:
        raise ValueError("argument type is not matched.")
    width, height = img.size
    textureData = img.tobytes()
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
    format = GL_RGBA
    if img.mode == "RGB":
        format = GL_RGB
    glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, textureData)
    return texture
