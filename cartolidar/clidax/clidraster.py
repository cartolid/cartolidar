#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Module included in cartolidar project (clidax package)
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidraster (ancillary to clidtools) is used for raster creation and
MFE vector layer reading
clidtwcfg requires clidcconfig module

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''

from __future__ import division, print_function
import inspect
import os
import sys
import time
import math
import random
import logging
# import pathlib
# import struct

import numpy as np
# import scipy
# import scipy.misc
import scipy.ndimage.interpolation
from PIL import Image
# from pandas.io import orc
try:
    import psutil
    psutilOk = True
except:
    psutilOk = False

# Para que funcione GDAL en eclipse:
#   En Windows->Preferences->Pydev->Interpreters->Python interpreter->Pestanna environment -> Incluir PATH = C:/OSGeo4W64/bin
#   Alternativa (no usar esto con Anaconda):
#     os.environ['PATH'] = 'C:/OSGeo4W64/bin;' + os.environ['PATH']
#    o bien:
#     sys.path.insert(0,'C:\OSGeo4W64\bin')
# Con esto resuelvo el error al cargar gdal, que ocurre en eclipse pero no el cmd.
# En eclipse busca antes en algun diretorio que tiene un gdal que no es que quiero usar (el de OSGeo4W64)
try:
    # print(os.environ['PATH'])
    from osgeo import gdal, ogr, osr, gdalnumeric, gdalconst
    gdalOk = True
except:
    print('clidflow-> No se puede importar gdal "from osgeo", se intenta directamente ("import gdal").')
    gdalOk = False
if not gdalOk:
    try:
        import gdal, ogr, osr, gdalnumeric, gdalconst
        sys.stdout.write('           gdal importado ok con "import gdal".\n')
        gdalOk = True
    except:
        gdalOk = False
        print('clidflow-> Error importando gdal.')
        sys.exit(0)
ogr.RegisterAll()
# Enable GDAL/OGR exceptions
gdal.UseExceptions()

# Recuperar la captura de errores de importacion en la version beta
try:
# if True:
    from cartolidar.clidax import clidconfig
    from cartolidar.clidax import clidcarto
    # Se importan los parametros de configuracion por defecto por si
    # se carga esta clase sin aportar algun parametro de configuracion
except:
    sys.stderr.write(f'qlidtwins-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).\n')
    sys.stderr.write('\t-> Se importa clidcarto desde clidtwcfg del directorio local {os.getcwd()}/clidtools.\n')
    from clidax import clidconfig
    from clidax import clidcarto

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
TB = ' ' * 13
TV = ' ' * 3
# ==============================================================================

# ==============================================================================
myModule = __name__.split('.')[-1]
myUser = clidconfig.infoUsuario()
# ==============================================================================
myLog = clidconfig.iniciaConsLog(myModule=myModule, myVerbose=__verbose__)
# ==============================================================================
myLog.debug('{:_^80}'.format(''))
myLog.debug('clidraster-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================

GLO_GLBLsubLoteTiff = ''
GLO_GLBLconvertirAlt = False

# ==============================================================================
class myClass(object):
    pass


# ==============================================================================
def crearRasterTiff(
    # self_LOCLrutaAscRaizBase,
    self_inFilesListAllTypes=None,  # Alternativo al siguiente
    self_inFilesDictAllTypes=None,  # Alternativo al anterior
    self_LOCLoutPathNameRuta=None,  # Optional
    self_LOCLoutFileNameWExt=None,  # Optional
    self_LOCLlistaDasoVarsFileTypes=None,  # Optional

    PAR_rasterPixelSize=0,
    PAR_outRasterDriver='GTiff',
    PAR_noDataTiffProvi=-8888,
    PAR_noDataMergeTiff=-9999,
    PAR_outputOptions=None,
    PAR_nInputVars=1,
    PAR_outputGdalDatatype=None,
    PAR_outputNpDatatype=None,
    integrarFicherosAsc=False,
    rasterQueSeUsaComoDeferencia=None,
    rasterEnElQueSeEscribe=None,
    LCL_convertirAlt=False,

    PAR_cartoMFEpathName=None,
    PAR_cartoMFEfileName=None,
    PAR_cartoMFEfileSoloExt=None,
    PAR_cartoMFEfileNSinExt=None,
    PAR_cartoMFEcampoSp=None,
    PAR_cartoMFErecorte=None,

    PAR_generarDasoLayers=False,
    PAR_ambitoTiffNuevo=None,
    PAR_verbose=False,

    AUX_subLoteTiff=GLO_GLBLsubLoteTiff,
    AUX_numTipoFichero=0,

    ARGSdasoVar='',
    ARGSconvertirAltAdm8Bit=False,
    ARGSconvertirAltAcm16Bit=False,
):

    # ==========================================================================
    if self_inFilesListAllTypes is None and self_inFilesDictAllTypes is None:
        myLog.error(f'\nclidraster-> ATENCION: no se han especificado las listas de ficheros a integrar.')
        myLog.error('\t-> Se interrumpe la ejecucion de cartolidar')
        sys.exit(0)

    if not os.path.isdir(self_LOCLoutPathNameRuta):
        if PAR_verbose:
            myLog.warning(f'\nclidraster-> AVISO: ruta {self_LOCLoutPathNameRuta} no disponible, se busca una alternativa.')
        self_LOCLoutPathNameRuta = None
    if self_LOCLoutPathNameRuta is None:
        MAIN_THIS_DIR = os.getcwd()
        if not 'site-packages' in MAIN_THIS_DIR:
            self_LOCLrutaAscRaizBase = MAIN_THIS_DIR
        else:
            MAIN_BASE_DIR = os.path.abspath('.')
            if not 'site-packages' in MAIN_BASE_DIR:
                self_LOCLrutaAscRaizBase = MAIN_BASE_DIR
            else:
                try:
                    MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
                except:
                    MAIN_FILE_DIR = None
                if not MAIN_FILE_DIR is None and not 'site-packages' in MAIN_BASE_DIR:
                    self_LOCLrutaAscRaizBase = MAIN_FILE_DIR
                else:
                    import pathlib
                    MAIN_HOME_DIR = str(pathlib.Path.home())
                    self_LOCLrutaAscRaizBase = MAIN_HOME_DIR

        self_LOCLoutPathNameRuta = os.path.join(self_LOCLrutaAscRaizBase, 'dasoLayers')
        if not os.path.exists(self_LOCLoutPathNameRuta):
            try:
                os.makedirs(self_LOCLoutPathNameRuta)
            except:
                myLog.error('\nATENCION: No se ha podido crear el directorio {}'.format(self_LOCLoutPathNameRuta))
                myLog.error('\tRevisar derechos de escritura en esa ruta o indicar una especifica con derechos.')
                myLog.error('\nSe interrumpe la ejecucion de cartolidar')
                sys.exit(0)
        if PAR_verbose:
            myLog.info(f'{TB}-> ruta de salida: {self_LOCLoutPathNameRuta}')

    if PAR_ambitoTiffNuevo is None:
        PAR_ambitoTiffNuevo = 'loteAsc'
    if PAR_ambitoTiffNuevo == 'FicherosTiffIndividuales' or PAR_ambitoTiffNuevo == 'ConvertirSoloUnFicheroASC':
        idAmbitoTif = 'Indi'
    elif PAR_ambitoTiffNuevo == 'rasterDest_CyL' or PAR_ambitoTiffNuevo == 'rasterRefe_CyL' or PAR_ambitoTiffNuevo[:3] == 'CyL':
        idAmbitoTif = 'CyL'
    elif PAR_ambitoTiffNuevo == 'loteAsc':
        idAmbitoTif = 'Lote'
    else:
        idAmbitoTif = 'Lote'

    if self_LOCLoutFileNameWExt is None:
        if PAR_outRasterDriver == 'GTiff':
            LCL_driverExtension = 'tif'
        elif PAR_outRasterDriver == 'JP2ECW':
            LCL_driverExtension = 'jp2'
        elif PAR_outRasterDriver == 'JP2OpenJPEG':
            LCL_driverExtension = 'jp2'
        elif PAR_outRasterDriver == 'KEA':
            LCL_driverExtension = 'KEA'
        elif PAR_outRasterDriver == 'HDF5':
            LCL_driverExtension = 'H5'
        else:
            LCL_driverExtension = 'xxx'

        LCL_idInputDir = os.path.basename(self_LOCLrutaAscRaizBase)

        self_LOCLoutFileNameWExt = '{}_{}_Global{}.{}'.format('uniCellAllDasoVars', LCL_idInputDir, idAmbitoTif, LCL_driverExtension)
        # self_LOCLoutFileNameWExtLote = '{}_{}_GlobalLote.{}'.format('uniCellAllDasoVars', 'local', LCL_driverExtension)
        # self_LOCLoutFileNameWExtCyL = '{}_{}_GlobalCyL.{}'.format('uniCellAllDasoVars', 'local', LCL_driverExtension)
        # self_LOCLoutFileNameWExtIndi = '{}_{}_GlobalIndi.{}'.format('uniCellAllDasoVars', 'local', LCL_driverExtension)
    # else:
    #     # self_LOCLoutFileNameWExtLote = self_LOCLoutFileNameWExt.replace('.', 'Lote.')
    #     # self_LOCLoutFileNameWExtCyL = self_LOCLoutFileNameWExt.replace('.', 'CyL.')
    #     # self_LOCLoutFileNameWExtIndi = self_LOCLoutFileNameWExt.replace('.', 'Indi.')

    # ==========================================================================
    if self_LOCLlistaDasoVarsFileTypes is None:
        myLog.critical('clidraster-> ATENCION: esto no debiera ocurrir (revisar codigo).')
        self_LOCLlistaDasoVarsFileTypes = []
        if not self_inFilesListAllTypes is None:
            # Se lee de las listas de ficheros (el priero de cada lista)
            for inFileTypeList in self_inFilesListAllTypes:
                self_LOCLlistaDasoVarsFileTypes.append(inFileTypeList[0][1][9:-4])
        else:
            for inFileTypePathName in list(self_inFilesDictAllTypes.values())[0]:
                self_LOCLlistaDasoVarsFileTypes.append(inFileTypePathName[1][9:-4])
        self_LOCLlistaDasoVarsFileTypes.append('MFE25')
        self_LOCLlistaDasoVarsFileTypes.append('TMasa')
        myLog.critical('\t-> Creado self_LOCLlistaDasoVarsFileTypes', self_LOCLlistaDasoVarsFileTypes)
    # ==========================================================================

    if not self_inFilesListAllTypes is None:
        numDLVs = len(self_inFilesListAllTypes)
        numBloques = len(self_inFilesListAllTypes[0])
        listaCodigosBloque = list(inFileBloqueX[1][:8] for inFileBloqueX in self_inFilesListAllTypes[0])
        for inFilesListTypeX in self_inFilesListAllTypes:
            # Debiera haber el mismo numero de ficheros por fileType.
            # Se verifica por si self_inFilesListAllTypes llegara incorrecto.
            if numBloques != len(inFilesListTypeX):
                myLog.error('clidraster-> ATENCION: todas las listas en self_inFilesListAllTypes deben tener el mismo numero de ficheros (ordenados por codBloque).')
                myLog.error('f{TB}-> Se inerrume la ejecucion.')
                sys.exit(0)
    else:
        numDLVs = len(list(self_inFilesDictAllTypes.values())[0])
        numBloques = len(self_inFilesDictAllTypes)
        listaCodigosBloque = sorted(list(self_inFilesDictAllTypes.keys()))

        numOrdenCodigoBloque0 = 0
        inFilesListPorCodigoBloque0 = list(self_inFilesDictAllTypes.values())[numOrdenCodigoBloque0]
        nFilesPorCodigoBloque0 = len(inFilesListPorCodigoBloque0)
        for numOrdenCodigoBloqueX in range(numBloques):
            # Debiera haber el mismo numero de ficheros por fileType.
            # Si no es asi con self_inFilesDictAllTypes significaria que algun codigoBloque
            # no tiene todos los fileTypes, pero eso ya se ha controlado en clidtwins
            inFilesListPorCodigoBloqueX = list(self_inFilesDictAllTypes.values())[numOrdenCodigoBloqueX]
            if nFilesPorCodigoBloque0 != len(inFilesListPorCodigoBloqueX):
                myLog.error('clidraster-> ATENCION: todos los bloques de self_inFilesDictAllTypes deben tener el mismo numero de ficheros (ordenados por DLV).')
                myLog.error('f{TB}-> Se inerrume la ejecucion.')
                sys.exit(0)

    nBandasOutput = numDLVs + 2
    myLog.debug('\n{:_^80}'.format(''))
    myLog.debug('clidraster-> Recuento de DLVs y boques:')
    myLog.debug(f'{TB}-> Num DLVs            {numDLVs}')
    myLog.debug(f'{TB}-> Num bloques:        {numBloques}')
    myLog.debug(f'{TB}-> listaCodigosBloque: {listaCodigosBloque}')
    myLog.debug('{:=^80}'.format(''))
    # myDasoVarsFileType0 = self_LOCLlistaDasoVarsFileTypes[0]
            
    txtTipoFichero = self_LOCLlistaDasoVarsFileTypes[AUX_numTipoFichero]

    # Para transformar coordenadas de huso 29 a 30 uso gdal.osr.SpatialReference(), que no se puede usar con nb.
    #  https://pcjericks.github.io/py-gdalogr-cookbook/projection.html
    #  https://github.com/OSGeo/gdal/issues/1546
    #  https://gis.stackexchange.com/questions/201061/python-gdal-api-transformosr-coordinatetransformation
    #  https://www.programcreek.com/python/example/97606/osgeo.osr.CoordinateTransformation
    try:
        srs_25829 = osr.SpatialReference()
        srs_25830 = osr.SpatialReference()
        ct_25829_to_25830 = osr.CoordinateTransformation(srs_25829, srs_25830)
    except:
        srs_25829 = gdal.osr.SpatialReference()
        srs_25830 = gdal.osr.SpatialReference()
        ct_25829_to_25830 = gdal.osr.CoordinateTransformation(srs_25829, srs_25830)
    srs_25829.ImportFromEPSG(25829)
    srs_25830.ImportFromEPSG(25830)
    hayBloquesH29 = False

    # ==========================================================================
    # Calculo las dimensiones del tiff
    # Recorro todos los ficheros para verificar si tienen mismas dimensiones y cellsize
    if PAR_ambitoTiffNuevo[:3] == 'CyL':
        if PAR_ambitoTiffNuevo == 'CyL':
            # Castilla y Leon: Valorar si se generan tb de 10x10 y 20x20 m
            nMinX_tif, nMaxX_tif = 165000.0, 601900.0
            nMinY_tif, nMaxY_tif = 4431800.0, 4789100.0
            anchoMarcoMetros, altoMarcoMetros = 21845 * 20, 17865 * 20
            # Tipo de datos de la banda= Byte
        elif PAR_ambitoTiffNuevo == 'CyL_w':
            nMinX_tif, nMaxX_tif = 165000.0, 385000.0
            nMinY_tif, nMaxY_tif = 4431800.0, 4789100.0
            anchoMarcoMetros, altoMarcoMetros = 220000, 17865 * 20
        elif PAR_ambitoTiffNuevo == 'CyL_e':
            nMinX_tif, nMaxX_tif = 385000.0, 601900.0
            nMinY_tif, nMaxY_tif = 4431800.0, 4789100.0
            anchoMarcoMetros, altoMarcoMetros = 220000, 17865 * 20
        elif PAR_ambitoTiffNuevo == 'CyL_marcoCE':
            #ladoMarco = 20000
            nMinX_tif, nMaxX_tif = 287000, 431000
            nMinY_tif, nMaxY_tif = 4520000, 4689000
        elif PAR_ambitoTiffNuevo == 'CyL_marcoSE':
            #ladoMarcoX = 260000
            nMinX_tif, nMaxX_tif = 342000, 602000
            nMinY_tif, nMaxY_tif = 4450000, 4623000
            # nMinX_tif, nMaxY_tif = 328000.0, 4622000.0
            # anchoMarcoMetros, altoMarcoMetros = xxxxx, 16700
        elif PAR_ambitoTiffNuevo == 'CyL_marcoSW':
            ladoMarco = 50000
            nMinX_tif, nMaxX_tif = 250000, 250000 + ladoMarco
            nMinY_tif, nMaxY_tif = 4550000 - ladoMarco, 4550000
            # nMinX_tif, nMaxY_tif = 165000.0, 4622000.0
            # anchoMarcoMetros, altoMarcoMetros = xxxxx, 16700
        elif PAR_ambitoTiffNuevo == 'CyL_marcoNW':
            ladoMarco = 50000
            nMinX_tif, nMaxX_tif = 200000, 200000 + ladoMarco
            nMinY_tif, nMaxY_tif = 4700000 - ladoMarco, 4700000
            # nMinX_tif, nMaxY_tif = 165000.0, 4790000.0
            # anchoMarcoMetros, altoMarcoMetros = 16300, 17200
        elif PAR_ambitoTiffNuevo == 'CyL_marcoNE':
            ladoMarco = 50000
            nMinX_tif, nMaxX_tif = 450000, 450000 + ladoMarco
            nMinY_tif, nMaxY_tif = 4700000 - ladoMarco, 4700000
            # nMinX_tif, nMaxY_tif = 328000.0, 4790000.0
            # anchoMarcoMetros, altoMarcoMetros = 28600, 17200
    else:
        nMinX_tif = 99999999
        nMaxX_tif = 0
        nMinY_tif = 99999999
        nMaxY_tif = 0
    listaMetrosBloqueX = []
    listaMetrosBloqueY = []
    listaCellSize = []
    dictInputAscNameSinPath = {}
    dictInputAscNameConPath = {}

    contadorBloquesCandidatos = 0
    contadorBloquesProcesando = 0

    # Las listas incluidas en self_inFilesListAllTypes estan ordenadas
    # por nombre de fichero (y por lo tanto por codigoBloque) 
    if not self_inFilesListAllTypes is None:
        # Lista de duplas (list) de [pathName, fileNme]
        infilesListTipo0 = self_inFilesListAllTypes[0]
    else:
        infilesListTipo0 = []
        for (codigoBloque, listaInFilesAllTypesPorCodigoBloque) in self_inFilesDictAllTypes.items():
            # Lista de duplas (tuple) de (pathName, fileNme)
            infilesListTipo0.append(listaInFilesAllTypesPorCodigoBloque[0])
            # for listaInFilesType0PorCodigoBloque in listaInFilesAllTypesPorCodigoBloque:
            #     myLog.debug(f'{TB}{TV}{TV}---->>>> listaInFilesType0PorCodigoBloque[1]: {listaInFilesType0PorCodigoBloque[1]}')

    myLog.info('\n{:_^80}'.format(''))
    if PAR_generarDasoLayers:
        myLog.info(f'clidraster-> Leyendo {len(infilesListTipo0)} bloques y {PAR_nInputVars} variables para cada bloque ({PAR_nInputVars} tipos de fichero):')
        myLog.info(f'{TB}-> Se leen las cabeceras de los ficheros del tipo {0} ({txtTipoFichero}).')
        myLog.info(f'{TB}{TV}-> Tambien se verifica que los ficheros de las otras variables tienen las mismas dimensiones y resolucion.')
        myLog.info(f'{TB}{TV}-> Se calculan los rangos de las coordenadas de los bloques (debiera exceder al del marco de analisis).')
        myLog.info(f'{TB}{TV}-> El noDataValue debe ser el mismo para todos los bloques en cada variable pero puede cambiar de una variable a otra.')
        myLog.info(f'{TB}{TV}-> Las coordenadas de la esquina superior-izquierda cambian de bloque a bloque')
        myLog.info(f'{TB}-> Se leen los valores de cada variable en todos los ficheros para calcular rango de valores de cada una.')
    else:
        myLog.info(f'clidraster-> Leyendo {len(infilesListTipo0)} bloques:')
    if len(infilesListTipo0) > 5:
        mostrarNumFicheros = 5
        myLog.info(f'{TB}-> Solo se muestran los {mostrarNumFicheros} primeros bloques.')
    else:
        mostrarNumFicheros = 0
    timeInicio = time.asctime(time.localtime(time.time()))
    myLog.info(f'{TB}-> Inicio lectura bloques: {timeInicio}')

    # ==========================================================================
    nFicherosDisponiblesPorTipoVariable = np.zeros(PAR_nInputVars, dtype=np.uint32)
    # arrayMinVariables = np.zeros(PAR_nInputVars, dtype=np.float32)
    arrayMinVariables = np.zeros(nBandasOutput, dtype=np.float32)
    arrayMinVariables.fill(999999)
    # arrayMaxVariables = np.zeros(PAR_nInputVars, dtype=np.float32)
    arrayMaxVariables = np.zeros(nBandasOutput, dtype=np.float32)
    arrayMaxVariables.fill(-999999)
    noDataDasoVarAll = 255

    # ==========================================================================
    for contadorInFiles, (inputAscDirTipo0, inputAscName1) in enumerate(infilesListTipo0):
        tiempo0 = time.time()
        myLog.debug(f'{TB}-> Procesando bloque {contadorInFiles + 1}/{len(infilesListTipo0)}:')
        #=======================================================================
        if PAR_ambitoTiffNuevo[:3] == 'CyL':
            nMinX_NombreAsc = int(inputAscName1[:3]) * 1000
            nMaxY_NombreAsc = int(inputAscName1[4:8]) * 1000
            if (
                nMinX_NombreAsc < nMinX_tif
                or nMinX_NombreAsc + 2000 > nMaxX_tif
                or nMaxY_NombreAsc - 2000 < nMinY_tif
                or nMaxY_NombreAsc > nMaxY_tif
            ):
                # Bloque fuera del marco
                myLog.info(
                    'Fichero {} fuera del marco {}-{} x {}-{}'. format(
                        inputAscName1, nMinX_tif, nMaxX_tif, nMinY_tif, nMaxY_tif
                    )
                )
                continue
            else:
                contadorBloquesCandidatos += 1
                myLog.info('Fichero {} Ok dentro del marco'. format(
                    inputAscName1,
                    )
                )

        # Para cada bloque, abro los todos los ascFiles (uno por variable) y guardo su controlador en este dict:
        contadorBloquesProcesando += 1
        dictAscFileObjet = {}
        #===================================================================
        codigoBloque = inputAscName1[:8]
        dictInputAscNameSinPath[0] = inputAscName1
        dictInputAscNameConPath[0] = os.path.join(inputAscDirTipo0, dictInputAscNameSinPath[0])
        if not os.path.exists(dictInputAscNameConPath[0]):
            myLog.error('clidraster-> ATENCION: no existe el fichero {}; debe haber un error de codigo'.format(dictInputAscNameConPath[0]))
            sys.exit(0)
        fileBytes = os.stat(dictInputAscNameConPath[0]).st_size
        if fileBytes <= 200: # 200 Bytes = 0.2 KB (un asc con solo cabecera tiene 102 B)
            myLog.warning('\n{}/{} Aviso: fichero sin contenido1: {}'.format(contadorBloquesProcesando, len(infilesListTipo0), inputAscName1))
            myLog.warning('\t-> Se pasa al siguiente: {}'.format(inputAscName1))
            continue
        #===================================================================
        if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
            myLog.debug(f'{TB}{TV}-> Primero se abren todos los tipos de fichero para este bloque ({inputAscName1[:8]}):')
        #===================================================================
        nInputVar = 0
        if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
            myLog.debug(f'{TB}{TV}{TV}-> Tipo de fichero_0: {nInputVar} ({self_LOCLlistaDasoVarsFileTypes[nInputVar]}): {inputAscName1}')
            # myLog.debug(f'clidraster---->>>1-> self_LOCLlistaDasoVarsFileTypes[0]:         {self_LOCLlistaDasoVarsFileTypes[0]}')
            # myLog.debug(f'clidraster---->>>2-> self_LOCLlistaDasoVarsFileTypes[nInputVar]: {self_LOCLlistaDasoVarsFileTypes[nInputVar]}')

        try:
            dictAscFileObjet[0] = open(dictInputAscNameConPath[nInputVar], mode='r', buffering=1)  # buffering=1 indica que lea por lineas
            if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                myLog.debug(f'{TB}{TV}{TV}{TV}-> Fichero abierto ok: {dictInputAscNameSinPath[nInputVar]}')
        except:
            myLog.error('ATENCION: No se ha posido abrir e fichero {}'.format(dictInputAscNameConPath[nInputVar]))
            myLog.error('\t-> Revisar disponibilidad del fichero y si esta corrupto.')
            sys.exit(0)
        nFicherosDisponiblesPorTipoVariable[0] += 1
        #=======================================================================
        # Cada tipo de variable (fichero) puede estar en un directorio diferente
        if PAR_generarDasoLayers:
            for nInputVar in range(1, PAR_nInputVars):
                # fileTypeX = self_LOCLlistaDasoVarsFileTypes[nInputVar]
                nFicherosDisponiblesPorTipoVariable[nInputVar] += 1

                # inputAscNameNew = inputAscName1.replace(self_LOCLlistaDasoVarsFileTypes[0], self_LOCLlistaDasoVarsFileTypes[nInputVar])
                # La lista self_inFilesListAllTypes tiene los ficheros ordenados por nombre (y por lo tanto por bloque)
                if not self_inFilesListAllTypes is None:
                    (inputAscPathNew, inputAscNameNew) = self_inFilesListAllTypes[nInputVar][contadorInFiles]
                else:
                    (inputAscPathNew, inputAscNameNew) = self_inFilesDictAllTypes[codigoBloque][nInputVar]
                if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                    myLog.debug(f'{TB}{TV}{TV}-> Tipo de fichero_{nInputVar}: {nInputVar} ({self_LOCLlistaDasoVarsFileTypes[nInputVar]}): {inputAscNameNew}')

                dictInputAscNameSinPath[nInputVar] = inputAscNameNew
                dictInputAscNameConPath[nInputVar] = os.path.join(inputAscPathNew, inputAscNameNew)
                if not os.path.exists(dictInputAscNameConPath[nInputVar]):
                    myLog.error('\nclidraster-> ATENCION: no se encuentra el fichero {}'.format(dictInputAscNameConPath[nInputVar]))
                    myLog.error('\t-> Revisar codigo, porque ha sido previamente localizado.')
                    sys.exit(0)
                fileBytes2 = os.stat(dictInputAscNameConPath[nInputVar]).st_size
                if fileBytes2 <= 200: # 200 Bytes = 0.2 KB (un asc con solo cabecera tiene 102 B)
                    if PAR_verbose:
                        myLog.warning(f'{TB}{TV}{TV}{contadorBloquesProcesando}/{len(infilesListTipo0)} Aviso: fichero sin contenido2: {dictInputAscNameSinPath[nInputVar]}')
                        myLog.warning(f'{TB}{TV}{TV}{TV}-> Se pasa al siguiente.')
                    continue
                try:
                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    dictAscFileObjet[nInputVar] = open(dictInputAscNameConPath[nInputVar], mode='r', buffering=1)  # buffering=1 indica que lea por lineas
                    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                        myLog.debug(f'{TB}{TV}{TV}{TV}-> Fichero abierto ok: {dictInputAscNameSinPath[nInputVar]}')
                except:
                    myLog.error('ATENCION: No se ha posido abrir el fichero {}'.format(dictInputAscNameConPath[nInputVar]))
                    myLog.error('\t-> Revisar disponibilidad del fichero y si esta corrupto.')
                    sys.exit(0)
            if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                myLog.debug('\t-> Se toma como referencia la cabecera de los ficheros tipo {}: {}'.format(txtTipoFichero, inputAscName1))
                myLog.debug(f'{TB}{TV}-> Los demas tipos deben tener las mismas coordenadas, dimensiones y pixel, pero pueden tener distinto noData')
                myLog.debug(f'{TB}{TV}-> Para el raster generado uso el noData y tipo de dato que sea apto para todos:')
                myLog.debug(f'{TB}{TV}{TV}-> Si hay algun -9999, prevalece sobre el 255 y el 0')
        # ======================================================================

        ncolsRef = -1
        nrowsRef = -1
        xllcenterRef = -1
        yllcenterRef = -1
        cellsizeRef = -1
        nodata_valueRef = -1
        noDataValuesPorTipoFichero = {}
        cabeceraLeida = True
        try:
            for nLinea in range(6):
                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                alinea1 = dictAscFileObjet[0].readline().split(' ')
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                if alinea1[0] == 'ncols':
                    ncolsRef = int(alinea1[1])
                elif alinea1[0] == 'nrows':
                    nrowsRef = int(alinea1[1])
                elif alinea1[0] == 'xllcenter':
                    xllcenterRef = float(alinea1[1])
                elif alinea1[0] == 'yllcenter':
                    yllcenterRef = float(alinea1[1])
                elif alinea1[0] == 'cellsize':
                    cellsizeRef = float(alinea1[1])
                elif alinea1[0] == 'nodata_value':
                    nodata_valueRef = int(alinea1[1])
                    noDataValuesPorTipoFichero[0] = int(alinea1[1])
                else:
                    cabeceraLeida = False
                    break
        except:
            cabeceraLeida = False
        if not cabeceraLeida:
            myLog.error(f'\nclidraster-> ATENCION: error de cabecera en {dictInputAscNameSinPath[0]}')
            for nLinea in range(6):
                myLog.error('\tLinea {}: {}'.format(nLinea, alinea1))
            sys.exit(0)

        ncolsValoresOk = True
        nrowsValoresOk = True
        cellsizeValoresOk = True
        # Leo las lineas de cabecera del resto de self_LOCLlistaDasoVarsFileTypes para avanzar en todos los ficheros hasta la linea de datos
        for nInputVar in range(1, PAR_nInputVars):
            if not nInputVar in dictAscFileObjet.keys():
                continue
            try:
                for nLinea in range(6):
                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    alineaX = dictAscFileObjet[nInputVar].readline().split(' ')
                    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    if alineaX[0] == 'ncols' and ncolsRef != int(alineaX[1]):
                        myLog.error(f'ATENCION: el fichero {dictInputAscNameSinPath[nInputVar]} no tiene la misma cabecera que el de referencia ({dictInputAscNameSinPath[0]})')
                        myLog.error(f'{TB} ncols-> Deferencia: {ncolsRef}; Actual: {int(alineaX[1])}')
                        cabeceraLeida = False
                        ncolsValoresOk = False
                    elif alineaX[0] == 'nrows' and nrowsRef != int(alineaX[1]):
                        myLog.error(f'ATENCION: el fichero {dictInputAscNameSinPath[nInputVar]} no tiene la misma cabecera que el de referencia ({dictInputAscNameSinPath[0]})')
                        myLog.error(f'{TB} nrows-> Deferencia: {nrowsRef}; Actual: {int(alineaX[1])}')
                        cabeceraLeida = False
                        nrowsValoresOk = False
                    elif alineaX[0] == 'xllcenter' and xllcenterRef != float(alineaX[1]):
                        myLog.error(f'ATENCION: el fichero {dictInputAscNameSinPath[nInputVar]} no tiene la misma cabecera que el de referencia ({dictInputAscNameSinPath[0]})')
                        myLog.error(f'{TB} xllcenter-> Deferencia: {xllcenterRef}; Actual: {int(alineaX[1])}')
                        cabeceraLeida = False
                    elif alineaX[0] == 'yllcenter' and yllcenterRef != float(alineaX[1]):
                        myLog.error(f'ATENCION: el fichero {dictInputAscNameSinPath[nInputVar]} no tiene la misma cabecera que el de referencia ({dictInputAscNameSinPath[0]})')
                        myLog.error(f'{TB} yllcenter-> Deferencia: {yllcenterRef}; Actual: {int(alineaX[1])}')
                        cabeceraLeida = False
                        cellsizeValoresOk = False
                    elif alineaX[0] == 'cellsize' and cellsizeRef != float(alineaX[1]):
                        myLog.error(f'ATENCION: el fichero {dictInputAscNameSinPath[nInputVar]} no tiene la misma cabecera que el de referencia ({dictInputAscNameSinPath[0]})')
                        myLog.error(f'{TB} cellsize-> Deferencia: {cellsizeRef}; Actual: {int(alineaX[1])}')
                        cabeceraLeida = False
                    elif alineaX[0] == 'nodata_value':
                        noDataValuesPorTipoFichero[nInputVar] = int(alineaX[1])
            except:
                cabeceraLeida = False

            if not cabeceraLeida:
                myLog.error(f'clidraster-> ATENCION: error de cabeceras: la cabecera de {dictInputAscNameSinPath[nInputVar]} es distinta a la de referencia ({dictInputAscNameSinPath[0]})')
                continue

        if not cellsizeRef in listaCellSize:
            listaCellSize.append(cellsizeRef)

        if PAR_generarDasoLayers:
            # No data virtual para tipoBosque (MFE25)
            noDataValuesPorTipoFichero[PAR_nInputVars] = PAR_noDataMergeTiff
            # No data virtual para tipoMasa
            noDataValuesPorTipoFichero[PAR_nInputVars + 1] = PAR_noDataMergeTiff

            if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                myLog.debug(f'{TB}{TV}{TV}{TV}-> noDataValuesPorTipoFichero: {noDataValuesPorTipoFichero}')
            # Adopto el valor de noData mas elevado en valor absoluto (normalmente -9999)
            for nInputVar in noDataValuesPorTipoFichero.keys():
                noDataDasoVarX = noDataValuesPorTipoFichero[nInputVar]
                if noDataDasoVarX != noDataDasoVarAll and abs(noDataDasoVarX) > abs(noDataDasoVarAll):
                    noDataDasoVarAll = noDataDasoVarX

        elif integrarFicherosAsc:
            if contadorBloquesProcesando == 1:
                noDataIni = nodata_valueRef
                if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                    myLog.debug(f'{TB}{TV}-> noData_valueRef: {nodata_valueRef}')
            elif noDataIni != nodata_valueRef:
                myLog.warning(f'{TB}{TV}->AVISO: Fichero con noData ({nodata_valueRef}) != del inicial ({noDataIni})')

        nMaxX_NombreAsc = (int(inputAscName1[:3]) * 1000) + (cellsizeRef * ncolsRef)
        nMinY_NombreAsc = (int(inputAscName1[4:8]) * 1000) - (cellsizeRef * nrowsRef)

        nMinX_HeaderAsc = xllcenterRef - (cellsizeRef / 2)
        nMaxX_HeaderAsc = xllcenterRef - (cellsizeRef / 2) + (cellsizeRef * ncolsRef)
        nMinY_HeaderAsc = yllcenterRef - (cellsizeRef / 2)
        nMaxY_HeaderAsc = yllcenterRef - (cellsizeRef / 2) + (cellsizeRef * nrowsRef)
        nPixelX_Origen, nPixelY_Origen = cellsizeRef, -cellsizeRef
        nCeldasX_Origen, nCeldasY_Origen = ncolsRef, nrowsRef
        metrosBloqueX = ncolsRef * cellsizeRef
        metrosBloqueY = nrowsRef * cellsizeRef
        if not metrosBloqueX in listaMetrosBloqueX:
            listaMetrosBloqueX.append(metrosBloqueX)
        if not metrosBloqueY in listaMetrosBloqueY:
            listaMetrosBloqueY.append(metrosBloqueY)
        listaMetrosBloqueX.sort(reverse=True)
        listaMetrosBloqueY.sort(reverse=True)

        if xllcenterRef > 650000:
            hayBloquesH29 = True
            TRNShuso29 = True
            # yllcenterH30, yllcenterH30, _ = ct_25829_to_25830.TransformPoint(xllcenterRef, yllcenterRef)
            nMinX_HeaderAscH30, nMinY_HeaderAscH30, _ = ct_25829_to_25830.TransformPoint(nMinX_HeaderAsc, nMinY_HeaderAsc)
            nMaxX_HeaderAscH30, nMaxY_HeaderAscH30, _ = ct_25829_to_25830.TransformPoint(nMaxX_HeaderAsc, nMaxY_HeaderAsc)
            if PAR_ambitoTiffNuevo[:3] != 'CyL':
                nMinX_tif = min(nMinX_tif, nMinX_HeaderAscH30)
                # nMaxX_tif = max(nMaxX_tif, nMaxX_HeaderAscH30 + metrosBloqueX)
                # nMinY_tif = min(nMinY_tif, nMinY_HeaderAscH30 - metrosBloqueY)
                nMaxX_tif = max(nMaxX_tif, nMaxX_HeaderAscH30)
                nMinY_tif = min(nMinY_tif, nMinY_HeaderAscH30)
                nMaxY_tif = max(nMaxY_tif, nMaxY_HeaderAscH30)
        else:
            TRNShuso29 = False
            if PAR_ambitoTiffNuevo[:3] != 'CyL':
                nMinX_tif = min(nMinX_tif, nMinX_HeaderAsc)
                # nMaxX_tif = max(nMaxX_tif, nMaxX_HeaderAsc + metrosBloqueX)
                # nMinY_tif = min(nMinY_tif, nMinY_HeaderAsc - metrosBloqueY)
                nMaxX_tif = max(nMaxX_tif, nMaxX_HeaderAsc)
                nMinY_tif = min(nMinY_tif, nMinY_HeaderAsc)
                nMaxY_tif = max(nMaxY_tif, nMaxY_HeaderAsc)

        if PAR_verbose > 1:
            if mostrarNumFicheros == 0 or (
                contadorInFiles < mostrarNumFicheros
                or contadorInFiles == len(infilesListTipo0) - 1
            ):
                myLog.debug(f'clidraster-> Resultado tras leer todas las cabeceras ({contadorInFiles + 1}/{len(infilesListTipo0)}):')
                myLog.debug(f'{TB}-> noDataDasoVarAll:     {noDataDasoVarAll}')
                myLog.debug(f'{TB}-> cellsizeRef:          {cellsizeRef} (ok: {cellsizeValoresOk})')
                myLog.debug(f'{TB}-> ncolsRef x nrowsRef:  {ncolsRef} x {nrowsRef} (ok: {ncolsValoresOk} & {nrowsValoresOk})')
                myLog.debug(f'{TB}-> metrosBloqueX:        {metrosBloqueX} metrosBloqueY: {metrosBloqueY}')
                myLog.debug(f'{TB}-> nMinXY_HeaderAsc:     {nMinX_HeaderAsc} // {nMinY_HeaderAsc}')
                myLog.debug(f'{TB}-> nMaxXY_HeaderAsc:     {nMaxX_HeaderAsc} // {nMaxY_HeaderAsc}')
                myLog.debug(f'{TB}-> Min XY:               {nMinX_tif} // {nMinY_tif}')
                myLog.debug(f'{TB}-> Max XY:               {nMaxX_tif} // {nMaxY_tif}')

        for nInputVar in range(PAR_nInputVars):
            if not nInputVar in dictAscFileObjet.keys():
                continue
            for nFila in range(nrowsRef):
                # ==============================================================
                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                strLineaCompleta = dictAscFileObjet[nInputVar].readline()
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                strLineaCompleta = ((strLineaCompleta.replace('\n', '')).replace('\r', '')).replace('  ', ' ')
                listLineaCompleta = strLineaCompleta.split(' ')
                if '' in listLineaCompleta:
                    listLineaCompleta.remove('')
                nColumnas = len(listLineaCompleta)
                if nColumnas != ncolsRef:
                    myLog.warning(f'clidraster-> Aviso: el fichero {dictInputAscNameSinPath[nInputVar]} tiene en la fila {nFila}: {nColumnas} columnas y su cabecera dice {ncolsRef} columnas. Ultimo elemento: <{listLineaCompleta[-1]}> len: {len(listLineaCompleta[-1])}')
                # ==============================================================
                for nColumna in range(nColumnas):
                    saltarFila = False
                    txtValorVariable = listLineaCompleta[nColumna]
                    if not txtValorVariable.replace('.', '', 1).replace('-', '', 1).isdigit():
                        if txtValorVariable != '\n' and txtValorVariable != '\r' and txtValorVariable != '':
                            myLog.warning(f'clidraster-> Aviso: revisar el contenido del fichero {dictInputAscNameSinPath[nInputVar]}, fila de datos num {nFila}: no debe tener texto: {txtValorVariable}')
                        saltarFila = True
                        break
                    valorVariable = np.float32(txtValorVariable)
                    # Se buscan los maximos y minimos, descartando los noData de cada ASC
                    if nInputVar in noDataValuesPorTipoFichero.keys() and valorVariable != noDataValuesPorTipoFichero[nInputVar]:
                        arrayMinVariables[nInputVar] = min(arrayMinVariables[nInputVar], valorVariable)
                        arrayMaxVariables[nInputVar] = max(arrayMaxVariables[nInputVar], valorVariable)
                if saltarFila:
                    continue
        tiempo1 = time.time()
        myLog.debug(f'{TB}-> Tiempo para leer bloque (para obtener los rangos de coordenadas y valores): {(tiempo1 - tiempo0):0.1f} segundos')
    # ==========================================================================
    timeFin = time.asctime(time.localtime(time.time()))
    myLog.info(f'{TB}-> Fin lectura bloques: {timeFin}')

    if nMinX_tif == 99999999 or nMinY_tif == 99999999 or nMaxX_tif == 0 or nMaxY_tif == 0:
        myLog.error(f'clidraster-> Revisar coordenadas de los ficheros ASC X. Rango: {nMinX_tif} {nMaxX_tif}, Y: {nMinY_tif} {nMaxY_tif}')
        sys.exit(0)
    # ==========================================================================
    if len(listaCellSize) == 0:
        myLog.error(f'Ningun fichero ASC entra dentro del marco previsto-> X: {nMinX_tif} {nMaxX_tif}, Y: {nMinY_tif} {nMaxY_tif}')
        sys.exit(0)
    # ==========================================================================
    myLog.info('{:=^80}'.format(''))

    if integrarFicherosAsc:
        noDataValueDasoVarAsc = noDataIni
    elif PAR_generarDasoLayers:
        noDataValueDasoVarAsc = noDataDasoVarAll
    else:
        noDataValueDasoVarAsc = noDataDasoVarAll

    if PAR_outputGdalDatatype is None or PAR_outputNpDatatype is None:
        if noDataValueDasoVarAsc == 255 or noDataValueDasoVarAsc == 0:
            PAR_outputGdalDatatype = gdal.GDT_Byte
            PAR_outputNpDatatype = np.uint8
        else:
            PAR_outputGdalDatatype = gdal.GDT_Float32
            PAR_outputNpDatatype = np.float32

    listaCellSize.sort(reverse=True)
    if PAR_rasterPixelSize == 0 or PAR_rasterPixelSize is None:
        metrosPixelX_Destino = max(listaCellSize)
        metrosPixelY_Destino = -max(listaCellSize)
    else:
        metrosPixelX_Destino = PAR_rasterPixelSize
        metrosPixelY_Destino = -PAR_rasterPixelSize

    # Ajusto las esquinas del tiff a coordenadas multiplo del pixel
    nMinX_tif = cellsizeRef * math.floor(nMinX_tif / cellsizeRef)
    nMaxX_tif = cellsizeRef * math.ceil(nMaxX_tif / cellsizeRef)
    nMinY_tif = cellsizeRef * math.floor(nMinY_tif / cellsizeRef)
    nMaxY_tif = cellsizeRef * math.ceil(nMaxY_tif / cellsizeRef)

    if PAR_ambitoTiffNuevo == 'CyL':
        nCeldasX_Destino, nCeldasY_Destino = 21845 * 2, 17865 * 2
        # Tipo de datos de la banda= Byte
    elif PAR_ambitoTiffNuevo == 'CyL_w':
        nCeldasX_Destino, nCeldasY_Destino = 22000, 17865 * 2
    elif PAR_ambitoTiffNuevo == 'CyL_e':
        nCeldasX_Destino, nCeldasY_Destino = 22000, 17865 * 2
    elif PAR_ambitoTiffNuevo[:9] == 'CyL_marco':
        nCeldasX_Destino, nCeldasY_Destino = math.ceil((nMaxX_tif - nMinX_tif) / metrosPixelX_Destino), abs(math.ceil((nMaxY_tif - nMinY_tif) / metrosPixelY_Destino))
    elif PAR_ambitoTiffNuevo[:3] == 'CyL':
        nCeldasX_Destino, nCeldasY_Destino = math.ceil(ladoMarco / metrosPixelX_Destino), abs(math.ceil(ladoMarco / metrosPixelY_Destino))
    else:
        # LoteAsc, FicherosTiffIndividuales
        nCeldasX_Destino = math.ceil((nMaxX_tif - nMinX_tif) / metrosPixelX_Destino)
        nCeldasY_Destino = math.ceil((nMaxY_tif - nMinY_tif) / metrosPixelX_Destino)

    # if not LCL_convertirAlt:
    #     PAR_noDataTiffProvi = noDataValueDasoVarAsc

    if PAR_ambitoTiffNuevo == 'rasterDest_CyL' or PAR_ambitoTiffNuevo == 'rasterRefe_CyL':
        # nTipoOutput == 6 or nTipoOutput == 7:
        # Integrar los ficheros asc en un tif creado previamente
        # or Integrar los ficheros asc en un tif igual a uno de referencia (mismas dimensiones y resolucion)
        # if rasterQueSeUsaComoDeferencia and os.path.exists(os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExtCyL)):
        if rasterQueSeUsaComoDeferencia and os.path.exists(os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExt)):
            # Si he establecido rasterQueSeUsaComoDeferencia or rasterEnElQueSeEscribe
            #  prevalecen las propiedades del raster de referencia o destino sobre los de los asc
            if rasterQueSeUsaComoDeferencia:
                # Abro la capa raster de referencia y extraigo informacion general
                inputRaster = gdal.Open(rasterQueSeUsaComoDeferencia)
            # elif os.path.exists(os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExtCyL)):
            elif os.path.exists(os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExt)):
                # Abro la capa raster de destino y extraigo informacion general
                # inputRaster = gdal.Open(os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExtCyL))
                inputRaster = gdal.Open(os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExt))
            # bandCount = inputRaster.RasterCount
            rasterXSize = inputRaster.RasterXSize
            rasterYSize = inputRaster.RasterYSize
            geoTransform = inputRaster.GetGeoTransform()
            rasterCRS = osr.SpatialReference()
            rasterCRS.ImportFromWkt(inputRaster.GetProjectionRef())
            # totalPixeles = rasterXSize * rasterYSize
            nPixelX_Deferencia = geoTransform[1]
            nPixelY_Deferencia = geoTransform[5]
            origenX = geoTransform[0]
            origenY = geoTransform[3]
            if rasterQueSeUsaComoDeferencia:
                myLog.info('\nPara generar el tiff se utiliza uno de referencia: {}'.format(rasterQueSeUsaComoDeferencia))
            elif rasterEnElQueSeEscribe and os.path.exists(os.path.join(self_LOCLoutPathNameRuta, rasterEnElQueSeEscribe)):
                myLog.info('\nLos fichero asc se escriben en un tiff ya existente: {}'.format(rasterEnElQueSeEscribe))
            myLog.info('\trasterSize: %i x %i' % (rasterXSize, rasterYSize))
            myLog.info(f'{TB}Esquina superior izquierda: {origenX} {origenY}')
            myLog.info(f'{TB}Ancho y alto de pixel:      {nPixelX_Deferencia} {nPixelY_Deferencia}')
            # inputRaster.Destroy() #Esto es para los datasources
            # inputBand1 = inputRaster.GetRasterBand(1)
            # infoSrcband(inputBand1)
            # inputBand1 = None
            del inputRaster
            '''
            # Otra forma de cargar el Raster como matriz de numpy:
            myLog.info('Cargando el raster en un np.array con gdalnumeric.LoadFile()')
            srcArray = gdalnumeric.LoadFile(rasterQueSeUsaComoDeferencia)
            myLog.info(f'srcArray.size:  {srcArray.size}')
            myLog.info(f'srcArray.shape: {srcArray.shape}')
            '''
            nMinX_tif = origenX
            nMaxY_tif = origenY
            metrosPixelX_Destino, metrosPixelY_Destino = nPixelX_Deferencia, nPixelY_Deferencia
            nCeldasX_Destino, nCeldasY_Destino = rasterXSize, rasterYSize
        else:
            myLog.critical('clidraster-> ATENCION: No se encuentra el raster de referencia o en el que se escribe: {}'.format(rasterQueSeUsaComoDeferencia))
            myLog.critical('\t-> Revisar codigo')
    #===========================================================================


    #===========================================================================
    if PAR_generarDasoLayers:
        fileCoordYear = '{}_{}'.format(int(nMinX_tif / 1000), int(nMaxY_tif / 1000))
        # self_LOCLrutaAscRaizBase = 'O:/Sigmena/usuarios/COMUNES/Bengoa/Lidar/cartoLidar/Sg_PinoSilvestre'
        # self_LOCLoutPathNameRuta = os.path.join(self_LOCLrutaAscRaizBase, self_LOCLoutputSubdirNew)

        # ATENCION: Valorar si genero siempre el tiff en huso 30
        if nMinX_tif >= 650000:
            LOCLhusoUTM = 29
        else:
            LOCLhusoUTM = 30
        LOCLmetrosCelda = metrosPixelX_Destino

        myLasHead = myClass()
        myLasHead.xSupIzda = nMinX_tif
        myLasHead.ySupIzda = nMaxY_tif
        myLasHead.xmin = nMinX_tif
        myLasHead.ymin = nMaxY_tif - (nCeldasY_Destino * LOCLmetrosCelda)
        myLasHead.xmax = nMinX_tif + (nCeldasX_Destino * LOCLmetrosCelda)
        myLasHead.ymax = nMaxY_tif
        # ATENCION: la conversion entre husos para dasoLidar esta pendiente
        if LOCLhusoUTM == 29:
            myLasHead.xminBloqueH30 = myLasHead.xmin
            myLasHead.yminBloqueH30 = myLasHead.ymin
            myLasHead.xmaxBloqueH30 = myLasHead.xmax
            myLasHead.ymaxBloqueH30 = myLasHead.ymax
    
        myLasData = myClass()
        myLasData.nCeldasX = nCeldasX_Destino
        myLasData.nCeldasY = nCeldasY_Destino

        cartoRefMfe = leerMFE(
            myLasHead,
            myLasData,
            fileCoordYear,
            nMinX_tif,
            nMaxY_tif,
            nCeldasX_Destino,
            nCeldasY_Destino,
            LOCLmetrosCelda,
            self_LOCLoutPathNameRuta,
            PAR_cartoMFEpathName=PAR_cartoMFEpathName,
            PAR_cartoMFEfileName=PAR_cartoMFEfileName,
            PAR_cartoMFEfileSoloExt=PAR_cartoMFEfileSoloExt,
            PAR_cartoMFEfileNSinExt=PAR_cartoMFEfileNSinExt,
            PAR_cartoMFEcampoSp=PAR_cartoMFEcampoSp,
            PAR_cartoMFErecorte=PAR_cartoMFErecorte,
            PAR_verbose=PAR_verbose,
            LOCLhusoUTM=LOCLhusoUTM,
        )
    #===========================================================================

    #===========================================================================
    if not cartoRefMfe.usarVectorRef:
        myLog.error('\nclidraster-> ATENCION: no se ha podido leer el MFE.')
        sys.exit(0)
    elif (
        nMinX_tif > cartoRefMfe.inputVectorXmax
        or nMaxX_tif < cartoRefMfe.inputVectorXmin
        or nMinY_tif > cartoRefMfe.inputVectorYmax
        or nMaxY_tif < cartoRefMfe.inputVectorYmin
    ):
        if (
            cartoRefMfe.inputVectorYmin > 0
            and cartoRefMfe.inputVectorYmin < 90
        ):
            myLog.error('\nclidraster-> ATENCION: usar una capa MFE con cordenadas proyectadas (no geograficas)')
            sys.exit(0)
        
        myLog.error('\nclidraster-> ATENCION: no hay cobertura de MFE en la zona analizada (a):')
        myLog.error(
            '\t-> Rango de coordenadas UTM de la zona analizada: X: {:0.2f} - {:0.2f}; Y: {:0.2f} - {:0.2f}'.format(
                nMinX_tif, nMaxX_tif, nMinY_tif, nMaxY_tif,
            )
        )
        myLog.error(
            '\t-> Rango de coordenadas UTM cubiertas por el MFE: X: {:0.2f} - {:0.2f}; Y: {:0.2f} - {:0.2f}'.format(
                cartoRefMfe.inputVectorXmin,
                cartoRefMfe.inputVectorXmax,
                cartoRefMfe.inputVectorYmin,
                cartoRefMfe.inputVectorYmax,
            )
        )
        myLog.error(
            '\t-> Fichero MFE: {}/{}'.format(
                PAR_cartoMFEpathName,
                PAR_cartoMFEfileName,
            )
        )
        sys.exit(0)
    #===========================================================================

    dictOutputBandX = {}
    dictArrayBandaX = {}
    # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    if PAR_ambitoTiffNuevo != 'FicherosTiffIndividuales' and PAR_ambitoTiffNuevo != 'ConvertirSoloUnFicheroASC':
        # nTipoOutput != 8 and nTipoOutput != 9:
        # Abro el raster existente o creo un nuevo raster y asigno su banda 1
        if PAR_ambitoTiffNuevo == 'rasterDest_CyL':
            # nTipoOutput == 6:
            # Integrar los ficheros asc en un tif creado previamente
            if rasterEnElQueSeEscribe and os.path.exists(os.path.join(self_LOCLoutPathNameRuta, rasterEnElQueSeEscribe)):
                # Abro la capa raster de destino y asigno su rasterband 1
                outputDatasetCyL = gdal.Open(os.path.join(self_LOCLoutPathNameRuta, rasterEnElQueSeEscribe), gdal.GA_Update)
                outputBandCyL1 = outputDatasetCyL.GetRasterBand(1)
                if LCL_convertirAlt:
                    outputBandCyL1.SetNoDataValue(PAR_noDataMergeTiff)
                else:
                    outputBandCyL1.SetNoDataValue(noDataValueDasoVarAsc)
                myLog.info('\n{:_^80}'.format(''))
                myLog.info(f'clidraster-> Raster CyL en el que se va a grabar la informacion de los grid de entrada: {rasterEnElQueSeEscribe}')
            else:
                myLog.critical('ATEMCION: No se encuentra el raster en el que se escribe: {}'.format(rasterEnElQueSeEscribe))
                myLog.critical('\t-> Revisar codigo')
        else:
            myLog.info('\n{:_^80}'.format(''))
            # myLog.info(f'clidraster-> Creando fichero raster: {self_LOCLoutFileNameWExtLote}')
            myLog.info(f'clidraster-> Creando fichero raster: {self_LOCLoutFileNameWExt}')
            outputDatasetLote, outputBandLote1 = CrearOutputRaster(
                self_LOCLoutPathNameRuta,
                # self_LOCLoutFileNameWExtLote,
                self_LOCLoutFileNameWExt,
                nMinX_tif,
                nMaxY_tif,
                nCeldasX_Destino,
                nCeldasY_Destino,
                metrosPixelX_Destino,
                metrosPixelY_Destino,
                PAR_outRasterDriver,
                PAR_outputOptions,
                nBandasOutput,
                PAR_outputGdalDatatype,
                PAR_outputNpDatatype,
                noDataValueDasoVarAsc,
                PAR_noDataTiffProvi,
                PAR_noDataMergeTiff,
                LCL_convertirAlt=GLO_GLBLconvertirAlt,
                PAR_generarDasoLayers=PAR_generarDasoLayers,
                LCL_verbose=PAR_verbose,
            )
            # myLog.info('{:_^80}'.format(''))
            # myLog.info(f'clidraster-> Raster en el que se va a grabar la informacion de los grid de entrada: {self_LOCLoutFileNameWExt}')

        # ======================================================================
        if PAR_generarDasoLayers:
            # for nInputVar in range(PAR_nInputVars):
            myLog.info(f'clidraster-> Leyendo las {nBandasOutput} bandas del tif creado')
            for outputNBand in range(1, nBandasOutput + 1):
                if PAR_ambitoTiffNuevo == 'rasterDest_CyL':
                    dictOutputBandX[outputNBand] = outputDatasetCyL.GetRasterBand(outputNBand)
                else:
                    dictOutputBandX[outputNBand] = outputDatasetLote.GetRasterBand(outputNBand)
                dictArrayBandaX[outputNBand] = dictOutputBandX[outputNBand].ReadAsArray().astype(PAR_outputNpDatatype)
                # myLog.debug(f'{TB}{TV}{TV}-> Banda: {outputNBand} -> shape: {dictArrayBandaX[outputNBand].shape}')
            # myLog.debug(f'{TB}{TV}claves de dictArrayBandaX: {dictArrayBandaX.keys()}')
            myLog.debug(f'{TB}Tipo de contenido de dictArrayBandaX[outputNBand]: {type(dictArrayBandaX[outputNBand])} {dictArrayBandaX[outputNBand].dtype}')
        myLog.info('{:=^80}'.format(''))

        # ======================================================================
        # Compruebo si puedo cargar la banda 1 en memoria
        myLog.debug('\n{:_^80}'.format(''))
        myLog.debug('clidraster-> Comprobando memoria RAM disponible:')
        nBytesPorBanda = 4
        if psutilOk:
            ramMem = psutil.virtual_memory()
            megasLibres = ramMem.available / 1048576 # ~1E6
            megasReservados = 1000 if megasLibres > 2000 else megasLibres / 2
            myLog.debug('\t-> Megas libres: {:0.2f} MB'.format(megasLibres))
            numMaximoPixeles = (megasLibres - megasReservados) * 1e6 / (nBandasOutput * nBytesPorBanda)
            myLog.debug(f'{TB}{TV}-> Num max. Pixeles: {numMaximoPixeles} ({nBandasOutput} bandas, {nBytesPorBanda} bytes por pixel)')
        else:
            numMaximoPixeles = 1e9
        nMegaPixeles = nCeldasX_Destino * nCeldasY_Destino / 1e6
        nMegaBytes = nMegaPixeles * nBandasOutput * nBytesPorBanda
        myLog.debug(
            '\t-> nCeldas previstas:  {} x {} = {:0.2f} MegaPixeles = {:0.2f} MegaBytes'.format(
                nCeldasX_Destino,
                nCeldasY_Destino,
                nMegaPixeles,
                nMegaBytes,
            )
        )
        if nMegaPixeles < numMaximoPixeles * 0.5:
            # Se puede cargar toda la banda1 en memoria
            cargarRasterEnMemoria = True
            # Creo un ndarray con el contenido de la banda 1 del raster dataset creado
            myLog.debug('\t-> SI se carga toda la banda en memoria.')
            arrayBanda1 = outputBandLote1.ReadAsArray().astype(PAR_outputNpDatatype)
            myLog.debug(f'{TB}{TV}-> Tipo de dato de la Banda con el tipo de masa:  {type(arrayBanda1)}, dtype: {arrayBanda1.dtype}')
            myLog.debug(f'{TB}{TV}-> Dimensiones de la banda 1 del ndArray creado:  {arrayBanda1.shape}')
        else:
            cargarRasterEnMemoria = False
            myLog.debug(f'{TB}{TV}-> Dimensiones de la banda destino: Y-> {outputBandLote1.YSize} X-> {outputBandLote1.XSize}')
            myLog.debug(f'{TB}{TV}-> NO se carga toda la banda en memoria porque no cabe.')
        # ======================================================================

        myLog.debug(f'clidraster-> cargarRasterEnMemoria: {cargarRasterEnMemoria}')
        nMaxX_tif = nMinX_tif + (nCeldasX_Destino * metrosPixelX_Destino)
        nMinY_tif = nMaxY_tif + (nCeldasY_Destino * metrosPixelY_Destino)
        myLog.debug('{:=^80}'.format(''))
        # ======================================================================

        # myLog.debug('-->arrayBanda1:')
        # myLog.debug(arrayBanda1[10:15, 10:15])
        # myLog.debug('-->dictArrayBandaX:')
        # myLog.debug(dictArrayBandaX[outputNBand][10:15, 10:15])




    # ======================================================================
    # Tipo de bosque del MFE
    if cartoRefMfe.usarVectorRef:
        # arrayMFE = (cartoRefMfe.aCeldasLandUseCover)[::-1]).transpose()
        arrayMFE = np.flipud(cartoRefMfe.aCeldasLandUseCover.transpose())
        # myLog.debug(f'->-> {nFilaRaster} {nColumnaRaster} -> shapes: {dictArrayBandaX[nBandasOutput - 1].shape} {cartoRefMfe.aCeldasLandUseCover.shape} {arrayMFE.shape}')
        # myLog.debug(f'->-> outputNBand: {nBandasOutput - 1}, nFilaColuna: {nFilaRaster} {nColumnaRaster}, nTipoMasa: {arrayMFE[nFilaRaster, nColumnaRaster]}')
    else:
        myLog.error('\nclidraster-> ATENCION: no se ha podido crear el MFE recortado')
        sys.exit(0)
    # ======================================================================

    nMinTipoMasa = 999999
    nMaxTipoMasa = -999999
    # Si no trabajo con subLoteAsc, este buce no tiene ningun efecto (solo se ejecuta una vez)
    listaSubLotesTiff = [AUX_subLoteTiff]
    for miSubLoteTiff in listaSubLotesTiff:
        if PAR_ambitoTiffNuevo.startswith('subLoteAsc'):
            if miSubLoteTiff == 'NE':
                nMinX_tif = nMinX_tif + ((nMaxX_tif - nMinX_tif) * (1 / 2))
                nMinY_tif = nMinY_tif + ((nMaxY_tif - nMinY_tif) * (1 / 2))
            elif miSubLoteTiff == 'NW':
                nMaxX_tif = nMaxX_tif - ((nMaxX_tif - nMinX_tif) * (1 / 2))
                nMinY_tif = nMinY_tif + ((nMaxY_tif - nMinY_tif) * (1 / 2))
            elif miSubLoteTiff == 'SE':
                nMinX_tif = nMinX_tif + ((nMaxX_tif - nMinX_tif) * (1 / 2))
                nMaxY_tif = nMaxY_tif - ((nMaxY_tif - nMinY_tif) * (1 / 2))
            elif miSubLoteTiff == 'SW':
                nMaxX_tif = nMaxX_tif - ((nMaxX_tif - nMinX_tif) * (3 / 4))
                nMaxY_tif = nMaxY_tif - ((nMaxY_tif - nMinY_tif) * (3 / 4))
                # nMaxX_tif = nMaxX_tif - ((nMaxX_tif - nMinX_tif) * (1 / 2))
                # nMaxY_tif = nMaxY_tif - ((nMaxY_tif - nMinY_tif) * (1 / 2))
    
            # Ajusto las esquinas del tiff a coordenadas multiplo del bloque
            nMetrosBloque = 2000
            nMinX_tif = nMetrosBloque * math.floor(nMinX_tif / nMetrosBloque)
            nMaxX_tif = nMetrosBloque * math.ceil(nMaxX_tif / nMetrosBloque)
            nMinY_tif = nMetrosBloque * math.floor(nMinY_tif / nMetrosBloque)
            nMaxY_tif = nMetrosBloque * math.ceil(nMaxY_tif / nMetrosBloque)
    
            nCeldasX_Destino = math.ceil((nMaxX_tif - nMinX_tif) / metrosPixelX_Destino)
            nCeldasY_Destino = math.ceil((nMaxY_tif - nMinY_tif) / metrosPixelX_Destino)
        # ==========================================================================

        # ==========================================================================
        myLog.info('\n{:_^80}'.format(''))
        myLog.info('clidraster-> Algunos datos de las capas input y output:')
        myLog.info('\t-> Ambito de trabajo:                                  {}'.format(PAR_ambitoTiffNuevo))
        myLog.info('\t-> Tipo de fichero de referencia (0):                  {}'.format(txtTipoFichero))
        myLog.info('\t-> Numero de Bloques Procesados                        {}'.format(contadorBloquesProcesando))
        myLog.info('\t-> Esquina superior izda del fichero tif a generar:    {:0.2f}, {:0.2f}'.format(nMinX_tif, nMaxY_tif))
        myLog.info('\t\tRango de coordenadas X del fichero tif a generar:  {:0.2f}, {:0.2f}'.format(nMinX_tif, nMaxX_tif))
        myLog.info('\t\tRango de coordenadas Y del fichero tif a generar:  {:0.2f}, {:0.2f}'.format(nMinY_tif, nMaxY_tif))
        if PAR_ambitoTiffNuevo.startswith('subLoteAsc'):
            myLog.info('\t-> Este rango es un cuarto ({}) del lote completo.'.format(AUX_subLoteTiff))
        if len(listaMetrosBloqueX) == 1 and len(listaMetrosBloqueY) == 1:
            myLog.info('\t-> Todos los bloques tienen las mismas dimensiones (en m):')
            myLog.info('\t\tDimensiones X e Y de los ficheros asc (en m):      {}, {}'.format(listaMetrosBloqueX[0], listaMetrosBloqueY[0]))
        else:
            myLog.info('\t-> No todos los bloques tienen las mismas dimensiones:')
            myLog.info('\t\tLista de dimensiones X de los ficheros asc (en m): {}'.format(listaMetrosBloqueX[:5]))
            myLog.info('\t\tLista de dimensiones Y de los ficheros asc (en m): {}'.format(listaMetrosBloqueY[:5]))
        myLog.info('\t-> Cellsize (pixel) y num de celdas (pixeles):')
        myLog.info('\t\tCelda (pixel) de los ficheros asc (en m):          {}'.format(listaCellSize[:5]))
        myLog.info('\t\tPixel asignado al tif que se crea (en m):          {}'.format(metrosPixelX_Destino))
        myLog.info('\t\tnCeldas de la envolvente de los asc:               {}, {}'.format(nCeldasX_Destino, nCeldasY_Destino))
        myLog.info('\t-> noDataValueDasoVarAsc:                              {}'.format(noDataValueDasoVarAsc))
        myLog.info('{:=^80}'.format(''))
        # ======================================================================

        # ======================================================================
        # Bucle para cada fichero
        contadorFicherosIntegrando = 0
        myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidraster-> Se van a procesar {len(infilesListTipo0)} bloques con {PAR_nInputVars} tipos de fichero (variables) por bloque.')
        if mostrarNumFicheros:
            if PAR_verbose > 1:
                myLog.info(f'{TB}-> Solo se Muestran los {mostrarNumFicheros} primeros bloques.')
        timeInicio = time.asctime(time.localtime(time.time()))
        myLog.info(f'{TB}-> Inicio procesado bloques: {timeInicio}')

        for contadorInFiles, (inputAscDir, inputAscName1) in enumerate(infilesListTipo0):
            tiempo0 = time.time()
            myLog.debug(f'{TB}Procesando bloque {contadorInFiles + 1}/{len(infilesListTipo0)}:')
            codigoBloque = inputAscName1[:8]
            # if PAR_ambitoTiffNuevo != 'FicherosTiffIndividuales' and PAR_ambitoTiffNuevo != 'ConvertirSoloUnFicheroASC':
            #     if inputAscName1[14:-4].upper() != txtTipoFichero.upper() or inputAscName1[-4:].upper() != '.ASC':
            #         # El fichero no responde a la mascara elegida
            #         continue
            #===================================================================
            if PAR_ambitoTiffNuevo[:3] == 'CyL':
                nMinX_NombreAsc = int(inputAscName1[:3]) * 1000
                nMaxY_NombreAsc = int(inputAscName1[4:8]) * 1000
                if (
                    nMinX_NombreAsc < nMinX_tif
                    or nMinX_NombreAsc + 2000 > nMaxX_tif
                    or nMaxY_NombreAsc - 2000 < nMinY_tif
                    or nMaxY_NombreAsc > nMaxY_tif
                ):
                    # Bloque fuera del marco
                    continue
            #===================================================================

            dictAscFileObjet = {}

            #===================================================================
            dictInputAscNameSinPath[0] = inputAscName1
            dictInputAscNameConPath[0] = os.path.join(inputAscDir, dictInputAscNameSinPath[0])
            if not os.path.exists(dictInputAscNameConPath[0]):
                myLog.info('No existe el fichero {}; debe haber un error de codigo'.format(dictInputAscNameConPath[0]))
                sys.exit(0)
            fileBytes = os.stat(dictInputAscNameConPath[0]).st_size
            if fileBytes <= 200: # 200 Bytes = 0.2 KB (un asc con solo cabecera tiene 102 B)
                myLog.warning('\n{}/{} Fichero sin contenido1: {}'.format(contadorBloquesProcesando, len(infilesListTipo0), inputAscName1))
                myLog.warning('\t-> Se pasa al siguiente: {}'.format(inputAscName1))
                continue
            #===================================================================
            contadorFicherosIntegrando += 1
            nInputVar = 0
            if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                myLog.debug(f'{TB}{TV}-> Tipo de fichero: {nInputVar} ({self_LOCLlistaDasoVarsFileTypes[nInputVar]}): {inputAscName1}')
            try:
                dictAscFileObjet[0] = open(dictInputAscNameConPath[nInputVar], mode='r', buffering=1)  # buffering=1 indica que lea por lineas
                myLog.debug(f'{TB}{TV}{TV}->> Fichero abierto ok: {dictInputAscNameSinPath[nInputVar]}')
            except:
                myLog.error('ATENCION: No se ha posido abrir e fichero {}'.format(dictInputAscNameConPath[nInputVar]))
                myLog.error('\t-> Revisar disponibilidad del fichero y si esta corrupto.')
                sys.exit(0)
            #===================================================================

            #===================================================================
            if PAR_generarDasoLayers:
                for nInputVar in range(1, PAR_nInputVars):
                    # inputAscNameNew = inputAscName1.replace(self_LOCLlistaDasoVarsFileTypes[0], self_LOCLlistaDasoVarsFileTypes[nInputVar])
                    # La lista self_inFilesListAllTypes tiene los ficheros ordenados por nombre (y por lo tanto por bloque)
                    if not self_inFilesListAllTypes is None:
                        (inputAscPathNew, inputAscNameNew) = self_inFilesListAllTypes[nInputVar][contadorInFiles]
                    else:
                        (inputAscPathNew, inputAscNameNew) = self_inFilesDictAllTypes[codigoBloque][nInputVar]

                    if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                        myLog.debug(f'{TB}{TV}-> nFile: {contadorInFiles + 1}; Tipo de fichero: {nInputVar} ({self_LOCLlistaDasoVarsFileTypes[nInputVar]}): {inputAscNameNew}')

                    dictInputAscNameSinPath[nInputVar] = inputAscNameNew
                    dictInputAscNameConPath[nInputVar] = os.path.join(inputAscPathNew, inputAscNameNew)
                    if not os.path.exists(dictInputAscNameConPath[nInputVar]):
                        myLog.error('ATENCION: No se encuentra el fichero {}'.format(dictInputAscNameConPath[nInputVar]))
                        myLog.error('\t-> Revisar codigo, porque ha sido previamente localizado.')
                        sys.exit(0)
                    fileBytes2 = os.stat(dictInputAscNameConPath[nInputVar]).st_size
                    if fileBytes2 <= 200: # 200 Bytes = 0.2 KB (un asc con solo cabecera tiene 102 B)
                        myLog.warning('\n{}/{} Aviso: fichero sin contenido2: {}'.format(contadorBloquesProcesando, len(infilesListTipo0), dictInputAscNameSinPath[nInputVar]))
                        myLog.warning('\t-> Se pasa al siguiente.')
                        continue
                    try:
                        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                        dictAscFileObjet[nInputVar] = open(dictInputAscNameConPath[nInputVar], mode='r', buffering=1)  # buffering=1 indica que lea por lineas
                        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                        if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                            myLog.debug(f'{TB}{TV}{TV}->> Fichero abierto ok: {dictInputAscNameSinPath[nInputVar]}')
                    except:
                        myLog.error('ATENCION: No se ha posido abrir e fichero {}'.format(dictInputAscNameConPath[nInputVar]))
                        myLog.error('\t-> Revisar disponibilidad del fichero y si esta corrupto.')
                        sys.exit(0)
            #===================================================================

            # myLog.debug('\nResumen de ficheros abiertos:')
            # for nInputVar in range(PAR_nInputVars):
            #     if nInputVar in dictAscFileObjet.keys():
            #         myLog.debug('dictAscFileObjet[{}]: {}'.format(nInputVar, dictAscFileObjet[nInputVar]))
            #     else:
            #         myLog.debug('dictAscFileObjet[{}]: {}'.format(nInputVar, 'No hay fichero'))
            if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                myLog.debug('\t-> Segundo se toma como referencia la cabecera de los ficheros tipo {}: {}'.format(txtTipoFichero, inputAscName1))
            cabeceraLeida = True
            for nLinea in range(6):
                # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                alinea1 = dictAscFileObjet[0].readline().split(' ')
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                # Leo las lineas de cabecera del resto de self_LOCLlistaDasoVarsFileTypes para avanzar en todos los fichero hasta las lineas de datos
                for nInputVar in range(1, PAR_nInputVars):
                    if nInputVar in dictAscFileObjet.keys():
                        # No uso las cabeceras de los otros ficheros
                        # Para simplificar, asumo que son iguales 
                        alineaX = dictAscFileObjet[nInputVar].readline().split(' ')
                if alinea1[0] == 'ncols':
                    ncolsRef = int(alinea1[1])
                elif alinea1[0] == 'nrows':
                    nrowsRef = int(alinea1[1])
                elif alinea1[0] == 'xllcenter':
                    xllcenterRef = float(alinea1[1])
                elif alinea1[0] == 'yllcenter':
                    yllcenterRef = float(alinea1[1])
                elif alinea1[0] == 'cellsize':
                    cellsizeRef = float(alinea1[1])
                elif alinea1[0] == 'nodata_value':
                    nodata_valueRef = int(alinea1[1])
                else:
                    cabeceraLeida = False
            '''
            #Ejemplo de Cabecera:
            ncols 200
            nrows 200
            xllcenter 350005
            yllcenter 4632005
            cellsize 10.000000
            nodata_value -9999
            '''
            if not cabeceraLeida:
                myLog.error('\nclidraster-> ATENCION: Error de cabecera en %s \n' % (inputAscName1))
                input('Pulsa una tecla.....')
                continue
            nMinX_HeaderAsc = xllcenterRef - (cellsizeRef / 2)
            nMaxX_HeaderAsc = xllcenterRef - (cellsizeRef / 2) + (cellsizeRef * ncolsRef)
            nMinY_HeaderAsc = yllcenterRef - (cellsizeRef / 2)
            nMaxY_HeaderAsc = yllcenterRef - (cellsizeRef / 2) + (cellsizeRef * nrowsRef)
            nMinX_NombreAsc = int(inputAscName1[:3]) * 1000
            nMaxX_NombreAsc = (int(inputAscName1[:3]) * 1000) + (cellsizeRef * ncolsRef)
            nMaxY_NombreAsc = int(inputAscName1[4:8]) * 1000
            nMinY_NombreAsc = (int(inputAscName1[4:8]) * 1000) - (cellsizeRef * nrowsRef)
            nPixelX_Origen, nPixelY_Origen = cellsizeRef, -cellsizeRef
            nCeldasX_Origen, nCeldasY_Origen = ncolsRef, nrowsRef
    
            # if (int(inputAscName1[:3]) * 1000) >= 650:
            if xllcenterRef > 650000:
                TRNShuso29 = True
                # yllcenterH30, yllcenterH30, _ = ct_25829_to_25830.TransformPoint(xllcenterRef, yllcenterRef)
                nMinX_HeaderAscH29, nMinY_HeaderAscH29 = nMinX_HeaderAsc, nMinY_HeaderAsc
                nMaxX_HeaderAscH29, nMaxY_HeaderAscH29 = nMaxX_HeaderAsc, nMaxY_HeaderAsc
                nMinX_NombreAscH29, nMinY_NombreAscH29 = nMinX_NombreAsc, nMinY_NombreAsc
                nMaxX_NombreAscH29, nMaxY_NombreAscH29 = nMaxX_NombreAsc, nMaxY_NombreAsc
    
                nMinX_HeaderAsc_0, nMinY_HeaderAsc_1, _ = ct_25829_to_25830.TransformPoint(nMinX_HeaderAscH29, nMinY_HeaderAscH29)
                nMinX_HeaderAsc_1, nMaxY_HeaderAsc_0, _ = ct_25829_to_25830.TransformPoint(nMinX_HeaderAscH29, nMaxY_HeaderAscH29)
                nMaxX_HeaderAsc_0, nMaxY_HeaderAsc_1, _ = ct_25829_to_25830.TransformPoint(nMaxX_HeaderAscH29, nMaxY_HeaderAscH29)
                nMaxX_HeaderAsc_1, nMinY_HeaderAsc_0, _ = ct_25829_to_25830.TransformPoint(nMaxX_HeaderAscH29, nMinY_HeaderAscH29)
                nMinX_NombreAsc_0, nMinY_NombreAsc_1, _ = ct_25829_to_25830.TransformPoint(nMinX_NombreAscH29, nMinY_NombreAscH29)
                nMinX_NombreAsc_1, nMaxY_NombreAsc_0, _ = ct_25829_to_25830.TransformPoint(nMinX_NombreAscH29, nMaxY_NombreAscH29)
                nMaxX_NombreAsc_0, nMaxY_NombreAsc_1, _ = ct_25829_to_25830.TransformPoint(nMaxX_NombreAscH29, nMaxY_NombreAscH29)
                nMaxX_NombreAsc_1, nMinY_NombreAsc_0, _ = ct_25829_to_25830.TransformPoint(nMaxX_NombreAscH29, nMinY_NombreAscH29)
    
                nMaxX_HeaderAsc = max(nMaxX_HeaderAsc_0, nMaxX_HeaderAsc_1)
                nMinX_HeaderAsc = min(nMinX_HeaderAsc_0, nMinX_HeaderAsc_1)
                nMaxY_HeaderAsc = max(nMaxY_HeaderAsc_0, nMaxY_HeaderAsc_1)
                nMinY_HeaderAsc = min(nMinY_HeaderAsc_0, nMinY_HeaderAsc_1)
                nMaxX_NombreAsc = max(nMaxX_NombreAsc_0, nMaxX_NombreAsc_1)
                nMinX_NombreAsc = min(nMinX_NombreAsc_0, nMinX_NombreAsc_1)
                nMaxY_NombreAsc = max(nMaxY_NombreAsc_0, nMaxY_NombreAsc_1)
                nMinY_NombreAsc = min(nMinY_NombreAsc_0, nMinY_NombreAsc_1)
    
                rangoX_H29 = (nMaxX_HeaderAscH29 - nMinX_HeaderAscH29)
                rangoY_H29 = (nMaxY_HeaderAscH29 - nMinY_HeaderAscH29)
    
            else:
                TRNShuso29 = False
    
            rangoX_H30 = (nMaxX_HeaderAsc - nMinX_HeaderAsc)
            rangoY_H30 = (nMaxY_HeaderAsc - nMinY_HeaderAsc)
    
    
            # ==================================================================
            if PAR_ambitoTiffNuevo.startswith('subLoteAsc'):
                if (
                    nMinX_HeaderAsc < nMinX_tif
                    or nMaxX_HeaderAsc > nMaxX_tif
                    or nMinY_HeaderAsc < nMinY_tif
                    or nMaxY_HeaderAsc > nMaxY_tif
                ):
                    continue
    
            # ==================================================================
            if PAR_ambitoTiffNuevo == 'FicherosTiffIndividuales' and PAR_ambitoTiffNuevo == 'ConvertirSoloUnFicheroASC':
                # nTipoOutput == 8 or nTipoOutput == 9:
                # Por el momento creo un raster como el cuadrado que proceso; luego lo grabare a un raster general
                myLog.debug('\nCreacion de raster con %ix%i celdas en formato GTiff, 1 banda.' % (ncolsRef, nrowsRef))
                metrosPixelX_Destino, metrosPixelY_Destino = nPixelX_Origen, nPixelY_Origen
                nCeldasX_Destino, nCeldasY_Destino = nCeldasX_Origen, nCeldasY_Origen
                nMinX_tif = nMinX_HeaderAsc
                nMaxY_tif = nMaxY_HeaderAsc
                myLog.debug(f'{TB}Esquina superior izda: {nMinX_tif} {nMaxY_tif}')
                myLog.debug(f'{TB}nCeldasX_Destino, nCeldasY_Destino: {nCeldasX_Destino} {nCeldasY_Destino}')
                # PAR_outputGdalDatatype = gdal.GDT_Float32  # Alternativas: gdal.GDT_Int32, gdal.GDT_Float32, gdal.GDT_Byte
                myLog.debug('\n{:_^80}'.format(''))
                # myLog.debug(f'clidraster-> crearTiff-> Creando raster: {self_LOCLoutFileNameWExtIndi}')
                myLog.debug(f'clidraster-> crearTiff-> Creando raster: {self_LOCLoutFileNameWExt}')
                outputDatasetIndi, outputBandIndi1 = CrearOutputRaster(
                    self_LOCLoutPathNameRuta,
                    # self_LOCLoutFileNameWExtIndi,
                    self_LOCLoutFileNameWExt,
                    nMinX_tif,
                    nMaxY_tif,
                    nCeldasX_Destino,
                    nCeldasY_Destino,
                    metrosPixelX_Destino,
                    metrosPixelY_Destino,
                    PAR_outRasterDriver,
                    PAR_outputOptions,
                    nBandasOutput,
                    PAR_outputGdalDatatype,
                    PAR_outputNpDatatype,
                    noDataValueDasoVarAsc,
                    PAR_noDataTiffProvi,
                    PAR_noDataMergeTiff,
                    LCL_convertirAlt=GLO_GLBLconvertirAlt,
                )

                # Creo un ndarray con el contenido de la banda 1 del raster dataset creado
                arrayBanda1 = outputBandIndi1.ReadAsArray().astype(PAR_outputNpDatatype)
                myLog.debug(f'Creo un ndArray que contiene toda la banda 1:  {type(arrayBanda1)} {arrayBanda1.dtype}')
                myLog.debug(f'Dimensiones del ndArray creado con la banda 1: {arrayBanda1.shape}')
                nOffsetX = 0
                nOffsetY = 0
            else:
                # El offset lo uso para asignar solo un trozo de outputBand____1 al arrayBanda1 si no hay sitio suficiente en memoria
                # O para escribir los valores en la ubicacion adecuada de outputBand____1 cuando se carga toda la manda en memoria
                nOffsetX = int((nMinX_NombreAsc - nMinX_tif) / nPixelX_Origen)  # Numero de celdas del asc
                nOffsetY = int((nMaxY_NombreAsc - nMaxY_tif) / nPixelY_Origen)  # nPixelY_Origen es negativo
                if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                    myLog.debug('\t\t-> Coordenadas y dimensiones del bloque:')
                    if TRNShuso29:
                        myLog.debug(f'{TB}{TV}{TV}-> nMinX nMaxY del asc origen en H29:   {nMinX_HeaderAscH29:9.2f}, {nMaxY_HeaderAscH29:10.2f}')
                        myLog.debug(f'{TB}{TV}{TV}-> Dimensiones del asc origen en H29:   {nCeldasX_Origen} x {nCeldasY_Origen} celdas de pixel {nPixelX_Origen} m. = {rangoX_H29} x {rangoY_H29} m.')
                        myLog.debug(f'{TB}{TV}{TV}-> \tCoordenadas de bloque transformadas a H30:')
                        myLog.debug(f'{TB}{TV}{TV}-> \t\tnMinX nMaxY del asc origen en H30:   {nMinX_HeaderAsc:9.2f}, {nMaxY_HeaderAsc:10.2f}')
                        try:
                            myLog.debug(
                                f'{TB}{TV}{TV}{TV}Rango del bloque transformado a H30: {rangoX_H30:0.2f} x {rangoY_H30:0.2f} m. '
                                f'~> {int((rangoX_H30 / cellsizeRef) * (rangoY_H30 / cellsizeRef))} pixeles teoricos de {nPixelX_Origen} m.'
                            )
                        except:
                            myLog.critical('clidraster-> Revisar este error')
                    else:
                        myLog.debug(f'{TB}{TV}{TV}-> nMinX nMaxY del asc origen (H30):    {nMinX_HeaderAsc:9.2f}, {nMaxY_HeaderAsc:10.2f}')
                        myLog.debug(f'{TB}{TV}{TV}-> Dimensiones del asc origen (H30):    {nCeldasX_Origen} x {nCeldasY_Origen} celdas de pixel {nPixelX_Origen} m. = {rangoX_H30} x {rangoY_H30} m.')
                    myLog.debug(f'{TB}{TV}{TV}-> nMinX nMaxY del tif (destino):       {nMinX_tif:9.2f}, {nMaxY_tif:10.2f}')
                    if PAR_ambitoTiffNuevo == 'rasterDest_CyL':
                        myLog.debug(f'{TB}{TV}{TV}-> Dimensiones X & Y del tif destino:   {outputBandCyL1.XSize} x {outputBandCyL1.YSize} celdas de {metrosPixelX_Destino} m.')
                    else:
                        myLog.debug(f'{TB}{TV}{TV}-> Dimensiones X & Y del tif destino:   {outputBandLote1.XSize} x {outputBandLote1.YSize} celdas de {metrosPixelX_Destino} m.')
                    myLog.debug(f'{TB}{TV}{TV}-> offset X e Y:                        {nOffsetX} {nOffsetY}')
    
                if nMinX_NombreAsc < nMinX_tif or nMaxX_NombreAsc > nMaxX_tif or nMinY_NombreAsc < nMinY_tif or nMaxY_NombreAsc > nMaxY_tif:
                    myLog.warning('\nATENCION: Coordenadas del fichero asc de entrada (%s) fuera del raster generado' % (inputAscName1))
                    myLog.warning('Fichero asc de entrada - Rango de coordendas segun el nombre   (x=%i-%i, y=%i-%i)' % (
                        nMinX_NombreAsc,
                        nMaxX_NombreAsc,
                        nMinY_NombreAsc,
                        nMaxY_NombreAsc,
                    ))
                    myLog.warning('Fichero asc de entrada - Rango de coordendas segun su cabecera (x=%i-%i, y=%i-%i)' % (
                        nMinX_HeaderAsc,
                        nMaxX_HeaderAsc,
                        nMinY_HeaderAsc,
                        nMaxY_HeaderAsc,
                    ))
                    myLog.warning('Fichero tif de salida  - Rango de coordendas (x=%i-%i, y=%i-%i)' % (nMinX_tif, nMaxX_tif, nMinY_tif, nMaxY_tif))
                    continue

                # Cargo la arrayBanda1 si no lo he hecho antes
                if not cargarRasterEnMemoria:
                    if PAR_ambitoTiffNuevo == 'rasterDest_CyL':
                        arrayBanda1 = outputBandCyL1.ReadAsArray(xoff=nOffsetX, yoff=nOffsetY, win_xsize=int(nCeldasX_Origen), win_ysize=int(nCeldasY_Origen)).astype(
                            PAR_outputNpDatatype
                        )
                    else:
                        arrayBanda1 = outputBandLote1.ReadAsArray(xoff=nOffsetX, yoff=nOffsetY, win_xsize=int(nCeldasX_Origen), win_ysize=int(nCeldasY_Origen)).astype(
                            PAR_outputNpDatatype
                        )

            # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
            # ==================================================================
            # Traslado los valores del fichero asc al arrayBanda1
            # aInputVals = np.zeros(nrowsRef * ncolsRef * PAR_nInputVars, dtype=np.float32).reshape(nrowsRef, ncolsRef, PAR_nInputVars)
            # aInputVals.fill(noDataValueDasoVarAsc)
            nMinColumnaAsc = 1E8
            nMinFilaAsc = 1E8
            nMaxColumnaAsc = 0
            nMaxFilaAsc = 0
            if PAR_verbose > 1:
                if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                    myLog.debug('\t-> Se continua leyendo todos los datos en todos los tipos de fichero (todas las variables).')
                    # myLog.debug(f'{TB}{TV}{TV}-> dictAscFileObjet.keys(): {dictAscFileObjet.keys()}')
            # ==================================================================

            for nInputVar in range(PAR_nInputVars):
                outputNBand = nInputVar + 1
                if not nInputVar in dictAscFileObjet.keys():
                    continue
                if nInputVar in noDataValuesPorTipoFichero.keys():
                    noDataValueThisVar = noDataValuesPorTipoFichero[nInputVar]
                else:
                    noDataValueThisVar = noDataValueDasoVarAsc

                for nFila in range(nrowsRef):
                    dictArrayLinea = {}
                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    strLineaCompleta = dictAscFileObjet[nInputVar].readline()
                    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    if '  ' in strLineaCompleta:
                        strLineaCompleta = strLineaCompleta.replace('  ', ' ')
                        strLineaCompleta = strLineaCompleta.replace('  ', ' ')
                    dictArrayLinea[nInputVar] = strLineaCompleta.split(' ')
                    nColumnas = len(dictArrayLinea[nInputVar]) - 1
                    if nColumnas > ncolsRef:
                        myLog.error('El fichero %s tiene mas columnas (%i) de las que indica su cabecera (%i)' % (dictInputAscNameSinPath[nInputVar], nColumnas, ncolsRef))
                        myLog.error('Revisar ficheros o codigo')
                        sys.exit(0)

                    # nInputVar = 0
                    # ==============================================================
                    # for nColumna, valor1 in enumerate(dictArrayLinea[nInputVar]):
                    for nColumna in range(ncolsRef):
                        # if not valor1.replace('.', '', 1).isdigit():
                        #     if valor1 != '\n' or valor1 != '\r' or valor1 != '':
                        #         myLog.error(f'ATENCION: Revisar el contenido del fichero {dictInputAscNameSinPath[nInputVar]}, fila de datos {nFila}; no debe tener texto: {valor1}')
                        #     continue
                        # aInputVals[nFila, nColumna, nInputVar] = np.float32(valor1)
                        # myLog.debug(f'valor1: {valor1} {type(valor1)} {float(valor1)}')

                        saltarFila = False
                        # dictValorVariables = {}
                        txtValorVariable = dictArrayLinea[nInputVar][nColumna]
                        if not txtValorVariable.replace('.', '', 1).replace('-', '', 1).isdigit():
                            if txtValorVariable != '\n' and txtValorVariable != '\r' and txtValorVariable != '':
                                myLog.error(f'ATENCION: Revisar el contenido del fichero {dictInputAscNameSinPath[nInputVar]}, fila de datos num {nFila}: no debe tener texto: {txtValorVariable}')
                            saltarFila = True
                            continue
                        valorVariableLeida = np.float32(txtValorVariable)
                        # dictValorVariables[nInputVar] = valorVariableLeida
                        # aInputVals[nFila, nColumna, nInputVar] = valorVariableLeida

                        # ==========================================================
                        # Fila y columna dentro del fichero asc: nFila, nColumna
                        # Coordenadas relativas del centro del pixel dentro del fichero asc:
                        if TRNShuso29:
                            coordXH29 = nMinX_HeaderAscH29 + (nColumna * nPixelX_Origen) + (nPixelX_Origen / 2)
                            coordYH29 = nMaxY_HeaderAscH29 + (nFila * nPixelY_Origen) + (nPixelY_Origen / 2)  # nPixelY_Origen es negativo
                            coordX, coordY, _ = ct_25829_to_25830.TransformPoint(coordXH29, coordYH29)
                            # Fila y columna dentro del raster generado:
                            if cargarRasterEnMemoria:
                                nColumnaRaster = int((coordX - (metrosPixelX_Destino/2) - nMinX_tif ) / metrosPixelX_Destino)
                                nFilaRaster = int((coordY - (metrosPixelY_Destino/2) - nMaxY_tif ) / metrosPixelY_Destino) #metrosPixelY_Destino es negativo
                            else:
                                nColumnaRaster = int((coordX - (metrosPixelX_Destino/2)) / metrosPixelX_Destino)
                                nFilaRaster = int((coordY - (metrosPixelY_Destino/2)) / metrosPixelY_Destino)
                        else:
                            coordX = nMinX_HeaderAsc + (nColumna * nPixelX_Origen) + (nPixelX_Origen / 2)
                            coordY = nMaxY_HeaderAsc + (nFila * nPixelY_Origen) + (nPixelY_Origen / 2)  # nPixelY_Origen es negativo
                            # Fila y columna dentro del raster generado:
                            if cargarRasterEnMemoria:
                                # nColumnaRaster = int(round((coordX - (metrosPixelX_Destino/2) - nMinX_tif ) / metrosPixelX_Destino, 0))
                                # nFilaRaster = int(round((coordY - (metrosPixelY_Destino/2) - nMaxY_tif ) / metrosPixelY_Destino, 0)) #metrosPixelY_Destino es negativo
                                nColumnaRaster = nColumna + nOffsetX
                                nFilaRaster = nFila + nOffsetY
                            else:
                                # nColumnaRaster = int(round((coordX - (metrosPixelX_Destino/2)) / metrosPixelX_Destino, 0))
                                # nFilaRaster = int(round((coordY - (metrosPixelY_Destino/2)) / metrosPixelY_Destino, 0))
                                nColumnaRaster = nColumna
                                nFilaRaster = nFila
    
                        if nFilaRaster < 0 or nColumnaRaster < 0:
                            myLog.critical('clidraster-> ATENCION: revisar transformacion de coordenadas.')
                            if TRNShuso29:
                                myLog.critical(f'{TB}-> coordXYH29: {coordXH29} {coordYH29}')
                            myLog.critical(f'{TB}-> coordXYH30: {coordX} {coordY}')
                            myLog.critical(f'{TB}-> nFilaRaster: {nFilaRaster} nColumnaRaster: {nColumnaRaster}')
                            sys.exit(0)
                        nMinColumnaAsc = min(nMinColumnaAsc, nColumnaRaster)
                        nMinFilaAsc = min(nMinFilaAsc, nFilaRaster)
                        nMaxColumnaAsc = max(nMaxColumnaAsc, nColumnaRaster)
                        nMaxFilaAsc = max(nMaxFilaAsc, nFilaRaster)
                        # ==========================================================
    
                        # ==========================================================
                        if nFilaRaster < arrayBanda1.shape[0] and nColumnaRaster < arrayBanda1.shape[1]:
                            try:
                                if integrarFicherosAsc:
                                    # Si el pixel no recibe ningun valor1 se queda con el PAR_noDataTiffProvi
                                    # Esto solo pasa cuando hay transformacion de coordenadas de H29 a H30
                                    # Los noData de las capas asc originales se dejan tal cual,
                                    # sin interpolar), con el valor1 PAR_noDataMergeTiff
                                    if valorVariableLeida == noDataValueThisVar:
                                        arrayBanda1[nFilaRaster, nColumnaRaster] = PAR_noDataMergeTiff
                                    else:
                                        if (ARGSdasoVar.lower()).startswith('alt'):
                                            if valorVariableLeida > 100:
                                                myLog.warning('\t-> Aviso: valor1 de altura excesivo: {}'.format(valorVariableLeida))
                                                if TRNShuso29:
                                                    myLog.warning('\t\t-> coordXYH29: {:9.2f}, {:10.2f}'.format(coordXH29, coordYH29))
                                                myLog.warning('\t\t-> coordXYH30: {:9.2f}, {:10.2f}'.format(coordX, coordY))
                                                myLog.warning('\t\t-> nFilaRaster: {}; nColumnaRaster: {}'.format(nFilaRaster, nColumnaRaster))
                                                valorVariableLeida = 100
                                            elif valorVariableLeida < 0:
                                                # Trunco los valores negativos a 0
                                                valorVariableLeida = 0
                                        # ======================================
                                        if (ARGSdasoVar.lower()).startswith('alt') and ARGSconvertirAltAdm8Bit:
                                            alturaEnCmTruncadaA254 = int(max(min(round(10 * valorVariableLeida, 0), 254), 0))
                                            arrayBanda1[nFilaRaster, nColumnaRaster] = alturaEnCmTruncadaA254
                                        elif (ARGSdasoVar.lower()).startswith('alt') and ARGSconvertirAltAcm16Bit:
                                            alturaEnCmTruncadaA5000 = int(max(min(round(100 * valorVariableLeida, 0), 5000), 0))
                                            arrayBanda1[nFilaRaster, nColumnaRaster] = alturaEnCmTruncadaA5000
                                        else:
                                            if PAR_outputNpDatatype == np.float16 or PAR_outputNpDatatype == np.float32 or PAR_outputNpDatatype == np.float64:
                                                arrayBanda1[nFilaRaster, nColumnaRaster] = valorVariableLeida
                                            else:
                                                arrayBanda1[nFilaRaster, nColumnaRaster] = int(valorVariableLeida)
                                        # ======================================
                                elif PAR_generarDasoLayers:
                                    # ==========================================
                                    if valorVariableLeida == noDataValueThisVar:
                                        dictArrayBandaX[outputNBand][nFilaRaster, nColumnaRaster] = PAR_noDataMergeTiff
                                    else:
                                        dictArrayBandaX[outputNBand][nFilaRaster, nColumnaRaster] = valorVariableLeida
                                    # ==========================================
                                    # Tipo de bosque del MFE
                                    if cartoRefMfe.usarVectorRef:
                                        # ======================================
                                        dictArrayBandaX[nBandasOutput - 1][nFilaRaster, nColumnaRaster] = arrayMFE[nFilaRaster, nColumnaRaster]
                                        # ======================================

                            except:
                                myLog.error('Error al integrar asc en tif-> shape: {} nFila: {} nFilaRaster: {} col: {} nColRaster: {} valor1: {}'.format(
                                    arrayBanda1.shape, nFila, nFilaRaster, nColumna, nColumnaRaster, valorVariableLeida
                                    )
                                )
                                # input('Pulsa una tecla..........')
                                sys.exit(0)
                            '''
                            if nFilaRaster < arrayBanda1.shape[0] and nColumnaRaster < arrayBanda1.shape[1]:
                              try:
                                arrayBanda1[nFilaRaster, nColumnaRaster] = valorVariableLeida
                              except:
                                myLog.error('Valores del fichero asc incorrectos: {valorVariableLeida}')
                            else:
                              myLog.debug('Coordenadas del punto fuera del raster generado (%s)' % (inputAscName1))
                              if nMinX_NombreAsc==nMinX_HeaderAsc and nMaxX_NombreAsc==nMaxX_HeaderAsc and nMinY_NombreAsc==nMinY_HeaderAsc and nMaxY_NombreAsc==nMaxY_HeaderAsc:
                                myLog.debug('Fichero asc de entrada - Rango de coordendas (x=%i-%i, y=%i-%i)' %\
                                      (nMinX_NombreAsc, nMaxX_NombreAsc, nMinY_NombreAsc, nMaxY_NombreAsc))
                              else:
                                myLog.debug('Fichero asc de entrada - Rango de coordendas segun el nombre   (x=%i-%i, y=%i-%i)' %\
                                      (nMinX_NombreAsc, nMaxX_NombreAsc, nMinY_NombreAsc, nMaxY_NombreAsc))
                                myLog.debug('Fichero asc de entrada - Rango de coordendas segun su cabecera (x=%i-%i, y=%i-%i)' %\
                                      (nMinX_HeaderAsc, nMaxX_HeaderAsc, nMinY_HeaderAsc, nMaxY_HeaderAsc))
                              myLog.debug('Fichero tif de salida  - Rango de coordendas (x=%i-%i, y=%i-%i)' %\
                                      (nMinX_tif, nMaxX_tif, nMinY_tif, nMaxY_tif))
                              myLog.debug('Fichero asc de entrada - Posicion de la celda: col=%i, raw=%i' % (nColumna, nFila))
                              myLog.debug('Fichero tif de salida  - Posicion de la celda: col=%i, raw=%i (dimensiones: col=%i row=%i)' %\
                                    (nColumnaRaster, nFilaRaster, arrayBanda1.shape[1], arrayBanda1.shape[0]))
                            '''
                    if saltarFila:
                        continue

            for nFilaRaster in range(dictArrayBandaX[1].shape[0]):
                for nColumnaRaster in range(dictArrayBandaX[1].shape[1]):
                    alt95 = dictArrayBandaX[1][nFilaRaster, nColumnaRaster]
                    fcc5m = dictArrayBandaX[2][nFilaRaster, nColumnaRaster]
                    fcc3m = dictArrayBandaX[3][nFilaRaster, nColumnaRaster]
                    fcmat = dictArrayBandaX[4][nFilaRaster, nColumnaRaster]
                    esp1MFE = dictArrayBandaX[nBandasOutput - 1][nFilaRaster, nColumnaRaster]
                    # Tipo de masa generado con todas las variables anteriores
                    nTipoMasa = asignaTipoMasa(esp1MFE, alt95, fcc5m, fcc3m, fcmat)
                    dictArrayBandaX[nBandasOutput][nFilaRaster, nColumnaRaster] = nTipoMasa
                    nMinTipoMasa = min(nMinTipoMasa, nTipoMasa)
                    nMaxTipoMasa = max(nMaxTipoMasa, nTipoMasa)

            if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                myLog.debug(f'{TB}{TV}-> Ok, datos leidos y guardados en el diccionario dictArrayBandaX con {len(dictArrayBandaX)} bandas.')

            if integrarFicherosAsc:
                arrayBandaN = arrayBanda1

            # ==================================================================
            if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                myLog.debug('\t-> clidraster-> Rellenando posibles huecos (interpolando):')
            # Relleno los posibles huecos puntuales que puedan quedar debido a la transformacion de coordenadas
            listaDesplXY = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1]]
            nPixelesAcumConValor = 0
            nPixelesAcumNoDataProvisional = 0
            nPixelesAcumInterpolados = 0
            for outputNBand in range(1, nBandasOutput + 1):
                nInputVar = outputNBand - 1
                if PAR_generarDasoLayers:
                    if not outputNBand in dictArrayBandaX.keys():
                        continue
                    arrayBandaN = dictArrayBandaX[outputNBand]
                    noDataValueAsc = noDataValuesPorTipoFichero[nInputVar]
                nPixelesConValor = 0
                nPixelesNoDataProvisional = 0
                nPixelesInterpolados = 0
                for nFilaRaster in range(nMinFilaAsc, nMaxFilaAsc + 1):
                    for nColumnaRaster in range(nMinColumnaAsc, nMaxColumnaAsc + 1):
                        if nFilaRaster < arrayBandaN.shape[0] and nColumnaRaster < arrayBandaN.shape[1]:
                            if arrayBandaN[nFilaRaster, nColumnaRaster] == PAR_noDataTiffProvi:
                                nPixelesNoDataProvisional += 1
                                numPixelesVecinos = 0
                                valorPixelesVecinos = 0
                                for desplXY in listaDesplXY:
                                    newFilaRaster = nFilaRaster + desplXY[0]
                                    newColumnaRaster = nColumnaRaster + desplXY[1]
                                    if (
                                        newFilaRaster >= 0
                                        and newFilaRaster < arrayBandaN.shape[0]
                                        and newColumnaRaster >= 0
                                        and newColumnaRaster < arrayBandaN.shape[1]
                                    ):
                                        if (
                                            arrayBandaN[newFilaRaster, newColumnaRaster] != noDataValueAsc
                                            and arrayBandaN[newFilaRaster, newColumnaRaster] != PAR_noDataTiffProvi
                                            and arrayBandaN[newFilaRaster, newColumnaRaster] != PAR_noDataMergeTiff
                                        ):
                                            numPixelesVecinos += 1
                                            valorPixelesVecinos += arrayBandaN[newFilaRaster, newColumnaRaster]
                                if numPixelesVecinos > 0:
                                    nPixelesInterpolados += 1
                                    valorMedioPixelesVecinos = valorPixelesVecinos / numPixelesVecinos
                                    if (ARGSdasoVar.lower()).startswith('alt') and ARGSconvertirAltAdm8Bit:
                                        valorMedioPixelesVecinos = int(max(min(round(valorMedioPixelesVecinos, 0), 254), 0))
                                    elif (ARGSdasoVar.lower()).startswith('alt') and ARGSconvertirAltAcm16Bit:
                                        valorMedioPixelesVecinos = int(max(min(round(valorMedioPixelesVecinos, 0), 5000), 0))
                                    if PAR_generarDasoLayers:
                                        dictArrayBandaX[outputNBand][nFilaRaster, nColumnaRaster] = valorMedioPixelesVecinos
                                    else:
                                        arrayBanda1[nFilaRaster, nColumnaRaster] = valorMedioPixelesVecinos
                                else:
                                    # Si no soy capaz de interpolarlo, lo pongo como noData
                                    if PAR_generarDasoLayers:
                                        dictArrayBandaX[outputNBand][nFilaRaster, nColumnaRaster] = PAR_noDataMergeTiff
                                    else:
                                        arrayBanda1[nFilaRaster, nColumnaRaster] = PAR_noDataMergeTiff
                            else:
                                nPixelesConValor += 1
                nPixelesAcumConValor += nPixelesConValor
                nPixelesAcumNoDataProvisional += nPixelesNoDataProvisional
                nPixelesAcumInterpolados += nPixelesInterpolados

                if mostrarNumFicheros == 0 or contadorInFiles < mostrarNumFicheros:
                    myLog.debug(f'{TB}{TV}{TV}-> outputNBand: {outputNBand}')
                    myLog.debug(
                        f'{TB}{TV}{TV}-> Num de pixeles recorridos para rellenar huecos: '
                        f'{nMaxFilaAsc - nMinFilaAsc + 1} x {nMaxColumnaAsc - nMinColumnaAsc + 1} '
                        f'= {(nMaxFilaAsc - nMinFilaAsc + 1) * (nMaxColumnaAsc - nMinColumnaAsc + 1)}'
                    )
                    myLog.debug(
                        f'{TB}{TV}{TV}-> Numero de pixeles con/sin valor asignado '
                        f'-> conValor: {nPixelesConValor} (acum: {nPixelesAcumConValor}); '
                        f'sinValor: {nPixelesNoDataProvisional} (acum: {nPixelesAcumNoDataProvisional})'
                    )
                    myLog.debug(
                        f'{TB}{TV}{TV}-> Numero de pixeles sin valor asignado     '
                        f'-> interpolados: {nPixelesInterpolados} (acum: {nPixelesAcumInterpolados}); '
                        f'sin interpolar: {nPixelesNoDataProvisional - nPixelesInterpolados}'
                    )

            rangoX_H30 = (nMaxX_HeaderAsc - nMinX_HeaderAsc)
            # ==================================================================

            # ==================================================================
            # Si no cargo todo el outputBand____1 en memoria, escribo el contenido
            # del arrayBanda1 especifico del fichero que proceso en el outputBand____1
            # Si he cargado todo outputBand____1 en memoria, esto lo hago todo a la vez al final
            if not cargarRasterEnMemoria:
                if PAR_generarDasoLayers:
                    for outputNBand in range(1, nBandasOutput + 1):
                        if PAR_generarDasoLayers:
                            if not outputNBand in dictArrayBandaX.keys():
                                continue
                        myLog.debug('\nAsigno valores de %s al raster (not cargarRasterEnMemoria)...' % (inputAscName1),)
                        # nFilas = dictArrayBandaX[outputNBand].shape[0]
                        # nColumnas = dictArrayBandaX[outputNBand].shape[1]
                        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                        for nFila in range(dictArrayBandaX[outputNBand].shape[0]):
                            nxarray = dictArrayBandaX[outputNBand][nFila, :]
                            nxarray.shape = (1, -1)
                            dictOutputBandX[outputNBand].WriteArray(nxarray, nOffsetX, nOffsetY + nFila)
                        dictOutputBandX[outputNBand].FlushCache()
                        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                else:
                    myLog.debug('\nAsigno valores de %s al raster (not cargarRasterEnMemoria)...' % (inputAscName1),)
                    if PAR_ambitoTiffNuevo == 'rasterDest_CyL':
                        # nFilas = outputBandCyL1.shape[0]
                        # nColumnas = outputBandCyL1.shape[1]
                        # for nFila in range(outputBandCyL1.shape[0]):
                        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                        for nFila in range(arrayBanda1.shape[0]):
                            # EN este caso el bucle solo ocurre una vez
                            nxarray = outputBandCyL1[nFila, :]
                            nxarray.shape = (1, -1)
                            outputBandCyL1.WriteArray(nxarray, nOffsetX, nOffsetY + nFila)
                        outputBandCyL1.FlushCache()
                        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    else:
                        # nFilas = outputBandLote1.shape[0]
                        # nColumnas = outputBandLote1.shape[1]
                        # for nFila in range(outputBandLote1.shape[0]):
                        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                        for nFila in range(arrayBanda1.shape[0]):
                            # EN este caso el bucle solo ocurre una vez
                            nxarray = outputBandLote1[nFila, :]
                            nxarray.shape = (1, -1)
                            outputBandLote1.WriteArray(nxarray, nOffsetX, nOffsetY + nFila)
                        outputBandLote1.FlushCache()
                        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                myLog.debug('ok WriteArray')
            tiempo1 = time.time()
            myLog.debug(f'{TB}-> Tiempo para procesar y guardar en tif el bloque: {(tiempo1 - tiempo0):0.1f} segundos')

        timeFin = time.asctime(time.localtime(time.time()))
        myLog.info(f'{TB}-> Fin procesado bloques: {timeFin}')

        # ======================================================================
        if PAR_verbose == 3:
            for nInputVar in range(PAR_nInputVars):
                nBanda = nInputVar + 1
                if not nBanda in dictArrayBandaX.keys():
                    myLog.debug(f'{TB}{TV}{TV}-> No se puede mostrar fragmento de banda {nBanda}.')
                    continue
                myLog.debug(f'{TB}{TV}{TV}-> Muestra de fragmento de banda {nBanda} ({self_LOCLlistaDasoVarsFileTypes[nInputVar]}) de shape {dictArrayBandaX[1].shape}:')
                if dictArrayBandaX[nBanda].shape[0] > 25 and dictArrayBandaX[nBanda].shape[1] > 20:
                    myLog.debug(f'[20:25, 10:20]-> {dictArrayBandaX[nBanda][20:25, 10:20]}')
                if dictArrayBandaX[nBanda].shape[0] > 25 and dictArrayBandaX[nBanda].shape[1] > 220:
                    myLog.debug(f'[20:25, 210:220]-> {dictArrayBandaX[nBanda][20:25, 210:220]}')
                if dictArrayBandaX[nBanda].shape[0] > 25 and dictArrayBandaX[nBanda].shape[1] > 2320:
                    myLog.debug(f'[20:25, 2310:2320]-> {dictArrayBandaX[nBanda][20:25, 2310:2320]}')
        # ======================================================================

        # ======================================================================
        if contadorFicherosIntegrando == 0:
            myLog.warning('Ningun fichero asc cumplia condiciones; raster generado sin contenido')
        elif cargarRasterEnMemoria:
            myLog.debug('\n{:_^80}'.format(''))
            myLog.debug(f'clidraster-> Repasando si quedan valores PAR_noDataTiffProvi ({PAR_noDataTiffProvi}) y pasandolos a PAR_noDataMergeTiff ({PAR_noDataMergeTiff})')

            if PAR_generarDasoLayers:
                for outputNBand in range(1, nBandasOutput + 1):
                    nInputVar = outputNBand - 1
                    if PAR_generarDasoLayers:
                        if not outputNBand in dictArrayBandaX.keys():
                            continue

                    nPixelesNoDataProvisional = np.count_nonzero(dictArrayBandaX[outputNBand] == PAR_noDataTiffProvi)
                    nPixelesConValorNoData = np.count_nonzero(dictArrayBandaX[outputNBand] == PAR_noDataMergeTiff)
                    nPixelesConValorSiData = np.ma.count(dictArrayBandaX[outputNBand]) - nPixelesNoDataProvisional - nPixelesConValorNoData
                    dictArrayBandaX[outputNBand][dictArrayBandaX[outputNBand] == PAR_noDataTiffProvi] = PAR_noDataMergeTiff
                    noDataValueAsc = noDataValuesPorTipoFichero[nInputVar]
                    dictArrayBandaX[outputNBand][dictArrayBandaX[outputNBand] == noDataValueAsc] = PAR_noDataMergeTiff
                    # nPixelesNoDataProvisional = 0
                    # nPixelesConValorNoData = 0
                    # nPixelesConValorSiData = 0
                    # for nFilaRaster in range(dictArrayBandaX[outputNBand].shape[0]):
                    #     for nColumnaRaster in range(dictArrayBandaX[outputNBand].shape[1]):
                    #         if dictArrayBandaX[outputNBand][nFilaRaster, nColumnaRaster] == PAR_noDataTiffProvi:
                    #             nPixelesNoDataProvisional += 1
                    #             dictArrayBandaX[outputNBand][nFilaRaster, nColumnaRaster] = PAR_noDataMergeTiff
                    #         elif dictArrayBandaX[outputNBand][nFilaRaster, nColumnaRaster] == PAR_noDataMergeTiff:
                    #             nPixelesConValorNoData += 1
                    #         else:
                    #             nPixelesConValorSiData += 1
                    myLog.debug('\t-> Banda {}:'.format(outputNBand))
                    myLog.debug('\t\t-> nPixelesNoDataProvisional:{}'.format(nPixelesNoDataProvisional))
                    myLog.debug('\t\t-> nPixelesConValorNoData:   {}'.format(nPixelesConValorNoData))
                    myLog.debug('\t\t-> nPixelesConValorSiData:   {}'.format(nPixelesConValorSiData))
            else:
                nPixelesNoDataProvisional = np.count_nonzero(arrayBanda1 == PAR_noDataTiffProvi)
                nPixelesConValorNoData = np.count_nonzero(arrayBanda1 == PAR_noDataMergeTiff)
                nPixelesConValorSiData = np.ma.count(arrayBanda1) - nPixelesNoDataProvisional - nPixelesConValorNoData
                arrayBanda1[arrayBanda1 == PAR_noDataTiffProvi] = PAR_noDataMergeTiff
                # nPixelesNoDataProvisional = 0
                # nPixelesConValorNoData = 0
                # nPixelesConValorSiData = 0
                # for nFilaRaster in range(arrayBanda1.shape[0]):
                #     for nColumnaRaster in range(arrayBanda1.shape[1]):
                #         if arrayBanda1[nFilaRaster, nColumnaRaster] == PAR_noDataTiffProvi:
                #             nPixelesNoDataProvisional += 1
                #             arrayBanda1[nFilaRaster, nColumnaRaster] = PAR_noDataMergeTiff
                #         elif arrayBanda1[nFilaRaster, nColumnaRaster] == PAR_noDataMergeTiff:
                #             nPixelesConValorNoData += 1
                #         else:
                #             nPixelesConValorSiData += 1
                myLog.debug('\t-> Banda {}:'.format(1))
                myLog.debug('\t\t-> nPixelesNoDataProvisional:{}'.format(nPixelesNoDataProvisional))
                myLog.debug('\t\t-> nPixelesConValorNoData:   {}'.format(nPixelesConValorNoData))
                myLog.debug('\t\t-> nPixelesConValorSiData:   {}'.format(nPixelesConValorSiData))
            if PAR_verbose > 1:
                myLog.debug('{:=^80}'.format(''))

            # Escritura en el raster creado:
            myLog.debug('\n{:_^80}'.format(''))
            myLog.debug('clidraster-> Asignando valores del array al raster...')
            if PAR_generarDasoLayers:
                for outputNBand in range(1, nBandasOutput + 1):
                    nInputVar = outputNBand - 1
                    if not outputNBand in dictArrayBandaX.keys():
                        continue
                    # Opcion 1: todo de una vez:
                    # dst_band1.WriteArray(dictArrayBandaX[outputNBand],0,0)
                    # Opcion 2: por filas (si tengo limitacion de memoria):
                    loteDeFilas = 1  # i.e. the number of rows to write with each iteration
                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    for j in range(dictArrayBandaX[outputNBand].shape[0]):
                        nxarray = dictArrayBandaX[outputNBand][j, :]
                        # if j >= 50 and j <= 60 :
                        #  nxarray = np.ones(dictArrayBandaX[outputNBand].shape[0]) * 255
                        # nxarray=nxarray[::-1]
                        nxarray.shape = (1, -1)
                        dictOutputBandX[outputNBand].WriteArray(nxarray, 0, loteDeFilas * j)
                    dictOutputBandX[outputNBand].FlushCache()
                    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

                    if (dictArrayBandaX[nBandasOutput - 1]).all() == PAR_noDataMergeTiff:
                        myLog.error('\nclidraster-> ATENCION: no hay cobertura de MFE en la zona analizada (b):')
                        myLog.error(
                            '\t-> Rango de coordenadas UTM de la zona analizada: X: {:0.2f} - {:0.2f}; Y: {:0.2f} - {:0.2f}'.format(
                                nMinX_tif, nMaxX_tif, nMinY_tif, nMaxY_tif,
                            )
                        )
                        myLog.error(
                            '\t-> Rango de coordenadas UTM cubiertas por el MFE: X: {:0.2f} - {:0.2f}; Y: {:0.2f} - {:0.2f}'.format(
                                cartoRefMfe.inputVectorXmin,
                                cartoRefMfe.inputVectorXmax,
                                cartoRefMfe.inputVectorYmin,
                                cartoRefMfe.inputVectorYmax,
                            )
                        )
                        myLog.error(
                            '\t-> Fichero MFE: {}/{}'.format(
                                PAR_cartoMFEpathName,
                                PAR_cartoMFEfileName,
                            )
                        )
                        # myLog.error(f'{nFilaRaster} {nColumnaRaster} dictArrayBandaX[MFE]: {dictArrayBandaX[nBandasOutput - 1]}')
                        sys.exit(0)

                    arrayMinVariables[nBandasOutput - 2] = (dictArrayBandaX[nBandasOutput - 1][dictArrayBandaX[nBandasOutput - 1] != PAR_noDataMergeTiff]).max()
                    arrayMinVariables[nBandasOutput - 1] = (dictArrayBandaX[nBandasOutput][dictArrayBandaX[nBandasOutput] != PAR_noDataMergeTiff]).min()
                    if nInputVar < len(self_LOCLlistaDasoVarsFileTypes):
                        if nInputVar < len(arrayMinVariables) and nInputVar < len(arrayMaxVariables):
                            myLog.info(
                                f'{TB}-> ok banda {outputNBand} escrita '
                                f'(variable {nInputVar}: {self_LOCLlistaDasoVarsFileTypes[nInputVar]}; '
                                'Rango: {:0.1f} -> {:0.1f})'.format(arrayMinVariables[nInputVar], arrayMaxVariables[nInputVar])
                            )
                        else:
                            myLog.info(
                                f'{TB}-> ok banda {outputNBand} escrita '
                                f'(variable {nInputVar}: {self_LOCLlistaDasoVarsFileTypes[nInputVar]}; Rango: sin datos.'
                            )

            else:
                # Opcion 1: todo de una vez:
                # dst_band1.WriteArray(arrayBanda1,0,0)
                # Opcion 2: por filas (si tengo limitacion de memoria):
                loteDeFilas = 1  # i.e. the number of rows to write with each iteration
                for j in range(arrayBanda1.shape[0]):
                    nxarray = arrayBanda1[j, :]
                    # if j >= 50 and j <= 60 :
                    #  nxarray = np.ones(arrayBanda1.shape[0]) * 255
                    # nxarray=nxarray[::-1]
                    nxarray.shape = (1, -1)
                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    if PAR_ambitoTiffNuevo == 'rasterDest_CyL':
                        outputBandCyL1.WriteArray(nxarray, 0, loteDeFilas * j)
                    else:
                        outputBandLote1.WriteArray(nxarray, 0, loteDeFilas * j)
                if PAR_ambitoTiffNuevo == 'rasterDest_CyL':
                    outputBandCyL1.FlushCache()
                else:
                    outputBandLote1.FlushCache()
                # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                myLog.info('ok banda escrita.')
            myLog.info('{:=^80}'.format(''))

        # myLog.debug('\nInfo sobre el raster destino (generadoo actualizado):')
        # infoSrcband(outputBandLote1)
        myLog.info('\n{:_^80}'.format(''))
        PAR_nInputVarsOk = 0
        for nInputVar in range(PAR_nInputVars):
            if nInputVar in dictAscFileObjet.keys():
                PAR_nInputVarsOk += 1
        myLog.info('clidraster-> Resumen de bloques y variables leidos para crear el raster con crearTiff<>:')
        myLog.info(f'{TB}-> Se han leido {contadorFicherosIntegrando} bloques de {len(dictAscFileObjet)} tipos de fichero.')
        myLog.info(f'{TB}-> Tipos de fichero localizados: {PAR_nInputVarsOk} de {PAR_nInputVars}')
        # myLog.info(f'{TB}-> Raster creado: {self_LOCLoutPathNameRuta}/{self_LOCLoutFileNameWExtLote}')
        myLog.info(f'{TB}-> Raster creado: {self_LOCLoutPathNameRuta}/{self_LOCLoutFileNameWExt}')
        myLog.info('{:=^80}'.format(''))

        # if PAR_generarDasoLayers and nBandasOutput >= 2:
        #     outputBand2 = outputDataset.GetRasterBand(2)
        #     arrayBanda2 = outputBand2.ReadAsArray().astype(PAR_outputNpDatatype)
        #     for nFilaRaster in range(nMinFilaAsc, nMaxFilaAsc):
        #         for nColumnaRaster in range(nMinColumnaAsc, nMaxColumnaAsc):
        #             if nFilaRaster < arrayBanda2.shape[0] and nColumnaRaster < arrayBanda2.shape[1]:
        #                 # Este es el valor previo del array a traer el valor del raster
        #                 # if (
        #                 #     arrayBanda2[nFilaRaster, nColumnaRaster] == PAR_noDataMergeTiff
        #                 #     and LCL_convertirAlt
        #                 # ) or (
        #                 #     arrayBanda2[nFilaRaster, nColumnaRaster] == PAR_noDataTiffProvi
        #                 #     and not LCL_convertirAlt
        #                 # ):
        #                 if arrayBanda2[nFilaRaster, nColumnaRaster] == PAR_noDataTiffProvi:
        #                     pass

        outputDatasetLote = None
        del outputDatasetLote
        outputDatasetCyL = None
        del outputDatasetCyL
        outputDatasetIndi = None
        del outputDatasetIndi

        if not PAR_generarDasoLayers:
            myLog.debug('\nok AUX_subLoteTiff: {}'.format(miSubLoteTiff))

    return (
        noDataDasoVarAll,
        PAR_outputGdalDatatype,
        PAR_outputNpDatatype,
        nCeldasX_Destino,
        nCeldasY_Destino,
        metrosPixelX_Destino,
        metrosPixelY_Destino,
        nMinX_tif,
        nMaxY_tif,
        nFicherosDisponiblesPorTipoVariable,
        arrayMinVariables,
        arrayMaxVariables,
        nMinTipoMasa,
        nMaxTipoMasa,
    )


# ==============================================================================
def leerMFE(
    myLasHead,
    myLasData,
    fileCoordYear,
    xSupIzda,
    ySupIzda,
    nCeldasX,
    nCeldasY,
    LOCLmetrosCelda,
    miOutputDir,
    PAR_cartoMFEpathName=None,
    PAR_cartoMFEfileName=None,
    PAR_cartoMFEfileSoloExt=None,
    PAR_cartoMFEfileNSinExt=None,
    PAR_cartoMFEcampoSp=None,
    PAR_cartoMFErecorte=None,
    PAR_verbose=False,
    LOCLhusoUTM=30,
):
    tiempo0 = time.time()

    myLog.info('\n{:_^80}'.format(''))
    myLog.info('clidraster-> Se va a leer y recortar el MFE')

    if PAR_cartoMFEfileSoloExt.lower() == '.shp':
        LOCLinputVectorDriverNameMFE = 'ESRI Shapefile'
    elif PAR_cartoMFEfileSoloExt.lower() == '.gpkg':
        # Ver mas en https://gdal.org/drivers/vector/gpkg.html
        # Ver tb https://gdal.org/drivers/raster/gpkg.html#raster-gpkg
        LOCLinputVectorDriverNameMFE = 'GPKG'
    else:
        LOCLinputVectorDriverNameMFE = ''
        myLog.error(f'clidraster-> No se ha identificado bien el driver de esta extension: {PAR_cartoMFEfileSoloExt} (fichero: {PAR_cartoMFEpathName})')
        sys.exit(0)

    miRutaCartoRecortes = miOutputDir
    
    subDirCapaInputVector = ''

    myLog.debug('Buscando capa MFE para generar un raster con:')
    myLog.debug(f'{TB}{TV}-> xSupIzda:       {xSupIzda:10.2f}')
    myLog.debug(f'{TB}{TV}-> myLasHead.xmin: {myLasHead.xmin:10.2f}')
    myLog.debug(f'{TB}{TV}-> sHead.xSupIzda: {myLasHead.xSupIzda:10.2f}')
    myLog.debug(f'{TB}{TV}-> ySupIzda:       {ySupIzda:10.2f}')
    myLog.debug(f'{TB}{TV}-> myLasHead.ymax: {myLasHead.ymax:10.2f}')
    myLog.debug(f'{TB}{TV}-> sHead.ySupIzda: {myLasHead.ySupIzda:10.2f}')
    myLog.debug(f'{TB}{TV}-> nCeldasX:       {nCeldasX}')
    myLog.debug(f'{TB}{TV}-> nCeldasY:       {nCeldasY}')

    cartoRefUsoSingular = clidcarto.CartoRefVector(
        myLasHead,
        myLasData,
        miRutaCartoRecortes,
        PAR_cartoMFEpathName,
        LOCLinputVectorDriverNameMFE,
        PAR_cartoMFEcampoSp,
        subDirCapaInputVector,
        PAR_cartoMFEfileNSinExt,
        PAR_cartoMFErecorte,
        tipoInfoRaster='UsosSingulares',
        LCLhusoUTM=LOCLhusoUTM,
        LCLverbose=PAR_verbose,
    )
    cartoRefUsoSingular.leerVector()
    # ==============================================================
    if cartoRefUsoSingular.usarVectorRef:
        # ==========================================================
        vectorRecortadoOk = cartoRefUsoSingular.recortarVector(forzarRecorteCuadrado=False)
        if vectorRecortadoOk:
            # ==========================================================
            rasterCreadoOk = cartoRefUsoSingular.rasterizarVectorRecortado()
            if rasterCreadoOk:
                rasterLeidoOk = cartoRefUsoSingular.leerElRasterYaRecortado()
                cartoRefUsoSingular.usarVectorRef = 1 * rasterLeidoOk
                if rasterLeidoOk:
                    myLog.info(
                        'clidraster-> CartoRef de uso/cobertura: capa recortada ok & recorte leido ok: {}'.format(
                            rasterLeidoOk
                        )
                    )
                else:
                    cartoRefUsoSingular.usarVectorRef = 0
            else:
                cartoRefUsoSingular.usarVectorRef = 0
        else:
            cartoRefUsoSingular.usarVectorRef = 0
    else:
        myLog.warning(
            'clidraster-> Avido: no se usa cartoRef MFE-> usarVectorRef: {}'.format(
                cartoRefUsoSingular.usarVectorRef
            )
        )
    myLog.debug(
        'clidraster-> Asignar celdas con uso singular (cartoRef)?-> usarVectorRef: {}'.format(
            cartoRefUsoSingular.usarVectorRef
        )
    )

    if cartoRefUsoSingular.usarVectorRef:
        cartoRefUsoSingular.asignarUsoSingularArrayCeldas()
    else:
        myLog.warning(
            '\nclidraster-> Aviso: revisar la causa por la que no es posible usar la capa singularUse {}.[shp/gpkg]'.format(
                PAR_cartoMFEfileNSinExt
            )
        )
        cartoRefUsoSingular.inputVectorXmax = 0
        cartoRefUsoSingular.inputVectorXmin = 0
        cartoRefUsoSingular.inputVectorYmax = 0
        cartoRefUsoSingular.inputVectorYmin = 0
        cartoRefUsoSingular.miRasterRefMinXY = np.array([0, 0], dtype=np.float32)
        cartoRefUsoSingular.miRasterRefOrigen = np.array([0, 0], dtype=np.float32)
        cartoRefUsoSingular.miRasterRefPixel = np.array([0, 0], dtype=np.float32)
        cartoRefUsoSingular.miRasterRefNumCeldas = np.array([0, 0], dtype=np.int32)
        cartoRefUsoSingular.miRasterRefCoordenadas = np.array([0, 0, 0, 0], dtype=np.float32)
        cartoRefUsoSingular.aCeldasLandUseCover = np.zeros(1, dtype=np.uint8).reshape(1, 1)
    # Con esto obtengo:
    #     cartoRefUsoSingular.usarRasterRef
    #     cartoRefUsoSingular.aCeldasVectorRecRasterizado
    #     cartoRefUsoSingular.aCeldasLandUseCover
    # Otras variables auxiliares de cartoRefUsoSingular:
    #     miRasterRefMinXY = [vectorRefMinX, vectorRefMinY]
    #     miRasterRefOrigen = [vectorRefOrigenX, vectorRefOrigenY]
    #     miRasterRefPixel = [vectorRefPixelX, vectorRefPixelY]
    #     miRasterRefNumCeldas = [vectorRefNumCeldasX, vectorRefNumCeldasY]
    #     miRasterRefCoordenadas = [vectorRefMinX, vectorRefMaxX, vectorRefMinY, vectorRefMaxY]
    # Nota: miRasterRefCoordenadas incluye miRasterRefMinXY (esta ultima sobra)
    tiempo1 = time.time()
    myLog.info(
        'clidraster-> Tiempo para leer capa vector singularUse y asignarUsoSingularArrayCeldas: {:0.1f} segundos'.format(
            (tiempo1 - tiempo0)
        )
    )
    if cartoRefUsoSingular.usarVectorRef:
        myLog.info('clidraster-> Capa MFE leida ok')
    else:
        myLog.warning('clidraster-> AVISO: tipo de bosque no disponible (ver causa mas arriba)')
    myLog.info('{:=^80}'.format(''))

    return cartoRefUsoSingular


# ==============================================================================
# Esta funcion esta pendiente de implementar
def asignaTipoMasa(aCeldasLandUseCover, alt95, fcc5m, fcc3m, fcmat):

    if alt95 < 0.25:
        nTipoMasa = 0
    if alt95 < 1.5:
        nTipoMasa = 1
    elif alt95 < 3:
        nTipoMasa = 2
    elif alt95 < 5:
        nTipoMasa = 3
    elif alt95 < 10:
        nTipoMasa = 4
    elif alt95 < 15:
        nTipoMasa = 5
    elif alt95 < 20:
        nTipoMasa = 6
    else:
        nTipoMasa = 7

    if fcc5m < 10:
        pass
    elif fcc5m < 50:
        nTipoMasa += 8
    elif fcc5m < 70:
        nTipoMasa += 16
    else:
        nTipoMasa += 32
    return nTipoMasa


# Ver cookbook en:
#     https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
# ==============================================================================
def CrearOutputRaster(
    self_LOCLoutPathNameRuta,
    self_LOCLoutFileNameWExt,
    nMinX_tif,
    nMaxY_tif,
    nCeldasX_Destino,
    nCeldasY_Destino,
    metrosPixelX_Destino,
    metrosPixelY_Destino,
    PAR_outRasterDriver,
    PAR_outputOptions,
    nBandasOutput,
    PAR_outputGdalDatatype,
    PAR_outputNpDatatype,
    noDataValueDasoVarAsc,
    PAR_noDataTiffProvi,
    PAR_noDataMergeTiff,
    LCL_convertirAlt=False,
    PAR_generarDasoLayers=False,
    generarMetaPixeles=False,
    LCL_verbose=False,
):

    '''
    Pixel data types
    GDT_Unknown  Unknown or unspecified type
    GDT_Byte     Eight bit unsigned integer
    GDT_UInt16   Sixteen bit unsigned integer
    GDT_Int16    Sixteen bit signed integer
    GDT_UInt32   Thirty two bit unsigned integer
    GDT_Int32    Thirty two bit signed integer
    GDT_Float32  Thirty two bit floating point
    GDT_Float64  Sixty four bit floating point
    GDT_CInt16   Complex Int16
    GDT_CInt32   Complex Int32
    GDT_CFloat32 Complex Float32
    GDT_CFloat64 Complex Float64
    '''
    driver = gdal.GetDriverByName(PAR_outRasterDriver)

    #   metadata = driver.GetMetadata()
    #   myLog.debug(metadata.keys())
    #   for clave in metadata.keys():
    #     myLog.debug(f'{clave} {metadata[clave]}')
    #   #Algunas de interes:
    #   #DMD_CREATIONDATATYPES Byte UInt16 Int16 UInt32 Int32 Float32 Float64 CInt16 CInt32 CFloat32 CFloat64
    #   #DMD_CREATIONOPTIONLIST (para verlo bien sustituyo "> " por ">\n " (aqui o en notepad++)
    #   '''
    #   <CreationOptionList>
    #      <Option name='COMPRESS' type='string-select'>
    #          <Value>NONE</Value>
    #          <Value>LZW</Value>
    #          <Value>PACKBITS</Value>
    #          <Value>JPEG</Value>
    #          <Value>CCITTRLE</Value>
    #          <Value>CCITTFAX3</Value>
    #          <Value>CCITTFAX4</Value>
    #          <Value>DEFLATE</Value>
    #      </Option>
    #      <Option name='PREDICTOR' type='int' description='Predictor Type'/>
    #      <Option name='JPEG_QUALITY' type='int' description='JPEG quality 1-100' default='75'/>
    #      <Option name='ZLEVEL' type='int' description='DEFLATE compression level 1-9' default='6'/>
    #      <Option name='NBITS' type='int' description='BITS for sub-byte files (1-7), sub-uint16 (9-15), sub-uint32 (17-31)'/>
    #      <Option name='INTERLEAVE' type='string-select' default='PIXEL'>
    #          <Value>BAND</Value>
    #          <Value>PIXEL</Value>
    #      </Option>
    #      <Option name='TILED' type='boolean' description='Switch to tiled format'/>
    #      <Option name='TFW' type='boolean' description='Write out world file'/>
    #      <Option name='RPB' type='boolean' description='Write out .RPB (RPC) file'/>
    #      <Option name='BLOCKXSIZE' type='int' description='Tile Width'/>
    #      <Option name='BLOCKYSIZE' type='int' description='Tile/Strip Height'/>
    #      <Option name='PHOTOMETRIC' type='string-select'>
    #          <Value>MINISBLACK</Value>
    #          <Value>MINISWHITE</Value>
    #          <Value>PALETTE</Value>
    #          <Value>RGB</Value>
    #          <Value>CMYK</Value>
    #          <Value>YCBCR</Value>
    #          <Value>CIELAB</Value>
    #          <Value>ICCLAB</Value>
    #          <Value>ITULAB</Value>
    #      </Option>
    #      <Option name='SPARSE_OK' type='boolean' description='Can newly created files have missing blocks?' default='FALSE'/>
    #      <Option name='ALPHA' type='string-select' description='Mark first extrasample as being alpha'>
    #          <Value>NON-PREMULTIPLIED</Value>
    #          <Value>PREMULTIPLIED</Value>
    #          <Value>UNSPECIFIED</Value>
    #          <Value aliasOf='NON-PREMULTIPLIED'>YES</Value>
    #          <Value aliasOf='UNSPECIFIED'>NO</Value>
    #      </Option>
    #      <Option name='PROFILE' type='string-select' default='GDALGeoTIFF'>
    #          <Value>GDALGeoTIFF</Value>
    #          <Value>GeoTIFF</Value>
    #          <Value>BASELINE</Value>
    #      </Option>
    #      <Option name='PIXELTYPE' type='string-select'>
    #          <Value>DEFAULT</Value>
    #          <Value>SIGNEDBYTE</Value>
    #      </Option>
    #      <Option name='BIGTIFF' type='string-select' description='Force creation of BigTIFF file'>
    #        <Value>YES</Value>
    #        <Value>NO</Value>
    #        <Value>IF_NEEDED</Value>
    #        <Value>IF_SAFER</Value>
    #      </Option>
    #      <Option name='ENDIANNESS' type='string-select' default='NATIVE' description='Force endianness of created file. For DEBUG purpose mostly'>
    #          <Value>NATIVE</Value>
    #          <Value>INVERTED</Value>
    #          <Value>LITTLE</Value>
    #          <Value>BIG</Value>
    #      </Option>
    #      <Option name='COPY_SRC_OVERVIEWS' type='boolean' default='NO' description='Force copy of overviews of source dataset (CreateCopy())'/>
    #      <Option name='SOURCE_ICC_PROFILE' type='string' description='ICC profile'/>
    #      <Option name='SOURCE_PRIMARIES_RED' type='string' description='x,y,1.0 (xyY) red chromaticity'/>
    #      <Option name='SOURCE_PRIMARIES_GREEN' type='string' description='x,y,1.0 (xyY) green chromaticity'/>
    #      <Option name='SOURCE_PRIMARIES_BLUE' type='string' description='x,y,1.0 (xyY) blue chromaticity'/>
    #      <Option name='SOURCE_WHITEPOINT' type='string' description='x,y,1.0 (xyY) whitepoint'/>
    #      <Option name='TIFFTAG_TRANSFERFUNCTION_RED' type='string' description='Transfer function for red'/>
    #      <Option name='TIFFTAG_TRANSFERFUNCTION_GREEN' type='string' description='Transfer function for green'/>
    #      <Option name='TIFFTAG_TRANSFERFUNCTION_BLUE' type='string' description='Transfer function for blue'/>
    #      <Option name='TIFFTAG_TRANSFERRANGE_BLACK' type='string' description='Transfer range for black'/>
    #      <Option name='TIFFTAG_TRANSFERRANGE_WHITE' type='string' description='Transfer range for white'/>
    #   </CreationOptionList>
    #   '''
    #   print
    #   if metadata.has_key(gdal.DCAP_CREATE) \
    #      and metadata[gdal.DCAP_CREATE] == 'YES':
    #       myLog.debug('Driver %s supports Create() method.' % PAR_outRasterDriver)
    #   if metadata.has_key(gdal.DCAP_CREATECOPY) \
    #      and metadata[gdal.DCAP_CREATECOPY] == 'YES':
    #       myLog.debug('Driver %s supports CreateCopy() method.' % PAR_outRasterDriver)
    #   input('$$$$$')

    miOutputFileNameConPath = os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExt)

    # myLog.debug('{:_^80}'.format(''))
    if generarMetaPixeles:
        myLog.debug('clidraster-> Creando nuevo raster con metaPixeles para el tipo de masa seleccionado:')
    else:
        myLog.debug('clidraster-> Creando nuevo raster con las variables dasoLidar, el tipo de bosque y el tipo de masa:')
    myLog.debug('\t\t{}'.format(miOutputFileNameConPath))
    myLog.debug('\t-> PAR_outRasterDriver:    {}'.format(PAR_outRasterDriver))
    myLog.debug('\t-> bandas:                 {}'.format(nBandasOutput))
    myLog.debug('\t-> PAR_outputNpDatatype:   {}'.format(PAR_outputNpDatatype))
    myLog.debug('\t-> PAR_outputGdalDatatype: {}'.format(PAR_outputGdalDatatype))
    myLog.debug('\t-> noDataValueDasoVarAsc:  {}'.format(noDataValueDasoVarAsc))
    myLog.debug('\t-> PAR_noDataTiffProvi:    {}'.format(PAR_noDataTiffProvi))
    myLog.debug('\t-> PAR_noDataMergeTiff:    {}'.format(PAR_noDataMergeTiff))
    myLog.debug('\t-> shape (X x Y):          {} x {}'.format(nCeldasX_Destino, nCeldasY_Destino))
    if LCL_convertirAlt:
        myLog.debug('\t-> PAR_noDataMergeTiff:    {}'.format(PAR_noDataMergeTiff))
    myLog.debug('\t-> PAR_outputOptions:      {}'.format(PAR_outputOptions))

    if os.path.exists(miOutputFileNameConPath):
        myLog.info('\t-> El fichero ya existe; se elimina antes de crearlo de nuevo.')
        try:
            os.remove(miOutputFileNameConPath)
        except:
            myLog.error(f'\n-> Comprobar si el fichero {miOutputFileNameConPath} esta bloqueado en uso por Qgis u otra aplicacion y ejecutar de nuevo.')
            sys.exit(0)

    outputDataset = driver.Create(
        miOutputFileNameConPath,
        xsize=nCeldasX_Destino,
        ysize=nCeldasY_Destino,
        bands=nBandasOutput,
        eType=PAR_outputGdalDatatype,
        options=PAR_outputOptions
    )
    outputDataset.SetGeoTransform([nMinX_tif, metrosPixelX_Destino, 0, nMaxY_tif, 0, metrosPixelY_Destino])
    # Creacion y asignacion del sistema de referencia espacial (SRS)
    targetSR = osr.SpatialReference()
    targetSR.SetUTM(30, True)  # = targetSR.SetUTM( 30, 1 )
    # targetSR.SetWellKnownGeogCS( 'EPSG:4258' ) #ETRS89
    targetSR.SetWellKnownGeogCS('EPSG:3042')  # ETRS89 UTM30
    outputDataset.SetProjection(targetSR.ExportToWkt())
    myLog.debug(f'{TB}{TV}-> Sistema de proyeccion del raster creado: {outputDataset.GetProjection()}')
    myLog.debug(f'{TB}{TV}-> Dimensiones del raster creado: Filas (Y)-> {outputDataset.RasterYSize} Columnas (X)-> {outputDataset.RasterXSize}')
    if PAR_outputNpDatatype == 1:
        # Accedo a su banda 1
        outputBand1 = outputDataset.GetRasterBand(1)
    else:
        # Pendiente organizar como guardo LotesDeCadatipoDeMasa en cada banda
        # Esto se hace despues de asignar el tipo de masa a cada pixel.
        # El tipo de masa se guarda en la banda 1
        outputBand1 = outputDataset.GetRasterBand(1)

    if PAR_generarDasoLayers:
        # self_LOCLmergedUniCellAllDasoVarsFileNameSinPath => multiDasoLayer
        myLog.debug('\t-> Asignando noData para dasoLayers:')
        myLog.debug('\t\t-> Asignando propiedad noData:    noDataValueDasoVarAsc = {}'.format(noDataValueDasoVarAsc))
        # myLog.debug('\t\t-> Asignando propiedad noData ->     PAR_noDataMergeTiff = {}'.format(PAR_noDataMergeTiff))
        myLog.debug('\t\t\t-> Se usa este noData porque hay una variable alturas')
        myLog.debug('\t\t-> Pero rellenando provisionalmente: PAR_noDataTiffProvi = {}'.format(PAR_noDataTiffProvi))
        for outputNBand in range(1, nBandasOutput + 1):
            outputBandN = outputDataset.GetRasterBand(outputNBand)
            outputBandN.SetNoDataValue(noDataValueDasoVarAsc)
            loteDeFilas = 1  # i.e. the number of rows to write with each iteration
            nxarray = np.ones(outputBandN.XSize) * PAR_noDataTiffProvi
            nxarray = nxarray[::-1]
            nxarray.shape = (1, -1)
            for j in range(outputBandN.YSize):
                try:
                    outputBandN.WriteArray(nxarray, 0, loteDeFilas * j)
                except:
                    myLog.critical('\t-> clidraster-> Aviso: (a) ha ocurrido un problema asignando PAR_noDataTiffProvi ({}):'.format(PAR_noDataTiffProvi), j)
    elif generarMetaPixeles:
        # outputTipoMasa => tipoMasaLayer
        # outputCluster  => dasoClusterLayer
        myLog.debug('\t-> Asignando noData para MetaPixeles:')
        myLog.debug('\t\t-> Asignando propiedad noData:      noDataValueDasoVarAsc = {}'.format(noDataValueDasoVarAsc))
        for outputNBand in range(1, nBandasOutput + 1):
            outputBandN = outputDataset.GetRasterBand(outputNBand)
            outputBandN.SetNoDataValue(noDataValueDasoVarAsc)
            loteDeFilas = 1  # i.e. the number of rows to write with each iteration
            nxarray = np.ones(outputBandN.XSize) * PAR_noDataTiffProvi
            nxarray = nxarray[::-1]
            nxarray.shape = (1, -1)
            for j in range(outputBandN.YSize):
                try:
                    outputBandN.WriteArray(nxarray, 0, loteDeFilas * j)
                except:
                    myLog.critical('\t-> clidraster-> Aviso: (a) ha ocurrido un problema asignando PAR_noDataTiffProvi ({}):'.format(PAR_noDataTiffProvi), j)
    else:
        if LCL_convertirAlt:
            myLog.debug('\t.> Asignando PAR_noDataMergeTiff = {}...'.format(PAR_noDataMergeTiff))
            outputBand1.SetNoDataValue(PAR_noDataMergeTiff)
        else:
            myLog.debug('\t-> Asignando noDataValueDasoVarAsc = {}...'.format(noDataValueDasoVarAsc))
            outputBand1.SetNoDataValue(noDataValueDasoVarAsc)
        loteDeFilas = 1  # i.e. the number of rows to write with each iteration
        # nxarray = np.ones(outputBand1.XSize*loteDeFilas, dtype=np.int16).reshape(outputBand1.XSize,loteDeFilas)
        # nxarray.fill(noDataValueDasoVarAsc)
        # nxarray = np.ones(outputBand1.XSize) * noDataValueDasoVarAsc
        myLog.debug('\t\t-> Pero rellenando provisionalmente con PAR_noDataTiffProvi = {}...'.format(PAR_noDataTiffProvi))
        nxarray = np.ones(outputBand1.XSize) * PAR_noDataTiffProvi
        nxarray = nxarray[::-1]
        nxarray.shape = (1, -1)
        for j in range(outputBand1.YSize):
            try:
                outputBand1.WriteArray(nxarray, 0, loteDeFilas * j)
            except:
                myLog.critical('\t-> clidraster-> Aviso: (c) ha ocurrido un problema asignando noDataValueDasoVarAsc ({}):'.format(PAR_noDataTiffProvi), j)
    # myLog.debug('{:=^80}'.format(''))

    return (outputDataset, outputBand1)


# ==============================================================================
if __name__ == "__main__":
    # import cartolidar
    pass
