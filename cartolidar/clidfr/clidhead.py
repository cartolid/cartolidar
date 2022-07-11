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
# import importlib
import struct
# import shutil
# import gc

# Paquetes de terceros
import numpy as np
import psutil


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
# Directorio que depende del entorno:
MAIN_HOME_DIR = str(pathlib.Path.home())
# Directorios de la aplicacion:
MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# Cuando estoy en un modulo principal (clidbase.py o clidflow.py):
# MAIN_PROJ_DIR = MAIN_FILE_DIR
# Cuando estoy en un modulo dentro de un paquete (subdirectorio):
MAIN_PROJ_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '../..'))
MAIN_RAIZ_DIR = os.path.abspath(os.path.join(MAIN_PROJ_DIR, '..'))
if 'cartolidar' in MAIN_RAIZ_DIR:
    MAIN_MDLS_DIR = os.path.abspath(os.path.join(MAIN_RAIZ_DIR, '../data'))
else:
    MAIN_MDLS_DIR = os.path.join(MAIN_RAIZ_DIR, 'data')
# Directorio desde el que se lanza la app (estos dos coinciden):
MAIN_BASE_DIR = os.path.abspath('.')
MAIN_THIS_DIR = os.getcwd()
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
# ==============================================================================
VERSIONFILE = os.path.abspath('_version.py')
if not os.path.exists(VERSIONFILE):
    VERSIONFILE = os.path.abspath(os.path.join(MAIN_FILE_DIR, '_version.py'))
    if not os.path.exists(VERSIONFILE):
        VERSIONFILE = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..', '_version.py'))
        if not os.path.exists(VERSIONFILE):
            VERSIONFILE = os.path.abspath(os.path.join(MAIN_FILE_DIR, '../..', '_version.py'))
if os.path.exists(VERSIONFILE):
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        # __version__ = mo.groups()[0]
        __version__ = mo.group(1)
    else:
        raise RuntimeError(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __version__ = "a.b.c"')
    VSRE = r"^__date__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        __date__ = mo.group(1)
    else:
        raise RuntimeError(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __date__ = "..."')
    VSRE = r"^__updated__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        __updated__ = mo.group(1)
    else:
        raise RuntimeError(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __updated__ = "..."')
    VSRE = r"^__copyright__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        __copyright__ = mo.group(1)
    else:
        raise RuntimeError(f'Revisar fichero {VERSIONFILE} -> Debe incluir la linea __copyright__ = "..."')
else:
    __version__ = '0.0'
    __date__ = '2016-2022'
    __updated__ = '2022'
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
    print(f'\nclidaux-> Cargando clidhead...')
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

# ==============================================================================
if callingModuleInicial == 'clidtools' or callingModuleInicial == 'clidclas':
    # No se usa el fichero de configuracion clidbase.slx cuando el modulo inicial es:
    #   clidtools: modulos auxiliares de cartolidar, que pueden ejecutarse de forma autonoma
    #   clidclas: modulo para lanzar el entrenamiento de forma autonoma
    class Object(object):
        pass
    GLO = Object()
    GLO.GLBLverbose = False
    GLO.GLBLcoordMinMaxAcordesConBloque = True
    GLO.MAIN_copyright = 'Bengoa 2016-22'
    MAIN_controlFileLas = None
    MAIN_controlFileGral = None
else:
    if os.getcwd().endswith('cartolidar\cartolidar') or os.getcwd().endswith('cartolidar/cartolidar'):
        if CONFIGverbose:
            sys.stdout.write('\nclidhead-> Importando clidconfig desde cartolidar.clidax\n')
        from cartolidar.clidax import clidconfig
        if CONFIGverbose:
            sys.stdout.write(f'\nclidhead-> Ok clidconfig importado de cartolidar.clidax (1)')
        from cartolidar.clidnb import clidnaux
    else:
        try:
            if CONFIGverbose:
                sys.stdout.write('\nclidhead-> Importando clidconfig desde cartolidar.clidax\n')
            from cartolidar.clidax import clidconfig
            if CONFIGverbose:
                sys.stdout.write(f'\nclidhead-> Ok clidconfig importado de cartolidar.clidax (1)')
            from cartolidar.clidnb import clidnaux
        except:
            if True:
            # try:
                if CONFIGverbose:
                    sys.stdout.write(f'\nclidhead-> Intento alternativo de importar clidconfig desde la version local {os.getcwd()}/clidax\n')
                from clidax import clidconfig
                if CONFIGverbose:
                    sys.stdout.write(f'\nclidhead-> Ok clidconfig importado del clidax local (2)')
            from clidnb import clidnaux
    configVarsDict = clidconfig.leerCambiarVariablesGlobales(
        idProceso=MAIN_idProceso
    )
    GLO = clidconfig.VariablesGlobales(configVarsDict)
    MAIN_controlFileLas = clidconfig.controlFileLas
    MAIN_controlFileGral = clidconfig.controlFileGral

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
# ==============================================================================


# Funcion copiada de clidaux.py, pera no tener que importar ese modulo
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
    try:
        if outputFileLas and MAIN_controlFileLas:
            try:
                MAIN_controlFileLas.write(str(mensaje) + end + '\n' if newLine else ' ')
            except:
                if MAIN_controlFileGral:
                    MAIN_controlFileGral.write('Error writing control file (1).\n')
        else:
            MAIN_controlFileGral.write(str(mensaje) + end + '\n' if newLine else ' ')
    except:
        pass


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
def buscarDirectorioDataExt():
    dataExtPath = os.path.abspath(GLO.MAINrutaDataExt)
    dataFiles = []
    if os.path.isdir(dataExtPath):
        for (_, _, filenames) in os.walk(dataExtPath):
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
            print(f'clidhead-> No hay ficheros de configuracion ni auxiliares (cfg, txt, csv, xls*) en {dataExtPath}')
            directorioDeTrabajo = buscarDirectorioDeTrabajo()
            print(f'{TB}-> Se buscan los ficheros de configuracion y auxiliares en el directorio de trabajo: {directorioDeTrabajo}')
            return directorioDeTrabajo
    else:
        print(f'clidhead-> La ruta {dataExtPath} no es valida.')
        directorioDeTrabajo = buscarDirectorioDeTrabajo()
        print(f'{TB}-> Se buscan los ficheros de configuracion y auxiliares en el directorio de trabajo: {directorioDeTrabajo}')
        return directorioDeTrabajo


# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
class LasHeadClass(object):
    """
    Object with properties of las file head
    and with methods to write a new LASF head
    """

    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def __init__(
            self,
            infileConRuta,
            lasDataMem=None,
            metersBlock=2000,
            metersCell=10,
            # fileCoordYear='', # No utilizo fileCoordYear como propiedad de esta clase sino que uso
                                # el valor obtenido en clidbase.py que tiene en cuenta el nombre y
                                # las coordenadas de la cabecera xSupIzda ySupIzda
            LCLordenColoresInput=None,
            TRNShuso29=False,
            coordenadasTransformadasDe29a30=False,
            verbose=False,
        ):
        """
        Class with info about lasFile
        Mandatory args for the class: infileConRuta
        Optional args: metersBlock=0, metersCell=10, verbose=False
            metersBlock only for checking coherence with lasFile head info
            metersCell for adjust corner coordinates to multiple of metersCell
                if metersCell=0 -> no adjust
        Properties asigned to the created object:
            headDict
            infileConRuta metersBlock metersCell  verbose
            lasVersion  pointformat nBytesPorPunto  numptrecords
            fileCoordYear   xSupIzdaDelNombre   ySupIzdaDelNombre   fileYear
            xmin    xmax    ymin    ymax
            xSupIzda    ySupIzda    xInfDcha    yInfDcha
            xmin        xmax        ymin        ymax
            lasPointFieldPropertiesList lasPointFieldPropertiesDict lasPointFieldOrdenDict
            npArrayPropPto  bytearrayPropPtoNombre  arrayPropPtoNombre
            arrayPropPtoRangoBytes  arrayPropPtoTipoDato
        LasFile head fields are readed from cartolidar/data/ext/io/lasHeadFields.cfg
        LasFile point fields are readed from cartolidar/data/ext/io/lasPointFields.cfg
        """

        # ======================================================================
        self.readOk = True
        self.infileConRuta = infileConRuta
        self.lasDataMem = lasDataMem
        self.metersBlock = metersBlock
        self.metersCell = metersCell
        self.verbose = verbose
        self.TRNShuso29 = TRNShuso29
        self.coordenadasTransformadasDe29a30 = coordenadasTransformadasDe29a30
        # En realidad creo que no uso esta variable como propiedad de esta clase
        # self.fileCoordYear = fileCoordYear # Lo obtengo mas adelante, con checkLasfile<>
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

        # En principio la extension indica si esta comprimido.
        # De todas formas se puede verificar leyendo la cabecera, que no requiere descomprimir porque no esta comprimida.
        if not self.lasDataMem is None:
            self.lazfile = False
            if self.verbose:
                print('clidhead-> Leyendo cabecera de fichero descomprimido en memoria (lasDataMem).')
        else:
            if infileConRuta[-4:].lower() == '.laz':
                self.lazfile = True
                if self.verbose:
                    print('clidhead-> Leyendo cabecera de fichero laz comprimido (sin descomprimir por el momento).')
            else:
                self.lazfile = False
                if self.verbose:
                    print('clidhead-> Leyendo cabecera de fichero las sin comprimir (o ya descomprimido en fichero).')
        # ======================================================================

        # ======================================================================
        # Showing lasFile head fields of all versions in cartolidar/data/ext/io/lasHeadFields.cfg
        # Showing las point formats in cartolidar/data/ext/io/lasPointFields.cfg
        if False:
            self.showAlllasFileVersions()
            self.showAllPointFormats()
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

        if self.lasDataMem is None:
            # print('------------------------clidhead--------------> self.lasDataMem is None')
            self.ficheroLas.close()

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
            print('\nclidhead-> nCreando copia del LASF con solo cabecera (sin puntos): %s' % outFileLasConRuta)
            print('clidhead-> Escribiendo cabecera original de prueba en', outFileLasConRuta, 'con', len(self.headBin), 'bytes')
            print('clidhead-> self.headBin', self.headBin)
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
            print('\nclidhead-> Version de LASF (1.3) implementada solo parcialmente')
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
            print('\nclidhead-> Version de LASF (%s) no implementada' % self.lasVersion)
            quit()
        self.headDict['formatoSRS'] = self.formatoSRS
        self.headDict['returnNumbersSyntheticallyGenerated'] = self.returnNumbersSyntheticallyGenerated
        self.headDict['waveformDataPacketsExternal'] = self.waveformDataPacketsExternal
        self.headDict['waveformDataPacketsInternal'] = self.waveformDataPacketsInternal

        # ======================================================================
        # Variantes ortograficas a extinguir
        self.nBytesPorPunto = self.headDict['pointreclen']
        self.xSupIzda = self.headDict['xmin']
        self.ySupIzda = self.headDict['ymax']
        self.xmin = self.headDict['xmin']
        self.xmax = self.headDict['xmax']
        self.ymin = self.headDict['ymin']
        self.ymax = self.headDict['ymax']

        self.guid1 = self.headDict['guid1']
        self.guid2 = self.headDict['guid2']
        self.guid3 = self.headDict['guid3']
        self.guid4 = self.headDict['guid4']

        if self.lasVersion == 'LasFormat_1_2' or self.lasVersion == 'LasFormat_1_3':
            self.numptrecords = self.headDict['numptrecords']
            self.numptbyreturn = self.headDict['numptbyreturn']
        elif self.lasVersion == 'LasFormat_1_4':
            # LASF format 1.4 mantiene el campo original con un maximo de 2^32 puntos y el nuevo con maximo de 2^64 puntos
            # Si el numero de puntos es menor de 2^32, ambos coicdein, en caso contrario el priero el 0 y solo vale el segundo
            self.numptrecords = self.headDict['pointrecords']
            # Asigno al capo legacy el nuevo valor mas completo
            self.headDict['numptrecords'] = self.numptrecords
            # Numero de puntos por retorno
            self.numptbyreturn = self.headDict['pointsbyreturn']
            # Asigno al capo legacy el nuevo valor mas completo
            self.headDict['numptbyreturn'] = self.headDict['pointsbyreturn']
            self.numptbyreturn = self.headDict['pointsbyreturn']
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
        # print('clidhead-> miPointformat:', miPointformat)
        # print('\t->', self.headDict['pointformat'])
        # print('clidhead-> (x) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesList,
            self.lasPointFieldPropertiesDict,
            self.lasPointFieldOrdenDictPtoMini,
            self.lasPointFieldOrdenDictPtoComp,
        ) = lasPointProperties(miPointformat, self.verbose)
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
        # print('clidhead-> (99) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat99,
            self.lasPointFieldPropertiesDictPointFormat99,
            self.lasPointFieldOrdenDictPtoMiniPointFormat99,
            self.lasPointFieldOrdenDictPtoCompPointFormat99,
        ) = lasPointProperties(miPointformat, False)
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
        # print('clidhead-> (0) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat00,
            self.lasPointFieldPropertiesDictPointFormat00,
            self.lasPointFieldOrdenDictPtoMiniPointFormat00,
            self.lasPointFieldOrdenDictPtoCompPointFormat00,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat00,
            self.bytearrayPropPtoNombrePointFormat00,
            self.arrayPropPtoNombrePointFormat00,
            self.arrayPropPtoRangoBytesPointFormat00,
            self.arrayPropPtoTipoDatoPointFormat00
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat00)

        miPointformat = 1
        # print('clidhead-> (1) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat01,
            self.lasPointFieldPropertiesDictPointFormat01,
            self.lasPointFieldOrdenDictPtoMiniPointFormat01,
            self.lasPointFieldOrdenDictPtoCompPointFormat01,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat01,
            self.bytearrayPropPtoNombrePointFormat01,
            self.arrayPropPtoNombrePointFormat01,
            self.arrayPropPtoRangoBytesPointFormat01,
            self.arrayPropPtoTipoDatoPointFormat01
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat01)

        miPointformat = 2
        # print('clidhead-> (2) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat02,
            self.lasPointFieldPropertiesDictPointFormat02,
            self.lasPointFieldOrdenDictPtoMiniPointFormat02,
            self.lasPointFieldOrdenDictPtoCompPointFormat02,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat02,
            self.bytearrayPropPtoNombrePointFormat02,
            self.arrayPropPtoNombrePointFormat02,
            self.arrayPropPtoRangoBytesPointFormat02,
            self.arrayPropPtoTipoDatoPointFormat02
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat02)

        miPointformat = 3
        # print('clidhead-> (3) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat03,
            self.lasPointFieldPropertiesDictPointFormat03,
            self.lasPointFieldOrdenDictPtoMiniPointFormat03,
            self.lasPointFieldOrdenDictPtoCompPointFormat03,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat03,
            self.bytearrayPropPtoNombrePointFormat03,
            self.arrayPropPtoNombrePointFormat03,
            self.arrayPropPtoRangoBytesPointFormat03,
            self.arrayPropPtoTipoDatoPointFormat03
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat03)

        miPointformat = 4
        # print('clidhead-> (4) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat04,
            self.lasPointFieldPropertiesDictPointFormat04,
            self.lasPointFieldOrdenDictPtoMiniPointFormat04,
            self.lasPointFieldOrdenDictPtoCompPointFormat04,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat04,
            self.bytearrayPropPtoNombrePointFormat04,
            self.arrayPropPtoNombrePointFormat04,
            self.arrayPropPtoRangoBytesPointFormat04,
            self.arrayPropPtoTipoDatoPointFormat04
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat04)

        miPointformat = 5
        # print('clidhead-> (5) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat05,
            self.lasPointFieldPropertiesDictPointFormat05,
            self.lasPointFieldOrdenDictPtoMiniPointFormat05,
            self.lasPointFieldOrdenDictPtoCompPointFormat05,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat05,
            self.bytearrayPropPtoNombrePointFormat05,
            self.arrayPropPtoNombrePointFormat05,
            self.arrayPropPtoRangoBytesPointFormat05,
            self.arrayPropPtoTipoDatoPointFormat05
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat05)

        miPointformat = 6
        # print('clidhead-> (6) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat06,
            self.lasPointFieldPropertiesDictPointFormat06,
            self.lasPointFieldOrdenDictPtoMiniPointFormat06,
            self.lasPointFieldOrdenDictPtoCompPointFormat06,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat06,
            self.bytearrayPropPtoNombrePointFormat06,
            self.arrayPropPtoNombrePointFormat06,
            self.arrayPropPtoRangoBytesPointFormat06,
            self.arrayPropPtoTipoDatoPointFormat06
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat06)

        miPointformat = 7
        # print('clidhead-> (7) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat07,
            self.lasPointFieldPropertiesDictPointFormat07,
            self.lasPointFieldOrdenDictPtoMiniPointFormat07,
            self.lasPointFieldOrdenDictPtoCompPointFormat07,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat07,
            self.bytearrayPropPtoNombrePointFormat07,
            self.arrayPropPtoNombrePointFormat07,
            self.arrayPropPtoRangoBytesPointFormat07,
            self.arrayPropPtoTipoDatoPointFormat07
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat07)

        miPointformat = 8
        # print('clidhead-> (8) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat08,
            self.lasPointFieldPropertiesDictPointFormat08,
            self.lasPointFieldOrdenDictPtoMiniPointFormat08,
            self.lasPointFieldOrdenDictPtoCompPointFormat08,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat08,
            self.bytearrayPropPtoNombrePointFormat08,
            self.arrayPropPtoNombrePointFormat08,
            self.arrayPropPtoRangoBytesPointFormat08,
            self.arrayPropPtoTipoDatoPointFormat08
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat08)

        miPointformat = 9
        # print('clidhead-> (9) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat09,
            self.lasPointFieldPropertiesDictPointFormat09,
            self.lasPointFieldOrdenDictPtoMiniPointFormat09,
            self.lasPointFieldOrdenDictPtoCompPointFormat09,
        ) = lasPointProperties(miPointformat, False)
        (
            self.npArrayPropPtoPointFormat09,
            self.bytearrayPropPtoNombrePointFormat09,
            self.arrayPropPtoNombrePointFormat09,
            self.arrayPropPtoRangoBytesPointFormat09,
            self.arrayPropPtoTipoDatoPointFormat09
        ) = crearArraysPropPto(miPointformat, self.lasPointFieldPropertiesListPointFormat09)

        miPointformat = 10
        # print('clidhead-> (10) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointFormat10,
            self.lasPointFieldPropertiesDictPointFormat10,
            self.lasPointFieldOrdenDictPtoMiniPointFormat10,
            self.lasPointFieldOrdenDictPtoCompPointFormat10,
        ) = lasPointProperties(miPointformat, False)
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

        self.formatoDtypePointFormatXXNotacionOneChar = []
        for pr in self.lasPointFieldPropertiesList:
            if pr[3] == 1:
                self.formatoDtypePointFormatXXNotacionOneChar.append((pr[0], pr[2]))
            else:
                self.formatoDtypePointFormatXXNotacionOneChar.append((pr[0], pr[2], (pr[3],)))
        # print( 'clidhead-> lasPointFieldPropertiesList', self.lasPointFieldPropertiesList)
        # print( 'clidhead->', [(pr[0], pr[2], pr[3]) for pr in self.lasPointFieldPropertiesList])
        self.formatoDtypePointFormatXXNotacionNpDtype = np.dtype(self.formatoDtypePointFormatXXNotacionOneChar)
        # print('clidhead-> pfX self.formatoDtypePointFormatXXNotacionOneChar:', self.formatoDtypePointFormatXXNotacionOneChar)
        # print('clidhead-> pfX self.formatoDtypePointFormatXXNotacionNpDtype:', self.formatoDtypePointFormatXXNotacionNpDtype)

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
        #     print(f'clidhead-> Descripcion del formato formatoDtype:')
        #     print(f'{TB}-> pf8 self.formatoDtypePointFormat99NotacionOneChar: {self.formatoDtypePointFormat99NotacionOneChar}')
        #     # [('x', '=I'), ('y', '=I'), ('z', '=I'), ('intensity', 'H'), ('return_grp', 'B'), ('extra_grp', 'B'), ('classification', 'B'),
        #     # ('user_data', 'b'), ('scan_angle_rank', 'h'), ('point_source_ID', 'H'), ('raw_time', 'd'), ('red', 'H'), ('green', 'H'), ('blue', 'H'), ('nir', 'H'),
        #     # ('lasClassAsignadaASPRS19', 'B'), ('lasClassAsignadaTRKTS99', 'B'), ('lasClassPredichaMiniSubCel', 'B'), ('lasClassPredichaConvolucion', 'B'),
        #     # ('lasClassPredichaTreeASPRS19', 'B'), ('lasClassPredichaTreeTRKTS99', 'B'), ('lasClassPredichaNlnASPRS19', 'B'), ('usoSingular', 'B'),
        #     # ('nucleoUrbano', 'B'), ('landCover', 'B'), ('geoTipo', 'B'), ('cartoExtra', 'B'), ('distanciaEnDmHastaEdificio', 'B'), ('usoSingularPredicho', 'B'),
        #     # ('usoSingularPredichoA', 'B'), ('usoSingularPredichoB', 'B'), ('cotaCmSobreMdb', 'h'), ('cotaCmMdf', '=I'), ('cotaCmSobreMdfConvol16bits', 'h'),
        #     # ('cotaCmSobreMdfConual16bits', 'h'), ('cotaCmSobreMdfManual16bits', 'h'), ('esMiniMaxiSubCel', 'B'), ('esMiniMaxiCel', 'B'), ('esApice', 'B'), ('xH30', '=I'), ('yH30', '=I')]
        #     print(f'{TB}-> pf8 self.formatoDtypePointFormat99NotacionNpDtype: {self.formatoDtypePointFormat99NotacionNpDtype}')
        #     # [('x', '<u4'), ('y', '<u4'), ('z', '<u4'), ('intensity', '<u2'), ('return_grp', 'u1'), ('extra_grp', 'u1'), ('classification', 'u1'),
        #     # ('user_data', 'i1'), ('scan_angle_rank', '<i2'), ('point_source_ID', '<u2'), ('raw_time', '<f8'), ('red', '<u2'), ('green', '<u2'), ('blue', '<u2'), ('nir', '<u2'),
        #     # ('lasClassAsignadaASPRS19', 'u1'), ('lasClassAsignadaTRKTS99', 'u1'), ('lasClassPredichaMiniSubCel', 'u1'), ('lasClassPredichaConvolucion', 'u1'),
        #     # ('lasClassPredichaTreeASPRS19', 'u1'), ('lasClassPredichaTreeTRKTS99', 'u1'), ('lasClassPredichaNlnASPRS19', 'u1'), ('usoSingular', 'u1'),
        #     # ('nucleoUrbano', 'u1'), ('landCover', 'u1'), ('geoTipo', 'u1'), ('cartoExtra', 'u1'), ('distanciaEnDmHastaEdificio', 'u1'), ('usoSingularPredicho', 'u1'),
        #     # ('usoSingularPredichoA', 'u1'), ('usoSingularPredichoB', 'u1'), ('cotaCmSobreMdb', '<i2'), ('cotaCmMdf', '<u4'), ('cotaCmSobreMdfConvol16bits', '<i2'), 
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
        # print('clidhead-> (100) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.lasPointFieldPropertiesListPointCustomizado,
            self.lasPointFieldPropertiesDictPointCustomizado,
            self.lasPointFieldOrdenDictPtoMiniPointCustomizado,
            self.lasPointFieldOrdenDictPtoCompPointCustomizado,
        ) = lasPointProperties(miPointformat, False)
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
        #     # [('x', 'd'), ('y', 'd'), ('z', 'd'), ('clase', 'B'), ('retN', 'B'), ('cotaMds', 'f'), ('cotaMdb', 'f'), ('cotaMdf', 'f'), ('lasClassAsignada', 'B'), ('lasClassInferida', 'B')]
        #     print(f'{TB}-> pf8 self.formatoDtypePointCustomizadoNotacionNpDtype: {self.formatoDtypePointCustomizadoNotacionNpDtype}')
        #     # [('x', '<f8'), ('y', '<f8'), ('z', '<f8'), ('clase', 'u1'), ('retN', 'u1'), ('cotaMds', '<f4'), ('cotaMdb', '<f4'), ('cotaMdf', '<f4'), ('lasClassAsignada', 'u1'), ('lasClassInferida', 'u1')]

        # ======================================================================
        # ================= Formato dtype de las extraVariables ================
        # ======================================================================
        # Leo las propiedades del punto de mis extraVariables (le llamo pointFormat=101) de lasPointFields.cfg
        # ======================================================================
        miPointformat = 101
        # print('clidhead-> (101) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.extraVariablesPropertiesList,
            self.extraVariablesPropertiesDict,
            self.extraVariablesOrdenDictPtoMini,
            self.extraVariablesOrdenDictPtoComp,
        ) = lasPointProperties(miPointformat, self.verbose)
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
        # print('clidhead-> (102) Llamando a lasPointProperties con {}'.format(miPointformat))
        (
            self.maxiMiniSubCelPropertiesList,
            self.maxiMiniSubCelPropertiesDict,
            self.maxiMiniSubCelOrdenDictPtoMini,
            self.maxiMiniSubCelOrdenDictPtoComp,
        ) = lasPointProperties(miPointformat, self.verbose)
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

        # Basic checking of las file, nCeldas and coordinates from fileName:
        if self.verbose or __verbose__:
            printMsg(f'\nclidhead-> Coordenadas del lasfile segun cabecera antes de checkLasfile:')
            printMsg(f'{TB}-> myLasHead.xmin: {self.xmin}')
            printMsg(f'{TB}-> myLasHead.ymin: {self.ymin}')
            printMsg(f'{TB}-> myLasHead.xmax: {self.xmax}')
            printMsg(f'{TB}-> myLasHead.ymax: {self.ymax}')
        self.checkLasfile()
        # print('------------------>clidhead-> infile***ConRutaLazZ:', self.infileConRuta)
        if self.verbose or __verbose__:
            printMsg(f'clidhead-> Coordenadas del lasfile segun cabecera despues de checkLasfile:')
            printMsg(f'{TB}-> myLasHead.xmin: {self.xmin}')
            printMsg(f'{TB}-> myLasHead.ymin: {self.ymin}')
            printMsg(f'{TB}-> myLasHead.xmax: {self.xmax}')
            printMsg(f'{TB}-> myLasHead.ymax: {self.ymax}')
            printMsg(f'{"":=^80}')


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
            printMsg('clidhead-> Reading head fields properties from cartolidar/data/ext/io/lasHeadFields.cfg:')
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
                    print('clidhead-> Se va a abrir el fichero: {}'.format(self.infileConRuta))
                self.ficheroLas = open(self.infileConRuta, "rb")
                if GLO.GLBLverbose or self.verbose:
                    print('\tLeyendo el fichero abierto. Se lee el byte 104'.format(self.infileConRuta))
                self.ficheroLas.seek(104)
                byteLeido = self.ficheroLas.read(1)
                if GLO.GLBLverbose or self.verbose:
                    print('\tByte leido:', byteLeido, 'Numero de bytes:', len(byteLeido))
                fmt = int(struct.unpack("<B", byteLeido)[0])
                if GLO.GLBLverbose or self.verbose:
                    print('\tByte unpack (fmt):', fmt)
                compression_bit_7 = (fmt & 0x80) >> 7
                compression_bit_6 = (fmt & 0x40) >> 6
                if (not compression_bit_6 and compression_bit_7):
                    if GLO.GLBLverbose or self.verbose:
                        print('\t\t-> Fichero SI comprimido')
                    esComprimido = True
                else:
                    if GLO.GLBLverbose or self.verbose:
                        print('\t\t-> Fichero NO comprimido')
                    esComprimido = False
                self.ficheroLas.close()
            except Exception as err:
                printMsg('clidhead.{:006}-> System error al leer el compression bit: {}'.format(GLO.MAIN_idProceso, err))
                print('\tinfileConRuta:', self.infileConRuta)
                fmt = '-'
                if self.infileConRuta[-4:].lower() == '.laz':
                    esComprimido = True
                else:
                    esComprimido = False
                #sys.exit(0)

            # Prevalece el contenido del fichero sobre la extension
            if self.lazfile and not esComprimido and self.lasDataMem is None:
                print('clidhead.{:006}-> ATENCION: fichero laz que no es realmente un laszip (no esta comprimido)'.format(GLO.MAIN_idProceso))
                print('\t-> self.lasDataMem is None:',  self.lasDataMem is None)
                print('\t-> pointformat: {}'.format(fmt))
                self.lazfile = False
            elif not self.lazfile and esComprimido:
                print('clidhead.{:006}-> ATENCION: fichero las que en realidad es un un laszip (esta comprimido)'.format(GLO.MAIN_idProceso))
                print('\t-> self.lasDataMem is None:',  self.lasDataMem is None)
                print('\t-> pointformat: {}'.format(fmt))
                self.lazfile = True

        if not self.lasDataMem is None:
            if self.verbose:
                printMsg('clidhead-> Lectura de los datos desde el objeto de tipo <memoryview> generado a partir del objeto <bytes> creado al descomprimir el laz')
                printMsg('\t-> type(self.lasDataMem)-> {}'.format(type(self.lasDataMem)))
                printMsg('\t-> len(self.lasDataMem)->  {}'.format(len(self.lasDataMem)))
                # https://www.devdungeon.com/content/working-binary-data-python
                printMsg('clidhead-> convirtiendo bytes a memoryview')
            # ==================================================================
            self.ficheroLas = memoryview(self.lasDataMem)
            # ==================================================================
            #self.ficheroLas = self.lasDataMem # 'bytes' object has no attribute 'tell'
            if self.verbose:
                printMsg('\tclidhead-> Ok memoryview, len(ficheroLas): {}'.format(len(self.ficheroLas)))
            if len(self.ficheroLas) == 0:
                printMsg('nclidhead.{:006}-> ATENCION: no se ha leido bien el fichero laz descomprimiendo en memoria. esComprimido: {}'.format(
                    GLO.MAIN_idProceso, esComprimido))
        else:
            if self.verbose:
                printMsg('clidhead-> Lectura de los datos desde el objeto de tipo <class "_io.BufferedReader"> generado con open()')
                printMsg('\t-> type(self.lasDataMem)-> {}'.format(type(self.lasDataMem)))
            try:
            # ==================================================================
                self.ficheroLas = open(self.infileConRuta, 'rb')
                if self.verbose:
                    printMsg('\t-> type(self.ficheroLas)-> {}'.format(type(self.ficheroLas)))
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
            # print('------------------>clidhead-> infile***ConRutaLazE:', self.infileConRuta)
            self.readOk = False
            return
#             sys.exit(0)

        if self.verbose:
            printMsg('clidhead-> Fields at header of las file:')

        lasVersionIni = 'LasFormat_1_2'
        for myField in self.lasHeaderFieldListVersionsDict[lasVersionIni][1:]:
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
                        print('clidhead-> Revisar esto')
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
                printMsg('clidhead-> WARNING w2')
                printMsg('Error reading Field {} at las head'.format(myField))
                value = readBytes

            if self.verbose:
                if not self.lasDataMem is None:
                    postPosicion = len(self.headBin)
                else:
                    postPosicion = self.ficheroLas.tell()
                printMsg(
                    '\t1-> Bytes:'
                    + '\t'
                    + str(postPosicion - int(fieldProperties[0]) + 1)
                    + '-'
                    + str(postPosicion)
                    + '\t'
                    + str(myField)
                    + '\t'
                    + str(value)
                )
            self.headDict[myField] = value
            setattr(self, myField, value)

        if self.headDict['vermajor'] > 1:
            print('clidhead-> LASF version %i.%i, no implementada. Se interrumpe el programa' % (self.headDict['vermajor'], self.headDict['verminor']))
            print('clidhead->           Esta aplicacion solo esta prearada para formatos LASF 1.2, [1.3] y 1.4')
            quit()

        self.lasVersion = 'LasFormat_%i_%i' % (self.headDict['vermajor'], self.headDict['verminor'])

        if (self.headDict['vermajor'] == 1 and self.headDict['verminor'] == 3) or (self.headDict['vermajor'] == 1 and self.headDict['verminor'] == 4):
            if self.headDict['vermajor'] == 1 and self.headDict['verminor'] == 3:
                printMsg('clidhead-> Las format 1.3 only provisional (TODO)')
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
                    printMsg('clidhead-> WARNING w3a')
                    printMsg('Field:', myField)
                    value = readBytes

                if self.verbose:
                    if not self.lasDataMem is None:
                        postPosicion = len(self.headBin)
                    else:
                        postPosicion = self.ficheroLas.tell()
                    printMsg(
                        '\t2-> Bytes:'
                        + '\t'
                        + str(postPosicion - int(fieldProperties[0]) + 1)
                        + '-'
                        + str(postPosicion)
                        + '\t'
                        + str(myField)
                        + '\t'
                        + str(value)
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
                    printMsg('clidhead-> WARNING w3b')
                    printMsg('Field:', myField)
                    value = readBytes

                if self.verbose:
                    if not self.lasDataMem is None:
                        postPosicion = len(self.headBin)
                    else:
                        postPosicion = self.ficheroLas.tell()
                    printMsg(
                        '\t3-> Bytes:'
                        + '\t'
                        + str(postPosicion - int(fieldProperties[0]) + 1)
                        + '-'
                        + str(postPosicion)
                        + '\t'
                        + str(myField)
                        + '\t'
                        + str(value)
                    )
                self.headDict[myField] = value
                setattr(self, myField, value)


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def readVariableLengthRecords(self, tipoVLR='normal'):
        if tipoVLR == 'normal':
            propiedadNumVLR = 'numvlrecords'
            grupoLasHeadFields = self.lasVersion + '_vlrecord'
            idTipoVLR = ''
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
                printMsg('clidhead-> Modalidad de lectura del fichero laz/las: lectura de fichero con read()')
            else:
                printMsg('clidhead-> Modalidad de lectura del fichero laz/las: lectura de lasDataMem con acceso por puntero')
                printMsg(f'{TB}-> lasDataMem es un <bytes> generado al descomprimir el laz y luego convertido a <memoryview> (self.ficheroLas)')
                printMsg(f'{TB}-> La lectura se hace accediendo al <memoryview> (self.ficheroLas) y agegando el trozo leido (readMemView) a un <bytes> (self.headBin)')
                # self.lasDataMem: <class 'bytes'>
                # self.ficheroLas: <class 'memoryview'>
                # readMemView: <class 'memoryview'>
                # self.headBin: <class 'bytes'>
                printMsg(f'{TB}-> type(self.lasDataMem): {type(self.lasDataMem)}, type(self.ficheroLas): {type(self.ficheroLas)}')
                printMsg(f'{TB}-> type(self.headBin): {type(self.headBin)}, len(self.headBin): {len(self.headBin)}')

        self.sumaBytesVLR = 0
        if self.headDict[propiedadNumVLR] > 0:
            if self.verbose:
                printMsg(f'\nclidhead-> Numero de variable lenght records: {self.headDict[propiedadNumVLR]}')
                # print('clidhead-> self.lasHeaderFieldListVersionsDict.keys():', self.lasHeaderFieldListVersionsDict.keys())
                printMsg(f'{TB}-> Campos de LasFormat_1_2_vlrecord: {self.lasHeaderFieldListVersionsDict[grupoLasHeadFields]}')

            for nVlrecord in range(self.headDict[propiedadNumVLR]):
                if True:
#                 try:
                    for myField in self.lasHeaderFieldListVersionsDict[grupoLasHeadFields]:
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
#                         try:
                            if fieldProperties[1].strip() == 'c':
                                # String
                                # value = readBytes.rstrip(b'\x00')
#                                 if not self.lasDataMem is None:
#                                     value = readBytes.decode('latin-1')
#                                 else:
                                value = readBytes.rstrip(b'\x00').decode('latin-1')
                            elif int(fieldProperties[2]) > 1:
                                # Array -> desempaquetar a una tupla
                                value = struct.unpack(fieldProperties[2].strip() + fieldProperties[1].strip(), readBytes)
                            else:
                                # Numero binario: guardar el primer elemento de la tupla
                                value = struct.unpack(fieldProperties[1].strip(), readBytes)[0]
#                         except:
#                             printMsg('clidhead-> WARNING w4a')
#                             printMsg('Field: {}'.format(myField))
#                             value = readBytes

                        if self.verbose:
                            printMsg(
                                f'{TB}{TV}4-> Bytes: {str(prePosicion)}-{str(postPosicion)}; TipoVLR: {tipoVLR}; NumVLR: {str(nVlrecord)}; NombreVLR: {myField}; Valor: {str(value)}'
                            )
                        self.headDict['%s%s_%i' % (idTipoVLR, myField, nVlrecord)] = value
                        setattr(self, '%s%s_%i' % (idTipoVLR, myField, nVlrecord), value)
                        # self.headDict['textoVRL_%i' % nVlrecord] = value
                    if self.verbose:
                        print(f'clidhead-> Variable lenght record num: {nVlrecord} leido ok')
#                 except:
#                     printMsg('clidhead-> WARNING w4b')
#                     printMsg('Ha habido un problema al leer el vlrecord {}'.format(nVlrecord))
#                     if not self.lasDataMem is None:
#                         postPosicion = len(self.headBin)
#                     else:
#                         postPosicion = self.ficheroLas.tell()
#                     printMsg('Position:' + '\t' + str(postPosicion))
#                     printMsg('Se cierra la aplicacion')
#                     sys.exit()
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
                    printMsg(f'{TB}-> Parte variable (contenido) del vlrecord {nVlrecord}: {readBytes}')
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
                printMsg('clidhead-> No hay vlrecords')


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
#             print('clidhead-> WARNING %s' % warningId)
#             print('clidhead-> There has been a problem reading las file header')
#             if not self.lasDataMem is None:
#                 postPosicion = len(self.headBin)
#             else:
#                 postPosicion = self.ficheroLas.tell()
#             print('clidhead-> Position:', postPosicion)
#             self.ficheroLas.close()
#             sys.exit()
        return readBytes


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def adjustCornersCoordinates(self, sizeToAdjust, envolvente=False, margenAdmisible=0):
        if sizeToAdjust > 0 and self.xmin % sizeToAdjust != 0:
            if self.verbose:
                print('clidhead-> Ajustando Xmin a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                print(f'{TB}Before: {self.xmin:0.2f}', end=' ')
            if self.xmin % sizeToAdjust <= margenAdmisible or self.xmin % sizeToAdjust >= sizeToAdjust - margenAdmisible:
                self.xmin = float(sizeToAdjust * round(self.xmin / sizeToAdjust, 0))
            else:
                if envolvente:
                    self.xmin = float(sizeToAdjust * math.floor(self.xmin / sizeToAdjust))
                else:
                    self.xmin = float(sizeToAdjust * math.ceil(self.xmin / sizeToAdjust))
            if self.verbose:
                print(f'{TB}After: {self.xmin:0.2f}')
        if sizeToAdjust > 0 and self.ymin % sizeToAdjust != 0:
            if self.verbose:
                print('clidhead-> Ajustando Ymin a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                print(f'{TB}Before: {self.ymin:0.2f}', end=' ')
            if self.ymin % sizeToAdjust <= margenAdmisible or self.ymin % sizeToAdjust >= sizeToAdjust - margenAdmisible:
                self.ymin = float(sizeToAdjust * round(self.ymin / sizeToAdjust, 0))
            else:
                if envolvente:
                    self.ymin = float(sizeToAdjust * math.floor(self.ymin / sizeToAdjust))
                else:
                    self.ymin = float(sizeToAdjust * math.ceil(self.ymin / sizeToAdjust))
            if self.verbose:
                print(f'{TB}After: {self.ymin:0.2f}')
        if sizeToAdjust > 0 and self.ymax % sizeToAdjust != 0:
            if self.verbose:
                print('clidhead-> Ajustando Ymax a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                print(f'{TB}Before: {self.ymax:0.2f}', end=' ')
            if self.ymax % sizeToAdjust <= margenAdmisible or self.ymax % sizeToAdjust >= sizeToAdjust - margenAdmisible:
                self.ymax = float(sizeToAdjust * round(self.ymax / sizeToAdjust, 0))
            else:
                if envolvente:
                    self.ymax = float(sizeToAdjust * math.ceil(self.ymax / sizeToAdjust))
                else:
                    self.ymax = float(sizeToAdjust * math.floor(self.ymax / sizeToAdjust))
            if self.verbose:
                print(f'{TB}After: {self.ymax:0.2f}')
        if sizeToAdjust > 0 and self.xmax % sizeToAdjust != 0:
            if self.verbose:
                print('clidhead-> Ajustando Xmax a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                print(f'{TB}Before: {self.xmax:0.2f}', end=' ')
            if self.xmax % sizeToAdjust <= margenAdmisible or self.xmax % sizeToAdjust >= sizeToAdjust - margenAdmisible:
                self.xmax = float(sizeToAdjust * round(self.xmax / sizeToAdjust, 0))
            else:
                if envolvente:
                    self.xmax = float(sizeToAdjust * math.ceil(self.xmax / sizeToAdjust))
                else:
                    self.xmax = float(sizeToAdjust * math.floor(self.xmax / sizeToAdjust))
            if self.verbose:
                print(f'{TB}After: {self.xmax:0.2f}')
        self.xSupIzda = self.xmin
        self.ySupIzda = self.ymax
        self.xInfDcha = self.xmax
        self.yInfDcha = self.ymin


#     # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
#     def adjustCornersCoordinates(self, sizeToAdjust, envolvente=False):
#         if sizeToAdjust > 0 and self.xmin % sizeToAdjust != 0:
#             if self.verbose:
#                 print('clidhead-> Ajustando xmin a la dimension', sizeToAdjust, 'm. Envolvente:', envolvente)
#                 print('\tAntes: %0.2f' % self.xmin, end=' ')
#             if envolvente:
#                 self.xmin = float(sizeToAdjust * int(self.xmin / sizeToAdjust))
#             else:
#                 self.xmin = float(sizeToAdjust * round((self.xmin / sizeToAdjust), 0))
#             if self.verbose:
#                 print('\tDespues: %0.2f' % self.xmin)
#         if sizeToAdjust > 0 and self.ymin % sizeToAdjust != 0:
#             if self.verbose:
#                 print('clidhead-> Ajustando ymin a la dimension', sizeToAdjust, 'm. Envolvente:', envolvente)
#                 print('\tAntes: %0.2f' % self.ymin, end=' ')
#             if envolvente:
#                 self.ymin = float(sizeToAdjust * int(self.ymin / sizeToAdjust))
#             else:
#                 self.ymin = float(sizeToAdjust * round((self.ymin / sizeToAdjust), 0))
#             if self.verbose:
#                 print('\tDespues: %0.2f' % self.ymin)
#         if sizeToAdjust > 0 and self.ymax % sizeToAdjust != 0:
#             if self.verbose:
#                 print('clidhead-> Ajustando ymax con la dimension de la celda.')
#                 print('\tAntes: %0.2f' % self.ymax, end=' ')
#             if envolvente:
#                 self.ymax = float(sizeToAdjust * math.ceil((self.ymax / sizeToAdjust)))
#             else:
#                 self.ymax = float(sizeToAdjust * round((self.ymax / sizeToAdjust), 0))
#             if self.verbose:
#                 print('\tDespues: %0.2f' % self.ymax)
#         if sizeToAdjust > 0 and self.xmax % sizeToAdjust != 0:
#             if self.verbose:
#                 print('clidhead-> Ajustando xmax con la dimension de la celda.')
#                 print('\tAntes: %0.2f' % self.xmax, end=' ')
#             if envolvente:
#                 self.xmax = float(sizeToAdjust * math.ceil((self.xmax / sizeToAdjust)))
#             else:
#                 self.xmax = float(sizeToAdjust * round((self.xmax / sizeToAdjust), 0))
#             if self.verbose:
#                 print('\tDespues: %0.2f' % self.xmax)
#         self.xSupIzda = self.xmin
#         self.ySupIzda = self.ymax
#         self.xInfDcha = self.xmax
#         self.yInfDcha = self.ymin


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def calculateCornersFromHeader(self):
        """
        Reads coordinates of the corners from header (stored in float)
        """
        self.xmin = float(self.headDict['xmin'])
        self.xmax = float(self.headDict['xmax'])
        self.ymin = float(self.headDict['ymin'])
        self.ymax = float(self.headDict['ymax'])
        self.xSupIzda = self.xmin
        self.ySupIzda = self.ymax
        self.xInfDcha = self.xmax
        self.yInfDcha = self.ymin
        self.xmin = self.headDict['xmin']
        self.xmax = self.headDict['xmax']
        self.ymin = self.headDict['ymin']
        self.ymax = self.headDict['ymax']


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def checkLasfile(self):

        # ======================================================================
        if self.pointreclen == 0:
            nBytesAcum = 0
            for propiedad in self.lasPointFieldPropertiesList:
                nBytesAcum += propiedad[1]
            self.pointreclen = nBytesAcum
        # ======================================================================

        # ======================================================================
        self.calculateCornersFromHeader()
        if self.metersBlock > 0:
            if (
                (self.xmax - self.xmin - (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)) > self.metersBlock
                or (self.ymax - self.ymin - (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)) > self.metersBlock
            ):
                # if self.coordenadasTransformadasDe29a30:
                print('{:_^80}'.format(''))
                if self.TRNShuso29:
                    print('\nclidhead-> Rango de coordenadas del fichero lidar superior a la dimension del bloque debido a la transformacion de coordenadas de h29 a h30')
                else:
                    print('\nclidhead-> ATENCION: el rango de coordenadas del fichero lidar es superior a la dimension del bloque')
                    print('clidhead-> Cambiar la variable de configuracion GLBLmetrosBloque en clidbase.xml o usar otro fichero las')
                print(
                    '\t->', round((self.xmax - self.xmin), 2),
                    '>', self.metersBlock,
                    'y/o', round((self.ymax - self.ymin), 2),
                    '>', self.metersBlock
                )
                print('\tself.xmin: {}'.format(round(self.xmin, 2)))
                print('\tself.ymin: {}'.format(round(self.ymin, 2)))
                print('\tself.xmax: {}'.format(round(self.xmax, 2)))
                print('\tself.ymax: {}'.format(round(self.ymax, 2)))
                # if not self.coordenadasTransformadasDe29a30:
                if not self.TRNShuso29:
                    print('clidhead-> Se recomienda cambiar GLBLmetrosBloque a', math.ceil(max(self.ymax - self.ymin, self.xmax - self.xmin)), 'metros')
                    print('\tSe cierra la aplicacion para cambiar manualmente GLBLmetrosBloque en clidbase.xml')
                    print('{:o^80}'.format(' Fin - revisar errores '))
                    sys.exit(0)
                print('{:=^80}'.format(''))
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

        # GLBLcoordMinMaxAcordesConBloque

        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        if self.TRNShuso29:
            LCLmetrosBloqueX = self.metersBlock
            LCLmetrosBloqueY = self.metersBlock
        else:
            if (
                (self.xmax - self.xmin) >= self.metersBlock - (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
                or (self.ymax - self.ymin) >= self.metersBlock - (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
            ) and (
                (self.xmax - self.xmin) < self.metersBlock + (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
                or (self.ymax - self.ymin) < self.metersBlock + (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
            ) or GLO.GLBLcoordMinMaxAcordesConBloque:
                # El lasFile se ajusta +- a la dimension prevista por GLBLmetrosBloque
                if (self.xmax - self.xmin) >= self.metersBlock + 1 or (self.ymax - self.ymin) >= self.metersBlock + 1:
                    envolvente = True
                    self.adjustCornersCoordinates(self.metersBlock, envolvente=True, margenAdmisible=1)
                else:
                    envolvente = False
                    self.adjustCornersCoordinates(self.metersBlock, envolvente=False, margenAdmisible=1)
                LCLmetrosBloqueX = GLO.GLBLmetrosBloque
                LCLmetrosBloqueY = GLO.GLBLmetrosBloque
                if self.verbose:
                    print('\nclidhead-> 1 Adjusting corners with block size:', self.metersBlock, 'm')
                    print('clidhead->   xmin, xmax, ymin, ymax:', self.xmin, self.xmax, self.ymin, self.ymax)
                    print(f'clidhead->   envolvente: {envolvente}')
            elif (
                (self.xmax - self.xmin) >= self.metersBlock + (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
                or (self.ymax - self.ymin) >= self.metersBlock + (2 * GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque)
            ):
                print('clidhead-> Alguna dimension del lasFile es superior al GLBLmetrosBloque (establecido en clidbase.xml)')
                print('\t-> Valor actual de GLBLmetrosBloque:', GLO.GLBLmetrosBloque, 'm.')
                print('\t-> Rango de coord x:', (self.xmax - self.xmin), 'Rango de coord y:', (self.ymax - self.ymin))
                if GLO.MAIN_ENTORNO == 'windows':
                    selec = input('Seguir adelante con el valor actual de GLBLmetrosBloque (S/n)')
                    rptaMantener = False if selec.upper() == 'N' else True
                    if not rptaMantener:
                        print('clidhead-> Se finaliza la aplicacion')
                        print('\t-> Se cierra la aplicacion para cambiar manualmente GLBLmetrosBloque en clidbase.xml')
                        print('{:=^80}'.format(' Fin - revisar errores '))
                        sys.exit(0)
            else:
                if self.verbose:
                    print('{:!^80}'.format(''))
                    print('clidhead-> ATENCION: el rango de coordenadas del lasFile es inferior a la dimension del bloque (dimension -lado- estandar de fichero lidar):')
                    print('\t-> Si ocurre con todos los ficheros, cambiar la variable de configuracion GLBLmetrosBloque en clidbase.xml o usar otro fichero las')
                    print('{:!^80}'.format(''))
                    print('\tself.xmin: {:0.2f}'.format(self.xmin))
                    print('\tself.xmax: {:0.2f}'.format(self.xmax))
                    print('\t\tRango X: {:0.2f}'.format(self.xmax - self.xmin, 'metros'))
                    print('\tself.ymin: {:0.2f}'.format(self.ymin))
                    print('\tself.ymax: {:0.2f}'.format(self.ymax))
                    print('\t\tRango Y: {:0.2f}'.format(self.ymax - self.ymin, 'metros'))
                    print(
                        'clidhead-> La aplicacion esta configurada para procesar ficheros lidar (las) de',
                        self.metersBlock,
                        'x',
                        self.metersBlock,
                        'metros (variables de configuracion en clidbase.xml)',
                    )
                if min(self.xmax - self.xmin, self.ymax - self.ymin) < 500:
                    if self.verbose:
                        print('\tSe recomienda usar ficheros lidar de mas de 500 x 500 metros')
                    if False:
                        selec = input(
                            'Continuar cambiando para esta ejecucion el parametro GLBLmetrosBloque al nuevo valor %i ? (s/n)'
                            % round(min(self.xmax - self.xmin, self.ymax - self.ymin), 0)
                        )
                        rptaCambiar = False if selec.upper() == 'N' else True
                        if not rptaCambiar:
                            print('clidhead-> Se finaliza la aplicacion')
                            print('\tSe cierra la aplicacion para cambiar manualmente GLBLmetrosBloque en clidbase.xml')
                            print('{:o^80}'.format(' Fin - revisar errores '))
                            sys.exit(0)
                    rptaCambiar = True
                else:
                    rptaCambiar = True
    
                if rptaCambiar:
                    if GLO.GLBLadapatarMetrosBloque:
                        GLBNmetrosBloque = int(GLO.GLBLmetrosCelda * math.ceil(min(self.xmax - self.xmin, self.ymax - self.ymin) / GLO.GLBLmetrosCelda))
                        if self.verbose:
                            print('clidhead-> Se recomienda cambiar la variable de configuracion GLBLmetrosBloque en clidbase.xml')
                            print('\tSe modifica para esta ejecucion el parametro GLBLmetrosBloque')
                            print('\tSe cambia el parametro GLBLmetrosBloque para esta ejecucion. Nuevo valor:', GLBNmetrosBloque, 'metros.')
                        else:
                            printMsg('\nclidhead-> ATENCION: se cambia el parametro GLBLmetrosBloque para esta ejecucion. Nuevo valor: {} metros'.format(GLBNmetrosBloque))
                        nuevosParametroConfiguracion = {}
                        nuevosParametroConfiguracion['GLBLmetrosBloque'] = [GLBNmetrosBloque, 'GrupoDimensionCeldasBloques', '', 'int']
                        clidconfig.configVarsDict = clidconfig.leerCambiarVariablesGlobales(nuevosParametroConfiguracion)
                        # input('Pulsa una tecla')
                        LCLmetrosBloqueX = int(GLO.GLBLmetrosCelda * math.ceil((self.xmax - self.xmin) / GLO.GLBLmetrosCelda))
                        LCLmetrosBloqueY = int(GLO.GLBLmetrosCelda * math.ceil((self.ymax - self.ymin) / GLO.GLBLmetrosCelda))
                    else:
                        print('clidhead-> No se modifica el parametro GLBLmetrosBloque porque GLBLadapatarMetrosBloque es {}'.format(GLO.GLBLadapatarMetrosBloque))
                        LCLmetrosBloqueX = self.metersBlock
                        LCLmetrosBloqueY = self.metersBlock
                else:
                    LCLmetrosBloqueX = self.metersBlock
                    LCLmetrosBloqueY = self.metersBlock
                if self.verbose:
                    print('{:!^80}\n'.format(''))
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        self.metersBlockX = self.headDict['xmax'] - self.headDict['xmin']
        self.metersBlockY = self.headDict['ymax'] - self.headDict['ymin']
        if self.metersBlock == 0:
            if round(self.metersBlockX, 2) != round(self.metersBlockY, 2):
                print('clidhead-> Warning: not square block. x: %0.2f; y: %0.2f' % (self.metersBlockX, self.metersBlockY))
        if self.metersCell > 0 and self.metersBlock % self.metersCell != 0:
            print('clidhead-> WARNING: block size is not multiple of cell size: block size: %0.2f; cell size: %0.2f' % (self.metersBlock, self.metersCell))
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        if (
            (self.xmin % self.metersCell < 0.9 and self.xmin % self.metersCell > 0)
            or self.xmax % self.metersCell >= 0.1
            or (self.ymin % self.metersCell < 0.9 and self.ymin % self.metersCell > 0)
            or self.ymax % self.metersCell >= 0.1
        ):
            envolvente = True
            self.adjustCornersCoordinates(self.metersCell, envolvente=True, margenAdmisible=0.1)
        else:
            envolvente = False
            self.adjustCornersCoordinates(self.metersCell, envolvente=False, margenAdmisible=0.1)
        if self.verbose:
            print('\nclidhead-> Ajustando esquinas a {} m (bis)'.format(self.metersCell))
            print('\txmin, xmax, ymin, ymax:', self.xmin, self.xmax, self.ymin, self.ymax)
            print(f'\t-> envolvente: {envolvente}')
        self.nCeldasX = int(math.ceil(float(LCLmetrosBloqueX) / GLO.GLBLmetrosCelda))
        self.nCeldasY = int(math.ceil(float(LCLmetrosBloqueY) / GLO.GLBLmetrosCelda))
        self.metrosBloqueX = int(math.ceil(self.xmax - self.xmin))
        self.metrosBloqueY = int(math.ceil(self.ymax - self.ymin))
        if self.verbose:
            print('clidhead-> Coordenadas min y max ajustadas a dimensiones de bloque y celdas:')
            print('\txmin: %07.1f; xmax: %07.1f; ymin: %07.1f; ymax: %07.1f' % (self.xmin, self.xmax, self.ymin, self.ymax))
            print('clidhead-> Dimesion del bloque ajustado: %i x %i metros' % (self.metrosBloqueX, self.metrosBloqueY))
            print('clidhead-> Numero de celdas previsto de acuerdo al nuevo valor de GLBLmetrosBloque: %i x %i' % (self.nCeldasX, self.nCeldasY))
        # ======================================================================

        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        # Asigned coordinates of up left corner after the lasFile name (and year)
        (
            self.fileCoordYear,
            self.xSupIzdaDelNombre,
            self.ySupIzdaDelNombre,
            self.fileYear
        ) = getFileCoordFromName(
            self.infileConRuta
        )
        # No utilizo fileCoordYear como propiedad de esta clase sino que uso
        # el valor obtenido en clidbase.py que tiene en cuenta el nombre y
        # las coordenadas de la cabecera xSupIzda ySupIzda
        # Ademas en ese modulo se chequea la coherencia coordenadas de nombre y cabecera
        if False:
            if self.fileCoordYear:
                print(
                    'clidhead-> Coordinates from las name: fileCoordYear:',
                    self.fileCoordYear,
                    'xSupIzdaDelNombre, ySupIzdaDelNombre:',
                    self.xSupIzdaDelNombre,
                    self.ySupIzdaDelNombre,
                    'fileYear:',
                    self.fileYear,
                )
            else:
                # print( 'clidhead-> Cannot obtain coordinates from las name')
                print('\tclidhead-> Cannot obtain coordinates from las name: %s' % (self.infileConRuta))

            # Check if coordinates match (lasFile name and lasFile head)
            if (
                self.xSupIzdaDelNombre != 0
                and self.ySupIzdaDelNombre != 0
                and (round(self.xSupIzda, 0) != round(self.xSupIzdaDelNombre, 0) or round(self.ySupIzda, 0) != round(self.ySupIzdaDelNombre, 0))
            ):
                printMsg('clidhead-> Warning: coordinates obtained from lasFile head do not match coordinates readed at lasFile name')
                printMsg('\tUpLeft corner accoding to lasFile name: xUpLeft: %0.1f; yUpLeft: %0.1f' % (self.xSupIzdaDelNombre, self.ySupIzdaDelNombre))
                printMsg('\tUpLeft corner accoding to lasFile head: xUpLeft: %0.1f; yUpLeft: %0.1f' % (self.xSupIzda, self.ySupIzda))
        # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

        # ======================================================================
        nBytesPorPuntoCheck = sum(int(pointField[1]) for pointField in self.lasPointFieldPropertiesList)
        if nBytesPorPuntoCheck != self.pointreclen:
            print('clidhead-> WARNING: error in nBytesPorPunto: {} {}'.format(nBytesPorPuntoCheck, self.pointreclen))
            print('clidhead-> ATENCION: Revisar esto')
        # ======================================================================

        # inputfile_las_baseName = os.path.splitext(os.path.basename(inputfile_las))[0] #Nombre sin extension
        # printMsg('clidhead-> Procesando sin liblas: %s' % (inputfile_las_baseName))

        if self.verbose:
            if self.headDict['numvlrecords'] == 0:
                print('\nclidhead-> La informacion del srs en el fichero las esta en formato compatible con: %s' % self.formatoSRS)
            else:
                print('\nclidhead-> La informacion del srs en el fichero las esta en formato compatible con: %s' % self.formatoSRS)
                if 'Description_0' in self.headDict.keys() and self.headDict['Description_0'].rstrip('\x00') == 'No Variable Lenght Records (VRL)':
                    print(self.headDict['Description_0'])
                else:
                    printMsg('\tCampos de LasFormat_1_2_vlrecord:' + str(self.lasHeaderFieldListVersionsDict[self.lasVersion + '_vlrecord']))
                    for nVlrecord in range(self.headDict['numvlrecords']):
                        print('\tInfo de Variable Lenght Records (VRL)', nVlrecord)
                        for myField in self.lasHeaderFieldListVersionsDict[self.lasVersion + '_vlrecord']:
                            fieldname = '%s_%i' % (myField, nVlrecord)
                            value = str(self.headDict[fieldname])
                            # value = self.headDict['textoVRL_%i' % nVlrecord]
                            print('\t------>', fieldname.rjust(25), '->', value)
            print('clidhead-> Las file created with software: %s' % str(self.headDict['gensoftware']))


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def showAlllasFileVersions(self):
        print('\nclidhead-> Cheking lasFile versions:')
        (
            self.lasHeaderFieldListVersionsDict,
            self.lasHeaderFieldPropertiesDict,
            self.lasHeaderFieldPropertiesList
        ) = lasHeadProperties()
        for lasFileVersion in sorted(self.lasHeaderFieldListVersionsDict.keys()):
            print('\nclidhead-> LasFile version: %s' % lasFileVersion)
            print('\tclidhead-> list of fields:', self.lasHeaderFieldListVersionsDict[lasFileVersion])
            print('\tclidhead-> Properties of fields:')
            for lasHeadField in self.lasHeaderFieldListVersionsDict[lasFileVersion]:
                print('\tclidhead-> \t', lasFileVersion + '_' + lasHeadField, self.lasHeaderFieldPropertiesDict[lasFileVersion + '_' + lasHeadField])


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def showAllPointFormats(self):
        print('\nclidhead-> Cheking las point formats:')
        # No incluyo el format 101 y 102 que incluye las extraVariables y la maxiMiniSubCel
        for nPointFormat in range(1, 11):
            try:
                print('\tclidhead-> Point format: %i' % nPointFormat)
                # print('clidhead-> (y) Llamando a lasPointProperties con {}'.format(nPointFormat))
                (
                    self.lasPointFieldPropertiesList,
                    self.lasPointFieldPropertiesDict,
                    self.lasPointFieldOrdenDictPtoMini,
                    self.lasPointFieldOrdenDictPtoComp,
                ) = lasPointProperties(nPointFormat, self.verbose)
                nBytesPorPuntoCheck = sum(int(pointField[1]) for pointField in self.lasPointFieldPropertiesList)
                print('\tclidhead-> \t', nBytesPorPuntoCheck, self.lasPointFieldPropertiesList)
            except:
                print('\tclidhead-> \tPoint format %i not implemented\n' % nPointFormat)


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def showInfoLas(self, mostrarPropiedadesDeLaClase=False):
        printMsg('clidhead->   lasVersion:     %s' % self.lasVersion)
        printMsg('  pointformat:               %i' % self.pointformat)
        strPuntosTotal = "{:,}".format(self.numptrecords)
        printMsg('  Number of returns (total): %s' % (strPuntosTotal))
        printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

        printMsg('\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        printMsg('clidhead->   Header Summary (sin "\x00" en sysid y gensoftware)')
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
        printMsg('  Min X Y Z:                   %f / %f / %f' % (self.xmin, self.ymin, self.zmin))
        printMsg('  Max X Y Z:                   %f / %f / %f' % (self.xmax, self.ymax, self.zmax))
        printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

        #         printMsg('\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        #         printMsg('  nBytesPorPunto:              %i' % self.pointreclen, self.verbose)
        #         printMsg('  xoffset: %f, yoffset: %f' % (self.headDict['xoffset'], self.headDict['yoffset']), self.verbose)
        #         printMsg('  Coords (round)  -> xmin: %i, xmax: %i, ymin: %i, ymax: %i:' %\
        #                         (round(self.xmin, 0), round(self.xmax, 0), round(self.ymin, 0), round(self.ymax, 0)), self.verbose)
        #         printMsg('  Coords (float)-> xmin: %f, xmax: %f, ymin: %f, ymax: %f:' %\
        #                         (self.xmin, self.xmax, self.ymin, self.ymax), self.verbose)
        #         printMsg('  self.listaTuplasPropPtoTodas: %s' % str(self.lasPointFieldPropertiesList), self.verbose)
        #         printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

        printMsg('\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        printMsg('clidhead->')
        if self.lasVersion == 'LasFormat_1_3' or self.lasVersion == 'LasFormat_1_4':
            printMsg('\tStart of Waveform Data Packet Record:            %i' % self.waveformStart)
        else:
            printMsg('\tStart of Waveform Data Packet Record:            %s' % 'No waveform data (las format 1.2)')

        if self.lasVersion == 'LasFormat_1_4':
            printMsg('\tStart of first Extended Variable Length Record:  %i' % self.extendedVLRstart)
            printMsg('\tNumber of Extended Variable Length Records:      %i' % self.extendedVLRnValues)
            printMsg('\tExtended number of point records:                %i' % self.pointrecords)
            printMsg('\tExtended number of points by return:             %s' % str(self.pointsbyreturn))
        else:
            printMsg('\tStart of first Extended Variable Length Record:  %s' % 'No extended VLR')
            printMsg('\tNumber of Extended Variable Length Records:      %s' % 'No extended VLR')
            printMsg('\tExtended number of point records:                %s' % 'No extended VLR')
            printMsg('\tExtended number of points by return:             %s' % 'No extended VLR')
        printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

        printMsg('\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        printMsg('clidhead-> Spatial Reference:')
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
            print('clidhead-> LASF format 1.2 solo admite srs compatible con GeoTiff')
            if self.headDict['numvlrecords'] == 0:
                print('clidhead-> Pero el LASF no incluye esta informacion al no incluir ningun VLR')
            else:
                for nVlrecord in range(self.headDict['numvlrecords']):
                    if (self.headDict['UserID_%i' % nVlrecord]).rstrip('\x00') == 'LASF_Projection' or (self.headDict['Description_%i' % nVlrecord]).rstrip(
                        '\x00'
                    ) == 'GeoTiff GeoKeyDirectoryTag':
                        print('clidhead-> Ver mas adelante el contenido del VLR GeoTiff GeoKeyDirectoryTag')
        elif self.lasVersion == 'LasFormat_1_4':
            print('clidhead-> LASF format 1.4 configurado para srs compatible con', self.formatoSRS)
            if self.headDict['numvlrecords'] == 0:
                print('clidhead-> Pero el LASF no incluye esta informacion al no incluir ningun VLR')
            else:
                for nVlrecord in range(self.headDict['numvlrecords']):
                    if 'Description_%i' % nVlrecord in self.headDict.keys():
                        if (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'OGC Transformation Record':
                            print('clidhead-> Ver mas adelante el contenido del VLR OGC Transformation Record')
                        elif (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoTiff GeoKeyDirectoryTag':
                            print('clidhead-> Ver mas adelante el contenido del VLR GeoTiff GeoKeyDirectoryTag')
        printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

        printMsg('\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        if 'Description_0' in self.headDict.keys() and self.headDict['Description_0'].rstrip('\x00') == 'No Variable Lenght Records (VRL)':
            print(self.headDict['Description_0'])
        else:
            directorioDeTrabajo = buscarDirectorioDataExt()
            VLRsFileName = os.path.join(
                directorioDeTrabajo, 'io/VLRs_{:04}{:02}{:02}.geo'.format(
                    datetime.datetime.now().year,
                    datetime.datetime.now().month,
                    datetime.datetime.now().day
                )
            )
            VLRsFile = open(VLRsFileName, mode='wb')
            # printMsg('Campos de LasFormat_1_2_vlrecord:' + str(self.lasHeaderFieldListVersionsDict[self.lasVersion + '_vlrecord']))
            for nVlrecord in range(self.headDict['numvlrecords']):
                if self.lasVersion == 'LasFormat_1_4':
                    print('clidhead->   Variable length header record %i of %i:' % (nVlrecord, self.extendedVLRnValues))
                else:
                    print('clidhead->   Variable length header record %i:' % (nVlrecord))
                for myField in self.lasHeaderFieldListVersionsDict[self.lasVersion + '_vlrecord']:
                    fieldname = '%s_%i' % (myField, nVlrecord)
                    # value = self.headDict['textoVRL_%i' % nVlrecord]
                    if myField == 'Description' or myField == 'UserID':
                        # value = self.headDict[fieldname].decode('latin-1')
                        value = self.headDict[fieldname]
                        print('clidhead->  ', myField.rjust(25), '->', value)
                    else:  # Reserved, RecordID, RecordLengthAfterHeader
                        value = str(self.headDict[fieldname])
                        print('clidhead->  ', myField.rjust(25), '->', value)
                #                     print( 'clidhead-> ------>UserID:                  %s' % str(self.headDict['UserID']) )
                #                     print( 'clidhead-> ------>RecordID:                %s' % str(self.headDict['RecordID']) )
                #                     print( 'clidhead-> ------>RecordLengthAfterHeader: %s' % str(self.headDict['RecordLengthAfterHeader']) )
                #                     print( 'clidhead-> ------>Description:             %s' % str(self.headDict['Description']) )
                #                     print( 'clidhead-> ------>textoVRL:                %s' % str(self.headDict['textoVRL_%i' % nVlrecord]) )

                fieldname = '%s_%i' % ('VLR_', nVlrecord)
                # value = self.headDict['VRL_%i' % nVlrecord].rstrip(b'\x00')
                value = self.headDict['VRL_%i' % nVlrecord]
                VLRsFile.write(value)
                VLRsFile.write(b'\n')

                if (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'OGC Transformation Record':
                    print(('OGC %s COORDINATE SYSTEM:' % self.formatoSRS).rjust(25))
                    print('clidhead->      ', value.decode('latin-1').rstrip('\x00'))
                elif (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'OGR variant of OpenGIS WKT SRS':
                    print('clidhead->  ', fieldname.rjust(25), '->', value.decode('latin-1').rstrip('\x00'))
                elif (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoTiff GeoKeyDirectoryTag':
                    # ver https://www.awaresystems.be/imaging/tiff/tifftags/geokeydirectorytag.html
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
                            # print( 'clidhead-> root.tag->', root.tag)
                            for item in root:
                                if 'srsName' in item.tag:
                                    srsName = item.text
                                    # print( 'clidhead-> +>Sistema de referencia:', item.text)
                                elif 'srsID' in item.tag:
                                    # print( 'clidhead-> +>', item.tag)
                                    for item2 in item:
                                        # <gml:name codeSpace="urn:ogc:def:crs:EPSG::">25830</gml:name>
                                        if 'name' in item2.tag:
                                            srsID = item2.text
                                        # print( 'clidhead->   -->>', item2.tag, '>', item2.text)
                                        # print( 'clidhead->        attrib->', item2.attrib)
                                elif 'baseCRS' in item.tag:
                                    # print( 'clidhead-> +>', item.tag)
                                    for item2 in item:
                                        for item3 in item2:
                                            if 'srsName' in item3.tag:
                                                srsBase = item3.text
                                                # print( 'clidhead->     --->>>', item3.tag, '>', item3.text)
                                elif 'definedByConversion' in item.tag:
                                    pass
                                elif 'usesCartesianCS' in item.tag:
                                    pass
                        except:
                            srsTag = 'Desconocdo'
                            srsName = 'Desconocdo'
                            srsBase = 'Desconocdo'
                        # print( 'clidhead-> EPSG', valuePlus[31], '->', srsTag, srsName, 'Elipsoide:', srsBase)

                        print('clidhead->     GeoKeyDirectoryTag version %i.%i.%i number of keys %i' % valuePlus[:4])
                        print(
                            'clidhead->       key %i tiff_tag_location %i count %i value_offset %i - GTModelTypeGeoKey: (#TODO) ModelTypeProjected -Provisional '
                            % valuePlus[4:8]
                        )
                        print(
                            'clidhead->       key %i tiff_tag_location %i count %i value_offset %i - GTRasterTypeGeoKey: (#TODO)RasterPixelIsArea -Provisional'
                            % valuePlus[8:12]
                        )
                        print(
                            'clidhead->       key %i tiff_tag_location %i count %i value_offset %i - GTCitationGeoKey: (#TODO)ETRS89 / UTM zone 30N -Provisional'
                            % valuePlus[12:16]
                        )
                        print(
                            'clidhead->       key %i tiff_tag_location %i count %i value_offset %i - GeogCitationGeoKey: (#TODO)ETRS89 -Provisional (#TODO)'
                            % valuePlus[16:20]
                        )
                        print(
                            'clidhead->       key %i tiff_tag_location %i count %i value_offset %i - GeogAngularUnitsGeoKey: (#TODO) Angular_Degree -Provisional'
                            % valuePlus[20:24]
                        )
                        print(
                            'clidhead->       key %i tiff_tag_location %i count %i value_offset %i - GeogTOWGS84GeoKey: (#TODO) TOWGS84[0,0,0] -Provisional'
                            % valuePlus[24:28]
                        )
                        print(
                            'clidhead->       key %i tiff_tag_location %i count %i value_offset %i - ProjectedCSTypeGeoKey: %s'
                            % (valuePlus[28], valuePlus[29], valuePlus[30], valuePlus[31], srsName)
                        )
                        print(
                            'clidhead->       key %i tiff_tag_location %i count %i value_offset %i - ProjLinearUnitsGeoKey: (#TODO) Linear_Meter -Provisional'
                            % valuePlus[32:36]
                        )
                    except:
                        valuePlus = 'No unpack'
                        print('clidhead-> GeoTiff GeoKeyDirectoryTag pendiente de desempaquetar y descifrar adecuadamente (#TODO)')
                elif (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoTiff GeoAsciiParamsTag':
                    print('clidhead->    GeoTIFF COORDINATE SYSTEM (AsciiParams):'.rjust(25))
                    print('clidhead->      ', value.decode('latin-1'))
                elif (self.headDict['Description_%i' % nVlrecord]).rstrip('\x00') == 'GeoTiff GeoDoubleParamsTag':
                    print('clidhead->    GeoTIFF COORDINATE SYSTEM (DoubleParams):'.rjust(25))
                    print('clidhead->  ', fieldname.rjust(25), '->', value.decode('latin-1'))
                else:
                    # print( 'clidhead-> ->', str(self.headDict['Description_%i' % nVlrecord].rstrip('\x00')) , '<-')
                    print('clidhead->  ', 'longitud'.rjust(25), '->', len(value))
                    try:
                        valorDecodificado = value.decode('latin-1')
                        print('clidhead->  ', fieldname.rjust(25), '->', valorDecodificado)
                    except:
                        try:
                            valorDecodificado = value.decode('latin-1', errors='ignore')
                            print('clidhead->  ', fieldname.rjust(25), '->', valorDecodificado, 'Decodificado ignorando errores')
                        except:
                            print('clidhead->  ', fieldname.rjust(25), '->', value, 'No decodificado')

                # print( 'clidhead->  ', fieldname.rjust(25), end=' -> ')
                # for letra in value:
                #    print(chr(letra), end='')
                # print( 'clidhead-> ')
                if nVlrecord < self.headDict['numvlrecords'] - 1:
                    printMsg('')
            VLRsFile.close()
        printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

        self.infoLasPoints(verbose=True)

        if mostrarPropiedadesDeLaClase:
            printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
            propiedades = [unaPropiedad for unaPropiedad in dir(self) if isinstance(getattr(self, unaPropiedad), property)]
            printMsg('\nclidhead-> Properties of LasHead object:', self.verbose)
            printMsg('\nPropiedades de self %s:' % str(propiedades), self.verbose)
            for unaPropiedad in dir(self):
                printMsg('{:>50}\t{}'.format(unaPropiedad, type(getattr(self, unaPropiedad)), getattr(self, unaPropiedad)), self.verbose)
            printMsg('\nVariables de self:', self.verbose)
            for variableDeMiBloque in vars(self).keys():
                printMsg('{:>50}\t{}'.format(variableDeMiBloque, vars(self)[variableDeMiBloque]), self.verbose)
            printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')


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
#                 'clidhead-> ATENCION: se amplia GLBLnMaxPtosCeldaArrayPredimensionadaTodos de',
#                 GLO.GLBLnMaxPtosCeldaArrayPredimensionadaTodos,
#                 'a',
#                 LCLnMaxPtosCeldaArrayPredimensionadaTodos,
#             )
#         else:
#             LCLnMaxPtosCeldaArrayPredimensionadaTodos = GLO.GLBLnMaxPtosCeldaArrayPredimensionadaTodos

        try:
            from cartolidar.clidfr import cliddata
        except:
            sys.stderr.write(f'clidhead-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).')
            sys.stderr.write('\t-> Se importan paquetes de cartolidar desde clidhead del directorio local {os.getcwd()}/....')
            from clidfr import cliddata
        myLasData = cliddata.LasData(self)
        myLasData.nPtosAleer = self.numptrecords
        myLasData.sampleLas = 1
#         self.LCLnMaxPtosCeldaArrayPredimensionadaTodos = LCLnMaxPtosCeldaArrayPredimensionadaTodos

        # ======================================================================oooo

        # ======================================================================oooo
        # oooooooooooooooooooooooo Lectura del fichero las oooooooooooooooooooooooooo
        # ======================================================================oooo
        # myLasData.readLasData(byREFAlmacenarPuntosComoNumpyDtype=True)  # Fuerzo almacenarPuntosComoNumpyDtype
        myLasData.leerLasDataLazLas(
            self.infileConRuta,
            self.fileCoordYear,
            self.LCLordenColoresInput,
        )
        # oooooooooo Muestro para verificacion el numero de puntos leidos ooooooooooo
        myLasData.numPuntosValidosTotalesSegunCabecera = self.headDict['numptrecords']
        # print( 'clidhead-> Numero de puntos segun la cabecera del las:', myLasData.numPuntosValidosTotalesSegunCabecera )
        if verbose:
            printMsg('\noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
            printMsg('clidhead-> Puntos que se indica en la cabecera:   %i puntos' % myLasData.numPuntosValidosTotalesSegunCabecera)
            if GLO.GLBLnumeroDePuntosAleer == 0:
                printMsg('clidhead-> Puntos a leer (segun XML):             Todos (0=todos)')
            else:
                printMsg('clidhead-> Puntos a leer (segun XML):             %i puntos' % GLO.GLBLnumeroDePuntosAleer)
            printMsg('clidhead-> Puntos cargados en la RAM:             %i puntos' % myLasData.numPuntosCargadosEnLaRAM)
            if self.infileConRuta[-4:].lower == '.las':
                printMsg(
                    'clidhead-> Segun el num de bytes del fichero hay: %0.5f puntos (fichero de %0.2f Mb)'
                    % (
                        ((os.path.getsize(self.infileConRuta) - self.headDict['offset']) / self.pointreclen),
                        os.path.getsize(self.infileConRuta) / 1e6,
                    )
                )
                printMsg(
                    'clidhead->                                        El num de puntos segun num de bytes calculado figura con decimales para ver si cuadra.'
                )

            if not GLO.GLBLalmacenarPuntosComoNumpyDtype:
                printMsg(
                    'clidhead-> Segun el num de bytes cargados en memoria, hay: %0.1f puntos' % (len(myLasData.ficheroCompletoEnLaRAM) / self.pointreclen)
                )
                printMsg(
                    'clidhead->                                                 = len(myLasData.ficheroCompletoEnLaRAM) (%i) / self.pointreclen (%i)'
                    % (len(myLasData.ficheroCompletoEnLaRAM), self.pointreclen)
                )
                printMsg(
                    'clidhead->                                                 ->myLasData.ficheroCompletoEnLaRAM se lee tras leer la cabecera, con myLasData.infile.read(self.pointreclen*self.numptrecords)'
                )
            if myLasData.numPuntosCargadosEnLaRAM != myLasData.numPuntosValidosTotalesSegunCabecera:
                printMsg('clidhead-> ATENCION: el numero de puntos que se indica en la cabecera no coincide con el numero de puntos en el fichero las.')
            printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

        pointformat = self.pointformat
        nPtosAleerDefinitivo = self.numptrecords
        miHeadScale = np.array([self.headDict['xscale'], self.headDict['yscale'], self.headDict['zscale']])
        miHeadOffset = np.array([self.headDict['xoffset'], self.headDict['yoffset'], self.headDict['zoffset']])

        if pointformat == 4 or pointformat == 5:
            print('clidhead-> ATENCION:')
            print('clidhead-> Los formatos 4 y 5 incluyen informacion de la waveform y no estan implementados')
            print('clidhead-> Se leen correctamente, pero la informacion de la forma de la onda no se interpreta')
            print('clidhead-> Quitar esto de lasPoint para que funcione sin usar esa informacion')
            sys.exit(0)

        timeIniRecorreLas = time.time()
        (
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
            myLasData.ficheroCompletoEnLaRAM,
            nPtosAleerDefinitivo,
            pointformat,
            miHeadScale,
            miHeadOffset,
            self.miPtoNpRecordPointFormatXX,
            self.miPtoNpRecordPointFormat99,
            LCLordenColoresInput=self.LCLordenColoresInput,
        )

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
            print('clidhead-> Numero de segundos y siguientes retornos:')
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
        printMsg('clidhead-> Reporting minimum and maximum for all LAS point record entries ...')
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
            print('clidhead-> Hay valores negativos (<0) del parametro miPto_classification')
        if noData_miPto_raw_time:
            print('clidhead-> Hay valores nulos o negativos (<=0) del parametro noData_miPto_raw_time')
        if noData_miPto_actual_time:
            print('clidhead-> Hay valores nulos o negativos (<=0) del parametro noData_miPto_actual_time')
        if noData_miPto_red:
            print('clidhead-> Hay valores negativos (<0) del parametro noData_miPto_red')
        if noData_miPto_green:
            print('clidhead-> Hay valores negativos (<0) del parametro noData_miPto_green')
        if noData_miPto_blue:
            print('clidhead-> Hay valores negativos (<0) del parametro noData_miPto_blue')
        if noData_miPto_nir:
            print('clidhead-> Hay valores negativos (<0) del parametro noData_miPto_nir')
        if noData_miPto_intensity:
            print('clidhead-> Hay valores negativos (<0) del parametro noData_miPto_intensity')
        if noData_point_source_ID:
            print('clidhead-> Hay valores negativos (<0) del parametro noData_point_source_ID')
        printMsg('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

        print('clidhead-> number of first returns:'.rjust(45), nFirstReturns)
        print('clidhead-> number of intermediate returns:'.rjust(45), nInterReturns)
        print('clidhead-> number of last returns:'.rjust(45), nLastReturns)
        print('clidhead-> number of single returns:'.rjust(45), nSingleReturns)
        print('clidhead-> total number of returns:'.rjust(45), nTotalReturns)

        print('clidhead-> covered area in square meters/kilometers:'.rjust(45), superficieEscaneadaEnM2, '/', superficieEscaneadaEnM2 / 1e6)

        print(
            'clidhead-> point density: all returns %0.2f first only %0.2f last only %0.2f (per square meter)'
            % (densidadAllReturns, densidadFirstReturns, densidadLastReturns)
        )
        print(
            'clidhead->       spacing: all returns %0.2f first only %0.2f last only %0.2f (in meters)'
            % (1 / np.sqrt(densidadAllReturns), 1 / np.sqrt(densidadFirstReturns), 1 / np.sqrt(densidadLastReturns))
        )
        print('clidhead-> overview over number of returns of given pulse:', end=' ')

        if nReturnsPorNumReturn[16] > 0:
            print('clidhead-> Atencion: numero de retornos superiores al limite (%i)' % maxNumReturn, end=' ')
        print()
        print('clidhead-> histogram of classification of points:')
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
        for nClase in range(len(nPuntosPorClase)):
            if nPuntosPorClase[nClase] > 0:
                if pointformat <= 5:
                    if nClase < 13:
                        print(str(nPuntosPorClase[nClase]).rjust(16), '%s (%i)' % (textoClase[nClase], nClase))
                    elif nClase < 32:
                        print(str(nPuntosPorClase[13]).rjust(16), '%s (%i)' % (textoClase[13], 13))
                    else:
                        print('clidhead-> Clase %i no permitida' % nClase)
                else:
                    if nClase < 19:
                        print(str(nPuntosPorClase[nClase]).rjust(16), '%s (%i)' % (textoClase[nClase], nClase))
                    elif nClase < 64:
                        print(str(nPuntosPorClase[nClase]).rjust(16), '%s (%i)' % (textoClase[19], nClase))
                    elif nClase < 256:
                        print(str(nPuntosPorClase[nClase]).rjust(16), '%s (%i)' % (textoClase[20], nClase))
                    else:
                        print('clidhead-> Clase %i no permitida' % nClase)

        timeFinRecorreLas = time.time()
        horaFin = time.asctime(time.localtime(timeFinRecorreLas))
        segundosDuracion = round((timeFinRecorreLas - timeIniRecorreLas), 2)
        minutosDuracion = round(segundosDuracion / 60.0, 2)
        print(
            'clidhead.%06i-> Fin de procesado de %s'
            % (GLO.MAIN_idProceso, os.path.basename(self.infileConRuta))
        )
        print(
            'clidhead.{:006}-> Tiempo de procesado:\t{:0.2}\tsegundos ({:0.2f} minutos).'.format(
                GLO.MAIN_idProceso, segundosDuracion, minutosDuracion
            )
        )
        print(
            'clidhead.{:006}-> Fecha/hora:\t{}'.format(
                GLO.MAIN_idProceso, horaFin
                )
        )
        

# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
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
        print('clidhead-> ATENCION: Falta', configFileName, 'Corregir')
        print('clidhead-> No se escriben los Variable Length Records')
        print('clidhead-> no encontrado', configFileName)
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
def lasPointProperties(pointformat=3, verbose=False):
    """
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
        # Lo guardo como dict:
        lasPointFieldPropertiesDict[myField] = tuple(properties)
        # Lo guardo como lista, con el primer valor el nombre de la propiedad
        myList = [myField]
        myList.extend(properties)
        lasPointFieldPropertiesList.append(tuple(myList))
        nOrden += 1
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
# Duplico esta funcion es la original; la tengo duplicada en clidbase.py
def getFileCoordFromName(
        infile,
        fileYearPorDefecto='0000'
    ):
    fileCoord = '000_0000'
    fileYear = '0000'
    for char1 in range(len(infile) - 4 - 8):
        # fileCoord_ = infile[char1: char1 + 3] + '_' + infile[char1 + 4: char1 + 8]
        if (
            (infile[char1: char1 + 4]).isdigit()
            and (char1 < 4 or not (infile[char1 - 4: char1 - 1]).isdigit())
            and (char1 == 0 or (infile[char1 - 1]) in ['-', '_'])
            and (infile[char1 + 4]) in ['-', '_', '.']
        ):
            # El fichero tiene la anualidad pero no las coordenadas cuando:
            #     Hay cuatro caracteres digitos no precedidos por otros 4 digitos
            #     Y estan precedidos y seguidos por '_' o '-' (salvo que sean los 4 primeros o 4 ultimos)
            fileCoord = '000_0000'
            fileYear = infile[char1: char1 + 4]
        elif (
            (infile[char1: char1 + 3]).isdigit()
            and (infile[char1 + 4: char1 + 8]).isdigit()
            and (infile[char1 + 3]) in ['-', '_']
            and (char1 == 0 or (infile[char1 - 1]) in ['-', '_'])
            and (infile[char1 + 8]) in ['-', '_', '.']
        ):
            # El fichero tiene las coordenadascuando:
            #    El nombre incluye el patron XXX_YYYY o XXX-YYY
            #     Y estan precedidos y seguidos por '_' o '-' (salvo que sean los 4 primeros o 4 ultimos)
            fileCoord = infile[char1: char1 + 3] + '_' + infile[char1 + 4: char1 + 8]
            # Ademas tiene la anualidad si despues de las coordenadas:
            #     Hay cuatro caracteres digitos
            #     Y estan precedidos y seguidos por '_' o '-'
            fileYear = '0000'
            if len(infile) - 4 - 4 > char1 + 9:
                for char2 in range(char1 + 9, len(infile) - 4 - 4):
                    if (
                        (infile[char2: char2 + 4]).isdigit()
                        and (infile[char2 - 1]) in ['-', '_']
                        and (infile[char2 + 4]) in ['-', '_', '.']
                    ):
                        fileYear = infile[char2: char2 + 4]
                        break
            break

    if fileYear == '0000':
        fileYear = fileYearPorDefecto
    fileCoordYear = fileCoord + '_' + str(fileYear)

    try:
        xSupIzdaDelNombre = int(fileCoord[:3]) * 1000
        ySupIzdaDelNombre = int(fileCoord[4:8]) * 1000
        # print( 'clidbase-> xSupIzda, ySupIzda (de acuerdo al nombre del fichero)        ', xSupIzdaDelNombre, ySupIzdaDelNombre )
    except:
        xSupIzdaDelNombre = 0
        ySupIzdaDelNombre = 0

    if fileCoord == '000_0000':
        print( 'clidbase-> AVISO: No se ha podido extraer las coordenadas del nombre fichero: %s; fileCoord: %s; fileYear: %s' % (infile, fileCoord, fileYear) )

    return fileCoordYear, xSupIzdaDelNombre, ySupIzdaDelNombre, fileYear


# ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
def getFileCoordFromNameOld(infile, fileYear=''):
    # print( 'clidhead-> 2. obteniendo coordenada de', infile)
    if '/' in infile or '\\' in infile:
        infile = os.path.basename(infile)
    if infile[:8].lower() == 'las_cam_' and infile[21:26].lower() == '_nav_':
        # Ej.: las_cam_600_4700_2017_NAV_EPSG25830
        #     las_cam_621_4792_2017_NAV_EPSG25830
        # Lidar de Navarra 2017
        fileCoord = infile[8:11] + '_' + infile[12:16]
        fileYear = infile[17:21]
        # if GLO.GLBLverbose:
        #    print( '\tclidhead-> Las File de Navarra:', fileCoord, 'year', fileYear)
    elif infile[:7].lower() == 'las_cm_' and infile[20:25].lower() == '_nav_':
        # Ej.: las_cm_600-4700_2012_NAV_SUR_EPSG25830.laz
        #     las_cm_600-4764_2012_NAV_NORTE_EPSG25830.laz
        # Lidar de Navarra 2012
        fileCoord = infile[7:10] + '_' + infile[11:15]
        fileYear = infile[16:20]
        # if GLO.GLBLverbose:
        #    print( '\tclidhead-> Las File de Navarra:', fileCoord, 'year', fileYear)
    elif infile.lower().startswith('pnoa_2010_lote7_cyl-mad'):
        # Ej.: pnoa_2010_lote7_cyl-mad_354-4614_ort-cla-cir.laz
        fileCoord = infile[24:27] + '_' + infile[28:32]
        fileYear = infile[5:9]
    elif (infile.upper()).startswith('PNOA_2016_MAD_'):
        # Ej: PNOA_2016_MAD_420-4524_ORT-CLA-IRC_PenalaraMadrid.laz
        fileCoord = infile[14:17] + '_' + infile[18:22]
        fileYear = infile[5:9]
    elif (infile.upper()).startswith('PNOA_2014_CYL_SW_25CM_'):
        # Ej: PNOA_2014_CYL_SW_25cm_302_4458_ORT-CLA-COL_Gredos.laz
        fileCoord = infile[22:25] + '_' + infile[26:30]
        fileYear = infile[5:9]

    elif (infile.upper()).startswith('PNOA_2019_CYL_C_'):
        # PNOA_2019_CYL_C_
        fileCoord = infile[16:19] + '_' + infile[20:24]
        fileYear = infile[5:9]
    elif (infile.upper()).startswith('PNOA_') and (infile.upper())[9:13] == '_CYL':
        # Ej: PNOA_2017_CYL_SE_398-4508_ORT-CLA-IRC_etc.las
        # Ej: PNOA_2017_CYL_SE_418-4522_ORT-CLA-RGBI_LF14PF8_Penalara.laz
        # Ej: PNOA_2019_CYL_C_372-4656_ORT-CLA-RGB.laz
        # PNOA_2017_CYL_SE_
        # PNOA_2017_CYL_CE_
        # PNOA_2018_CYL_CE_
        # PNOA_2019_CYL_CE_
        # PNOA_2021_CYL_NW_
        fileCoord = infile[17:20] + '_' + infile[21:25]
        fileYear = infile[5:9]

    elif len(infile) == 4 + 1 + 4 + 1 + 3 + 1 + 8 + 1 + 11 + 4:  # 38
        # Ej: PNOA_2016_MAD_398-4507_ORT-CLA-IRC.laz
        fileCoord = infile[14:17] + '_' + infile[18:22]
        fileYear = infile[5:9]
    elif len(infile) == 24 + 20 + 4:  # 48
        # Ej: PNOA_2010_Lote5_CYL-RIO_328-4638_ORT-CLA-COL.laz
        # fileCoord = infile[24:32]
        fileCoord = infile[24:27] + '_' + infile[28:32]
    elif len(infile) == 20 + 20 + 4:  # 44
        # Ej: PNOA_2010_LOTE4_CYL_160-4656_ORT-CLA-COL.laz
        # fileCoord = infile[20:28]
        fileCoord = infile[20:23] + '_' + infile[24:28]
    elif len(infile) == 17 + 20 + 4:  # 41
        # Ej: PNOA_2014_CYL_SW_198_4568_ORT-CLA-COL.laz
        # fileCoord = infile[17:25]
        fileCoord = infile[17:20] + '_' + infile[21:25]
    elif len(infile) == 22 + 20 + 4:  # 46
        # Ej: PNOA_2014_CYL_SW_25cm_264-4520_ORT-CLA-COL.laz
        # fileCoord = infile[22:30]
        fileCoord = infile[22:25] + '_' + infile[26:30]
    elif len(infile) == 22 + 22 + 20 + 4:  # 68
        # Ej: PNOA_2014_CYL_SW_25cm_PNOA_2014_CYL_SW_25cm_170_4466_ORT-000-COL.laz
        # fileCoord = infile[44:52]
        fileCoord = infile[44:47] + '_' + infile[48:52]
    elif len(infile) == 12:
        # Ej: 328-4638.laz
        fileCoord = infile[:3] + '_' + infile[4:8]
    elif len(infile) == 17:
        # Ej: 328-4638_2017.laz
        fileCoord = infile[:3] + '_' + infile[4:8]
        fileYear = infile[9:13]
    elif len(infile) == 8 + 5 + 7 + 4 or infile[13:17] == '_new':  # 24
        # Ej: 398_4508_2017_new_X0.las
        fileCoord = infile[:3] + '_' + infile[4:8]
        fileYear = infile[9:13]
    elif infile[:3].isdigit() and infile[4:8].isdigit():
        # Ej: 398_4508.las
        # Ej: 398_4508_2017.las
        fileCoord = infile[:3] + '_' + infile[4:8]
        if infile[9:13].isdigit():
            fileYear = infile[9:13]
        else:
            fileYear = '0000'
    elif infile[:6].isdigit() and infile[7:14].isdigit():
        # Ej.: 766000_3846000.laz
        fileCoord = infile[:3] + '_' + infile[7:11]
        fileYear = '0000'
    else:
        print('\n{:_^80}'.format(''))
        print('clidhead-> ATENCION: No se identifican coordenadas y anualidad del Las File por seguir una convencion de nombre desconocida:')
        print('\t', infile)
        fileCoord = '000_0000'
        fileYear = '0000'

    # print('clidhead-> fileCoord:', type(fileCoord), fileCoord)
    # print('clidhead-> fileYear: ', type(fileYear), fileYear)
    
    if fileYear != '0000':
        fileCoordYear = fileCoord + '_' + str(fileYear)
    else:
        try:
            fileYear = infile[-8:-4]
        except:
            fileYear = '0000'
        fileCoordYear = fileCoord + '_' + str(fileYear)

    try:
        xSupIzdaDelNombre = int(fileCoord[:3]) * 1000
        ySupIzdaDelNombre = int(fileCoord[4:8]) * 1000
        # print( 'clidhead-> xSupIzda, ySupIzda (de acuerdo al nombre del fichero)        ', xSupIzdaDelNombre, ySupIzdaDelNombre )
    except:
        xSupIzdaDelNombre = 0
        ySupIzdaDelNombre = 0
        fileCoordYear = False
        # print( 'clidhead-> No se ha podido extraer las coordenadas del nombre fichero: %s; fileCoord (extraido del nombre del fichero): %s' % (infile, fileCoord) )

    return fileCoordYear, xSupIzdaDelNombre, ySupIzdaDelNombre, fileYear


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
        vermajor=1,
        verminor=4,
        pointformat=8,
        numptrecords=0,
        numptbyreturn=np.zeros(16, dtype=np.int64),
        xmin=0,
        ymin=0,
        xmax=0,
        ymax=0,
        zmin=0,
        zmax=0,
        xscale=0,
        yscale=0,
        zscale=0,
        xoffset=0,
        yoffset=0,
        zoffset=0,
        GPSTimeType='',
        CRS='WKT',
        filesourceid=0,
        guid1=0,
        guid2=0,
        guid3=0,
        guid4=np.zeros(8, dtype=np.int8),
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
        self.miSoftware = f'CartoLid v {__version__}. {GLO.MAIN_copyright}'
        self.gensoftware = self.miSoftware[:31].ljust(32, '\x00')
        if verbose:
            print(f'clidhead-> Software original: {self.myOldLasHead.headDict["gensoftware"]}')
            nuevoSoftware = self.gensoftware.rstrip('\x00') # No se permite \ dentro del f-format
            print(f'clidhead-> Nuevo Software:    {nuevoSoftware}')

        # ======================================================================
        # Uso estos valores para:
        #    Numero de puntos:
        #        Original y legacy    -> numptrecords = 4, =L, 1
        #        New in pointformat>5 -> pointrecords = 8, Q, 1
        #    Numero de retornos por pulso:
        #        Original y legacy    -> pointsbyreturn = 120, Q, 15
        #        New in pointformat>5 -> numptbyreturn = 20, L, 5
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
        self.numptbyreturn = numptbyreturn
        self.numptrecords = numptrecords
        self.pointrecords = self.numptrecords  # Para LASF 1.4
        self.pointsbyreturn = self.numptbyreturn  # Para LASF 1.4
        # ======================================================================

        # ======================================================================
        if xmin == 0 and ymin == 0 and not self.myOldLasHead is None:
            self.xmin = self.myOldLasHead.xmin
            self.ymin = self.myOldLasHead.ymin
        else:
            self.xmin = xmin
            self.ymin = ymin

        if xmax == 0 and ymax == 0 and not self.myOldLasHead is None:
            self.xmax = self.myOldLasHead.xmax
            self.ymax = self.myOldLasHead.ymax
        else:
            self.xmax = xmax
            self.ymax = ymax

        if zmin == 0 and zmax == 0 and not self.myOldLasHead is None:
            self.zmin = self.myOldLasHead.zmin
            self.zmax = self.myOldLasHead.zmax
        else:
            self.zmin = zmin
            self.zmax = zmax
        # ======================================================================

        self.adjustCornersCoordinates(1.0, envolvente=True)
        if self.verbose:
            print('\nclidhead-> Ajustando esquinas a {} m'.format(1))
            print('clidhead->   xmin, xmax, ymin, ymax:', self.xmin, self.xmax, self.ymin, self.ymax)
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

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
        if xoffset == 0 and not self.myOldLasHead is None:
            self.xoffset = self.myOldLasHead.xoffset
        else:
            self.xoffset = xoffset

        if yoffset == 0 and not self.myOldLasHead is None:
            self.yoffset = self.myOldLasHead.yoffset
        else:
            self.yoffset = yoffset

        if zoffset == 0 and not self.myOldLasHead is None:
            self.zoffset = self.myOldLasHead.zoffset
        else:
            self.zoffset = zoffset
        # ======================================================================

        if self.verbose:
            print('------------------->clidhead-> self.xscale:', self.xscale, 'xscale:', xscale)
            print('------------------->clidhead-> self.xoffset:', self.xoffset, 'xoffset:', xoffset)

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
        # Reading Las Head properties for all Las Formats (lasHeadFields.cfg)
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
                    print(lasVersion, myField, 'nuevoHeaderSize', nuevoHeaderSize)
        if self.verminor >= 3:
            lasVersion = 'LasFormat_1_3'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersion]:
                # Lista ordenada de campos para cada version de Las Format
                fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersion + '_' + myField]
                nuevoHeaderSize += int(fieldProperties[0])
                if self.verbose:
                    print(lasVersion, myField, 'nuevoHeaderSize', nuevoHeaderSize)
        if self.verminor >= 4:
            lasVersion = 'LasFormat_1_4'
            for myField in self.lasHeaderFieldListVersionsDict[lasVersion]:
                # Lista ordenada de campos para cada version de Las Format
                fieldProperties = self.lasHeaderFieldPropertiesDict[lasVersion + '_' + myField]
                nuevoHeaderSize += int(fieldProperties[0])
                if self.verbose:
                    print(lasVersion, myField, 'nuevoHeaderSize', nuevoHeaderSize)
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
        ) = lasPointProperties(self.pointformat, self.verbose)
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
        ) = lasPointProperties(miPointformat, self.verbose)
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
        ) = lasPointProperties(miPointformat, self.verbose)
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
        self.headDict['xmax'] = self.xmax  # = 8, d, 1
        # Min X double 8 bytes *
        self.headDict['xmin'] = self.xmin  # = 8, d, 1
        # Max Y double 8 bytes *
        self.headDict['ymax'] = self.ymax  # = 8, d, 1
        # Min Y double 8 bytes *
        self.headDict['ymin'] = self.ymin  # = 8, d, 1
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
        self.headDict['pointsbyreturn'] = self.numptbyreturn  # = 8, Q, 15
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
    #         self.xmax = xmax
    #         self.xmin = xmin
    #         self.ymax = ymax
    #         self.ymin = ymin
    #         self.zmax = zmax
    #         self.zmin = zmin
    #
    #         self.headDict['infile'] = self.newLasFileNameConRuta
    #         self.headDict['numptrecords'] = self.numptrecords
    #         self.headDict['numptbyreturn'] = self.numptbyreturn
    #         self.headDict['xmax'] = self.xmax
    #         self.headDict['xmin'] = self.xmin
    #         self.headDict['ymax'] = self.ymax
    #         self.headDict['ymin'] = self.ymin
    #         self.headDict['zmax'] = self.zmax
    #         self.headDict['zmin'] = self.zmin
    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def adjustCornersCoordinates(self, sizeToAdjust, envolvente=False):
        if sizeToAdjust > 0 and self.xmin % sizeToAdjust != 0:
            if self.verbose:
                print('clidhead-> Ajustando Xmin a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                print('\tBefore: %0.2f' % self.xmin, end=' ')
            if envolvente:
                self.xmin = float(sizeToAdjust * math.floor(self.xmin / sizeToAdjust))
            else:
                self.xmin = float(sizeToAdjust * math.ceil(self.xmin / sizeToAdjust))
            if self.verbose:
                print('\tAfter: %0.2f' % self.xmin)
        if sizeToAdjust > 0 and self.ymin % sizeToAdjust != 0:
            if self.verbose:
                print('clidhead-> Ajustando Ymin a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                print('\tBefore: %0.2f' % self.ymin, end=' ')
            if envolvente:
                self.ymin = float(sizeToAdjust * math.floor(self.ymin / sizeToAdjust))
            else:
                self.ymin = float(sizeToAdjust * math.ceil(self.ymin / sizeToAdjust))
            if self.verbose:
                print('\tAfter: %0.2f' % self.ymin)
        if sizeToAdjust > 0 and self.ymax % sizeToAdjust != 0:
            if self.verbose:
                print('clidhead-> Ajustando Ymax a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                print('\tBefore: %0.2f' % self.ymax, end=' ')
            if envolvente:
                self.ymax = float(sizeToAdjust * math.ceil(self.ymax / sizeToAdjust))
            else:
                self.ymax = float(sizeToAdjust * math.floor(self.ymax / sizeToAdjust))
            if self.verbose:
                print('\tAfter: %0.2f' % self.ymax)
        if sizeToAdjust > 0 and self.xmax % sizeToAdjust != 0:
            if self.verbose:
                print('clidhead-> Ajustando Xmax a la dimension de la celda/bloque de {} m.'.format(sizeToAdjust))
                print('\tBefore: %0.2f' % self.xmax, end=' ')
            if envolvente:
                self.xmax = float(sizeToAdjust * math.ceil(self.xmax / sizeToAdjust))
            else:
                self.xmax = float(sizeToAdjust * math.floor(self.xmax / sizeToAdjust))
            if self.verbose:
                print('\tAfter: %0.2f' % self.xmax)
        self.xSupIzda = self.xmin
        self.ySupIzda = self.ymax
        self.xInfDcha = self.xmax
        self.yInfDcha = self.ymin


    # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    def wkt25830(self):
        # EPSG:25830 -> ETRS89 / UTM zone 30N
        return 'PROJCS["ETRS89 / UTM zone 30N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","25830"]]'

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
    import clidbase
