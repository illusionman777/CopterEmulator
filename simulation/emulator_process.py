import time
import CopterEmulator.c_emulator as c_emulator


def emulator_process(copter, settings, receive_conn, controller_conn, logger_conn, graphics_conn,
                     stop_event, running_event, graphics_event, em_stopped_event, contr_stopped_event):
    emulator_c = c_emulator.cEmulator(copter, settings.dt)
    controller_period = 1 / settings.controller_freq
    state = receive_conn.recv()
    controller_conn.send(state.fuselage_state)
    controller_conn.send(state.t)
    # running_time = time.time()
    running = True
    while running:
        # if time.time() - running_time >= 10.0:
            # stop_event.set()
        if not running_event.is_set():
            running_event.wait()
        if stop_event.is_set():
            running = False
            continue
        input_pwm = receive_conn.recv()
        start_time = time.time()

        for i in range(len(state.engines_state)):
            state.engines_state[i].current_pwm = input_pwm[i]

        if settings.log_enabled:
            logger_conn.send(state)
        if settings.graphics_enabled and graphics_event.is_set():
            graphics_event.clear()
            graphics_conn.send(state)

        end_time = state.t + controller_period
        emulator_c.calculate_state(input_pwm, end_time, state)

        if settings.real_time_syncr:
            sleep_time = controller_period + start_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

        controller_conn.send(state.fuselage_state)
        controller_conn.send(state.t)
        if settings.ground_collision:
            if state.fuselage_state.pos_v[2] < settings.ground_level:
                stop_event.set()
    if settings.log_enabled:
        logger_conn.send(state)
    if settings.graphics_enabled:
        graphics_conn.send(state)
    em_stopped_event.set()
    contr_stopped_event.wait()
    controller_conn.close()
    logger_conn.close()
    graphics_conn.close()
    # print(state.t)
    return
