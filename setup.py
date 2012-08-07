#!/usr/bin/env python

import os
import sys

from distutils.core import setup
from distutils.command.install_scripts import install_scripts

class my_install(install_scripts):
    def run(self):
        install_scripts.run(self)

        try:
            os.symlink(
                os.sep.join([self.install_dir, 'rscadstreamer']),
                os.sep.join([self.install_dir, 'rscad-control'])
                )
        except:
            pass


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
        cmdclass=dict(install_scripts=my_install)
    )

