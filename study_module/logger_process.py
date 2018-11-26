from logger import Logger


def logger_process(copter, settings, resieve_conn):
    logger = Logger(copter, settings)
    running = True
    while running:
        state = resieve_conn.recv()
        if state == "stop":
            running = False
            continue
        logger.copter_state = state
        logger.write_log()
    logger.compose_log_file()
    return
