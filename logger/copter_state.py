from .fuselage_props import FuselageProps
from .engine_props import EngineProps
import numpy


class CopterState:
    def __init__(self, *args):
        self.t = 0.0
        self.fuselage_state = FuselageProps()
        self.engines_state = []
        if args:
            copter = args[0]
            for i in range(copter.num_of_engines):
                self.engines_state.append(EngineProps())
                self.engines_state[i].rotation_dir = copter.engines[i].rotation_dir
        return

    def to_list(self):
        self.fuselage_state.pos_v = self.fuselage_state.pos_v.tolist()
        self.fuselage_state.velocity_v = self.fuselage_state.velocity_v.tolist()
        self.fuselage_state.acel_v = self.fuselage_state.acel_v.tolist()
        self.fuselage_state.rot_q = self.fuselage_state.rot_q.tolist()
        self.fuselage_state.angular_vel_v = self.fuselage_state.angular_vel_v.tolist()
        self.fuselage_state.angular_acel_v = self.fuselage_state.angular_acel_v.tolist()
        for engine_state in self.engines_state:
            engine_state.pos_v = engine_state.pos_v.tolist()
            engine_state.velocity_v = engine_state.velocity_v.tolist()
            engine_state.acel_v = engine_state.acel_v.tolist()
            engine_state.rot_q = engine_state.rot_q.tolist()
            engine_state.angular_vel_v = engine_state.angular_vel_v.tolist()
            engine_state.angular_acel_v = engine_state.angular_acel_v.tolist()
        return

    def to_array(self):
        self.fuselage_state.pos_v = numpy.array(self.fuselage_state.pos_v)
        self.fuselage_state.velocity_v = numpy.array(self.fuselage_state.velocity_v)
        self.fuselage_state.acel_v = numpy.array(self.fuselage_state.acel_v)
        self.fuselage_state.rot_q = numpy.array(self.fuselage_state.rot_q)
        self.fuselage_state.angular_vel_v = numpy.array(self.fuselage_state.angular_vel_v)
        self.fuselage_state.angular_acel_v = numpy.array(self.fuselage_state.angular_acel_v)
        for engine_state in self.engines_state:
            engine_state.pos_v = numpy.array(engine_state.pos_v)
            engine_state.velocity_v = numpy.array(engine_state.velocity_v)
            engine_state.acel_v = numpy.array(engine_state.acel_v)
            engine_state.rot_q = numpy.array(engine_state.rot_q)
            engine_state.angular_vel_v = numpy.array(engine_state.angular_vel_v)
            engine_state.angular_acel_v = numpy.array(engine_state.angular_acel_v)
        return
