from .obj_loader import OBJLoader
from math import sqrt, fabs, acos, cos, sin
from pyquaternion import Quaternion
import numpy
import os


class Constructor3D:
    __obj_dir_path__ = os.path.dirname(os.path.realpath(__file__)) + \
                       os.path.sep + 'obj_files' + os.sep

    def __init__(self, widget):
        self.fuselage_obj = OBJLoader()
        self.engine_obj = []
        self.copter_scale = 1.0
        self._copter = widget.copter
        self._settings = widget.settings
        self._gl_widget = widget
        self._default_dimensions = 0.2866 + 0.2536
        self._default_blade_d = 0.2536
        self._default_fus_r = 0.1
        self._min_fus_r = 0.02
        self._blade_const = 0.02
        self._from_eng_to_blade_center = numpy.array([0.0, 0.0, -0.00575, 1.0])
        self._from_eng_to_tube = numpy.array([-0.030, 0.0, -0.016350, 1.0])
        self._z_min = -0.040992
        self._z_max = 0.0375
        return

    def construct_copter(self):
        scale_factor = numpy.ndarray([self._copter.num_of_engines])
        engine_matrices = numpy.ndarray([self._copter.num_of_engines], dtype=object)
        for i in range(self._copter.num_of_engines):
            if self._copter.engines[i].blade_diameter < 1e-6:
                scale_factor[i] = 1.0
            else:
                scale_factor[i] = self._copter.engines[i].blade_diameter / self._default_blade_d
            engine_matrix = numpy.identity(4)
            rot_matrix = self._copter.fus_engine_q[i].rotation_matrix
            for j in range(3):
                for k in range(3):
                    engine_matrix[j, k] = rot_matrix[k, j]
                engine_matrix[3, j] = self._copter.vector_fus_engine_mc[i][j]
            engine_matrices[i] = engine_matrix
        fuselage_scale_factor = numpy.max(scale_factor)

        fuselage_r = self._calculate_radius(scale_factor, fuselage_scale_factor, engine_matrices)
        fuselage_r = min(fuselage_r, self._default_fus_r * fuselage_scale_factor)

        self.copter_scale = self._calculate_dimensions(scale_factor, engine_matrices) / \
                            self._default_dimensions
        self.copter_scale = max(self.copter_scale, fuselage_r * 2 / self._default_dimensions)
        [tube_coordinates,
         tube_quaternions] = self._calculate_tube_geometry(scale_factor, fuselage_r, engine_matrices)
        self._load_objects3d(scale_factor, tube_coordinates, tube_quaternions,
                             fuselage_r, fuselage_scale_factor)
        return

    def _calculate_radius(self, scale_factor, fuselage_scale_factor, engine_matrices):
        z_lim_low = self._z_min * fuselage_scale_factor
        z_lim_high = self._z_max * fuselage_scale_factor
        r_temp = numpy.ndarray([self._copter.num_of_engines])
        for i in range(self._copter.num_of_engines):
            rot_matrix = self._copter.fus_engine_q[i].rotation_matrix
            blade_normal_vector = numpy.array([0.0, 0.0, 1.0])
            blade_normal_vector = rot_matrix.dot(blade_normal_vector)
            blade_normal_vector = blade_normal_vector / numpy.linalg.norm(blade_normal_vector)
            a = blade_normal_vector[0]
            b = blade_normal_vector[1]
            c = blade_normal_vector[2]
            d = self._default_blade_d * scale_factor[i]
            eng_blade_center = self._from_eng_to_blade_center * scale_factor[i]
            eng_blade_center[3] = 1.0
            eng_blade_center = eng_blade_center.dot(engine_matrices[i])
            x0 = eng_blade_center[0]
            y0 = eng_blade_center[1]
            z0 = eng_blade_center[2]
            z_max = (a * a + b * b) * d * d / 4
            z_min = -sqrt(z_max) + z0
            z_max = sqrt(z_max) + z0
            if z_max < z_lim_low or z_min > z_lim_high:
                r_temp[i] = self._default_fus_r * fuselage_scale_factor
                continue
            z_min = max(z_min, z_lim_low)
            z_max = min(z_max, z_lim_high)

            if not fabs(c) < 1e-6:
                z_check = -a * x0 - b * y0
                z_check /= c
                if d * d / 4 - x0 * x0 - y0 * y0 - z_check * z_check > 1e-6 and \
                        z_lim_low < z_check < z_lim_high:
                    r_temp[i] = self._default_fus_r * fuselage_scale_factor
                    continue
            r_temp[i] = self._find_min(z_min, z_max, a, b, c, x0, y0, z0, d)
            if r_temp[i] < 1.6 * self._min_fus_r * fuselage_scale_factor:
                r_temp[i] = self._default_fus_r * fuselage_scale_factor
            else:
                r_temp[i] -= 1.6 * self._min_fus_r * fuselage_scale_factor
        return numpy.min(r_temp)

    def _find_min(self, z_min, z_max, a, b, c, x0, y0, z0, d):
        if fabs(a) < 1e-6 and fabs(b) < 1e-6:
            lambda_coef = sqrt(d * d / 4 / (x0 * x0 + y0 * y0))
            x = x0 * (1 - lambda_coef)
            y = y0 * (1 - lambda_coef)
            result = sqrt(x * x + y * y)
            return result
        if fabs(a) < 1e-6:
            f = self._min_func_zero_a.__call__
        else:
            f = self._min_func.__call__
        diff = z_max - z_min
        eps = diff / 1e6
        diff_step = diff / 1e6
        z_left = z_min
        z_right = z_max
        z_cur = (z_min + z_max) / 2
        z_w = z_cur
        z_v = z_cur
        f_cur = f(z_cur, a, b, c, x0, y0, z0, d)
        f_w = f_cur
        f_v = f_cur
        df_cur = (f(z_cur + diff_step, a, b, c, x0, y0, z0, d) -
                  f(z_cur - diff_step, a, b, c, x0, y0, z0, d)) / 2 / diff_step
        df_w = df_cur
        df_v = df_cur

        counter = 0
        u1 = 0
        u2 = 0
        search = True
        z_res = 0
        while search:
            u1_flag = False
            u2_flag = False
            if not fabs(z_cur - z_w) < 1e-6 and not fabs(df_cur - df_w) < 1e-6:
                u1 = z_w - df_w * (z_w - z_cur) / (df_w - df_cur)
                if z_left + eps <= u1 <= z_right - eps and fabs(u1 - z_cur) < diff / 2:
                    u1_flag = True
            if not fabs(z_cur - z_v) < 1e-6 and not fabs(df_cur - df_v) < 1e-6:
                u2 = z_v - df_v * (z_v - z_cur) / (df_v - df_cur)
                if z_left + eps <= u2 <= z_right - eps and fabs(u2 - z_cur) < diff / 2:
                    u2_flag = True
            if u1_flag or u2_flag:
                z_u = u1 * (u1_flag and not u2_flag) + u2 * (not u1_flag and u2_flag) + \
                      u1 * (u1_flag and u2_flag) * (fabs(u1 - z_cur) <= fabs(u2 - z_cur)) + \
                      u2 * (u1_flag and u2_flag) * (fabs(u1 - z_cur) > fabs(u2 - z_cur))
            else:
                if df_cur > 0:
                    z_u = (z_left + z_cur) / 2
                else:
                    z_u = (z_cur + z_right) / 2
            if fabs(z_u - z_cur) < eps or counter > 1000:
                z_res = z_u * (fabs(z_u) > 1e-10) + \
                        (z_cur + numpy.sign(z_u - z_cur) * eps) * (fabs(z_u) < 1e-10)
                search = False
            diff = fabs(z_cur - z_u)
            f_u = f(z_u, a, b, c, x0, y0, z0, d)
            df_u = (f(z_u + diff_step, a, b, c, x0, y0, z0, d) -
                    f(z_u - diff_step, a, b, c, x0, y0, z0, d)) / 2 / diff_step
            if f_u <= f_cur:
                if z_u >= z_cur:
                    z_left = z_cur
                else:
                    z_right = z_cur
                z_v = z_w
                z_w = z_cur
                z_cur = z_u
                f_v = f_w
                f_cur = f_u
                df_v = df_w
                df_w = df_cur
                df_cur = df_u
            else:
                if z_u >= z_cur:
                    z_right = z_u
                else:
                    z_left = z_u
                if f_u <= f_w or fabs(z_w - z_cur) < 1e-10:
                    z_v = z_w
                    z_w = z_u
                    f_v = f_w
                    f_w = f_u
                    df_v = df_w
                    df_w = df_u
                else:
                    if f_u <= f_v or \
                            fabs(z_v - z_cur) < 1e-10 or \
                            fabs(z_w - z_w) < 1e-10:
                        z_v = z_u
                        f_v = f_u
                        df_v = df_u
            counter += 1
        result = f(z_res, a, b, c, x0, y0, z0, d)
        return result

    @staticmethod
    def _min_func(z_cur, a, b, c, x0, y0, z0, d):
        lambda_coef = sqrt((a * a + b * b) * d * d / 4 - (z_cur - z0) * (z_cur - z0))
        y1 = y0 + (-b * c * (z_cur - z0) + a * lambda_coef) / (a * a + b * b)
        y2 = y0 + (-b * c * (z_cur - z0) - a * lambda_coef) / (a * a + b * b)
        x1 = x0 + b / a * (b * c * (z_cur - z0) - a * lambda_coef) / (a * a + b * b) - c / a * (z_cur - z0)
        x2 = x0 + b / a * (b * c * (z_cur - z0) + a * lambda_coef) / (a * a + b * b) - c / a * (z_cur - z0)
        y_check = (a * b * x0 + b * b * y0 - b * c * (z_cur - z0)) / (a * a + b * b)
        if y1 < y2:
            x_min = x1
            y_min = y1
            x_max = x2
            y_max = y2
        else:
            x_min = x2
            y_min = y2
            x_max = x1
            y_max = y1
        if y_min <= y_check <= y_max:
            x = (a * a * x0 + a * b * y0 - a * c * (z_cur - z0)) / (a * a + b * b)
            y = y_check
        elif y_max <= y_check:
            x = x_max
            y = y_max
        else:
            x = x_min
            y = y_min
        result = sqrt(x * x + y * y)
        return result

    @staticmethod
    def _min_func_zero_a(z_cur, a, b, c, x0, y0, z0, d):
        if fabs(a) > 1e-6:
            raise ValueError("Coefficient 'a' must be 0 to use this function")
        lambda_coef = sqrt(d * d / 4 - (z_cur - z0) * (z_cur - z0) * (1 + c * c / b / b))
        y = y0 - c / b * (z_cur - z0)
        x1 = x0 + lambda_coef
        x2 = x0 - lambda_coef
        x_check = 0.0
        if x2 <= x_check <= x1:
            x = x_check
        elif x1 <= x_check:
            x = x1
        else:
            x = x2
        result = sqrt(x * x + y * y)
        return result

    def _calculate_dimensions(self, scale_factor, engine_matrices):
        x_max = numpy.ndarray([self._copter.num_of_engines])
        x_min = numpy.ndarray([self._copter.num_of_engines])
        y_max = numpy.ndarray([self._copter.num_of_engines])
        y_min = numpy.ndarray([self._copter.num_of_engines])
        for i in range(self._copter.num_of_engines):
            rot_matrix = self._copter.fus_engine_q[i].rotation_matrix
            blade_normal_vector = numpy.array([0.0, 0.0, 1.0])
            blade_normal_vector = rot_matrix.dot(blade_normal_vector)
            blade_normal_vector = blade_normal_vector / numpy.linalg.norm(blade_normal_vector)
            a = blade_normal_vector[0]
            b = blade_normal_vector[1]
            c = blade_normal_vector[2]
            d = self._default_blade_d * scale_factor[i]
            eng_blade_center = self._from_eng_to_blade_center * scale_factor[i]
            eng_blade_center[3] = 1.0
            eng_blade_center = eng_blade_center.dot(engine_matrices[i])
            x0 = eng_blade_center[0]
            y0 = eng_blade_center[1]
            x_max[i] = sqrt((b * b + c * c) * d * d / 4)
            x_min[i] = -x_max[i] + x0
            x_max[i] = x_max[i] + x0
            y_max[i] = sqrt((a * a + c * c) * d * d / 4)
            y_min[i] = -y_max[i] + y0
            y_max[i] = y_max[i] + y0
        x_dimensions = numpy.max(x_max) - numpy.min(x_min)
        y_dimensions = numpy.max(y_max) - numpy.min(y_min)
        result = max(x_dimensions, y_dimensions)
        return result

    def _calculate_tube_geometry(self, scale_factor, fuselage_r, engine_matrices):
        tube_coordinates = numpy.ndarray([self._copter.num_of_engines, 3], dtype=object)
        tube_quaternions = numpy.ndarray([self._copter.num_of_engines, 3], dtype=object)
        main_vector = numpy.array([1.0, 0, 0])
        for i in range(self._copter.num_of_engines):
            rot_matrix = self._copter.fus_engine_q[i].rotation_matrix
            blade_normal_vector = numpy.array([0.0, 0.0, 1.0])
            blade_normal_vector = rot_matrix.dot(blade_normal_vector)
            blade_normal_vector = blade_normal_vector / numpy.linalg.norm(blade_normal_vector)
            tube_coordinates[i, 0] = numpy.ndarray([3])
            tube_coordinates[i, 0][0] = self._copter.vector_fus_engine_mc[i][0]
            tube_coordinates[i, 0][1] = self._copter.vector_fus_engine_mc[i][1]
            tube_coordinates[i, 0][2] = 0.0
            if not numpy.linalg.norm(tube_coordinates[i, 0]) < 1e-6:
                tube_coordinates[i, 0] = tube_coordinates[i, 0] / numpy.linalg.norm(tube_coordinates[i, 0]) * \
                                         (fuselage_r + self._min_fus_r * scale_factor[i])
            else:
                tube_coordinates[i, 0][0] = fuselage_r + self._min_fus_r * scale_factor[i]
            tube_coordinates[i, 1] = numpy.ndarray([3])
            from_eng_to_tube = self._from_eng_to_tube * scale_factor[i]
            from_eng_to_tube[3] = 1.0
            rot_vector = numpy.cross(
                main_vector,
                tube_coordinates[i, 0] / numpy.linalg.norm(tube_coordinates[i, 0])
            )
            if numpy.linalg.norm(rot_vector) > 1e-6:
                rot_vector /= numpy.linalg.norm(rot_vector)
            else:
                rot_vector = numpy.array([0.0, 0.0, 1.0])
            angle = acos(numpy.vdot(tube_coordinates[i, 0], main_vector) /
                         numpy.linalg.norm(tube_coordinates[i, 0])) / 2
            from_eng_to_tube_quat = Quaternion(
                real=cos(angle),
                imaginary=rot_vector * sin(angle)
            )
            from_eng_to_tube[:3] = from_eng_to_tube_quat.rotation_matrix.dot(from_eng_to_tube[:3])
            from_eng_to_tube = from_eng_to_tube.dot(engine_matrices[i])
            tube_coordinates[i, 2] = from_eng_to_tube[:3]
            eng_blade_center = self._from_eng_to_blade_center * scale_factor[i]
            eng_blade_center[3] = 1.0
            eng_blade_center = eng_blade_center.dot(engine_matrices[i])
            tube_vector = tube_coordinates[i, 2] - tube_coordinates[i, 0]
            blade_center_vector = eng_blade_center[:3] - tube_coordinates[i, 0]
            normal_vector = numpy.cross(tube_vector, blade_center_vector)
            blade_vector = numpy.cross(blade_normal_vector, normal_vector)
            blade_vector = blade_vector / numpy.linalg.norm(blade_vector)
            numerator_vector = numpy.cross(blade_center_vector, tube_vector)
            numerator_check_vector = numpy.cross(blade_center_vector, blade_vector)
            denom_vector = numpy.cross(tube_vector, blade_vector)
            if numpy.linalg.norm(denom_vector) < 1e-10:
                tube_coordinates[i, 1][0] = tube_coordinates[i, 0][0] + tube_vector[0] / 2
                tube_coordinates[i, 1][1] = tube_coordinates[i, 0][1] + tube_vector[1] / 2
                tube_coordinates[i, 1][2] = tube_coordinates[i, 0][2] + tube_vector[2] / 2
            else:
                for j in range(3):
                    if fabs(denom_vector[j]) > 1e-10:
                        lambda_coef = numerator_vector[j] / denom_vector[j]
                        lambda_check = numerator_check_vector[j] / denom_vector[j]
                        break
                if fabs(lambda_coef) >= (self._default_blade_d / 2 + self._blade_const) * scale_factor[i] or \
                        lambda_check > 1.0:
                    tube_coordinates[i, 1][0] = tube_coordinates[i, 0][0] + tube_vector[0] / 2
                    tube_coordinates[i, 1][1] = tube_coordinates[i, 0][1] + tube_vector[1] / 2
                    tube_coordinates[i, 1][2] = tube_coordinates[i, 0][2] + tube_vector[2] / 2
                else:
                    lambda_coef = numpy.sign(lambda_coef) * \
                                  (self._default_blade_d / 2 + self._blade_const) * \
                                  scale_factor[i]
                    tube_coordinates[i, 1][0] = eng_blade_center[0] + lambda_coef * blade_vector[0]
                    tube_coordinates[i, 1][1] = eng_blade_center[1] + lambda_coef * blade_vector[1]
                    tube_coordinates[i, 1][2] = eng_blade_center[2] + lambda_coef * blade_vector[2]

            tube_vectors = numpy.ndarray([3], dtype=object)
            tube_vectors[0] = tube_coordinates[i, 0] / numpy.linalg.norm(tube_coordinates[i, 0])
            tube_vectors[1] = tube_coordinates[i, 1] - tube_coordinates[i, 0]
            tube_vectors[1] /= numpy.linalg.norm(tube_vectors[1])
            tube_vectors[2] = tube_coordinates[i, 2] - tube_coordinates[i, 1]
            tube_vectors[2] /= numpy.linalg.norm(tube_vectors[2])
            for j in range(3):
                rot_vector = numpy.cross(main_vector, tube_vectors[j])
                if numpy.linalg.norm(rot_vector) > 1e-6:
                    rot_vector /= numpy.linalg.norm(rot_vector)
                else:
                    rot_vector = numpy.array([0.0, 0.0, 1.0])
                angle = acos(numpy.vdot(main_vector, tube_vectors[j])) / 2
                tube_quaternions[i, j] = Quaternion(
                    real=cos(angle),
                    imaginary=rot_vector * sin(angle)
                )
        return [tube_coordinates, tube_quaternions]

    def _load_objects3d(self, scale_factor, tube_coordinates,
                        tube_quaternions, fuselage_r, fuselage_scale_factor):
        fuselage_parts = []
        body = OBJLoader()
        body.scale_matrix *= fuselage_r / self._default_fus_r
        body.scale_matrix[2, 2] = fuselage_scale_factor
        body.scale_matrix[3, 3] = 1.0
        body.load(self.__obj_dir_path__ + 'Fuselage.obj')
        fuselage_parts.append(body)
        for i in range(self._copter.num_of_engines):
            tube_in_body = OBJLoader()
            rot_matrix = tube_quaternions[i, 0].rotation_matrix

            for j in range(3):
                for k in range(3):
                    tube_in_body.rotation_matrix[j, k] = rot_matrix[k, j]

            tube_connector01 = OBJLoader()
            tube_connector01.scale_matrix *= scale_factor[i]
            tube_connector01.scale_matrix[3, 3] = 1.0
            tube_middle = OBJLoader()
            rot_matrix = tube_quaternions[i, 1].rotation_matrix

            for j in range(3):
                for k in range(3):
                    tube_middle.rotation_matrix[j, k] = rot_matrix[k, j]
                tube_middle.trans_matrix[3, j] = tube_coordinates[i, 0][j]
                tube_connector01.trans_matrix[3, j] = tube_coordinates[i, 0][j]

            tube_connector12 = OBJLoader()
            tube_connector12.scale_matrix *= scale_factor[i]
            tube_connector12.scale_matrix[3, 3] = 1.0
            tube_at_engine = OBJLoader()
            rot_matrix = tube_quaternions[i, 2].rotation_matrix

            for j in range(3):
                for k in range(3):
                    tube_at_engine.rotation_matrix[j, k] = rot_matrix[k, j]
                tube_at_engine.trans_matrix[3, j] = tube_coordinates[i, 1][j]
                tube_connector12.trans_matrix[3, j] = tube_coordinates[i, 1][j]

            tube_in_body.scale_matrix[0, 0] = numpy.linalg.norm(tube_coordinates[i, 0])
            tube_middle.scale_matrix[0, 0] = numpy.linalg.norm(tube_coordinates[i, 1] - tube_coordinates[i, 0])
            tube_at_engine.scale_matrix[0, 0] = numpy.linalg.norm(tube_coordinates[i, 2] - tube_coordinates[i, 1])
            for j in range(1, 3):
                tube_in_body.scale_matrix[j, j] = scale_factor[i]
                tube_middle.scale_matrix[j, j] = scale_factor[i]
                tube_at_engine.scale_matrix[j, j] = scale_factor[i]

            engine_holder = OBJLoader()
            engine_holder.scale_matrix *= scale_factor[i]
            engine_holder.scale_matrix[3, 3] = 1.0
            engine_holder_q = self._copter.fus_engine_q[i] * tube_quaternions[i, 0]
            rot_matrix = engine_holder_q.rotation_matrix
            for j in range(3):
                for k in range(3):
                    engine_holder.rotation_matrix[j, k] = rot_matrix[k, j]
                engine_holder.trans_matrix[3, j] = self._copter.vector_fus_engine_mc[i][j]

            tube_in_body.load(self.__obj_dir_path__ + 'Tube.obj')
            tube_connector01.load(self.__obj_dir_path__ + 'Tube_connector.obj')
            tube_middle.load(self.__obj_dir_path__ + 'Tube.obj')
            tube_connector12.load(self.__obj_dir_path__ + 'Tube_connector.obj')
            tube_at_engine.load(self.__obj_dir_path__ + 'Tube.obj')
            engine_holder.load(self.__obj_dir_path__ + 'Engine_holder.obj')

            fuselage_parts.append(tube_in_body)
            fuselage_parts.append(tube_connector01)
            fuselage_parts.append(tube_middle)
            fuselage_parts.append(tube_connector12)
            fuselage_parts.append(tube_at_engine)
            fuselage_parts.append(engine_holder)

            engine = OBJLoader()
            rot_matrix = self._copter.fus_engine_q[i].rotation_matrix
            for j in range(3):
                engine.scale_matrix[j, j] = scale_factor[i]
                for k in range(3):
                    engine.rotation_matrix[j, k] = rot_matrix[k, j]
            if self._copter.engines[i].blade_dir == 'counterclockwise' and \
                    self._copter.vector_fus_engine_mc[i][0] > 0:
                engine.load(self.__obj_dir_path__ + 'Engine_front_cc.obj')
            elif self._copter.engines[i].blade_dir == 'counterclockwise':
                engine.load(self.__obj_dir_path__ + 'Engine_back_cc.obj')
            elif self._copter.engines[i].blade_dir == 'clockwise' and \
                    self._copter.vector_fus_engine_mc[i][0] > 0:
                engine.load(self.__obj_dir_path__ + 'Engine_front_c.obj')
            else:
                engine.load(self.__obj_dir_path__ + 'Engine_back_c.obj')
            self.engine_obj.append(engine)
        self.fuselage_obj = OBJLoader()
        self.fuselage_obj.vertices_indexed = numpy.ndarray([0, 3], dtype='float32')
        self.fuselage_obj.normals_indexed = numpy.ndarray([0, 3], dtype='float32')
        self.fuselage_obj.texcoords_indexed = numpy.ndarray([0, 2], dtype='float32')
        self.fuselage_obj.indices = numpy.ndarray([0], dtype='uint32')
        for part in fuselage_parts:
            num_of_elements = part.num_of_elements + self.fuselage_obj.num_of_elements
            fuselage_nov = len(self.fuselage_obj.vertices_indexed)
            part_nov = len(part.vertices_indexed)
            num_of_vertices = fuselage_nov + part_nov
            vertices = numpy.ndarray([num_of_vertices, 3], dtype='float32')
            normals = numpy.ndarray([num_of_vertices, 3], dtype='float32')
            texcoords = numpy.ndarray([num_of_vertices, 2], dtype='float32')
            indices = numpy.ndarray([num_of_elements], dtype='uint32')
            vertices[:fuselage_nov] = self.fuselage_obj.vertices_indexed
            vertices[fuselage_nov:] = part.vertices_indexed
            normals[:fuselage_nov] = self.fuselage_obj.normals_indexed
            normals[fuselage_nov:] = part.normals_indexed
            texcoords[:fuselage_nov] = self.fuselage_obj.texcoords_indexed
            texcoords[fuselage_nov:] = part.texcoords_indexed
            indices[:self.fuselage_obj.num_of_elements] = self.fuselage_obj.indices
            part_index_counter = 0
            for i in range(len(part.mat_lib.keys())):
                material = list(part.mat_lib.keys())[i]
                part_end_counter = part_index_counter + part.material_noe[i]
                fus_noe_sum = sum(self.fuselage_obj.material_noe)
                if self.fuselage_obj.mat_lib.get(material) and \
                        not len(self.fuselage_obj.material_noe) == 0:
                    fus_index_counter = 0
                    for j in range(len(self.fuselage_obj.mat_lib.keys())):
                        fus_mid_counter = fus_index_counter + part.material_noe[i]
                        fus_end_counter = fus_noe_sum + part.material_noe[i]
                        if material == list(self.fuselage_obj.mat_lib.keys())[j]:
                            indices[fus_mid_counter:fus_end_counter] = indices[fus_index_counter:fus_noe_sum]
                            indices[
                                fus_index_counter:fus_mid_counter
                            ] = part.indices[part_index_counter:part_end_counter] + fuselage_nov
                            self.fuselage_obj.material_noe[j] += part.material_noe[i]
                            break
                        fus_index_counter += self.fuselage_obj.material_noe[j]
                else:
                    fus_end_counter = fus_noe_sum + part.material_noe[i]
                    indices[
                        fus_noe_sum:fus_end_counter
                    ] = part.indices[part_index_counter:part_end_counter] + fuselage_nov
                    self.fuselage_obj.material_noe.append(part.material_noe[i])
                    self.fuselage_obj.mat_lib.update({material: part.mat_lib[material]})
                part_index_counter = part_end_counter
            self.fuselage_obj.num_of_elements = num_of_elements
            self.fuselage_obj.vertices_indexed = vertices
            self.fuselage_obj.normals_indexed = normals
            self.fuselage_obj.texcoords_indexed = texcoords
            self.fuselage_obj.indices = indices
        return
