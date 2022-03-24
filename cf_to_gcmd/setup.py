#!/usr/bin/env python

from distutils.core import setup

setup(name='cf_to_gcmd',
      version='0.1',
      description='Python module for converting CF to GCMD using an ERDDAP source file',
      packages=['cf_to_gcmd'],
      install_requires=['pandas']
      )