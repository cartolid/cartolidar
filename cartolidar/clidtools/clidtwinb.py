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
# from scipy.spatial import distance_matrix
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
    print('clidtwinb-> No se puede importar gdal "from osgeo", se intenta directamente ("import gdal").')
    gdalOk = False
if not gdalOk:
    try:
        import gdal, ogr, osr, gdalnumeric, gdalconst
        sys.stdout.write('           gdal importado ok con "import gdal".\n')
        gdalOk = True
    except:
        gdalOk = False
        print('clidtwinb-> Error importando gdal.')
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
            sys.stderr.write(f'clidtwinb-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).\n')
            sys.stderr.write(f'\t-> Se importa clidconfig desde clidtwcfg del directorio local {os.getcwd()}/clidtools.\n')
        from clidax import clidconfig
        from clidax import clidraster
        from clidtools.clidtwcfg import GLO


# GLO.GLBLcompilaConNumbaPorDefecto = False
'''
configuracion original que da error:
llvmlite==0.33.0+1.g022ab0f
numba==0.50.1
numpy==1.21.6
'''
try:
    if GLO.GLBLcompilaConNumbaPorDefecto:
        import numba as nb
        # print('clidtwinb-> numba ok')
        # print('numba version:', nb.__version__)
        # print('numpy version:', np.__version__)
        # Acualizo a numba=0.53.00 (no uso el 0.55.0 porque requiere python 3.10)
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
        print('clidtwinb-> numba NO usar')
        sys.exit()
except:
    print('clidtwinb-> numba error')
    sys.exit()

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
myLog.debug('clidtwinb-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================


# ==============================================================================
@nb.jit(nopython=True)
def recorrerGeneraRasterClusterNb(
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
        self_nBandasRasterOutput,
        self_noDataDasoVarAll,
        self_LOCLradioClusterPix,
        self_outputNpDatatypeAll,
        # self_LOCLlistLstDasoVars,
            # self_LOCLlistaDasoVarsFileTypes,
            # self_LOCLlistaDasoVarsNickNames,
            # self_LOCLlistaDasoVarsRangoLinf,
            # self_LOCLlistaDasoVarsRangoLsup,
            # self_LOCLlistaDasoVarsNumClases,
            # self_LOCLlistaDasoVarsMovilidad,
            self_LOCLlistaDasoVarsPonderado,
        self_nInputVars,
        self_myNBins,
        self_myRange,
        self_listHistProb01,
        self_codeTipoBosquePatronMasFrecuente1,
        self_pctjTipoBosquePatronMasFrecuente1,
        self_codeTipoBosquePatronMasFrecuente2,
        self_pctjTipoBosquePatronMasFrecuente2,
        self_maxDistanciaScipyMono,
        self_GLBLnoDataDistancia,
        self_maxDistanciaScipySuma,
        self_listaCeldasConDasoVarsOkPatron,
        self_GLBLumbralMatriDist,
        nScipyMethods,
        self_LOCLverbose=False,
    ):
    for nRowRaster in range(arrayBandaTipoMasa.shape[0]):
        if self_LOCLverbose:
            if nRowRaster % (arrayBandaTipoMasa.shape[0] / 10) == 0:
                if nRowRaster > 0:
                    print()
                    # tiempo1 = time.time()
                    # myLog.debug(f'{TB}{TV}-> Tiempo para recorrer lote (10 % de las filas del raster): {(tiempo1 - tiempo0):0.1f} segundos')
                    # tiempo0 = time.time()
                if arrayBandaTipoMasa.shape[0] <= 999:
                    print(TB, 'Recorriendo fila', nRowRaster, 'de', arrayBandaTipoMasa.shape[0])  # , end ='')
                elif arrayBandaTipoMasa.shape[0] <= 9999:
                    print(TB, 'Recorriendo fila', nRowRaster, 'de', arrayBandaTipoMasa.shape[0])  # , end ='')
                else:
                    print(TB, 'Recorriendo fila', nRowRaster, 'de', arrayBandaTipoMasa.shape[0])  # , end ='')
            else:
                # print('.', end ='')
                pass
        coordY = arrayBandaTipoMasa.shape[0] - nRowRaster
        for nColRaster in range(arrayBandaTipoMasa.shape[1]):
            coordX = nColRaster
            if TRNS_saltarPixelsSinTipoBosque:
                if arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1][nRowRaster, nColRaster] == self_noDataDasoVarAll:
                    continue

            # ==============================================================
            # if (
            #     nRowRaster % (int(arrayBandaTipoMasa.shape[0] / 5)) == 0
            #     and nColRaster % (int(arrayBandaTipoMasa.shape[1] / 5)) == 0
            # ):
            # if nRowRaster == 0 and nColRaster == 0:
            #     mostrarPixelClusterMatch = True
            # else:
            #     if (
            #         coordX == 0 or coordX == 35 or coordX == 59
            #     ) and (
            #         coordY == 0 or coordY == 85 or coordY == 95
            #     ):
            #         mostrarPixelClusterMatch = True
            #     else:
            #         mostrarPixelClusterMatch = False
            mostrarPixelClusterMatch = False
            # if coordX == 156 and coordY == 35:
            #     mostrarPixelClusterMatch = True
            # ==============================================================

            clusterRelleno = rellenarLocalClusterNb(
                arrayBandaXinputMonoPixelAll,
                nRowRaster,
                nColRaster,
                self_LOCLradioClusterPix,  # self_LOCLradioClusterPix=
                self_noDataDasoVarAll,  # self_noDataDasoVarAll=
                self_outputNpDatatypeAll,  # self_outputNpDatatypeAll=
                mostrarPixelClusterMatch,  # mostrarPixelClusterMatch=
                contadorAvisosCluster,  # contadorAvisosCluster=
                self_LOCLverbose=self_LOCLverbose,
                # localClusterArrayMultiBandaDasoVars,
                # localSubClusterArrayMultiBandaDasoVars,
                # arrayBandaXMaskCluster,
                # arrayBandaXMaskSubCluster,
            )
            localClusterOk = clusterRelleno[0]
            contadorAvisosCluster = clusterRelleno[1]
            if not localClusterOk:
                if contadorAvisosCluster == -1:
                    return (
                        False,
                        contadorAvisosCluster,
                        arrayBandaTipoBosc,
                        arrayBandaTipoMasa,
                        arrayDistanciaEuclideaMedia,
                        arrayDistanciaEuclideaRazon,
                        arrayPctjPorcentajeDeProximidad,
                        arrayDistanciaScipy,
                        self_maxDistanciaScipySuma,
                    )
                continue
            clusterCompleto = clusterRelleno[2]
            nCeldasConDasoVarsOk = clusterRelleno[3]
            localClusterArrayMultiBandaDasoVars = clusterRelleno[4]
            localSubClusterArrayMultiBandaDasoVars = clusterRelleno[5]
            arrayBandaXMaskCluster = clusterRelleno[6]
            arrayBandaXMaskSubCluster = clusterRelleno[7]

            listaCeldasConDasoVarsOkCluster = np.zeros(
                nCeldasConDasoVarsOk * self_nBandasRasterOutput, dtype=self_outputNpDatatypeAll
            ).reshape(nCeldasConDasoVarsOk, self_nBandasRasterOutput)
            listaCeldasConDasoVarsOkSubCluster = np.zeros(
                nCeldasConDasoVarsOk * self_nBandasRasterOutput, dtype=self_outputNpDatatypeAll
            ).reshape(nCeldasConDasoVarsOk, self_nBandasRasterOutput)

            # if not nCeldasConDasoVarsOk and self_LOCLverbose > 1:
            #     # Por aqui no pasa porque ya he interceptado este problema mas arriba
            #     myLog.warning(f'{TB}{TV}-> AVISO (c): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
            #     continue

            # ==============================================================
            nVariablesNoOk = 0
            tipoBosqueOk = 0
            # myLog.debug(f'clidtwinb-> {nRowRaster} // {nColRaster} Recorriendo bandas+++')
            sumaPoderaciones = 0
            for nBanda in range(1, self_nBandasRasterOutput + 1):
                nInputVar = nBanda - 1
                # sumaPoderaciones += self_LOCLlistLstDasoVars[nInputVar][6]
                sumaPoderaciones += self_LOCLlistaDasoVarsPonderado[nInputVar]
            if sumaPoderaciones == 0:
                # myLog.warning(f'clidtwinb-> ATENCION: las ponderaciones de las variables DasoLidar son todas nulas')
                print('clidtwinb-> ATENCION: las ponderaciones de las variables DasoLidar son todas nulas')
                for nBanda in range(1, self_nBandasRasterOutput + 1):
                    nInputVar = nBanda - 1
                    # myLog.warning(f'{TB}Banda: {nBanda} -> dasovar: {self_LOCLlistLstDasoVars[nInputVar]} (poderacion: {self_LOCLlistLstDasoVars[nInputVar][6]})')
                    print(TB, 'Banda:', nBanda, '-> nInputVar:', nInputVar, '(poderacion:', self_LOCLlistaDasoVarsPonderado[nInputVar], ')')
                # myLog.warning(f'{TB}-> Se asigna la misma ponderacion a todas las dasoVars.')
                print(TB, '-> Se asigna la misma ponderacion a todas las dasoVars.')
                sumaPoderaciones = 1
                hayPonderaciones = False
            else:
                hayPonderaciones = True
            for nBanda in range(1, self_nBandasRasterOutput + 1):
                nInputVar = nBanda - 1
                if hayPonderaciones:
                    # ponderacionDeLaVariable = self_LOCLlistLstDasoVars[nInputVar][6]
                    ponderacionDeLaVariable = self_LOCLlistaDasoVarsPonderado[nInputVar]
                else:
                    ponderacionDeLaVariable = 1 / (self_nBandasRasterOutput - 2)
                # Factor entre 0 y 1 que modifica el numero de clases que estan fuera de rango
                # al comparar el histograma de testeo con el de referencia (patron),
                # Tras establecer para cada clase un rango admisible de frecuencias
                # alrededdor de la frecuencia del histograma de referencia para esa clase.
                # El valor 1 suma todos los "fuera de rango"; el factor 0.5 los contabiliza mitad
                multiplicadorDeFueraDeRangoParaLaVariable = ponderacionDeLaVariable / 10
                # claveRef = str(nInputVar) + '_' + str(self_LOCLlistLstDasoVars[nInputVar][1]) + '_ref'
                if mostrarPixelClusterMatch and self_LOCLverbose > 1:
                    if nInputVar >= 0 and nInputVar < self_nInputVars:
                        # myLog.debug(f'{TB}-> Banda {nBanda} -> (cluster) Chequeando rangos admisibles para: {claveRef} (pondera: {ponderacionDeLaVariable})')
                        print(TB, '-> Banda', nBanda, '-> (cluster) Chequeando rangos admisibles para nInputVar:', nInputVar, '(pondera:', ponderacionDeLaVariable, ')')
                    elif nBanda == self_nBandasRasterOutput - 1:
                        # myLog.debug(f'{TB}-> Banda {nBanda} -> (cluster) Chequeando tipo de bosque.')
                        print(TB, '-> Banda', nBanda, '-> (cluster) Chequeando tipo de bosque.')

                # if clusterCompleto:
                #     localClusterArrayMultiBandaDasoVars[nBanda-1] = arrayBandaXinputMonoPixelAll[nBanda - 1][
                #         nRowClusterIni:nRowClusterFin + 1, nColClusterIni:nColClusterFin + 1
                #     ]
                #     # Sustituyo el self_noDataDasoVarAll (-9999) por self_GLBLnoDataTipoDMasa (255)
                #     # localClusterArrayMultiBandaDasoVars[nBanda-1][localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = self_GLBLnoDataTipoDMasa
                #     if (localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll).all():
                #         continue
                # else:
                #     for desplY in range(-self_LOCLradioClusterPix, self_LOCLradioClusterPix + 1):
                #         for desplX in range(-self_LOCLradioClusterPix, self_LOCLradioClusterPix + 1):
                #             nRowCluster = nRowRaster + desplY
                #             nColCluster = nColRaster + desplX
                #             if (
                #                 nRowCluster >= 0
                #                 and nRowCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[0]
                #                 and nColCluster >= 0
                #                 and nColCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[1]
                #             ):
                #                 try:
                #                     localClusterArrayMultiBandaDasoVars[nInputVar, self_LOCLradioClusterPix + desplY, self_LOCLradioClusterPix + desplX] = (arrayBandaXAll[nBanda - 1])[nRowCluster, nColCluster]
                #                 except:
                #                     myLog.error(f'\n-> Revisar error: {nInputVar} {self_LOCLradioClusterPix + desplY} {self_LOCLradioClusterPix + desplX}')
                #                     myLog.error(f'localClusterArrayMultiBandaDasoVars.shape: {localClusterArrayMultiBandaDasoVars.shape}')
                #                     myLog.error(f'nRowCluster, nColCluster: {nRowCluster} {nColCluster}')
                #                     return (
                #                         False,
                #                         contadorAvisosCluster,
                #                         arrayBandaTipoBosc,
                #                         arrayBandaTipoMasa,
                #                         arrayDistanciaEuclideaMedia,
                #                         arrayDistanciaEuclideaRazon,
                #                         arrayPctjPorcentajeDeProximidad,
                #                         arrayDistanciaScipy,
                #                         self_maxDistanciaScipySuma,
                #                     )
                #     localSubClusterArrayMultiBandaDasoVars[nBanda-1] = localClusterArrayMultiBandaDasoVars[nInputVar, nRowClustIni:nRowClustFin, nColClustIni:nColClustFin]
                #     # Sustituyo el self_noDataDasoVarAll (-9999) por self_GLBLnoDataTipoDMasa (255)
                #     # localSubClusterArrayMultiBandaDasoVars[localSubClusterArrayMultiBandaDasoVars == self_noDataDasoVarAll] = self_GLBLnoDataTipoDMasa
                #     if (localSubClusterArrayMultiBandaDasoVars == self_noDataDasoVarAll).all():
                #         continue
                #
                #     # myLog.debug(localClusterArrayMultiBandaDasoVars[nBanda-1])
                #     # myLog.debug(localSubClusterArrayMultiBandaDasoVars)
                #         #     else:
                #         #         clusterCompleto = False
                #         #         break
                #         # if not clusterCompleto:
                #         #     break

                # myLog.debug(f'{TB}Calculando histograma+++')
                (
                    histogramaOk,
                    histNumberCluster,
                    histClasesCluster,
                    histProb01Cluster,
                    # localClusterArrayMultiBandaDasoVarsMasked,
                    # localSubClusterArrayMultiBandaDasoVarsMasked,
                    listaCeldasConDasoVarsOkCluster,
                    listaCeldasConDasoVarsOkSubCluster,
                ) = calculaHistogramasNb(
                    nRowRaster,
                    nColRaster,
                    clusterCompleto,
                    localClusterArrayMultiBandaDasoVars,
                    localSubClusterArrayMultiBandaDasoVars,
                    listaCeldasConDasoVarsOkCluster,
                    listaCeldasConDasoVarsOkSubCluster,
                    arrayBandaXMaskCluster,
                    arrayBandaXMaskSubCluster,
                    arrayRoundCluster,
                    nBanda,
                    self_myNBins,
                    self_myRange,
                    self_LOCLradioClusterPix=self_LOCLradioClusterPix,
                    self_outputNpDatatypeAll=self_outputNpDatatypeAll,
                    mostrarPixelClusterMatch=mostrarPixelClusterMatch,
                    self_noDataDasoVarAll=self_noDataDasoVarAll,
                    self_LOCLverbose=self_LOCLverbose and nInputVar < self_nInputVars,
                )
                if not histogramaOk:
                    return (
                        False,
                        contadorAvisosCluster,
                        arrayBandaTipoBosc,
                        arrayBandaTipoMasa,
                        arrayDistanciaEuclideaMedia,
                        arrayDistanciaEuclideaRazon,
                        arrayPctjPorcentajeDeProximidad,
                        arrayDistanciaScipy,
                        self_maxDistanciaScipySuma,
                    )
                if len(np.nonzero(histNumberCluster)[0]) == 0:
                    if mostrarPixelClusterMatch:
                        # myLog.warning(f'clidtwinb-> Aviso: el cluster de nRowColRaster: {nRowRaster} {nColRaster} nBanda: {nBanda} tiene todas celdas nulas (clusterCompleto: {clusterCompleto}).')
                        print('clidtwinb-> Aviso: el cluster de nRowColRaster:', nRowRaster, nColRaster, 'nBanda:', nBanda, 'tiene todas celdas nulas (clusterCompleto:', clusterCompleto, ').')
                    continue
                (
                    clusterOk,
                    dictArrayMultiBandaClusterDasoVars,
                    nVariablesNoOk,
                    tipoBosqueOk,
                ) = calculaClusterDasoVarsNb(
                    dictArrayMultiBandaClusterDasoVars,
                    nBanda,
                    histNumberCluster,
                    histProb01Cluster,
                    self_listHistProb01,
                    self_codeTipoBosquePatronMasFrecuente1,
                    self_pctjTipoBosquePatronMasFrecuente1,
                    self_codeTipoBosquePatronMasFrecuente2,
                    self_pctjTipoBosquePatronMasFrecuente2,
                    self_nInputVars,
                    self_myNBins,
                    self_myRange,
                    # self_LOCLlistLstDasoVars,
                    multiplicadorDeFueraDeRangoParaLaVariable,
                    ponderacionDeLaVariable,
                    nVariablesNoOk,
                    tipoBosqueOk,
                    # localClusterArrayMultiBandaDasoVars,
                    self_outputNpDatatypeAll,
                    nRowRaster=nRowRaster,
                    nColRaster=nColRaster,
                    mostrarPixelClusterMatch=mostrarPixelClusterMatch,
                    self_LOCLverbose=self_LOCLverbose,
                )
                if not clusterOk:
                    return (
                        False,
                        contadorAvisosCluster,
                        arrayBandaTipoBosc,
                        arrayBandaTipoMasa,
                        arrayDistanciaEuclideaMedia,
                        arrayDistanciaEuclideaRazon,
                        arrayPctjPorcentajeDeProximidad,
                        arrayDistanciaScipy,
                        self_maxDistanciaScipySuma,
                    )

                # Se compara el histograma del patron con el del cluster
                if nInputVar < self_nInputVars:
                    # if mostrarPixelClusterMatch:
                    #     print(f'nBanda: {nBanda}, nInputVar:{nInputVar}')
                    #     print(f'{TB}histProb01Cluster:             {histProb01Cluster.shape}')
                    #     print(f'{TB}self_dictHistProb01[claveRef]: {self_dictHistProb01[claveRef].shape}')
                    # for numMethod, (methodName, method) in enumerate(SCIPY_METHODS):
                    for numMethod in nb.prange(nScipyMethods):
                        # distanciaEntreHistogramas = method(self_dictHistProb01[claveRef], histProb01Cluster)
                        # Uso solo las primeras clases del histograma (por defecto tiene maxNBins = 256 clases)
                        # distanciaEntreHistogramas = method(self_listHistProb01[nInputVar, 1, :self_nBandasRasterOutput + 1], histProb01Cluster)
                        # Ver metodos de distancia entre vectores en:
                        #  https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html#scipy.spatial.distance.pdist
                        if numMethod == 0:
                            methodName = 'Euclidean'
                            # distanciaEntreHistogramas = distance_hist.euclidean(self_listHistProb01[nInputVar, 1, :self_nBandasRasterOutput + 1], histProb01Cluster)
                            distanciaEntreHistogramas = myDistanceEuclidea(self_listHistProb01[nInputVar, 1, :self_myNBins[nBanda]], histProb01Cluster)
                        elif numMethod == 1:
                            methodName = 'Manhattan'
                            # city block or Manhattan distance between the points:
                            #  https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cityblock.html#scipy.spatial.distance.cityblock
                            #  d(u, v) = sum_i|ui - vi|
                            # distanciaEntreHistogramas = distance_hist.cityblock(self_listHistProb01[nInputVar, 1, :self_myNBins[nBanda]], histProb01Cluster)
                            distanciaEntreHistogramas = 0
                        elif numMethod == 2:
                            methodName = 'Chebysev'
                            # The Chebyshev distance between two n-vectors u and v is the maximum norm-1 distance
                            #  https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.chebyshev.html#scipy.spatial.distance.chebyshev
                            #  between their respective elements. More precisely, the distance is given by
                            #  d(u, v) = max_i(ui - vi)
                            # distanciaEntreHistogramas = distance_hist.chebyshev(self_listHistProb01[nInputVar, 1, :self_myNBins[nBanda]], histProb01Cluster)
                            distanciaEntreHistogramas = 0
                        arrayDistanciaScipy[nInputVar, numMethod, nRowRaster, nColRaster] = distanciaEntreHistogramas
                        self_maxDistanciaScipyMono = max(arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster], self_maxDistanciaScipyMono)
                        # La ultma banda (extra) tiene la suma ponderada de las distancias
                        # if mostrarPixelClusterMatch:
                        #     myLog.debug(
                        #         f'clidtwinb-> sumando distancias-> nBanda: {nBanda}; '
                        #         f'M{numMethod} ({methodName}): {distanciaEntreHistogramas} * {ponderacionDeLaVariable} '
                        #         f'suma: {arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster]} '
                        #         f'noData: {self_GLBLnoDataDistancia}'
                        #     )
                        if arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster] == self_GLBLnoDataDistancia:
                            arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster] = distanciaEntreHistogramas * ponderacionDeLaVariable / sumaPoderaciones
                        else:
                            arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster] += distanciaEntreHistogramas * ponderacionDeLaVariable / sumaPoderaciones
                            self_maxDistanciaScipySuma = max(arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster], self_maxDistanciaScipySuma)
                        # if mostrarPixelClusterMatch:
                        #     myLog.debug(
                        #         f'suma: {arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster]} '
                        #         f'maxDist: {self_maxDistanciaScipySuma} '
                        #     )

            # ==================================================================
            if clusterCompleto:
                # Distancias entre listas de vectores:
                #  https://docs.scipy.org/doc/scipy/reference/spatial.distance.html
                # ññññ
                # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance_matrix.html
                # matrizDeDistanciasPatronCluster = distance_matrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], listaCeldasConDasoVarsOkCluster[:, :self.nInputVars], p=2) / self.nInputVars
                # matrizDeDistanciasPatronPatron = distance_matrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], p=2) / self.nInputVars
                # distance_matrix y np.average no implementados en numba
                # Se sustituyen por esta otra, que es muy lenta si no se compila con numba:
                matrizDeDistanciasPatronCluster = myDistanceMatrix(self_listaCeldasConDasoVarsOkPatron[:, :self_nInputVars], listaCeldasConDasoVarsOkCluster[:, :self_nInputVars])
                matrizDeDistanciasPatronPatron = myDistanceMatrix(self_listaCeldasConDasoVarsOkPatron[:, :self_nInputVars], self_listaCeldasConDasoVarsOkPatron[:, :self_nInputVars])
                # distanciaEuclideaMedia_ = np.average(matrizDeDistancias_)
                distanciaEuclideaMediaPatronCluster = np.mean(matrizDeDistanciasPatronCluster)
                distanciaEuclideaMediaPatronPatron = np.mean(matrizDeDistanciasPatronPatron)
                if mostrarPixelClusterMatch:
                    # myLog.debug(f'Numero de puntos Cluster con dasoVars ok: {len(ma.compressed(localClusterArrayMultiBandaDasoVarsMasked))}')
                    # myLog.debug(f'matrizDeDistanciasPatronCluster.shape: {matrizDeDistanciasPatronCluster.shape} Distancia media: {distanciaEuclideaMediaPatronCluster}')
                    print('Numero de puntos Cluster con dasoVars ok:', len(listaCeldasConDasoVarsOkCluster[:, nInputVar]))
                    print('matrizDeDistanciasPatronCluster.shape:', matrizDeDistanciasPatronCluster.shape, 'Distancia media PatronCluster:', distanciaEuclideaMediaPatronCluster)
                    print('matrizDeDistanciasPatronPatron.shape: ', matrizDeDistanciasPatronPatron.shape, 'Distancia media PatronPatron: ', distanciaEuclideaMediaPatronPatron)
                    # myLog.debug('clidtwinb-> Matriz de distancias:')
                    # myLog.debug(matrizDeDistanciasPatronCluster[:5,:5])
            else:
                # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance_matrix.html
                # matrizDeDistanciasPatronCluster = distance_matrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], listaCeldasConDasoVarsOkSubCluster[:, :self.nInputVars], p=2) / self.nInputVars
                # matrizDeDistanciasPatronPatron = distance_matrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], p=2) / self.nInputVars
                # distance_matrix y np.average no implementados en numba
                # Se sustituyen por esta otra, que es muy lenta si no se compila con numba:
                matrizDeDistanciasPatronCluster = myDistanceMatrix(self_listaCeldasConDasoVarsOkPatron[:, :self_nInputVars], listaCeldasConDasoVarsOkSubCluster[:, :self_nInputVars])
                matrizDeDistanciasPatronPatron = myDistanceMatrix(self_listaCeldasConDasoVarsOkPatron[:, :self_nInputVars], self_listaCeldasConDasoVarsOkPatron[:, :self_nInputVars])
                # distanciaEuclideaMedia_ = np.average(matrizDeDistancias_)
                distanciaEuclideaMediaPatronCluster = np.mean(matrizDeDistanciasPatronCluster)
                distanciaEuclideaMediaPatronPatron = np.mean(matrizDeDistanciasPatronPatron)
                if mostrarPixelClusterMatch:
                    # myLog.debug(f'Numero de puntos subCluster con dasoVars ok: {len(ma.compressed(localSubClusterArrayMultiBandaDasoVarsMasked))}')
                    # myLog.debug(f'matrizDeDistanciasPatronCluster.shape: {matrizDeDistanciasPatronCluster.shape} Distancia media: {distanciaEuclideaMediaPatronCluster}')
                    print('Numero de puntos subCluster con dasoVars ok:', len(listaCeldasConDasoVarsOkSubCluster[:, nInputVar]))
                    print('matrizDeDistanciasPatronCluster.shape:', matrizDeDistanciasPatronCluster.shape, 'Distancia media PatronCluster:', distanciaEuclideaMediaPatronCluster)
                    print('matrizDeDistanciasPatronPatron.shape: ', matrizDeDistanciasPatronPatron.shape, 'Distancia media PatronPatron: ', distanciaEuclideaMediaPatronPatron)
                    # myLog.debug('clidtwinb-> Matriz de distancias:')
                    # myLog.debug(matrizDeDistanciasPatronCluster[:5,:5])
            # ==================================================================
            tipoMasaOk = tipoBosqueOk >= TRNS_tipoBoscCompatible and nVariablesNoOk <= 1
            if mostrarPixelClusterMatch:
                # myLog.debug(
                #     f'nRowColRaster: {nRowRaster} {nColRaster}; '
                #     f'coordXY: {coordX} {coordY} '
                #     f'-> Resumen del match-> tipoBosqueOk: {tipoBosqueOk} '
                #     f'nVariablesNoOk: {nVariablesNoOk}. '
                #     f'Match: {tipoMasaOk}')
                print(
                    'nRowColRaster:', nRowRaster, nColRaster, '; ',
                    'coordXY:', coordX, coordY,
                    '-> Resumen del match-> tipoBosqueOk:', tipoBosqueOk,
                    'nVariablesNoOk:', nVariablesNoOk,
                    'Match:', tipoMasaOk
                )
                if self_LOCLverbose == 3:
                    if not listaCeldasConDasoVarsOkSubCluster is None:
                        # myLog.debug(f'listaCeldasConDasoVarsOkSubCluster (shape (nCeldasClusterOk, nBandas): {listaCeldasConDasoVarsOkSubCluster.shape}):')
                        print('listaCeldasConDasoVarsOkSubCluster (shape (nCeldasClusterOk, nBandas):', listaCeldasConDasoVarsOkSubCluster.shape, '):')
                    else:
                        # myLog.debug(f'listaCeldasConDasoVarsOkSubCluster:')
                        print('listaCeldasConDasoVarsOkSubCluster:')
                    # myLog.debug(listaCeldasConDasoVarsOkSubCluster)
                    ##print(listaCeldasConDasoVarsOkSubCluster)

                    if not listaCeldasConDasoVarsOkCluster is None:
                        # myLog.debug(f'listaCeldasConDasoVarsOkCluster (shape: {listaCeldasConDasoVarsOkCluster.shape}):')
                        print('listaCeldasConDasoVarsOkCluster (shape:', listaCeldasConDasoVarsOkCluster.shape, '):')
                    else:
                        # myLog.debug(f'listaCeldasConDasoVarsOkCluster:')
                        print('listaCeldasConDasoVarsOkCluster:')
                    # myLog.debug(listaCeldasConDasoVarsOkCluster)
                    ##print(listaCeldasConDasoVarsOkCluster)

                    # myLog.debug(f'listaCeldasConDasoVarsOkPatron (shape (nCeldasPatron, nBandas): {self_listaCeldasConDasoVarsOkPatron.shape}):')
                    # myLog.debug(self_listaCeldasConDasoVarsOkPatron)
                    # myLog.debug(f'matrizDeDistanciasPatronCluster (shape: (nCeldasPatron, nCeldasClusterOk): {matrizDeDistanciasPatronCluster.shape}):')
                    # myLog.debug(matrizDeDistanciasPatronCluster)
                    print('listaCeldasConDasoVarsOkPatron (shape (nCeldasPatron, nBandas):', self_listaCeldasConDasoVarsOkPatron.shape, '):')
                    ##print(self_listaCeldasConDasoVarsOkPatron)
                    print('matrizDeDistanciasPatronCluster (shape: (nCeldasPatron, nCeldasClusterOk):', matrizDeDistanciasPatronCluster.shape, '):')
                    ##print(matrizDeDistanciasPatronCluster)

            arrayBandaTipoBosc[nRowRaster, nColRaster] = tipoBosqueOk
            arrayBandaTipoMasa[nRowRaster, nColRaster] = tipoMasaOk
            arrayDistanciaEuclideaMedia[nRowRaster, nColRaster] = distanciaEuclideaMediaPatronCluster
            if distanciaEuclideaMediaPatronPatron:
                arrayDistanciaEuclideaRazon[nRowRaster, nColRaster] = distanciaEuclideaMediaPatronCluster / distanciaEuclideaMediaPatronPatron
            numElementosTotal = matrizDeDistanciasPatronCluster.shape[0] * matrizDeDistanciasPatronCluster.shape[1]
            # if np.ma.count(matrizDeDistanciasPatronCluster) != 0:
            if numElementosTotal:
                numeroValoresSobreUmbral = (matrizDeDistanciasPatronCluster < self_GLBLumbralMatriDist).sum()
                arrayPctjPorcentajeDeProximidad[nRowRaster, nColRaster] = 100 * (
                    numeroValoresSobreUmbral / numElementosTotal
                )
            # else:
            #     myLog.debug(f'----> {nRowRaster} {nColRaster} {matrizDeDistanciasPatronCluster[:5,:5]}')

    '''
    print('contadorAvisosCluster:', contadorAvisosCluster)
    print('arrayBandaTipoBosc:')
    ##print(arrayBandaTipoBosc)
    print('arrayBandaTipoMasa:')
    ##print(arrayBandaTipoMasa)
    print('arrayDistanciaEuclideaMedia:')
    ##print(arrayDistanciaEuclideaMedia)
    print('arrayDistanciaEuclideaRazon:')
    ##print(arrayDistanciaEuclideaRazon)
    print('arrayPctjPorcentajeDeProximidad:')
    ##print(arrayPctjPorcentajeDeProximidad)
    print('arrayDistanciaScipy:')
    ##print(arrayDistanciaScipy)
    print('self_maxDistanciaScipySuma:', self_maxDistanciaScipySuma)
    '''

    return (
        True,
        contadorAvisosCluster,
        arrayBandaTipoBosc,
        arrayBandaTipoMasa,
        arrayDistanciaEuclideaMedia,
        arrayDistanciaEuclideaRazon,
        arrayPctjPorcentajeDeProximidad,
        arrayDistanciaScipy,
        self_maxDistanciaScipySuma,
    )


# ==============================================================================
@nb.jit(nopython=True)
def rellenarLocalClusterNb(
        arrayBandaXinputMonoPixelAll,
        nRowRaster,
        nColRaster,
        self_LOCLradioClusterPix,
        self_noDataDasoVarAll,
        self_outputNpDatatypeAll,
        mostrarPixelClusterMatch,
        contadorAvisosCluster,
        self_LOCLverbose=False,
        # localClusterArrayMultiBandaDasoVars,
        # localSubClusterArrayMultiBandaDasoVars,
        # arrayBandaXMaskCluster,
        # arrayBandaXMaskSubCluster,
    ):

    # No admitido con numba (cambio de dict a ndarray):
    # self_nBandasRasterOutput = len(arrayBandaXinputMonoPixelAll.keys())
    self_nBandasRasterOutput = arrayBandaXinputMonoPixelAll.shape[0]
    ladoCluster = (self_LOCLradioClusterPix * 2) + 1
    coordY = (arrayBandaXinputMonoPixelAll[0]).shape[0] - nRowRaster
    coordX = nColRaster

    # ======================================================================
    localClusterArrayMultiBandaDasoVars = np.zeros(
        (self_nBandasRasterOutput)
        * (ladoCluster ** 2),
        dtype=self_outputNpDatatypeAll
    ).reshape(
        self_nBandasRasterOutput,
        ladoCluster,
        ladoCluster
    )
    # localSubClusterArrayMultiBandaDasoVars = np.zeros(
    #     (self_nBandasRasterOutput)
    #     * (ladoCluster ** 2),
    #     dtype=self_outputNpDatatypeAll
    # ).reshape(
    #     self_nBandasRasterOutput,
    #     ladoCluster,
    #     ladoCluster
    # )
    localSubClusterArrayMultiBandaDasoVars = np.zeros(1, dtype=self_outputNpDatatypeAll).reshape(1, 1, 1)
    arrayBandaXMaskCluster = np.zeros(
        (ladoCluster ** 2), dtype=np.uint8
    ).reshape(
        ladoCluster,
        ladoCluster
    )
    # arrayBandaXMaskSubCluster = np.zeros(
    #     (ladoCluster ** 2), dtype=np.uint8
    # ).reshape(
    #     ladoCluster,
    #     ladoCluster
    # )
    arrayBandaXMaskSubCluster = np.zeros(1, dtype=np.uint8).reshape(1, 1)
    # ======================================================================

    # ======================================================================
    arrayBandaXMaskCluster.fill(0)
    # arrayBandaXMaskSubCluster.fill(0)
    # ======================================================================
    # Array con los valores de las dasoVars en el cluster local,
    # cambia para cada cluster local de cada pixel
    localClusterArrayMultiBandaDasoVars.fill(0)
    # localSubClusterArrayMultiBandaDasoVars.fill(0)
    # ======================================================================

    # # myLog.debug(f'-->>nRowRaster: {nRowRaster} nColRaster: {nColRaster}') 
    # print('-->>nRowRaster:', nRowRaster, 'nColRaster:', nColRaster) 
    nCeldasConDasoVarsOk = 0
    nRowClusterIni = nRowRaster - self_LOCLradioClusterPix
    nRowClusterFin = nRowRaster + self_LOCLradioClusterPix
    nColClusterIni = nColRaster - self_LOCLradioClusterPix
    nColClusterFin = nColRaster + self_LOCLradioClusterPix
    if (
        nRowClusterIni >= 0
        and nColClusterIni >= 0
        and nRowClusterFin < (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[0]
        and nColClusterFin < (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[1]
    ):
        clusterCompleto = True
    else:
        clusterCompleto = False
        if nRowClusterIni < 0:
            nRowClustIni = - nRowClusterIni
        else:
            nRowClustIni = 0
        if nColClusterIni < 0:
            nColClustIni = - nColClusterIni
        else:
            nColClustIni = 0
        if nRowClusterFin >= (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[0]:
            nRowClustFin = ladoCluster - (nRowClusterFin - (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[0])
        else:
            nRowClustFin = ladoCluster
        if nColClusterFin >= (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[1]:
            nColClustFin = ladoCluster - (nColClusterFin - (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape[1])
        else:
            nColClustFin = ladoCluster
        # # myLog.debug(f'-->>nRowClusterIniFin: {nRowClusterIni} {nRowClusterFin} nColClustIniFin: {nColClusterIni} {nColClusterFin} clusterCompleto: {clusterCompleto}')
        # # myLog.debug(f'-->>(arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape: {(arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape}')
        # # myLog.debug(f'-->>nRowClustIniFin: {nRowClustIni} {nRowClustFin} nColClustIniFin: {nColClustIni} {nColClustFin}')
        # print('-->>nRowClusterIniFin:', nRowClusterIni, nRowClusterFin, 'nColClustIniFin:', nColClusterIni, nColClusterFin, 'clusterCompleto:', clusterCompleto)
        # print('-->>(arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape:', (arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape)
        # print('-->>nRowClustIniFin:', nRowClustIni, nRowClustFin, 'nColClustIniFin:', nColClustIni, nColClustFin)

    # ==================================================================
    # Tengo que recorrer todas las bandas para enmascarar las celdas con alguna banda noData
    # Empiezo contando el numero de celdas con valor valido en todas las bandas
    # Una vez contadas (nCeldasConDasoVarsOk) creare en la funcion principal
    # el array listaCeldasConDasoVarsOkCluster
    if clusterCompleto:
        # Para contar el numero de celdas con valores distintos de noData en todas las bandas,
        # se parte de un array con todos los valores cero (arrayBandaXMaskCluster),
        # se ponen a 1 las celdas con ALGUN valor noData y, despues de recorrer 
        # todas las bandas, se cuenta el numero de celdas igual a cero.
        # Con eso, se crea un array que va a contener la lista de celdas con valor ok
        arrayBandaXMaskCluster.fill(0)
        # Recorro todas las bandas para verificar en cada celda si hay valores validos en todas las bandas
        # Calculo arrayBandaXMaskCluster y con ella enmascaro los noData al calcular el histograma de cada banda
        for nBanda in range(1, self_nBandasRasterOutput + 1):
            localClusterArrayMultiBandaDasoVars[nBanda-1] = arrayBandaXinputMonoPixelAll[
                nBanda - 1,
                nRowClusterIni:nRowClusterFin + 1,
                nColClusterIni:nColClusterFin + 1
            ]
            # Sustituyo el self_noDataDasoVarAll (-9999) por self_GLBLnoDataTipoDMasa (255)
            # localClusterArrayMultiBandaDasoVars[nBanda-1][localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = self_GLBLnoDataTipoDMasa
            # Si no hay informacion de TipoBosque (MFE):
            if (localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll).all():
                localClusterOk = False
                return (
                    localClusterOk,
                    contadorAvisosCluster,
                    clusterCompleto,
                    nCeldasConDasoVarsOk,
                    localClusterArrayMultiBandaDasoVars,
                    localSubClusterArrayMultiBandaDasoVars,
                    arrayBandaXMaskCluster,
                    arrayBandaXMaskSubCluster,
                )
                # continue
            # No admitido con numba:
            # arrayBandaXMaskCluster[localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = 1
            for nRowNb in nb.prange(ladoCluster):
                for nColNb in nb.prange(ladoCluster):
                    if localClusterArrayMultiBandaDasoVars[nBanda-1, nRowNb, nColNb] == self_noDataDasoVarAll:
                        arrayBandaXMaskCluster[nRowNb, nColNb] = 1
        if (arrayBandaXMaskCluster == 1).all():
            if self_LOCLverbose:
                if contadorAvisosCluster == 0:
                    # myLog.debug('')
                    print('')
                if contadorAvisosCluster < 10:
                    # myLog.debug(f'{TB}{TV}-> AVISO (cluster): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
                    print('clidtwinb-> AVISO (cluster):', nRowRaster, nColRaster ,'-> celda sin valores disponibles para generar cluster')
                elif contadorAvisosCluster == 10:
                    # myLog.debug(f'{TB}{TV}-> AVISO (cluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster.')
                    # myLog.debug(f'{TB}{TV}-> No se muestran mas.')
                    print('clidtwinb-> AVISO (cluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster.')
                    print('         -> No se muestran mas.')
            contadorAvisosCluster += 1
            localClusterOk = False
            return (
                localClusterOk,
                contadorAvisosCluster,
                clusterCompleto,
                nCeldasConDasoVarsOk,
                localClusterArrayMultiBandaDasoVars,
                localSubClusterArrayMultiBandaDasoVars,
                arrayBandaXMaskCluster,
                arrayBandaXMaskSubCluster,
            )
            # continue
        elif (arrayBandaXMaskCluster != 1).sum() < MINIMO_PIXELS_POR_CLUSTER:
            if self_LOCLverbose:
                if contadorAvisosCluster == 0:
                    # myLog.debug('')
                    print('')
                if contadorAvisosCluster < 10:
                    # myLog.debug(f'{TB}{TV}-> AVISO (cluster): {nRowRaster} {nColRaster} -> celda con pocos valores disponibles para generar cluster: {(arrayBandaXMaskCluster != 1).sum()}')
                    print('clidtwinb-> AVISO (cluster):', nRowRaster, nColRaster ,'-> celda con pocos valores disponibles para generar cluster:', (arrayBandaXMaskCluster != 1).sum())
                elif contadorAvisosCluster == 10:
                    # myLog.debug(f'{TB}{TV}-> AVISO (cluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
                    print('clidtwinb-> AVISO (cluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1

            localClusterOk = False
            return (
                localClusterOk,
                contadorAvisosCluster,
                clusterCompleto,
                nCeldasConDasoVarsOk,
                localClusterArrayMultiBandaDasoVars,
                localSubClusterArrayMultiBandaDasoVars,
                arrayBandaXMaskCluster,
                arrayBandaXMaskSubCluster,
            )
            # continue

        nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskCluster == 0)
    else:
        localSubClusterArrayMultiBandaDasoVars = np.zeros(
            (self_nBandasRasterOutput)
            * (nRowClustFin - nRowClustIni)
            * (nColClustFin - nColClustIni),
            dtype=self_outputNpDatatypeAll
        ).reshape(
            self_nBandasRasterOutput,
            nRowClustFin - nRowClustIni,
            nColClustFin - nColClustIni
        )
        # Este array es para contar las celda con valores validos en todas las bandas:
        arrayBandaXMaskSubCluster = np.zeros(
            (nRowClustFin - nRowClustIni)
            * (nColClustFin - nColClustIni),
            dtype=np.uint8
        ).reshape(
            nRowClustFin - nRowClustIni,
            nColClustFin - nColClustIni
        )

        # Tomo prestado este array que no uso por no ser clusterCompleto
        # Para calcular el subCluster
        localClusterArrayMultiBandaDasoVars.fill(nb.float32(self_noDataDasoVarAll))
        # Recorro todas las bandas para verificar en cada celda si hay valores validos en todas las bandas
        # Calculo arrayBandaXMaskSubCluster y con ella enmascaro los noData al calcular el histograma de cada banda
        for nBanda in range(1, self_nBandasRasterOutput + 1):
            nInputVar = nBanda - 1
            for desplY in range(-self_LOCLradioClusterPix, self_LOCLradioClusterPix + 1):
                for desplX in range(-self_LOCLradioClusterPix, self_LOCLradioClusterPix + 1):
                    nRowCluster = nRowRaster + desplY
                    nColCluster = nColRaster + desplX
                    if (
                        nRowCluster >= 0
                        and nRowCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[0]
                        and nColCluster >= 0
                        and nColCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[1]
                    ):
                        try:
                            localClusterArrayMultiBandaDasoVars[
                                nInputVar,
                                self_LOCLradioClusterPix + desplY,
                                self_LOCLradioClusterPix + desplX
                            ] = arrayBandaXinputMonoPixelAll[nBanda - 1][
                                nRowCluster, nColCluster
                            ]
                        except:
                            # myLog.error(f'\n-> Revisar error: {nInputVar} {self_LOCLradioClusterPix + desplY} {self_LOCLradioClusterPix + desplX}')
                            # myLog.error(f'localClusterArrayMultiBandaDasoVars.shape: {localClusterArrayMultiBandaDasoVars.shape}')
                            # myLog.error(f'nRowCluster, nColCluster: {nRowCluster} {nColCluster}')
                            print('\n-> Revisar error:', nInputVar, self_LOCLradioClusterPix + desplY, self_LOCLradioClusterPix + desplX)
                            print('localClusterArrayMultiBandaDasoVars.shape:', localClusterArrayMultiBandaDasoVars.shape)
                            print('nRowCluster, nColCluster:', nRowCluster, nColCluster)
                            localClusterOk = False
                            contadorAvisosCluster = -1
                            return (
                                localClusterOk,
                                contadorAvisosCluster,
                                clusterCompleto,
                                nCeldasConDasoVarsOk,
                                localClusterArrayMultiBandaDasoVars,
                                localSubClusterArrayMultiBandaDasoVars,
                                arrayBandaXMaskCluster,
                                arrayBandaXMaskSubCluster,
                            )
            # localSubClusterArrayMultiBandaDasoVars[nBanda-1][
            #     nRowClustIni:nRowClustFin,
            #     nColClustIni:nColClustFin
            # ] = localClusterArrayMultiBandaDasoVars[nBanda - 1][
            localSubClusterArrayMultiBandaDasoVars[nBanda-1] = localClusterArrayMultiBandaDasoVars[nBanda - 1][
                nRowClustIni:nRowClustFin,
                nColClustIni:nColClustFin
            ]
            # Sustituyo el self_noDataDasoVarAll (-9999) por self_GLBLnoDataTipoDMasa (255)
            # localSubClusterArrayMultiBandaDasoVars[localSubClusterArrayMultiBandaDasoVars == self_noDataDasoVarAll] = self_GLBLnoDataTipoDMasa
            if (localSubClusterArrayMultiBandaDasoVars == self_noDataDasoVarAll).all():
                localClusterOk = False
                return (
                    localClusterOk,
                    contadorAvisosCluster,
                    clusterCompleto,
                    nCeldasConDasoVarsOk,
                    localClusterArrayMultiBandaDasoVars,
                    localSubClusterArrayMultiBandaDasoVars,
                    arrayBandaXMaskCluster,
                    arrayBandaXMaskSubCluster,
                )
                # continue
            # No admitido con numba:
            # arrayBandaXMaskSubCluster[localSubClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = 1
            for nRowNb in nb.prange(localSubClusterArrayMultiBandaDasoVars.shape[1]):
                for nColNb in nb.prange(localSubClusterArrayMultiBandaDasoVars.shape[2]):
                    if localSubClusterArrayMultiBandaDasoVars[nBanda-1, nRowNb, nColNb] == self_noDataDasoVarAll:
                        arrayBandaXMaskSubCluster[nRowNb, nColNb] = 1

        # Anulo el array de cluster completo prestado temporalmente para el subCLuster
        localClusterArrayMultiBandaDasoVars.fill(nb.float32(self_noDataDasoVarAll))

        if (arrayBandaXMaskSubCluster == 1).all():
            if self_LOCLverbose:
                if contadorAvisosCluster == 0:
                    # myLog.debug('')
                    print('')
                if contadorAvisosCluster < 10:
                    # myLog.debug(f'{TB}{TV}-> AVISO (subcluster): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
                    print('clidtwinb-> AVISO (subcluster):', nRowRaster, nColRaster ,'-> celda sin valores disponibles para generar cluster')
                elif contadorAvisosCluster == 10:
                    # myLog.debug(f'{TB}{TV}-> AVISO (subcluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
                    print('clidtwinb-> AVISO (subcluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1
            localClusterOk = False
            return (
                localClusterOk,
                contadorAvisosCluster,
                clusterCompleto,
                nCeldasConDasoVarsOk,
                localClusterArrayMultiBandaDasoVars,
                localSubClusterArrayMultiBandaDasoVars,
                arrayBandaXMaskCluster,
                arrayBandaXMaskSubCluster,
            )
            # continue
        elif (arrayBandaXMaskSubCluster != 1).sum() < MINIMO_PIXELS_POR_CLUSTER:
            if self_LOCLverbose:
                if contadorAvisosCluster == 0:
                    # myLog.debug('')
                    print('')
                if contadorAvisosCluster < 10:
                    # myLog.debug(f'{TB}{TV}-> AVISO (subcluster): {nRowRaster} {nColRaster} -> celda con pocos valores disponibles para generar cluster: {(arrayBandaXMaskSubCluster != 1).sum()}')
                    print('clidtwinb-> AVISO (subcluster):', nRowRaster, nColRaster ,'-> celda con pocos valores disponibles para generar cluster:', (arrayBandaXMaskSubCluster != 1).sum())
                elif contadorAvisosCluster == 10:
                    # myLog.debug(f'{TB}{TV}-> AVISO (subcluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
                    print('clidtwinb-> AVISO (subcluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1
            localClusterOk = False
            return (
                localClusterOk,
                contadorAvisosCluster,
                clusterCompleto,
                nCeldasConDasoVarsOk,
                localClusterArrayMultiBandaDasoVars,
                localSubClusterArrayMultiBandaDasoVars,
                arrayBandaXMaskCluster,
                arrayBandaXMaskSubCluster,
            )
            # continue

        nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskSubCluster == 0)
    # ==============================================================

    if mostrarPixelClusterMatch:
        # myLog.debug(f'\n-> nRowColRaster: {nRowRaster} {nColRaster}; coordXY: {coordX} {coordY}')
        # myLog.debug(f'{TB}{TV}-> clusterCompleto: {clusterCompleto}')
        # myLog.debug(f'{TB}{TV}-> Numero de celdas con dasoVars ok en todas las bandas: {nCeldasConDasoVarsOk}')
        # myLog.debug(f'{TB}{TV}-> Celdas noData (valor=1): {arrayBandaXMaskSubCluster}')
        print('\n-> nRowColRaster:', nRowRaster, nColRaster, 'coordXY:', coordX, coordY)
        print('clidtwinb-> clusterCompleto:', clusterCompleto)
        print('clidtwinb-> Numero de celdas con dasoVars ok en todas las bandas:', nCeldasConDasoVarsOk)
        ##print('clidtwinb-> Celdas noData (valor=1):', arrayBandaXMaskSubCluster)

    localClusterOk = True
    return (
        localClusterOk,
        contadorAvisosCluster,
        clusterCompleto,
        nCeldasConDasoVarsOk,
        localClusterArrayMultiBandaDasoVars,
        localSubClusterArrayMultiBandaDasoVars,
        arrayBandaXMaskCluster,
        arrayBandaXMaskSubCluster,
    )


# ==============================================================================
@nb.jit(nopython=True)
def calculaHistogramasNb(
        nRowRaster,
        nColRaster,
        clusterCompleto,
        localClusterArrayMultiBandaDasoVars,
        localSubClusterArrayMultiBandaDasoVars,
        listaCeldasConDasoVarsOkCluster,
        listaCeldasConDasoVarsOkSubCluster,
        arrayBandaXMaskCluster,
        arrayBandaXMaskSubCluster,
        arrayRoundCluster,
        nBanda,
        self_myNBins,
        self_myRange,
        self_LOCLradioClusterPix=3,
        self_outputNpDatatypeAll=None,
        mostrarPixelClusterMatch=False,
        self_noDataDasoVarAll=None,
        self_LOCLverbose=False,
    ):
    if self_outputNpDatatypeAll is None:
        # self_outputNpDatatypeAll = localClusterArrayMultiBandaDasoVars.dtype
        self_outputNpDatatypeAll = np.float32
    nInputVar = nBanda - 1
    ladoCluster = (self_LOCLradioClusterPix * 2) + 1
    nRowClusterIni = nRowRaster - self_LOCLradioClusterPix
    # nRowClusterFin = nRowRaster + self_LOCLradioClusterPix
    nColClusterIni = nColRaster - self_LOCLradioClusterPix
    # nColClusterFin = nColRaster + self_LOCLradioClusterPix
    # localClusterArrayMultiBandaDasoVarsMasked = None
    # localSubClusterArrayMultiBandaDasoVarsMasked = None
    celdasConValorSiData = np.zeros((ladoCluster ** 2), dtype=self_outputNpDatatypeAll)

    # myLog.debug(f'\nCluster asignado a la variable {nInputVar}, coordendas del raster -> row: {nRowRaster} col: {nColRaster} (completo: {clusterCompleto}):')
    if clusterCompleto:
        # Esto no funciona con numba:
        # https://github.com/numba/numba/issues/1834
        # localClusterArrayMultiBandaDasoVarsMasked = ma.masked_array(
        #     localClusterArrayMultiBandaDasoVars[nBanda-1],
        #     mask=arrayBandaXMaskCluster,
        #     dtype=self_outputNpDatatypeAll
        # )
        # listaCeldasConDasoVarsOkCluster[:, nInputVar] = ma.compressed(localClusterArrayMultiBandaDasoVarsMasked)
        # Mascara alternativa que tampoco funciona con numba
        # localClusterArrayMultiBandaDasoVarsMasked = localClusterArrayMultiBandaDasoVars[nBanda-1][
        #     arrayBandaXMaskCluster == False
        # ]
        # listaCeldasConDasoVarsOkCluster[:, nInputVar] = np.ravel(localClusterArrayMultiBandaDasoVarsMasked)
        nContadorCluster = 0
        for nRowCluster in nb.prange(localClusterArrayMultiBandaDasoVars[nBanda-1].shape[0]):
            for nColCluster in nb.prange(localClusterArrayMultiBandaDasoVars[nBanda-1].shape[1]):
                if not arrayBandaXMaskCluster[nRowCluster, nColCluster]:
                    listaCeldasConDasoVarsOkCluster[
                        nContadorCluster, nInputVar
                    ] = localClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster]
                    nContadorCluster += 1

        # Utilizo el mismo arrayRoundCluster para todos los clusters porque tienen las mismas dimensiones

        # if localClusterArrayMultiBandaDasoVars[nBanda-1].sum() <= 0:
        #     myLog.debug(f'\nclidtwinb-> +++ {nRowRaster} // {nColRaster} clusterCompleto {clusterCompleto} '
        #           f'(b) Revisar myNBins {self_myNBins[nBanda]} '
        #           f'y myRange {self_myRange[nBanda]} para banda {nBanda} '
        #           f'con sumaValores: {localClusterArrayMultiBandaDasoVars[nBanda-1].sum()}')
        #     myLog.debug('arrayRoundCluster: {arrayRoundCluster}')
        #     myLog.debug(f'{TB}Se crean histogramas con {self_myNBins[nBanda]} clases nulas')
        #     myLog.debug(localClusterArrayMultiBandaDasoVars[nBanda-1])
        #     myLog.debug(f'Masked: {localClusterArrayMultiBandaDasoVarsMasked}')
        #     myLog.debug(f'Valores ok: {np.count_nonzero(localClusterArrayMultiBandaDasoVars[nBanda-1] != self_noDataDasoVarAll)}')
        # Mascara no admitida con numba:
        # celdasConValorSiData = localClusterArrayMultiBandaDasoVars[nBanda-1][
        #     (arrayRoundCluster != 0)
        #     & (localClusterArrayMultiBandaDasoVars[nBanda-1] != self_noDataDasoVarAll)
        #     & (localClusterArrayMultiBandaDasoVars[nBanda-1] >= self_myRange[nBanda][0])
        #     & (localClusterArrayMultiBandaDasoVars[nBanda-1] < self_myRange[nBanda][1])
        # ]
        # celdasConValorSiData = np.zeros((ladoCluster ** 2), dtype=self_outputNpDatatypeAll)
        celdasConValorSiData.fill(0)
        nContadorCluster = 0
        for nRowCluster in nb.prange(localClusterArrayMultiBandaDasoVars[nBanda-1].shape[0]):
            for nColCluster in nb.prange(localClusterArrayMultiBandaDasoVars[nBanda-1].shape[1]):
                if (
                    (arrayRoundCluster[nRowCluster, nColCluster] != 0)
                    and (localClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster] != self_noDataDasoVarAll)
                    and (localClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster] >= self_myRange[nBanda, 0])
                    and (localClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster] < self_myRange[nBanda, 1])
                ):
                    celdasConValorSiData[
                        nContadorCluster
                    ] = localClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster]
                    nContadorCluster += 1
        if (
            (np.count_nonzero(celdasConValorSiData) > 0)
            and (self_myNBins[nBanda] > 0)
            and (self_myRange[nBanda, 1] - self_myRange[nBanda, 0] > 0)
        ):
            # if np.count_nonzero(celdasConValorSiData) == 0:
            #     myLog.debug(f'\nclidtwinb-> ------------> ATENCION: celda sin datos.')
            # else:
            #     myLog.debug(f'\nclidtwinb-> ------------> Celdas con datos: {np.count_nonzero(celdasConValorSiData)} {celdasConValorSiData}')
            # numpy.histograms no esta en numba:
            # https://numba.pydata.org/numba-examples/examples/density_estimation/histogram/results.html
            # histNumberCluster, histClasesCluster = np.histogram(
            #     localClusterArrayMultiBandaDasoVars[nBanda-1],
            #     bins=self_myNBins[nBanda],
            #     range=self_myRange[nBanda],
            #     weights=arrayRoundCluster
            # )
            histNumberCluster, histClasesCluster = numba_histogram(
                localClusterArrayMultiBandaDasoVars[nBanda-1],
                bins=self_myNBins[nBanda],
                range=self_myRange[nBanda],
                weights=arrayRoundCluster,
                density=False
            )
            # histDensitCluster, histClasesCluster = np.histogram(
            #     localClusterArrayMultiBandaDasoVars[nBanda-1],
            #     bins=self_myNBins[nBanda],
            #     range=self_myRange[nBanda],
            #     weights=arrayRoundCluster,
            #     density=True
            # )
            # histDensitCluster, histClasesCluster = numba_histogram(
            #     localClusterArrayMultiBandaDasoVars[nBanda-1],
            #     bins=self_myNBins[nBanda],
            #     range=self_myRange[nBanda],
            #     weights=arrayRoundCluster,
            #     density=True,
            # )
        else:
            # myLog.debug(f'clidtwinb-> {nRowRaster} // {nColRaster} clusterCompleto {clusterCompleto} '
            #       f'(b) Revisar myNBins {self_myNBins[nBanda]} '
            #       f'y myRange {self_myRange[nBanda]} para banda {nBanda} '
            #       f'con sumaValores: {localClusterArrayMultiBandaDasoVars[nBanda-1].sum()}')
            # myLog.debug(f'{TB}Se crean histogramas con {self_myNBins[nBanda]} clases nulas')
            histNumberCluster = np.zeros(self_myNBins[nBanda], dtype=np.float32)
            histClasesCluster = np.zeros(self_myNBins[nBanda] + 1, dtype=np.float32)
            # histDensitCluster = np.zeros(self_myNBins[nBanda], dtype=np.float32)

    else:
        # myLog.debug(f'---->>>> {localSubClusterArrayMultiBandaDasoVars.shape}')
        # myLog.debug(f'---->>>> {arrayBandaXMaskSubCluster.shape} {nRowClustFin - nRowClustIni}, {nColClustFin - nColClustIni}')
        # myLog.debug(f'---->>>> {nRowClustFin}, {nRowClustIni}, {nColClustFin}, {nColClustIni}')
        # myLog.debug(f'---->>>> {nRowClusterFin}, {nRowClusterIni}, {nColClusterFin}, {nColClusterIni}')
        # Esto no funciona con numba:
        # https://github.com/numba/numba/issues/1834
        # localSubClusterArrayMultiBandaDasoVarsMasked = ma.masked_array(
        #     localSubClusterArrayMultiBandaDasoVars[nBanda-1],
        #     mask=arrayBandaXMaskSubCluster,
        #     dtype=self_outputNpDatatypeAll
        #     )
        # listaCeldasConDasoVarsOkSubCluster[:, nInputVar] = ma.compressed(localSubClusterArrayMultiBandaDasoVarsMasked)
        # Mascara alternativa que tampoco funciona con numba
        # localSubClusterArrayMultiBandaDasoVarsMasked = localClusterArrayMultiBandaDasoVars[nBanda-1][
        #     arrayBandaXMaskSubCluster == False
        # ]
        # listaCeldasConDasoVarsOkSubCluster[:, nInputVar] = np.ravel(localSubClusterArrayMultiBandaDasoVarsMasked)
        nContadorCluster = 0
        for nRowCluster in nb.prange(localSubClusterArrayMultiBandaDasoVars[nBanda-1].shape[0]):
            for nColCluster in nb.prange(localSubClusterArrayMultiBandaDasoVars[nBanda-1].shape[1]):
                if arrayBandaXMaskSubCluster[nRowCluster, nColCluster] == False:
                    listaCeldasConDasoVarsOkSubCluster[
                        nContadorCluster, nInputVar
                    ] = localSubClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster]
                    nContadorCluster += 1

        # myLog.debug(localSubClusterArrayMultiBandaDasoVars[nBanda-1])

        # Utilizo un arrayRoundSubCluster especifico para este subCluster aunque creo q no es imprescindible
        arrayRoundSubCluster = np.full_like(localSubClusterArrayMultiBandaDasoVars[nBanda-1], 1, dtype=np.uint8)
        desplRow = nRowClusterIni - (nRowRaster - self_LOCLradioClusterPix)
        desplCol = nColClusterIni - (nColRaster - self_LOCLradioClusterPix)
        # Posicion del centro del cluster completo referido a la esquina sup-izda del subCluster
        #     En coordenadas referidas al array completo: nRowRaster, nColRaster
        #     En coordenadas referidas al subCluster hay que tener en cuenta el origen del subCluster dentro del cluster (desplRow, desplCol)
        nRowCenter = (arrayRoundSubCluster.shape[0] / 2) - desplRow
        nColCenter = (arrayRoundSubCluster.shape[1] / 2) - desplCol
        for nRowCell in range(arrayRoundSubCluster.shape[0]):
            for nColCell in range(arrayRoundSubCluster.shape[1]):
                if np.sqrt(((nRowCell - nRowCenter) ** 2) + ((nColCell - nColCenter) ** 2)) > ladoCluster / 2:
                    arrayRoundSubCluster[nRowCell, nColCell] = 0
    
        # if localSubClusterArrayMultiBandaDasoVars[nBanda-1].sum() <= 0:
        #     myLog.debug(f'clidtwinb-> +++ {nRowRaster} // {nColRaster} clusterCompleto {clusterCompleto} '
        #           f'(c) Revisar myNBins {self_myNBins[nBanda]} '
        #           f'y myRange {self_myRange[nBanda]} para banda {nBanda} '
        #           f'con sumaValores: {localSubClusterArrayMultiBandaDasoVars[nBanda-1].sum()}')
        #     myLog.debug(f'{TB}Se crean histogramas con {self_myNBins[nBanda]} clases nulas')
        #     myLog.debug(localSubClusterArrayMultiBandaDasoVars[nBanda-1])
        #     myLog.debug(f'Masked: {localSubClusterArrayMultiBandaDasoVarsMasked}')
        #     myLog.debug(f'Valores ok: {np.count_nonzero(localSubClusterArrayMultiBandaDasoVars[nBanda-1] != self_noDataDasoVarAll)}')
        try:
            # Mascara no admitida con numba:
            # celdasConValorSiData = localSubClusterArrayMultiBandaDasoVars[nBanda-1][
            #     (arrayRoundSubCluster != 0)
            #     & (localSubClusterArrayMultiBandaDasoVars[nBanda-1] != self_noDataDasoVarAll)
            #     & (localSubClusterArrayMultiBandaDasoVars[nBanda-1] >= self_myRange[nBanda][0])
            #     & (localSubClusterArrayMultiBandaDasoVars[nBanda-1] < self_myRange[nBanda][1])
            # ]
            # celdasConValorSiData = np.zeros((ladoCluster ** 2), dtype=self_outputNpDatatypeAll)
            celdasConValorSiData.fill(0)
            nContadorCluster = 0
            for nRowCluster in nb.prange(localSubClusterArrayMultiBandaDasoVars[nBanda-1].shape[0]):
                for nColCluster in nb.prange(localSubClusterArrayMultiBandaDasoVars[nBanda-1].shape[1]):
                    if (
                        (arrayRoundSubCluster[nRowCluster, nColCluster] != 0)
                        and (localSubClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster] != self_noDataDasoVarAll)
                        and (localSubClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster] >= self_myRange[nBanda, 0])
                        and (localSubClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster] < self_myRange[nBanda, 1])
                    ):
                        celdasConValorSiData[
                            nContadorCluster
                        ] = localSubClusterArrayMultiBandaDasoVars[nBanda-1, nRowCluster, nColCluster]
                        nContadorCluster += 1


            if (
                (np.count_nonzero(celdasConValorSiData) > 0)
                and (self_myNBins[nBanda] > 0)
                and (self_myRange[nBanda, 1] - self_myRange[nBanda, 0] > 0)
            ):
                # histNumberCluster, histClasesCluster = np.histogram(
                #     localSubClusterArrayMultiBandaDasoVars[nBanda-1],
                #     bins=self_myNBins[nBanda],
                #     range=self_myRange[nBanda],
                #     weights=arrayRoundSubCluster
                # )
                histNumberCluster, histClasesCluster = numba_histogram(
                    localSubClusterArrayMultiBandaDasoVars[nBanda-1],
                    self_myNBins[nBanda],
                    self_myRange[nBanda],
                    arrayRoundSubCluster,
                    False,
                )
                # histDensitCluster, histClasesCluster = np.histogram(
                #     localSubClusterArrayMultiBandaDasoVars[nBanda-1],
                #     bins=self_myNBins[nBanda],
                #     range=self_myRange[nBanda],
                #     weights=arrayRoundSubCluster,
                #     density=True
                # )
                # histDensitCluster, histClasesCluster = numba_histogram(
                #     localSubClusterArrayMultiBandaDasoVars[nBanda-1],
                #     self_myNBins[nBanda],
                #     self_myRange[nBanda],
                #     arrayRoundSubCluster,
                #     True,
                # )
            else:
                # myLog.debug(f'clidtwinb-> {nRowRaster} // {nColRaster} clusterCompleto {clusterCompleto} '
                #       f'(c) Revisar myNBins {self_myNBins[nBanda]} '
                #       f'y myRange {self_myRange[nBanda]} para banda {nBanda} '
                #       f'con sumaValores: {localSubClusterArrayMultiBandaDasoVars[nBanda-1].sum()}')
                # myLog.debug(f'{TB}Se crean histogramas con {self_myNBins[nBanda]} clases nulas')
                histNumberCluster = np.zeros(self_myNBins[nBanda], dtype=np.float32)
                histClasesCluster = np.zeros(self_myNBins[nBanda] + 1, dtype=np.float32)
                # histDensitCluster = np.zeros(self_myNBins[nBanda], dtype=np.float32)
        except:
            # myLog.warning(f'\nclidtwinb-> AVISO: error al generar histograma con el cluster: {localSubClusterArrayMultiBandaDasoVars[nBanda-1]}')
            print('\nclidtwinb-> AVISO: error al generar histograma con el cluster:', localSubClusterArrayMultiBandaDasoVars[nBanda-1])
            histNumberCluster = np.zeros(self_myNBins[nBanda], dtype=np.float32)
            histClasesCluster = np.zeros(self_myNBins[nBanda] + 1, dtype=np.float32)
            histProb01Cluster = np.zeros(self_myNBins[nBanda], dtype=np.float32)
            return (
                False,
                histNumberCluster,
                histClasesCluster,
                histProb01Cluster,
                # localClusterArrayMultiBandaDasoVarsMasked,
                # localSubClusterArrayMultiBandaDasoVarsMasked,
                listaCeldasConDasoVarsOkCluster,
                listaCeldasConDasoVarsOkSubCluster,
            )
            # sys.exit(0)

        # if localSubClusterArrayMultiBandaDasoVars[nBanda-1].sum() <= 0:
        #     myLog.debug(f'{TB}{TV}PostInCompleto+++ {histNumberCluster}')

    # Histograma con suma de clases = 1:
    # histProb01Cluster = histDensitCluster * (
    #     (self_myRange[nBanda, 1] - self_myRange[nBanda, 0])
    #     / self_myNBins[nBanda]
    # )
    if histNumberCluster.sum():
        histProb01Cluster = histNumberCluster / histNumberCluster.sum()
    else:
        histProb01Cluster = histNumberCluster
    # if mostrarPixelClusterMatch and self_LOCLverbose > 2:
    #     myLog.debug(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVars {localClusterArrayMultiBandaDasoVars[nBanda-1]}')
    #     myLog.debug(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVarsMasked {localClusterArrayMultiBandaDasoVarsMasked[nBanda-1]}')
    #     myLog.debug(f'{TB}{TV}->->histNumberCluster {histNumberCluster}')

    if histProb01Cluster is None:
        # myLog.debug(f'{TB}{TV}Cluster completo {clusterCompleto}-> rowCol: {nRowRaster} {nColRaster} banda: {nBanda} bins: {self_myNBins[nBanda]} range: {self_myRange[nBanda]}')
        # myLog.debug(f'{TB}{TV}histNumberCluster: {histNumberCluster}')
        # myLog.debug(f'{TB}{TV}histClasesCluster: {histClasesCluster}')
        # myLog.debug(f'{TB}{TV}histProb01Cluster: {type(histProb01Cluster)} shape: --- -> {histProb01Cluster}')
        print(TB, TV, 'Cluster completo', clusterCompleto, '-> rowCol:', nRowRaster, nColRaster, 'banda:', nBanda, 'bins:', self_myNBins[nBanda], 'range:', self_myRange[nBanda])
        print(TB, TV, 'histNumberCluster:', histNumberCluster)
        print(TB, TV, 'histClasesCluster:', histClasesCluster)
        # print(TB, TV, 'histProb01Cluster.shape:', histDensitCluster.shape)

    if mostrarPixelClusterMatch and self_LOCLverbose:
        if not histProb01Cluster is None:
            # myLog.debug(f'{TB}{TV}Cluster completo {clusterCompleto}-> rowCol: {nRowRaster} {nColRaster} banda: {nBanda} bins: {self_myNBins[nBanda]} range: {self_myRange[nBanda]}')
            # myLog.debug(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVars {localClusterArrayMultiBandaDasoVars[nBanda-1]}')
            # myLog.debug(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVarsMasked {localClusterArrayMultiBandaDasoVarsMasked[nBanda-1]}')
            # myLog.debug(f'{TB}{TV}->->histNumberCluster-> shape: {len(histNumberCluster)}')
            # myLog.debug(f'{TB}{TV}->->histNumberCluster {histNumberCluster}')
            # #myLog.debug(f'{TB}{TV}->->histDensitCluster-> shape: {histDensitCluster.shape}')
            # #myLog.debug(f'{TB}{TV}->->histDensitCluster {histDensitCluster}')
            # myLog.debug(f'{TB}{TV}->->histProb01Cluster-> shape: {histProb01Cluster.shape}')
            # myLog.debug(f'{TB}{TV}->->histProb01Cluster {histProb01Cluster}')
            print(TB, TV, '->->Cluster completo', clusterCompleto, '-> rowCol:', nRowRaster, nColRaster, 'banda:', nBanda, 'bins:', self_myNBins[nBanda], 'range:', self_myRange[nBanda])
            # print(TB, TV, '->->localClusterArrayMultiBandaDasoVars', localClusterArrayMultiBandaDasoVars[nBanda-1])
            # print(TB, TV, '->->localClusterArrayMultiBandaDasoVarsMasked', localClusterArrayMultiBandaDasoVarsMasked[nBanda-1])
            print(TB, TV, '->->histNumberCluster-> shape:', len(histNumberCluster))
            print(TB, TV, '->->histNumberCluster', histNumberCluster)
            # print(TB, TV, '->->histDensitCluster-> shape:', histDensitCluster.shape)
            # print(TB, TV, '->->histDensitCluster', histDensitCluster)
            print(TB, TV, '->->histProb01Cluster-> shape:', histProb01Cluster.shape)
            print(TB, TV, '->->histProb01Cluster', histProb01Cluster)
        else:
            # myLog.debug(f'{TB}{TV}Cluster completo {clusterCompleto}-> rowCol: {nRowRaster} {nColRaster} banda: {nBanda} bins: {self_myNBins[nBanda]} range: {self_myRange[nBanda]}')
            # myLog.debug(f'{TB}{TV}histNumberCluster: {histNumberCluster}')
            # myLog.debug(f'{TB}{TV}histClasesCluster: {histClasesCluster}')
            # myLog.debug(f'{TB}{TV}histProb01Cluster: {type(histProb01Cluster)} shape: --- -> {histProb01Cluster}')
            print(TB, TV, 'Cluster completo', clusterCompleto, '-> rowCol:', nRowRaster, nColRaster, 'banda:', nBanda, 'bins:', self_myNBins[nBanda], 'range:', self_myRange[nBanda])
            print(TB, TV, 'histNumberCluster:', histNumberCluster)
            print(TB, TV, 'histClasesCluster:', histClasesCluster)
            print(TB, TV, 'histProb01Cluster.shape:', histProb01Cluster.shape)

    return (
        True,
        histNumberCluster,
        histClasesCluster,
        histProb01Cluster,
        # localClusterArrayMultiBandaDasoVarsMasked,
        # localSubClusterArrayMultiBandaDasoVarsMasked,
        listaCeldasConDasoVarsOkCluster,
        listaCeldasConDasoVarsOkSubCluster,
    )


# ==============================================================================
@nb.jit(nopython=True)
def calculaClusterDasoVarsNb(
        dictArrayMultiBandaClusterDasoVars,
        nBanda,
        histNumberCluster,
        histProb01Cluster,
        self_listHistProb01,
        self_codeTipoBosquePatronMasFrecuente1,
        self_pctjTipoBosquePatronMasFrecuente1,
        self_codeTipoBosquePatronMasFrecuente2,
        self_pctjTipoBosquePatronMasFrecuente2,
        self_nInputVars,
        self_myNBins,
        self_myRange,
        # self_LOCLlistLstDasoVars,
        multiplicadorDeFueraDeRangoParaLaVariable,
        ponderacionDeLaVariable,
        nVariablesNoOk,
        tipoBosqueOk,
        # localClusterArrayMultiBandaDasoVars,
        self_outputNpDatatypeAll,
        nRowRaster=0,
        nColRaster=0,
        mostrarPixelClusterMatch=False,
        self_LOCLverbose=False,
    ):
    nInputVar = nBanda - 1
    self_nBandasRasterOutput = self_nInputVars + 2

    if nBanda == self_nBandasRasterOutput - 1:
        if mostrarPixelClusterMatch:
            # El histNumberCluster son las frecuencias del histograma
            # El histClasesCluster son los limites de las clases del histograma
            # myLog.debug(
            #     f'Histograma del cluster de Tipos de bosque (banda {nBanda}):'
            #     + f' histNumberCluster: {histNumberCluster}'
            # )
            print(
                'Histograma del cluster de Tipos de bosque (banda', nBanda, '):'
                + ' histNumberCluster:', histNumberCluster
            )
        tipoBosqueUltimoNumero = np.max(np.nonzero(histNumberCluster)[0])
        # ATENCION, esto no debiera funcionar con numba:
        #  https://stackoverflow.com/questions/23926670/numba-sorting-an-array-in-place
        #  https://github.com/numba/numba/issues/5373
        # histogramaTemp = (histNumberCluster).copy()
        # histogramaTemp.sort()
        histogramaTemp = np.sort(histNumberCluster)
        # codeTipoBosqueClusterMasFrecuente1 = (histNumberCluster).argmax(axis=0)
        codeTipoBosqueClusterMasFrecuente1 = (histNumberCluster).argmax()
        arrayPosicionTipoBosqueCluster1 = np.where(histNumberCluster == histogramaTemp[-1])
        arrayPosicionTipoBosqueCluster2 = np.where(histNumberCluster == histogramaTemp[-2])

        if mostrarPixelClusterMatch:
            # myLog.debug(
            #     f'{TB}{TV}-->>> Valor original de la celda: '
            #     f'{dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster]}; ' 
            #     f'TipoBosqueCluster MasFrecuente1: '
            #     f'{codeTipoBosqueClusterMasFrecuente1} '
            #     f'(= {arrayPosicionTipoBosqueCluster1[0][0]}) '
            #     f'MasFrecuente2: {arrayPosicionTipoBosqueCluster2[0][0]}'
            # )
            print(
                '-->>> nRowCol:', nRowRaster, nColRaster
            )
            print(
                'Valor original de la celda: ',
                # dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster], '; ',
                'TipoBosqueCluster MasFrecuente1: ',
                codeTipoBosqueClusterMasFrecuente1, '(=', arrayPosicionTipoBosqueCluster1[0][0], ') ',
                'MasFrecuente2: ', arrayPosicionTipoBosqueCluster2[0][0]
            )

        # myLog.debug(f'{TB}-> Tipo de bosque principal (cluster): {codeTipoBosqueClusterMasFrecuente1}; frecuencia: {int(round(100 * histProb01Cluster[codeTipoBosqueClusterMasFrecuente1], 0))} %')
        # myLog.debug(f'{TB}-> {arrayPosicionTipoBosqueCluster1}')

        # for contadorTB1, numPosicionTipoBosqueCluster1 in enumerate(arrayPosicionTipoBosqueCluster1[0]):
        #     myLog.debug(f'{TB}-> {numPosicionTipoBosqueCluster1}')
        #     myLog.debug(f'{TB}-> {contadorTB1} Tipo de bosque primero (cluster): {numPosicionTipoBosqueCluster1}; frecuencia: {int(round(100 * histProb01Cluster[numPosicionTipoBosqueCluster1], 0))} %')
        # if histProb01Cluster[arrayPosicionTipoBosqueCluster2[0][0]] != 0:
        #     for contadorTB2, numPosicionTipoBosqueCluster2 in enumerate(arrayPosicionTipoBosqueCluster2[0]):
        #         myLog.debug(f'{TB}-> {numPosicionTipoBosqueCluster2}')
        #         myLog.debug(f'{TB}-> {contadorTB2} Tipo de bosque segundo (cluster): {numPosicionTipoBosqueCluster2}; frecuencia: {int(round(100 * histProb01Cluster[numPosicionTipoBosqueCluster2], 0))} %')
        # else:
        #     myLog.debug(f'{TB}-> Solo hay tipo de bosque princial')

        if codeTipoBosqueClusterMasFrecuente1 != arrayPosicionTipoBosqueCluster1[0][0]:
            # myLog.critical(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoBosqueClusterMasFrecuente1} != {arrayPosicionTipoBosqueCluster1[0][0]}')
            print(TB, '-> ATENCION: revisar esto porque debe haber algun error:', codeTipoBosqueClusterMasFrecuente1, '!=', arrayPosicionTipoBosqueCluster1[0][0])
        if len(arrayPosicionTipoBosqueCluster1[0]) == 1:
            codeTipoBosqueClusterMasFrecuente2 = arrayPosicionTipoBosqueCluster2[0][0]
        else:
            codeTipoBosqueClusterMasFrecuente2 = arrayPosicionTipoBosqueCluster1[0][1]

        pctjTipoBosqueClusterMasFrecuente1 = int(round(100 * histProb01Cluster[codeTipoBosqueClusterMasFrecuente1], 0))
        pctjTipoBosqueClusterMasFrecuente2 = int(round(100 * histProb01Cluster[codeTipoBosqueClusterMasFrecuente2], 0))

        # codeTipoBosqueClusterMasFrecuente1 = (localClusterArrayMultiBandaDasoVars[nBanda-1]).flatten()[(localClusterArrayMultiBandaDasoVars[nBanda-1]).argmax()]
        # if nRowRaster >= 16 and nRowRaster <= 30 and nColRaster <= 5:
        #     myLog.debug(
        #         f'{TB} {nRowRaster} {nColRaster} nBanda {nBanda}' 
        #         f'-> codeTipoBosqueClusterMasFrecuente1: {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1})'
        #         f'-> codeTipoBosqueClusterMasFrecuente2: {codeTipoBosqueClusterMasFrecuente2} ({pctjTipoBosqueClusterMasFrecuente2})'
        #     )

        # ==================================================
        dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster] = self_outputNpDatatypeAll(codeTipoBosqueClusterMasFrecuente1)
        # ==================================================

        if mostrarPixelClusterMatch:
            if codeTipoBosqueClusterMasFrecuente1 != 0:
                # myLog.debug(f'{TB}-> nRowColRaster: {nRowRaster} {nColRaster} -> (cluster) Chequeando tipo de bosque: codeTipoBosqueClusterMasFrecuente1: {dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster]} = {codeTipoBosqueClusterMasFrecuente1}')
                # myLog.debug(f'{TB}{TV}-> Tipos de bosque mas frecuentes (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %); 2-> {codeTipoBosqueClusterMasFrecuente2} ({pctjTipoBosqueClusterMasFrecuente2} %)')
                # myLog.debug(f'{TB}{TV}-> Numero pixeles de cada tipo de bosque (cluster) ({(histNumberCluster).sum()}):\n{histNumberCluster[:tipoBosqueUltimoNumero + 1]}')
                print(TB, TV, '-> Tipos de bosque mas frecuentes (cluster): 1->', codeTipoBosqueClusterMasFrecuente1, '(', pctjTipoBosqueClusterMasFrecuente1, '%); 2->', codeTipoBosqueClusterMasFrecuente2, '(', pctjTipoBosqueClusterMasFrecuente2, '%)')
                print(TB, TV, '-> Numero pixeles de cada tipo de bosque (cluster) (', (histNumberCluster).sum(), '):')
                ##print(histNumberCluster[:tipoBosqueUltimoNumero + 1])
            else:
                # # myLog.debug(f'nRow: {nRowRaster} nCol {nColRaster} ->codeTipoBosqueClusterMasFrecuente1: {localClusterArrayMultiBandaDasoVars[nBanda-1][nRowRaster, nColRaster]} Revisar')
                # myLog.debug(f'nRow: {nRowRaster} nCol {nColRaster} -> Revisar')
                print('nRow:', nRowRaster, 'nCol', nColRaster, '-> Revisar')

        if self_pctjTipoBosquePatronMasFrecuente1 >= 70 and pctjTipoBosqueClusterMasFrecuente1 >= 70:
            if (codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente1):
                tipoBosqueOk = 10
                if mostrarPixelClusterMatch:
                    # myLog.debug(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion SI ok:')
                    print(TB, '-> Tipo de bosque principal con mas del 70 de ocupacion SI ok:')
            else:
                # binomioEspecies = str(codeTipoBosqueClusterMasFrecuente1) + '_' + str(self_codeTipoBosquePatronMasFrecuente1)
                if (
                    codeTipoBosqueClusterMasFrecuente1 < GLBLarrayProximidadInterEspecies.shape[0]
                    and self_codeTipoBosquePatronMasFrecuente1 < GLBLarrayProximidadInterEspecies.shape[1]
                ):
                    tipoBosqueOk = GLBLarrayProximidadInterEspecies[
                        codeTipoBosqueClusterMasFrecuente1,
                        self_codeTipoBosquePatronMasFrecuente1
                    ]
                else:
                    tipoBosqueOk = 0
                if mostrarPixelClusterMatch:
                    # myLog.debug(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion NO ok: {tipoBosqueOk}')
                    print(TB, '-> Tipo de bosque principal con mas del 70 de ocupacion NO ok:', tipoBosqueOk)
            if mostrarPixelClusterMatch:
                # myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (patron):  1-> {self_codeTipoBosquePatronMasFrecuente1} ({self_pctjTipoBosquePatronMasFrecuente1} %)')
                # myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %)')
                print(TB, TV, '-> Tipo mas frecuente (patron):  1->', self_codeTipoBosquePatronMasFrecuente1, '(', self_pctjTipoBosquePatronMasFrecuente1, '%)')
                print(TB, TV, '-> Tipo mas frecuente (cluster): 1->', codeTipoBosqueClusterMasFrecuente1, '(', pctjTipoBosqueClusterMasFrecuente1, '%)')
        else:
            if (
                codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente1
                and codeTipoBosqueClusterMasFrecuente2 == self_codeTipoBosquePatronMasFrecuente2
            ):
                tipoBosqueOk = 10
                if mostrarPixelClusterMatch:
                    # myLog.debug(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo SI ok:')
                    print(TB, '-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo SI ok:')
            elif (
                codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente2
                and codeTipoBosqueClusterMasFrecuente2 == self_codeTipoBosquePatronMasFrecuente1
            ):
                tipoBosqueOk = 7
                if mostrarPixelClusterMatch:
                    # myLog.debug(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo XX ok:')
                    print(TB, '-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo XX ok:')
            else:
                # binomioEspecies = str(codeTipoBosqueClusterMasFrecuente1) + '_' + str(self_codeTipoBosquePatronMasFrecuente1)
                if (
                    codeTipoBosqueClusterMasFrecuente1 < GLBLarrayProximidadInterEspecies.shape[0]
                    and self_codeTipoBosquePatronMasFrecuente1 < GLBLarrayProximidadInterEspecies.shape[1]
                ):
                    tipoBosqueOk = GLBLarrayProximidadInterEspecies[
                        codeTipoBosqueClusterMasFrecuente1,
                        self_codeTipoBosquePatronMasFrecuente1
                    ]
                else:
                    tipoBosqueOk = 0
                if mostrarPixelClusterMatch:
                    # myLog.debug(f'{TB}-> Tipos de bosque principal (menos del 70 de ocupacion) y segundo NO ok: {tipoBosqueOk}')
                    print(TB, '-> Tipos de bosque principal (menos del 70 de ocupacion) y segundo NO ok:', tipoBosqueOk)

            if mostrarPixelClusterMatch:
                # myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (patron): 1-> {self_codeTipoBosquePatronMasFrecuente1} ({self_pctjTipoBosquePatronMasFrecuente1} %)')
                # myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %)')
                # myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (patron): 2-> {self_codeTipoBosquePatronMasFrecuente2} ({self_pctjTipoBosquePatronMasFrecuente2} %)')
                # myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (cluster): 2-> {codeTipoBosqueClusterMasFrecuente2} ({pctjTipoBosqueClusterMasFrecuente2} %)')
                print(TB, TV, '-> Tipo mas frecuente (patron): 1->', self_codeTipoBosquePatronMasFrecuente1, '(', self_pctjTipoBosquePatronMasFrecuente1, '%)')
                print(TB, TV, '-> Tipo mas frecuente (cluster): 1->', codeTipoBosqueClusterMasFrecuente1, '(', pctjTipoBosqueClusterMasFrecuente1, '%)')
                print(TB, TV, '-> Tipo mas frecuente (patron): 2->', self_codeTipoBosquePatronMasFrecuente2, '(', self_pctjTipoBosquePatronMasFrecuente2, '%)')
                print(TB, TV, '-> Tipo mas frecuente (cluster): 2->', codeTipoBosqueClusterMasFrecuente2, '(', pctjTipoBosqueClusterMasFrecuente2, '%)')

    elif nInputVar >= 0 and nInputVar < self_nInputVars:
        # claveRef = str(nInputVar) + '_' + str(self_LOCLlistLstDasoVars[nInputVar][1]) + '_ref'
        # claveMin = str(nInputVar) + '_' + str(self_LOCLlistLstDasoVars[nInputVar][1]) + '_min'
        # claveMax = str(nInputVar) + '_' + str(self_LOCLlistLstDasoVars[nInputVar][1]) + '_max'
        # self_listHistProb01[nInputVar, 1, :myNBins[nBanda]] = histProb01Cluster

        todosLosRangosOk = True
        nTramosFueraDeRango = 0
        for nRango in range(len(histProb01Cluster)):
            histProb01Cluster[nRango] = round(histProb01Cluster[nRango], 3)
            limInf = nRango * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            limSup = (nRango + 1) * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            # No esta implementado el str(float) en numba, solo para int
            # https://numba.pydata.org/numba-doc/dev/reference/pysupported.html
            # miRango = str(int(limInf)) + '-' + str(int(limSup))
            if histProb01Cluster[nRango] < self_listHistProb01[nInputVar, 0, nRango]:
                todosLosRangosOk = False
                # nTramosFueraDeRango += 1
                esteTramoFueraDeRango = (
                    (self_listHistProb01[nInputVar, 0, nRango] - histProb01Cluster[nRango])
                    / (self_listHistProb01[nInputVar, 2, nRango] - self_listHistProb01[nInputVar, 0, nRango])
                )
                nTramosFueraDeRango += esteTramoFueraDeRango
                if mostrarPixelClusterMatch:
                    # myLog.debug(
                    #     f'{TB}{TV}-> {claveRef}-> nRango {nRango} ({miRango}): '
                    #     f'{histProb01Cluster[nRango]} debajo del rango '
                    #     f'{self_listHistProb01[nInputVar, 0, nRango]} '
                    #     f'- {self_listHistProb01[nInputVar, 2, nRango]};'
                    #     f' Valor de referencia: {self_listHistProb01[nInputVar, 1, nRango]} '
                    #     f'-> fuera: {esteTramoFueraDeRango}'
                    # )
                    print(
                        # TB, TV, '->', claveRef, '-> nRango', nRango, '(', miRango, '): '
                        TB, TV, 'nInputVar', nInputVar, '-> nRango', nRango, '(', limInf, '-', limSup, '): '
                        '', histProb01Cluster[nRango], 'debajo del rango '
                        '', self_listHistProb01[nInputVar, 0, nRango], ''
                        '-', self_listHistProb01[nInputVar, 2, nRango], ';'
                        ' Valor de referencia:', self_listHistProb01[nInputVar, 1, nRango], ''
                        '-> fuera:', esteTramoFueraDeRango, ''
                    )
            if histProb01Cluster[nRango] > self_listHistProb01[nInputVar, 2, nRango]:
                todosLosRangosOk = False
                # nTramosFueraDeRango += 1
                esteTramoFueraDeRango = (
                    (histProb01Cluster[nRango] - self_listHistProb01[nInputVar, 2, nRango])
                    / (self_listHistProb01[nInputVar, 2, nRango] - self_listHistProb01[nInputVar, 0, nRango])
                )
                nTramosFueraDeRango += esteTramoFueraDeRango
                if mostrarPixelClusterMatch:
                    # myLog.debug(
                    #     f'{TB}{TV}-> {claveRef}-> nRango {nRango} ({miRango}): '
                    #     f'{histProb01Cluster[nRango]} encima del rango '
                    #     f'{self_listHistProb01[nInputVar, 0, nRango]} '
                    #     f'- {self_listHistProb01[nInputVar, 2, nRango]}; '
                    #     f'Valor de referencia: {self_listHistProb01[nInputVar, 1, nRango]} '
                    #     f'-> fuera: {esteTramoFueraDeRango}')
                    print(
                        # TB, TV, '->', claveRef, '-> nRango', nRango, '(', miRango, '): '
                        TB, TV, '-> nRango', nRango, '(',  limInf, '-', limSup, '): '
                        '', histProb01Cluster[nRango], 'encima del rango '
                        '', self_listHistProb01[nInputVar, 0, nRango], ''
                        '-', self_listHistProb01[nInputVar, 2, nRango], '; '
                        'Valor de referencia:', self_listHistProb01[nInputVar, 1, nRango], ''
                        '-> fuera:', esteTramoFueraDeRango)
        if todosLosRangosOk:
            if mostrarPixelClusterMatch:
                # myLog.debug(f'{TB}{TV}-> Todos los tramos ok.')
                print(TB, TV, '-> Todos los tramos ok.')
        else:
            if mostrarPixelClusterMatch:
                # myLog.debug(
                #     '{}{}-> Cluster-> Numero de tramos fuera de rango: {} (ponderado: {:0.2f})'.format(
                #         TB, TV,
                #         nTramosFueraDeRango,
                #         nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable
                #     )
                # )
                print(
                    TB, TV, '-> Cluster-> Numero de tramos fuera de rango:', nTramosFueraDeRango,
                    '(ponderado:', nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable, ')'
                )
            if nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable >= 1:
                nVariablesNoOk += 1 * ponderacionDeLaVariable 
                if mostrarPixelClusterMatch:
                    # myLog.debug(
                    #     '{}{}{}-> Esta variable desviaciones respecto a zona de referencia (patron) con {:0.2f} puntos'.format(
                    #         TB, TV, TV,
                    #         ponderacionDeLaVariable
                    #     )
                    # )
                    print(
                        TB, TV, TV, '-> Esta variable desviaciones respecto a zona de referencia (patron) con',
                        ponderacionDeLaVariable, 'puntos'
                    )

        # ==========================================================
        dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster] = self_outputNpDatatypeAll(nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable)
        # ==========================================================
    clusterOk = True
    return (
        clusterOk,
        dictArrayMultiBandaClusterDasoVars,
        nVariablesNoOk,
        tipoBosqueOk,
    )


# ==============================================================================
@nb.jit(nopython=True)
def myDistanceMatrix(array1, array2):
    """
    Distancia uclidea entre cada par de valores de dos arrays NxP y MxP:
    N y M: numero de filas de los arrays, que son las dimensiones de la matriz de distancias
    P: numero de parametros de cada fila, sobre los que se calcula la distancia euclidea
    Attributes
    ----------
    array1 : ndarray
        Default: None
    array2 : ndarray
        Default: None
    """
    matrizDeDistancias = np.zeros(array1.shape[0] * array2.shape[0], dtype=np.float32).reshape(array1.shape[0], array2.shape[0])
    if array1.shape[1] != array2.shape[1]:
        print('clidtwinb-> ATENCION: revisar dimensiones de arrays', array1.shape, array2.shape)
        print('            Las dimensiones', array1.shape[1], 'y', array2.shape[1], 'deben ser iguales') 
        return matrizDeDistancias
    for myRow in range(array1.shape[0]):
        for myCol in range(array2.shape[0]):
            sumaCuadratica = 0
            for myVar in range(array1.shape[1]):
                sumaCuadratica += (array1[myRow, myVar] - array2[myCol, myVar]) ** 2
            mediaCuadratica = (sumaCuadratica ** 0.5) / array1.shape[1]
            matrizDeDistancias[myRow, myCol] = mediaCuadratica
    return matrizDeDistancias


# ==============================================================================
@nb.jit(nopython=True)
def myDistanceEuclidea(array1, array2):
    if array1.shape[0] != array2.shape[0]:
        print('clidtwinb-> ATENCION: revisar dimensiones de arrays para myDistanceEuclidea', array1.shape, array2.shape)
        return 0.0
    sumaCuadratica = 0
    # for myVar in range(array1.shape[1]):
    for myVar1, myVar2 in zip(array1, array2):
        # sumaCuadratica += (array1[myVar] - array2[myVar]) ** 2
        sumaCuadratica += (myVar1 - myVar2) ** 2
    mediaCuadratica = (sumaCuadratica / array1.shape[0]) ** 0.5
    return mediaCuadratica


# Uso esta implementacion de los histogramas para numba (retocada para incluir rango):
#  https://numba.pydata.org/numba-examples/examples/density_estimation/histogram/results.html
# ==============================================================================
@nb.jit(nopython=True)
def get_bin_edges(a, bins, myRange):
    bin_edges = np.zeros((bins+1,), dtype=np.float32)
    if (myRange == np.array([0.0, 0.0])).all():
        a_min = a.min()
        a_max = a.max()
    else:
        a_min = myRange[0]
        a_max = myRange[1]
    delta = (a_max - a_min) / bins
    for i in range(bin_edges.shape[0]):
        bin_edges[i] = a_min + i * delta

    bin_edges[-1] = a_max  # Avoid roundoff error on last point
    return bin_edges


# ==============================================================================
@nb.jit(nopython=True)
def compute_bin(x, bin_edges):
    # assuming uniform bins for now
    n = bin_edges.shape[0] - 1
    a_min = bin_edges[0]
    a_max = bin_edges[-1]

    # special case to mirror NumPy behavior for last bin
    if x == a_max:
        return n - 1 # a_max always in last bin

    bin = int(n * (x - a_min) / (a_max - a_min))

    if bin < 0 or bin >= n:
        return None
    else:
        return bin


# ==============================================================================
@nb.jit(nopython=True)
def numba_histogram(
        myArray,
        bins=10,
        range=None,
        weights=None,
        density=False,
    ):
    hist = np.zeros((bins,), dtype=np.float32)
    if range is None:
        range = np.zeros(2, dtype=np.float32)
        range[0] = myArray.ravel()[0]
        range[1] = myArray.ravel()[0]
        for x in myArray.flat:
            range[0] = min(x, range[0])
            range[1] = max(x, range[1])

    bin_edges = get_bin_edges(myArray, bins, range)

    if weights is None:
        for x in myArray.flat:
            myBin = compute_bin(x, bin_edges)
            if myBin is not None:
                hist[int(myBin)] += 1
    else:
        wf = weights.ravel()
        # ws = weights.sum()
        for nn, xx in enumerate(myArray.flat):
            myBin = compute_bin(xx, bin_edges)
            if myBin is not None and nn < wf.shape[0]:
                hist[int(myBin)] += wf[nn]
    if density:
        # Densidad referida a la unidad de la variable, de forma que 
        # la integral de esta funcion en el rango range, es 1.
        # La suma de los valores hist solo es uno si las clases son unitarias
        ss = hist.sum()
        for hh in nb.prange(hist.shape[0]):
            hist[hh] = (hist[hh] / ss) / ((range[1] - range[0]) / bins)

    return (hist, bin_edges)
