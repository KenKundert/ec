from setuptools import setup
from setuptools.command.install import install as Install
import os
import errno

# Completes the install
class MyInstall(Install):
    def run(self):
        # create the manpage
        import manpage

        # move manpage it into position
        # not sure which of these is preferred, just use the first that exists
        for candidate in [
            'prefix', 'install_base', 'install_data',
            'install_platbase', 'install_userbase'
        ]:
            root = getattr(self, candidate, None)
            if root:
                break
        if root:
            mandir = os.path.join(root, 'man', 'man1')
            try:
                os.makedirs(mandir)
            except (IOError, OSError) as err:
                if err.errno != errno.EEXIST:
                    print(str(err))
            manfile = os.path.join(mandir, 'ec.1')
        else:
            manfile = 'ec.1'
        print('Installing manpage to %s.' % manfile)
        manpage.write(manfile)

        # complete the install
        Install.run(self)

# Return the contents of a file
# Path is relative to the location of this setup file.
def contents(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requires=[
    'docopt',
    'docutils',
    'quantiphy>=1.3.0',
    'inform>=1.4.3',
]

setup(
    name='engineering-calculator',
    version='1.5.0',
    description='engineering calculator',
    long_description=contents('README.rst'),
    author="Ken Kundert",
    author_email='ec@nurdletech.com',
    url='http://nurdletech.com/linux-utilities/ec',
    download_url='https://github.com/kenkundert/ec/tarball/master',
    scripts=['ec'],
    py_modules=[
        'actions',
        'calculator',
        'manpage',
    ],
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
