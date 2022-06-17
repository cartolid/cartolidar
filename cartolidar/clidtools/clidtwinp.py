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
from operator import itemgetter, attrgetter
from configparser import RawConfigParser
# import random

import numpy as np
import numpy.ma as ma
from scipy.spatial import distance_matrix
from scipy.spatial import distance as distance_hist
# from scipy.spatial import KDTree
import matplotlib.pyplot as plt
try:
    import psutil
    psutilOk = True
except:
    psutilOk = False

try:
    import gdal, ogr, gdalconst
    # import osr, gdalnumeric
    gdalOk = True
except:
    gdalOk = False

# try:
#     from osgeo import gdal, ogr, osr, gdalnumeric, gdalconst
#     gdalOk = True
# except:
#     gdalOk = False
#     sys.stderr.write('clidtwinp-> Tampoco se ha podido cargar desde la carpeta osgeo')
#     sys.exit(0)

# Recuperar la captura de errores de importacion en la version beta
# try:
if True:
    from cartolidar.clidax import clidconfig
    from cartolidar.clidax import clidraster
    from cartolidar.clidtools.clidtwcfg import GLO
# except:
#     sys.stderr.write(f'qlidtwins-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).')
#     sys.stderr.write('\t-> Se importa clidconfig desde clidtwcfg del directorio local {os.getcwd()}/clidtools.')
#     from clidax import clidconfig
#     from clidax import clidraster
#     from clidtools.clidtwcfg import GLO

myUser = clidconfig.infoUsuario()

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
myLog = logging.getLogger(thisModule)
myLog.addHandler(consoleLog)
# ==============================================================================
myLog.debug('{:_^80}'.format(''))
myLog.debug('clidtwinp-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================


# ==============================================================================
def recorrerGeneraRasterClusterPy(
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
    ):
    for nRowRaster in range(arrayBandaTipoMasa.shape[0]):
        if self.LOCLverbose:
            if nRowRaster % (arrayBandaTipoMasa.shape[0] / 10) == 0:
                if nRowRaster > 0:
                    print()
                    tiempo1 = time.time()
                    myLog.debug(f'{TB}{TV}-> Tiempo para recorrer lote (10 % de las filas del raster): {(tiempo1 - tiempo0):0.1f} segundos')
                    tiempo0 = time.time()
                if arrayBandaTipoMasa.shape[0] <= 999:
                    print(f'{TB}Recorriendo fila {nRowRaster:03d} de {arrayBandaTipoMasa.shape[0]}', end ='')
                elif arrayBandaTipoMasa.shape[0] <= 9999:
                    print(f'{TB}Recorriendo fila {nRowRaster:04d} de {arrayBandaTipoMasa.shape[0]}', end ='')
                else:
                    print(f'{TB}Recorriendo fila {nRowRaster:06d} de {arrayBandaTipoMasa.shape[0]}', end ='')
            else:
                print('.', end ='')
        coordY = arrayBandaTipoMasa.shape[0] - nRowRaster
        for nColRaster in range(arrayBandaTipoMasa.shape[1]):
            coordX = nColRaster
            if TRNS_saltarPixelsSinTipoBosque:
                if arrayBandaXinputMonoPixelAll[self.nBandasRasterOutput - 1][nRowRaster, nColRaster] == self.noDataDasoVarAll:
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
            if coordX == 156 and coordY == 35:
                mostrarPixelClusterMatch = True
            # ==============================================================

            clusterRelleno = rellenarLocalClusterPy(
                arrayBandaXinputMonoPixelAll,
                nRowRaster,
                nColRaster,
                self_LOCLradioClusterPix=self.LOCLradioClusterPix,
                self_noDataDasoVarAll=self.noDataDasoVarAll,
                self_outputNpDatatypeAll=self.outputNpDatatypeAll,
                mostrarPixelClusterMatch=mostrarPixelClusterMatch,
                contadorAvisosCluster=contadorAvisosCluster,
                self_LOCLverbose=self.LOCLverbose,
            )
            localClusterOk = clusterRelleno[0]
            contadorAvisosCluster = clusterRelleno[1]
            if not localClusterOk:
                if contadorAvisosCluster == -1:
                    sys.exit(0)
                continue
            clusterCompleto = clusterRelleno[2]
            nCeldasConDasoVarsOk = clusterRelleno[3]
            localClusterArrayMultiBandaDasoVars = clusterRelleno[4]
            localSubClusterArrayMultiBandaDasoVars = clusterRelleno[5]
            arrayBandaXMaskCluster = clusterRelleno[6]
            arrayBandaXMaskSubCluster = clusterRelleno[7]

            listaCeldasConDasoVarsOkCluster = np.zeros(
                nCeldasConDasoVarsOk * self.nBandasRasterOutput, dtype=self.outputNpDatatypeAll
            ).reshape(nCeldasConDasoVarsOk, self.nBandasRasterOutput)
            listaCeldasConDasoVarsOkSubCluster = np.zeros(
                nCeldasConDasoVarsOk * self.nBandasRasterOutput, dtype=self.outputNpDatatypeAll
            ).reshape(nCeldasConDasoVarsOk, self.nBandasRasterOutput)

            # if not nCeldasConDasoVarsOk and self.LOCLverbose > 1:
            #     # Por aqui no pasa porque ya he interceptado este problema mas arriba
            #     myLog.warning(f'{TB}{TV}-> AVISO (c): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
            #     continue

            # ==============================================================
            nVariablesNoOk = 0
            tipoBosqueOk = 0
            # myLog.debug(f'clidtwinp-> {nRowRaster} // {nColRaster} Recorriendo bandas+++')
            sumaPoderaciones = 0
            for nBanda in range(1, self.nBandasRasterOutput + 1):
                nInputVar = nBanda - 1
                sumaPoderaciones += self.LOCLlistLstDasoVars[nInputVar][6]
            if sumaPoderaciones == 0:
                myLog.warning(f'clidtwinp-> ATENCION: las ponderaciones de las variables DasoLidar son todas nulas')
                for nBanda in range(1, self.nBandasRasterOutput + 1):
                    nInputVar = nBanda - 1
                    myLog.warning(f'{TB}Banda: {nBanda} -> dasovar: {self.LOCLlistLstDasoVars[nInputVar]} (poderacion: {self.LOCLlistLstDasoVars[nInputVar][6]})')
                myLog.warning(f'{TB}-> Se asigna la misma ponderacion a todas las dasoVars.')
                sumaPoderaciones = 1
                hayPonderaciones = False
            else:
                hayPonderaciones = True
            for nBanda in range(1, self.nBandasRasterOutput + 1):
                nInputVar = nBanda - 1
                if hayPonderaciones:
                    ponderacionDeLaVariable = self.LOCLlistLstDasoVars[nInputVar][6]
                else:
                    ponderacionDeLaVariable = 1 / (self.nBandasRasterOutput - 2)
                # Factor entre 0 y 1 que modifica el numero de clases que estan fuera de rango
                # al comparar el histograma de testeo con el de referencia (patron),
                # Tras establecer para cada clase un rango admisible de frecuencias
                # alrededdor de la frecuencia del histograma de referencia para esa clase.
                # El valor 1 suma todos los "fuera de rango"; el factor 0.5 los contabiliza mitad
                multiplicadorDeFueraDeRangoParaLaVariable = ponderacionDeLaVariable / 10
                claveRef = f'{str(nInputVar)}_{self.LOCLlistLstDasoVars[nInputVar][1]}_ref'
                if mostrarPixelClusterMatch and self.LOCLverbose > 1:
                    if nInputVar >= 0 and nInputVar < self.nInputVars:
                        myLog.debug(f'{TB}-> Banda {nBanda} -> (cluster) Chequeando rangos admisibles para: {claveRef} (pondera: {ponderacionDeLaVariable})')
                    elif nBanda == self.nBandasRasterOutput - 1:
                        myLog.debug(f'{TB}-> Banda {nBanda} -> (cluster) Chequeando tipo de bosque.')

                # if clusterCompleto:
                #     localClusterArrayMultiBandaDasoVars[nBanda-1] = arrayBandaXinputMonoPixelAll[nBanda - 1][
                #         nRowClusterIni:nRowClusterFin + 1, nColClusterIni:nColClusterFin + 1
                #     ]
                #     # Sustituyo el self.noDataDasoVarAll (-9999) por self.GLBLnoDataTipoDMasa (255)
                #     # localClusterArrayMultiBandaDasoVars[nBanda-1][localClusterArrayMultiBandaDasoVars[nBanda-1] == self.noDataDasoVarAll] = self.GLBLnoDataTipoDMasa
                #     if (localClusterArrayMultiBandaDasoVars[nBanda-1] == self.noDataDasoVarAll).all():
                #         continue
                # else:
                #     for desplY in range(-self.LOCLradioClusterPix, self.LOCLradioClusterPix + 1):
                #         for desplX in range(-self.LOCLradioClusterPix, self.LOCLradioClusterPix + 1):
                #             nRowCluster = nRowRaster + desplY
                #             nColCluster = nColRaster + desplX
                #             if (
                #                 nRowCluster >= 0
                #                 and nRowCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[0]
                #                 and nColCluster >= 0
                #                 and nColCluster < (arrayBandaXinputMonoPixelAll[nBanda - 1]).shape[1]
                #             ):
                #                 try:
                #                     localClusterArrayMultiBandaDasoVars[nInputVar, self.LOCLradioClusterPix + desplY, self.LOCLradioClusterPix + desplX] = (arrayBandaXAll[nBanda - 1])[nRowCluster, nColCluster]
                #                 except:
                #                     myLog.error(f'\n-> Revisar error: {nInputVar} {self.LOCLradioClusterPix + desplY} {self.LOCLradioClusterPix + desplX}')
                #                     myLog.error(f'localClusterArrayMultiBandaDasoVars.shape: {localClusterArrayMultiBandaDasoVars.shape}')
                #                     myLog.error(f'nRowCluster, nColCluster: {nRowCluster} {nColCluster}')
                #                     sys.exit(0)
                #     localSubClusterArrayMultiBandaDasoVars[nBanda-1] = localClusterArrayMultiBandaDasoVars[nInputVar, nRowClustIni:nRowClustFin, nColClustIni:nColClustFin]
                #     # Sustituyo el self.noDataDasoVarAll (-9999) por self.GLBLnoDataTipoDMasa (255)
                #     # localSubClusterArrayMultiBandaDasoVars[localSubClusterArrayMultiBandaDasoVars == self.noDataDasoVarAll] = self.GLBLnoDataTipoDMasa
                #     if (localSubClusterArrayMultiBandaDasoVars == self.noDataDasoVarAll).all():
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
                    localClusterArrayMultiBandaDasoVarsMasked,
                    localSubClusterArrayMultiBandaDasoVarsMasked,
                    listaCeldasConDasoVarsOkCluster,
                    listaCeldasConDasoVarsOkSubCluster,
                ) = calculaHistogramasPy(
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
                    self.myNBins,
                    self.myRange,
                    self_LOCLradioClusterPix=self.LOCLradioClusterPix,
                    self_outputNpDatatypeAll=self.outputNpDatatypeAll,
                    mostrarPixelClusterMatch=mostrarPixelClusterMatch,
                    self_noDataDasoVarAll=self.noDataDasoVarAll,
                    self_LOCLverbose=self.LOCLverbose and nInputVar < self.nInputVars,
                )
                if not histogramaOk:
                    sys.exit(0)
                if len(np.nonzero(histNumberCluster)[0]) == 0:
                    if mostrarPixelClusterMatch:
                        myLog.warning(f'clidtwinp-> Aviso: el cluster de nRowColRaster: {nRowRaster} {nColRaster} nBanda: {nBanda} tiene todas celdas nulas (clusterCompleto: {clusterCompleto}).')
                    continue
                (
                    clusterOk,
                    dictArrayMultiBandaClusterDasoVars,
                    nVariablesNoOk,
                    tipoBosqueOk,
                ) = calculaClusterDasoVarsPy(
                    dictArrayMultiBandaClusterDasoVars,
                    nBanda,
                    histNumberCluster,
                    histProb01Cluster,
                    self.dictHistProb01,
                    self.codeTipoBosquePatronMasFrecuente1,
                    self.pctjTipoBosquePatronMasFrecuente1,
                    self.codeTipoBosquePatronMasFrecuente2,
                    self.pctjTipoBosquePatronMasFrecuente2,
                    self.nInputVars,
                    self.myNBins,
                    self.myRange,
                    self.LOCLlistLstDasoVars,
                    multiplicadorDeFueraDeRangoParaLaVariable,
                    ponderacionDeLaVariable,
                    nVariablesNoOk,
                    tipoBosqueOk,
                    # localClusterArrayMultiBandaDasoVars,
                    nRowRaster=nRowRaster,
                    nColRaster=nColRaster,
                    mostrarPixelClusterMatch=mostrarPixelClusterMatch,
                    self_LOCLverbose=self.LOCLverbose,
                )
                if not clusterOk:
                    sys.exit(0)

                # Se compara el histograma del patron con el del cluster
                if nInputVar < self.nInputVars:
                    # if mostrarPixelClusterMatch:
                    #     print(f'nBanda: {nBanda}, nInputVar:{nInputVar}')
                    #     print(f'{TB}histProb01Cluster:             {histProb01Cluster.shape}')
                    #     print(f'{TB}self.dictHistProb01[claveRef]: {self.dictHistProb01[claveRef].shape}')
                    for numMethod, (methodName, method) in enumerate(SCIPY_METHODS):
                        distanciaEntreHistogramas = method(self.dictHistProb01[claveRef], histProb01Cluster)
                        arrayDistanciaScipy[nInputVar, numMethod, nRowRaster, nColRaster] = distanciaEntreHistogramas
                        self.maxDistanciaScipyMono = max(arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster], self.maxDistanciaScipyMono)
                        # La ultma banda (extra) tiene la suma ponderada de las distancias
                        # if mostrarPixelClusterMatch:
                        #     myLog.debug(
                        #         f'clidtwinp-> sumando distancias-> nBanda: {nBanda}; '
                        #         f'M{numMethod} ({methodName}): {distanciaEntreHistogramas} * {ponderacionDeLaVariable} '
                        #         f'suma: {arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster]} '
                        #         f'noData: {self.GLBLnoDataDistancia}'
                        #     )
                        if arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster] == self.GLBLnoDataDistancia:
                            arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster] = distanciaEntreHistogramas * ponderacionDeLaVariable / sumaPoderaciones
                        else:
                            arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster] += distanciaEntreHistogramas * ponderacionDeLaVariable / sumaPoderaciones
                            self.maxDistanciaScipySuma = max(arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster], self.maxDistanciaScipySuma)
                        # if mostrarPixelClusterMatch:
                        #     myLog.debug(
                        #         f'suma: {arrayDistanciaScipy[-1, numMethod, nRowRaster, nColRaster]} '
                        #         f'maxDist: {self.maxDistanciaScipySuma} '
                        #     )

            # ==================================================================
            if clusterCompleto:
                # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance_matrix.html
                matrizDeDistanciasPatronCluster = distance_matrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], listaCeldasConDasoVarsOkCluster[:, :self.nInputVars], p=2) / self.nInputVars
                matrizDeDistanciasPatronPatron = distance_matrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], p=2) / self.nInputVars
                # distance_matrix y np.average no implementados en numba
                # Se sustituyen por esta otra, que es muy lenta si no se compila con numba:
                # matrizDeDistanciasPatronCluster = myDistanceMatrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], listaCeldasConDasoVarsOkCluster[:, :self.nInputVars])
                # matrizDeDistanciasPatronPatron = myDistanceMatrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars])
                # distanciaEuclideaMedia_ = np.average(matrizDeDistancias_)
                distanciaEuclideaMediaPatronCluster = np.mean(matrizDeDistanciasPatronCluster)
                distanciaEuclideaMediaPatronPatron = np.mean(matrizDeDistanciasPatronPatron)
                if mostrarPixelClusterMatch:
                    myLog.debug(f'Numero de puntos Cluster con dasoVars ok: {len(ma.compressed(localClusterArrayMultiBandaDasoVarsMasked))}')
                    myLog.debug(f'matrizDeDistanciasPatronCluster.shape: {matrizDeDistanciasPatronCluster.shape} Distancia media PatronCluster: {distanciaEuclideaMediaPatronCluster}')
                    myLog.debug(f'matrizDeDistanciasPatronCluster.shape: {matrizDeDistanciasPatronPatron.shape} Distancia media PatronPatron: {distanciaEuclideaMediaPatronPatron}')
                    # myLog.debug('clidtwinp-> Matriz de distancias:')
                    # myLog.debug(matrizDeDistanciasPatronCluster[:5,:5])
            else:
                # distance_matrix y np.average no implementados en numba
                matrizDeDistanciasPatronCluster = distance_matrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], listaCeldasConDasoVarsOkSubCluster[:, :self.nInputVars], p=2) / self.nInputVars
                matrizDeDistanciasPatronPatron = distance_matrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], p=2) / self.nInputVars
                # Funciones muy lentas si no se compilan con numba:
                # matrizDeDistanciasPatronCluster = myDistanceMatrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], listaCeldasConDasoVarsOkSubCluster[:, :self.nInputVars])
                # matrizDeDistanciasPatronPatron = myDistanceMatrix(self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars], self.listaCeldasConDasoVarsOkPatron[:, :self.nInputVars])
                # distanciaEuclideaMedia = np.average(matrizDeDistancias)
                distanciaEuclideaMediaPatronCluster = np.mean(matrizDeDistanciasPatronCluster)
                distanciaEuclideaMediaPatronPatron = np.mean(matrizDeDistanciasPatronPatron)
                if mostrarPixelClusterMatch:
                    myLog.debug(f'Numero de puntos subCluster con dasoVars ok: {len(ma.compressed(localSubClusterArrayMultiBandaDasoVarsMasked))}')
                    myLog.debug(f'matrizDeDistanciasPatronCluster.shape: {matrizDeDistanciasPatronCluster.shape} Distancia media PatronCluster: {distanciaEuclideaMediaPatronCluster}')
                    myLog.debug(f'matrizDeDistanciasPatronCluster.shape: {matrizDeDistanciasPatronPatron.shape} Distancia media PatronPatron: {distanciaEuclideaMediaPatronPatron}')
                    # myLog.debug('clidtwinp-> Matriz de distancias:')
                    # myLog.debug(matrizDeDistanciasPatronCluster[:5,:5])
            # ==================================================================
            tipoMasaOk = tipoBosqueOk >= TRNS_tipoBoscCompatible and nVariablesNoOk <= 1
            if mostrarPixelClusterMatch:
                myLog.debug(
                    f'nRowColRaster: {nRowRaster} {nColRaster}; '
                    f'coordXY: {coordX} {coordY} '
                    f'-> Resumen del match-> tipoBosqueOk: {tipoBosqueOk} '
                    f'nVariablesNoOk: {nVariablesNoOk}. '
                    f'Match: {tipoMasaOk}')
                if self.LOCLverbose == 3:
                    if not listaCeldasConDasoVarsOkSubCluster is None:
                        myLog.debug(f'listaCeldasConDasoVarsOkSubCluster (shape (nCeldasClusterOk, nBandas): {listaCeldasConDasoVarsOkSubCluster.shape}):')
                    else:
                        myLog.debug(f'listaCeldasConDasoVarsOkSubCluster:')
                    myLog.debug(listaCeldasConDasoVarsOkSubCluster)

                    if not listaCeldasConDasoVarsOkCluster is None:
                        myLog.debug(f'listaCeldasConDasoVarsOkCluster (shape: {listaCeldasConDasoVarsOkCluster.shape}):')
                    else:
                        myLog.debug(f'listaCeldasConDasoVarsOkCluster:')
                    myLog.debug(listaCeldasConDasoVarsOkCluster)

                    myLog.debug(f'listaCeldasConDasoVarsOkPatron (shape (nCeldasPatron, nBandas): {self.listaCeldasConDasoVarsOkPatron.shape}):')
                    myLog.debug(self.listaCeldasConDasoVarsOkPatron)
                    myLog.debug(f'matrizDeDistanciasPatronCluster (shape: (nCeldasPatron, nCeldasClusterOk): {matrizDeDistanciasPatronCluster.shape}):')
                    myLog.debug(matrizDeDistanciasPatronCluster)

            arrayBandaTipoBosc[nRowRaster, nColRaster] = tipoBosqueOk
            arrayBandaTipoMasa[nRowRaster, nColRaster] = tipoMasaOk
            arrayDistanciaEuclideaMedia[nRowRaster, nColRaster] = distanciaEuclideaMediaPatronCluster
            if distanciaEuclideaMediaPatronPatron:
                arrayDistanciaEuclideaRazon[nRowRaster, nColRaster] = distanciaEuclideaMediaPatronCluster / distanciaEuclideaMediaPatronPatron
            if np.ma.count(matrizDeDistanciasPatronCluster) != 0:
                arrayPctjPorcentajeDeProximidad[nRowRaster, nColRaster] = 100 * (
                    np.count_nonzero(matrizDeDistanciasPatronCluster < self.GLBLumbralMatriDist)
                    / np.ma.count(matrizDeDistanciasPatronCluster)
                )
            # else:
            #     myLog.debug(f'----> {nRowRaster} {nColRaster} {matrizDeDistanciasPatronCluster[:5,:5]}')

    return (
        True,
        contadorAvisosCluster,
        arrayBandaTipoBosc,
        arrayBandaTipoMasa,
        arrayDistanciaEuclideaMedia,
        arrayDistanciaEuclideaRazon,
        arrayPctjPorcentajeDeProximidad,
        arrayDistanciaScipy,
        self.maxDistanciaScipySuma,
        self,
    )


# ==============================================================================
def rellenarLocalClusterPy(
        arrayBandaXinputMonoPixelAll,
        nRowRaster,
        nColRaster,
        self_LOCLradioClusterPix=3,
        self_noDataDasoVarAll=-9999,
        self_outputNpDatatypeAll=None,
        mostrarPixelClusterMatch=False,
        contadorAvisosCluster=0,
        self_LOCLverbose=False,
    ):
    # self_nBandasRasterOutput = len(arrayBandaXinputMonoPixelAll)
    self_nBandasRasterOutput = arrayBandaXinputMonoPixelAll.shape[0]
    if self_outputNpDatatypeAll is None:
        self_outputNpDatatypeAll = np.float32
    ladoCluster = (self_LOCLradioClusterPix * 2) + 1
    coordY = (arrayBandaXinputMonoPixelAll[0]).shape[0] - nRowRaster
    coordX = nColRaster
    arrayBandaXMaskCluster = None
    arrayBandaXMaskSubCluster = None

    # ======================================================================
    # Array con los valores de las dasoVars en el cluster local,
    # cambia para cada el cluster local de cada pixel
    localClusterArrayMultiBandaDasoVars = np.zeros(
        (self_nBandasRasterOutput)
        * (ladoCluster ** 2),
        dtype=self_outputNpDatatypeAll
    ).reshape(
        self_nBandasRasterOutput,
        ladoCluster,
        ladoCluster
    )
    # localClusterArrayMultiBandaDasoVars.fill(0)
    localSubClusterArrayMultiBandaDasoVars = None

    # myLog.debug(f'-->>nRowRaster: {nRowRaster} nColRaster: {nColRaster}') 
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
        # myLog.debug(f'-->>nRowClusterIniFin: {nRowClusterIni} {nRowClusterFin} nColClustIniFin: {nColClusterIni} {nColClusterFin} clusterCompleto: {clusterCompleto}')
        # myLog.debug(f'-->>(arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape: {(arrayBandaXinputMonoPixelAll[self_nBandasRasterOutput - 1]).shape}')
        # myLog.debug(f'-->>nRowClustIniFin: {nRowClustIni} {nRowClustFin} nColClustIniFin: {nColClustIni} {nColClustFin}')

    # ==================================================================
    # Tengo que recorrer todas las bandas para enmascarar las celdas con alguna banda noData
    # Empiezo contando el numero de celdas con valor valido en todas las bandas
    # Una vez contadas (nCeldasConDasoVarsOk) creo el array listaCeldasConDasoVarsOkCluster
    if clusterCompleto:
        # Para contar el numero de celdas con valores distintos de noData en todas las bandas,
        # se parte de un array con todos los valores cero (arrayBandaXMaskCluster),
        # se ponen a 1 las celdas con ALGUN valor noData y, despues de recorrer 
        # todas las bandas, se cuenta el numero de celdas igual a cero.
        # Con eso, se crea un array que va a contener la lista de celdas con valor ok
        arrayBandaXMaskCluster = np.zeros((ladoCluster ** 2), dtype=np.uint8).reshape(ladoCluster, ladoCluster)
        # Recorro todas las bandas para verificar en cada celda si hay valores validos en todas las bandas
        # Calculo arrayBandaXMaskCluster y con ella enmascaro los noData al calcular el histograma de cada banda
        for nBanda in range(1, self_nBandasRasterOutput + 1):
            localClusterArrayMultiBandaDasoVars[nBanda-1] = arrayBandaXinputMonoPixelAll[nBanda - 1][
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
                )
                # continue
            arrayBandaXMaskCluster[localClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = 1

        if (arrayBandaXMaskCluster == 1).all():
            if contadorAvisosCluster == 0:
                myLog.debug('')
            if contadorAvisosCluster < 10:
                myLog.debug(f'{TB}{TV}-> AVISO (cluster): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
            elif contadorAvisosCluster == 10:
                myLog.debug(f'{TB}{TV}-> AVISO (cluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1
            localClusterOk = False
            return (
                localClusterOk,
                contadorAvisosCluster,
            )
            # continue
        elif (arrayBandaXMaskCluster != 1).sum() < MINIMO_PIXELS_POR_CLUSTER:
            if contadorAvisosCluster == 0:
                myLog.debug('')
            if contadorAvisosCluster < 10:
                myLog.debug(f'{TB}{TV}-> AVISO (cluster): {nRowRaster} {nColRaster} -> celda con pocos valores disponibles para generar cluster: {(arrayBandaXMaskCluster != 1).sum()}')
            elif contadorAvisosCluster == 10:
                myLog.debug(f'{TB}{TV}-> AVISO (cluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1

            localClusterOk = False
            return (
                localClusterOk,
                contadorAvisosCluster,
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
        localClusterArrayMultiBandaDasoVars.fill(self_noDataDasoVarAll)
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
                            myLog.error(f'\n-> Revisar error: {nInputVar} {self_LOCLradioClusterPix + desplY} {self_LOCLradioClusterPix + desplX}')
                            myLog.error(f'localClusterArrayMultiBandaDasoVars.shape: {localClusterArrayMultiBandaDasoVars.shape}')
                            myLog.error(f'nRowCluster, nColCluster: {nRowCluster} {nColCluster}')
                            sys.exit(0)
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
                )
                # continue
            arrayBandaXMaskSubCluster[localSubClusterArrayMultiBandaDasoVars[nBanda-1] == self_noDataDasoVarAll] = 1

        # Anulo el array de cluster completo prestado temporalmente para el subCLuster
        localClusterArrayMultiBandaDasoVars.fill(self_noDataDasoVarAll)

        if (arrayBandaXMaskSubCluster == 1).all():
            if contadorAvisosCluster == 0:
                myLog.debug('')
            if contadorAvisosCluster < 10:
                myLog.debug(f'{TB}{TV}-> AVISO (subcluster): {nRowRaster} {nColRaster} -> celda sin valores disponibles para generar cluster')
            elif contadorAvisosCluster == 10:
                myLog.debug(f'{TB}{TV}-> AVISO (subcluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1
            localClusterOk = False
            return (
                localClusterOk,
                contadorAvisosCluster,
            )
            # continue
        elif (arrayBandaXMaskSubCluster != 1).sum() < MINIMO_PIXELS_POR_CLUSTER:
            if contadorAvisosCluster == 0:
                myLog.debug('')
            if contadorAvisosCluster < 10:
                myLog.debug(f'{TB}{TV}-> AVISO (subcluster): {nRowRaster} {nColRaster} -> celda con pocos valores disponibles para generar cluster: {(arrayBandaXMaskSubCluster != 1).sum()}')
            elif contadorAvisosCluster == 10:
                myLog.debug(f'{TB}{TV}-> AVISO (subcluster): hay mas celdas sin valores disponibles o con pocos valores para generar cluster; no se muestran mas.')
            contadorAvisosCluster += 1
            localClusterOk = False
            return (
                localClusterOk,
                contadorAvisosCluster,
            )
            # continue

        nCeldasConDasoVarsOk = np.count_nonzero(arrayBandaXMaskSubCluster == 0)
    # ==============================================================

    if mostrarPixelClusterMatch:
        myLog.debug(f'\n-> nRowColRaster: {nRowRaster} {nColRaster}; coordXY: {coordX} {coordY}')
        myLog.debug(f'{TB}{TV}-> clusterCompleto: {clusterCompleto}')
        myLog.debug(f'{TB}{TV}-> Numero de celdas con dasoVars ok en todas las bandas: {nCeldasConDasoVarsOk}')
        myLog.debug(f'{TB}{TV}-> Celdas noData (valor=1): {arrayBandaXMaskSubCluster}')

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
def calculaHistogramasPy(
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
        self_outputNpDatatypeAll = localClusterArrayMultiBandaDasoVars.dtype
    nInputVar = nBanda - 1
    ladoCluster = (self_LOCLradioClusterPix * 2) + 1
    nRowClusterIni = nRowRaster - self_LOCLradioClusterPix
    # nRowClusterFin = nRowRaster + self_LOCLradioClusterPix
    nColClusterIni = nColRaster - self_LOCLradioClusterPix
    # nColClusterFin = nColRaster + self_LOCLradioClusterPix
    localClusterArrayMultiBandaDasoVarsMasked = None
    localSubClusterArrayMultiBandaDasoVarsMasked = None

    # myLog.debug(f'\nCluster asignado a la variable {nInputVar}, coordendas del raster -> row: {nRowRaster} col: {nColRaster} (completo: {clusterCompleto}):')
    if clusterCompleto:
        # localClusterArrayMultiBandaDasoVarsMasked = ma.masked_array(
        #     localClusterArrayMultiBandaDasoVars[nBanda-1],
        #     mask=arrayBandaXMaskCluster,
        #     dtype=self_outputNpDatatypeAll
        # )
        # listaCeldasConDasoVarsOkCluster[:, nInputVar] = ma.compressed(localClusterArrayMultiBandaDasoVarsMasked)
        localClusterArrayMultiBandaDasoVarsMasked = localClusterArrayMultiBandaDasoVars[nBanda-1][
            arrayBandaXMaskCluster == False
        ]
        listaCeldasConDasoVarsOkCluster[:, nInputVar] = np.ravel(localClusterArrayMultiBandaDasoVarsMasked)

        # Utilizo el mismo arrayRoundCluster para todos los clusters porque tienen las mismas dimensiones

        # if localClusterArrayMultiBandaDasoVars[nBanda-1].sum() <= 0:
        #     myLog.debug(f'\nclidtwinp-> +++ {nRowRaster} // {nColRaster} clusterCompleto {clusterCompleto} '
        #           f'(b) Revisar myNBins {self_myNBins[nBanda]} '
        #           f'y myRange {self_myRange[nBanda]} para banda {nBanda} '
        #           f'con sumaValores: {localClusterArrayMultiBandaDasoVars[nBanda-1].sum()}')
        #     myLog.debug('arrayRoundCluster: {arrayRoundCluster}')
        #     myLog.debug(f'{TB}Se crean histogramas con {self_myNBins[nBanda]} clases nulas')
        #     myLog.debug(localClusterArrayMultiBandaDasoVars[nBanda-1])
        #     myLog.debug(f'Masked: {localClusterArrayMultiBandaDasoVarsMasked}')
        #     myLog.debug(f'Valores ok: {np.count_nonzero(localClusterArrayMultiBandaDasoVars[nBanda-1] != self_noDataDasoVarAll)}')

        celdasConValorSiData = localClusterArrayMultiBandaDasoVars[nBanda-1][
            (arrayRoundCluster != 0)
            & (localClusterArrayMultiBandaDasoVars[nBanda-1] != self_noDataDasoVarAll)
            & (localClusterArrayMultiBandaDasoVars[nBanda-1] >= self_myRange[nBanda][0])
            & (localClusterArrayMultiBandaDasoVars[nBanda-1] < self_myRange[nBanda][1])
        ]
        if (
            (np.count_nonzero(celdasConValorSiData) > 0)
            & (self_myNBins[nBanda] > 0)
            & (self_myRange[nBanda][1] - self_myRange[nBanda][0] > 0)
        ):
            # if np.count_nonzero(celdasConValorSiData) == 0:
            #     myLog.debug(f'\nclidtwinp-> ------------> ATENCION: celda sin datos.')
            # else:
            #     myLog.debug(f'\nclidtwinp-> ------------> Celdas con datos: {np.count_nonzero(celdasConValorSiData)} {celdasConValorSiData}')
            histNumberCluster, histClasesCluster = np.histogram(
                localClusterArrayMultiBandaDasoVars[nBanda-1],
                bins=self_myNBins[nBanda],
                range=self_myRange[nBanda],
                weights=arrayRoundCluster
            )
            # Densidad: value of the probability density function at the bin, 
            # normalized such that the integral over the range is 1.
            # Note that the sum of the histogram values will not be equal to 1 unless 
            # bins of unity width are chosen; it is not a probability mass function.
            #  https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
            # histDensitCluster, histClasesCluster = np.histogram(
            #     localClusterArrayMultiBandaDasoVars[nBanda-1],
            #     bins=self_myNBins[nBanda],
            #     range=self_myRange[nBanda],
            #     weights=arrayRoundCluster,
            #     density=True
            # )
        else:
            # myLog.debug(f'clidtwinp-> {nRowRaster} // {nColRaster} clusterCompleto {clusterCompleto} '
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
        # localSubClusterArrayMultiBandaDasoVarsMasked = ma.masked_array(
        #     localSubClusterArrayMultiBandaDasoVars[nBanda-1],
        #     mask=arrayBandaXMaskSubCluster,
        #     dtype=self_outputNpDatatypeAll
        #     )
        # listaCeldasConDasoVarsOkSubCluster[:, nInputVar] = ma.compressed(localSubClusterArrayMultiBandaDasoVarsMasked)
        localSubClusterArrayMultiBandaDasoVarsMasked = localSubClusterArrayMultiBandaDasoVars[nBanda-1][
            arrayBandaXMaskSubCluster == False
        ]
        listaCeldasConDasoVarsOkSubCluster[:, nInputVar] = np.ravel(localSubClusterArrayMultiBandaDasoVarsMasked)

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
        #     myLog.debug(f'clidtwinp-> +++ {nRowRaster} // {nColRaster} clusterCompleto {clusterCompleto} '
        #           f'(c) Revisar myNBins {self_myNBins[nBanda]} '
        #           f'y myRange {self_myRange[nBanda]} para banda {nBanda} '
        #           f'con sumaValores: {localSubClusterArrayMultiBandaDasoVars[nBanda-1].sum()}')
        #     myLog.debug(f'{TB}Se crean histogramas con {self_myNBins[nBanda]} clases nulas')
        #     myLog.debug(localSubClusterArrayMultiBandaDasoVars[nBanda-1])
        #     myLog.debug(f'Masked: {localSubClusterArrayMultiBandaDasoVarsMasked}')
        #     myLog.debug(f'Valores ok: {np.count_nonzero(localSubClusterArrayMultiBandaDasoVars[nBanda-1] != self_noDataDasoVarAll)}')
        try:
            celdasConValorSiData = localSubClusterArrayMultiBandaDasoVars[nBanda-1][
                (arrayRoundSubCluster != 0)
                & (localSubClusterArrayMultiBandaDasoVars[nBanda-1] != self_noDataDasoVarAll)
                & (localSubClusterArrayMultiBandaDasoVars[nBanda-1] >= self_myRange[nBanda][0])
                & (localSubClusterArrayMultiBandaDasoVars[nBanda-1] < self_myRange[nBanda][1])
            ]
            if (
                (np.count_nonzero(celdasConValorSiData) > 0)
                & (self_myNBins[nBanda] > 0)
                & (self_myRange[nBanda][1] - self_myRange[nBanda][0] > 0)
            ):
                histNumberCluster, histClasesCluster = np.histogram(
                    localSubClusterArrayMultiBandaDasoVars[nBanda-1],
                    bins=self_myNBins[nBanda],
                    range=self_myRange[nBanda],
                    weights=arrayRoundSubCluster
                )
                # Densidad: value of the probability density function at the bin, 
                # normalized such that the integral over the range is 1.
                # Note that the sum of the histogram values will not be equal to 1 unless 
                # bins of unity width are chosen; it is not a probability mass function.
                #  https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
                # histDensitCluster, histClasesCluster = np.histogram(
                #     localSubClusterArrayMultiBandaDasoVars[nBanda-1],
                #     bins=self_myNBins[nBanda],
                #     range=self_myRange[nBanda],
                #     weights=arrayRoundSubCluster,
                #     density=True
                # )
            else:
                # myLog.debug(f'clidtwinp-> {nRowRaster} // {nColRaster} clusterCompleto {clusterCompleto} '
                #       f'(c) Revisar myNBins {self_myNBins[nBanda]} '
                #       f'y myRange {self_myRange[nBanda]} para banda {nBanda} '
                #       f'con sumaValores: {localSubClusterArrayMultiBandaDasoVars[nBanda-1].sum()}')
                # myLog.debug(f'{TB}Se crean histogramas con {self_myNBins[nBanda]} clases nulas')
                histNumberCluster = np.zeros(self_myNBins[nBanda], dtype=np.float32)
                histClasesCluster = np.zeros(self_myNBins[nBanda] + 1, dtype=np.float32)
                # histDensitCluster = np.zeros(self_myNBins[nBanda], dtype=np.float32)
        except:
            myLog.warning(f'\nclidtwinp-> AVISO: error al generar histograma con el cluster: {localSubClusterArrayMultiBandaDasoVars[nBanda-1]}')
            sys.exit(0)

        # if localSubClusterArrayMultiBandaDasoVars[nBanda-1].sum() <= 0:
        #     myLog.debug(f'{TB}{TV}PostInCompleto+++ {histNumberCluster}')

    # Histograma con suma de clases = 1:
    # histProb01Cluster = np.array(histDensitCluster) * (
    #     (self_myRange[nBanda][1] - self_myRange[nBanda][0])
    #     / self_myNBins[nBanda]
    #     )
    # histProb01Cluster = np.array(histNumberCluster) / np.array(histNumberCluster).sum()
    if histNumberCluster.sum():
        histProb01Cluster = histNumberCluster / histNumberCluster.sum()
    else:
        histProb01Cluster = histNumberCluster
    # if mostrarPixelClusterMatch and self_LOCLverbose > 2:
    #     myLog.debug(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVars {localClusterArrayMultiBandaDasoVars[nBanda-1]}')
    #     myLog.debug(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVarsMasked {localClusterArrayMultiBandaDasoVarsMasked[nBanda-1]}')
    #     myLog.debug(f'{TB}{TV}->->histNumberCluster {histNumberCluster}')

    if histProb01Cluster is None:
        myLog.debug(f'{TB}{TV}Cluster completo {clusterCompleto}-> rowCol: {nRowRaster} {nColRaster} banda: {nBanda} bins: {self_myNBins[nBanda]} range: {self_myRange[nBanda]}')
        myLog.debug(f'{TB}{TV}histNumberCluster: {histNumberCluster}')
        myLog.debug(f'{TB}{TV}histClasesCluster: {histClasesCluster}')
        myLog.debug(f'{TB}{TV}histProb01Cluster: {type(histProb01Cluster)} shape: --- -> {histProb01Cluster}')

    if mostrarPixelClusterMatch and self_LOCLverbose:
        if not histProb01Cluster is None:
            myLog.debug(f'{TB}{TV}Cluster completo {clusterCompleto}-> rowCol: {nRowRaster} {nColRaster} banda: {nBanda} bins: {self_myNBins[nBanda]} range: {self_myRange[nBanda]}')
            myLog.debug(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVars {localClusterArrayMultiBandaDasoVars[nBanda-1]}')
            myLog.debug(f'{TB}{TV}->->localClusterArrayMultiBandaDasoVarsMasked {localClusterArrayMultiBandaDasoVarsMasked[nBanda-1]}')
            myLog.debug(f'{TB}{TV}->->histNumberCluster-> shape: {len(histNumberCluster)}')
            myLog.debug(f'{TB}{TV}->->histNumberCluster {histNumberCluster}')
            # myLog.debug(f'{TB}{TV}->->histDensitCluster-> shape: {histDensitCluster.shape}')
            # myLog.debug(f'{TB}{TV}->->histDensitCluster {histDensitCluster}')
            myLog.debug(f'{TB}{TV}->->histProb01Cluster-> shape: {histProb01Cluster.shape}')
            myLog.debug(f'{TB}{TV}->->histProb01Cluster {histProb01Cluster}')
        else:
            myLog.debug(f'{TB}{TV}Cluster completo {clusterCompleto}-> rowCol: {nRowRaster} {nColRaster} banda: {nBanda} bins: {self_myNBins[nBanda]} range: {self_myRange[nBanda]}')
            myLog.debug(f'{TB}{TV}histNumberCluster: {histNumberCluster}')
            myLog.debug(f'{TB}{TV}histClasesCluster: {histClasesCluster}')
            myLog.debug(f'{TB}{TV}histProb01Cluster: {type(histProb01Cluster)} shape: --- -> {histProb01Cluster}')

    return (
        True,
        histNumberCluster,
        histClasesCluster,
        histProb01Cluster,
        localClusterArrayMultiBandaDasoVarsMasked,
        localSubClusterArrayMultiBandaDasoVarsMasked,
        listaCeldasConDasoVarsOkCluster,
        listaCeldasConDasoVarsOkSubCluster,
    )


# ==============================================================================
def calculaClusterDasoVarsPy(
        dictArrayMultiBandaClusterDasoVars,
        nBanda,
        histNumberCluster,
        histProb01Cluster,
        self_dictHistProb01,
        self_codeTipoBosquePatronMasFrecuente1,
        self_pctjTipoBosquePatronMasFrecuente1,
        self_codeTipoBosquePatronMasFrecuente2,
        self_pctjTipoBosquePatronMasFrecuente2,
        self_nInputVars,
        self_myNBins,
        self_myRange,
        self_LOCLlistLstDasoVars,
        multiplicadorDeFueraDeRangoParaLaVariable,
        ponderacionDeLaVariable,
        nVariablesNoOk,
        tipoBosqueOk,
        # localClusterArrayMultiBandaDasoVars,
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
            myLog.debug(
                f'Histograma del cluster de Tipos de bosque (banda {nBanda}):'
                + f' histNumberCluster: {histNumberCluster}'
            )
        try:
            tipoBosqueUltimoNumero = np.max(np.nonzero(histNumberCluster)[0])
        except:
            tipoBosqueUltimoNumero = 0
        histogramaTemp = (histNumberCluster).copy()
        histogramaTemp.sort()
        codeTipoBosqueClusterMasFrecuente1 = (histNumberCluster).argmax(axis=0)
        arrayPosicionTipoBosqueCluster1 = np.where(histNumberCluster == histogramaTemp[-1])
        arrayPosicionTipoBosqueCluster2 = np.where(histNumberCluster == histogramaTemp[-2])

        if mostrarPixelClusterMatch:
            myLog.debug(
                f'-->>> nRowCol: {nRowRaster} {nColRaster}'
            )
            myLog.debug(
                f'Valor original de la celda: '
                f'{dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster]}; ' 
                f'TipoBosqueCluster MasFrecuente1: '
                f'{codeTipoBosqueClusterMasFrecuente1} '
                f'(= {arrayPosicionTipoBosqueCluster1[0][0]}) '
                f'MasFrecuente2: {arrayPosicionTipoBosqueCluster2[0][0]}'
            )
            # quit()
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
            myLog.critical(f'{TB}-> ATENCION: revisar esto porque debe haber algun error: {codeTipoBosqueClusterMasFrecuente1} != {arrayPosicionTipoBosqueCluster1[0][0]}')
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
        dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster] = codeTipoBosqueClusterMasFrecuente1
        # ==================================================

        if mostrarPixelClusterMatch:
            if codeTipoBosqueClusterMasFrecuente1 != 0:
                # myLog.debug(f'{TB}-> nRowColRaster: {nRowRaster} {nColRaster} -> (cluster) Chequeando tipo de bosque: codeTipoBosqueClusterMasFrecuente1: {dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster]} = {codeTipoBosqueClusterMasFrecuente1}')
                myLog.debug(f'{TB}{TV}-> Tipos de bosque mas frecuentes (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %); 2-> {codeTipoBosqueClusterMasFrecuente2} ({pctjTipoBosqueClusterMasFrecuente2} %)')
                myLog.debug(f'{TB}{TV}-> Numero pixeles de cada tipo de bosque (cluster) ({(histNumberCluster).sum()}):\n{histNumberCluster[:tipoBosqueUltimoNumero + 1]}')
            else:
                # myLog.debug(f'nRow: {nRowRaster} nCol {nColRaster} ->codeTipoBosqueClusterMasFrecuente1: {localClusterArrayMultiBandaDasoVars[nBanda-1][nRowRaster, nColRaster]} Revisar')
                myLog.debug(f'nRow: {nRowRaster} nCol {nColRaster} -> Revisar')

        if self_pctjTipoBosquePatronMasFrecuente1 >= 70 and pctjTipoBosqueClusterMasFrecuente1 >= 70:
            if (codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente1):
                tipoBosqueOk = 10
                if mostrarPixelClusterMatch:
                    myLog.debug(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion SI ok:')
            else:
                binomioEspecies = f'{codeTipoBosqueClusterMasFrecuente1}_{self_codeTipoBosquePatronMasFrecuente1}'
                if binomioEspecies in (GLO.GLBLdictProximidadInterEspecies).keys():
                    tipoBosqueOk = GLO.GLBLdictProximidadInterEspecies[binomioEspecies]
                else:
                    tipoBosqueOk = 0
                if mostrarPixelClusterMatch:
                    myLog.debug(f'{TB}-> Tipo de bosque principal con mas del 70 de ocupacion NO ok: {tipoBosqueOk}')
            if mostrarPixelClusterMatch:
                myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (patron):  1-> {self_codeTipoBosquePatronMasFrecuente1} ({self_pctjTipoBosquePatronMasFrecuente1} %)')
                myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %)')
        else:
            if (
                codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente1
                and codeTipoBosqueClusterMasFrecuente2 == self_codeTipoBosquePatronMasFrecuente2
            ):
                tipoBosqueOk = 10
                if mostrarPixelClusterMatch:
                    myLog.debug(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo SI ok:')
            elif (
                codeTipoBosqueClusterMasFrecuente1 == self_codeTipoBosquePatronMasFrecuente2
                and codeTipoBosqueClusterMasFrecuente2 == self_codeTipoBosquePatronMasFrecuente1
            ):
                tipoBosqueOk = 7
                if mostrarPixelClusterMatch:
                    myLog.debug(f'{TB}-> Tipo de bosque principal (menos del 70 de ocupacion) y segundo XX ok:')
            else:
                binomioEspecies = f'{codeTipoBosqueClusterMasFrecuente1}_{self_codeTipoBosquePatronMasFrecuente1}'
                if binomioEspecies in (GLO.GLBLdictProximidadInterEspecies).keys():
                    tipoBosqueOk = GLO.GLBLdictProximidadInterEspecies[binomioEspecies] - 1
                else:
                    tipoBosqueOk = 0
                if mostrarPixelClusterMatch:
                    myLog.debug(f'{TB}-> Tipos de bosque principal (menos del 70 de ocupacion) y segundo NO ok: {tipoBosqueOk}')

            if mostrarPixelClusterMatch:
                myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (patron): 1-> {self_codeTipoBosquePatronMasFrecuente1} ({self_pctjTipoBosquePatronMasFrecuente1} %)')
                myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (cluster): 1-> {codeTipoBosqueClusterMasFrecuente1} ({pctjTipoBosqueClusterMasFrecuente1} %)')
                myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (patron): 2-> {self_codeTipoBosquePatronMasFrecuente2} ({self_pctjTipoBosquePatronMasFrecuente2} %)')
                myLog.debug(f'{TB}{TV}-> Tipo mas frecuente (cluster): 2-> {codeTipoBosqueClusterMasFrecuente2} ({pctjTipoBosqueClusterMasFrecuente2} %)')

    elif nInputVar >= 0 and nInputVar < self_nInputVars:
        claveRef = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_ref'
        claveMin = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_min'
        claveMax = f'{str(nInputVar)}_{self_LOCLlistLstDasoVars[nInputVar][1]}_max'
        # self_dictHistProb01[claveRef] = histProb01Cluster

        todosLosRangosOk = True
        nTramosFueraDeRango = 0
        for nRango in range(len(histProb01Cluster)):
            histProb01Cluster[nRango] = round(histProb01Cluster[nRango], 3)
            limInf = nRango * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            limSup = (nRango + 1) * (self_myRange[nBanda][1] - self_myRange[nBanda][0]) / self_myNBins[nBanda]
            miRango = f'{limInf}-{limSup}'
            if histProb01Cluster[nRango] < self_dictHistProb01[claveMin][nRango]:
                todosLosRangosOk = False
                # nTramosFueraDeRango += 1
                esteTramoFueraDeRango = (
                    (self_dictHistProb01[claveMin][nRango] - histProb01Cluster[nRango])
                    / (self_dictHistProb01[claveMax][nRango] - self_dictHistProb01[claveMin][nRango])
                )
                nTramosFueraDeRango += esteTramoFueraDeRango
                if mostrarPixelClusterMatch:
                    myLog.debug(
                        f'{TB}{TV}-> {claveRef}-> nRango {nRango} ({miRango}): '
                        f'{histProb01Cluster[nRango]} debajo del rango '
                        f'{self_dictHistProb01[claveMin][nRango]} '
                        f'- {self_dictHistProb01[claveMax][nRango]};'
                        f' Valor de referencia: {self_dictHistProb01[claveRef][nRango]} '
                        f'-> fuera: {esteTramoFueraDeRango}'
                    )
            if histProb01Cluster[nRango] > self_dictHistProb01[claveMax][nRango]:
                todosLosRangosOk = False
                # nTramosFueraDeRango += 1
                esteTramoFueraDeRango = (
                    (histProb01Cluster[nRango] - self_dictHistProb01[claveMax][nRango])
                    / (self_dictHistProb01[claveMax][nRango] - self_dictHistProb01[claveMin][nRango])
                )
                nTramosFueraDeRango += esteTramoFueraDeRango
                if mostrarPixelClusterMatch:
                    myLog.debug(
                        f'{TB}{TV}-> {claveRef}-> nRango {nRango} ({miRango}): '
                        f'{histProb01Cluster[nRango]} encima del rango '
                        f'{self_dictHistProb01[claveMin][nRango]} '
                        f'- {self_dictHistProb01[claveMax][nRango]}; '
                        f'Valor de referencia: {self_dictHistProb01[claveRef][nRango]} '
                        f'-> fuera: {esteTramoFueraDeRango}')
        if todosLosRangosOk:
            if mostrarPixelClusterMatch:
                myLog.debug(f'{TB}{TV}-> Todos los tramos ok.')
        else:
            if mostrarPixelClusterMatch:
                myLog.debug(
                    '{}{}-> Cluster-> Numero de tramos fuera de rango: {} (ponderado: {:0.2f})'.format(
                        TB, TV,
                        nTramosFueraDeRango,
                        nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable
                    )
                )
            if nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable >= 1:
                nVariablesNoOk += 1 * ponderacionDeLaVariable 
                if mostrarPixelClusterMatch:
                    myLog.debug(
                        '{}{}{}-> Esta variable desviaciones respecto a zona de referencia (patron) con {:0.2f} puntos'.format(
                            TB, TV, TV,
                            ponderacionDeLaVariable
                        )
                    )

        # ==========================================================
        dictArrayMultiBandaClusterDasoVars[nBanda][nRowRaster, nColRaster] = nTramosFueraDeRango * multiplicadorDeFueraDeRangoParaLaVariable
        # ==========================================================
    clusterOk = True
    return (
        clusterOk,
        dictArrayMultiBandaClusterDasoVars,
        nVariablesNoOk,
        tipoBosqueOk,
    )


# ==============================================================================
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
        print('clidtwinp-> ATENCION: revisar dimensiones de arrays', array1.shape, array2.shape)
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
def myDistanceEuclidea(array1, array2):
    if array1.shape[0] != array2.shape[0]:
        print('clidtwinp-> ATENCION: revisar dimensiones de arrays para myDistanceEuclidea', array1.shape, array2.shape)
        return 0.0
    sumaCuadratica = 0
    # for myVar in range(array1.shape[1]):
    for myVar1, myVar2 in zip(array1, array2):
        # sumaCuadratica += (array1[myVar] - array2[myVar]) ** 2
        sumaCuadratica += (myVar1 - myVar2) ** 2
    mediaCuadratica = (sumaCuadratica / array1.shape[0]) ** 0.5
    return mediaCuadratica

    
