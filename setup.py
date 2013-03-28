#!/usr/bin/env python
"""
RSCADStreamer install
"""

import os

from distutils.core import setup
from distutils.command.install_scripts import install_scripts

class my_install(install_scripts):
    """
    Custom install_script class to create symlinks
    """

    def run(self):
        install_scripts.run(self)

        try:
            os.symlink(
                os.sep.join([self.install_dir, 'rscadstreamer']),
                os.sep.join([self.install_dir, 'rscad-control'])
                )
        except Exception:
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

