#!/usr/bin/env python

import os
import sys

from distutils.core import setup

setup(
        name='rscadstreamer',
        author='Jeremy Jones',
        author_email='jmjone@illinois.edu',
        url='http://code.iti.illinois.edu/redmine/projects/rscadstreamer',
        version='1.0',
        requires=[
            'argparse',
        ],
        packages=['rtds'],
        scripts=['rscadstreamer'],
    )

try:
    os.symlink(
        os.sep.join([sys.prefix, 'bin', 'rscadstreamer']),
        os.sep.join([sys.prefix, 'bin', 'rscad-control'])
        )
except:
    pass
