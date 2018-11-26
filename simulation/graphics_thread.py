import time
import threading


def graphics_thread(widget_3d, plotter, settings, receive_conn, stop_event,
                    running_event, graphics_event, update_event, em_stopped_event):
    sleep_event = threading.Event()
    sleep_event.clear()
    fps_3d = 60
    fps_plot = 20
    frame_time_3d = 1 / fps_3d
    frame_time_plot = 1 / fps_plot
    frame_time = frame_time_plot
    running = True
    while running:
        if not running_event.is_set():
            running_event.wait()
        if stop_event.is_set():
            running = False
            continue
        state = receive_conn.recv()
        start_time = time.time()
        state.to_array()
        if settings.view3d_enabled:
            widget_3d.state = state
            if widget_3d.isVisible():
                widget_3d.update()
                update_event.wait()
                update_event.clear()
                frame_time = frame_time_3d
            else:
                frame_time = frame_time_plot
        plotter.copter_state = state
        plotter.plot()
        graphics_event.set()
        if settings.vert_syncr:
            sleep_time = frame_time - (time.time() - start_time)
            # print(sleep_time)
            if sleep_time > 0:
                sleep_event.wait(timeout=sleep_time)
                # time.sleep(sleep_time)
    em_stopped_event.wait()
    return
