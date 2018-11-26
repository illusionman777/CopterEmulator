

def stop_signal(server, stop_event):
    stop_event.wait()
    if server.simulation_running:
        try:
            server.graphics_widget.stop_simulation()
        except AttributeError:
            server.stop_simulation()
    return
