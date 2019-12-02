#!/usr/bin/env python
from distutils.core import setup,Extension
import numpy

setup(name='CreateSpiketrains',
    version='0.5',
    description='Create spiketrains from hmmsort',
    author='Roger Herikstad',
    author_email='roger.herikstad@gmail.com',
    packages=['CreateSpiketrains'],
    scripts=['CreateSpiketrains/create_spiketrains.py']
)
