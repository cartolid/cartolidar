#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Module included in cartolidar project 
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidtwcfg (ancillary to clidtwins) is used for clidtwins configuration.
It creates global object GLO with configuration parameters as properties.
GLO can be imported from clidtwins module to read configuration parameters.
clidtwcfg requires clidconfig module (clidax package of cartolidar).

clidtwins provides classes and functions that can be used to search for
areas similar to a reference one in terms of dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''

import os
import sys
import pathlib
import traceback
import logging
from configparser import RawConfigParser
import unicodedata
try:
    import psutil
    psutilOk = True
except:
    psutilOk = False

# Recuperar la captura de errores de importacion en la version beta
# try:
if True:
    from cartolidar.clidax import clidconfig
# except:
#     sys.stderr.write(f'qlidtwins-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).')
#     sys.stderr.write('\t-> Se importa clidconfig desde clidtwcfg del directorio local {os.getcwd()}/clidtools.')
#     from clidax import clidconfig
myUser = clidconfig.infoUsuario()


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
if (
    'tests/test_' in sys.argv[0]
    or 'tests\\test_' in sys.argv[0]
    or r'tests\test_' in sys.argv[0]
    or '/pytest' in sys.argv[0]
    or r'\pytest' in sys.argv[0]
    or 'prueba' in sys.argv[0]
):
    TRNS_testTwins = True
else:
    TRNS_testTwins = False
# ==============================================================================

# ==============================================================================
thisModule = __name__.split('.')[-1]
# class ContextFilter(logging.Filter):
#     """
#     This is a filter which injects contextual information into the log.
#     """
#
#     def filter(self, record):
#         record.thisUser = myUser
#         record.thisFile = thisModule[:10]
#         return True
# myFilter = ContextFilter()
# ==============================================================================
# formatter1 = '{asctime}|{name:10s}|{levelname:8s}|{thisUser:8s}|> {message}'
# formatterFile = logging.Formatter(formatter1, style='{', datefmt='%d-%m-%y %H:%M:%S')
formatterCons = logging.Formatter('{message}', style='{')

# fileLog = logging.FileHandler('qlidtwins.log', mode='w')
# fileLog.set_name(thisModule)
# fileLog.setLevel(logging.DEBUG)
# fileLog.setFormatter(formatterFile)
# fileLog.addFilter(myFilter)

consLog = logging.StreamHandler()
if __verbose__ == 3:
    consLog.setLevel(logging.DEBUG)
elif __verbose__ == 2:
    consLog.setLevel(logging.INFO)
elif __verbose__ == 1:
    consLog.setLevel(logging.WARNING)
elif not __quiet__:
    consLog.setLevel(logging.ERROR)
else:
    consLog.setLevel(logging.CRITICAL)
consLog.setFormatter(formatterCons)

myLog = logging.getLogger(thisModule)
myLog.setLevel(logging.DEBUG)
# myLog.addFilter(myFilter)
# myLog.addHandler(fileLog)
myLog.addHandler(consLog)
# ==============================================================================
myLog.debug('{:_^80}'.format(''))
myLog.debug('clidtwcfg-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================

# ==============================================================================
# El idProceso sirve para dar nombres unicos a los ficheros de configracion y
# asi poder lanzar trabajos paralelos con distintas configuraciones.
# Sin embargo, qlidtwins no esta pensada para lanzar trabajos en paralelo.
# Mantengo el idProceso por si acaso
if '--idProceso' in sys.argv and len(sys.argv) > sys.argv.index('--idProceso') + 1:
    MAIN_idProceso = sys.argv[sys.argv.index('--idProceso') + 1]
else:
    # MAIN_idProceso = random.randint(1, 999998)
    MAIN_idProceso = 0
    sys.argv.append('--idProceso')
    sys.argv.append(MAIN_idProceso)
# ==============================================================================


# ==============================================================================
def infoUsuario():
    if psutilOk:
        try:
            USERusuario = psutil.users()[0].name
        except Exception as excpt:
            USERusuario = psutil.users()
        if not isinstance(USERusuario, str) or USERusuario == '':
            USERusuario = 'local'
        return USERusuario
    else:
        return 'SinUsuario'


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


# ==============================================================================
def leerConfig(LOCL_configDictPorDefecto, LOCL_configFileNameCfg, LOCL_verbose=False, LOCL_verboseAll=False):
    myLog.info('\n{:_^80}'.format(''))
    myLog.info('clidtwcfg-> Fichero de configuracion:  {}'.format(LOCL_configFileNameCfg))
    # ==========================================================================
    if not os.path.exists(LOCL_configFileNameCfg):
        myLog.info('\t-> Fichero no disponible; se crea con valores por defecto.')
        # En ausencia de fichero de configuracion, uso valores por defecto y los guardo en un nuevo fichero cfg
        config = RawConfigParser()
        config.optionxform = str  # Avoid change to lowercase
    
        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            grupoParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion][1]
            if not grupoParametroConfiguracion in config.sections():
                if LOCL_verboseAll:
                    myLog.debug('\t\tclidtwcfg-> grupoParametros nuevo:', grupoParametroConfiguracion)
                config.add_section(grupoParametroConfiguracion)
        # Puedo agregar otras secciones:
        # config.add_section('custom')
    
        if LOCL_verboseAll:
            myLog.debug('\t\tclidtwcfg-> Lista de parametros de configuracion por defecto:')
        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            listaParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion]
            valorParametroConfiguracion = listaParametroConfiguracion[0]
            if len(listaParametroConfiguracion) > 1:
                grupoParametroConfiguracion = listaParametroConfiguracion[1]
            else:
                grupoParametroConfiguracion = 'dasolidar'
            if len(listaParametroConfiguracion) > 2:
                tipoParametroConfiguracion = listaParametroConfiguracion[2]
            else:
                tipoParametroConfiguracion = 'desconocido'
            if len(listaParametroConfiguracion) > 3:
                descripcionParametroConfiguracion = listaParametroConfiguracion[3]
            else:
                descripcionParametroConfiguracion = ''
    
            # config.set(grupoParametroConfiguracion, nombreParametroDeConfiguracion, [str(valorParametroConfiguracion), tipoParametroConfiguracion])
            if not descripcionParametroConfiguracion is None:
                if (
                    'á' in descripcionParametroConfiguracion
                    or 'é' in descripcionParametroConfiguracion
                    or 'í' in descripcionParametroConfiguracion
                    or 'ó' in descripcionParametroConfiguracion
                    or 'ú' in descripcionParametroConfiguracion
                    or 'ñ' in descripcionParametroConfiguracion
                    or 'ç' in descripcionParametroConfiguracion
                ):
                    descripcionParametroConfiguracion = ''.join(unicodedata.normalize("NFD", c)[0] for c in str(descripcionParametroConfiguracion))
                if (descripcionParametroConfiguracion.encode('utf-8')).decode('cp1252') != descripcionParametroConfiguracion:
                    descripcionParametroConfiguracion = ''
    
            listaConcatenada = '{}|+|{}'.format(
                str(valorParametroConfiguracion),
                str(tipoParametroConfiguracion),
                # str(descripcionParametroConfiguracion)
            )
    
            config.set(
                grupoParametroConfiguracion,
                nombreParametroDeConfiguracion,
                listaConcatenada
            )
            if LOCL_verboseAll:
                myLog.debug('\t\t\t-> {}: {} (tipo {})-> {}'.format(nombreParametroDeConfiguracion, valorParametroConfiguracion, tipoParametroConfiguracion, descripcionParametroConfiguracion))

        try:
            with open(LOCL_configFileNameCfg, mode='w+') as configfile:
                config.write(configfile)
        except PermissionError as excpt:
            program_name = 'clidtwcfg.py'
            # myLog.error(f'\n{program_name}-> Error PermissionError:\n{excpt}')
            (lineError, descError, typeError) = mensajeError(program_name)
            if lineError == 13 or descError.strerror == 'Permission denied' or typeError == 'PermissionError':
                sys.stderr.write(f'Revisar el acceso de escritura en la ruta:\n')
                sys.stderr.write(f'\t\t{os.path.dirname(LOCL_configFileNameCfg)}\n')  # = {os.path.dirname(exc_obj.filename)}
                sys.stderr.write(f'\t-> Esta es la rua en la que se intenta guardar el archivo de configuracion:\n')
                sys.stderr.write(f'\t\t{LOCL_configFileNameCfg}\n')  # {exc_obj.filename}
                sys.stderr.write(f'\t-> Si no tiene acceso de escritura en esta ruta ejecute\n')
                sys.stderr.write(f'\t   la aplicacion desde una ruta que no tenga esta restriccion.\n')
            sys.exit(0)

        except UnicodeError as excpt:
            program_name = 'clidtwcfg.py'
            # myLog.error(f'\n{program_name}-> Error UnicodeError:\n{excpt}')
            mensajeError(program_name)
            myLog.error(f'\nclidtwcfg-> ATENCION, revisar caracteres no admitidos en el fichero de configuracion: {LOCL_configFileNameCfg}')
            myLog.error('\tEjemplos: vocales acentuadas, ennes, cedillas, flecha dchea (->), etc.')
            sys.exit(0)

        except ValueError as excpt:
            program_name = 'clidtwcfg.py'
            # myLog.error(f'\n{program_name}-> Error ValueError:\n{excpt}')
            mensajeError(program_name)
            sys.exit(0)

        except Exception as excpt:
            program_name = 'clidtwcfg.py'
            # myLog.error(f'\n{program_name}-> Error Exception:\n{excpt}')
            mensajeError(program_name)
            sys.exit(0)

    # Asigno los parametros de configuracion a varaible globales:
    config = RawConfigParser()
    config.optionxform = str  # Avoid change to lowercase
    
    
    # Confirmo que se ha creado correctamente el fichero de configuracion
    if not os.path.exists(LOCL_configFileNameCfg):
        myLog.error('\nclidtwcfg-> ATENCION: fichero de configuracion no encontrado ni creado:', LOCL_configFileNameCfg)
        myLog.error('\t-> Revisar derechos de escritura en la ruta en la que esta la aplicacion')
        sys.exit(0)
    
    try:
        LOCL_configDict = {}
        config.read(LOCL_configFileNameCfg)
        if LOCL_verboseAll:
            myLog.debug('\t-> Parametros de configuracion:')
        for grupoParametroConfiguracion in config.sections():
            for nombreParametroDeConfiguracion in config.options(grupoParametroConfiguracion):
                strParametroConfiguracion = config.get(grupoParametroConfiguracion, nombreParametroDeConfiguracion)
                listaParametroConfiguracion = strParametroConfiguracion.split('|+|')
                valorPrincipal = listaParametroConfiguracion[0]
                if len(listaParametroConfiguracion) > 1:
                    tipoParametroConfiguracion = listaParametroConfiguracion[1]
                else:
                    tipoParametroConfiguracion = 'desconocido'
                valorParametroConfiguracion = clidconfig.valorConfig(
                    valorPrincipal,
                    valorAlternativoTxt='',
                    usarAlternativo=False,
                    nombreParametro=nombreParametroDeConfiguracion,
                    tipoVariable=tipoParametroConfiguracion,
                )

                if len(listaParametroConfiguracion) > 2:
                    descripcionParametroConfiguracion = listaParametroConfiguracion[2]
                else:
                    descripcionParametroConfiguracion = ''
                if nombreParametroDeConfiguracion[:1] == '_':
                    grupoParametroConfiguracion_new = '_%s' % grupoParametroConfiguracion
                else:
                    grupoParametroConfiguracion_new = grupoParametroConfiguracion
                LOCL_configDict[nombreParametroDeConfiguracion] = [
                    valorParametroConfiguracion,
                    grupoParametroConfiguracion_new,
                    descripcionParametroConfiguracion,
                    tipoParametroConfiguracion,
                ]
                if LOCL_verboseAll:
                    myLog.debug('\t\t-> parametro {:<35} -> {}'.format(nombreParametroDeConfiguracion, LOCL_configDict[nombreParametroDeConfiguracion]))
    
        # Compruebo que el fichero de configuracion tiene todos los parametros de LOCL_configDictPorDefecto
        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            if not nombreParametroDeConfiguracion in LOCL_configDict:
                listaParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion]
                valorPrincipal = listaParametroConfiguracion[0]
                grupoParametroConfiguracion = listaParametroConfiguracion[1]
                if len(listaParametroConfiguracion) > 1:
                    tipoParametroConfiguracion = listaParametroConfiguracion[2]
                else:
                    tipoParametroConfiguracion = 'str'
                valorParametroConfiguracion = clidconfig.valorConfig(
                    valorPrincipal,
                    valorAlternativoTxt='',
                    usarAlternativo=False,
                    nombreParametro=nombreParametroDeConfiguracion,
                    tipoVariable=tipoParametroConfiguracion,
                )
                descripcionParametroConfiguracion = listaParametroConfiguracion[3]
                LOCL_configDict[nombreParametroDeConfiguracion] = [
                    valorParametroConfiguracion,
                    grupoParametroConfiguracion,
                    tipoParametroConfiguracion,
                    descripcionParametroConfiguracion,
                ]
                myLog.info('\t-> AVISO: el parametro <{}> no esta en el fichero de configuacion; se adopta valor por defecto: <{}>'.format(nombreParametroDeConfiguracion, valorParametroConfiguracion))

        # config_ok = True
    except Exception as excpt:
        program_name = 'clidtwcfg.py'
        # myLog.error(f'\n{program_name}-> Error Exception:\n{excpt}')
        myLog.error(f'clidtwcfg-> Error al leer la configuracion del fichero: {LOCL_configFileNameCfg}')
        mensajeError(program_name)
        # config_ok = False
        sys.exit(0)
    # myLog.debug('\t\tclidtwcfg-> LOCL_configDict:', LOCL_configDict)

    myLog.info('{:=^80}'.format(''))

    return LOCL_configDict


# ==============================================================================
def foo0():
    pass

# # ==============================================================================
# class myClass(object):
#     pass
#
# GLO = myClass()
# GLO.GLBLverbose = None
# GLO.GLBLaccionPrincipalPorDefecto = None
# GLO.GLBLrutaAscRaizBasePorDefecto = None
# GLO.GLBLrasterPixelSizePorDefecto = None
# GLO.GLBLradioClusterPixPorDefecto = None
# GLO.GLBLrutaCompletaMFEPorDefecto = None
# GLO.GLBLcartoMFEcampoSpPorDefecto = None
# GLO.GLBLpatronVectrNamePorDefecto = None
# GLO.GLBLtesteoVectrNamePorDefecto = None
# GLO.GLBLpatronLayerNamePorDefecto = None
# GLO.GLBLpatronFieldNamePorDefecto = None
# GLO.GLBLtesteoLayerNamePorDefecto = None
# GLO.GLBLnPatronDasoVarsPorDefecto = None
#
# GLO.GLBLlistaDasoVarsFileTypes = None
# GLO.GLBLlistaDasoVarsNickNames = None
# GLO.GLBLlistaDasoVarsRangoLinf = None
# GLO.GLBLlistaDasoVarsRangoLsup = None
# GLO.GLBLlistaDasoVarsNumClases = None
# GLO.GLBLlistaDasoVarsMovilidad = None
# GLO.GLBLlistLstDasoVarsPorDefecto = None
# GLO.GLBLlistTxtDasoVarsPorDefecto = None
#
# GLO.GLBLmenuInteractivoPorDefecto = None
# GLO.GLBLmarcoPatronTestPorDefecto = None
# GLO.GLBLnivelSubdirExplPorDefecto = None
# GLO.GLBLoutRasterDriverPorDefecto = None
# GLO.GLBLoutputSubdirNewPorDefecto = None
# GLO.GLBLcartoMFErecortePorDefecto = None
# GLO.GLBLvarsTxtFileNamePorDefecto = None
# GLO.GLBLambitoTiffNuevoPorDefecto = None
# GLO.GLBLnoDataTiffProviPorDefecto = None
# GLO.GLBLnoDataTiffFilesPorDefecto = None
# GLO.GLBLnoDataTipoDMasaPorDefecto = None
# GLO.GLBLumbralMatriDistPorDefecto = None
#
# GLO.GLBLaccionPrincipal = None
# GLO.GLBLrutaAscRaizBase = None
# GLO.GLBLrasterPixelSize = None
# GLO.GLBLradioClusterPix = None
# GLO.GLBLrutaCompletaMFE = None
# GLO.GLBLcartoMFEcampoSp = None
# GLO.GLBLpatronVectrName = None
# GLO.GLBLpatronLayerName = None
# GLO.GLBLtesteoVectrName = None
# GLO.GLBLtesteoLayerName = None
# GLO.GLBLnPatronDasoVars = None
#
# GLO.GLBLlistaDasoVarsFileTypes = None
# GLO.GLBLlistaDasoVarsNickNames = None
# GLO.GLBLlistaDasoVarsRangoLinf = None
# GLO.GLBLlistaDasoVarsRangoLsup = None
# GLO.GLBLlistaDasoVarsNumClases = None
# GLO.GLBLlistaDasoVarsMovilidad = None
# GLO.GLBLlistLstDasoVars = None
# GLO.GLBLlistTxtDasoVars = None
#
# GLO.GLBLmenuInteractivo = None
# GLO.GLBLmarcoPatronTest = None
# GLO.GLBLnivelSubdirExpl = None
# GLO.GLBLoutRasterDriver = None
# GLO.GLBLoutputSubdirNew = None
# GLO.GLBLcartoMFErecorte = None
# GLO.GLBLvarsTxtFileName = None
# GLO.GLBLambitoTiffNuevo = None
# GLO.GLBLnoDataTiffProvi = None
# GLO.GLBLnoDataTiffFiles = None
# GLO.GLBLnoDataTipoDMasa = None
# GLO.GLBLumbralMatriDist = None
#
# GLO.GLBLmarcoCoordMiniX = 0
# GLO.GLBLmarcoCoordMaxiX = 0
# GLO.GLBLmarcoCoordMiniY = 0
# GLO.GLBLmarcoCoordMaxiY = 0
#
# GLO.configFileNameCfg = None


# ==============================================================================
def leerConfigDictPorDefecto():
    ''''Dict de parametros de configuracion con valores por defecto.
    Estructura:
        GRAL_configDict[nombreParametroDeConfiguracion] = [valorParametro, grupoParametros, tipoVariable, descripcionParametro]
    '''
    localData = 'PuenteDuero'
    configDictPorDefecto = {
        'GLBLverbose': [2,
                        'general', 'bool',
                        'Mostrar info de ejecucion en consola'],
        'GLBLmenuInteractivoPorDefecto': [0,
                                          'general', 'bool',
                                          'Preguntar en tiempo de ejecucion para confirmar opciones'],
        'GLBLnivelSubdirExplPorDefecto': [0,
                                          'general', 'bool',
                                          'Explorar subdirectorios de rutaAscRaizBase'],
        'GLBLrasterPixelSizePorDefecto': [10,
                                          'general', 'uint8',
                                          'Lado del pixel dasometrico en metros (pte ver diferencia con GLBLmetrosCelda)'],
        'GLBLambitoTiffNuevoPorDefecto': ['loteAsc',
                                          'general', 'str',
                                          'Principalmente para merge: ambito geografico del nuevo raster creado (uno predeterminado o el correspondiente a los ASC)'],

    
        'GLBLaccionPrincipalPorDefecto': ['1', 'dasoLidar', 'bool', '1. Verificar analog�a con un determinado patron dasoLidar; 2. Generar raster con presencia de un determinado patron dasoLidar.'],
    
        # Ruta de los lasFiles para Leon:
        # 'GLBLrutaAscRaizBasePorDefecto': ['K:/calendula/NW',
        # 'GLBLrutaAscRaizBasePorDefecto': ['O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Sg_PinoSilvestre',
        # 'GLBLrutaAscRaizBasePorDefecto': ['',
        'GLBLrutaAscRaizBasePorDefecto': [f'../data/asc/{localData}',
                                          'dasoLidar', 'str',
                                          'Ruta de los ASC para el dasolidar cluster en JCyL'],
    
        # 'GLBLpatronVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/zonaEnsayoTolosana.shp',
        # 'GLBLpatronVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/perimetrosDeReferencia.gpkg',
        # 'GLBLpatronVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/recintos_roble.gpkg',
        # 'GLBLpatronVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Sg_PinoSilvestre/poligonos Riaza1.shp',
        'GLBLpatronVectrNamePorDefecto': [f'../data/ref/cartoLidar{localData}.gpkg',
                                          'dasoLidar', 'str',
                                          'Nombre del dataset (shp o gpkg) de referencia (patron) para caracterizacion dasoLidar'],
    
        # 'GLBLtesteoVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/MUP_rodales_zonaEstudio.shp',
        # 'GLBLtesteoVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/testeo_roble.shp',
        # 'GLBLtesteoVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Le_roble/vector/recintos_roble.gpkg',
        # 'GLBLtesteoVectrNamePorDefecto': [r'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Sg_PinoSilvestre/poligonos Riaza2.shp',
        'GLBLtesteoVectrNamePorDefecto': [f'../data/ref/cartoLidar{localData}.gpkg',
                                          'dasoLidar', 'str',
                                          'Nombre del dataset (shp o gpkg) cuya semejanza con el de entrada se chequea con dasoLidar.'],

        # 'GLBLpatronLayerNamePorDefecto': [r'robleAlto1',
        # 'GLBLpatronLayerNamePorDefecto': [r'',
        'GLBLpatronLayerNamePorDefecto': [r'vectorPatron',
                                          'dasoLidar', 'str',
                                          'Nombre del layer de referencia (patron) para caracterizacion dasoLidar (solo si el dataset es gpkg; para shp layer=capa=dataset).'],

        # 'GLBLtesteoLayerNamePorDefecto': [r'robleAlto2',
        # 'GLBLtesteoLayerNamePorDefecto': [r'',
        'GLBLtesteoLayerNamePorDefecto': [r'vectorTesteo',
                                          'dasoLidar', 'str',
                                          'Nombre del layer cuya semejanza con el de entrada se chequea con dasoLidar (solo si el dataset es gpkg; para shp layer=capa=dataset).'],

        'GLBLpatronFieldNamePorDefecto': [r'TM',
                                          'dasoLidar', 'str',
                                          'Nombre del campo con el identificador del tipo de masa de los poligonos de referencia (patron) para caracterizacion dasoLidar.'],
    
        'GLBLradioClusterPixPorDefecto': [3,
                                          'dasoLidar', 'uint8',
                                          'Numero de anillos de pixeles que tiene el cluster, ademas del central'],
    
        # 'GLBLrutaCompletaMFEPorDefecto': [r'O:/Sigmena/Carto/VEGETACI/MFE/MFE50/MFE50AD/40_MFE50AD_etrs89.shp',
        'GLBLrutaCompletaMFEPorDefecto': [f'../data/mfe/{localData}/MFE_{localData}.shp',
                                          'dasoLidar', 'str',
                                          'Nombre (con ruta y extension) del fichero con la capa MFE'],

        'GLBLcartoMFEcampoSpPorDefecto': ['SP1',
                                          'dasoLidar', 'str',
                                          'Nombre del campo con el codigo numerico de la especie principal o tipo de bosque en la capa MFE'],
    
        'GLBLnPatronDasoVarsPorDefecto': [0,
                                          'dasoLidar', 'int',
                                          'Si es distinto de cero, numero de dasoVars con las que se caracteriza el patron (n primeras dasoVars)'],
    
        'GLBLnClasesDasoVarsPorDefecto': [5,
                                          'dasoLidar', 'int',
                                          'Numero de clases por defecto para todas las variables si no se especifica para cada variable.'],

        'GLBLtrasferDasoVarsPorDefecto': [25,
                                          'dasoLidar', 'int',
                                          'Porcentaje de movilidad admisible interclases si no se especifica para cada variable.'],

        'GLBLlistaDasoVarsFileTypes': [
            # 'CeldasAlt95SobreMdk,FccRptoAmdk_PrimeRets_MasDe0500,FccRptoAmdk_PrimeRets_MasDe0300,FccRptoAmdk_PrimeRets_0025_0150,FccRptoAmdk_TodosRets_200cm_50%HD,MFE25,TMasa',
            'alt95,fcc3m,cob050_200cm,MFE25,TMasa',
            'dasoLidar', 'list_str',
            'Lista de tipos de fichero para el dasoLidar'
        ],
        'GLBLlistaDasoVarsNickNames': [
            # 'Alt95,FCC5m,FCC3m,FCmat,FCsub,MFE25,TMasa',
            'Alt95,Fcc3m,CobMt,MFE25,TMasa',
            'dasoLidar', 'list_str',
            'Lista de variables para el dasoLidar'
        ],
        'GLBLlistaDasoVarsRangoLinf': [
            # '0,0,0,0,0,0,0',
            '0,0,0,0,0',
            'dasoLidar', 'list_int',
            'Lista de variables para el dasoLidar'
        ],
        'GLBLlistaDasoVarsRangoLsup': [
            # '36,100,100,100,100,255,255',
            '36,100,100,255,255',
            'dasoLidar', 'list_int',
            'Lista de variables para el dasoLidar'
        ],
        'GLBLlistaDasoVarsNumClases': [
            # '18,5,5,5,5,255,255',
            '18,5,5,255,255',
            'dasoLidar', 'list_int',
            'Lista de variables para el dasoLidar'
        ],
        'GLBLlistaDasoVarsMovilidad': [
            # '40,25,30,35,35,0,0',
            '40,25,35,0,0',
            'dasoLidar', 'list_int',
            'Lista de factores de movilidad admitidas entre clases del histograma de la variable dasoVar (0-100)'
        ],
        'GLBLlistaDasoVarsPonderado': [
            # '10,8,5,4,3,0,0',
            '10,8,5,0,0',
            'dasoLidar', 'list_int',
            'Peso de cada variable para poderar las discrepancias respecto al modelo o patron (0-10).'
        ],
    
        'GLBLmarcoPatronTestPorDefecto': [1,
                                          'dasoLidar', 'bool',
                                          'Zona de analisis definida por la envolvente de los poligonos de referencia (patron) y de chequeo (testeo)'],
        'GLBLoutRasterDriverPorDefecto': ['GTiff',
                                          'dasoLidar', 'str',
                                          'Formato de fichero raster de salida para el dasolidar'],
        'GLBLoutputSubdirNewPorDefecto': ['dasoLayers',
                                          'dasoLidar', 'str',
                                          'Subdirectorio de GLBLrutaAscRaizBasePorDefecto donde se guardan los resultados'],
        'GLBLcartoMFErecortePorDefecto': ['mfe50rec',
                                          'dasoLidar', 'str',
                                          'Nombre del fichero en el que se guarda la version recortada raster del MFE'],
        'GLBLvarsTxtFileNamePorDefecto': ['rangosDeDeferencia.txt',
                                          'dasoLidar', 'str',
                                          'Nombre de fichero en el que se guardan los rangos calculados para todas las variables'],
    
        'GLBLnoDataTiffProviPorDefecto': [-8888,
                                          'dasoLidar', 'int',
                                          'NoData temporal para los ficheros raster de salida para el dasolidar'],
        'GLBLnoDataTiffFilesPorDefecto': [-9999,
                                          'dasoLidar', 'int',
                                          'NoData definitivo para los ficheros raster de salida para el dasolidar'],
        'GLBLnoDataTipoDMasaPorDefecto': [255,
                                          'dasoLidar', 'int',
                                          'NoData definitivo para el raster de salida con el tipo de masa para el dasolidar'],
        'GLBLumbralMatriDistPorDefecto': [20,
                                          'dasoLidar', 'int',
                                          'Umbral de distancia por debajo del cual se considera que una celda es parecida a otra enla matriz de distancias entre dasoVars'],
        'GLBLdistMaxScipyAdmPorDefecto': [2,
                                          'dasoLidar', 'int',
                                          'Umbral de distancia Scipy (entre histogramas) por encima del cual se descarta que una celda sea parecida a la patron aunque sea la de distancia minima'],

        'GLBLmarcoCoordMiniXPorDefecto': [0,
                                          'dasoLidar', 'int',
                                          'Limite inferior X para delimitar la zona de analisis'],
        'GLBLmarcoCoordMaxiXPorDefecto': [0,
                                          'dasoLidar', 'int',
                                          'Limite superior X para delimitar la zona de analisis'],
        'GLBLmarcoCoordMiniYPorDefecto': [0,
                                          'dasoLidar', 'int',
                                          'Limite inferior Y para delimitar la zona de analisis'],
        'GLBLmarcoCoordMaxiYPorDefecto': [0,
                                          'dasoLidar', 'int',
                                          'Limite superior Y para delimitar la zona de analisis'],
    }
    return configDictPorDefecto


# ==============================================================================
def readSppMatch():
    sppMatch = [
        [21, 22, 7], # Ps Pu
        [21, 23, 3], # Ps Pp
        [21, 24, 2], # Ps Ph
        [21, 25, 6], # Ps Pn
        [21, 26, 5], # Ps Pt
        [21, 28, 3], # Ps Pr
        [22, 23, 3], # Pu Pp
        [22, 24, 2], # Pu Ph
        [22, 25, 5], # Pu Pn
        [22, 26, 4], # Pu Pt
        [22, 28, 3], # Pu Pr
        [23, 24, 4], # Pp Ph
        [23, 25, 4], # Pp Pn
        [23, 26, 5], # Pp Pt
        [23, 28, 2], # Pp Pr
        [24, 25, 3], # Ph Pn
        [24, 26, 3], # Ph Pt
        [24, 28, 2], # Ph Pr
        [25, 26, 5], # Pn Pt
        [25, 28, 4], # Pn Pr
        [26, 28, 5], # Pt Pr
        [41, 42, 9], # Qr Qt
        [41, 43, 5], # Qr Qp
        [41, 44, 4], # Qr Qf
        [41, 45, 3], # Qr Qi
        [41, 46, 3], # Qr Qs
        [42, 43, 5], # Qt Qp
        [42, 44, 4], # Qt Qf
        [42, 45, 3], # Qt Qi
        [42, 46, 3], # Qt Qs
        [43, 44, 7], # Qp Qf
        [43, 45, 5], # Qp Qi
        [43, 46, 3], # Qp Qs
        [44, 45, 7], # Qf Qi
        [44, 46, 5], # Qf Qs
        [45, 46, 7], # Qi Qs
        ]
    return sppMatch


# ==============================================================================
def checkGLO(GLO):
    GLO.GLBLinputVectorMfePathName = os.path.dirname(GLO.GLBLrutaCompletaMFEPorDefecto)
    inputVectorMfeFilePathName, GLO.GLBLinputVectorMfeFileExt = os.path.splitext(GLO.GLBLrutaCompletaMFEPorDefecto)
    GLO.GLBLinputVectorMfeFileName = os.path.basename(inputVectorMfeFilePathName)
    if GLO.GLBLinputVectorMfeFileExt.lower() == '.shp':
        GLO.GLBLinputVectorDriverNameMFE = 'ESRI Shapefile'
    elif GLO.GLBLinputVectorMfeFileExt.lower() == '.gpkg':
        GLO.GLBLinputVectorDriverNameMFE = 'ESRI Shapefile'
    else:
        GLO.GLBLinputVectorDriverNameMFE = ''
        myLog.critical(f'clidtwcfg-> No se ha identificado bien el driver de esta extension: {GLO.GLBLinputVectorMfeFileExt} (fichero: {GLO.GLBLrutaCompletaMFEPorDefecto})')
        sys.exit(0)

    # ==============================================================================
    if (
        len(GLO.GLBLlistaDasoVarsNickNames) < len(GLO.GLBLlistaDasoVarsFileTypes) 
        or len(GLO.GLBLlistaDasoVarsRangoLinf) < len(GLO.GLBLlistaDasoVarsFileTypes)
        or len(GLO.GLBLlistaDasoVarsRangoLsup) < len(GLO.GLBLlistaDasoVarsFileTypes)
        or len(GLO.GLBLlistaDasoVarsNumClases) < len(GLO.GLBLlistaDasoVarsFileTypes)
        or len(GLO.GLBLlistaDasoVarsMovilidad) < len(GLO.GLBLlistaDasoVarsFileTypes)
        or len(GLO.GLBLlistaDasoVarsPonderado) < len(GLO.GLBLlistaDasoVarsFileTypes)
        
    ):
        myLog.error('\nclidtwcfg-> ATENCION: revisar coherencia en numero de propiedades de la lista de variables en el fichero de parametros de configuracion:')
        myLog.error('\t-> FileTypes', type(GLO.GLBLlistaDasoVarsFileTypes), 'NumDasoVars:', len(GLO.GLBLlistaDasoVarsFileTypes), '->', GLO.GLBLlistaDasoVarsFileTypes)
        myLog.error('\t-> NickNames', type(GLO.GLBLlistaDasoVarsNickNames), 'NumDasoVars:', len(GLO.GLBLlistaDasoVarsNickNames), '->', GLO.GLBLlistaDasoVarsNickNames)
        myLog.error('\t-> RangoLinf', type(GLO.GLBLlistaDasoVarsRangoLinf), 'NumDasoVars:', len(GLO.GLBLlistaDasoVarsRangoLinf), '->', GLO.GLBLlistaDasoVarsRangoLinf)
        myLog.error('\t-> RangoLinf', type(GLO.GLBLlistaDasoVarsRangoLinf), 'NumDasoVars:', len(GLO.GLBLlistaDasoVarsRangoLsup), '->', GLO.GLBLlistaDasoVarsRangoLinf)
        myLog.error('\t-> NumClases', type(GLO.GLBLlistaDasoVarsNumClases), 'NumDasoVars:', len(GLO.GLBLlistaDasoVarsNumClases), '->', GLO.GLBLlistaDasoVarsNumClases)
        myLog.error('\t-> Movilidad', type(GLO.GLBLlistaDasoVarsMovilidad), 'NumDasoVars:', len(GLO.GLBLlistaDasoVarsMovilidad), '->', GLO.GLBLlistaDasoVarsMovilidad)
        myLog.error('\t-> Ponderado', type(GLO.GLBLlistaDasoVarsPonderado), 'NumDasoVars:', len(GLO.GLBLlistaDasoVarsPonderado), '->', GLO.GLBLlistaDasoVarsPonderado)
        myLog.error(f'Corregir o eliminar el fichero almacenado ({GLO.configFileNameCfg}).')
        sys.exit(0)

    nBandasPrevistasOutput = len(GLO.GLBLlistaDasoVarsFileTypes)
    GLO.GLBLlistTxtDasoVarsPorDefecto = []
    for nVar in range(nBandasPrevistasOutput):
        GLO.GLBLlistTxtDasoVarsPorDefecto.append(
            '{},{},{},{},{},{},{}'.format(
                GLO.GLBLlistaDasoVarsFileTypes[nVar],
                GLO.GLBLlistaDasoVarsNickNames[nVar],
                GLO.GLBLlistaDasoVarsRangoLinf[nVar],
                GLO.GLBLlistaDasoVarsRangoLsup[nVar],
                GLO.GLBLlistaDasoVarsNumClases[nVar],
                GLO.GLBLlistaDasoVarsMovilidad[nVar],
                GLO.GLBLlistaDasoVarsPonderado[nVar],
            )
        )

    GLO.GLBLlistLstDasoVarsPorDefecto = []
    for nVar in range(nBandasPrevistasOutput):
        GLO.GLBLlistLstDasoVarsPorDefecto.append(
            [
                GLO.GLBLlistaDasoVarsFileTypes[nVar],
                GLO.GLBLlistaDasoVarsNickNames[nVar],
                GLO.GLBLlistaDasoVarsRangoLinf[nVar],
                GLO.GLBLlistaDasoVarsRangoLsup[nVar],
                GLO.GLBLlistaDasoVarsNumClases[nVar],
                GLO.GLBLlistaDasoVarsMovilidad[nVar],
                GLO.GLBLlistaDasoVarsPonderado[nVar],
            ]
        )

    # # Partiendo del formato listTxtDasoVars (lista de textos emulando listas):
    # GLO.GLBLlistLstDasoVarsPorDefecto = []
    # for nVar in range(nBandasPrevistasOutput):
    #     for numLista, txtListaDasovar in enumerate(GLO.GLBLlistTxtDasoVarsPorDefecto):
    #         if nVar == 0 or nVar == 1:
    #             # FileTypes y NickNames
    #             listDasoVar = [item.strip() for item in txtListaDasovar.split(',')]
    #         elif nVar == 2 or nVar == 3:
    #             # RangoLinf y RangoLinf
    #             listDasoVar = [float(item.strip()) for item in txtListaDasovar.split(',')]
    #         else:
    #             # NumClases, Movilidad y Ponderado
    #             listDasoVar = [int(item.strip()) for item in txtListaDasovar.split(',')]
    #         GLO.GLBLlistLstDasoVarsPorDefecto.append(listDasoVar)

        # myLog.debug('clidtwcfg->', nVar, type(GLO.GLBLlistaDasoVarsMovilidad[nVar]), GLO.GLBLlistaDasoVarsMovilidad[nVar], end=' -> ')
        # GLO.GLBLlistaDasoVarsRangoLinf[nVar] = int(GLO.GLBLlistaDasoVarsRangoLinf[nVar])
        # GLO.GLBLlistaDasoVarsRangoLsup[nVar] = int(GLO.GLBLlistaDasoVarsRangoLsup[nVar])
        # GLO.GLBLlistaDasoVarsNumClases[nVar] = int(GLO.GLBLlistaDasoVarsNumClases[nVar])
        # GLO.GLBLlistaDasoVarsMovilidad[nVar] = int(GLO.GLBLlistaDasoVarsMovilidad[nVar])
        # myLog.debug(type(GLO.GLBLlistaDasoVarsMovilidad[nVar]), GLO.GLBLlistaDasoVarsMovilidad[nVar])
    # ==========================================================================
    GLO.GLBLverbose = GLO.GLBLverbose
    GLO.GLBLaccionPrincipalPorDefecto = int(GLO.GLBLaccionPrincipalPorDefecto)
    GLO.GLBLrutaAscRaizBasePorDefecto = str(GLO.GLBLrutaAscRaizBasePorDefecto)
    GLO.GLBLrasterPixelSizePorDefecto = int(GLO.GLBLrasterPixelSizePorDefecto)
    GLO.GLBLradioClusterPixPorDefecto = int(GLO.GLBLradioClusterPixPorDefecto)
    GLO.GLBLrutaCompletaMFEPorDefecto = str(GLO.GLBLrutaCompletaMFEPorDefecto)
    GLO.GLBLcartoMFEcampoSpPorDefecto = str(GLO.GLBLcartoMFEcampoSpPorDefecto)
    GLO.GLBLpatronVectrNamePorDefecto = str(GLO.GLBLpatronVectrNamePorDefecto)
    GLO.GLBLpatronLayerNamePorDefecto = GLO.GLBLpatronLayerNamePorDefecto
    GLO.GLBLpatronFieldNamePorDefecto = GLO.GLBLpatronFieldNamePorDefecto
    GLO.GLBLtesteoVectrNamePorDefecto = str(GLO.GLBLtesteoVectrNamePorDefecto)
    GLO.GLBLtesteoLayerNamePorDefecto = GLO.GLBLtesteoLayerNamePorDefecto
    GLO.GLBLnPatronDasoVarsPorDefecto = int(GLO.GLBLnPatronDasoVarsPorDefecto)
    
    GLO.GLBLlistaDasoVarsFileTypes = list(GLO.GLBLlistaDasoVarsFileTypes)
    GLO.GLBLlistaDasoVarsNickNames = list(GLO.GLBLlistaDasoVarsNickNames)
    GLO.GLBLlistaDasoVarsRangoLinf = list(GLO.GLBLlistaDasoVarsRangoLinf)
    GLO.GLBLlistaDasoVarsRangoLsup = list(GLO.GLBLlistaDasoVarsRangoLsup)
    GLO.GLBLlistaDasoVarsNumClases = list(GLO.GLBLlistaDasoVarsNumClases)
    GLO.GLBLlistaDasoVarsMovilidad = list(GLO.GLBLlistaDasoVarsMovilidad)
    GLO.GLBLlistLstDasoVarsPorDefecto = list(GLO.GLBLlistLstDasoVarsPorDefecto)
    GLO.GLBLlistTxtDasoVarsPorDefecto = list(GLO.GLBLlistTxtDasoVarsPorDefecto)
    
    GLO.GLBLmenuInteractivoPorDefecto = int(GLO.GLBLmenuInteractivoPorDefecto)
    GLO.GLBLmarcoPatronTestPorDefecto = int(GLO.GLBLmarcoPatronTestPorDefecto)
    GLO.GLBLnivelSubdirExplPorDefecto = int(GLO.GLBLnivelSubdirExplPorDefecto)
    GLO.GLBLoutRasterDriverPorDefecto = str(GLO.GLBLoutRasterDriverPorDefecto)
    GLO.GLBLoutputSubdirNewPorDefecto = str(GLO.GLBLoutputSubdirNewPorDefecto)
    GLO.GLBLcartoMFErecortePorDefecto = str(GLO.GLBLcartoMFErecortePorDefecto)
    GLO.GLBLvarsTxtFileNamePorDefecto = str(GLO.GLBLvarsTxtFileNamePorDefecto)
    GLO.GLBLambitoTiffNuevoPorDefecto = str(GLO.GLBLambitoTiffNuevoPorDefecto)
    GLO.GLBLnoDataTiffProviPorDefecto = int(GLO.GLBLnoDataTiffProviPorDefecto)
    GLO.GLBLnoDataTiffFilesPorDefecto = int(GLO.GLBLnoDataTiffFilesPorDefecto)
    GLO.GLBLnoDataTipoDMasaPorDefecto = int(GLO.GLBLnoDataTipoDMasaPorDefecto)
    GLO.GLBLumbralMatriDistPorDefecto = int(GLO.GLBLumbralMatriDistPorDefecto)
    # ==========================================================================
    
    # ==========================================================================
    sppMatch = readSppMatch()
    GLO.GLBLdictProximidadInterEspecies = {}
    for (codeEsp1, codeEsp2, proximidadInterEsp) in sppMatch:
        binomioEspeciesA = f'{codeEsp1}_{codeEsp2}'
        binomioEspeciesB = f'{codeEsp2}_{codeEsp1}'
        GLO.GLBLdictProximidadInterEspecies[binomioEspeciesA] = proximidadInterEsp
        GLO.GLBLdictProximidadInterEspecies[binomioEspeciesB] = proximidadInterEsp
    # myLog.debug('GLBLdictProximidadInterEspecies:')
    # for binomioSpp in GLO.GLBLdictProximidadInterEspecies:
    #     myLog.debug(binomioSpp, GLO.GLBLdictProximidadInterEspecies[binomioSpp])
    # ==========================================================================

    return GLO


# ==============================================================================
def readGLO():
    configFileNameCfg = clidconfig.getConfigFileName(MAIN_idProceso, LOCL_verbose=__verbose__)
    configDictPorDefecto = leerConfigDictPorDefecto()
    # Se guardan los parametros de configuracion en un diccionario:
    GRAL_configDict = leerConfig(configDictPorDefecto, configFileNameCfg, LOCL_verbose=__verbose__)
    # Se crea un objeto de la clase VariablesGlobales para almacenar los
    # parametros de configuracion guardados en GRAL_configDict como atributos
    GLO = clidconfig.VariablesGlobales(GRAL_configDict)
    GLO.configFileNameCfg = configFileNameCfg
    checkGLO(GLO)

    if __verbose__ == 3:
        myLog.debug('clidtwcfg-> GLO:')
        for myParameter in dir(GLO):
            if not myParameter.startswith('__'):
                myLog.debug(f'{TB}{myParameter}')
                if hasattr(GLO, myParameter):
                #  and (
                #     'listaDasoVars' in myParameter
                #     or 'listLstDasoVars' in myParameter
                #     or 'listTxtDasoVars' in myParameter
                # ):
                    myLog.debug(f'{TB}{TV}-> {getattr(GLO, myParameter)}')
        myLog.debug('{:=^80}'.format(''))

    return GLO


# ==============================================================================
GLO = readGLO()


# ==============================================================================
if __name__ == "__main__":
    pass
