#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on 17/05/2017

@author: JB
# -*- coding: latin-1 -*-
'''
# from __future__ import division, print_function
# from __future__ import unicode_literals

import os
import sys
import pathlib
import time
from datetime import datetime, timedelta
import types # Ver https://docs.python.org/2/library/types.html
# import csv
import re
import math
# import random
import platform
import inspect
import traceback
import subprocess
# import argparse
# from configparser import RawConfigParser
import logging
import importlib
import importlib.util
import struct
import shutil
import gc
import socket
import collections

# Paquetes de terceros
import numpy as np
import numba
import scipy
from _ast import Or
try:
    import psutil
    psutilOk = True
except:
    psutilOk = False
# from scipy.spatial.distance import pdist

try:
    # print(os.environ['PATH'])
    from osgeo import gdal, ogr, osr, gdalnumeric, gdalconst
    gdalOk = True
except:
    print('clidaux-> No se puede importar gdal "from osgeo", se intenta directamente ("import gdal").')
    gdalOk = False
if not gdalOk:
    try:
        import gdal, ogr, osr, gdalnumeric, gdalconst
        sys.stdout.write('           gdal importado ok con "import gdal".\n')
        gdalOk = True
    except:
        gdalOk = False
        print('clidaux-> Error importando gdal.')
        # sys.exit(0)

# ==============================================================================
if __name__ == '__main__':
    print('\nclidaux-> ATENCION: este modulo no se puede ejecutar de forma autonoma')
    sys.exit(0)
# ==============================================================================
if '--cargadoClidaux' in sys.argv:
    moduloPreviamenteCargado = True
    print(f'\nclidaux->1> moduloPreviamenteCargado: {moduloPreviamenteCargado}; sys.argv: {sys.argv}')
else:
    moduloPreviamenteCargado = False
    print(f'\nclidaux->1> moduloPreviamenteCargado: {moduloPreviamenteCargado}; sys.argv: {sys.argv}')
    sys.argv.append('--cargadoClidaux')
# ==============================================================================
if '--idProceso' in sys.argv and len(sys.argv) > sys.argv.index('--idProceso') + 1:
    ARGS_idProceso = sys.argv[sys.argv.index('--idProceso') + 1]
else:
    # ARGS_idProceso = str(random.randint(1, 999998))
    ARGS_idProceso = '999999'
    sys.argv.append('--idProceso')
    sys.argv.append(ARGS_idProceso)
# ==============================================================================
if type(ARGS_idProceso) == int:
    MAIN_idProceso = ARGS_idProceso
elif type(ARGS_idProceso) == str:
    try:
        MAIN_idProceso = int(ARGS_idProceso)
    except:
        print(f'clidaux-> ATENCION: revisar asignacion de idProceso.')
        print(f'ARGS_idProceso: {type(ARGS_idProceso)} {ARGS_idProceso}')
        print(f'sys.argv: {sys.argv}')
else:
    MAIN_idProceso = 0
    print(f'clidaux-> ATENCION: revisar codigo de idProceso.')
    print(f'ARGS_idProceso: {type(ARGS_idProceso)} {ARGS_idProceso}')
    print(f'sys.argv: {sys.argv}')
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

# ==============================================================================
# ============================ Variables GLOBALES ==============================
# ==============================================================================
# TB = '\t'
TB = ' ' * 10
TV = ' ' * 3
TW = ' ' * 2
# ==============================================================================
# ATENCION: las2las no me funciona para descomprimir en memoria
TRNSdescomprimirConlaszip = True
TRNSdescomprimirConlas2las = False
# ==============================================================================

# ==============================================================================
# ============================== Variables MAIN ================================
# ==============================================================================
# Directorios de la aplicacion:
# Dir del modulo que se esta ejecutando (clidaux.py):
MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))  # En calendula /LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1/cartolidar/cartolidar/clidax
# Dir de clidbase.py:
MAIN_BASE_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))
# Dir de setup.py:
MAIN_PROJ_DIR = os.path.abspath(os.path.join(MAIN_BASE_DIR, '..')) # Equivale a MAIN_FILE_DIR = pathlib.Path(__file__).parent
# Dir en el que esta el proyecto (D:/_clid o /LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1):
MAIN_RAIZ_DIR = os.path.abspath(os.path.join(MAIN_PROJ_DIR, '..'))
# Directorio desde el que se lanza la app (estos dos coinciden):
MAIN_THIS_DIR = os.path.abspath('.')
MAIN_WORK_DIR = os.getcwd()
# Directorio que depende del entorno:
MAIN_HOME_DIR = str(pathlib.Path.home())
# ==============================================================================
# Unidad de disco si MAIN_ENTORNO = 'windows'
MAIN_DRIVE = os.path.splitdrive(MAIN_FILE_DIR)[0]  # 'D:' o 'C:'
# ==============================================================================
if MAIN_FILE_DIR[:12] == '/LUSTRE/HOME':
    MAIN_ENTORNO = 'calendula'
    MAIN_PC = 'calendula'
elif MAIN_FILE_DIR[:8] == '/content':
    MAIN_ENTORNO = 'colab'
    MAIN_PC = 'colab'
else:
    MAIN_ENTORNO = 'windows'
    try:
        if MAIN_DRIVE[0] == 'D':
            MAIN_PC = 'Casa'
        else:
            MAIN_PC = 'JCyL'
    except:
        MAIN_ENTORNO = 'calendula'
        MAIN_PC = 'calendula'
# ==============================================================================

# ==============================================================================
# Ver https://peps.python.org/pep-0008/#module-level-dunder-names
# Ver https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
# Lectura de VERSIONFILE en clidbase.py, clidflow.py, qlidtwins.py,
#     clidax.config.py, clidax.clidaux.py, clidfr.clidhead.py, clidtools.__init__.py 
# ==============================================================================
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


# ==============================================================================
# Version original de la funcion
def infoUsuario(verbose=False):
    if psutilOk:
        try:
            esteUsuario = psutil.users()[0].name
            if verbose:
                print('clidaux-> Usuario:', esteUsuario)
        except:
            esteUsuario = psutil.users()
            if verbose:
                print('clidaux-> Users:', esteUsuario)
        if not isinstance(esteUsuario, str) or esteUsuario == '':
            esteUsuario = 'local'
    else:
        esteUsuario = 'SinUsuario'
    return esteUsuario


# ==============================================================================
# Version original de la funcion
def showCallingModules(inspect_stack=inspect.stack(), verbose=False):
    # print('->->->inspect_stack  ', inspect_stack
    # print('->->->inspect.stack()', inspect.stack())
    if len(inspect_stack) > 1:
        try:
            esteModuloFile0 = inspect_stack[0][1]
            esteModuloNum0 = inspect_stack[0][2]
            esteModuloFile1 = inspect_stack[1][1]
            esteModuloNum1 = inspect_stack[1][2]
            esteModuloName0 = inspect.getmodulename(esteModuloFile0)
            esteModuloName1 = inspect.getmodulename(esteModuloFile1)
        except:
            print(f'{TB}clidaux-> Error identificando el modulo 1')
            return 'desconocido1', 'desconocido1'
    else:
        if verbose:
            print(f'{TB}clidaux-> No hay modulos que identificar')
        return 'noHayModuloPrevio', 'esteModulo'

    if not esteModuloName0 is None:
        esteModuloName = esteModuloName0
        esteModuloNum = esteModuloNum0
        stackSiguiente = 1
    else:
        esteModuloName = esteModuloName1
        esteModuloNum = esteModuloNum1
        stackSiguiente = 2

    callingModulePrevio = ''
    callingModuleInicial = ''
    if verbose:
        print(f'{TB}clidaux-> El modulo {esteModuloName} ({esteModuloNum}) ha sido', end=' ')
    for llamada in inspect_stack[stackSiguiente:]:
        if 'cartolid' in llamada[1] or 'clid' in llamada[1] or 'qlid' in llamada[1]:
            callingModule = inspect.getmodulename(llamada[1])
            if callingModule != esteModuloName and callingModulePrevio == '':
                callingModulePrevio = callingModule
            callingModuleInicial = callingModule
            # if callingModule != 'clidaux' and callingModule != 'callingModule':
                # print('clidaux-> llamado por', llamada[1:3], end=' ')
            if verbose:
                print(f'importado desde: {callingModule} ({llamada[2]})', end='; ')
    if verbose:
        print('')
    return callingModulePrevio, callingModuleInicial


# ==============================================================================
def iniciaConsLog(myModule='clidaux', myVerbose=False, myQuiet=False):
    if myVerbose == 3:
        logLevel = logging.DEBUG  # 10
    elif myVerbose == 2:
        logLevel = logging.INFO  # 20
    elif myVerbose == 1:
        logLevel = logging.WARNING  # 30
    elif not __quiet__:
        logLevel = logging.ERROR
    else:
        logLevel = logging.CRITICAL
    # ==============================================================================
    # class ContextFilter(logging.Filter):
    #     """
    #     This is a filter which injects contextual information into the log.
    #     """
    #
    #     def filter(self, record):
    #         record.thisUser = myUser
    #         record.thisFile = myModule[:10]
    #         return True
    # myFilter = ContextFilter()
    # ==============================================================================
    # formatter1 = '{asctime}|{name:10s}|{levelname:8s}|{thisUser:8s}|> {message}'
    # formatterFile = logging.Formatter(formatter1, style='{', datefmt='%d-%m-%y %H:%M:%S')
    formatterCons = logging.Formatter('{message}', style='{')
    
    myLog = logging.getLogger(myModule)
    if sys.argv[0].endswith('__main__.py') and 'cartolidar' in sys.argv[0]:
        # qlidtwins.py se ejecuta lanzando el paquete cartolidar desde linea de comandos:
        #  python -m cartolidar
        # En __main__.py ya se ha confiigurado el logging.basicConfig()
        # if myModule == __name__.split('.')[-1]:
        #     print(f'{myModule}-> En __main.py se va a crear el loggin de consola para todos los modulos en __main__.py')
        # else:
        #     print(f'{myModule}-> Ya se ha creado el loggin de consola para todos los modulos en __main__.py')
        pass
    consLog = logging.StreamHandler()
    consLog.setFormatter(formatterCons)
    consLog.setLevel(logLevel)
    myLog.setLevel(logLevel)
    myLog.addHandler(consLog)
    return myLog


# ==============================================================================
def foo0():
    pass

# ==============================================================================
CONFIGverbose = __verbose__ > 2
if CONFIGverbose:
    print(f'\nclidaux-> AVISO: CONFIGverbose True; __verbose__: {__verbose__}')
# ==============================================================================

# ==============================================================================
myUser = infoUsuario()
myModule = __name__.split('.')[-1]
# ==============================================================================
if not moduloPreviamenteCargado or True:
    print('\nclidaux-> AVISO: creando myLog (ConsLog)')
    myLog = iniciaConsLog(myModule=myModule, myVerbose=__verbose__)
    # print('myLog.getEffectiveLevel:', myLog.getEffectiveLevel())
    # print('myLog.Level:', myLog.level)
# ==============================================================================
if CONFIGverbose:
    myLog.debug(f'{"":_^80}')
    myLog.debug(f'clidaux-> Debug & alpha version info:')
    myLog.debug(f'{TB}-> ENTORNO:          {MAIN_ENTORNO}')
    myLog.debug(f'{TB}-> Modulo principal: <{sys.argv[0]}>') # = __file__
    myLog.debug(f'{TB}-> __package__ :     <{__package__ }>')
    myLog.debug(f'{TB}-> __name__:         <{__name__}>')
    myLog.debug(f'{TB}-> __verbose__:      <{__verbose__}>')
    myLog.debug(f'{TB}-> IdProceso         <{MAIN_idProceso:006}>')
    # myLog.debug(f'{TB}-> configFile:       <{GLO.configFileNameCfg}>')
    myLog.debug(f'{TB}-> sys.argv:         <{sys.argv}>')
    myLog.debug(f'{"":=^80}')
# ==============================================================================

# ==============================================================================
if CONFIGverbose:
    myLog.debug(f'\nclidaux-> Cargando clidaux...')
    myLog.debug(f'{TB}-> Directorio desde el que se lanza la aplicacion-> os.getcwd(): {os.getcwd()}')
    myLog.debug(f'{TB}-> Revisando la pila de llamadas...')
callingModulePrevio, callingModuleInicial = showCallingModules(inspect_stack=inspect.stack(), verbose=False)
if CONFIGverbose:
    myLog.debug(f'{TB}{TV}-> callingModulePrevio:  {callingModulePrevio}')
    myLog.debug(f'{TB}{TV}-> callingModuleInicial: {callingModuleInicial}')
# ==============================================================================


# ==============================================================================
if CONFIGverbose:
    sys.stdout.write(f'\nclidaux-> Importando clidconfig desde clidaux, a su vez importado desde {callingModulePrevio} (modulo inicial: {callingModuleInicial})\n')
# if True:
    # https://stackoverflow.com/questions/61234609/how-to-import-python-package-from-another-directory
    # https://realpython.com/python-import/
    # https://blog.ionelmc.ro/2014/05/25/python-packaging/
    # sys.path.insert(0, os.path.join(MAIN_PROJ_DIR, 'cartolidar/clidax'))

spec = importlib.util.find_spec('cartolidar')
if not spec is None:
    if CONFIGverbose:
        sys.stdout.write('\nclidaux-> Importando clidconfig desde cartolidar.clidax\n')
    from cartolidar.clidax import clidconfig
    if CONFIGverbose:
        sys.stdout.write(f'\nclidaux-> Ok clidconfig importado de cartolidar.clidax (0)\n')
else:
    try:
        if CONFIGverbose:
            sys.stdout.write('\nclidaux-> Importando clidconfig desde cartolidar.clidax\n')
        from cartolidar.clidax import clidconfig
        if CONFIGverbose:
            sys.stdout.write(f'\nclidaux-> Ok clidconfig importado de cartolidar.clidax (1)\n')
    except:
        try:
            if CONFIGverbose:
                sys.stdout.write(f'\nclidaux-> Intento alternativo de importar clidconfig desde la version local {os.getcwd()}/clidax\n')
            from clidax import clidconfig
            if CONFIGverbose:
                sys.stdout.write(f'\nclidaux-> Ok clidconfig importado del clidax local (2)\n')
        except:
            sys.stdout.write(f'\nclidaux-> Alternativa para cuando el modulo inicial es este u otro modulo de este package:\n')
            import clidconfig
            if CONFIGverbose:
                sys.stdout.write(f'\nclidaux-> Ok clidconfig importado directamente (modulo inicial en el mismo package que clidconfig) (3)\n')

# ==============================================================================
MAINusuario = infoUsuario(False)
# ==============================================================================
nuevosParametroConfiguracion = {}
if CONFIGverbose:
    print(f'\nclidaux-> A Llamo a clidconfig.leerCambiarVariablesGlobales<> (sin nuevosParametroConfiguracion)')
    print(f'{TB}para leer los parametros de configuracion del fichero cfg.')
GLOBALconfigDict = clidconfig.leerCambiarVariablesGlobales(
    nuevosParametroConfiguracion,
    LCL_idProceso=MAIN_idProceso,
    inspect_stack=inspect.stack(),
    verbose=CONFIGverbose,
)
if CONFIGverbose:
    print(f'clidaux-> B Cargando parametros de configuracion GLOBALconfigDict en GLO')
GLO = clidconfig.VariablesGlobales(GLOBALconfigDict)
if CONFIGverbose:
    print(f'{TB}-> configFileNameCfg:       {GLO.configFileNameCfg}')
    print(f'{"":=^80}')
LCLverbose = max(GLO.GLBLverbose, __verbose__)

# ==============================================================================
if CONFIGverbose:
    print(f'clidaux-> C ok. GLO.GLBLverbose: {GLO.GLBLverbose}; CONFIGverbose: {CONFIGverbose}; __verbose__: {__verbose__}')
    print(f'clidaux-> C ok. GLO.MAINrutaOutput: {GLO.MAINrutaOutput}')
# ==============================================================================

# ==============================================================================
# if callingModuleInicial == 'generax' or os.getcwd().endswith('gens'):
#     print(f'\nclidaux-> NO se cargan las variables globales. Modulo importado desde la ruta: {os.getcwd()} -> Inicial: {callingModuleInicial}')
#     print(f'{TB}-> __name__:        {__name__}')
#     print(f'{TB}-> Modulo inicial:  {callingModuleInicial}')
#     print(f'{TB}-> Ruta de trabajo: {os.getcwd()}')
#
#     class Object(object):
#         pass
#
#     GLO = Object()
#     GLO.GLBLficheroLasTemporal = ''
#     GLO.GLBLverbose = True
# ==============================================================================

# ==============================================================================
# Estos parametros tb se asignan en clidbase.py y guardan en el cfg, pero
# clidbase.py importa clidaux antes, x lo q pasa antes x aqui y tb lo hago aqui.
if MAIN_ENTORNO == 'calendula':
    # MAINrutaRaiz = MAIN_RAIZ_DIR
    MAINrutaRaiz =  '/LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1'  # = MAIN_RAIZ_DIR
    MAIN_RAIS_DIR = '/scratch/jcyl_spi_1/jcyl_spi_1_1'
elif (
    'MAINrutaRaiz' in dir(GLO)
    and not GLO.MAINrutaRaiz is None
    and GLO.MAINrutaRaiz != 'None'
    and GLO.MAINrutaRaiz != ''
):
    MAINrutaRaiz = GLO.MAINrutaRaiz
    MAIN_RAIS_DIR = GLO.MAINrutaRaiz
else:
    MAINrutaRaiz = MAIN_RAIZ_DIR
    MAIN_RAIS_DIR = MAIN_RAIZ_DIR
# ==============================================================================
if 'cartolidar' in MAINrutaRaiz:
    MAIN_MDLS_DIR = os.path.abspath(os.path.join(
        MAINrutaRaiz,
        '../data'
    ))
else:
    MAIN_MDLS_DIR = os.path.abspath(os.path.join(
        MAINrutaRaiz,
        'data'
    ))
# ==============================================================================
# Estos parametros se asignan en clidbase.py y guardan en el cfg, pero lo reitero aqui para darle autonomia
paramConfigAdicionalesMAIN = {}
paramConfigAdicionalesMAIN['MAIN_copyright'] = [__copyright__, 'str', '', 'GrupoMAIN', __copyright__]
paramConfigAdicionalesMAIN['MAIN_version'] = [__version__, 'str', '', 'GrupoMAIN', __version__]
paramConfigAdicionalesMAIN['MAIN_idProceso'] = [MAIN_idProceso, 'str', '', 'GrupoMAIN']
paramConfigAdicionalesMAIN['MAINusuario'] = [MAINusuario, 'str', '', 'GrupoMAIN']
paramConfigAdicionalesMAIN['MAINmiRutaProyecto'] = [MAIN_PROJ_DIR, 'str', '', 'GrupoMAIN']
paramConfigAdicionalesMAIN['MAIN_ENTORNO'] = [MAIN_ENTORNO, 'str', '', 'GrupoMAIN']
paramConfigAdicionalesMAIN['MAIN_PC'] = [MAIN_PC, 'str', '', 'GrupoMAIN']
paramConfigAdicionalesMAIN['MAIN_DRIVE'] = [MAIN_DRIVE, 'str', '', 'GrupoMAIN']
paramConfigAdicionalesMAIN['MAIN_HOME_DIR'] = [MAIN_HOME_DIR, 'str', '', 'GrupoDirsFiles']
paramConfigAdicionalesMAIN['MAIN_FILE_DIR'] = [MAIN_FILE_DIR, 'str', '', 'GrupoDirsFiles']
paramConfigAdicionalesMAIN['MAIN_PROJ_DIR'] = [MAIN_PROJ_DIR, 'str', '', 'GrupoDirsFiles']
paramConfigAdicionalesMAIN['MAIN_RAIZ_DIR'] = [MAIN_RAIZ_DIR, 'str', '', 'GrupoDirsFiles']
paramConfigAdicionalesMAIN['MAIN_RAIZ_DIR'] = [MAIN_RAIZ_DIR, 'str', '', 'GrupoDirsFiles']
paramConfigAdicionalesMAIN['MAIN_THIS_DIR'] = [MAIN_THIS_DIR, 'str', '', 'GrupoDirsFiles']
paramConfigAdicionalesMAIN['MAIN_WORK_DIR'] = [MAIN_WORK_DIR, 'str', '', 'GrupoDirsFiles']
# ==============================================================================
# En calendula, no uso la MAINrutaRaiz que haya en el fichero de configuracion.
paramConfigAdicionalesMAIN['MAINrutaRaiz'] = [MAINrutaRaiz, 'str', '', 'GrupoDirsFiles', MAINrutaRaiz]
# Creo el parametro MAIN_RAIS_DIR, que no esta en el fichero de configuracion y que depende del entorno
paramConfigAdicionalesMAIN['MAIN_RAIS_DIR'] = [MAIN_RAIS_DIR, 'str', '', 'GrupoDirsFiles', MAIN_RAIS_DIR]
# Creo el parametro MAIN_MDLS_DIR, que no esta en el fichero de configuracion y que depende del entorno
paramConfigAdicionalesMAIN['MAIN_MDLS_DIR'] = [MAIN_MDLS_DIR, 'str', '', 'GrupoDirsFiles', MAIN_MDLS_DIR]
# ==============================================================================
if CONFIGverbose:
    print(f'\nclidaux-> D Llamo a clidconfig.leerCambiarVariablesGlobales<> (con paramConfigAdicionalesMAIN)')
    print(f'{TB}para guardar parametros de configuracion adicionales en el fichero cfg.')
GLOBALconfigDict = clidconfig.leerCambiarVariablesGlobales(
    LCL_idProceso=MAIN_idProceso,
    nuevosParametroConfiguracion=paramConfigAdicionalesMAIN,
    inspect_stack=inspect.stack(),
    verbose=False,
)
if CONFIGverbose:
    print(f'clidaux-> E Cargando parametros de configuracion GLOBALconfigDict en GLO')
GLO = clidconfig.VariablesGlobales(GLOBALconfigDict)

# Esto ya no hace falta porque recargo todas las GLO:
# GLO.MAINrutaRaiz = MAINrutaRaiz
# GLO.MAIN_RAIS_DIR = MAIN_RAIS_DIR
# GLO.MAIN_MDLS_DIR = MAIN_MDLS_DIR
# GLO.MAIN_idProceso = MAIN_idProceso

# ==============================================================================
print(f'\n{"":_^80}')
print(f'clidaux-> Al importar clidaux se asignan las variables globales con directorios MAIN_...')
print(f'{TB}como propiedades de GLO y se guardan en el fichero de configuracion cfg.')
print(f'{TB}-> Este modulo:     {__name__}')
print(f'{TB}-> Importado desde: {callingModulePrevio}')
print(f'{TB}-> Modulo inicial:  {callingModuleInicial}')
print(f'{TB}-> MAIN_FILE_DIR: {MAIN_FILE_DIR}')
print(f'{TB}-> MAIN_BASE_DIR: {MAIN_BASE_DIR}')
print(f'{TB}-> MAIN_PROJ_DIR: {MAIN_PROJ_DIR}')
print(f'{TB}-> MAIN_RAIZ_DIR: {MAIN_RAIZ_DIR}')
print(f'{TB}-> =============')
print(f'{TB}-> MAIN_RAIS_DIR: {MAIN_RAIS_DIR}')
print(f'{TB}-> =============')
print(f'{TB}-> MAINrutaRaiz:  {MAINrutaRaiz}')
print(f'{TB}-> MAIN_MDLS_DIR: {MAIN_MDLS_DIR}')
print(f'{TB}-> =============')
print(f'{TB}-> MAIN_THIS_DIR: {MAIN_THIS_DIR}')
print(f'{TB}-> MAIN_WORK_DIR: {MAIN_WORK_DIR}')
print(f'{TB}-> MAIN_HOME_DIR: {MAIN_HOME_DIR}')
print(f'{"":=^80}')
# ==============================================================================

# ==============================================================================
if callingModuleInicial == 'clidflow':
    printMsgToFile = False
else:
    printMsgToFile = True
# ==============================================================================o
def printMsg(mensaje='', outputFileLas=True, verbose=True, newLine=True, end=None):
    if verbose:
        if not end is None:
            print(mensaje, end=end)
        elif not newLine:
            end=''
            print(mensaje, end=end)
        else:
            end=''
            print(mensaje)
    if printMsgToFile and outputFileLas:
        try:
            if 'controlFileLas' in dir(GLO) and GLO.controlFileLas:
                try:
                    GLO.controlFileLas.write(str(mensaje) + end + '\n' if newLine else ' ')
                except:
                    if GLO.controlFileGral:
                        GLO.controlFileGral.write('Error writing control file (1).\n')
            elif 'controlFileGral' in dir(GLO):
                GLO.controlFileGral.write(str(mensaje) + end + '\n' if newLine else ' ')
        except:
            print(f'clidaux-> printMsg: no hay acceso a controlFileLas o controlFileGral.')
            if 'controlFileLasName' in dir(GLO):
                print(f'{TB}-> controlFileLasName:   {GLO.controlFileLasName}')
            if 'GLBLficheroDeControlGral' in dir(GLO):
                print(f'{TB}-> ficheroDeControlGral: {GLO.GLBLficheroDeControlGral}')


# ==============================================================================
# #Puedo usar esta funcion para mensajes individuales y globales
# def mostrarMensaje(mensaje, outputFileLas=True, verbose=True, newLine=True):
#     if verbose:
#         if newLine:
#             print( mensaje )
#         else:
#             print( mensaje, )
#     if outputFileLas and clidconfig.controlFileLas:
#         try:
#             clidconfig.controlFileLas.write(str(mensaje) + '\n' if newLine else ' ')
#         except:
#             if clidconfig.controlFileGral:
#                 clidconfig.controlFileGral.write('Error writing control file (1).\n')
#     else:
#         try:
#             clidconfig.controlFileGral.write(str(mensaje) + '\n' if newLine else ' ')
#         except:
#             print( 'Error writing control file (2).' )


# ==============================================================================
def mensajeError(program_name):
    # https://stackoverflow.com/questions/1278705/when-i-catch-an-exception-how-do-i-get-the-type-file-and-line-number
    exc_type, exc_obj, exc_tb = sys.exc_info()
    # ==================================================================
    # tb = traceback.extract_tb(exc_tb)[-1]
    # lineError = tb[1]
    # funcError = tb[2]
    try:
        lineasTraceback = list((traceback.format_exc()).split('\n'))
        codigoConError = lineasTraceback[2]
    except:
        codigoConError = ''
    # ==================================================================
    fileNameError = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    lineError = exc_tb.tb_lineno
    funcError = os.path.split(exc_tb.tb_frame.f_code.co_name)[1]
    typeError = exc_type.__name__
    try:
        descError = exc_obj.strerror
    except:
        descError = exc_obj
    sys.stderr.write(f'\nOps! Ha surgido un error inesperado.\n')
    sys.stderr.write(f'Si quieres contribuir a depurar este programa envía el\n')
    sys.stderr.write(f'texto que aparece a continacion a: cartolidar@gmail.com\n')
    sys.stderr.write(f'\tError en:    {fileNameError}\n')
    sys.stderr.write(f'\tFuncion:     {funcError}\n')
    sys.stderr.write(f'\tLinea:       {lineError}\n')
    sys.stderr.write(f'\tDescripcion: {descError}\n') # = {exc_obj}
    sys.stderr.write(f'\tTipo:        {typeError}\n')
    sys.stderr.write(f'\tError en:    {codigoConError}\n')
    sys.stderr.write(f'Gracias!\n')
    # ==================================================================
    sys.stderr.write(f'\nFor help use:\n')
    sys.stderr.write(f'\thelp for main arguments:         python {program_name}.py -h\n')
    sys.stderr.write(f'\thelp for main & extra arguments: python {program_name}.py -e 1 -h\n')
    # ==================================================================
    # sys.stderr.write('\nFormato estandar del traceback:\n')
    # sys.stderr.write(traceback.format_exc())
    return (lineError, descError, typeError)


# ==============================================================================o
def mostrarVersionesDePythonEnElRegistro(verbose):
    import pytz

    print(f'\n{"":_^80}')
    epoch = datetime(1601, 1, 1, tzinfo=pytz.utc)
    # Ver: https://docs.python.org/2/library/winreg.html
    if sys.version_info[0] == 2:
        print(f'clidaux-> Consultando versiones de python en el registro (Python2)')
        import _winreg as winreg
    else:
        print(f'clidaux-> Consultando versiones de python en el registro (Python3)')
        import winreg

    # key = "HKEY_CURRENT_USER/Environment"
    keys = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
    for key1 in keys:
        key2 = winreg.OpenKey(key1, 'SOFTWARE')
        try:
            key3 = winreg.OpenKey(key2, 'Python')
        except:
            print(f'{TB}-> El registro no tiene la clave SOFTWARE/Python/PythonCore')

        key4txts = ['ContinuumAnalytics', 'PythonCore']
        for key4txt in key4txts:
            try:
                key4 = winreg.OpenKey(key3, key4txt)
                infoKey4 = winreg.QueryInfoKey(key4)
                print(f'{TB}-> Clave: HKEY_LOCAL_MACHINE.SOFTWARE.Python.{key4txt}')
                for indexValue4 in range(infoKey4[1]):
                    print(f'{TB}-> \tValor {indexValue4} {winreg.EnumValue(key4, indexValue4)}')
                if infoKey4[0] > 0:
                    print(f'{TB}-> Versiones de python:')
                for indexKey4 in range(infoKey4[0]):
                    sub_key4 = winreg.EnumKey(key4, indexKey4)
                    key5 = winreg.OpenKey(key4, sub_key4)
                    infoKey5 = winreg.QueryInfoKey(key5)
                    installdatetime = epoch + timedelta(microseconds=infoKey5[2] / 10)
                    print(f'{TB}-> Version: {indexKey4} {sub_key4}, Instalado: {installdatetime}, ->Claves: {infoKey5[0]}, Valores: {infoKey5[1]}')
                    if verbose:
                        if infoKey5[1] != 0:
                            for indexValue5 in range(infoKey5[1]):
                                print(f'{TB}-> \tValor {indexValue5} {winreg.EnumValue(key5, indexValue5)}')
                        for indexKey5 in range(infoKey5[0]):
                            sub_key5 = winreg.EnumKey(key5, indexKey5)
                            key6 = winreg.OpenKey(key5, sub_key5)
                            infoKey6 = winreg.QueryInfoKey(key6)
                            installdatetime = epoch + timedelta(microseconds=infoKey6[2] / 10)
                            print(f'{TB}-> \tClave {indexKey5} {sub_key5}, Instalado: {installdatetime}, ->Claves: {infoKey6[0]}, Valores: {infoKey6[1]}')
                            if infoKey6[1] >= 1:
                                for indexValue6 in range(infoKey6[1]):
                                    print(f'{TB}-> \t\tValor {indexValue6} {winreg.EnumValue(key6, indexValue6)}')
                            if infoKey6[0] != 0:
                                for indexKey6 in range(infoKey6[0]):
                                    sub_key6 = winreg.EnumKey(key6, indexKey6)
                                    key7 = winreg.OpenKey(key6, sub_key6)
                                    infoKey7 = winreg.QueryInfoKey(key7)
                                    installdatetime = epoch + timedelta(microseconds=infoKey7[2] / 10)
                                    print(f'{TB}-> \t\tClave {indexKey6} {sub_key6}, Instalado: {installdatetime}, ->Claves: {infoKey7[0]}, Valores: {infoKey7[1]}')

                                    if infoKey7[1] >= 1:
                                        for indexValue7 in range(infoKey7[1]):
                                            print(f'{TB}-> \t\t\tValor {indexValue7} {winreg.EnumValue(key7, indexValue7)}')

            except:
                print(f'No hay {key4txt} en HKEY_LOCAL_MACHINE.SOFTWARE.Python')
    print(f'{"":=^80}')


# ==============================================================================o
def memoriaRam(marcador='-', verbose=True, swap=False, sangrado=''):
    ramMem = psutil.virtual_memory()
    if verbose:
        if marcador == '-':
            print(
                '%sTotal RAM: %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb'
                % (sangrado, ramMem.total / 1e9, ramMem.used / 1e9, ramMem.available / 1e9)
            )
        else:
            print(
                '%sTotal RAM (%s): %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb'
                % (sangrado, str(marcador), ramMem.total / 1e9, ramMem.used / 1e9, ramMem.available / 1e9)
            )
    if swap:
        swapMem = psutil.swap_memory()
        if verbose:
            print('Total SWAP memory: %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb' % (swapMem.total / 1e9, swapMem.used / 1e9, swapMem.free / 1e9))
    else:
        swapMem = None
    return ramMem, swapMem


# ==============================================================================o
def infoPC(verbosePlus=False):
    print(f'\n{"":_^80}')
    print(f'clidaux-> Sistema operativo:')
    print(f'  OS:       {platform.system()}')
    print(f'  Version:  {platform.release()}')
    print(f'\nIP local: {socket.gethostbyname(socket.gethostname())}')

    print(f'\nHardware:')
    print(f'  CPU totales {psutil.cpu_count()} (fisicas: {psutil.cpu_count(logical=False)})')
    # print( 'CPU times - interrupt:', psutil.cpu_times(percpu=False) )
    # print( 'CPU times - interrupt:', psutil.cpu_times(percpu=True) )
    # print( 'CPU statistics:', psutil.cpu_stats() )
    # print( 'Addresses associated to each NIC (network interface card):' )
    # print( 'Ethernet', psutil.net_if_addrs()['Ethernet'] )
    # print( 'Wi-Fi', psutil.net_if_addrs()['Wi-Fi'] )
    # print( 'Conexion de area local* 11', psutil.net_if_addrs()['Conexi\xf3n de \xe1rea local* 11'] )

    # print( 'Procesos en ejecucion:' )
    # for proc in psutil.process_iter():
    #     try:
    #         pinfo = proc.as_dict(attrs=['pid', 'name'])
    #     except psutil.NoSuchProcess:
    #         pass
    #     else:
    #         print(pinfo)
    # import datetime
    # print( 'FechaHora de inicio:', datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S") )
    print('  Procesador:', platform.processor())
    info = 'No info'
    try:
        info = subprocess.check_output(["wmic", "cpu", "get", "name"])
        info = info.decode('utf-8')
        print('  Version:    %s' % info.split('Name')[1].split('@')[0].lstrip().replace('\r', '').replace('\n', ''))
        print('  Velocidad:  %s' % info.split('@')[1].replace(' ', '').replace('\r', '').replace('\n', ''))
    except:
        print('  subprocess->', info, '<-')

    print('\nMemoria RAM:')
    proc = psutil.Process(os.getpid())
    memoria = proc.memory_info().rss / 1e6
    print('  Memoria utilizada en este proceso (inicial) {:5.1f} [Mb]'.format(memoria))
    memoriaRam(sangrado='  ')
    if verbosePlus:
        print(' ', proc.memory_info())
    print(f'{"":=^80}')

    # import np.distutils.cpuinfo as cpuinfo
    # print( '1.', dir(cpuinfo) )
    # print( 'Procesador de 64 bits:', cpuinfo.CPUInfoBase()._is_64bit() )
    # print( 'Procesador de 32 bits:', cpuinfo.CPUInfoBase()._is_32bit() )
    # print( '3.', cpuinfo.Win32CPUInfo().info )
    # for inf in cpuinfo.Win32CPUInfo().info:
    #    print( inf )
    # print( '4.', cpuinfo.cpuinfo().info )
    # print( '5.', dir(cpuinfo.os) )
    # print( '5.', cpuinfo.os.path )
    # print( '5.', cpuinfo.os.system )
    # print( '6.', dir(cpuinfo.platform) )
    # print( '6.', cpuinfo.platform.version )
    # print( '7.', dir(cpuinfo.sys) )
    # print( '8.', cpuinfo.sys.version )

    if verbosePlus:
        try:
            # print( 'Usuario principal:', psutil.users()[0] )
            print('clidaux-> Nombre de usuario:', psutil.users()[0].name)
            print('  Info usuarios:', psutil.users())
            # print( type(psutil.users()[0]), dir(psutil.users()[0]) )
        except:
            print('clidaux-> Nombre de usuario:', psutil.users())



# ==============================================================================o
def mostrarEntornoDeTrabajo(verbosePlus=False):
    print(f'\n{"":_^80}')
    print('clidaux-> Info sobre Python:')
    print('\t-> Version:      %i.%i' % (sys.version_info[0], sys.version_info[1]))
    print('\t-> Ruta python:  %s' % sys.prefix)
    EXEC_DIR = os.path.dirname(os.path.abspath(sys.executable))
    print('\t-> Ruta binario: %s' % EXEC_DIR)
    print('\t-> Ejecutable:   %s' % sys.executable)

    if sys.version_info[0] == 2:
        pass
        # maximoEntero = sys.maxint
        # numBits = int( math.log(maximoEntero, 2) ) + 2
        # print( '\tNum bits (in python): %i (Max int: %i)' % (numBits, maximoEntero))
    else:
        # Esto solo funciona con python3
        numBits = int(math.log(sys.maxsize, 2)) + 1
        print('  Num bits:     %i (Max int: %i)' % (numBits, sys.maxsize))
        # python3 no tiene una maximo para los enteros
        # Ver: http://docs.python.org/3.1/whatsnew/3.0.html#integers
        # Ver: https://stackoverflow.com/questions/13795758/what-is-sys-maxint-in-python-3
    # Tres formas de leeer una variable de entorno
    # print('  PYTHONHOME (1) ->', os.environ.get('PYTHONHOME'))  # Si no existe devuelve None
    # print('  PYTHONHOME (2) ->', os.getenv('PYTHONHOME', 'PYTHONHOME Sin definir'))
    try:
        print('  PYTHONHOME:  ', os.environ['PYTHONHOME'])
    except:
        print('  PYTHONHOME:   no definida')
    try:
        print('  PYTHONPATH:  ', os.environ['PYTHONPATH'])
    except:
        print('  PYTHONPATH:   no definida')

    print('\nclidaux-> Versiones de algunos paquetes:')
    print('  Version de python:    ', platform.python_version())
    print('  Version de numpy:     ', np.__version__) # <=> np.version.version
    print('  Version de scipy:     ', scipy.__version__) # <=> scipy.version.version
    print('  Version de Numba:     ', numba.__version__)
    endMajor = numba.__version__.find('.')
    endMinor = numba.__version__.find('.', endMajor + 1)
    verMajor = int(numba.__version__[:endMajor])
    if endMinor == -1:
        verMinor = int(numba.__version__[endMajor + 1:])
    else:
        verMinor = int(numba.__version__[endMajor + 1: endMinor])
    if verMajor == 0 and verMinor < 53:
        print('   -> Atencion: recomendable actualizar numba a 0.53.0')
    print('  Version de gdal:      ', gdal.VersionInfo())
    try:
        import pyproj
        print('  Version de pyproj:    ', pyproj.__version__)
        print('  Version de PROJ:      ', pyproj.__proj_version__)
        if verbosePlus:
            print('\nclidaux-> Mostrando info de pyproj:')
            print(pyproj.show_versions())
    except:
        print('  pyproj no disponible')
    print(f'{"":=^80}')


# ==============================================================================o
def mostrar_directorios(verbosePlus=False):
    print(f'\n{"":_^80}')
    print('clidaux-> Modulos y directorios de la aplicacion:')
    print('\t-> Modulos de la aplicacion:')
    print('\t\t-> Modulo principal (sys.argv[0]) {}'.format(sys.argv[0]))
    print('\t\t-> Este modulo  (__file__):       {}'.format(__file__)) # MAIN_FILE_DIR
    print('\t-> Directorios de la aplicacion:')
    print('\t\t-> Proyecto     (MAIN_PROJ_DIR):  {}'.format(MAIN_PROJ_DIR))
    print('\t\t-> Raiz         (MAIN_RAIZ_DIR):  {}'.format(MAIN_RAIZ_DIR))
    print('\t-> Directorio desde el que se llama a la aplicacion:')
    print('\t\t-> Lanzadera    (MAIN_THIS_DIR):  {}'.format(MAIN_THIS_DIR))
    print('\t\t-> Actual       (MAIN_WORK_DIR):  {}'.format(MAIN_WORK_DIR))
    print('\t-> Directorio del usuario:')
    print('\t\t-> User-home    (MAIN_HOME_DIR):  {}'.format(MAIN_HOME_DIR))
    if len(sys.argv) > 3:
        print('\t-> Argumentos en linea de comandos:')
        print('\t\t-> Args: {}'.format(sys.argv[3:]))
    print(f'{"":=^80}')


# ==============================================================================o
def buscarDirectorioDeTrabajo():
    MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    directorioActual = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))  # Equivale a MAIN_FILE_DIR = pathlib.Path(__file__).parent
    filenameAPP = os.path.join(directorioActual, 'clidbase.py')
    if os.path.exists(filenameAPP):
        directorioDeTrabajo = directorioActual
    else:
        directorioPadre = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        # directorioPadre = quitarContrabarrasAgregarBarraFinal(directorioPadre)
        directorioPadre = (directorioPadre).replace(os.sep, '/')

        filenameAPP = os.path.join(directorioPadre, 'clidbase.py')
        if os.path.exists(filenameAPP):
            directorioDeTrabajo = directorioPadre
        else:
            directorioDeTrabajo = MAIN_FILE_DIR
    return directorioDeTrabajo


# ==============================================================================o
# Version original de esta funcion, si se modifica, copiarla en clidhead.py
def buscarDirectorioDataExt():
    dataFiles = []
    dataExtPathFound = False
    dataExtPath = os.path.abspath(os.path.join(MAIN_FILE_DIR, GLO.MAINrutaDataExt))
    dataExtIoPath = os.path.join(dataExtPath, 'io')
    if os.path.isdir(dataExtIoPath):
        for (_, _, filenames) in os.walk(dataExtIoPath):
            break
        dataFiles = [
            filename for filename in filenames
            if filename[-4:].lower() == '.txt'
            or filename[-4:].lower() == '.cfg'
            or filename[-4:].lower() == '.csv'
            or filename[-4:].lower() == '.xls'
            or filename[-5:].lower() == '.xlsx'
            or filename[-5:].lower() == '.xlsm'
        ]
        if dataFiles:
            return dataExtPath
        else:
            print(f'clidaux-> No hay ficheros de configuracion ni auxiliares (cfg, txt, csv, xls*) en {dataExtPath}')
    else:
        print(f'clidaux-> Buscando ruta con ficheros de configuracion y auxiliares:')
        print(f'{TB}-> La ruta {dataExtPath} no existe.')

    dataExtPath = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..', GLO.MAINrutaDataExt))
    dataExtIoPath = os.path.join(dataExtPath, 'io')
    print(f'{TB}-> Se prueba un nivel de directorios superior: {dataExtPath}')
    if os.path.isdir(dataExtIoPath):
        for (_, _, filenames) in os.walk(dataExtIoPath):
            break
        dataFiles = [
            filename for filename in filenames
            if filename[-4:].lower() == '.txt'
            or filename[-4:].lower() == '.cfg'
            or filename[-4:].lower() == '.csv'
            or filename[-4:].lower() == '.xls'
            or filename[-5:].lower() == '.xlsx'
            or filename[-5:].lower() == '.xlsm'
        ]
        if dataFiles:
            return dataExtPath
        else:
            print(f'clidaux-> No hay ficheros de configuracion ni auxiliares (cfg, txt, csv, xls*) en {dataExtPath}')
    else:
        print(f'clidaux-> Buscando ruta con ficheros de configuracion y auxiliares: la ruta {dataExtPath} no existe.')

    dataExtPath = os.path.abspath(GLO.MAINrutaDataExt)
    dataExtIoPath = os.path.join(dataExtPath, 'io')
    print(f'{TB}-> Se prueba una ruta equivalente en el directorio de trabajo: {dataExtPath}')
    if os.path.isdir(dataExtIoPath):
        for (_, _, filenames) in os.walk(dataExtIoPath):
            break
        dataFiles = [
            filename for filename in filenames
            if filename[-4:].lower() == '.txt'
            or filename[-4:].lower() == '.cfg'
            or filename[-4:].lower() == '.csv'
            or filename[-4:].lower() == '.xls'
            or filename[-5:].lower() == '.xlsx'
            or filename[-5:].lower() == '.xlsm'
        ]
        if dataFiles:
            return dataExtPath
        else:
            print(f'clidaux-> No hay ficheros de configuracion ni auxiliares (cfg, txt, csv, xls*) en {dataExtPath}')
    else:
        print(f'clidaux-> Buscando ruta con ficheros de configuracion y auxiliares: la ruta {dataExtPath} tampoco existe.')

    dataExtPath = buscarDirectorioDeTrabajo()
    dataExtIoPath = os.path.join(dataExtPath, 'io')
    print(f'{TB}-> Se buscan los ficheros de configuracion y auxiliares en el directorio de trabajo: {dataExtPath}')
    if os.path.isdir(dataExtIoPath):
        for (_, _, filenames) in os.walk(dataExtIoPath):
            break
        dataFiles = [
            filename for filename in filenames
            if filename[-4:].lower() == '.txt'
            or filename[-4:].lower() == '.cfg'
            or filename[-4:].lower() == '.csv'
            or filename[-4:].lower() == '.xls'
            or filename[-5:].lower() == '.xlsx'
            or filename[-5:].lower() == '.xlsm'
        ]
        if dataFiles:
            return dataExtPath
        else:
            print(f'clidaux-> No se ha encontrado la ruta de los ficheros de configuracion ni auxiliares (cfg, txt, csv, xls*) en {dataExtPath}')
            print(f'{TB}-> Cambiar el parametro MAINrutaDataExt en el fichero de configuracion:')
            print(f'{TB}-> Indicar ruta relativa o absoluta a los ficheros cfg, txt, csv, xls*. Por ejemplo: D:/data/ext')
            dataExtPath = None
            sys.exit(1)
    else:
        print(f'clidaux-> Buscando ruta con ficheros de configuracion y auxiliares: la ruta {dataExtPath} tampoco existe.')
        print(f'{TB}-> Cambiar el parametro MAINrutaDataExt en el fichero de configuracion:')
        print(f'{TB}-> Indicar ruta relativa o absoluta a los ficheros cfg, txt, csv, xls*. Por ejemplo: D:/data/ext')
        dataExtPath = None
        sys.exit(1)

    return dataExtPath


# ==============================================================================o
# ooooooooooooooooooooooooo Librerias para los ajustes oooooooooooooooooooooooooo
try:
    if GLO.GLBLusarSklearn:
        print('Importando sklearn')
        from sklearn import linear_model

        # from sklearn.metrics import mean_squared_error
        print('sklearn importado')
    else:

        class linear_model:
            def __init__(self):
                pass

            def LinearRegression(self):
                return None

        # def mean_squared_error(array1, array2):
        #    return 0
    # ==============================================================================o
    if GLO.GLBLusarSklearn:
        clf = linear_model.LinearRegression()
    else:
        clf = None
    if GLO.GLBLusarStatsmodels:
        print('Importando statsmodel.api')
        # import statsmodels.api as sm
        print('statsmodel importado')
    else:
        class Foo:
            def __init__(self):
                pass
            def fit(self):
                return None
        class sm:
            def __init__(self):
                pass
            def OLS(self, endog=None, exog=None):
                foo = Foo()
                return foo
except:
    pass
# ==============================================================================o
# El paquete scikit me da problemas para empaquetarlo con pyinstaller
# No se compila bien con numba
# ==============================================================================o
def ajustarPlanoSinNumba(listaCoordenadas, nX, nY):
    nPtosAjuste = len(listaCoordenadas)
    if nPtosAjuste < 3:
        return [0, 0, 0, -1]
    z_true = listaCoordenadas[:, 2]
    if GLO.GLBLusarSklearn:
        x_y_values = listaCoordenadas[:, 0:2]
        clf.fit(x_y_values, z_true)
        z_est = clf.intercept_ + (clf.coef_[0] * x_y_values[:, 0]) + (clf.coef_[1] * x_y_values[:, 1])
        print('-->z_est:', z_est)
        # mse = ( ((mean_squared_error(z_true, z_est))**0.5) *
        #                nPtosAjuste / (nPtosAjuste-1) )
        mse = (((np.square(z_true - z_est)).mean(axis=0)) ** 0.5) * nPtosAjuste / (nPtosAjuste - 1)
        coeficientes = [clf.intercept_, clf.coef_[0], clf.coef_[1], mse]
        return coeficientes

    if GLO.GLBLusarStatsmodels:
        # Ver:            http://stackoverflow.com/questions/11479064/multivariate-linear-regression-in-python
        # Paquete:    http://statsmodels.sourceforge.net/devel/
        # OLS:            http://statsmodels.sourceforge.net/devel/regression.html
        # Detalles: http://statsmodels.sourceforge.net/devel/generated/statsmodels.regression.linear_model.RegressionResults.html#statsmodels.regression.linear_model.RegressionResults
        x_y_values = [[1, punto[0], punto[1]] for punto in listaCoordenadas]
        results = sm.OLS(endog=z_true, exog=x_y_values).fit()
        z_est = [results.params[0] + (results.params[1] * punto[0]) + (results.params[2] * punto[1]) for punto in listaCoordenadas]
        coeficientes = results.params
        coeficientes.append.results.mse_resid ** 0.5
        # if nX == celdaX and nY == celdaY and mostrarAjuste:
        #    print( 'Coeficientes estimados con statsmodel (A0, A1, intercept):', results.params )
        #    print( 'Coordenadas:', nX, nY )
        #    print( 'Lista de valores x, y:                         ', x_y_values )
        #    print( 'Lista de valores z:                                ', z_true )
        #    print( 'Lista de valores ajustados:                ', results.fittedvalues )
        #    print( 'Lista de valores ajustados (z_est):', z_est )
        #    print( 'Lista de residuos (z_real-z_est):    ', results.resid )
        #    #Lo siguiente permitiria generar un fichero con los ajustes del plano-suelo de cada celda 10x10
        #    print( 'results.params[0], results.params[1], results.params[2]', results.params[0], results.params[1], results.params[2] )
        #    print( results.summary() )
        #    #print( results.summary2() )
        #    #print( 'Error cuadratico medio residual: %f (total: %f; R2: %f)' %\
        #    #             (results.mse_resid, results.mse_total, 100*results.mse_resid/results.mse_total) )
        #    #print( 'Error standar medio residual: %f m', (results.mse_resid**0.5) )
        #    #print( 'Suma de cuadrados (mse_resid x nobs)', results.ssr )
        #    #print( 'rsquared:', results.rsquared )
        return coeficientes


# ==============================================================================o
def leerPropiedadDePunto(ptoEnArray, txtPropiedad, miHead, lasPointFieldOrdenDict, lasPointFieldPropertiesDict):
    # Leer propiedades de los puntos guardados en el array aCeldasListaDePtosTlcAll[] o aCeldasListaDePtosTlcPralPF8[] y aCeldasListaDePtosAux[]
    # Por el momento lo guardo siempre como lista de propiedades sin interpretar (posiblemente implemente tb como string)
    if type(ptoEnArray) == np.ndarray or type(ptoEnArray) == list or type(ptoEnArray) == tuple or type(ptoEnArray) == np.void:
        if txtPropiedad == 'x':
            valorPropiedad = (ptoEnArray[lasPointFieldOrdenDict[txtPropiedad]] * miHead['xscale']) + miHead['xoffset']
        elif txtPropiedad == 'y':
            valorPropiedad = (ptoEnArray[lasPointFieldOrdenDict[txtPropiedad]] * miHead['yscale']) + miHead['yoffset']
        elif txtPropiedad == 'z':
            valorPropiedad = (ptoEnArray[lasPointFieldOrdenDict[txtPropiedad]] * miHead['zscale']) + miHead['zoffset']
        elif txtPropiedad in lasPointFieldOrdenDict.keys():
            valorPropiedad = ptoEnArray[lasPointFieldOrdenDict[txtPropiedad]]
        elif (
            txtPropiedad == 'scan_angle_rank'
            or txtPropiedad == 'user_data'
            or txtPropiedad == 'raw_time'
            or txtPropiedad == 'red'
            or txtPropiedad == 'green'
            or txtPropiedad == 'blue'
        ):
            # Propiedades que no se alacenan si GLBLalmacenarPuntosComoNumpyDtypeMini
            # TODO: ver si las consecuencias van mas alla de generar algunas salidas con todos los valores nulos
            valorPropiedad = 0
        else:
            if txtPropiedad == 'nRetorno' or txtPropiedad == 'totalRetornos' or txtPropiedad == 'scan_dir' or txtPropiedad == 'esPuntoEdge':
                return_grp = ptoEnArray[lasPointFieldOrdenDict['return_grp']]
            else:
                valorPropiedad = 0
                print('Propiedad no contemplada en el formato de punto usado:', txtPropiedad)
                print('ptoEnArray:', type(ptoEnArray), ptoEnArray)
                input('Implementar esto si ha lugar 2')
    elif type(ptoEnArray) == str or type(ptoEnArray) == bytes:
        if txtPropiedad in lasPointFieldPropertiesDict.keys():
            posIni = lasPointFieldPropertiesDict[txtPropiedad][3]
            posFin = lasPointFieldPropertiesDict[txtPropiedad][3] + lasPointFieldPropertiesDict[txtPropiedad][0]
            fmt = lasPointFieldPropertiesDict[txtPropiedad][1]
            valor = struct.unpack(fmt, ptoEnArray[posIni:posFin])[0]
            if txtPropiedad == 'x':
                valorPropiedad = (valor * miHead['xscale']) + miHead['xoffset']
            elif txtPropiedad == 'y':
                valorPropiedad = (valor * miHead['yscale']) + miHead['yoffset']
            elif txtPropiedad == 'z':
                valorPropiedad = (valor * miHead['zscale']) + miHead['zoffset']
            else:
                valorPropiedad = valor
        else:
            if txtPropiedad == 'nRetorno' or txtPropiedad == 'totalRetornos' or txtPropiedad == 'scan_dir' or txtPropiedad == 'esPuntoEdge':
                posIni = lasPointFieldPropertiesDict['return_grp'][3]
                posFin = lasPointFieldPropertiesDict['return_grp'][3] + lasPointFieldPropertiesDict['return_grp'][0]
                fmt = lasPointFieldPropertiesDict['return_grp'][1]
                return_grp = struct.unpack(fmt, ptoEnArray[posIni:posFin])[0]
            else:
                valorPropiedad = 0
                print('Propiedad no contemplada en el formato de punto usado:', txtPropiedad)
                print('ptoEnArray:', type(ptoEnArray), ptoEnArray)
                input('Implementar esto si ha lugar 3')
    else:
        print('Tipo de dato:', type(ptoEnArray))
        input('No contemplo otras opciones de guardar punto en el array -> revisar si hay que implementar esto')

    # Provisional: quitar el try cuando vea que funciona
    try:
        if txtPropiedad == 'nRetorno' or txtPropiedad == 'totalRetornos' or txtPropiedad == 'scan_dir' or txtPropiedad == 'esPuntoEdge':
            if txtPropiedad == 'esPuntoEdge':
                valorPropiedad = return_grp & 0b10000000
            elif txtPropiedad == 'scan_dir':
                valorPropiedad = return_grp & 0b01000000
            elif txtPropiedad == 'totalRetornos':
                valorPropiedad = return_grp & 0b00111000
            elif txtPropiedad == 'nRetorno':
                valorPropiedad = return_grp & 0b111
            else:
                valorPropiedad = 0
    except:
        print('clidaux-> ATENCION error: tipo de dato:', type(ptoEnArray))
    return valorPropiedad


# ==============================================================================o
def estaDentro(x, y, poly):
    n = len(poly)
    estaDentro = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        estaDentro = not estaDentro
        p1x, p1y = p2x, p2y
    return estaDentro


# # ==============================================================================o
# def quitarContrabarrasAgregarBarraFinal(ruta=''):
#     if not ruta:
#         return None
#     nuevaRuta = ruta.replace(os.sep, '/')
#     # nuevaRuta = ''
#     # for letra in ruta:
#     #     letraSinBackslash = letra if letra != '\\' else '/'
#     #     nuevaRuta += letraSinBackslash
#     # if nuevaRuta[-1:] != '/':
#     #     nuevaRuta += '/'
#     nuevaRuta = os.path.dirname(nuevaRuta.replace('//', '/'))
#     return nuevaRuta


# ==============================================================================o
def generar_tfw():
    # import gdal
    # path, gen_prj
    infile = 'O:/Sigmena/usuarios/COMUNES/Bengoa/SIC/cartolidar/JAEscudero/tif1/AltMdb95_LoteAsc.tif'
    src = gdal.Open(infile)
    xform = src.GetGeoTransform()

    #     if gen_prj == 'prj':
    #             src_srs = osr.SpatialReference()
    #             src_srs.ImportFromWkt(src.GetProjection())
    #             src_srs.MorphToESRI()
    #             src_wkt = src_srs.ExportToWkt()
    #
    #             prj = open(os.path.splitext(infile)[0] + '.prj', 'wt')
    #             prj.write(src_wkt)
    #             prj.close()

    src = None
    edit1 = xform[0] + xform[1] / 2
    edit2 = xform[3] + xform[5] / 2
    print('xform:', xform)
    print('edit1:', edit1)
    print('edit2:', edit2)
    print(os.path.splitext(infile)[0])

    tfw = open(os.path.splitext(infile)[0] + '.tfw', 'wt')
    tfw.write("%0.8f\n" % xform[1])
    tfw.write("%0.8f\n" % xform[2])
    tfw.write("%0.8f\n" % xform[4])
    tfw.write("%0.8f\n" % xform[5])
    tfw.write("%0.8f\n" % edit1)
    tfw.write("%0.8f\n" % edit2)
    tfw.close()


# ==============================================================================o
# https://code.tutsplus.com/tutorials/understand-how-much-memory-your-python-objects-use--cms-25609
# https://stackoverflow.com/questions/14372006/variables-memory-size-in-python
# getsizeof() function doesn't return the actual memory of the objects,
# but only the memory of the pointers to objects.
# En el caso de una lista: memory of the list and the pointers to its objects
def mostrarSizeof(x, level=0):
    print("\t" * level, x.__class__, sys.getsizeof(x), x)
    if hasattr(x, '__iter__'):
        if hasattr(x, 'items'):
            for xx in x.items():
                mostrarSizeof(xx, level + 1)
        else:
            for xx in x:
                mostrarSizeof(xx, level + 1)


# ==============================================================================o
# https://code.tutsplus.com/tutorials/understand-how-much-memory-your-python-objects-use--cms-25609
def deep_getsizeof(o, ids):
    """Find the memory footprint of a Python object
 
    This is a recursive function that drills down a Python object graph
    like a dictionary holding nested dictionaries with lists of lists
    and tuples and sets.
 
    The sys.getsizeof function does a shallow size of only. It counts each
    object inside a container as pointer only regardless of how big it
    really is.
 
    :param o: the object
    :param ids:
    :return:
    """
    d = deep_getsizeof
    if id(o) in ids:
        return 0
 
    r = sys.getsizeof(o)
    ids.add(id(o))
 
    if isinstance(o, str):
        return r
 
    if isinstance(o, collections.Mapping):
        try:
            return r + sum(d(k, ids) + d(v, ids) for k, v in o.iteritems())
        except:
            return 0
 
    if isinstance(o, collections.Container):
        return r + sum(d(x, ids) for x in o)
 
    return r 


# ==============================================================================o
def procesoActivo():
    return psutil.Process(os.getpid())


# ==============================================================================o
def mostrarPropiedadesDeUnObjetoClase(
        myObjectClass,
        myClassObjectName='miObjeto',
        mostrarBuiltin=False,
        mostrarVariables=True,
        mostrarMetodos=False,
        sizeMaxKbParaMostrar=1.0):
    sumaBuiltinKb = 0
    sumaMetodosKb = 0
    sumaVariablesKb = 0
    printMsg('\nclidaux-> Mostrando propiedades del objeto/clase {}:'.format(myClassObjectName))
    for nombrePropiedad in dir(myObjectClass):
        valorPropiedad = getattr(myObjectClass, nombrePropiedad)
        sizePropiedadKb = deep_getsizeof(valorPropiedad, set()) / 1E3
        if nombrePropiedad[:2] == '__' and nombrePropiedad[-2:] == '__':
            esBuiltin = True
        else:
            esBuiltin = False

        if (
            isinstance(valorPropiedad, bool)
            or isinstance(valorPropiedad, str)
            or isinstance(valorPropiedad, int)
            or isinstance(valorPropiedad, float)
            or isinstance(valorPropiedad, complex)
            or isinstance(valorPropiedad, list)
            or isinstance(valorPropiedad, tuple)
            or isinstance(valorPropiedad, range)
            or isinstance(valorPropiedad, dict)
            or isinstance(valorPropiedad, bytes)
            or isinstance(valorPropiedad, bytearray)
            or isinstance(valorPropiedad, memoryview)
            or isinstance(valorPropiedad, set)
            or isinstance(valorPropiedad, frozenset)
            or isinstance(valorPropiedad, np.ndarray)
            # https://docs.python.org/3/library/stdtypes.html
        ):
            tipoPropiedad = 'variable'
        elif isinstance(valorPropiedad, types.FunctionType):
            tipoPropiedad = 'function'
        elif isinstance(valorPropiedad, types.MethodType):
            tipoPropiedad = 'method'
        elif isinstance(valorPropiedad, types.ModuleType):
            tipoPropiedad = 'modulo'
        elif isinstance(valorPropiedad, types.CodeType):
            tipoPropiedad = 'codeType'
        elif isinstance(valorPropiedad, types.BuiltinFunctionType):
            tipoPropiedad = 'builtinFun'
        elif isinstance(valorPropiedad, types.BuiltinMethodType):
            tipoPropiedad = 'builtinMet'
        elif isinstance(valorPropiedad, types.MethodWrapperType):
            tipoPropiedad = 'wrapper'
        elif (
            isinstance(valorPropiedad, types.MethodDescriptorType)
            or isinstance(valorPropiedad, types.WrapperDescriptorType)
            or isinstance(valorPropiedad, types.GetSetDescriptorType)
        ):
            tipoPropiedad = 'descriptor'
        else:
            tipoPropiedad = 'otros'

        if esBuiltin:
            sumaBuiltinKb += sizePropiedadKb
            if not mostrarBuiltin:
                continue

        if tipoPropiedad == 'variable':
            sumaVariablesKb += sizePropiedadKb
            if not mostrarVariables:
                continue
            try:
                variableShape = valorPropiedad.shape
            except:
                variableShape = [0]
            try:
                variableLen = len(valorPropiedad)
            except:
                variableLen = -1
        else:
            sumaMetodosKb += sizePropiedadKb
            if not mostrarMetodos:
                continue
            variableShape = None
            variableLen = None

        if nombrePropiedad == 'ficheroCompletoEnLaRAM':
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30} --->No se muestra por incluir todo el fichero las. nElem: {}'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableLen
                )
            )
            continue
        elif sizePropiedadKb > sizeMaxKbParaMostrar: 
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}--->Muy grande-> nElem: {} variableShape: {}'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableLen, variableShape
                )
            )
            continue
        elif len(variableShape) > 1 and (variableShape[0] > 5 or variableShape[1] > 5):
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}--->Array de Shape: {}'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableShape
                )
            )
            continue
        elif (isinstance(valorPropiedad, list) or isinstance(valorPropiedad, tuple)) and variableLen > 10:
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}--->Lista/tupla con {} elementos'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableLen
                )
            )
            continue
        elif isinstance(valorPropiedad, dict) and variableLen > 10:
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}--->Diccionario con {} elementos'.format(
                    sizePropiedadKb, nombrePropiedad, tipoPropiedad, str(type(valorPropiedad)), variableLen
                )
            )
            continue

        try:
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}: {}'.format(
                    sizePropiedadKb,
                    nombrePropiedad,
                    tipoPropiedad,
                    str(type(valorPropiedad)),
                    str(valorPropiedad)
                )
            )
        except:
            printMsg(
                '->memSize: {:08.1f} Kb {:>35} {:>10}->{:<30}: ATENCION, no se puede mostrar'.format(
                    sizePropiedadKb,
                    nombrePropiedad,
                    tipoPropiedad,
                    str(type(valorPropiedad))
                )
            )

    printMsg('\n{:o^80}'.format(''))
    printMsg('clidaux-> Size suma de builtins  de la clase {}: {:05.1f} Mb'.format(myClassObjectName, sumaBuiltinKb / 1E3))
    printMsg('clidaux-> Size suma de metodos   de la clase {}: {:05.1f} Mb'.format(myClassObjectName, sumaMetodosKb / 1E3))
    printMsg('clidaux-> Size suma de variables de la clase {}: {:05.1f} Mb'.format(myClassObjectName, sumaVariablesKb / 1E3))
    printMsg('clidaux-> Size acum de b&m&v     de la clase {}: {:05.1f} Mb'.format(myClassObjectName, sumaVariablesKb / 1E3))
    printMsg('{:o^80}\n'.format(''))


# ==============================================================================o
def controlarAvance(contador, x=0, y=0, z=0, intervalo=1e6):
    if contador != 0 and contador % intervalo == 0:
        ramMem, _ = memoriaRam('0', False)
        if intervalo == 1e6:
            print(
                'clidaux-> %i %s x: %0.0f, y: %0.0f, z: %0.1f. Mem disp: %0.1f Mb'
                % (contador / intervalo, 'millon ptos.  ' if contador / intervalo == 1 else 'millones ptos.', x, y, z, ramMem.available / 1e6)
            )
        else:
            print('clidaux-> %i %s x: %0.0f, y: %0.0f, z: %0.1f. Mem disp: %0.1f Mb' % (contador, 'ptos.', x, y, z, ramMem.available / 1e6))

    if contador % (intervalo / 10) == 0:
        ramMem, _ = memoriaRam('99', False)
        if ramMem.available / 1e6 < GLO.GLBLminimoDeMemoriaRAM:
            print('clidaux-> Puede haber problemas de memoria:')
            memoriaRam('2', True)
            time.sleep(5)
            gc.collect()
            ramMem, _ = memoriaRam('99', False)
            if ramMem.available / 1e6 < GLO.GLBLminimoDeMemoriaRAM:
                print('clidaux-> Confirmado:')
                memoriaRam('3', True)
                return False
            else:
                print('clidaux-> Eran solo dificultades transitorias; memoria RAM disponible: %0.2f Mb' % (ramMem.available / 1e6))
    return True


# ==============================================================================o
def mostrarMemoriaOcupada(miLasClass):
    print('Memoria ocupada por miLasClass:')
    propiedades = [p for p in dir(miLasClass) if isinstance(getattr(miLasClass, p), property)]
    print('\nChequeo la memoria ocupada por las propiedades de miLasClass:', propiedades)
    for p in dir(miLasClass):
        try:
            if type(getattr(miLasClass, p)) in [bool, str, int, float]:
                # [types.NoneType, types.BooleanType, types.StringType, types.IntType, types.LongType, types.FloatType]:
                pass
            elif type(getattr(miLasClass, p)) in [type, dict]:
                # [types.TypeType, types.DictionaryType, types.ModuleType, types.ClassType, types.InstanceType, types.MethodType]:
                pass
            elif sys.getsizeof(getattr(miLasClass, p)) / 1e3 > 1:
                print('\s\t%0.2f MB\t' % (p, sys.getsizeof(getattr(miLasClass, p)) / 1e6), type(getattr(miLasClass, p)), '\t', getattr(miLasClass, p))
            else:
                print('\s\t%0.2f MB\t' % (p, sys.getsizeof(getattr(miLasClass, p)) / 1e6), type(getattr(miLasClass, p)), '\t', getattr(miLasClass, p))
            # elif getattr(miLasClass, p).nbytes / 1e3 > 1:
            #    print( '\s\t%0.2f MB\t' % (p, p.nbytes/1e6), type(getattr(miLasClass, p)), '\t', getattr(miLasClass, p) )
        except:
            print('Error al mostrar la memoria ocupada por', p, type(getattr(miLasClass, p)), getattr(miLasClass, p))
    print('\nVariables de miLasClass:')
    # for variableDeMiBloque in vars(miLasClass).keys():
    #    print( variableDeMiBloque, '\t', vars(miLasClass)[variableDeMiBloque] )


# ==============================================================================o
def interrumpoPorFaltaDeRAM(contador, totalPoints, miLasClass):
    elMensaje = '\nATENCION:\t\tInterrumpo el preprocesado para evitar problemas de memoria RAM (lectura de fichero completo).\n'
    clidconfig.controlFileGral.write(elMensaje)
    printMsg(elMensaje)
    if contador > totalPoints * 0.5:
        elMensaje = 'Puntos leidos:\t\t%i (<1/2). Continuo con los puntos ya procesados en primera vuelta.' % (contador)
        clidconfig.controlFileGral.write(elMensaje)
        printMsg(elMensaje)
    else:
        elMensaje = 'Puntos leidos:\t\t%i (<1/2). Interrumpo el procesado y reintento con distinta configuracion.\n' % (contador)
        clidconfig.controlFileGral.write(elMensaje)
        printMsg(elMensaje)
    printMsg(
        'Desactivar la opcion de cargar todos los puntos en array. Si tb falla: Lectura de registros individuales (en vez de leer el fichero completo cargandolo entero en la RAM).\n'
    )
    mostrarMemoriaOcupada(miLasClass)


# ==============================================================================o
def coordenadasDeBloque(miHead, metrosBloque, metrosCelda):
    xmin = miHead['xmin']
    ymin = miHead['ymin']
    xmax = miHead['xmax']
    ymax = miHead['ymax']
    xInfIzda = float(xmin)
    yInfIzda = float(ymin)
    xSupIzda = xInfIzda
    if metrosBloque == 1000 or metrosBloque == 2000:
        # print( 'Calculando las coordenadas de la esquina inferior del bloque' )
        if xInfIzda % metrosCelda != 0:
            print(
                'Corrigiendo xInfIzda. Antes:',
                xInfIzda,
            )
            #             (xInfIzda / metrosCelda), round((xInfIzda / metrosCelda), 0), metrosCelda * round((xInfIzda / metrosCelda), 0),
            xInfIzda = float(metrosCelda * round((xInfIzda / metrosCelda), 0))
            print('Despues:', xInfIzda)
        if yInfIzda % metrosCelda != 0:
            print(
                'Corrigiendo yInfIzda. Antes:',
                yInfIzda,
            )
            yInfIzda = float(metrosCelda * round((yInfIzda / metrosCelda), 0))
            print('Despues:', yInfIzda)
        # Esquina nominal del fichero las
        xSupDcha = xSupIzda + metrosBloque
        ySupIzda = yInfIzda + metrosBloque
    else:
        xSupDcha = float(xmax)
        ySupIzda = float(ymax)
    ySupDcha = ySupIzda

    return {'xInfIzda': xInfIzda, 'yInfIzda': yInfIzda, 'xSupIzda': xSupIzda, 'ySupIzda': ySupIzda, 'xSupDcha': xSupDcha, 'ySupDcha': ySupDcha}


# ==============================================================================o
def chequearHuso29(fileCoordYearFromName):
    # Lo mejor es dejar GLO.MAINhuso == 0 y asigno el huso en funcion de las coordenadas
    # Mantengo el huso 30 en el caso de que incluya _H29_ en GLO.MAINprocedimiento
    #  Esto solo lo hago cuando tengo los lasFiles en una carpeta especial (por ejemplo IRC_H29 en vez de IRC)
    if GLO.MAINhuso == 0:
        if int(fileCoordYearFromName[:3]) >= 650: # or '_H29_' in GLO.MAINprocedimiento:
            TRNShuso29 = True
        else:
            TRNShuso29 = False
    elif GLO.MAINhuso == 29:
        TRNShuso29 = True
    else:
        TRNShuso29 = False
    return TRNShuso29


# ==============================================================================o
def renombraFicheros(
        rutaLazCompleta,
        infileSinRuta,
        fileCoordYear='',
        listaFicheros=None,
    ):
    infileConRuta = os.path.join(rutaLazCompleta, infileSinRuta)
    # Convierte los nombres de los ficheros al formato XXX_YYYY_AAAA.las
    # AAAA es la GLO.MAINanualidad y es opcional
    if len(infileSinRuta) == 17 and infileSinRuta[4] =='_' and infileSinRuta[9] =='_':
        # Nombre de fichero de xxx_yyyy_AAAA.las
        nuevoInfile = infileSinRuta
        if not listaFicheros is None:
            listaFicheros.write(nuevoInfile + '\t<-\t' + infileSinRuta + '\n')
        return
    elif len(infileSinRuta) == 12 and infileSinRuta[4] =='_' and infileSinRuta[9] =='_' and GLO.MAINanualidad != '0000':
        # Nombre de fichero de tipo xxx_yyyy.las
        nuevoInfile = infileSinRuta[:8] + '_' + GLO.MAINanualidad + infileSinRuta[-4:]
    elif fileCoordYear:
        nuevoInfile = fileCoordYear + infileSinRuta[-4:]
        nuevoInfileConRuta = os.path.join(rutaLazCompleta, nuevoInfile)
    else:
        return
    try:
        os.rename(infileConRuta, nuevoInfileConRuta)
    except:
        print('Error en %s -> %s' % (infileSinRuta, nuevoInfile))
        sys.exit()
    if not listaFicheros is None:
        listaFicheros.write(nuevoInfile + '\t<-\t' + infileSinRuta + '\n')
    return


def creaDirectorio(rutaDirectorio):
    # Parecido a os.makedirs(), pero que este no crea todo el arbol de directorios,
    # sino solo intenta crear el directorio y su padre.
    if not os.path.exists(rutaDirectorio):
        try:
            os.mkdir(rutaDirectorio)
        except:
            rutaPadre = os.path.abspath(os.path.join(rutaDirectorio, '..'))
            try:
                os.mkdir(rutaPadre)
                os.mkdir(rutaDirectorio)
                print('clidaux-> Se ha creado el directorio %s despues de crear su dir padre: %s' % (rutaDirectorio, rutaPadre))
            except:
                print('clidaux-> No se ha podido crear el directorio %s ni su dir padre %s' % (rutaDirectorio, rutaPadre))
            sys.exit(0)


def creaRutaDeFichero(rutaFichero):
    rutaDirectorio = os.path.dirname(os.path.realpath(rutaFichero))
    miFileNameSinPath = os.path.basename(os.path.realpath(rutaFichero))
    if not os.path.exists(rutaDirectorio):
        print(f'clidaux-> Creando ruta {rutaDirectorio} para {miFileNameSinPath}')
        try:
            os.makedirs(rutaDirectorio)
        except:
            print(f'\nclidaux-> ATENCION: No se ha podido crear el directorio {rutaDirectorio}')
            sys.exit()


def creaDirectorios(GLOBAL_rutaResultados, listaSubdirectorios=[]):
    if not os.path.exists(GLOBAL_rutaResultados):
        print('No existe el directorio %s -->> Se crea automaticamente...' % (GLOBAL_rutaResultados))
    listaDirectorios = [
        GLOBAL_rutaResultados,
        GLOBAL_rutaResultados + 'Ajustes/',
        GLOBAL_rutaResultados + 'Ajustes/Basal/',
        GLOBAL_rutaResultados + 'Ajustes/Suelo/',
        GLOBAL_rutaResultados + 'Alt/',
        GLOBAL_rutaResultados + 'AltClases/',
        GLOBAL_rutaResultados + 'Clasificacion/',
        GLOBAL_rutaResultados + 'CobClases/',
        GLOBAL_rutaResultados + 'Fcc/',
        GLOBAL_rutaResultados + 'Fcc/RptoAzMin_MasDe/',
        GLOBAL_rutaResultados + 'Fcc/RptoAsuelo_MasDe/',
        GLOBAL_rutaResultados + 'Fcc/RptoAmds_MasDe/',
        GLOBAL_rutaResultados + 'Fcc/RptoAmds/',
        GLOBAL_rutaResultados + 'Fcc/RptoAmdb/',
        GLOBAL_rutaResultados + 'FormasUsos/',
        GLOBAL_rutaResultados + 'NumPtosPasadas/',
        GLOBAL_rutaResultados + 'NumPtosPasadas/PorRetornos/',
        GLOBAL_rutaResultados + 'NumPtosPasadas/PorClases/',
        GLOBAL_rutaResultados + 'OrientPte/',
        GLOBAL_rutaResultados + 'Varios/',
        GLOBAL_rutaResultados + 'z/',
    ]
    for directorio in listaDirectorios:
        if not os.path.exists(directorio):
            try:
                os.makedirs(directorio)
            except:
                print('No se ha podido crear el directorio %s' % (directorio))
                sys.exit()


def mostrarCabecera(header):
    if GLO.GLBLusarLiblas:
        # print( 'Propiedades y metodos de miHead:', dir(header) )
        """
        ['DeleteVLR', 'GetVLR', '__class__', '__del__', '__delattr__', '__dict__',
        '__doc__', '__format__', '__getattribute__', '__hash__', '__init__',
        '__len__', '__module__', '__new__', '__reduce__', '__reduce_ex__',
        '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__',
        'add_vlr', 'compressed', 'count', 'data_format_id', 'data_offset',
        'data_record_length', 'dataformat_id', 'date', 'delete_vlr', 'doc',
        'encoding', 'file_signature', 'file_source_id', 'filesource_id',
        'get_compressed', 'get_count', 'get_dataformatid', 'get_dataoffset',
        'get_datarecordlength', 'get_date', 'get_filesignature', 'get_filesourceid',
        'get_global_encoding', 'get_guid', 'get_headersize', 'get_majorversion',
        'get_max', 'get_min', 'get_minorversion', 'get_offset', 'get_padding',
        'get_pointrecordsbyreturncount', 'get_pointrecordscount', 'get_projectid',
        'get_recordscount', 'get_scale', 'get_schema', 'get_softwareid', 'get_srs',
        'get_systemid', 'get_version', 'get_vlr', 'get_vlrs', 'get_xml',
        'global_encoding', 'guid', 'handle', 'header_length', 'header_size',
        'major', 'major_version', 'max', 'min', 'minor', 'minor_version',
        'num_vlrs', 'offset', 'owned', 'padding', 'point_records_count',
        'point_return_count', 'project_id', 'records_count', 'return_count',
        'scale', 'schema', 'set_compressed', 'set_count', 'set_dataformatid',
        'set_dataoffset', 'set_date', 'set_filesourceid', 'set_global_encoding',
        'set_guid', 'set_majorversion', 'set_max', 'set_min', 'set_minorversion',
        'set_offset', 'set_padding', 'set_pointrecordsbyreturncount',
        'set_pointrecordscount', 'set_scale', 'set_schema', 'set_softwareid',
        'set_srs', 'set_systemid', 'set_version', 'set_vlrs', 'software_id',
        'srs', 'system_id', 'version', 'version_major', 'version_minor', 'vlrs', 'xml']
        """
        print('Version de formato LAS:', header.version)
        print('version:', header.version)
        print('data_format_id:', header.data_format_id)
        print('dataformat_id:', header.dataformat_id)
        print('data_record_length:', header.data_record_length)
        print('global_encoding:', header.global_encoding)
        print('header_length', header.header_length)
        print('header_size', header.header_size)
        print('major', header.major)
        print('major_version', header.major_version)
        print('max', header.max)
        print('min', header.min)
        print('minor', header.minor)
        print('minor_version', header.minor_version)
        print('num_vlrs')
        print('offset', header.offset)
        print('owned', header.owned)
        print('padding', header.padding)
        print('point_records_count', header.point_records_count)
        print('point_return_count', header.point_return_count)
        print('project_id', header.project_id)
        print('records_count', header.records_count)
        print('return_count', header.return_count)
        print('scale', header.scale)
        print('schema', header.schema)
        print('Numero total de puntos:', header.count)
        print('point_return_count:', header.point_return_count)
        print('data_offset:', header.data_offset)
        print('offset:', header.offset)
        print('srs:', header.srs)
        '''
        #Ejemplo:
        version: 1.2
        data_format_id: 3
        dataformat_id: 3
        data_record_length: 34
        global_encoding: 0
        header_length 227
        header_size 227
        major 1
        major_version 1
        max [343999.99, 4629999.99, 863.94]
        min [342058.62, 4628000.0, 845.6700000000001]
        minor 2
        minor_version 2
        num_vlrs
        offset [-0.0, -0.0, -0.0]
        owned False
        padding 2
        point_records_count 2397593
        point_return_count [2378079L, 19475L, 39L, 0L, 0L, 0L, 0L, 0L]
        project_id 00000000-0000-0000-0000-000000000000
        records_count 0
        return_count [2378079L, 19475L, 39L, 0L, 0L, 0L, 0L, 0L]
        scale [0.01, 0.01, 0.01]
        schema <liblas.schema.Schema object at 0x04E921B0>
        Numero total de puntos: 2397593
        point_return_count: [2378079L, 19475L, 39L, 0L, 0L, 0L, 0L, 0L]
        data_offset: 229
        offset: [-0.0, -0.0, -0.0]
        srs: <liblas.srs.SRS object at 0x04E921B0>
        '''
    else:  # Cabecera leida con file.read()
        print('Version de formato LAS: %i.%i' % (header['vermajor'], header['verminor']))
        print('Formato de puntos:', header['pointformat'])
        print('Numero total de puntos:', header['numptrecords'])
        print('pointreclen:', header['pointreclen'])
        print('xscale:', header['xscale'])
        print('yscale:', header['yscale'])
        print('xoffset, yoffset', header['xoffset'], header['yoffset'])
        '''
        #Ejemplo:
        pointreclen: 34
        xscale: 0.01
        yscale: 0.01
        xoffset, yoffset -0.0 -0.0
        '''


# def mostrarPunto(p):
#     if GLO.GLBLusarLiblas:
#         print( 'point_source_id', p.point_source_id )
#         print( 'handle', p.handle )
#         #print( 'header', p.header )
#         print( 'time', p.time )
#         print( 'raw_time', p.raw_time, time.asctime( time.localtime(p.raw_time) ) )
#         #print( 'xml', p.xml )
#         #print( 'x', p.x )
#         #print( 'y', p.y )
#         #print( 'z', p.z )
#         print( 'scan_angle', p.scan_angle )
#         print( 'scan_direction', p.scan_direction )
#         print( 'scan_flags', p.scan_flags )
#         #print( 'return_number', p.return_number )
#         #print( 'number_of_returns', p.number_of_returns )
#         #print( 'intensity', p.intensity )
#         #print( 'user_data', p.user_data )
#         #print( 'point_source_ID', p.point_source_ID )
#     else:
#         pass


# ==============================================================================o
def convertirMirecordEnDict(miRecord, listaTuplasPropPtoTodas):
    dctData = {}
    if GLO.GLBLalmacenarPuntosComoNumpyDtype:  # type(miPto) == np.void
        contador = 0
        for row in listaTuplasPropPtoTodas:
            dctData[row[0]] = miRecord[contador]
            contador += 1
    elif type(miRecord) == str or type(miRecord) == bytes:
        # Lectura del fichero .las con infile.read()
        puntero = 0
        for row in listaTuplasPropPtoTodas:
            # print( row[0], puntero, row[1], miRecord[puntero:puntero+row[1]], struct.unpack(row[2], miRecord[puntero:puntero+row[1]])[0] )
            dctData[row[0]] = struct.unpack(row[2], miRecord[puntero : puntero + row[1]])[0]
            puntero = puntero + row[1]
    elif type(miRecord) == list or type(miRecord) == tuple or type(miRecord) == np.ndarray:
        # Opcion no desarrollada, pero posible, igual que con
        if len(listaTuplasPropPtoTodas) != len(miRecord):
            print('Revisar problema de propiedades del punto:')
            print(listaTuplasPropPtoTodas)
            print(miRecord)
        contador = 0
        for row in listaTuplasPropPtoTodas:
            dctData[row[0]] = miRecord[contador]
            contador += 1
    else:
        print('Hay un error en el tipo de registro leido 1-> type(miRecord):', type(miRecord))
        print('type(miRecord) == np.ndarray', type(miRecord) == np.ndarray)
        print('Contenido del registro:', miRecord)
        print('Revisar este error de type()')
        quit()


# ==============================================================================o
def lasToolsDEM(infileConRuta):
    infile = os.path.basename(infileConRuta)
    rutaLazCompleta = os.path.dirname(infileConRuta)

    if MAIN_ENTORNO == 'calendula':
        las2dem_binary = 'las2dem'
    elif MAIN_ENTORNO == 'windows':
        # las2dem_binary = 'las2dem.exe'
        las2dem_binary = MAIN_DRIVE + '/_App/LAStools/bin/'
        if not os.path.isfile(las2dem_binary):
            las2dem_binary = 'C:/_app/LAStools/bin/'
            if not os.path.isfile(las2dem_binary):
                laszip_names = ('las2dem.exe')
                for binary in laszip_names:
                    in_path = [os.path.isfile(os.path.join(x, binary)) for x in os.environ["PATH"].split(os.pathsep)]
                    if any(in_path):
                        las2dem_binary = binary
                        break
                    else:
                        print('No se ha encontrado las2dem.exe en el path ni en D:/_App/LAStools/ ni C:/_app/LAStools/bin/')
                        sys.exit(0)

    # extensionDem = '.asc'
    extensionDem = '.tif'
    outfileDem = (infile.replace('.las', extensionDem)).replace('.laz', extensionDem)
    if outfileDem[-4:] != extensionDem:
        outfileDem = outfileDem + extensionDem
    outfileLasConRuta = os.path.join(rutaLazCompleta, outfileDem)
    print('\tSe crea el fichero dem %s' % outfileDem)
    # print('\t\t%s -i %s -o %s' % (las2dem_binary, infileConRuta, outfileLasConRuta))
    subprocess.call([las2dem_binary, '-i', infileConRuta, '-o', outfileLasConRuta, ' -keep_class 2 -step 2 -v -utm 30T'])


# ==============================================================================o
def buscarLaszip(LCLverbose=False):
    laszip_binary_encontrado = True
    laszip_binary = os.path.join(MAIN_RAIZ_DIR, 'laszip', 'laszip.exe')
    if not os.path.exists(laszip_binary):
        laszip_binary = os.path.join(MAIN_PROJ_DIR, 'laszip', 'laszip.exe')
        if not os.path.exists(laszip_binary):
            if TRNSdescomprimirConlaszip and TRNSdescomprimirConlas2las:
                laszip_names = ('laszip.exe', 'laszip', 'las2las.exe', 'las2las')
            elif TRNSdescomprimirConlaszip and not TRNSdescomprimirConlas2las:
                laszip_names = ('laszip.exe', 'laszip')
            elif TRNSdescomprimirConlas2las:
                laszip_names = ('las2las.exe', 'las2las')
            else:
                laszip_names = ('laszip-cli', 'laszip-cli.exe')

            laszip_binary_encontrado = False
            for binary in laszip_names:
                in_path = [os.path.isfile(os.path.join(x, binary)) for x in os.environ["PATH"].split(os.pathsep)]
                # print('clidaux-> path: {}'.format(os.environ["PATH"].split(os.pathsep)))
                # print('clidaux-> Buscando {} {}'.format(any(in_path), in_path))
                if any(in_path):
                    laszip_binary = binary
                    laszip_binary_encontrado = True
                    break
    
            if not laszip_binary_encontrado:
                if LCLverbose:
                    print("clidaux-> No se ha encontrado ningun binario de laszip (%s) en el path; busco en mis directorios" % ", ".join(laszip_names))
                if TRNSdescomprimirConlaszip:
                    if LCLverbose:
                        print('\t-> Buscando {}'.format(os.path.abspath('./laszip/laszip.exe')))
    
                    if os.path.exists(os.path.abspath('./laszip/laszip.exe')):
                        laszip_binary_encontrado = True
                        if LCLverbose:
                            print('\t-> Utilizo  {}'.format(os.path.abspath('./laszip/laszip.exe')))
                        laszip_binary = os.path.abspath('./laszip/laszip')
                    elif os.path.exists('C:/_app/LAStools/bin/laszip.exe'):
                        laszip_binary_encontrado = True
                        if LCLverbose:
                            print('\t-> Utilizo  {}'.format('C:/_app/LAStools/bin/laszip.exe'))
                        laszip_binary = os.path.abspath('C:/_app/LAStools/bin/laszip')
                    elif os.path.exists(MAIN_DRIVE + '/_app/LAStools/bin/laszip.exe'):
                        laszip_binary_encontrado = True
                        if LCLverbose:
                            print('\t-> Utilizo  {}'.format(MAIN_DRIVE + '/_app/LAStools/bin/laszip.exe'))
                        laszip_binary = os.path.abspath(MAIN_DRIVE + '/_app/LAStools/bin/laszip')
                if not laszip_binary_encontrado and TRNSdescomprimirConlas2las:
                    if (
                        os.path.exists('./laszip/las2las.exe')
                        and os.path.exists('./laszip/LASzip.dll')
                    ):
                        laszip_binary_encontrado = True
                        laszip_binary = os.path.abspath('./laszip/las2las')
                    elif (
                        os.path.exists('C:/_app/LAStools/bin/las2las.exe')
                        and os.path.exists('C:/_app/LAStools/laszip/dll/LASzip.dll')
                    ):
                        laszip_binary_encontrado = True
                        laszip_binary ='C:/_app/LAStools/bin/las2las.exe'
                    elif (
                        os.path.exists(MAIN_DRIVE + '/_app/LAStools/bin/las2las.exe')
                        and os.path.exists(MAIN_DRIVE + '/_app/LAStools/laszip/dll/LASzip.dll')
                    ):
                        laszip_binary_encontrado = True
                        laszip_binary =MAIN_DRIVE + '/_app/LAStools/bin/las2las.exe'
                    else:
                        print('No se encuentran los ficheros LDA2LAS.exe, LASzip.dll y/o relacionados. Solucionar el problema y empezar de nuevo')
                        sys.exit(0)
                elif False:
                    # Esto es antiguo: miro si hay acceso a LDA2LAS.exe y las dll que necesita (laszip.dll y otros)
                    if (
                        os.path.exists('LDA2LAS.exe')
                        and os.path.exists('LASzip.dll')
                        and os.path.exists('MSVCRTD.DLL')
                        and os.path.exists('MFC42D.DLL')
                        and os.path.exists('MSVCP60D.DLL')
                    ):
                        laszip_binary = 'LDA2LAS'
                    elif (
                        os.path.exists('./laszip/LDA2LAS.exe')
                        and os.path.exists('./laszip/LASzip.dll')
                        and os.path.exists('./laszip/MSVCRTD.DLL')
                        and os.path.exists('./laszip/MFC42D.DLL')
                        and os.path.exists('./laszip/MSVCP60D.DLL')
                    ):
                        laszip_binary = os.path.abspath('./laszip/LDA2LAS')
                    elif os.path.exists('C:/FUSION/LDA2LAS.exe') and os.path.exists('C:\FUSION\LASzip.dll'):
                        laszip_binary = 'c:/fusion/LDA2LAS'
                    elif os.path.exists('C:/_app/FUSION/LDA2LAS.exe') and os.path.exists('C:/_app/FUSION/LASzip.dll'):
                        laszip_binary = 'c:/_app/fusion/LDA2LAS'
                    elif os.path.exists(MAIN_DRIVE + '/_App/FUSION/LDA2LAS.exe') and os.path.exists(MAIN_DRIVE + '/_App/FUSION/LASzip.dll'):
                        laszip_binary = MAIN_DRIVE + '/_App/FUSION/LDA2LAS'
                    else:
                        print('No se encuentran los ficheros LDA2LAS.exe, LASzip.dll y/o relacionados. Solucionar el problema y empezar de nuevo')
                        sys.exit(0)

    return (laszip_binary, laszip_binary_encontrado)


# ==============================================================================o
def comprimeLaz(
        infileConRuta,
        eliminarLasFile=False,
        LCLverbose=False,
        sobreEscribirOutFile=False,
    ):
    if LCLverbose:
        printMsg(f'\n{"":_^80}')

    if not os.path.exists(infileConRuta):
        printMsg(f'clidaux-> Fichero no disponible para comprimir: {infileConRuta}')
        return False

    infile = os.path.basename(infileConRuta)
    rutaLazCompleta = os.path.dirname(infileConRuta)
    if 'RGBI' in rutaLazCompleta:
        rutaLazCompleta = rutaLazCompleta.replace('RGBI', 'RGBI_laz')
    else:
        rutaLazCompleta = rutaLazCompleta.replace('RGB', 'RGB_laz')
    if not os.path.isdir(rutaLazCompleta):
        try:
            os.makedirs(rutaLazCompleta)
        except:
            print(f'clidaux-> AVISO: no se ha podido crear la ruta: {rutaLazCompleta} -> No se genera lazFile.')
            return False

    if MAIN_ENTORNO == 'calendula':
        # laszip_binary = 'las2las'
        laszip_binary = 'laszip'
        outfileLaz = (infile.replace('.las', '.laz')).replace('.LAS', '.laz')
        outfileLazConRuta = (os.path.join(rutaLazCompleta, outfileLaz))
    elif MAIN_ENTORNO == 'windows':
        # laszip_binary = '{}/_clid/cartolid/laszip/laszip'.format(MAIN_PROJ_DIR)
        (laszip_binary, laszip_binary_encontrado) = buscarLaszip(LCLverbose=LCLverbose)

        if not laszip_binary_encontrado:
            print('\nclidaux-> AVISO: no se ha encontrado un binario para comprimir (no se genera lazFile).')
            return False

        outfileLaz = (infile.replace('.las', '.laz')).replace('.LAS', '.laz')
        outfileLazConRuta = os.path.join(rutaLazCompleta, outfileLaz)
        # print('\t-> Compresor: {}'.format(laszip_binary))
        # print('\t-> infileConRuta:', infileConRuta)
        # print('\t-> outfileLazConRuta:', outfileLazConRuta)
        # print('\t\t%s -i %s -o %s' % (laszip_binary, infileConRuta, outfileLasConRuta))
    if os.path.exists(outfileLazConRuta) and not sobreEscribirOutFile:
        print('\t-> clidaux-> No se genera el fichero comprimido porque sobreEscribirOutFile={} y ya existe: {}'.format(sobreEscribirOutFile, outfileLazConRuta))
        return False

    if LCLverbose:
        print('\t-> clidaux-> Se comprime el fichero para generar: {}'.format(outfileLazConRuta))
        print('\t-> clidaux-> Compresor:', laszip_binary)
    subprocess.call([laszip_binary, '-i', infileConRuta, '-o', outfileLazConRuta])

    if eliminarLasFile and os.path.exists(infileConRuta):
        print('\tEliminando el fichero las despues de comprimir a laz:', infileConRuta)
        os.remove(infileConRuta)

    return True


# ==============================================================================o
def descomprimeLaz(
        infileConRuta,
        descomprimirLazEnMemoria=True,
        LCLverbose=False,
        sobreEscribirOutFile=False,
    ):
    if LCLverbose:
        printMsg(f'\n{"":_^80}')

    if not os.path.exists(infileConRuta):
        printMsg(f'clidaux-> Fichero no disponible para descomprimir: {infileConRuta}')
        return ''
    infileConRuta = infileConRuta.replace('.las', '.laz')

    infile = os.path.basename(infileConRuta)
    rutaLazCompleta = os.path.dirname(infileConRuta)

    if MAIN_ENTORNO == 'calendula':
        laszip_binary_encontrado = True
        # laszip_binary = 'las2las'
        laszip_binary = 'laszip'
    elif MAIN_ENTORNO == 'windows':
        # ======================================================================
        # ======================================================================
        # Atencion: laszip.exe funciona con las 1.4 con todos los formatos de punto (las2las no)
        # ======================================================================
        # ======================================================================
        # 
        (laszip_binary, laszip_binary_encontrado) = buscarLaszip(LCLverbose=LCLverbose)

    if not laszip_binary_encontrado:
        print('\nclidaux-> ATENCION: no se ha encontrado un binario para descomprimir')
        sys.exit(0)

    # outfileLas = infile.replace('.laz', '.las')
    if descomprimirLazEnMemoria:
        # laspy usa subprocess.Popen() (https://github.com/grantbrown/laspy/tree/master/laspy)
        # El fichero descomprimido no se guarda en un fichero, sino que se almacena en memoria (data)
        # Quito la opcion '-stdout' porque las2las.exe da error con esa opcion
        if LCLverbose:
            print('clidaux-> Descomprimiendo {} en memoria con {} '.format(infileConRuta, laszip_binary))
        if laszip_binary.endswith('laszip') or laszip_binary.endswith('laszip.exe'):
            prc = subprocess.Popen(
                [laszip_binary, '-olas', '-stdout', '-i', infileConRuta],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=-1
            )
        else:
            prc = subprocess.Popen(
                [laszip_binary, '-olas', '-i', infileConRuta],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=-1
            )
        lasDataMem, stderr = prc.communicate()
        if LCLverbose:
            print('clidaux-> subprocess ejecutado. type(lasDataMem): {} stderr: {}.'.format(type(lasDataMem), stderr))
        if not lasDataMem is None:
            if LCLverbose:
                print('\t-> len(lasDataMem): {}'.format(len(lasDataMem)))

        if prc.returncode != 0:
            print('clidaux-> Revisar este return code de %s: %d' % (laszip_binary, prc.returncode))
            # if stderr and len(stderr) < 2048:
            print(stderr)
            print('No se ha podido descomprimir el fichero laz en memoria, se prueba con fichero temporal')
            outfileLas = 'FicheroTemporal.las'
            outfileLasConRuta = os.path.join(rutaLazCompleta, outfileLas)
            print('\tSe crea el fichero las %s' % outfileLasConRuta)
            # print('\t\t%s -i %s -o %s' % (laszip_binary, infileConRuta, outfileLasConRuta))
            subprocess.call([laszip_binary, '-i', infileConRuta, '-o', outfileLasConRuta])
            # print('\tOk ejecutado laszip')
            lasDataMem = outfileLasConRuta
            # sys.exit(0)
    else:
        if GLO.GLBLficheroLasTemporal:
            outfileLas = 'FicheroTemporal.las'
        else:
            if infile[-4:] == '.las':
                outfileLas = infile.replace('.las', '.las_')
            elif infile[-4:] == '.laz':
                outfileLas = infile.replace('.laz', '.las')
            else:
                outfileLas = infile + '.las'
        outfileLasConRuta = os.path.join(rutaLazCompleta, outfileLas)
        if os.path.exists(outfileLasConRuta) and not sobreEscribirOutFile:
            printMsg(f'clidaux-> Fichero descomprimdo ya existe: {outfileLasConRuta}')
            return ''
        if LCLverbose:
            print('\tSe crea el fichero las %s' % outfileLasConRuta)
        # print('\t\t%s -i %s -o %s' % (laszip_binary, infileConRuta, outfileLasConRuta))
        subprocess.call([laszip_binary, '-i', infileConRuta, '-o', outfileLasConRuta])
        # print('\tOk ejecutado laszip')
        lasDataMem = outfileLasConRuta

        # #Ya no uso os.system() xq en linux no me funciona
        # if MAIN_ENTORNO == 'windows':
        #     ejecutar = laszip_binary + ' ' + infileConRuta + ' ' + outfileLasConRuta
        #     os.system(ejecutar)

    if LCLverbose:
        printMsg(f'{"":=^80}')

    return lasDataMem


# ==============================================================================o
# ==============================================================================o
# ==============================================================================o
# Comodin
class Bloque2x2(object):
    def __init__(self, xInfIzda, yInfIzda, nCeldasX, nCeldasY, metrosPixel):
        self.xInfIzda = xInfIzda
        self.yInfIzda = yInfIzda
        self.nCeldasX = nCeldasX
        self.nCeldasY = nCeldasY
        self.xSupDcha = self.xInfIzda + (self.nCeldasX * metrosPixel)
        self.ySupDcha = self.yInfIzda + (self.nCeldasY * metrosPixel)
        self.numPuntosFueraDeBloque = 0
        self.hayPuntosDescartadosPorCotaAnomala = False
        self.hayPuntosConCotaExcesivaRptoAzMin = False
        self.numPuntosConCotaExcesivaRptoAzMin = 0
        self.cotaExcesivaMaximaRptoAzMin = 0
        self.hayPuntosConCotaExcesiva = False
        self.numPuntosConCotaExcesiva = 0
        self.cotaExcesivaMaxima = 0
        self.hayPuntosConCotaNegativa = False
        self.numPuntosConCotaNegativa = 0
        self.cotaNegativaMinima = 0
        self.primerIntento = True


class CeldaClass(object):
    def __init__(self, cX, cY, nCeldasX, nCeldasY, xInfIzda, yInfIzda, miHead, nBytesPorPunto):
        self.cX = cX
        self.cY = cY
        # self.xInfIzda = xInfIzda
        # self.yInfIzda = yInfIzda
        # self.nCeldasX = nCeldasX
        # self.nCeldasY = nCeldasY
        self.miHead = miHead
        self.nBytesPorPunto = nBytesPorPunto

    def celdaToBloc(self, cQ):
        bloc = np.zeros(10, dtype='int8')
        for nivel in range(10):
            bloc[nivel] = cQ % 2
            cQ = int(cQ / 2)
        return bloc

    def calculaOffsetDelIndice(self):
        # Offset desde el inicio del indice de blocs (despues del puntoIndiceGeneral)
        # print( 'Calculando offsets...', self.tipoIndice )
        self.offsetPtoFisicoPrimeroDesdeInicio = self.miHead['offset'] + (self.nBytesPorPunto * self.nPuntosIndice)

        if self.tipoIndice == 101:
            blocX = self.celdaToBloc(self.cX)
            blocY = self.celdaToBloc(self.cY)
            cX_ = sum([blocX[i] * (2 ** i) for i in range(0, len(blocX))])
            cY_ = sum([blocY[i] * (2 ** i) for i in range(0, len(blocY))])
            if cX_ != self.cX or cY_ != self.cY:
                print('\nCeldas mal calculadas', cX_, self.cX, cY_, self.cY)
            nCeldaSecuencial = 1
            for nivel in range(10):
                nCeldaSecuencial += blocX[nivel] * (2 ** (2 * nivel))
                nCeldaSecuencial += blocY[nivel] * (2 ** (2 * nivel)) * 2
            self.nCeldaSecuencial = nCeldaSecuencial
            print(blocX, blocY, 'Celda %i, %i -> Orden secuencial: %i' % (self.cX, self.cY, nCeldaSecuencial))
            self.offsetPtoIndiceBlocDesdeInicioIndice = self.nBytesPorPunto * (1 + self.nCeldaSecuencial)
        elif self.tipoIndice <= 0:
            # No hay indice
            self.offsetPtoIndiceBlocDesdeInicioIndice = 0  # Desconocido
            self.nCeldaSecuencial = 0
        elif self.tipoIndice < 100:
            # Indice matricial
            self.nCeldaSecuencial = (self.bY * self.nBlocsY) + self.bX
            self.offsetPtoIndiceBlocDesdeInicioIndice = self.nBytesPorPunto * (1 + self.nCeldaSecuencial)


# Sin uso
class BlocClass(object):
    def __init__(self, bX, bY, nBlocsX, nBlocsY, nCeldasX, nCeldasY, xInfIzda, yInfIzda, miHead, listaTuplasPropPtoTodas, nBytesPorPunto):
        self.bX = bX
        self.bY = bY
        self.nBlocsX = nBlocsX
        self.nBlocsY = nBlocsY

        self.xInfIzda = xInfIzda
        self.yInfIzda = yInfIzda
        self.nCeldasX = nCeldasX
        self.nCeldasY = nCeldasY
        self.miHead = miHead
        self.listaTuplasPropPtoTodas = listaTuplasPropPtoTodas
        self.nBytesPorPunto = nBytesPorPunto


# ==============================================================================#
def listarMetodos(object, spacing=10, collapse=1):
    'Listado de metodos del objeto "object" y doc strings. El objeto puede ser: modulo, clase, lista, dict o string'
    methodList = [method for method in dir(object) if callable(getattr(object, method))]
    processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
    print("\n".join(["%s %s" % (method.ljust(spacing), processFunc(str(getattr(object, method).__doc__))) for method in methodList]))


#!/usr/bin/env python
""" a small class for Principal Component Analysis
Usage:
        p = PCA( A, fraction=0.90 )
In:
        A: an array of e.g. 1000 observations x 20 variables, 1000 rows x 20 columns
        fraction: use principal components that account for e.g.
                90 % of the total variance

Out:
        p.U, p.d, p.Vt: from np.linalg.svd, A = U . d . Vt
        p.dinv: 1/d or 0, see NR
        p.eigen: the eigenvalues of A*A, in decreasing order (p.d**2).
                eigen[j] / eigen.sum() is variable j's fraction of the total variance;
                look at the first few eigen[] to see how many PCs get to 90 %, 95 % ...
        p.npc: number of principal components,
                e.g. 2 if the top 2 eigenvalues are >= `fraction` of the total.
                It's ok to change this; methods use the current value.

Methods:
        The methods of class PCA transform vectors or arrays of e.g.
        20 variables, 2 principal components and 1000 observations,
        using partial matrices U' d' Vt', parts of the full U d Vt:
        A ~ U' . d' . Vt' where e.g.
                U' is 1000 x 2
                d' is diag([ d0, d1 ]), the 2 largest singular values
                Vt' is 2 x 20.    Dropping the primes,

        d . Vt            2 principal vars = p.vars_pc( 20 vars )
        U                     1000 obs = p.pc_obs( 2 principal vars )
        U . d . Vt    1000 obs, p.obs( 20 vars ) = pc_obs( vars_pc( vars ))
                fast approximate A . vars, using the `npc` principal components

        Ut                            2 pcs = p.obs_pc( 1000 obs )
        V . dinv                20 vars = p.pc_vars( 2 principal vars )
        V . dinv . Ut     20 vars, p.vars( 1000 obs ) = pc_vars( obs_pc( obs )),
                fast approximate Ainverse . obs: vars that give ~ those obs.


Notes:
        PCA does not center or scale A; you usually want to first
                A -= A.mean(A, axis=0)
                A /= A.std(A, axis=0)
        with the little class Center or the like, below.

See also:
        http://en.wikipedia.org/wiki/Principal_component_analysis
        http://en.wikipedia.org/wiki/Singular_value_decomposition
        Press et al., Numerical Recipes (2 or 3 ed), SVD
        PCA micro-tutorial
        iris-pca .py .png

"""


# ==============================================================================
def completarVariablesGlobales(
        GLO,
        LCLobjetivoSiReglado='GENERAL',
        LCLprocedimiento='',
        LCLcuadrante='',
        ARGSnInputsModeloNln=0,
        ARGScodModeloNln='',
        rutaLazCompleta=''
    ):
    # Si hay ARGScodCuadrante, prevalece sobre el que figure en el fichero de configuracion xls (y se incorpora a la configuracion)

    # ==========================================================================
    MAINusuario = infoUsuario(False)
    # ==========================================================================

    # global GLO
    # En esta funcion se establecen algunas variables globales (si es necesario modificarlas):
    #    MAINrutaCarto      -> Se adapta para que cuelgue de MAIN_RAIZ_DIR o se adapta segun MAINprocedimiento
    #    MAINrutaOutput     -> Se vincula a MAIN_RAIZ_DIR (windows) o se establece especificamente (calendula) y se adapta segun MAINprocedimiento
    #    MAINrutaLaz        -> Se vincula a MAIN_RAIZ_DIR (windows) o se establece especificamente (calendula) y se adapta segun MAINprocedimiento 
    #    MAINprocedimiento  -> Se retoca si el procedimiento menciona calendula pero lo ejecuto en Windows
    #    GLBLshapeNumPoints, GLBLtipoLectura, GLBLshapeFilter, GLBLprocesarComprimidosLaz, etc.
    # Y se devuelven variables (sin utilidad para determinados procedimiento)
    #    listaDirsLaz, listaSubDirsLaz, coordenadasDeMarcos
    coordenadasDeMarcos = {}
    # ==========================================================================

    # print('{:_^80}'.format(' El Entorno y el cuadrante condicionan MAINrutaLaz y MAINrutaOutput'))
    # print(f'{"":_^80}')

    # Esto lo hago antes en clidbase y clidflow y queda guardado en el cfg
    '''
    # ==========================================================================
    # Ruta raiz del proyecto:    MAIN_RAIZ_DIR
    #  En windows:
    #    Si cartolid NO esta instalado -> D:/_clid (depende de donde este clidbase.py)
    #    Si cartolid SI esta instalado -> C:\conda\py37\envs\clid\lib (depende de donde este site-packages)
    #  En calendula:
    #    /LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1
    GLO.MAIN_RAIZ_DIR = MAIN_RAIZ_DIR
    # Ruta raiz para resultados: MAIN_RAIS_DIR
    #    -> Esta variable solo se usa desde clidaux.py, para
    #  En windows: normalmente sera D:/_clid (o lo que diga clidbase.xlsx)
    #    Tiro de GLO.MAINrutaRaiz (de clidbase.xlsx), que lo he creado para 
    #    cuando se ejecuta el cartolidar de site-packages, ya que no
    #    quiero que los log, cfg, y resultados vayan a site-packages  
    #  En calendula:
    #    /scratch/jcyl_spi_1/jcyl_spi_1_1
    if MAIN_ENTORNO == 'calendula':
        GLO.MAIN_RAIS_DIR = '/scratch/jcyl_spi_1/jcyl_spi_1_1'
    elif 'MAINrutaRaiz' in dir(GLO):
        GLO.MAIN_RAIS_DIR = GLO.MAINrutaRaiz
    else:
        GLO.MAIN_RAIS_DIR = MAIN_RAIZ_DIR
    GLO.MAINmiRutaProyecto = MAIN_PROJ_DIR
    # ==========================================================================
    '''
    # ==========================================================================
    # =========================== MAINrutaLaz ==================================
    # ==========================================================================
    # Sitio por defecto para MAINrutaLaz
    # No se recorren subcarpetas de MAINrutaLaz salvo que lo establezca el MAINprocedimiento
    if __verbose__:
        print(f'\n{"":_^80}')
        print(f'clidaux-> Identificando la ruta de los ficheros laz con completarVariablesGlobales<>')
        print(f'{TB}-> Valor de inicial de rutaLazCompleta: <{rutaLazCompleta}>')
        print(f'{TB}-> Valor de inicial de GLO.MAINrutaLaz: <{GLO.MAINrutaLaz}>')
    if rutaLazCompleta != '':
        # Solo cuando se inicia con clidflow
        GLO.MAINrutaLaz = os.path.abspath(rutaLazCompleta)
        if __verbose__:
            print(f'{TB}Se adopta el valor de rutaLazCompleta: {GLO.MAINrutaLaz}')
    else:
        if (not GLO.MAINrutaLaz is None
            and GLO.MAINrutaLaz != 'None'
            and  GLO.MAINrutaLaz != ''
        ):
            if MAIN_ENTORNO == 'calendula':
                GLO.MAINrutaLaz = os.path.join(GLO.MAIN_RAIS_DIR, GLO.MAINrutaLaz)
            else:
                if ':' in GLO.MAINrutaLaz:
                    # GLO.MAINrutaLaz = 'E:/incendioZamora'
                    # GLO.MAINrutaLaz = GLO.MAINrutaLaz
                    pass
                    if __verbose__:
                        print(f'{TB}MAINrutaLaz-> Se usa directamente GLO.MAINrutaLaz: {GLO.MAINrutaLaz}')
                elif 'MAINrutaRaiz' in dir(GLO):
                    GLO.MAINrutaLaz = os.path.join(GLO.MAINrutaRaiz, GLO.MAINrutaLaz)
                    if __verbose__:
                        print(f'{TB}MAINrutaLaz-> Se integra MAINrutaRaiz y GLO.MAINrutaLaz: {GLO.MAINrutaLaz}')
                else:
                    GLO.MAINrutaLaz = os.path.join(GLO.MAIN_RAIZ_DIR, GLO.MAINrutaLaz)
                    if __verbose__:
                        print(f'{TB}MAINrutaLaz-> Se integra MAIN_RAIZ_DIR y GLO.MAINrutaLaz: {GLO.MAINrutaLaz}')
        else:
            if MAIN_ENTORNO == 'calendula':
                GLO.MAINrutaLaz = os.path.join(GLO.MAIN_RAIS_DIR, 'laz')
            elif 'MAINrutaRaiz' in dir(GLO):
                GLO.MAINrutaLaz = os.path.join(GLO.MAINrutaRaiz, 'laz')
            else:
                GLO.MAINrutaLaz = os.path.join(GLO.MAIN_RAIZ_DIR, 'laz')
            if __verbose__:
                print(f'{TB}Valor por defecto basado en rutaRaiz: {GLO.MAINrutaLaz}')

    if __verbose__:
        print(f'{"":=^80}')
    # ==========================================================================
    if __verbose__:
        print(f'\n{"":_^80}')
        print(f'clidaux-> Se lanza casosEspecialesParaMAINrutaLaz<>')
    GLO.MAINrutaLaz, listaDirsLaz, listaSubDirsLaz = casosEspecialesParaMAINrutaLaz(
        GLO.MAINprocedimiento,
        GLO.MAINrutaLaz,
        LCLcuadrante
    )
    if __verbose__:
        print('clidaux-> GLO.MAINrutaLaz:', GLO.MAINrutaLaz)
        print(f'{"":=^80}')
    # ==========================================================================

    # ==========================================================================
    # ========================== MAINrutaCarto =================================
    # ==========================================================================
    print(f'clidaux-> Antes GLO.MAINrutaCarto: {GLO.MAINrutaCarto}')
    if (
        not GLO.MAINrutaCarto is None
        and GLO.MAINrutaCarto != 'None'
        and GLO.MAINrutaCarto != ''
    ):
        print(f'clidaux-> Antes GLO.MAINrutaCarto no es nulo: {type(GLO.MAINrutaCarto)}')
        GLO.MAINrutaCarto = os.path.abspath(GLO.MAINrutaCarto)
    else:
        GLO.MAINrutaCarto = asignarMAINrutaCarto()
    print(f'clidaux-> Desp  GLO.MAINrutaRaiz:  {GLO.MAINrutaRaiz}')
    print(f'clidaux-> Desp  GLO.MAINrutaCarto: {GLO.MAINrutaCarto}')
    # ==========================================================================

    # ==========================================================================
    # ========================== MAINrutaOutput ================================
    # ==========================================================================
    if (
        not GLO.MAINrutaOutput is None
        and GLO.MAINrutaOutput != 'None'
        and GLO.MAINrutaOutput != ''
    ):
        print(f'clidaux-> MAINrutaOutput (a1): {GLO.MAINrutaOutput}')
        GLO.MAINrutaOutput = os.path.abspath(GLO.MAINrutaOutput)
        print(f'clidaux-> MAINrutaOutput (a2): {GLO.MAINrutaOutput}')
    else:
        print(f'clidaux-> MAINrutaOutput (b1): {GLO.MAINrutaOutput}')
        GLO.MAINrutaOutput = asignarMAINrutaOutput(
            GLO.MAINprocedimiento,
            GLO.MAINrutaOutput,
            GLO.MAIN_RAIS_DIR,
            LCLobjetivoSiReglado,
            LCLcuadrante,
        )
        print(f'clidaux-> MAINrutaOutput (b2): {GLO.MAINrutaOutput}')
    # ==========================================================================

    # ==========================================================================
    if GLO.MAINrutaOutput is None:
        print(f'clidaux-> ATENCION: no se ha asignado correctamente MAINrutaOutput: {GLO.MAINrutaOutput}')
        print(f'{TB}-> Revisar codigo')
        sys.exit(0)
    elif not os.path.exists(GLO.MAINrutaOutput):
        print(f'clidaux-> No existe el directorio {GLO.MAINrutaOutput} -> Se crea automaticamente')
        try:
            os.makedirs(GLO.MAINrutaOutput)
        except:
            print(f'{TB}-> No se ha podido crear el directorio {GLO.MAINrutaOutput}. Revisar MAINprocedimiento')
            sys.exit(0)
    # ==========================================================================

    # ==========================================================================
    if (
        GLO.GLBLcrearTilesTargetDeCartoRefSoloSiHaySingUseSuficientes
        or GLO.GLBLcrearTilesTargetMiniSubCelSoloSiHayNoSueloSuficientes
    ):
        subDirTrain = 'trainSel'
    else:
        subDirTrain = 'trainAll'
    # ==========================================================================
    if MAIN_ENTORNO == 'calendula':
        GLO.MAIN_MDLS_DIR = '/LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1/data'
#         GLO.MAIN_MDLS_DIR = os.path.abspath(os.path.join(MAIN_RAIZ_DIR, 'cartolidar/cartolidar/data'))
        GLO.GLBL_TRAIN_DIR = os.path.join(GLO.MAINrutaOutput, subDirTrain)
    elif MAIN_ENTORNO == 'colab':
        GLO.MAIN_MDLS_DIR = os.path.join(MAIN_RAIZ_DIR, 'data')
        GLO.GLBL_TRAIN_DIR = os.path.join(MAIN_RAIZ_DIR, 'data/datasets/cartolid/trainImg')
    elif 'MAINrutaRaiz' in dir(GLO):
        GLO.MAIN_MDLS_DIR = os.path.abspath(os.path.join(
            GLO.MAINrutaRaiz,
            'data'
        ))
        GLO.GLBL_TRAIN_DIR = os.path.join(GLO.MAINrutaOutput, subDirTrain)
        # GLO.GLBL_TRAIN_DIR = os.path.abspath(os.path.join(
        #     GLO.MAINrutaRaiz,
        #     'data/datasets/cartolid/trainImg'
        # ))
    else:
        if 'cartolidar' in MAIN_RAIZ_DIR:
            GLO.MAIN_MDLS_DIR = os.path.abspath(os.path.join(MAIN_RAIZ_DIR, '../data'))
        else:
            GLO.MAIN_MDLS_DIR = os.path.join(MAIN_RAIZ_DIR, 'data')
        if MAIN_PC == 'JCyL':
            # Imagenes de entrenamiento en disco externo
            # GLO.GLBL_TRAIN_DIR = 'D:/trainImg'
            # GLO.GLBL_TRAIN_DIR = os.path.join(RAIZ_DIR, 'cartolidout/train')
            # GLO.GLBL_TRAIN_DIR = os.path.join(GLO.MAINrutaOutput, subDirTrain)
            # Imagenes de entrenamiento en disco duro
            # GLO.GLBL_TRAIN_DIR = os.path.join(RAIZ_DIR, 'data/datasets/cartolid/trainImg')
            # GLO.GLBL_TRAIN_DIR = 'C:/_ws/cartolidout/train'
            GLO.GLBL_TRAIN_DIR = os.path.join(GLO.MAINrutaOutput, subDirTrain)
        else:
            # En casa
            # GLO.GLBL_TRAIN_DIR = os.path.join(RAIZ_DIR, 'data/trainImg')
            GLO.GLBL_TRAIN_DIR = os.path.join(GLO.MAINrutaOutput, subDirTrain)
    # ==========================================================================


    # ==========================================================================
    # ======================== Procesados especiales ===========================
    # ================ RENOMBRAR_FICHEROS, MERGEAR, GEOINTEGRAR ================
    # ==================== COMPRIMIR_LAS, DESCOMPRIMIR_LAZ ===================== 
    # ==== CREAR_SHAPE, CREAR_CAPA_CON_UNA_PROPIEDAD_DE_LOS_FICHEROS_LIDAR =====
    # ==========================================================================


    # ==========================================================================
    MOSTRAR_CONFIGURACION = __verbose__ >= 1
    if MOSTRAR_CONFIGURACION:
        print(f'{"":_^80}')
        print(f'{" clidaux-> Configuracion final ":_^80}')
        print(f'{"":_^80}')
        print(f'{TB}{"MAINobjetivoEjecucion":.<21}: {GLO.MAINobjetivoEjecucion}')
        print(f'{TB}{"MAINobjetivoSiReglado":.<21}: {LCLobjetivoSiReglado}')
        print(f'{TB}{"MAINprocedimiento":.<21}: {GLO.MAINprocedimiento}')
        print(f'{TB}{"MAINrutaRaiz":.<21}: {GLO.MAINrutaRaiz}')
        print(f'{TB}{"MAINmiRutaProyecto":.<21}: {GLO.MAINmiRutaProyecto}')
        print(f'{TB}{"MAINrutaCarto":.<21}: {GLO.MAINrutaCarto}')
        print(f'{TB}{"MAINrutaLaz":.<21}: {GLO.MAINrutaLaz}')
        print(f'{TB}{"MAINrutaOutput":.<21}: {GLO.MAINrutaOutput}')
        print(f'{TB}{"MAINcuadrante":.<21}: {GLO.MAINcuadrante}')
        if 'MAIN_RAIZ_DIR' in dir(GLO):
            print(f'{TB}{"MAIN_RAIZ_DIR":.<21}: {GLO.MAIN_RAIZ_DIR}')
        else:
            print(f'{TB}{"MAIN_RAIZ_DIR":.<21}: {"no en clidbase.xls"}')
        if 'MAIN_RAIS_DIR' in dir(GLO):
            print(f'{TB}{"MAIN_RAIS_DIR":.<21}: {GLO.MAIN_RAIS_DIR}')
        else:
            print(f'{TB}{"MAIN_RAIS_DIR":.<21}: {"no en clidbase.xls"}')
        if 'MAIN_MDLS_DIR' in dir(GLO):
            print(f'{TB}{"MAIN_MDLS_DIR":.<21}: {GLO.MAIN_MDLS_DIR}')
        else:
            print(f'{TB}{"MAIN_MDLS_DIR":.<21}: {"no en clidbase.xls"}')
        if 'GLBL_TRAIN_DIR' in dir(GLO):
            print(f'{TB}{"GLBL_TRAIN_DIR":.<21}: {GLO.GLBL_TRAIN_DIR}')
        else:
            print(f'{TB}{"GLBL_TRAIN_DIR":.<21}: {"no en clidbase.xls"}')
        print(f'{"":=^80}')
    # ==========================================================================

    #print('clidaux: Creando directorio: {}'.format(GLO.MAINrutaOutput))
    # try:
    #     creaDirectorio(GLO.MAINrutaOutput)
    # except:
    #     time.sleep(10)
    #     creaDirectorio(GLO.MAINrutaOutput)


    # ==========================================================================
    GLO.GLBLficheroDeControlGral = os.path.join(
        GLO.MAINrutaOutput,
        'GlobalControl_{}.txt'.format(MAINusuario)
    )
    # ==========================================================================
    creaRutaDeFichero(GLO.GLBLficheroDeControlGral)
    # ==========================================================================

    # ==========================================================================
    # Nombres de los modelos convolucionales
    if GLO.GLBLpredecirCubiertasSingularesConvolucional or GLO.GLBLpredecirClasificaMiniSubCelConvolucional:
        if (
            not GLO.GLBLmodeloCartolidMiniSubCelEntrenado is None
            and GLO.GLBLmodeloCartolidMiniSubCelEntrenado != ''
        ):
            idCuadranteActual = '_{}'.format((LCLcuadrante)[:2].upper())
            indexCuadranteModelo = GLO.GLBLmodeloCartolidMiniSubCelEntrenado.find('_Png') - 4
            if indexCuadranteModelo > 0:
                idCuadranteModelo = GLO.GLBLmodeloCartolidMiniSubCelEntrenado[indexCuadranteModelo: indexCuadranteModelo + 3]
                GLO.GLBLmodeloCartolidMiniSubCelEntrenado = GLO.GLBLmodeloCartolidMiniSubCelEntrenado.replace(
                    idCuadranteModelo,
                    idCuadranteActual
                )
        if (
            not GLO.GLBLmodeloCartolidCartoSinguEntrenadoA is None
            and GLO.GLBLmodeloCartolidCartoSinguEntrenadoA != ''
        ):
            idCuadranteActual = '_{}'.format((LCLcuadrante)[:2].upper())
            indexCuadranteModelo = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA.find('_Png') - 4
            if indexCuadranteModelo > 0:
                idCuadranteModelo = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA[indexCuadranteModelo: indexCuadranteModelo + 3]
                GLO.GLBLmodeloCartolidCartoSinguEntrenadoA = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA.replace(
                    idCuadranteModelo,
                    idCuadranteActual
                )
        if (
            not GLO.GLBLmodeloCartolidCartoSinguEntrenadoB is None
            and GLO.GLBLmodeloCartolidCartoSinguEntrenadoB != ''
        ):
            idCuadranteActual = '_{}'.format((LCLcuadrante)[:2].upper())
            indexCuadranteModelo = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB.find('_Png') - 4
            if indexCuadranteModelo > 0:
                idCuadranteModelo = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB[indexCuadranteModelo: indexCuadranteModelo + 3]
                GLO.GLBLmodeloCartolidCartoSinguEntrenadoB = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB.replace(
                    idCuadranteModelo,
                    idCuadranteActual
                )

        # Nombre del modelo acumulativo
        if LCLcuadrante != '' and ARGSnInputsModeloNln != 0 and ARGScodModeloNln != '':
            # Si se incluyen estos argumentos en linea de comandos, prevalecen sobre el nombre del fichero xls de configuracion
            nInputVars = ARGSnInputsModeloNln
            if ARGScodModeloNln == '64+32+16_resBatchN':
                GLO.GLBLnombreFicheroConModeloParaInferencia = 'NNCaleLote{}_i{:03}_h64_h32_h16_o10_dropoutPriUlt_normHL_RNN'.format(
                    LCLcuadrante.upper(),
                    nInputVars
                )
            else:
                print('clidclas-> ATENCION: codigo de modelo en linea de comandos no implementado: {}'.format(ARGScodModeloNln))
                sys.exit(0)
            print('clidclas-> Nombre del modelo: {}'.format(GLO.GLBLnombreFicheroConModeloParaInferencia))
        elif (
            not GLO.GLBLnombreFicheroConModeloParaInferencia is None
            and GLO.GLBLnombreFicheroConModeloParaInferencia != ''
        ):
            idCuadranteActual = 'Lote{}'.format((LCLcuadrante)[:2].upper())
            indexCuadranteModelo = GLO.GLBLnombreFicheroConModeloParaInferencia.find('_i') - 6
            if indexCuadranteModelo > 0:
                idCuadranteModelo = GLO.GLBLnombreFicheroConModeloParaInferencia[indexCuadranteModelo: indexCuadranteModelo + 6]
                GLO.GLBLnombreFicheroConModeloParaInferencia = GLO.GLBLnombreFicheroConModeloParaInferencia.replace(
                    idCuadranteModelo,
                    idCuadranteActual
                )

        # GLO.GLBLmodeloCartolidMiniSubCelEntrenado = 'clidGen_cale_LasClass_2_345_6_reDepurada_Png6_012345_20210605v0.h5'
        if GLO.GLBLmodeloCartolidMiniSubCelEntrenado:
            iniDataset = 13
            if '__Png' in GLO.GLBLmodeloCartolidMiniSubCelEntrenado:
                finDataset = GLO.GLBLmodeloCartolidMiniSubCelEntrenado.find('__Png')
            elif '_Png' in GLO.GLBLmodeloCartolidMiniSubCelEntrenado:
                finDataset = GLO.GLBLmodeloCartolidMiniSubCelEntrenado.find('_Png')
            else:
                finDataset = GLO.GLBLmodeloCartolidMiniSubCelEntrenado.find('.h5')
            txtDataset = GLO.GLBLmodeloCartolidMiniSubCelEntrenado[iniDataset: finDataset]
            if '_Png' in GLO.GLBLmodeloCartolidMiniSubCelEntrenado: # Incluye '__Png'
                iniNumPngs = GLO.GLBLmodeloCartolidMiniSubCelEntrenado.find('_Png') + 1
                finNumPngs = iniNumPngs + 4
                txtNumPngs = GLO.GLBLmodeloCartolidMiniSubCelEntrenado[iniNumPngs: finNumPngs]
                intNumPngs = int(txtNumPngs[-1])
                iniLstPngs = finNumPngs + 1
                finLstPngs = iniLstPngs + intNumPngs
                txtLstPngs = GLO.GLBLmodeloCartolidMiniSubCelEntrenado[iniLstPngs: finLstPngs]
            else:
                print('clidaux-> ATENCION: revisar el nombre del modelo entrenado (no incluye _PngX): {}'.format(GLO.GLBLmodeloCartolidMiniSubCelEntrenado))
                intNumPngs = 0
                txtLstPngs = ''

            MAIN_COD_18_16N_04_MODELOENTRENADO_MINI = 'cartolidMiniSubCel{}{}'.format(txtDataset, txtNumPngs)
            MAIN_LISTA_PNGS_MODELOENTRENADO_MINI = 'X{}'.format(txtLstPngs)
            # print('clidaux-> MAIN_COD_18_16N_04_MODELOENTRENADO_MINI:', MAIN_COD_18_16N_04_MODELOENTRENADO_MINI)
            # print('txtDataset:', txtDataset)
            # print('txtNumPngs:', txtNumPngs)
            # print('txtLstPngs:', txtLstPngs)

        # GLO.GLBLmodeloCartolidCartoSinguEntrenadoA = 'clidGen_cale_UsosDisp12_45678_Png6_012345_20210612v0.h5.h5'
        # GLO.GLBLmodeloCartolidCartoSinguEntrenadoA = 'clidGen_cale_UsosDisp_2_45678_Png6_012345_20210202.h5.h5'
        if GLO.GLBLmodeloCartolidCartoSinguEntrenadoA:
            if '__Png' in GLO.GLBLmodeloCartolidCartoSinguEntrenadoA:
                finDataset = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA.find('__Png')
            elif '_Png' in GLO.GLBLmodeloCartolidCartoSinguEntrenadoA:
                finDataset = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA.find('_Png')
            else:
                finDataset = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA.find('.h5')
            txtDataset = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA[iniDataset: finDataset] # Puede ser: UsosDisp12_45678, UsosDisp_2_45678
            if '_Png' in GLO.GLBLmodeloCartolidCartoSinguEntrenadoA:
                iniNumPngs = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA.find('_Png') + 1
                finNumPngs = iniNumPngs + 4
                txtNumPngs = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA[iniNumPngs: finNumPngs]
                intNumPngs = int(txtNumPngs[-1])
                iniLstPngs = finNumPngs + 1
                finLstPngs = iniLstPngs + intNumPngs
                txtLstPngs = GLO.GLBLmodeloCartolidCartoSinguEntrenadoA[iniLstPngs: finLstPngs]
            else:
                print('clidaux-> ATENCION: revisar el nombre del modelo entrenadoA (no incluye _PngX): {}'.format(GLO.GLBLmodeloCartolidCartoSinguEntrenadoA))
                intNumPngs = 0
                txtLstPngs = ''
            MAIN_COD_18_16N_04_MODELOENTRENADO_CART_ = 'cartolidCartoSingu{}{}'.format(txtDataset, txtNumPngs)
            MAIN_COD_18_16N_04_MODELOENTRENADO_CARTA = 'cartolidCartoSingu{}{}'.format(txtDataset, txtNumPngs)
            MAIN_LISTA_PNGS_MODELOENTRENADO_CART_ = 'X{}'.format(txtLstPngs)
            MAIN_LISTA_PNGS_MODELOENTRENADO_CARTA = 'X{}'.format(txtLstPngs)
        else:
            MAIN_COD_18_16N_04_MODELOENTRENADO_CART_ = 'cartolidCartoSingu_'
            MAIN_COD_18_16N_04_MODELOENTRENADO_CARTA = 'cartolidCartoSingu_'
            MAIN_LISTA_PNGS_MODELOENTRENADO_CART_ = 'X123456'
            MAIN_LISTA_PNGS_MODELOENTRENADO_CARTA = 'X123456'
        # print('clidaux-> MAIN_COD_18_16N_04_MODELOENTRENADO_CARTA:', MAIN_COD_18_16N_04_MODELOENTRENADO_CARTA)
        # print('txtDataset:', txtDataset)
        # print('txtNumPngs:', txtNumPngs)
        # print('txtLstPngs:', txtLstPngs)
    
        # GLO.GLBLmodeloCartolidCartoSinguEntrenadoB = 'clidGen_cale_UsosDisp___45678_Png6_012345_20210202.h5.h5'
        if GLO.GLBLmodeloCartolidCartoSinguEntrenadoB:
            if '__Png' in GLO.GLBLmodeloCartolidCartoSinguEntrenadoB:
                finDataset = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB.find('__Png')
            elif '_Png' in GLO.GLBLmodeloCartolidCartoSinguEntrenadoB:
                finDataset = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB.find('_Png')
            else:
                finDataset = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB.find('.h5')
            txtDataset = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB[iniDataset: finDataset] # Puede ser: UsosDisp12_45678, UsosDisp_2_45678
            if '_Png' in GLO.GLBLmodeloCartolidCartoSinguEntrenadoB:
                iniNumPngs = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB.find('_Png') + 1
                finNumPngs = iniNumPngs + 4
                txtNumPngs = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB[iniNumPngs: finNumPngs]
                intNumPngs = int(txtNumPngs[-1])
                iniLstPngs = finNumPngs + 1
                finLstPngs = iniLstPngs + intNumPngs
                txtLstPngs = GLO.GLBLmodeloCartolidCartoSinguEntrenadoB[iniLstPngs: finLstPngs]
            else:
                print('clidaux-> ATENCION: revisar el nombre del modelo entrenadoB (no incluye _PngX): {}'.format(GLO.GLBLmodeloCartolidCartoSinguEntrenadoA))
                intNumPngs = 0
                txtLstPngs = ''
            MAIN_COD_18_16N_04_MODELOENTRENADO_CARTB = 'cartolidCartoSingu{}{}'.format(txtDataset, txtNumPngs)
            MAIN_LISTA_PNGS_MODELOENTRENADO_CARTB = 'X{}'.format(txtLstPngs)
        else:
            MAIN_COD_18_16N_04_MODELOENTRENADO_CARTB = 'cartolidCartoSingu_'
            MAIN_LISTA_PNGS_MODELOENTRENADO_CARTB = 'X123456'
        # print('clidaux-> MAIN_COD_18_16N_04_MODELOENTRENADO_CARTB:', MAIN_COD_18_16N_04_MODELOENTRENADO_CARTB)
        # print('txtDataset:', txtDataset)
        # print('txtNumPngs:', txtNumPngs)
        # print('txtLstPngs:', txtLstPngs)
    
        # GLO.GLBLmodeloCartolid128PixelesEntrenado = 'modeloPix2PixGeneratEntrenado_calendula_Pn6_012345_20201224.h5'
        txtDataset = 'SingUse128pixel'
        txtNumPngs = 'Png6'
        txtLstPngs = '012345'
        MAIN_COD_18_16N_04_MODELOENTRENADO_128P = 'cartolid128Pixeles{}{}'.format(txtDataset, txtNumPngs)
        MAIN_LISTA_PNGS_MODELOENTRENADO_128P = 'X{}'.format(txtLstPngs)
    else:
        MAIN_COD_18_16N_04_MODELOENTRENADO_MINI = ''
        MAIN_COD_18_16N_04_MODELOENTRENADO_CART_ = ''
        MAIN_COD_18_16N_04_MODELOENTRENADO_CARTA = ''
        MAIN_COD_18_16N_04_MODELOENTRENADO_CARTB = ''
        MAIN_COD_18_16N_04_MODELOENTRENADO_128P = ''
    
        MAIN_LISTA_PNGS_MODELOENTRENADO_MINI = ''
        MAIN_LISTA_PNGS_MODELOENTRENADO_CART_ = ''
        MAIN_LISTA_PNGS_MODELOENTRENADO_CARTA = ''
        MAIN_LISTA_PNGS_MODELOENTRENADO_CARTB = ''
        MAIN_LISTA_PNGS_MODELOENTRENADO_128P = ''
    # ==========================================================================

    if (
        (
            not GLO.GLBLmodeloCartolidMiniSubCelEntrenado is None
            and not '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLmodeloCartolidMiniSubCelEntrenado
        )
        or (
            not GLO.GLBLmodeloCartolidCartoSinguEntrenadoA is None
            and not '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLmodeloCartolidCartoSinguEntrenadoA
        )
        or (
            not GLO.GLBLmodeloCartolidCartoSinguEntrenadoB is None
            and not '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLmodeloCartolidCartoSinguEntrenadoB
        )
        or (
            not GLO.GLBLnombreFicheroConModeloParaInferencia is None
            and not '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLnombreFicheroConModeloParaInferencia
        )

        or (
            not MAIN_COD_18_16N_04_MODELOENTRENADO_MINI is None
            and not '{}_'.format((LCLcuadrante[:2]).upper()) in MAIN_COD_18_16N_04_MODELOENTRENADO_MINI
        )
        or (
            not MAIN_COD_18_16N_04_MODELOENTRENADO_CART_ is None
            and not '{}_'.format((LCLcuadrante[:2]).upper()) in MAIN_COD_18_16N_04_MODELOENTRENADO_CART_
        )
    ):
        print(f'\n{"":_^80}')
        print('clidaux-> Verificando modelos entrenados disponibles para el cuadrante {} (identificador completo: {}):'.format((LCLcuadrante[:2]).upper(), LCLcuadrante))
        print('\t-> GLBLmodeloCartolidMiniSubCelEntrenado:    {}'.format(GLO.GLBLmodeloCartolidMiniSubCelEntrenado))
        print('\t-> GLBLmodeloCartolidCartoSinguEntrenadoA:   {}'.format(GLO.GLBLmodeloCartolidCartoSinguEntrenadoA))
        print('\t-> GLBLmodeloCartolidCartoSinguEntrenadoB:   {}'.format(GLO.GLBLmodeloCartolidCartoSinguEntrenadoB))
        print('\t-> GLBLnombreFicheroConModeloParaInferencia: {}'.format(GLO.GLBLnombreFicheroConModeloParaInferencia))
        print('\t-> MAIN_COD_18_16N_04_MODELOENTRENADO_MINI:  {}'.format(MAIN_COD_18_16N_04_MODELOENTRENADO_MINI))
        print('\t-> MAIN_COD_18_16N_04_MODELOENTRENADO_CART_: {}'.format(MAIN_COD_18_16N_04_MODELOENTRENADO_CART_))
        print('\t-> cuadrante: {}_'.format((LCLcuadrante[:2]).upper()), '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLmodeloCartolidMiniSubCelEntrenado)
        if not GLO.GLBLmodeloCartolidMiniSubCelEntrenado is None:
            if not '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLmodeloCartolidMiniSubCelEntrenado:
                print(
                    'clidaux-> ATENCION 1: el modelo <{}> no esta disponible para el cuadrante {}'.format(
                        GLO.GLBLmodeloCartolidMiniSubCelEntrenado,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
            else:
                print(
                    '\tModelo1 <{}> entrenado OK para el cuadrante {}'.format(
                        GLO.GLBLmodeloCartolidMiniSubCelEntrenado,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
        if not GLO.GLBLmodeloCartolidCartoSinguEntrenadoA is None:
            if not '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLmodeloCartolidCartoSinguEntrenadoA:
                print(
                    'clidaux-> ATENCION 2: el modelo <{}> no esta disponible para el cuadrante {}'.format(
                        GLO.GLBLmodeloCartolidCartoSinguEntrenadoA,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
            else:
                print(
                    '\tModelo2 <{}> entrenado OK para el cuadrante {}'.format(
                        GLO.GLBLmodeloCartolidCartoSinguEntrenadoA,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
        if not GLO.GLBLmodeloCartolidCartoSinguEntrenadoB is None:
            if not '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLmodeloCartolidCartoSinguEntrenadoB:
                print(
                    'Modelo3: el modelo <{}> no esta disponible para el cuadrante {} (no esencial)'.format(
                        GLO.GLBLmodeloCartolidCartoSinguEntrenadoB,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
            else:
                print(
                    '\tModelo3 <{}> entrenado OK para el cuadrante {}'.format(
                        GLO.GLBLmodeloCartolidCartoSinguEntrenadoB,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
        else:
            print(
                '\tModelo3 <{}> no se usa para el cuadrante {}'.format(
                    GLO.GLBLmodeloCartolidCartoSinguEntrenadoB,
                    '{}_'.format((LCLcuadrante[:2]).upper()),
                )
            )

        if (
            GLO.MAINobjetivoEjecucion == 'CREAR_LAZ'
            and not GLO.GLBLnombreFicheroConModeloParaInferencia is None
        ):
            if not '{}_'.format((LCLcuadrante[:2]).upper()) in GLO.GLBLnombreFicheroConModeloParaInferencia:
                # Solo necesito el modelo para inferencia si voy a CREAR_LAZ
                print(
                    'clidaux-> ATENCION 4: el modelo <{}> no esta disponible para el cuadrante {}'.format(
                        GLO.GLBLnombreFicheroConModeloParaInferencia,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
            else:
                print(
                    '\tModelo4 <{}> entrenado OK para el cuadrante {}'.format(
                        GLO.GLBLnombreFicheroConModeloParaInferencia,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
        if not MAIN_COD_18_16N_04_MODELOENTRENADO_MINI is None:
            if not '{}_'.format((LCLcuadrante[:2]).upper()) in MAIN_COD_18_16N_04_MODELOENTRENADO_MINI:
                print(
                    '\tModelo5 <{}> no disponible para el cuadrante {} (no esencial)'.format(
                        MAIN_COD_18_16N_04_MODELOENTRENADO_MINI,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
            else:
                print(
                    '\tModelo5 <{}> entrenado OK para el cuadrante {}'.format(
                        MAIN_COD_18_16N_04_MODELOENTRENADO_MINI,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )

        if not MAIN_COD_18_16N_04_MODELOENTRENADO_CART_ is None:
            if not '{}_'.format((LCLcuadrante[:2]).upper()) in MAIN_COD_18_16N_04_MODELOENTRENADO_CART_:
                print(
                    '\tModelo6 <{}> no disponible para el cuadrante {} (no esencial)'.format(
                        MAIN_COD_18_16N_04_MODELOENTRENADO_CART_,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
            else:
                print(
                    '\tModelo6 <{}> entrenado OK para el cuadrante {}'.format(
                        MAIN_COD_18_16N_04_MODELOENTRENADO_CART_,
                        '{}_'.format((LCLcuadrante[:2]).upper()),
                    )
                )
        print(f'{"":=^80}')

    # ==========================================================================
    paramConfigAdicionalesGLBL = {}
    paramConfigAdicionalesGLBL['MAINusuario'] = [MAINusuario, 'str', '', 'GrupoMAIN', MAINusuario]
    paramConfigAdicionalesGLBL['MAIN_ENTORNO'] = [MAIN_ENTORNO, 'str', '', 'GrupoMAIN', MAIN_ENTORNO]
    paramConfigAdicionalesGLBL['MAIN_PC'] = [MAIN_PC, 'str', '', 'GrupoMAIN', MAIN_PC]

    paramConfigAdicionalesGLBL['MAIN_DRIVE'] = [MAIN_DRIVE, 'str', '', 'GrupoDirsFiles', MAIN_DRIVE]
    paramConfigAdicionalesGLBL['MAIN_HOME_DIR'] = [MAIN_HOME_DIR, 'str', '', 'GrupoDirsFiles', MAIN_HOME_DIR]
    paramConfigAdicionalesGLBL['MAIN_FILE_DIR'] = [MAIN_FILE_DIR, 'str', '', 'GrupoDirsFiles', MAIN_FILE_DIR]
    paramConfigAdicionalesGLBL['MAIN_PROJ_DIR'] = [MAIN_PROJ_DIR, 'str', '', 'GrupoDirsFiles', MAIN_PROJ_DIR]
    paramConfigAdicionalesGLBL['MAIN_RAIZ_DIR'] = [MAIN_RAIZ_DIR, 'str', '', 'GrupoDirsFiles', MAIN_RAIZ_DIR]
    paramConfigAdicionalesGLBL['MAIN_THIS_DIR'] = [MAIN_THIS_DIR, 'str', '', 'GrupoDirsFiles', MAIN_THIS_DIR]
    paramConfigAdicionalesGLBL['MAIN_WORK_DIR'] = [MAIN_WORK_DIR, 'str', '', 'GrupoDirsFiles', MAIN_WORK_DIR]
    paramConfigAdicionalesGLBL['MAIN_RAIZ_DIR'] = [GLO.MAIN_RAIZ_DIR, 'str', '', 'GrupoDirsFiles', MAIN_RAIZ_DIR]
    paramConfigAdicionalesGLBL['MAIN_RAIS_DIR'] = [GLO.MAIN_RAIS_DIR, 'str', '', 'GrupoDirsFiles', MAIN_RAIZ_DIR]

    paramConfigAdicionalesGLBL['MAINmiRutaProyecto'] = [MAIN_PROJ_DIR, 'str', '', 'GrupoDirsFiles', MAIN_PROJ_DIR]
    paramConfigAdicionalesGLBL['MAINrutaLaz'] = [GLO.MAINrutaLaz, 'str', '', 'GrupoDirsFiles']
    # paramConfigAdicionalesGLBL['MAINrutaLazFinal'] = [
    #     GLO.MAINrutaLaz,
    #     'str',
    #     'Ruta en la que estan los ficheros laz o las (la usada finalmente, que puede ser distinta del establecido en cartolid.xml)',
    #     'GrupoDirsFiles',
    #     ]
    paramConfigAdicionalesGLBL['MAINrutaOutput'] = [GLO.MAINrutaOutput, 'str', '', 'GrupoDirsFiles']
    paramConfigAdicionalesGLBL['MAINrutaCarto'] = [GLO.MAINrutaCarto, 'str', '', 'GrupoDirsFiles']

    paramConfigAdicionalesGLBL['MAIN_MDLS_DIR'] = [GLO.MAIN_MDLS_DIR, 'str', '', 'GrupoDirsFiles', GLO.MAIN_MDLS_DIR]
    paramConfigAdicionalesGLBL['GLBL_TRAIN_DIR'] = [GLO.GLBL_TRAIN_DIR, 'str', '', 'GrupoDirsFiles', GLO.GLBL_TRAIN_DIR]

    paramConfigAdicionalesGLBL['GLBLficheroDeControlGral'] = [GLO.GLBLficheroDeControlGral, 'str', '', 'GrupoDirsFiles']
    paramConfigAdicionalesGLBL['GLBL_TRAIN_DIR'] = [GLO.GLBL_TRAIN_DIR, 'str', '', 'GrupoDirsFiles']

    paramConfigAdicionalesGLBL['GLBLmodeloCartolidMiniSubCelEntrenado'] = [GLO.GLBLmodeloCartolidMiniSubCelEntrenado, 'str', '', 'GrupoPredConvolucional']
    paramConfigAdicionalesGLBL['GLBLmodeloCartolidCartoSinguEntrenadoA'] = [GLO.GLBLmodeloCartolidCartoSinguEntrenadoA, 'str', '', 'GrupoPredConvolucional']
    paramConfigAdicionalesGLBL['GLBLmodeloCartolidCartoSinguEntrenadoB'] = [GLO.GLBLmodeloCartolidCartoSinguEntrenadoB, 'str', '', 'GrupoPredConvolucional']
    paramConfigAdicionalesGLBL['GLBLnombreFicheroConModeloParaInferencia'] = [GLO.GLBLnombreFicheroConModeloParaInferencia, 'str', '', 'GrupoPredConvolucional']

    paramConfigAdicionalesGLBL['MAIN_COD_18_16N_04_MODELOENTRENADO_MINI'] = [MAIN_COD_18_16N_04_MODELOENTRENADO_MINI, 'str', '', 'GrupoModeloEntrenado']
    paramConfigAdicionalesGLBL['MAIN_COD_18_16N_04_MODELOENTRENADO_CART_'] = [MAIN_COD_18_16N_04_MODELOENTRENADO_CART_, 'str', '', 'GrupoModeloEntrenado']
    paramConfigAdicionalesGLBL['MAIN_COD_18_16N_04_MODELOENTRENADO_CARTA'] = [MAIN_COD_18_16N_04_MODELOENTRENADO_CARTA, 'str', '', 'GrupoModeloEntrenado']
    paramConfigAdicionalesGLBL['MAIN_COD_18_16N_04_MODELOENTRENADO_CARTB'] = [MAIN_COD_18_16N_04_MODELOENTRENADO_CARTB, 'str', '', 'GrupoModeloEntrenado']
    paramConfigAdicionalesGLBL['MAIN_COD_18_16N_04_MODELOENTRENADO_128P'] = [MAIN_COD_18_16N_04_MODELOENTRENADO_128P, 'str', '', 'GrupoModeloEntrenado']

    paramConfigAdicionalesGLBL['MAIN_LISTA_PNGS_MODELOENTRENADO_MINI'] = [MAIN_LISTA_PNGS_MODELOENTRENADO_MINI, 'str', '', 'GrupoModeloEntrenado']
    paramConfigAdicionalesGLBL['MAIN_LISTA_PNGS_MODELOENTRENADO_CART_'] = [MAIN_LISTA_PNGS_MODELOENTRENADO_CART_, 'str', '', 'GrupoModeloEntrenado']
    paramConfigAdicionalesGLBL['MAIN_LISTA_PNGS_MODELOENTRENADO_CARTA'] = [MAIN_LISTA_PNGS_MODELOENTRENADO_CARTA, 'str', '', 'GrupoModeloEntrenado']
    paramConfigAdicionalesGLBL['MAIN_LISTA_PNGS_MODELOENTRENADO_CARTB'] = [MAIN_LISTA_PNGS_MODELOENTRENADO_CARTB, 'str', '', 'GrupoModeloEntrenado']
    paramConfigAdicionalesGLBL['MAIN_LISTA_PNGS_MODELOENTRENADO_128P'] = [MAIN_LISTA_PNGS_MODELOENTRENADO_128P, 'str', '', 'GrupoModeloEntrenado']

    paramConfigAdicionalesGLBL['MAINprocedimiento'] = [GLO.MAINprocedimiento, 'str', '', 'GrupoMAIN']

    paramConfigAdicionalesGLBL['GLBLsoloCuadradoDeEjemplo'] = [GLO.GLBLsoloCuadradoDeEjemplo, 'bool', '', 'GrupoGestionDeFicheros']
    paramConfigAdicionalesGLBL['GLBLreprocesarFallidosUsandoMenosRAM'] = [GLO.GLBLreprocesarFallidosUsandoMenosRAM, 'bool', '', 'GrupoGestionDeFicheros']
    paramConfigAdicionalesGLBL['GLBLficheroLasTemporal'] = [GLO.GLBLficheroLasTemporal, 'bool', '', 'GrupoGestionDeFicheros']
    paramConfigAdicionalesGLBL['GLBLprocesarComprimidosLaz'] = [GLO.GLBLprocesarComprimidosLaz, 'bool', '', 'GrupoGestionDeFicheros']

    paramConfigAdicionalesGLBL['GLBLshapeNumPoints'] = [GLO.GLBLshapeNumPoints, 'int', '', 'GrupoShape']
    paramConfigAdicionalesGLBL['GLBLshapeFilter'] = [GLO.GLBLshapeFilter, 'str', '', 'GrupoShape']

    paramConfigAdicionalesGLBL['GLBLtipoLectura'] = [GLO.GLBLtipoLectura, 'str', '', 'GrupoManejoMemoria']
    paramConfigAdicionalesGLBL['GLBLusoDeRAM'] = [GLO.GLBLusoDeRAM, 'str', '', 'GrupoManejoMemoria']

    paramConfigAdicionalesGLBL['GLBLnumeroDePuntosAleer'] = [GLO.GLBLnumeroDePuntosAleer, 'int', '', 'GrupoLecturaPuntosPasadas']
    paramConfigAdicionalesGLBL['GLBLgrabarPercentilesRelativos'] = [GLO.GLBLgrabarPercentilesRelativos, 'bool', '', 'GrupoDasoLidar']
    paramConfigAdicionalesGLBL['GLBLmetrosCelda'] = [GLO.GLBLmetrosCelda, 'float', '', 'GrupoDimensionCeldasBloques']

    paramConfigAdicionalesGLBL['MAINprocedimientoFinal'] = [
        GLO.MAINprocedimiento,
        'str',
        'Procedimiento finalmente ejecutado (puede ser distinto del establecido en cartolid.xml)',
        'GrupoMAIN',
    ]

    if LCLverbose:
        print('clidaux-> paramConfigAdicionalesGLBL:')
        for nuevoParametro in paramConfigAdicionalesGLBL.keys():
            print('\t{:>40}: {}'.format(nuevoParametro, paramConfigAdicionalesGLBL[nuevoParametro]))

    _ = clidconfig.leerCambiarVariablesGlobales(
        nuevosParametroConfiguracion=paramConfigAdicionalesGLBL,
        LCL_idProceso=MAIN_idProceso,
        inspect_stack=inspect.stack(),
        verbose=False
    )
    return listaDirsLaz, listaSubDirsLaz, coordenadasDeMarcos


# ==============================================================================
def casosEspecialesParaMAINrutaLaz(
        LCLprocedimiento,
        LCLrutaLaz,
        LCLcuadrante,
    ):

    listaDirsLaz = ['']
    listaSubDirsLaz = ['']

    # ==========================================================================
    # ============== Casos especiales para MAINrutaLaz =========================
    # ==========================================================================
    if (
        LCLprocedimiento.startswith('DESCOMPRIMIR_LAZ')
        or LCLprocedimiento.startswith('COMPRIMIR_LAS')
    ):
        # Rutas ad-hoc
        listaDirsLaz = ['lasfile-nw']
        listaSubDirsLaz = ['RGBI_laz_H29']
    elif MAIN_ENTORNO == 'calendula':
        # Solo los laz se ubican en scratch, el resto en home
        # GLO.MAINrutaCarto = '/scratch/jcyl_spi_1/jcyl_spi_1_1/data/carto'
        # GLO.MAINrutaCarto = '/LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1/data/carto'
        # MAIN_RAIZ_DIR = '/scratch/jcyl_spi_1/jcyl_spi_1_1/'

        # Se recorren estos subdirectorios de laz:
        listaDirsLaz = ['']
        listaDirsLaz = ['', 'lasfile-se', 'lasfile-ce']
        listaDirsLaz = ['roquedos']

        if (LCLcuadrante)[:2].upper() == 'CE':
            listaDirsLaz = ['lasfile-ce']
        elif (LCLcuadrante)[:2].upper() == 'NW':
            listaDirsLaz = ['lasfile-nw']
        elif (LCLcuadrante)[:2].upper() == 'NE':
            listaDirsLaz = ['lasfile-ne']
        elif (LCLcuadrante)[:2].upper() == 'SE':
            listaDirsLaz = ['lasfile-se']
        elif (LCLcuadrante)[:2].upper() == 'SW':
            listaDirsLaz = ['lasfile-sw']
        elif (LCLcuadrante)[:2].upper() == 'XX':
            listaDirsLaz = ['lasfile-ce', 'lasfile-nw', 'lasfile-ne', 'lasfile-se', 'lasfile-sw']
            listaDirsLaz = ['lasfile-yy']
            listaDirsLaz = ['lasfiles']
        else:
            listaDirsLaz = ['', 'lasfile-ce', 'lasfile-nw', 'lasfile-ne', 'lasfile-se', 'lasfile-sw', 'roquedos']

        if (
            LCLprocedimiento.startswith('COMPRIMIR_LAS')
            or LCLprocedimiento.startswith('DESCOMPRIMIR_LAZ')
        ):
            if 'RGBI_cartolid' in LCLprocedimiento:
                listaSubDirsLaz = ['RGBI_cartolid']
            elif 'RGB_cartolid' in LCLprocedimiento:
                listaSubDirsLaz = ['RGB_cartolid']
            elif 'IRG_cartolid' in LCLprocedimiento:
                listaSubDirsLaz = ['IRC_cartolid']
            elif 'IRG_cartolid' in LCLprocedimiento:
                listaSubDirsLaz = ['IRG_cartolid']
            else:
                listaSubDirsLaz = ['RGBI']
        elif (
            LCLprocedimiento.endswith('UNIFICAR_RGBI')
            or LCLprocedimiento.endswith('COLOREAR_RGBI')
        ):
            listaSubDirsLaz = ['IRC']
            # listaSubDirsLaz = ['IRC/_corregidos_versionOk_preORT_preCOLOR'] # Lo traslado temporalmente a SW y lo proceso ahi
        else:
            if GLO.MAINobjetivoEjecucion == 'CREAR_PUNTOS_TRAIN_ACUMULATIVO_NPZ':
                # listaSubDirsLaz = ['lazNew']
                listaSubDirsLaz = ['lazNewCLR']
            else:
                if LCLcuadrante[:2].upper() == 'SE':
                    if 'SELECT' in LCLprocedimiento:
                        listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI', 'RGBI_laz_H29', 'RGBI_laz']
                    else:
                        listaSubDirsLaz = ['RGBI_laz_cartolid_20220316']
                elif LCLcuadrante[:2].upper() == 'NE':
                        listaSubDirsLaz = ['', '000_laz1']  # , '000_laz2
                elif LCLcuadrante[:2].upper() == 'NW':
                    if 'SELECT' in LCLprocedimiento:
                        primeraVersionDeLasFiles = False
                        if primeraVersionDeLasFiles:
                            # La primera vez proceso una muestra (SELECT) de bloques sin clasicacion
                            # para tener una primera version de lasFiles clasificados provisionalmente en lasNew
                            # Los lasFiles clasificados los muevo a lazNewCLR para trabajar preferencialmente con ellos en lo sucesivo
                            # La segunda vez trabajo sobre esos lasFiles clasificados para mejorarlos
                            rutaLazCompleta = os.path.join(GLO.MAINrutaLaz, listaDirsLaz[0], 'lazNewCLR')
                            if len(listaDirsLaz) == 1 and os.path.isdir(rutaLazCompleta):
                                print('clidaux-> Aviso: Uso lazNewCLR para usar lasFiles provisionalmente clasificados y disponer de clase del miniSubCel')
                                listaSubDirsLaz = ['lazNewCLR']
                            else:
                                print('clidaux-> Aviso: No se ha encontrado la ruta de lasFiles pro-clasificados: {}'.format(rutaLazCompleta))
                                print('\t-> listaDirsLaz: {}'.format(listaDirsLaz))
                                # listaSubDirsLaz = ['RGBI_H29']
                                # listaSubDirsLaz = ['RGBI_laz_H29', 'RGBI_laz']
                                # listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI']
                                listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI', 'RGBI_laz_H29', 'RGBI_laz']
                        else:
                            listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI', 'RGBI_laz_H29', 'RGBI_laz']
                    else:
                        listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI']
                        listaSubDirsLaz = ['lazNewCompletoAll_RGBI']
                        listaSubDirsLaz = ['lazNewCompleto_RGBI_laz_20220302']
                        listaSubDirsLaz = ['lazNewCompleto_RGBI_laz_20220316']

                elif LCLcuadrante[:2].upper() == 'CE':
                    if 'SELECT' in LCLprocedimiento:
                        listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI', 'RGBI_laz_H29', 'RGBI_laz']
                    else:
                        listaSubDirsLaz = ['RGBI_laz_cartolid_20220316']
                elif LCLcuadrante[:2].upper() == 'SE':
                    if 'SELECT' in LCLprocedimiento:
                        listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI', 'RGBI_laz_H29', 'RGBI_laz']
                    else:
                        listaSubDirsLaz = ['RGBI_laz_cartolid_20220316']

                elif LCLcuadrante[:2].upper() == 'SW':
                    # listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI', 'RGBI_laz_H29', 'RGBI_laz']
                    # listaSubDirsLaz = ['RGBI_H29']
                    listaSubDirsLaz = ['RGBI_laz_H29', 'RGBI_laz']
                    # listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI']
                elif LCLcuadrante[:2].upper() == 'XX':
                    listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI_H30']
                else:
                    # listaSubDirsLaz = ['RGBI_laz']
                    listaSubDirsLaz = ['RGBI']

        if '_H29_' in GLO.MAINprocedimiento:
            # Por el momento, esto solo lo uso para AUTOMATICO_EN_CALENDULA_SCRATCH_H29_COLOREAR_RGBI
            for nSubDir, subDirLaz in enumerate(listaSubDirsLaz):
                if '_H29' in subDirLaz.upper():
                    print(f'\nclidaux-> ATENCION: revisar este codigo para adaptarlo a la lista de directorios que quiero recorrer:')
                    print(f'\t-> GLO.MAINprocedimiento: {GLO.MAINprocedimiento}')
                    print(f'\t-> listaSubDirsLaz:       {listaSubDirsLaz}')
                    sys.exit(0)
                listaSubDirsLaz[nSubDir] = subDirLaz + '_H29'

    elif LCLprocedimiento.startswith('LAS_INFO_ASK_LASDIR'):
        LCLrutaLaz = preguntarRutaLaz(GLO.MAINrutaLaz)
    elif LCLprocedimiento == 'LAS_INFO_BASE_LASDIR':
        LCLrutaLaz = GLO.MAINrutaLaz
    elif (
        LCLprocedimiento.startswith('AUTOMATICO_CON_RUTA_LAZ_PREDETERMINADA')
        or LCLprocedimiento.startswith('AUTOMATICO_EN_CALENDULA')
        or LCLprocedimiento.startswith('LAS_INFO')
    ):
        # Se usan los valores establecidos por defecto
        if (LCLcuadrante)[:2].upper() == 'CE':
            listaDirsLaz = ['lasfile-ce']
        elif (LCLcuadrante)[:2].upper() == 'NE':
            listaDirsLaz = ['lasfile-ne']
        elif (LCLcuadrante)[:2].upper() == 'NW':
            listaDirsLaz = ['lasfile-nw']
        elif (LCLcuadrante)[:2].upper() == 'SE':
            listaDirsLaz = ['lasfile-se']
        elif (LCLcuadrante)[:2].upper() == 'SW':
            listaDirsLaz = ['lasfile-sw']
        elif (LCLcuadrante)[:2].upper() == 'XX':
            listaDirsLaz = ['lasfile-ce', 'lasfile-nw', 'lasfile-ne', 'lasfile-se', 'lasfile-sw']
            listaDirsLaz = ['lasfile-yy']
        else:
            listaDirsLaz = ['', 'lasfile-ce', 'lasfile-nw', 'lasfile-ne', 'lasfile-se', 'lasfile-sw', 'roquedos']
        listaSubDirsLaz = ['', 'RGBI_H29', 'RGBI', 'RGBI_laz_H29', 'RGBI_laz']
        print(f'\n{"":_^80}')
        print(f'clidaux-> ATENCION: ASIGNACION PROVISIONAL DE listaDirsLaz Y listaSubDirsLaz EN FUNCION DE LCLcuadrante:')
        print(f'{TB}cuando el procedimiento es AUTOMATICO_CON_RUTA_LAZ_PREDETERMINADA, AUTOMATICO_EN_CALENDULA o LAS_INFO')
        print(f'{TB}Lista de directorios y subdirectorios de {GLO.MAINrutaLaz} que se exploran:')
        print(f'{TB}-> listaDirsLaz:    {listaDirsLaz}')
        print(f'{TB}-> listaSubDirsLaz: {listaSubDirsLaz}')
        print(f'{"":=^80}')
    elif LCLprocedimiento == 'PRECONFIGURADO_SINRUTA':
        bloqueElegido = 0
        if not LCLrutaLaz:
            LCLrutaLaz = preguntarRutaLaz(r'../laz/')
    elif (LCLprocedimiento).startswith('AUTOMATICO_DISCOEXTERNO'):
        # Incluye 'AUTOMATICO_DISCOEXTERNO_UNIFICAR_RGBI_E'
        unidadLaz = LCLprocedimiento[-1:]
        # LCLrutaLaz = unidadLaz + ':/laz1/'
        # LCLrutaLaz = unidadLaz + ':/CE/CIR/LAS/Huso_30/'
        LCLrutaLaz = unidadLaz + ':/lidardata_2017_2021/lasfile_SE/IRC/'
    elif (LCLprocedimiento).startswith('AUTOMATICO_SIGMENA'):
        rutaSigmenaIntercam = LCLprocedimiento[19:]
        LCLrutaLaz = os.path.join('O:Sigmena/intercam/', rutaSigmenaIntercam)
    elif LCLprocedimiento[:20] == 'AUTOMATICO_CUADRANTE':
        bloqueElegido = 0
        miCuadrante = LCLprocedimiento[21:23]
        miMarco = LCLprocedimiento[-8:]
        miUbicacionLaz = LCLprocedimiento[24:31]
        if LCLrutaLaz is None or LCLrutaLaz == '':
            if miUbicacionLaz == 'SIGMENA':
                LCLrutaLaz = 'O:/Sigmena/Intercam/laz/'
            else:
                input('ATENCION: nombre de procedimiento incorrecto: si empieza con AUTOMATIZADO_CUADRANTE solo admite SIGMENA en las posiciones 24:31')
                sys.exit(0)
        print('  MAINrutaLaz     ', LCLrutaLaz)

        if miCuadrante == 'XX':
            listaDirsLaz = ['2010_NW', '2010_NE', '2014_SW', '2010_SE']
        elif miCuadrante in ['NW', 'NE', 'SW', 'SE']:
            listaDirsLaz = ['2010_%s' % miCuadrante]
        else:
            input('ATENCION: nombre de procedimiento incorrecto: si empieza con AUTOMATIZADO_CUADRANTE solo admite cuadrantes NW, NE, SW o SE')
            sys.exit(0)
        if miMarco == 'SINMARCO':
            GLO.GLBLsoloCuadradoDeEjemplo = False
        elif miMarco == 'CONMARCO':
            GLO.GLBLsoloCuadradoDeEjemplo = True
        else:
            input('ATENCION: nombre de procedimiento incorrecto: si empieza con AUTOMATIZADO_CUADRANTE debe terminar con SINMARCO o CONMARCO')
            sys.exit(0)

    elif (
        LCLprocedimiento == 'PRECONFIGURADO_CONRUTA_4CUADRANTES_SIGMENA_CONOSINMARCO'
        or LCLprocedimiento == 'PRECONFIGURADO_CONRUTA_4CUADRANTES_DISCOEXTERNO_CONOSINMARCO'
    ):
        if LCLprocedimiento == 'PRECONFIGURADO_CONRUTA_4CUADRANTES_DISCOEXTERNO_CONOSINMARCO':
            selec = input('Para trabajar en disco externo (x:/LAZ/) pulsa la letra de unidad (C)')
            try:
                LCLrutaLaz = selec[:1] + ':/LAZ/'
            except:
                print('Entrada incorrecta')
                LCLrutaLaz = 'C:/LAZ/'
        else:
            #LCLrutaLaz = 'O:/Sigmena/Intercam/laz/'
            pass

        listaDirsLaz = elegirSubcarpetas(LCLrutaLaz)
        bloqueElegido = 0

        selec = input('\nProcesar solo determinados cuadrados de cada cuadrante? (n/s)')
        GLO.GLBLsoloCuadradoDeEjemplo = True if selec.upper() == 'S' else False

        if GLO.GLBLsoloCuadradoDeEjemplo:
            xMin_NW, yMin_NW, ladoMarco_NW = 200000, 4700000, 40000  # Zona generica
            xMin_NE, yMin_NE, ladoMarco_NE = 450000, 4650000, 20000  # Zona generica
            xMin_NE, yMin_NE, ladoMarco_NE = 458000, 4672000, 20000  # Cuadricula de ensayo Burgos
            xMin_NE, yMin_NE, ladoMarco_NE = 436000, 4760000, 20000  # Soncillo - Machorras
            xMin_SW, yMin_SW, ladoMarco_SW = 240000, 4584000, 22000  # Cuadricula de ensayo Zamora
            xMin_SE, yMin_SE, ladoMarco_SE = 490000, 4600000, 20000  # Zona generica
            coordenadasDeMarcos = {
                'NW': [xMin_NW, yMin_NW, ladoMarco_NW],
                'NE': [xMin_NE, yMin_NE, ladoMarco_NE],
                'SW': [xMin_SW, yMin_SW, ladoMarco_SW],
                'SE': [xMin_SE, yMin_SE, ladoMarco_SE],
            }
            listaValores = ['x min (inclusive)', 'y Min (inclusive)', 'lado del marco']
            listaCuadrantes = ['NW', 'NE', 'SW', 'SE']
            selec = input('\nEditar coordenadas para cada cuadrante? (n/s)')
            if selec.upper() == 'S':
                for cuadrante in listaCuadrantes:
                    selec = input('\nEditar coordenadas para el cuadrante %s? (n/s/x) (x: no procesarlo)' % cuadrante)
                    if selec.upper() == 'X':
                        coordenadasDeMarcos[cuadrante] = [0, 0, 0]
                    elif selec.upper() == 'S':
                        nuevosValores = []
                        for nValor, nombreValor in enumerate(listaValores):
                            strNuevoValor = input('Cuadrante %s -> %s (%i):' % (cuadrante, nombreValor, coordenadasDeMarcos[cuadrante][nValor]))
                            if strNuevoValor == '':
                                nuevosValores.append(coordenadasDeMarcos[cuadrante][nValor])
                            else:
                                nuevosValores.append(int(strNuevoValor))
                        coordenadasDeMarcos[cuadrante] = nuevosValores
        else:
            coordenadasDeMarcos = {}

    elif LCLprocedimiento == 'MANUAL':
        selec = input('Nombre de este PC (%s) -> ' % (GLO.MAINusuario))
        if selec != '':
            GLO.MAINusuario = selec
        print('Los ficheros de control empiezan con una linea %s\n' % (GLO.MAINusuario))

        selec = input('Ancho del pixel: (10 m)')
        try:
            GLO.GLBLmetrosCelda = float(selec)
        except:
            GLO.GLBLmetrosCelda = 10.0
        print('Ancho del pixel: %i m\n' % (GLO.GLBLmetrosCelda))

        LCLrutaLaz = preguntarRutaLaz(r'../laz/')

        selec = input('\nProcesar solo los que quedaron incompletos en anteriores sesiones? (n/s)')
        GLO.GLBLprocesarSoloIncompletos = True if selec.upper() == 'S' else False
        print(
            'Procesado normal'
            if GLO.GLBLprocesarSoloIncompletos
            else 'Se procesan los que quedaron incompletos en la primera vuelta (por falta de RAM disponible)'
        )
        GLO.GLBLreprocesarFallidosUsandoMenosRAM = False

        print('1. Uso de RAM standard')
        print('2. Uso de RAM alternativo')
        selec = input('Selecciona opcion 1-2 (1):')

        try:
            if int(selec) == 1:
                GLO.GLBLusoDeRAM = 'standard'
            elif int(selec) == 2:
                GLO.GLBLusoDeRAM = 'alternativo'
            else:
                sys.exit()
        except:
            GLO.GLBLusoDeRAM = 'standard'
        print('Opcion elegida: %s' % (GLO.GLBLusoDeRAM))

        selec = input('\nNumero de registros a procesar: (por defecto: todos -> Escribir 0 o [enter] directamente)')
        try:
            GLO.GLBLnumeroDePuntosAleer = int(selec)
        except:
            GLO.GLBLnumeroDePuntosAleer = 0
        print('Numero de puntos: %s' % (str(GLO.GLBLnumeroDePuntosAleer) if GLO.GLBLnumeroDePuntosAleer != 0 else 'todos'))

        selec = input('\nCalcular percentiles de valores absolutos (altitud o cota absoluta): (s/n)')
        GLO.GLBLgrabarPercentilesAbsolutos = False if selec.upper() == 'N' else True
        print('Calcular percentiles absolutos:', GLO.GLBLgrabarPercentilesAbsolutos)

        selec = input('\nCalcular percentiles de valores relativos (altura sobre el plano-suelo o plano-basal): (s/n)')
        GLO.GLBLgrabarPercentilesRelativos = False if selec.upper() == 'N' else True
        print('Calcular percentiles relativos:', GLO.GLBLgrabarPercentilesRelativos)
        # ==========================================================================

        exploraDirectorios = False
        # selec = input('Explorar directorios de '+LCLrutaLaz+ ' (n/s)')
        # exploraDirectorios = True if selec.upper() == 'S' else False

        if exploraDirectorios:
            listaDirsLaz = []
            for (_, dirnames, _) in os.walk(LCLrutaLaz):
                listaDirsLaz.extend(dirnames)
                # files.extend(filenames)
                break
            print(
                'Directorios en %s:' % (LCLrutaLaz),
            )
            print(listaDirsLaz)
            if len(listaDirsLaz) == 0:
                print('No se rastrean los directorios')
                listaDirsLaz = ['']
            # bloqueElegido = 5
        else:
            print('\n0. Procesar ficheros de %s' % (LCLrutaLaz))
            print('1. Procesar los ficheros laz de 2010_NW (%s)' % (LCLrutaLaz + '2010_NW/'))
            print('2. Procesar los ficheros laz de 2010_NW (%s)' % (LCLrutaLaz + '2010_NW_las/'))
            print('3. Procesar los ficheros las de 2010_NE (%s)' % (LCLrutaLaz + '2010_NE/'))
            print('4. Procesar los ficheros laz de 2010_NE (%s)' % (LCLrutaLaz + '2010_NE_las/'))
            print('5. Procesar los ficheros laz de 2014_SW (%s)' % (LCLrutaLaz + '2014_SW/'))
            print('6. Procesar los ficheros las de 2014_SW (%s)' % (LCLrutaLaz + '2014_SW_las/'))
            print('7. Procesar los ficheros laz de 2010_SE (%s)' % (LCLrutaLaz + '2010_SE/'))
            print('8. Procesar los ficheros las de 2010_SE (%s)' % (LCLrutaLaz + '2010_SE_las/'))
            try:
                bloqueElegido = int(input('Selecciona opcion 1-9 (0):'))
            except:
                bloqueElegido = 0
            if bloqueElegido == 1:
                listaDirsLaz = ['2010_NW/']
            elif bloqueElegido == 2:
                listaDirsLaz = ['2010_NW_las/']
            elif bloqueElegido == 3:
                listaDirsLaz = ['2010_NE/']
            elif bloqueElegido == 4:
                listaDirsLaz = ['2010_NE_las/']
            elif bloqueElegido == 5:
                listaDirsLaz = ['2014_SW/']
            elif bloqueElegido == 6:
                listaDirsLaz = ['2014_SW_las/']
            elif bloqueElegido == 7:
                listaDirsLaz = ['2010_SE/']
            elif bloqueElegido == 8:
                listaDirsLaz = ['2010_SE_las/']
            else:
                listaDirsLaz = ['']

        selec = input('Crear ficheros las de forma permanente (no se borran una vez procesados) (S/n)')
        GLO.GLBLficheroLasTemporal = True if selec.upper() == 'N' else False
        if GLO.GLBLficheroLasTemporal:
            print('Los ficheros las creados son temporales (se borran tras procesarlos)\n')
        else:
            print('Los ficheros las creados son permanentes\n')
    elif LCLprocedimiento.startswith('CREAR_CAPA_CON_UNA_PROPIEDAD_DE_LOS_FICHEROS_LIDAR'):
        # Rutas por defecto, o bien:
        if not LCLrutaLaz:
            # LCLrutaLaz = 'E:/lidardata_2017_2021/lasfile_SE/IRC'
            LCLrutaLaz = 'E:/lidardata_2017_2021/lasfile_CE/IRC'
        pass
    elif LCLprocedimiento == 'CREAR_SHAPE':
        listaDirsLaz = ['']
        bloqueElegido = 0
        LCLrutaLaz = preguntarRutaLaz(r'../laz/')
        selec = input('\nNumero de puntos del shape: (1000 por defecto; indicar 0 para todos)')
        try:
            GLO.GLBLshapeNumPoints = int(selec)
        except:
            GLO.GLBLshapeNumPoints = 1000
        print('\nNumero de puntos: %s' % (str(GLO.GLBLshapeNumPoints) if GLO.GLBLshapeNumPoints != 0 else 'todos'))
        if GLO.GLBLshapeNumPoints != 0:
            GLO.GLBLtipoLectura = 'registrosPorLotes'
        else:
            GLO.GLBLtipoLectura = 'registrosIndividuales'

        print('\n1. Todas las clases')
        print('2. Todas las clases menos la 12 (relleno)')
        print('3. Solo puntos de borde de escaneo')
        selec = input('Selecciona opcion (1):')
        try:
            if int(selec) == 2:
                GLO.GLBLshapeFilter = 'sinClase12'
            elif int(selec) == 3:
                GLO.GLBLshapeFilter = 'soloEdge'
            else:
                GLO.GLBLshapeFilter = 'noFilter'
        except:
            GLO.GLBLshapeFilter = 'noFilter'
        print('Tipo de filtro: %s\n' % (GLO.GLBLshapeFilter))
    elif LCLprocedimiento == 'RENOMBRAR_FICHEROS':
        LCLrutaLaz = 'O:/Sigmena/Intercam/laz/'

        listaDirsLaz = ['2010_NW', '2010_NE', '2014_SW', '2010_SE']
        listaDirsLaz = ['2010_NW_Huso_29', '2010_NW_las']
        GLO.GLBLprocesarComprimidosLaz = True
        bloqueElegido = 0

    elif LCLprocedimiento == 'MERGEAR':
        input('Lo desarrollo en raster2vector de clidgis.py (rescatado de copiaSeg/2017/lidasMerge.py)')
        sys.exit()

    elif LCLprocedimiento == 'GEOINTEGRAR':
        input('Lo desarrollo en raster2vector de clidcluster.py (antes GIS/cluster.py, renombrado a cluster_old_VerCartolid_clidax.py')
        sys.exit()

    else:
        print('\nRevisar el nombre del procedimiento en cartolid.xlm. MAINprocedimiento:', LCLprocedimiento)
        sys.exit()

    # print('clidaux-> 3b LCLrutaLaz:', LCLrutaLaz)

    return LCLrutaLaz, listaDirsLaz, listaSubDirsLaz


# ==============================================================================
def asignarMAINrutaCarto(
    ):
    if MAIN_ENTORNO == 'calendula':
#         MAINrutaRaizCarto =  LCLmiRutaRais
        MAINrutaRaizCarto =  GLO.MAINrutaRaiz
        print(f'clidaux-> GLO.MAINrutaCarto en calendula es GLO.MAINrutaRaiz: {GLO.MAINrutaRaiz}')
    elif 'MAINrutaRaiz' in dir(GLO):
        MAINrutaRaizCarto =  GLO.MAINrutaRaiz
    else:
        if 'cartolidar' in MAIN_RAIZ_DIR:
            MAINrutaRaizCarto = os.path.abspath(os.path.join(MAIN_RAIZ_DIR, '..'))
        else:
            MAINrutaRaizCarto = os.path.abspath(MAIN_RAIZ_DIR)
    print(f'clidaux-> MAINrutaRaizCarto: {MAINrutaRaizCarto}')
    print(f'{TB}-> GLO.MAINrutaRaiz: {GLO.MAINrutaRaiz}')

    # Primera opcion:
    MAINrutaCarto1 = os.path.abspath(
        os.path.join(
            MAINrutaRaizCarto,
            'data/carto/'
        )
    )
    if os.path.isdir(MAINrutaCarto1):
        LCLrutaCarto = MAINrutaCarto1
    else:
        # Segunda opcion:
        MAINrutaCarto2 = os.path.abspath(
            os.path.join(
                MAINrutaRaizCarto,
                '../data/carto/'
            )
        )
        if os.path.isdir(MAINrutaCarto2):
            LCLrutaCarto = MAINrutaCarto2
        else:
            myLog.warning(f'{"":+^80}')
            myLog.warning(f'clidaux-> ATENCION: No se ha localizado el directorio data/carto con informacion cartografica de apoyo.')
            myLog.warning(f'{TB}Directorios buscados:')
            myLog.warning(f'{TB}{TV}{MAINrutaCarto1}')
            myLog.warning(f'{TB}{TV}{MAINrutaCarto2}')
            myLog.warning(f'{"":+^80}')
            LCLrutaCarto = ''

    return LCLrutaCarto


# ==============================================================================
def asignarMAINrutaOutput(
        LCLprocedimiento,
        LCLrutaOutput,
        LCLmiRutaRais,
        LCLobjetivoSiReglado,
        LCLcuadrante,
    ):

    if MAIN_ENTORNO == 'calendula':
        MAINrutaRaizOutput =  LCLmiRutaRais
    elif 'MAINrutaRaiz' in dir(GLO):
        MAINrutaRaizOutput =  GLO.MAINrutaRaiz
    else:
        if 'cartolidar' in MAIN_RAIZ_DIR:
            MAINrutaRaizOutput = os.path.abspath(os.path.join(MAIN_RAIZ_DIR, '..'))
        else:
            MAINrutaRaizOutput = os.path.abspath(MAIN_RAIZ_DIR)

    print(f'clidaux-> MAINrutaRaizOutput (b): {MAINrutaRaizOutput}')
    # ==========================================================================
    # Ruta por defecto
    GLO.MAINrutaOutput = os.path.abspath(os.path.join(
        MAINrutaRaizOutput,
        'cartolidout'
    ))
    print(f'clidaux-> MAINrutaOutput por defecto: {GLO.MAINrutaOutput}')
    # ==========================================================================
    # Casos especiales
    if (
        LCLobjetivoSiReglado == 'GENERAL'
        or LCLobjetivoSiReglado == 'CREAR_TILES_TRAIN'
        or LCLobjetivoSiReglado == 'PREPROCESADO_EN_CALENDULA'
        or LCLobjetivoSiReglado == 'CREAR_PUNTOS_TRAIN_ACUMULATIVO_NPZ'
        or LCLobjetivoSiReglado == 'CREAR_PUNTOS_TRAIN_ROQUEDOS'
        or LCLobjetivoSiReglado == 'CREAR_LAZ'
        or LCLobjetivoSiReglado == 'EXTRA2'
        or LCLobjetivoSiReglado == 'EXTRA3'
    ):
        if (
            LCLprocedimiento == 'AUTOMATICO_EN_CALENDULA_SCRATCH'
        ):
            LCLrutaOutput = os.path.abspath(os.path.join(
                MAINrutaRaizOutput,
                # '..',
                'cartolidout_{}_{}_{}'.format(
                    (LCLcuadrante)[:2].upper(),
                    LCLobjetivoSiReglado,
                    'completo'
                )
            ))
        elif (
            LCLprocedimiento == 'AUTOMATICO_EN_CALENDULA_SELECT'
            or LCLprocedimiento == 'AUTOMATICO_CON_RUTA_LAZ_PREDETERMINADA'
            or LCLprocedimiento == 'AUTOMATICO_CON_RUTA_LAZ_PREDETERMINADA_SELECT'
        ):
            LCLrutaOutput = os.path.abspath(os.path.join(
                MAINrutaRaizOutput,
                # '..',
                'cartolidout_{}_{}'.format(
                    (LCLcuadrante)[:2].upper(),
                    LCLobjetivoSiReglado,
                )
            ))
        elif LCLprocedimiento == 'AUTOMATICO_EN_CALENDULA_SCRATCH_COLOREAR_RGBI':
            LCLrutaOutput = os.path.abspath(os.path.join(
                MAINrutaRaizOutput,
                # '..',
                'cartolidout_{}_{}_{}'.format(
                    (LCLcuadrante)[:2].upper(),
                    'COLOREAR_RGBI',
                    'completo'
                )
            ))
        elif LCLprocedimiento == 'AUTOMATICO_EN_CALENDULA_SCRATCH_H29_COLOREAR_RGBI':
            LCLrutaOutput = os.path.abspath(os.path.join(
                MAINrutaRaizOutput,
                # '..',
                'cartolidout_{}_{}_{}'.format(
                    (LCLcuadrante)[:2].upper(),
                    'COLOREAR_RGBI_H29',
                    'completo'
                )
            ))
        elif not GLO.MAINrutaOutput is None:
            LCLrutaOutput = GLO.MAINrutaOutput
            print(f'clidaux-> 6 Asignando LCLrutaOutput: {LCLrutaOutput}')
        elif not LCLcuadrante is None:
            LCLrutaOutput = os.path.abspath(os.path.join(
                MAINrutaRaizOutput,
                # '..',
                'cartolidout_{}_{}'.format(
                    (LCLcuadrante)[:2].upper(),
                    LCLobjetivoSiReglado
                )
            ))
            print(f'clidaux-> 7 Asignando LCLrutaOutput: {LCLrutaOutput}')
        elif LCLobjetivoSiReglado == 'GENERAL':
            LCLrutaOutput = os.path.abspath(os.path.join(
                MAINrutaRaizOutput,
                # '..',
                'cartolidout'
            ))
            print(f'clidaux-> 8 Asignando LCLrutaOutput: {LCLrutaOutput}')
        else:
            LCLrutaOutput = GLO.MAINrutaOutput
            print(f'clidaux-> 9 Asignando LCLrutaOutput: {LCLrutaOutput}')
        if not LCLcuadrante is None:
            LCLrutaOutput = (LCLrutaOutput).replace('_XX', '_{}'.format((LCLcuadrante)[:2].upper()))
        # print('\t{:.<25}: {}'.format('MAINrutaOutput (adaptado)', LCLrutaOutput))
    elif (
        LCLrutaOutput is None
        or LCLrutaOutput == 'None'
        or LCLrutaOutput == ''
    ):
        LCLrutaOutput = os.path.abspath(os.path.join(
            MAINrutaRaizOutput,
            # '..',
            'cartolidout_{}'.format(
                (LCLcuadrante)[:2].upper()
            )
        ))
        LCLrutaOutput = (LCLrutaOutput).replace('_XX', '_{}'.format((LCLcuadrante)[:2].upper()))
        print('\t{:.<25}: {}'.format('MAINrutaOutput (adaptado)', LCLrutaOutput))
    else:
        print('\t{:.<25}: {}'.format('MAINrutaOutput (original)', LCLrutaOutput))



    if (LCLprocedimiento).startswith('AUTOMATICO_DISCOEXTERNO'):
        # Incluye 'AUTOMATICO_DISCOEXTERNO_UNIFICAR_RGBI_E'
        unidadLaz = LCLprocedimiento[-1:]
        # LCLrutaOutput = unidadLaz + ':/CE/cartolidout/'
        LCLrutaOutput = unidadLaz + ':/lidardata_2017_2021/Result/SE/cartolidout/'
    elif LCLprocedimiento[:20] == 'AUTOMATICO_CUADRANTE':
        # Guardo los resultados en una ruta que cuelga de la ruta de los laz (no de la ruta de cartolid)
        bloqueElegido = 0
        miCuadrante = LCLprocedimiento[21:23]
        miMarco = LCLprocedimiento[-8:]
        if LCLrutaOutput == '':
            LCLrutaOutput = os.path.join(GLO.MAIN_RAIZ_DIR, 'cartolidout_%s_%s' % (miCuadrante, miMarco))
        else:
            # LCLrutaOutput = quitarContrabarrasAgregarBarraFinal(LCLrutaOutput)
            LCLrutaOutput = (LCLrutaOutput).replace(os.sep, '/')

    if LCLrutaOutput == '' or LCLrutaOutput == None:
        miCarpetaResultadosInicial = 'cartolidout'
        print(f'\n{"":_^80}')
        print('Escribir ruta en la que se guardan los resultados:')
        print('Se interpreta como ruta completa si empieza por "/" o por letra de unidad ("C:", "D:", etc.).')
        print('y como subdirectorio de "%s" en el resto de los casos' % GLO.MAIN_RAIZ_DIR)
        selec = input('Introduce un valor (pulsa [enter] para valor por defecto: %s): ' %
                      os.path.join(GLO.MAIN_RAIZ_DIR, miCarpetaResultadosInicial))
        if selec[1:2] == ':' or selec[:1] == '/':
            # Es una ruta completa en vez de un subdirectorio
            LCLrutaOutput = selec
        elif selec != '':
            LCLrutaOutput = os.path.join(GLO.MAIN_RAIZ_DIR, selec)
        else:
            LCLrutaOutput = os.path.join(GLO.MAIN_RAIZ_DIR, miCarpetaResultadosInicial)
        print('{:^80}'.format(''))

    return LCLrutaOutput




# ==============================================================================
def preguntarRutaLaz(rutaInicial):
    rutaNormalizada = os.path.abspath(rutaInicial)
    # rutaNormalizada = os.path.normpath(rutaInicial)
    # rutaNormalizada = quitarContrabarrasAgregarBarraFinal(rutaNormalizada)
    rutaNormalizada = rutaNormalizada.replace(os.sep, '/')

    print('\nSe solicitan datos:')
    selec = input('\nEscribir la ruta base de los ficheros lidar (.laz o las; p. ej. C:/laz/): (por defecto: %s)' % rutaNormalizada)
    if selec == '':
        rutaFinal = rutaNormalizada
    else:
        # rutaFinal = quitarContrabarrasAgregarBarraFinal(selec)
        rutaFinal = selec.replace(os.sep, '/')
    print('Ruta elegida: %s' % (rutaFinal))
    return rutaFinal


# ==============================================================================
def preguntarRutaCarto(rutaInicial):
    rutaNormalizada = os.path.abspath(rutaInicial)
    # rutaNormalizada = os.path.normpath(rutaInicial)
    # rutaNormalizada = quitarContrabarrasAgregarBarraFinal(rutaNormalizada)
    rutaNormalizada = rutaNormalizada.replace(os.sep, '/')
    selec = input('\nEscribir la ruta base de los ficheros cartograficos (shp, tif, etc; p. ej. C:/data/carto/): (por defecto: %s) ' % rutaNormalizada)
    if selec == '':
        rutaFinal = rutaNormalizada
    else:
        # rutaFinal = quitarContrabarrasAgregarBarraFinal(selec)
        rutaFinal = selec.replace(os.sep, '/')
    print('Ruta elegida: %s' % (rutaFinal))
    return rutaFinal


# ==============================================================================
def elegirSubcarpetas(USERmiRutaRaiz):
    print('\nElegir directorios:')
    print('        (0) Solo los ficheros que cuelgan directamente de %s' % USERmiRutaRaiz)
    print('        (1) Las subcarpetas "2010_NW", "2010_NE", "2014_SW" y "2010_SE"')
    print('        (2) Las subcarpetas "2010_NW_las", "2010_NE_las", "2014_SW_las" y "2010_SE_las"')
    print('        (3) Solo la subcarpeta "2014_SW"')
    print('        (4) Solo la subcarpeta "2010_SE"')
    print('        (6) Ficheros de subcarpetas Zona1 y Zona2, que cuelgan de %s2009' % USERmiRutaRaiz)
    print('        (7) Ficheros de subcarpetas Zona1 y Zona2, que cuelgan de %s2017' % USERmiRutaRaiz)
    print('        (8) Ficheros de subcarpetas Zona1 y Zona2, que cuelgan de %s2009 y %s2017' % (USERmiRutaRaiz, USERmiRutaRaiz))
    print('        (9) Todos los ficheros de todas las subcarpetas que cuelgan de %s (sin implementar)' % USERmiRutaRaiz)
    print('(1) y (3) tienen todos los ficheros y (2) solo ficheros ya descomprimidos.')
    selec = input('\nSelecciona las subcarpetas a procesar (0)')
    if selec.upper() == '1':
        listaDirsLaz = ['2010_NW', '2010_NE', '2014_SW', '2010_SE']
    elif selec.upper() == '2':
        GLO.GLBLdescomprimirLaz = False
        listaDirsLaz = ['2010_NW_las', '2010_NE_las', '2014_SW_las', '2010_SE_las']
    elif selec.upper() == '3':
        listaDirsLaz = ['2014_SW']
    elif selec.upper() == '4':
        listaDirsLaz = ['2010_SE']
    elif selec.upper() == '6':
        listaDirsLaz = ['2009/Zona1', '2009/Zona2']
    elif selec.upper() == '7':
        listaDirsLaz = ['2017/Zona1', '2017/Zona2']
    elif selec.upper() == '8':
        listaDirsLaz = ['2009/Zona1', '2009/Zona2', '2017/Zona1', '2017/Zona2']
    elif selec.upper() == '9':
        listaDirsLaz = ['']
    else:
        listaDirsLaz = ['']
    return listaDirsLaz


# ==============================================================================
def borrarFicheroDeConfiguracionTemporal():

    if GLO.GLBLeliminarTilesTrasProcesado:
        printMsg('\t-> clidaux-> Eliminando input images del entrenamiento del directorio {}'.format(GLO.GLBL_TRAIN_DIR))
        # Ver detalles en clidtry-> leerDirectoriosEnCalendula
        if os.path.isdir(GLO.GLBL_TRAIN_DIR):
            # Elimino el directorio y su contenido
            shutil.rmtree(GLO.GLBL_TRAIN_DIR)
    
            # Elimino fichero a fichero
            # for (thisPath1, filepaths, filenames) in os.walk(GLO.GLBL_TRAIN_DIR):
            #     for filename in filenames:
            #         print('\tBorrando: {}'.format(os.path.join(thisPath1, filename)))
            #     for filepath in filepaths:
            #         for (thisPath2, _, filenames) in os.walk(os.path.join(filepath, GLO.GLBL_TRAIN_DIR)):
            #             print('\tBorrando: {}'.format(os.path.join(thisPath2, filename)))


    configFileNameCfg = sys.argv[0].replace('.py', '%06i.cfg' % MAIN_idProceso)
    if os.path.exists(configFileNameCfg):
        print('clidaux-> Eliminando {}'.format(configFileNameCfg))
        os.remove(configFileNameCfg)
    #configFileNameXlsx = sys.argv[0].replace('.py', '%06i.xlsx' % MAIN_idProceso)
    configFileNameXlsx = sys.argv[0].replace('.py', '{:006}.xlsx'.format(MAIN_idProceso))
    if os.path.exists(configFileNameXlsx):
        print('clidaux-> Eliminando {}'.format(configFileNameXlsx))
        os.remove(configFileNameXlsx)

