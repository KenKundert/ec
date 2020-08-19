from setuptools import setup

setup(
    name = 'engineering-calculator',
    version = '1.7.0',
    description = 'engineering calculator',
    long_description = open('README.rst').read(),
    long_description_content_type = 'text/x-rst',
    author = "Ken Kundert",
    author_email = 'ec@nurdletech.com',
    url = 'http://nurdletech.com/linux-utilities/ec',
    download_url = 'https://github.com/kenkundert/ec/tarball/master',
    packages = 'engineering_calculator'.split(),
    entry_points = {
        'console_scripts': ['ec = engineering_calculator.main:main'],
    },
    install_requires = 'docopt docutils quantiphy>=2.1.0 inform>=1.9'.split(),
    classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Environment :: Console',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Operating System :: POSIX :: Linux',
      #'Programming Language :: Python :: 2',
      #'Programming Language :: Python :: 2.7',
      #   should work, but no longer tested
      #'Programming Language :: Python :: 3',
      #'Programming Language :: Python :: 3.3',
      #   should work, but no longer tested
      #'Programming Language :: Python :: 3.4',
      #   should work, but no longer tested
      #'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
      'Topic :: Scientific/Engineering',
    ],
    license = 'GPLv3',
)
