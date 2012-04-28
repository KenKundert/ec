from distutils.core import setup

longDescription='''
Engineering calculator.
'''

setup(
    name='ec'
  , version='1.0'
  , description='engineering calculator'
  , long_description=longDescription
  , author="Ken Kundert"
  , author_email='ken@theKunderts.net'
  , scripts=['ec']
  , py_modules=['ec']
  , data_files=[
        ('man/man1', ['ec.1'])
    ]
  , platforms=['rhel']
)
