#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
import distutils.log as log
import shutil
import os

# Return the contents of a file
# Path is relative to the location of this setup file.
def contents(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Supplement the built-in build command such that manpage (ec.1) is created
# during the build phase
from distutils.command.build import build as _build
class build(_build):
    def initialize_options(self):
        import manpage
        log.info("Creating manpage.")
        manpage.write('ec.1')
        _build.initialize_options(self)

setup(
    name='ec'
  , version='1.0'
  , description='engineering calculator'
  , long_description=contents('README')
  , author="Ken Kundert"
  , author_email='ec@shalmirane.com'
  , url='http://www.nurdletech.com/ec.html'
  , download_url='https://github.com/KenKundert/ec/downloads'
  , setup_requires='docutils >= 0.7'
  , install_requires='python >= 2.6'
  , cmdclass = {'build': build}
  , scripts=['ec']
  , py_modules=['ec', 'calculator', 'actions', 'engfmt', 'cmdline', 'textcolors']
  , data_files=[
        ('man/man1', ['ec.1'])
    ]
  , classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python :: 2.6',
      'Topic :: Scientific/Engineering',
    ],
)
