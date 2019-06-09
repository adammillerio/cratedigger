#!/usr/bin/env python3
from setuptools import setup, find_packages

# Load version from file
with open('version', 'r') as version_file:
  version = version_file.read().strip()

setup(
  name='cratedigger',
  version=version,
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'click==7.0',
    'anytree==2.6.0'
  ],
  entry_points='''
    [console_scripts]
    cratedigger=cratedigger.cli:cli
  '''
)
