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
  , author_email='ec@shalmirane.com'
  , scripts=['ec']
  , py_modules=['ec', 'engfmt', 'cmdline', 'textcolors']
  , data_files=[
        ('man/man1', ['ec.1'])
    ]
  , platforms=['rhel']
)
