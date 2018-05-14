#!/usr/bin/env python

from distutils.core import setup

setup(name='hos_protocol_v2',
      version='0.1',
      description='Protocols by Hallgren, Ochoa and Sabelfeld. Edited by Gunnarsson and Talebi.',
      author='Per Hallgren',
      author_email='per.zut@gmail.com',
      packages=['hos_protocol_v2'],
      requires=['gmpy2', 'bettertimes'],
)
