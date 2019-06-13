#!/usr/bin/env python3
from setuptools import setup, find_packages

# Load version from file
with open('version', 'r') as version_file:
  version = version_file.read().strip()

setup(
  name='cratedigger',
  version=version,
  license='MIT',
  description='cratedigger is a command line tool for managing your Serato library',
  author='Adam Miller',
  author_email='miller@adammiller.io',
  url='https://github.com/adammillerio/cratedigger',
  download_url='https://github.com/adammillerio/cratedigger/archive/v%s.tar.gz' % version,
  keywords=['serato', 'dj', 'music', 'library', 'crate', 'sync'],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: End Users/Desktop',
    'Topic :: Multimedia :: Sound/Audio :: Editors',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3 :: Only',
  ],
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'click>=7.0',
    'anytree>=2.6.0'
  ],
  entry_points='''
    [console_scripts]
    cratedigger=cratedigger.cli:cli
  '''
)
