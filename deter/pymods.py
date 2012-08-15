#!/usr/bin/env python

import sys

## Chack for argparse
try:
    import argparse
except ImportError:
    sys.stdout.write('argparse ')

## Check for pyev.  If it's there, then we know libev is installed
try:
    import pyev
except ImportError:
    sys.stdout.write('pyev')



