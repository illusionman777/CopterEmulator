from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt
from pyquaternion import Quaternion
from math import sin, cos, pi, acos
from CopterEmulator.graphics.constructor3d import Constructor3D
from CopterEmulator.graphics.calc_csm_vp_matrix import calc_csm_vp_matrix
from CopterEmulator.graphics.set_text_buffer import set_text_buffer
from CopterEmulator.graphics.obj_loader import OBJLoader
import CopterEmulator.physicalmodel as model
import os
import numpy
# import time
import CopterEmulator.extrafunctions as func
import sys
import png
import json
import OpenGL

OpenGL.ERROR_CHECKING = False
OpenGL.ARRAY_SIZE_CHECKING = False
OpenGL.ERROR_LOGGING = False
OpenGL.CONTEXT_CHECKING = False
OpenGL.FULL_LOGGING = False
OpenGL.USE_ACCELERATE = True
OpenGL.ERROR_ON_COPY = False
OpenGL.WARN_ON_FORMAT_UNAVAILABLE = False
from OpenGL.GL import *
from CopterEmulator.graphics.shader import load_shaders
import ctypes


class Copter3DWidget(QOpenGLWidget):
    __dir_path__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + \
                   os.path.sep + 'graphics' + os.path.sep
    __vertexshader_dir__ = __dir_path__ + 'shaders_vertex' + os.path.sep
    __fragmentshader_dir__ = __dir_path__ + 'shaders_fragment' + os.path.sep
    _rotate_camera = bool
    _start_mouse_x = int
    _start_mouse_y = int
    _stop_mouse_x = int
    _stop_mouse_y = int
    distance_to_camera = numpy.array
    _camera_q = Quaternion
    copter = model.Copter

    def __init__(self, *args):
        if args:
            super(QOpenGLWidget, self).__init__(args[0])
            self.copter = args[0].copter
            self.settings = args[0].settings
        else:
            super(QOpenGLWidget, self).__init__()
            self.copter = model.Copter()
        self.update_event = None
        self.state = self.settings.start_state
        gl_format = self.format()
        gl_format.setSamples(8)
        self.setFormat(gl_format)
        self.num_of_cascades = 6
        self._shadowmap_resolution = 4 * 1024

        self._rotate_camera = False
        self._default_camera_distance = numpy.array([0.0, 0.0, 0.6])
        self._default_dimensions = numpy.array([0.0, 0.0, 0.2866 + 0.2536])
        self._camera_q = Quaternion([cos(pi / 4), 0, sin(pi / 4), 0])
        self._camera_q = self._camera_q * Quaternion([cos(pi / 4), -sin(pi / 4), 0, 0])
        self._camera_q = self._camera_q * Quaternion([cos(pi / 8), 0, -sin(pi / 8), 0])

        self._light_power = 1.0
        self._light_color = numpy.array([1.0, 1.0, 251 / 255], dtype='float32')
        self.light_dir = numpy.array([-1.0, 0.0, 0.0], dtype='float')
        light_q_az = Quaternion([
            cos(151.233 / 180 * pi),
            0,
            0,
            -sin(151.233 / 180 * pi)
        ])
        light_q_height = Quaternion([
            cos(60.598 / 180 * pi),
            0,
            -sin(60.598 / 180 * pi),
            0
        ])
        light_q = light_q_az * light_q_height
        self.light_dir = light_q.rotation_matrix.dot(self.light_dir)
        self._g_specular_power = 5.0

        self._objects3d = []
        self._copter3d = []
        self._fuselage3d = None
        self._ground = None
        self._coord_start_point = None
        self._copter_start_point = None
        self._copter_end_point = None
        self._pointer = None
        self._default_pointer_scale = 1.0
        self._default_pointer_length = 0.2
        self._max_pointer_length = self._default_pointer_length
        self._min_pointer_length = 0.001
        self._copter_pos_matrix = numpy.identity(4)
        self._view = numpy.identity(4)
        self._projection = numpy.identity(4)
        self.vp_matrix = numpy.identity(4)
        rot_matrix = self._camera_q.rotation_matrix
        for i in range(3):
            for j in range(3):
                self._view[i, j] = rot_matrix[j, i]
        self._fov = 60
        self._aspect_ratio = 16.0 / 9.0
        self._default_z_near = 0.01
        self._default_z_far = 100.0
        self._camera_scale = 1.0
        self._define_vp_matrix(self._camera_scale)

        self.cascade_vp = numpy.ndarray([self.num_of_cascades], dtype=object)
        self._csm_texture = 0
        self._depth_program_id = 0
        self._cascade_matrix_id = 0
        self._csm_fbo = 0
        self._csm_start_elm_num = 0
        self._axis_ortho = func.ortho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
        self._axis_view = numpy.identity(4)
        self._axis_view[:3, :3] = self._view[:3, :3]
        self._axis_view[3, 2] = 0.0
        self._axis_vp = self._axis_view.dot(self._axis_ortho)

        self._shadow_noe = 0
        self._shadow_vertices = numpy.ndarray([0, 3], dtype='float32')
        self._shadow_normals = numpy.ndarray([0, 3], dtype='float32')
        self._shadow_indices = numpy.ndarray([0], dtype='uint32')

        self._noe = 0
        self._vertices = numpy.ndarray([0, 3], dtype='float32')
        self._normals = numpy.ndarray([0, 3], dtype='float32')
        self._indices = numpy.ndarray([0], dtype='uint32')

        self._start_elm_num = 0
        self._program_id = 0
        self._mvp_matrix_id = 0
        self._mv_matrix_id = 0
        self._v_matrix_id = 0
        self._m_matrix_id = 0
        self._light_mvp_id = 0
        self._shadowmap_id = 0
        self._diffuse_color_id = 0
        self._ambient_color_id = 0
        self._specular_color_id = 0
        self._specular_power_id = 0

        self._vertex_array_id = 0
        self._vertex_buffer = 0
        self._normals_buffer = 0
        self._element_buffer = 0
        self._shadow_vertex_buffer = 0
        self._shadow_elm_buffer = 0
        self._axis_vertex_buffer = 0
        self._axis_normals_buffer = 0
        self._axis_element_buffer = 0

        self._size_of_elm = sys.getsizeof(numpy.ndarray([1], dtype='uint32')) - \
                            sys.getsizeof(numpy.ndarray([0], dtype='uint32'))
        self._size_of_float = sys.getsizeof(numpy.ndarray([1], dtype='float32')) - \
                              sys.getsizeof(numpy.ndarray([0], dtype='float32'))

        font_file = open(self.__dir_path__ + 'obj_files' + os.sep + 'Font.json', 'r')
        self._font = json.load(font_file)
        font_file.close()
        num_of_chars = 360 + 22 * self.copter.num_of_engines + 12
        self._text_state_index = 100
        num_of_engines = self.copter.num_of_engines
        i = 9
        while num_of_engines > i:
            num_of_chars += num_of_engines - i
            i += 10 * i

        self._text_vertices = numpy.ndarray([num_of_chars * 4, 2], dtype='float32')
        self._text_uv = numpy.ndarray([num_of_chars * 4, 2], dtype='float32')
        self._text_indices = numpy.ndarray([num_of_chars * 6], dtype='uint32')
        self._text_ver_index = 0
        self._text_elm_index = 0

        self._text_program_id = 0
        self._text_vertex_buffer = 0
        self._text_uv_buffer = 0
        self._text_element_buffer = 0
        self._text_row_interval = 20
        return

    def initializeGL(self):
        # glClearColor(0.529, 0.808, 0.922, 0.0)
        glClearColor(64 / 255, 156 / 255, 255 / 255, 0.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_CULL_FACE)

        self._vertex_array_id = glGenVertexArrays(1)
        glBindVertexArray(self._vertex_array_id)

        self.load_objects3d()
        self._init_text_vbo()
        self._create_shadow_fbo()
        return

    def paintGL(self):
        # time_start = time.time()
        self.set_copter_state(self.state)
        self.vp_matrix = self._view.dot(self._projection)
        self.vp_matrix = self._copter_pos_matrix.dot(self.vp_matrix)
        calc_csm_vp_matrix(self)
        self._render_shadowmap()

        glViewport(0, 0, self.width(), self.height())

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._start_elm_num = 0
        glUseProgram(self._program_id)
        glUniformMatrix4fv(self._v_matrix_id, 1, GL_FALSE, self._view)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self._csm_texture)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_COMPARE_MODE, GL_COMPARE_R_TO_TEXTURE)
        glUniform1i(self._shadowmap_id, 0)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self._vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._normals_buffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._element_buffer)
        self._draw_obj3d_list(self._copter3d)
        self._draw_obj3d_list(self._objects3d)

        glViewport(0, 0, 128, 128)
        self._start_elm_num = 0
        mv_matrix = self._axis_view
        mvp_matrix = self._axis_vp
        cascade_mvp = numpy.ndarray([self.num_of_cascades, 4, 4], dtype='float32')
        for j in range(self.num_of_cascades):
            cascade_mvp[j] = self.cascade_vp[j]

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self._axis_vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._axis_normals_buffer)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._axis_element_buffer)

        glUniformMatrix4fv(self._mvp_matrix_id, 1, GL_FALSE, mvp_matrix)
        glUniformMatrix4fv(self._mv_matrix_id, 1, GL_FALSE, mv_matrix)
        glUniformMatrix4fv(self._m_matrix_id, 1, GL_FALSE, self._coord_start_point.model_matrix)
        glUniformMatrix4fv(
            self._light_mvp_id,
            self.num_of_cascades,
            GL_FALSE,
            cascade_mvp
        )
        mat_list = list(self._coord_start_point.mat_lib.values())
        for j in range(len(self._coord_start_point.material_noe)):
            if not self._coord_start_point.material_noe:
                continue
            material = mat_list[j]
            glUniform3f(self._diffuse_color_id, *material.diffuse_color)
            glUniform3f(self._ambient_color_id, *material.ambient_color)
            glUniform3f(self._specular_color_id, *material.specular_color)
            glUniform1f(self._specular_power_id, material.specular_power)
            if self._start_elm_num == 0:
                pointer = 0
            else:
                pointer = self._size_of_elm * self._start_elm_num
            glDrawElements(
                GL_TRIANGLES,
                self._coord_start_point.material_noe[j],
                GL_UNSIGNED_INT,
                ctypes.c_void_p(pointer)
            )
            self._start_elm_num += self._coord_start_point.material_noe[j]
        glViewport(0, self.height() - 600, 800, 600)
        self._render_text()
        if self.update_event:
            self.update_event.set()
        # print(time.time() - time_start)
        return

    def resizeGL(self, width, height):
        self._aspect_ratio = width / height
        self._define_vp_matrix(self._camera_scale)
        return

    def mouseMoveEvent(self, *args, **kwargs):
        if not self._rotate_camera:
            return
        mouse_event = args[0]
        self._stop_mouse_x = float(mouse_event.x())
        self._stop_mouse_y = float(mouse_event.y())
        z_vector = numpy.array([0., 0., 1.0])
        xy_vector = numpy.array(
            [self._stop_mouse_x - self._start_mouse_x,
             -self._stop_mouse_y + self._start_mouse_y,
             0]
        )
        xy_norm = numpy.linalg.norm(xy_vector)
        angle = xy_norm / min([self.width(), self.height()]) * 1.1 * pi
        xy_vector = xy_vector / xy_norm
        rot_vector = -numpy.cross(xy_vector, z_vector) * sin(angle)
        rot_quaternion = Quaternion(real=cos(angle), imaginary=rot_vector)
        rot_quaternion = rot_quaternion.normalised
        self._camera_q = rot_quaternion * self._camera_q
        rot_matrix = self._camera_q.rotation_matrix
        for i in range(3):
            for j in range(3):
                self._view[i, j] = rot_matrix[j, i]
                self._axis_view[i, j] = rot_matrix[j, i]
        self._axis_vp = self._axis_view.dot(self._axis_ortho)
        self._start_mouse_x = self._stop_mouse_x
        self._start_mouse_y = self._stop_mouse_y
        self.update()
        return

    def mousePressEvent(self, *args, **kwargs):
        mouse_event = args[0]
        if mouse_event.button() == 1:
            self._rotate_camera = True
            self._start_mouse_x = float(mouse_event.x())
            self._start_mouse_y = float(mouse_event.y())
            self.setCursor(Qt.ClosedHandCursor)
        return

    def mouseReleaseEvent(self, *args, **kwargs):
        mouse_event = args[0]
        if mouse_event.button() == 1:
            self._rotate_camera = False
            self.setCursor(Qt.ArrowCursor)
        return

    def showEvent(self, *args, **kwargs):
        self.update()
        return

    def hideEvent(self, *args, **kwargs):
        if self.update_event:
            self.update_event.set()
        return

    def cleanup_vbo(self):
        self._shadow_noe = 0
        self._shadow_vertices = numpy.ndarray([0, 3], dtype='float32')
        self._shadow_normals = numpy.ndarray([0, 3], dtype='float32')
        self._shadow_indices = numpy.ndarray([0], dtype='uint32')

        self._noe = 0
        self._vertices = numpy.ndarray([0, 3], dtype='float32')
        self._normals = numpy.ndarray([0, 3], dtype='float32')
        self._indices = numpy.ndarray([0], dtype='uint32')
        glDeleteBuffers(1, int(self._shadow_vertex_buffer))
        glDeleteBuffers(1, int(self._shadow_elm_buffer))
        glDeleteBuffers(1, int(self._vertex_buffer))
        glDeleteBuffers(1, int(self._normals_buffer))
        glDeleteBuffers(1, int(self._element_buffer))
        glDeleteBuffers(1, int(self._axis_vertex_buffer))
        glDeleteBuffers(1, int(self._axis_normals_buffer))
        glDeleteBuffers(1, int(self._axis_element_buffer))
        glDeleteProgram(int(self._program_id))
        return

    def cleanup_all(self):
        self.cleanup_vbo()
        glDeleteBuffers(1, int(self._text_vertex_buffer))
        glDeleteBuffers(1, int(self._text_uv_buffer))
        glDeleteBuffers(1, int(self._text_element_buffer))
        glDeleteProgram(int(self._text_program_id))
        glDeleteProgram(int(self._depth_program_id))
        glDeleteFramebuffers(1, int(self._csm_fbo))
        glDeleteTextures(self._csm_texture)
        glDeleteFramebuffers(1, self.defaultFramebufferObject())
        glDeleteVertexArrays(1, int(self._vertex_array_id))
        return

    def set_settings(self):
        self._ground.trans_matrix[3, 2] = self.settings.ground_level
        rot_q_start = Quaternion(self.settings.start_state.fuselage_state.rot_q)
        rot_matrix_start = rot_q_start.rotation_matrix
        rot_matrix_end = self.settings.dest_q.rotation_matrix
        for i in range(3):
            for j in range(3):
                self._copter_start_point.rotation_matrix[i, j] = rot_matrix_start[j, i]
                self._copter_end_point.rotation_matrix[i, j] = rot_matrix_end[j, i]
            self._copter_start_point.trans_matrix[3, i] = self.settings.start_state.fuselage_state.pos_v[i]
            self._copter_end_point.trans_matrix[3, i] = self.settings.dest_pos[i]
        self.set_copter_state(self.settings.start_state)
        return

    def set_copter_state(self, copter_state):
        fus_q = Quaternion(copter_state.fuselage_state.rot_q)
        fus_q_matrix = fus_q.rotation_matrix
        self._ground.trans_matrix[3, 0] = copter_state.fuselage_state.pos_v[0]
        self._ground.trans_matrix[3, 1] = copter_state.fuselage_state.pos_v[1]
        for i in range(3):
            for j in range(3):
                self._fuselage3d.rotation_matrix[i, j] = fus_q_matrix[j, i]
            self._fuselage3d.trans_matrix[3, i] = copter_state.fuselage_state.pos_v[i]
            self._copter_pos_matrix[3, i] = -self._fuselage3d.trans_matrix[3, i]

        for i in range(self.copter.num_of_engines):
            engine_quat = Quaternion([
                copter_state.engines_state[i].rot_q[0],
                0.0,
                0.0,
                copter_state.engines_state[i].rot_q[3]
            ])
            engine_quat = fus_q * \
                          self.copter.fus_engine_q[i] * \
                          engine_quat
            engine_q_matrix = engine_quat.rotation_matrix
            for j in range(3):
                for k in range(3):
                    self._copter3d[i].rotation_matrix[j, k] = engine_q_matrix[k, j]
                vector_fus_engine_mc = fus_q_matrix.dot(self.copter.vector_fus_engine_mc[i])
                self._copter3d[i].trans_matrix[3, j] = copter_state.fuselage_state.pos_v[j] + \
                                                       vector_fus_engine_mc[j]
        pointer_vector = self.settings.dest_pos - copter_state.fuselage_state.pos_v
        pointer_length = numpy.linalg.norm(pointer_vector) / 2
        pointer_scale = min(pointer_length / self._max_pointer_length, 1.0)
        pointer_scale = max(self._min_pointer_length / self._max_pointer_length, pointer_scale)
        self._pointer.scale_matrix = numpy.identity(4)
        self._pointer.scale_matrix[:3, :3] *= pointer_scale
        pointer_default_vector = numpy.array([1.0, 0.0, 0.0])
        pointer_normal_vector = numpy.cross(pointer_default_vector, pointer_vector)
        pointer_normal_norm = numpy.linalg.norm(pointer_normal_vector)
        pointer_norm = numpy.linalg.norm(pointer_vector)
        if pointer_normal_norm < 1e-6:
            pointer_normal_vector = numpy.array([0.0, 0.0, 1.0])
        else:
            pointer_normal_vector /= pointer_normal_norm
        if pointer_norm < 1e-6:
            pointer_vector = numpy.array([1.0, 0.0, 0.0])
        else:
            pointer_vector /= pointer_norm
        angle = acos(numpy.vdot(pointer_vector, pointer_default_vector)) / 2
        pointer_q = Quaternion(
            real=cos(angle),
            imaginary=sin(angle) * pointer_normal_vector
        )
        pointer_rot_matrix = pointer_q.rotation_matrix
        for i in range(3):
            for j in range(3):
                self._pointer.rotation_matrix[i, j] = pointer_rot_matrix[j, i]
            self._pointer.trans_matrix[3, i] = copter_state.fuselage_state.pos_v[i]
        # self.vp_matrix = self._view.dot(self._projection)
        # self.vp_matrix = self._copter_pos_matrix.dot(self.vp_matrix)
        x_start = 8
        y_start = 600 - 2 * self._text_row_interval
        self._text_ver_index = 4 * self._text_state_index
        self._text_elm_index = 6 * self._text_state_index
        set_text_buffer(self, '    t = %e' % copter_state.t, x_start, y_start)
        y_start -= 2 * self._text_row_interval
        set_text_buffer(self, '    x = {0:>13e}'.format(copter_state.fuselage_state.pos_v[0]), x_start, y_start)
        y_start -= self._text_row_interval
        set_text_buffer(self, '    y = {0:>13e}'.format(copter_state.fuselage_state.pos_v[1]), x_start, y_start)
        y_start -= self._text_row_interval
        set_text_buffer(self, '    z = {0:>13e}'.format(copter_state.fuselage_state.pos_v[2]), x_start, y_start)
        y_start -= 2 * self._text_row_interval
        set_text_buffer(self, '    x = {0:>13e}'.format(copter_state.fuselage_state.velocity_v[0]), x_start, y_start)
        y_start -= self._text_row_interval
        set_text_buffer(self, '    y = {0:>13e}'.format(copter_state.fuselage_state.velocity_v[1]), x_start, y_start)
        y_start -= self._text_row_interval
        set_text_buffer(self, '    z = {0:>13e}'.format(copter_state.fuselage_state.velocity_v[2]), x_start, y_start)
        y_start -= 2 * self._text_row_interval
        set_text_buffer(self, '    x = {0:>13e}'.format(copter_state.fuselage_state.acel_v[0]), x_start, y_start)
        y_start -= self._text_row_interval
        set_text_buffer(self, '    y = {0:>13e}'.format(copter_state.fuselage_state.acel_v[1]), x_start, y_start)
        y_start -= self._text_row_interval
        set_text_buffer(self, '    z = {0:>13e}'.format(copter_state.fuselage_state.acel_v[2]), x_start, y_start)
        y_start -= 2 * self._text_row_interval
        set_text_buffer(self, '    x = {0:>13e}'.format(copter_state.fuselage_state.angular_vel_v[0]), x_start, y_start)
        y_start -= self._text_row_interval
        set_text_buffer(self, '    y = {0:>13e}'.format(copter_state.fuselage_state.angular_vel_v[1]), x_start, y_start)
        y_start -= self._text_row_interval
        set_text_buffer(self, '    z = {0:>13e}'.format(copter_state.fuselage_state.angular_vel_v[2]), x_start, y_start)
        y_start -= 2 * self._text_row_interval
        for i in range(self.copter.num_of_engines):
            engine_load = copter_state.engines_state[i].current_pwm / self.copter.engines[i].max_pwm * 100
            set_text_buffer(self, '    Engine{0} = {1:>7.3f}%'.format(i + 1, engine_load), x_start, y_start)
            y_start -= self._text_row_interval
        return

    def _define_vp_matrix(self, scale):
        self.distance_to_camera = self._default_camera_distance + self._default_dimensions * (scale - 1)
        for i in range(3):
            self._view[3, i] = -self.distance_to_camera[i]
        self.z_near = self._default_z_near * scale
        self.z_far = self._default_z_far * scale
        self._projection = func.perspective(self._fov, self._aspect_ratio, self.z_near, self.z_far)
        # self.vp_matrix = self._view.dot(self._projection)
        # self.vp_matrix = self._copter_pos_matrix.dot(self.vp_matrix)

        self.cascade_border = numpy.zeros(self.num_of_cascades + 1, dtype='float')
        self.cascade_border[0] = self.z_near
        log_coef = 0.97
        min_distance = 0.001
        max_distance = 1.0
        clip_range = self.z_far - self.z_near
        min_z = self.z_near + min_distance * clip_range
        max_z = self.z_near + max_distance * clip_range

        z_range = max_z - min_z
        ratio = max_z / min_z
        for i in range(self.num_of_cascades):
            p = (i + 1) / self.num_of_cascades
            log = min_z * pow(ratio, p)
            uniform = min_z + z_range * p
            d = log_coef * (log - uniform) + uniform
            self.cascade_border[i + 1] = (d - self.z_near)
        return

    def load_objects3d(self):
        # start = time.time()
        self._objects3d = []
        self._copter3d = []
        copter = Constructor3D(self)
        copter.construct_copter()
        self._camera_scale = copter.copter_scale
        self._default_pointer_scale = copter.copter_scale
        self._max_pointer_length = self._default_pointer_length * copter.copter_scale
        self._min_pointer_length = 0.001 * copter.copter_scale
        self._fuselage3d = copter.fuselage_obj
        self._fuselage3d.scale_matrix = numpy.identity(4)
        self._define_vp_matrix(self._camera_scale)

        self._copter3d = copter.engine_obj
        self._copter3d.append(self._fuselage3d)
        for i in range(self.copter.num_of_engines):
            self._copter3d[i].scale_matrix = numpy.identity(4)

        self._ground = OBJLoader()
        self._ground.scale_matrix[:3, :3] *= copter.copter_scale
        self._ground.load(self.__dir_path__ + 'obj_files' + os.sep + 'Ground.obj')
        self._ground.scale_matrix = numpy.identity(4)
        self._objects3d.append(self._ground)

        self._coord_start_point = OBJLoader()
        self._coord_start_point.load(self.__dir_path__ + 'obj_files' + os.sep + 'OriginCoordinates.obj')
        self._objects3d.append(self._coord_start_point)

        self._copter_start_point = OBJLoader()
        self._copter_start_point.scale_matrix[:3, :3] *= copter.copter_scale
        self._copter_start_point.load(self.__dir_path__ + 'obj_files' + os.sep + 'Start_point.obj')
        self._copter_start_point.scale_matrix = numpy.identity(4)
        self._objects3d.append(self._copter_start_point)

        self._copter_end_point = OBJLoader()
        self._copter_end_point.scale_matrix[:3, :3] *= copter.copter_scale
        self._copter_end_point.load(self.__dir_path__ + 'obj_files' + os.sep + 'End_point.obj')
        self._copter_end_point.scale_matrix = numpy.identity(4)
        self._objects3d.append(self._copter_end_point)

        self._pointer = OBJLoader()
        self._pointer.scale_matrix[:3, :3] *= copter.copter_scale
        self._pointer.load(self.__dir_path__ + 'obj_files' + os.sep + 'Pointer.obj')
        self._pointer.scale_matrix = numpy.identity(4)
        self._objects3d.append(self._pointer)

        self.set_settings()

        self._create_vbo_array(self._copter3d)
        # self.shadow_noe = self.noe
        # self.shadow_vertices = self.vertices
        # self.shadow_indices = self.indices
        self._create_vbo_array(self._objects3d)
        self._shadow_noe = self._noe
        self._shadow_vertices = self._vertices
        self._shadow_indices = self._indices
        self._init_vbo()
        # print(time.time() - start)
        return

    def _init_vbo(self):
        vertex_shader_file = self.__vertexshader_dir__ + 'CSM.sdr'
        fragment_shader_file = self.__fragmentshader_dir__ + 'CSM.sdr'
        self._program_id = load_shaders(vertex_shader_file, fragment_shader_file)
        self._mvp_matrix_id = glGetUniformLocation(self._program_id, "mvpMatrix")
        self._mv_matrix_id = glGetUniformLocation(self._program_id, "mvMatrix")
        self._v_matrix_id = glGetUniformLocation(self._program_id, "vMatrix")
        self._m_matrix_id = glGetUniformLocation(self._program_id, "mMatrix")
        self._light_mvp_id = glGetUniformLocation(self._program_id, "lightMVP")
        self._shadowmap_id = glGetUniformLocation(self._program_id, "shadowTextureArray")
        self._diffuse_color_id = glGetUniformLocation(self._program_id, "materialDiffuseColor")
        self._ambient_color_id = glGetUniformLocation(self._program_id, "materialAmbientColor")
        self._specular_color_id = glGetUniformLocation(self._program_id, "materialSpecularColor")
        self._specular_power_id = glGetUniformLocation(self._program_id, "specularPower")
        light_dir_norm = self.light_dir / numpy.linalg.norm(self.light_dir)
        glUseProgram(self._program_id)
        glUniform3f(glGetUniformLocation(self._program_id, "lightColor"),
                    *self._light_color)
        glUniform3f(glGetUniformLocation(self._program_id, "lightDirection"),
                    *light_dir_norm)
        glUniform1f(glGetUniformLocation(self._program_id, "lightPower"),
                    self._light_power)
        glUniform1fv(
            glGetUniformLocation(self._program_id, "cascadedSplits"),
            self.num_of_cascades,
            self.cascade_border[1:]
        )
        self._vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._vertex_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            # sys.getsizeof(self._vertices),
            len(self._vertices) * 3 * self._size_of_elm,
            self._vertices,
            GL_STATIC_DRAW
        )
        self._normals_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._normals_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            # sys.getsizeof(self._normals),
            len(self._normals) * 3 * self._size_of_elm,
            self._normals,
            GL_STATIC_DRAW
        )
        self._element_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._element_buffer)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            # sys.getsizeof(self._indices),
            len(self._indices) * self._size_of_elm,
            self._indices,
            GL_STATIC_DRAW
        )
        self._shadow_vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._shadow_vertex_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            # sys.getsizeof(self._shadow_vertices),
            len(self._shadow_vertices) * 3 * self._size_of_elm,
            self._shadow_vertices,
            GL_STATIC_DRAW
        )
        self._shadow_elm_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._shadow_elm_buffer)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            # sys.getsizeof(self._shadow_indices),
            len(self._shadow_indices) * self._size_of_elm,
            self._shadow_indices,
            GL_STATIC_DRAW
        )
        self._axis_vertex_buffer = glGenBuffers(1)
        vertex_array = self._coord_start_point.vertices_indexed
        glBindBuffer(GL_ARRAY_BUFFER, self._axis_vertex_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            # sys.getsizeof(vertex_array),
            len(vertex_array) * 3 * self._size_of_elm,
            vertex_array,
            GL_STATIC_DRAW
        )
        self._axis_normals_buffer = glGenBuffers(1)
        normals_array = self._coord_start_point.normals_indexed
        glBindBuffer(GL_ARRAY_BUFFER, self._axis_normals_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            # sys.getsizeof(normals_array),
            len(normals_array) * 3 * self._size_of_elm,
            normals_array,
            GL_STATIC_DRAW
        )
        self._axis_element_buffer = glGenBuffers(1)
        elements_array = self._coord_start_point.indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._axis_element_buffer)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            # sys.getsizeof(elements_array),
            len(elements_array) * self._size_of_elm,
            elements_array,
            GL_STATIC_DRAW
        )
        return

    def _create_vbo_array(self, obj_list):
        for object_3d in obj_list:
            noe = object_3d.num_of_elements + self._noe
            nov = len(self._vertices) + len(object_3d.vertices_indexed)
            vertices = numpy.ndarray([nov, 3], dtype='float32')
            normals = numpy.ndarray([nov, 3], dtype='float32')
            indices = numpy.ndarray([noe], dtype='uint32')
            if not self._noe == 0:
                vertices[:len(self._vertices)] = self._vertices
                normals[:len(self._normals)] = self._normals
                indices[:self._noe] = self._indices
            vertices[len(self._vertices):] = object_3d.vertices_indexed
            normals[len(self._normals):] = object_3d.normals_indexed
            indices[self._noe:] = object_3d.indices + \
                                  len(self._vertices)
            self._noe = noe
            self._vertices = vertices
            self._normals = normals
            self._indices = indices
        return

    def _create_shadow_fbo(self):
        depth_vertex_shader = self.__vertexshader_dir__ + 'DepthRTT.sdr'
        depth_fragment_shader = self.__fragmentshader_dir__ + 'DepthRTT.sdr'
        self._depth_program_id = load_shaders(depth_vertex_shader, depth_fragment_shader)
        self._cascade_matrix_id = glGetUniformLocation(self._depth_program_id, "depthMVP")

        self._csm_fbo = glGenFramebuffers(1)
        self._csm_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self._csm_texture)
        glTexImage3D(
            GL_TEXTURE_2D_ARRAY,
            0,
            GL_DEPTH_COMPONENT16,
            self._shadowmap_resolution,
            self._shadowmap_resolution,
            self.num_of_cascades,
            0,
            GL_DEPTH_COMPONENT,
            GL_FLOAT,
            ctypes.c_void_p(0)
        )
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_COMPARE_MODE, GL_COMPARE_R_TO_TEXTURE)

        glBindFramebuffer(GL_FRAMEBUFFER, self._csm_fbo)
        glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, self._csm_texture, 0)

        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)

        if not glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE:
            raise SystemError("Can't create depth framebuffer")
        glBindFramebuffer(GL_FRAMEBUFFER, self.defaultFramebufferObject())
        return

    def _render_shadowmap(self):
        glUseProgram(self._depth_program_id)
        glBindFramebuffer(GL_FRAMEBUFFER, self._csm_fbo)
        glViewport(0, 0, self._shadowmap_resolution, self._shadowmap_resolution)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self._shadow_vertex_buffer)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._shadow_elm_buffer)

        for cascade_count in range(self.num_of_cascades):
            glFramebufferTextureLayer(
                GL_FRAMEBUFFER,
                GL_DEPTH_ATTACHMENT,
                self._csm_texture,
                0,
                cascade_count
            )
            glClear(GL_DEPTH_BUFFER_BIT)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_CULL_FACE)
            glEnable(GL_DEPTH_CLAMP)
            glCullFace(GL_FRONT)
            self._csm_start_elm_num = 0

            self._draw_shadowmap(self._copter3d, cascade_count)
            self._draw_shadowmap(self._objects3d, cascade_count)
            glDisable(GL_DEPTH_CLAMP)
        glBindFramebuffer(GL_FRAMEBUFFER, self.defaultFramebufferObject())

    def _draw_shadowmap(self, obj_list, cascade_count):
        if not obj_list:
            return
        for i in range(len(obj_list)):
            object3d = obj_list[i]
            pointer = self._size_of_elm * self._csm_start_elm_num
            cascade_mvp = object3d.model_matrix.dot(self.cascade_vp[cascade_count])
            glUniformMatrix4fv(self._cascade_matrix_id, 1, GL_FALSE, cascade_mvp)
            glDrawElements(
                GL_TRIANGLES,
                object3d.num_of_elements,
                GL_UNSIGNED_INT,
                ctypes.c_void_p(pointer)
            )
            self._csm_start_elm_num += object3d.num_of_elements
        return

    def _draw_obj3d_list(self, obj_list):
        if not obj_list:
            return
        for i in range(len(obj_list)):
            object3d = obj_list[i]
            mv_matrix = self._copter_pos_matrix.dot(self._view)
            mv_matrix = object3d.model_matrix.dot(mv_matrix)
            mvp_matrix = object3d.model_matrix.dot(self.vp_matrix)
            cascade_mvp = numpy.ndarray([self.num_of_cascades, 4, 4], dtype='float32')
            for j in range(self.num_of_cascades):
                cascade_mvp[j] = object3d.model_matrix.dot(self.cascade_vp[j])

            glUniformMatrix4fv(self._mvp_matrix_id, 1, GL_FALSE, mvp_matrix)
            glUniformMatrix4fv(self._mv_matrix_id, 1, GL_FALSE, mv_matrix)
            glUniformMatrix4fv(self._m_matrix_id, 1, GL_FALSE, object3d.model_matrix)
            glUniformMatrix4fv(
                self._light_mvp_id,
                self.num_of_cascades,
                GL_FALSE,
                cascade_mvp
            )
            j = 0
            for material in object3d.mat_lib.values():
                if not object3d.material_noe:
                    continue
                glUniform3f(self._diffuse_color_id, *material.diffuse_color)
                glUniform3f(self._ambient_color_id, *material.ambient_color)
                glUniform3f(self._specular_color_id, *material.specular_color)
                glUniform1f(self._specular_power_id, material.specular_power)
                if self._start_elm_num == 0:
                    pointer = 0
                else:
                    pointer = self._size_of_elm * self._start_elm_num
                glDrawElements(
                    GL_TRIANGLES,
                    object3d.material_noe[j],
                    GL_UNSIGNED_INT,
                    ctypes.c_void_p(pointer)
                )
                self._start_elm_num += object3d.material_noe[j]
                j += 1
        return

    def _init_text_vbo(self):
        font_texture = png.Reader(
            filename=self.__dir_path__ + 'obj_files' + os.sep + 'Font_texture.png'
        ).asRGBA()
        width = font_texture[0]
        height = font_texture[1]
        texture_data = list(font_texture[2])
        texture_data = numpy.array(texture_data, dtype='uint8')
        texture_data = numpy.flip(texture_data, axis=0)
        self._font_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._font_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D)
        vertex_shader_file = self.__vertexshader_dir__ + 'Text2D.sdr'
        fragment_shader_file = self.__fragmentshader_dir__ + 'Text2D.sdr'
        self._text_program_id = load_shaders(vertex_shader_file, fragment_shader_file)
        glUseProgram(self._text_program_id)
        self._font_texture_id = glGetUniformLocation(self._text_program_id, "fontTexture")
        x_start = 8
        y_start = 600 - self._text_row_interval
        self._text_ver_index = 0
        self._text_elm_index = 0
        set_text_buffer(self, 'Time, [s]:', x_start, y_start)
        y_start -= 2 * self._text_row_interval
        set_text_buffer(self, 'Position, [m]:', x_start, y_start)
        y_start -= 4 * self._text_row_interval
        set_text_buffer(self, 'Velocity, [m/s]:', x_start, y_start)
        y_start -= 4 * self._text_row_interval
        set_text_buffer(self, 'Acceleration, [m/s^2]:', x_start, y_start)
        y_start -= 4 * self._text_row_interval
        set_text_buffer(self, 'Angular velocity, [rad/s]:', x_start, y_start)
        y_start -= 4 * self._text_row_interval
        set_text_buffer(self, 'Engine load:', x_start, y_start)
        self._text_vertex_buffer = glGenBuffers(1)
        self._text_uv_buffer = glGenBuffers(1)
        self._text_element_buffer = glGenBuffers(1)
        return

    def _render_text(self):
        glBindBuffer(GL_ARRAY_BUFFER, self._text_vertex_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            # sys.getsizeof(self._text_vertices),
            len(self._text_vertices) * 2 * self._size_of_elm,
            self._text_vertices,
            GL_STATIC_DRAW
        )
        glBindBuffer(GL_ARRAY_BUFFER, self._text_uv_buffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            # sys.getsizeof(self._text_uv),
            len(self._text_uv) * 2 * self._size_of_elm,
            self._text_uv,
            GL_STATIC_DRAW
        )
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._text_element_buffer)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            # sys.getsizeof(self._text_indices),
            len(self._text_indices) * self._size_of_elm,
            self._text_indices,
            GL_STATIC_DRAW
        )
        glUseProgram(self._text_program_id)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self._font_texture)
        glUniform1i(self._font_texture_id, 0)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self._text_vertex_buffer)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self._text_uv_buffer)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._text_element_buffer)
        glDrawElements(
            GL_TRIANGLES,
            len(self._text_indices),
            GL_UNSIGNED_INT,
            ctypes.c_void_p(0)
        )
        glDisable(GL_BLEND)
        return
