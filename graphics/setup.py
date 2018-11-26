from distutils.core import setup
from Cython.Build import cythonize

setup(name='OBJ Loader',
      ext_modules=cythonize("obj_loader1.pyx"))
