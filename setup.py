from setuptools import setup
import os

# Create/update manpage before installing
try:
    import manpage
    manpage.write('ec.1')
except ImportError:
    # inform is not installed yet, so just use the existing version of the
    # manpage rather than try to recreate/update it.
    pass

# Return the contents of a file
# Path is relative to the location of this setup file.
def contents(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='engineering-calculator'
  , version="1.1.5"
  , description='engineering calculator'
  , long_description=contents('README.rst')
  , author="Ken Kundert"
  , author_email='ec@nurdletech.com'
  , url='http://nurdletech.com/linux-utilities/ec'
  , download_url='https://github.com/kenkundert/ec/tarball/master'
  , scripts=['ec']
  , py_modules=['ec', 'calculator', 'actions']
  , data_files=[
        ('man/man1', ['ec.1'])
    ]
  , install_requires=[
        'docopt',
        'engfmt',
        'inform',
    ]
  , classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: Console',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Topic :: Scientific/Engineering',
    ]
  , license='GPLv3'
)
