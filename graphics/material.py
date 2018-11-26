import numpy


class Material:
    name = str
    ambient_color = numpy.array
    diffuse_color = numpy.array
    _specular_color = numpy.array
    transparency = float
    specular_power = float
    _illum = int
    map_kd = str

    def __init__(self):
        self.name = None
        self.ambient_color = numpy.array([0., 0., 0.])
        self.diffuse_color = numpy.array([0., 0., 0.])
        self._specular_color = numpy.array([0., 0., 0.])
        self.transparency = 1.0
        self.specular_power = 1.0
        self._illum = 2
        self.map_kd = None
        return

    @property
    def illum(self):
        return self._illum

    @illum.setter
    def illum(self, value):
        if value == 1:
            self._specular_color = numpy.array([0., 0., 0.])
        return

    @property
    def specular_color(self):
        return self._specular_color

    @specular_color.setter
    def specular_color(self, value):
        if self.illum == 1:
            self._specular_color = numpy.array([0., 0., 0.])
        else:
            self._specular_color = value
        return
