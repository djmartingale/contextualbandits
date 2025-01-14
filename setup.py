from setuptools import setup, Extension
from Cython.Distutils import build_ext
import numpy as np
from sys import platform
import sys, os, subprocess, warnings, re

class build_ext_subclass( build_ext ):
    def build_extensions(self):
        if self.compiler.compiler_type == 'msvc':
            for e in self.extensions:
                e.extra_compile_args += ['/O2', '/openmp']
        else:
            self.add_march_native()
            self.add_openmp_linkage() ### for c++ only

            for e in self.extensions:
                # e.extra_compile_args += ['-O3', '-march=native', '-fopenmp']
                # e.extra_link_args += ['-fopenmp']
                e.extra_compile_args += ['-O3']

                if e.language == "c++":
                    e.extra_compile_args += ['-std=c++11']

        build_ext.build_extensions(self)

    def add_march_native(self):
        arg_march_native = "-march=native"
        arg_mcpu_native = "-mcpu=native"
        if self.test_supports_compile_arg(arg_march_native):
            for e in self.extensions:
                e.extra_compile_args.append(arg_march_native)
        elif self.test_supports_compile_arg(arg_mcpu_native):
            for e in self.extensions:
                e.extra_compile_args.append(arg_mcpu_native)

    def add_openmp_linkage(self):
        arg_omp1 = "-fopenmp"
        arg_omp2 = "-qopenmp"
        arg_omp3 = "-xopenmp"
        args_apple_omp = ["-Xclang", "-fopenmp", "-lomp"]
        if self.test_supports_compile_arg(arg_omp1):
            for e in self.extensions:
                e.extra_compile_args.append(arg_omp1)
                e.extra_link_args.append(arg_omp1)
        elif (sys.platform[:3].lower() == "dar") and self.test_supports_compile_arg(args_apple_omp):
            for e in self.extensions:
                e.extra_compile_args += ["-Xclang", "-fopenmp"]
                e.extra_link_args += ["-lomp"]
        elif self.test_supports_compile_arg(arg_omp2):
            for e in self.extensions:
                e.extra_compile_args.append(arg_omp2)
                e.extra_link_args.append(arg_omp2)
        elif self.test_supports_compile_arg(arg_omp3):
            for e in self.extensions:
                e.extra_compile_args.append(arg_omp3)
                e.extra_link_args.append(arg_omp3)

    def test_supports_compile_arg(self, comm):
        is_supported = False
        try:
            if not hasattr(self.compiler, "compiler_cxx"):
                return False
            if not isinstance(comm, list):
                comm = [comm]
            print("--- Checking compiler support for option '%s'" % " ".join(comm))
            fname = "contextualbandits_compiler_testing.cpp"
            with open(fname, "w") as ftest:
                ftest.write(u"int main(int argc, char**argv) {return 0;}\n")
            try:
                cmd = [self.compiler.compiler_cxx[0]]
            except:
                cmd = list(self.compiler.compiler_cxx)
            val_good = subprocess.call(cmd + [fname])
            try:
                val = subprocess.call(cmd + comm + [fname])
                is_supported = (val == val_good)
            except:
                is_supported = False
        except:
            pass
        try:
            os.remove(fname)
        except:
            pass
        return is_supported

setup(
    name = 'contextualbandits',
    packages = ['contextualbandits', 'contextualbandits.linreg'],
    install_requires=[
        'numpy>=1.17',
        'scipy',
        'pandas>=0.25.0',
        'scikit-learn>=0.22',
        'joblib>=0.13',
        'cython'
    ],
    version = '0.3.15',
    description = 'Python Implementations of Algorithms for Contextual Bandits',
    author = 'David Cortes',
    author_email = 'david.cortes.rivera@gmail.com',
    url = 'https://github.com/david-cortes/contextualbandits',
    keywords = 'contextual bandits offset tree doubly robust policy linucb thompson sampling',
    classifiers = [],
    cmdclass = {'build_ext': build_ext_subclass},
    ext_modules = [
        Extension("contextualbandits.linreg._wrapper_double",
                  sources=["contextualbandits/linreg/linreg_double.pyx"],
                  include_dirs=[np.get_include()]),
        Extension("contextualbandits.linreg._wrapper_float",
                  sources=["contextualbandits/linreg/linreg_float.pyx"],
                  include_dirs=[np.get_include()]),
        Extension("contextualbandits._cy_utils", language="c++",
                  sources=["contextualbandits/_cy_utils.pyx"],
                  include_dirs=[np.get_include()])
    ]
)
