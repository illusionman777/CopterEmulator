import OpenGL.GL as GL


def load_shaders(vertex_file_path, fragment_file_path):
    vertex_shader_id = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    fragment_shader_id = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)

    vertex_shader_file = open(vertex_file_path, 'r')
    vertex_shader_code = vertex_shader_file.read()
    vertex_shader_file.close()

    fragment_shader_file = open(fragment_file_path, 'r')
    fragment_shader_code = fragment_shader_file.read()
    fragment_shader_file.close()

    GL.glShaderSource(vertex_shader_id, vertex_shader_code)
    GL.glCompileShader(vertex_shader_id)
    if not GL.glGetShaderiv(vertex_shader_id, GL.GL_COMPILE_STATUS):
        raise Exception('failed to compile shader "{0}":\n'
                        '{1}'.format(vertex_shader_id, GL.glGetShaderInfoLog(vertex_shader_id).decode()))

    GL.glShaderSource(fragment_shader_id, fragment_shader_code)
    GL.glCompileShader(fragment_shader_id)
    if not GL.glGetShaderiv(fragment_shader_id, GL.GL_COMPILE_STATUS):
        raise Exception('failed to compile shader "{0}":\n'
                        '{1}'.format(fragment_shader_id, GL.glGetShaderInfoLog(fragment_shader_id).decode()))

    program_id = GL.glCreateProgram()
    GL.glAttachShader(program_id, vertex_shader_id)
    GL.glAttachShader(program_id, fragment_shader_id)
    GL.glLinkProgram(program_id)
    if not GL.glGetProgramiv(program_id, GL.GL_LINK_STATUS):
        raise Exception('failed to link program:\n{}'.format(GL.glGetProgramInfoLog(program_id).decode()))

    GL.glDeleteShader(vertex_shader_id)
    GL.glDeleteShader(fragment_shader_id)
    return program_id
