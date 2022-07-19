#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Module included in cartolidar project (clidtools package)
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidtwinx is aux to clidtwins, that provides classes and functions that can be used to search for
areas similar to a reference one in terms of dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''
# -*- coding: latin-1 -*-

import os
import sys
import time
import unicodedata
import warnings
import pathlib
import logging
import importlib
import importlib.util
from operator import itemgetter, attrgetter
from configparser import RawConfigParser
# import random

import numpy as np
import numpy.ma as ma
from scipy.spatial import distance as distance_hist
# from scipy.spatial import KDTree

# Si se importa este modulo hay que modificar el logging para que no duplique la salida a pantalla:
#  Eliminar la creacion del MyLog en __main__.py y activar siempre la de qlidtwins.py
mostrarGraficaHistograma = False
if mostrarGraficaHistograma:
    import matplotlib.pyplot as plt

try:
    import psutil
    psutilOk = True
except:
    psutilOk = False

# ==============================================================================
try:
    # print(os.environ['PATH'])
    from osgeo import gdal, ogr, osr, gdalnumeric, gdalconst
    gdalOk = True
except:
    print('clidtwinx-> No se puede importar gdal "from osgeo", se intenta directamente ("import gdal").')
    gdalOk = False
if not gdalOk:
    try:
        import gdal, ogr, osr, gdalnumeric, gdalconst
        sys.stdout.write('           gdal importado ok con "import gdal".\n')
        gdalOk = True
    except:
        gdalOk = False
        print('clidtwinx-> Error importando gdal.')
        sys.exit(0)
# ==============================================================================


spec = importlib.util.find_spec('cartolidar')
if not spec is None:
    from cartolidar.clidax import clidconfig
    from cartolidar.clidax import clidraster
    from cartolidar.clidtools.clidtwcfg import GLO
else:
    try:
        from cartolidar.clidax import clidconfig
        from cartolidar.clidax import clidraster
        from cartolidar.clidtools.clidtwcfg import GLO
    except:
        if '-vv' in sys.argv or '--verbose' in sys.argv:
            sys.stderr.write(f'clidtwinx-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).\n')
            sys.stderr.write(f'\t-> Se importa clidconfig desde clidtwcfg del directorio local {os.getcwd()}/clidtools.\n')
        from clidax import clidconfig
        from clidax import clidraster
        from clidtools.clidtwcfg import GLO

# Alternativa, si necesitara algun otro ingreciente de clidtwcfg:
# from cartolidar.clidtools import clidtwcfg as CNFG
# ==============================================================================
# Nota: en clidtwcfg se asignan algunos parametros de configuracion que
# no se usan en clidtwins: pero se mantienen porque se usan en otros modulos
# de cartolidar, como son las funciones compartidas con clidmerge.py
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
TW = ' ' * 2
TB = ' ' * 12
TV = ' ' * 3
# ==============================================================================
TRNS_buscarBloquesSoloDentroDelMarcoUTM = True
TRNS_reducirConsumoRAM = False
TRNS_saltarPixelsSinTipoBosque = True
MINIMO_PIXELS_POR_CLUSTER = 5
TRNS_tipoBoscCompatible = 5
SCIPY_METHODS = (
    ("Euclidean", distance_hist.euclidean),
    # ("Manhattan", distance_hist.cityblock),
    # ("Chebysev", distance_hist.chebyshev)
)
nScipyMethods = len(SCIPY_METHODS)
# ==============================================================================
GLBLarrayProximidadInterEspecies = GLO.GLBLarrayProximidadInterEspecies
# ==============================================================================

# ==============================================================================
myModule = __name__.split('.')[-1]
myUser = clidconfig.infoUsuario()
# ==============================================================================
myLog = clidconfig.iniciaConsLog(myModule=myModule, myVerbose=__verbose__)
# ==============================================================================
myLog.debug('{:_^80}'.format(''))
myLog.debug('clidtwinx-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================


# ==============================================================================
def guardarArrayEnBandaDataset(
        arrayBandaActualizado,
        outputBandaActualizar,
        nOffsetX=0,
        nOffsetY=0,
    ):
    for nFila in range(arrayBandaActualizado.shape[0]):
        nxarray = arrayBandaActualizado[nFila, :]
        nxarray.shape = (1, -1)
        outputBandaActualizar.WriteArray(nxarray, nOffsetX, nOffsetY + nFila)
    outputBandaActualizar.FlushCache()
    return outputBandaActualizar


# ==============================================================================
def getParametroConPath(
        valorParametro=None,
        dataBasePath=os.getcwd(),
        nombreParametro='',
        valorPorDefecto='',
        ):

    if valorParametro is None:
        valorParametro = valorPorDefecto

    if valorParametro == '':
        if os.path.isdir(os.path.abspath(valorParametro)):
            parametroConAbsPath = os.path.abspath(valorParametro)
        else:
            print(f'clidtwinx-> Se requiere el argumento {nombreParametro}')
            sys.exit(0)
    else:
        if ':' in valorParametro or valorParametro.startswith('/'):
            # El valorParametro es una ruta absoluta
            parametroConAbsPath = valorParametro
        elif dataBasePath is None:
            parametroConAbsPath = os.path.abspath(valorParametro)
        else:
            # El valorParametro es una ruta relativa.
            # Supongo que:
            #   O bien cartolidar se ejecuta con -m o esa ruta esta referida al directorio de trabajo.
            #   O bien se ejecuta directamente qlidtiwns y el directorio de trabajo es el que contiene a ese modulo.
            if '__main__.py' in sys.argv[0]:
                parametroConAbsPath = os.path.abspath(os.path.join(dataBasePath, 'cartolidar', valorParametro))
            # elif 'qlidtwins.py' in sys.argv[0]:
            else:
                parametroConAbsPath = os.path.abspath(os.path.join(dataBasePath, valorParametro))
            # print(f'\nChequeo de asignacion de rutasAbsolutas:')
            # print(f'{TB}-> os.getcwd():         {os.getcwd()}')
            # print(f'{TB}-> dataBasePath:        {dataBasePath}')
            # print(f'{TB}-> valorParametro:      {valorParametro}')
            # print(f'{TB}-> parametroConAbsPath: {parametroConAbsPath}')
    return parametroConAbsPath


# ==============================================================================
def verificarExistencia(
        LOCLvectorFileName,
        LOCLrutaAscBase=None,
    ):
    patronVectrNameConPath = getParametroConPath(
        LOCLvectorFileName,
        dataBasePath=LOCLrutaAscBase,
        nombreParametro='vectorFileName',
        )

    try:
        if os.path.exists(patronVectrNameConPath):
            return (True, patronVectrNameConPath)
        else:
            return (False, patronVectrNameConPath)
    except:
        return (False, patronVectrNameConPath)


# ==============================================================================
def obtenerExtensionDeCapaVectorial(
        LOCLrutaAscBase,
        LOCLvectorFileName,
        LOCLlayerName=None,
        LOCLverbose=False,
    ):
    (usarVectorFileParaDelimitarZona, patronVectrNameConPath) = verificarExistencia(
        LOCLvectorFileName,
        LOCLrutaAscBase=LOCLrutaAscBase,
        )
    # print(f'clidtwinx-> patronVectrNameConPath (b): {patronVectrNameConPath}')

    if not usarVectorFileParaDelimitarZona:
        myLog.error(f'\nclidtwinx-> ATENCION: no esta disponible el fichero: {patronVectrNameConPath}')
        myLog.error(f'{TB}-> Este fichero se especifica en el fichero de configuracion ({GLO.configFileNameCfg}).')
        myLog.error(f'{TB}-> Es necesaro porque contiene los poligonos de referencia para buscar otros similares.')
        return None
    if not gdalOk:
        myLog.error('\nclidtwinx-> ATENCION: Gdal no disponible; no se puede leer %s' % (patronVectrNameConPath))
        sys.exit(0)

    if LOCLverbose:
        myLog.info(f'clidtwinx-> Obteniendo extension de la capa vectorial:')
        myLog.info(f'{TB}-> File {patronVectrNameConPath}')
    if (LOCLvectorFileName.lower()).endswith('.shp'):
        LOCLPatronVectorDriverName = 'ESRI Shapefile'
    elif (LOCLvectorFileName.lower()).endswith('.gpkg'):
        # Ver mas en https://gdal.org/drivers/vector/gpkg.html
        # Ver tb https://gdal.org/drivers/raster/gpkg.html#raster-gpkg
        LOCLPatronVectorDriverName = 'GPKG'
    else:
        LOCLPatronVectorDriverName = ''
        myLog.critical(f'clidtwinx-> No se ha identificado bien el driver para este fichero: {patronVectrNameConPath}')
        sys.exit(0)
    if LOCLverbose > 1:
        myLog.debug(f'{TB}{TV}-> Driver: {LOCLPatronVectorDriverName}')

    inputVectorRefOgrDriver = ogr.GetDriverByName(LOCLPatronVectorDriverName)
    if inputVectorRefOgrDriver is None:
        myLog.error('\nclidtwinx-> ATENCION: el driver {} no esta disponible.'.format(LOCLPatronVectorDriverName))
        sys.exit(0)
    try:
        patronVectorRefDataSource = inputVectorRefOgrDriver.Open(patronVectrNameConPath, 0)  # 0 means read-only. 1 means writeable.
    except:
        myLog.error('\nclidtwinx-> No se puede abrir {}-> revisar si esta corrupto, faltan ficheros o esta bloqueado'.format(patronVectrNameConPath))
        sys.exit(0)
    try:
        if LOCLlayerName == '' or LOCLlayerName is None or (LOCLvectorFileName.lower()).endswith('.shp'):
            # or LOCLlayerName == 'None':
            patronVectorRefLayer = patronVectorRefDataSource.GetLayer()
        else:
            # Ver: https://developer.ogc.org/samples/build/python-osgeo-gdal/text/load-data.html#using-the-gdal-ogr-library
            # Ver tb: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
            # Ver tb: https://gdal.org/tutorials/vector_api_tut.html
            # Para editar los registros de forma r�pida usar StartTransaction:
            #  https://gis.stackexchange.com/questions/277587/why-editing-a-geopackage-table-with-ogr-is-very-slow
            if LOCLverbose:
                myLog.info(f'{TB}{TV}-> Layer: {LOCLlayerName}')
            patronVectorRefLayer = patronVectorRefDataSource.GetLayer(LOCLlayerName)
    except:
        myLog.error('\nclidtwinx-> ATENCION: el fichero {} no tiene al layer {} (o da error al intentar leerlo).'.format(patronVectrNameConPath, LOCLlayerName))
        myLog.error(f'{TB}-> LOCLlayerName: {LOCLlayerName} {type(LOCLlayerName)}')
        sys.exit(0)
    if patronVectorRefLayer is None:
        myLog.error('\nclidtwinx-> ATENCION: el fichero {} no tiene al layer {} (o no esta accesible).'.format(patronVectrNameConPath, LOCLlayerName))
        myLog.error(f'{TB}-> LOCLlayerName: {LOCLlayerName} {type(LOCLlayerName)}')
        sys.exit(0)
    patronVectorRefFeatureCount = patronVectorRefLayer.GetFeatureCount()
    (
        patronVectorXmin,
        patronVectorXmax,
        patronVectorYmin,
        patronVectorYmax,
    ) = patronVectorRefLayer.GetExtent()

    myLog.debug(f'{TB}-> Layer leido ok: {LOCLlayerName}')
    if LOCLverbose:
        myLog.info(f'{TB}{TV}-> Numero de poligonos: {patronVectorRefFeatureCount}')
        myLog.info(f'{TB}{TV}-> Extension del layer:')
        myLog.info(f'{TB}{TV}{TV}-> patronVectorXmin: {patronVectorXmin:10.2f}')
        myLog.info(f'{TB}{TV}{TV}-> patronVectorXmax: {patronVectorXmax:10.2f}')
        myLog.info(f'{TB}{TV}{TV}-> patronVectorYmin: {patronVectorYmin:10.2f}')
        myLog.info(f'{TB}{TV}{TV}-> patronVectorYmax: {patronVectorYmax:10.2f}')

    # Cierro la capa
    patronVectorRefDataSource = None

    return (
        patronVectorXmin,
        patronVectorXmax,
        patronVectorYmin,
        patronVectorYmax,
    )


# ==============================================================================
def comprobarTipoMasaDeCapaVectorial(
        LOCLrutaAscBase,
        LOCLvectorFileName,
        LOCLlayerName=None,
        LOCLpatronFieldName=None,
        LOCLtipoDeMasaSelec=None,
        LOCLverbose=False,
    ):
    (usarVectorFileParaDelimitarZona, patronVectrNameConPath) = verificarExistencia(
        LOCLvectorFileName,
        LOCLrutaAscBase=LOCLrutaAscBase,
        )
    if not usarVectorFileParaDelimitarZona:
        myLog.error(f'\nclidtwinx-> ATENCION: verificando tipoDeMasa, no esta disponible el fichero: {patronVectrNameConPath}')
        return (None, None, [None])
    if not gdalOk:
        myLog.error('\nclidtwinx-> ATENCION: Gdal no disponible; no se puede leer %s' % (patronVectrNameConPath))
        sys.exit(0)
    if __verbose__:
        myLog.info(f'clidtwinx-> Verificando poligono(s) con tipoDeMasa (patron) seleccionado:')
        myLog.info(f'{TB}-> File {patronVectrNameConPath}')

    if (LOCLvectorFileName.lower()).endswith('.shp'):
        LOCLPatronVectorDriverName = 'ESRI Shapefile'
    elif (LOCLvectorFileName.lower()).endswith('.gpkg'):
        # Ver mas en https://gdal.org/drivers/vector/gpkg.html
        # Ver tb https://gdal.org/drivers/raster/gpkg.html#raster-gpkg
        LOCLPatronVectorDriverName = 'GPKG'
    else:
        LOCLPatronVectorDriverName = ''
        myLog.critical(f'clidtwinx-> No se ha identificado bien el driver para este fichero: {patronVectrNameConPath}')
        sys.exit(0)
    if LOCLverbose > 1:
        myLog.debug(f'{TB}{TV}-> Driver: {LOCLPatronVectorDriverName}')

    inputVectorRefOgrDriver = ogr.GetDriverByName(LOCLPatronVectorDriverName)
    if inputVectorRefOgrDriver is None:
        myLog.error('\nclidtwinx-> ATENCION: el driver {} no esta disponible.'.format(LOCLPatronVectorDriverName))
        sys.exit(0)
    try:
        patronVectorRefDataSource = inputVectorRefOgrDriver.Open(patronVectrNameConPath, 0)  # 0 means read-only. 1 means writeable.
    except:
        myLog.error('\nclidtwinx-> No se puede abrir {}-> revisar si esta corrupto, faltan ficheros o esta bloqueado'.format(patronVectrNameConPath))
        sys.exit(0)
    try:
        if LOCLlayerName == '' or LOCLlayerName is None or (LOCLvectorFileName.lower()).endswith('.shp'):
            # or LOCLlayerName == 'None':
            patronVectorRefLayer = patronVectorRefDataSource.GetLayer()
        else:
            # Ver: https://developer.ogc.org/samples/build/python-osgeo-gdal/text/load-data.html#using-the-gdal-ogr-library
            # Ver tb: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
            # Ver tb: https://gdal.org/tutorials/vector_api_tut.html
            # Para editar los registros de forma r�pida usar StartTransaction:
            #  https://gis.stackexchange.com/questions/277587/why-editing-a-geopackage-table-with-ogr-is-very-slow
            if __verbose__:
                myLog.info(f'{TB}{TV}-> Layer: {LOCLlayerName}')
            patronVectorRefLayer = patronVectorRefDataSource.GetLayer(LOCLlayerName)
    except:
        myLog.error(
            '\nclidtwinx-> ATENCION: el fichero {} no tiene al layer {} (o da error al intentar leerlo).'.format(
                patronVectrNameConPath,
                LOCLlayerName
            )
        )
        myLog.error(f'{TB}-> LOCLlayerName: {LOCLlayerName} {type(LOCLlayerName)}')
        sys.exit(0)
    if patronVectorRefLayer is None:
        myLog.error(
            '\nclidtwinx-> ATENCION: el fichero {} no tiene al layer {} (o no esta accesible).'.format(
                patronVectrNameConPath,
                LOCLlayerName
            )
        )
        myLog.error(f'{TB}-> LOCLlayerName: {LOCLlayerName} {type(LOCLlayerName)}')
        sys.exit(0)
    # patronVectorRefFeatureCount = patronVectorRefLayer.GetFeatureCount()

    if __verbose__:
        myLog.info(f'{TB}{TV}-> Campo tipoDeMasa: {LOCLpatronFieldName}')
    featureDefnAll = patronVectorRefLayer.GetLayerDefn()
    listaCampos = []
    for nCampo in range(featureDefnAll.GetFieldCount()):
        listaCampos.append(featureDefnAll.GetFieldDefn(nCampo).GetName())
    if LOCLpatronFieldName in listaCampos:
        tipoDeMasaField = True
    else:
        tipoDeMasaField = False
        myLog.error(f'clidtwinx-> ATENCION: la capa {LOCLvectorFileName} no incluye el campo {LOCLpatronFieldName}')
        myLog.error(f'{TB}-> Todos los campos en esa capa: {listaCampos}')
        return (False, False, [None])

    listaTM = []
    nFeature = 0
    for feature in patronVectorRefLayer:
        # geom = feature.GetGeometryRef()
        try:
            myTM = feature.GetField(LOCLpatronFieldName)
            nFeature += 1
        except:
            myLog.error(f'{TW}clidtwinx-> nFeature {nFeature} ERROR')
            myTM = -1
        if not myTM in listaTM:
            listaTM.append(myTM)
    if LOCLtipoDeMasaSelec is None:
        tipoDeMasaValue = True
    else:
        if LOCLtipoDeMasaSelec in listaTM:
            tipoDeMasaValue = True
        else:
            myLog.error(f'{TW}clidtwinx-> ATENCION: la capa {LOCLvectorFileName} (campo {LOCLpatronFieldName}) no incluye el valor {LOCLtipoDeMasaSelec}')
            tipoDeMasaValue = False

    # Cierro la capa
    patronVectorRefDataSource = None

    return (tipoDeMasaField, tipoDeMasaValue, listaTM)


# ==============================================================================
def recortarRasterTiffPatronDasoLidar(
        self_LOCLrutaAscRaizBase,
        self_LOCLoutPathNameRuta,
        self_LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
        noDataDasoVarAll,
        outputNpDatatypeAll,
        nMinTipoMasa,
        nMaxTipoMasa,
        nInputVars,
        nFicherosDisponiblesPorTipoVariable,
        self_LOCLlistaDasoVarsMovilidad=GLO.GLBLlistaDasoVarsMovilidad,
        # self_LOCLlistaDasoVarsPonderado=GLO.GLBLlistaDasoVarsPonderado,
        self_LOCLvarsTxtFileName=GLO.GLBLvarsTxtFileNamePorDefecto,
        self_LOCLpatronVectrName=GLO.GLBLpatronVectrNamePorDefecto,
        self_LOCLpatronLayerName=GLO.GLBLpatronLayerNamePorDefecto,
        self_LOCLpatronFieldName=GLO.GLBLpatronFieldNamePorDefecto,
        self_LOCLtipoDeMasaSelec=None,
        self_LOCLlistLstDasoVars=GLO.GLBLlistLstDasoVarsPorDefecto,

        self_nCeldasX_Destino=0,
        self_nCeldasY_Destino=0,
        self_metrosPixelX_Destino=0,
        self_metrosPixelY_Destino=0,
        self_nMinX_tif=0,
        self_nMaxY_tif=0,

        self_LOCLverbose=False,
    ):
    # ==========================================================================
    patronVectrNameConPath = getParametroConPath(
        self_LOCLpatronVectrName,
        dataBasePath=self_LOCLrutaAscRaizBase,
        nombreParametro='patronVectrName',
        )
    # print(f'clidtwinx-> patronVectrNameConPath (a): {patronVectrNameConPath}')
    # ==========================================================================
    envolventeShape = obtenerExtensionDeCapaVectorial(
        self_LOCLrutaAscRaizBase,
        self_LOCLpatronVectrName,
        LOCLlayerName=self_LOCLpatronLayerName,
        LOCLverbose=False,
    )
    if envolventeShape is None:
        myLog.error('\nclidtwinx-> AVISO: no esta disponible el fichero {}'.format(self_LOCLpatronVectrName))
        myLog.error(f'{TB}-> Ruta base: {self_LOCLrutaAscRaizBase}')
        sys.exit(0)
    patronVectorXmin = envolventeShape[0]
    patronVectorXmax = envolventeShape[1]
    patronVectorYmin = envolventeShape[2]
    patronVectorYmax = envolventeShape[3]

    self_nMaxX_tif = self_nMinX_tif + (self_nCeldasX_Destino * self_metrosPixelX_Destino)
    self_nMinY_tif = self_nMaxY_tif + (self_nCeldasY_Destino * self_metrosPixelY_Destino)  # self_metrosPixelY_Destino es negativo

    if (
        self_nMinX_tif > patronVectorXmax
        or self_nMaxX_tif < patronVectorXmin
        or self_nMinY_tif > patronVectorYmax
        or self_nMaxY_tif < patronVectorYmin
    ):
        myLog.error('\nclidtwinx-> ATENCION: el perimetro de referencia (patron) no esta dentro de la zona analizada:')
        myLog.error(
            '{}-> Rango de coordenadas UTM de la zona analizada: X: {:0.2f} - {:0.2f}; Y: {:0.2f} - {:0.2f}'.format(
                TB,
                self_nMinX_tif, self_nMaxX_tif, self_nMinY_tif, self_nMaxY_tif,
            )
        )
        myLog.error(
            '{}-> Rango de coord UTM del perimetro del patron:   X: {:0.2f} - {:0.2f}; Y: {:0.2f} - {:0.2f}'.format(
                TB,
                patronVectorXmin,
                patronVectorXmax,
                patronVectorYmin,
                patronVectorYmax,
            )
        )
        myLog.error(
            '{}-> Raster con la zona analizada (envolvente de los asc): {}/{}'.format(
                TB,
                self_LOCLoutPathNameRuta,
                self_LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
            )
        )
        myLog.error(f'{TB}-> Vector file con el perimetro de referencia (patron):  {patronVectrNameConPath}')
        sys.exit(0)

    #===========================================================================
    if self_LOCLtipoDeMasaSelec is None:
        tipoDeMasaSeleccionado = 'True'
    else:
        (tipoDeMasaFieldOk, tipoDeMasaValueOk, listaTM) = comprobarTipoMasaDeCapaVectorial(
            self_LOCLrutaAscRaizBase,
            self_LOCLpatronVectrName,
            LOCLlayerName=self_LOCLpatronLayerName,
            LOCLpatronFieldName=self_LOCLpatronFieldName,
            LOCLtipoDeMasaSelec=self_LOCLtipoDeMasaSelec,
            LOCLverbose=False,
        )
        if tipoDeMasaFieldOk is None:
            myLog.error('\nclidtwinx-> AVISO: no esta disponible el fichero {}'.format(self_LOCLpatronVectrName))
            myLog.error(f'{TB}-> Ruta base: {self_LOCLrutaAscRaizBase}')
            sys.exit(0)
        if not tipoDeMasaFieldOk:
            self_LOCLtipoDeMasaSelec = None
        elif not tipoDeMasaValueOk:
            self_LOCLtipoDeMasaSelec = None
        else:
            tipoDeMasaSeleccionado = f'{self_LOCLpatronFieldName}={self_LOCLtipoDeMasaSelec}'
    # ==========================================================================

    # ==========================================================================
    mergedUniCellAllDasoVarsFileNameConPath = os.path.join(self_LOCLoutPathNameRuta, self_LOCLoutFileNameWExt_mergedUniCellAllDasoVars)
    outputRasterNameClip = mergedUniCellAllDasoVarsFileNameConPath.replace('Global', f'Patron_TM{self_LOCLtipoDeMasaSelec}')
    if __verbose__:
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwinx-> Abriendo raster creado mergedUniCellAllDasoVars:\n{TB}{mergedUniCellAllDasoVarsFileNameConPath}')
    rasterDatasetAll = gdal.Open(mergedUniCellAllDasoVarsFileNameConPath, gdalconst.GA_ReadOnly)
    # myLog.debug('--->>> rasterDatasetAll (1): {rasterDatasetAll}')
    #===========================================================================

    LOCLoutputRangosFileTxtSinPath = self_LOCLvarsTxtFileName
    LOCLoutputRangosFileNpzSinPath = self_LOCLvarsTxtFileName.replace('.txt', '.npz')
    LOCLdictHistProb01 = {}
    maxNBins = 256
    LOCLlistHistProb01 = np.zeros(nInputVars * 3 * maxNBins, dtype=np.float32).reshape(nInputVars, 3, maxNBins)

    # outputBand1 = rasterDatasetAll.GetRasterBand(1)
    # arrayBanda1 = outputBand1.ReadAsArray().astype(outputNpDatatypeAll)
    if __verbose__:
        myLog.info(f'clidtwinx-> Recortando el raster con poligono de referencia (patron):\n'
              f'{TB}{patronVectrNameConPath}')
    # Ver:
    #  https://gdal.org/python/
    #  https://gdal.org/python/osgeo.gdal-module.html
    #  https://gdal.org/python/osgeo.gdal-pysrc.html#Warp
    try:
        if self_LOCLpatronLayerName == '' or self_LOCLpatronLayerName is None:
            rasterDatasetClip = gdal.Warp(
                outputRasterNameClip,
                rasterDatasetAll,
                cutlineDSName=patronVectrNameConPath,
                cutlineWhere=tipoDeMasaSeleccionado,
                cropToCutline=True,
                # dstNodata=np.nan,
                dstNodata=noDataDasoVarAll,
            )
        else:
            myLog.debug(f'{TB}Layer: {self_LOCLpatronLayerName}')
            rasterDatasetClip = gdal.Warp(
                outputRasterNameClip,
                rasterDatasetAll,
                cutlineDSName=patronVectrNameConPath,
                cutlineLayer=self_LOCLpatronLayerName,
                cutlineWhere=tipoDeMasaSeleccionado,
                cropToCutline=True,
                # dstNodata=np.nan,
                dstNodata=noDataDasoVarAll,
            )
    except:
        myLog.error(f'\nclidtwinx-> No se ha podido recortar el raster generado con {patronVectrNameConPath}, cutlineLayer: {self_LOCLpatronLayerName}, {type(self_LOCLpatronLayerName)}')
        myLog.error(f'{TB}Revisar si se ha generado adecuadamente el raster {mergedUniCellAllDasoVarsFileNameConPath}')
        myLog.error(f'{TB}Revisar si la capa vectorial de recorte es correcta, no esta bloqueada (y tiene un poligono) {patronVectrNameConPath}')
        sys.exit(0)

    # Para contar el numero de celdas con valores distintos de noData en todas las bandas,
    # se parte de un array con todos los valores cero (arrayBandaXMaskClip),
    # se ponen a 1 las celdas con ALGUN valor noData y, despues de recorrer 
    # todas las bandas, se cuenta el numero de celdas igual a cero.
    # Con eso, se crea un array que va a contener la lista de celdas con valor ok
    if __verbose__:
        myLog.info(f'clidtwinx-> Leyendo raster recortado para crear mascara de noData: {outputRasterNameClip}')
    # rasterDatasetClip = gdal.Open(outputRasterNameClip, gdalconst.GA_ReadOnly)
    nBandasRasterOutput = rasterDatasetClip.RasterCount
    outputBand1Clip = rasterDatasetClip.GetRasterBand(1)
    # arrayBanda1Clip = outputBand1Clip.ReadAsArray().astype(outputNpDatatypeAll)
    arrayBanda1Clip = outputBand1Clip.ReadAsArray()
    arrayBandaXMaskClip = np.full_like(arrayBanda1Clip, 0, dtype=np.uint8)
    for nBanda in range(1, nBandasRasterOutput + 1):
        outputBandXClip = rasterDatasetClip.GetRasterBand(nBanda)
        # arrayBandaXClip = outputBandXClip.ReadAsArray().astype(outputNpDatatypeAll)
        arrayBandaXClip = outputBandXClip.ReadAsArray()
        arrayBandaXMaskClip[arrayBandaXClip == noDataDasoVarAll] = 1
        # if self_LOCLverbose:
        #     myLog.debug(f'{TB}Leyendo banda {nBanda} de {nBandasRasterOutput}')

    nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskClip == 0)
    listaCeldasConDasoVarsOkPatron = np.zeros(nCeldasConDasoVarsOk * nBandasRasterOutput, dtype=outputNpDatatypeAll).reshape(nCeldasConDasoVarsOk, nBandasRasterOutput)
    if __verbose__:
        myLog.info(f'{TB}Numero de celdas patron con dasoVars ok: {nCeldasConDasoVarsOk} (valor != noDataDasoVarAll: {noDataDasoVarAll})')
    if nCeldasConDasoVarsOk == 0:
        myLog.warning('')
        myLog.warning(f'clidtwinx-> ATENCION: no hay info de DLVs para la(s) zona(s) de referencia (patron): faltan ficheros asc para esa zona')
        myLog.warning(f'{TB}-> Se ignora el Tipo de masa {self_LOCLtipoDeMasaSelec}')
        return (
            None,  # LOCLoutputRangosFileTxtSinPath,
            None,  # LOCLoutputRangosFileNpzSinPath,
            None,  # nBandasRasterOutput,
            None,  # rasterDatasetAll,
            None,  # listaCeldasConDasoVarsOkPatron,
            None,  # LOCLdictHistProb01,
            None,  # LOCLlistHistProb01,
            None,  # myNBins,
            None,  # myRange,
            None,  # pctjTipoBosquePatronMasFrecuente1,
            None,  # codeTipoBosquePatronMasFrecuente1,
            None,  # pctjTipoBosquePatronMasFrecuente2,
            None,  # codeTipoBosquePatronMasFrecuente2,
            None,  # histProb01PatronBosque,
        )

    # if nBandasRasterOutput != nBandasPrevistasOutput:
    #     myLog.warning(f'\nAVISO: el numero de bandas del raster generado ({nBandasRasterOutput}) no es igual al previsto ({nBandasPrevistasOutput}), es decir num. de variables + 2 (num variables: {nInputVars})')
    # Las nInputVars primeras bandas corresponden a las variables utilizadas (self_LOCLlistaDasoVarsFileTypes)
    # La penultima corresponde al tipo de bosque o cobertura MFE
    # La ultima corresponde al tipo de masa.
    # La numeracion de las bandas empieza en 1 y la de variables empieza en 0.

    # myRange = {}
    # myNBins = {}
    # factorMovilidad = {}
    # Se crean con un elemento que no se usa, porque las banas se empiezan a numerar en 1
    myRange = np.zeros((nBandasRasterOutput + 1) * 2, dtype=np.float32).reshape((nBandasRasterOutput + 1), 2)
    myNBins = np.zeros((nBandasRasterOutput + 1), dtype=np.int32)
    factorMovilidad = [0]
    for nBanda in range(1, nBandasRasterOutput + 1):
        nInputVar = nBanda - 1
        # factorMovilidad[nBanda] = self_LOCLlistaDasoVarsMovilidad[nInputVar] / 100
        factorMovilidad.append(self_LOCLlistaDasoVarsMovilidad[nInputVar] / 100)
        if nBanda == nBandasRasterOutput:
            # TipoMasa
            # myRange[nBanda] = (nMinTipoMasa, nMaxTipoMasa)
            myRange[nBanda] = np.array((nMinTipoMasa, nMaxTipoMasa))
            # myNBins[nBanda] = nMaxTipoMasa - nMinTipoMasa
            myNBins[nBanda] = nMaxTipoMasa - nMinTipoMasa
            # factorMovilidad[nBanda] = 0
        elif nBanda == nBandasRasterOutput - 1:
            # TipoBosqueMfe
            # myRange[nBanda] = (0, 255)
            myRange[nBanda] = np.array((0, 255))
            # myNBins[nBanda] = 255
            myNBins[nBanda] = 255
            # factorMovilidad[nBanda] = 0
        else:
            # Alturas y Coberturas
            # myRange[nBanda] = (self_LOCLlistLstDasoVars[nInputVar][2], self_LOCLlistLstDasoVars[nInputVar][3])
            myRange[nBanda] = np.array((self_LOCLlistLstDasoVars[nInputVar][2], self_LOCLlistLstDasoVars[nInputVar][3]))
            # myNBins[nBanda] = self_LOCLlistLstDasoVars[nInputVar][4]
            myNBins[nBanda] = self_LOCLlistLstDasoVars[nInputVar][4]
            # factorMovilidad[nBanda] = 0.25

    if __verbose__:
        myLog.info(f'clidtwinx-> Analizando bandas del raster recortado:')

    for nBanda in range(1, nBandasRasterOutput + 1):
        # Si para esa variable estan todos los bloques:
        nInputVar = nBanda - 1
        if nInputVar >= 0 and nInputVar < nInputVars:
            if nFicherosDisponiblesPorTipoVariable[nInputVar] != nFicherosDisponiblesPorTipoVariable[0]:
                myLog.debug(f'\nHistograma para banda {nBanda} (variable {nInputVar}: {self_LOCLlistLstDasoVars[nInputVar][1]})')
                # claveRef = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_ref'
                # myLog.debug(f'{TB}-> (1) Chequeando rangos admisibles para: {claveRef}')
                myLog.warning(f'{TB}AVISO: La banda {nBanda} (variable {nInputVar}) no cuenta con fichero para todos los bloques ({nFicherosDisponiblesPorTipoVariable[nInputVar]} de {nFicherosDisponiblesPorTipoVariable[0]})')
                continue
        outputBandXClip = rasterDatasetClip.GetRasterBand(nBanda)
        # arrayBandaXClip = outputBandXClip.ReadAsArray().astype(outputNpDatatypeAll)
        arrayBandaXClip = outputBandXClip.ReadAsArray()

        # myLog.debug(f'\nFragmento de banda {nBanda} ({outputNpDatatypeAll}):')
        # myLog.debug(arrayBandaXClip[20:25, 10:20])

        # https://numpy.org/doc/stable/reference/maskedarray.html
        # https://numpy.org/doc/stable/reference/routines.ma.html#conversion-operations
        arrayBandaXClipMasked = ma.masked_array(
            arrayBandaXClip,
            mask=arrayBandaXMaskClip,
            dtype=outputNpDatatypeAll
            )
        myLog.debug(f'{TB}Banda {nBanda}: numero de puntos patron con dasoVars ok: {len(ma.compressed(arrayBandaXClipMasked))}; arrayBandaXClip.shape: {arrayBandaXClip.shape}')
        # myLog.debug(f'----------------------------------outputNpDatatypeAll: {outputNpDatatypeAll}; noDataDasoVarAll: {noDataDasoVarAll}')
        # myLog.debug(f'----------------------------------Algunos valores arrayBandaXClip: {arrayBandaXClip[0][:5]}')
        # myLog.debug(f'----------------------------------Algunos valores arrayBandaXClipMasked: {ma.compressed(arrayBandaXClipMasked)[:5]}')
        listaCeldasConDasoVarsOkPatron[:, nInputVar] = ma.compressed(arrayBandaXClipMasked)

        # histNumberPatron = [np.zeros(myNBins[nBanda]), None]
        # histProbabPatron = [np.zeros(myNBins[nBanda]), None]
        # histProb01PatronBandaX = np.array([0])
        # codeTipoBosquePatronMasFrecuente1 = 0
        # codeTipoBosquePatronMasFrecuente2 = 0
        # pctjTipoBosquePatronMasFrecuente1 = 0
        # pctjTipoBosquePatronMasFrecuente2 = 0

        celdasConValorSiData = arrayBandaXClip[
            (arrayBandaXClip != noDataDasoVarAll)
            & (arrayBandaXClip >= myRange[nBanda][0])
            & (arrayBandaXClip < myRange[nBanda][1])
        ]
        if (
            (np.count_nonzero(celdasConValorSiData) > 0)
            & (myNBins[nBanda] > 0)
            & (myRange[nBanda][1] - myRange[nBanda][0] > 0)
        ):
            histNumberPatron = np.histogram(
                arrayBandaXClip,
                bins=myNBins[nBanda],
                range=myRange[nBanda]
            )
            histProbabPatron = np.histogram(
                arrayBandaXClip,
                bins=myNBins[nBanda],
                range=myRange[nBanda],
                density=True
            )
            histogramaDisponible = True
        else:
            myLog.debug(f'clidtwinx-> (d) Revisar myNBins {myNBins[nBanda]} y myRange {myRange[nBanda]} para banda {nBanda} con sumaValores: {arrayBandaXClip.sum()}')
            myLog.debug(f'{TB}Se crea histograma con {myNBins[nBanda]} clases nulas')
            histNumberPatron = [np.zeros(myNBins[nBanda]), None]
            histProbabPatron = [np.zeros(myNBins[nBanda]), None]
            histogramaDisponible = False
            continue

        # myLog.debug(f'\nhistProbabPatron[0]: {type(histProbabPatron[0])}')
        histProb01PatronBandaX = np.array(histProbabPatron[0]) * ((myRange[nBanda][1] - myRange[nBanda][0]) / myNBins[nBanda])

        if nBanda == nBandasRasterOutput:
            if self_LOCLverbose:
                myLog.debug(f'\nHistograma para tipos de masa (banda {nBanda})')
                myLog.debug(f'{TB}Por el momento no utilizo esta informacion.')
            try:
                tipoDeMasaUltimoNumero = np.max(np.nonzero(histNumberPatron[0])[0])
            except:
                tipoBosqueUltimoNumero = 0
            histogramaTemp = (histNumberPatron[0]).copy()
            histogramaTemp.sort()
            codeTipoDeMasaPatronMasFrecuente1 = (histNumberPatron[0]).argmax(axis=0)
            arrayPosicionTipoDeMasaPatron1 = np.where(histNumberPatron[0] == histogramaTemp[-1])
            arrayPosicionTipoDeMasaPatron2 = np.where(histNumberPatron[0] == histogramaTemp[-2])
            myLog.debug(f'{TB}-> Tipo de masa principal (patron): {codeTipoDeMasaPatronMasFrecuente1}; frecuencia: {int(round(100 * histProb01PatronBandaX[codeTipoDeMasaPatronMasFrecuente1], 0))} %')
            # myLog.debug(f'{TB}-> {arrayPosicionTipoDeMasaPatron1}')
            for contadorTB1, numPosicionTipoDeMasaPatron1 in enumerate(arrayPosicionTipoDeMasaPatron1[0]):
                # myLog.debug(f'{TB}-> {numPosicionTipoDeMasaPatron1}')
                myLog.debug(f'{TB}-> {contadorTB1} Tipo de masa primero (patron): {numPosicionTipoDeMasaPatron1}; frecuencia: {int(round(100 * histProb01PatronBandaX[numPosicionTipoDeMasaPatron1], 0))} %')
            if histProb01PatronBandaX[arrayPosicionTipoDeMasaPatron2[0][0]] != 0:
                for contadorTB2, numPosicionTipoDeMasaPatron2 in enumerate(arrayPosicionTipoDeMasaPatron2[0]):
                    # myLog.debug(f'{TB}-> {numPosicionTipoDeMasaPatron2}')
                    myLog.debug(f'{TB}-> {contadorTB2} Tipo de masa segundo (patron): {numPosicionTipoDeMasaPatron2}; frecuencia: {int(round(100 * histProb01PatronBandaX[numPosicionTipoDeMasaPatron2], 0))} %')

            if codeTipoDeMasaPatronMasFrecuente1 != arrayPosicionTipoDeMasaPatron1[0][0]:
                myLog.critical(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoDeMasaPatronMasFrecuente1} != {arrayPosicionTipoDeMasaPatron1[0][0]}')
            if len(arrayPosicionTipoDeMasaPatron1[0]) == 1:
                codeTipoDeMasaPatronMasFrecuente2 = arrayPosicionTipoDeMasaPatron2[0][0]
            else:
                codeTipoDeMasaPatronMasFrecuente2 = arrayPosicionTipoDeMasaPatron1[0][1]

            pctjTipoDeMasaPatronMasFrecuente1 = int(round(100 * histProb01PatronBandaX[codeTipoDeMasaPatronMasFrecuente1], 0))
            pctjTipoDeMasaPatronMasFrecuente2 = int(round(100 * histProb01PatronBandaX[codeTipoDeMasaPatronMasFrecuente2], 0))

            if __verbose__:
                myLog.info(f'{TB}-> Tipos de masa mas frecuentes (patron):   1-> {codeTipoDeMasaPatronMasFrecuente1} ({pctjTipoDeMasaPatronMasFrecuente1} %); 2-> {codeTipoDeMasaPatronMasFrecuente2} ({pctjTipoDeMasaPatronMasFrecuente2} %)')
            myLog.debug(f'{TB}-> Numero pixeles de cada tipo de masa (patron) ({(histNumberPatron[0]).sum()}):')
            for numTipoMasa in range(len(histNumberPatron[0])):
                if histNumberPatron[0][numTipoMasa] != 0:
                    myLog.debug(f'{TB}{TV}-> tipoMasa: {numTipoMasa} -> nPixeles: {histNumberPatron[0][numTipoMasa]}')

        elif nBanda == nBandasRasterOutput - 1:
            myLog.debug(f'\nHistograma para tipos de bosque (banda {nBanda})')
            # tipoBosquePrimerNumero = np.min(np.nonzero(histNumberPatron[0])[0])
            histProb01PatronBosque = histProb01PatronBandaX
            try:
                tipoBosqueUltimoNumero = np.max(np.nonzero(histNumberPatron[0])[0])
            except:
                tipoBosqueUltimoNumero = 0
            histogramaTemp = (histNumberPatron[0]).copy()
            histogramaTemp.sort()
            codeTipoBosquePatronMasFrecuente1 = (histNumberPatron[0]).argmax(axis=0)
            arrayPosicionTipoBosquePatron1 = np.where(histNumberPatron[0] == histogramaTemp[-1])
            arrayPosicionTipoBosquePatron2 = np.where(histNumberPatron[0] == histogramaTemp[-2])
            myLog.debug(f'{TB}-> Tipo de bosque principal (patron): {codeTipoBosquePatronMasFrecuente1}; frecuencia: {int(round(100 * histProb01PatronBandaX[codeTipoBosquePatronMasFrecuente1], 0))} %')
            # myLog.debug(f'{TB}-> {arrayPosicionTipoBosquePatron1}')
            for contadorTB1, numPosicionTipoBosquePatron1 in enumerate(arrayPosicionTipoBosquePatron1[0]):
                # myLog.debug(f'{TB}-> {numPosicionTipoBosquePatron1}')
                myLog.debug(f'{TB}-> {contadorTB1} Tipo de bosque primero (patron): {numPosicionTipoBosquePatron1}; frecuencia: {int(round(100 * histProb01PatronBandaX[numPosicionTipoBosquePatron1], 0))} %')
            if histProb01PatronBandaX[arrayPosicionTipoBosquePatron2[0][0]] != 0:
                for contadorTB2, numPosicionTipoBosquePatron2 in enumerate(arrayPosicionTipoBosquePatron2[0]):
                    # myLog.debug(f'{TB}-> {numPosicionTipoBosquePatron2}')
                    myLog.debug(f'{TB}-> {contadorTB2} Tipo de bosque segundo (patron): {numPosicionTipoBosquePatron2}; frecuencia: {int(round(100 * histProb01PatronBandaX[numPosicionTipoBosquePatron2], 0))} %')
            else:
                myLog.debug(f'{TB}-> Solo hay tipo de bosque princial')
            if codeTipoBosquePatronMasFrecuente1 != arrayPosicionTipoBosquePatron1[0][0]:
                myLog.critical(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoBosquePatronMasFrecuente1} != {arrayPosicionTipoBosquePatron1[0][0]}')
            if len(arrayPosicionTipoBosquePatron1[0]) == 1:
                codeTipoBosquePatronMasFrecuente2 = arrayPosicionTipoBosquePatron2[0][0]
            else:
                codeTipoBosquePatronMasFrecuente2 = arrayPosicionTipoBosquePatron1[0][1]

            pctjTipoBosquePatronMasFrecuente1 = int(round(100 * histProb01PatronBandaX[codeTipoBosquePatronMasFrecuente1], 0))
            pctjTipoBosquePatronMasFrecuente2 = int(round(100 * histProb01PatronBandaX[codeTipoBosquePatronMasFrecuente2], 0))

            if __verbose__:
                myLog.info(f'{TB}-> Tipos de bosque mas frecuentes (patron): 1-> {codeTipoBosquePatronMasFrecuente1} ({pctjTipoBosquePatronMasFrecuente1} %); 2-> {codeTipoBosquePatronMasFrecuente2} ({pctjTipoBosquePatronMasFrecuente2} %)')
            myLog.debug(f'{TB}-> Numero pixeles de cada tipo de bosque (patron) ({(histNumberPatron[0]).sum()}):')
            for numTipoBosque in range(len(histNumberPatron[0])):
                if histNumberPatron[0][numTipoBosque] != 0:
                    myLog.debug(f'{TB}{TV}-> tipoBosque: {numTipoBosque} -> nPixeles: {histNumberPatron[0][numTipoBosque]}')
        else:
            if nInputVar < len(self_LOCLlistLstDasoVars):
                myLog.debug(f'\nHistograma para banda {nBanda} (variable {nInputVar}: {self_LOCLlistLstDasoVars[nInputVar][1]}) con {myNBins[nBanda]} Clases')
            else:
                myLog.debug(f'\nHistograma para banda {nBanda} (variable {nInputVar} de {self_LOCLlistLstDasoVars})')
            myLog.debug(f'{TB}-> myRange: {myRange[nBanda]}; nBins: {myNBins[nBanda]}')
            try:
                ultimoNoZero = np.max(np.nonzero(histNumberPatron[0])[0])
            except:
                ultimoNoZero = 0
            myLog.debug(f'{TB}-> Numero puntos: {(histNumberPatron[0]).sum()} -> Histograma: {histNumberPatron[0][:ultimoNoZero + 2]}')
            # myLog.debug(f'{TB}-> Numero pixeles de cada rango de la variable (patron) (total: {(histNumberPatron[0]).sum()}):')
            # for numRango in range(len(histNumberPatron[0])):
            #     if histNumberPatron[0][numRango] != 0:
            #         myLog.debug(f'{TB}{TV}-> Rango num: {numRango} -> nPixeles: {histNumberPatron[0][numRango]}')
        # myLog.debug(f'{TB}-> Suma frecuencias: {round(histProb01PatronBandaX.sum(), 2)}')

        if nInputVar >= 0 and nInputVar < nInputVars:
            claveRef = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_ref'
            claveMin = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_min'
            claveMax = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_max'
            LOCLdictHistProb01[claveRef] = histProb01PatronBandaX
            LOCLdictHistProb01[claveMin] = np.zeros(myNBins[nBanda], dtype=np.float32)
            LOCLdictHistProb01[claveMax] = np.zeros(myNBins[nBanda], dtype=np.float32)
            # El valor de referencia corresponde al index 1,
            # mientras que min y max a los index 0 y 2
            LOCLlistHistProb01[nInputVar, 1, :myNBins[nBanda]] = histProb01PatronBandaX

            # if 0 in LOCLdictHistProb01[claveRef]:
            #     primerCero = LOCLdictHistProb01[claveRef].index(0)
            # else:
            #     primerCero = len(LOCLdictHistProb01[claveRef])
            try:
                ultimoNoZero = np.max(np.nonzero(LOCLdictHistProb01[claveRef])[0])
            except:
                ultimoNoZero = 0
            if __verbose__:
                myLog.info(f'{TB}-> Banda {nBanda} -> Creando rangos admisibles para: {claveRef}')
            myLog.debug(f'{TB}{TV}Valores de referencia (patron):')
            myLog.debug(f'{TB}{TV}-> LOCLdictHistProb01[{claveRef}]: {LOCLdictHistProb01[claveRef][:ultimoNoZero + 2]}')
            # myLog.debug('LOCLdictHistProb01[claveMin]: {LOCLdictHistProb01[claveMin]}')
            # myLog.debug('LOCLdictHistProb01[claveMax]: {LOCLdictHistProb01[claveMax]}')
            for nRango in range(len(histProb01PatronBandaX)):
                # myLog.debug(f'claveRef: {claveRef}; nRango: {type(nRango)} {nRango}')
                # myLog.debug(LOCLdictHistProb01[claveRef])
                # myLog.debug(LOCLdictHistProb01[claveRef][nRango])
                decrementoFrecuencia = max(0.05, (factorMovilidad[nBanda] * LOCLdictHistProb01[claveRef][nRango]))
                LOCLdictHistProb01[claveMin][nRango] = round(LOCLdictHistProb01[claveRef][nRango] - decrementoFrecuencia, 3)
                LOCLlistHistProb01[nInputVar, 0, nRango] = round(LOCLlistHistProb01[nInputVar, 1, nRango] - decrementoFrecuencia, 3)
                if LOCLdictHistProb01[claveMin][nRango] < 0.05:
                    LOCLdictHistProb01[claveMin][nRango] = 0
                    LOCLlistHistProb01[nInputVar, 0, nRango] = 0
                if nRango == 0:
                    if LOCLdictHistProb01[claveRef][nRango] > 0 or LOCLdictHistProb01[claveRef][nRango + 1] > 0:
                        incrementoMinimo = 0.05
                    else:
                        incrementoMinimo = 0.1
                    incrementoFrecuencia = max(
                        incrementoMinimo, (
                            # (factorMovilidad[nBanda] * LOCLdictHistProb01[claveRef][nRango] * 2)
                            + (
                                factorMovilidad[nBanda] * 0.5 * (
                                    LOCLdictHistProb01[claveRef][nRango]
                                    + LOCLdictHistProb01[claveRef][nRango + 1]
                                )
                            )
                        )
                    )
                    myLog.debug(
                        '{}{}{}+{:03}-> claveRef: {} nRango: {}; prev: {}; this: {:0.3f}; post: {:0.3f}'.format(
                            TB, TV, TV,
                            incrementoMinimo * 100,
                            claveRef,
                            nRango,
                            '-.---',
                            LOCLdictHistProb01[claveRef][nRango],
                            LOCLdictHistProb01[claveRef][nRango + 1],
                        )
                    )
                elif nRango == len(histProb01PatronBandaX) - 1:
                    if LOCLdictHistProb01[claveRef][nRango] > 0 or LOCLdictHistProb01[claveRef][nRango - 1] > 0:
                        incrementoMinimo = 0.05
                    else:
                        incrementoMinimo = 0.02
                    incrementoFrecuencia = max(
                        incrementoMinimo, (
                            # (factorMovilidad[nBanda] * LOCLdictHistProb01[claveRef][nRango] * 2)
                            + (
                                factorMovilidad[nBanda] * 0.5 * (
                                    LOCLdictHistProb01[claveRef][nRango]
                                    + LOCLdictHistProb01[claveRef][nRango - 1]
                                )
                            )
                        )
                    )
                    myLog.debug(
                        '{}{}{}+{:03}-> claveRef: {} nRango: {}; prev: {:0.3f}; this: {:0.3f}; post: {}'.format(
                            TB, TV, TV,
                            incrementoMinimo * 100,
                            claveRef,
                            nRango,
                            LOCLdictHistProb01[claveRef][nRango - 1],
                            LOCLdictHistProb01[claveRef][nRango],
                            '-.---',
                        )
                    )
                else:
                    if LOCLdictHistProb01[claveRef][nRango] > 0 or (LOCLdictHistProb01[claveRef][nRango - 1] > 0 and LOCLdictHistProb01[claveRef][nRango + 1] > 0):
                        incrementoMinimo = 0.1
                        myLog.debug(
                            '{}{}{}+{:03}-> claveRef: {} nRango: {}; prev: {:0.3f}; this: {:0.3f}; post: {:0.3f}'.format(
                                TB, TV, TV,
                                10,
                                claveRef,
                                nRango,
                                LOCLdictHistProb01[claveRef][nRango - 1],
                                LOCLdictHistProb01[claveRef][nRango],
                                LOCLdictHistProb01[claveRef][nRango + 1],
                            )
                        )
                    elif LOCLdictHistProb01[claveRef][nRango - 1] > 0 or LOCLdictHistProb01[claveRef][nRango + 1] > 0:
                        incrementoMinimo = 0.05
                        myLog.debug(
                            '{}{}{}+{:03}-> claveRef: {} nRango: {}; prev: {:0.3f}; this: {:0.3f}; post: {:0.3f}'.format(
                                TB, TV, TV,
                                5,
                                claveRef,
                                nRango,
                                LOCLdictHistProb01[claveRef][nRango - 1],
                                LOCLdictHistProb01[claveRef][nRango],
                                LOCLdictHistProb01[claveRef][nRango + 1],
                            )
                        )
                    elif LOCLdictHistProb01[claveRef][nRango - 1] != 0 or LOCLdictHistProb01[claveRef][nRango + 1] != 0:
                        incrementoMinimo = 0.01
                        myLog.debug(
                            '{}{}{}+{:03}-> claveRef: {} nRango: {}; prev: {:0.3f}; this: {:0.3f}; post: {:0.3f}'.format(
                                TB, TV, TV,
                                1,
                                claveRef,
                                nRango,
                                LOCLdictHistProb01[claveRef][nRango - 1],
                                LOCLdictHistProb01[claveRef][nRango],
                                LOCLdictHistProb01[claveRef][nRango + 1],
                            )
                        )
                    incrementoFrecuencia = max(
                        incrementoMinimo, (
                            # (factorMovilidad[nBanda] * LOCLdictHistProb01[claveRef][nRango] * 2)
                            + (
                                factorMovilidad[nBanda] * 0.5 * (
                                    LOCLdictHistProb01[claveRef][nRango]
                                    + LOCLdictHistProb01[claveRef][nRango - 1]
                                )
                            )
                            + (
                                factorMovilidad[nBanda] * 0.5 * (
                                    LOCLdictHistProb01[claveRef][nRango]
                                    + LOCLdictHistProb01[claveRef][nRango + 1]
                                )
                            )
                        )
                    )
                LOCLdictHistProb01[claveMax][nRango] = round(LOCLdictHistProb01[claveRef][nRango] + incrementoFrecuencia, 3)
                LOCLlistHistProb01[nInputVar, 2, nRango] = round(LOCLdictHistProb01[claveRef][nRango] + incrementoFrecuencia, 3)
                myLog.debug(
                    '{}{}{}-> Rango: {} -> decrementoFrecuencia: {} incrementoFrecuencia: {} -> min/max: {:0.3f} / {:0.3f}'.format(
                        TB, TV, TV,
                        nRango,
                        decrementoFrecuencia,
                        incrementoFrecuencia,
                        LOCLdictHistProb01[claveMin][nRango],
                        LOCLdictHistProb01[claveMax][nRango],
                    )
                )
                if LOCLdictHistProb01[claveMax][nRango] - LOCLdictHistProb01[claveMin][nRango] < 0.05:
                    ampliarLimites = False
                    if nRango == 0:
                        if LOCLdictHistProb01[claveRef][nRango + 1] != 0:
                            ampliarLimites = True
                    elif nRango == len(histProb01PatronBandaX) - 1:
                        if LOCLdictHistProb01[claveRef][nRango - 1] != 0:
                            ampliarLimites = True
                    else:
                        if (
                            LOCLdictHistProb01[claveRef][nRango + 1] != 0
                            or LOCLdictHistProb01[claveRef][nRango - 1] != 0
                        ):
                            ampliarLimites = True
                    if ampliarLimites:
                        LOCLdictHistProb01[claveMin][nRango] -= 0.02
                        LOCLdictHistProb01[claveMax][nRango] += 0.03

                if LOCLdictHistProb01[claveMin][nRango] > 1:
                    LOCLdictHistProb01[claveMin][nRango] = 1
                    LOCLlistHistProb01[nInputVar, 0, nRango] = 1
                if LOCLdictHistProb01[claveMin][nRango] < 0:
                    LOCLdictHistProb01[claveMin][nRango] = 0
                    LOCLlistHistProb01[nInputVar, 0, nRango] = 0
                if LOCLdictHistProb01[claveMax][nRango] > 1:
                    LOCLdictHistProb01[claveMax][nRango] = 1
                    LOCLlistHistProb01[nInputVar, 2, nRango] = 1
                if LOCLdictHistProb01[claveMax][nRango] < 0:
                    LOCLdictHistProb01[claveMax][nRango] = 0
                    LOCLlistHistProb01[nInputVar, 2, nRango] = 0

            myLog.debug(f'{TB}{TV}Rangos admisibles:')
            # myLog.debug(f'LOCLdictHistProb01[claveRef]: {LOCLdictHistProb01[claveRef]}')
            try:
                ultimoNoZero = np.max(np.nonzero(LOCLdictHistProb01[claveMin])[0])
            except:
                ultimoNoZero = 0
            myLog.debug(f'{TB}{TV}{TV}-> LOCLdictHistProb01[claveMin]: {LOCLdictHistProb01[claveMin][:ultimoNoZero + 2]}')
            myLog.debug(f'{TB}{TV}{TV}-> LOCLdictHistProb01[claveMax]: {LOCLdictHistProb01[claveMax][:ultimoNoZero + 9]}')

        # if nInputVar >= 0:
        #     myLog.debug(f'{TB}-> valores de referencia: {histProb01PatronBandaX}')
        #     myLog.debug(f'{TB}{TV}-> Rango min admisible:   {LOCLdictHistProb01[claveMin]}')
        #     myLog.debug(f'{TB}{TV}-> Rango max admisible:   {LOCLdictHistProb01[claveMax]}')


        if mostrarGraficaHistograma:
            # rng = np.random.RandomState(10)  # deterministic random data
            # a = np.hstack((rng.normal(size=1000),
            #                rng.normal(loc=5, scale=2, size=1000)))
            _ = plt.hist(arrayBandaXClip.flatten(), bins=myNBins[nBanda], range=myRange[nBanda])  # arguments are passed to np.histogram
            if nBanda == nBandasRasterOutput:
                plt.title(f'Histograma para tipos de masa (banda {nBanda})')
            elif nBanda == nBandasRasterOutput - 1:
                plt.title(f'\nHistograma para tipos de bosque (banda {nBanda})')
            else:
                plt.title(f'Histograma para (banda {nBanda})-> variable {nInputVar}: {self_LOCLlistLstDasoVars[nInputVar][1]}')
            plt.show()

    # Descartado porque no funciona:
    # recortarRasterConShape( patronVectrNameConPath, mergedUniCellAllDasoVarsFileNameConPath )
    #===========================================================================
    return (
        LOCLoutputRangosFileTxtSinPath,
        LOCLoutputRangosFileNpzSinPath,
        nBandasRasterOutput,
        rasterDatasetAll,
        listaCeldasConDasoVarsOkPatron,
        LOCLdictHistProb01,
        LOCLlistHistProb01,
        myNBins,
        myRange,
        pctjTipoBosquePatronMasFrecuente1,
        codeTipoBosquePatronMasFrecuente1,
        pctjTipoBosquePatronMasFrecuente2,
        codeTipoBosquePatronMasFrecuente2,
        histProb01PatronBosque,
    )


# ==============================================================================
def mostrarExportarRangos(
        self_LOCLoutPathNameRuta,
        self_outputRangosFileNpzSinPath,
        self_LOCLdictHistProb01,
        self_LOCLlistHistProb01,
        self_nInputVars,
        self_myRange,
        self_myNBins,
        self_nFicherosDisponiblesPorTipoVariable,
        self_LOCLvarsTxtFileName=GLO.GLBLvarsTxtFileNamePorDefecto,
        self_LOCLlistLstDasoVars=GLO.GLBLlistLstDasoVarsPorDefecto,
    ):
    self_nBandasRasterOutput = self_nInputVars + 2

    #===========================================================================
    outputRangosFileTxtConPath = os.path.join(self_LOCLoutPathNameRuta, self_LOCLvarsTxtFileName)
    outputRangosFileNpzConPath = os.path.join(self_LOCLoutPathNameRuta, self_outputRangosFileNpzSinPath)

    outputRangosFileTxtControl = open(outputRangosFileTxtConPath, mode='w+')
    outputRangosFileTxtControl.write('Valores y rangos admisibles para el histograma de frecuencias de las variables analizadas.\n')

    myLog.debug('clidtwinx-> Rangos para cada variable en self_LOCLdictHistProb01[claveRef]:')
    for claveRef in self_LOCLdictHistProb01.keys():
        try:
            ultimoNoZero = np.max(np.nonzero(self_LOCLdictHistProb01[claveRef])[0])
        except:
            ultimoNoZero = 0
        myLog.debug(f'{TB}-> claveRef: {claveRef} -> num. de rangos: {len(self_LOCLdictHistProb01[claveRef])} -> self_LOCLdictHistProb01: {self_LOCLdictHistProb01[claveRef][:ultimoNoZero + 2]}')

    myLog.debug('\nclidtwinx-> Recorriendo bandas para guardar intervalos para el histograma de cada variable:')
    for nBanda in range(1, self_nBandasRasterOutput + 1):
        nInputVar = nBanda - 1
        if nInputVar < 0 or nInputVar >= self_nInputVars:
            continue
        claveRef = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_ref'
        claveMin = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_min'
        claveMax = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_max'
        # self_myRange[nBanda] = (self_LOCLlistLstDasoVars[nInputVar][2], self_LOCLlistLstDasoVars[nInputVar][3])
        # self_myNBins[nBanda] = self_LOCLlistLstDasoVars[nInputVar][4]
        if nBanda == self_nBandasRasterOutput:
            outputRangosFileTxtControl.write(f'\nTipoMasa{TB}Band{nBanda}{TB}\n')
        else:
            outputRangosFileTxtControl.write(f'\n{self_LOCLlistLstDasoVars[nInputVar][1]}{TB}Var{nInputVar}{TB}RangoVar:{TB}{self_myRange[nBanda][0]}{TB}{self_myRange[nBanda][1]}{TB}nClases{TB}{self_myNBins[nBanda]}\n')
        myLog.debug(f'{TB}-> nBanda: {nBanda}')
        myLog.debug(f'{TB}{TV}-> self_myRange: {self_myRange[nBanda]}')
        myLog.debug(f'{TB}{TV}-> nBins: {self_myNBins[nBanda]}')
        try:
            ultimoNoZero = np.max(np.nonzero(self_LOCLdictHistProb01[claveRef])[0])
        except:
            ultimoNoZero = 0

        myLog.debug(f'{TB}{TV}{TV}-> self_LOCLdictHistProb01[claveRef]: {self_LOCLdictHistProb01[claveRef][:ultimoNoZero + 2]}')
        for nRango in range(self_myNBins[nBanda]):
            self_LOCLdictHistProb01[claveRef][nRango] = round(self_LOCLdictHistProb01[claveRef][nRango], 3)
            self_LOCLdictHistProb01[claveMin][nRango] = round(self_LOCLdictHistProb01[claveMin][nRango], 3)
            self_LOCLdictHistProb01[claveMax][nRango] = round(self_LOCLdictHistProb01[claveMax][nRango], 3)
            self_LOCLlistHistProb01[nInputVar, 0, nRango] = round(self_LOCLlistHistProb01[nInputVar, 0, nRango], 3)
            self_LOCLlistHistProb01[nInputVar, 1, nRango] = round(self_LOCLlistHistProb01[nInputVar, 1, nRango], 3)
            self_LOCLlistHistProb01[nInputVar, 2, nRango] = round(self_LOCLlistHistProb01[nInputVar, 2, nRango], 3)

            limInf = nRango * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            limSup = (nRango + 1) * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            if claveRef in self_LOCLdictHistProb01.keys():
                if limInf < 10:
                    signoInf = '+'
                else:
                    signoInf = ''
                if limSup < 10:
                    signoSup = '+'
                else:
                    signoSup = ''
                valDef = round(100 * self_LOCLdictHistProb01[claveRef][nRango], 0)
                valInf = round(100 * self_LOCLdictHistProb01[claveMin][nRango], 0)
                valSup = round(100 * self_LOCLdictHistProb01[claveMax][nRango], 0)
                signoDef = '+' if valDef < 10 else ''
                if valDef != 0 or valInf != 0 or valSup > 5:
                    textoWrite = '{}{}nClase{}{:02}{}TramoVar->{}{:0.2f}{}{:0.2f}{}valDef{}{:0.2f}{}limInf{}{:0.2f}{}limSup{}{:0.2f}'.format(
                        TB, TV, TV,
                        nRango, TB,
                        TB, limInf,
                        TB, limSup, TB,
                        TB, valDef, TB,
                        TB, valInf, TB,
                        TB, valSup,
                        )
                    myLog.debug(f'{TB}{TV}{TV}{textoWrite}')
                    outputRangosFileTxtControl.write(f'{textoWrite}\n')
    outputRangosFileTxtControl.close()

    if os.path.exists(outputRangosFileNpzConPath):
        myLog.debug(f'{TB}-> clidnat-> Antes se va a eliminar el fichero npz existente: {outputRangosFileNpzConPath}')
        os.remove(outputRangosFileNpzConPath)
        if os.path.exists(outputRangosFileNpzConPath):
            myLog.debug(f'{TB}No se ha podido eliminar el fichero npz existente: {outputRangosFileNpzConPath}')
    np.savez_compressed(
        outputRangosFileNpzConPath,
        listaDasoVars=self_LOCLlistLstDasoVars,
        nInputVars=self_nInputVars,
        nBandasRasterOutput=self_nBandasRasterOutput,
        nFicherosDisponiblesPorTipoVariable=self_nFicherosDisponiblesPorTipoVariable,
        myRange=self_myRange[nBanda],
        dictHistProb01=self_LOCLdictHistProb01,
    )


# ==============================================================================
def infoSrcband(srcband):
    myLog.info(f'Tipo de datos de la banda= {gdal.GetDataTypeName(srcband.DataType)}')
    stats1 = srcband.GetStatistics(True, True)
    stats2 = srcband.ComputeStatistics(0)
    if stats1 is None or stats2 is None:
        exit
    myLog.info('Estadisticas guardadas en metadatos:')
    myLog.info('Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f' % (stats1[0], stats1[1], stats1[2], stats1[3]))
    myLog.info('Estadisticas recalculadas:')
    myLog.info('Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f' % (stats2[0], stats2[1], stats2[2], stats2[3]))
    # Tambien se puede conocer el minimo y el maximo con:
    # minimo = srcband.GetMinimum()
    # maximo = srcband.GetMaximum()
    # Y tambien con:
    # (minimo,maximo) = srcband.ComputeRasterMinMax(1)
    myLog.info('Otras caracteristicas de la capa:')
    myLog.info(f'No data value= {srcband.GetNoDataValue()}')
    myLog.info(f'Scale=         {srcband.GetScale()}')
    myLog.info(f'Unit type=     {srcband.GetUnitType()}')

    ctable = srcband.GetColorTable()
    if not ctable is None:
        myLog.info(f'Color table count = {ctable.GetCount()}')
        for i in range(0, ctable.GetCount()):
            entry = ctable.GetColorEntry(i)
            if not entry:
                continue
            myLog.info(f'Color entry RGB = {ctable.GetColorEntryAsRGB(i, entry)}')
    else:
        myLog.info('No ColorTable')
        # sys.exit(0)
    if not srcband.GetRasterColorTable() is None:
        myLog.info(f'Band has a color table with {srcband.GetRasterColorTable().GetCount()} entries.')
    else:
        myLog.info('No RasterColorTable')
    if srcband.GetOverviewCount() > 0:
        myLog.info(f'Band has {srcband.GetOverviewCount()} overviews.')
    else:
        myLog.info('No overviews')


# ==============================================================================
def mostrarListaDrivers():
    cnt = ogr.GetDriverCount()
    formatsList = []
    for i in range(cnt):
        driver = ogr.GetDriver(i)
        driverName = driver.GetName()
        if not driverName in formatsList:
            formatsList.append(driverName)
    formatsList.sort()
    for i in formatsList:
        myLog.info(i)


# ==============================================================================
def leerConfig(LOCL_configDictPorDefecto, LOCL_configFileNameCfg, LOCL_verbose=False):
    if LOCL_verbose:
        myLog.info('\n{:_^80}'.format(''))
        myLog.info('clidtwinx-> Fichero de configuracion:  {}'.format(LOCL_configFileNameCfg))
    # ==========================================================================
    if not os.path.exists(LOCL_configFileNameCfg):
        if LOCL_verbose:
            myLog.info(f'{TB}  clidtwinx-> Fichero no encontrado: se crea con valores por defecto')
        # En ausencia de fichero de configuracion, uso valores por defecto y los guardo en un nuevo fichero cfg
        config = RawConfigParser()
        config.optionxform = str  # Avoid change to lowercase

        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            grupoParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion][1]
            if not grupoParametroConfiguracion in config.sections():
                if LOCL_verbose and False:
                    myLog.debug(f'{TB}{TV}clidtwinx-> grupoParametros nuevo: {grupoParametroConfiguracion}')
                config.add_section(grupoParametroConfiguracion)
        # Puedo agregar otras secciones:
        config.add_section('Custom')

        if LOCL_verbose and False:
            myLog.debug(f'{TB}{TV}clidtwinx-> Lista de parametros de configuracion por defecto:')
        for nombreParametroDeConfiguracion in LOCL_configDictPorDefecto.keys():
            listaParametroConfiguracion = LOCL_configDictPorDefecto[nombreParametroDeConfiguracion]
            valorParametroConfiguracion = listaParametroConfiguracion[0]
            grupoParametroConfiguracion = listaParametroConfiguracion[1]
            tipoParametroConfiguracion = listaParametroConfiguracion[2]
            descripcionParametroConfiguracion = listaParametroConfiguracion[3]

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

            listaConcatenada = '{}|+|{}|+|{}'.format(
                str(valorParametroConfiguracion),
                str(tipoParametroConfiguracion),
                str(descripcionParametroConfiguracion)
            )

            config.set(
                grupoParametroConfiguracion,
                nombreParametroDeConfiguracion,
                listaConcatenada
            )
            if LOCL_verbose and False:
                myLog.debug(f'{TB}{TV}{TV}-> {nombreParametroDeConfiguracion}: {valorParametroConfiguracion} (tipo {tipoParametroConfiguracion})-> {descripcionParametroConfiguracion}')

        try:
            with open(LOCL_configFileNameCfg, mode='w+') as configfile:
                config.write(configfile)
        except:
            myLog.critical(f'\nclidtwinx-> ATENCION, revisar caracteres no admitidos en el fichero de configuracion: {LOCL_configFileNameCfg}')
            myLog.critical(f'{TB}Ejemplos: vocales acentuadas, ennes, cedillas, flecha dcha (->), etc.')

    # Asigno los parametros de configuracion a varaible globales:
    config = RawConfigParser()
    config.optionxform = str  # Avoid change to lowercase

    # Confirmo que se ha creado correctamente el fichero de configuracion
    if not os.path.exists(LOCL_configFileNameCfg):
        myLog.error(f'\nclidtwinx-> ATENCION: fichero de configuracion no encontrado ni creado: {LOCL_configFileNameCfg}')
        myLog.error(f'{TB}-> Revisar derechos de escritura en la ruta en la que esta la aplicacion')
        sys.exit(0)

    try:
        LOCL_configDict = {}
        config.read(LOCL_configFileNameCfg)
        if LOCL_verbose:
            myLog.info(f'{TB}-> clidtwinx-> Parametros de configuracion (guardados en {LOCL_configFileNameCfg}):')
        for grupoParametroConfiguracion in config.sections():
            for nombreParametroDeConfiguracion in config.options(grupoParametroConfiguracion):
                strParametroConfiguracion = config.get(grupoParametroConfiguracion, nombreParametroDeConfiguracion)
                listaParametroConfiguracion = strParametroConfiguracion.split('|+|')
                valorPrincipal = listaParametroConfiguracion[0]
                if len(listaParametroConfiguracion) > 1:
                    tipoParametroConfiguracion = listaParametroConfiguracion[1]
                else:
                    tipoParametroConfiguracion = 'str'
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
                myLog.debug(
                    '{}{}-> parametro {:<35} -> {}'.format(
                        TB, TV,
                        nombreParametroDeConfiguracion,
                        LOCL_configDict[nombreParametroDeConfiguracion]
                    )
                )

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
                if LOCL_verbose or True:
                    myLog.warning(
                        f'{TB}-> AVISO: el parametro <{nombreParametroDeConfiguracion}> no esta en'
                        f'el fichero de configuacion; se adopta valor por defecto: <{valorParametroConfiguracion}>'
                    )

        config_ok = True
    except:
        myLog.error(f'clidtwinx-> Error al leer la configuracion del fichero: {LOCL_configFileNameCfg}')
        config_ok = False
        sys.exit(0)
    # myLog.debug(f'{TB}{TV}clidtwinx-> LOCL_configDict: {LOCL_configDict}')

    if LOCL_verbose:
        myLog.info('{:=^80}'.format(''))
    return LOCL_configDict
    # ==========================================================================


# ==============================================================================
class myClass(object):
    pass

# ==============================================================================
def fxn():
    warnings.warn("deprecated", DeprecationWarning)

# ==============================================================================
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()
# ==============================================================================

ogr.RegisterAll()
gdal.UseExceptions()

# ==============================================================================
if __name__ == '__main__':
    pass

