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
# from _ast import Or
try:
    import psutil
    psutilDisponible = True
except:
    print('clidconfig-> AVISO: error al importar psutil')
    psutilDisponible = False
# from scipy.spatial.distance import pdist

# Para que funcione: GDAL en eclipse he hecho esto:
# En Windows->Preferences->Pydev->Interpreters->Python interpreter->Pestaña environment -> INlcuir PATH = C:/OSGeo4W64/bin
try:
# if True:
    # print(os.environ['PATH'])
    from osgeo import gdal
    gdalOk = True
except:
    print('clidaux-> No se puede importar gdal "from osgeo", se intenta directamente ("import gdal").')
    gdalOk = False
if not gdalOk:
    try:
        import gdal
        print('           gdal importado ok con "import gdal".\n')
        gdalOk = True
    except:
        gdalOk = False
        print('clidaux-> No se ha podido cargar gdal ni directamente ni desde osgeo')
        print('          -> En windows: comprobar que las variables de entorno apuntan a la version de gdal del env conda activado (clid o pruebas)') 
        print('             GDAL_DRIVER_PATH=C:/OSGeo4W/bin/gdalplugins') 
        # print('\nclidaux-> Se cierra el programa')
        # sys.exit(0)

# ==============================================================================
if __name__ == '__main__':
    print('\nclidaux-> ATENCION: este modulo no se puede ejecutar de forma autonoma')
    sys.exit(0)
# ==============================================================================
if '--cargadoClidaux' in sys.argv:
    moduloPreviamenteCargado = True
    sys.stdout.write(f'\nclidaux-> moduloPreviamenteCargado: {moduloPreviamenteCargado}\n')
    sys.stdout.write(f'          sys.argv: {sys.argv}\n')
else:
    moduloPreviamenteCargado = False
    sys.stdout.write(f'\nclidaux-> moduloPreviamenteCargado: {moduloPreviamenteCargado}\n')
    sys.stdout.write(f'          sys.argv: {sys.argv}\n')
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
        sys.stdout.write(f'clidaux-> ATENCION: revisar asignacion de idProceso.\n')
        sys.stdout.write(f'ARGS_idProceso: {type(ARGS_idProceso)} {ARGS_idProceso}\n')
        sys.stdout.write(f'sys.argv: {sys.argv}\n')
else:
    MAIN_idProceso = 0
    sys.stdout.write(f'clidaux-> ATENCION: revisar codigo de idProceso.\n')
    sys.stdout.write(f'ARGS_idProceso: {type(ARGS_idProceso)} {ARGS_idProceso}\n')
    sys.stdout.write(f'sys.argv: {sys.argv}\n')
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
CONFIGverbose = __verbose__ > 2
# CONFIGverbose = True
if CONFIGverbose:
    sys.stdout.write(f'\nclidaux-> AVISO: CONFIGverbose: {CONFIGverbose} (asignado con codigo en funcion de __verbose__)\n')
if __verbose__ > 1:
    sys.stdout.write(f'\nclidaux-> INFO:  __verbose__:   {__verbose__} (leido en linea de comandos: -v)\n')
    sys.stdout.write(f'clidaux-> sys.argv: {sys.argv}\n')
# ==============================================================================
# ==============================================================================

# ==============================================================================
# ============================ Variables GLOBALES ==============================
# ==============================================================================

# ==============================================================================
# #variablesGlobalesBasicas
# ==============================================================================
# TB = '\t'
TB = ' ' * 10
TV = ' ' * 3
TW = ' ' * 2
# ==============================================================================
# No se importa nada con: from clidaux import *
__all__ = []
# ==============================================================================

# ==============================================================================
# #variablesGlobalesMAINentorno
# ==============================================================================
# Directorio que depende del entorno:
MAIN_HOME_DIR = str(pathlib.Path.home())
# Dir del modulo que se esta ejecutando (clidconfig.py):
MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))  # En calendula /LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1/cartolidar/cartolidar/clidax
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
        if 'benmarjo' in MAIN_HOME_DIR:
            MAIN_PC = 'JCyL'
        elif 'joseb' in MAIN_HOME_DIR:
            MAIN_PC = 'Casa'
        else:
            MAIN_PC = 'Otro'
    except:
        MAIN_ENTORNO = 'calendula'
        MAIN_PC = 'calendula'
# ==============================================================================

# ==============================================================================
# #variablesGlobalesMAINdirs
# ==============================================================================
# Directorios de la aplicacion:
# Dir de clidbase.py:
MAIN_BASE_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))
# Dir de setup.py:
MAIN_PROJ_DIR = os.path.abspath(os.path.join(MAIN_BASE_DIR, '..')) # Equivale a MAIN_FILE_DIR = pathlib.Path(__file__).parent
# Dir en el que esta el proyecto (D:/_clid o /LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1):
MAIN_RAIZ_DIR = os.path.abspath(os.path.join(MAIN_PROJ_DIR, '..'))
# Directorio desde el que se lanza la app (estos dos coinciden):
MAIN_THIS_DIR = os.path.abspath('.')
MAIN_WORK_DIR = os.getcwd()
# Directorio del ejecutable de python:
MAIN_PYTHON_DIR = os.path.dirname(sys.executable)
# ==============================================================================

# ==============================================================================
# Valores provisionales de MAINrutaRaizHome y MAINrutaRaizData que se modificaran 
# despues de obtener GLO (tras leer el .cfg) si el fichero de configuracion
# tiene algun valor en el parametro MAINrutaRaizManual
# Estos parametros tb se asignan en clidbase.py y guardan en el cfg, pero
# clidbase.py importa clidaux antes, x lo q pasa antes x aqui y tb lo hago aqui.
if MAIN_ENTORNO == 'calendula':
    # MAINrutaRaizHome = MAIN_RAIZ_DIR
    MAINrutaRaizHome =  '/LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1'  # = MAIN_RAIZ_DIR
    MAINrutaRaizData = '/scratch/jcyl_spi_1/jcyl_spi_1_1'
else:
    MAINrutaRaizHome = MAIN_RAIZ_DIR
    MAINrutaRaizData = MAIN_RAIZ_DIR
# ==============================================================================

# ==============================================================================
# #variablesGlobalesVERSIONFILE
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
# ============================== Variables TRNS ================================
# ==============================================================================
# ================== TRNS: Variables globales transitorias =====================
# ======= Si las quiero usar en todos los modulos, pasarlas a Globales =========
# ATENCION: las2las no me funciona para descomprimir en memoria
TRNSdescomprimirConlaszip = True
TRNSdescomprimirConlas2las = False
# ==============================================================================

# ==============================================================================
# Version original de la funcion
def infoUsuario(verbose=False):
    if psutilDisponible:
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
myUser = infoUsuario()
myModule = __name__.split('.')[-1]
# ==============================================================================
if not moduloPreviamenteCargado or True:
    print('\nclidaux-> Aviso: creando myLog (ConsLog)')
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
if spec is None or MAIN_ENTORNO == 'calendula':
    if True:
    # try:
        if CONFIGverbose:
            sys.stdout.write(f'\nclidaux-> Intento alternativo de importar clidconfig desde la version local {os.getcwd()}/clidax\n')
        from clidax import clidconfig
        if CONFIGverbose:
            sys.stdout.write(f'\nclidaux-> Ok clidconfig importado del clidax local (2)\n')
    # except:
    #     sys.stdout.write(f'\nclidaux-> Alternativa para cuando el modulo inicial es este u otro modulo de este package:\n')
    #     import clidconfig
    #     if CONFIGverbose:
    #         sys.stdout.write(f'\nclidaux-> Ok clidconfig importado directamente (modulo inicial en el mismo package que clidconfig) (3)\n')
else:
    if CONFIGverbose:
        sys.stdout.write('\nclidaux-> Importando clidconfig desde cartolidar.clidax\n')
    from cartolidar.clidax import clidconfig
    if CONFIGverbose:
        sys.stdout.write(f'\nclidaux-> Ok clidconfig importado de cartolidar.clidax (0)\n')

# ==============================================================================
MAINusuario = infoUsuario(False)
# ==============================================================================
# nuevosParametroConfiguracion = {}
# if CONFIGverbose:
#     print(f'\nclidaux-> A Llamo a clidconfig.leerCambiarVariablesGlobales<> (sin nuevosParametroConfiguracion)')
#     print(f'{TB}para leer los parametros de configuracion del fichero cfg.')
# GLOBALconfigDict = clidconfig.leerCambiarVariablesGlobales(
#     nuevosParametroConfiguracion,
#     LCL_idProceso=MAIN_idProceso,
#     inspect_stack=inspect.stack(),
#     verbose=CONFIGverbose,
# )
# if CONFIGverbose:
#     print(f'clidaux-> B Cargando parametros de configuracion GLOBALconfigDict en GLO')
# GLO = clidconfig.GLO_CLASS(GLOBALconfigDict)

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
# Esto se asigna en clidconfig.py, junto con GLBL_TRAIN_DIR:
# if 'cartolidar' in MAINrutaRaizHome:
#     MAIN_MDLS_DIR = os.path.abspath(os.path.join(
#         MAINrutaRaizHome,
#         '../data'
#     ))
# else:
#     MAIN_MDLS_DIR = os.path.abspath(os.path.join(
#         MAINrutaRaizHome,
#         'data'
#     ))
# ==============================================================================
# Estos parametros tb se asignan en clidbase.py y guardan en el cfg, pero lo reitero aqui para darle autonomia
if __verbose__:
    print(f'\n{"":_^80}')
    print(f'{" clidaux-> Asignando rutas MAIN 1 ":=^80}')
    print(f'{" y guardandolas en el fichero de configuracion cfg ":=^80}')
    print(f'{"":=^80}')
    print(f'{TB}-> MAIN_copyright, MAIN_version, MAIN_idProceso, MAINusuario')
    print(f'{TB}-> MAIN_ENTORNO, MAIN_PC, MAIN_DRIVE')
    print(f'{TB}-> MAIN_HOME_DIR, MAIN_FILE_DIR, MAIN_PROJ_DIR, MAIN_THIS_DIR, MAIN_WORK_DIR')
    print(f'{TB}-> MAIN_RAIZ_DIR, MAINrutaRaizHome, MAINrutaRaizData')
    print(f'{"":=^80}')
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
paramConfigAdicionalesMAIN['MAIN_THIS_DIR'] = [MAIN_THIS_DIR, 'str', '', 'GrupoDirsFiles']
paramConfigAdicionalesMAIN['MAIN_WORK_DIR'] = [MAIN_WORK_DIR, 'str', '', 'GrupoDirsFiles']
# ==============================================================================
paramConfigAdicionalesMAIN['MAIN_RAIZ_DIR'] = [MAIN_RAIZ_DIR, 'str', '', 'GrupoDirsFiles']
# Valores provisionales de MAINrutaRaizHome y MAINrutaRaizData que se modificaran 
# despues de obtener GLO (tras leer el .cfg) si el fichero de configuracion
# tiene algun valor en el parametro MAINrutaRaizManual
# En calendula, no uso la MAINrutaRaizHome que haya en el fichero de configuracion
paramConfigAdicionalesMAIN['MAINrutaRaizHome'] = [
    MAINrutaRaizHome, 'str', '', 'GrupoDirsFiles', MAINrutaRaizHome,
    MAINrutaRaizHome, MAINrutaRaizHome, MAINrutaRaizHome,
    MAINrutaRaizHome, MAINrutaRaizHome, MAINrutaRaizHome,
]
paramConfigAdicionalesMAIN['MAINrutaRaizData'] = [
    MAINrutaRaizData, 'str', '', 'GrupoDirsFiles', MAINrutaRaizData,
    MAINrutaRaizData, MAINrutaRaizData, MAINrutaRaizData,
    MAINrutaRaizData, MAINrutaRaizData, MAINrutaRaizData,
]
# Esto se asigna en clidconfig.py, junto con GLBL_TRAIN_DIR:
# # Creo el parametro MAIN_MDLS_DIR, que no esta en el fichero de configuracion y que depende del entorno
# paramConfigAdicionalesMAIN['MAIN_MDLS_DIR'] = [MAIN_MDLS_DIR, 'str', '', 'GrupoDirsFiles', MAIN_MDLS_DIR]
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
GLO = clidconfig.GLO_CLASS(GLOBALconfigDict)
# ==============================================================================

# ==============================================================================
if (
    'MAINrutaRaizManual' in dir(GLO)
    and not GLO.MAINrutaRaizManual is None
    and GLO.MAINrutaRaizManual != 'None'
    and GLO.MAINrutaRaizManual != ''
):
    if MAIN_ENTORNO == 'calendula':
        # En calendula no hago caso del MAINrutaRaizManual que hay en el .cfg
        MAINrutaRaizHome =  '/LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1'
        MAINrutaRaizData = '/scratch/jcyl_spi_1/jcyl_spi_1_1'
    else:
        MAINrutaRaizHome = GLO.MAINrutaRaizManual
        MAINrutaRaizData = GLO.MAINrutaRaizManual
    # Guardo los nuevos valores en el .cfg:
    paramConfigAdicionalesMAIN = {}
    # En calendula, no uso la MAINrutaRaizHome que haya en el fichero de configuracion.
    paramConfigAdicionalesMAIN['MAINrutaRaizHome'] = [
        MAINrutaRaizHome, 'str', '', 'GrupoDirsFiles', MAINrutaRaizHome,
        MAINrutaRaizHome, MAINrutaRaizHome, MAINrutaRaizHome,
        MAINrutaRaizHome, MAINrutaRaizHome, MAINrutaRaizHome,
    ]
    # Creo el parametro MAINrutaRaizData, que no esta en el fichero de configuracion y que depende del entorno
    paramConfigAdicionalesMAIN['MAINrutaRaizData'] = [
        MAINrutaRaizData, 'str', '', 'GrupoDirsFiles', MAINrutaRaizData,
        MAINrutaRaizData, MAINrutaRaizData, MAINrutaRaizData,
        MAINrutaRaizData, MAINrutaRaizData, MAINrutaRaizData,
    ]
    # Esto se asigna en clidconfig.py, junto con GLBL_TRAIN_DIR:
    # # Creo el parametro MAIN_MDLS_DIR, que no esta en el fichero de configuracion y que depende del entorno
    # paramConfigAdicionalesMAIN['MAIN_MDLS_DIR'] = [MAIN_MDLS_DIR, 'str', '', 'GrupoDirsFiles', MAIN_MDLS_DIR]
    GLOBALconfigDict = clidconfig.leerCambiarVariablesGlobales(
        LCL_idProceso=MAIN_idProceso,
        nuevosParametroConfiguracion=paramConfigAdicionalesMAIN,
        inspect_stack=inspect.stack(),
        verbose=False,
    )
    GLO.MAINrutaRaizHome = MAINrutaRaizHome
    GLO.MAINrutaRaizData = MAINrutaRaizData
# ==============================================================================

# ==============================================================================
if CONFIGverbose:
    # configFileNameCfg se establece como parametro de configuracion y se guarda en el .cfg
    # en clidconfig.initConfigDicts<>, que se ejecuta al importar clidconfig desde clidbase.py 
    print(f'{TB}-> configFileNameCfg:       {GLO.configFileNameCfg}')
    print(f'{"":=^80}')
# ==============================================================================
if CONFIGverbose:
    print(f'clidaux-> C ok. GLO.GLBLverbose: {GLO.GLBLverbose}; CONFIGverbose: {CONFIGverbose}; __verbose__: {__verbose__}')
    print(f'clidaux-> C ok. GLO.MAINrutaOutput: {GLO.MAINrutaOutput}')
# ==============================================================================

# ==============================================================================
print(f'\n{"":_^80}')
print(f'clidaux-> Al importar clidaux se asignan las variables globales con directorios MAIN_...')
print(f'{TB}como propiedades de GLO y se guardan en el fichero de configuracion cfg.')
print(f'{TB}-> Este modulo:      {__name__}')
print(f'{TB}-> Importado desde:  {callingModulePrevio}')
print(f'{TB}-> Modulo inicial:   {callingModuleInicial}')
print(f'{TB}-> =============')
print(f'{TB}-> MAIN_FILE_DIR:    {MAIN_FILE_DIR}')
print(f'{TB}-> MAIN_BASE_DIR:    {MAIN_BASE_DIR}')
print(f'{TB}-> MAIN_PROJ_DIR:    {MAIN_PROJ_DIR}')
print(f'{TB}-> MAIN_RAIZ_DIR:    {MAIN_RAIZ_DIR}')
print(f'{TB}-> =============')
print(f'{TB}-> MAINrutaRaizHome: {MAINrutaRaizHome}')
print(f'{TB}-> MAINrutaRaizData: {MAINrutaRaizData}')
print(f'{TB}-> =============')
print(f'{TB}-> MAIN_THIS_DIR:    {MAIN_THIS_DIR}')
print(f'{TB}-> MAIN_WORK_DIR:    {MAIN_WORK_DIR}')
print(f'{TB}-> MAIN_HOME_DIR:    {MAIN_HOME_DIR}')
# print(f'{TB}-> =============')
# Esto se asigna en clidconfig.py, junto con GLBL_TRAIN_DIR:
# print(f'{TB}-> MAIN_MDLS_DIR:  {MAIN_MDLS_DIR}')
# print(f'{TB}-> =============')
print(f'{"":=^80}')
# ==============================================================================

# ==============================================================================
if callingModuleInicial == 'clidflow':
    printMsgToFile = False
else:
    printMsgToFile = True
contadorErroresEscrituraControlFileLas = 0
# ==============================================================================
def printMsg(mensaje='', outputFileLas=True, verbose=True, newLine=True, end=None):
    global contadorErroresEscrituraControlFileLas
    if printMsgToFile and outputFileLas:
        try:
            if 'controlFileLasObj' in dir(GLO) and GLO.controlFileLasObj:
                try:
                    if not end is None:
                        GLO.controlFileLasObj.write(str(mensaje) + end + '\n' if newLine else ' ')
                    else:
                        GLO.controlFileLasObj.write(str(mensaje) + '\n' if newLine else ' ')
                except:
                    try:
                        controlFileGralObj = open(GLO.GLBLficheroDeControlGral, mode='a+')
                        controlFileGralObj.write(f'\nError (1) escribiendo en {GLO.controlFileLasObj}')
                        controlFileGralObj.write(f'\nMensaje no escrito:\n')
                        controlFileGralObj.write(str(mensaje))
                        controlFileGralObj.close()
                    except:
                        contadorErroresEscrituraControlFileLas += 1
                        if contadorErroresEscrituraControlFileLas < 10:
                            print(f'clidaux-> printLog: no hay acceso a controlFileLasObj ni controlFileGralObj.')
                        else:
                            mensaje = f'!!! {mensaje}'
            elif 'GLBLficheroDeControlGral' in dir(GLO) and GLO.GLBLficheroDeControlGral:
                controlFileGralObj = open(GLO.GLBLficheroDeControlGral, mode='a+')
                controlFileGralObj.write(f'\nNo hay acceso a controlFileLasObj: {GLO.controlFileLasObj}\n')
                controlFileGralObj.write(str(mensaje))
                controlFileGralObj.close()
        except:
            contadorErroresEscrituraControlFileLas += 1
            if contadorErroresEscrituraControlFileLas < 5:
                print(f'clidaux-> printLog: no hay acceso a controlFileLasObj o controlFileGralObj.')
                if 'controlFileLasName' in dir(GLO):
                    print(f'{TB}-> controlFileLasName:   {GLO.controlFileLasName}')
                if 'GLBLficheroDeControlGral' in dir(GLO):
                    print(f'{TB}-> ficheroDeControlGral: {GLO.GLBLficheroDeControlGral}')
            mensaje = f'### {mensaje}'
    if verbose:
        if not end is None:
            print(mensaje, end=end)
        elif not newLine:
            end=''
            print(mensaje, end=end)
        else:
            print(mensaje)

# ==============================================================================
# #Puedo usar esta funcion para mensajes individuales y globales
# def mostrarMensaje(mensaje, outputFileLas=True, verbose=True, newLine=True):
#     if verbose:
#         if newLine:
#             print( mensaje )
#         else:
#             print( mensaje, )
#     if outputFileLas and GLO.controlFileLasObj:
#         try:
#             GLO.controlFileLasObj.write(str(mensaje) + '\n' if newLine else ' ')
#         except:
#             if GLO.controlFileGralObj:
#                 GLO.controlFileGralObj.write('Error writing control file (1).\n')
#     else:
#         try:
#             GLO.controlFileGralObj.write(str(mensaje) + '\n' if newLine else ' ')
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
def mostrarTiempoConsumido(
        tiempo0=time.time(),
        tiempo1=time.time(),
        mensaje='tarea indefinida',
        modulo='cartolidar',
        fileCoordYear=''
    ):
    segundosDuracion = round(tiempo1 - tiempo0, 1)
    minutosDuracion = round(segundosDuracion / 60.0, 1)
    printMsg(
        f'clidaux-> {modulo}.{fileCoordYear}-> Tiempo para [{mensaje}]: '
        f'{segundosDuracion:0.1f} segundos ({minutosDuracion:0.1f} minutos)'
    )

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
                '%sclidaux-> Total RAM: %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb'
                % (sangrado, ramMem.total / 1e9, ramMem.used / 1e9, ramMem.available / 1e9)
            )
        else:
            print(
                '%sclidaux-> Total RAM (%s): %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb'
                % (sangrado, str(marcador), ramMem.total / 1e9, ramMem.used / 1e9, ramMem.available / 1e9)
            )
    if swap:
        swapMem = psutil.swap_memory()
        if verbose:
            print('clidaux-> Total SWAP memory: %0.2f Gb; usada: %0.2f Gb; disponible: %0.2f Gb' % (swapMem.total / 1e9, swapMem.used / 1e9, swapMem.free / 1e9))
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
def mostrar_directorios():
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

        if nombrePropiedad == 'pointsAllFromFile_xtypePFXX':
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
    GLO.controlFileGralObj.write(elMensaje)
    printMsg(elMensaje)
    if contador > totalPoints * 0.5:
        elMensaje = 'Puntos leidos:\t\t%i (<1/2). Continuo con los puntos ya procesados en primera vuelta.' % (contador)
        GLO.controlFileGralObj.write(elMensaje)
        printMsg(elMensaje)
    else:
        elMensaje = 'Puntos leidos:\t\t%i (<1/2). Interrumpo el procesado y reintento con distinta configuracion.\n' % (contador)
        GLO.controlFileGralObj.write(elMensaje)
        printMsg(elMensaje)
    printMsg(
        'Desactivar la opcion de cargar todos los puntos en array. Si tb falla: Lectura de registros individuales (en vez de leer el fichero completo cargandolo entero en la RAM).\n'
    )
    mostrarMemoriaOcupada(miLasClass)


# ==============================================================================o
def coordenadasDeBloque(miHead, metrosBloque, metrosCelda):
    xmin = miHead['xminBloqueMalla']
    ymin = miHead['yminBloqueMalla']
    xmax = miHead['xmaxBloqueMalla']
    ymax = miHead['ymaxBloqueMalla']
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
def chequearHuso29(fileCoordYear):
    # Lo mejor es dejar GLO.MAINhuso == 0 y asigno el huso en funcion de las coordenadas
    # Mantengo el huso 30 en el caso de que incluya _H29_ en GLO.MAINprocedimiento
    #  Esto solo lo hago cuando tengo los lasFiles en una carpeta especial (por ejemplo IRC_H29 en vez de IRC)
    # En coordenadas de H30, la recta que separa el uso 29 del 30 es: Y = 28.71*X - 2569980; X = 0.034831 * Y + 89515
    #   Usando coordenadas H30: Si X > 0,034831 * Y + 89515 -> H30
    # En coordenadas de H29, la recta que separa el uso 29 del 30 es: Y = -28.6153*X + 26069477.35; X = -0.03494637 * Y + 911033
    #   Usando coordenadas H29: Si X > 0,034831 * Y + 89515 -> H30
    # Si esta en CyL y la coordenada X es superior a 610000, esta expresada en H29

    if fileCoordYear[:8] == '000_0000':
        if GLO.MAINhuso == 29:
            TRNShuso29_coord, TRNShuso29_ubica = True, True
        else:
            TRNShuso29_coord, TRNShuso29_ubica = False, False
    else:
        if GLO.MAINhuso == 29 or (GLO.MAINhuso == 0 and int(fileCoordYear[:3]) >= 610): # or '_H29_' in GLO.MAINprocedimiento:
            TRNShuso29_coord = True
            if int(fileCoordYear[:3]) * 1000 > -0.03494637 * (int(fileCoordYear[4:8]) * 1000) + 911033:
                TRNShuso29_ubica = True
            else:
                TRNShuso29_ubica = False
        else:
            TRNShuso29_coord = False
            # Si la coordenada esta referida a H30 y X es inferior a 0,034831 * Y + 89515 -> En realidad es H29
            if int(fileCoordYear[:3]) * 1000 < 0.034831 * (int(fileCoordYear[4:8]) * 1000) + 89515:
                TRNShuso29_ubica = True
            else:
                TRNShuso29_ubica = False
    return TRNShuso29_coord, TRNShuso29_ubica


# ==============================================================================
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

    if not os.path.exists(infileConRuta):
        printMsg(f'{TB}-> clidaux-> Fichero no disponible para comprimir: {infileConRuta}')
        return False

    infile = os.path.basename(infileConRuta)
    rutaLazCompleta = os.path.dirname(infileConRuta)
    if 'RGBI' in rutaLazCompleta:
        rutaLazCompleta = rutaLazCompleta.replace('RGBI', 'RGBI_laz')
    elif 'RGB' in rutaLazCompleta:
        rutaLazCompleta = rutaLazCompleta.replace('RGB', 'RGB_laz')
    else:
        rutaLazCompleta = f'{rutaLazCompleta}_laz'
    if not os.path.isdir(rutaLazCompleta):
        try:
            os.makedirs(rutaLazCompleta)
        except:
            print(f'{TB}-> clidaux-> AVISO: no se ha podido crear la ruta: {rutaLazCompleta} -> No se genera lazFile.')
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
            print(f'{TB}-> clidaux-> AVISO: no se ha encontrado un binario para comprimir (no se genera lazFile).')
            return False

        outfileLaz = (infile.replace('.las', '.laz')).replace('.LAS', '.laz')
        outfileLazConRuta = os.path.join(rutaLazCompleta, outfileLaz)
        # print('\t-> Compresor: {}'.format(laszip_binary))
        # print('\t-> infileConRuta:', infileConRuta)
        # print('\t-> outfileLazConRuta:', outfileLazConRuta)
        # print('\t\t%s -i %s -o %s' % (laszip_binary, infileConRuta, outfileLasConRuta))
    if os.path.exists(outfileLazConRuta) and not sobreEscribirOutFile:
        print(f'{TB}-> clidaux-> No se genera el fichero comprimido porque sobreEscribirOutFile={sobreEscribirOutFile} y ya existe: {outfileLazConRuta}')
        return False

    if LCLverbose or True:
        print(f'{TB}-> clidaux-> Se comprime:  {infileConRuta}')
        print(f'{TB}-> {TB}Para generar: {outfileLazConRuta}')
        print(f'{TB}-> {TB}-> Compresor:', laszip_binary)
    subprocess.call([laszip_binary, '-i', infileConRuta, '-o', outfileLazConRuta])

    if os.path.exists(outfileLazConRuta) and os.path.exists(infileConRuta):
        # eliminarLasFile = True
        try:
            outfileLazSizeKB = os.stat(outfileLazConRuta).st_size / 1000
            infileLasSizeKB = os.stat(infileConRuta).st_size / 1000
            if outfileLazSizeKB < infileLasSizeKB / 100: # size en KB
                print(f'{TB}-> clidaux-> AVISO: el laz generado ocupa menos de lo esperado:   {outfileLazSizeKB:10.1f} KB -> {outfileLazConRuta}')
                print(f'{TB}{TV} en comparacion con el las que se quiere comprimir:           {infileLasSizeKB:10.1f} KB -> {infileConRuta}')
                print(f'{TB}-> No se elimina el fichero sin comprimir: {infileConRuta}')
                eliminarLasFile = False
        except:
            print(f'{TB}-> clidaux-> Aviso: No se ha podido calcular cuantos bytes tienen los ficheros {infileConRuta} y {outfileLazConRuta}')
        if eliminarLasFile and os.path.exists(infileConRuta):
            print(f'{TB}{TV}-> Eliminando el fichero las despues de comprimir a laz: {infileConRuta}')
            try:
                os.remove(infileConRuta)
            except:
                print(f'{TB}-> clidaux-> Aviso: revisar si el fichero {infileConRuta} esta bloqueado por otra aplicacion (error al intentar borrarlo)')
    else:
        print(f'{TB}-> clidaux-> AVISO: no se ha podido generar el laz:  {outfileLazConRuta}')
        print(f'{TB}{TV}-> No se elimina el fichero sin comprimir: {infileConRuta}')

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

