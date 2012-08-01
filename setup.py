#!/usr/bin/env python
from distutils.core import setup
import manpage # simply importing the manpage creates the manpage as a side effect

longDescription='''
Engineering calculator.
'''

setup(
    name='ec'
  , version='1.0'
  , description='engineering calculator'
  , long_description=longDescription
  , author="Ken Kundert"
  , author_email='ec@shalmirane.com'
  , scripts=['ec']
  , py_modules=['ec', 'calculator', 'actions', 'engfmt', 'cmdline', 'textcolors']
  , data_files=[
        ('man/man1', ['ec.1'])
    ]
  , platforms=['rhel']
)
