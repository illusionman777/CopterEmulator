import random


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

    pwm_current = list()
    state = receive_conn.recv()
    for engine_state in state.engines_state:
        pwm_current.append(engine_state.current_pwm)
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

        for i in range(len(pwm_current)):
            # pwm_current[i] = random.randint(0, copter.engines[i].max_pwm)
            if pwm_current[i] < copter.engines[i].max_pwm:
                pwm_current[i] = pwm_current[i]

        ###

        emulator_conn.send(pwm_current)
    contr_stopped_event.set()
    em_stopped_event.wait()
    emulator_conn.close()
    return
