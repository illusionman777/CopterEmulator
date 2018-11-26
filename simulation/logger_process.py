from logger import Logger


def logger_process(copter, settings, receive_conn, stop_event, running_event, em_stopped_event):
    logger = Logger(copter, settings)
    running = True
    while running:
        if not running_event.is_set():
            running_event.wait()
        if stop_event.is_set():
            running = False
            continue
        state = receive_conn.recv()
        logger.copter_state = state
        logger.write_log()
    logger.compose_log_file()
    em_stopped_event.wait()
    return
