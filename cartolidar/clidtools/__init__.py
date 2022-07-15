#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Utilities included in cartolidar project 
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidtools incldes ancillary tools that work on raster outputs of cartolidar
Most of those raster represent dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
@deffield    updated: 2022-06-01
'''

import os
import sys
import re
import logging
import importlib
import importlib.util

spec = importlib.util.find_spec('cartolidar')
if not spec is None:
    from cartolidar.clidtools.clidtwcfg import GLO # GLO es una variable publica del modulo clidtwcfg
    from cartolidar.clidtools.clidtwins import DasoLidarSource # DasoLidarSource es la clase principal del modulo clidtwins
    from cartolidar.clidtools.clidtwinx import mostrarListaDrivers # mostrarListaDrivers es una funcion del modulo clidtwinx
else:
    try:
        from cartolidar.clidtools.clidtwcfg import GLO # GLO es una variable publica del modulo clidtwcfg
        from cartolidar.clidtools.clidtwins import DasoLidarSource # DasoLidarSource es la clase principal del modulo clidtwins
        from cartolidar.clidtools.clidtwinx import mostrarListaDrivers # mostrarListaDrivers es una funcion del modulo clidtwinx
    except:
        from .clidtwcfg import GLO # GLO es una variable publica del modulo clidtwcfg
        from .clidtwins import DasoLidarSource # DasoLidarSource es la clase principal del modulo clidtwins
        from .clidtwinx import mostrarListaDrivers # mostrarListaDrivers es una funcion del modulo clidtwinx

# from . import clidtwins # Inlcuye DasoLidarSource, mostrarListaDrivers, etc.
# from . import clidtwcfg # Incluye GLO, que es una variable publica del modulo clidtwcfg
# Lectura de VERSIONFILE en clidbase.py, clidflow.py, qlidtwins.py,
#     clidax.config.py, clidax.clidaux.py, clidfr.clidhead.py, clidtools.__init__.py 
# ==============================================================================
MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSIONFILE = os.path.abspath(os.path.join(MAIN_FILE_DIR, '_version.py'))
if not os.path.exists(VERSIONFILE):
    VERSIONFILE = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..', '_version.py'))
    if not os.path.exists(VERSIONFILE):
        VERSIONFILE = os.path.abspath(os.path.join(MAIN_FILE_DIR, '../..', '_version.py'))
        if not os.path.exists(VERSIONFILE):
            VERSIONFILE = os.path.abspath('_version.py')
if os.path.exists(VERSIONFILE):
    try:
        verstrline = open(VERSIONFILE, "rt").read()
        VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, verstrline, re.M)
        if mo:
            # __version__ = mo.groups()[0]
            __version__ = mo.group(1)
        else:
            # raise RuntimeError(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __version__ = "a.b.c"')
            sys.stderr.write(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __version__ = "a.b.c"\n')
            __version__ = '0.0a0'
        VSRE = r"^__date__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, verstrline, re.M)
        mo = re.search(VSRE, verstrline, re.M)
        if mo:
            __date__ = mo.group(1)
        else:
            # raise RuntimeError(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __date__ = "year1-year2"')
            sys.stderr.write(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __date__ = "year1-year2"\n')
            __date__ = '2016-2022'
        VSRE = r"^__updated__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, verstrline, re.M)
        mo = re.search(VSRE, verstrline, re.M)
        if mo:
            __updated__ = mo.group(1)
        else:
            # raise RuntimeError(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __updated__ = "date"')
            sys.stderr.write(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __updated__ = "date"\n')
            __updated__ = '2022-07-01'
        VSRE = r"^__copyright__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, verstrline, re.M)
        mo = re.search(VSRE, verstrline, re.M)
        if mo:
            __copyright__ = mo.group(1)
        else:
            # raise RuntimeError(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __copyright__ = "..."')
            sys.stderr.write(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __copyright__ = "..."')
            __copyright__ = '@clid 2016-22'
    except:
        sys.stderr.write(f'clidtools.__init__-> no se ha podido leer {VERSIONFILE}\n')
        __version__ = '0.0a0'
        __date__ = '2016-2022'
        __updated__ = '2022-07-01'
        __copyright__ = '@clid 2016-22'
else:
    __version__ = '0.0a0'
    __date__ = '2016-2022'
    __updated__ = '2022-07-01'
    __copyright__ = '@clid 2016-22'
# ==============================================================================
# __all__ = [
#     'clidtwins',
#     'clidtwcfg',
# ]
# Variables, clases y funciones que se importan con: from clidtwins import *
__all__ = [
    'GLO',
    'DasoLidarSource',
    'mostrarListaDrivers'
]
# No se importa nada con: from qlidtwins import *
__all__ = []
# ==============================================================================

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
TB = ' ' * 12
TV = ' ' * 3
# ==============================================================================

# ==============================================================================
thisModule = __name__.split('.')[-1]
formatter0 = logging.Formatter('{message}', style='{')
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
myModule = 'clidconfig'
myLog = logging.getLogger(myModule)
myLog.addHandler(consoleLog)
# ==============================================================================
myLog.debug('{:_^80}'.format(''))
myLog.debug('clidtools.__init__-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================
