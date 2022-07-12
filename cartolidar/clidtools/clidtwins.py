#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Module included in cartolidar project (clidtools package)
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidtwins provides classes and functions that can be used to search for
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
from operator import itemgetter, attrgetter
from configparser import RawConfigParser
# import random

import numpy as np
import numpy.ma as ma
from scipy.spatial import distance_matrix
from scipy.spatial import distance as distance_hist
# from scipy.spatial import KDTree
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
    print('clidtwins-> No se puede importar gdal "from osgeo", se intenta directamente ("import gdal").')
    gdalOk = False
if not gdalOk:
    try:
        import gdal, ogr, osr, gdalnumeric, gdalconst
        sys.stdout.write('           gdal importado ok con "import gdal".\n')
        gdalOk = True
    except:
        gdalOk = False
        print('clidtwins-> Error importando gdal.')
        sys.exit(0)
# ==============================================================================

'''
configuracion original que da error:
llvmlite==0.33.0+1.g022ab0f
numba==0.50.1
numpy==1.21.6
'''
try:
    from cartolidar.clidtools.clidtwcfg import GLO
except:
    sys.stderr.write(f'qlidtwins-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).')
    sys.stderr.write('\t-> Se importa clidconfig desde clidtwcfg del directorio local {os.getcwd()}/clidtools.')
    from clidtools.clidtwcfg import GLO
try:
    # GLO.GLBLcompilaConNumbaPorDefecto = False
    if GLO.GLBLcompilaConNumbaPorDefecto:
        import numba as nb
        numbaOk = True
        # print('clidtwins-> numba ok')
        # print('numba version:', nb.__version__)
        # print('numpy version:', np.__version__)
        # Usar numba=0.53.00 (no uso el 0.55.0 porque requiere python 3.10)
        # Requiere:
        #  llvmlite==0.36.0
        #  NumPy >=1.15 (uso 1.19.0)
        # Lo intento instalar con:
        #  conda install numba==0.53.0
        #  Pero me da error por compatibilidad de paquetes
        # Si funciona instalandolo con:
        #  conda install llvmlite==0.36.0
        #   Esto actualiza numba:
        # The following packages will be UPDATED:
        #   llvmlite                            0.33.0-py37ha925a31_0 --> 0.36.0-py37h34b8924_4
        #   numba                               0.50.1-py37h47e9c7a_0 --> 0.53.0-py37hf11a4ad_0
        # Ver https://github.com/alan-turing-institute/sktime/issues/764
        # https://pypi.org/project/numba/0.53.1/
    else:
        numbaOk = False
        print('clidtwins-> numba NO usar')
except:
    numbaOk = False
    print('clidtwins-> numba error')

# numbaOk = False


# Recuperar la captura de errores de importacion en la version beta
try:
# if True:
    # from cartolidar.clidtools.clidtwcfg import GLO
    from cartolidar.clidtools import clidtwinx
    from cartolidar.clidtools import clidtwinp
    from cartolidar.clidtools import clidtwinb
    from cartolidar.clidax import clidconfig
    from cartolidar.clidax import clidraster
except:
    sys.stderr.write(f'qlidtwins-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).\n')
    sys.stderr.write('\t-> Se importa clidconfig desde clidtwcfg del directorio local {os.getcwd()}/clidtools.\n')
    from clidtools.clidtwcfg import GLO
    from clidtools import clidtwinx
    from clidtools import clidtwinp
    from clidtools import clidtwinb
    from clidax import clidconfig
    from clidax import clidraster


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
myLog.debug('clidtwins-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================


# ==============================================================================
class DasoLidarSource:
    """Main Class of clidtwins module with the methods needed to search source
files, analyze Dasolidar Variables (DLVs) and check o locate similar areas to
the reference one(s) in terms of DLVs."""

    # ==========================================================================
    # Se leen los argumentos y se convierte la listLstDasoVars en listas individuales:
    # FileTypes, NickNames, RangoLinf, RangoLsup, NumClases, Movilidad, Ponderado,
    def __init__(
            self,
            LCL_leer_extra_args=0,  # optional
            LCL_menuInteractivo=GLO.GLBLmenuInteractivoPorDefecto,  # extra: 0
            LCL_outRasterDriver=GLO.GLBLoutRasterDriverPorDefecto,  # extra: 'GTiff'
            LCL_outputSubdirNew=GLO.GLBLoutputSubdirNewPorDefecto,  # extra: 'dasoLayers'
            LCL_cartoMFErecorte=GLO.GLBLcartoMFErecortePorDefecto,  # extra: 'mfe50rec'
            LCL_varsTxtFileName=GLO.GLBLvarsTxtFileNamePorDefecto,  # extra: 'rangosDeDeferencia.txt'
            LCL_ambitoTiffNuevo=GLO.GLBLambitoTiffNuevoPorDefecto,  # extra: 'loteAsc'
            LCL_noDataTiffProvi=GLO.GLBLnoDataTiffProviPorDefecto,  # extra: -8888
            LCL_noDataTiffFiles=GLO.GLBLnoDataTiffFilesPorDefecto,  # extra: -9999
            LCL_noDataTipoDMasa=GLO.GLBLnoDataTipoDMasaPorDefecto,  # extra: 255
            LCL_umbralMatriDist=GLO.GLBLumbralMatriDistPorDefecto,  # extra: 20
            LCL_verbose=__verbose__,  # optional
        ):
        """Instantiation of DasoLidarSource Class with asignation of some optional extra arguments
that usually take the default values (from configuration file or clidtwcfg.py module
    Attributes
    ----------
    LCL_leer_extra_args : bool
        Default: False (optional)
    LCL_menuInteractivo
        Default: param GLBLmenuInteractivoPorDefecto from cfg file (0)
    LCL_outRasterDriver : str
        Default: param GLBLoutRasterDriverPorDefecto from cfg file ('GTiff')
    LCL_outputSubdirNew : str
        Default: param GLBLoutputSubdirNewPorDefecto from cfg file ('dasoLayers')
    LCL_cartoMFErecorte : str
        Default: param GLBLcartoMFErecortePorDefecto from cfg file ('mfe50rec')
    LCL_varsTxtFileName : str
        Default: param GLBLvarsTxtFileNamePorDefecto from cfg file ('rangosDeDeferencia.txt')
    LCL_ambitoTiffNuevo : str
        Default: param GLBLambitoTiffNuevoPorDefecto from cfg file ('loteAsc')
    LCL_noDataTiffProvi : int
        Default: param GLBLnoDataTiffProviPorDefecto from cfg file (-8888)
    LCL_noDataTiffFiles : int
        Default: param GLBLnoDataTiffFilesPorDefecto from cfg file (-9999)
    LCL_noDataTipoDMasa : int
        Default: param GLBLnoDataTipoDMasaPorDefecto from cfg file (255)
    LCL_umbralMatriDist : int
        Default: param GLBLumbralMatriDistPorDefecto from cfg file (20)
    LCL_verbose : bool
        Default: __verbose__ (optional)
"""
        self.LOCLverbose = LCL_verbose

        # Esto parece redundante con el valor por defecto de estos parametros.
        # Sin embargo, no lo es porque el argumento LCL_leer_extra_args,
        # fuerza, si es True, a usar los parametros por defecto. Uso esta modalidad
        # a pesar de que la forma canonica de python para argumentos por defecto es
        # usar None y asignar despues el valor que corresponda si el parametro es None.
        if LCL_leer_extra_args:
            self.GLBLmenuInteractivo = LCL_menuInteractivo
            self.GLBLoutRasterDriver = LCL_outRasterDriver
            self.GLBLoutputSubdirNew = LCL_outputSubdirNew
            self.GLBLcartoMFErecorte = LCL_cartoMFErecorte
            self.GLBLvarsTxtFileName = LCL_varsTxtFileName
            self.GLBLambitoTiffNuevo = LCL_ambitoTiffNuevo
            self.GLBLnoDataTiffProvi = LCL_noDataTiffProvi
            self.GLBLnoDataTiffFiles = LCL_noDataTiffFiles
            self.GLBLnoDataTipoDMasa = LCL_noDataTipoDMasa
            self.GLBLumbralMatriDist = LCL_umbralMatriDist
        else:
            self.GLBLmenuInteractivo = GLO.GLBLmenuInteractivoPorDefecto  # p.ej.: 0
            self.GLBLoutRasterDriver = GLO.GLBLoutRasterDriverPorDefecto  # p.ej.: 'GTiff'
            self.GLBLoutputSubdirNew = GLO.GLBLoutputSubdirNewPorDefecto  # p.ej.: 'dasoLayers'
            self.GLBLcartoMFErecorte = GLO.GLBLcartoMFErecortePorDefecto  # p.ej.: 'mfe50rec'
            self.GLBLvarsTxtFileName = GLO.GLBLvarsTxtFileNamePorDefecto  # p.ej.: 'rangosDeDeferencia.txt'
            self.GLBLambitoTiffNuevo = GLO.GLBLambitoTiffNuevoPorDefecto  # p.ej.: 'loteAsc'
            self.GLBLnoDataTiffProvi = GLO.GLBLnoDataTiffProviPorDefecto  # p.ej.: -8888
            self.GLBLnoDataTiffFiles = GLO.GLBLnoDataTiffFilesPorDefecto  # p.ej.: -9999
            self.GLBLnoDataTipoDMasa = GLO.GLBLnoDataTipoDMasaPorDefecto  # p.ej.: 255
            self.GLBLumbralMatriDist = GLO.GLBLumbralMatriDistPorDefecto  # p.ej.: 20
        if self.GLBLnoDataTipoDMasa == 255 or self.GLBLnoDataTipoDMasa == 0:
            self.outputGdalDatatypeTipoMasa = gdal.GDT_Byte
            self.outputNpDatatypeTipoMasa = np.uint8
        else:
            self.outputGdalDatatypeTipoMasa = gdal.GDT_Float32
            self.outputNpDatatypeTipoMasa = np.float32
        self.GLBLnoDataDistancia = 9999

        # Se inician estos atributos por si no se ejecuta el metodo setRangeUTM<>
        self.LOCLrutaAscRaizBase = None 
        self.LOCLmarcoCoordMiniX = 0
        self.LOCLmarcoCoordMaxiX = 0
        self.LOCLmarcoCoordMiniY = 0
        self.LOCLmarcoCoordMaxiY = 0
        self.marcoCoordEjecutado = False
        self.marcoCoordDisponible = False
        self.usarVectorFileParaDelimitarZona = False
        self.GLBLmarcoPatronTest = GLO.GLBLmarcoPatronTestPorDefecto
        self.idInputDir = None
        self.rasterDatasetAll = None
        self.dictHistProb01 = None

    # ==========================================================================
    def setRangeUTM(
            self,
            LCL_marcoCoordMiniX=None,  # opcional
            LCL_marcoCoordMaxiX=None,  # opcional
            LCL_marcoCoordMiniY=None,  # opcional
            LCL_marcoCoordMaxiY=None,  # opcional
            LCL_marcoPatronTest=None,  # extra: 0
            LCL_rutaAscRaizBase=None,  # opcional
            LCL_patronVectrName=None,  # opcional
            LCL_patronLayerName=None,  # opcional
            LCL_testeoVectrName=None,  # opcional
            LCL_testeoLayerName=None,  # opcional
            LCL_verbose=None,
        ):
        f"""Method for seting UTM range for analysis area
        Attributes
        ----------
        LCL_marcoCoordMiniX : int
            Default: None
        LCL_marcoCoordMaxiX : int
            Default: None
        LCL_marcoCoordMiniY : int
            Default: None
        LCL_marcoCoordMaxiY : int
            Default: None
        LCL_marcoPatronTest = bool
            Default: None -> {GLO.GLBLmarcoPatronTestPorDefecto} from cfg file or clidtwcfg.py module
        LCL_rutaAscRaizBase : str
            Default: None -> {GLO.GLBLrutaAscRaizBasePorDefecto} (optional)
        LCL_patronVectrName : str
            Default: None (optional)
        LCL_patronLayerName : str
            Default: None (optional)
        LCL_testeoVectrName : str
            Default: None (optional)
        LCL_testeoLayerName : str
            Default: None (optional)
        """

        if not LCL_verbose is None:
            self.LOCLverbose = LCL_verbose

        self.marcoCoordEjecutado = True

        if LCL_marcoPatronTest is None:
            self.GLBLmarcoPatronTest = GLO.GLBLmarcoPatronTestPorDefecto
        else:
            self.GLBLmarcoPatronTest = LCL_marcoPatronTest

        if LCL_marcoCoordMiniX is None:
            self.LOCLmarcoCoordMiniX = GLO.GLBLmarcoCoordMiniXPorDefecto
        else:
            self.LOCLmarcoCoordMiniX = LCL_marcoCoordMiniX
        if LCL_marcoCoordMaxiX is None:
            self.LOCLmarcoCoordMaxiX = GLO.GLBLmarcoCoordMaxiXPorDefecto
        else:
            self.LOCLmarcoCoordMaxiX = LCL_marcoCoordMaxiX
        if LCL_marcoCoordMiniY is None:
            self.LOCLmarcoCoordMiniY = GLO.GLBLmarcoCoordMiniYPorDefecto
        else:
            self.LOCLmarcoCoordMiniY = LCL_marcoCoordMiniY
        if LCL_marcoCoordMaxiY is None:
            self.LOCLmarcoCoordMaxiY = GLO.GLBLmarcoCoordMaxiYPorDefecto
        else:
            self.LOCLmarcoCoordMaxiY = LCL_marcoCoordMaxiY

        if self.LOCLmarcoCoordMiniX > 0:
            self.marcoCoordDisponible = True
            self.LOCLmarcoLibreMiniX = False
        else:
            self.LOCLmarcoCoordMiniX = 0
            self.LOCLmarcoLibreMiniX = True
        if self.LOCLmarcoCoordMaxiX > 0:
            self.marcoCoordDisponible = True
            self.LOCLmarcoLibreMaxiX = False
        else:
            self.LOCLmarcoCoordMaxiX = 0
            self.LOCLmarcoLibreMaxiX = True
        if self.LOCLmarcoCoordMiniY > 0:
            self.marcoCoordDisponible = True
            self.LOCLmarcoLibreMiniY = False
        else:
            self.LOCLmarcoCoordMiniY = 0
            self.LOCLmarcoLibreMiniY = True
        if self.LOCLmarcoCoordMaxiY > 0:
            self.marcoCoordDisponible = True
            self.LOCLmarcoLibreMaxiY = False
        else:
            self.LOCLmarcoCoordMaxiY = 0
            self.LOCLmarcoLibreMaxiY = True

        # if LCL_rutaAscRaizBase is None:
        #     self.LOCLrutaAscRaizBase = os.path.abspath(GLO.GLBLrutaAscRaizBasePorDefecto)
        # else:
        #     self.LOCLrutaAscRaizBase = os.path.abspath(LCL_rutaAscRaizBase)
        self.verificarRutaAscRaiz(
            LCL_rutaAscRaizBase=LCL_rutaAscRaizBase,
        )

        if LCL_patronVectrName is None:
            self.LOCLpatronVectrName = os.path.abspath(GLO.GLBLpatronVectrNamePorDefecto)
        else:
            self.LOCLpatronVectrName = os.path.abspath(LCL_patronVectrName)
        if LCL_patronLayerName is None:
            self.LOCLpatronLayerName = GLO.GLBLpatronLayerNamePorDefecto
        else:
            self.LOCLpatronLayerName = LCL_patronLayerName
        if LCL_testeoVectrName is None:
            self.LOCLtesteoVectrName = os.path.abspath(GLO.GLBLtesteoVectrNamePorDefecto)
        else:
            self.LOCLtesteoVectrName = os.path.abspath(LCL_testeoVectrName)
        if LCL_testeoLayerName is None:
            self.LOCLtesteoLayerName = GLO.GLBLtesteoLayerNamePorDefecto
        else:
            self.LOCLtesteoLayerName = LCL_testeoLayerName

        myLog.info('\n{:_^80}'.format(''))
        if self.GLBLmarcoPatronTest:
            if (
                self.LOCLmarcoCoordMiniX != 0
                and self.LOCLmarcoCoordMaxiX != 0
                and self.LOCLmarcoCoordMiniY != 0
                and self.LOCLmarcoCoordMaxiY != 0
            ):
                myLog.warning('\nclidtwins-> AVISO: Se ha proporcionado rango de coordenadas y GLBLmarcoPatronTest = True')
                myLog.warning(f'{TB}-> Se adopta la envolvente del rango y los ficheros de referencia y test.')

            # if hasattr(self, 'LOCLpatronVectrName') and hasattr(self, 'LOCLpatronLayerName'):
            #     (usarVectorFileParaDelimitarZona, patronVectrNameConPath) = verificarExistencia(self.LOCLpatronVectrName)
            # else:
            #     (usarVectorFileParaDelimitarZona, patronVectrNameConPath) = verificarExistencia(GLO.GLBLpatronVectrNamePorDefecto)
            #     if usarVectorFileParaDelimitarZona:
            #         self.LOCLpatronVectrName = GLO.GLBLpatronVectrNamePorDefecto
            #         self.LOCLpatronLayerName = GLO.GLBLpatronLayerNamePorDefecto

            envolventePatron = clidtwinx.obtenerExtensionDeCapaVectorial(
                self.LOCLrutaAscRaizBase,
                self.LOCLpatronVectrName,
                LOCLlayerName=self.LOCLpatronLayerName,
                LOCLverbose=self.LOCLverbose,
            )
            if not envolventePatron is None:
                if self.LOCLmarcoCoordMiniX != 0:
                    self.LOCLmarcoCoordMiniX = min(
                        self.LOCLmarcoCoordMiniX,
                        envolventePatron[0]
                    )
                if self.LOCLmarcoCoordMaxiX != 0:
                    self.LOCLmarcoCoordMaxiX = max(
                        self.LOCLmarcoCoordMaxiX,
                        envolventePatron[1]
                    )
                if self.LOCLmarcoCoordMiniY != 0:
                    self.LOCLmarcoCoordMiniY = min(
                        self.LOCLmarcoCoordMiniY,
                        envolventePatron[2]
                    )
                if self.LOCLmarcoCoordMaxiY != 0:
                    self.LOCLmarcoCoordMaxiY = max(
                        self.LOCLmarcoCoordMaxiY,
                        envolventePatron[3]
                    )
                self.usarVectorFileParaDelimitarZona = True
            else:
                myLog.warning('\nclidtwins-> AVISO: identificando rango de coordenadas-> no esta disponible el fichero: {}'.format(self.LOCLpatronVectrName))
                myLog.warning(f'{TB}-> Ruta base: {self.LOCLrutaAscRaizBase}')
                # sys.exit(0)
            envolventeTesteo = clidtwinx.obtenerExtensionDeCapaVectorial(
                self.LOCLrutaAscRaizBase,
                self.LOCLtesteoVectrName,
                LOCLlayerName=self.LOCLtesteoLayerName,
                LOCLverbose=self.LOCLverbose,
            )
            if not envolventeTesteo is None:
                self.LOCLmarcoCoordMiniX = min(
                    self.LOCLmarcoCoordMiniX,
                    envolventeTesteo[0]
                )
                self.LOCLmarcoCoordMaxiX = max(
                    self.LOCLmarcoCoordMaxiX,
                    envolventeTesteo[1]
                )
                self.LOCLmarcoCoordMiniY = min(
                    self.LOCLmarcoCoordMiniY,
                    envolventeTesteo[2]
                )
                self.LOCLmarcoCoordMaxiY = max(
                    self.LOCLmarcoCoordMaxiY,
                    envolventeTesteo[3]
                )
                self.usarVectorFileParaDelimitarZona = True

            if envolventeTesteo is None:
                myLog.info('clidtwins-> Se adopta la envolvente del shapes de referencia (patron) -no se dispone de shape de chequeo (testeo)-:')
            else:
                myLog.info('clidtwins-> Se adopta la envolvente de los shapes de referencia (patron) y chequeo (testeo):')
            myLog.info(
                '{}-> X: {:10.2f} {:10.2f} -> {:4.0f} m'.format(
                    TB,
                    self.LOCLmarcoCoordMiniX, self.LOCLmarcoCoordMaxiX,
                    self.LOCLmarcoCoordMaxiX - self.LOCLmarcoCoordMiniX
                )
            )
            myLog.info(
                '{}-> Y: {:10.2f} {:10.2f} -> {:4.0f} m'.format(
                    TB,
                    self.LOCLmarcoCoordMiniY, self.LOCLmarcoCoordMaxiY,
                    self.LOCLmarcoCoordMaxiY - self.LOCLmarcoCoordMiniY
                )
            )
        elif not self.marcoCoordDisponible:
            myLog.warning(
                'clidtwins-> AVISO: tras ejecutar el metodo .setRangeUTM\n'
                f'{TB}no se han establecido coordenadas para la zona de estudio.'
            )
        # myLog.info('{:=^80}'.format(''))

    # ==========================================================================
    def searchSourceFiles(
            self,
            LCL_listLstDasoVars=None,  # optional (si existe, prevalece sobre el siguiente)
            LCL_listaTxtDasoVarsFileTypes=None,  # optional (alternativa simplificada al anterior en formato str o list)
            LCL_nClasesDasoVars=None,  # optional
            LCL_trasferDasoVars=None,  # optional
            LCL_nPatronDasoVars=None,  # optional

            LCL_rutaAscRaizBase=None,  # opcional
            LCL_nivelSubdirExpl=None,  # opcional
            LCL_outputSubdirNew=None,  # opcional
            LCL_verbose=None,
        ):
        f"""Search asc files with dasoLidar variables
        Attributes
        ----------
        LCL_listLstDasoVars : list
            Default: None (optional)
        LCL_listaTxtDasoVarsFileTypes : list or str
            Default: None (optional)
        LCL_nClasesDasoVars : int
            Default: None (optional)
        LCL_trasferDasoVars : int
            Default: None (optional)
        LCL_nPatronDasoVars : int
            Default: None (optional)

        LCL_rutaAscRaizBase : str
            Default: None -> {GLO.GLBLrutaAscRaizBasePorDefecto}
        LCL_nivelSubdirExpl : int
            Default: None -> {GLO.GLBLnivelSubdirExplPorDefecto} (optional)
        LCL_outputSubdirNew : str
            Default: None -> {GLO.GLBLoutputSubdirNewPorDefecto} (optional)
        """

        if not LCL_verbose is None:
            self.LOCLverbose = LCL_verbose

        # if hasattr(self, 'LOCLpatronVectrName') and hasattr(self, 'LOCLpatronLayerName'):
        #     myLog.warning('\nclidtwins-> AVISO: Se ha proporcionado rango de coordenadas y GLBLmarcoPatronTest = True')
        #     myLog.warning('{TB}-> Se adopta la envolvente del rango y los ficheros de referencia y test.')

        # ======================================================================
        self.verificarlistaDasoVars(
            LCL_listLstDasoVars=LCL_listLstDasoVars,
            LCL_listaTxtDasoVarsFileTypes=LCL_listaTxtDasoVarsFileTypes,
            LCL_nClasesDasoVars=LCL_nClasesDasoVars,
            LCL_trasferDasoVars=LCL_trasferDasoVars,
            LCL_nPatronDasoVars=LCL_nPatronDasoVars,
        )
        # if LCL_rutaAscRaizBase is None:
        #     self.LOCLrutaAscRaizBase = os.path.abspath(GLO.GLBLrutaAscRaizBasePorDefecto)
        # else:
        #     self.LOCLrutaAscRaizBase = os.path.abspath(LCL_rutaAscRaizBase)
        self.verificarRutaAscRaiz(
            LCL_rutaAscRaizBase=LCL_rutaAscRaizBase,
        )

        if LCL_nivelSubdirExpl is None or not type(LCL_nivelSubdirExpl) == int:
            self.LOCLnivelSubdirExpl = GLO.GLBLnivelSubdirExplPorDefecto
        else:
            self.LOCLnivelSubdirExpl = LCL_nivelSubdirExpl
        if LCL_outputSubdirNew is None:
            self.LOCLoutputSubdirNew = GLO.GLBLoutputSubdirNewPorDefecto
        else:
            self.LOCLoutputSubdirNew = LCL_outputSubdirNew

        # ======================================================================
        self.idInputDir = os.path.basename(self.LOCLrutaAscRaizBase)
        self.verificarMarcoCoord()
        # ======================================================================

        # ======================================================================
        myLog.info('\n{:_^80}'.format(''))
        myLog.info('clidtwins-> Explorando directorios...')
        myLog.info(f'{TB}-> Directorio raiz para los ficheros dasolidar (asc):')
        myLog.info('{}{}{}'.format(TB, TV, self.LOCLrutaAscRaizBase))
        # myLog.info(f'{TB}-> Identificador de este lote de ficheros -> IdDir: {}'.format(self.idInputDir))
        if self.LOCLnivelSubdirExpl:
            myLog.info(f'{TB}-> Se van a explorar subdirectorios hasta nivel: {self.LOCLnivelSubdirExpl}')
        else:
            myLog.info(f'{TB}-> Se van a explorar subdirectorios hasta el ultimo nivel')
        listaDirsExcluidos = [self.LOCLoutputSubdirNew]
        myLog.info(f'{TB}-> Directorios excluidos:')
        for dirExcluido in listaDirsExcluidos:
            myLog.info(f'{TB}{TV}{os.path.join(self.LOCLrutaAscRaizBase, dirExcluido)}')
        myLog.info('{:=^80}'.format(''))

        myLog.info('\n{:_^80}'.format(''))
        myLog.info('clidtwins-> Ficheros encontrados:')
        if not self.marcoCoordDisponible:
            myLog.info(f'{TB}-> Sin restricciones de coordendas porque no se han pre-establecido coordenadas para la zona de estudio.')
        elif not TRNS_buscarBloquesSoloDentroDelMarcoUTM and not self.GLBLmarcoPatronTest:
            myLog.info(f'{TB}-> Sin restricciones de coordendas porque se ha desabilitado temporalmente esta opcion.')
        else:
            if self.GLBLmarcoPatronTest:
                myLog.info(f'{TB}-> Que solapen con la envolvente de los shapes de referencia (patron) y chequeo (testeo):')
            else:
                myLog.info(f'{TB}-> Dentro de las coordenadas establecidas en linea de comandos o configuracion por defecto:')
            myLog.info(
                '{}{}X {:10.2f} - {:10.2f} -> {:4.0f} m:'.format(
                    TB, TV,
                    self.LOCLmarcoCoordMiniX, self.LOCLmarcoCoordMaxiX,
                    self.LOCLmarcoCoordMaxiX - self.LOCLmarcoCoordMiniX
                )
            )
            myLog.info(
                '{}{}Y {:10.2f} - {:10.2f} -> {:4.0f} m:'.format(
                    TB, TV,
                    self.LOCLmarcoCoordMiniY, self.LOCLmarcoCoordMaxiY,
                    self.LOCLmarcoCoordMaxiY - self.LOCLmarcoCoordMiniY
                )
            )

        # ======================================================================
        # Listas de ficheros reunidas por tipoDeFichero
        self.inFilesListAllTypes = []
        for nInputVar, miTipoDeFicheroDasoLayer in enumerate(self.LOCLlistaDasoVarsFileTypes):
            if self.LOCLnPatronDasoVars != 0 and nInputVar >= self.LOCLnPatronDasoVars:
                break
            miDasoVarNickName = self.LOCLlistaDasoVarsNickNames[nInputVar]
            if nInputVar < self.nInputVars:
                myLog.info('-> Tipo {}: > Variable: {} - Identificador del tipo de fichero: {}'.format(nInputVar, miDasoVarNickName, miTipoDeFicheroDasoLayer))
            if miDasoVarNickName.startswith('MFE') or miDasoVarNickName == 'TMasa':
                myLog.debug(f'{TB}{TV}-> No requiere explorar directorios')
                continue

            dirIterator = iter(os.walk(self.LOCLrutaAscRaizBase))
            # dirpath, dirnames, filenames = next(dirIterator)
            # dirpathPrevio = os.path.abspath(os.path.join(self.LOCLrutaAscRaizBase, '..'))
            # dirpathPrevio = self.LOCLrutaAscRaizBase
            infilesX = []
            for dirpathOk, dirnames, filenames in dirIterator:
                if miDasoVarNickName == 'MFE' or miDasoVarNickName == 'TipoMasa':
                    # El MFE se obtiene de una capa vectorial y el tipo de masa por ahoraa no lo uso (se generaria en esta aplicacion)
                    continue
                if dirpathOk.endswith(self.LOCLoutputSubdirNew):
                    myLog.debug(f'{TB}{TV}-> Saltando el directorio {dirpathOk}')
                    continue

                subDirExplorado = dirpathOk.replace(self.LOCLrutaAscRaizBase, '')
                if dirpathOk == self.LOCLrutaAscRaizBase:
                    nivelDeSubdir = 1
                elif not '/' in subDirExplorado and not '\\' in subDirExplorado:
                    nivelDeSubdir = 1
                else:
                    nivelDeSubdir = subDirExplorado.count('/') + subDirExplorado.count('\\') + 1
                if self.LOCLnivelSubdirExpl and nivelDeSubdir > self.LOCLnivelSubdirExpl:
                    if self.LOCLverbose == 3:
                        myLog.debug(f'{TB}{TV}Se ha alcanzado el nivel de directorios maximo ({self.LOCLnivelSubdirExpl})\n')
                    continue
                else:
                    if self.LOCLverbose == 3:
                        myLog.debug(f'{TB}Explorando nivel de subdirectorios {nivelDeSubdir} de {self.LOCLnivelSubdirExpl}')
                    pass

                excluirDirectorio = False
                for dirExcluido in listaDirsExcluidos:
                    if dirpathOk == os.path.join(self.LOCLrutaAscRaizBase, dirExcluido):
                        excluirDirectorio = True
                        break
                if excluirDirectorio:
                    myLog.debug(f'\n{TB}-> Directorio excluido: {dirpathOk}')
                    continue
                myLog.debug(f'{TB}-> Explorando directorio: {dirpathOk}')
                if len(filenames) == 0:
                    myLog.debug(f'{TB}{TV}-> No hay ficheros; se pasa al siguiente directorio')
                    continue

                #===================================================================
                try:
                    # Si se ha establecido marco UTM se incorporan los bloques
                    # que esten dentro del marco; en caso contrario, todos.
                    # Siempre y cuando tengan todas las variables dasoLidar.
                    if (
                        self.marcoCoordDisponible
                        and TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    ):
                        filenamesSeleccionadosX = [
                            filename for filename in filenames
                            if (
                                miTipoDeFicheroDasoLayer.upper() in filename.upper()
                                and filename[-4:].upper() == '.ASC'
                                and (self.LOCLmarcoLibreMiniX or (int(filename[:3]) * 1000) + 2000 >= self.LOCLmarcoCoordMiniX)
                                and (self.LOCLmarcoLibreMaxiX or int(filename[:3]) * 1000 < self.LOCLmarcoCoordMaxiX)
                                and (self.LOCLmarcoLibreMiniY or int(filename[4:8]) * 1000 >= self.LOCLmarcoCoordMiniY)
                                and (self.LOCLmarcoLibreMaxiY or (int(filename[4:8]) * 1000) - 2000 < self.LOCLmarcoCoordMaxiY)
                            )
                        ]
                    else:
                        filenamesSeleccionadosX = [
                            filename for filename in filenames
                            if (
                                miTipoDeFicheroDasoLayer.upper() in filename.upper()
                                and filename[-4:].upper() == '.ASC'
                            )
                        ]
                except:
                    myLog.warning('\nAVISO: no se han podido filtrar los ficheros por coordenadas debido a que no siguen el patron XXX_YYYY...asc.')
                    filenamesSeleccionadosX = [
                        filename for filename in filenames
                        if (
                            miTipoDeFicheroDasoLayer.upper() in filename.upper()
                            and filename[-4:].upper() == '.ASC'
                        )
                    ]

                if filenamesSeleccionadosX:
                    if self.LOCLverbose == 3:
                        myLog.debug(f'{TB}{TV}{TV}AscRaiz => subDir: {self.LOCLrutaAscRaizBase} => {subDirExplorado}')
                        myLog.debug(f'{TB}{TV}{TV}nivelDeSubdir:     {nivelDeSubdir}')
                        myLog.debug(f'{TB}{TV}{TV}dirnames:          {dirnames}')
                        myLog.debug(f'{TB}{TV}{TV}numFiles:          {len(filenames)}')
                        myLog.debug(f'{TB}{TV}{TV}Algunos files:     {filenames[:2]}, etc.')
                        # myLog.debug(f'{TB}{TV}{TV}dirpathPrevio:     {}'.format(dirpathPrevio))
                        # dirpathPadre1 = os.path.abspath(os.path.join(dirpathOk, '..'))
                        # myLog.debug(f'{TB}{TV}{TV}dirpathPadre1:     {}'.format(dirpathPadre1))
                        # dirpathPrevio = dirpathPadre1
                    for filenameSel in filenamesSeleccionadosX:
                        infilesX.append([dirpathOk, filenameSel])
                    myLog.info(f'{TB}{TV}-> Encontrados: {len(filenamesSeleccionadosX)} ficheros.')
                    myLog.info(f'{TB}{TV}-> Primeros {min(len(filenamesSeleccionadosX), 5)} ficheros:')
                    for nFile, pathAndfilename in enumerate(filenamesSeleccionadosX[:5]):
                        myLog.info(f'{TB}{TV}{TV} {nFile} {pathAndfilename}')
                else:
                    if self.LOCLverbose == 3:
                        myLog.debug(f'{TB}{TV}dirpathOk:         {dirpathOk}')
                        myLog.debug(f'{TB}{TV}numFiles:          {len(filenames)}')
                    if self.marcoCoordDisponible and TRNS_buscarBloquesSoloDentroDelMarcoUTM:
                        myLog.info(
                            '{}{}{}No se ha localizado ningun fichero en {}/{} con el patron: <{}> que solape con el marco de coordenadas X: {} {} Y: {} {}'.format(
                                TB, TV, TV,
                                self.LOCLrutaAscRaizBase,
                                subDirExplorado,
                                miTipoDeFicheroDasoLayer,
                                self.LOCLmarcoCoordMiniX,
                                self.LOCLmarcoCoordMaxiX,
                                self.LOCLmarcoCoordMiniY,
                                self.LOCLmarcoCoordMaxiY,
                            )
                        )
                    else:
                        myLog.info(
                            '{}No se ha localizado ningun fichero en {}/{} con el patron: <{}>'.format(
                                TB,
                                self.LOCLrutaAscRaizBase,
                                subDirExplorado,
                                miTipoDeFicheroDasoLayer,
                            )
                        )
                #===================================================================

            # Las listas infilesX pueden diferir de un tipo de fichero a otro
            # Mas adelante se ordenan y cuadran para que sean listas paralelas
            self.inFilesListAllTypes.append(infilesX)
        # ======================================================================

        if self.LOCLverbose == 3:
            myLog.info(f'clidtwins-> Resumen de ficheros encontrados:')
            for nInputVar, filenamesSeleccionadosX in enumerate(self.inFilesListAllTypes):
                if len(self.LOCLlistaDasoVarsFileTypes) > nInputVar:
                    myLog.info(f'{TB}-> Ficheros tipo {self.LOCLlistaDasoVarsFileTypes[nInputVar]}:')
                else:
                    myLog.info(f'{TB}-> Ficheros sin tipo asigando (ATENCION: revisar):')
                myLog.info(f'{TB}{TV}-> Encontrados: {len(filenamesSeleccionadosX)} ficheros.')
                myLog.info(f'{TB}{TV}-> Primeros {min(len(filenamesSeleccionadosX), 5)} ficheros:')
                for nFile, pathAndfilename in enumerate(filenamesSeleccionadosX[:5]):
                    myLog.info(f'{TB}{TV}{TV} {nFile} {pathAndfilename}')


        # Despues de buscar todos los ficheros disponibles de cada tipo (cada variable)
        # Elimino los ficheros de bloques que no tengan todos los tipos (todas las variables)

        # myLog.debug('\nNumero de ficheros en {}: {} {}'.format(self.LOCLrutaAscRaizBase, len(self.inFilesListAllTypes), len(self.LOCLlistaDasoVarsFileTypes)))
        # myLog.debug('Numero de tipos de fichero: {}'.format(min(self.LOCLnPatronDasoVars, len(self.LOCLlistLstDasoVars) - 2)))
        self.inFilesNumPorBloque = {}
        self.inFilesDictAllTypes = {}
        myLog.debug('\nclidtwins-> Buscando codigos de Bloque:')
        hayAlgunBloqueCompleto = False
        # Hay una lista de tuplas (path, file) por cada fileType (DLV)
        for numDasoVarX, listaFileTuplesDasoVarX in enumerate(self.inFilesListAllTypes):
            if (
                (self.LOCLlistLstDasoVars[numDasoVarX][1]).startswith('MFE')
                or self.LOCLlistLstDasoVars[numDasoVarX][1] == 'TMasa'
            ):
                myLog.critical('clidtwins-> ATENCION: por aqui no debiera pasar: revisar codigo.')
                continue
            for numFile, [pathFile, nameFile] in enumerate(listaFileTuplesDasoVarX):
                codigoBloque = nameFile[:8]
                if codigoBloque in self.inFilesDictAllTypes.keys():
                    self.inFilesDictAllTypes[codigoBloque].append((pathFile, nameFile))
                    self.inFilesNumPorBloque[codigoBloque] += 1
                else:
                    self.inFilesDictAllTypes[codigoBloque] = [(pathFile, nameFile)]
                    self.inFilesNumPorBloque[codigoBloque] = 1
                    myLog.debug(f'{TB}-> Nuevo codigoBloque encontrado: {codigoBloque} (total: {len(self.inFilesDictAllTypes)})')

        if self.LOCLverbose == 3:
            myLog.debug('\nclidtwins-> Muestra de bloques encontrados por fileType (DLV):')
        for numDasoVarX, listaFileTuplesDasoVarX in enumerate(self.inFilesListAllTypes):
            if len(listaFileTuplesDasoVarX) == 0:
                myLog.error(
                    '{}-> DLV {:<2} (nickName: {}); fileType: {:<35}'.format(
                        TB,
                        numDasoVarX,
                        self.LOCLlistLstDasoVars[numDasoVarX][1],
                        self.LOCLlistLstDasoVars[numDasoVarX][0],
                    )
                )
                myLog.error(f'\nclidtwins-> ATENCION: no hay ficheros para el fileType {self.LOCLlistLstDasoVars[numDasoVarX][0]} (DLV: {self.LOCLlistLstDasoVars[numDasoVarX][1]}).')
                myLog.error(f'Revisar los codigos de ficheros: los ficheros asc deben incluir esos codigos en el nombre.')
                sys.exit(0)
            else:
                if self.LOCLverbose == 3:
                    myLog.debug(
                        '{}-> DLV {:<2} (nickName: {}; fileType: {:<35}) -> {:<2} ficheros totales (antes de revisar completitud de DLVs):'.format(
                            TB,
                            numDasoVarX,
                            self.LOCLlistLstDasoVars[numDasoVarX][1],
                            self.LOCLlistLstDasoVars[numDasoVarX][0],
                            len(listaFileTuplesDasoVarX),
                        )
                    )
                    for tuplaFiles in listaFileTuplesDasoVarX[:2]:
                        myLog.debug(f'{TB}{TV}{tuplaFiles[1]}')
                    if len(listaFileTuplesDasoVarX) > 2:
                        myLog.debug(f'{TB}{TV}Etc.')

        myLog.info('\nclidtwins-> Numero total de ficheros encontrados por cada bloque:')
        # Corregir: RuntimeError: dictionary changed size during iteration
        listaCodigosBloque = list(self.inFilesDictAllTypes.keys())
        for bloqueKey in listaCodigosBloque:
            myLog.info(f'{TB}-> Bloque {bloqueKey}: {len(self.inFilesDictAllTypes[bloqueKey])} ficheros')
            if len(self.inFilesDictAllTypes[bloqueKey]) < self.nInputVars:
                if len(self.inFilesDictAllTypes[bloqueKey]) < self.nInputVars:
                    myLog.info(f'{TB}   Eliminando codigoBloque por no tener todas las dasoVars ({len(self.inFilesDictAllTypes[bloqueKey])} < {self.nInputVars})')
                # del self.inFilesDictAllTypes[bloqueKey]
                self.inFilesDictAllTypes.pop(bloqueKey, None)
                self.inFilesNumPorBloque[bloqueKey] = 0
            else:
                hayAlgunBloqueCompleto = True

        if not hayAlgunBloqueCompleto:
            myLog.error(f'\nclidtwins-> ATENCION: No hay ningun bloque con todos los tipos de fichero (DLVs).')
            myLog.error(f'{TB}Se interrumpe la ejecucion.')
            sys.exit(0)

        myLog.debug(f'\nclidtwins-> Numero de ficheros por bloque (con todas las DLVs):')
        for codigoBloque in self.inFilesNumPorBloque.keys():
            if codigoBloque in self.inFilesDictAllTypes.keys():
                if self.inFilesNumPorBloque[codigoBloque] == len(self.inFilesDictAllTypes[codigoBloque]):
                    myLog.debug(f'{TB}Bloque {codigoBloque} -> {self.inFilesNumPorBloque[codigoBloque]} ficheros (ok).')
                else:
                    myLog.critical(f'{TB}Bloque {codigoBloque} -> ATENCION: revisar codigo: {self.inFilesNumPorBloque[codigoBloque]} != {len(self.inFilesDictAllTypes[codigoBloque])} ficheros (no ok).')
            else:
                myLog.debug(f'{TB}Bloque {codigoBloque} -> Aviso: bloque no disponible (eliminado por no tener todos los ficheros).')

        for numDasoVarX, listaFileTuplesDasoVarX in enumerate(self.inFilesListAllTypes):
            if (
                (self.LOCLlistLstDasoVars[numDasoVarX][1]).startswith('MFE')
                or self.LOCLlistLstDasoVars[numDasoVarX][1] == 'TMasa'
            ):
                myLog.critical('clidtwins-> ATENCION: por aqui no debiera pasar, revisar codigo.')
                continue
            # Si no se han localizado los N ficheros del bloque, se elimina todos los ficheros de ese bloque
            # Ver manejo dict para python > 3.6 en https://realpython.com/iterate-through-dictionary-python/
            for numFile, [pathFile, nameFile] in enumerate(listaFileTuplesDasoVarX):
                codigoBloque = nameFile[:8]
                if codigoBloque in self.inFilesDictAllTypes.keys() and len(self.inFilesDictAllTypes[codigoBloque]) < self.nInputVars:
                    del self.inFilesListAllTypes[numDasoVarX][numFile]
        for numDasoVarX, listaFileTuplesDasoVarX in enumerate(self.inFilesListAllTypes):
            self.inFilesListAllTypes[numDasoVarX] = sorted(listaFileTuplesDasoVarX, key=itemgetter(1))

        if not hayAlgunBloqueCompleto:
            myLog.error('\nATENCION: No hay ningun bloque con todas las variables (todos los tipos de fichero).')
            myLog.error(f'{TB}-> Ruta de busqueda de ficheros: {self.LOCLrutaAscRaizBase}')
            sys.exit(0)

        # Actualizo el marco de coordenadas de la zona de estudio con los bloques encontrados y admitidos
        if not TRNS_buscarBloquesSoloDentroDelMarcoUTM or (
            self.LOCLmarcoLibreMiniX
            or self.LOCLmarcoLibreMaxiX
            or self.LOCLmarcoLibreMiniY
            or self.LOCLmarcoLibreMaxiY
        ):
            myLog.debug('\nclidtwuins-> Actualizando marco de analisis:')
        for codigoBloque in self.inFilesNumPorBloque.keys():
            if (
                self.LOCLmarcoLibreMiniX
                or (
                    not TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    and int(codigoBloque[:3]) * 1000 < self.LOCLmarcoCoordMiniX
                )
            ):
                myLog.debug(
                    '{}-> Actualizando marcoCoordMiniX de {:0.2f} a {}'.format(
                        TB,
                        self.LOCLmarcoCoordMiniX,
                        int(codigoBloque[:3]) * 1000
                    )
                )
                self.LOCLmarcoCoordMiniX = int(codigoBloque[:3]) * 1000
            if (
                self.LOCLmarcoLibreMaxiX
                or (
                    not TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    and (int(codigoBloque[:3]) * 1000) + 2000 > self.LOCLmarcoCoordMaxiX
                )
            ):
                myLog.debug(
                    '{}-> Actualizando marcoCoordMaxiX de {:0.2f} a {:0.2f}'.format(
                        TB,
                        self.LOCLmarcoCoordMaxiX,
                        (int(codigoBloque[:3]) * 1000) + 2000
                    )
                )
                self.LOCLmarcoCoordMaxiX = (int(codigoBloque[:3]) * 1000) + 1999.99
            if (
                self.LOCLmarcoLibreMaxiY
                or (
                    not TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    and int(codigoBloque[4:8]) * 1000 > self.LOCLmarcoCoordMaxiY
                )
            ):
                myLog.debug(
                    '{}-> Actualizando marcoCoordMaxiY de {:0.2f} a {:0.2f}'.format(
                        TB,
                        self.LOCLmarcoCoordMaxiY,
                        int(codigoBloque[4:8]) * 1000
                    )
                )
                self.LOCLmarcoCoordMaxiY = int(codigoBloque[4:8]) * 1000
            if (
                self.LOCLmarcoLibreMiniY
                or (
                    not TRNS_buscarBloquesSoloDentroDelMarcoUTM
                    and (int(codigoBloque[4:8]) * 1000) - 2000 < self.LOCLmarcoCoordMiniY
                )
            ):
                myLog.debug(
                    '{}-> Actualizando marcoCoordMiniY de {:0.2f} a {:0.2f}'.format(
                        TB,
                    self.LOCLmarcoCoordMiniY,
                    (int(codigoBloque[4:8]) * 1000) - 2000
                    )
                )
            self.LOCLmarcoCoordMiniY = (int(codigoBloque[4:8]) * 1000) - 2000

        myLog.debug('clidtwins-> Resultado tras eliminar los que procedan y ordenar los ficheros por codigoBloque:')
        for numDasoVarX, listaFileTuplesDasoVarX in enumerate(self.inFilesListAllTypes):
            myLog.debug(f'Variable num {numDasoVarX} -> {len(listaFileTuplesDasoVarX)} Files: {listaFileTuplesDasoVarX}')
        for bloqueKey in self.inFilesDictAllTypes.keys():
            myLog.debug(f'Bloque: {bloqueKey} -> {len(self.inFilesDictAllTypes[bloqueKey])} Files -> {self.inFilesDictAllTypes[bloqueKey]}')
        myLog.info('{:=^80}'.format(''))

    # ==========================================================================
    def verificarlistaDasoVars(
            self,
            LCL_listLstDasoVars=None,  # optional (si existe, prevalece sobre el siguiente)
            LCL_listaTxtDasoVarsFileTypes=None,  # optional (alternativa simplificada al anterior)
            LCL_nClasesDasoVars=None,  # optional
            LCL_trasferDasoVars=None,  # optional
            LCL_nPatronDasoVars=None,  # optional
        ):
        # ======================================================================
        myLog.debug('\n{:_^80}'.format(''))
        if not LCL_listLstDasoVars is None:
            self.LOCLlistLstDasoVars = LCL_listLstDasoVars
            myLog.debug('clidtwins-> Se crea un objeto de la clase DasoLidarSource con las listas\n'
                  f'{TB}de identificadores de tipo de fichero y demas propiedades de cada\n'
                  f'{TB}variable pasadas como argumento (LCL_listLstDasoVars):')
            myLog.debug(f'{TB}{TV}-> NickName')
            myLog.debug(f'{TB}{TV}-> Rango de valores')
            myLog.debug(f'{TB}{TV}-> Numero de clases')
            myLog.debug(f'{TB}{TV}-> Movilidad inter-clases')
            myLog.debug(f'{TB}{TV}-> Peso relativo.')
            self.calcularRangoVariables = False
        elif not LCL_listaTxtDasoVarsFileTypes is None:
            myLog.debug('clidtwins-> Se crea un objeto de la clase DasoLidarSource con la lista de\n'
                  f'{TB}identificadores de tipo de fichero (LCL_listaTxtDasoVarsFileTypes).\n'
                  f'{TB}Cada tipo de fichero corresponde a una variable dasoLidar.\n'
                  f'{TB}Ficheros: XXX_YYYY_*IdFileType*.asc\n'
                  f'{TB}{TV}XXX, YYYY: coord. UTM /1000 m;\n'
                  f'{TB}{TV}*IdFileType*: cadena que incluye el\n'
                  f'{TB}{TV}{TV}identificador de tipo de fichero.\n'
                  f'{TB}Para cada variable se establecen clases dividiendo su rango\n'
                  f'{TB}absoluto entre el num de clases. El numero de clases, la movilidad\n'
                  f'{TB}inter-clases y el peso relativo son iguales para todas las variables:')
            if LCL_nClasesDasoVars is None:
                self.LOCLnClasesDasoVars = GLO.GLBLnClasesDasoVarsPorDefecto
                myLog.debug(f'{TB}{TV}Numero de clases: {self.LOCLnClasesDasoVars} clases (valor por defecto).')
            else:
                self.LOCLnClasesDasoVars = LCL_nClasesDasoVars
                myLog.debug(f'{TB}{TV}Numero de clases: {self.LOCLnClasesDasoVars} clases (argumeto LCL_nClasesDasoVars).')
            if LCL_trasferDasoVars is None:
                self.LOCLtrasferDasoVars = GLO.GLBLtrasferDasoVarsPorDefecto
                myLog.debug(f'{TB}{TV}Movilidad inter-clases: {self.LOCLtrasferDasoVars} % (valor por defecto).')
            else:
                self.LOCLtrasferDasoVars = LCL_trasferDasoVars
                myLog.debug(f'{TB}{TV}Movilidad inter-clases: {self.LOCLnClasesDasoVars} % (argumeto LCL_nClasesDasoVars).')
            self.LOCLponderaDasoVars = 10
            myLog.debug(f'{TB}{TV}Todas las variables se poderan igual.')

            self.calcularRangoVariables = True
            if type(LCL_listaTxtDasoVarsFileTypes) == str:
                self.LOCLlistaDasoVarsFileTypes = [item.strip() for item in LCL_listaTxtDasoVarsFileTypes.split(',')]
            elif type(LCL_listaTxtDasoVarsFileTypes) == list:
                self.LOCLlistaDasoVarsFileTypes = LCL_listaTxtDasoVarsFileTypes
            elif type(LCL_listaTxtDasoVarsFileTypes) == tuple:
                self.LOCLlistaDasoVarsFileTypes = list(LCL_listaTxtDasoVarsFileTypes)
            else:
                myLog.error(f'\nclidtwins-> ATENCION: el argumento LCL_listaTxtDasoVarsFileTypes es de tipo {type(LCL_listaTxtDasoVarsFileTypes)}, y debe ser str o list.')
                myLog.error('Se interrumpe la ejecucion.')
                sys.exit(0)

            self.LOCLlistaDasoVarsNickNames = [
                'alt95' if ('alt' in item.lower() and '95' in item) else
                'fcc3m' if ('fcc' in item.lower() and '03' in item) else
                'fcc5m' if ('fcc' in item.lower() and '05' in item) else
                item[:5]
                for item in self.LOCLlistaDasoVarsFileTypes
            ]
            self.LOCLlistaDasoVarsRangoLinf = [0] * len(self.LOCLlistaDasoVarsFileTypes)  # Se calcula al leer los ficheros
            self.LOCLlistaDasoVarsRangoLsup = [100] * len(self.LOCLlistaDasoVarsFileTypes)  # Se calcula al leer los ficheros
            self.LOCLlistaDasoVarsNumClases = [self.LOCLnClasesDasoVars] * len(self.LOCLlistaDasoVarsFileTypes)
            self.LOCLlistaDasoVarsMovilidad = [self.LOCLtrasferDasoVars] * len(self.LOCLlistaDasoVarsFileTypes)
            self.LOCLlistaDasoVarsPonderado = [self.LOCLponderaDasoVars] * len(self.LOCLlistaDasoVarsFileTypes)

            self.LOCLlistLstDasoVars = []
            for nVar in range(len(self.LOCLlistaDasoVarsFileTypes)):
                self.LOCLlistLstDasoVars.append(
                    [
                        self.LOCLlistaDasoVarsFileTypes[nVar],
                        self.LOCLlistaDasoVarsNickNames[nVar],
                        self.LOCLlistaDasoVarsRangoLinf[nVar],
                        self.LOCLlistaDasoVarsRangoLsup[nVar],
                        self.LOCLlistaDasoVarsNumClases[nVar],
                        self.LOCLlistaDasoVarsMovilidad[nVar],
                        self.LOCLlistaDasoVarsPonderado[nVar],
                    ]
                )
        else:
            # LCL_listLstDasoVars is None and LCL_listaTxtDasoVarsFileTypes is None:
            self.LOCLlistLstDasoVars = GLO.GLBLlistLstDasoVarsPorDefecto
            self.calcularRangoVariables = False
            if self.LOCLverbose:
                myLog.info('clidtwins-> Lista de DasoVars:')
                if os.path.exists(GLO.configFileNameCfg):
                    myLog.info(f'{TB}Se lee la lista de DasoVars del fichero de configuracion ({GLO.configFileNameCfg})')
                else:
                    myLog.info(f'{TB}Se usa la lista de DasoVars por defecto (incluida en clidtwins._config.py)')
                myLog.info(f'{TB}por no haberse especificado LCL_listLstDasoVars de forma explicita')
                myLog.info(f'{TB}al instanciar la clase DasoLidarSource.')
                myLog.debug(f'listaDasoVars: {self.LOCLlistLstDasoVars}')

        myLog.info('{:=^80}'.format(''))

        if not type(self.LOCLlistLstDasoVars) == list:
            myLog.error(f'\nclidtwins-> ATENCION: revisar el parametro LCL_listLstDasoVars para que permita generar una lista de DLVs (cada una, a su vez, con su lista de propiedades).')
            myLog.error(f'\t-> Si se ha usado LCL_listaTxtDasoVarsFileTypes en lugar de LCL_listLstDasoVars, aquel debe ser una lista simple de fileTypes separada por comas')
            myLog.error(f'\t-> Valor obtenido a partir de LCL_listLstDasoVars: {type(self.LOCLlistLstDasoVars)} -> {self.LOCLlistLstDasoVars}')
            myLog.error(f'\t-> Valor obtenido de LCL_listaTxtDasoVarsFileTypes: {type(LCL_listaTxtDasoVarsFileTypes)} -> {LCL_listaTxtDasoVarsFileTypes}')
            sys.exit(0)

        if not hasattr(self, 'LOCLlistaDasoVarsFileTypes'):
            self.LOCLlistaDasoVarsFileTypes = []
            self.LOCLlistaDasoVarsNickNames = []
            self.LOCLlistaDasoVarsRangoLinf = []
            self.LOCLlistaDasoVarsRangoLsup = []
            self.LOCLlistaDasoVarsNumClases = []
            self.LOCLlistaDasoVarsMovilidad = []
            self.LOCLlistaDasoVarsPonderado = []
            for thisListLstDasoVar in self.LOCLlistLstDasoVars:
                if not type(thisListLstDasoVar) == list:
                    myLog.error(f'\nclidtwins-> ATENCION: revisar el parametro LCL_listLstDasoVars para que permita generar una lista de DLVs (cada una, a su vez, con su lista de propiedades).')
                    myLog.error(f'\t-> Si se ha usado LCL_listaTxtDasoVarsFileTypes en lugar de LCL_listLstDasoVars, aquel debe ser una lista simple de fileTypes separada por comas')
                    myLog.error(f'\t-> Valor obtenido a partir de LCL_listLstDasoVars: {type(self.LOCLlistLstDasoVars)} -> {self.LOCLlistLstDasoVars}')
                    myLog.error(f'\t-> Valor obtenido de LCL_listaTxtDasoVarsFileTypes: {type(LCL_listaTxtDasoVarsFileTypes)} -> {LCL_listaTxtDasoVarsFileTypes}')
                    sys.exit(0)
                self.LOCLlistaDasoVarsFileTypes.append(thisListLstDasoVar[0])
                self.LOCLlistaDasoVarsNickNames.append(thisListLstDasoVar[1])
                self.LOCLlistaDasoVarsRangoLinf.append(thisListLstDasoVar[2])
                self.LOCLlistaDasoVarsRangoLsup.append(thisListLstDasoVar[3])
                self.LOCLlistaDasoVarsNumClases.append(thisListLstDasoVar[4])
                self.LOCLlistaDasoVarsMovilidad.append(thisListLstDasoVar[5])
                if len(thisListLstDasoVar) > 6:
                    self.LOCLlistaDasoVarsPonderado.append(thisListLstDasoVar[6])
                else:
                    self.LOCLlistaDasoVarsPonderado.append(10)

        # myLog.debug('--------------------------->self.LOCLlistLstDasoVars {self.LOCLlistLstDasoVars}')
        if (
            not (self.LOCLlistLstDasoVars[-2][0]).upper().startswith('MFE')
            and not (self.LOCLlistLstDasoVars[-2][0]).upper().startswith('LAND')
        ):
            dasoVarTipoBosquePorDefecto = ['MFE25', 'MFE25', 0, 255, 255, 0, 0]
            dasoVarTipoDeMasaPorDefecto = ['TMasa', 'TMasa', 0, 255, 255, 0, 0]
            if self.LOCLverbose:
                myLog.debug('\n{:_^80}'.format(''))
                myLog.debug('clidtwins-> AVISO: la lista de variables dasolidar no incluye las dos adicionales')
                myLog.debug(f'{TB}que deben ser tipo de bosque (MFE**) y tipo de masa (TMasa).')
                myLog.debug(f'{TB}Se agregan a la lista con esta configuracion:')
                myLog.debug(f'{TB}Tipos de bosque: {dasoVarTipoBosquePorDefecto}')
                myLog.debug(f'{TB}Tipos de masa:   {dasoVarTipoDeMasaPorDefecto}')
                if self.LOCLverbose > 1:
                    rpta = input('Agregar estas dos variables? (S/n) ')
                    if rpta.upper() == 'N':
                        myLog.debug('Se ha elegido no agregar las variables TipoBosque y TipoDeMasa.')
                        myLog.debug('\nDefinir las variables de entrada con TipoBosque y TipoDeMasa como argumento'
                              'en linea de comandos el fichero de configuracion o en codigo por defecto')
                        myLog.debug('Se interrumpe la ejecucion')
                        sys.exit(0)
                else:
                    myLog.debug(f'{TB}Se agregan estas dos variables.')
                myLog.info('{:=^80}'.format(''))
            self.LOCLlistLstDasoVars.append(dasoVarTipoBosquePorDefecto)
            self.LOCLlistLstDasoVars.append(dasoVarTipoDeMasaPorDefecto)
            for dasoVarMFE25TMasaPorDefecto in [dasoVarTipoBosquePorDefecto, dasoVarTipoDeMasaPorDefecto]:
                self.LOCLlistaDasoVarsFileTypes.append(dasoVarMFE25TMasaPorDefecto[0])
                self.LOCLlistaDasoVarsNickNames.append(dasoVarMFE25TMasaPorDefecto[1])
                self.LOCLlistaDasoVarsRangoLinf.append(dasoVarMFE25TMasaPorDefecto[2])
                self.LOCLlistaDasoVarsRangoLsup.append(dasoVarMFE25TMasaPorDefecto[3])
                self.LOCLlistaDasoVarsNumClases.append(dasoVarMFE25TMasaPorDefecto[4])
                self.LOCLlistaDasoVarsMovilidad.append(dasoVarMFE25TMasaPorDefecto[5])
                self.LOCLlistaDasoVarsPonderado.append(dasoVarMFE25TMasaPorDefecto[6])
        # ======================================================================

        # ======================================================================
        if LCL_nPatronDasoVars is None:
            self.LOCLnPatronDasoVars = GLO.GLBLnPatronDasoVarsPorDefecto
        else:
            self.LOCLnPatronDasoVars = LCL_nPatronDasoVars

        if self.LOCLnPatronDasoVars == 0:
            self.nBandasPrevistasOutput = len(self.LOCLlistLstDasoVars)
        else:
            self.nBandasPrevistasOutput = self.LOCLnPatronDasoVars + 2
        self.nInputVars = self.nBandasPrevistasOutput - 2
        # ======================================================================

        # ======================================================================
        myLog.info('\n{:_^80}'.format(''))
        myLog.info('clidtwins-> Lista de variables DasoLidar:')

        # Esto es reiterativo:
        # self.LOCLlistaDasoVarsFileTypes = []
        # self.LOCLlistaDasoVarsNickNames = []
        # self.LOCLlistaDasoVarsRangoLinf = []
        # self.LOCLlistaDasoVarsRangoLsup = []
        # self.LOCLlistaDasoVarsNumClases = []
        # self.LOCLlistaDasoVarsMovilidad = []
        # self.LOCLlistaDasoVarsPonderado = []
        for nInputVar, thisListLstDasoVar in enumerate(self.LOCLlistLstDasoVars):
            # nBanda = nInputVar + 1
            # self.LOCLlistaDasoVarsFileTypes.append(thisListLstDasoVar[0])
            # self.LOCLlistaDasoVarsNickNames.append(thisListLstDasoVar[1])
            # self.LOCLlistaDasoVarsRangoLinf.append(thisListLstDasoVar[2])
            # self.LOCLlistaDasoVarsRangoLsup.append(thisListLstDasoVar[3])
            # self.LOCLlistaDasoVarsNumClases.append(thisListLstDasoVar[4])
            # self.LOCLlistaDasoVarsMovilidad.append(thisListLstDasoVar[5])
            # if len(thisListLstDasoVar) > 6:
            #     self.LOCLlistaDasoVarsPonderado.append(thisListLstDasoVar[6])
            # else:
            #     self.LOCLlistaDasoVarsPonderado.append(10)
            if (thisListLstDasoVar[0]).startswith('MFE'):
                pesoPonderado = 'Excluyente'
            elif thisListLstDasoVar[6] == 0:
                pesoPonderado = '--'
            else:
                pesoPonderado = '{:>2} (/10)'.format(thisListLstDasoVar[6])
            # if nBanda < self.nBandasPrevistasOutput - 1:
            if nInputVar < self.nInputVars:
                myLog.info(
                    '{}Variable {} ({})-> codigoFichero: {:<35}'.format(
                        TB, 
                        nInputVar,
                        thisListLstDasoVar[1],
                        thisListLstDasoVar[0],
                    )
                )
                myLog.info(
                    '{}{}Rango: {:>2} - {:>3};'.format(TB, TV, thisListLstDasoVar[2], thisListLstDasoVar[3])
                    + ' clases: {:>3};'.format(thisListLstDasoVar[4])
                    + ' movilidad: {:>3} %'.format(thisListLstDasoVar[5])
                    + ' peso: {}'.format(pesoPonderado)
                )

        myLog.info(f'{TB}-> Para cada variable DasoLidar se indica:')
        myLog.info(f'{TB}{TV}-> CodigoFichero             -> para buscar ficheros con ese codigo')
        myLog.info(f'{TB}{TV}-> (NickName)                -> sin uso interno, unicamente para identificacion rapida')
        myLog.info(f'{TB}{TV}-> Rango y numero de clases  -> para crear histograma') 
        myLog.info(f'{TB}{TV}-> Movilidad inter-clases    -> para buscar zonas similares')
        myLog.info(f'{TB}{TV}-> Peso relativo             -> para ponderar al comparar con el patron')
        myLog.info('{:=^80}'.format(''))

    # ==========================================================================
    def verificarRutaAscRaiz(
            self,
            LCL_rutaAscRaizBase=None,  # opcional
        ):
        # ======================================================================
        # Si no se ha especificado LCL_rutaAscRaizBase, se elige una que exista:
        if type(LCL_rutaAscRaizBase) == str:
            LCL_rutaAscRaizBase = os.path.abspath(LCL_rutaAscRaizBase)
            if 'site-packages' in LCL_rutaAscRaizBase:
                LCL_rutaAscRaizBase = str(pathlib.Path.home())
            if not os.path.isdir(LCL_rutaAscRaizBase):
                myLog.error(f'\nclidtwins-> ATENCION: ruta {LCL_rutaAscRaizBase} no disponible, se interrumpe la ejecucion.')
                myLog.error(f'{TB}-> Esta ruta se especifica en el fichero de configuracion ({GLO.configFileNameCfg}).')
                myLog.error(f'{TB}-> En esta ruta estan los ficheros con las capas vectoriales y raster requeridas para el procesado.')
                sys.exit(0)
        else:
            LCL_rutaAscRaizBase = None

        if LCL_rutaAscRaizBase is None:
            if hasattr(self, 'LOCLrutaAscRaizBase') and not self.LOCLrutaAscRaizBase is None:
                # Ya hay un valor asignado a self.LOCLrutaAscRaizBase, probablemente en setRangeUTM<>
                return
            myLog.debug('\n{:_^80}'.format(''))
            myLog.warning(f'clidtwins-> AVISO: no se ha indicado ruta para los ficheros asc con las variables dasoLidar de entrada.')
            myLog.warning(f'{TB}Ruta: {LCL_rutaAscRaizBase}')
            if os.path.isdir(os.path.abspath(GLO.GLBLrutaAscRaizBasePorDefecto)):
                if os.path.exists(GLO.configFileNameCfg):
                    myLog.warning(f'{TB}-> Se adopta el valor del fichero de configuracion ({GLO.configFileNameCfg})')
                else:
                    myLog.warning(f'{TB}-> Se adopta el valor por defecto (incluida en clidtwins._config.py)')
                LCL_rutaAscRaizBase = os.path.abspath(GLO.GLBLrutaAscRaizBasePorDefecto)
            else:
                # Directorio que depende del entorno:
                MAIN_HOME_DIR = str(pathlib.Path.home())
                listaRutasDisponibles = [MAIN_HOME_DIR]
                # Directorio desde el que se lanza la app (estos dos coinciden):
                MAIN_THIS_DIR = os.getcwd()
                if not 'site-packages' in MAIN_THIS_DIR and not MAIN_THIS_DIR in listaRutasDisponibles:
                    listaRutasDisponibles.append(MAIN_THIS_DIR)
                MAIN_BASE_DIR = os.path.abspath('.')
                if not 'site-packages' in MAIN_BASE_DIR and not MAIN_BASE_DIR in listaRutasDisponibles:
                    listaRutasDisponibles.append(MAIN_BASE_DIR)
                # Directorios de la aplicacion:
                try:
                    MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
                except:
                    MAIN_FILE_DIR = MAIN_BASE_DIR
                if not 'site-packages' in MAIN_FILE_DIR and not MAIN_FILE_DIR in listaRutasDisponibles:
                    listaRutasDisponibles.append(MAIN_FILE_DIR)
                # Cuando estoy en un modulo dentro de un paquete (subdirectorio):
                MAIN_RAIZ_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))
                if not 'site-packages' in MAIN_RAIZ_DIR and not MAIN_RAIZ_DIR in listaRutasDisponibles:
                    listaRutasDisponibles.append(MAIN_RAIZ_DIR)

                if self.LOCLverbose == 3:
                    myLog.info(f'{TB}-> Elegir ruta: ')
                    for numRuta, txtRutaDisponible in enumerate(listaRutasDisponibles):
                        myLog.info(f'{TB}   {numRuta + 1}. {txtRutaDisponible}')
                    myLog.info(f'{TB}   9. Interrumpir la ejecucion y especificar una ruta') # (como argumento en el codigo o en cmd, o en el fichero de configuracion)
                    txtNumRuta = input(f'{TB}-> Ruta elegida: ')
                    try:
                        numRuta = int(txtNumRuta)
                    except:
                        numRuta = 9
                    if numRuta < len(listaRutasDisponibles) + 1:
                        LCL_rutaAscRaizBase = listaRutasDisponibles[numRuta - 1]
                        myLog.info(
                            f'Opcion selecionada: {numRuta} -> {LCL_rutaAscRaizBase}'
                        )
                    else:
                        if numRuta != 9:
                            myLog.error(
                                f'Opcion selecionada ({numRuta}) no disponible.'
                            )
                        myLog.error('\nSe interrumpe la ejecucion')
                        sys.exit(0)
                else:
                    if len(listaRutasDisponibles) >= 2:
                        LCL_rutaAscRaizBase = listaRutasDisponibles[1]
                    else:
                        LCL_rutaAscRaizBase = listaRutasDisponibles[0]
            myLog.debug('{:=^80}'.format(''))
        # ======================================================================
        self.LOCLrutaAscRaizBase = LCL_rutaAscRaizBase
        # ======================================================================

    # ==========================================================================
    def verificarMarcoCoord(self):
        # ======================================================================
        # Si no se ha ejecutado setRangeUTM<> se usan todos los asc disponibles.
        if not self.marcoCoordEjecutado:
            TRNS_verbose = self.LOCLverbose
            self.setRangeUTM(
                LCL_marcoCoordMiniX=0,
                LCL_marcoCoordMaxiX=0,
                LCL_marcoCoordMiniY=0,
                LCL_marcoCoordMaxiY=0,
                LCL_marcoPatronTest=False,
                LCL_verbose=False,
            )
            self.marcoCoordEjecutado = False
            self.LOCLverbose = TRNS_verbose
            
            self.LOCLpatronVectrName = None
            self.LOCLpatronLayerName = None
            self.LOCLtesteoVectrName = None
            self.LOCLtesteoLayerName = None

        if not self.marcoCoordEjecutado:
            myLog.warning('clidtwins-> AVISO: no se ha ejecurtado el metodo .setRangeUTM para delimitar la zona de estudio.\n'
                  f'{TB}-> Se adopta la envolvente de los ficheros ASC que se encuentren en {self.LOCLrutaAscRaizBase}\n'
                  f'{TB}con dasoLidarVars (siempre que se esten los ficheros correspondientes a todas las dasoLidarVars).')
        elif not self.marcoCoordDisponible and not self.GLBLmarcoPatronTest:
            myLog.warning('clidtwins-> AVISO: no se dispone de coordenadas para delimitar la zona de estudio.\n'
                  f'{TB}-> Se adopta la envolvente de los ficheros ASC que se encuentren en {self.LOCLrutaAscRaizBase}\n'
                  f'{TB}con dasoLidarVars (siempre que se esten los ficheros correspondientes a todas las dasoLidarVars).')
        elif self.marcoCoordDisponible and self.GLBLmarcoPatronTest and self.usarVectorFileParaDelimitarZona:
            myLog.warning('clidtwins-> AVISO: se delimita la zona de estudio que abarca tanto las coordenadas indicadas expresamente\n'
                  f'{TB}como la envolvente de los ficheros de referencia y chequeo (patron y testeo) para las variables dasoLidar.')
        elif self.GLBLmarcoPatronTest and self.usarVectorFileParaDelimitarZona:
            myLog.info('clidtwins-> Se delimita la zona de estudio con la envolvente de los ficheros\n'
                  f'{TB}de referencia y chequeo (patron y testeo) para las variables dasoLidar.')
        else:
            myLog.info('clidtwins-> Se delimita la zona de estudio con las coordenadas indicadas expresamente.')
        myLog.info('{:=^80}'.format(''))
        # ======================================================================

    # ==========================================================================
    def createMultiDasoLayerRasterFile(
            self,
            LCL_rutaCompletaMFE=None,
            LCL_cartoMFEcampoSp=None,
            LCL_rasterPixelSize=None,  # opcional
            LCL_outRasterDriver=None,  # opcional
            LCL_cartoMFErecorte=None,  # opcional
            LCL_varsTxtFileName=None,  # opcional
        ):
        f"""Create a new raster file with one layer for every dasoLidar Variable
and two more layers for forest type (land cover) and stand type.
        Attributes
        ----------
        LCL_rutaCompletaMFE : str
            Default: None (optional)
        LCL_cartoMFEcampoSp : str
            Default: None (optional)
        LCL_rasterPixelSize : int
            Default: {GLO.GLBLrasterPixelSizePorDefecto} (optional)
        LCL_outRasterDriver : str
            Default: '{GLO.GLBLoutRasterDriverPorDefecto}' (optional)
        LCL_cartoMFErecorte : str
            Default: '{GLO.GLBLcartoMFErecortePorDefecto}' (optional)
        LCL_varsTxtFileName : str
            Default: '{GLO.GLBLvarsTxtFileNamePorDefecto}' (optional)
        """

        if hasattr(self, 'inFilesListAllTypes'):
            if len((self.inFilesListAllTypes)[0]) == 0:
                myLog.warning(f'clidtwins-> AVISO: no se han encontrado ficheros con las variables dasoLidar.')
                myLog.warning(f'{TB}-> Se interrume el metodo createMultiDasoLayerRasterFile')
                return
        else:
            if self.LOCLverbose:
                myLog.warning(f'clidtwins-> AVISO: antes de generar y analizar el nuevo raster con las variables dasoLidar')
                myLog.warning(f'{TB}-> hay que buscar ficheros con dichas variables (metodo searchSourceFiles)')
                myLog.warning(f'{TB}-> Se interrume el metodo createMultiDasoLayerRasterFile')
                return

        if LCL_rutaCompletaMFE is None:
            self.LOCLrutaCompletaMFE = os.path.abspath(GLO.GLBLrutaCompletaMFEPorDefecto)
        else:
            self.LOCLrutaCompletaMFE = os.path.abspath(LCL_rutaCompletaMFE)
        if LCL_cartoMFEcampoSp is None:
            self.LOCLcartoMFEcampoSp = GLO.GLBLcartoMFEcampoSpPorDefecto
        else:
            self.LOCLcartoMFEcampoSp = LCL_cartoMFEcampoSp

        if LCL_rasterPixelSize is None:
            self.LOCLrasterPixelSize = GLO.GLBLrasterPixelSizePorDefecto
        else:
            self.LOCLrasterPixelSize = LCL_outRasterDriver

        if LCL_outRasterDriver is None:
            self.LOCLoutRasterDriver = self.GLBLoutRasterDriver
        else:
            self.LOCLoutRasterDriver = LCL_outRasterDriver
        if LCL_cartoMFErecorte is None:
            self.LOCLcartoMFErecorte = self.GLBLcartoMFErecorte
        else:
            self.LOCLcartoMFErecorte = LCL_cartoMFErecorte
        if LCL_varsTxtFileName is None:
            self.LOCLvarsTxtFileName = self.GLBLvarsTxtFileName
        else:
            self.LOCLvarsTxtFileName = LCL_varsTxtFileName

        self.LOCLcartoMFEpathName = os.path.dirname(self.LOCLrutaCompletaMFE)
        self.LOCLcartoMFEfileName = os.path.basename(self.LOCLrutaCompletaMFE)
        self.LOCLcartoMFEfileNSinExt, self.LOCLcartoMFEfileSoloExt = os.path.splitext(self.LOCLcartoMFEfileName)

        #===========================================================================
        # En teoria no pasa por aqui si antes no se ha ejecutado el metodo .searchSourceFiles<>
        # que, a su vez llama al metodo .setRangeUTM<> para establecer los limites de la zona de analisis.
        # Con esto, los limites quedan establecidos con setRangeUTM<> o, en su defecto, al leer los ficheros.
        # Al ejecutar estos metodos, ningun limite del marco puede quedar a 0. No obstante,
        # si se llega aqui sin pasar por esos metodos (creando manualmente la propiedad inFilesListAllTypes) 
        # se verifica de nuevo que haya limites de coordenadas por los cuatro costados.
        if hasattr(self, 'LOCLpatronVectrName') and not self.LOCLpatronVectrName is None:
            if (
                self.LOCLmarcoCoordMiniX <= 0
                or self.LOCLmarcoCoordMaxiX <= 0
                or self.LOCLmarcoCoordMiniY <= 0
                or self.LOCLmarcoCoordMaxiY <= 0
            ):
                if self.LOCLverbose:
                    myLog.warning('\n{:_^80}'.format(''))
                    myLog.warning(f'clidtwins-> AVISO: no se han establecido previamente los limites de la zona de analisis.')
                    if self.LOCLpatronLayerName == '' or self.LOCLpatronLayerName is None or (self.LOCLpatronVectrName.lower()).endswith('.shp'):
                        myLog.warning(f'{TB}-> Se adopta como rango de coordenadas la extension de la capa {self.LOCLpatronVectrName}')
                    else:
                        myLog.warning(f'{TB}-> Se adopta como rango de coordenadas la extension de la capa {self.LOCLpatronVectrName} layer {self.LOCLpatronLayerName}')
                    myLog.warning('{:=^80}'.format(''))
                self.setRangeUTM(
                    LCL_marcoPatronTest=True,
                    LCL_rutaAscRaizBase=self.LOCLrutaAscRaizBase,
                    LCL_patronVectrName=self.LOCLpatronVectrName,
                    LCL_patronLayerName=self.LOCLpatronLayerName,
                )
                if (
                    self.LOCLmarcoCoordMiniX == 0
                    or self.LOCLmarcoCoordMaxiX == 0
                    or self.LOCLmarcoCoordMiniY == 0
                    or self.LOCLmarcoCoordMaxiY == 0
                ):
                    self.marcoCoordDisponible = False
        #===========================================================================

        #===========================================================================
        # Formatos raster alternativos a GTiff:
        # self.GLBLoutRasterDriver = "JP2ECW"
        #     https://gdal.org/drivers/raster/jp2ecw.html#raster-jp2ecw
        #     Requiere descargar:
        #         https://download.hexagongeospatial.com/en/downloads/ecw/erdas-ecw-jp2-sdk-v5-4
        # self.GLBLoutRasterDriver = 'JP2OpenJPEG' # Solo permite copiar y editar, no crear
        #     https://gdal.org/drivers/raster/jp2openjpeg.html
        # self.GLBLoutRasterDriver = 'KEA'
        #     https://gdal.org/drivers/raster/kea.html#raster-kea
        # self.GLBLoutRasterDriver = 'HDF5'
        #     https://gdal.org/drivers/raster/hdf5.html#raster-hdf5
        # self.GLBLoutRasterDriver = 'SENTINEL2'
        #     https://gdal.org/drivers/raster/sentinel2.html#raster-sentinel2
        # self.GLBLoutRasterDriver = 'netCDF'
        #     https://gdal.org/drivers/raster/netcdf.html#raster-netcdf
        # self.GLBLoutRasterDriver = "GTiff"
        #     https://gdal.org/drivers/raster/gtiff.html#raster-gtiff
        if self.GLBLoutRasterDriver == 'GTiff':
            self.driverExtension = 'tif'
        elif self.GLBLoutRasterDriver == 'JP2ECW':
            self.driverExtension = 'jp2'
        elif self.GLBLoutRasterDriver == 'JP2OpenJPEG':
            self.driverExtension = 'jp2'
        elif self.GLBLoutRasterDriver == 'KEA':
            self.driverExtension = 'KEA'
        elif self.GLBLoutRasterDriver == 'HDF5':
            self.driverExtension = 'H5'
        else:
            self.driverExtension = 'xxx'
        if self.GLBLoutRasterDriver == "GTiff":
            self.outputOptions = ['COMPRESS=LZW']
            self.outputOptions.append('BIGTIFF=YES')
        else:
            self.outputOptions = []
        #===========================================================================

        if self.GLBLambitoTiffNuevo == 'FicherosTiffIndividuales' or self.GLBLambitoTiffNuevo == 'ConvertirSoloUnFicheroASC':
            idAmbitoTif = 'Indi'
        elif self.GLBLambitoTiffNuevo == 'rasterDest_CyL' or self.GLBLambitoTiffNuevo == 'rasterRefe_CyL' or self.GLBLambitoTiffNuevo[:3] == 'CyL':
            idAmbitoTif = 'CyL'
        elif self.GLBLambitoTiffNuevo == 'loteAsc':
            idAmbitoTif = 'Lote'
        else:
            idAmbitoTif = 'Lote'
        self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars = '{}_{}_Global{}.{}'.format('uniCellAllDasoVars', self.idInputDir, idAmbitoTif, self.driverExtension)

        self.LOCLoutPathNameRuta = os.path.join(self.LOCLrutaAscRaizBase, self.LOCLoutputSubdirNew)

        myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Outputs:')
        myLog.info(f'{TB}-> Ruta para los ficheros de salida:')
        myLog.info(f'{TB}{TV}{self.LOCLoutPathNameRuta}')
        myLog.info(f'{TB}-> Se crea un fichero merge con todas las variables dasoLidar:')
        myLog.info(f'{TB}{TV}{self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars}')

        if self.marcoCoordDisponible and TRNS_buscarBloquesSoloDentroDelMarcoUTM:
            myLog.info(f'{TB}{TV}-> Integra todos los bloques localizados dentro del rango de coordenadas: '
                  f'X: {self.LOCLmarcoCoordMiniX:10.2f}-{self.LOCLmarcoCoordMaxiX:10.2f}; '
                  f'Y: {self.LOCLmarcoCoordMiniY:10.2f}-{self.LOCLmarcoCoordMaxiY:10.2f}')
        else:
            myLog.info(f'{TB}{TV}-> Integra todos los bloques localizados ')
        myLog.info(f'{TB}{TV}-> Una variable en cada banda mas dos bandas adicionales con tipo de bosque (MFE) y tipo de masa (ad-hoc)')

        if not os.path.exists(self.LOCLoutPathNameRuta):
            myLog.info(f'{TB}-> No existe directorio %s -> Se crea automaticamente' % (self.LOCLoutPathNameRuta))
            try:
                os.makedirs(self.LOCLoutPathNameRuta)
            except:
                myLog.error('\nATENCION: No se ha podido crear el directorio {}'.format(self.LOCLoutPathNameRuta))
                myLog.error(f'{TB}Revisar derechos de escritura en esa ruta')
                sys.exit(0)
        else:
            myLog.info(f'{TB}-> Ya existe el directorio {self.LOCLoutPathNameRuta}')
            myLog.info(f'{TB}{TV}-> Se agregan los outputs (tif, txt, npz, ...) a este directorio')
        myLog.info('{:=^80}'.format(''))
        # ======================================================================

        # ======================================================================
        # Primer tipo de fichero (y de variable) de la lista:
        (
            self.noDataDasoVarAll,
            self.outputGdalDatatypeAll,
            self.outputNpDatatypeAll,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nFicherosDisponiblesPorTipoVariable,
            self.arrayMinVariables,
            self.arrayMaxVariables,
            self.nMinTipoMasa,
            self.nMaxTipoMasa,
        ) = clidraster.crearRasterTiff(
            # self.LOCLrutaAscRaizBase,
            # self_inFilesListAllTypes=self.inFilesListAllTypes,
            self_inFilesDictAllTypes=self.inFilesDictAllTypes,
            self_LOCLoutPathNameRuta=self.LOCLoutPathNameRuta,
            self_LOCLoutFileNameWExt=self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
            self_LOCLlistaDasoVarsFileTypes=self.LOCLlistaDasoVarsFileTypes,

            PAR_rasterPixelSize=self.LOCLrasterPixelSize,
            PAR_outRasterDriver=self.GLBLoutRasterDriver,
            PAR_noDataTiffProvi=self.GLBLnoDataTiffProvi,
            PAR_noDataMergeTiff=self.GLBLnoDataTiffFiles,
            PAR_outputOptions=self.outputOptions,
            PAR_nInputVars=self.nInputVars,
            PAR_outputGdalDatatype=None,
            PAR_outputNpDatatype=None,

            PAR_cartoMFEpathName=self.LOCLcartoMFEpathName,
            PAR_cartoMFEfileName=self.LOCLcartoMFEfileName,
            PAR_cartoMFEfileSoloExt=self.LOCLcartoMFEfileSoloExt,
            PAR_cartoMFEfileNSinExt=self.LOCLcartoMFEfileNSinExt,

            PAR_cartoMFEcampoSp=self.LOCLcartoMFEcampoSp,
            PAR_cartoMFErecorte=self.GLBLcartoMFErecorte,

            PAR_generarDasoLayers=True,
            PAR_ambitoTiffNuevo=self.GLBLambitoTiffNuevo,
            PAR_verbose=self.LOCLverbose,
        )

    # ==========================================================================
    def analyzeMultiDasoLayerRasterFile(
            self,
            LCL_patronVectrName=None,
            LCL_patronLayerName=None,
            LCL_patronFieldName=None,
            LCL_tipoDeMasaSelec=None,
        ):
        f"""Analize the dasoLidar Variables included in the created raster file (with one band for every DLV).
        ----------
        LCL_patronVectrName : str
            Default: None (optional)
        LCL_patronLayerName : str
            Default: None (optional)
        LCL_patronFieldName : str
            Default: None (optional)
        LCL_tipoDeMasaSelec : str
            Default: None (optional)
        """
        #===========================================================================
        # distanciaEuclideaMediaPatronTesteo
        # distanciaEuclideaMediaPatronpatron
        # DistanciaEuclideaRazon
        # PorcentajeDeProximidad
        # CoeficienteParidad
        # Proximidad
        # Semejanza
        # Similitud
        # Analogia
        # Homogeneidad
        #===========================================================================

        if LCL_patronVectrName is None:
            self.LOCLpatronVectrName = GLO.GLBLpatronVectrNamePorDefecto
        else:
            self.LOCLpatronVectrName = LCL_patronVectrName
        if LCL_patronLayerName is None:
            self.LOCLpatronLayerName = GLO.GLBLpatronLayerNamePorDefecto
        else:
            self.LOCLpatronLayerName = LCL_patronLayerName
        if LCL_patronFieldName is None:
            self.LOCLpatronFieldName = GLO.GLBLpatronFieldNamePorDefecto
        else:
            self.LOCLpatronFieldName = LCL_patronFieldName
        self.LOCLtipoDeMasaSelec = LCL_tipoDeMasaSelec

        #=======================================================================
        (
            self.outputRangosFileTxtSinPath,
            self.outputRangosFileNpzSinPath,
            self.nBandasRasterOutput,
            self.rasterDatasetAll,
            self.listaCeldasConDasoVarsOkPatron,
            self.dictHistProb01,
            self.listHistProb01,
            self.myNBins,
            self.myRange,
            self.pctjTipoBosquePatronMasFrecuente1,
            self.codeTipoBosquePatronMasFrecuente1,
            self.pctjTipoBosquePatronMasFrecuente2,
            self.codeTipoBosquePatronMasFrecuente2,
            self.histProb01PatronBosque,
        ) = clidtwinx.recortarRasterTiffPatronDasoLidar(
            self.LOCLrutaAscRaizBase,
            self.LOCLoutPathNameRuta,
            self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
            self.noDataDasoVarAll,
            self.outputNpDatatypeAll,
            self.nMinTipoMasa,
            self.nMaxTipoMasa,
            self.nInputVars,
            self.nFicherosDisponiblesPorTipoVariable,
            self_LOCLlistaDasoVarsMovilidad=self.LOCLlistaDasoVarsMovilidad,
            # self_LOCLlistaDasoVarsPonderado=self.LOCLlistaDasoVarsPonderado,
            self_LOCLvarsTxtFileName=self.GLBLvarsTxtFileName,
            self_LOCLpatronVectrName=self.LOCLpatronVectrName,
            self_LOCLpatronLayerName=self.LOCLpatronLayerName,
            self_LOCLpatronFieldName=self.LOCLpatronFieldName,
            self_LOCLtipoDeMasaSelec=self.LOCLtipoDeMasaSelec,
            self_LOCLlistLstDasoVars=self.LOCLlistLstDasoVars,

            self_nCeldasX_Destino=self.nCeldasX_Destino,
            self_nCeldasY_Destino=self.nCeldasY_Destino,
            self_metrosPixelX_Destino=self.metrosPixelX_Destino,
            self_metrosPixelY_Destino=self.metrosPixelY_Destino,
            self_nMinX_tif=self.nMinX_tif,
            self_nMaxY_tif=self.nMaxY_tif,

            self_LOCLverbose=self.LOCLverbose,
        )
        # ======================================================================
        if self.rasterDatasetAll is None:
            return

        if self.nBandasRasterOutput != self.nBandasPrevistasOutput:
            myLog.error('clidtwins-> ATENCION: la capa creada con las dasoVars en la zona de referencia (patron) no niene el numero previsto de bandas')
            myLog.error(f'{TB}-> Numero de bandas en la capa creada {self.nBandasRasterOutput}; numero previsto: {self.nBandasPrevistasOutput}')
            sys.exit(0)

        clidtwinx.mostrarExportarRangos(
            self.LOCLoutPathNameRuta,
            self.outputRangosFileNpzSinPath,
            self.dictHistProb01,
            self.listHistProb01,
            self.nInputVars,
            self.myRange,
            self.myNBins,
            self.nFicherosDisponiblesPorTipoVariable,
            self_LOCLvarsTxtFileName=self.GLBLvarsTxtFileName,
            self_LOCLlistLstDasoVars=self.LOCLlistLstDasoVars,
        )

    # ==========================================================================
    def verificaCreateAnalyzeMultiDasoLayer(self, procesoObjetivo='generar el rasterCluster'):
        if self.idInputDir is None:
            myLog.warning(f'clidtwins-> Aviso: antes de generar el rasterCluster hay que:')
            myLog.warning(f'{TB}1. Buscar ficheros asc con las las variables DasoLidar (funcion searchSourceFiles<>)')
            myLog.warning(f'{TB}{TV}-> Se genera la lista inFilesListAllTypes')
            myLog.warning(f'{TB}2. Generar el raster con todas las variables DasoLidar (funcion createMultiDasoLayerRasterFile<>)')
            myLog.warning(f'{TB}{TV}-> Al abrirlo se obtiene el dataset rasterDatasetAll')
            myLog.warning(f'{TB}3. Calcular los rangos de las variables Dasolidar (funcion analyzeMultiDasoLayerRasterFile<>)')
            myLog.warning(f'{TB}{TV}-> Se genera el dict dictHistProb01')
            self.variablesDasoLidarAnalizadas = False
        elif self.rasterDatasetAll is None:
            myLog.warning(f'clidtwins-> Aviso: antes de {procesoObjetivo} hay que:')
            myLog.warning(f'{TB}1. Generar el raster con todas las variables DasoLidar (con la funcion createMultiDasoLayerRasterFile<>)')
            myLog.warning(f'{TB}{TV}-> Al abrirlo se obtiene el dataset rasterDatasetAll')
            myLog.warning(f'{TB}2. Calcular los rangos de las variables Dasolidar (con la funcion analyzeMultiDasoLayerRasterFile<>)')
            myLog.warning(f'{TB}{TV}-> Se genera el dict dictHistProb01')
            self.variablesDasoLidarAnalizadas = False
        elif self.dictHistProb01 is None:
            myLog.warning(f'clidtwins-> Aviso: antes de generar el rasterCluster hay que:')
            myLog.warning(f'{TB}calcular los rangos de las variables Dasolidar (con la funcion analyzeMultiDasoLayerRasterFile<>)')
            myLog.warning(f'{TB}{TV}-> Se genera el dict dictHistProb01')
            self.variablesDasoLidarAnalizadas = False
        else:
            self.variablesDasoLidarAnalizadas = True


    # ==========================================================================
    def chequearCompatibilidadConTesteoVector(
            self,
            LCL_testeoVectrName=None,
            LCL_testeoLayerName=None,
        ):
        # Variables de clase (previamente definidas) que se usan en esta funcion:
        # self.LOCLrutaAscRaizBase,
        # self.LOCLoutPathNameRuta,
        # self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars,
        # self.noDataDasoVarAll,
        # self.outputNpDatatypeAll,
        # self.nBandasPrevistasOutput,
        # self.nInputVars,
        # self.nFicherosDisponiblesPorTipoVariable,
        # self.listaCeldasConDasoVarsOkPatron,
        # self.dictHistProb01,
        # self.myNBins,
        # self.myRange,
        # self.ññ
        # self.pctjTipoBosquePatronMasFrecuente1,
        # self.codeTipoBosquePatronMasFrecuente1,
        # self.pctjTipoBosquePatronMasFrecuente2,
        # self.codeTipoBosquePatronMasFrecuente2,
        # self.histProb01Patron,
        # self.GLBLumbralMatriDist,
        # self.LOCLlistLstDasoVars,
        self.LOCLtesteoVectrName = LCL_testeoVectrName
        self.LOCLtesteoLayerName = LCL_testeoLayerName

        self.verificaCreateAnalyzeMultiDasoLayer(procesoObjetivo='chequear la compatibilidad')
        if not self.variablesDasoLidarAnalizadas:
            return False

        if ':/' in self.LOCLtesteoVectrName or ':\\' in self.LOCLtesteoVectrName:
            testeoVectrNameConPath = self.LOCLtesteoVectrName
        else:
            testeoVectrNameConPath = os.path.join(self.LOCLrutaAscRaizBase, self.LOCLtesteoVectrName)
        mergedUniCellAllDasoVarsFileNameConPath = os.path.join(self.LOCLoutPathNameRuta, self.LOCLoutFileNameWExt_mergedUniCellAllDasoVars)
        outputRasterNameClip = mergedUniCellAllDasoVarsFileNameConPath.replace('Global', 'Testeo')
        myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Recortando raster: {mergedUniCellAllDasoVarsFileNameConPath}')
        myLog.info(f'{TB}con perimetro de testeo: {testeoVectrNameConPath}')
        rasterDataset = gdal.Open(mergedUniCellAllDasoVarsFileNameConPath, gdalconst.GA_ReadOnly)

        # outputBand1 = rasterDataset.GetRasterBand(1)
        # arrayBanda1 = outputBand1.ReadAsArray().astype(self.outputNpDatatypeAll)
        # Ver: https://gdal.org/python/osgeo.gdal-module.html
        try:
            rasterDatasetClip = gdal.Warp(
                outputRasterNameClip,
                rasterDataset,
                cutlineDSName=testeoVectrNameConPath,
                cutlineLayer=self.LOCLtesteoLayerName,
                cropToCutline=True,
                # dstNodata=np.nan,
                dstNodata=self.noDataDasoVarAll,
            )
        except:
            myLog.error(f'\nclidtwins-> No se ha podido recortar el raster generado con {testeoVectrNameConPath}, cutlineLayer: {self.LOCLtesteoLayerName}, {type(self.LOCLtesteoLayerName)}')
            myLog.error(f'\nRevisar si se ha generado adecuadamente el raster {mergedUniCellAllDasoVarsFileNameConPath}')
            myLog.error(f'\nRevisar si la capa vectorial de testeo es correcta, no esta bloqueada y tiene un poligono.')
            if '.shp' in testeoVectrNameConPath and self.LOCLtesteoLayerName != '':
                myLog.error(f'\nRevisar si el layer indicado ({self.LOCLtesteoLayerName}) es el correcto para la capa {testeoVectrNameConPath} (para shp poner layer = "").')
            elif '.gpkg' in testeoVectrNameConPath and self.LOCLtesteoLayerName == '':
                myLog.error(f'\nRevisar si se ha indicado en la configuracion el layer para el fichero {testeoVectrNameConPath} (layer indicado: <{self.LOCLtesteoLayerName}>')
            else:
                myLog.error(f'\nRevisar si la capa vectorial de recorte incluye el layer {self.LOCLtesteoLayerName}, no esta bloqueada y (tiene un poligono) {testeoVectrNameConPath}')
            sys.exit(0)

        rasterDatasetClip = gdal.Open(outputRasterNameClip, gdalconst.GA_ReadOnly)
        nBandasRasterOutput = rasterDatasetClip.RasterCount
        if nBandasRasterOutput != self.nBandasPrevistasOutput:
            myLog.warning(f'\nAVISO: el numero de bandas del raster generado ({nBandasRasterOutput}) no es igual al previsto ({self.nBandasPrevistasOutput}), es decir num. de variables + 2 (num variables: {self.nInputVars})')

        outputBand1Clip = rasterDatasetClip.GetRasterBand(1)
        arrayBanda1Clip = outputBand1Clip.ReadAsArray().astype(self.outputNpDatatypeAll)
        # Se recorren todas las variables para generar una Mascara
        # con unos en celdas con alguna variable noData
        arrayBandaXMaskTesteo = np.full_like(arrayBanda1Clip, 0, dtype=np.uint8)
        arrayBandaXPesoTesteo = np.full_like(arrayBanda1Clip, 1, dtype=np.uint8)
        for nBanda in range(1, nBandasRasterOutput + 1):
            outputBandXClip = rasterDatasetClip.GetRasterBand(nBanda)
            arrayBandaXClip = outputBandXClip.ReadAsArray().astype(self.outputNpDatatypeAll)
            arrayBandaXMaskTesteo[arrayBandaXClip == self.noDataDasoVarAll] = 1
            arrayBandaXPesoTesteo[arrayBandaXClip == self.noDataDasoVarAll] = 0

        nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskTesteo == 0)
        listaCeldasConDasoVarsTesteo = np.zeros(nCeldasConDasoVarsOk * nBandasRasterOutput, dtype=self.outputNpDatatypeAll).reshape(nCeldasConDasoVarsOk, nBandasRasterOutput)
        myLog.info(f'{TB}-> Numero de celdas Testeo con dasoVars ok: {nCeldasConDasoVarsOk}')

        # Las self.nInputVars primeras bandas corresponden a las variables utilizadas (self_LOCLlistaDasoVarsFileTypes)
        # La penultima corresponde al tipo de bosque o cobertura MFE
        # La ultima corresponde al tipo de masa.
        # La numeracion de las bandas empieza en 1 y la de variables empieza en 0.
        nVariablesNoOk = 0
        tipoBosqueOk = 0
        for nBanda in range(1, nBandasRasterOutput + 1):
            # Si para esa variable estan todos los bloques:
            nInputVar = nBanda - 1
            if nInputVar >= 0 and nInputVar < self.nInputVars:
                if self.nFicherosDisponiblesPorTipoVariable[nInputVar] != self.nFicherosDisponiblesPorTipoVariable[0]:
                    # myLog.warning(f'\nHistograma para banda {nBanda} (variable {nInputVar}: {self.LOCLlistLstDasoVars[nInputVar][1]})')
                    claveRef = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_ref'
                    myLog.warning(f'{TB}-> (2) Chequeando rangos admisibles para: {claveRef}')
                    myLog.warning(f'{TB}AVISO: La banda {nBanda} (variable {nInputVar}) no cuenta con fichero para todos los bloques ({self.nFicherosDisponiblesPorTipoVariable[nInputVar]} de {self.nFicherosDisponiblesPorTipoVariable[0]})')
                    continue
            outputBandXClip = rasterDatasetClip.GetRasterBand(nBanda)
            arrayBandaXClip = outputBandXClip.ReadAsArray().astype(self.outputNpDatatypeAll)
            # hist = histogram(arrayBandaXClip)
            # hist = np.histogram(arrayBandaXClip, bins=5, range=(0, arrayBandaXClip.max()))

            # https://numpy.org/doc/stable/reference/maskedarray.html
            # https://numpy.org/doc/stable/reference/routines.ma.html#conversion-operations
            arrayBandaXClipMasked = ma.masked_array(
                arrayBandaXClip,
                mask=arrayBandaXMaskTesteo, # misma mascara para todas las bandas (enmascara cuando alguna dasoVar es noData)
                dtype=self.outputNpDatatypeAll
                )
            myLog.debug(f'Numero de puntos Testeo con dasoVars ok (banda {nBanda}): {len(ma.compressed(arrayBandaXClipMasked))}')

            listaCeldasConDasoVarsTesteo[:, nInputVar] = ma.compressed(arrayBandaXClipMasked)
            celdasConValorSiData = arrayBandaXClip[
                (arrayBandaXPesoTesteo != 0)
                & (arrayBandaXClip != self.noDataDasoVarAll)
                & (arrayBandaXClip >= self.myRange[nBanda][0])
                & (arrayBandaXClip < self.myRange[nBanda][1])
            ]
            if (
                (np.count_nonzero(celdasConValorSiData) > 0)
                & (self.myNBins[nBanda] > 0)
                & (self.myRange[nBanda][1] - self.myRange[nBanda][0] > 0)
            ):
                histNumberTesteo = np.histogram(
                    arrayBandaXClip,
                    bins=self.myNBins[nBanda],
                    range=self.myRange[nBanda],
                    weights=arrayBandaXPesoTesteo,
                )
                histProbabTesteo = np.histogram(
                    arrayBandaXClip,
                    bins=self.myNBins[nBanda],
                    range=self.myRange[nBanda],
                    weights=arrayBandaXPesoTesteo,
                    density=True,
                )
            else:
                myLog.info(f'clidtwins-> Aviso: (a) Revisar myNBins {self.myNBins[nBanda]} y myRange {self.myRange[nBanda]} para banda {nBanda} con sumaValores: {arrayBandaXClip.sum()}')
                myLog.info(f'{TB}Se crean histogramas con {self.myNBins} clases nulas')
                histNumberTesteo = [np.zeros(self.myNBins[nBanda]), None]
                histProbabTesteo = [np.zeros(self.myNBins[nBanda]), None]
            # myLog.debug(f'\nhistProbabTesteo[0]: {type(histProbabTesteo[0])}')
            histProb01Testeo = np.array(histProbabTesteo[0]) * ((self.myRange[nBanda][1] - self.myRange[nBanda][0]) / self.myNBins[nBanda])

            # if nBanda == nBandasRasterOutput:
            #     myLog.debug(f'\nHistograma para tipos de masa (banda {nBanda})')
            # elif nBanda == nBandasRasterOutput - 1:
            #     myLog.debug(f'\nHistograma para tipos de bosque (banda {nBanda})')
            # else:
            #     if nInputVar < len(self.LOCLlistLstDasoVars):
            #         myLog.debug(f'\nHistograma para banda {nBanda} (variable {nInputVar}: {self.LOCLlistLstDasoVars[nInputVar][1]})')
            #     else:
            #         myLog.debug(f'\nHistograma para banda {nBanda} (variable {nInputVar} de {self.LOCLlistLstDasoVars})')
            # myLog.debug(f'{TB}-> Numero puntos: {(histNumberTesteo[0]).sum()}-> {histNumberTesteo}')
            # # myLog.debug(f'{TB}-> Suma frecuencias: {round(histProb01Testeo.sum(), 2)}')

            if nBanda == nBandasRasterOutput - 1:
                myLog.debug(f'\nChequeando Tipos de bosque (banda {nBanda}):')
                try:
                    tipoBosqueUltimoNumero = np.max(np.nonzero(histNumberTesteo[0])[0])
                except:
                    tipoBosqueUltimoNumero = 0
                histogramaTemp = (histNumberTesteo[0]).copy()
                histogramaTemp.sort()
                codeTipoBosqueTesteoMasFrecuente1 = (histNumberTesteo[0]).argmax(axis=0)
                arrayPosicionTipoBosqueTesteo1 = np.where(histNumberTesteo[0] == histogramaTemp[-1])
                arrayPosicionTipoBosqueTesteo2 = np.where(histNumberTesteo[0] == histogramaTemp[-2])
                myLog.debug(f'{TB}-> Tipo de bosque principal (testeo): {codeTipoBosqueTesteoMasFrecuente1}; frecuencia: {int(round(100 * histProb01Testeo[codeTipoBosqueTesteoMasFrecuente1], 0))} %')
                # myLog.debug(f'{TB}-> {arrayPosicionTipoBosqueTesteo1}')
                for contadorTB1, numPosicionTipoBosqueTesteo1 in enumerate(arrayPosicionTipoBosqueTesteo1[0]):
                    # myLog.debug(f'{TB}-> {numPosicionTipoBosqueTesteo1}')
                    myLog.debug(f'{TB}-> {contadorTB1} Tipo de bosque primero (testeo): {numPosicionTipoBosqueTesteo1}; frecuencia: {int(round(100 * histProb01Testeo[numPosicionTipoBosqueTesteo1], 0))} %')
#ñññ
                if self.histProb01PatronBosque[arrayPosicionTipoBosqueTesteo2[0][0]] != 0:
                    for contadorTB2, numPosicionTipoBosqueTesteo2 in enumerate(arrayPosicionTipoBosqueTesteo2[0]):
                        myLog.debug(f'{TB}-> numPosicionTipoBosqueTesteo2: {numPosicionTipoBosqueTesteo2}')
                        if histProb01Testeo[numPosicionTipoBosqueTesteo2] != 0:
                            myLog.debug(f'{TB}-> {contadorTB2} Tipo de bosque segundo (testeo): {numPosicionTipoBosqueTesteo2}; frecuencia: {int(round(100 * histProb01Testeo[numPosicionTipoBosqueTesteo2], 0))} %')
                else:
                    myLog.debug(f'{TB}-> Solo hay tipo de bosque princial')

                if codeTipoBosqueTesteoMasFrecuente1 != arrayPosicionTipoBosqueTesteo1[0][0]:
                    myLog.critical(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoBosqueTesteoMasFrecuente1} != {arrayPosicionTipoBosqueTesteo1[0][0]}')
                if len(arrayPosicionTipoBosqueTesteo1[0]) == 1:
                    codeTipoBosqueTesteoMasFrecuente2 = arrayPosicionTipoBosqueTesteo2[0][0]
                else:
                    codeTipoBosqueTesteoMasFrecuente2 = arrayPosicionTipoBosqueTesteo1[0][1]

                pctjTipoBosqueTesteoMasFrecuente1 = int(round(100 * histProb01Testeo[codeTipoBosqueTesteoMasFrecuente1], 0))
                pctjTipoBosqueTesteoMasFrecuente2 = int(round(100 * histProb01Testeo[codeTipoBosqueTesteoMasFrecuente2], 0))

                myLog.debug(f'{TB}-> Tipos de bosque mas frecuentes (testeo): 1-> {codeTipoBosqueTesteoMasFrecuente1} ({pctjTipoBosqueTesteoMasFrecuente1} %); 2-> {codeTipoBosqueTesteoMasFrecuente2} ({pctjTipoBosqueTesteoMasFrecuente2} %)')

                # myLog.debug(f'{TB}-> Numero pixeles de cada tipo de bosque (testeo) ({(histNumberTesteo[0]).sum()}):\n{histNumberTesteo[0][:tipoBosqueUltimoNumero + 1]}')
                myLog.debug(f'{TB}-> Numero pixeles de cada tipo de bosque (testeo) ({(histNumberTesteo[0]).sum()}):')
                for numTipoBosque in range(len(histNumberTesteo[0])):
                    if histNumberTesteo[0][numTipoBosque] != 0:
                        myLog.debug(f'tipoBosque: {numTipoBosque} -> nPixeles: {histNumberTesteo[0][numTipoBosque]}')

                if self.pctjTipoBosquePatronMasFrecuente1 >= 70 and pctjTipoBosqueTesteoMasFrecuente1 >= 70:
                    if (codeTipoBosqueTesteoMasFrecuente1 == self.codeTipoBosquePatronMasFrecuente1):
                        myLog.info(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion SI ok:')
                        myLog.info(f'{TB}{TV}-> Tipo mas frecuente (patron): 1-> {self.codeTipoBosquePatronMasFrecuente1} ({self.pctjTipoBosquePatronMasFrecuente1} %)')
                        myLog.info(f'{TB}{TV}-> Tipo mas frecuente (testeo): 1-> {codeTipoBosqueTesteoMasFrecuente1} ({pctjTipoBosqueTesteoMasFrecuente1} %)')
                        tipoBosqueOk = 10
                    else:
                        binomioEspecies = f'{codeTipoBosqueTesteoMasFrecuente1}_{self.codeTipoBosquePatronMasFrecuente1}'
                        if binomioEspecies in (GLO.GLBLdictProximidadInterEspecies).keys():
                            tipoBosqueOk = GLO.GLBLdictProximidadInterEspecies[binomioEspecies]
                        else:
                            tipoBosqueOk = 0
                        myLog.info(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion NO ok: {tipoBosqueOk}')
                else:
                    if (
                        codeTipoBosqueTesteoMasFrecuente1 == self.codeTipoBosquePatronMasFrecuente1
                        and codeTipoBosqueTesteoMasFrecuente2 == self.codeTipoBosquePatronMasFrecuente2
                    ):
                        myLog.info(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo SI ok:')
                        tipoBosqueOk = 10
                    elif (
                        codeTipoBosqueTesteoMasFrecuente1 == self.codeTipoBosquePatronMasFrecuente2
                        and codeTipoBosqueTesteoMasFrecuente2 == self.codeTipoBosquePatronMasFrecuente1
                    ):
                        myLog.info(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo XX ok:')
                        tipoBosqueOk = 10
                    else:
                        binomioEspecies = f'{codeTipoBosqueTesteoMasFrecuente1}_{self.codeTipoBosquePatronMasFrecuente1}'
                        if binomioEspecies in (GLO.GLBLdictProximidadInterEspecies).keys():
                            tipoBosqueOk = GLO.GLBLdictProximidadInterEspecies[binomioEspecies] - 1
                        else:
                            tipoBosqueOk = 0
                        myLog.info(f'{TB}-> Tipos de bosque principal (menos del 70 de ocupacion) y segundo NO ok: {tipoBosqueOk}')
                    myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (patron): 1-> {self.codeTipoBosquePatronMasFrecuente1} ({self.pctjTipoBosquePatronMasFrecuente1} %)')
                    myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (testeo): 1-> {codeTipoBosqueTesteoMasFrecuente1} ({pctjTipoBosqueTesteoMasFrecuente1} %)')
                    myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (patron): 2-> {self.codeTipoBosquePatronMasFrecuente2} ({self.pctjTipoBosquePatronMasFrecuente2} %)')
                    myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (testeo): 2-> {codeTipoBosqueTesteoMasFrecuente2} ({pctjTipoBosqueTesteoMasFrecuente2} %)')

            elif nInputVar >= 0 and nInputVar < self.nInputVars:
                claveRef = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_ref'
                claveMin = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_min'
                claveMax = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_max'
                # self.dictHistProb01[claveRef] = histProb01Testeo



                if self.calcularRangoVariables:
                    print('\n{:_^80}'.format(''))
                    print('\n\n\nclidtwins-> ATENCION: calcular rangos aqui.\n\n\n')
                    print('{:=^80}'.format(''))




                myLog.debug(f'{TB}-> (3) Chequeando rangos admisibles para: {claveRef}')
                # myLog.debug(f'{TB}Valores de referencia:')
                # myLog.debug(f'{TB}{TV}-> self.dictHistProb01[claveRef]: {self.dictHistProb01[claveRef]}')
                todosLosRangosOk = True
                nTramosFueraDeRango = 0
                # for nRango in range(len(histProb01Testeo)):
                for nRango in range(self.myNBins[nBanda]):
                    histProb01Testeo[nRango] = round(histProb01Testeo[nRango], 3)
                    limInf = nRango * (self.myRange[nBanda][1] - self.myRange[nBanda][0]) / self.myNBins[nBanda]
                    limSup = (nRango + 1) * (self.myRange[nBanda][1] - self.myRange[nBanda][0]) / self.myNBins[nBanda]
                    miRango = f'{limInf}-{limSup}'
                    if histProb01Testeo[nRango] < self.dictHistProb01[claveMin][nRango]:
                        myLog.debug(f'{TB}-> {claveRef}-> nRango {nRango} de {self.myNBins[nBanda]} ({miRango}): {histProb01Testeo[nRango]} debajo del rango {self.dictHistProb01[claveMin][nRango]} - {self.dictHistProb01[claveMax][nRango]}; Valor de referencia: {self.dictHistProb01[claveRef][nRango]}')
                        todosLosRangosOk = False
                        nTramosFueraDeRango += 1
                    if histProb01Testeo[nRango] > self.dictHistProb01[claveMax][nRango]:
                        myLog.debug(f'{TB}-> {claveRef}-> nRango {nRango} ({miRango}): {histProb01Testeo[nRango]} encima del rango {self.dictHistProb01[claveMin][nRango]} - {self.dictHistProb01[claveMax][nRango]}; Valor de referencia: {self.dictHistProb01[claveRef][nRango]}')
                        todosLosRangosOk = False
                        nTramosFueraDeRango += 1
                if todosLosRangosOk:
                    myLog.info(f'{TB}-> Todos los tramos ok.')
                else:
                    myLog.info(f'{TB}-> Banda {nBanda}-> Numero de tramos fuera de rango: {nTramosFueraDeRango} de {self.myNBins[nBanda]}')
                    if nTramosFueraDeRango >= 1:
                        nVariablesNoOk += 1

        self.matrizDeDistanciasPatronTesteo = distance_matrix(self.listaCeldasConDasoVarsOkPatron, listaCeldasConDasoVarsTesteo)
        self.matrizDeDistanciasPatronPatron = distance_matrix(self.listaCeldasConDasoVarsOkPatron, self.listaCeldasConDasoVarsOkPatron)
        self.distanciaEuclideaMediaPatronTesteo = np.average(self.matrizDeDistanciasPatronTesteo)
        self.distanciaEuclideaMediaPatronPatron = np.average(self.matrizDeDistanciasPatronPatron)
        self.pctjPorcentajeDeProximidad = 100 * (
            np.count_nonzero(self.matrizDeDistanciasPatronTesteo < self.GLBLumbralMatriDist)
            / np.ma.count(self.matrizDeDistanciasPatronTesteo)
        )
        self.tipoBosqueOk = tipoBosqueOk
        self.nVariablesNoOk = nVariablesNoOk

        # myLog.debug('clidtwins-> Matriz de distancias:')
        # myLog.debug(self.matrizDeDistanciasPatronTesteo[:5,:5])
        myLog.info(f'clidtwins-> Resumen del match: (TM: {self.LOCLtipoDeMasaSelec})')
        myLog.info(f'{TB}-> tipoBosqueOk:                  {self.tipoBosqueOk}')
        myLog.info(f'{TB}-> nVariablesNoOk:                {self.nVariablesNoOk}')
        myLog.info(f'{TB}-> matrizDeDistancias.shape:      {self.matrizDeDistanciasPatronTesteo.shape}') 
        myLog.info(f'{TB}-> Distancia media patron-testeo: {self.distanciaEuclideaMediaPatronTesteo}')
        myLog.info(f'{TB}-> Distancia media patron-patron: {self.distanciaEuclideaMediaPatronPatron}')
        if self.distanciaEuclideaMediaPatronPatron:
            self.distanciaEuclideaRazon = self.distanciaEuclideaMediaPatronTesteo / self.distanciaEuclideaMediaPatronPatron
            myLog.info(f'{TB}-> Razon de distancias medias:    {self.distanciaEuclideaRazon}')
        else:
            self.distanciaEuclideaRazon = -1
        myLog.info(f'{TB}-> Factor de proximidad:          {self.pctjPorcentajeDeProximidad}')
        myLog.info('{:=^80}'.format(''))

        return True

    # ==========================================================================
    def generarRasterCluster(
            self,
            LCL_radioClusterPix=0,
        ):
        # Variables de clase (previamente definidas) que se usan en esta funcion:
        # self.nBandasRasterOutput,
        # self.rasterDatasetAll,
        # self.outputNpDatatypeAll,
        # self.LOCLoutPathNameRuta,
        # self.outputClusterAllDasoVarsFileNameSinPath,
        # self.outputClusterTipoBoscProFileNameSinPath,
        # self.outputClusterTipoMasaParFileNameSinPath,
        # self.outputClusterFactorProxiFileNameSinPath,
        # self.outputClusterDistanciaEuFileNameSinPath,
        # self.LOCLrasterPixelSize,
        # self.nMinX_tif,
        # self.nMaxY_tif,
        # self.nCeldasX_Destino,
        # self.nCeldasY_Destino,
        # self.metrosPixelX_Destino,
        # self.metrosPixelY_Destino,
        # self.LOCLoutRasterDriver,
        # self.outputOptions,
        # self.nInputVars,
        # self.noDataDasoVarAll,
        # self.GLBLnoDataTipoDMasa,
        # self.GLBLnoDataTiffFiles,
        # self.nBandasPrevistasOutput,
        # self.listaCeldasConDasoVarsOkPatron,
        # self.myNBins,
        # self.myRange,
        # self.pctjTipoBosquePatronMasFrecuente1,
        # self.codeTipoBosquePatronMasFrecuente1,
        # self.pctjTipoBosquePatronMasFrecuente2,
        # self.codeTipoBosquePatronMasFrecuente2,
        # self.dictHistProb01,
        # self.GLBLumbralMatriDist,
        # self.LOCLlistLstDasoVars,

        # ======================================================================
        # Lectura del raster con todas las variables en distintas bandas,
        # mas el tipo de bosque y el tipo de masa, por el momento sin asignar.
        # Requiere haber ejecutado antes createMultiDasoLayerRasterFile<>
        # Para generar el dict rasterDatasetAll con los datos de todas las bandas.
        # ======================================================================
        self.verificaCreateAnalyzeMultiDasoLayer(procesoObjetivo='generar el rasterCluster')
        if not self.variablesDasoLidarAnalizadas:
            return False

        # ======================================================================
        if LCL_radioClusterPix == 0:
            self.LOCLradioClusterPix = GLO.GLBLradioClusterPixPorDefecto
        elif LCL_radioClusterPix > 10:
            if self.LOCLverbose:
                myLog.warning('\n{:_^80}'.format(''))
                myLog.warning(f'clidtwins-> AVISO: radio de cluster excesivo ({LCL_radioClusterPix} pixeles); se reduce a 10 pixeles.')
                myLog.warning('{:=^80}'.format(''))
            self.LOCLradioClusterPix = 10
        else:
            self.LOCLradioClusterPix = LCL_radioClusterPix
        ladoCluster = (self.LOCLradioClusterPix * 2) + 1
        # ======================================================================
        self.maxDistanciaScipyMono = 0.0
        self.maxDistanciaScipySuma = 0.0

        if self.LOCLtipoDeMasaSelec is None:
            idTipoDeMasaSelec = ''
        else:
            idTipoDeMasaSelec = f'_TM{self.LOCLtipoDeMasaSelec}'
        # ======================================================================
        (
            self.outputClusterAllDasoVarsFileNameSinPath,
            self.outputClusterTipoMasaParFileNameSinPath,
            self.outputClusterDistanciaEuFileNameSinPath,
            self.outputClusterDistEuRazonFileNameSinPath,
            self.outputClusterFactorProxiFileNameSinPath,
            self.outputClusterTipoBoscProFileNameSinPath,
            self.outputClusterDistScipyM1FileNameSinPath,
            self.outputClusterDistScipyM2FileNameSinPath,
            self.outputClusterDistScipyM3FileNameSinPath,
            ) = getFileNamesDistScipy(self.idInputDir, idTipoDeMasaSelec, self.driverExtension)

        myLog.info('\n{:_^80}'.format(''))
        myLog.info('clidtwins-> Ficheros que se generan:')
        myLog.info(f'{TB}-> Fichero multibanda* con las variables dasoLidar clusterizadas (radio de {self.LOCLradioClusterPix} pixeles):')
        myLog.info(f'{TB}{TV}{self.outputClusterAllDasoVarsFileNameSinPath}')
        myLog.info(f'{TB}{TV}* Con todas las variables dasoLidar (una en cada banda) y dos bandas adicionales con tipo de bosque y tipo de masa.')

        myLog.info(f'{TB}-> Fichero monoBanda con presencia del tipo de bosque patron:')
        myLog.info(f'{TB}{TV}{self.outputClusterTipoBoscProFileNameSinPath}')
        myLog.info(f'{TB}-> Fichero monoBanda con presencia del tipo de masa patron:')
        myLog.info(f'{TB}{TV}{self.outputClusterTipoMasaParFileNameSinPath}')
        myLog.info(f'{TB}{TV}* Segunda banda: MFE')
        myLog.info(f'{TB}-> Fichero biBanda con la distancia euclidea al patron y proximidad a especie principal clusterizados:')
        myLog.info(f'{TB}{TV}{self.outputClusterDistanciaEuFileNameSinPath}')
        myLog.info(f'{TB}{TV}* Segunda banda: MFE')
        myLog.info(f'{TB}-> Fichero biBanda con la relacion entre distancia euclidea patro-testoe y patron-patron y proximidad a especie principal clusterizados:')
        myLog.info(f'{TB}{TV}{self.outputClusterDistEuRazonFileNameSinPath}')
        myLog.info(f'{TB}{TV}* Segunda banda: MFE')
        myLog.info(f'{TB}-> Fichero biBanda con el factor de proximidad al patron y proximidad a especie principal clusterizados:')
        myLog.info(f'{TB}{TV}{self.outputClusterFactorProxiFileNameSinPath}')
        myLog.info(f'{TB}-> Ficheros con nDasoVars bandas ({self.nInputVars}Banda), con las distancias scipy al patron clusterizado (methods 1, 2 y 3):')
        myLog.info(f'{TB}{TV}{self.outputClusterDistScipyM1FileNameSinPath}')
        myLog.info(f'{TB}{TV}{self.outputClusterDistScipyM2FileNameSinPath}')
        myLog.info(f'{TB}{TV}{self.outputClusterDistScipyM3FileNameSinPath}')
        # ======================================================================

        # ======================================================================
        # Lectura de las DLVs del dataset  rasterDatasetAll
        # arrayBandaXinputMonoPixelAll = {}
        if (
            not hasattr(self, 'nBandasRasterOutput')
            or not hasattr(self, 'nCeldasX_Destino')
            or not hasattr(self, 'nCeldasY_Destino')
        ):
            myLog.critical('\n{:_^80}'.format(''))
            myLog.critical(f'clidtwins-> ATENCION: Revisar codigo (no existen algunas variables despues de verificaCreateAnalyzeMultiDasoLayer<>).')
            myLog.critical('{:=^80}'.format(''))
            sys.exit(0)
        arrayBandaXinputMonoPixelAll = np.zeros(
            self.nBandasRasterOutput * self.nCeldasY_Destino * self.nCeldasX_Destino,
            dtype=self.outputNpDatatypeAll
        ).reshape(self.nBandasRasterOutput, self.nCeldasY_Destino, self.nCeldasX_Destino)

        # arrayBandaFlip = {}
        for nBanda in range(1, self.nBandasRasterOutput + 1):
            selecBandaXinputMonoPixelAll = self.rasterDatasetAll.GetRasterBand(nBanda)
            arrayBandaXinputMonoPixelAll[nBanda - 1] = selecBandaXinputMonoPixelAll.ReadAsArray().astype(self.outputNpDatatypeAll)
            # arrayBandaFlip[nBanda - 1] = np.flipud(arrayBandaXinputMonoPixelAll[nBanda - 1])
            # arrayBandaFlip[nBanda - 1] = arrayBandaXinputMonoPixelAll[nBanda - 1].copy()
            # if self.LOCLverbose == 3:
            #     myLog.debug(f'{TB}{TV}nBanda {nBanda}')
            #     myLog.debug(f'{TB}{TV}--->>> shape: {arrayBandaXinputMonoPixelAll[nBanda - 1].shape}')
            #     myLog.debug(f'{TB}{TV}-->> Dos fragmentos de arrayBandaXinputMonoPixelAll:')
            #     try:
            #         # myLog.debug(f'{TB}{TV}{TV}-->> {arrayBandaXinputMonoPixelAll[nBanda - 1][0:5, 2200:2210]}')
            #         # myLog.debug(f'{TB}{TV}{TV}-->> {arrayBandaXinputMonoPixelAll[nBanda - 1][195:199, 2200:2210]}')
            #         myLog.debug(f'{TB}{TV}{TV}-->> {arrayBandaXinputMonoPixelAll[nBanda - 1][0:5, 100:110]}')
            #         myLog.debug(f'{TB}{TV}{TV}-->> {arrayBandaXinputMonoPixelAll[nBanda - 1][195:199, 100:110]}')
            #     except:
            #         myLog.debug(f'{TB}{TV}{TV}-->> Fuera de rango; elegir otros rangos en codigo.')
        # ======================================================================

        # ======================================================================
        nBandasOutputMonoBanda = 1
        nBandasOutputBiBanda = 2
        nBandasOutputCluster = self.nInputVars + 2
        # ======================================================================
        if self.noDataDasoVarAll == 255 or self.noDataDasoVarAll == 0:
            self.outputGdalDatatypeAll = gdal.GDT_Byte
            self.outputNpDatatypeAll = np.uint8
        else:
            self.outputGdalDatatypeAll = gdal.GDT_Float32  # No existe GDT_Float16
            if TRNS_reducirConsumoRAM:
                self.outputNpDatatypeAll = np.float16
            else:
                self.outputNpDatatypeAll = np.float32
        self.outputGdalDatatypeFloatX = gdal.GDT_Float32
        if TRNS_reducirConsumoRAM:
            self.outputNpDatatypeFloatX = np.float16
        else:
            self.outputNpDatatypeFloatX = np.float32
        # ======================================================================

        # ======================================================================
        # Creacion de los raster (vacios), que albergaran:
        # 0. Monolayer con tipo de bosque similar al de referencia (patron)
        # 1. Monolayer con tipo de masa similar al de referencia (patron)
        # 2. Bilayer con DistanciaEu y MFE
        # 3. Bilayer con factorProxi y MFE
        # 4. MultiLayer clusterAllDasoVars
        # Los pixeles de estos raster integran el cluster correspondiente 

        # ======================================================================
        # 0. MonoLayer con presencia de tipo de masa similar al de referencia (patron)
        # ======================================================================
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Creando fichero para el layer tipoBosque {self.outputClusterTipoBoscProFileNameSinPath}')
        outputDatasetTipoBosc, outputBandaTipoBosc = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterTipoBoscProFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputMonoBanda,
            self.outputGdalDatatypeTipoMasa,
            self.outputNpDatatypeTipoMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )

        # ======================================================================
        # 1. MonoLayer con presencia de tipo de masa similar al de referencia (patron)
        # ======================================================================
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Creando fichero para el layer tipoMasa {self.outputClusterTipoMasaParFileNameSinPath}')
        outputDatasetTipoMasa, outputBandaTipoMasa = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterTipoMasaParFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputMonoBanda,
            self.outputGdalDatatypeTipoMasa,
            self.outputNpDatatypeTipoMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )

        # ======================================================================
        # 2. Bilayer con DistanciaEu y MFE
        # ======================================================================
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Creando fichero para el layer distanciaEu {self.outputClusterDistanciaEuFileNameSinPath}')
        outputDatasetDistanciaEuclideaMedia, outputBandaDistanciaEuclideaMedia = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterDistanciaEuFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputBiBanda,
            self.outputGdalDatatypeFloatX,
            self.outputNpDatatypeFloatX,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )
        outputBandaProximidadInterEspecies1a = outputDatasetDistanciaEuclideaMedia.GetRasterBand(2)

        # ======================================================================
        # 2a. Bilayer con razon de DistanciaEu patron-testeo a patron-patron y MFE
        # ======================================================================
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Creando fichero para el layer distanciaEu razon {self.outputClusterDistEuRazonFileNameSinPath}')
        outputDatasetDistanciaEuclideaRazon, outputBandaDistanciaEuclideaRazon = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterDistEuRazonFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputBiBanda,
            self.outputGdalDatatypeFloatX,
            self.outputNpDatatypeFloatX,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )
        outputBandaProximidadInterEspecies1b = outputDatasetDistanciaEuclideaRazon.GetRasterBand(2)

        # ======================================================================
        # 3. Bilayer con factorProxi y MFE
        # ======================================================================
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Creando fichero para el layer factorProxi {self.outputClusterFactorProxiFileNameSinPath}')
        outputDatasetPorcentajeDeProximidad, outputBandaPorcentajeDeProximidad = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterFactorProxiFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputBiBanda,
            self.outputGdalDatatypeFloatX,
            self.outputNpDatatypeFloatX,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )
        outputBandaProximidadInterEspecies2 = outputDatasetPorcentajeDeProximidad.GetRasterBand(2)

        # ======================================================================
        # 4. MultiLayer clusterAllDasoVars
        # ======================================================================
        # Creacion del raster, con las variables y tipo de bosque clusterizados
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Creando fichero para el multiLayer clusterAllDasoVars {self.outputClusterAllDasoVarsFileNameSinPath}')
        outputDatasetClusterDasoVarMultiple, outputBandaClusterDasoVarBanda1 = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterAllDasoVarsFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nBandasOutputCluster,
            self.outputGdalDatatypeAll,
            self.outputNpDatatypeAll,
            self.noDataDasoVarAll,
            self.noDataDasoVarAll,
            self.GLBLnoDataTiffFiles,
            generarMetaPixeles=True,
        )

        myLog.info(f'clidtwins-> Creando fichero para el Layer con nVars+1 bandas clusterDistanScipyMethod1 {self.outputClusterDistScipyM1FileNameSinPath}')
        outputDatasetClusterDistanciaScipyMethod1, outputBandaDistanciaScipyMethod1Var0 = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputClusterDistScipyM1FileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            self.nInputVars + 1,
            self.outputGdalDatatypeFloatX,
            self.outputNpDatatypeFloatX,
            self.GLBLnoDataDistancia,
            self.GLBLnoDataDistancia,
            self.GLBLnoDataDistancia,
            generarMetaPixeles=True,
        )
        outputBandaDistanciaScipyMethod1 = {}
        for nInputVar in range(self.nInputVars + 1):
            outputBandaDistanciaScipyMethod1[nInputVar] = outputDatasetClusterDistanciaScipyMethod1.GetRasterBand(nInputVar + 1)

        if nScipyMethods >= 2:
            myLog.info(f'clidtwins-> Creando fichero para el Layer con nVars+1 bandas clusterDistanScipyMethod2 {self.outputClusterDistScipyM2FileNameSinPath}')
            outputDatasetClusterDistanciaScipyMethod2, outputBandaDistanciaScipyMethod2Var0 = clidraster.CrearOutputRaster(
                self.LOCLoutPathNameRuta,
                self.outputClusterDistScipyM2FileNameSinPath,
                self.nMinX_tif,
                self.nMaxY_tif,
                self.nCeldasX_Destino,
                self.nCeldasY_Destino,
                self.metrosPixelX_Destino,
                self.metrosPixelY_Destino,
                self.LOCLoutRasterDriver,
                self.outputOptions,
                self.nInputVars + 1,
                self.outputGdalDatatypeFloatX,
                self.outputNpDatatypeFloatX,
                self.GLBLnoDataDistancia,
                self.GLBLnoDataDistancia,
                self.GLBLnoDataDistancia,
                generarMetaPixeles=True,
            )
            outputBandaDistanciaScipyMethod2 = {}
            for nInputVar in range(self.nInputVars + 1):
                outputBandaDistanciaScipyMethod2[nInputVar] = outputDatasetClusterDistanciaScipyMethod2.GetRasterBand(nInputVar + 1)

        if nScipyMethods >= 3:
            myLog.info(f'clidtwins-> Creando fichero para el Layer con nVars+1 bandas clusterDistanScipyMethod3 {self.outputClusterDistScipyM3FileNameSinPath}')
            outputDatasetClusterDistanciaScipyMethod3, outputBandaDistanciaScipyMethod3Var0 = clidraster.CrearOutputRaster(
                self.LOCLoutPathNameRuta,
                self.outputClusterDistScipyM3FileNameSinPath,
                self.nMinX_tif,
                self.nMaxY_tif,
                self.nCeldasX_Destino,
                self.nCeldasY_Destino,
                self.metrosPixelX_Destino,
                self.metrosPixelY_Destino,
                self.LOCLoutRasterDriver,
                self.outputOptions,
                self.nInputVars + 1,
                self.outputGdalDatatypeFloatX,
                self.outputNpDatatypeFloatX,
                self.GLBLnoDataDistancia,
                self.GLBLnoDataDistancia,
                self.GLBLnoDataDistancia,
                generarMetaPixeles=True,
            )
            outputBandaDistanciaScipyMethod3 = {}
            for nInputVar in range(self.nInputVars + 1):
                outputBandaDistanciaScipyMethod3[nInputVar] = outputDatasetClusterDistanciaScipyMethod3.GetRasterBand(nInputVar + 1)

        if self.LOCLverbose:
            myLog.info('{:=^80}'.format(''))
        # ======================================================================

        # ======================================================================
        # Compruebo si puedo cargar la banda 1 en memoria
        myLog.debug('\n{:_^80}'.format(''))
        myLog.debug('clidtwins-> Comprobando memoria RAM disponible:')
        nBytesPorBanda = 4
        if psutilOk:
            ramMem = psutil.virtual_memory()
            megasLibres = ramMem.available / 1048576 # ~1E6
            megasReservados = 1000 if megasLibres > 2000 else megasLibres / 2
            myLog.debug('{}-> Megas libres: {:0.2f} MB'.format(TB, megasLibres))
            numMaximoPixeles = (megasLibres - megasReservados) * 1e6 / (self.nBandasRasterOutput * nBytesPorBanda)
            myLog.debug(
                '{}-> Num max. Pixeles: {:0.2f} MegaPixeles ({} bandas, {} bytes por pixel)'.format(
                    TB,
                    numMaximoPixeles / 1e6,
                    self.nBandasRasterOutput,
                    nBytesPorBanda
                )
            )
        else:
            numMaximoPixeles = 1e9
        nMegaPixeles = self.nCeldasX_Destino * self.nCeldasY_Destino / 1e6
        nMegaBytes = nMegaPixeles * self.nBandasRasterOutput * nBytesPorBanda
        myLog.debug(
            '{}-> nCeldas previstas:  {} x {} = {:0.2f} MegaPixeles = {:0.2f} MegaBytes'.format(
                TB,
                self.nCeldasX_Destino,
                self.nCeldasY_Destino,
                nMegaPixeles,
                nMegaBytes,
            )
        )
        if nMegaPixeles < numMaximoPixeles * 0.5:
            # Se puede cargar toda la banda1 en memoria
            cargarRasterEnMemoria = True
            # Creo un ndarray con el contenido de la banda 1 del raster dataset creado
            myLog.debug(f'{TB}-> SI se carga toda la banda en memoria.')
        else:
            cargarRasterEnMemoria = False
            myLog.debug(f'{TB}-> NO se carga toda la banda en memoria.')
            myLog.debug(f'{TB}{TV} OPCION PARCIALMENTE IMPLEMENTADA: seguir el procedimiento usado en mergeBloques<>')
            sys.exit(0)
        myLog.debug('{:=^80}'.format(''))
        # ======================================================================

        # ======================================================================
        arrayBandaTipoBosc = outputBandaTipoBosc.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
        arrayBandaTipoMasa = outputBandaTipoMasa.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
        arrayBandaDistanciaEuclideaMedia = outputBandaDistanciaEuclideaMedia.ReadAsArray().astype(self.outputNpDatatypeFloatX)
        arrayBandaDistanciaEuclideaRazon = outputBandaDistanciaEuclideaRazon.ReadAsArray().astype(self.outputNpDatatypeFloatX)
        arrayBandaPorcentajeDeProximidad = outputBandaPorcentajeDeProximidad.ReadAsArray().astype(self.outputNpDatatypeFloatX)
        arrayBandaClusterDasoVarBanda1 = outputBandaClusterDasoVarBanda1.ReadAsArray().astype(self.outputNpDatatypeAll)
        # ======================================================================
        arrayDistanciaEuclideaMedia = np.full_like(arrayBandaTipoMasa, self.GLBLnoDataTiffFiles, dtype=self.outputNpDatatypeFloatX)
        arrayDistanciaEuclideaRazon = np.full_like(arrayBandaTipoMasa, self.GLBLnoDataTiffFiles, dtype=self.outputNpDatatypeFloatX)
        arrayPctjPorcentajeDeProximidad = np.full_like(arrayBandaTipoMasa, self.GLBLnoDataTiffFiles, dtype=self.outputNpDatatypeFloatX)
        # ======================================================================
        arrayDistanciaScipy = np.zeros(
            (self.nInputVars + 1) * len(SCIPY_METHODS) * arrayBandaTipoMasa.shape[0] * arrayBandaTipoMasa.shape[1],
            dtype=self.outputNpDatatypeFloatX
        ).reshape(self.nInputVars + 1, len(SCIPY_METHODS), arrayBandaTipoMasa.shape[0], arrayBandaTipoMasa.shape[1])
        # Descartado: Pongo zeros en la ultima banda porque la uso para la suma ponderada de
        # las demas bandas, y el nodata que use en el resto:
        # arrayDistanciaScipy[self.nInputVars, ::] = 0
        # arrayDistanciaScipy[:self.nInputVars, ::] = self.GLBLnoDataDistancia
        # Descartado: Uso noData 0, asumiendo que ningun pixel tiene distancia 0
        # arrayDistanciaScipy.fill(0)
        # Opcion elegida: Uso noData self.GLBLnoDataDistancia, que se sustituye 
        # cuando empiezo a acumular distancias en la ultima banda
        arrayDistanciaScipy.fill(self.GLBLnoDataDistancia)
        # Convertir esto a uint8 (los arrays y el rasterDataset)
        # ======================================================================

        # ======================================================================
        # dictDtSetMultiBandaClusterDasoVars = {}
        # dictArrayMultiBandaClusterDasoVars = {}
        # Primeros dataset y banda:
        ds1 = outputDatasetClusterDasoVarMultiple.GetRasterBand(1)
        bd1 = ds1.ReadAsArray().astype(self.outputNpDatatypeAll)
        dictDtSetMultiBandaClusterDasoVars = [None]
        dictArrayMultiBandaClusterDasoVars = np.zeros(
            (self.nBandasPrevistasOutput + 1) * bd1.shape[0] * bd1.shape[1],
            dtype=self.outputNpDatatypeAll
        ).reshape(
            self.nBandasPrevistasOutput + 1, bd1.shape[0], bd1.shape[1]
        )
        for outputNBand in range(1, self.nBandasPrevistasOutput + 1):
            # dictDtSetMultiBandaClusterDasoVars[outputNBand] = outputDatasetClusterDasoVarMultiple.GetRasterBand(outputNBand)
            dictDtSetMultiBandaClusterDasoVars.append(outputDatasetClusterDasoVarMultiple.GetRasterBand(outputNBand))
            dictArrayMultiBandaClusterDasoVars[outputNBand] = dictDtSetMultiBandaClusterDasoVars[outputNBand].ReadAsArray().astype(self.outputNpDatatypeAll)
            # myLog.debug(f'{TB}-> Banda: {outputNBand} -> shape: {dictArrayMultiBandaClusterDasoVars[outputNBand].shape}')
        myLog.debug('\n{:_^80}'.format(''))
        myLog.debug(f'clidtwins-> Dimensiones de los raster creados (pixeles): {arrayBandaTipoMasa.shape}')
        myLog.debug(f'-> Tipo de dato de los rasters creados:')
        myLog.debug(
            f'{TB}-> Raster mono-banda con el tipo de bosque:       '
            f'{type(arrayBandaTipoBosc)}, dtype: {arrayBandaTipoBosc.dtype} '
            f'-> {self.outputClusterTipoBoscProFileNameSinPath}'
        )
        myLog.debug(
            f'{TB}-> Raster mono-banda con el tipo de masa:         '
            f'{type(arrayBandaTipoMasa)}, dtype: {arrayBandaTipoMasa.dtype} '
            f'-> {self.outputClusterTipoMasaParFileNameSinPath}'
        )
        myLog.debug(
            f'{TB}-> Raster bi-banda con la DistanciaEuclideaMedia: '
            f'{type(arrayBandaDistanciaEuclideaMedia)}, dtype: {arrayBandaDistanciaEuclideaMedia.dtype} '
            f'-> {self.outputClusterDistanciaEuFileNameSinPath}'
        )
        myLog.debug(
            f'{TB}-> Raster bi-banda con la razon de Distancias Euclideas Medias: '
            f'{type(arrayBandaDistanciaEuclideaRazon)}, dtype: {arrayBandaDistanciaEuclideaRazon.dtype} '
            f'-> {self.outputClusterDistEuRazonFileNameSinPath}'
        )
        myLog.debug(
            f'{TB}-> Raster bi-banda con el PorcentajeDeProximidad: '
            f'{type(arrayBandaPorcentajeDeProximidad)}, dtype: {arrayBandaPorcentajeDeProximidad.dtype} '
            f'-> {self.outputClusterFactorProxiFileNameSinPath}'
        )
        myLog.debug(
            f'{TB}-> Raster multi-banda con las clusterDasoVars:    '
            f'{type(arrayBandaClusterDasoVarBanda1)}, dtype: {arrayBandaClusterDasoVarBanda1.dtype} '
            f'-> {self.outputClusterAllDasoVarsFileNameSinPath}'
        )
        # myLog.debug(f'-> Otros datos del rater cluster multibanda creado ({self.outputClusterAllDasoVarsFileNameSinPath}:')
        # myLog.debug(f'-> Datos del raster cluster multibanda creado ({self.outputClusterAllDasoVarsFileNameSinPath}:')
        # myLog.debug(f'{TB}-> Tipo de dato:              {type(dictArrayMultiBandaClusterDasoVars[1])} = {self.outputNpDatatypeAll}, dtype: {dictArrayMultiBandaClusterDasoVars[1].dtype}')
        # myLog.debug(f'{TB}-> Dimensiones de las bandas: {dictArrayMultiBandaClusterDasoVars[1].shape}')
        myLog.debug('{:=^80}'.format(''))
        # ======================================================================

        # ======================================================================
        # Array con unos en el circulo central (se usa como peso para los histogramas (como contra-mascara)
        arrayRoundCluster = np.ones((ladoCluster ** 2), dtype=np.uint8).reshape(ladoCluster, ladoCluster)
        nRowCenter = arrayRoundCluster.shape[0] / 2
        nColCenter = arrayRoundCluster.shape[1] / 2
        for nRowCell in range(arrayRoundCluster.shape[0]):
            for nColCell in range(arrayRoundCluster.shape[1]):
                if np.sqrt((((nRowCell + 0.5) - nRowCenter) ** 2) + (((nColCell + 0.5) - nColCenter) ** 2)) > ladoCluster / 2:
                    arrayRoundCluster[nRowCell, nColCell] = 0
        # ======================================================================

        # ======================================================================
        timeInicio = time.asctime(time.localtime(time.time()))
        contadorAvisosCluster = 0
        myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Recorriendo raster multibanda (nBandas: {self.nBandasRasterOutput}; ladoCluster: {ladoCluster})')
        myLog.info(f'{TB}para calcular clusterVars, tipoDeMasa, tipoDeBosque y dos parametros de proximidad.')
        myLog.info(f'{TB}{timeInicio}')
        print('numbaOk:', numbaOk)

        tiempo0 = time.time()

        if numbaOk:
            (
                recorrerRasterOk,
                contadorAvisosCluster,
                arrayBandaTipoBosc,
                arrayBandaTipoMasa,
                arrayDistanciaEuclideaMedia,
                arrayDistanciaEuclideaRazon,
                arrayPctjPorcentajeDeProximidad,
                arrayDistanciaScipy,
                self.maxDistanciaScipySuma,
            ) = clidtwinb.recorrerGeneraRasterClusterNb(
                arrayBandaXinputMonoPixelAll,
                arrayRoundCluster,
                dictArrayMultiBandaClusterDasoVars,
                arrayDistanciaScipy,
                arrayBandaTipoBosc,
                arrayBandaTipoMasa,
                arrayDistanciaEuclideaMedia,
                arrayDistanciaEuclideaRazon,
                arrayPctjPorcentajeDeProximidad,
                contadorAvisosCluster,
                self.nBandasRasterOutput,
                self.noDataDasoVarAll,
                self.LOCLradioClusterPix,
                self.outputNpDatatypeAll,
                # self.LOCLlistLstDasoVars,
                # self.LOCLlistaDasoVarsFileTypes,  # self.LOCLlistLstDasoVars[:, 0]
                # self.LOCLlistaDasoVarsNickNames,  # self.LOCLlistLstDasoVars[:, 1]
                # self.LOCLlistaDasoVarsRangoLinf,  # self.LOCLlistLstDasoVars[:, 2]
                # self.LOCLlistaDasoVarsRangoLsup,  # self.LOCLlistLstDasoVars[:, 3]
                # self.LOCLlistaDasoVarsNumClases,  # self.LOCLlistLstDasoVars[:, 4]
                # self.LOCLlistaDasoVarsMovilidad,  # self.LOCLlistLstDasoVars[:, 5]
                np.array(self.LOCLlistaDasoVarsPonderado, dtype=np.int8),  # self.LOCLlistLstDasoVars[:, 6]
                self.nInputVars,
                self.myNBins,
                self.myRange,
                self.listHistProb01,
                self.codeTipoBosquePatronMasFrecuente1,
                self.pctjTipoBosquePatronMasFrecuente1,
                self.codeTipoBosquePatronMasFrecuente2,
                self.pctjTipoBosquePatronMasFrecuente2,
                self.maxDistanciaScipyMono,
                self.GLBLnoDataDistancia,
                self.maxDistanciaScipySuma,
                self.listaCeldasConDasoVarsOkPatron,
                self.GLBLumbralMatriDist,
                nScipyMethods,
                self.LOCLverbose,
            )
            if not recorrerRasterOk:
                sys.exit(0)
        else:
            (
                recorrerRasterOk,
                contadorAvisosCluster,
                arrayBandaTipoBosc,
                arrayBandaTipoMasa,
                arrayDistanciaEuclideaMedia,
                arrayDistanciaEuclideaRazon,
                arrayPctjPorcentajeDeProximidad,
                arrayDistanciaScipy,
                self.maxDistanciaScipySuma,
                self,
            ) = clidtwinp.recorrerGeneraRasterClusterPy(
                arrayBandaXinputMonoPixelAll,
                arrayRoundCluster,
                dictArrayMultiBandaClusterDasoVars,
                arrayDistanciaScipy,
                arrayBandaTipoBosc,
                arrayBandaTipoMasa,
                arrayDistanciaEuclideaMedia,
                arrayDistanciaEuclideaRazon,
                arrayPctjPorcentajeDeProximidad,
                contadorAvisosCluster,
                SCIPY_METHODS,
                tiempo0,
                self,
            )

        tiempo1 = time.time()
        myLog.debug(f'{TB}{TV}-> Tiempo para recorrer todos los lotes: {(tiempo1 - tiempo0):0.0f} segundos ({round((tiempo1 - tiempo0)/60, 1)} minutos)')

        myLog.debug('')
        # PENDIENTE: ofrecer la conversión de asc de 10x10 en tif de 20x20
        # y verificar que al escribir en una fila del tif no se carga lo que hay previamente en esa fila

        # El noDataTiffProvi es el propio self.GLBLnoDataTipoDMasa; no necesito esto:
        # arrayBandaTipoMasa[arrayBandaTipoMasa == self.GLBLnoDataTiffFiles] = self.GLBLnoDataTipoDMasa
        # myLog.debug('\nAsigno valores de matchTipoMasa al raster')
        # nFilas = outputBandaTipoMasa.shape[0]
        # nColumnas = outputBandaTipoMasa.shape[1]
        # myLog.debug(f'outputBandaTipoMasa: {outputBandaTipoMasa}')
        # myLog.debug(dir(outputBandaTipoMasa))
        # myLog.debug(f'arrayBandaTipoMasa: {arrayBandaTipoMasa}')
        # myLog.debug(dir(arrayBandaTipoMasa))
        # myLog.debug(f'arrayBandaTipoMasa.shape: {arrayBandaTipoMasa.shape}')

        outputBandaTipoBosc = clidtwinx.guardarArrayEnBandaDataset(
            arrayBandaTipoBosc, outputBandaTipoBosc
        )

        outputBandaTipoMasa = clidtwinx.guardarArrayEnBandaDataset(
            arrayBandaTipoMasa, outputBandaTipoMasa
        )

        outputBandaProximidadInterEspecies1a = clidtwinx.guardarArrayEnBandaDataset(
            arrayBandaTipoBosc, outputBandaProximidadInterEspecies1a
        )
        outputBandaProximidadInterEspecies1b = clidtwinx.guardarArrayEnBandaDataset(
            arrayBandaTipoBosc, outputBandaProximidadInterEspecies1b
        )
        outputBandaProximidadInterEspecies2 = clidtwinx.guardarArrayEnBandaDataset(
            arrayBandaTipoBosc, outputBandaProximidadInterEspecies2
        )
        outputBandaDistanciaEuclideaMedia = clidtwinx.guardarArrayEnBandaDataset(
            arrayDistanciaEuclideaMedia, outputBandaDistanciaEuclideaMedia
        )
        outputBandaDistanciaEuclideaRazon = clidtwinx.guardarArrayEnBandaDataset(
            arrayDistanciaEuclideaRazon, outputBandaDistanciaEuclideaRazon
        )
        outputBandaPorcentajeDeProximidad = clidtwinx.guardarArrayEnBandaDataset(
            arrayPctjPorcentajeDeProximidad, outputBandaPorcentajeDeProximidad
        )
        for outputNBand in range(1, self.nBandasPrevistasOutput + 1):
            dictDtSetMultiBandaClusterDasoVarsNBand = clidtwinx.guardarArrayEnBandaDataset(
                dictArrayMultiBandaClusterDasoVars[outputNBand],
                dictDtSetMultiBandaClusterDasoVars[outputNBand]
            )
            dictDtSetMultiBandaClusterDasoVars[outputNBand] = dictDtSetMultiBandaClusterDasoVarsNBand

        # Distancas Scipy: sustituyo el valor noData por el maximo valor de distancia acumulada
        myLog.debug(f'clidtwins-> Convirtiendo noData ({self.GLBLnoDataDistancia}) al valor de la mistancia maxima ({int(self.maxDistanciaScipySuma) + 1}).')
        arrayDistanciaScipy[arrayDistanciaScipy == self.GLBLnoDataDistancia] = int(self.maxDistanciaScipySuma) + 1
        for nInputVar in range(self.nInputVars):
            # for numMethod, (methodName, method) in enumerate(SCIPY_METHODS):
            outputBandaDistanciaScipyMethod1[nInputVar] = clidtwinx.guardarArrayEnBandaDataset(
                arrayDistanciaScipy[nInputVar, 0], outputBandaDistanciaScipyMethod1[nInputVar]
            )
            if nScipyMethods >= 2:
                outputBandaDistanciaScipyMethod2[nInputVar] = clidtwinx.guardarArrayEnBandaDataset(
                    arrayDistanciaScipy[nInputVar, 1], outputBandaDistanciaScipyMethod2[nInputVar]
                )
            if nScipyMethods >= 3:
                outputBandaDistanciaScipyMethod3[nInputVar] = clidtwinx.guardarArrayEnBandaDataset(
                    arrayDistanciaScipy[nInputVar, 2], outputBandaDistanciaScipyMethod3[nInputVar]
                )

        # Banda final con la media ponderada de distancias teniendo en cuenta todas las dasoVars
        try:
            outputBandaDistanciaScipyMethod1[self.nInputVars] = clidtwinx.guardarArrayEnBandaDataset(
                arrayDistanciaScipy[-1, 0], outputBandaDistanciaScipyMethod1[self.nInputVars]
            )
            if nScipyMethods >= 2:
                outputBandaDistanciaScipyMethod2[self.nInputVars] = clidtwinx.guardarArrayEnBandaDataset(
                    arrayDistanciaScipy[-1, 1], outputBandaDistanciaScipyMethod2[self.nInputVars]
                )
            if nScipyMethods >= 3:
                outputBandaDistanciaScipyMethod3[self.nInputVars] = clidtwinx.guardarArrayEnBandaDataset(
                    arrayDistanciaScipy[-1, 2], outputBandaDistanciaScipyMethod3[self.nInputVars]
                )
        except:
            myLog.error(f'clidtwins-> ATENCION: revisar dimensiones {type(arrayDistanciaScipy)} {type(outputBandaDistanciaScipyMethod3)}, {type(outputBandaDistanciaScipyMethod3[self.nInputVars])}')
            myLog.error(f'{TB}arrayDistanciaScipy.shape: {arrayDistanciaScipy.shape}')
            myLog.error(f'{TB}outputBandaDistanciaScipyMethod3[self.nInputVars].shape: {outputBandaDistanciaScipyMethod3[self.nInputVars].shape}')

        return True
        # return (
        #     self.LOCLoutPathNameRuta,
        #     self.outputClusterAllDasoVarsFileNameSinPath,
        #     self.outputClusterTipoBoscProFileNameSinPath,
        #     self.outputClusterTipoMasaParFileNameSinPath,
        #     self.outputClusterDistanciaEuFileNameSinPath,
        #     self.outputClusterFactorProxiFileNameSinPath,
        # )

    # ==========================================================================
    def asignarTipoDeMasaConDistanciaMinima(
            self,
            LCL_listaTM=None,
            LCL_distMaxScipyAdm=None
        ):
        if LCL_listaTM is None:
            self.LOCLlistaTM = [None]
        else:
            self.LOCLlistaTM = LCL_listaTM
        if LCL_distMaxScipyAdm is None:
            self.LOCLdistMaxScipyAdm = GLO.GLBLdistMaxScipyAdmPorDefecto
        else:
            self.LOCLdistMaxScipyAdm = LCL_distMaxScipyAdm
            LCL_distMaxScipyAdm=None

        outputClusterTipoBoscProFileNameSinPath = {}
        outputClusterDistScipyM1FileNameSinPath = {}
        outputClusterDistScipyM2FileNameSinPath = {}
        outputClusterDistScipyM3FileNameSinPath = {}
        arrayClusterTipoBoscPro = {}
        arrayClusterDistScipyM1 = {}
        arrayClusterDistScipyM2 = {}
        arrayClusterDistScipyM3 = {}
        disponibleClusterDistScipyM1 = False
        disponibleClusterDistScipyM2 = False
        disponibleClusterDistScipyM3 = False
        for LCL_tipoDeMasaSelec in self.LOCLlistaTM:
            if LCL_tipoDeMasaSelec is None:
                idTipoDeMasaSelec = ''
            else:
                idTipoDeMasaSelec = f'_TM{LCL_tipoDeMasaSelec}'

            (
                _,
                _,
                _,
                _,
                _,
                outputClusterTipoBoscProFileNameSinPath[LCL_tipoDeMasaSelec],
                outputClusterDistScipyM1FileNameSinPath[LCL_tipoDeMasaSelec],
                outputClusterDistScipyM2FileNameSinPath[LCL_tipoDeMasaSelec],
                outputClusterDistScipyM3FileNameSinPath[LCL_tipoDeMasaSelec],
            ) = getFileNamesDistScipy(self.idInputDir, idTipoDeMasaSelec, self.driverExtension)

            myLog.info(f'clidtwins-> Abriendo raster con factor de proximidad al tipo de bosque de referencia (0-10): {outputClusterTipoBoscProFileNameSinPath[LCL_tipoDeMasaSelec]}')
            outputClusterTipoBoscProFileNameConPath = os.path.join(self.LOCLoutPathNameRuta, outputClusterTipoBoscProFileNameSinPath[LCL_tipoDeMasaSelec])
            if os.path.exists(outputClusterTipoBoscProFileNameConPath):
                try:
                    rasterDatasetClusterTipoBoscPro = gdal.Open(outputClusterTipoBoscProFileNameConPath, gdalconst.GA_ReadOnly)
                    # nBandasRasterOutput = rasterDatasetClusterTipoBoscPro.RasterCount
                    lastBandClusterTipoBoscPro = rasterDatasetClusterTipoBoscPro.GetRasterBand(1)
                    arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec] = lastBandClusterTipoBoscPro.ReadAsArray().astype(self.outputNpDatatypeAll)
                    disponibleClusterTipoBoscPro = True
                    myLog.debug(f'{TB}-> Raster M1 - TM {LCL_tipoDeMasaSelec} leido ok')
                except:
                    myLog.error(f'{TB}-> ATENCION: error al leer {outputClusterTipoBoscProFileNameConPath}')
                    myLog.error(f'{TB}-> Revisar si esta corrupto o esta bloqueado.')
                    # sys.exit(0)
            else:
                myLog.warning(f'{TB}-> No se encuentra el raster con el tipo de bosque - TM{LCL_tipoDeMasaSelec}: {outputClusterTipoBoscProFileNameConPath}')

            myLog.info(f'clidtwins-> Abriendo raster con distancias scipy method M1: {outputClusterDistScipyM1FileNameSinPath[LCL_tipoDeMasaSelec]}')
            outputClusterDistScipyM1FileNameConPath = os.path.join(self.LOCLoutPathNameRuta, outputClusterDistScipyM1FileNameSinPath[LCL_tipoDeMasaSelec])
            if os.path.exists(outputClusterDistScipyM1FileNameConPath):
                try:
                    rasterDatasetClusterDistScipyM1 = gdal.Open(outputClusterDistScipyM1FileNameConPath, gdalconst.GA_ReadOnly)
                    nBandasRasterOutput = rasterDatasetClusterDistScipyM1.RasterCount
                    lastBandClusterDistScipyM1 = rasterDatasetClusterDistScipyM1.GetRasterBand(nBandasRasterOutput)
                    arrayClusterDistScipyM1[LCL_tipoDeMasaSelec] = lastBandClusterDistScipyM1.ReadAsArray().astype(self.outputNpDatatypeAll)
                    disponibleClusterDistScipyM1 = True
                    myLog.debug(f'{TB}-> Raster M1 - TM {LCL_tipoDeMasaSelec} leido ok')
                except:
                    myLog.error(f'{TB}-> ATENCION: error al leer {outputClusterDistScipyM1FileNameConPath}')
                    myLog.error(f'{TB}-> Revisar si esta corrupto o esta bloqueado.')
                    # sys.exit(0)
            else:
                myLog.warning(f'{TB}-> No se encuentra el raster con las distancias scipy method M1 - TM{LCL_tipoDeMasaSelec}')

            if len(SCIPY_METHODS) >= 2:
                myLog.info(f'clidtwins-> Abriendo raster con distancias scipy method M2: {outputClusterDistScipyM2FileNameSinPath[LCL_tipoDeMasaSelec]}')
                outputClusterDistScipyM2FileNameConPath = os.path.join(self.LOCLoutPathNameRuta, outputClusterDistScipyM2FileNameSinPath[LCL_tipoDeMasaSelec])
                if os.path.exists(outputClusterDistScipyM2FileNameConPath):
                    try:
                        rasterDatasetClusterDistScipyM2 = gdal.Open(outputClusterDistScipyM2FileNameConPath, gdalconst.GA_ReadOnly)
                        nBandasRasterOutput = rasterDatasetClusterDistScipyM2.RasterCount
                        lastBandClusterDistScipyM2 = rasterDatasetClusterDistScipyM2.GetRasterBand(nBandasRasterOutput)
                        arrayClusterDistScipyM2[LCL_tipoDeMasaSelec] = lastBandClusterDistScipyM2.ReadAsArray().astype(self.outputNpDatatypeAll)
                        disponibleClusterDistScipyM2 = True
                        myLog.debug(f'{TB}-> Raster M2 - TM {LCL_tipoDeMasaSelec} leido ok')
                    except:
                        myLog.error(f'{TB}-> ATENCION: error al leer {outputClusterDistScipyM2FileNameConPath}')
                        myLog.error(f'{TB}-> Revisar si esta corrupto o esta bloqueado.')
                        # sys.exit(0)
                else:
                    myLog.warning(f'{TB}-> No se encuentra el raster con las distancias scipy method M2 - TM{LCL_tipoDeMasaSelec}')

            if len(SCIPY_METHODS) >= 3:
                myLog.info(f'clidtwins-> Abriendo raster con distancias scipy method M3: {outputClusterDistScipyM3FileNameSinPath[LCL_tipoDeMasaSelec]}')
                outputClusterDistScipyM3FileNameConPath = os.path.join(self.LOCLoutPathNameRuta, outputClusterDistScipyM3FileNameSinPath[LCL_tipoDeMasaSelec])
                if os.path.exists(outputClusterDistScipyM3FileNameConPath):
                    try:
                        rasterDatasetClusterDistScipyM3 = gdal.Open(outputClusterDistScipyM3FileNameConPath, gdalconst.GA_ReadOnly)
                        nBandasRasterOutput = rasterDatasetClusterDistScipyM3.RasterCount
                        lastBandClusterDistScipyM3 = rasterDatasetClusterDistScipyM3.GetRasterBand(nBandasRasterOutput)
                        arrayClusterDistScipyM3[LCL_tipoDeMasaSelec] = lastBandClusterDistScipyM3.ReadAsArray().astype(self.outputNpDatatypeAll)
                        disponibleClusterDistScipyM3 = True
                        myLog.debug(f'{TB}-> Raster M3 - TM {LCL_tipoDeMasaSelec} leido ok')
                    except:
                        myLog.error(f'{TB}-> ATENCION: error al leer {outputClusterDistScipyM3FileNameConPath}')
                        myLog.error(f'{TB}-> Revisar si esta corrupto o esta bloqueado.')
                        # sys.exit(0)
                else:
                    myLog.warning(f'{TB}-> No se encuentra el raster con las distancias scipy method M3 - TM{LCL_tipoDeMasaSelec}')

            if disponibleClusterTipoBoscPro and LCL_tipoDeMasaSelec in arrayClusterTipoBoscPro.keys():
                nDistRows, nDistCols = arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec].shape
                if (
                    (
                        disponibleClusterDistScipyM1 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM1.keys() and (
                            nDistRows != arrayClusterDistScipyM1[LCL_tipoDeMasaSelec].shape[0]
                            or nDistCols != arrayClusterDistScipyM1[LCL_tipoDeMasaSelec].shape[1]
                        )
                    ) or (
                    (
                        disponibleClusterDistScipyM2 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM2.keys() and (
                            nDistRows != arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape[0]
                            or nDistCols != arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape[1]
                        )
                    )
                    ) or (
                        disponibleClusterDistScipyM3 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM3.keys() and (
                            nDistRows != arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[0]
                            or nDistCols != arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[1]
                        )
                    )
                ):
                    myLog.error(f'clidtwins-> ATENCION: revisar dimensiones de los rasters con distancias scipy')
                    if LCL_tipoDeMasaSelec in arrayClusterDistScipyM1.keys():
                        myLog.error(f'{TB}M1 rows: {nDistRows} != {arrayClusterDistScipyM1[LCL_tipoDeMasaSelec].shape[0]}')
                        myLog.error(f'{TB}M1 cols: {nDistCols} != {arrayClusterDistScipyM1[LCL_tipoDeMasaSelec].shape[1]}')
                    if LCL_tipoDeMasaSelec in arrayClusterDistScipyM2.keys():
                        myLog.error(f'{TB}M2 rows: {nDistRows} != {arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape[0]}')
                        myLog.error(f'{TB}M2 cols: {nDistCols} != {arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape[1]}')
                    if LCL_tipoDeMasaSelec in arrayClusterDistScipyM3.keys():
                        myLog.error(f'{TB}M3 rows: {nDistRows} != {arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[0]}')
                        myLog.error(f'{TB}M3 cols: {nDistCols} != {arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[1]}')
                    sys.exit(0)
            elif disponibleClusterDistScipyM1 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM1.keys():
                nDistRows, nDistCols = arrayClusterDistScipyM1[LCL_tipoDeMasaSelec].shape
                if (
                    (
                        disponibleClusterDistScipyM2 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM2.keys() and (
                            nDistRows != arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape[0]
                            or nDistCols != arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape[1]
                        )
                    ) or (
                        disponibleClusterDistScipyM3 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM3.keys() and (
                            nDistRows != arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[0]
                            or nDistCols != arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[1]
                        )
                    )
                ):
                    myLog.error(f'clidtwins-> ATENCION: revisar dimensiones de los rasters con distancias scipy')
                    if LCL_tipoDeMasaSelec in arrayClusterDistScipyM2.keys():
                        myLog.error(f'{TB}M2 rows: {nDistRows} != {arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape[0]}')
                        myLog.error(f'{TB}M2 cols: {nDistCols} != {arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape[1]}')
                    if LCL_tipoDeMasaSelec in arrayClusterDistScipyM3.keys():
                        myLog.error(f'{TB}M3 rows: {nDistRows} != {arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[0]}')
                        myLog.error(f'{TB}M3 cols: {nDistCols} != {arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[1]}')
                    sys.exit(0)
            elif disponibleClusterDistScipyM2 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM2.keys():
                nDistRows, nDistCols = arrayClusterDistScipyM2[LCL_tipoDeMasaSelec].shape
                if (
                    disponibleClusterDistScipyM3 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM3.keys() and (
                        nDistRows != arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[0]
                        or nDistCols != arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[1]
                    )
                ):
                    myLog.error(f'clidtwins-> ATENCION: revisar dimensiones de los rasters con distancias scipy')
                    myLog.error(f'{TB}M3_ rows: {nDistRows} != {arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[0]}')
                    myLog.error(f'{TB}M3_ cols: {nDistCols} != {arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape[1]}')
                    sys.exit(0)
            elif disponibleClusterDistScipyM3 and LCL_tipoDeMasaSelec in arrayClusterDistScipyM3.keys():
                nDistRows, nDistCols = arrayClusterDistScipyM3[LCL_tipoDeMasaSelec].shape
            else:
                myLog.error(f'clidtwins-> ATENCION: no hay rasters disponibles con distancias scipy para el TM{LCL_tipoDeMasaSelec}')
                continue

        # myLog.info(f'clidtwins-> Dimensiones de los raster origen y destino compatibles '
        #            f'scipyM1: {disponibleClusterDistScipyM1}; '
        #            f'scipyM2: {disponibleClusterDistScipyM2}; '
        #            f'scipyM3: {disponibleClusterDistScipyM3}')
        # myLog.info(f'{TB}nDistRows: {nDistRows} = {self.nCeldasY_Destino}')
        # myLog.info(f'{TB}nDistCols: {nDistCols} = {self.nCeldasX_Destino}')

        # Se genera un raster con el Tipo de Masa de minima distancia en cada pixel, para cada metodo Scipy
        self.outputTiposDeMasaDistanciaMinimaTipoBoscAnyFileNameSinPath = '{}_{}.{}'.format('clusterTiposDeMasaDistMinimaTipoBosqueCualquiera', self.idInputDir, self.driverExtension)
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Creando fichero para el layer tipoMasa con distancia scipy minima sin comparar tipo de bosque {self.outputTiposDeMasaDistanciaMinimaTipoBoscAnyFileNameSinPath}')
        nScipyMethods = len(SCIPY_METHODS)
        datasetTipoMasaScipyTipoBoscAny, bandaTipoMasaScipyTipoBoscAnyM1 = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputTiposDeMasaDistanciaMinimaTipoBoscAnyFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nScipyMethods,
            self.outputGdalDatatypeTipoMasa,
            self.outputNpDatatypeTipoMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTipoDMasa,
            generarMetaPixeles=True,
        )
        if nScipyMethods >= 2 and disponibleClusterDistScipyM2:
            bandaTipoMasaScipyTipoBoscAnyM2 = datasetTipoMasaScipyTipoBoscAny.GetRasterBand(2)
        if nScipyMethods >= 3 and disponibleClusterDistScipyM3:
            bandaTipoMasaScipyTipoBoscAnyM3 = datasetTipoMasaScipyTipoBoscAny.GetRasterBand(3)

        # Se genera un raster adicional con el Tipo de Masa de minima distancia 
        # que tenga especie compatible con patron en cada pixel, para cada metodo Scipy
        self.outputTiposDeMasaDistanciaMinimaTipoBoscProFileNameSinPath = '{}_{}.{}'.format('clusterTiposDeMasaDistMinimaTipoBosqueCompatible', self.idInputDir, self.driverExtension)
        # myLog.info('\n{:_^80}'.format(''))
        myLog.info(f'clidtwins-> Creando fichero para el layer tipoMasa con distancia scipy minima con tipo de bosque compatible {self.outputTiposDeMasaDistanciaMinimaTipoBoscProFileNameSinPath}')
        nScipyMethods = len(SCIPY_METHODS)
        datasetTipoMasaScipyTipoBoscPro, bandaTipoMasaScipyTipoBoscProM1 = clidraster.CrearOutputRaster(
            self.LOCLoutPathNameRuta,
            self.outputTiposDeMasaDistanciaMinimaTipoBoscProFileNameSinPath,
            self.nMinX_tif,
            self.nMaxY_tif,
            self.nCeldasX_Destino,
            self.nCeldasY_Destino,
            self.metrosPixelX_Destino,
            self.metrosPixelY_Destino,
            self.LOCLoutRasterDriver,
            self.outputOptions,
            nScipyMethods,
            self.outputGdalDatatypeTipoMasa,
            self.outputNpDatatypeTipoMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTipoDMasa,
            self.GLBLnoDataTipoDMasa,
            generarMetaPixeles=True,
        )
        if nScipyMethods >= 2 and disponibleClusterDistScipyM2:
            bandaTipoMasaScipyTipoBoscProM2 = datasetTipoMasaScipyTipoBoscPro.GetRasterBand(2)
        if nScipyMethods >= 3 and disponibleClusterDistScipyM3:
            bandaTipoMasaScipyTipoBoscProM3 = datasetTipoMasaScipyTipoBoscPro.GetRasterBand(3)

        if disponibleClusterDistScipyM1:
            myLog.info(f'clidtwins-> Calculando para cada pixel ({nDistRows} x {nDistCols}) el tipoMasa con distancia minima scipy M1')
            arrayTipoMasaScipyTipoBoscAnyM1 = bandaTipoMasaScipyTipoBoscAnyM1.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
            arrayTipoMasaScipyTipoBoscProM1 = bandaTipoMasaScipyTipoBoscProM1.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
            for nDistRow in range(nDistRows):
                for nDistCol in range(nDistCols):
                    distanciaMinimaScipyM1TipoBoscAny = 99999
                    distanciaMinimaScipyM1TipoBoscPro = 99999
                    for LCL_tipoDeMasaSelec in self.LOCLlistaTM:
                        if LCL_tipoDeMasaSelec in arrayClusterDistScipyM1.keys():
                            distanciaMinimaScipyM1TipoBoscAny = min(
                                distanciaMinimaScipyM1TipoBoscAny,
                                arrayClusterDistScipyM1[LCL_tipoDeMasaSelec][nDistRow, nDistCol],
                            )
                            if (
                                arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] >= TRNS_tipoBoscCompatible
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] != self.GLBLnoDataTipoDMasa
                            ):
                                distanciaMinimaScipyM1TipoBoscPro = min(
                                    distanciaMinimaScipyM1TipoBoscPro,
                                    arrayClusterDistScipyM1[LCL_tipoDeMasaSelec][nDistRow, nDistCol],
                                )
                    for LCL_tipoDeMasaSelec in self.LOCLlistaTM:
                        if LCL_tipoDeMasaSelec in arrayClusterDistScipyM1.keys(): 
                            if (
                                distanciaMinimaScipyM1TipoBoscAny != 99999
                                and distanciaMinimaScipyM1TipoBoscAny < self.LOCLdistMaxScipyAdm
                                and arrayClusterDistScipyM1[LCL_tipoDeMasaSelec][nDistRow, nDistCol] == distanciaMinimaScipyM1TipoBoscAny
                            ):
                                arrayTipoMasaScipyTipoBoscAnyM1[nDistRow, nDistCol] = LCL_tipoDeMasaSelec
                            if (
                                distanciaMinimaScipyM1TipoBoscPro != 99999
                                and distanciaMinimaScipyM1TipoBoscPro < self.LOCLdistMaxScipyAdm
                                and arrayClusterDistScipyM1[LCL_tipoDeMasaSelec][nDistRow, nDistCol] == distanciaMinimaScipyM1TipoBoscPro
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] >= TRNS_tipoBoscCompatible
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] != self.GLBLnoDataTipoDMasa
                            ):
                                arrayTipoMasaScipyTipoBoscProM1[nDistRow, nDistCol] = LCL_tipoDeMasaSelec

        if disponibleClusterDistScipyM2:
            myLog.info(f'clidtwins-> Calculando para cada pixel ({nDistRows} x {nDistCols}) el tipoMasa con distancia minima scipy M2')
            arrayTipoMasaScipyTipoBoscAnyM2 = bandaTipoMasaScipyTipoBoscAnyM2.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
            arrayTipoMasaScipyTipoBoscProM2 = bandaTipoMasaScipyTipoBoscProM2.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
            for nDistRow in range(nDistRows):
                for nDistCol in range(nDistCols):
                    distanciaMinimaScipyM2TipoBoscAny = 99999
                    distanciaMinimaScipyM2TipoBoscPro = 99999
                    for LCL_tipoDeMasaSelec in self.LOCLlistaTM:
                        if LCL_tipoDeMasaSelec in arrayClusterDistScipyM2.keys(): 
                            distanciaMinimaScipyM2TipoBoscAny = min(
                                distanciaMinimaScipyM2TipoBoscAny,
                                arrayClusterDistScipyM2[LCL_tipoDeMasaSelec][nDistRow, nDistCol],
                            )
                            if (
                                arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] >= TRNS_tipoBoscCompatible
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] != self.GLBLnoDataTipoDMasa
                            ):
                                distanciaMinimaScipyM2TipoBoscPro = min(
                                    distanciaMinimaScipyM2TipoBoscPro,
                                    arrayClusterDistScipyM2[LCL_tipoDeMasaSelec][nDistRow, nDistCol],
                                )
                    for LCL_tipoDeMasaSelec in self.LOCLlistaTM:
                        if LCL_tipoDeMasaSelec in arrayClusterDistScipyM2.keys(): 
                            if (
                                distanciaMinimaScipyM2TipoBoscAny != 99999
                                and distanciaMinimaScipyM2TipoBoscAny < self.LOCLdistMaxScipyAdm
                                and arrayClusterDistScipyM2[LCL_tipoDeMasaSelec][nDistRow, nDistCol] == distanciaMinimaScipyM2TipoBoscAny
                            ):
                                arrayTipoMasaScipyTipoBoscAnyM2[nDistRow, nDistCol] = LCL_tipoDeMasaSelec
                            if (
                                distanciaMinimaScipyM2TipoBoscPro != 99999
                                and distanciaMinimaScipyM2TipoBoscPro < self.LOCLdistMaxScipyAdm
                                and arrayClusterDistScipyM2[LCL_tipoDeMasaSelec][nDistRow, nDistCol] == distanciaMinimaScipyM2TipoBoscPro
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] >= TRNS_tipoBoscCompatible
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] != self.GLBLnoDataTipoDMasa
                            ):
                                arrayTipoMasaScipyTipoBoscProM2[nDistRow, nDistCol] = LCL_tipoDeMasaSelec

        if disponibleClusterDistScipyM3:
            myLog.info(f'clidtwins-> Calculando para cada pixel ({nDistRows} x {nDistCols}) el tipoMasa con distancia minima scipy M3')
            arrayTipoMasaScipyTipoBoscAnyM3 = bandaTipoMasaScipyTipoBoscAnyM3.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
            arrayTipoMasaScipyTipoBoscProM3 = bandaTipoMasaScipyTipoBoscProM3.ReadAsArray().astype(self.outputNpDatatypeTipoMasa)
            for nDistRow in range(nDistRows):
                for nDistCol in range(nDistCols):
                    distanciaMinimaScipyM3TipoBoscAny = 99999
                    distanciaMinimaScipyM3TipoBoscPro = 99999
                    for LCL_tipoDeMasaSelec in self.LOCLlistaTM:
                        if LCL_tipoDeMasaSelec in arrayClusterDistScipyM3.keys(): 
                            distanciaMinimaScipyM3TipoBoscAny = min(
                                distanciaMinimaScipyM3TipoBoscAny,
                                arrayClusterDistScipyM3[LCL_tipoDeMasaSelec][nDistRow, nDistCol],
                            )
                            if (
                                arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] >= TRNS_tipoBoscCompatible
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] != self.GLBLnoDataTipoDMasa
                            ):
                                distanciaMinimaScipyM3TipoBoscPro = min(
                                    distanciaMinimaScipyM3TipoBoscPro,
                                    arrayClusterDistScipyM3[LCL_tipoDeMasaSelec][nDistRow, nDistCol],
                                )
                    for LCL_tipoDeMasaSelec in self.LOCLlistaTM:
                        if LCL_tipoDeMasaSelec in arrayClusterDistScipyM3.keys(): 
                            if (
                                distanciaMinimaScipyM3TipoBoscAny != 99999
                                and distanciaMinimaScipyM3TipoBoscAny < self.LOCLdistMaxScipyAdm
                                and arrayClusterDistScipyM3[LCL_tipoDeMasaSelec][nDistRow, nDistCol] == distanciaMinimaScipyM3TipoBoscAny
                            ):
                                arrayTipoMasaScipyTipoBoscAnyM3[nDistRow, nDistCol] = LCL_tipoDeMasaSelec
                            if (
                                distanciaMinimaScipyM3TipoBoscPro != 99999
                                and distanciaMinimaScipyM3TipoBoscPro < self.LOCLdistMaxScipyAdm
                                and arrayClusterDistScipyM3[LCL_tipoDeMasaSelec][nDistRow, nDistCol] == distanciaMinimaScipyM3TipoBoscPro
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] >= TRNS_tipoBoscCompatible
                                and arrayClusterTipoBoscPro[LCL_tipoDeMasaSelec][nDistRow, nDistCol] != self.GLBLnoDataTipoDMasa
                            ):
                                arrayTipoMasaScipyTipoBoscProM3[nDistRow, nDistCol] = LCL_tipoDeMasaSelec

        if disponibleClusterDistScipyM1:
            myLog.info(f'clidtwins-> Guardando tipoMasa con distancia minima scipy M1')
            bandaTipoMasaScipyTipoBoscAnyM1 = clidtwinx.guardarArrayEnBandaDataset(
                arrayTipoMasaScipyTipoBoscAnyM1, bandaTipoMasaScipyTipoBoscAnyM1
            )
            bandaTipoMasaScipyTipoBoscProM1 = clidtwinx.guardarArrayEnBandaDataset(
                arrayTipoMasaScipyTipoBoscProM1, bandaTipoMasaScipyTipoBoscProM1
            )

        if disponibleClusterDistScipyM2:
            myLog.info(f'clidtwins-> Guardando tipoMasa con distancia minima scipy M2')
            bandaTipoMasaScipyTipoBoscAnyM2 = clidtwinx.guardarArrayEnBandaDataset(
                arrayTipoMasaScipyTipoBoscAnyM2, bandaTipoMasaScipyTipoBoscAnyM2
            )
            myLog.info(f'clidtwins-> Guardando tipoMasa con distancia minima scipy M2')
            bandaTipoMasaScipyTipoBoscProM2 = clidtwinx.guardarArrayEnBandaDataset(
                arrayTipoMasaScipyTipoBoscProM2, bandaTipoMasaScipyTipoBoscProM2
            )
        if disponibleClusterDistScipyM3:
            myLog.info(f'clidtwins-> Guardando tipoMasa con distancia minima scipy M3')
            bandaTipoMasaScipyTipoBoscAnyM3 = clidtwinx.guardarArrayEnBandaDataset(
                arrayTipoMasaScipyTipoBoscAnyM3, bandaTipoMasaScipyTipoBoscAnyM3
            )
            myLog.info(f'clidtwins-> Guardando tipoMasa con distancia minima scipy M3')
            bandaTipoMasaScipyTipoBoscProM3 = clidtwinx.guardarArrayEnBandaDataset(
                arrayTipoMasaScipyTipoBoscProM3, bandaTipoMasaScipyTipoBoscProM3
            )


def getFileNamesDistScipy(idInputDir, idTipoDeMasaSelec, driverExtension):
    outputClusterAllDasoVarsFileNameSinPath = '{}_{}{}.{}'.format('clusterAllDasoVars', idInputDir, idTipoDeMasaSelec, driverExtension)
    outputClusterTipoMasaParFileNameSinPath = '{}_{}{}.{}'.format('clusterTipoMasaPar', idInputDir, idTipoDeMasaSelec, driverExtension)
    outputClusterDistanciaEuFileNameSinPath = '{}_{}{}.{}'.format('clusterDistanciaEu', idInputDir, idTipoDeMasaSelec, driverExtension)
    outputClusterDistEuRazonFileNameSinPath = '{}_{}{}.{}'.format('clusterDistEuRazon', idInputDir, idTipoDeMasaSelec, driverExtension)
    outputClusterFactorProxiFileNameSinPath = '{}_{}{}.{}'.format('clusterFactorProxi', idInputDir, idTipoDeMasaSelec, driverExtension)

    outputClusterTipoBoscProFileNameSinPath = '{}_{}{}.{}'.format('clusterTipoBoscPro', idInputDir, idTipoDeMasaSelec, driverExtension)
    outputClusterDistScipyM1FileNameSinPath = '{}_{}{}.{}'.format('clusterDistScipyM1', idInputDir, idTipoDeMasaSelec, driverExtension)
    outputClusterDistScipyM2FileNameSinPath = '{}_{}{}.{}'.format('clusterDistScipyM2', idInputDir, idTipoDeMasaSelec, driverExtension)
    outputClusterDistScipyM3FileNameSinPath = '{}_{}{}.{}'.format('clusterDistScipyM3', idInputDir, idTipoDeMasaSelec, driverExtension)
    return(
        outputClusterAllDasoVarsFileNameSinPath,
        outputClusterTipoMasaParFileNameSinPath,
        outputClusterDistanciaEuFileNameSinPath,
        outputClusterDistEuRazonFileNameSinPath,
        outputClusterFactorProxiFileNameSinPath,

        outputClusterTipoBoscProFileNameSinPath,
        outputClusterDistScipyM1FileNameSinPath,
        outputClusterDistScipyM2FileNameSinPath,
        outputClusterDistScipyM3FileNameSinPath,
    )

# ==============================================================================
if __name__ == '__main__':
    pass

