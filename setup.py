#!/usr/bin/env python3

import distutils.core

VERSION = '0.0.1-devel'

distutils.core.setup(
    name='bloodloan',
    version=VERSION,
    description='Mortgage calculation backend for a Jupyter Notebook',
    author='Micah R Ledbetter',
    author_email='me@micahrl.com',
    url='https://github.com/mrled/jupyter-mortgage',
    long_description="\n".join([
        'BLOODLOAN: HUMAN SACRIFICE IS THE INTEREST ON LOANS FROM JOVE',
        'Mortgage calculation backend module for a Jupyter Notebook']),
    license='Public Domain',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'License :: Public Domain',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['bloodloan'],
    package_dir={'bloodloan': 'bloodloan'})
