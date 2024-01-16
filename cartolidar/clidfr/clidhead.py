#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Module included in cartolidar project (clidtfr package)
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidhead includes a class (LasHeadClass) for reading the header of lidar files (LAS format)

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''
# from __future__ import division, print_function
# from __future__ import unicode_literals

import os
import sys
import pathlib
import time
import datetime
# import types
# import csv
import re
import math
# import random
# import platform
import inspect
# import traceback
# import subprocess
# import argparse
from configparser import RawConfigParser
import logging
import importlib
import importlib.util
import struct
# import shutil
# import gc

# Paquetes de terceros
import numpy as np
import psutil
from _ast import If


# ==============================================================================
if '--cargadoClidhead' in sys.argv:
    moduloPreviamenteCargado = True
    print(f'\nclidhead->1> moduloPreviamenteCargado: {moduloPreviamenteCargado}; sys.argv: {sys.argv}')
else:
    moduloPreviamenteCargado = False
    print(f'\nclidhead->1> moduloPreviamenteCargado: {moduloPreviamenteCargado}; sys.argv: {sys.argv}')
    sys.argv.append('--cargadoClidhead')
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
        print(f'clidhead-> ATENCION: revisar asignacion de idProceso.')
        print(f'ARGS_idProceso: {type(ARGS_idProceso)} {ARGS_idProceso}')
        print(f'sys.argv: {sys.argv}')
else:
    MAIN_idProceso = 0
    print(f'clidconfig-> ATENCION: revisar codigo de idProceso.')
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
TB = ' ' * 11
TV = ' ' * 3
TW = ' ' * 2
# ==============================================================================
 
# ==============================================================================
# ============================== Variables MAIN ================================
# ==============================================================================
# Directorios de la aplicacion:
# Dir del modulo que se esta ejecutando (clidhead.py):
MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))  # En calendula /LUSTRE/HOME/jcyl_spi_1/jcyl_spi_1_1/cartolidar/cartolidar/clidax
# Dir de clidbase.py:
MAIN_BASE_DIR = os.path.join(MAIN_FILE_DIR, '..')
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
# Duplico esta funcion de clidaux para no importar clidaux
def infoUsuario(verbose=False):
    try:
        esteUsuario = psutil.users()[0].name
        if verbose:
            print('clidconfig-> Usuario:', esteUsuario)
    except:
        esteUsuario = psutil.users()
        if verbose:
            print('clidconfig-> Users:', esteUsuario)
    if not isinstance(esteUsuario, str) or esteUsuario == '':
        esteUsuario = 'local'
    return esteUsuario


# ==============================================================================
# Duplico esta funcion de clidaux para no importar clidaux
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
            print(f'{TB}clidhead-> Error identificando el modulo 1')
            return 'desconocido1', 'desconocido1'
    else:
        if verbose:
            print(f'{TB}clidhead-> No hay modulos que identificar')
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
        print(f'{TB}clidhead-> El modulo {esteModuloName} ({esteModuloNum}) ha sido', end=' ')
    for llamada in inspect_stack[stackSiguiente:]:
        if 'cartolid' in llamada[1] or 'clid' in llamada[1] or 'qlid' in llamada[1]:
            callingModule = inspect.getmodulename(llamada[1])
            if callingModule != esteModuloName and callingModulePrevio == '':
                callingModulePrevio = callingModule
            callingModuleInicial = callingModule
            # if callingModule != 'clidaux' and callingModule != 'callingModule':
                # print('clidhead-> llamado por', llamada[1:3], end=' ')
            if verbose:
                print(f'importado desde: {callingModule} ({llamada[2]})', end='; ')
    if verbose:
        print('')
    return callingModulePrevio, callingModuleInicial


# ==============================================================================
def iniciaConsLog(myModule='clidhead', myVerbose=False, myQuiet=False):
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
    print(f'\nclidhead-> AVISO: CONFIGverbose True; __verbose__: {__verbose__}')
# ==============================================================================
if CONFIGverbose:
    print(f'\nclidhead-> Cargando clidhead...')
    print(f'{TB}-> Directorio desde el que se lanza la aplicacion-> os.getcwd(): {os.getcwd()}')
    print(f'{TB}-> Revisando la pila de llamadas...')
callingModulePrevio, callingModuleInicial = showCallingModules(inspect_stack=inspect.stack(), verbose=False)
if CONFIGverbose:
    print(f'{TB}{TV}-> callingModulePrevio:  {callingModulePrevio}')
    print(f'{TB}{TV}-> callingModuleInicial: {callingModuleInicial}')
# ==============================================================================

# ==============================================================================
myUser = infoUsuario()
myModule = __name__.split('.')[-1]
# ==============================================================================
if not moduloPreviamenteCargado or True:
    print('\nclidconfig-> AVISO: creando myLog (ConsLog)')
    myLog = iniciaConsLog(myModule=myModule, myVerbose=__verbose__)
# ==============================================================================
if CONFIGverbose:
    myLog.debug(f'{"":_^80}')
    myLog.debug(f'clidhead-> Debug & alpha version info:')
    myLog.debug(f'{TB}-> ENTORNO:          {MAIN_ENTORNO}')
    myLog.debug(f'{TB}-> Modulo principal: <{sys.argv[0]}>') # = __file__
    myLog.debug(f'{TB}-> __package__ :     <{__package__ }>')
    myLog.debug(f'{TB}-> __name__:         <{__name__}>')
    myLog.debug(f'{TB}-> __verbose__:      <{__verbose__}>')
    myLog.debug(f'{TB}-> IdProceso         <{MAIN_idProceso}>')
        # myLog.debug(f'{TB}-> configFile:       <{GLO.configFileNameCfg}>')
    myLog.debug(f'{TB}-> sys.argv:         <{sys.argv}>')
    myLog.debug(f'{"":=^80}')
# ==============================================================================

print(f'clidhead-> callingModuleInicial: {callingModuleInicial}')
# ==============================================================================
if callingModuleInicial == 'clidclas': #  or callingModuleInicial == 'clidtools'
    # No se usa el fichero de configuracion clidbase.slx cuando el modulo inicial es:
    #   clidtools: modulos auxiliares de cartolidar, que pueden ejecutarse de forma autonoma
    #   clidclas: modulo para lanzar el entrenamiento de forma autonoma
    class Object(object):
        pass
    GLO = Object()
    GLO.GLBLverbose = False
    GLO.GLBLcoordMinMaxAcordesConBloque = True
    GLO.MAIN_copyright = 'Bengoa 2016-22'
    GLO.MAINrutaDataExt = '../data/ext'
    GLO.GLBLforzarExtensionDeBloqueAvalorNominal = False
    GLO.GLBLadapatarMetrosBloque = False
    GLO.GLBLincluirYearEnFileCoordYear = True
    # GLO.GLBLincluirYearEnControlFile = False
    GLO.GLBLnumeroMaximoDeRetornosPorPulso = 15
    GLO.MAINprocedimiento = ''
else:
    spec = importlib.util.find_spec('cartolidar')
    if spec is None or MAIN_ENTORNO == 'calendula':
        if True:
        # try:
            if CONFIGverbose:
                sys.stdout.write(f'\nclidhead-> Intento alternativo de importar clidconfig desde la version local {os.getcwd()}/clidax\n')
            from clidax import clidconfig
            if CONFIGverbose:
                sys.stdout.write(f'\nclidhead-> Ok clidconfig importado del clidax local (2)')
        from clidnb import clidnaux
    else:
        if CONFIGverbose:
            sys.stdout.write('\nclidhead-> Importando clidconfig desde cartolidar.clidax\n')
        from cartolidar.clidax import clidconfig
        if CONFIGverbose:
            sys.stdout.write(f'\nclidhead-> Ok clidconfig importado de cartolidar.clidax (1)')
        from cartolidar.clidnb import clidnaux
    configVarsDict = clidconfig.leerCambiarVariablesGlobales(
        LCL_idProceso=MAIN_idProceso
    )
    GLO = clidconfig.GLO_CLASS(configVarsDict)

GLO.MAIN_idProceso = MAIN_idProceso

if not hasattr(GLO, 'MAIN_ENTORNO'):
    MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    MAIN_DRIVE = os.path.splitdrive(MAIN_FILE_DIR)[0]  # 'D:' o 'C:'
    if MAIN_FILE_DIR[:12] == '/LUSTRE/HOME':
        GLO.MAIN_ENTORNO = 'calendula'
    elif MAIN_FILE_DIR[:8] == '/content':
        GLO.MAIN_ENTORNO = 'colab'
    else:
        GLO.MAIN_ENTORNO = 'windows'
if not hasattr(GLO, 'GLBLordenColoresInput'):
    GLO.GLBLordenColoresInput = ''
if not hasattr(GLO, 'GLBLcorregirGPStimeBit'):
    GLO.GLBLcorregirGPStimeBit = True
if not hasattr(GLO, 'GLBLalmacenarPuntosComoCompactNpDtype'):
    GLO.GLBLalmacenarPuntosComoCompactNpDtype = True
if not hasattr(GLO, 'GLBLmargenParaAdmitirPuntosFueraDeBloque'):
    GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque = 0.5
if not hasattr(GLO, 'GLBLmetrosBloque'):
    GLO.GLBLmetrosBloque = 2000
if not hasattr(GLO, 'GLBLmetrosCelda'):
    GLO.GLBLmetrosCelda = 10
if not hasattr(GLO, 'GLBLmetrosSubCelda'):
    GLO.GLBLmetrosSubCelda = 2
# ==============================================================================


# ==============================================================================o
def printMsg(mensaje, outputFileLas=True, verbose=True, newLine=True, end=None):
    if verbose:
        if not end is None:
            print(mensaje, end=end)
        elif not newLine:
            end=''
            print(mensaje, end=end)
        else:
            end=''
            print(mensaje)


# Funcion copiada de clidaux.py, pera no tener que importar ese modulo
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


# Funcion copiada de clidaux.py, pera no tener que importar ese modulo
# ==============================================================================o
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


# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
class LasHeadClass(object):
    """
    Clase/objeto con las propiedades de la cabecera del lasFile
    y con metodos para escribir una nueva cabecera
    """

    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def __init__(
            self,
            infileConRuta,
            lasDataMem=None,
            metersBlock=GLO.GLBLmetrosBloque,
            metersCell=GLO.GLBLmetrosSubCelda,
            LCLordenColoresInput=None,
            TRNShuso29=False,
            TRNShuso29_coord=False,
            TRNShuso29_ubica=False,
            coordenadasTransformadasDe29a30=False,
            fileCoordYearDelNombre='',
            controlFileLasNameConRuta='',
            verbose=False,
            checkLas=False,
            LCLforzarExtensionDeBloqueAvalorNominal=GLO.GLBLforzarExtensionDeBloqueAvalorNominal,
        ):
        """
        Clase/objeto con las propiedades de la cabecera del lasFile
        Argumentos obligatrios de clase: infileConRuta
        Argumentos opcionales: metersBlock=0, metersCell=10, verbose=False
            metersBlock only for checking coherence with lasFile head info
            metersCell for adjust corner coordinates to multiple of metersCell
                if metersCell=0 -> no adjust
        Propiedades que se asignan al instanciar la clase:
            headDict
            infileConRuta metersBlock metersCell  verbose
            lasVersion  pointformat nBytesPorPunto  numptrecords
            fileCoordYearDelNombre   xSupIzdaDelNombre   ySupIzdaDelNombre   fileYear
            xmin    xmax    ymin    ymax
            xSupIzda    ySupIzda    xInfDcha    yInfDcha
            xmin        xmax        ymin        ymax
            lasPointFieldPropertiesList lasPointFieldPropertiesDict lasPointFieldOrdenDict
            npArrayPropPto  bytearrayPropPtoNombre  arrayPropPtoNombre
            arrayPropPtoRangoBytes  arrayPropPtoTipoDato
        La lista de campos de la cabecera de un LasFile se leen de cartolidar/data/ext/io/lasHeadFields.cfg
        La lista de propiedades de cada punto de un LasFile se leen de cartolidar/data/ext/io/lasPointFields.cfg
        """

        # ======================================================================
        if not os.path.exists(infileConRuta):
            self.readOk = False
            print(f'clidhead-> Atencion: no se encuentra el fichero {infileConRuta}')
            return
        self.readOk = True
        self.infileConRuta = infileConRuta
        self.lasDataMem = lasDataMem
        self.controlFileLasNameConRuta = controlFileLasNameConRuta
        self.metersBlock = metersBlock
        self.metersCell = metersCell
        self.verbose = verbose
        # Transitorio hasta que elimine el TRNShuso29
        if TRNShuso29_coord:
            self.TRNShuso29 = TRNShuso29_coord
        else:
            self.TRNShuso29 = TRNShuso29
        self.TRNShuso29_coord = TRNShuso29_coord
        self.TRNShuso29_ubica = TRNShuso29_ubica
        self.coordenadasTransformadasDe29a30 = coordenadasTransformadasDe29a30
        # En realidad creo que no uso esta variable como propiedad de esta clase
        self.fileCoordYeahDelNombre = fileCoordYearDelNombre
        if LCLordenColoresInput is None:
            if 'rgbi' in infileConRuta.lower():
                self.LCLordenColoresInput = 'RGBI'
            elif 'rgb' in infileConRuta.lower():
                self.LCLordenColoresInput = 'RGB'
            elif 'irc' in infileConRuta.lower() or 'irg' in infileConRuta.lower():
                self.LCLordenColoresInput = 'IRG'
            else:
                self.LCLordenColoresInput = GLO.GLBLordenColoresInput
        else:
            self.LCLordenColoresInput = LCLordenColoresInput

        self.LCLforzarExtensionDeBloqueAvalorNominal = LCLforzarExtensionDeBloqueAvalorNominal
        # En principio la extension indica si esta comprimido.
        # De todas formas se puede verificar leyendo la cabecera, que no requiere descomprimir porque no esta comprimida.
        if self.verbose:
            printMsg(f'\n{"":_^80}')
        if not self.lasDataMem is None:
            self.lazfile = False
            if self.verbose:
                print('clidhead-> LasHeadClass-> Leyendo cabecera de fichero en memoria (lasDataMem).')
        else:
            if infileConRuta[-4:].lower() == '.laz':
                self.lazfile = True
                if self.verbose:
                    print('clidhead-> LasHeadClass-> Leyendo cabecera de fichero laz comprimido (sin descomprimir por el momento).')
            else:
                self.lazfile = False
                if self.verbose:
                    print('clidhead-> LasHeadClass-> Leyendo cabecera de fichero las sin comprimir (o ya descomprimido en fichero).')
        # ======================================================================

        # ======================================================================
        # Showing lasFile head fields of all versions in cartolidar/data/ext/io/lasHeadFields.cfg
        # Showing las point formats in cartolidar/data/ext/io/lasPointFields.cfg
        if False:
            self.showAlllasFileVersions()
            self.showAllPointFormats()
        # ======================================================================

        # ======================================================================
        # ======================================================================
        # Reading head of las file:
        #    Create self.headDict[]
        self.readLasHead()
        if not self.readOk:
            return
        self.readVariableLengthRecords(tipoVLR='normal')
        if self.lasVersion == 'LasFormat_1_4':
            self.readVariableLengthRecords(tipoVLR='extended')
        # ======================================================================
        # ======================================================================
        self.projection_type = self.headDict['projection_type']
        self.projection_value = self.headDict['projection_value']
        self.VLRhuso = self.headDict['VLRhuso']
        self.OGCprojectionVLR = self.headDict['OGCprojectionVLR']
        self.GeoKeyDirectoryTagVLR = self.headDict['GeoKeyDirectoryTagVLR']
        self.GeoDoubleParamsTagVLR = self.headDict['GeoDoubleParamsTagVLR']
        # ======================================================================

        if self.lasDataMem is None:
            # print('------------------------clidhead--------------> self.lasDataMem is None')
            self.ficheroLas.close()

        self.pointformat = self.headDict['pointformat']
        self.pointformatOriginal = self.headDict['pointformat']
        self.pointformatNuevo = self.headDict['pointformat']
        # ======================================================================
        print(f'\nclidhead-> Se va a calcular extraBytesPorRegistro para pointformat: {self.pointformat}')
        print(f'{TB}-> GLBLdarPrioridadAPointFormatFrenteAReclen: {GLO.GLBLdarPrioridadAPointFormatFrenteAReclen}')
        self.headDict['extraBytesPorRegistro'] = 0
        listaPointRecLens = [20, 28, 64, 34, 57, 63, 30, 36, 38, 59, 67]
        if self.headDict['pointformat'] < len(listaPointRecLens):
            pointRecLenTeorico = listaPointRecLens[self.headDict['pointformat']]
            if self.headDict['pointreclen'] != pointRecLenTeorico:
                print(f'clidhead-> ATENCION: la cabecera indica pointformat {self.headDict["pointformat"]} y pointreclen {self.headDict["pointreclen"]}')
                print(f'{TB}-> A ese pointformat le corresponde un pointreclen de {pointRecLenTeorico}')
                if (
                    GLO.GLBLdarPrioridadAPointFormatFrenteAReclen
                    or not self.headDict['pointreclen'] in listaPointRecLens
                ):
                    if self.headDict['pointreclen'] > pointRecLenTeorico:
                        self.headDict['extraBytesPorRegistro'] = self.headDict['pointreclen'] - pointRecLenTeorico
                    else:
                        print(f'{TB}-> Se da credibilidad a pointreclen pero no hay ningun pointformat con ese pointreclen')
                        print(f'{TB}-> No se cambia pointformat, por lo que es previsible que la lectura del lasFile sea erronea')
                else:
                    pointRecLenPrevisible = listaPointRecLens.index(self.headDict['pointreclen'])
                    self.pointformatNuevo = pointRecLenPrevisible
                    print(f'{TB}-> Se da credibilidad a pointreclen e interpreta como error de pointformat, que puede ser {pointRecLenPrevisible}.')
                    print(f'{TB}-> Se cambia a este valor')
        else:
            print(f'clidhead-> ATENCION: la cabecera indica pointformat {self.headDict["pointformat"]} pero ese valor no esta implementado en cartolidar')
            print(f'{TB}-> Se pasa al siguiente fichero')
            self.readOk = False
            return
        self.headDict['pointformat'] = self.pointformatNuevo
        self.pointformat = self.headDict['pointformat']
        self.extraBytesPorRegistro = self.headDict['extraBytesPorRegistro']
        print(f'{TB}-> extraBytesPorRegistro: {self.extraBytesPorRegistro}')

        # if self.headDict['pointformat'] == 1 and self.headDict['pointreclen'] == 34:
        #     print(f'clidhead-> ATENCION: la cabecera indica pointformat 1 y pointreclen 34')
        #     print(f'{TB}-> Se da credibilidad a pointreclen e interpreta como error de pointformat, que puede ser 3. Se cambia a este valor')
        #     self.headDict['pointformat'] = 3
        # elif self.headDict['pointformat'] == 1 and self.headDict['pointreclen'] == 30:
        #     print(f'clidhead-> ATENCION: la cabecera indica pointformat 1 y pointreclen 30')
        #     print(f'{TB}-> Se da credibilidad a pointreclen e interpreta como error de pointformat, que puede ser 6. Se cambia a este valor')
        #     self.headDict['pointformat'] = 6
        # elif self.headDict['pointformat'] == 1 and self.headDict['pointreclen'] != 28:
        #     print(f'clidhead-> ATENCION: la cabecera indica pointformat {self.headDict["pointformat"]} y pointreclen {self.headDict["pointreclen"]}')
        #     print(f'{TB}-> Se da credibilidad a pointreclen e interpreta como error de pointformat, que puede ser 6. Se cambia a este valor')
        # ======================================================================


        if self.verbose and self.sumaBytesCabecera != self.headDict['offset']:
            printMsg(
                'clidhead.{:006}-> El numero de bytes calculado tras leer la cabecera ({}) y los VLRs ({}) es {}'.format(
                    GLO.MAIN_idProceso, self.headDict['headersize'], self.sumaBytesVLR, self.sumaBytesCabecera)
            )
            printMsg(
                '\tNo coincide con el offset que figura en la cabecera del LASF ({})'.format(
                self.headDict['offset'])
            )
            printMsg(
                '\tEso significa que hay bytes extras al final de la cabecera, antes del inicio de los puntos.'
            )
            printMsg(
                '\tNumero de Bytes extra: %i'
                % (self.headDict['offset'] - self.sumaBytesCabecera)
            )
            printMsg(
                '\tNota: el fichero tiene %i VLRs' % self.headDict['numvlrecords']
            )
        if self.sumaBytesCabecera != len(self.headBin):
            printMsg(
                'clidhead.%06i-> ATENCION: ha habido un error de lectura porque no se han leido todos los bytes de la cabecera (%i)'
                % (GLO.MAIN_idProceso, self.sumaBytesCabecera)
            )

        crearFicheroConSoloLaCabecera = False
        if crearFicheroConSoloLaCabecera and not infileConRuta is None:
            outFileLasConRuta = self.infileConRuta.replace('.las', '_Cabecera.las')
            print('\nclidhead-> LasHeadClass-> nCreando copia del LASF con solo cabecera (sin puntos): %s' % outFileLasConRuta)
            print('clidhead-> LasHeadClass-> Escribiendo cabecera original de prueba en', outFileLasConRuta, 'con', len(self.headBin), 'bytes')
            print('clidhead-> LasHeadClass-> self.headBin', self.headBin)
            self.newLax = open(outFileLasConRuta, mode='wb')
            self.newLax.write(self.headBin)

        # Tengo dos formas de acceder a las propiedades del LASF head:
        #    Como atributos de este objeto
        #    Como valores del dict self.headDict[propiedad]
        # Ver lista de propiedades en cartolidar/data/ext/io/lasHeadFields.cfg

        # La propiedad globalencoding tiene info del tipo de hora/fecha y, si LASF = 1.4 tb del srs y otras cosas que no uso
        self.headDict['GPSTimeType'] = (self.headDict['globalencoding']) & 1
        if GLO.GLBLcorregirGPStimeBit and self.headDict['GPSTimeType'] == 0:
            self.headDict['GPSTimeType'] = 1
        self.GPSTimeType = self.headDict['GPSTimeType']

        if self.lasVersion == 'LasFormat_1_2':
            # las format 1.2 solo admite CRS en forma GeoTiff.
            # Este las format requiere obligatoriamente un Variable Length Record, GeoKeyDirectoryTag).
            WKT = 0
            self.formatoSRS = 'GeoTIFF'
            self.returnNumbersSyntheticallyGenerated = 0
            self.waveformDataPacketsExternal = 0
            self.waveformDataPacketsInternal = 0
        elif self.lasVersion == 'LasFormat_1_3':
            # las format 1.3 solo admite CRS en forma GeoTiff.
            print('\nclidhead-> LasHeadClass-> Version de LASF (1.3) implementada solo parcialmente')
            WKT = 0
            self.formatoSRS = 'GeoTIFF'
            self.returnNumbersSyntheticallyGenerated = (self.headDict['globalencoding'] >> 3) & 1
            self.waveformDataPacketsExternal = (self.headDict['globalencoding'] >> 2) & 1
            self.waveformDataPacketsInternal = (self.headDict['globalencoding'] >> 1) & 1
        elif self.lasVersion == 'LasFormat_1_4':
            WKT = (self.headDict['globalencoding'] >> 4) & 1
            # Ver WKT en https://www.opengeospatial.org/standards/ct
            if self.headDict['pointformat'] < 6:
                if WKT:
                    self.formatoSRS = 'WKT'
                else:
                    self.formatoSRS = 'GeoTIFF'
            else:
                if WKT:
                    self.formatoSRS = 'WKT'
                else:
                    # Point Record Formats 6-10 must use WKT.
                    self.formatoSRS = 'Error'
            self.returnNumbersSyntheticallyGenerated = (self.headDict['globalencoding'] >> 3) & 1
            self.waveformDataPacketsExternal = (self.headDict['globalencoding'] >> 2) & 1
            self.waveformDataPacketsInternal = (self.headDict['globalencoding'] >> 1) & 1
        else:
            print('\nclidhead-> LasHeadClass-> Version de LASF (%s) no implementada' % self.lasVersion)
            quit()
        self.headDict['formatoSRS'] = self.formatoSRS
        self.headDict['returnNumbersSyntheticallyGenerated'] = self.returnNumbersSyntheticallyGenerated
        self.headDict['waveformDataPacketsExternal'] = self.waveformDataPacketsExternal
        self.headDict['waveformDataPacketsInternal'] = self.waveformDataPacketsInternal

        # ======================================================================
        # Variantes ortograficas a extinguir
        self.nBytesPorPunto = self.headDict['pointreclen']
        self.pointreclen = self.headDict['pointreclen']

        self.fileYear = self.headDict['fileyear']

        # Coordenadas de la esquina superior izquierda deducidas del nombre del fichero (and year)
        (
            self.fileCoordYeahDelNombre,
            self.xSupIzdaDelNombre,
            self.ySupIzdaDelNombre,
            self.fileYearDelNombre
        ) = getFileCoordFromName(
            self.infileConRuta
        )
        # No utilizo el valor self.fileCoordYeahDelNombre como propiedad de esta clase
        # porque doy prioridad al valor obtenido en clidbase.py que tiene en cuenta
        # el nombre y las coordenadas de la cabecera xSupIzda ySupIzda
        # Ademas en ese modulo se chequea la coherencia coordenadas de nombre y cabecera

        if GLO.GLBLforzarExtensionDeBloqueAvalorNominal and self.LCLforzarExtensionDeBloqueAvalorNominal:
            self.xminBloqueMalla = self.xSupIzdaDelNombre
            self.ymaxBloqueMalla = self.ySupIzdaDelNombre
            self.xmaxBloqueMalla = self.xminBloqueMalla + GLO.GLBLmetrosBloque
            self.yminBloqueMalla = self.ymaxBloqueMalla - GLO.GLBLmetrosBloque
            self.xminBloqueIni = self.xminBloqueMalla
            self.xmaxBloqueIni = self.xmaxBloqueMalla
            self.yminBloqueIni = self.yminBloqueMalla
            self.ymaxBloqueIni = self.ymaxBloqueMalla
        else:
            # Se asigna xmin, xmax, ymin, ymax a partir de headDict[]
            # Si los rangos xmax-xmin y ymax-ymin redondeados al metro
            # se corresponde con GLBLmetrosBloque, se aplica ese redondeo.
            # En caso conrtario se mantienen tal cual.
            # Los valores de headDict['xminBloqueMalla'], etc. no se tocan
            self.xminBloqueIni = self.headDict['xminBloqueMalla']
            self.xmaxBloqueIni = self.headDict['xmaxBloqueMalla']
            self.yminBloqueIni = self.headDict['yminBloqueMalla']
            self.ymaxBloqueIni = self.headDict['ymaxBloqueMalla']

            if (
                'LAS_INFO' in GLO.MAINprocedimiento
                or 'LAS_EDIT' in GLO.MAINprocedimiento
                or 'PASADAS' in GLO.MAINprocedimiento
            ):
                print(f'\nclidhead-> No se hace redondeo de coordenadas marco de bloque por estar ejecutando el procedimiento: {GLO.MAINprocedimiento}')
                self.xminBloqueMalla = self.headDict['xminBloqueMalla']
                self.xmaxBloqueMalla = self.headDict['xmaxBloqueMalla']
                self.yminBloqueMalla = self.headDict['yminBloqueMalla']
                self.ymaxBloqueMalla = self.headDict['ymaxBloqueMalla']
            else:
                self.calculaRedondeaCoordenadasBloqueDeLaCabecera()

        self.zminBloqueIni = self.headDict['zmin']
        self.zmaxBloqueIni = self.headDict['zmax']

        self.xSupIzda = self.xminBloqueMalla
        self.ySupIzda = self.ymaxBloqueMalla
        self.xInfDcha = self.xmaxBloqueMalla
        self.yInfDcha = self.yminBloqueMalla

        if self.verbose or __verbose__:
            if GLO.GLBLforzarExtensionDeBloqueAvalorNominal and self.LCLforzarExtensionDeBloqueAvalorNominal:
                printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> Coordenadas del lasfile segun fileName (GLBLforzarExtensionDeBloqueAvalorNominal es True):')
                printMsg(f'{TB}-> myLasName.xminBloqueMalla: {self.xminBloqueMalla}')
                printMsg(f'{TB}-> myLasName.xmaxBloqueMalla: {self.xmaxBloqueMalla}')
                printMsg(f'{TB}-> myLasName.yminBloqueMalla: {self.yminBloqueMalla}')
                printMsg(f'{TB}-> myLasName.ymaxBloqueMalla: {self.ymaxBloqueMalla}')
            else:
                printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> LasHeadClass-> Coordenadas del lasfile segun cabecera (redondeadas al metro, si procede):')
                printMsg(f'{TB}-> myLasHead.xminBloqueMalla: {self.xminBloqueMalla}')
                printMsg(f'{TB}-> myLasHead.xmaxBloqueMalla: {self.xmaxBloqueMalla}')
                printMsg(f'{TB}-> myLasHead.yminBloqueMalla: {self.yminBloqueMalla}')
                printMsg(f'{TB}-> myLasHead.ymaxBloqueMalla: {self.ymaxBloqueMalla}')


        self.guid1 = self.headDict['guid1']
        self.guid2 = self.headDict['guid2']
        self.guid3 = self.headDict['guid3']
        self.guid4 = self.headDict['guid4']

        if self.lasVersion == 'LasFormat_1_2' or self.lasVersion == 'LasFormat_1_3':
            self.numptrecords = self.headDict['numptrecords']
            self.pointrecords = self.numptrecords
            self.numptbyreturn = np.array(self.headDict['numptbyreturn'], dtype=np.int64)
            self.pointsbyreturn = self.numptbyreturn
        elif self.lasVersion == 'LasFormat_1_4':
            # LASF format 1.4 mantiene el campo original con un maximo de 2^32 puntos y el nuevo con maximo de 2^64 puntos
            # Si el numero de puntos es menor de 2^32, ambos coicdein, en caso contrario el priero el 0 y solo vale el segundo
            self.pointrecords = self.headDict['pointrecords']
            if self.pointrecords < 2**32 - 1: #  ~ 4e9
                self.numptrecords = self.pointrecords
            else: #  Esto no ocurre nunca, porque ningun fichero tiene mas de 4.000 millones de puntos
                self.numptrecords = 2**32 - 1
            # Asigno al campo legacy el nuevo valor mas completo
            self.headDict['numptrecords'] = self.numptrecords
            # Numero de puntos por retorno
            self.pointsbyreturn = np.array(self.headDict['pointsbyreturn'], dtype=np.int64)
            self.numptbyreturn = self.pointsbyreturn
            # Asigno al campo legacy el nuevo valor (truncado a 5 retornos por pulso)
            self.headDict['numptbyreturn'] = self.headDict['pointsbyreturn'][:5]
        # ======================================================================

        # ======================================================================
        # No se puede pasar un np.dtype() como self.formatoDtypeIdValNotacionNpDtype como argumento a una funcion Numba
        # self.formatoDtypeIdValNotacionNpDtype = np.dtype([ ('Id', '=h', 1), ('Val', '=l', 1)]) #h: short integer (2bytes); l: long integer (4 bytes)
        self.formatoDtypeIdValNotacionNpDtype = np.dtype([('Id', '=h'), ('Val', '=l')])  # h: short integer (2bytes); l: long integer (4 bytes)
        # ======================================================================
        # Ver: https://docs.scipy.org/doc/numpy/reference/generated/numpy.dtype.html
        # self.myLasHead.formatoDtypeTipoPlanoNotacionNpDtype = np.dtype([ ('nTP', '=h', 1), ('Nombre', '|S5', 1), ('Calcular', '?', 1)]) #TP (h: short integer (2bytes)): [1, 2, 3]; Nombre: ['Basal', 'Cielo', 'Major']; 'Calcular': bool
        self.formatoDtypeTipoPlanoNotacionNpDtype = np.dtype(
            [('nTP', '=h'), ('Nombre', '|S5'), ('Calcular', '?')]
        )  # TP (h: short integer (2bytes)): [1, 2, 3]; Nombre: ['Basal', 'Cielo', 'Major']; 'Calcular': bool
        # ======================================================================


        # ======================================================================
        # ============= Formato dtype del pointformat seleccionado =============
        # ======================================================================
        # Leo las propiedades del punto de mi las file de lasPointFields.cfg
        # ======================================================================
        miPointformat = self.pointformat
        # print('clidhead-> LasHeadClass-> miPointformat:', miPointformat)
        # print('\t->', self.headDict['pointformat'])
        # print('clidhead-> LasHeadClass-> (x) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesList,
            self.lasPointFieldPropertiesDict,
            self.lasPointFieldOrdenDictPtoMini,
            self.lasPointFieldOrdenDictPtoComp,
        ) = lasPointProperties(
            miPointformat,
            extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPto,
            self.bytearrayPropPtoNombre,
            self.arrayPropPtoNombre,
            self.arrayPropPtoRangoBytes,
            self.arrayPropPtoTipoDato,
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesList)

        # ======================================================================
        # =============== Formato dtype del pointformat completo ===============
        # ======================================================================
        # Leo las propiedades del punto completo adicional de mi las file de lasPointFields.cfg
        # Es un juego completo adicional para el formato de punto que abarca a todos (~8)
        # ======================================================================
        miPointformat = 99
        # print('clidhead-> LasHeadClass-> (99) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat99,
            self.lasPointFieldPropertiesDictPointFormat99,
            self.lasPointFieldOrdenDictPtoMiniPointFormat99,
            self.lasPointFieldOrdenDictPtoCompPointFormat99,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat99,
            self.bytearrayPropPtoNombrePointFormat99,
            self.arrayPropPtoNombrePointFormat99,
            self.arrayPropPtoRangoBytesPointFormat99,
            self.arrayPropPtoTipoDatoPointFormat99
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat99)

        # ======================================================================
        # ==== Formatos dtype del pointformat 3 y 8 para generar nuevo las =====
        # ======================================================================
        # Leo las propiedades del punto completo adicional de mi las file de lasPointFields.cfg
        # ======================================================================

        miPointformat = 0
        # print('clidhead-> LasHeadClass-> (0) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat00,
            self.lasPointFieldPropertiesDictPointFormat00,
            self.lasPointFieldOrdenDictPtoMiniPointFormat00,
            self.lasPointFieldOrdenDictPtoCompPointFormat00,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat00,
            self.bytearrayPropPtoNombrePointFormat00,
            self.arrayPropPtoNombrePointFormat00,
            self.arrayPropPtoRangoBytesPointFormat00,
            self.arrayPropPtoTipoDatoPointFormat00
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat00)

        miPointformat = 1
        # print('clidhead-> LasHeadClass-> (1) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat01,
            self.lasPointFieldPropertiesDictPointFormat01,
            self.lasPointFieldOrdenDictPtoMiniPointFormat01,
            self.lasPointFieldOrdenDictPtoCompPointFormat01,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat01,
            self.bytearrayPropPtoNombrePointFormat01,
            self.arrayPropPtoNombrePointFormat01,
            self.arrayPropPtoRangoBytesPointFormat01,
            self.arrayPropPtoTipoDatoPointFormat01
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat01)

        miPointformat = 2
        # print('clidhead-> LasHeadClass-> (2) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat02,
            self.lasPointFieldPropertiesDictPointFormat02,
            self.lasPointFieldOrdenDictPtoMiniPointFormat02,
            self.lasPointFieldOrdenDictPtoCompPointFormat02,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat02,
            self.bytearrayPropPtoNombrePointFormat02,
            self.arrayPropPtoNombrePointFormat02,
            self.arrayPropPtoRangoBytesPointFormat02,
            self.arrayPropPtoTipoDatoPointFormat02
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat02)

        miPointformat = 3
        # print('clidhead-> LasHeadClass-> (3) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat03,
            self.lasPointFieldPropertiesDictPointFormat03,
            self.lasPointFieldOrdenDictPtoMiniPointFormat03,
            self.lasPointFieldOrdenDictPtoCompPointFormat03,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat03,
            self.bytearrayPropPtoNombrePointFormat03,
            self.arrayPropPtoNombrePointFormat03,
            self.arrayPropPtoRangoBytesPointFormat03,
            self.arrayPropPtoTipoDatoPointFormat03
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat03)

        miPointformat = 4
        # print('clidhead-> LasHeadClass-> (4) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat04,
            self.lasPointFieldPropertiesDictPointFormat04,
            self.lasPointFieldOrdenDictPtoMiniPointFormat04,
            self.lasPointFieldOrdenDictPtoCompPointFormat04,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat04,
            self.bytearrayPropPtoNombrePointFormat04,
            self.arrayPropPtoNombrePointFormat04,
            self.arrayPropPtoRangoBytesPointFormat04,
            self.arrayPropPtoTipoDatoPointFormat04
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat04)

        miPointformat = 5
        # print('clidhead-> LasHeadClass-> (5) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat05,
            self.lasPointFieldPropertiesDictPointFormat05,
            self.lasPointFieldOrdenDictPtoMiniPointFormat05,
            self.lasPointFieldOrdenDictPtoCompPointFormat05,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat05,
            self.bytearrayPropPtoNombrePointFormat05,
            self.arrayPropPtoNombrePointFormat05,
            self.arrayPropPtoRangoBytesPointFormat05,
            self.arrayPropPtoTipoDatoPointFormat05
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat05)

        miPointformat = 6
        # print('clidhead-> LasHeadClass-> (6) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat06,
            self.lasPointFieldPropertiesDictPointFormat06,
            self.lasPointFieldOrdenDictPtoMiniPointFormat06,
            self.lasPointFieldOrdenDictPtoCompPointFormat06,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat06,
            self.bytearrayPropPtoNombrePointFormat06,
            self.arrayPropPtoNombrePointFormat06,
            self.arrayPropPtoRangoBytesPointFormat06,
            self.arrayPropPtoTipoDatoPointFormat06
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat06)

        miPointformat = 7
        # print('clidhead-> LasHeadClass-> (7) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat07,
            self.lasPointFieldPropertiesDictPointFormat07,
            self.lasPointFieldOrdenDictPtoMiniPointFormat07,
            self.lasPointFieldOrdenDictPtoCompPointFormat07,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat07,
            self.bytearrayPropPtoNombrePointFormat07,
            self.arrayPropPtoNombrePointFormat07,
            self.arrayPropPtoRangoBytesPointFormat07,
            self.arrayPropPtoTipoDatoPointFormat07
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat07)

        miPointformat = 8
        # print('clidhead-> LasHeadClass-> (8) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat08,
            self.lasPointFieldPropertiesDictPointFormat08,
            self.lasPointFieldOrdenDictPtoMiniPointFormat08,
            self.lasPointFieldOrdenDictPtoCompPointFormat08,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat08,
            self.bytearrayPropPtoNombrePointFormat08,
            self.arrayPropPtoNombrePointFormat08,
            self.arrayPropPtoRangoBytesPointFormat08,
            self.arrayPropPtoTipoDatoPointFormat08
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat08)

        miPointformat = 9
        # print('clidhead-> LasHeadClass-> (9) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat09,
            self.lasPointFieldPropertiesDictPointFormat09,
            self.lasPointFieldOrdenDictPtoMiniPointFormat09,
            self.lasPointFieldOrdenDictPtoCompPointFormat09,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat09,
            self.bytearrayPropPtoNombrePointFormat09,
            self.arrayPropPtoNombrePointFormat09,
            self.arrayPropPtoRangoBytesPointFormat09,
            self.arrayPropPtoTipoDatoPointFormat09
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat09)

        miPointformat = 10
        # print('clidhead-> LasHeadClass-> (10) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat10,
            self.lasPointFieldPropertiesDictPointFormat10,
            self.lasPointFieldOrdenDictPtoMiniPointFormat10,
            self.lasPointFieldOrdenDictPtoCompPointFormat10,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointFormat10,
            self.bytearrayPropPtoNombrePointFormat10,
            self.arrayPropPtoNombrePointFormat10,
            self.arrayPropPtoRangoBytesPointFormat10,
            self.arrayPropPtoTipoDatoPointFormat10
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat10)

        # ======================================================================
        # self.formatoDtypePointFormatXXNotacionNpDtype = np.dtype([(pr[0], pr[2], pr[3]) for pr in self.lasPointFieldPropertiesList])
        # self.formatoDtypePointFormatXXNotacionNpDtype = np.dtype([(pr[0], pr[2], (pr[3],)) for pr in self.lasPointFieldPropertiesList])
        # Alternativa para usar ndarrays solo para cuando hay multiplicidad:

        # Si intento usar un formato de punto con campos ficticios tiene que ser
        # un tipo de dato que me permita longitud 0 o tratarlo como un array (nestedarray) con 0 elementos 
        # Pero los arrays vacios son incompatibles con otros posibles valores dentro de una funcion numba:
        #  hash() es la unica funcion que puedo aplicar lo mismo a un string o un int (o a un array o lista ... pero con elementos)
        #   pero hash() da error con listas o arrays vacios:
        #    cannot compute fingerprint of empty list
        # Esto se discute en:
        #    https://github.com/stuartarchibald/numba/commit/917590eb1e8ab7534ab8eb085a9fc751c2e14b37
        # ======================================================================
        # Necesito que una misma variable dentro de una funcion numba pueda adoptar
        # valores enteros (de 1, 2, 4 u 8 bytes) o "algo" que ocupe 0 bytes 
        # para el point format 3 y n bytes para el point format 8.
        # La solucion final que me permite que a una misma variable se pueda asignar 
        # un entero de 1, 2, 4 u 8 bytes o un algo de 0 bytes
        # ha sido usar el tipo de dato 'S0'
        # Lo tengo que definir directamente en notacion "Array-protocol type strings")
        # porque en notacion "One-character strings" -> Ver lasPointFields.cfg
        # ======================================================================
        # https://numpy.org/doc/stable/reference/arrays.dtypes.html
        # ======================================================================

        # ======================================================================
        self.formatoDtypePointFormatXXNotacionOneChar = []
        for pr in self.lasPointFieldPropertiesList:
            if pr[3] == 1:
                self.formatoDtypePointFormatXXNotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormatXXNotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        # print( 'clidhead-> LasHeadClass-> lasPointFieldPropertiesList', self.lasPointFieldPropertiesList)
        # print( 'clidhead-> LasHeadClass->', [(pr[0], pr[2], pr[3]) for pr in self.lasPointFieldPropertiesList])
        self.formatoDtypePointFormatXXNotacionNpDtype = np.dtype(self.formatoDtypePointFormatXXNotacionOneChar)
        # print('clidhead-> LasHeadClass-> pfX self.formatoDtypePointFormatXXNotacionOneChar:', self.formatoDtypePointFormatXXNotacionOneChar)
        # print('clidhead-> LasHeadClass-> pfX self.formatoDtypePointFormatXXNotacionNpDtype:', self.formatoDtypePointFormatXXNotacionNpDtype)

        if GLO.GLBLdarPrioridadAPointFormatFrenteAReclen:
            print(f'{TB}-> Se da prioridad al pointFormat frente al reclen')
            print(f'{TB}{TV}con lo que el point format se mantiene en {self.pointformatOriginal}')
            print(f'{TB}{TV}y se usa el extraBytesPorRegistro de {self.extraBytesPorRegistro} bytes para generar el dtype:')
            print(f'{TB}{TV}-> formatoDtypePointFormatXXNotacionNpDtype: {self.formatoDtypePointFormatXXNotacionNpDtype}')
        else:
            print(f'{TB}-> Se da prioridad al reclen frente al pointFormat')
            print(f'{TB}{TV}con lo que el point format se ha cambiado de {self.pointformatOriginal} a {self.pointformatNuevo}')
            print(f'{TB}{TV}el extraBytesPorRegistro es nulo y el dtype es el propio del pointFormat {self.pointformatNuevo}:')
            print(f'{TB}{TV}-> formatoDtypePointFormatXXNotacionNpDtype: {self.formatoDtypePointFormatXXNotacionNpDtype}')
        # ======================================================================

        # Creo el juego adicional para el formato de punto completo, engloba al 3 y al 8 
        self.formatoDtypePointFormat99NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat99:
            if pr[3] == 1:
                self.formatoDtypePointFormat99NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat99NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat99NotacionNpDtype = np.dtype(self.formatoDtypePointFormat99NotacionOneChar)

        # Creo los juegos adicionales para los formatos de punto 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 y 10 
        self.formatoDtypePointFormat00NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat00:
            if pr[3] == 1:
                self.formatoDtypePointFormat00NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat00NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat00NotacionNpDtype = np.dtype(self.formatoDtypePointFormat00NotacionOneChar)

        self.formatoDtypePointFormat01NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat01:
            if pr[3] == 1:
                self.formatoDtypePointFormat01NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat01NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat01NotacionNpDtype = np.dtype(self.formatoDtypePointFormat01NotacionOneChar)

        self.formatoDtypePointFormat02NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat02:
            if pr[3] == 1:
                self.formatoDtypePointFormat02NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat02NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat02NotacionNpDtype = np.dtype(self.formatoDtypePointFormat02NotacionOneChar)

        self.formatoDtypePointFormat03NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat03:
            if pr[3] == 1:
                self.formatoDtypePointFormat03NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat03NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat03NotacionNpDtype = np.dtype(self.formatoDtypePointFormat03NotacionOneChar)

        self.formatoDtypePointFormat04NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat04:
            if pr[3] == 1:
                self.formatoDtypePointFormat04NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat04NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat04NotacionNpDtype = np.dtype(self.formatoDtypePointFormat04NotacionOneChar)

        self.formatoDtypePointFormat05NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat05:
            if pr[3] == 1:
                self.formatoDtypePointFormat05NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat05NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat05NotacionNpDtype = np.dtype(self.formatoDtypePointFormat05NotacionOneChar)

        self.formatoDtypePointFormat06NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat06:
            if pr[3] == 1:
                self.formatoDtypePointFormat06NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat06NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat06NotacionNpDtype = np.dtype(self.formatoDtypePointFormat06NotacionOneChar)

        self.formatoDtypePointFormat07NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat07:
            if pr[3] == 1:
                self.formatoDtypePointFormat07NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat07NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat07NotacionNpDtype = np.dtype(self.formatoDtypePointFormat07NotacionOneChar)

        self.formatoDtypePointFormat08NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat08:
            if pr[3] == 1:
                self.formatoDtypePointFormat08NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat08NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat08NotacionNpDtype = np.dtype(self.formatoDtypePointFormat08NotacionOneChar)

        self.formatoDtypePointFormat09NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat09:
            if pr[3] == 1:
                self.formatoDtypePointFormat09NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat09NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat09NotacionNpDtype = np.dtype(self.formatoDtypePointFormat09NotacionOneChar)

        self.formatoDtypePointFormat10NotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointFormat10:
            if pr[3] == 1:
                self.formatoDtypePointFormat10NotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormat10NotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormat10NotacionNpDtype = np.dtype(self.formatoDtypePointFormat10NotacionOneChar)
        # ======================================================================

        # if GLO.GLBLverbose:
        #     print(f'clidhead-> LasHeadClass-> Descripcion del formato formatoDtype:')
        #     print(f'{TB}-> pf8 self.formatoDtypePointFormat99NotacionOneChar: {self.formatoDtypePointFormat99NotacionOneChar}')
        #     # [('x', '=I'), ('y', '=I'), ('z', '=I'), ('intensity', 'H'), ('return_grp', 'B'), ('extra_grp', 'B'), ('classification', 'B'),
        #     # ('user_data', 'b'), ('scan_angle_rank', 'h'), ('point_source_ID', 'H'), ('raw_time', 'd'), ('red', 'H'), ('green', 'H'), ('blue', 'H'), ('nir', 'H'),
        #     # ('lasClassAsignadaASPRS19', 'B'), ('lasClassAsignadaTRKTS99', 'B'), ('lasClassPredichaMiniSubCel', 'B'), ('lasClassPredichaConvolucion', 'B'),
        #     # ('lasClassPredichaTreeASPRS19', 'B'), ('lasClassPredichaTreeTRKTS99', 'B'), ('lasClassPredichaNlnASPRS19', 'B'), ('usoSingular', 'B'),
        #     # ('nucleoUrbano', 'B'), ('landCover', 'B'), ('geoTipo', 'B'), ('cartoExtra', 'B'), ('distanciaEnDmHastaEdificio', 'B'), ('usoSingularPredicho', 'B'),
        #     # ('usoSingularPredichoA', 'B'), ('usoSingularPredichoB', 'B'), ('cotaCmSobreMdt', 'h'), ('cotaCmMdf', '=I'), ('cotaCmSobreMdfConvol16bits', 'h'),
        #     # ('cotaCmSobreMdfConual16bits', 'h'), ('cotaCmSobreMdfManual16bits', 'h'), ('esMiniMaxiSubCel', 'B'), ('esMiniMaxiCel', 'B'), ('esApice', 'B'), ('xH30', '=I'), ('yH30', '=I')]
        #     print(f'{TB}-> pf8 self.formatoDtypePointFormat99NotacionNpDtype: {self.formatoDtypePointFormat99NotacionNpDtype}')
        #     # [('x', '<u4'), ('y', '<u4'), ('z', '<u4'), ('intensity', '<u2'), ('return_grp', 'u1'), ('extra_grp', 'u1'), ('classification', 'u1'),
        #     # ('user_data', 'i1'), ('scan_angle_rank', '<i2'), ('point_source_ID', '<u2'), ('raw_time', '<f8'), ('red', '<u2'), ('green', '<u2'), ('blue', '<u2'), ('nir', '<u2'),
        #     # ('lasClassAsignadaASPRS19', 'u1'), ('lasClassAsignadaTRKTS99', 'u1'), ('lasClassPredichaMiniSubCel', 'u1'), ('lasClassPredichaConvolucion', 'u1'),
        #     # ('lasClassPredichaTreeASPRS19', 'u1'), ('lasClassPredichaTreeTRKTS99', 'u1'), ('lasClassPredichaNlnASPRS19', 'u1'), ('usoSingular', 'u1'),
        #     # ('nucleoUrbano', 'u1'), ('landCover', 'u1'), ('geoTipo', 'u1'), ('cartoExtra', 'u1'), ('distanciaEnDmHastaEdificio', 'u1'), ('usoSingularPredicho', 'u1'),
        #     # ('usoSingularPredichoA', 'u1'), ('usoSingularPredichoB', 'u1'), ('cotaCmSobreMdt', '<i2'), ('cotaCmMdf', '<u4'), ('cotaCmSobreMdfConvol16bits', '<i2'), 
        #     # ('cotaCmSobreMdfConual16bits', '<i2'), ('cotaCmSobreMdfManual16bits', '<i2'), ('esMiniMaxiSubCel', 'u1'), ('esMiniMaxiCel', 'u1'), ('esApice', 'u1'), ('xH30', '<u4'), ('yH30', '<u4')]

        self.miPtoNpArrayRecord = np.zeros(1 * 1 * 1, dtype=np.dtype(self.formatoDtypePointFormatXXNotacionNpDtype)).reshape(1, 1, 1)
        self.miPtoNpRecordPointFormatXX = self.miPtoNpArrayRecord[0, 0, 0]

        self.miPtoNpArrayRecordPointFormat99 = np.zeros(1, dtype=np.dtype(self.formatoDtypePointFormat99NotacionNpDtype))
        self.miPtoNpRecordPointFormat99 = self.miPtoNpArrayRecordPointFormat99[0]

        # ======================================================================
        # ================= Formato dtype de PointCustomizado ==================
        # ======================================================================
        # Leo las propiedades del punto customizado ([lo uso] en clidnv2x y clidnv6) (le llamo pointFormat=100) de lasPointFields.cfg
        # ======================================================================
        miPointformat = 100
        # print('clidhead-> LasHeadClass-> (100) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointCustomizado,
            self.lasPointFieldPropertiesDictPointCustomizado,
            self.lasPointFieldOrdenDictPtoMiniPointCustomizado,
            self.lasPointFieldOrdenDictPtoCompPointCustomizado,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        (
            self.npArrayPropPtoPointCustomizado,
            self.bytearrayPropPtoNombrePointCustomizado,
            self.arrayPropPtoNombrePointCustomizado,
            self.arrayPropPtoRangoBytesPointCustomizado,
            self.arrayPropPtoTipoDatoPointCustomizado
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointCustomizado)
        # ======================================================================
        self.nBytesPointCustomizado = sum(int(pointField[1]) for pointField in self.lasPointFieldPropertiesListPointCustomizado)
        # ======================================================================
        self.formatoDtypePointCustomizadoNotacionOneChar = []
        for pr in self.lasPointFieldPropertiesListPointCustomizado:
            if pr[3] == 1:
                self.formatoDtypePointCustomizadoNotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointCustomizadoNotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointCustomizadoNotacionNpDtype = np.dtype(self.formatoDtypePointCustomizadoNotacionOneChar)
        # ======================================================================

        # if GLO.GLBLverbose:
        #     print(f'{TB}-> pf8 self.formatoDtypePointCustomizadoNotacionOneChar: {self.formatoDtypePointCustomizadoNotacionOneChar}')
        #     # [('x', 'd'), ('y', 'd'), ('z', 'd'), ('clase', 'B'), ('retN', 'B'), ('cotaMds', 'f'), ('cotaMdb', 'f'), ('cotaMdf', 'f'), ('lasClassAsignada', 'B'), ('lasClassPredicha', 'B')]
        #     print(f'{TB}-> pf8 self.formatoDtypePointCustomizadoNotacionNpDtype: {self.formatoDtypePointCustomizadoNotacionNpDtype}')
        #     # [('x', '<f8'), ('y', '<f8'), ('z', '<f8'), ('clase', 'u1'), ('retN', 'u1'), ('cotaMds', '<f4'), ('cotaMdb', '<f4'), ('cotaMdf', '<f4'), ('lasClassAsignada', 'u1'), ('lasClassPredicha', 'u1')]

        # ======================================================================
        # ================= Formato dtype de las extraVariables ================
        # ======================================================================
        # Leo las propiedades del punto de mis extraVariables (le llamo pointFormat=101) de lasPointFields.cfg
        # ======================================================================
        miPointformat = 101
        # print('clidhead-> LasHeadClass-> (101) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.extraVariablesPropertiesList,
            self.extraVariablesPropertiesDict,
            self.extraVariablesOrdenDictPtoMini,
            self.extraVariablesOrdenDictPtoComp,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        # Esto otro para facilitar el acceso a las propiedades desde funciones numba
        (
            self.npArrayextraVar,
            self.bytearrayextraVarNombre,
            self.arrayextraVarNombre,
            self.arrayextraVarRangoBytes,
            self.arrayextraVarTipoDato,
        ) = crearArraysPropPto(miPointformat, self.extraVariablesPropertiesList)
        # ======================================================================
        self.nBytesExtraVars = sum(int(pointField[1]) for pointField in self.extraVariablesPropertiesList)
        # ======================================================================
        self.formatoDtypeExtrVarNotacionOneChar = []
        for pr in self.extraVariablesPropertiesList:
            if pr[3] == 1:
                self.formatoDtypeExtrVarNotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypeExtrVarNotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypeExtrVarNotacionNpDtype = np.dtype(self.formatoDtypeExtrVarNotacionOneChar)
        # ======================================================================

        # ======================================================================
        # ================= Formato dtype de las maxiMiniSubCel ================
        # ======================================================================
        # Leo las propiedades del punto de mis maxiMiniSubCel (le llamo pointFormat=102) de lasPointFields.cfg
        # ======================================================================
        miPointformat = 102
        # print('clidhead-> LasHeadClass-> (102) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.maxiMiniSubCelPropertiesList,
            self.maxiMiniSubCelPropertiesDict,
            self.maxiMiniSubCelOrdenDictPtoMini,
            self.maxiMiniSubCelOrdenDictPtoComp,
        ) = lasPointProperties(
            miPointformat,
            # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
            verbose=self.verbose,
        )
        # Esto otro para facilitar el acceso a las propiedades desde funciones numba
        (
            self.npArrayextraVar,
            self.bytearrayextraVarNombre,
            self.arrayextraVarNombre,
            self.arrayextraVarRangoBytes,
            self.arrayextraVarTipoDato,
        ) = crearArraysPropPto(miPointformat, self.maxiMiniSubCelPropertiesList)
        # ======================================================================
        self.nBytesExtraVars = sum(int(pointField[1]) for pointField in self.maxiMiniSubCelPropertiesList)
        # ======================================================================
        self.formatoDtypePointMaxMinNotacionOneChar = []
        for pr in self.maxiMiniSubCelPropertiesList:
            if pr[3] == 1:
                self.formatoDtypePointMaxMinNotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointMaxMinNotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointMaxMinNotacionNpDtype = np.dtype(self.formatoDtypePointMaxMinNotacionOneChar)
        # ======================================================================

        # ======================================================================
        if GLO.GLBLalmacenarPuntosComoCompactNpDtype:
            # Ver notacion en https://docs.scipy.org/doc/numpy/reference/generated/numpy.dtype.html
            # Ver tb https://www.numpy.org/devdocs/reference/arrays.dtypes.html -> Specifying and constructing data types
            # Ver tb https://www.numpy.org/devdocs/reference/arrays.scalars.html#arrays-scalars-built-in
            # self.formatoDtypePointCompactNotacionNpDtype = np.dtype([('x', '<u4', 1), ('y', '<u4', 1), ('z', '<u4', 1), ('return_grp', '|u1', 1), ('classification', '|u1', 1), ('scan_angle_rank', '|i1', 1), ('point_source_ID', '<u2', 1), ('raw_time', '<u8', 1)])
            self.formatoDtypePointCompactNotacionNpDtype = np.dtype(
                [
                    ('x', '<u4'),
                    ('y', '<u4'),
                    ('z', '<u4'),
                    ('return_grp', '|u1'),
                    ('classification', '|u1'),
                    ('scan_angle_rank', '|i1'),
                    ('point_source_ID', '<u2'),
                    ('raw_time', '<u8'),
                ]
            )
        else:
            self.formatoDtypePointCompactNotacionNpDtype = self.formatoDtypePointFormatXXNotacionNpDtype
        # ======================================================================
        # https://docs.python.org/3/library/array.html#module-array
        # https://docs.python.org/3/library/struct.html#format-characters
        # point_source_ID = 2, H, 1, 18, p
        # x = 4, =L, 1, 0, x
        # y = 4, =L, 1, 4, y
        # z = 4, =L, 1, 8, z
        # intensity = 2, H, 1, 12, i
        # return_grp = 1, B, 1, 14, n
        # classification = 1, B, 1, 15, c
        # raw_time = 8, d, 1, 16, t
        # Notacion np.dtype():
        # char
        #     A unique character code for each of the 21 different built-in types.
        # kind
        #     A character code (one of 'biufcmMOSUV') identifying the general kind of data.
        #     b     boolean
        #     i     signed integer
        #     u     unsigned integer
        #     f     floating-point
        #     c     complex floating-point
        #     m     timedelta
        #     M     datetime
        #     O     object
        #     S     (byte-)string
        #     U     Unicode
        #     V     void
        # byteorder
        #     A character indicating the byte-order of this data-type object.
        #     One of:
        #     '='     native
        #     '<'     little-endian
        #     '>'     big-endian
        #     '|'     not applicable
        # tipoDatoPuntoString = '|S%i' % self.myLasHead.nBytesPorPunto
        # ======================================================================

        if self.verbose:
            sys.stdout.write('\nclidhead-> Control AA\n')
            sys.stdout.flush()
            sys.stderr.flush()

        # Basic checking of las file, nCeldas and coordinates from fileName:
        if self.verbose or __verbose__:
            if GLO.GLBLforzarExtensionDeBloqueAvalorNominal and self.LCLforzarExtensionDeBloqueAvalorNominal:
                printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> LasHeadClass-> Info: Se parte de las coordenadas de bloque deducidas del nombre del fichero-> GLBLforzarExtensionDeBloqueAvalorNominal: {GLO.GLBLforzarExtensionDeBloqueAvalorNominal}')
                printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> LasHeadClass-> Coordenadas del lasfile segun fileName antes de checkLasfile:')
            else:
                printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> LasHeadClass-> Coordenadas del lasfile segun cabecera antes de checkLasfile:')
            printMsg(f'{TB}-> myLasHead.xminBloqueMalla: {self.xminBloqueMalla}')
            printMsg(f'{TB}-> myLasHead.xmaxBloqueMalla: {self.xmaxBloqueMalla}')
            printMsg(f'{TB}-> myLasHead.yminBloqueMalla: {self.yminBloqueMalla}')
            printMsg(f'{TB}-> myLasHead.ymaxBloqueMalla: {self.ymaxBloqueMalla}')

        self.metersBlockX = self.headDict['xmaxBloqueMalla'] - self.headDict['xminBloqueMalla']
        self.metersBlockY = self.headDict['ymaxBloqueMalla'] - self.headDict['yminBloqueMalla']

        self.checkLasfile(LCLverbose=verbose)
        # print('------------------>clidhead-> LasHeadClass-> infile***ConRutaLazZ:', self.infileConRuta)
        if self.verbose or __verbose__:
            if GLO.GLBLforzarExtensionDeBloqueAvalorNominal and self.LCLforzarExtensionDeBloqueAvalorNominal:
                printMsg(f'\nclidhead.{self.fileCoordYeahDelNombre}-> LasHeadClass-> Info: Se parte de las coordenadas de bloque deducidas del nombre del fichero-> GLBLforzarExtensionDeBloqueAvalorNominal: {GLO.GLBLforzarExtensionDeBloqueAvalorNominal}')
                printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> LasHeadClass-> Coordenadas del lasfile segun fileName despues de checkLasfile:')
            else:
                printMsg(f'\nclidhead.{self.fileCoordYeahDelNombre}-> LasHeadClass-> Coordenadas del lasfile segun cabecera despues de checkLasfile:')
            printMsg(f'{TB}-> myLasHead.xminBloqueMalla: {self.xminBloqueMalla}')
            printMsg(f'{TB}-> myLasHead.xmaxBloqueMalla: {self.xmaxBloqueMalla}')
            printMsg(f'{TB}-> myLasHead.yminBloqueMalla: {self.yminBloqueMalla}')
            printMsg(f'{TB}-> myLasHead.ymaxBloqueMalla: {self.ymaxBloqueMalla}')
            printMsg(f'{"":=^80}')

        if self.verbose:
            sys.stdout.write('\nclidhead-> Control AB\n')
            sys.stdout.flush()
            sys.stderr.flush()


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def readLasHead(self):
        """
        Read lasFile head (i/ VLR) of self.infileConRuta and creates self.headDict[]
        This is the main method of LasHeadClass
        LasFile head fields are readed from cartolidar/data/ext/io/lasHeadFields.cfg
            Properties of lasFile version 1.3 correspond to LasFormat_1_2 + LasFormat_1_3
            Properties of lasFile version 1.4 correspond to LasFormat_1_2 + LasFormat_1_3 + LasFormat_1_4
        LasFile point fields are readed from cartolidar/data/ext/io/lasPointFields.cfg
        """
        (
            self.lasHeaderFieldListVersionsDict,
            self.lasHeaderFieldPropertiesDict,
            self.lasHeaderFieldPropertiesList
        ) = lasHeadProperties()
        if self.verbose:
            printMsg('clidhead-> LasHeadClass-> Leyendo propiedades de los campos de cabecera de cartolidar/data/ext/io/lasHeadFields.cfg:')
            # printMsg('\tlasHeaderFieldListVersionsDict-> ' + str(self.lasHeaderFieldListVersionsDict))
            # printMsg('\tlasHeaderFieldPropertiesDict>    ' + str(self.lasHeaderFieldPropertiesDict))
            # printMsg('\tlasHeaderFieldPropertiesList->   ' + str(self.lasHeaderFieldPropertiesList))

        # r      reading only.
        # rb     reading only in binary format.
        # r+     both reading and writing. Read and write to a file without overwriting it
        # rb+    both reading and writing in binary format.
        # w      writing only. Erase and write to a file
        # wb     writing only in binary format.
        # w+     both writing and reading (Overwrite). Write and read a file, overwriting its contents
        # wb+    both writing and reading in binary format.
        # a      appending. Add new lines to the end of a file
        # ab     appending in binary format.
        # a+     both appending and reading.
        # ab+    both appending and reading in binary format. 

        # A pesar de conocer la extension, chequeo si es un fichero comprimido:
        #  Se lee el pointformat de la cabecera: si es superior a 128, es laszip
        #  Eso tb se puede verificar con los bit 6 y 7 (metodo de laspy)
        if not self.lasDataMem is None:
            # En este caso, ya se ha descomprimido en memoria.
            # La propiedad esComprimido se refiere al objeto que voy a usar (self.lasDataMem)
            esComprimido = False
        else:
            try:
                if GLO.GLBLverbose or self.verbose:
                    print('clidhead-> LasHeadClass-> Se va a abrir el fichero: {}'.format(self.infileConRuta))
                self.ficheroLas = open(self.infileConRuta, "rb")
                if GLO.GLBLverbose or self.verbose:
                    print(f'{TB}-> Leyendo el fichero abierto. Se lee el byte 104'.format(self.infileConRuta))
                self.ficheroLas.seek(104)
                byteLeido = self.ficheroLas.read(1)
                if GLO.GLBLverbose or self.verbose:
                    print(f'{TB}-> Byte leido:', byteLeido, 'Numero de bytes:', len(byteLeido))
                fmt = int(struct.unpack("<B", byteLeido)[0])
                if GLO.GLBLverbose or self.verbose:
                    print(f'{TB}-> Byte unpack (fmt):', fmt)
                compression_bit_7 = (fmt & 0x80) >> 7
                compression_bit_6 = (fmt & 0x40) >> 6
                if (not compression_bit_6 and compression_bit_7):
                    if GLO.GLBLverbose or self.verbose:
                        print(f'{TB}{TV}-> Fichero SI comprimido')
                    esComprimido = True
                else:
                    if GLO.GLBLverbose or self.verbose:
                        print(f'{TB}{TV}-> Fichero NO comprimido')
                    esComprimido = False
                self.ficheroLas.close()
            except Exception as err:
                printMsg('clidhead.{:006}-> System error al leer el compression bit: {}'.format(GLO.MAIN_idProceso, err))
                print(f'{TB}-> infileConRuta:', self.infileConRuta)
                fmt = '-'
                if self.infileConRuta[-4:].lower() == '.laz':
                    esComprimido = True
                else:
                    esComprimido = False
                #sys.exit(0)

            # Prevalece el contenido del fichero sobre la extension
            if self.lazfile and not esComprimido and self.lasDataMem is None:
                print('clidhead.{:006}-> ATENCION: fichero laz que no es realmente un laszip (no esta comprimido)'.format(GLO.MAIN_idProceso))
                print(f'{TB}-> self.lasDataMem is None:',  self.lasDataMem is None)
                print(f'{TB}-> pointformat: {fmt}')
                self.lazfile = False
            elif not self.lazfile and esComprimido:
                print('clidhead.{:006}-> ATENCION: fichero las que en realidad es un un laszip (esta comprimido)'.format(GLO.MAIN_idProceso))
                print(f'{TB}-> self.lasDataMem is None:',  self.lasDataMem is None)
                print(f'{TB}-> pointformat: {fmt}')
                self.lazfile = True

        if not self.lasDataMem is None:
            if self.verbose:
                printMsg(f'clidhead-> LasHeadClass-> Lectura de los datos desde el objeto de tipo <memoryview> generado a partir del objeto <bytes> creado al descomprimir el laz')
                printMsg(f'{TB}-> type(self.lasDataMem)-> {type(self.lasDataMem)}')
                printMsg(f'{TB}-> len(self.lasDataMem)->  {len(self.lasDataMem)}')
                # https://www.devdungeon.com/content/working-binary-data-python
                printMsg('clidhead-> LasHeadClass-> convirtiendo bytes a memoryview')
            # ==================================================================
            self.ficheroLas = memoryview(self.lasDataMem)
            # ==================================================================
            #self.ficheroLas = self.lasDataMem # 'bytes' object has no attribute 'tell'
            if self.verbose:
                printMsg(f'{TB}-> LasHeadClass-> Ok memoryview, len(ficheroLas): {len(self.ficheroLas)}')
            if len(self.ficheroLas) == 0:
                printMsg('nclidhead.{:006}-> ATENCION: no se ha leido bien el fichero laz descomprimiendo en memoria. esComprimido: {}'.format(
                    GLO.MAIN_idProceso, esComprimido))
        else:
            if self.verbose:
                printMsg('clidhead-> LasHeadClass-> Lectura de los datos desde el objeto de tipo <class "_io.BufferedReader"> generado con open()')
                printMsg(f'{TB}-> type(self.lasDataMem)-> {type(self.lasDataMem)}')
            try:
            # ==================================================================
                self.ficheroLas = open(self.infileConRuta, 'rb')
                if self.verbose:
                    printMsg(f'{TB}-> type(self.ficheroLas)-> {type(self.ficheroLas)}')
            # ==================================================================
            except SystemError as err:  # Raised for operating systemrelated errors.
                printMsg('clidhead.%06i-> System error when opening lasFile %s (for head reading)' % (GLO.MAIN_idProceso, self.infileConRuta))
                printMsg('\tError: {}'.format(err))
                sys.exit(0)
            except (Exception) as err:
                sys.stderr.write('clidhead.%06i-> Error al leer la cabecera del fichero las: %s\n' % (GLO.MAIN_idProceso, self.infileConRuta))
                printMsg('\tTipo de valor de error: {}'.format(type(err)))
                printMsg('\tArgumentos del error:   {}'.format(err.args))
                printMsg('\tError:                  {}'.format(err))
                sys.exit(0)
            except:  # catch *all* exceptions
                printMsg('clidhead.%06i-> Error opening lasFile %s (for head reading)' % (GLO.MAIN_idProceso, self.infileConRuta))
                err = sys.exc_info()[0]
                printMsg('\tError desconocido: {}'.format(err))
                sys.exit(0)

        self.headBin = b''
        self.sumaBytesCabecera = 0

        # Para eliminar los /x00 (caracteres nulos) ver https://stackoverflow.com/questions/38883476/how-to-remove-those-x00-x00
        # Aviso: Con .decode('latin-1') se decodifica para que se muestre bien con print(), pero los /x00 siguen en el string
        self.headDict = {'infile': self.infileConRuta}

        # Los primeros 227 Bytes del fichero son la cabecera
        leerNumBytes = 4
        self.signature = self.readLasBytes(leerNumBytes, warningId='w1a')
        self.headBin += self.signature
        self.sumaBytesCabecera += leerNumBytes
        self.headDict['filesignature'] = self.signature
        if self.signature.decode('ascii') != u'LASF':
            printMsg('clidhead.%06i-> WARNING w1b' % (GLO.MAIN_idProceso))
            printMsg('\tATENCION: este fichero no parece un las file (bytes 1-4 != LASF)')
            printMsg('\tBytes 1-4: ->{}<-. Num de bytes: {}'.format(self.signature.decode('ascii'), len(self.signature)))
            printMsg('\tinfileConRuta: {}'.format(self.infileConRuta))
            # print('------------------>clidhead-> LasHeadClass-> infile***ConRutaLazE:', self.infileConRuta)
            self.readOk = False
            return
#             sys.exit(0)

        if self.verbose:
            printMsg('clidhead-> LasHeadClass-> Campos en el header del lasFile:')

        lasVersionIni = 'LasFormat_1_2'
        for nField, myField in enumerate(self.lasHeaderFieldListVersionsDict[lasVersionIni][1:]):
            fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersionIni + '_' + myField]
            readBytes = self.readLasBytes(fieldProperties[0], warningId='w1c')
            self.headBin += readBytes
            self.sumaBytesCabecera += int(fieldProperties[0])
            try:
                if fieldProperties[1].strip() == 'c':
                    # String
                    # value = readBytes.rstrip(b'\x00')
                    try:
                        value = readBytes.rstrip(b'\x00').decode('latin-1')
                    except:
                        value = readBytes.rstrip(b'\x00').decode('latin-1', errors='ignore')
                elif int(fieldProperties[2]) > 1:
                    # Array -> unpack a tuple
                    try:
                        value = struct.unpack(fieldProperties[2].strip() + fieldProperties[1].strip(), readBytes)
                    except:
                        # struct.error: unpack requires a buffer of 40 bytes
                        print('Num bytes de', fieldProperties[1], struct.calcsize(fieldProperties[1]))
                        print('fieldProperties[2]', fieldProperties[2])
                        print('fieldProperties[1]', fieldProperties[1])
                        print('fieldProperties[0]', fieldProperties[0], len(readBytes))
                        print('readBytes <', readBytes, '>')
                        print('clidhead-> LasHeadClass-> Revisar esto')
                        sys.exit(0)
                else:
                    # Others: save fist item in tuple
                    value = struct.unpack(fieldProperties[1].strip(), readBytes)[0]

                '''
                Del articulo laszip de Martin Isenburg:
                LASzip does not compress the LAS header or any of the
                variable length records. It simply copies them unmodified from
                the LAS to the LAZ file. It however adds 128 to the value of
                the current point type to prevent standard LAS readers from
                attempting to read a compressed LAZ file. It also adds one
                variable length record that specifies the composition of the
                compressed points and various compression options used.
                '''
                if myField == 'pointformat' and self.lazfile:
                    value = value - 128
            except:
                printMsg('clidhead-> LasHeadClass-> WARNING w2')
                printMsg('Error reading Field {} at las head'.format(myField))
                value = readBytes

            if self.verbose:
                if not self.lasDataMem is None:
                    postPosicion = len(self.headBin)
                else:
                    postPosicion = self.ficheroLas.tell()
                printMsg(
                    f'{TB}LASF1.2-{nField:>2}-> Bytes:'
                    + f'\t{postPosicion - int(fieldProperties[0]) + 1:>3}-{postPosicion}'
                    + f'\t{myField:>14}\t{value}'
                )
            self.headDict[myField] = value
            setattr(self, myField, value)

        if self.headDict['vermajor'] > 1:
            print('clidhead-> LasHeadClass-> LASF version %i.%i, no implementada. Se interrumpe el programa' % (self.headDict['vermajor'], self.headDict['verminor']))
            print('clidhead-> LasHeadClass->           Esta aplicacion solo esta prearada para formatos LASF 1.2, [1.3] y 1.4')
            quit()

        self.lasVersion = 'LasFormat_%i_%i' % (self.headDict['vermajor'], self.headDict['verminor'])

        if (self.headDict['vermajor'] == 1 and self.headDict['verminor'] == 3) or (self.headDict['vermajor'] == 1 and self.headDict['verminor'] == 4):
            if self.headDict['vermajor'] == 1 and self.headDict['verminor'] == 3:
                printMsg('clidhead-> LasHeadClass-> Las format 1.3 only provisional (TODO)')
            lasVersion = 'LasFormat_1_3'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersion]:
                fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersion + '_' + myField]
                readBytes = self.readLasBytes(fieldProperties[0], warningId='w1d')
                self.headBin += readBytes
                self.sumaBytesCabecera += int(fieldProperties[0])
                try:
                    if fieldProperties[1].strip() == 'c':
                        # String
                        # value = readBytes.rstrip(b'\x00')
                        value = readBytes
                    elif int(fieldProperties[2]) > 1:
                        # Array -> desempaquetar a una tupla
                        value = struct.unpack(fieldProperties[2].strip() + fieldProperties[1].strip(), readBytes)
                    else:
                        # Numero binario: guardar el primer elemento de la tupla
                        value = struct.unpack(fieldProperties[1].strip(), readBytes)[0]
                except:
                    printMsg('clidhead-> LasHeadClass-> WARNING w3a')
                    printMsg('Field:', myField)
                    value = readBytes

                if self.verbose:
                    if not self.lasDataMem is None:
                        postPosicion = len(self.headBin)
                    else:
                        postPosicion = self.ficheroLas.tell()
                    printMsg(
                        f'{TB}LASF1.3-{nField:>2}-> Bytes:'
                        + f'\t{postPosicion - int(fieldProperties[0]) + 1:>3}-{postPosicion}'
                        + f'\t{myField:>14}\t{value}'
                    )
                self.headDict[myField] = value
                setattr(self, myField, value)

        if self.headDict['vermajor'] == 1 and self.headDict['verminor'] == 4:
            # TODO: revisar el las format 1.4
            # Las version 1.4: bytes in second version of las head: 148
            lasVersion = 'LasFormat_1_4'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersion]:
                fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersion + '_' + myField]
                readBytes = self.readLasBytes(fieldProperties[0], warningId='1d')
                self.headBin += readBytes
                self.sumaBytesCabecera += int(fieldProperties[0])
                try:
                    if fieldProperties[1].strip() == 'c':
                        # String
                        # value = readBytes.rstrip(b'\x00')
                        value = readBytes
                    elif int(fieldProperties[2]) > 1:
                        # Array -> desempaquetar a una tupla
                        value = struct.unpack(fieldProperties[2].strip() + fieldProperties[1].strip(), readBytes)
                    else:
                        # Numero binario: guardar el primer elemento de la tupla
                        value = struct.unpack(fieldProperties[1].strip(), readBytes)[0]
                except:
                    printMsg('clidhead-> LasHeadClass-> WARNING w3b')
                    printMsg('Field:', myField)
                    value = readBytes

                if self.verbose:
                    if not self.lasDataMem is None:
                        postPosicion = len(self.headBin)
                    else:
                        postPosicion = self.ficheroLas.tell()
                    printMsg(
                        f'{TB}LASF1.4-{nField:>2}-> Bytes:'
                        + f'\t{postPosicion - int(fieldProperties[0]) + 1:>3}-{postPosicion}'
                        + f'\t{myField:>14}\t{value}'
                    )
                self.headDict[myField] = value
                setattr(self, myField, value)


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def readVariableLengthRecords(self, tipoVLR='normal'):
        if tipoVLR == 'normal':
            propiedadNumVLR = 'numvlrecords'
            grupoLasHeadFields = self.lasVersion + '_vlrecord'
            idTipoVLR = ''
            self.headDict['projection_type'] = ''
            self.headDict['projection_value'] = ''
            self.headDict['VLRhuso'] = 0
            self.headDict['OGCprojectionVLR'] = False
            self.headDict['GeoKeyDirectoryTagVLR'] = False
            self.headDict['GeoDoubleParamsTagVLR'] = False
        elif tipoVLR == 'extended':
            propiedadNumVLR = 'extendedVLRnValues'
            grupoLasHeadFields = self.lasVersion + '_evlrecord'
            idTipoVLR = 'extended_'
            if not self.lasDataMem is None:
                #TODO: avanzo en el fichero leyendo bytes que no uso. Pte revisar.
                # Ver https://laspy.readthedocs.io/en/latest/tut_part_3.html:
                #  EVLRS work very much the same way as traditional VLRs, though they are stored in a different part of the file.
                # Ver https://pdal.io/tutorial/las.html#variable-length-records:
                #  For LAS 1.0-1.3, the VLR length could be no larger than 65535 bytes. Version 1.4 introduced extended VLRs, stored at the end of the file, which could be up to 4gb in size.
                prePosicion = len(self.headBin)
                readBytes = self.ficheroLas[prePosicion: prePosicion+int(self.extendedVLRstart)]
            else:
                self.ficheroLas.seek(self.extendedVLRstart)
            '''
            extendedVLRstart = 8, Q, 1
                Start of First Extended Variable Length Record:  This value provides the offset, in bytes, from 
                the beginning of the LAS file to the first byte of the first EVLR.   
            extendedVLRnValues = 4, L, 1
                Number of Extended Variable Length Records: This field contains the current number of 
                EVLRs (including, if present, the Waveform Data Packet Record) that are stored in the file after 
                the Point Data Records. This number must be updated if the number of EVLRs changes.  If there 
                are no EVLRs this value is zero.       
            '''

        if self.verbose:
            if self.lasDataMem is None:
                printMsg(f'{TB}-> LasHeadClass-> Modalidad de lectura del fichero laz/las: lectura de fichero con read()')
            else:
                printMsg(f'{TB}-> LasHeadClass-> Modalidad de lectura del fichero laz/las: lectura de lasDataMem con acceso por puntero')
                printMsg(f'{TB}{TV}-> lasDataMem es un <bytes> generado al descomprimir el laz y luego convertido a <memoryview> (self.ficheroLas)')
                printMsg(f'{TB}{TV}-> La lectura se hace accediendo al <memoryview> (self.ficheroLas) y agegando el trozo leido (readMemView) a un <bytes> (self.headBin)')
                # self.lasDataMem: <class 'bytes'>
                # self.ficheroLas: <class 'memoryview'>
                # readMemView: <class 'memoryview'>
                # self.headBin: <class 'bytes'>
                printMsg(f'{TB}{TV}-> type(self.lasDataMem): {type(self.lasDataMem)}, type(self.ficheroLas): {type(self.ficheroLas)}')
                printMsg(f'{TB}{TV}-> type(self.headBin): {type(self.headBin)}, len(self.headBin): {len(self.headBin)}')

        self.sumaBytesVLR = 0
        if self.headDict[propiedadNumVLR] > 0:
            if self.verbose:
                printMsg(f'\nclidhead-> LasHeadClass-> Numero de variable lenght records de tipo {tipoVLR}: {self.headDict[propiedadNumVLR]}')
                # print('clidhead-> LasHeadClass-> self.lasHeaderFieldListVersionsDict.keys():', self.lasHeaderFieldListVersionsDict.keys())
                printMsg(f'{TB}-> Campos de LasFormat_1_2_vlrecord: {self.lasHeaderFieldListVersionsDict[grupoLasHeadFields]}')

            for nVlrecord in range(self.headDict[propiedadNumVLR]):
                if self.verbose:
                    printMsg(f'{TB}-> Leyendo vlrecord {nVlrecord}:')

                LASFprojectionVLR = False
                OGCprojectionVLR = False
                GeoKeyDirectoryTagVLR = False
                GeoDoubleParamsTagVLR = False
                if True:
                # try:
                    for nField, myField in enumerate(self.lasHeaderFieldListVersionsDict[grupoLasHeadFields]):
                        # Reserved = 2, H, 1
                        # UserID = 16, c, 16
                        # RecordID = 2, H, 1
                        # RecordLengthAfterHeader = 2, H, 1
                        # Description = 32, c, 32
                        fieldProperties = self.lasHeaderFieldPropertiesDict[self.lasVersion + '_vlrecord_' + myField]
                        if not self.lasDataMem is None:
                            prePosicion = len(self.headBin)
                            readMemView = self.ficheroLas[prePosicion: prePosicion+int(fieldProperties[0])]
                            # Comvierto el fragmento elegido (<memoryview>) a <bytes> para luego poder aplicarle rstrip(), etc.
                            readBytes = b'' + readMemView
                        else:
                            prePosicion = self.ficheroLas.tell()
                            readBytes = self.ficheroLas.read(int(fieldProperties[0]))
                        self.headBin += readBytes
                        self.sumaBytesVLR += int(fieldProperties[0])
                        self.sumaBytesCabecera += int(fieldProperties[0])
                        if not self.lasDataMem is None:
                            postPosicion = len(self.headBin)
                        else:
                            postPosicion = self.ficheroLas.tell()

                        if True:
                        # try:
                            if fieldProperties[1].strip() == 'c':
                                # String
                                # value = readBytes.rstrip(b'\x00')
                                # if not self.lasDataMem is None:
                                #     value = readBytes.decode('latin-1')
                                # else:
                                value = readBytes.rstrip(b'\x00').decode('latin-1')
                            elif int(fieldProperties[2]) > 1:
                                # Array -> desempaquetar a una tupla
                                value = struct.unpack(fieldProperties[2].strip() + fieldProperties[1].strip(), readBytes)
                            else:
                                # Numero binario: guardar el primer elemento de la tupla
                                value = struct.unpack(fieldProperties[1].strip(), readBytes)[0]
                        # except:
                        #     printMsg('clidhead-> LasHeadClass-> WARNING w4a')
                        #     printMsg('Field: {}'.format(myField))
                        #     value = readBytes

                        if self.verbose:
                            printMsg(
                                f'{TB}{TV}VLR{nVlrecord}-{nField:>2}-> Bytes:'
                                + f'\t{prePosicion:>3}-{postPosicion};'
                                + f'\tTipoVLR: {tipoVLR};'
                                + f'\tNombreVLR: {myField:<24}\tValor: {value}'
                            )
                        self.headDict['%s%s_%i' % (idTipoVLR, myField, nVlrecord)] = value
                        setattr(self, '%s%s_%i' % (idTipoVLR, myField, nVlrecord), value)
                        # self.headDict['textoVRL_%i' % nVlrecord] = value

                        if myField == 'UserID' and value == 'LASF_Projection':
                            LASFprojectionVLR = True
                        if LASFprojectionVLR and myField == 'Description':
                            if (
                                value == 'OGC Transformation Record'
                                or value == 'OGC COORDINATE SYSTEM WKT'
                                or 'OGC' in value
                            ):
                                OGCprojectionVLR = True
                            elif (
                                'GeoKeyDirectoryTag' in value
                            ):
                                GeoKeyDirectoryTagVLR = True
                            elif (
                                'GeoDoubleParamsTag' in value
                            ):
                                GeoDoubleParamsTagVLR = True
                    if self.verbose:
                        print(f'{TB}{TV}-> LasHeadClass-> Variable lenght record num: {nVlrecord} leido ok')
                # except:
                #     printMsg('clidhead-> LasHeadClass-> WARNING w4b')
                #     printMsg('Ha habido un problema al leer el vlrecord {}'.format(nVlrecord))
                #     if not self.lasDataMem is None:
                #         postPosicion = len(self.headBin)
                #     else:
                #         postPosicion = self.ficheroLas.tell()
                #     printMsg('Position:' + '\t' + str(postPosicion))
                #     printMsg('Se cierra la aplicacion')
                #     sys.exit()
                lengthAfterHeader = int(self.headDict['%s_%i' % ('RecordLengthAfterHeader', nVlrecord)])
                if not self.lasDataMem is None:
                    prePosicion = len(self.headBin)
                    readBytes = self.ficheroLas[prePosicion: prePosicion + int(lengthAfterHeader)]
                else:
                    prePosicion = self.ficheroLas.tell()
                    readBytes = self.ficheroLas.read(int(lengthAfterHeader))
                self.headBin += readBytes
                self.sumaBytesVLR += int(lengthAfterHeader)
                self.sumaBytesCabecera += int(lengthAfterHeader)
                self.headDict['%sVRL_%i' % (idTipoVLR, nVlrecord)] = readBytes
                setattr(self, '%sVRL_%i' % (idTipoVLR, nVlrecord), value)

                if self.verbose:
                    printMsg(f'{TB}{TV}-> Parte variable (contenido) del vlrecord {nVlrecord}: {readBytes}')

                if LASFprojectionVLR:
                    if OGCprojectionVLR:
                        self.headDict['OGCprojectionVLR'] = True
                        self.headDict['projection_type'] = 'OGC Transformation Record'
                        self.headDict['projection_value'] = readBytes
                        if '["EPSG","25830"]' in str(readBytes):
                            self.headDict['VLRhuso'] = 30
                            # self.VLRhuso = 30
                        elif '["EPSG","25829"]' in str(readBytes):
                            self.headDict['VLRhuso'] = 29
                        else:
                            self.headDict['VLRhuso'] = 0
                            # self.VLRhuso = 29
                    elif GeoKeyDirectoryTagVLR and not OGCprojectionVLR:
                        self.headDict['GeoKeyDirectoryTagVLR'] = True
                        print('clidhead-> Aviso: el sistema de referencia es de tipo GeoKeyDirectoryTag y por el momento no ha salido uno del tipo OGC WKT.')
                    elif GeoDoubleParamsTagVLR and not OGCprojectionVLR:
                        self.headDict['GeoDoubleParamsTagVLR'] = True
                        print('clidhead-> Aviso: el sistema de referencia es de tipo GeoDoubleParamsTag y por el momento no ha salido uno del tipo OGC WKT.')
                    else:
                        print('clidhead-> Aviso: VLR con projection type no implementada.')
        else:
            self.headDict['Reserved'] = 0
            self.headDict['UserID'] = ''
            self.headDict['RecordID'] = 0
            self.headDict['RecordLengthAfterHeader'] = 0
            self.headDict['Description'] = b'No Variable Lenght Records (VRL)'
            self.headDict['VRL'] = b'No VRL'

            self.headDict['Reserved_0'] = 0
            self.headDict['UserID_0'] = ''
            self.headDict['RecordID_0'] = 0
            self.headDict['RecordLengthAfterHeader_0'] = 0
            self.headDict['Description_0'] = 'No Variable Lenght Records (VRL)'
            self.headDict['VRL_0'] = b'No VRL'
            # self.headDict['textoVRL_0'] = 'No VRL'
            if self.verbose:
                printMsg(f'clidhead-> LasHeadClass-> No hay vlrecords de tipo {tipoVLR}')


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def readLasBytes(self, nBytes, warningId=''):
        # prePosicion = self.ficheroLas.tell() # AttributeError: 'memoryview' object has no attribute 'tell'
        if not self.lasDataMem is None:
            prePosicion = len(self.headBin)
            readBytes = bytes(self.ficheroLas[prePosicion: prePosicion + int(nBytes)])
        else:
            readBytes = self.ficheroLas.read(int(nBytes))
#         try:
#             readBytes = self.ficheroLas.read(int(nBytes))
#         except:
#             print('clidhead-> LasHeadClass-> WARNING %s' % warningId)
#             print('clidhead-> LasHeadClass-> There has been a problem reading las file header')
#             if not self.lasDataMem is None:
#                 postPosicion = len(self.headBin)
#             else:
#                 postPosicion = self.ficheroLas.tell()
#             print('clidhead-> LasHeadClass-> Position:', postPosicion)
#             self.ficheroLas.close()
#             sys.exit()
        return readBytes


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def calculaRedondeaCoordenadasBloqueDeLaCabecera(self):
        """
        Se leen las coordenadas de la cabecera (guardadas en float)
        """
        self.xminBloqueMalla = self.headDict['xminBloqueMalla']
        self.xmaxBloqueMalla = self.headDict['xmaxBloqueMalla']
        self.yminBloqueMalla = self.headDict['yminBloqueMalla']
        self.ymaxBloqueMalla = self.headDict['ymaxBloqueMalla']
        # Si las coordenadas redondeadas al metro se corresponden
        # con las dimensiones del bloque completo, se ajusta a esas dimensiones
        if self.verbose or (
            (
                round(self.xminBloqueMalla, 0) == round(self.xmaxBloqueMalla - GLO.GLBLmetrosBloque, 0) and (
                    self.xminBloqueMalla != round(self.xminBloqueMalla, 0) or self.xmaxBloqueMalla != self.xminBloqueMalla + GLO.GLBLmetrosBloque
                )
            ) or (
                round(self.yminBloqueMalla, 0) == round(self.ymaxBloqueMalla - GLO.GLBLmetrosBloque, 0) and (
                    self.ymaxBloqueMalla != round(self.ymaxBloqueMalla, 0) or self.yminBloqueMalla != self.ymaxBloqueMalla - GLO.GLBLmetrosBloque
                )
            )
        ):
            print(f'\nclidhead-> Revisando si es necesario redondear los valores xmin, xmax, ymin, ymax de la cabecera')
            print(f'{TB}para que se correspondan con la dimension nominal del bloque ({GLO.GLBLmetrosBloque}):')
        seHanCorregidoRedondeadoEsquinas = False
        if round(self.xminBloqueMalla, 0) == round(self.xmaxBloqueMalla - GLO.GLBLmetrosBloque, 0):
            if self.xminBloqueMalla != round(self.xminBloqueMalla, 0):
                print(f'{TB}-> Aviso: se corrige el valor de xmin de la cabecera de {self.xminBloqueMalla:0.2f} a {round(self.xminBloqueMalla, 0):0.2f} (round(xmin, 0))')
                self.xminBloqueMalla = round(self.xminBloqueMalla, 0)
                seHanCorregidoRedondeadoEsquinas = True
            if self.xmaxBloqueMalla != self.xminBloqueMalla + GLO.GLBLmetrosBloque:
                print(f'{TB}-> Aviso: se corrige el valor de xmax de la cabecera de {self.xmaxBloqueMalla:0.2f} a {self.xminBloqueMalla + GLO.GLBLmetrosBloque:0.2f} (xmin + GLBLmetrosBloque)')
                self.xmaxBloqueMalla = self.xminBloqueMalla + GLO.GLBLmetrosBloque
                # self.headDict['xmaxBloqueMalla'] = self.xmaxBloqueMalla
                seHanCorregidoRedondeadoEsquinas = True
        if round(self.yminBloqueMalla, 0) == round(self.ymaxBloqueMalla - GLO.GLBLmetrosBloque, 0):
            if self.ymaxBloqueMalla != round(self.ymaxBloqueMalla, 0):
                print(f'{TB}-> Aviso: se corrige el valor de ymax de la cabecera de {self.ymaxBloqueMalla:0.2f} a {round(self.ymaxBloqueMalla, 0):0.2f} (round(ymax, 0))')
                self.ymaxBloqueMalla = round(self.ymaxBloqueMalla, 0)
                seHanCorregidoRedondeadoEsquinas = True
            if self.yminBloqueMalla != self.ymaxBloqueMalla - GLO.GLBLmetrosBloque:
                print(f'{TB}-> Aviso: se corrige el valor de ymin de la cabecera de {self.yminBloqueMalla:0.2f} a {self.ymaxBloqueMalla - GLO.GLBLmetrosBloque:0.2f} (ymax - GLBLmetrosBloque)')
                self.yminBloqueMalla = self.ymaxBloqueMalla - GLO.GLBLmetrosBloque
                # self.headDict['yminBloqueMalla'] = self.yminBloqueMalla
                seHanCorregidoRedondeadoEsquinas = True

        if self.verbose:
            if not seHanCorregidoRedondeadoEsquinas:
                print(f'{TB}-> No es necesario corregir: xmin, xmax, ymin, ymax cuadran con la dimension nominal del bloque.')
            print(f'clidhead-> Posteriormente se chequea si los limites cuadran con la malla satelital de referencia (checkLasfile<>).')


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def checkLasfile(self, LCLverbose=False):

        # ======================================================================
        if self.pointreclen == 0:
            nBytesAcum = 0
            for propiedad in self.lasPointFieldPropertiesList:
                nBytesAcum += propiedad[1]
            self.pointreclen = nBytesAcum
        # ======================================================================

        # # ======================================================================
        # if self.pointformat == 1 and self.pointreclen == 34:
        #     print(f'clidhead-> ATENCION: la cabecera indica pointformat 1 y pointreclen 34')
        #     print(f'{TB}-> Se da credibilidad a pointreclen e interpreta como error de pointformat, que puede ser 3. Se cambia a este valor')
        #     self.pointformat = 3
        # # ======================================================================

        # ======================================================================
        if self.metersBlock > 0:
            if not 'PASADAS' in GLO.MAINprocedimiento and (
                (self.xmaxBloqueMalla - self.xminBloqueMalla) > self.metersBlock + (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
                or (self.ymaxBloqueMalla - self.yminBloqueMalla) > self.metersBlock + (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
            ):
                # if self.coordenadasTransformadasDe29a30:
                if LCLverbose:
                    print('{:_^80}'.format(''))
                    print(f'clidhead.{self.fileCoordYeahDelNombre}:')
                    if (
                        (self.xmaxBloqueMalla - self.xminBloqueMalla) > self.metersBlock * 2
                        or (self.ymaxBloqueMalla - self.yminBloqueMalla) > self.metersBlock * 2
                    ):
                        if 'LAS_INFO' in GLO.MAINprocedimiento:
                            tipoAdvertencia = 'AVISO'
                        else:
                            tipoAdvertencia = 'ATENCION'
                        print(f'{TB}-> checkLasfile-> {tipoAdvertencia}: el rango de coordenadas del fichero lidar es superior al doble de la dimension del bloque.')
                        if not 'LAS_INFO' in GLO.MAINprocedimiento:
                            print(f'{TB}-> Revisar si el fichero es correcto y/o cambiar la variable de configuracion GLBLmetrosBloque.')
                    else:
                        if 'LAS_INFO' in GLO.MAINprocedimiento:
                            tipoAdvertencia = 'Aviso'
                        else:
                            tipoAdvertencia = 'Atencion'
                        if self.TRNShuso29_coord:
                            print(f'{TB}-> checkLasfile-> {tipoAdvertencia}: Rango de coordenadas del fichero lidar superior a la dimension del bloque debido a la transformacion de coordenadas de h29 a h30')
                        else:
                            print(f'{TB}-> checkLasfile-> {tipoAdvertencia}: el rango de coordenadas del fichero lidar es superior a la dimension del bloque + 2 veces el margenParaAdmitirPuntos pero no llega al doble de la dimension del bloque.')
                            if not 'LAS_INFO' in GLO.MAINprocedimiento:
                                print(f'{TB}-> Revisar si el fichero es correcto y/o cambiar la variable de configuracion GLBLmetrosBloque.')
                    print(
                        f'{TB}{TV}->', round((self.xmaxBloqueMalla - self.xminBloqueMalla), 2),
                        '>', self.metersBlock, '+ 4 *', GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque,
                        'y/o', round((self.ymaxBloqueMalla - self.yminBloqueMalla), 2),
                        '>', self.metersBlock, '+ 4 *', GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque,
                    )
                    print(f'{TB}{TV}{TV}-> self.xminBloqueMalla: {round(self.xminBloqueMalla, 2)}')
                    print(f'{TB}{TV}{TV}-> self.yminBloqueMalla: {round(self.yminBloqueMalla, 2)}')
                    print(f'{TB}{TV}{TV}-> self.xmaxBloqueMalla: {round(self.xmaxBloqueMalla, 2)}')
                    print(f'{TB}{TV}{TV}-> self.ymaxBloqueMalla: {round(self.ymaxBloqueMalla, 2)}')
                # if not self.coordenadasTransformadasDe29a30:
                if not self.TRNShuso29_coord:
                    if LCLverbose:
                        print('clidhead-> checkLasfile-> Se puede cambiar GLBLmetrosBloque a', math.ceil(max(self.ymaxBloqueMalla - self.yminBloqueMalla, self.xmaxBloqueMalla - self.xminBloqueMalla)), 'metros')
                    if not GLO.GLBLadmitirBloquesMayoresQueMetrosBloque:
                        print('\tSe cierra la aplicacion para cambiar manualmente GLBLmetrosBloque en el fichero de configuracion')
                        sys.exit(0)
                if LCLverbose:
                    print('{:=^80}'.format(''))
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

        # Se ajustan, si procede, self.xminBloqueMalla, self.xmaxBloqueMalla, self.ymaxBloqueMalla, self.yminBloqueMalla
        if (
            'LAS_INFO' in GLO.MAINprocedimiento
            or 'LAS_EDIT' in GLO.MAINprocedimiento
            or 'PASADAS' in GLO.MAINprocedimiento
        ):
            self.LCLmetrosBloqueX = self.metersBlock
            self.LCLmetrosBloqueY = self.metersBlock
        else:
            if GLO.GLBLcoordMinMaxAcordesConBloque:
                # Redondear los valores de las coordenadas de las esquinas del bloque 
                # a un multiplo de la dimension del bloque siempre que el desvio sea inferior a 20 m y el huso se H30.
                # Este ajuste solo se mantiene si la malla satelital cuadra con las esquinas del bloque.
                # En caso contrario, el ajuste que prevalece es el de adjustCornersCoordinatesCelda<>
                self.adjustCornersCoordinatesBloque(
                    self.metersBlock,
                    margenAdmisible=self.metersBlock * 0.01
                )

        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        if self.metersBlock == 0:
            if round(self.metersBlockX, 2) != round(self.metersBlockY, 2):
                print('clidhead-> checkLasfile-> AVISO: bloque no cuadrado. x: %0.2f; y: %0.2f' % (self.metersBlockX, self.metersBlockY))
        if self.metersCell > 0 and self.metersBlock % self.metersCell != 0:
            print('clidhead-> checkLasfile-> AVISO: la dimension del bloque no es multiplo de la de la celda. Bloque: %0.2f m; Celda: %0.2f m.' % (self.metersBlock, self.metersCell))
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

        if self.TRNShuso29:
            LCLorigenDeCoordenadasX = GLO.GLBLorigenDeCoordenadasH29X
            LCLorigenDeCoordenadasY = GLO.GLBLorigenDeCoordenadasH29Y
        else:
            LCLorigenDeCoordenadasX = GLO.GLBLorigenDeCoordenadasH30X
            LCLorigenDeCoordenadasY = GLO.GLBLorigenDeCoordenadasH30Y

        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        # Se ajustan, si procede, self.xminBloqueMalla, self.xmaxBloqueMalla, self.ymaxBloqueMalla, self.yminBloqueMalla
        # y se asigna a self.xSupIzda, self.xInfDcha, self.ySupIzda, self.yInfDcha
        # if (
        #     (self.xminBloqueMalla % self.metersCell < 0.9 and self.xminBloqueMalla % self.metersCell > 0)
        #     or self.xmaxBloqueMalla % self.metersCell >= 0.1
        #     or (self.yminBloqueMalla % self.metersCell < 0.9 and self.yminBloqueMalla % self.metersCell > 0)
        #     or self.ymaxBloqueMalla % self.metersCell >= 0.1
        # ):
        #     envolvente = True
        # else:
        #     envolvente = False
        # Para ajustar de la malla de celdas a la del satelite uso GLBLforzarExtensionDeCeldasDentroDelBloque
        # De todas formas mantengo los parametros TRNSpermitirQueLaMallaExcedaElBloque por si acaso
        TRNSpermitirQueLaMallaExcedaElBloqueX = True
        TRNSpermitirQueLaMallaExcedaElBloqueY = True
        if (
            'LAS_INFO' in GLO.MAINprocedimiento
            or 'LAS_EDIT' in GLO.MAINprocedimiento
            or 'PASADAS' in GLO.MAINprocedimiento
        ):
            self.xSupIzda = self.xminBloqueMalla
            self.xInfDcha = self.xmaxBloqueMalla
            self.yInfDcha = self.yminBloqueMalla
            self.ySupIzda = self.ymaxBloqueMalla
        else:
            self.adjustCornersCoordinatesCelda(
                self.metersCell,
                TRNSpermitirQueLaMallaExcedaElBloqueX=TRNSpermitirQueLaMallaExcedaElBloqueX,
                TRNSpermitirQueLaMallaExcedaElBloqueY=TRNSpermitirQueLaMallaExcedaElBloqueY,
                margenAdmisible=self.metersCell * 0.1,
                LCLorigenDeCoordenadasX=LCLorigenDeCoordenadasX,
                LCLorigenDeCoordenadasY=LCLorigenDeCoordenadasX,
            )

        self.LCLmetrosBloqueX = self.xmaxBloqueMalla - self.xminBloqueMalla
        self.LCLmetrosBloqueY = self.ymaxBloqueMalla - self.yminBloqueMalla
        self.nCeldasX = math.ceil(self.LCLmetrosBloqueX / GLO.GLBLmetrosCelda) #  type int
        self.nCeldasY = math.ceil(self.LCLmetrosBloqueY / GLO.GLBLmetrosCelda) #  type int
        if (
            not 'LAS_INFO' in GLO.MAINprocedimiento
            and not 'LAS_EDIT' in GLO.MAINprocedimiento
            and not 'PASADAS' in GLO.MAINprocedimiento
        ):
            if self.LCLmetrosBloqueX % GLO.GLBLmetrosCelda != 0:
                printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> ATENCION-> No se ha hecho bien el ajuste de las celdas a la malla satelital en X:')
                printMsg(f'{TB} rango X: {self.xminBloqueMalla} - {self.xmaxBloqueMalla} -> {self.LCLmetrosBloqueX}; malla: {GLO.GLBLmetrosCelda}; resto: {self.LCLmetrosBloqueX % GLO.GLBLmetrosCelda}')
                printMsg(f'{TB} Se adopta un numero de celdas redondeado al alza para incluir todos los puntos-> nCeldasX: {self.nCeldasX}')
            if self.LCLmetrosBloqueX % GLO.GLBLmetrosCelda != 0:
                printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> ATENCION-> No se ha hecho bien el ajuste de las celdas a la malla satelital en Y:')
                printMsg(f'{TB} rango Y: {self.yminBloqueMalla} - {self.ymaxBloqueMalla} -> {self.LCLmetrosBloqueY}; malla: {GLO.GLBLmetrosCelda}; resto: {self.LCLmetrosBloqueY % GLO.GLBLmetrosCelda}')
                printMsg(f'{TB} Se adopta un numero de celdas redondeado al alza para incluir todos los puntos-> nCeldasY: {self.nCeldasY}')

            if self.verbose:
                if GLO.GLBLforzarExtensionDeBloqueAvalorNominal and self.LCLforzarExtensionDeBloqueAvalorNominal:
                    printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> checkLasfile-> Coordenadas del lasfile segun fileName despues de adjustCornersCoordinates a celda (=malla satelital):')
                    printMsg(f'{TB}-> myLasName.xminBloqueMalla: {self.xminBloqueMalla}')
                    printMsg(f'{TB}-> myLasName.xmaxBloqueMalla: {self.xmaxBloqueMalla}')
                    printMsg(f'{TB}-> myLasName.yminBloqueMalla: {self.yminBloqueMalla}')
                    printMsg(f'{TB}-> myLasName.ymaxBloqueMalla: {self.ymaxBloqueMalla}')
                else:
                    printMsg(f'clidhead.{self.fileCoordYeahDelNombre}-> checkLasfile-> Coordenadas del lasfile segun cabecera despues de adjustCornersCoordinates a celda (=malla satelital):')
                    printMsg(f'{TB}-> myLasHead.xminBloqueMalla: {self.xminBloqueMalla}')
                    printMsg(f'{TB}-> myLasHead.xmaxBloqueMalla: {self.xmaxBloqueMalla}')
                    printMsg(f'{TB}-> myLasHead.yminBloqueMalla: {self.yminBloqueMalla}')
                    printMsg(f'{TB}-> myLasHead.ymaxBloqueMalla: {self.ymaxBloqueMalla}')
                printMsg(f'{TB}-> GLBLforzarExtensionDeCeldasDentroDelBloque: {GLO.GLBLforzarExtensionDeCeldasDentroDelBloque}')
                printMsg(f'{TB}-> TRNSpermitirQueLaMallaExcedaElBloqueXY:     {TRNSpermitirQueLaMallaExcedaElBloqueX} {TRNSpermitirQueLaMallaExcedaElBloqueY}')

            if self.verbose:
                print(f'clidhead-> checkLasfile-> Numero de celdas ajustado a la malla (GLBLmetrosCelda: {GLO.GLBLmetrosCelda} m): {self.nCeldasX} x {self.nCeldasY} celdas.')
            
        self.metrosBloqueX = self.nCeldasX * GLO.GLBLmetrosCelda
        self.metrosBloqueY = self.nCeldasY * GLO.GLBLmetrosCelda
        if self.verbose:
            print(f'clidhead-> checkLasfile-> Dimension del bloque ajustado: {self.metrosBloqueX} x {self.metrosBloqueY} metros')

        if GLO.GLBLforzarExtensionDeBloqueAvalorNominal and self.LCLforzarExtensionDeBloqueAvalorNominal:
            self.xmaxBloqueMalla = self.xminBloqueMalla + self.metrosBloqueX
            self.yminBloqueMalla = self.ymaxBloqueMalla - self.metrosBloqueY
        # ======================================================================

        # ======================================================================
        nBytesPorPuntoCheck = sum(int(pointField[1]) for pointField in self.lasPointFieldPropertiesList)
        if nBytesPorPuntoCheck != self.pointreclen:
            print(
                'clidhead-> checkLasfile-> ATENCION: revisar nBytesPorPunto: El valor normal para P.F. {} es {} bytes pero la cabecera dice {} bytes'.format(
                    self.pointformat,
                    nBytesPorPuntoCheck,
                    self.pointreclen
                )
            )
            print(
                f'{TB}-> Se usa el valor indicado en la cabecera ({self.pointreclen}),'
                f' pero no se interpretan los bytes de cada punto despues del byte ({nBytesPorPuntoCheck})'
            )
            self.pointreclenASPRS = nBytesPorPuntoCheck
        # ======================================================================

        # inputfile_las_baseName = os.path.splitext(os.path.basename(inputfile_las))[0] #Nombre sin extension
        # printMsg('clidhead-> checkLasfile-> Procesando sin liblas: %s' % (inputfile_las_baseName))

        if self.verbose:
            if self.headDict['numvlrecords'] == 0:
                print('\nclidhead-> checkLasfile-> La informacion del srs en el fichero las debe estar en formato compatible con: %s' % self.formatoSRS)
            else:
                print('\nclidhead-> checkLasfile-> La informacion del srs en el fichero las debe estar en formato compatible con: %s' % self.formatoSRS)
                if 'Description_0' in self.headDict.keys() and self.headDict['Description_0'].rstrip('\x00') == 'No Variable Lenght Records (VRL)':
                    print(f'{TB}{self.headDict["Description_0"]}')
                else:
                    printMsg(
                        f'{TB}Campos de LasFormat_1_2_vlrecord:',
                        str(self.lasHeaderFieldListVersionsDict[self.lasVersion + "_vlrecord"])
                    )
                    for nVlrecord in range(self.headDict['numvlrecords']):
                        print(f'{TB}{TV}Info de Variable Lenght Records (VRL) {nVlrecord}')
                        for myField in self.lasHeaderFieldListVersionsDict[self.lasVersion + '_vlrecord']:
                            fieldname = '%s_%i' % (myField, nVlrecord)
                            value = str(self.headDict[fieldname])
                            # value = self.headDict['textoVRL_%i' % nVlrecord]
                            print(f'{TB}{TV}{TV}------> {fieldname.rjust(25)} -> {value}')
            print('clidhead-> checkLasfile-> Las file creado con el software: %s' % str(self.headDict['gensoftware']))


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def adjustCornersCoordinatesBloque(
            self,
            sizeToAdjust,
            margenAdmisible=1,
        ):
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        if self.TRNShuso29_coord:
            self.LCLmetrosBloqueX = self.metersBlock
            self.LCLmetrosBloqueY = self.metersBlock
        else:
            if (
                (self.xmaxBloqueMalla - self.xminBloqueMalla) >= self.metersBlock - margenAdmisible
                and (self.ymaxBloqueMalla - self.yminBloqueMalla) >= self.metersBlock - margenAdmisible
                and (self.xmaxBloqueMalla - self.xminBloqueMalla) < self.metersBlock + margenAdmisible
                and (self.ymaxBloqueMalla - self.yminBloqueMalla) < self.metersBlock + margenAdmisible
            ):
                # dimensionDeBloqueOk = True
                self.xminBloqueMalla = float(sizeToAdjust * round((self.xminBloqueMalla) / sizeToAdjust, 0))
                self.xmaxBloqueMalla = float(sizeToAdjust * round((self.xmaxBloqueMalla) / sizeToAdjust, 0))
                self.yminBloqueMalla = float(sizeToAdjust * round((self.yminBloqueMalla) / sizeToAdjust, 0))
                self.ymaxBloqueMalla = float(sizeToAdjust * round((self.ymaxBloqueMalla) / sizeToAdjust, 0))
                self.LCLmetrosBloqueX = GLO.GLBLmetrosBloque
                self.LCLmetrosBloqueY = GLO.GLBLmetrosBloque

            # if GLO.GLBLcoordMinMaxAcordesConBloque:
            #     # El lasFile se ajusta +- a la dimension prevista por GLBLmetrosBloque
            #     if (self.xmaxBloqueMalla - self.xminBloqueMalla) > self.metersBlock:
            #         TRNSpermitirQueLaMallaExcedaElBloqueX = False
            #     else:
            #         TRNSpermitirQueLaMallaExcedaElBloqueX = True
            #     if (self.ymaxBloqueMalla - self.yminBloqueMalla) > self.metersBlock:
            #         TRNSpermitirQueLaMallaExcedaElBloqueY = False
            #     else:
            #         TRNSpermitirQueLaMallaExcedaElBloqueY = True
            #     self.adjustCornersCoordinates(
            #         self.metersBlock,
            #         TRNSpermitirQueLaMallaExcedaElBloqueX=TRNSpermitirQueLaMallaExcedaElBloqueX,
            #         TRNSpermitirQueLaMallaExcedaElBloqueY=TRNSpermitirQueLaMallaExcedaElBloqueY,
            #         margenAdmisible=self.metersBlock * 0.01
            #         LCLorigenDeCoordenadasX=0,
            #         LCLorigenDeCoordenadasY=0,
            #     )
            #     self.LCLmetrosBloqueX = GLO.GLBLmetrosBloque
            #     self.LCLmetrosBloqueY = GLO.GLBLmetrosBloque
            #     if self.verbose:
            #         print('\nclidhead-> LasHeadClass-> 1 Adjusting corners with block size:', self.metersBlock, 'm')
            #         print('clidhead-> LasHeadClass->   xmin, xmax, ymin, ymax:', self.xminBloqueMalla, self.xmaxBloqueMalla, self.yminBloqueMalla, self.ymaxBloqueMalla)
            #         print(f'clidhead-> LasHeadClass->   TRNSpermitirQueLaMallaExcedaElBloqueX: {TRNSpermitirQueLaMallaExcedaElBloqueX}; TRNSpermitirQueLaMallaExcedaElBloqueY: {TRNSpermitirQueLaMallaExcedaElBloqueY}')
            # elif (
            #     (self.xmaxBloqueMalla - self.xminBloqueMalla) >= self.metersBlock + (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
            #     or (self.ymaxBloqueMalla - self.yminBloqueMalla) >= self.metersBlock + (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
            # ):
            #     if LCLverbose:
            #         print('clidhead-> LasHeadClass-> Alguna dimension del lasFile es superior al GLBLmetrosBloque (establecido en el fichero de configuracion)')
            #         print(f'{TB}-> Valor actual de GLBLmetrosBloque:', GLO.GLBLmetrosBloque, 'm.')
            #         print(f'{TB}-> Rango de coord x:', (self.xmaxBloqueMalla - self.xminBloqueMalla), 'Rango de coord y:', (self.ymaxBloqueMalla - self.yminBloqueMalla))
            #         if GLO.MAIN_ENTORNO == 'windows':
            #             selec = input('Seguir adelante con el valor actual de GLBLmetrosBloque (S/n)')
            #             rptaMantener = False if selec.upper() == 'N' else True
            #             if not rptaMantener:
            #                 print('clidhead-> Se cierra la aplicacion para cambiar manualmente GLBLmetrosBloque en el fichero de configuracion')
            #                 print('{:=^80}'.format(' Fin - revisar errores '))
            #                 sys.exit(0)
            else:
                # dimensionDeBloqueOk = False
                if self.verbose:
                    print('{:!^80}'.format(''))
                    print('clidhead-> LasHeadClass-> Aviso: el rango de coordenadas del lasFile es inferior a la dimension del bloque (dimension -lado- estandar de fichero lidar):')
                    print(f'{TB}-> Si ocurre con todos los ficheros, cambiar la variable de configuracion GLBLmetrosBloque en el fichero de configuracion o usar otro fichero las')
                    print('{:!^80}'.format(''))
                    print('\tself.xminBloqueMalla: {:0.2f}'.format(self.xminBloqueMalla))
                    print('\tself.xmaxBloqueMalla: {:0.2f}'.format(self.xmaxBloqueMalla))
                    print('\t\tRango X: {:0.2f}'.format(self.xmaxBloqueMalla - self.xminBloqueMalla, 'metros'))
                    print('\tself.yminBloqueMalla: {:0.2f}'.format(self.yminBloqueMalla))
                    print('\tself.ymaxBloqueMalla: {:0.2f}'.format(self.ymaxBloqueMalla))
                    print('\t\tRango Y: {:0.2f}'.format(self.ymaxBloqueMalla - self.yminBloqueMalla, 'metros'))
                    print(
                        'clidhead-> LasHeadClass-> La aplicacion esta configurada para procesar ficheros lidar (las) de',
                        self.metersBlock,
                        'x',
                        self.metersBlock,
                        'metros (variables de configuracion en el fichero de configuracion)',
                    )
                if min(self.xmaxBloqueMalla - self.xminBloqueMalla, self.ymaxBloqueMalla - self.yminBloqueMalla) < 500:
                    rptaCambiar = True
                    print(f'clidhead-> LasHeadClass-> Bloque con menos de 500 m en alguna dimension:')
                    print('\tSe recomienda usar ficheros lidar de mas de 500 x 500 metros')
                    if False:
                        selec = input(
                            'Continuar cambiando para esta ejecucion el parametro GLBLmetrosBloque al nuevo valor %i ? (s/n)'
                            % round(min(self.xmaxBloqueMalla - self.xminBloqueMalla, self.ymaxBloqueMalla - self.yminBloqueMalla), 0)
                        )
                        rptaCambiar = False if selec.upper() == 'N' else True
                        if not rptaCambiar:
                            print('clidhead-> LasHeadClass-> Se finaliza la aplicacion')
                            print('\tSe cierra la aplicacion para cambiar manualmente GLBLmetrosBloque en el fichero de configuracion')
                            print('{:o^80}'.format(' Fin - revisar errores '))
                            sys.exit(0)
                else:
                    print(f'clidhead-> LasHeadClass-> Bloque con menos de {GLO.GLBLmetrosBloque} m en alguna dimension pero mas de 500 m:')
                    rptaCambiar = True
                print(f'                          Rango X: {(self.xmaxBloqueMalla - self.xminBloqueMalla)}')
                print(f'                          Rango Y: {(self.ymaxBloqueMalla - self.yminBloqueMalla)}')

                if rptaCambiar:
                    if GLO.GLBLadapatarMetrosBloque: # False
                        GLBNmetrosBloque = int(GLO.GLBLmetrosCelda * math.ceil(min(self.xmaxBloqueMalla - self.xminBloqueMalla, self.ymaxBloqueMalla - self.yminBloqueMalla) / GLO.GLBLmetrosCelda))
                        if self.verbose:
                            print('clidhead-> LasHeadClass-> Se recomienda cambiar la variable de configuracion GLBLmetrosBloque en el fichero de configuracion')
                            print('\tSe modifica para esta ejecucion el parametro GLBLmetrosBloque')
                            print('\tSe cambia el parametro GLBLmetrosBloque para esta ejecucion. Nuevo valor:', GLBNmetrosBloque, 'metros.')
                        else:
                            printMsg('\nclidhead-> LasHeadClass-> ATENCION: se cambia el parametro GLBLmetrosBloque para esta ejecucion. Nuevo valor: {} metros'.format(GLBNmetrosBloque))
                        nuevosParametroConfiguracion = {}
                        nuevosParametroConfiguracion['GLBLmetrosBloque'] = [GLBNmetrosBloque, 'GrupoDimensionCeldasBloques', '', 'int']
                        clidconfig.configVarsDict = clidconfig.leerCambiarVariablesGlobales(nuevosParametroConfiguracion)
                        # input('Pulsa una tecla')
                        self.LCLmetrosBloqueX = int(GLO.GLBLmetrosCelda * math.ceil((self.xmaxBloqueMalla - self.xminBloqueMalla) / GLO.GLBLmetrosCelda))
                        self.LCLmetrosBloqueY = int(GLO.GLBLmetrosCelda * math.ceil((self.ymaxBloqueMalla - self.yminBloqueMalla) / GLO.GLBLmetrosCelda))
                    else:
                        print(f'                       -> No se modifica el parametro GLBLmetrosBloque porque GLBLadapatarMetrosBloque es {GLO.GLBLadapatarMetrosBloque}')
                        self.LCLmetrosBloqueX = self.metersBlock
                        self.LCLmetrosBloqueY = self.metersBlock
                else:
                    self.LCLmetrosBloqueX = self.metersBlock
                    self.LCLmetrosBloqueY = self.metersBlock
                if self.verbose:
                    print('{:!^80}\n'.format(''))


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def adjustCornersCoordinatesCelda(
            self,
            sizeToAdjust,
            TRNSpermitirQueLaMallaExcedaElBloqueX=True,
            TRNSpermitirQueLaMallaExcedaElBloqueY=True,
            margenAdmisible=0,
            LCLorigenDeCoordenadasX=0,
            LCLorigenDeCoordenadasY=0,
        ):
        if self.verbose:
            print('clidhead-> HeadClass-> Se ajusta el rango de X e Y del bloque para que haya alineamiento de la malla de celdas con los pixeles satelitales.')
            print(f'{TB}-> Coordenadas de referencia-> X: {LCLorigenDeCoordenadasX} Y: {LCLorigenDeCoordenadasY}')
        if sizeToAdjust > 0:
            # Reviso si hay desfase en X entre la esquina infIzda del bloque y los pixeles del satelite de referencia
            desfaseIzdaX = (self.xminBloqueMalla - LCLorigenDeCoordenadasX) % sizeToAdjust
            desfaseDchaX = (sizeToAdjust - desfaseIzdaX) % sizeToAdjust
            if desfaseIzdaX != 0:
                # Hay desfase en X entre la esquina infIzda del bloque y los pixeles del satelite de referencia
                # Fuerzo a que la malla de celdas quede alineada con los pixeles del satelite de referencia
                if GLO.GLBLforzarExtensionDeCeldasDentroDelBloque or not TRNSpermitirQueLaMallaExcedaElBloqueX:
                    # La malla de celdas queda dentro de las dimensiones del bloque por la izda
                    # self.xminBloqueMalla = self.xminBloqueMalla + desfaseDchaX
                    self.xminBloqueMalla = (
                        LCLorigenDeCoordenadasX
                        + float(sizeToAdjust * math.ceil(
                            (self.xminBloqueMalla - LCLorigenDeCoordenadasX) / sizeToAdjust)
                        )
                    )
                else:
                    # Como me lo permite, eligo el movimiento que menos se aleja de los limites del bloque 
                    if desfaseIzdaX < desfaseDchaX:
                        # La malla de celdas se sale de las dimensiones del bloque por la izda
                        # self.xminBloqueMalla = self.xminBloqueMalla - desfaseIzdaX
                        self.xminBloqueMalla = (
                            LCLorigenDeCoordenadasX
                            + float(sizeToAdjust * math.floor(
                                (self.xminBloqueMalla - LCLorigenDeCoordenadasX + margenAdmisible) / sizeToAdjust)
                            )
                        )
                    else:
                        # La malla de celdas queda dentro de las dimensiones del bloque por la izda
                        # self.xminBloqueMalla = self.xminBloqueMalla + desfaseDchaX
                        self.xminBloqueMalla = (
                            LCLorigenDeCoordenadasX
                            + float(sizeToAdjust * math.ceil(
                                (self.xminBloqueMalla - LCLorigenDeCoordenadasX) / sizeToAdjust)
                            )
                        )
                if self.verbose:
                    print(f'{TB}clidhead-> HeadClass-> Ajustando xmin a la dimension de la celda y malla satelital de {sizeToAdjust} m.')
                    print(f'{TB}{TB}Antes (pre-redondeo):     {self.xminBloqueIni:0.2f}')
                    print(f'{TB}{TB}Ahora (ajustado a malla): {self.xminBloqueMalla:0.2f}')
            # Reviso si hay desfase en X entre la esquina supDcha del bloque y los pixeles del satelite de referencia
            desfaseIzdaX = (self.xmaxBloqueMalla - LCLorigenDeCoordenadasX) % sizeToAdjust
            desfaseDchaX = (sizeToAdjust - desfaseIzdaX) % sizeToAdjust
            if desfaseIzdaX != 0:
                # Hay desfase en X entre la esquina supDcha del bloque y los pixeles del satelite de referencia
                # Fuerzo a que la malla de celdas quede alineada con los pixeles del satelite de referencia
                if GLO.GLBLforzarExtensionDeCeldasDentroDelBloque or not TRNSpermitirQueLaMallaExcedaElBloqueX:
                    # La malla de celdas queda dentro de las dimensiones del bloque por la dcha
                    # self.xmaxBloqueMalla = self.xmaxBloqueMalla - desfaseIzdaX
                    self.xmaxBloqueMalla = (
                        LCLorigenDeCoordenadasX
                        + float(sizeToAdjust * math.floor(
                            (self.xmaxBloqueMalla - LCLorigenDeCoordenadasX + margenAdmisible) / sizeToAdjust)
                        )
                    )
                else:
                    # Como me lo permite, eligo el movimiento que menos se aleja de los limites del bloque 
                    if desfaseIzdaX >= desfaseDchaX:
                        # La malla de celdas se sale de las dimensiones del bloque por la dcha
                        # self.xmaxBloqueMalla = self.xmaxBloqueMalla + desfaseDchaX
                        self.xmaxBloqueMalla = (
                            LCLorigenDeCoordenadasX
                            + float(sizeToAdjust * math.ceil(
                                (self.xmaxBloqueMalla - LCLorigenDeCoordenadasX) / sizeToAdjust)
                            )
                        )
                    else:
                        # La malla de celdas queda dentro de las dimensiones del bloque por la dcha
                        # self.xmaxBloqueMalla = self.xmaxBloqueMalla - desfaseIzdaX
                        self.xmaxBloqueMalla = (
                            LCLorigenDeCoordenadasX
                            + float(sizeToAdjust * math.floor(
                                (self.xmaxBloqueMalla - LCLorigenDeCoordenadasX + margenAdmisible) / sizeToAdjust)
                            )
                        )
                if self.verbose:
                    print(f'{TB}clidhead-> LasHeadClass-> Ajustando xmax a la dimension de la celda y malla satelital de {sizeToAdjust} m.')
                    print(f'{TB}{TB}Antes (pre-redondeo):     {self.xmaxBloqueIni:0.2f}')
                    print(f'{TB}{TB}Ahora (ajustado a malla): {self.xmaxBloqueMalla:0.2f}')

            # Reviso si hay desfase en Y entre la esquina infIzda del bloque y los pixeles del satelite de referencia
            desfaseAbjoY = (self.yminBloqueMalla - LCLorigenDeCoordenadasY) % sizeToAdjust
            desfaseArrbY = (sizeToAdjust - desfaseAbjoY) % sizeToAdjust
            if desfaseAbjoY != 0:
                # Hay desfase en Y entre la esquina infIzda del bloque y los pixeles del satelite de referencia
                # Fuerzo a que la malla de celdas quede alineada con los pixeles del satelite de referencia
                if GLO.GLBLforzarExtensionDeCeldasDentroDelBloque or not TRNSpermitirQueLaMallaExcedaElBloqueY:
                    # La malla de celdas queda dentro de las dimensiones del bloque por la abajo
                    # self.yminBloqueMalla = self.yminBloqueMalla + desfaseArrbY
                    self.yminBloqueMalla = (
                        LCLorigenDeCoordenadasY
                        + float(sizeToAdjust * math.ceil(
                            (self.yminBloqueMalla - LCLorigenDeCoordenadasY) / sizeToAdjust)
                        )
                    )
                else:
                    if desfaseAbjoY < desfaseArrbY:
                        # La malla de celdas se sale de las dimensiones del bloque por la abajo
                        # self.yminBloqueMalla = self.yminBloqueMalla - desfaseAbjoY
                        self.yminBloqueMalla = (
                            LCLorigenDeCoordenadasY
                            + float(sizeToAdjust * math.floor(
                                (self.yminBloqueMalla - LCLorigenDeCoordenadasY + margenAdmisible) / sizeToAdjust)
                            )
                        )
                    else:
                        # La malla de celdas queda dentro de las dimensiones del bloque por la abajo
                        # self.yminBloqueMalla = self.yminBloqueMalla + desfaseArrbY
                        self.yminBloqueMalla = (
                            LCLorigenDeCoordenadasY
                            + float(sizeToAdjust * math.ceil(
                                (self.yminBloqueMalla - LCLorigenDeCoordenadasY) / sizeToAdjust)
                            )
                        )
                if self.verbose:
                    print(f'{TB}clidhead-> HeadClass-> Ajustando ymin a la dimension de la celda y malla satelital de {sizeToAdjust} m.')
                    print(f'{TB}{TB}Antes (pre-redondeo):     {self.yminBloqueIni:0.2f}')
                    print(f'{TB}{TB}Ahora (ajustado a malla): {self.yminBloqueMalla:0.2f}')
            # Reviso si hay desfase en Y entre la esquina supDcha del bloque y los pixeles del satelite de referencia
            desfaseAbjoY = (self.ymaxBloqueMalla - LCLorigenDeCoordenadasY) % sizeToAdjust
            desfaseArrbY = (sizeToAdjust - desfaseAbjoY) % sizeToAdjust
            if desfaseAbjoY != 0:
                # Hay desfase en Y entre la esquina supDcha del bloque y los pixeles del satelite de referencia
                # Fuerzo a que la malla de celdas quede alineada con los pixeles del satelite de referencia
                if GLO.GLBLforzarExtensionDeCeldasDentroDelBloque or not TRNSpermitirQueLaMallaExcedaElBloqueY:
                    # La malla de celdas queda dentro de las dimensiones del bloque por la arriba
                    # self.ymaxBloqueMalla = self.ymaxBloqueMalla - desfaseAbjoY
                    self.ymaxBloqueMalla = (
                        LCLorigenDeCoordenadasY
                        + float(sizeToAdjust * math.floor(
                            (self.ymaxBloqueMalla - LCLorigenDeCoordenadasY + margenAdmisible) / sizeToAdjust)
                        )
                    )
                else:
                    if desfaseAbjoY >= desfaseArrbY:
                        # La malla de celdas se sale de las dimensiones del bloque por la arriba
                        # self.ymaxBloqueMalla = self.ymaxBloqueMalla + desfaseArrbY
                        self.ymaxBloqueMalla = (
                            LCLorigenDeCoordenadasY
                            + float(sizeToAdjust * math.ceil(
                                (self.ymaxBloqueMalla - LCLorigenDeCoordenadasY) / sizeToAdjust)
                            )
                        )
                    else:
                        # La malla de celdas queda dentro de las dimensiones del bloque por la arriba
                        # self.ymaxBloqueMalla = self.ymaxBloqueMalla - desfaseAbjoY
                        self.ymaxBloqueMalla = (
                            LCLorigenDeCoordenadasY
                            + float(sizeToAdjust * math.floor(
                                (self.ymaxBloqueMalla - LCLorigenDeCoordenadasY + margenAdmisible) / sizeToAdjust)
                            )
                        )
                if self.verbose:
                    print(f'{TB}clidhead-> HeadClass-> Ajustando ymax a la dimension de la celda y malla satelital de {sizeToAdjust} m.')
                    print(f'{TB}{TB}Antes (pre-redondeo):     {self.ymaxBloqueIni:0.2f}')
                    print(f'{TB}{TB}Ahora (ajustado a malla): {self.ymaxBloqueMalla:0.2f}')

        else:
            print('clidhead-> HeadClass-> AVISO: No se puede ajustar coordenadas a una malla de dimension nula.')

        # if sizeToAdjust > 0:
        #     if self.xminBloqueMalla % sizeToAdjust != 0 or self.xmaxBloqueMalla % sizeToAdjust != 0:
        #         if self.verbose:
        #             print('clidhead-> LasHeadClass-> Ajustando Xmin a la dimension de la celda y malla satelital de {} m.'.format(sizeToAdjust))
        #
        #     if self.xminBloqueMalla % sizeToAdjust != 0:
        #         if self.verbose:
        #             print(f'{TB}Before: {self.xminBloqueMalla:0.2f}')
        #     if self.xmaxBloqueMalla % sizeToAdjust != 0:
        #         if self.verbose:
        #             print(f'{TB}Before: {self.xmaxBloqueMalla:0.2f}')
        #
        #
        #         roundXmin = float(sizeToAdjust * round(self.xminBloqueMalla / sizeToAdjust, 0))
        #         roundXmax = float(sizeToAdjust * round(self.xmaxBloqueMalla / sizeToAdjust, 0))
        #         step0Xmin = float(sizeToAdjust * math.floor(self.xminBloqueMalla / sizeToAdjust))
        #         step1Xmin = float(sizeToAdjust * math.ceil(self.xminBloqueMalla / sizeToAdjust))
        #         step0Xmax = float(sizeToAdjust * math.floor(self.xmaxBloqueMalla / sizeToAdjust))
        #         step1Xmax = float(sizeToAdjust * math.ceil(self.xmaxBloqueMalla / sizeToAdjust))
        #         if abs(self.xminBloqueMalla - roundXmin) < margenAdmisible:
        #             if abs(self.xmaxBloqueMalla - roundXmax) < margenAdmisible:
        #                 if roundXmax > roundXmin:
        #                     self.xminBloqueMalla = roundXmin
        #                     self.xmaxBloqueMalla = roundXmax
        #                 else:
        #                     if abs(self.xminBloqueMalla - roundXmin) < abs(self.xmaxBloqueMalla - roundXmax):
        #                         self.xminBloqueMalla = roundXmin
        #                         self.xmaxBloqueMalla = roundXmin + sizeToAdjust
        #                     else:
        #                         self.xminBloqueMalla = roundXmax - sizeToAdjust
        #                         self.xmaxBloqueMalla = roundXmax
        #             else:
        #                 self.xminBloqueMalla = roundXmin
        #                 if step1Xmax == self.xminBloqueMalla + sizeToAdjust:
        #                     self.xmaxBloqueMalla = step1Xmax
        #                 else:
        #                     self.xmaxBloqueMalla = step0Xmax
        #         else:
        #             if abs(self.xmaxBloqueMalla - roundXmax) < margenAdmisible:
        #                 self.xmaxBloqueMalla = roundXmax
        #                 if step0Xmin == self.xmaxBloqueMalla - sizeToAdjust:
        #                     self.xminBloqueMalla = step0Xmin
        #                 elif step1Xmin == self.xmaxBloqueMalla - sizeToAdjust:
        #                     self.xminBloqueMalla = step1Xmin
        #                 else:
        #                     if sizeToAdjust == GLO.GLBLmetrosBloque:
        #                         print(f'clidhead-> ATENCION: las coordenadas de los puntos no se corresponden con bloques de {sizeToAdjust} m')
        #                     self.xminBloqueMalla = self.xmaxBloqueMalla - sizeToAdjust
        #             else:
        #                 # Ninguno de los limites de coordX esta cerca de los posibles limites de bloque
        #                 if step1Xmax == step0Xmin + sizeToAdjust:
        #                     # Los puntos entran dentro del bloque
        #                     self.xminBloqueMalla = step0Xmin
        #                     self.xmaxBloqueMalla = step1Xmax
        #                 elif step0Xmax == step1Xmin + sizeToAdjust:
        #                     # Los puntos exceden el bloque por ambos lados
        #                     self.xminBloqueMalla = step1Xmin
        #                     self.xmaxBloqueMalla = step0Xmax
        #                 elif (
        #                     step1Xmax == step1Xmin + sizeToAdjust
        #                     and step0Xmax == step0Xmin + sizeToAdjust
        #                 ):
        #                     # Los puntos estan a caballo de dos bloques
        #                     if abs(self.xmaxBloqueMalla - step1Xmax) < abs(self.xminBloqueMalla - step0Xmin):
        #                         self.xminBloqueMalla = step1Xmin
        #                         self.xmaxBloqueMalla = step1Xmax
        #                     else:
        #                         self.xminBloqueMalla = step0Xmin
        #                         self.xmaxBloqueMalla = step0Xmax
        #                 else:
        #                     # Creo que esto es imposible (uso la envolvente exterior)
        #                     if sizeToAdjust == GLO.GLBLmetrosBloque:
        #                         print(f'clidhead-> ATENCION: las coordenadas de los puntos no se corresponden con bloques de {sizeToAdjust} m')
        #                     self.xminBloqueMalla = step0Xmin
        #                     self.xmaxBloqueMalla = step1Xmax
        #         if self.verbose:
        #             print(f'{TB}After:  {self.xminBloqueMalla:0.2f}')
        #             print(f'{TB}After:  {self.xmaxBloqueMalla:0.2f}')
        #
        #     if self.yminBloqueMalla % sizeToAdjust != 0 or self.ymaxBloqueMalla % sizeToAdjust != 0:
        #         if self.verbose:
        #             print('\nclidhead-> LasHeadClass-> Ajustando Ymin a la dimension de la celda y malla satelital de {} m.'.format(sizeToAdjust))
        #             print(f'{TB}Before: {self.yminBloqueMalla:0.2f}')
        #
        #         roundYmin = float(sizeToAdjust * round(self.yminBloqueMalla / sizeToAdjust, 0))
        #         roundYmax = float(sizeToAdjust * round(self.ymaxBloqueMalla / sizeToAdjust, 0))
        #         step0Ymin = float(sizeToAdjust * math.floor(self.yminBloqueMalla / sizeToAdjust))
        #         step1Ymin = float(sizeToAdjust * math.ceil(self.yminBloqueMalla / sizeToAdjust))
        #         step0Ymax = float(sizeToAdjust * math.floor(self.ymaxBloqueMalla / sizeToAdjust))
        #         step1Ymax = float(sizeToAdjust * math.ceil(self.ymaxBloqueMalla / sizeToAdjust))
        #         if abs(self.yminBloqueMalla - roundYmin) < margenAdmisible:
        #             if abs(self.ymaxBloqueMalla - roundYmax) < margenAdmisible:
        #                 if roundYmax > roundYmin:
        #                     self.yminBloqueMalla = roundYmin
        #                     self.ymaxBloqueMalla = roundYmax
        #                 else:
        #                     if abs(self.yminBloqueMalla - roundYmin) < abs(self.ymaxBloqueMalla - roundYmax):
        #                         self.yminBloqueMalla = roundYmin
        #                         self.ymaxBloqueMalla = roundYmin + sizeToAdjust
        #                     else:
        #                         self.yminBloqueMalla = roundYmax - sizeToAdjust
        #                         self.ymaxBloqueMalla = roundYmax
        #             else:
        #                 self.yminBloqueMalla = roundYmin
        #                 if step1Ymax == self.yminBloqueMalla + sizeToAdjust:
        #                     self.ymaxBloqueMalla = step1Ymax
        #                 else:
        #                     self.ymaxBloqueMalla = step0Ymax
        #         else:
        #             if abs(self.ymaxBloqueMalla - roundYmax) < margenAdmisible:
        #                 self.ymaxBloqueMalla = roundYmax
        #                 if step0Ymin == self.ymaxBloqueMalla - sizeToAdjust:
        #                     self.yminBloqueMalla = step0Ymin
        #                 elif step1Ymin == self.ymaxBloqueMalla - sizeToAdjust:
        #                     self.yminBloqueMalla = step1Ymin
        #                 else:
        #                     if sizeToAdjust == GLO.GLBLmetrosBloque:
        #                         print(f'clidhead-> ATENCION: las coordenadas de los puntos no se corresponden con bloques de {sizeToAdjust} m')
        #                     self.yminBloqueMalla = self.ymaxBloqueMalla - sizeToAdjust
        #             else:
        #                 # Ninguno de los limites de coordX esta cerca de los posibles limites de bloque
        #                 if step1Ymax == step0Ymin + sizeToAdjust:
        #                     # Los puntos entran dentro del bloque
        #                     self.yminBloqueMalla = step0Ymin
        #                     self.ymaxBloqueMalla = step1Ymax
        #                 elif step0Ymax == step1Ymin + sizeToAdjust:
        #                     # Los puntos exceden el bloque por ambos lados
        #                     self.yminBloqueMalla = step1Ymin
        #                     self.ymaxBloqueMalla = step0Ymax
        #                 elif (
        #                     step1Ymax == step1Ymin + sizeToAdjust
        #                     and step0Ymax == step0Ymin + sizeToAdjust
        #                 ):
        #                     # Los puntos estan a caballo de dos bloques
        #                     if abs(self.ymaxBloqueMalla - step1Ymax) < abs(self.yminBloqueMalla - step0Ymin):
        #                         self.yminBloqueMalla = step1Ymin
        #                         self.ymaxBloqueMalla = step1Ymax
        #                     else:
        #                         self.yminBloqueMalla = step0Ymin
        #                         self.ymaxBloqueMalla = step0Ymax
        #                 else:
        #                     # Creo que esto es imposible (uso la envolvente exterior)
        #                     if sizeToAdjust == GLO.GLBLmetrosBloque:
        #                         print(f'clidhead-> ATENCION: las coordenadas de los puntos no se corresponden con bloques de {sizeToAdjust} m')
        #                     self.yminBloqueMalla = step0Ymin
        #                     self.ymaxBloqueMalla = step1Ymax
        #
        #     # if self.xminBloqueMalla % sizeToAdjust != 0:
        #     #             self.xminBloqueMalla = step0
        #     #     elif abs(self.xmaxBloqueMalla - step1) < margenAdmisible:
        #     #         self.xminBloqueMalla = step1
        #     #
        #     #     if (
        #     #         (self.xmaxBloqueMalla - self.xminBloqueMalla) >= sizeToAdjust - margenAdmisible
        #     #
        #     #     if (
        #     #         self.xmaxBloqueMalla - self.xminBloqueMalla < sizeToAdjust
        #     #         or self.xminBloqueMalla % sizeToAdjust <= margenAdmisible
        #     #         or self.xminBloqueMalla % sizeToAdjust >= sizeToAdjust - margenAdmisible
        #     #     ):
        #     #         self.xminBloqueMalla = float(sizeToAdjust * math.floor(self.xminBloqueMalla / sizeToAdjust))
        #     #     else:
        #     #         if envolvente:
        #     #             self.xminBloqueMalla = float(sizeToAdjust * math.floor(self.xminBloqueMalla / sizeToAdjust))
        #     #         else:
        #     #             self.xminBloqueMalla = float(sizeToAdjust * math.ceil(self.xminBloqueMalla / sizeToAdjust))
        #     #     if self.verbose:
        #     #         print(f'{TB}After: {self.xminBloqueMalla:0.2f}')
        #     # if self.xmaxBloqueMalla % sizeToAdjust != 0:
        #     #     if self.verbose:
        #     #         print('clidhead-> LasHeadClass-> Ajustando Xmax a la dimension de la celda y malla satelital de {} m.'.format(sizeToAdjust))
        #     #         print(f'{TB}Before: {self.xmaxBloqueMalla:0.2f}')
        #     #     if (
        #     #         self.xmaxBloqueMalla - self.xminBloqueMalla < sizeToAdjust
        #     #         or self.xmaxBloqueMalla % sizeToAdjust <= margenAdmisible
        #     #         or self.xmaxBloqueMalla % sizeToAdjust >= sizeToAdjust - margenAdmisible
        #     #     ):
        #     #         self.xmaxBloqueMalla = float(sizeToAdjust * math.ceil(self.xmaxBloqueMalla / sizeToAdjust))
        #     #     else:
        #     #         if envolvente:
        #     #             self.xmaxBloqueMalla = float(sizeToAdjust * math.ceil(self.xmaxBloqueMalla / sizeToAdjust))
        #     #         else:
        #     #             self.xmaxBloqueMalla = float(sizeToAdjust * math.floor(self.xmaxBloqueMalla / sizeToAdjust))
        #     #     if self.verbose:
        #     #         print(f'{TB}After: {self.xmaxBloqueMalla:0.2f}')
        #     # if self.yminBloqueMalla % sizeToAdjust != 0:
        #     #     if self.verbose:
        #     #         print('clidhead-> LasHeadClass-> Ajustando Ymin a la dimension de la celda y malla satelital de {} m.'.format(sizeToAdjust))
        #     #         print(f'{TB}Before: {self.yminBloqueMalla:0.2f}')
        #     #     if (
        #     #         self.ymaxBloqueMalla - self.yminBloqueMalla < sizeToAdjust
        #     #         or self.yminBloqueMalla % sizeToAdjust <= margenAdmisible
        #     #         or self.yminBloqueMalla % sizeToAdjust >= sizeToAdjust - margenAdmisible
        #     #     ):
        #     #         # self.yminBloqueMalla = float(sizeToAdjust * round(self.yminBloqueMalla / sizeToAdjust, 0))
        #     #         self.yminBloqueMalla = float(sizeToAdjust * math.floor(self.yminBloqueMalla / sizeToAdjust))
        #     #     else:
        #     #         if envolvente:
        #     #             self.yminBloqueMalla = float(sizeToAdjust * math.floor(self.yminBloqueMalla / sizeToAdjust))
        #     #         else:
        #     #             self.yminBloqueMalla = float(sizeToAdjust * math.ceil(self.yminBloqueMalla / sizeToAdjust))
        #     #     if self.verbose:
        #     #         print(f'{TB}After: {self.yminBloqueMalla:0.2f}')
        #     # if self.ymaxBloqueMalla % sizeToAdjust != 0:
        #     #     if self.verbose:
        #     #         print('clidhead-> LasHeadClass-> Ajustando Ymax a la dimension de la celda y malla satelital de {} m.'.format(sizeToAdjust))
        #     #         print(f'{TB}Before: {self.ymaxBloqueMalla:0.2f}')
        #     #     if (
        #     #         self.ymaxBloqueMalla - self.yminBloqueMalla < sizeToAdjust
        #     #         or self.ymaxBloqueMalla % sizeToAdjust <= margenAdmisible
        #     #         or self.ymaxBloqueMalla % sizeToAdjust >= sizeToAdjust - margenAdmisible
        #     #     ):
        #     #         # self.ymaxBloqueMalla = float(sizeToAdjust * round(self.ymaxBloqueMalla / sizeToAdjust, 0))
        #     #         self.ymaxBloqueMalla = float(sizeToAdjust * math.ceil(self.ymaxBloqueMalla / sizeToAdjust))
        #     #     else:
        #     #         if envolvente:
        #     #             self.ymaxBloqueMalla = float(sizeToAdjust * math.ceil(self.ymaxBloqueMalla / sizeToAdjust))
        #     #         else:
        #     #             self.ymaxBloqueMalla = float(sizeToAdjust * math.floor(self.ymaxBloqueMalla / sizeToAdjust))
        #     #     if self.verbose:
        #     #         print(f'{TB}After: {self.ymaxBloqueMalla:0.2f}')
        # else:
        #     print('clidhead-> LasHeadClass-> AVISO: Ajustando coordenadas a una dimension nula')
        self.xSupIzda = self.xminBloqueMalla
        self.ySupIzda = self.ymaxBloqueMalla
        self.xInfDcha = self.xmaxBloqueMalla
        self.yInfDcha = self.yminBloqueMalla


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def showAlllasFileVersions(self):
        print('\nclidhead-> LasHeadClass-> Cheking lasFile versions:')
        (
            self.lasHeaderFieldListVersionsDict,
            self.lasHeaderFieldPropertiesDict,
            self.lasHeaderFieldPropertiesList
        ) = lasHeadProperties()
        for lasFileVersion in sorted(self.lasHeaderFieldListVersionsDict.keys()):
            print('\nclidhead-> LasHeadClass-> LasFile version: %s' % lasFileVersion)
            print('\tclidhead-> LasHeadClass-> list of fields:', self.lasHeaderFieldListVersionsDict[lasFileVersion])
            print('\tclidhead-> LasHeadClass-> Properties of fields:')
            for lasHeadField in self.lasHeaderFieldListVersionsDict[lasFileVersion]:
                print('\tclidhead-> LasHeadClass-> \t', lasFileVersion + '_' + lasHeadField, self.lasHeaderFieldPropertiesDict[lasFileVersion + '_' + lasHeadField])


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def showAllPointFormats(self):
        print('\nclidhead-> LasHeadClass-> Cheking las point formats:')
        # No incluyo el format 101 y 102 que incluye las extraVariables y la maxiMiniSubCel
        for nPointFormat in range(1, 11):
            try:
                print('\tclidhead-> LasHeadClass-> Point format: %i' % nPointFormat)
                # print('clidhead-> LasHeadClass-> (y) Llamando a lasPointProperties con {}'.format(nPointFormat))
                (
                    self.lasPointFieldPropertiesList,
                    self.lasPointFieldPropertiesDict,
                    self.lasPointFieldOrdenDictPtoMini,
                    self.lasPointFieldOrdenDictPtoComp,
                ) = lasPointProperties(
                    nPointFormat,
                    # extraBytesPorRegistro=self.headDict['extraBytesPorRegistro'],
                    verbose=self.verbose,
                )

                nBytesPorPuntoCheck = sum(int(pointField[1]) for pointField in self.lasPointFieldPropertiesList)
                print('\tclidhead-> LasHeadClass-> \t', nBytesPorPuntoCheck, self.lasPointFieldPropertiesList)
            except:
                print('\tclidhead-> LasHeadClass-> \tPoint format %i not implemented\n' % nPointFormat)


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def showInfoLas(self, mostrarPropiedadesDeLaClase=False):
        printMsg(f'\n{"":_^80}')
        printMsg('clidhead-> LasHeadClass-> showInfoLas<>:')
        printMsg('  lasVersion:  %s' % self.lasVersion)
        printMsg('  pointformat: %i' % self.pointformat)
        strPuntosTotal = "{:,}".format(self.numptrecords)
        printMsg('  Number of returns (total): %s' % (strPuntosTotal))
        printMsg(f'{"":=^80}')

        printMsg('clidhead-> LasHeadClass-> showInfoLas<>-> Header Summary (sin "\x00" en sysid y gensoftware):')
        printMsg('  Source ID:                   %i' % self.filesourceid)
        printMsg('  globalencoding:              %s' % self.globalencoding)
        printMsg(
            '  Project ID/GUID:             %08i-%04i-%04i-%04i-%04i%04i%04i'
            % (self.guid1, self.guid2, self.guid3, self.guid4[0], self.guid4[1], self.guid4[2], self.guid4[3])
        )
        # printMsg('  System ID:                   %s' % self.sysid.rstrip(b'\x00').decode('latin-1'))
        printMsg('  System ID:                   %s' % self.sysid)
        # printMsg('  Generating Software:         %s' % self.gensoftware.rstrip(b'\x00').decode('latin-1'))
        printMsg('  Generating Software:         %s' % self.gensoftware)
        printMsg('  File Creation Day/Year:      %i / %i' % (self.fileday, self.fileyear))
        printMsg('  Header Byte Size             %i' % self.headersize)
        printMsg('  Data Offset Leido:           %i' % self.headDict['offset'])
        printMsg('  Data Offset Leido:           %i' % self.offset)
        printMsg('  Data suma Bytes cabecera:    %i' % self.sumaBytesCabecera)
        # self.padding = 0
        # printMsg('  Header Padding:              %i' % self.padding)
        printMsg('  Number Var. Length Records:  %i' % self.numvlrecords)
        printMsg('  Point Data Format:           %i' % self.pointformat)
        printMsg('  Point Rec lenght:            %i' % self.pointreclen, self.verbose)
        printMsg('  Number of Point Records:     %i' % self.numptrecords)
        # self.compressed = False
        # printMsg('  Compressed:                  %s' % self.compressed)
        try:
            primerNulo = np.where(np.array(self.numptbyreturn) == 0)[0][0]
        except:
            primerNulo = len(self.numptbyreturn)
        printMsg('  Number of Points by Return:  %s' % str(self.numptbyreturn[: primerNulo + 1]))
        printMsg('  Scale Factor X Y Z:          %0.11f / %0.11f / %0.11f' % (self.xscale, self.yscale, self.zscale))
        printMsg('  Offset X Y Z:                %f / %f / %f' % (self.xoffset, self.yoffset, self.zoffset))
        printMsg('  Min X Y Z:                   %f / %f / %f' % (self.xminBloqueMalla, self.yminBloqueMalla, self.zmin))
        printMsg('  Max X Y Z:                   %f / %f / %f' % (self.xmaxBloqueMalla, self.ymaxBloqueMalla, self.zmax))
        printMsg(f'{"":=^80}')

        #         printMsg('\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        #         printMsg('  nBytesPorPunto:              %i' % self.pointreclen, self.verbose)
        #         printMsg('  xoffset: %f, yoffset: %f' % (self.headDict['xoffset'], self.headDict['yoffset']), self.verbose)
        #         printMsg('  Coords (round)  -> xmin: %i, xmax: %i, ymin: %i, ymax: %i:' %\
        #                         (round(self.xminBloqueMalla, 0), round(self.xmaxBloqueMalla, 0), round(self.yminBloqueMalla, 0), round(self.ymaxBloqueMalla, 0)), self.verbose)
        #         printMsg('  Coords (float)-> xmin: %f, xmax: %f, ymin: %f, ymax: %f:' %\
        #                         (self.xminBloqueMalla, self.xmaxBloqueMalla, self.yminBloqueMalla, self.ymaxBloqueMalla), self.verbose)
        #         printMsg('  self.listaTuplasPropPtoTodas: %s' % str(self.lasPointFieldPropertiesList), self.verbose)
        #         printMsg(f'{"":=^80}')
        printMsg(f'{"":=^80}')

        printMsg('clidhead-> LasHeadClass-> Spatial Reference:')
        #         WKT = (self.headDict['globalencoding'] >> 4) & 1
        #         if self.headDict['pointformat'] < 6:
        #             if WKT:
        #                 self.formatoSRS = 'WKT'
        #             else:
        #                 self.formatoSRS = 'GeoTIFF'
        #         else:
        #             if WKT:
        #                 self.formatoSRS = 'WKT'
        #             else:
        #                 #Point Record Formats 6-10 must use WKT.
        #                 self.formatoSRS = 'Error'
        if self.lasVersion == 'LasFormat_1_2':
            # las format 1.2 solo admite CRS en forma GeoTiff.
            # Este las format requiere obligatoriamente un Variable Length Record, GeoKeyDirectoryTag).
            print(f'{TB}-> LASF format 1.2 solo admite srs compatible con GeoTiff')
            if self.headDict['numvlrecords'] == 0:
                print(f'{TB}{TV}-> Pero el LASF no incluye esta informacion al no incluir ningun VLR')
            else:
                for nVlrecord in range(self.headDict['numvlrecords']):
                    if (self.headDict['UserID_%i' % nVlrecord]).rstrip('\x00') == 'LASF_Projection' or (self.headDict['Description_%i' % nVlrecord]).rstrip(
                        '\x00'
                    ) == 'GeoTiff GeoKeyDirectoryTag':
                        print(f'{TB}{TV}-> Ver mas adelante el contenido del VLR GeoTiff GeoKeyDirectoryTag')
        elif self.lasVersion == 'LasFormat_1_4':
            print(f'{TB}-> LASF format 1.4 configurado para srs compatible con', self.formatoSRS)
            if self.headDict['numvlrecords'] == 0:
                print(f'{TB}{TV}-> Pero el LASF no incluye esta informacion al no incluir ningun VLR')
            else:
                for nVlrecord in range(self.headDict['numvlrecords']):
                    if 'Description_%i' % nVlrecord in self.headDict.keys():
                        if (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'OGC Transformation Record':
                            print(f'{TB}{TV}-> Ver mas adelante el contenido del VLR OGC Transformation Record')
                        elif (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoTiff GeoKeyDirectoryTag':
                            print(f'{TB}{TV}-> Ver mas adelante el contenido del VLR GeoTiff GeoKeyDirectoryTag')
        printMsg(f'{"":=^80}')

        printMsg('clidhead-> LasHeadClass-> showInfoLas<>-> VLR (lasFormat 1.4):')
        if self.lasVersion == 'LasFormat_1_4':
            printMsg('\tStart of first Extended Variable Length Record:  %i' % self.extendedVLRstart)
            printMsg('\tNumber of Extended Variable Length Records:      %i' % self.extendedVLRnValues)
            printMsg('\tExtended number of point records:                %i' % self.pointrecords)
            printMsg('\tExtended number of points by return:             %s' % str(self.pointsbyreturn))
        else:
            printMsg('\tNumber of Extended Variable Length Records:      %s' % 'No extended VLR')
            printMsg('\tStart of first Extended Variable Length Record:  %s' % 'No extended VLR')
            printMsg('\tExtended number of point records:                %s' % 'No extended VLR')
            printMsg('\tExtended number of points by return:             %s' % 'No extended VLR')
        if self.lasVersion == 'LasFormat_1_3' or self.lasVersion == 'LasFormat_1_4':
            printMsg('\tStart of Waveform Data Packet Record:            %i' % self.waveformStart)
        else:
            printMsg('\tStart of Waveform Data Packet Record:            %s' % 'No waveform data (las format 1.2)')
        printMsg(f'{"":=^80}')

        if self.VLRhuso == 29 or self.TRNShuso29:
            husoNewLas = 29
        else:
            husoNewLas = 30
        if 'Description_0' in self.headDict.keys() and self.headDict['Description_0'].rstrip('\x00') == 'No Variable Lenght Records (VRL)':
            print(f'clidhead-> LasHeadClass-> {self.headDict["Description_0"]}')
        else:
            directorioDeTrabajo = buscarDirectorioDataExt()
            VLRsFileName = os.path.join(
                directorioDeTrabajo, 'io/VLRs_{:04}{:02}{:02}_H{}.geo'.format(
                    datetime.datetime.now().year,
                    datetime.datetime.now().month,
                    datetime.datetime.now().day,
                    husoNewLas,
                )
            )
            VLRsFile = open(VLRsFileName, mode='wb')
            # printMsg('Campos de LasFormat_1_2_vlrecord:' + str(self.lasHeaderFieldListVersionsDict[self.lasVersion + '_vlrecord']))
            for nVlrecord in range(self.headDict['numvlrecords']):
                if self.lasVersion == 'LasFormat_1_4':
                    print('clidhead-> LasHeadClass->   Variable length header record %i of %i:' % (nVlrecord, self.extendedVLRnValues))
                else:
                    print('clidhead-> LasHeadClass->   Variable length header record %i:' % (nVlrecord))
                for myField in self.lasHeaderFieldListVersionsDict[self.lasVersion + '_vlrecord']:
                    fieldname = '%s_%i' % (myField, nVlrecord)
                    # value = self.headDict['textoVRL_%i' % nVlrecord]
                    if myField == 'Description' or myField == 'UserID':
                        # value = self.headDict[fieldname].decode('latin-1')
                        value = self.headDict[fieldname]
                    else:  # Reserved, RecordID, RecordLengthAfterHeader
                        value = str(self.headDict[fieldname])
                    print('clidhead-> LasHeadClass->  ', myField.rjust(25), '->', value)
                    # print( 'clidhead-> LasHeadClass-> ------>UserID:                  %s' % str(self.headDict['UserID']) )
                    # print( 'clidhead-> LasHeadClass-> ------>RecordID:                %s' % str(self.headDict['RecordID']) )
                    # print( 'clidhead-> LasHeadClass-> ------>RecordLengthAfterHeader: %s' % str(self.headDict['RecordLengthAfterHeader']) )
                    # print( 'clidhead-> LasHeadClass-> ------>Description:             %s' % str(self.headDict['Description']) )
                    # print( 'clidhead-> LasHeadClass-> ------>textoVRL:                %s' % str(self.headDict['textoVRL_%i' % nVlrecord]) )

                fieldname = '%s_%i' % ('VLR_', nVlrecord)
                # value = self.headDict['VRL_%i' % nVlrecord].rstrip(b'\x00')
                value = self.headDict['VRL_%i' % nVlrecord]
                VLRdescription = f'{self.headDict["Description_%i" % nVlrecord]}'.rstrip("\x00")
                # VLRsFile.write(b'%s' % VLRdescription)
                VLRsFile.write(bytes(VLRdescription, 'latin-1'))
                VLRsFile.write(b'\n')
                VLRsFile.write(value)
                VLRsFile.write(b'\n')
                if (
                    (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'OGC Transformation Record'
                    or (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'OGC COORDINATE SYSTEM WKT'
                    or 'OGC' in self.headDict['Description_%i' % nVlrecord]
                ):
                    print(f'                       ->  {fieldname.rjust(25)} -> OGC COORDINATE SYSTEM ({self.formatoSRS}): - {self.headDict["Description_%i" % nVlrecord]}:')
                    print(f'clidhead-> LasHeadClass->  {fieldname.rjust(25)} -> {value.decode("latin-1")}'.rstrip('\x00'))
                    VLRsFileName = os.path.join(
                        directorioDeTrabajo, 'io/VLRs_{:04}{:02}{:02}_{}_H{}.geo'.format(
                            datetime.datetime.now().year,
                            datetime.datetime.now().month,
                            datetime.datetime.now().day,
                            f'OGC_{self.formatoSRS}',
                            husoNewLas,
                        )
                    )
                    VLRsFileOGC = open(VLRsFileName, mode='wb')
                    VLRsFileOGC.write(value)
                    VLRsFileOGC.write(b'\n')
                    VLRsFileOGC.close()
                elif (
                    (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'OGR variant of OpenGIS WKT SRS'
                    or 'OGR' in self.headDict['Description_%i' % nVlrecord]
                ):
                    print(f'                       ->  {fieldname.rjust(25)} -> OGR variant of OpenGIS WKT SRS - {self.headDict["Description_%i" % nVlrecord]}:')
                    print(f'clidhead-> LasHeadClass->  {fieldname.rjust(25)} -> {value.decode("latin-1")}'.rstrip('\x00'))
                    VLRsFileName = os.path.join(
                        directorioDeTrabajo, 'io/VLRs_{:04}{:02}{:02}_{}_H{}.geo'.format(
                            datetime.datetime.now().year,
                            datetime.datetime.now().month,
                            datetime.datetime.now().day,
                            f'OGR_{self.formatoSRS}',
                            husoNewLas,
                        )
                    )
                    VLRsFileOGC = open(VLRsFileName, mode='wb')
                    VLRsFileOGC.write(value)
                    VLRsFileOGC.write(b'\n')
                    VLRsFileOGC.close()
                elif (
                    (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoTiff GeoAsciiParamsTag'
                    or 'GeoAsciiParamsTag' in self.headDict['Description_%i' % nVlrecord]
                    or (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoASCIIParamsTag (optional)'
                    or 'GeoASCIIParamsTag' in self.headDict['Description_%i' % nVlrecord]
                ):
                    print(f'                       ->  {fieldname.rjust(25)} -> GeoTiff GeoAsciiParamsTag - {self.headDict["Description_%i" % nVlrecord]}:')
                    print(f'clidhead-> LasHeadClass->  {fieldname.rjust(25)} -> {value.decode("latin-1")}'.rstrip('\x00'))
                    VLRsFileName = os.path.join(
                        directorioDeTrabajo, 'io/VLRs_{:04}{:02}{:02}_{}_H{}.geo'.format(
                            datetime.datetime.now().year,
                            datetime.datetime.now().month,
                            datetime.datetime.now().day,
                            f'GeoAsciiParamsTag_{self.formatoSRS}',
                            husoNewLas,
                        )
                    )
                    VLRsFileOGC = open(VLRsFileName, mode='wb')
                    VLRsFileOGC.write(value)
                    VLRsFileOGC.write(b'\n')
                    VLRsFileOGC.close()
                elif (
                    (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoTiff GeoDoubleParamsTag'
                    or 'GeoDoubleParamsTag' in self.headDict['Description_%i' % nVlrecord]
                ):
                    print(f'                       ->  {fieldname.rjust(25)} -> GeoTiff GeoDoubleParamsTag - {self.headDict["Description_%i" % nVlrecord]}:')
                    print(f'clidhead-> LasHeadClass->  {fieldname.rjust(25)} -> {value.decode("latin-1")}'.rstrip('\x00'))
                    VLRsFileName = os.path.join(
                        directorioDeTrabajo, 'io/VLRs_{:04}{:02}{:02}_{}_H{}.geo'.format(
                            datetime.datetime.now().year,
                            datetime.datetime.now().month,
                            datetime.datetime.now().day,
                            f'GeoDoubleParamsTag_{self.formatoSRS}',
                            husoNewLas,
                        )
                    )
                    VLRsFileOGC = open(VLRsFileName, mode='wb')
                    VLRsFileOGC.write(value)
                    VLRsFileOGC.write(b'\n')
                    VLRsFileOGC.close()
                elif (
                    (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoTiff GeoKeyDirectoryTag'
                    or 'GeoKeyDirectoryTag' in self.headDict['Description_%i' % nVlrecord]
                ):
                    # ver https://www.awaresystems.be/imaging/tiff/tifftags/geokeydirectorytag.html
                    print(f'                       ->  {fieldname.rjust(25)} -> GeoTiff GeoKeyDirectoryTag - {self.headDict["Description_%i" % nVlrecord]}:')
                    print(f'clidhead-> LasHeadClass->  {fieldname.rjust(25)} -> {value.decode("latin-1")}'.rstrip('\x00'))
                    VLRsFileName = os.path.join(
                        directorioDeTrabajo, 'io/VLRs_{:04}{:02}{:02}_{}_H{}.geo'.format(
                            datetime.datetime.now().year,
                            datetime.datetime.now().month,
                            datetime.datetime.now().day,
                            f'GeoKeyDirectoryTag_{self.formatoSRS}',
                            husoNewLas,
                        )
                    )
                    VLRsFileOGC = open(VLRsFileName, mode='wb')
                    VLRsFileOGC.write(value)
                    VLRsFileOGC.write(b'\n')
                    VLRsFileOGC.close()


                    numeroDeShorts = int(len(value) / 2)
                    try:
                        valuePlus = struct.unpack('%iH' % numeroDeShorts, value)

                        EPSGid = valuePlus[31]
                        import osr
                        import xml.etree.ElementTree as ET

                        # Establecer variable de entorno
                        # PROJ_LIB=C:\OSGeo4W64\share\proj
                        spatialRef = osr.SpatialReference()
                        spatialRef.ImportFromEPSG(EPSGid)

                        # miProyeccionWKT = spatialRef.ExportToWkt()
                        # miProyeccionPrettyWkt = spatialRef.ExportToPrettyWkt()
                        # miProyeccionPCI = spatialRef.ExportToPCI()
                        # miProyeccionUSGS = spatialRef.ExportToUSGS()

                        xmlPre = (
                            '<?xml version="1.0" encoding="UTF-8"?>'
                            + '\n'
                            + '<schema elementFormDefault="qualified" \
                                 targetNamespace="http://www.opengis.net/gml/3.2" \
                                 version="3.2.1.2" \
                                 xmlns="http://www.w3.org/2001/XMLSchema" \
                                 xmlns:gml="http://www.opengis.net/gml/3.2" \
                                 xmlns:xlink="https://www.w3.org/1999/xlink">'
                            + '\n'
                        )
                        xmlPost = '</schema>'
                        # miProyeccionXML = xmlPre + spatialRef.ExportToXML() + xmlPost
                        # En vez de especificar los namespaces al inicio del XML, simplemente los quito de las etiquetas
                        namespace1pre = 'gml:'
                        namespace1post = ''
                        namespace2pre = 'xlink:'
                        namespace2post = ''
                        miProyeccionXML = spatialRef.ExportToXML().replace(namespace1pre, namespace1post).replace(namespace2pre, namespace2post)

                        try:
                            root = ET.fromstring(miProyeccionXML)
                            srsTag = root.tag
                            # print( 'clidhead-> LasHeadClass-> root.tag->', root.tag)
                            for item in root:
                                if 'srsName' in item.tag:
                                    srsName = item.text
                                    # print( 'clidhead-> LasHeadClass-> +>Sistema de referencia:', item.text)
                                elif 'srsID' in item.tag:
                                    # print( 'clidhead-> LasHeadClass-> +>', item.tag)
                                    for item2 in item:
                                        # <gml:name codeSpace="urn:ogc:def:crs:EPSG::">25830</gml:name>
                                        if 'name' in item2.tag:
                                            srsID = item2.text
                                        # print( 'clidhead-> LasHeadClass->   -->>', item2.tag, '>', item2.text)
                                        # print( 'clidhead-> LasHeadClass->        attrib->', item2.attrib)
                                elif 'baseCRS' in item.tag:
                                    # print( 'clidhead-> LasHeadClass-> +>', item.tag)
                                    for item2 in item:
                                        for item3 in item2:
                                            if 'srsName' in item3.tag:
                                                srsBase = item3.text
                                                # print( 'clidhead-> LasHeadClass->     --->>>', item3.tag, '>', item3.text)
                                elif 'definedByConversion' in item.tag:
                                    pass
                                elif 'usesCartesianCS' in item.tag:
                                    pass
                        except:
                            srsTag = 'Desconocdo'
                            srsName = 'Desconocdo'
                            srsBase = 'Desconocdo'
                        # print( 'clidhead-> LasHeadClass-> EPSG', valuePlus[31], '->', srsTag, srsName, 'Elipsoide:', srsBase)

                        print('                       ->     GeoKeyDirectoryTag version %i.%i.%i number of keys %i' % valuePlus[:4])
                        print(
                            'clidhead-> LasHeadClass->       key %i tiff_tag_location %i count %i value_offset %i - GTModelTypeGeoKey: (#TODO) ModelTypeProjected -Provisional '
                            % valuePlus[4:8]
                        )
                        print(
                            'clidhead-> LasHeadClass->       key %i tiff_tag_location %i count %i value_offset %i - GTRasterTypeGeoKey: (#TODO)RasterPixelIsArea -Provisional'
                            % valuePlus[8:12]
                        )
                        print(
                            'clidhead-> LasHeadClass->       key %i tiff_tag_location %i count %i value_offset %i - GTCitationGeoKey: (#TODO)ETRS89 / UTM zone 30N -Provisional'
                            % valuePlus[12:16]
                        )
                        print(
                            'clidhead-> LasHeadClass->       key %i tiff_tag_location %i count %i value_offset %i - GeogCitationGeoKey: (#TODO)ETRS89 -Provisional (#TODO)'
                            % valuePlus[16:20]
                        )
                        print(
                            'clidhead-> LasHeadClass->       key %i tiff_tag_location %i count %i value_offset %i - GeogAngularUnitsGeoKey: (#TODO) Angular_Degree -Provisional'
                            % valuePlus[20:24]
                        )
                        print(
                            'clidhead-> LasHeadClass->       key %i tiff_tag_location %i count %i value_offset %i - GeogTOWGS84GeoKey: (#TODO) TOWGS84[0,0,0] -Provisional'
                            % valuePlus[24:28]
                        )
                        print(
                            'clidhead-> LasHeadClass->       key %i tiff_tag_location %i count %i value_offset %i - ProjectedCSTypeGeoKey: %s'
                            % (valuePlus[28], valuePlus[29], valuePlus[30], valuePlus[31], srsName)
                        )
                        print(
                            'clidhead-> LasHeadClass->       key %i tiff_tag_location %i count %i value_offset %i - ProjLinearUnitsGeoKey: (#TODO) Linear_Meter -Provisional'
                            % valuePlus[32:36]
                        )
                    except:
                        valuePlus = 'No unpack'
                        print('clidhead-> LasHeadClass-> GeoTiff GeoKeyDirectoryTag pendiente de desempaquetar y descifrar adecuadamente (#TODO)')
                else:
                    # print( 'clidhead-> LasHeadClass-> ->', str(self.headDict['Description_%i' % nVlrecord].rstrip('\x00')) , '<-')
                    print('clidhead-> LasHeadClass->  ', 'longitud'.rjust(25), '->', len(value))
                    try:
                        valorDecodificado = value.decode('latin-1')
                        print('clidhead-> LasHeadClass->  ', fieldname.rjust(25), '->', valorDecodificado)
                    except:
                        try:
                            valorDecodificado = value.decode('latin-1', errors='ignore')
                            print('clidhead-> LasHeadClass->  ', fieldname.rjust(25), '->', valorDecodificado, 'Decodificado ignorando errores')
                        except:
                            print('clidhead-> LasHeadClass->  ', fieldname.rjust(25), '->', value, 'No decodificado')

                # print( 'clidhead-> LasHeadClass->  ', fieldname.rjust(25), end=' -> ')
                # for letra in value:
                #    print(chr(letra), end='')
                # print( 'clidhead-> LasHeadClass-> ')
                if nVlrecord < self.headDict['numvlrecords'] - 1:
                    printMsg('')
            VLRsFile.close()
        printMsg(f'{"":=^80}')

        self.infoLasPoints(verbose=True)

        if mostrarPropiedadesDeLaClase:
            printMsg(f'{"":=^80}')
            propiedades = [unaPropiedad for unaPropiedad in dir(self) if isinstance(getattr(self, unaPropiedad), property)]
            printMsg('\nclidhead-> LasHeadClass-> Properties of LasHead object:', self.verbose)
            printMsg('\nPropiedades de self %s:' % str(propiedades), self.verbose)
            for unaPropiedad in dir(self):
                printMsg('{:>50}\t{}'.format(unaPropiedad, type(getattr(self, unaPropiedad)), getattr(self, unaPropiedad)), self.verbose)
            printMsg('\nVariables de self:', self.verbose)
            for variableDeMiBloque in vars(self).keys():
                printMsg('{:>50}\t{}'.format(variableDeMiBloque, vars(self)[variableDeMiBloque]), self.verbose)
                printMsg(f'{"":=^80}')


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def infoLasPoints(self, verbose=False, devolverPropiedad=False):

        #         myLasHead = LasHeadClass(self.infileConRuta,
        #                                  GLO.GLBLmetrosBloque,
        #                                  GLO.GLBLmetrosCelda,
        #                                  verbose=False)
        #         #Basic checking of las file, nCeldas and coordinates from fileName:
        #         myLasHead.checkLasfile()

#         numPuntosPorMetroCuadrado = self.headDict['numptrecords'] / (GLO.GLBLmetrosBloque ** 2)
#         if GLO.GLBLnMaxPtosCeldaArrayPredimensionadaTodos < numPuntosPorMetroCuadrado * (GLO.GLBLmetrosCelda ** 2):
#             LCLnMaxPtosCeldaArrayPredimensionadaTodos = int(numPuntosPorMetroCuadrado * (GLO.GLBLmetrosCelda ** 2))
#             print(
#                 'clidhead-> infoLasPoints-> ATENCION: se amplia GLBLnMaxPtosCeldaArrayPredimensionadaTodos de',
#                 GLO.GLBLnMaxPtosCeldaArrayPredimensionadaTodos,
#                 'a',
#                 LCLnMaxPtosCeldaArrayPredimensionadaTodos,
#             )
#         else:
#             LCLnMaxPtosCeldaArrayPredimensionadaTodos = GLO.GLBLnMaxPtosCeldaArrayPredimensionadaTodos

        if self.controlFileLasNameConRuta != '':
            global GLO
            GLO.controlFileLasName = self.controlFileLasNameConRuta
            printMsg(f'{"":=^80}')
            paramConfigAdicionalesMAIN = {}
            paramConfigAdicionalesMAIN['controlFileLasName'] = [GLO.controlFileLasName, 'str', '', 'GrupoMAIN', GLO.controlFileLasName]
            printMsg(f'clidflow-> Guardando controlFileLasNameConRuta en el fichero con los parametros de configuracion.')
            GLOBALconfigDict = clidconfig.leerCambiarVariablesGlobales(
                LCL_idProceso=GLO.MAIN_idProceso,
                nuevosParametroConfiguracion=paramConfigAdicionalesMAIN,
                inspect_stack=inspect.stack(),
                verbose=False,
            )

        spec = importlib.util.find_spec('cartolidar')
        if spec is None or MAIN_ENTORNO == 'calendula':
            sys.stderr.write(f'clidhead-> infoLasPoints-> Info: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).\n')
            sys.stderr.write(f'{TB}-> Se importan paquetes de cartolidar desde clidhead del directorio local {os.getcwd()}/....\n')
            from clidfr import cliddata
        else:
            from cartolidar.clidfr import cliddata
        myLasData = cliddata.LasData(self)
        myLasData.nPtosAleer = self.numptrecords
        myLasData.sampleLas = 1
#         self.LCLnMaxPtosCeldaArrayPredimensionadaTodos = LCLnMaxPtosCeldaArrayPredimensionadaTodos
        # ======================================================================

        # ======================================================================
        # oooooooooooooooooooooooo Lectura del fichero las ooooooooooooooooooooo
        # ======================================================================
        # myLasData.readLasData(byREFAlmacenarPuntosComoNumpyDtype=True)  # Fuerzo almacenarPuntosComoNumpyDtype
        printMsg('clidhead-> infoLasPoints-> Se lanza myLasData.leerLasDataLazLas<>')
        myLasData.leerLasDataLazLas(
            self.infileConRuta,
            self.fileCoordYeahDelNombre,
            self.LCLordenColoresInput,
        )
        if not myLasData.myLasHead.readOk:
            print(f'clidhead-> Error al leer el fichero laz en entorno.')
            return False
        # oooooooooo Muestro para verificacion el numero de puntos leidos ooooooooooo
        myLasData.numPuntosValidosTotalesSegunCabecera = self.headDict['numptrecords']
        # print( 'clidhead-> infoLasPoints-> Numero de puntos segun la cabecera del las:', myLasData.numPuntosValidosTotalesSegunCabecera )
        if verbose:
            printMsg(f'{"":=^80}')
            printMsg('clidhead-> infoLasPoints-> Puntos que se indica en la cabecera:   %i puntos' % myLasData.numPuntosValidosTotalesSegunCabecera)
            if GLO.GLBLnumeroDePuntosAleer == 0:
                printMsg('clidhead-> infoLasPoints-> Puntos a leer (segun fichero config):  Todos (GLBLnumeroDePuntosAleer=0)')
            else:
                printMsg('clidhead-> infoLasPoints-> Puntos a leer (segun fichero config):  %i puntos' % GLO.GLBLnumeroDePuntosAleer)
            printMsg('clidhead-> infoLasPoints-> Puntos cargados en la RAM:             %i puntos' % myLasData.numPuntosCargadosEnLaRAM)
            if self.infileConRuta[-4:].lower() == '.las':
                printMsg(
                    'clidhead-> infoLasPoints-> Segun el num de bytes del fichero hay: %0.5f puntos (fichero de %0.2f Mb)'
                    % (
                        ((os.path.getsize(self.infileConRuta) - self.headDict['offset']) / self.pointreclen),
                        os.path.getsize(self.infileConRuta) / 1e6,
                    )
                )
                printMsg(
                    'clidhead-> infoLasPoints->                                        El num de puntos segun num de bytes calculado figura con decimales para ver si cuadra.'
                )
            else:
                printMsg(f'clidhead-> infoLasPoints-> Verificando que es fichero .laz-> infileConRuta: {self.infileConRuta}')

            printMsg(f'clidhead-> infoLasPoints-> Verificando GLBLalmacenarPuntosComoNumpyDtype: {GLO.GLBLalmacenarPuntosComoNumpyDtype}')
            if not GLO.GLBLalmacenarPuntosComoNumpyDtype:
                printMsg(
                    'clidhead-> infoLasPoints-> Segun el num de bytes cargados en memoria, hay: %0.1f puntos' % (len(myLasData.pointsAllFromFile_xtypePFXX) / self.pointreclen)
                )
                printMsg(
                    'clidhead-> infoLasPoints->                                                 = len(myLasData.pointsAllFromFile_xtypePFXX) (%i) / self.pointreclen (%i)'
                    % (len(myLasData.pointsAllFromFile_xtypePFXX), self.pointreclen)
                )
                printMsg(
                    'clidhead-> infoLasPoints->                                                 ->myLasData.pointsAllFromFile_xtypePFXX se lee tras leer la cabecera, con myLasData.infile.read(self.pointreclen*self.numptrecords)'
                )
            if myLasData.numPuntosCargadosEnLaRAM != myLasData.numPuntosValidosTotalesSegunCabecera:
                printMsg('clidhead-> infoLasPoints-> ATENCION: el numero de puntos que se indica en la cabecera no coincide con el numero de puntos en el fichero las.')
            printMsg(f'{"":=^80}')

        pointformat = self.pointformat
        nPtosAleerDefinitivo = self.numptrecords
        miHeadScale = np.array([self.headDict['xscale'], self.headDict['yscale'], self.headDict['zscale']])
        miHeadOffset = np.array([self.headDict['xoffset'], self.headDict['yoffset'], self.headDict['zoffset']])

        if pointformat == 4 or pointformat == 5:
            print('clidhead-> infoLasPoints-> ATENCION:')
            print('clidhead-> infoLasPoints-> Los formatos 4 y 5 incluyen informacion de la waveform y no estan implementados')
            print('clidhead-> infoLasPoints-> Se leen correctamente, pero la informacion de la forma de la onda no se interpreta')
            print('clidhead-> infoLasPoints-> Quitar esto de lasPoint para que funcione sin usar esa informacion')
            sys.exit(0)

        printMsg(f'clidhead-> infoLasPoints-> Verificando nPtosAleerDefinitivo: {nPtosAleerDefinitivo}')
        printMsg(f'clidhead-> infoLasPoints-> Verificando pointsAllFromFile_xtypePFXX.shape: {myLasData.pointsAllFromFile_xtypePFXX.shape}')
        printMsg(f'clidhead-> infoLasPoints-> Verificando pointformat: {self.pointformat}')
        printMsg(f'clidhead-> infoLasPoints-> Verificando formatoDtypePointFormatXXNotacionNpDtype: {self.formatoDtypePointFormatXXNotacionNpDtype}')
        printMsg(f'clidhead-> infoLasPoints-> Verificando miPtoNpRecordPointFormatXX: {type(self.miPtoNpRecordPointFormatXX)}')
        printMsg(f'clidhead-> infoLasPoints-> Verificando miPtoNpRecordPointFormatXX: {self.miPtoNpRecordPointFormatXX}')
        printMsg(f'clidhead-> infoLasPoints-> Verificando formatoDtypePointFormat99NotacionNpDtype: {self.formatoDtypePointFormat99NotacionNpDtype}')
        printMsg(f'clidhead-> infoLasPoints-> Verificando miPtoNpRecordPointFormat99: {type(self.miPtoNpRecordPointFormat99)}')
        printMsg(f'clidhead-> infoLasPoints-> Verificando miPtoNpRecordPointFormat99: {self.miPtoNpRecordPointFormat99}')


        timeIniRecorreLas = time.time()
        (
            recorreLasOk,
            rango_miPto_x,
            rango_miPto_y,
            rango_miPto_z,
            rango_miPto_classification,
            rango_miPto_scan_angle_rank,
            rango_miPto_intensity,
            rango_miPto_point_source_ID,
            rango_miPto_user_data,
            rango_miPto_raw_time,
            rango_miPto_actual_time,
            rango_miPto_red,
            rango_miPto_green,
            rango_miPto_blue,
            rango_miPto_nir,
            rango_return_number,
            rango_return_tot,
            rango_scan_dir,
            rango_scan_edge,
            rango_clas_flags,
            rango_scan_chanl,
            noData_miPto_classification,
            noData_miPto_raw_time,
            noData_miPto_actual_time,
            noData_miPto_red,
            noData_miPto_green,
            noData_miPto_blue,
            noData_miPto_nir,
            noData_miPto_intensity,
            noData_point_source_ID,
            nTotalReturns,
            nFirstReturns,
            nInterReturns,
            nLastReturns,
            nSingleReturns,
            nReturnsPorNumReturn,
            nPuntosPorClase,
        ) = clidnaux.recorreLas(
            myLasData.pointsAllFromFile_xtypePFXX,
            nPtosAleerDefinitivo,
            pointformat,
            miHeadScale,
            miHeadOffset,
            self.miPtoNpRecordPointFormatXX,
            self.miPtoNpRecordPointFormat99,
            LCLordenColoresInput=self.LCLordenColoresInput,
        )

        if not recorreLasOk:
            print('\nNo se ha podido ejecutar recorreLas<>')
            return 0
        # actual_time         -> numero de segundos desde 1970
        # time.localtime(actual_time))
        #    time.struct_time(tm_year=2020, tm_mon=12, tm_mday=14, tm_hour=13, tm_min=34, tm_sec=16, tm_wday=0, tm_yday=349, tm_isdst=0)
        #    year: time.localtime(actual_time)).tm_year = time.localtime(actual_time))[0]
        #    mes: time.localtime(actual_time)).tm_mon = time.localtime(actual_time))[1]
        #    dia del mes: time.localtime(actual_time)).tm_mday = time.localtime(actual_time))[2]
        #    dia del year: time.localtime(actual_time)).tm_yday = time.localtime(actual_time))[7]
        # horaInicio, horaFin -> eso expresado en texto
        try:
            horaInicio = time.asctime(time.localtime(rango_miPto_actual_time[0]))
            horaFin = time.asctime(time.localtime(rango_miPto_actual_time[1]))
        except:
            horaInicio = ''
            horaFin = ''

        superficieEscaneadaEnM2 = (rango_miPto_x[1] - rango_miPto_x[0]) * (rango_miPto_y[1] - rango_miPto_y[0])
        densidadAllReturns = nTotalReturns / superficieEscaneadaEnM2
        densidadFirstReturns = nFirstReturns / superficieEscaneadaEnM2
        densidadLastReturns = nLastReturns / superficieEscaneadaEnM2

        if pointformat <= 5:
            maxNumReturn = 8
        else:
            maxNumReturn = 16

        if GLO.GLBLverbose:
            print('clidhead-> infoLasPoints-> Numero de segundos y siguientes retornos:')
            for numReturn in range(maxNumReturn):
                numReturnAnterior = max(0, numReturn - 1)
                if nReturnsPorNumReturn[numReturnAnterior] > 0:
                    print(nReturnsPorNumReturn[numReturn], end=' ')

        # Cuando GLO.MAINprocedimiento.startswith('CREAR_CAPA_CON_UNA_PROPIEDAD_DE_LOS_FICHEROS_LIDAR')
        if devolverPropiedad:
            if devolverPropiedad.startswith('fechaInicialVuelo'):
                return rango_miPto_actual_time[0]
            elif devolverPropiedad.startswith('fechaFinalVuelo'):
                return rango_miPto_actual_time[1]
            elif devolverPropiedad == 'numMedRt1SinSolape':
                # TODO: pendiente de implementar
                print('\nNo implementado')
                return 0
            elif devolverPropiedad == 'numCeldasConPocosRt1SinSolape':
                # TODO: pendiente de implementar
                print('\nNo implementado')
                return 0
            else:
                print('\nPropiedad no contemplada!')
                sys.exit(0)
                
        if not verbose:
            return


        printMsg('\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        printMsg('clidhead-> infoLasPoints-> Reporting minimum and maximum for all LAS point record entries ...')
        print('X'.rjust(45), str(rango_miPto_x[0]).rjust(12), str(rango_miPto_x[1]).rjust(12))
        print('Y'.rjust(45), str(rango_miPto_y[0]).rjust(12), str(rango_miPto_y[1]).rjust(12))
        print('Z'.rjust(45), str(rango_miPto_z[0]).rjust(12), str(rango_miPto_z[1]).rjust(12))
        print('classification'.rjust(45), str(rango_miPto_classification[0]).rjust(12), str(rango_miPto_classification[1]).rjust(12))
        print('scan_angle_rank'.rjust(45), str(rango_miPto_scan_angle_rank[0]).rjust(12), str(rango_miPto_scan_angle_rank[1]).rjust(12))
        print('intensity'.rjust(45), str(rango_miPto_intensity[0]).rjust(12), str(rango_miPto_intensity[1]).rjust(12))
        print('point_source_ID'.rjust(45), str(rango_miPto_point_source_ID[0]).rjust(12), str(rango_miPto_point_source_ID[1]).rjust(12))
        print('user_data'.rjust(45), str(rango_miPto_user_data[0]).rjust(12), str(rango_miPto_user_data[1]).rjust(12))
        print('raw_time'.rjust(45), str(rango_miPto_raw_time[0]).rjust(12), str(rango_miPto_raw_time[1]).rjust(12))
        print('actual_time'.rjust(45), str(rango_miPto_actual_time[0]).rjust(12), str(rango_miPto_actual_time[1]).rjust(12))
        print('Rango de horas de captura de informacion:')
        print(''.rjust(45), horaInicio)
        print(''.rjust(45), horaFin)
        print('red'.rjust(45), str(rango_miPto_red[0]).rjust(12), str(rango_miPto_red[1]).rjust(12))
        print('green'.rjust(45), str(rango_miPto_green[0]).rjust(12), str(rango_miPto_green[1]).rjust(12))
        print('blue'.rjust(45), str(rango_miPto_blue[0]).rjust(12), str(rango_miPto_blue[1]).rjust(12))
        print('nir'.rjust(45), str(rango_miPto_nir[0]).rjust(12), str(rango_miPto_nir[1]).rjust(12))
        print('return_number'.rjust(45), str(rango_return_number[0]).rjust(12), str(rango_return_number[1]).rjust(12))
        print('return_tot'.rjust(45), str(rango_return_tot[0]).rjust(12), str(rango_return_tot[1]).rjust(12))
        print('scan_dir'.rjust(45), str(rango_scan_dir[0]).rjust(12), str(rango_scan_dir[1]).rjust(12))
        print('scan_edge'.rjust(45), str(rango_scan_edge[0]).rjust(12), str(rango_scan_edge[1]).rjust(12))
        # print( 'clas_flags'.rjust(45), str(rango_clas_flags[0]).rjust(12), str(rango_clas_flags[1]).rjust(12))
        # print( 'scan_chanl'.rjust(45), str(rango_scan_chanl[0]).rjust(12), str(rango_scan_chanl[1]).rjust(12))

        if noData_miPto_classification:
            print('clidhead-> infoLasPoints-> Hay valores negativos (<0) del parametro miPto_classification')
        if noData_miPto_raw_time:
            print('clidhead-> infoLasPoints-> Hay valores nulos o negativos (<=0) del parametro noData_miPto_raw_time')
        if noData_miPto_actual_time:
            print('clidhead-> infoLasPoints-> Hay valores nulos o negativos (<=0) del parametro noData_miPto_actual_time')
        if noData_miPto_red:
            print('clidhead-> infoLasPoints-> Hay valores negativos (<0) del parametro noData_miPto_red')
        if noData_miPto_green:
            print('clidhead-> infoLasPoints-> Hay valores negativos (<0) del parametro noData_miPto_green')
        if noData_miPto_blue:
            print('clidhead-> infoLasPoints-> Hay valores negativos (<0) del parametro noData_miPto_blue')
        if noData_miPto_nir:
            print('clidhead-> infoLasPoints-> Hay valores negativos (<0) del parametro noData_miPto_nir')
        if noData_miPto_intensity:
            print('clidhead-> infoLasPoints-> Hay valores negativos (<0) del parametro noData_miPto_intensity')
        if noData_point_source_ID:
            print('clidhead-> infoLasPoints-> Hay valores negativos (<0) del parametro noData_point_source_ID')
        printMsg(f'{"":=^80}')

        print('clidhead-> infoLasPoints-> Numero de primeros retornos:'.rjust(60), nFirstReturns)
        print('clidhead-> infoLasPoints-> Numero de retornos intermedios:'.rjust(60), nInterReturns)
        print('clidhead-> infoLasPoints-> Numero de ultimos retornos:'.rjust(60), nLastReturns)
        print('clidhead-> infoLasPoints-> Num pulsos con un solo retorno:'.rjust(60), nSingleReturns)
        print('clidhead-> infoLasPoints-> Numero total de retornos:'.rjust(60), nTotalReturns)

        print('clidhead-> infoLasPoints-> Superficie cubierta m2/km2:'.rjust(60), int(superficieEscaneadaEnM2), '/', round(superficieEscaneadaEnM2 / 1e6, 2))

        print(
            'clidhead-> infoLasPoints-> Densidad de puntos-> todos %0.2f primeros: %0.2f ultimos: %0.2f (por m2)'
            % (densidadAllReturns, densidadFirstReturns, densidadLastReturns)
        )
        print(
            'clidhead-> infoLasPoints-> Distancia media entre puntos: todos (metros): %0.2f primeros %0.2f ultimos %0.2f'
            % (1 / np.sqrt(densidadAllReturns), 1 / np.sqrt(densidadFirstReturns), 1 / np.sqrt(densidadLastReturns))
        )
        if nReturnsPorNumReturn[16] > 0:
            print('clidhead-> infoLasPoints-> Atencion: numero de retornos superiores al limite (%i)' % maxNumReturn, end=' ')

        if pointformat <= 5:
            textoClase = [
                'Created, never classified',
                'Unclassified',
                'Ground',
                'Low Vegetation',
                'Medium Vegetation',
                'High Vegetation',
                'Building',
                'Low Point (noise)',
                'Model Key-point (mass point)',
                'Water',
                'Reserved for ASPRS Definition',
                'Reserved for ASPRS Definition',
                'Overlap Points2',
                '13-31 Reserved for ASPRS Definition',
            ]
        else:
            textoClase = [
                'Created, never classified',
                'Unclassified',
                'Ground',
                'Low Vegetation',
                'Medium Vegetation',
                'High Vegetation',
                'Building',
                'Low Point (noise)',
                'Reserved',
                'Water',
                'Rail',
                'Road Surface',
                'Reserved',
                'Wire - Guard (Shield)',
                'Wire - Conductor (Phase)',
                'Transmission Tower',
                'Wire-structure Connector (e.g. Insulator)',
                'Bridge Deck',
                'High Noise',
                '19-63 Reserved',
                '64-255 User definable',
            ]
        if (nPuntosPorClase > 0).any():
            print('\nclidhead-> infoLasPoints-> Histograma de la clasificacion de puntos:')
        else:
            print('\nclidhead-> infoLasPoints-> No hay informacion de la clasificacion de puntos.')
        for nClase in range(len(nPuntosPorClase)):
            if nPuntosPorClase[nClase] > 0:
                if pointformat <= 5:
                    if nClase < 13:
                        print(str(nPuntosPorClase[nClase]).rjust(16), '%s (%i)' % (textoClase[nClase], nClase))
                    elif nClase < 32:
                        print(str(nPuntosPorClase[13]).rjust(16), '%s (%i)' % (textoClase[13], 13))
                    else:
                        print('clidhead-> infoLasPoints-> Clase %i no permitida' % nClase)
                else:
                    if nClase < 19:
                        print(str(nPuntosPorClase[nClase]).rjust(16), '%s (%i)' % (textoClase[nClase], nClase))
                    elif nClase < 64:
                        print(str(nPuntosPorClase[nClase]).rjust(16), '%s (%i)' % (textoClase[19], nClase))
                    elif nClase < 256:
                        print(str(nPuntosPorClase[nClase]).rjust(16), '%s (%i)' % (textoClase[20], nClase))
                    else:
                        print('clidhead-> infoLasPoints-> Clase %i no permitida' % nClase)
        printMsg(f'{"":=^80}')

        timeFinRecorreLas = time.time()
        horaFin = time.asctime(time.localtime(timeFinRecorreLas))
        segundosDuracion = round((timeFinRecorreLas - timeIniRecorreLas), 2)
        minutosDuracion = round(segundosDuracion / 60.0, 2)
        print(
            'clidhead.%06i-> Fin de recopilacion de info de %s'
            % (GLO.MAIN_idProceso, os.path.basename(self.infileConRuta))
        )
        print(
            'clidhead.{:006}-> Tiempo de lectura:\t{:0.2}\tsegundos ({:0.2f} minutos).'.format(
                GLO.MAIN_idProceso, segundosDuracion, minutosDuracion
            )
        )
        print(
            'clidhead.{:006}-> Fecha/hora:\t{}'.format(
                GLO.MAIN_idProceso, horaFin
                )
        )
        printMsg(f'{"":=^80}')


# ==============================================================================
def lasHeadProperties():
    """
    Read las head file properties from lasHeadFields.cfg file with configparser.
    Fields at PUBLIC HEADER BLOCK of a las file:
        [LasFormat_1_2]                                  -> type 1.2 (LAS Specification Version 1.2 Approved by ASPRS Board 09/02/2008)
        [LasFormat_1_2]+[LasFormat_1_3]                  -> type 1.3 (LAS Specification Version 1.3 - R11 24 October 2010)
        [LasFormat_1_2]+[LasFormat_1_3]+[LasFormat_1_4]  -> type 1.4 (LAS Specification Version 1.4 - R13 15 July 2013)
    ATTENTION: Only tested with type 1.2 of Spanish PNOA Lidar
    oututs:
        lasHeaderFieldListVersionsDict: Dictionary with keys = versionName and values = list fields in that version
        lasHeaderFieldPropertiesDict: Dictionary with keys = fieldName and values = list of properties + versionName
        lasHeaderFieldPropertiesList: List of fieldNames + FieldProperties
    """
    directorioDeTrabajo = buscarDirectorioDataExt()
    configFileName = os.path.join(directorioDeTrabajo, 'io/lasHeadFields.cfg')
    if not os.path.exists(configFileName):
        print(f'\nclidhead-> ATENCION: no se encuentra el fichero {configFileName}')
        print(f'{TB}-> No se escriben los Variable Length Records')
        print(f'{TB}-> Revisar codigo o disponibilidad de este fichero; se interrumpe la ejecucion de cartolidar.')
        sys.exit(0)
    config = RawConfigParser()
    config.optionxform = str  # Avoid change to lowercase
    config.read(configFileName)
#     try:
#         config.read(configFileName)
#     except:
#         print('Error al leer configFileName:', configFileName)
#         configFileName = os.path.join(directorioDeTrabajo, 'io/lasHeadFieldsNew.cfg')
#         myFile = open(configFileName, 'w')
#         myFile.write('[LasFormat_1_2]')
#         myFile.write('filesignature = 4, c, 4')
#         myFile.close()
#         sys.exit(0)
    versionList = config.sections()
    lasHeaderFieldListVersionsDict = {}
    lasHeaderFieldPropertiesDict = {}
    lasHeaderFieldPropertiesList = []
    for myVersion in versionList:
        fieldList = config.options(myVersion)
        lasHeaderFieldListVersionsDict[myVersion] = fieldList
        for myField in fieldList:
            properties = config.get(myVersion, myField).split(',')
            # properties.append(myVersion)
            lasHeaderFieldPropertiesDict[myVersion + '_' + myField] = properties
            fieldVersionNameProperties = [myVersion]
            fieldVersionNameProperties.extend([myField])
            fieldVersionNameProperties.extend(properties)
            lasHeaderFieldPropertiesList.append(fieldVersionNameProperties)
    return (
        lasHeaderFieldListVersionsDict,
        lasHeaderFieldPropertiesDict,
        lasHeaderFieldPropertiesList
    )


# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
# Para conocer los formatos que usa struct.unpack(fmt, string) y struct.pack(fmt, v1, v2, ...)
# Ver https://docs.python.org/2/library/struct.html o miAyuda.py
def lasPointProperties(
        pointformat=3,
        extraBytesPorRegistro=0,
        verbose=False
    ):
    """
    Ver:
        https://docs.python.org/3/library/struct.html
            x pad byte no value (7)
            c char bytes of length       1 bytes
            b signed char integer        1 bytes (1), (2)
            B unsigned char integer      1 bytes (2)
            ? _Bool bool                 1 bytes (1)
            h short integer              2 bytes (2)
            H unsigned short integer     2 bytes (2)
            i int integer                4 bytes (2)
            I unsigned int integer       4 bytes (2)
            l long integer               4 bytes (2)
            L unsigned long integer      4 bytes (2)
            q long long integer          8 bytes (2)
            Q unsigned long long integer 8 bytes (2)
            n ssize_t integer                    (3)
            N size_t integer                     (3)
            e (6) float                  2 bytes (4)
            f float float                4 bytes (4) 
            d double float               8 bytes (4)
            s char[] bytes                       (9)
            p char[] bytes                       (8)
            P void* integer                      (5)

            Character Byte order             Size       Alignment
            @         native                 native     native
            =         native                 standard   none
            <         little-endian          standard   none
            >         big-endian             standard   none
            !         network (= big-endian) standard   none

        https://numpy.org/doc/stable/reference/arrays.dtypes.html
        Buscar: One-character strings:
            '?' boolean
            'b' (signed) byte
            'B' unsigned byte
            'i' (signed) integer
            'u' unsigned integer
            'f' floating-point
            'c'complex-floating point
            'm' timedelta
            'M' datetime
            'O' (Python) objects
            'S', 'a' zero-terminated bytes (not recommended)
            'U' Unicode string
            'V' raw data (void)

Read las point properties from lasPointFields.cfg file with configparser.
    Point formats 1-4 and 6-10
    ATENTION: Only tested with point format 3 and 8 of Spanish PNOA Lidar (lasFile version 1.2)
    #TODO point fotmat 8 (in progress)
    oututs:
        lasPointFieldPropertiesDict: Dictionary with keys = fieldName and values = list of properties + versionName
        lasPointFieldPropertiesList: List of lasVersion + fieldNames + FieldProperties
    Codigo de una letra de las propiedades del punto
        b    98     blue
        c    99     classification
        1    49     extra_1    <-
        2    50     extra_2    <-
        e    101    extra_grp
        g    103    green
        I    73     int_grp    <-
        i    105    intensity
        N    78     nir
        o    111    offsetToWaveformData
        p    112    point_source_ID
        t    116    raw_time    <-
        r    114    red
        m    109    resto    <-
        n    110    return_grp
        R    82     ReturnPointWaveformLocation
        s    115    scan_angle_rank
        u    117    user_data
        W    87     WaveformPacketSize
        w    119    WavePacketDescriptorIndex    <-
        x    120    x
        X    88     X_t
        y    121    y
        Y    89     Y_t
        z    122    z
        Z    90     Z_t
    """
    directorioDeTrabajo = buscarDirectorioDataExt()
    configFileName = os.path.join(directorioDeTrabajo, 'io/lasPointFields.cfg')
    if not os.path.exists(configFileName):
        print('clidhead-> ATENCION: Falta', configFileName, 'Corregir')
        sys.exit()
    # print( 'clidhead-> No se escriben los Variable Length Records')
    strPointFormat = 'PointFormat_{}'.format(pointformat)
    config = RawConfigParser()
    config.optionxform = str  # Avoid change to lowercase
    config.read(configFileName)
    pointFormatList = config.sections()
    # if verbose or True:
    #     printMsg('clidhead-> Verificando si esta implementado strPointFormat>: {}'.format(strPointFormat))
    #     if strPointFormat in pointFormatList:
    #         printMsg('\n-> Point format {} ok'.format(strPointFormat))

    if not strPointFormat in pointFormatList:
        printMsg('clidhead-> PointFormat: {}'.format(strPointFormat))
        printMsg('clidhead-> Point format {} no implementado. pointFormatList: {}'.format(strPointFormat, str(pointFormatList)))
        sys.exit(1)
    lasPointFieldOrdenDictPtoComp = {}
    lasPointFieldOrdenDictPtoMini = {}
    lasPointFieldPropertiesDict = {}
    lasPointFieldPropertiesList = []
    fieldList = config.options(strPointFormat)
    nOrden = 0
    for myField in fieldList:
        lasPointFieldOrdenDictPtoComp[myField] = nOrden
        properties = config.get(strPointFormat, myField).split(',')
        properties[0] = int(properties[0])  # convert str to int -> num de bytes
        properties[1] = properties[1].strip()  # remove whitespaces -> tipo de dato (b, B, H, d, =L, etc)
        properties[2] = int(properties[2])  # convert str to int -> num de repeticiones (si es array)
        properties[3] = int(properties[3])  # convert str to int -> posicion del primer byte empezando en 0
        properties[4] = properties[4].strip()  # remove whitespaces -> letra identificativa de la propiedad (etiqueta)
        numeroBytesAcum = properties[3] + (properties[0] * properties[2])
        # Lo guardo como dict:
        lasPointFieldPropertiesDict[myField] = tuple(properties)
        # Lo guardo como lista, con el primer valor el nombre de la propiedad
        myList = [myField]
        myList.extend(properties)
        lasPointFieldPropertiesList.append(tuple(myList))
        nOrden += 1
    if (
        extraBytesPorRegistro != 0
        and strPointFormat != 'PointFormat_99'
        and strPointFormat != 'PointFormat_100'
        and strPointFormat != 'PointFormat_101'
        and strPointFormat != 'PointFormat_102'
    ):
        myField = 'extraBytesPorRegistro'
        properties[0] = extraBytesPorRegistro #  -> num de bytes
        properties[1] = 'B' #  -> tipo de dato (b, B, H, d, =L, etc)
        properties[2] = extraBytesPorRegistro  #  -> num de repeticiones (si es array)
        properties[3] = numeroBytesAcum  #  -> posicion del primer byte empezando en 0
        properties[4] = 'x' #  -> letra identificativa de la propiedad (etiqueta)
        # Lo guardo como dict:
        lasPointFieldPropertiesDict[myField] = tuple(properties)
        # Lo guardo como lista, con el primer valor el nombre de la propiedad
        myList = [myField]
        myList.extend(properties)
        lasPointFieldPropertiesList.append(tuple(myList))

    # ->Si quisiera trabajar con menos propiedades puedo seleccionarlas aqui:
    #  Este orden es el complemento al diccionario lasPointFieldPropertiesDict
    lasPointFieldOrdenDictPtoMini['x'] = 0
    lasPointFieldOrdenDictPtoMini['y'] = 1
    lasPointFieldOrdenDictPtoMini['z'] = 2
    lasPointFieldOrdenDictPtoMini['return_grp'] = 3
    lasPointFieldOrdenDictPtoMini['classification'] = 4
    lasPointFieldOrdenDictPtoMini['scan_angle_rank'] = 5
    lasPointFieldOrdenDictPtoMini['point_source_ID'] = 6

    return lasPointFieldPropertiesList, lasPointFieldPropertiesDict, lasPointFieldOrdenDictPtoMini, lasPointFieldOrdenDictPtoComp


# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
def lasVlrProperties():
    """
    Read Crs and other file properties from lasHeadVlr.cfg file with configparser.
    oututs:
        lasCrsKeyListsDict: Dictionary with keys = group and values = key list in that group
        lasCrsPropertiesDict: Dictionary with keys = fieldName and values = list of properties + versionName
        lasCrsPropertiesList: List of fieldNames + FieldProperties
    """
    directorioDeTrabajo = buscarDirectorioDataExt()
    configFileName = os.path.join(directorioDeTrabajo, 'io/lasHeadVlr.cfg')
    if not os.path.exists(configFileName):
        print('clidhead-> ATENCION: Falta', configFileName, 'Corregir')
        print('clidhead-> No se escriben los Variable Length Records')
    config = RawConfigParser()
    config.optionxform = str  # Avoid change to lowercase
    config.read(configFileName)
    myGrupos = config.sections()
    lasCrsKeyListsDict = {}
    lasCrsPropertiesDict = {}
    lasCrsPropertiesList = []
    for myGrupo in myGrupos:
        fieldList = config.options(myGrupo)
        lasCrsKeyListsDict[myGrupo] = fieldList
        for myField in fieldList:
            properties = config.get(myGrupo, myField).split(',')
            # properties.append(myGrupo)
            lasCrsPropertiesDict[myGrupo + '_' + myField] = properties
            fieldVersionNameProperties = [myGrupo]
            fieldVersionNameProperties.extend([myField])
            fieldVersionNameProperties.extend(properties)
            lasCrsPropertiesList.append(fieldVersionNameProperties)
    return lasCrsKeyListsDict, lasCrsPropertiesDict, lasCrsPropertiesList


# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
def crearArraysPropPto(pointformat, lasPointFieldPropertiesList=None, propIndividuales=True):
    # print('clidhead-> (z) Llamando a lasPointProperties con {}'.format(pointformat))
    if lasPointFieldPropertiesList is None:
        lasPointFieldPropertiesList, _, _, _ = lasPointProperties(pointformat)

    numCaracteresPropiedad = 30
    # Convierto lasPointFieldPropertiesList en un ndarray npArrayPropPto cuyos elementos son Records con una estructura de datos propPtoDtype
    # https://docs.python.org/3/library/array.html#module-array
    propPtoDtype = np.dtype(
        [
            ('Orden', 'H'),
            ('Letra', '|S1'),
            ('Ascii', 'B'),
            ('Nombre', '|S30'),
            ('byteArrayNombre', '=B', (30,)),
            ('nBytes', '=H'),
            ('Formato', '|S2'),
            ('nValores', '=H'),
            ('primerByte', '=H'),
        ]
    )
    npArrayPropPto = np.empty(len(lasPointFieldPropertiesList), dtype=np.dtype(propPtoDtype))
    # Por si acaso creo estas otras ndarrays con tipos de datos separados:
    #    El nombre de la propiedad con dos versiones: str y bytearray
    #    El tipo de dato en str de 2 char
    #    nBytes, nValores (multiplicidad) y primerByte en una ndarray con tres valores de tipo byte por registro
    byteArrayPropPtoNombre = np.empty(len(lasPointFieldPropertiesList) * numCaracteresPropiedad, dtype='int8').reshape(
        len(lasPointFieldPropertiesList), numCaracteresPropiedad
    )
    arrayPropPtoNombre = np.empty(len(lasPointFieldPropertiesList), dtype='|S%i' % numCaracteresPropiedad)
    arrayPropPtoRangoBytes = np.zeros(len(lasPointFieldPropertiesList) * 3, dtype=np.byte).reshape(len(lasPointFieldPropertiesList), 3)
    arrayPropPtoTipoDato = np.empty(len(lasPointFieldPropertiesList), dtype='|S2')
    for microContador in range(len(lasPointFieldPropertiesList)):
        nombrePropiedadPadl = lasPointFieldPropertiesList[microContador][0].ljust(numCaracteresPropiedad, ' ')
        npArrayPropPto[microContador]['Orden'] = microContador
        npArrayPropPto[microContador]['Letra'] = lasPointFieldPropertiesList[microContador][5]
        npArrayPropPto[microContador]['Ascii'] = ord(lasPointFieldPropertiesList[microContador][5])
        npArrayPropPto[microContador]['Nombre'] = nombrePropiedadPadl
        npArrayPropPto[microContador]['byteArrayNombre'] = bytearray(nombrePropiedadPadl, 'latin-1')
        npArrayPropPto[microContador]['nBytes'] = lasPointFieldPropertiesList[microContador][1]
        npArrayPropPto[microContador]['Formato'] = lasPointFieldPropertiesList[microContador][2]
        npArrayPropPto[microContador]['nValores'] = lasPointFieldPropertiesList[microContador][3]
        npArrayPropPto[microContador]['primerByte'] = lasPointFieldPropertiesList[microContador][4]
        byteArrayPropPtoNombre[microContador] = bytearray(nombrePropiedadPadl, 'latin-1')
        arrayPropPtoNombre[microContador] = lasPointFieldPropertiesList[microContador][0]
        arrayPropPtoRangoBytes[microContador] = [
            lasPointFieldPropertiesList[microContador][1],
            lasPointFieldPropertiesList[microContador][3],
            lasPointFieldPropertiesList[microContador][4],
        ]
        arrayPropPtoTipoDato[microContador] = lasPointFieldPropertiesList[microContador][2]

    # Se puede obtener una tupla con todas las caracteristicas, por ejemplo de la primera propiedad del punto (x):
    # print(npArrayPropPto[0])
    # Se puede acceder al nombre de esa propiedad de dos formas (la segunda no funciona con numba):
    # print(npArrayPropPto[1]['Nombre'])
    # print(npArrayPropPto[1][0]) #(no funciona con numba)

    return npArrayPropPto, byteArrayPropPtoNombre, arrayPropPtoNombre, arrayPropPtoRangoBytes, arrayPropPtoTipoDato


# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
# Esta funcion es la original; antes tb la tenia duplicada en clidbase.py
def getFileCoordFromName(
        infile,
        fileYearPorDefecto='0000'
    ):
    fileCoordDelNombre = '000_0000'
    fileYearDelNombre = 'AAAA'
    for char1 in range(len(infile) - 4 - 8 + 1):
        # fileCoordDelNombre_ = infile[char1: char1 + 3] + '_' + infile[char1 + 4: char1 + 8]
        if (
            (infile[char1: char1 + 4]).isdigit()
            and (char1 < 4 or not (infile[char1 - 4: char1 - 1]).isdigit()) #-> Si ocurriera esto ultimo, los cuatro digitos son la coord Y
            and (char1 == 0 or (infile[char1 - 1]) in ['-', '_'])
            and (infile[char1 + 4]) in ['-', '_', '.']
        ):
            # Los 4 digitos siguientes son la anualidad cuando El fichero tiene la anualidad pero no las coordenadas cuando:
            #     Son 4 digitos pero no precedidos por _ y 3 digitos (no son los YYYY de XXX_YYYY)
            #     Y estan precedidos y seguidos por '_' o '-' o '.' (salvo que sean los 4 primeros o 4 ultimos)
            # fileCoordDelNombre = '000_0000'
            fileYearDelNombre = infile[char1: char1 + 4]
        elif (
            (infile[char1: char1 + 3]).isdigit()
            and (infile[char1 + 4: char1 + 8]).isdigit()
            and (infile[char1 + 3]) in ['-', '_']
            and (char1 == 0 or (infile[char1 - 1]) in ['-', '_'])
            and (infile[char1 + 8]) in ['-', '_', '.']
        ):
            # El fichero tiene las coordenadas cuando:
            #    El nombre incluye el patron XXX_YYYY o XXX-YYYY
            #     Y estan precedidos y seguidos por '_' o '-' (salvo que sean los 4 primeros o 4 ultimos)
            fileCoordDelNombre = infile[char1: char1 + 3] + '_' + infile[char1 + 4: char1 + 8]
            # Ademas tiene la anualidad si despues de las coordenadas:
            #     Hay cuatro caracteres digitos
            #     Y estan precedidos y seguidos por '_' o '-'
            # Si no tengo ya el year, lo busco a continuacion
            if fileYearDelNombre == 'AAAA':
                fileYearDelNombre = '0000'
            if len(infile) - 4 - 4 > char1 + 9:
                for char2 in range(char1 + 9, len(infile) - 4 - 4):
                    if (
                        (infile[char2: char2 + 4]).isdigit()
                        and (infile[char2 - 1]) in ['-', '_']
                        and (infile[char2 + 4]) in ['-', '_', '.']
                    ):
                        fileYearDelNombre = infile[char2: char2 + 4]
                        break
            break

    if fileYearDelNombre == '0000' or fileYearDelNombre == 'AAAA':
        fileYearDelNombre = fileYearPorDefecto

    if GLO.GLBLincluirYearEnFileCoordYear:
        fileCoordYearDelNombre = fileCoordDelNombre + '_' + str(fileYearDelNombre)
    else:
        fileCoordYearDelNombre = fileCoordDelNombre

    try:
        xSupIzdaDelNombre = int(fileCoordDelNombre[:3]) * 1000
        ySupIzdaDelNombre = int(fileCoordDelNombre[4:8]) * 1000
        # print( 'clidhead-> xSupIzda, ySupIzda (de acuerdo al nombre del fichero)        ', xSupIzdaDelNombre, ySupIzdaDelNombre )
    except:
        xSupIzdaDelNombre = 0
        ySupIzdaDelNombre = 0

    return fileCoordYearDelNombre, xSupIzdaDelNombre, ySupIzdaDelNombre, fileYearDelNombre


# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
class NewLasHeadClass(object):
    """
    classdocs
    """

    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def __init__(
        self,
        myOldLasHead=None,
        newLasFileNameConRuta='newLASF',
        TRNShuso29=False,
        vermajor=1,
        verminor=4,
        pointformat=8,
        numptrecords=0,
        numptbyreturn=np.zeros(GLO.GLBLnumeroMaximoDeRetornosPorPulso, dtype=np.int64),
        xmin=0,
        ymin=0,
        xmax=0,
        ymax=0,
        zmin=0,
        zmax=0,
        xscale=0,
        yscale=0,
        zscale=0,
        xoffset=-9999,
        yoffset=-9999,
        zoffset=-9999,
        GPSTimeType='',
        CRS='WKT',
        filesourceid=0,
        guid1=0,
        guid2=0,
        guid3=0,
        guid4=np.zeros(8, dtype=np.uint8),
        sysid='OTHER',
        fileday=0,
        fileyear=0,
        headersize=0,
        offset=0,
        numvlrecords=0,
        pointreclen=0,
        waveformStart=0,
        extendedVLRstart=0,
        extendedVLRnValues=0,
        verbose=False,
    ):
        if vermajor != 1 or verminor not in [2, 3, 4]:
            print('clidhead-> Las Format no implementado')
            quit()

        self.TRNShuso29 = TRNShuso29
        # ======================================================================
        self.myOldLasHead = myOldLasHead
        self.newLasFileNameConRuta = newLasFileNameConRuta
        self.vermajor = vermajor
        self.verminor = verminor
        self.lasVersion = 'LasFormat_%i_%i' % (vermajor, verminor)
        self.pointformat = pointformat
        # ======================================================================
        if self.vermajor != 1:
            print('clidhead-> Version de las (%i) no implementada' % self.vermajor)
            quit()

        self.verbose = verbose
        self.filesignature = 'LASF'
        # self.miSoftware = f'CartoLid v{__version__} {GLO.MAIN_copyright}'
        self.miSoftware = f'CartoLid v{__version__}'
        self.gensoftware = self.miSoftware[:31].ljust(32, '\x00')
        if verbose:
            print(f'clidhead-> Software original: {self.myOldLasHead.headDict["gensoftware"]}')
            nuevoSoftware = self.gensoftware.rstrip('\x00') # No se permite \ dentro del f-format
            print(f'clidhead-> Nuevo Software:    {nuevoSoftware}')

        # ======================================================================
        # Uso estos valores para:
        #    Numero de puntos:
        #        Original y legacy    -> numptrecords = 4, =L, 1
        #        New in lasFormat 1.4 -> pointrecords = 8, Q, 1
        #    Numero de retornos por pulso:
        #        Original y legacy    -> numptbyreturn = 20, L, 5
        #        New in lasFormat 1.4 -> pointsbyreturn = 120, Q, 15
        # Notas sobre pointrecords y pointsbyreturn
        # pointrecords
        # Number of point records: This field contains the total number of point records in the file.  Note
        # that this field must always be correctly populated, regardless of legacy mode intent.
        # pointsbyreturn
        # Number of points by return: These fields contain an array of the total point records per return.
        # The first value will be the total number of records from the first return, the second contains the
        # total number for return two, and so on up to fifteen returns.  Note that these fields must always be
        # correctly populated, regardless of legacy mode intent.
        # ======================================================================
        # Si estos valores son nulos, ya se rellenan a partir de aCeldasListaDePtosTlcPralPF99 en lasLax.
        # No heredo los valores de myOldLasHead porque no son los correctos (puede haber mas puntos)
        self.numptrecords = numptrecords
        self.pointrecords = numptrecords  # Para LASF 1.4
        self.numptbyreturn = numptbyreturn
        self.pointsbyreturn = numptbyreturn  # Para LASF 1.4
        # ======================================================================

        # ======================================================================
        if xmin == 0 and ymin == 0 and not self.myOldLasHead is None:
            self.xminBloqueMalla = self.myOldLasHead.xminBloqueMalla
            self.yminBloqueMalla = self.myOldLasHead.yminBloqueMalla
        else:
            self.xminBloqueMalla = xmin
            self.yminBloqueMalla = ymin

        if xmax == 0 and ymax == 0 and not self.myOldLasHead is None:
            self.xmaxBloqueMalla = self.myOldLasHead.xmaxBloqueMalla
            self.ymaxBloqueMalla = self.myOldLasHead.ymaxBloqueMalla
        else:
            self.xmaxBloqueMalla = xmax
            self.ymaxBloqueMalla = ymax

        if zmin == 0 and zmax == 0 and not self.myOldLasHead is None:
            self.zmin = self.myOldLasHead.zmin
            self.zmax = self.myOldLasHead.zmax
        else:
            self.zmin = zmin
            self.zmax = zmax
        # ======================================================================

        if self.TRNShuso29:
            LCLorigenDeCoordenadasX = GLO.GLBLorigenDeCoordenadasH29X
            LCLorigenDeCoordenadasY = GLO.GLBLorigenDeCoordenadasH29Y
        else:
            LCLorigenDeCoordenadasX = GLO.GLBLorigenDeCoordenadasH30X
            LCLorigenDeCoordenadasY = GLO.GLBLorigenDeCoordenadasH30Y

        sizeToAdjust = 1.0
        if (
            'LAS_INFO' in GLO.MAINprocedimiento
            or 'LAS_EDIT' in GLO.MAINprocedimiento
            or 'PASADAS' in GLO.MAINprocedimiento
        ):
            print(f'\nclidhead-> No se hace el ajuste de las celdas a la malla satelital por estar ejecutando el procedimiento: {GLO.MAINprocedimiento}')
        else:
            self.adjustCornersCoordinates(
                sizeToAdjust,
                envolvente=True,
                margenAdmisible=sizeToAdjust * 0.01,
                LCLorigenDeCoordenadasX=LCLorigenDeCoordenadasX,
                LCLorigenDeCoordenadasY=LCLorigenDeCoordenadasX,
            )
        if self.verbose:
            print('\nclidhead-> Ajustando esquinas a {} m'.format(1))
            print('clidhead->   xmin, xmax, ymin, ymax:', self.xminBloqueMalla, self.xmaxBloqueMalla, self.yminBloqueMalla, self.ymaxBloqueMalla)
        self.xminBloqueMalla = xmin
        self.yminBloqueMalla = ymin
        self.xmaxBloqueMalla = xmax
        self.ymaxBloqueMalla = ymax

        # ======================================================================
        if xscale == 0 and not self.myOldLasHead is None:
            self.xscale = self.myOldLasHead.xscale
        elif xscale == 0:
            self.xscale = 0.01
        else:
            self.xscale = xscale

        if yscale == 0 and not self.myOldLasHead is None:
            self.yscale = self.myOldLasHead.yscale
        elif yscale == 0:
            self.yscale = 0.01
        else:
            self.yscale = yscale

        if zscale == 0 and not self.myOldLasHead is None:
            self.zscale = self.myOldLasHead.zscale
        elif zscale == 0:
            self.zscale = 0.01
        else:
            self.zscale = zscale
        # ======================================================================
        if xoffset != -9999:
            self.xoffset = xoffset
        else:
            if not self.myOldLasHead is None:
                self.xoffset = self.myOldLasHead.xoffset
            else:
                self.xoffset = 0

        if yoffset != -9999:
            self.yoffset = yoffset
        else:
            if not self.myOldLasHead is None:
                self.yoffset = self.myOldLasHead.yoffset
            else:
                self.yoffset = 0
        if zoffset != -9999:
            self.zoffset = zoffset
        else:
            if not self.myOldLasHead is None:
                self.zoffset = self.myOldLasHead.zoffset
            else:
                self.zoffset = 0
        # ======================================================================

        if self.verbose:
            print('------------------->clidhead-> self.xscale:', self.xscale, 'xscale:', xscale)
            print('------------------->clidhead-> self.xoffset:', self.xoffset, 'yoffset:', yoffset)

        # ======================================================================
        if GPSTimeType == '' and not self.myOldLasHead is None:
            gpstimetype = myOldLasHead.globalencoding & 1
        else:
            if gpstimetype == 'weektime':
                gpstimetype = 0
            elif gpstimetype == 'standardMinus10^9':
                gpstimetype = 1
        if verbose:
            print('clidhead-> gpstimetype:', gpstimetype, '-> globalencoding orig:', myOldLasHead.globalencoding, 'Bit menos significativo del globalencoding (el de la derecha: & 1):', myOldLasHead.globalencoding & 1)

        if CRS == '' and not self.myOldLasHead is None:
            crs = (myOldLasHead.globalencoding >> 4) & 1
        else:
            if (CRS == 'GeoTIFF' and self.pointformat < 5) or self.verminor < 4:
                crs = 0
            elif CRS == 'WKT' or True:
                crs = 1
        if self.verminor < 4:
            crs = 0
            self.formatoSRS = 'GeoTIFF'
        else:
            # Para el LASF 1.4:
            #    Para pointformat <= 5 -> Se puede elegir WKT o GeoTIFF
            #    Para pointformat >= 6 -> WKT es obligatorio
            if self.pointformat < 5 and crs == 0:
                self.formatoSRS = 'GeoTIFF'
            else:
                self.formatoSRS = 'WKT'
                crs = 1

        # Convierto la cadena que expresa el numero en binario, en numero, indicando que esta en base 2
        if self.verminor < 4:
            crs = 0
            waveformDataPacketsInternal = 0
            waveformDataPacketsExternal = 0
            returnNumbersSyntheticallyGenerated = 0
        else:
            waveformDataPacketsInternal = 0
            if self.pointformat == 9 or self.pointformat == 10:
                # Formatos d epuntos que admiten WaveformPacke
                waveformDataPacketsExternal = 1
            else:
                waveformDataPacketsExternal = 0
            returnNumbersSyntheticallyGenerated = 0
        self.globalencoding = int(
            '0b00000000000%i%i%i%i%i' % (crs, returnNumbersSyntheticallyGenerated, waveformDataPacketsExternal, waveformDataPacketsInternal, gpstimetype), 2
        )
        # print( 'clidhead-> self.formatoSRS', self.formatoSRS, crs)
        # print( 'clidhead-> self.globalencoding', self.globalencoding, CRS, gpstimetype)
        # input('pulsa')
        # ======================================================================

        # ======================================================================
        if filesourceid == 0 and not self.myOldLasHead is None:
            self.filesourceid = self.myOldLasHead.filesourceid
        else:
            self.filesourceid = filesourceid

        if (guid1 == 0 and guid2 == 0 and guid3 == 0 and np.all(guid4 == 0)) and not self.myOldLasHead is None:
            self.guid1 = self.myOldLasHead.guid1
            self.guid2 = self.myOldLasHead.guid2
            self.guid3 = self.myOldLasHead.guid3
            self.guid4 = self.myOldLasHead.guid4
        else:
            self.guid1 = guid1
            self.guid2 = guid2
            self.guid3 = guid3
            self.guid4 = guid4

        if sysid == '' and not self.myOldLasHead is None:
            self.sysid = self.myOldLasHead.sysid
        else:
            self.sysid = sysid
        # ======================================================================

        # ======================================================================
        if fileday == 0 and not self.myOldLasHead is None:
            self.fileday = self.myOldLasHead.fileday
        elif fileday == 0:
            today_dayOfyear = time.localtime(time.time())[7]
            self.fileday = today_dayOfyear
        else:
            self.fileday = fileday

        if fileyear == 0 and not self.myOldLasHead is None:
            self.fileyear = self.myOldLasHead.fileyear
        elif fileyear == 0:
            today_year = time.localtime(time.time())[0]
            self.fileyear = today_year
        else:
            self.fileyear = fileyear
        # ======================================================================

        # ======================================================================
        # Campos que componen la cabecera para Las format version 1.2, 1.3 y 1.4 en dicts y lista.
        # Se leen las propiedades de cabecera de todos los formatos de lasFile (lasHeadFields.cfg)
        (
            self.lasHeaderFieldListVersionsDict,
            self.lasHeaderFieldPropertiesDict,
            self.lasHeaderFieldPropertiesList
        ) = lasHeadProperties()
        # ======================================================================
        # Size of Las Head (num bytes):
        lasVersion = 'LasFormat_1_%i' % self.verminor
        nuevoHeaderSize = 0
        if self.verminor >= 2:
            lasVersion = 'LasFormat_1_2'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersion]:
                # Lista ordenada de campos para cada version de Las Format
                fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersion + '_' + myField]
                nuevoHeaderSize += int(fieldProperties[0])
                if self.verbose:
                    print(TB, lasVersion, myField, 'nuevoHeaderSize', nuevoHeaderSize)
        if self.verminor >= 3:
            lasVersion = 'LasFormat_1_3'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersion]:
                # Lista ordenada de campos para cada version de Las Format
                fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersion + '_' + myField]
                nuevoHeaderSize += int(fieldProperties[0])
                if self.verbose:
                    print(TB, lasVersion, myField, 'nuevoHeaderSize', nuevoHeaderSize)
        if self.verminor >= 4:
            lasVersion = 'LasFormat_1_4'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersion]:
                # Lista ordenada de campos para cada version de Las Format
                fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersion + '_' + myField]
                nuevoHeaderSize += int(fieldProperties[0])
                if self.verbose:
                    print(TB, lasVersion, myField, 'nuevoHeaderSize', nuevoHeaderSize)
        if (self.verminor == 2 and nuevoHeaderSize != 227) or (self.verminor == 4 and nuevoHeaderSize != 375):
            print('clidhead-> Revisar la definicion la cabecera del forma 1.%i en lasHeadFields.cfg' % self.verminor)
            print('clidhead-> La cabecera tiene %i bytes y deberia tener %i' % (nuevoHeaderSize, 227 if self.verminor == 2 else 375))
            input('clidhead-> Pulsa una tecla')
        self.headersize = nuevoHeaderSize
        # ======================================================================

        # ======================================================================
        # No se puede pasar un np.dtype() como self.formatoDtypeIdValNotacionNpDtype como argumento a una funcion Numba
        # self.formatoDtypeIdValNotacionNpDtype = np.dtype([ ('Id', '=h', 1), ('Val', '=l', 1)]) #h: short integer (2bytes); l: long integer (4 bytes)
        self.formatoDtypeIdValNotacionNpDtype = np.dtype([('Id', '=h'), ('Val', '=l')])  # h: short integer (2bytes); l: long integer (4 bytes)
        # ======================================================================


        # ======================================================================
        # Leo las propiedades del punto de mi pointFormat en lasPointFields.cfg
        # print('clidhead-> (k) Llamando a lasPointProperties con {}'.format(self.pointformat))
        (
            self.lasPointFieldPropertiesList,
            self.lasPointFieldPropertiesDict,
            self.lasPointFieldOrdenDictPtoMini,
            self.lasPointFieldOrdenDictPtoComp,
        ) = lasPointProperties(
            self.pointformat,
            # extraBytesPorRegistro=self.myOldLasHead.headDict['extraBytesPorRegistro'],
            extraBytesPorRegistro=0,
            verbose=self.verbose,
        )
        # Esto otro para facilitar el acceso a las propiedades desde funciones numba
        self.npArrayPropPto, self.bytearrayPropPtoNombre, self.arrayPropPtoNombre, self.arrayPropPtoRangoBytes, self.arrayPropPtoTipoDato = crearArraysPropPto(
            self.pointformat,
            lasPointFieldPropertiesList=self.lasPointFieldPropertiesList,
        )
        # ======================================================================
        # ->Esto es una verificacion de que la longitud que se propone es la del punto seleccionado
        #  En realidad no deberia pedir pointreclen porque viene dada por el pointformat
        nBytesPorPuntoCheck = sum(int(pointField[1]) for pointField in self.lasPointFieldPropertiesList)
        if pointreclen == 0 or pointreclen == nBytesPorPuntoCheck:
            self.pointreclen = nBytesPorPuntoCheck
        else:
            print('clidhead-> ATENCION se propone un valor de pointreclen incorecto (%i). Deberia ser: %i' % (pointreclen, nBytesPorPuntoCheck))
            self.pointreclen = pointreclen
        self.nBytesPorPunto = self.pointreclen

        # ======================================================================
        # oooooo IMPORTANTE: formato dtype del pointformat seleccionado ooooooooo
        # ======================================================================
        # self.formatoDtypePointFormatXXNotacionNpDtype = np.dtype([(pr[0], pr[2], pr[3]) for pr in self.lasPointFieldPropertiesList])
        # self.formatoDtypePointFormatXXNotacionNpDtype = np.dtype([(pr[0], pr[2], (pr[3],)) for pr in self.lasPointFieldPropertiesList])
        # Alternativa para usar ndarrays solo para cuando hay multiplicidad:
        self.formatoDtypePointFormatXXNotacionOneChar = []
        for pr in self.lasPointFieldPropertiesList:
            if pr[3] == 1:
                self.formatoDtypePointFormatXXNotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormatXXNotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointFormatXXNotacionNpDtype = np.dtype(self.formatoDtypePointFormatXXNotacionOneChar)
        # print( '\nclidhead-> formatoDtypePointFormatXXNotacionOneChar         ', self.formatoDtypePointFormatXXNotacionOneChar)
        # print( 'clidhead-> formatoDtypePointFormatXXNotacionNpDtype', self.formatoDtypePointFormatXXNotacionNpDtype)
        # input('lasHead.............')
        # ======================================================================
        # ======================================================================
        # Leo las propiedades del punto de mis extraVariables (le llamo pointFormat=101) de lasPointFields.cfg
        miPointformat = 101
        # print('clidhead-> (l) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.extraVariablesPropertiesList,
            self.extraVariablesPropertiesDict,
            self.extraVariablesOrdenDictPtoMini,
            self.extraVariablesOrdenDictPtoComp,
        ) = lasPointProperties(
            self.pointformat,
            # extraBytesPorRegistro=self.myOldLasHead.headDict['extraBytesPorRegistro'],
            extraBytesPorRegistro=0,
            verbose=self.verbose,
        )
        # Esto otro para facilitar el acceso a las propiedades desde funciones numba
        (
            self.npArrayextraVar,
            self.bytearrayextraVarNombre,
            self.arrayextraVarNombre,
            self.arrayextraVarRangoBytes,
            self.arrayextraVarTipoDato,
        ) = crearArraysPropPto(miPointformat, lasPointFieldPropertiesList=self.extraVariablesPropertiesList)
        # ======================================================================
        self.nBytesExtraVars = sum(int(pointField[1]) for pointField in self.extraVariablesPropertiesList)
        # ======================================================================
        # ======================================================================
        # ========= IMPORTANTE: formato dtype de las extraVariables ooooooooooooo
        # ======================================================================
        # self.formatoDtypeExtrVarNotacionNpDtype = np.dtype([(pr[0], pr[2], pr[3]) for pr in self.extraVariablesPropertiesList])
        # self.formatoDtypeExtrVarNotacionNpDtype = np.dtype([(pr[0], pr[2], (pr[3],)) for pr in self.extraVariablesPropertiesList])
        # Alternativa para usar ndarrays solo para cuando hay multiplicidad:
        self.formatoDtypeExtrVarNotacionOneChar = []
        for pr in self.extraVariablesPropertiesList:
            if pr[3] == 1:
                self.formatoDtypeExtrVarNotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypeExtrVarNotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypeExtrVarNotacionNpDtype = np.dtype(self.formatoDtypeExtrVarNotacionOneChar)
        # print( '\nclidhead-> formatoDtypeExtrVarNotacionOneChar         ', self.formatoDtypeExtrVarNotacionOneChar)
        # print( 'clidhead-> formatoDtypeExtrVarNotacionNpDtype', self.formatoDtypeExtrVarNotacionNpDtype)
        # input('clidhead.............')
        # ======================================================================

        # ======================================================================
        # Leo las propiedades del punto de mis maxiMiniSubCel (le llamo pointFormat=102) de lasPointFields.cfg
        miPointformat = 102
        # print('clidhead-> (m) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.maxiMiniSubCelPropertiesList,
            self.maxiMiniSubCelPropertiesDict,
            self.maxiMiniSubCelOrdenDictPtoMini,
            self.maxiMiniSubCelOrdenDictPtoComp,
        ) = lasPointProperties(
            self.pointformat,
            # extraBytesPorRegistro=self.myOldLasHead.headDict['extraBytesPorRegistro'],
            extraBytesPorRegistro=0,
            verbose=self.verbose,
        )
        # Esto otro para facilitar el acceso a las propiedades desde funciones numba
        (
            self.npArrayextraVar,
            self.bytearrayextraVarNombre,
            self.arrayextraVarNombre,
            self.arrayextraVarRangoBytes,
            self.arrayextraVarTipoDato,
        ) = crearArraysPropPto(miPointformat, lasPointFieldPropertiesList=self.maxiMiniSubCelPropertiesList)
        # ======================================================================
        self.nBytesExtraVars = sum(int(pointField[1]) for pointField in self.maxiMiniSubCelPropertiesList)
        # ======================================================================
        # ======================================================================
        # ========= IMPORTANTE: formato dtype de las maxiMiniSubCel ooooooooooooo
        # ======================================================================
        # self.formatoDtypePointMaxMinNotacionNpDtype = np.dtype([(pr[0], pr[2], pr[3]) for pr in self.maxiMiniSubCelPropertiesList])
        # self.formatoDtypePointMaxMinNotacionNpDtype = np.dtype([(pr[0], pr[2], (pr[3],)) for pr in self.maxiMiniSubCelPropertiesList])
        # Alternativa para usar ndarrays solo para cuando hay multiplicidad:
        self.formatoDtypePointMaxMinNotacionOneChar = []
        for pr in self.maxiMiniSubCelPropertiesList:
            if pr[3] == 1:
                self.formatoDtypePointMaxMinNotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointMaxMinNotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        self.formatoDtypePointMaxMinNotacionNpDtype = np.dtype(self.formatoDtypePointMaxMinNotacionOneChar)
        # print( 'clidhead-> maxiMiniSubCelPropertiesList', self.maxiMiniSubCelPropertiesList)
        # print( 'clidhead->', [(pr[0], pr[2], pr[3]) for pr in self.maxiMiniSubCelPropertiesList])
        # print( 'clidhead-> self.formatoDtypePointMaxMinNotacionNpDtype', self.formatoDtypePointMaxMinNotacionNpDtype)
        # ======================================================================

        # ======================================================================
        # Esto lo pasare al fichero de configuracion
        self.bytesExtras = False
        self.nBytesExtras = 2
        self.vlrHeredados = False
        self.vlrPropios = True
        self.vlrClassificationLookup = True
        nuevoOffset = self.headersize
        # ======================================================================
        if self.vlrPropios:
            # Para tipo de punto 8 (lasFormat 1.4) el formatoSRS es 'WKT' obligado
            if self.formatoSRS == 'WKT':
                nuevoNumvlrecords = 1
                # No es valido con LASF formar 1.2
                nuevoOffset += 54 + 656
                if self.vlrClassificationLookup:
                    # ->VRL_CLASSIFICATION LOOKUP
                    nuevoNumvlrecords += 1
                    nuevoOffset += 54 + (256 * 16)
            elif self.formatoSRS == 'GeoTIFF':
                nuevoNumvlrecords = 3
                # Creo tres VLR para asignar ETRS89 30N
                # ->VRL_0
                nuevoOffset += 54 + 72 # ---------->Con el \n son 73
                # ->VRL_1
                nuevoOffset += 54 + 24 # ---------->Con el \n son 25
                # ->VRL_2
                nuevoOffset += 54 + 30 # ---------->Con el \n son 731
                if self.vlrClassificationLookup:
                    # ->VRL_CLASSIFICATION LOOKUP
                    nuevoNumvlrecords += 1
                    nuevoOffset += 54 + (256 * 16)
        else:
            nuevoNumvlrecords = 0

        if self.vlrHeredados:
            nuevoNumvlrecords += self.myOldLasHead.numvlrecords
            offsetDeVLRsOriginal = self.myOldLasHead.offset - self.myOldLasHead.headersize
            nuevoOffset += offsetDeVLRsOriginal
            if verbose:
                print(f'clidhead-> Se incluyen los VLRs del fichero original que suman un offset de {offsetDeVLRsOriginal} bytes.')

        if self.bytesExtras:
            nuevoOffset += self.nBytesExtras
            if verbose:
                print(f'clidhead-> nBytesExtras que se suman al offset: {self.nBytesExtras}.')

        self.numvlrecords = nuevoNumvlrecords
        self.offset = nuevoOffset

        # ======================================================================
        if verbose:
            print(f'clidhead-> nuevoHeaderSize calculado:         {nuevoHeaderSize}')
            print(f'clidhead-> headersize del fichero original:   {self.myOldLasHead.headersize}')
            print(f'clidhead-> headersize del fichero creado:     {self.headersize}')
            print(f'clidhead-> Offset del fichero original:       {self.myOldLasHead.offset}')
            print(f'clidhead-> Offset del fichero creado:         {self.offset}')
            print(f'clidhead-> numvlrecords del fichero original: {self.myOldLasHead.numvlrecords}')
            print(f'clidhead-> numvlrecords del fichero creado:   {self.numvlrecords}')
        # ======================================================================

        # ======================================================================
        # No implementado
        # Otros campos nuevos para Point Format >5:
        self.waveformStart = waveformStart
        # Start of Waveform Data Packet Record:  This value provides the offset, in bytes, from the
        # beginning of the LAS file to the first byte of the Waveform Data Package Record.  Note that this
        # will be the first byte of the Waveform Data Packet header.  If no waveform records are contained
        # within the file, this value must be zero. It should be noted that LAS 1.4 allows multiple Extended
        # Variable Length Records (EVLR) and that the Waveform Data Packet Record is not necessarily
        # the first EVLR in the file.
        self.extendedVLRstart = extendedVLRstart
        # Start of First Extended Variable Length Record:  This value provides the offset, in bytes, from
        # the beginning of the LAS file to the first byte of the first EVLR.
        self.extendedVLRnValues = extendedVLRnValues
        # Number of Extended Variable Length Records: This field contains the current number of
        # EVLRs (including, if present, the Waveform Data Packet Record) that are stored in the file after
        # the Point Data Records. This number must be updated if the number of EVLRs changes.  If there
        # are no EVLRs this value is zero.
        # ======================================================================

        # ======================================================================
        self.headDict = {'infile': self.newLasFileNameConRuta}
        self.lasVersion = 'LasFormat_%i_%i' % (self.vermajor, self.verminor)
        lasVersionUno = 'LasFormat_1_2'
        for myField in self.lasHeaderFieldListVersionsDict[lasVersionUno]:
            # fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersionUno+'_'+myField]
            self.headDict[myField] = getattr(self, myField)
            # setattr(self, myField, self.headDict[myField])
        if self.verminor == 3 or self.verminor == 4:
            lasVersionDos = 'LasFormat_1_3'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersionDos]:
                # fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersionUno+'_'+myField]
                self.headDict[myField] = getattr(self, myField)
                # setattr(self, myField, self.headDict[myField])
        if self.verminor == 4:
            lasVersionTres = 'LasFormat_1_4'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersionTres]:
                # fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersionUno+'_'+myField]
                self.headDict[myField] = getattr(self, myField)
                # setattr(self, myField, self.headDict[myField])

        # self.createLasFileHeadDict()


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def createLasFileHeadDict(self, newLasFileNameConRuta):

        self.headDict = {}
        self.headDict['infile'] = self.newLasFileNameConRuta
        # First 227 Bytes at las head common to all formats

        # File Signature ("LASF") char[4] 4 bytes *
        self.headDict['filesignature'] = 'LASF'  # = 4, c, 4

        # File Source ID unsigned short 2 bytes *
        self.headDict['filesourceid'] = self.filesourceid  # = 2, H, 1
        # Global Encoding unsigned short 2 bytes *
        # Bits Field Name     Description
        # 0    GPS Time Type  The meaning of GPS Time in the point records. If this bit is not set, the GPS time in the point record fields is GPS Week Time (the same as versions 1.0 through 1.2 of LAS). Otherwise, if this bit is set, the GPS Time is standard GPS Time (satellite GPS Time) minus 1 x 109 (Adjusted Standard GPS Time). The offset moves the time back to near zero to improve floating point resolution.
        # 1    Waveform Data   If this bit is set, the waveform data packets are located within this file (note that this bit is mutually exclusive with bit 2). This is deprecated now.
        # 2    Waveform Data   If this bit is set, the waveform data packets are located externally in an auxiliary file with the same base name as this file but the extension *.wdp. (note that this bit is mutually exclusive with bit 1)
        # 3    Return numbers   If this bit is set, the point return numbers in the point data records have been synthetically generated. This could be the case, for example, when a composite file is created by combining a First Return File and a Last Return File.  In this case, first return data will be labeled "1 of 2" and second return data will be labeled "2 of 2"4 WKT If set, the Coordinate Reference System (CRS) is WKT.  If not set, the CRS is GeoTIFF.  It should not be set if the file writer wishes to ensure legacy compatibility (which means the CRS must be GeoTIFF)
        # 5:15 Reserved Must be set to zero
        self.headDict['globalencoding'] = self.globalencoding  # = 2, H, 1
        # Project ID - GUID data 1 unsigned long 4 bytes
        self.headDict['guid1'] = self.guid1  # = 4, =L, 1
        # Project ID - GUID data 2 unsigned short 2 byte
        self.headDict['guid2'] = self.guid2  # = 2, H, 1
        # Project ID - GUID data 3 unsigned short 2 byte
        self.headDict['guid3'] = self.guid3  # = 2, H, 1
        # Project ID - GUID data 4 unsigned char[8] 8 bytes
        self.headDict['guid4'] = self.guid4  # = 8, B, 8
        # Version Major unsigned char 1 byte *
        self.headDict['vermajor'] = self.vermajor  # = 1, B, 1
        # Version Minor unsigned char 1 byte *
        self.headDict['verminor'] = self.verminor  # = 1, B, 1
        # System Identifier char[32] 32 bytes *
        self.headDict['sysid'] = self.sysid  # = 32, c, 32
        # Lo empaqueto con: misBytes = bytes(self.headDict['sysid'], 'ascii') o con self.headDict['sysid'].encode('ascii') ->Debe tener 32 caracteres
        # Generating Software char[32] 32 bytes *
        self.headDict['gensoftware'] = self.gensoftware  # = 32, c, 32
        # Lo empaqueto con: misBytes = bytes(self.headDict['gensoftware'].ljust(32)[:32], 'ascii') o con self.headDict['gensoftware'].ljust(32)[:32].encode('ascii') ->Debe tener 32 caracteres
        # secs= time.clock( ) #Returns the current CPU time as a floating-point number of seconds.
        # ticks = time.time() #Returns the current system time in ticks since 12:00am, January 1, 1970(epoch).
        # localtime = time.localtime(time.time())
        # print "Local current time :", localtime -> Local current time : (2008, 5, 15, 12, 55, 32, 0, 136, 1); This is a tuple of 9 numbers:
        #   Index Field         Values
        #   0     4-digit year  2008
        #   1     Month         1 to 12
        #   2     Day           1 to 31
        #   3     Hour          0 to 23
        #   4     Minute        0 to 59
        #   5     Second        0 to 61 (60 or 61 are leap-seconds)
        #   6     Day of Week   0 to 6 (0 is Monday)
        #   7     Day of year   1 to 366 (Julian day)
        #   8     Daylight savings -1, 0, 1, -1 means library determines DST
        # File Creation Day of Year unsigned short 2 bytes *
        year = time.localtime(time.time())[0]
        dayOfyear = time.localtime(time.time())[7]
        self.headDict['fileday'] = dayOfyear  # = 2, H, 1
        # File Creation Year unsigned short 2 bytes *
        self.headDict['fileyear'] = year  # = 2, H, 1
        # Lo empaqueto con: misBytes = struct.pack('=L', self.headDict['fileyear']) -> b'\xe3\x07\x00\x00' (year=2019)
        # Header Size unsigned short 2 bytes *
        self.headDict['headersize'] = self.headersize  # = 2, H, 1
        # Offset to point data unsigned long 4 bytes *
        self.headDict['offset'] = self.nuevoOffset  # = 4, =L, 1
        # Number of Variable Length Records unsigned long 4 bytes *
        self.headDict['numvlrecords'] = self.numvlrecords  # = 4, =L, 1
        # Point Data Record Format unsigned char 1 byte *
        self.headDict['pointformat'] = self.pointformat  # = 1, B, 1
        # Point Data Record Length unsigned short 2 bytes *
        self.headDict['pointreclen'] = self.pointreclen  # = 2, H, 1

        # Legacy Number of point records unsigned long 4 bytes *
        self.headDict['numptrecords'] = self.numptrecords  # = 4, =L, 1
        # Lo empaqueto con: misBytes = struct.pack('=L', self.headDict['numptrecords']) -> b'\x00\x00\x00\x00'
        # Legacy Number of points by return unsigned long [5] 20 bytes *
        self.headDict['numptbyreturn'] = self.numptbyreturn[:5]  # = 20, L, 5
        # Son 5 valores unsigned long de 4 bytes cada uno
        # Los empaqueto con: misBytes = struct.pack('5L', *self.headDict['numptbyreturn']) <=> struct.pack('5L', 0, 0, 0, 0, 0) -> b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        # El * convierte la lista en secuencia de valores separados por comas
        # Ver codigos de formateo en MiAyuda.py #paquete struct

        # X scale factor double 8 bytes *
        self.headDict['xscale'] = self.xscale  # = 8, d, 1
        # Y scale factor double 8 bytes *
        self.headDict['yscale'] = self.yscale  # = 8, d, 1
        # Z scale factor double 8 bytes *
        self.headDict['zscale'] = self.zscale  # = 8, d, 1
        # X offset double 8 bytes *
        self.headDict['xoffset'] = self.xoffset  # = 8, d, 1
        # Y offset double 8 bytes *
        self.headDict['yoffset'] = self.yoffset  # = 8, d, 1
        # Z offset double 8 bytes *
        self.headDict['zoffset'] = self.zoffset  # = 8, d, 1
        # Max X double 8 bytes *
        self.headDict['xmaxBloqueMalla'] = self.xmaxBloqueMalla  # = 8, d, 1
        # Min X double 8 bytes *
        self.headDict['xminBloqueMalla'] = self.xminBloqueMalla  # = 8, d, 1
        # Max Y double 8 bytes *
        self.headDict['ymaxBloqueMalla'] = self.ymaxBloqueMalla  # = 8, d, 1
        # Min Y double 8 bytes *
        self.headDict['yminBloqueMalla'] = self.yminBloqueMalla  # = 8, d, 1
        # Max Z double 8 bytes *
        self.headDict['zmax'] = self.zmax  # = 8, d, 1
        # Min Z double 8 bytes *
        self.headDict['zmin'] = self.zmin  # = 8, d, 1
        # Start of Waveform Data Packet Record Unsigned long long 8 bytes *
        # Hasta aqui la cabecera del Las Format 1.2 ->Total: 227 bytes

        # 1 campo adicional para Las Format 1.3
        self.headDict['waveformStart'] = 0  # = 8, Q, 1
        # Hasta aqui la cabecera del Las Format 1.2 ->Total: 235 bytes

        # 4 Campos adicionales para Las Format 1.4
        # Start of first Extended Variable Length Record unsigned long long 8 bytes *
        self.headDict['extendedVLRstart'] = 0  # = 8, Q, 1
        # Number of Extended Variable Length Records unsigned long 4 bytes *
        self.headDict['extendedVLRnValues'] = 0  # = 4, L, 1
        # Number of point records unsigned long long 8 bytes *
        self.headDict['pointrecords'] = self.numptrecords  # = 8, Q, 1
        # Number of points by return unsigned long long [15] 120 bytes *
        # self.headDict['pointsbyreturn'] = self.numptbyreturn  # = 120, Q, 15
        self.headDict['pointsbyreturn'] = self.pointsbyreturn  # = 120, L, 15
        # Hasta aqui la cabecera del Las Format 1.4 ->Total: 375 bytes

    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    #     #ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    #     def writeLasHead(self, newLasFileNameConRuta,
    #                      numptrecords = 0,
    #                      numptbyreturn = [0, 0, 0, 0, 0],
    #                      xmax = 0, xmin = 0, ymax = 0, ymin = 0, zmax = 0, zmin = 0):
    #         self.newLasFileNameConRuta = newLasFileNameConRuta
    #         self.numptrecords = numptrecords
    #         self.numptbyreturn = numptbyreturn
    #         self.xmaxBloqueMalla = xmax
    #         self.xminBloqueMalla = xmin
    #         self.ymaxBloqueMalla = ymax
    #         self.yminBloqueMalla = ymin
    #         self.zmax = zmax
    #         self.zmin = zmin
    #
    #         self.headDict['infile'] = self.newLasFileNameConRuta
    #         self.headDict['numptrecords'] = self.numptrecords
    #         self.headDict['numptbyreturn'] = self.numptbyreturn
    #         self.headDict['xmaxBloqueMalla'] = self.xmaxBloqueMalla
    #         self.headDict['xminBloqueMalla'] = self.xminBloqueMalla
    #         self.headDict['ymaxBloqueMalla'] = self.ymaxBloqueMalla
    #         self.headDict['yminBloqueMalla'] = self.yminBloqueMalla
    #         self.headDict['zmax'] = self.zmax
    #         self.headDict['zmin'] = self.zmin
    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def adjustCornersCoordinates(
            self,
            sizeToAdjust,
            envolvente=False,
            margenAdmisible=0,
            LCLorigenDeCoordenadasX=0,
            LCLorigenDeCoordenadasY=0,
        ):
        if sizeToAdjust > 0:
            if self.xminBloqueMalla % sizeToAdjust != 0:
                if self.verbose:
                    print('clidhead-> NewLasHeadClass-> Ajustando xmin a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                    print(f'{TB}Before: {self.xminBloqueMalla:0.2f}')
                if envolvente:
                    self.xminBloqueMalla = float(sizeToAdjust * math.floor((self.xminBloqueMalla + margenAdmisible) / sizeToAdjust))
                else:
                    self.xminBloqueMalla = float(sizeToAdjust * math.ceil((self.xminBloqueMalla) / sizeToAdjust))
                if self.verbose:
                    print(f'{TB}After: {self.xminBloqueMalla:0.2f}')
            if self.xmaxBloqueMalla % sizeToAdjust != 0:
                if self.verbose:
                    print('clidhead-> NewLasHeadClass-> Ajustando xmax a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                    print(f'{TB}Before: {self.xmaxBloqueMalla:0.2f}')
                if envolvente:
                    self.xmaxBloqueMalla = float(sizeToAdjust * math.ceil((self.xmaxBloqueMalla - margenAdmisible) / sizeToAdjust))
                else:
                    self.xmaxBloqueMalla = float(sizeToAdjust * math.floor((self.xmaxBloqueMalla + margenAdmisible) / sizeToAdjust))
                if self.verbose:
                    print(f'{TB}After: {self.xmaxBloqueMalla:0.2f}')

            if self.yminBloqueMalla % sizeToAdjust != 0:
                if self.verbose:
                    print('clidhead-> NewLasHeadClass-> Ajustando ymin a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                    print(f'{TB}Before: {self.yminBloqueMalla:0.2f}')
                if envolvente:
                    self.yminBloqueMalla = float(sizeToAdjust * math.floor((self.yminBloqueMalla + margenAdmisible) / sizeToAdjust))
                else:
                    self.yminBloqueMalla = float(sizeToAdjust * math.ceil((self.yminBloqueMalla) / sizeToAdjust))
                if self.verbose:
                    print(f'{TB}After: {self.yminBloqueMalla:0.2f}')
            if self.ymaxBloqueMalla % sizeToAdjust != 0:
                if self.verbose:
                    print('clidhead-> NewLasHeadClass-> Ajustando ymax a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                    print(f'{TB}Before: {self.yminBloqueMalla:0.2f}')
                if envolvente:
                    self.ymaxBloqueMalla = float(sizeToAdjust * math.ceil((self.ymaxBloqueMalla - margenAdmisible) / sizeToAdjust))
                else:
                    self.ymaxBloqueMalla = float(sizeToAdjust * math.floor((self.ymaxBloqueMalla + margenAdmisible) / sizeToAdjust))
                if self.verbose:
                    print(f'{TB}After: {self.yminBloqueMalla:0.2f}')
        else:
            print('clidhead-> NewLasHeadClass-> AVISO: Ajustando coordenadas a una dimension nula')
        self.xSupIzda = self.xminBloqueMalla
        self.ySupIzda = self.ymaxBloqueMalla
        self.xInfDcha = self.xmaxBloqueMalla
        self.yInfDcha = self.yminBloqueMalla


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def wkt25830(self):
        # EPSG:25830 -> ETRS89 / UTM zone 30N
        # Fuente https://epsg.io/25830
        OGC_WKT1 = 'PROJCS["ETRS89 / UTM zone 30N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25830"]]'
        '''PROJCS["ETRS89 / UTM zone 30N",
    GEOGCS["ETRS89",
        DATUM["European_Terrestrial_Reference_System_1989",
            SPHEROID["GRS 1980",6378137,298.257222101,
                AUTHORITY["EPSG","7019"]],
            TOWGS84[0,0,0,0,0,0,0],
            AUTHORITY["EPSG","6258"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4258"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",-3],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH],
    AUTHORITY["EPSG","25830"]]'''

        OGC_WKT2 = 'PROJCRS["ETRS89 / UTM zone 30N",BASEGEOGCRS["ETRS89",ENSEMBLE["European Terrestrial Reference System 1989 ensemble",MEMBER["European Terrestrial Reference Frame 1989"],MEMBER["European Terrestrial Reference Frame 1990"],MEMBER["European Terrestrial Reference Frame 1991"],MEMBER["European Terrestrial Reference Frame 1992"],MEMBER["European Terrestrial Reference Frame 1993"],MEMBER["European Terrestrial Reference Frame 1994"],MEMBER["European Terrestrial Reference Frame 1996"],MEMBER["European Terrestrial Reference Frame 1997"],MEMBER["European Terrestrial Reference Frame 2000"],MEMBER["European Terrestrial Reference Frame 2005"],MEMBER["European Terrestrial Reference Frame 2014"],ELLIPSOID["GRS 1980",6378137,298.257222101,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[0.1]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4258]],CONVERSION["UTM zone 30N",METHOD["Transverse Mercator",ID["EPSG",9807]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",-3,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9996,SCALEUNIT["unity",1],ID["EPSG",8805]],PARAMETER["False easting",500000,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1]],USAGE[SCOPE["Engineering survey, topographic mapping."],AREA["Europe between 6°W and 0°W: Faroe Islands offshore; Ireland - offshore; Jan Mayen - offshore; Norway including Svalbard - offshore; Spain - onshore and offshore."],BBOX[35.26,-6,80.49,0.01]],ID["EPSG",25830]]'
        '''PROJCRS["ETRS89 / UTM zone 30N",
    BASEGEOGCRS["ETRS89",
        ENSEMBLE["European Terrestrial Reference System 1989 ensemble",
            MEMBER["European Terrestrial Reference Frame 1989"],
            MEMBER["European Terrestrial Reference Frame 1990"],
            MEMBER["European Terrestrial Reference Frame 1991"],
            MEMBER["European Terrestrial Reference Frame 1992"],
            MEMBER["European Terrestrial Reference Frame 1993"],
            MEMBER["European Terrestrial Reference Frame 1994"],
            MEMBER["European Terrestrial Reference Frame 1996"],
            MEMBER["European Terrestrial Reference Frame 1997"],
            MEMBER["European Terrestrial Reference Frame 2000"],
            MEMBER["European Terrestrial Reference Frame 2005"],
            MEMBER["European Terrestrial Reference Frame 2014"],
            ELLIPSOID["GRS 1980",6378137,298.257222101,
                LENGTHUNIT["metre",1]],
            ENSEMBLEACCURACY[0.1]],
        PRIMEM["Greenwich",0,
            ANGLEUNIT["degree",0.0174532925199433]],
        ID["EPSG",4258]],
    CONVERSION["UTM zone 30N",
        METHOD["Transverse Mercator",
            ID["EPSG",9807]],
        PARAMETER["Latitude of natural origin",0,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8801]],
        PARAMETER["Longitude of natural origin",-3,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8802]],
        PARAMETER["Scale factor at natural origin",0.9996,
            SCALEUNIT["unity",1],
            ID["EPSG",8805]],
        PARAMETER["False easting",500000,
            LENGTHUNIT["metre",1],
            ID["EPSG",8806]],
        PARAMETER["False northing",0,
            LENGTHUNIT["metre",1],
            ID["EPSG",8807]]],
    CS[Cartesian,2],
        AXIS["(E)",east,
            ORDER[1],
            LENGTHUNIT["metre",1]],
        AXIS["(N)",north,
            ORDER[2],
            LENGTHUNIT["metre",1]],
    USAGE[
        SCOPE["Engineering survey, topographic mapping."],
        AREA["Europe between 6°W and 0°W: Faroe Islands offshore; Ireland - offshore; Jan Mayen - offshore; Norway including Svalbard - offshore; Spain - onshore and offshore."],
        BBOX[35.26,-6,80.49,0.01]],
    ID["EPSG",25830]]'''

        ESRI_WKT = 'PROJCS["ETRS_1989_UTM_Zone_30N",GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-3.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
        '''PROJCS["ETRS_1989_UTM_Zone_30N",
    GEOGCS["GCS_ETRS_1989",
        DATUM["D_ETRS_1989",
            SPHEROID["GRS_1980",6378137.0,298.257222101]],
        PRIMEM["Greenwich",0.0],
        UNIT["Degree",0.0174532925199433]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["False_Easting",500000.0],
    PARAMETER["False_Northing",0.0],
    PARAMETER["Central_Meridian",-3.0],
    PARAMETER["Scale_Factor",0.9996],
    PARAMETER["Latitude_Of_Origin",0.0],
    UNIT["Meter",1.0]]'''
        GeoServer = '25830=PROJCS["ETRS89 / UTM zone 30N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25830"]]'

        return OGC_WKT1


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def wkt25829(self):
        # EPSG:25829 -> ETRS89 / UTM zone 29N
        # Fuente: https://epsg.io/25829
        OGC_WKT1 = 'PROJCS["ETRS89 / UTM zone 29N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25829"]]'
        '''PROJCS["ETRS89 / UTM zone 29N",
    GEOGCS["ETRS89",
        DATUM["European_Terrestrial_Reference_System_1989",
            SPHEROID["GRS 1980",6378137,298.257222101,
                AUTHORITY["EPSG","7019"]],
            TOWGS84[0,0,0,0,0,0,0],
            AUTHORITY["EPSG","6258"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4258"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",-9],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH],
    AUTHORITY["EPSG","25829"]]'''

        OGC_WKT2 = 'PROJCRS["ETRS89 / UTM zone 29N",BASEGEOGCRS["ETRS89",ENSEMBLE["European Terrestrial Reference System 1989 ensemble",MEMBER["European Terrestrial Reference Frame 1989"],MEMBER["European Terrestrial Reference Frame 1990"],MEMBER["European Terrestrial Reference Frame 1991"],MEMBER["European Terrestrial Reference Frame 1992"],MEMBER["European Terrestrial Reference Frame 1993"],MEMBER["European Terrestrial Reference Frame 1994"],MEMBER["European Terrestrial Reference Frame 1996"],MEMBER["European Terrestrial Reference Frame 1997"],MEMBER["European Terrestrial Reference Frame 2000"],MEMBER["European Terrestrial Reference Frame 2005"],MEMBER["European Terrestrial Reference Frame 2014"],ELLIPSOID["GRS 1980",6378137,298.257222101,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[0.1]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4258]],CONVERSION["UTM zone 29N",METHOD["Transverse Mercator",ID["EPSG",9807]],PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",-9,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9996,SCALEUNIT["unity",1],ID["EPSG",8805]],PARAMETER["False easting",500000,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1]],USAGE[SCOPE["Engineering survey, topographic mapping."],AREA["Europe between 12°W and 6°W: Faroe Islands - onshore and offshore; Ireland - offshore; Jan Mayen - onshore and offshore; Portugal - onshore and offshore; Spain - onshore and offshore; United Kingdom - UKCS offshore."],BBOX[34.91,-12,74.13,-6]],ID["EPSG",25829]]'
        '''PROJCRS["ETRS89 / UTM zone 29N",
    BASEGEOGCRS["ETRS89",
        ENSEMBLE["European Terrestrial Reference System 1989 ensemble",
            MEMBER["European Terrestrial Reference Frame 1989"],
            MEMBER["European Terrestrial Reference Frame 1990"],
            MEMBER["European Terrestrial Reference Frame 1991"],
            MEMBER["European Terrestrial Reference Frame 1992"],
            MEMBER["European Terrestrial Reference Frame 1993"],
            MEMBER["European Terrestrial Reference Frame 1994"],
            MEMBER["European Terrestrial Reference Frame 1996"],
            MEMBER["European Terrestrial Reference Frame 1997"],
            MEMBER["European Terrestrial Reference Frame 2000"],
            MEMBER["European Terrestrial Reference Frame 2005"],
            MEMBER["European Terrestrial Reference Frame 2014"],
            ELLIPSOID["GRS 1980",6378137,298.257222101,
                LENGTHUNIT["metre",1]],
            ENSEMBLEACCURACY[0.1]],
        PRIMEM["Greenwich",0,
            ANGLEUNIT["degree",0.0174532925199433]],
        ID["EPSG",4258]],
    CONVERSION["UTM zone 29N",
        METHOD["Transverse Mercator",
            ID["EPSG",9807]],
        PARAMETER["Latitude of natural origin",0,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8801]],
        PARAMETER["Longitude of natural origin",-9,
            ANGLEUNIT["degree",0.0174532925199433],
            ID["EPSG",8802]],
        PARAMETER["Scale factor at natural origin",0.9996,
            SCALEUNIT["unity",1],
            ID["EPSG",8805]],
        PARAMETER["False easting",500000,
            LENGTHUNIT["metre",1],
            ID["EPSG",8806]],
        PARAMETER["False northing",0,
            LENGTHUNIT["metre",1],
            ID["EPSG",8807]]],
    CS[Cartesian,2],
        AXIS["(E)",east,
            ORDER[1],
            LENGTHUNIT["metre",1]],
        AXIS["(N)",north,
            ORDER[2],
            LENGTHUNIT["metre",1]],
    USAGE[
        SCOPE["Engineering survey, topographic mapping."],
        AREA["Europe between 12°W and 6°W: Faroe Islands - onshore and offshore; Ireland - offshore; Jan Mayen - onshore and offshore; Portugal - onshore and offshore; Spain - onshore and offshore; United Kingdom - UKCS offshore."],
        BBOX[34.91,-12,74.13,-6]],
    ID["EPSG",25829]]'''

        ESRI_WKT = 'PROJCS["ETRS_1989_UTM_Zone_29N",GEOGCS["GCS_ETRS_1989",DATUM["D_ETRS_1989",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-9.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'
        ''''PROJCS["ETRS_1989_UTM_Zone_29N",
    GEOGCS["GCS_ETRS_1989",
        DATUM["D_ETRS_1989",
            SPHEROID["GRS_1980",6378137.0,298.257222101]],
        PRIMEM["Greenwich",0.0],
        UNIT["Degree",0.0174532925199433]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["False_Easting",500000.0],
    PARAMETER["False_Northing",0.0],
    PARAMETER["Central_Meridian",-9.0],
    PARAMETER["Scale_Factor",0.9996],
    PARAMETER["Latitude_Of_Origin",0.0],
    UNIT["Meter",1.0]]'''

        GeoServer = '25829=PROJCS["ETRS89 / UTM zone 29N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25829"]]'

        return OGC_WKT1


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

'''
Global Encoding
its Field Name                              Description
0   GPS Time Type
                                            The meaning of GPS Time in the point records. If 
                                            this bit is not set, the GPS time in the point record 
                                            fields is GPS Week Time (the same as versions 
                                            1.0 through 1.2 of LAS). Otherwise, if this bit is 
                                            set, the GPS Time is standard GPS Time (satellite 
                                            GPS Time) minus 1 x 10^9 (Adjusted Standard 
                                            GPS Time). The offset moves the time back to 
                                            near zero to improve floating point resolution.
1    Waveform Data Packets Internal
                                            If this bit is set, the waveform data packets are 
                                            located within this file (note that this bit is mutually 
                                            exclusive with bit 2). This is deprecated now.
2    Waveform Data Packets External
                                            If this bit is set, the waveform data packets are 
                                            located externally in an auxiliary file with the same 
                                            base name as this file but the extension *.wdp. 
                                            (note that this bit is mutually exclusive with bit 1) 
3    Return numbers have been synthetically generated
                                            If this bit is set, the point return numbers in the 
                                            point data records have been synthetically 
                                            generated. This could be the case, for example, 
                                            when a composite file is created by combining a 
                                            First Return File and a Last Return File.    In this 
                                            case, first return data will be labeled "1 of 2" and 
                                            second return data will be labeled "2 of 2"
4    WKT
                                            If set, the Coordinate Reference System (CRS) is 
                                            WKT.    If not set, the CRS is GeoTIFF.    It should 
                                            not be set if the file writer wishes to ensure legacy 
                                            compatibility (which means the CRS must be 
                                            GeoTIFF) 
5:15    Reserved
                                            Must be set to zero
'''


if __name__ == '__main__':
    print(f'\n{"":_^80}')
    print('clidflow-> Este modulo ya no puede ejecutarse directamente-> Hay que lanzar clidbase.py.')
    print(f'{"":=^80}')
    sys.exit()
