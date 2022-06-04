#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Tools for Lidar processing focused on Spanish PNOA datasets

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
@deffield    updated: 2022-06-01
'''

import sys
import logging

__version__ = '0.0a3'
__date__ = '2016-2022'
__updated__ = '2022-06-01'

# ==============================================================================
# Verbose provisional para la version alpha
if '-vvv' in sys.argv:
    __verbose__ = 3
elif '-vv' in sys.argv:
    __verbose__ = 2
elif '-v' in sys.argv or '--verbose' in sys.argv:
    __verbose__ = 1
else:
    # En eclipse se adopta el valor indicado en Run Configurations -> Arguments
    __verbose__ = 0
# ==============================================================================
if '-q' in sys.argv:
    __quiet__ = 1
    __verbose__ = 0
else:
    __quiet__ = 0
# ==============================================================================
# TB = '\t'
TB = ' ' * 19
TV = ' ' * 3
# ==============================================================================

# ==============================================================================
# set a format which is simpler for console use
formatter0 = logging.Formatter('{message}', style='{')
# define a Handler which writes INFO messages or higher to the sys.stderr
consoleLog = logging.StreamHandler()
if __verbose__ == 3:
    consoleLog.setLevel(logging.DEBUG)
elif __verbose__ == 2:
    consoleLog.setLevel(logging.INFO)
elif __verbose__ == 1:
    consoleLog.setLevel(logging.WARNING)
elif not __quiet__:
    consoleLog.setLevel(logging.ERROR)
else:
    consoleLog.setLevel(logging.CRITICAL)
consoleLog.setFormatter(formatter0)
myLog = logging.getLogger(__name__.split('.')[-1])
myLog.addHandler(consoleLog)
# ==============================================================================
myLog.debug('{:_^80}'.format(''))
myLog.debug('cartolidar.__init__-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================

# Paquetes, clases y modulos que se importan con: from cartolidar import *
# __all__ = [
#     'clidtools',
#     'clidax',
#     'DasoLidarSource',
# ]

# from cartolidar import clidtools
# from cartolidar import clidax
# from cartolidar.clidtools.clidtwins import DasoLidarSource
# from . import clidtools
# from . import clidax
# from clidtools.clidtwins import DasoLidarSource
