import numpy
import os
import subprocess

from distutils.command.build import build
from distutils.command.build_ext import build_ext
from setuptools import setup, Extension
from setuptools.command.build_py import build_py

PACKAGE = 'tensorflow.contrib.lite.python'

TENSORFLOW_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
MAKEFILE_PATH = 'tensorflow/contrib/lite/tools/make/Makefile'

def make_args(target=''):
  args = ['make', 'SHELL=/bin/bash', '--quiet', '-C', TENSORFLOW_DIR, '-f', MAKEFILE_PATH]
  if target:
    args.append(target)
  return args

def make_output(target):
  return subprocess.check_output(make_args(target)).decode('utf-8').strip()

DOWNLOADS_DIR = make_output('downloadsdir')
print('DOWNLOADS_DIR=%s' % DOWNLOADS_DIR)

LIB_TFLITE = 'tensorflow-lite'
LIB_TFLITE_DIR = make_output('libdir')
print('LIB_TFLITE_DIR=%s' % LIB_TFLITE_DIR)

class CustomBuildExt(build_ext):
  def run(self):
    subprocess.call(make_args())
    super().run()

class CustomBuildPy(build_py):
  def run(self):
    self.run_command("build_ext")
    return super().run()

ext = Extension(name='%s._interpreter_wrapper' % PACKAGE,
  language='c++',
  sources=['interpreter_wrapper/interpreter_wrapper.i',
           'interpreter_wrapper/interpreter_wrapper.cc'],
  swig_opts=['-c++', '-I%s' % TENSORFLOW_DIR, '-module', 'interpreter_wrapper', '-outdir', '.'],
  extra_compile_args=['-std=c++11'],
  include_dirs=[TENSORFLOW_DIR,
                numpy.get_include(),
                os.path.join(DOWNLOADS_DIR, 'flatbuffers','include'),
                os.path.join(DOWNLOADS_DIR, 'absl')],
  libraries=[LIB_TFLITE],
  library_dirs=[LIB_TFLITE_DIR])

setup(
  name='tflite',
  version='1.0',
  py_modules=['%s.interpreter' % PACKAGE,
              '%s.interpreter_wrapper' % PACKAGE],
  ext_modules=[ext],
  package_dir={PACKAGE: '.'},
  cmdclass={
    'build_ext': CustomBuildExt,
    'build_py' : CustomBuildPy,
  }
)
