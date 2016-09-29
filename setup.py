from setuptools import setup
from setuptools.command.install import install as Install
import os
import errno

# Completes the install
class MyInstall(Install):
    def run(self):
        # create the manpage
        import manpage

        # move it into position
        location = self.install_lib
        try:
            mandir = os.path.join(self.prefix, 'man', 'man1')
            manfile = os.path.join(mandir, 'ec.1')
            os.makedirs(mandir)
            manpage.write(manfile)
        except (IOError, OSError) as err:
            if err.errno != errno.EEXIST:
                print(str(err))

        # complete the install
        Install.run(self)

# Return the contents of a file
# Path is relative to the location of this setup file.
def contents(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requires=[
    'docopt',
    'docutils',
    'engfmt>=0.9',
    'inform',
]

setup(
    name='engineering-calculator',
    version="1.1.12",
    description='engineering calculator',
    long_description=contents('README.rst'),
    author="Ken Kundert",
    author_email='ec@nurdletech.com',
    url='http://nurdletech.com/linux-utilities/ec',
    download_url='https://github.com/kenkundert/ec/tarball/master',
    scripts=['ec'],
    py_modules=['ec', 'calculator', 'actions'],
    setup_requires=requires,
    install_requires=requires,
    cmdclass={
        'install': MyInstall,
    },
    classifiers=[
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
    ],
    license='GPLv3',
)
