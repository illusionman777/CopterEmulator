from .fuselage_props import FuselageProps


class EngineProps(FuselageProps):
    def __init__(self):
        super(EngineProps, self).__init__()
        self.current_pwm = 0
        self.current_pow = 0.
        self.rotation_dir = "counterclockwise"
        return
