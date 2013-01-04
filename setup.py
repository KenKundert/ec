#!/bin/env python
from distutils.core import setup
import os
from calculator import versionNumber

# Create/update manpage before installing
import manpage
manpage.write('ec.1')

# Return the contents of a file
# Path is relative to the location of this setup file.
def contents(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='ec'
  , version=versionNumber
  , description='engineering calculator'
  , long_description=contents('README')
  , author="Ken Kundert"
  , author_email='ec@nurdletech.com'
  , url='http://www.nurdletech.com/ec.html'
  , download_url='https://github.com/KenKundert/ec/downloads'
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
    ]
)
