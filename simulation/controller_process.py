import random
from pyquaternion import Quaternion
import numpy
import math


def controller_process(copter, settings, receive_conn, emulator_conn,
                       stop_event, running_event, em_stopped_event, contr_stopped_event):
    """ This variables contains all parameters, that controller can use:
            settings.dest_pos                    copter destination point (x, y, z), [m]
            settings.dest_q                      copter destination quaternion (w, x, y, z)
            t_cur                                current time, [s]
            fuselage_state.pos_v                 current copter position (x, y, z), [m]
            fuselage_state.velocity_v            current copter velocity (x, y, z), [m/s]
            fuselage_state.acel_v                current copter acceleration (x, y, z), [m/s^2]
            fuselage_state.rot_q                 current copter rotation quaternion (w, x, y, z)
            fuselage_state.angular_vel_v         current copter angular velocity (x, y, z), [rad/s]
            fuselage_state.angular_acel_v        current copter angular acceleration (x, y, z), [rad/s^2]

        Controller must return variable "pwm_current", which is a list of integers and contains
        pwm for every copter engine
        Minimum pwm value is 0, maximum pwm - copter.engines[i].max_pwm """

    # kp = 30.0
    # kd = 90.0
    kp = 200.0
    kd = 700.0
    kp_vert = 40.0
    kd_vert = 100.0
    pwm_current = list()
    pwm_force = list()
    state = receive_conn.recv()
    for engine_state in state.engines_state:
        pwm_current.append(engine_state.current_pwm)
        pwm_force.append(engine_state.current_pwm)
    emulator_conn.send(pwm_current)
    running = True
    while running:
        if not running_event.is_set():
            running_event.wait()
        if stop_event.is_set():
            running = False
            continue
        random.seed()
        fuselage_state = receive_conn.recv()
        t_cur = receive_conn.recv()

        # Controller function here

        quat_cur = Quaternion(fuselage_state.rot_q)
        quat_cur = quat_cur.normalised
        quat_relative = quat_cur.conjugate * settings.dest_q

        direction_vec = numpy.dot(quat_cur.rotation_matrix, numpy.array([0.0, 0.0, 1.0]))

        if direction_vec[2] > 0:
            #if numpy.sign(settings.dest_pos[2] - fuselage_state.pos_v[2]) == numpy.sign(fuselage_state.velocity_v[2])
            pid_controller = 392 + kp_vert * (settings.dest_pos[2] - fuselage_state.pos_v[2]) - \
                             kd_vert * fuselage_state.velocity_v[2]
        else:
            pid_controller = 392

        pwm_force[0] = pid_controller
        pwm_force[1] = pid_controller
        pwm_force[2] = pid_controller
        pwm_force[3] = pid_controller

        func_cur = (1 - abs(quat_relative[0]) + math.sqrt(1 - quat_relative[0] * quat_relative[0]))
        moment = numpy.array([
            quat_relative[1] * copter.engines[0].blade_coef_alpha * abs(copter.vector_fus_engine_mc[0][0]),
            quat_relative[2] * copter.engines[0].blade_coef_alpha * abs(copter.vector_fus_engine_mc[0][1]),
            quat_relative[3] * copter.engines[0].blade_coef_beta * copter.engines[0].blade_diameter
        ])
        moment_norm = numpy.linalg.norm(moment)
        if moment_norm > 1e-10:
            moment /= numpy.linalg.norm(moment)
        '''moment *= kp * func_cur + \
                  kd * (func_cur - func_prev)'''
        angular_vel = numpy.array(fuselage_state.angular_vel_v)
        ang_vel_sign = numpy.sign(
            -fuselage_state.angular_vel_v[0] * quat_relative[1] -
            fuselage_state.angular_vel_v[1] * quat_relative[2] -
            fuselage_state.angular_vel_v[2] * quat_relative[3]
        ) * numpy.sign(quat_relative[0])
        if ang_vel_sign < 0:
            pd_controller = kp * math.sqrt(func_cur / 2) - kd * numpy.linalg.norm(angular_vel) * numpy.linalg.norm(angular_vel)
        else:
            # pd_controller = kp * func_cur + kd * func_cur * func_cur * numpy.linalg.norm(angular_vel) / 4
            pd_controller = kp * math.sqrt(func_cur / 2)
        # print(pd_controller)
        moment *= pd_controller

        power_current = list()
        power_current.append(pwm_force[0] * pwm_force[0] / copter.engines[0].max_pwm / copter.engines[0].max_pwm)
        power_current.append(pwm_force[1] * pwm_force[1] / copter.engines[1].max_pwm / copter.engines[1].max_pwm)
        power_current.append(pwm_force[2] * pwm_force[2] / copter.engines[2].max_pwm / copter.engines[2].max_pwm)
        power_current.append(pwm_force[3] * pwm_force[3] / copter.engines[3].max_pwm / copter.engines[3].max_pwm)

        power_current[0] += numpy.sign(moment[0] - moment[1] - moment[2]) * \
                            (moment[0] - moment[1] - moment[2])**2 / (copter.engines[0].max_pwm**2)
        power_current[1] += numpy.sign(moment[0] + moment[1] + moment[2]) * \
                            (moment[0] + moment[1] + moment[2])**2 / (copter.engines[1].max_pwm**2)
        power_current[2] += numpy.sign(-moment[0] + moment[1] - moment[2]) * \
                            (-moment[0] + moment[1] - moment[2])**2 / (copter.engines[2].max_pwm**2)
        power_current[3] += numpy.sign(-moment[0] - moment[1] + moment[2]) * \
                            (-moment[0] - moment[1] + moment[2])**2 / (copter.engines[3].max_pwm**2)

        for i in range(len(pwm_current)):
            if power_current[i] > 1.0:
                power_current[i] = 1.0
            if power_current[i] < 0:
                power_current[i] = 0

        pwm_current[0] = round(math.sqrt(power_current[0]) * copter.engines[0].max_pwm)
        pwm_current[1] = round(math.sqrt(power_current[1]) * copter.engines[1].max_pwm)
        pwm_current[2] = round(math.sqrt(power_current[2]) * copter.engines[2].max_pwm)
        pwm_current[3] = round(math.sqrt(power_current[3]) * copter.engines[3].max_pwm)

        '''for i in range(len(pwm_current)):
            # pwm_current[i] = random.randint(0, copter.engines[i].max_pwm)
           
            if pwm_current[i] < copter.engines[i].max_pwm:
                pwm_current[i] = pwm_current[i]'''

        ###

        emulator_conn.send(pwm_current)
    contr_stopped_event.set()
    em_stopped_event.wait()
    emulator_conn.close()
    return
