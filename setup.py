from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

setup(
    name = "hisparc-sapphire",
    version = "0.9.3",
    packages = find_packages(),
    url = "http://github.com/hisparc/sapphire/",
    license = "GPLv3",
    author = "David Fokkema",
    author_email = "davidf@nikhef.nl",
    description = "A framework for the HiSPARC experiment",
    long_description = long_description,
    classifiers=['Intended Audience :: Science/Research',
                 'Intended Audience :: Education',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Education'],

    install_requires = ['numpy', 'scipy', 'tables', 'matplotlib',
                        'progressbar', 'mock'],
)
