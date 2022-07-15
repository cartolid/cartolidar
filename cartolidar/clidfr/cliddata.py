'''
Created on 1 oct. 2019

@author: benmarjo
'''
from __future__ import division, print_function

import os
import sys
# import pathlib
import time
# import datetime
# import types
# import csv
# import re
import math
# import random
# import platform
import inspect
# import traceback
# import subprocess
# import argparse
# from configparser import RawConfigParser
# import logging
import importlib
import importlib.util
# import struct
# import shutil
# import gc

# Paquetes de terceros
import numpy as np

spec = importlib.util.find_spec('cartolidar')
if not spec is None:
    from cartolidar.clidax import clidaux
    # from cartolidar.clidax.clidconfig import GLO
    from cartolidar.clidax import clidconfig
    from cartolidar.clidfr import clidhead
    from cartolidar.clidnb import clidnaux
    try:
        from cartolidar.clidnb import clidnv0
    except:
        print('cliddata-> No se importan clidnv0 por no estar disponible todavia')
else:
    try:
        from cartolidar.clidax import clidaux
        # from cartolidar.clidax.clidconfig import GLO
        from cartolidar.clidax import clidconfig
        from cartolidar.clidfr import clidhead
        from cartolidar.clidnb import clidnaux
    except:
        sys.stderr.write(f'cliddata-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).')
        sys.stderr.write('\t-> Se importan paquetes de cartolidar desde cliddata del directorio local {os.getcwd()}/....')
        from clidax import clidaux
        # from clidax.clidconfig import GLO
        from clidax import clidconfig
        from clidfr import clidhead
        from clidnb import clidnaux
    try:
        from cartolidar.clidnb import clidnv0
    except:
        print('cliddata-> No se importan clidnv0 por no estar disponible todavia')

# ==============================================================================
# ========================== Variables globales ================================
# ==============================================================================
# TB = '\t'
TB = ' ' * 11
TV = ' ' * 3
TW = ' ' * 2
# ==============================================================================

configVarsDict = clidconfig.leerCambiarVariablesGlobales(inspect_stack=inspect.stack())
GLO = clidconfig.VariablesGlobales(configVarsDict)

if GLO.GLBLverbose:
    print('->->Cargando cliddata')
    clidaux.showCallingModules(inspect_stack=inspect.stack())

GLBNsubCeldasPorCelda = int(GLO.GLBLmetrosCelda / GLO.GLBLmetrosSubCelda)
# GLBNceldillasPorCelda = int(GLO.GLBLmetrosCelda / GLO.GLBLmetrosCeldilla)

if (
    GLO.GLBLacumularPuntosEnNpzParaEntrenamientoFuturo
    or GLO.GLBLentrenarNeuronalNetworkConTF
    or GLO.GLBLhacerInferenciaParaTodosLosPuntos
):
    GLBNmuestreoAcumulativoOEntrenamientoOInferencia = True
else:
    GLBNmuestreoAcumulativoOEntrenamientoOInferencia = False

class LasData(object):
    """
    Class with raw readed points from lasFile
    """

    # ==========================================================================
    def __init__(self, myLasHead):
        """
        Constructor
        """
        self.myLasHead = myLasHead
        self.nCeldasX = myLasHead.nCeldasX
        self.nCeldasY = myLasHead.nCeldasY
        # self.nPtosAleer = nPtosAleer
        # self.sampleLas = sampleLas
        # self.pointreclen = myLasHead.pointreclen


    # ==========================================================================
    def readLasData(self, byREFAlmacenarPuntosComoNumpyDtype=False, entrenamiento=False):
        """
        Opens lasFile (self.infile) and read dataPoints (after header) and stores in self.ficheroCompletoEnLaRAM
        This variable is different depending on GLO.GLBLalmacenarPuntosComoNumpyDtype:
            if True: Also creates self.numPuntosCargadosEnLaRAM
        """
        # ooooooooooooooooo Paso el contenido a memoria RAM ooooooooooooooooooooo
        # print('---------->clidnat-> Leyendo:', self.myLasHead.infileConRuta)
        try:
            self.infile = open(self.myLasHead.infileConRuta, 'rb')
        except:
            print('cliddata-> Error reading %s' % (self.myLasHead.infileConRuta))
            sys.exit()
        self.infile.seek(self.myLasHead.headDict['offset'])

        if GLO.GLBLalmacenarPuntosComoNumpyDtype or byREFAlmacenarPuntosComoNumpyDtype:
            # print( 'cliddata-> Reading dataPoints with np.dtype() to store them in a ndArray' )
            # print( 'cliddata-> (Just the number of points indicated in head of lasFile (file could have more points)' )
            # TODO: Check also np.savez()
            # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
            try:
                self.ficheroCompletoEnLaRAM = np.fromfile(
                    self.infile,
                    dtype=self.myLasHead.formatoDtypePointFormatXXNotacionNpDtype,
                    count=self.myLasHead.numptrecords
                )
            except:
                clidaux.memoriaRam('4b')
                print('\ncliddata-> Error reading dataPoints with np.dtype()')
                print('np.dtype():', self.myLasHead.formatoDtypePointFormatXXNotacionNpDtype)
                quit()
            # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
            self.numPuntosCargadosEnLaRAM = len(self.ficheroCompletoEnLaRAM)
            if self.numPuntosCargadosEnLaRAM != self.nPtosAleer:
                print('cliddata-> Number of points to read different to number of points in lasFile')
                print('cliddata-> Number of points in lasFile: %i' % self.numPuntosCargadosEnLaRAM)
                print('cliddata-> Number of points to read:    %i (one of every %i)' % (self.nPtosAleer, self.sampleLas))
        else:
            print(
                'cliddata-> Reading dataPoints loading bytes in lasFile in RAM (after head offset) and storing points with Append in corresponding cell (no np.dtype())'
            )
            print('cliddata-> It is read just the number of points indicated in head of lasFile (there could be more)')
            try:
                self.ficheroCompletoEnLaRAM = self.infile.read(self.myLasHead.pointreclen * self.myLasHead.numptrecords)
            except:
                print('cliddata-> Error reading with self.infile.read()')
                clidaux.memoriaRam('4b')
                self.ficheroCompletoEnLaRAM = None

            print('cliddata-> Tipo de objeto self.ficheroCompletoEnLaRAM:', type(self.ficheroCompletoEnLaRAM))
            self.numPuntosCargadosEnLaRAM = len(self.ficheroCompletoEnLaRAM) / self.myLasHead.pointreclen

        self.infile.close()


    # ==========================================================================
    def leerLasDataLazLas(
            self,
            infileRgxConRuta,
            fileCoordYear,
            LCLordenColoresInput,
        ):
        TRNShuso29 = clidaux.chequearHuso29(fileCoordYear)
        clidaux.printMsg(f'\n{"":_^80}')
        clidaux.printMsg(f'{" Fase previa-1 ":_^80}')
        clidaux.printMsg(f'{" Lectura del fichero lidar (lasFile o lazFile) ":_^80}')
        clidaux.printMsg(f'{"":=^80}')
        if GLO.GLBLverbose:
            clidaux.printMsg(f'cliddata.{fileCoordYear}-> Leyendo el contenido de {self.myLasHead.infileConRuta}')
        if infileRgxConRuta[-4:].lower() == '.las':
            # clidaux.printMsg('\n---------------->cliddata-> infileLasConRuta_ (rgx): {}'.format(infileRgxConRuta))
            self.readLasData()
        elif infileRgxConRuta[-4:].lower() == '.laz':
            if GLO.GLBLdescomprimirLazEnMemoria:
                # ==============================================================
                lasDataMem = clidaux.descomprimeLaz(
                    infileRgxConRuta,
                    descomprimirLazEnMemoria=GLO.GLBLdescomprimirLazEnMemoria
                )
                # clidaux.printMsg('\ncliddata-> lasDataMem: {} {}'.format(type(lasDataMem), len(lasDataMem)))
                # ==============================================================
                if GLO.GLBLverbose:
                    clidaux.printMsg('cliddata.{}-> Leyendo la cabecera del fichero laz descomprimido en memoria'.format(fileCoordYear))

                # ATENCION: Recalculo las propiedades de la cabecera con el fichero descomprimido en memoria
                # porque el fichero comprimido tiene un offset de 335 en lugar de 229 por el VLR de laszip 
                # Se puede abreviar a cambiar solo esa propiedad
                # clidaux.printMsg('\n---------------->cliddata-> infileRgxConRuta10:       {}'.format(infileRgxConRuta))
                # clidaux.printMsg('\n---------------->cliddata-> lasDataMem:               {} {}'.format(type(lasDataMem), len(lasDataMem)))
                self.myLasHead = clidhead.LasHeadClass(
                    infileRgxConRuta,
                    lasDataMem=lasDataMem,
                    metersBlock=GLO.GLBLmetrosBloque,
                    metersCell=GLO.GLBLmetrosCelda,
                    LCLordenColoresInput=LCLordenColoresInput,
                    verbose=GLO.GLBLverbose,
                    TRNShuso29=TRNShuso29,
                    )
                if not self.myLasHead.readOk:
                    return

                if (
                    (len(lasDataMem) - self.myLasHead.headDict['offset']) / self.myLasHead.pointreclen != self.myLasHead.numptrecords
                ):
                    clidaux.printMsg('\ncliddata-> ATENCION: las cuentas NO cuadran con el offset:')
                    clidaux.printMsg(
                        '\t-> len(lasDataMem): {}; Calculado por el num. de puntos: {}; Diferencia: {}'.format(
                            len(lasDataMem),
                            (self.myLasHead.headDict['offset'] + (self.myLasHead.pointreclen * self.myLasHead.numptrecords)),
                            len(lasDataMem) - (self.myLasHead.headDict['offset'] + (self.myLasHead.pointreclen * self.myLasHead.numptrecords))
                        )
                    )

                if GLO.GLBLverbose:
                    clidaux.printMsg(f'cliddata.{fileCoordYear}-> Cargando en un ndArray los puntos del fichero descomprimido en memoria')
                    clidaux.printMsg(f'{TB}-> A. len(lasDataMem): {len(lasDataMem)}')
                    clidaux.printMsg(f'{TB}-> B. offset:          {self.myLasHead.headDict["offset"]}')
                    clidaux.printMsg(f'{TB}-> C. pointreclen:     {self.myLasHead.pointreclen}')
                    clidaux.printMsg(f'{TB}-> D. numptrecords:    {self.myLasHead.numptrecords}')
                    clidaux.printMsg(f'{TB}-> (A - B) / C:        {(len(lasDataMem) - self.myLasHead.headDict["offset"]) / self.myLasHead.pointreclen}')
                # https://numpy.org/doc/stable/reference/generated/numpy.frombuffer.html

                try:
                    if self.myLasHead.numptrecords <= len(lasDataMem):
                        self.ficheroCompletoEnLaRAM = np.frombuffer(
                            lasDataMem,
                            dtype=self.myLasHead.formatoDtypePointFormatXXNotacionNpDtype,
                            count=self.myLasHead.numptrecords,
                            offset=self.myLasHead.headDict['offset'])
                    else:
                        clidaux.printMsg(
                            'cliddata-> ATENCION: revisar por que lasDataMem tiene menos registros ({}) que los previstos: {}; offset: {}'.format(
                                len(lasDataMem),
                                self.myLasHead.numptrecords,
                                self.myLasHead.headDict['offset']
                            )
                        )
                        self.ficheroCompletoEnLaRAM = np.frombuffer(
                            lasDataMem,
                            dtype=self.myLasHead.formatoDtypePointFormatXXNotacionNpDtype,
                            count=self.myLasHead.numptrecords,
                            offset=self.myLasHead.headDict['offset'])
                except:
                    clidaux.printMsg(
                        'cliddata-> Error en frombuffer() lasDataMem: {}; dtype: {}; count: {}; offset: {}'.format(
                            len(lasDataMem),
                            self.myLasHead.formatoDtypePointFormatXXNotacionNpDtype,
                            self.myLasHead.numptrecords,
                            self.myLasHead.headDict['offset'],
                        )
                    )
                    self.myLasHead.readOk = False
                    return
                    # sys.exit(0)
                # ==================================================================
                self.numPuntosCargadosEnLaRAM = len(self.ficheroCompletoEnLaRAM)
                # ==================================================================
                TRNSchequearUsoDeBytesIO = False
                if TRNSchequearUsoDeBytesIO:
                    # Alternativa descartada: io.BytesIO()
                    # https://docs.python.org/3/library/io.html#in-memory-streams
                    #  It is also possible to use a str or bytes-like object as a file for both reading and writing
                    #    https://docs.python.org/3/glossary.html#term-bytes-like-object
                    #      This includes all bytes, bytearray, and array.array objects, as well as many common memoryview objects.
                    #      Bytes-like objects can be used for various operations that work with binary data;
                    #      these include compression, saving to a binary file, and sending over a socket.
                    #  BytesIO can be used like a file opened in binary mode. Both provide full read-write capabilities with random access.
                    #    https://docs.python.org/3/library/io.html#io.BytesIO
                    import io
                    lasDataBinaryStream = io.BytesIO(lasDataMem)
                    clidaux.printMsg('cliddata-> lasDataBinaryStream: {}'.format(type(lasDataBinaryStream)))
                    # clidaux.printMsg(dir(lasDataBinaryStream)) # 'close', 'closed', 'detach', 'fileno', 'flush', 'getbuffer', 'getvalue', 'isatty', 'read', 'read1', 'readable', 'readinto', 'readinto1', 'readline', 'readlines', 'seek', 'seekable', 'tell', 'truncate', 'writable', 'write', 'writelines']
                    if False:
                        miCabecera = lasDataBinaryStream.read(227)
                        clidaux.printMsg('cliddata-> miCabecera leida con read(<class "_io.BytesIO"">): {}'.format(type(miCabecera), miCabecera))
        
                    # self.ficheroCompletoEnLaRAM = np.fromfile(
                    #     lasDataBinaryStream,
                    #     dtype=self.myLasHead.formatoDtypePointFormatXXNotacionNpDtype,
                    #     count=self.myLasHead.numptrecords,
                    #     offset=self.myLasHead.headDict['offset']) # io.UnsupportedOperation: fileno
                # ==================================================================
    
                # ==================================================================
                TRNSchequearUsoDeMemoryview = False
                if TRNSchequearUsoDeMemoryview:
                    # Alternativa si necesitara un comportamiento distinto a bytes: memoryview()
                    # https://docs.python.org/dev/library/stdtypes.html#memoryview
                    # https://stackoverflow.com/questions/18655648/what-exactly-is-the-point-of-memoryview-in-python
                    lasDataView = memoryview(lasDataMem)
                    lasDataViewPoints = lasDataView[self.myLasHead.headDict['offset']:]
                    totalPointBytes = self.myLasHead.pointreclen * self.myLasHead.numptrecords
                    clidaux.printMsg('\n________________________________________________________________________________')
                    clidaux.printMsg('ooooooooooooooooo Propiedades de lasDataMem y lasDataView oooooooooooooooooooooo')
                    clidaux.printMsg('cliddata-> lasDataMem:                {}\t{}'.format(type(lasDataMem), len(lasDataMem))) # <class 'bytes'>
                    clidaux.printMsg('cliddata-> lasDataView:               {}\t{}'.format(type(lasDataView), len(lasDataView))) # <class 'memoryview'>
                    clidaux.printMsg('cliddata-> lasDataView == lasDataMem: {}'.format(lasDataView == lasDataMem)) # True
        
                    # Uso de np.frombuffer() con memoryview, con dos dtypes:
                    LCLficheroCompletoEnLaRAM = np.frombuffer(
                        lasDataView,
                        dtype=np.uint8
                    )
                    clidaux.printMsg('cliddata-> np.frombuffer(lasDataView, dtype=np.uint8): {} {}'.format(type(LCLficheroCompletoEnLaRAM), len(LCLficheroCompletoEnLaRAM))) # <class 'numpy.ndarray'> 160615413
                    LCLficheroCompletoEnLaRAM = np.frombuffer(
                        lasDataViewPoints,
                        dtype=self.myLasHead.formatoDtypePointFormatXXNotacionNpDtype,
                        count=self.myLasHead.numptrecords
                    )
                    clidaux.printMsg('cliddata-> np.frombuffer(lasDataViewPoints, dtype=myLasHead.formatoDtypePointFormatXXNotacionNpDtype): {} {}'.format(type(LCLficheroCompletoEnLaRAM), len(LCLficheroCompletoEnLaRAM))) # <class 'numpy.ndarray'> 4723976
        
                    # Propiedades de memoryview()
                    # memoryview objects allow Python code to access the internal data of an object that supports the buffer protocol without copying.
                    # https://docs.python.org/dev/library/stdtypes.html#memoryview
                    # https://bugs.python.org/issue19014
                    clidaux.printMsg('\n00 c_contiguous: {} {}'.format(type(lasDataView), len(lasDataView)))
                    clidaux.printMsg('01 c_contiguous: {}'.format(lasDataView.c_contiguous))
                    clidaux.printMsg('02 f_contiguous: {}'.format(lasDataView.f_contiguous))
                    clidaux.printMsg('03 contiguous: {}'.format(lasDataView.contiguous))
                    clidaux.printMsg('04 format: {}'.format(lasDataView.format))
                    clidaux.printMsg('05 itemsize: {}'.format(lasDataView.itemsize))
                    clidaux.printMsg('06 nbytes: {}'.format(lasDataView.nbytes))
                    clidaux.printMsg('07 ndim: {}'.format(lasDataView.ndim))
                    clidaux.printMsg('08 readonly: {}'.format(lasDataView.readonly))
                    clidaux.printMsg('09 shape: {}'.format(lasDataView.shape))
                    clidaux.printMsg('10 strides: {}'.format(lasDataView.strides))
                    clidaux.printMsg('11 suboffsets: {}'.format(lasDataView.suboffsets))
                    # obj The underlying object of the memoryview:
                    clidaux.printMsg('12 obj {} {}'.format(type(lasDataView.obj), lasDataView.obj[:20])) # <class 'bytes'>
                    # tobytes(order=None) -> Return the data in the buffer as a bytestring. This is equivalent to calling the bytes constructor on the memoryview.
                    #  https://docs.python.org/dev/library/stdtypes.html#memoryview.tobytes
                    clidaux.printMsg('13 tobytes {} {}'.format(type(lasDataView.tobytes()), len(lasDataView.tobytes()))) # <class 'bytes'>
                    # cast(format[, shape]) -> Cast a memoryview to a new format or shape.
                    #  https://docs.python.org/dev/library/stdtypes.html#memoryview.cast
                    clidaux.printMsg('14 cast() {} {}'.format(type(lasDataView.cast('b')), len(lasDataView.cast('b')))) #<class 'memoryview'>
                    try:
                        LCLficheroCompletoEnLaRAM = np.frombuffer(lasDataView.tobytes())
                        clidaux.printMsg('13a frombuffer {} {}'.format(type(LCLficheroCompletoEnLaRAM), len(LCLficheroCompletoEnLaRAM)))
                    except:
                        clidaux.printMsg('13a Error en np.frombuffer(lasDataView.tobytes())')
                    try:
                        LCLficheroCompletoEnLaRAM = np.frombuffer(lasDataView.cast('b'))
                        clidaux.printMsg('14a frombuffer {} {}'.format(type(LCLficheroCompletoEnLaRAM), len(LCLficheroCompletoEnLaRAM)))
                    except:
                        clidaux.printMsg('14a Error en np.frombuffer(lasDataView.cast("b"))')
                    clidaux.printMsg('________________________________________________________________________________')
                # ==================================================================
    
            else:
                infileLasConRuta = clidaux.descomprimeLaz(infileRgxConRuta, descomprimirLazEnMemoria=False)
                # ATENCION: recalculo las propiedades de la cabecera con el fichero descomprimido en memoria
                # porque el fichero comprimido tiene un offset de 335 en lugar de 229 por el VLR de laszip 
                # Se puede abreviar a cambiar solo esa propiedad
                # clidaux.printMsg('\n---------------->cliddata-> infileLasConRuta11 (rgx): {}'.format(infileLasConRuta))
                self.myLasHead = clidhead.LasHeadClass(
                    infileLasConRuta,
                    lasDataMem=None,
                    metersBlock=GLO.GLBLmetrosBloque,
                    metersCell=GLO.GLBLmetrosCelda,
                    LCLordenColoresInput=LCLordenColoresInput,
                    verbose=GLO.GLBLverbose,
                    TRNShuso29=TRNShuso29,
                )
                # Obtengo self.ficheroCompletoEnLaRAM:
                self.readLasData()
        else:
            clidaux.printMsg(f'cliddata-> ATENCION: extension del fichero no las ni laz: revisar codigo')


    # ==========================================================================
    def crearPuntoRecordDtypes(self):
        # Este no lo uso porque lo obtengo en clidnv0.numbaMainVuelta0() con miPtoNpRecordPointFormatXX = arrayFicheroCompletoEnLaRAM[contadorPral]
        miPtoNpArrayRecord = np.zeros(1, dtype=np.dtype(self.myLasHead.formatoDtypePointFormatXXNotacionNpDtype))
        self.miPtoNpRecordPointFormatXX = miPtoNpArrayRecord[0]

        miPtoNpArrayRecord = np.zeros(1, dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype))
        self.miPtoNpRecordPointFormat99 = miPtoNpArrayRecord[0]

        # Este ya no lo uso
        # miPtoNpArrayRecord = np.zeros(1, dtype=np.dtype(self.myLasHead.formatoDtypePointCompactNotacionNpDtype))
        # self.miPtoNpRecordMini = miPtoNpArrayRecord[0]

        # Este lo uso en diversos modulos
        self.miPtoNpArrayEstrVar = np.zeros(1, dtype=np.dtype(self.myLasHead.formatoDtypeExtrVarNotacionNpDtype))
        self.miPtoNpExtrVar = self.miPtoNpArrayEstrVar[0]

        # Este lo uso clidnv0, clidnv1 y clidshow
        self.miPtoNpArrayMaxiMiniSubCel = np.zeros(1, dtype=np.dtype(self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype))
        self.miPtoNpMaxiMiniSubCel = self.miPtoNpArrayMaxiMiniSubCel[0]


    # ==========================================================================
    def crearListaRangosAltura(self):
        if GLO.GLBLrangosDeAlturasSuperSimplificados:
            # [0.50, 3.00, 5.00, 99.99]  # Para matorral medio o alto y para arbolado
            listaRangos_AlturasMasDe = [
                GLO.GLBLrangosDeAlturasSuperSimplificados1,
                GLO.GLBLrangosDeAlturasSuperSimplificados2,
                GLO.GLBLrangosDeAlturasSuperSimplificados3,
                99.99,
            ]
            # listaRangos_AlturasRango = [0.25, 1.50, 2.50, 99.99]  # Para matorral bajo, medio o alto.
            listaRangos_AlturasRango = [
                GLO.GLBLrangosDeAlturasSuperSimplificados1 / 2,
                GLO.GLBLrangosDeAlturasSuperSimplificados2 / 2,
                GLO.GLBLrangosDeAlturasSuperSimplificados3 / 2,
                GLO.GLBLrangosDeAlturasSuperSimplificados3,
                99.99,
            ]
        else:
            # [0.25, 0.50, 1.50, 3.00, 5.00, 99.99]
            listaRangos_AlturasMasDe = [
                GLO.GLBLrangosDeAlturasSimplificados1,
                GLO.GLBLrangosDeAlturasSimplificados2,
                GLO.GLBLrangosDeAlturasSimplificados3,
                GLO.GLBLrangosDeAlturasSimplificados4,
                GLO.GLBLrangosDeAlturasSimplificados5,
                99.99,
            ]
            # [0.25, 0.50, 1.50, 3.00, 5.00, 99.99]
            listaRangos_AlturasRango = [
                GLO.GLBLrangosDeAlturasSuperSimplificados1,
                GLO.GLBLrangosDeAlturasSuperSimplificados2,
                GLO.GLBLrangosDeAlturasSuperSimplificados3,
                GLO.GLBLrangosDeAlturasSuperSimplificados4,
                GLO.GLBLrangosDeAlturasSuperSimplificados5,
                99.99,
            ]

        # Para Hdom= 5m -> 0.5 m; 2.0 m;         5.0 m:
        # Para Hdom=10m -> 0.5 m; 2.0 m; 5.0 m;  10.0 m:
        # Para Hdom=15m -> 0.5 m; 2.0 m; 7.5 m;  15.0 m:
        # Para Hdom=20m -> 0.5 m; 2.0 m; 10.0 m; 20.0 m:
        # Si es < 1000 indica cm; si es > 1000 indice 1000 + % referido a AltDom
        # El ultimo limite es 10150 en vez de 10100 porque uso el 150% de Alt95
        #  y asi incluir todos los puntos por encima del 50% de Alt95
        listaRangos_AlturasPctjNum = [0.5, 2.0, 1050, 1150]
        listaRangos_AlturasPctjTxt = ['050cm', '200cm', '50%HD', 'TopHD']

        self.listaRangos_AlturasMasDe = np.array(listaRangos_AlturasMasDe)
        self.listaRangos_AlturasRango = np.array(listaRangos_AlturasRango)
        self.listaRangos_AlturasPctjNum = np.array(listaRangos_AlturasPctjNum)
        self.listaRangos_AlturasPctjTxt = np.array(listaRangos_AlturasPctjTxt)


    # ==========================================================================
    def crearDictArraysOutputFileNames(self, fileCoord, lasFileReclasificado):
        dictFilesSinConRuta = {}
        arrayFilesSinRuta = []
        arrayFilesConRuta = []
        arrayFilesNombreLote = []

        contadorLotes = 0
        if GLO.GLBLverbose:
            print('cliddata-> GLO.MAINrutaOutput->->', GLO.MAINrutaOutput)

        # ======================================================================
        listaGrabarInfoPorClase = [
            [GLO.GLBLgrabarPuntosPorClaseLasOrig, 'Orig'],
            [GLO.GLBLgrabarPuntosPorClaseLasRecl, 'Recl'],
        ]
        for grabarInfoPorClase in listaGrabarInfoPorClase:
            lasOrigRecl = grabarInfoPorClase[1]
            if not grabarInfoPorClase[0]:
                # print('cliddata-> NO se guardan datos por clase con lasOrigRecl: {}'.format(lasOrigRecl))
                continue
            # print('cliddata-> SI se guardan datos por clase con lasOrigRecl: {}'.format(lasOrigRecl))
            if GLO.GLBLgrabarNumeroPuntosPorClase:
                listaFilesSinRutaClases = []
                listaFilesConRutaClases = []
                for lasClassNum in range(GLO.GLBLnumMaximoDeClases):
                    fileText = 'Clase{:02}_TodasLasPasadasTodosLosRetornos_NumPuntos_{}.asc'.format(
                        lasClassNum,
                        lasOrigRecl
                    )
                    fileNameSinRuta = '{}_{}.asc'.format(fileCoord, fileText)
                    fileRuta = os.path.join(GLO.MAINrutaOutput, 'PointClass/{}/10mCell/NumPtos/'.format(lasOrigRecl))
                    fileNameConRuta = os.path.join(
                        fileRuta,
                        fileNameSinRuta
                    )
                    #fileNameSinRuta = 'Clase{:02}_NumPuntos_{}'.format(lasClassNum, lasOrigRecl)
                    listaFilesSinRutaClases.append(fileText)
                    listaFilesConRutaClases.append(fileNameConRuta)
                    dictFilesSinConRuta[fileNameSinRuta] = fileNameConRuta
                arrayFilesSinRuta.append(listaFilesSinRutaClases)
                arrayFilesConRuta.append(listaFilesConRutaClases)
                arrayFilesNombreLote.append('ClasesNumPuntos')
                contadorLotes += 1
            # ======================================================================
    
            # ======================================================================
            if GLO.GLBLgrabarCeldasClasesSueloVegetacion or GLO.GLBLgrabarCeldasClasesEdificio or GLO.GLBLgrabarCeldasClasesOtros:
                listaRutasCobs = []
                listaFilesSinRutaCobs = []
                listaFilesConRutaCobs = []
                if GLO.GLBLgrabarCeldasClasesSueloVegetacion: # PointClass/{Orig/Recl}/10mCell/
                    listaFilesSinRutaCobs.extend(['CeldasPrcntjPrimerosRetornosSuelo_{}'.format(lasOrigRecl)])  # aCeldasNumPrimerosRetornosSuelo {LasOrig/Recl}, aCeldasNumPrimerosRetornosTlp
                    listaFilesSinRutaCobs.extend(['CeldasPrcntjPrimerosRetornosVeget_{}'.format(lasOrigRecl)])  # aCeldasNumPrimerosRetornosVeget {LasOrig/Recl}, aCeldasNumPrimerosRetornosTlp
                    listaRutasCobs.extend(['PointClass/{}/10mCell/PorcentajePtosSuelo/'.format(lasOrigRecl)])
                    listaRutasCobs.extend(['PointClass/{}/10mCell/PorcentajePtosVegetacion/'.format(lasOrigRecl)])
                if GLO.GLBLgrabarCeldasClasesEdificio: # PointClass/{Orig/Recl}/10mCell/
                    listaFilesSinRutaCobs.extend(['CeldasPrcntjPrimerosRetornosEdifi_{}'.format(lasOrigRecl)])  # aCeldasNumPrimerosRetornosEdificio {LasOrig/Recl}, aCeldasNumPrimerosRetornosTlp
                    listaRutasCobs.extend(['PointClass/{}/10mCell/PorcentajePtosEdificio/'.format(lasOrigRecl)])
                if GLO.GLBLgrabarCeldasClasesOtros: # PointClass/{Orig/Recl}/10mCell/
                    listaFilesSinRutaCobs.extend(['CeldasPrcntjPrimerosRetornosOverl_{}'.format(lasOrigRecl)])  # aCeldasNumTodosLosRetornosOverlap {LasOrig/Recl}, aCeldasNumPrimerosRetornosTlp
                    listaFilesSinRutaCobs.extend(['CeldasPrcntjPrimerosRetornosOtros_{}'.format(lasOrigRecl)])  # aCeldasNumPrimerosRetornosOtros {LasOrig/Recl}, aCeldasNumPrimerosRetornosTlp
                    listaRutasCobs.extend(['PointClass/{}/10mCell/PorcentajePtosOverlay/'.format(lasOrigRecl)])
                    listaRutasCobs.extend(['PointClass/{}/10mCell/PorcentajePtosOtros/'.format(lasOrigRecl)])
                for item in range(len(listaFilesSinRutaCobs)):
                    txtFileRuta = listaRutasCobs[item]
                    fileText = listaFilesSinRutaCobs[item]
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput, txtFileRuta, '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaCobs.append(fileNameConRuta)
                    dictFilesSinConRuta[fileText] = fileNameConRuta
                arrayFilesSinRuta.append(listaFilesSinRutaCobs)
                arrayFilesConRuta.append(listaFilesConRutaCobs)
                arrayFilesNombreLote.append('ClasesCobsCeldas')
                contadorLotes += 1
            # ======================================================================
    
            # ======================================================================
            if GLO.GLBLgrabarSubCeldasClasesSueloVegetacion or GLO.GLBLgrabarSubCeldasClasesEdificio or GLO.GLBLgrabarSubCeldasClasesOtros:
                listaRutasnPtosClasesSubCeldas = []
                listaFilesSinRutaClasesSubCeldas = []
                listaFilesConRutaClasesSubCeldas = []
                if GLO.GLBLgrabarSubCeldasClasesSueloVegetacion: # PointClass/{Orig/Recl}/02mCell/
                    listaFilesSinRutaClasesSubCeldas.extend(['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)])  # aSubCeldasProp09TodosLosRetornosSuelo {LasOrig/Recl}
                    listaFilesSinRutaClasesSubCeldas.extend(['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)])  # aSubCeldasProp09TodosLosRetornosVeget {LasOrig/Recl}
                    listaRutasnPtosClasesSubCeldas.extend(['PointClass/{}/02mCell/Prop09SueloTlr/'.format(lasOrigRecl)])
                    listaRutasnPtosClasesSubCeldas.extend(['PointClass/{}/02mCell/Prop09VegetacionTlr/'.format(lasOrigRecl)])
                    if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                        listaFilesSinRutaClasesSubCeldas.extend(['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)])  # aSubCeldasProp09PrimerosRetornosSuelo {LasOrig/Recl}
                        listaFilesSinRutaClasesSubCeldas.extend(['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)])  # aSubCeldasProp09PrimerosRetornosVeget {LasOrig/Recl}
                        listaRutasnPtosClasesSubCeldas.extend(['PointClass/{}/02mCell/Prop09SueloRt1/'.format(lasOrigRecl)])
                        listaRutasnPtosClasesSubCeldas.extend(['PointClass/{}/02mCell/Prop09VegetacionRt1/'.format(lasOrigRecl)])
                if GLO.GLBLgrabarSubCeldasClasesEdificio: # PointClass/{Orig/Recl}/02mCell/
                    listaFilesSinRutaClasesSubCeldas.extend(['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)])  # aSubCeldasProp09TodosLosRetornosEdificio {LasOrig/Recl}
                    listaRutasnPtosClasesSubCeldas.extend(['PointClass/{}/02mCell/Prop09EdificioTlr/'.format(lasOrigRecl)])
                    if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                        listaFilesSinRutaClasesSubCeldas.extend(['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)])  # aSubCeldasProp09PrimerosRetornosEdificio {LasOrig/Recl}
                        listaRutasnPtosClasesSubCeldas.extend(['PointClass/{}/02mCell/Prop09EdificioRt1/'.format(lasOrigRecl)])
                if GLO.GLBLgrabarSubCeldasClasesOtros: # PointClass/{Orig/Recl}/02mCell/
                    listaFilesSinRutaClasesSubCeldas.extend(['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)])  # aSubCeldasProp09TodosLosRetornosOtros {LasOrig/Recl}
                    listaRutasnPtosClasesSubCeldas.extend(['PointClass/{}/02mCell/Prop09OtrosTlr/'.format(lasOrigRecl)])
                    if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                        listaFilesSinRutaClasesSubCeldas.extend(['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)])  # aSubCeldasProp09PrimerosRetornosOtros {LasOrig/Recl}
                        listaRutasnPtosClasesSubCeldas.extend(['PointClass/{}/02mCell/Prop09OtrosRt1/'.format(lasOrigRecl)])
                for item in range(len(listaFilesSinRutaClasesSubCeldas)):
                    txtFileRuta = listaRutasnPtosClasesSubCeldas[item]
                    fileText = listaFilesSinRutaClasesSubCeldas[item]
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput, txtFileRuta, '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaClasesSubCeldas.append(fileNameConRuta)
                    dictFilesSinConRuta[fileText] = fileNameConRuta
                arrayFilesSinRuta.append(listaFilesSinRutaClasesSubCeldas)
                arrayFilesConRuta.append(listaFilesConRutaClasesSubCeldas)
                arrayFilesNombreLote.append('ClasesNumPtosSubCeldas')
            # ======================================================================
    
            # ======================================================================
            if GLO.GLBLgrabarMetricoClasesSueloVegetacion or GLO.GLBLgrabarMetricoClasesEdificio or GLO.GLBLgrabarMetricoClasesOtros:
                # print(
                #     'cliddata-> GLBLgrabarMetricoClasesSueloVegetacion: {}; GLBLgrabarMetricoClasesEdificio: {}; GLBLgrabarMetricoClasesOtros: {}'.format(
                #         GLO.GLBLgrabarMetricoClasesSueloVegetacion,
                #         GLO.GLBLgrabarMetricoClasesEdificio,
                #         GLO.GLBLgrabarMetricoClasesOtros
                #     )
                # )
                listaRutasnPtosClasesMetrico = []
                listaFilesSinRutaClasesMetrico = []
                listaFilesConRutaClasesMetrico = []
                if GLO.GLBLgrabarMetricoClasesSueloVegetacion: # PointClass/{Orig/Recl}/01mCell/
                    listaFilesSinRutaClasesMetrico.extend(['MetricoProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)])  # aMetricoProp09TodosLosRetornosSuelo {LasOrig/Recl}
                    listaFilesSinRutaClasesMetrico.extend(['MetricoProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)])  # aMetricoProp09TodosLosRetornosVeget {LasOrig/Recl}
                    listaRutasnPtosClasesMetrico.extend(['PointClass/{}/01mCell/Prop09SueloTlr/'.format(lasOrigRecl)])
                    listaRutasnPtosClasesMetrico.extend(['PointClass/{}/01mCell/Prop09VegetacionTlr/'.format(lasOrigRecl)])
                    if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                        listaFilesSinRutaClasesMetrico.extend(['MetricoProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)])  # aMetricoProp09PrimerosRetornosSuelo {LasOrig/Recl}
                        listaFilesSinRutaClasesMetrico.extend(['MetricoProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)])  # aMetricoProp09PrimerosRetornosVeget {LasOrig/Recl}
                        listaRutasnPtosClasesMetrico.extend(['PointClass/{}/01mCell/Prop09SueloRt1/'.format(lasOrigRecl)])
                        listaRutasnPtosClasesMetrico.extend(['PointClass/{}/01mCell/Prop09VegetacionRt1/'.format(lasOrigRecl)])
                if GLO.GLBLgrabarMetricoClasesEdificio: # PointClass/{Orig/Recl}/01mCell/
                    listaFilesSinRutaClasesMetrico.extend(['MetricoProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)])  # aMetricoProp09TodosLosRetornosEdificio {LasOrig/Recl}
                    listaRutasnPtosClasesMetrico.extend(['PointClass/{}/01mCell/Prop09EdificioTlr/'.format(lasOrigRecl)])
                    if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                        listaFilesSinRutaClasesMetrico.extend(['MetricoProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)])  # aMetricoProp09PrimerosRetornosEdificio {LasOrig/Recl}
                        listaRutasnPtosClasesMetrico.extend(['PointClass/{}/01mCell/Prop09EdificioRt1/'.format(lasOrigRecl)])
                if GLO.GLBLgrabarMetricoClasesOtros: # PointClass/{Orig/Recl}/01mCell/
                    listaFilesSinRutaClasesMetrico.extend(['MetricoProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)])  # aMetricoProp09TodosLosRetornosOtros {LasOrig/Recl}
                    listaRutasnPtosClasesMetrico.extend(['PointClass/{}/01mCell/Prop09OtrosTlr/'.format(lasOrigRecl)])
                    if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                        listaFilesSinRutaClasesMetrico.extend(['MetricoProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)])  # aMetricoProp09PrimerosRetornosOtros {LasOrig/Recl}
                        listaRutasnPtosClasesMetrico.extend(['PointClass/{}/01mCell/Prop09OtrosRt1/'.format(lasOrigRecl)])
                for item in range(len(listaFilesSinRutaClasesMetrico)):
                    txtFileRuta = listaRutasnPtosClasesMetrico[item]
                    fileText = listaFilesSinRutaClasesMetrico[item]
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput, txtFileRuta, '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaClasesMetrico.append(fileNameConRuta)
                    dictFilesSinConRuta[fileText] = fileNameConRuta
                arrayFilesSinRuta.append(listaFilesSinRutaClasesMetrico)
                arrayFilesConRuta.append(listaFilesConRutaClasesMetrico)
                arrayFilesNombreLote.append('ClasesNumPtosMetrico')
        # ======================================================================

        # ======================================================================
        # Si estoy chequeando el lasFileReclasificado solo guardo NumeroPuntosPorClase con lasOrigRecl = 'recl'
        if lasFileReclasificado:
            self.dictFilesSinConRuta = dictFilesSinConRuta
            self.arrayFilesSinRuta = arrayFilesSinRuta
            self.arrayFilesConRuta = arrayFilesConRuta
            return
        # ======================================================================

        # ======================================================================
        if GLO.GLBLcalcularFcc:
            listaGrabarFccPorMayorDe = [
                GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmds,
                GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmdb,
                GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmdf,
                GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmdk,
            ]
            listaTextoFccPorMayorDe = [
                'FccRptoAmds_PrimeRets_MasDe',
                'FccRptoAmdb_PrimeRets_MasDe',
                'FccRptoAmdf_PrimeRets_MasDe',
                'FccRptoAmdk_PrimeRets_MasDe',
            ]
            for GLBLgrabar, tipoFCC in zip(listaGrabarFccPorMayorDe, listaTextoFccPorMayorDe):
                listaFilesSinRutaFccsPrimRet = []
                listaFilesConRutaFccsPrimRet = []
                if GLBLgrabar:
                    for miAltura in self.listaRangos_AlturasMasDe[:-1]:
                        fileText = '{}{:04}'.format(
                            tipoFCC,
                            int(miAltura * 100)
                        )
                        fileRuta = os.path.join(
                            GLO.MAINrutaOutput,'Fcc/10mCell/{}{:04}'.format(
                                tipoFCC[3:],
                                int(miAltura * 100)
                            )
                        )
                        fileNameConRuta = os.path.join(
                            fileRuta,
                            '{}_{}.asc'.format(
                                fileCoord,
                                fileText
                            )
                        )
                        listaFilesSinRutaFccsPrimRet.append(fileText)
                        listaFilesConRutaFccsPrimRet.append(fileNameConRuta)
                        dictFilesSinConRuta[fileText] = fileNameConRuta
                    arrayFilesSinRuta.append(listaFilesSinRutaFccsPrimRet)
                    arrayFilesConRuta.append(listaFilesConRutaFccsPrimRet)
                    arrayFilesNombreLote.append(tipoFCC)
                    contadorLotes += 1

            listaGrabarFccPorPctjDe = [
                GLO.GLBLgrabarFccPorPctjDeAltDomConTodosLosRetRptoAmdb,
                GLO.GLBLgrabarFccPorPctjDeAltDomConTodosLosRetRptoAmdk
            ]
            listaTextoFccPorPctjDe = [
                'FccRptoAmdb_TodosRets',
                'FccRptoAmdk_TodosRets',
            ]
            # Se usan estos rangos:
            #   listaRangos_AlturasPctjNum = [50, 200, 10050, 10100]
            #   listaRangos_AlturasPctjTxt = ['050cm', '200cm', '50%HD', 'TopHD']
            for GLBLgrabar, tipoFCC in zip(listaGrabarFccPorPctjDe, listaTextoFccPorPctjDe):
                listaFilesSinRutaFccsRango = []
                listaFilesConRutaFccsRango = []
                if GLBLgrabar:
                    for nRango in range(len(self.listaRangos_AlturasPctjTxt) - 1):
                        miAltura1Txt = self.listaRangos_AlturasPctjTxt[nRango]
                        miAltura2Txt = self.listaRangos_AlturasPctjTxt[nRango + 1]
                        fileText = '{}_{}_{}'.format(tipoFCC, miAltura1Txt, miAltura2Txt)
                        fileRuta = os.path.join(
                            GLO.MAINrutaOutput,'Fcc/10mCell/Fcc_Rango_{}_{}'.format(
                                miAltura1Txt,
                                miAltura2Txt,
                            )
                        )
                        fileNameConRuta = os.path.join(
                            fileRuta,
                            '{}_{}.asc'.format(
                                fileCoord,
                                fileText
                            )
                        )
                        listaFilesSinRutaFccsRango.append(fileText)
                        listaFilesConRutaFccsRango.append(fileNameConRuta)
                        dictFilesSinConRuta[fileText] = fileNameConRuta
                    arrayFilesSinRuta.append(listaFilesSinRutaFccsRango)
                    arrayFilesConRuta.append(listaFilesConRutaFccsRango)
                    arrayFilesNombreLote.append(tipoFCC)
                    contadorLotes += 1
        # ======================================================================


            listaGrabarFccPorRangoDe = [
                GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmds,
                GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmds,
                GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmdb,
                GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmdb,
                GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmdf,
                GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmdf,
                GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmdk,
                GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmdk,
            ]
            listaTextoFccPorRangoDe = [
                'FccRptoAmds_PrimeRets',
                'FccRptoAmds_TodosRets',
                'FccRptoAmdb_PrimeRets',
                'FccRptoAmdb_TodosRets',
                'FccRptoAmdf_PrimeRets',
                'FccRptoAmdf_TodosRets',
                'FccRptoAmdk_PrimeRets',
                'FccRptoAmdk_TodosRets',
            ]
            for GLBLgrabar, tipoFCC in zip(listaGrabarFccPorRangoDe, listaTextoFccPorRangoDe):
                listaFilesSinRutaFccsRango = []
                listaFilesConRutaFccsRango = []
                if GLBLgrabar:
                    for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                        miAltura1 = self.listaRangos_AlturasRango[nRango]
                        miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                        fileText = '{}_{:04}_{:04}'.format(
                            tipoFCC,
                            int(miAltura1 * 100),
                            int(miAltura2 * 100),
                        )
                        fileRuta = os.path.join(
                            GLO.MAINrutaOutput,'Fcc/10mCell/{}_Rango_{:04}_{:04}'.format(
                                tipoFCC[3:],
                                int(miAltura1 * 100),
                                int(miAltura2 * 100),
                            )
                        )
                        fileNameConRuta = os.path.join(
                            fileRuta,
                            '{}_{}.asc'.format(
                                fileCoord,
                                fileText
                            )
                        )
                        listaFilesSinRutaFccsRango.append(fileText)
                        listaFilesConRutaFccsRango.append(fileNameConRuta)
                        dictFilesSinConRuta[fileText] = fileNameConRuta
                    arrayFilesSinRuta.append(listaFilesSinRutaFccsRango)
                    arrayFilesConRuta.append(listaFilesConRutaFccsRango)
                    arrayFilesNombreLote.append(tipoFCC)
                    contadorLotes += 1
        # ======================================================================

        # ======================================================================
        listaFilesSinRutaAlts = []
        listaFilesConRutaAlts = []
        if GLO.GLBLgrabarAlturasRptoAzMin:
            listaFilesSinRutaAlts = [
                'AltClaseSueloRptAzMin',  # aCeldasCotaMediaTlrSuePsel - aCeldasCotaMinAbsPse
                'AltClasesVegetacionRptoAzMin',  # aCeldasCotaMediaTlrVegPsel - aCeldasCotaMinAbsPse
                'AltClaseEdificiosRptoAzMin',
            ]  # aCeldasCotaMediaTlrEdiPsel - aCeldasCotaMinAbsPse
            for fileText in listaFilesSinRutaAlts:
                fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'PointClass/Orig/10mCell/Alt/', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaAlts.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
        arrayFilesSinRuta.append(listaFilesSinRutaAlts)
        arrayFilesConRuta.append(listaFilesConRutaAlts)
        arrayFilesNombreLote.append('ClasesAlts')
        contadorLotes += 1
        # ======================================================================

        # ======================================================================
        listaFilesSinRutaApices = []
        listaFilesConRutaApices = []
        if GLO.GLBLcalcularApices:
            listaFilesSinRutaApices = [
                'CeldasApicesMicro',
                'CeldasApicesMesos',
                'CeldasApicesMacro',
                'CeldasApicesMegas',
            ] # aCeldasApices
            for fileText in listaFilesSinRutaApices:
                fileNameConRuta = os.path.join(
                    GLO.MAINrutaOutput,'Apices/10mCell/{}/'.format(fileText[-5:]),
                    '{}_{}.asc'.format(fileCoord, fileText)
                )
                listaFilesConRutaApices.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
        arrayFilesSinRuta.append(listaFilesSinRutaApices)
        arrayFilesConRuta.append(listaFilesConRutaApices)
        arrayFilesNombreLote.append('Apices')
        contadorLotes += 1

        listaRutasVarios = []
        listaFilesSinRutaVarios = []
        listaFilesConRutaVarios = []
        if GLO.GLBLgrabarNumPuntosTotales:
            listaFilesSinRutaVarios.extend(['numPuntosTotalesDentroDeBloque'])
            listaFilesSinRutaVarios.extend(['numPuntosPasadaSelecOk'])
            listaRutasVarios.extend(['NumPtos/10mCell/Totales/'])
            listaRutasVarios.extend(['NumPtos/10mCell/PasadaSelec/'])
        if GLO.GLBLgrabarPrimerosRetornosNoSolape:
            listaFilesSinRutaVarios.extend(['numPuntosPrimRetSinSolape'])
            listaRutasVarios.extend(['NumPtos/10mCell/SinSolapeRt1/'])
        if GLO.GLBLgrabarNumPuntosAuxiliar:
            listaFilesSinRutaVarios.extend(['numPuntosAlmacenablesSinOutliers'])
            listaFilesSinRutaVarios.extend(['numPuntosPasadaSelecSinFiltrarSospechosos'])
            listaRutasVarios.extend(['NumPtos/10mCell/Auxiliar/'])
            listaRutasVarios.extend(['NumPtos/10mCell/Auxiliar/'])
        if GLO.GLBLgrabarNumIdPasada:
            listaFilesSinRutaVarios.extend(['numPasadas'])
            listaFilesSinRutaVarios.extend(['idPasadaBasalSeleccionada'])
            listaFilesSinRutaVarios.extend(['idPasadaSueloSeleccionada'])
            listaRutasVarios.extend(['Pasadas/10mCell/NumPasadas/'])
            listaRutasVarios.extend(['Pasadas/10mCell/IdPasadaBasal/'])
            listaRutasVarios.extend(['Pasadas/10mCell/IdPasadaSuelo/'])

        if GLO.GLBLgrabarCotaMinMaxCelda:
            listaFilesSinRutaVarios.extend(['CeldasCotaMinAbsTlp', 'CeldasCotaMaxAbsTlp'])
            listaRutasVarios.extend(['CotaMinMax/10mCell/', 'CotaMinMax/10mCell/'])
        if GLO.GLBLcalcularMds and GLO.GLBLgrabarNumPuntosSuelo:
            listaFilesSinRutaVarios.extend(['numPuntosSueloTodasLasPasadas', 'numPuntosSueloPsue', 'numPuntosSueloPselOk'])
            listaRutasVarios.extend(['NumPtos/10mCell/Suelo/', 'NumPtos/10mCell/Suelo/', 'NumPtos/10mCell/Suelo/'])

        if GLO.GLBLgrabarCotasDiferenciaEntrePasadas:
            #listaFilesSinRutaVarios.extend(['zMediaPtsTodosOtraPasada'])
            listaFilesSinRutaVarios.extend(['zMediaPtsTodosDiferenciaEntrePasadas'])
            listaRutasVarios.extend(['Pasadas/DifEntrePasadas'])

        if GLO.GLBLgrabarCotasMediasPorClase:
            listaFilesSinRutaVarios.extend(['zMediaPtsVegetPsel', 'zMediaPtsEdifiPsel'])
            listaRutasVarios.extend(['CotaMinMax/10mCell/Veget/', 'CotaMinMax/10mCell/Edifi'])
            if GLO.GLBLcalcularMds:
                listaFilesSinRutaVarios.extend(['zMediaPtsSueloPsel', 'zMediaPtsSueloPsue'])
                listaRutasVarios.extend(['CotaMinMax/10mCell/Suelo/', 'CotaMinMax/10mCell/Suelo'])

        if GLO.GLBLgrabarPercentilesAbsolutos:
            listaFilesSinRutaVarios.extend(['zMin10', 'zMax95', 'zRango10a95'])
            listaRutasVarios.extend(['CotaMinMax/10mCell/', 'CotaMinMax/10mCell/', 'CotaMinMax/10mCell/'])
            if GLO.GLBLcalcularMds:
                listaFilesSinRutaVarios.extend(['zRangoDesdeMediaSueloHasta95'])
                listaRutasVarios.extend(['CotaMinMax/10mCell/'])

        if GLO.GLBLgrabarPrimerosVsSegundosRetornos:
            listaFilesSinRutaVarios.extend(
                [
                    'SingleReturnTodasLasPasadas',
                    'MultiReturnTodasLasPasadas',
                    'RetornosPrimerosTodasLasPasadas',
                    'RetornosSiguientesTodasLasPasadas',
                    'RetornosPrimerosPasadaSel',
                    'RetornosSiguientesPasadaSel',
                ]
            )
            listaRutasVarios.extend(
                [
                    'NumPtos/10mCell/PorRetornos/SingleReturn/',
                    'NumPtos/10mCell/PorRetornos/MultiReturn/',
                    'NumPtos/10mCell/PorRetornos/RetPriTlp/',
                    'NumPtos/10mCell/PorRetornos/RetSigTlp/',
                    'NumPtos/10mCell/PorRetornos/RetPriPsel/',
                    'NumPtos/10mCell/PorRetornos/RetSigPsel/'
                 ]
            )

        if GLO.GLBLleerGrabarCeldasEdge:
            listaFilesSinRutaVarios.extend(['scanEdge'])
            listaRutasVarios.extend(['Varios/'])
        if GLO.GLBLgrabarPropiedadTime:
            listaFilesSinRutaVarios.extend(['rawTime'])
            listaRutasVarios.extend(['Varios/'])
        if GLO.GLBLgrabarAngulos:
            listaFilesSinRutaVarios.extend(['Ang'])
            listaRutasVarios.extend(['Varios/'])

        if GLO.GLBLcalcularSubCeldas and GLO.GLBLgrabarCotaMinMaxSubCelda:  # Mde/02mCell/CotaMinMax/
            listaFilesSinRutaVarios.extend(['SubCeldasCotaMin'])  # aSubCeldasCotaMinAA
            # fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CotaMinMax/02mCell/CotaMin/', '%s_%s.asc' % (fileCoord, fileText))
            listaRutasVarios.extend(['CotaMinMax/02mCell/CotaMin'])
            listaFilesSinRutaVarios.extend(['SubCeldasCotaMax'])  # aSubCeldasCotaMaxAA
            # fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CotaMinMax/02mCell/CotaMax/', '%s_%s.asc' % (fileCoord, fileText))
            listaRutasVarios.extend(['CotaMinMax/02mCell/CotaMax'])

        for item in range(len(listaFilesSinRutaVarios)):
            txtFileRuta = listaRutasVarios[item]
            fileText = listaFilesSinRutaVarios[item]
            fileNameConRuta = os.path.join(GLO.MAINrutaOutput, txtFileRuta, '%s_%s.asc' % (fileCoord, fileText))
            listaFilesConRutaVarios.append(fileNameConRuta)
            dictFilesSinConRuta[fileText] = fileNameConRuta
        arrayFilesSinRuta.append(listaFilesSinRutaVarios)
        arrayFilesConRuta.append(listaFilesConRutaVarios)
        arrayFilesNombreLote.append('Varios')

        # ======================================================================
        listaRutasAlturaSobreSuelo = []
        listaFilesSinRutaAlturaSobreSuelo = []
        listaFilesConRutaAlturaSobreSuelo = []
        if GLO.GLBLgrabarPercentilesRelativos:
            if GLO.GLBLcalcularMds:
                listaFilesSinRutaAlturaSobreSuelo.extend(['CeldasAlt95SobreMds'])  # aCeldasAlt95SobreMds
                listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell/Alt95SobreMds/'])
                if GLO.GLBLgrabarPercentilAdicional:
                    listaFilesSinRutaAlturaSobreSuelo.extend(['CeldasAlt{:02}SobreMds'.format(GLO.GLBLgrabarPercentilAdicional)])  # aCeldasAltXxSobreMds
                    listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell/Alt{:02}SobreMds/'.format(GLO.GLBLgrabarPercentilAdicional)])
            if GLO.GLBLcalcularMdb:
                listaFilesSinRutaAlturaSobreSuelo.extend(['CeldasAlt95SobreMdb'])  # aCeldasAlt95SobreMdb
                listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell/Alt95SobreMdb/'])
                if GLO.GLBLgrabarPercentilAdicional:
                    listaFilesSinRutaAlturaSobreSuelo.extend(['CeldasAlt{:02}SobreMdb'.format(GLO.GLBLgrabarPercentilAdicional).format(GLO.GLBLgrabarPercentilAdicional)])  # aCeldasAltXxSobreMdb
                    listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell/Alt{:02}SobreMdb/'.format(GLO.GLBLgrabarPercentilAdicional)])
            if GLO.GLBLcalcularMdp:
                listaFilesSinRutaAlturaSobreSuelo.extend(['CeldasAlt95SobreMdf'])  # aCeldasAlt95SobreMdf
                listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell/Alt95SobreMdf/'])
                if GLO.GLBLgrabarPercentilAdicional:
                    listaFilesSinRutaAlturaSobreSuelo.extend(['CeldasAlt{:02}SobreMdf'.format(GLO.GLBLgrabarPercentilAdicional)])  # aCeldasAltXxSobreMdf
                    listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell/Alt{:02}SobreMdf/'.format(GLO.GLBLgrabarPercentilAdicional)])
                if  GLO.GLBLgrabarPercentilesSubCeldas:
                    listaFilesSinRutaAlturaSobreSuelo.extend(['SubCeldasAlt95SobreMdf'])  # aSubCeldasAlt95SobreMdf
                    listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell_split02mCell/Alt95SobreMdf/'])
            if GLO.GLBLcalcularMdk2mConPuntosClasificados:
                listaFilesSinRutaAlturaSobreSuelo.extend(['CeldasAlt95SobreMdk'])  # aCeldasAlt95SobreMdk
                listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell/Alt95SobreMdk/'])
                if GLO.GLBLgrabarPercentilAdicional:
                    listaFilesSinRutaAlturaSobreSuelo.extend(['CeldasAlt{:02}SobreMdk'.format(GLO.GLBLgrabarPercentilAdicional)])  # aCeldasAltXxSobreMdk
                    listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell/Alt{:02}SobreMdk/'.format(GLO.GLBLgrabarPercentilAdicional)])
                if  GLO.GLBLgrabarPercentilesSubCeldas:
                    listaFilesSinRutaAlturaSobreSuelo.extend(['SubCeldasAlt95SobreMdk'])  # aSubCeldasAlt95SobreMdk
                    listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/10mCell_split02mCell/Alt95SobreMdk/'])
        if GLO.GLBLgrabarSubCeldasAltMaxSobreMdf:
            if GLO.GLBLcalcularMdp and GLO.GLBLcalcularSubCeldas:
                listaFilesSinRutaAlturaSobreSuelo.extend(['SubCeldasAltMaxSobreMdf'])  # aSubCeldasAltMaxSobreMdf
                listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/02mCell/AltMaxSobreMdf/'])
        if GLO.GLBLgrabarSubCeldasAltMaxSobreMdk:
            if GLO.GLBLcalcularMdk2mConPuntosClasificados and GLO.GLBLcalcularSubCeldas:
                listaFilesSinRutaAlturaSobreSuelo.extend(['SubCeldasAltMaxSobreMdk'])  # aSubCeldasAltMaxSobreMdk
                listaRutasAlturaSobreSuelo.extend(['AltSobreTerreno/02mCell/AltMaxSobreMdk/'])

        for item in range(len(listaFilesSinRutaAlturaSobreSuelo)):
            txtFileRuta = listaRutasAlturaSobreSuelo[item]
            fileText = listaFilesSinRutaAlturaSobreSuelo[item]
            fileNameConRuta = os.path.join(GLO.MAINrutaOutput, txtFileRuta, '%s_%s.asc' % (fileCoord, fileText))
            listaFilesConRutaAlturaSobreSuelo.append(fileNameConRuta)
            dictFilesSinConRuta[fileText] = fileNameConRuta
        arrayFilesSinRuta.append(listaFilesSinRutaAlturaSobreSuelo)
        arrayFilesConRuta.append(listaFilesConRutaAlturaSobreSuelo)
        arrayFilesNombreLote.append('AlturaSobreSuelo')
        # ======================================================================

        # ======================================================================
        if (
            GLO.GLBLcalcularMds
            or GLO.GLBLcalcularMdb
            or GLO.GLBLcalcularMdc
            or GLO.GLBLcalcularMdm
            or GLO.GLBLcalcularMdg
            or GLO.GLBLcalcularMdk2mConPuntosClasificados
            or GLO.GLBLcalcularMdc2mConTodosLosPuntos
        ):
            listaFilesSinRutaAjustes = []
            listaFilesConRutaAjustes = []
            if GLO.GLBLverbose:
                print('cliddata-> Creando output files para Mds, Mdb, Mdc, Mdm, Mdg')
                print('cliddata-> GLBLcalcularMdb:            ', GLO.GLBLcalcularMdb)
                print('cliddata-> GLBLgrabarMdbPreInterpol:   ', GLO.GLBLgrabarMdbPreInterpol)
                print('cliddata-> GLBLgrabarMdbPosInterpol:   ', GLO.GLBLgrabarMdbPosInterpol)
                print('cliddata-> GLBLcalcularMdbCotaSubcelda:', GLO.GLBLcalcularMdbCotaSubcelda)
                print('cliddata-> GLBLgrabarMdbCotaSubceldaPreInterpol:', GLO.GLBLgrabarMdbCotaSubceldaPreInterpol)
                print('cliddata-> GLBLgrabarMdbCotaSubceldaPosInterpol:', GLO.GLBLgrabarMdbCotaSubceldaPosInterpol)
                print('cliddata-> GLBLcalcularMds:', GLO.GLBLcalcularMds)
                print('cliddata-> GLBLcalcularMdc:', GLO.GLBLcalcularMdc)
                print('cliddata-> GLBLcalcularMdm:', GLO.GLBLcalcularMdm)
                print('cliddata-> GLBLcalcularMdg:', GLO.GLBLcalcularMdg)
                print('cliddata-> GLBLcalcularMdk2mConPuntosClasificados:', GLO.GLBLcalcularMdk2mConPuntosClasificados)
                print('cliddata-> GLBLcalcularMdc2mConTodosLosPuntos:    ', GLO.GLBLcalcularMdc2mConTodosLosPuntos)

            # ->Estos ficheros se graban con guardarAjustesMdxPreInterpol{} y guardarCoeficientesAjuste{}
            #  que recorren secuencialmente los planos basal, Cielo y Major o Global
            if GLO.GLBLcalcularMds and GLO.GLBLgrabarMds:
                listaFilesSinRutaAjustes.extend(['planoSuelo_intercept'])  # aCeldasCoeficientesMds
                if GLO.GLBLgrabarCoeficientesXY:
                    listaFilesSinRutaAjustes.extend(['planoSuelo_coefX'])  # aCeldasCoeficientesMds
                    listaFilesSinRutaAjustes.extend(['planoSuelo_coefY'])  # aCeldasCoeficientesMds
                if GLO.GLBLgrabarEcmr:
                    listaFilesSinRutaAjustes.extend(['planoSuelo_Ecmr'])  # aCeldasCoeficientesMds
            if GLO.GLBLcalcularMdb and GLO.GLBLgrabarMdbPreInterpol:
                if GLO.GLBLverbose:
                    print('cliddata-> Creando output files para Mdb')
                listaFilesSinRutaAjustes.extend(['planoBasal_intercept'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=0, 0] -> aCeldasCoeficientesMdb[nX, nY, 0]
                if GLO.GLBLgrabarCoeficientesXY:
                    listaFilesSinRutaAjustes.extend(['planoBasal_coefX'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=0, 1] -> aCeldasCoeficientesMdb[nX, nY, 1]
                    listaFilesSinRutaAjustes.extend(['planoBasal_coefY'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=0, 2] -> aCeldasCoeficientesMdb[nX, nY, 2]
                if GLO.GLBLgrabarEcmr:
                    listaFilesSinRutaAjustes.extend(['planoBasal_Ecmr'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=0, 3] -> aCeldasCoeficientesMdb[nX, nY, 3]
                    listaFilesSinRutaAjustes.extend(
                        ['planoBasal_EcmrInicial']
                    )  # aCeldasCoeficientesMdxAll[nX, nY, nTP=0, 5] -> aCeldasCoeficientesMdb[nX, nY, 5]
                if GLO.GLBLcalcularMdbCotaSubcelda:  # Mde/02mCell/Basal/
                    if GLO.GLBLverbose:
                        print('cliddata-> Creando output files para SubCeldasMdb*')
                    if GLO.GLBLgrabarMdbCotaSubceldaPreInterpol:
                        listaFilesSinRutaAjustes.extend(['SubCeldasMdbPreInterpol'])  # aSubCeldasMdbPreInterpol
                    if GLO.GLBLgrabarMdbCotaSubceldaPosInterpol:
                        listaFilesSinRutaAjustes.extend(['SubCeldasMdbPostInterpol'])  # aSubCeldasMdbPostInterpol
                    # listaFilesSinRutaAjustes.extend(['SubCeldasMdbPost2Interpol'])  # aSubCeldasMdbPost2Interpol
            if GLO.GLBLcalcularMdk2mConPuntosClasificados:  # Mde/02mCell/Basal/
                if GLO.GLBLverbose:
                    print('cliddata-> Creando output files para SubCeldasMdk*')
                listaFilesSinRutaAjustes.extend(['SubCeldasMdkCotaMed'])  # aSubCeldasMdkCotaMed
                listaFilesSinRutaAjustes.extend(['SubCeldasMdkCotaMin'])  # aSubCeldasMdkCotaMin
                listaFilesSinRutaAjustes.extend(['SubCeldasMdkCotaItp'])  # aSubCeldasMdkCotaItp
            if GLO.GLBLcalcularMdc2mConTodosLosPuntos:  # Mde/02mCell/Basal/
                listaFilesSinRutaAjustes.extend(['SubCeldasMdcCotaMax'])  # aSubCeldasMdcCotaMax

            if GLO.GLBLcalcularMdc and GLO.GLBLgrabarMdc:
                listaFilesSinRutaAjustes.extend(['planoCielo_intercept'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=1, 0] -> aCeldasCoeficientesMdc[nX, nY, 0]
                if GLO.GLBLgrabarCoeficientesXYMdc:
                    listaFilesSinRutaAjustes.extend(['planoCielo_coefX'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=1, 1] -> aCeldasCoeficientesMdc[nX, nY, 1]
                    listaFilesSinRutaAjustes.extend(['planoCielo_coefY'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=1, 2] -> aCeldasCoeficientesMdc[nX, nY, 2]
                if GLO.GLBLgrabarEcmrMdcFinal:
                    listaFilesSinRutaAjustes.extend(
                        ['planoCielo_EcmrFinal']
                    )  # aCeldasCoeficientesMdxAll[nX, nY, nTP=1, 3] -> aCeldasCoeficientesMdc[nX, nY, 3]
                if GLO.GLBLgrabarEcmrMdcInicial:
                    listaFilesSinRutaAjustes.extend(
                        ['planoCielo_EcmrInicial']
                    )  # aCeldasCoeficientesMdxAll[nX, nY, nTP=1, 5] -> aCeldasCoeficientesMdc[nX, nY, 5]
            if GLO.GLBLcalcularMdm and GLO.GLBLgrabarMdm:
                listaFilesSinRutaAjustes.extend(['planoMajor_intercept'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=2, 1] -> aCeldasCoeficientesMdm[nX, nY, 1]
                listaFilesSinRutaAjustes.extend(['planoMajor_nPuntos'])  # aCeldasNumPuntosAjusteMajor[nX, nY]
                if GLO.GLBLgrabarCoeficientesXY:
                    listaFilesSinRutaAjustes.extend(['planoMajor_coefX'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=2, 1] -> aCeldasCoeficientesMdm[nX, nY, 1]
                    listaFilesSinRutaAjustes.extend(['planoMajor_coefY'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=2, 2] -> aCeldasCoeficientesMdm[nX, nY, 2]
                if GLO.GLBLgrabarEcmr:
                    listaFilesSinRutaAjustes.extend(['planoMajor_Ecmr'])  # aCeldasCoeficientesMdxAll[nX, nY, nTP=2, 3] -> aCeldasCoeficientesMdm[nX, nY, 3]
                    listaFilesSinRutaAjustes.extend(
                        ['planoMajor_EcmrInicial']
                    )  # aCeldasCoeficientesMdxAll[nX, nY, nTP=2, 5] -> aCeldasCoeficientesMdm[nX, nY, 5]
            if (GLO.GLBLcalcularMdg or GLO.GLBLcalcularMdp) and GLO.GLBLgrabarMdgAjusteCelda:
                if GLO.GLBLgrabarInterceptMdg:
                    listaFilesSinRutaAjustes.extend(['CeldasMdgCota'])
                if GLO.GLBLgrabarCoeficientesXY:
                    listaFilesSinRutaAjustes.extend(['CeldasMdgPteX'])
                    listaFilesSinRutaAjustes.extend(['CeldasMdgPteY'])
                if GLO.GLBLgrabarEcmrMdg:
                    listaFilesSinRutaAjustes.extend(['CeldasMdgEcmr'])
                    listaFilesSinRutaAjustes.extend(['CeldasMdgUnderPoint'])
            if GLO.GLBLgrabarInterpoladoMdx:
                # ->ATENCION: ESTOS FICHEROS SE GRABAN EN clidnv5.py CON EL NOMBRE:
                #  'planoSuelo_intercept_interpolado' y 'planoBasal_intercept_interpolado'
                #  LO TENGO INHABILITADO TEMPORALMENTE
                # ->Se calculan en clidnv3 y clidnv5 (incluye revisar la capa e interpolar las celdas dudosas):
                #  clidnv3.detectarAgua{} y clidnv3.guardarAgua{}
                #  clidnv3.controlarCalidadTopografica{} y clidnv3.guardarCalidadTopografica{} -> antes y despues de clidnv5.interpolarPlanos{}
                #  clidnv3.controlarCalidadDelAjuste{} y clidnv3.guardarCalidadDelAjuste{}
                #  clidnv5.interpolarPlanos{}, que incluye guardarAjustesMdsPostInterpol<> y guardarAjustesMdbPostInterpol<>
                if GLO.GLBLcalcularMds and GLO.GLBLcontrolarCalidadMds:
                    listaFilesSinRutaAjustes.extend(['planoSuelo_intercept_interpolado'])  # aCeldasCoeficientesMds RECALCULADO
                    # listaFilesSinRutaAjustes.extend(['planoSuelo_intercept_interpolado1'])  # aCeldasCoeficientesMds RECALCULADO
                    if GLO.GLBLgrabarCoeficientesXY:
                        listaFilesSinRutaAjustes.extend(['planoSuelo_coefX_interpolado',
                                                         'planoSuelo_coefY_interpolado'])  # aCeldasCoeficientesMds RECALCULADO
                if GLO.GLBLcalcularMdb and GLO.GLBLcontrolarCalidadMdb and GLO.GLBLgrabarMdbPosInterpol:
                    listaFilesSinRutaAjustes.extend(['planoBasal_intercept_interpolado'])  # aCeldasCoeficientesMdb_ RECALCULADO
                    # listaFilesSinRutaAjustes.extend(['planoBasal_intercept_interpolado1'])  # aCeldasCoeficientesMdb_ RECALCULADO
                    if GLO.GLBLgrabarCoeficientesXY:
                        listaFilesSinRutaAjustes.extend(['planoBasal_coefX_interpolado'])  # aCeldasCoeficientesMdb_ RECALCULADO
                        listaFilesSinRutaAjustes.extend(['planoBasal_coefY_interpolado'])  # aCeldasCoeficientesMdb_ RECALCULADO

            for fileText in listaFilesSinRutaAjustes:
                if fileText.lower().startswith('planosuelo'.lower()):
                    if fileText.lower().startswith('planosuelo_intercept'.lower()):
                        fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Suelo/mdt/', '%s_%s.asc' % (fileCoord, fileText))
                    else:
                        fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Suelo/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('planobasal'.lower()):
                    if fileText.lower().startswith('planoBasal_intercept'.lower()):
                        fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Basal/mdt/', '%s_%s.asc' % (fileCoord, fileText))
                    else:
                        fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Basal/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdb'.lower()):
                    if GLO.GLBLverbose:
                        print('cliddata-> Creando output dir para SubCeldasMdb*')
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/Basal/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdkCotaItp'.lower()):
                    if GLO.GLBLverbose:
                        print('cliddata-> Creando output dir para SubCeldasMdkCotaItp')
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/Klass/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdk'.lower()):
                    if GLO.GLBLverbose:
                        print('cliddata-> Creando output dir para SubCeldasMdk*')
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/Klass/SinInterpol', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdc'.lower()):
                    if GLO.GLBLverbose:
                        print('cliddata-> Creando output dir para SubCeldasMdc*')
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/Cielo/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('celdasMdg'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Global/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('planocielo'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Cielo/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('planoglobal'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Global/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('planomajor'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Major/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('planogridd'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Gridd/', '%s_%s.asc' % (fileCoord, fileText))
                else:
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaAjustes.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            arrayFilesSinRuta.append(listaFilesSinRutaAjustes)
            arrayFilesConRuta.append(listaFilesConRutaAjustes)
            arrayFilesNombreLote.append('Ajustes')
        # ======================================================================

        # ======================================================================
        if GLO.GLBLcalcularMdp or GLO.GLBLcalcularMdr or (
            GLO.GLBLcalcularMdg
            and GLO.GLBLcalcularSubCeldas
            and GLO.GLBLgrabarMdgAjusteSubCelda
            ):
            listaFilesSinRutaAjustesMdp = []
            listaFilesConRutaAjustesMdp = []
            if GLO.GLBLcalcularMdp and GLO.GLBLcalcularSubCeldas and GLO.GLBLgrabarCotaMinMaxSubCelda:  # Mde/02mCell/CotaMinMax/
                listaFilesSinRutaAjustesMdp.extend(['SubCeldasCotaMiniMacroEsOk'])  # aSubCeldasCotaMiniMacroEsOk
                listaFilesSinRutaAjustesMdp.extend(['SubCeldasCotaMiniMicroEsOk'])  # aSubCeldasCotaMiniMicroEsOk
            if GLO.GLBLcalcularMdp:
                if GLO.GLBLgrabarMdpAjusteCelda:  # Mde/10mCell/Pleno/
                    listaFilesSinRutaAjustesMdp.extend(['CeldasMdpCota'])  # aCeldasMdpAjuste
                    if GLO.GLBLgrabarCoeficientesXYMdp:
                        listaFilesSinRutaAjustesMdp.extend(['CeldasMdpPteX'])  # aCeldasMdpAjuste
                        listaFilesSinRutaAjustesMdp.extend(['CeldasMdpPteY'])  # aCeldasMdpAjuste
                    if GLO.GLBLgrabarEcmrMdp:
                        listaFilesSinRutaAjustesMdp.extend(['CeldasMdpEcmr'])  # aCeldasMdpAjuste
                        listaFilesSinRutaAjustesMdp.extend(['CeldasMdpOctn'])  # aCeldasMdpAjuste
                if GLO.GLBLgrabarMdpInfoAuxiliar:  # Mde/10mCell/Pleno/Auxiliar/
                    listaFilesSinRutaAjustesMdp.extend(['CeldasMdpNumPtosMiniMacro'])  # aCeldasMdpNumPtosMiniMacro
                    listaFilesSinRutaAjustesMdp.extend(['CeldasMdpNumPtosMiniMicro'])  # aCeldasMdpNumPtosMiniMicro
                if GLO.GLBLcalcularSubCeldas:
                    listaFilesSinRutaAjustesMdp.extend(['SubCeldasPuntoMiniSubCelValidado'])  # aSubCeldasPuntoMiniSubCelValidado
            if GLO.GLBLcalcularSubCeldas:
                if GLO.GLBLcalcularMdg and GLO.GLBLgrabarMdgAjusteSubCelda:  # Mde/02mCell/Global/
                    if GLO.GLBLgrabarInterceptMdg:
                        listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdgCota'])  # aSubCeldasMdgAjuste
                    if GLO.GLBLgrabarCoeficientesXYMdg:
                        listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdgPteX'])  # aSubCeldasMdgAjuste
                        listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdgPteY'])  # aSubCeldasMdgAjuste
                    if GLO.GLBLgrabarEcmrMdg:
                        listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdgEcmr'])  # aSubCeldasMdgAjuste
                if GLO.GLBLcalcularMdp:
                    if GLO.GLBLgrabarMdpCotaSubceldaMacroMicro:  # Mde/Pleno/02mCell/
                        listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdpCotaMacroManual'])  # aSubCeldasMdpCotaMacroManual
                        listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdpCotaMicroManual'])  # aSubCeldasMdpCotaMicroManual
                    if GLO.GLBLgrabarMdfCotaSubcelda:  # Mde/02mCell/Final/
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConMetodoManualPuro:
                            listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdfCotaManual'])  # aSubCeldasMdfCotaManual
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModeloConvolucional:
                            listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdfCotaConvol'])  # aSubCeldasMdfCotaConvol
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModConvoManualizado:
                            listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdfCotaConual'])  # aSubCeldasMdfCotaConual
                    if GLO.GLBLgrabarMdfCotaSubceldaTransitoria:  # Mde/02mCell/Final/
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConMetodoManualPuro:
                            listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdfCotaTransitoriaManual'])  # aSubCeldasMdfCotaTransitoriaManual
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModeloConvolucional:
                            listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdfCotaTransitoriaConvol'])  # aSubCeldasMdfCotaTransitoriaConvol
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModConvoManualizado:
                            listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdfCotaTransitoriaConual'])  # aSubCeldasMdfCotaTransitoriaConual
                    if GLO.GLBLgrabarMdpInfoAuxiliar:  # Mde/02mCell/Pleno/Auxiliar/
                        listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdpTipoCotaMacroManual'])  # aSubCeldasMdpTipoCotaMacroManual
                        listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdpTipoCotaMicroManual'])  # aSubCeldasMdpTipoCotaMicroManual

            if GLO.GLBLcalcularMdr and GLO.GLBLgrabarMdr:  # Mde/10mCell/Grid/
                listaFilesSinRutaAjustesMdp.extend(['CeldasMdrGridNearest'])  # aCeldasMdrCoeficientes
                listaFilesSinRutaAjustesMdp.extend(['CeldasMdrGridLinear'])  # aCeldasMdrCoeficientes
                listaFilesSinRutaAjustesMdp.extend(['CeldasMdrGridCubic'])  # aCeldasMdrCoeficientes
                if GLO.GLBLcalcularCotaDeSubceldasConGriddata:  # Mde/02mCell/Grid/
                    listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdrGridPtoMinor'])  # aSubCeldasMdrCotaInterpolada
                    listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdrGridNearest'])  # aSubCeldasMdrCotaInterpolada
                    listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdrGridLinear'])  # aSubCeldasMdrCotaInterpolada
                    listaFilesSinRutaAjustesMdp.extend(['SubCeldasMdrGridCubic'])  # aSubCeldasMdrCotaInterpolada

            for fileText in listaFilesSinRutaAjustesMdp:
                if fileText.lower().startswith('CeldaMdp'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Pleno/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdp'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/Pleno/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdg'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/Global/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdf'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/Final/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('CeldasMdpNumPtosMini'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Pleno/Auxiliar/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdpTipoCota'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Pleno/Auxiliar/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('CeldasMdrGrid'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/10mCell/Grid/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasMdrGrid'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/Grid/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasCotaMiniM'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CotaMinMax/02mCell/CotaMiniOk/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasCotaMin'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CotaMinMax/02mCell/CotaMin/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasCotaMax'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CotaMinMax/02mCell/CotaMax/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasPuntoMiniSubCelValidado'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/MiniSubCelClass/ClassSueloValidadaPorMdp/', '%s_%s.asc' % (fileCoord, fileText))

                elif fileText.lower().startswith('subCelda'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/02mCell/', '%s_%s.asc' % (fileCoord, fileText))
                else:
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'Mde/', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaAjustesMdp.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            arrayFilesSinRuta.append(listaFilesSinRutaAjustesMdp)
            arrayFilesConRuta.append(listaFilesConRutaAjustesMdp)
            arrayFilesNombreLote.append('AjustesMdp')
        # ======================================================================

        # ======================================================================
        if GLO.GLBLgrabarHiperFormas:
            listaFilesSinRutaHiperFormas = []
            listaFilesConRutaHiperFormas = []
            if GLO.GLBLguardarCapaRugosidadInterCeldillasCeldas:  # HiperCubo/Rugosidad/10mCell/
                listaFilesSinRutaHiperFormas.extend(['CeldasRugosidadMacroInterCeldillas'])  # aCeldasRugosidadMacroInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['CeldasRugosidadMesosInterCeldillas'])  # aCeldasRugosidadMesosInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['CeldasRugosidadMicroInterCeldillas'])  # aCeldasRugosidadMicroInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['CeldasRugosidadMegasInterCeldillas'])  # aCeldasRugosidadMegasInterCeldillas
            if GLO.GLBLguardarCapaRugosidadInterCeldillasSubCeldas:  # HiperCubo/Rugosidad/02mCell/
                listaFilesSinRutaHiperFormas.extend(['SubCeldasRugosidadMacroInterCeldillas'])  # aSubCeldasRugosidadMacroInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['SubCeldasRugosidadMesosInterCeldillas'])  # aSubCeldasRugosidadMesosInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['SubCeldasRugosidadMicroInterCeldillas'])  # aSubCeldasRugosidadMicroInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['SubCeldasRugosidadMegasInterCeldillas'])  # aSubCeldasRugosidadMegasInterCeldillas
            if GLO.GLBLguardarCapaRugosidadInterCeldillasMetrico:  # HiperCubo/Rugosidad/01mCell/
                listaFilesSinRutaHiperFormas.extend(['MetricoRugosidadMacroInterCeldillas'])  # aMetricoRugosidadMacroInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['MetricoRugosidadMesosInterCeldillas'])  # aMetricoRugosidadMesosInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['MetricoRugosidadMicroInterCeldillas'])  # aMetricoRugosidadMicroInterCeldillas
                listaFilesSinRutaHiperFormas.extend(['MetricoRugosidadMegasInterCeldillas'])  # aMetricoRugosidadMegasInterCeldillas
            if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoCeldas:  # HiperCubo/Tejado/10mCell/
                listaFilesSinRutaHiperFormas.extend(['CeldasNumeroDePlanosTejado'])  # aCeldasNumeroDePlanosTejado
                listaFilesSinRutaHiperFormas.extend(['CeldasPuntosEnPlanosTejado'])  # aCeldasPuntosEnPlanosTejado
            if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoSubCeldas:  # HiperCubo/Tejado/02mCell/
                listaFilesSinRutaHiperFormas.extend(['SubCeldasPlanoTejado'])  # aSubCeldasPlanoTejado
            if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoMetrico:  # HiperCubo/Tejado/01mCell/
                listaFilesSinRutaHiperFormas.extend(['MetricoPlanoTejado'])  # aMetricoPlanoTejado
            for fileText in listaFilesSinRutaHiperFormas:
                if fileText.lower().startswith('CeldasRugosidad'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'HiperCubo/10mCell/Rugosidad/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasRugosidad'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'HiperCubo/02mCell/Rugosidad/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('MetricoRugosidad'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'HiperCubo/01mCell/Rugosidad/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText == 'CeldasPuntosEnPlanosTejado' or fileText == 'CeldasNumeroDePlanosTejado':
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'HiperCubo/10mCell/Tejado/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('SubCeldasPlanoTejado'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'HiperCubo/02mCell/Tejado/', '%s_%s.asc' % (fileCoord, fileText))
                elif fileText.lower().startswith('MetricoPlanoTejado'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'HiperCubo/01mCell/Tejado/', '%s_%s.asc' % (fileCoord, fileText))
                else:
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'HiperCubo/', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaHiperFormas.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            arrayFilesSinRuta.append(listaFilesSinRutaHiperFormas)
            arrayFilesConRuta.append(listaFilesConRutaHiperFormas)
            arrayFilesNombreLote.append('HiperFormas')
        # ======================================================================

        # ======================================================================
        if GLO.GLBLgrabarIndicesVegetacionNDVIetAlSubCelda or GLO.GLBLgrabarIndicesVegetacionNDVIetAlMetricos:
            listaFilesSinRutaRGBI = []
            listaFilesConRutaRGBI = []
            if GLO.GLBLgrabarIndicesVegetacionNDVIetAlSubCelda:  # RGBI/02mCell/***/
                if GLO.GLBLgrabarIndicesVegetacionIntSRet:  # RGBI/02mCell/IntSRet/
                    fileText = 'SubCeldasIntSRetMed'
                    listaFilesSinRutaRGBI.extend([fileText])  # aSubCeldasIntSRetMed
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/02mCell/IntSRet/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
                if GLO.GLBLgrabarIndicesVegetacionIntMRet:  # RGBI/02mCell/IntMRet/
                    fileText = 'SubCeldasIntMRetMed'
                    listaFilesSinRutaRGBI.extend([fileText])  # aSubCeldasIntMRetMed
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/02mCell/IntMRet/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
                if GLO.GLBLgrabarIndicesVegetacionEVI2:  # RGBI/02mCell/EVI2/
                    fileText = 'SubCeldasEVI2'
                    listaFilesSinRutaRGBI.extend([fileText])  # aSubCeldasEVI2Med
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/02mCell/EVI2/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
                if GLO.GLBLgrabarIndicesVegetacionNDVI:  # RGBI/02mCell/NDVI/
                    fileText = 'SubCeldasNDVI'
                    listaFilesSinRutaRGBI.extend([fileText])  # aSubCeldasNDVIMed
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/02mCell/NDVI/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
                if GLO.GLBLgrabarIndicesVegetacionNDWI:  # RGBI/02mCell/NDWI/
                    fileText = 'SubCeldasNDWI'
                    listaFilesSinRutaRGBI.extend([fileText])  # aSubCeldasNDWIMed
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/02mCell/NDWI/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
            if GLO.GLBLgrabarIndicesVegetacionNDVIetAlMetricos:  # RGBI/01mCell/***/
                if GLO.GLBLgrabarIndicesVegetacionIntSRet:  # RGBI/01mCell/IntSRet/
                    fileText = 'MetricoIntSRet'
                    listaFilesSinRutaRGBI.extend([fileText])  # a01mCell/IntSRet
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/01mCell/IntSRet/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
                if GLO.GLBLgrabarIndicesVegetacionEVI2:  # RGBI/01mCell/EVI2/
                    fileText = 'MetricoEVI2'
                    listaFilesSinRutaRGBI.extend([fileText])  # a01mCell/EVI2Med
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/01mCell/EVI2/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
                if GLO.GLBLgrabarIndicesVegetacionNDVI:  # RGBI/01mCell/NDVI/
                    fileText = 'MetricoNDVI'
                    listaFilesSinRutaRGBI.extend([fileText])  # a01mCell/NDVIMed
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/01mCell/NDVI/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
                if GLO.GLBLgrabarIndicesVegetacionNDWI:  # RGBI/01mCell/NDWI/
                    fileText = 'MetricoNDWI'
                    listaFilesSinRutaRGBI.extend([fileText])  # a01mCell/NDWIMed
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RGBI/01mCell/NDWI/', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaRGBI.append(fileNameConRuta)
            for fileNum, fileText in enumerate(listaFilesSinRutaRGBI):
                dictFilesSinConRuta[fileText] = listaFilesConRutaRGBI[fileNum]
            arrayFilesSinRuta.append(listaFilesSinRutaRGBI)
            arrayFilesConRuta.append(listaFilesConRutaRGBI)
            arrayFilesNombreLote.append('RGBI')
        # ======================================================================

        # ======================================================================
        if (
            GLO.GLBLcalcularMdp
            and GLO.GLBLcalcularSubCeldas
            and (
                GLO.GLBLguardarLateralidadInterSubCeldasMinMax
                or GLO.GLBLguardarLateralidadInterSubCeldasMinMin
                or GLO.GLBLguardarRugosidadInterSubCeldas
                or GLO.GLBLguardarRugosidadMultiCeldas
                or GLO.GLBLcrearTilesPostVuelta1
            )
        ):
            listaFilesSinRutaRugoLateralidad = []
            listaFilesConRutaRugoLateralidad = []
            if GLO.GLBLrugosidadExplorandoCeldasColindantes:
                conSincolindantes = 'InclColindantes'
            else:
                conSincolindantes = 'ExclColindantes'
            if GLO.GLBLguardarLateralidadInterSubCeldasMinMax:
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasLateralidadMinMaxMacro'])  # aSubCeldasLateralidadMinMaxMacro
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasLateralidadMinMaxMesos'])  # aSubCeldasLateralidadMinMaxMesos
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasLateralidadMinMaxMicro'])  # aSubCeldasLateralidadMinMaxMicro
            if GLO.GLBLguardarLateralidadInterSubCeldasMinMin:
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasLateralidadMinMinMacro'])  # aSubCeldasLateralidadMinMinMacro
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasLateralidadMinMinMesos'])  # aSubCeldasLateralidadMinMinMesos
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasLateralidadMinMinMicro'])  # aSubCeldasLateralidadMinMinMicro
            if GLO.GLBLguardarRugosidadInterSubCeldas:
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasRugosidadMacroInterSubCeldas'])  # aSubCeldasRugosidadMinMaxMacroInterSubCeldas
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasRugosidadMesosInterSubCeldas'])  # aSubCeldasRugosidadMinMaxMesosInterSubCeldas
                listaFilesSinRutaRugoLateralidad.extend(['SubCeldasRugosidadMicroInterSubCeldas'])  # aSubCeldasRugosidadMinMaxMicroInterSubCeldas
            if GLO.GLBLguardarRugosidadMultiCeldas:
                listaFilesSinRutaRugoLateralidad.extend(
                    ['MultiCeldasRugosidadMacroInterSubCeldasCrit%i%s' % (GLO.GLBLcriterioParaEvaluarLaRugosidad, conSincolindantes)]
                )  # aMultiCeldasRugosidadMacroInterSubCeldas
                listaFilesSinRutaRugoLateralidad.extend(
                    ['MultiCeldasRugosidadMesosInterSubCeldasCrit%i%s' % (GLO.GLBLcriterioParaEvaluarLaRugosidad, conSincolindantes)]
                )  # aMultiCeldasRugosidadMesosInterSubCeldas
                listaFilesSinRutaRugoLateralidad.extend(
                    ['MultiCeldasRugosidadMicroInterSubCeldasCrit%i%s' % (GLO.GLBLcriterioParaEvaluarLaRugosidad, conSincolindantes)]
                )  # aMultiCeldasRugosidadMicroInterSubCeldas
            if GLO.GLBLgrabarMdpInfoAuxiliar:
                listaFilesSinRutaRugoLateralidad.extend(['MultiCeldasEstruct'])  # RugoLateralidad/MultiCelda/Auxiliar/
            for fileText in listaFilesSinRutaRugoLateralidad:
                if (fileText.lower()).startswith('SubCeldasLateralidadMinMax'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RugoLateralidad/02mCell/LateralidadMinMax/', '%s_%s.asc' % (fileCoord, fileText))
                elif (fileText.lower()).startswith('SubCeldasLateralidadMinMin'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RugoLateralidad/02mCell/LateralidadMinMin/', '%s_%s.asc' % (fileCoord, fileText))
                elif (fileText.lower()).startswith('SubCeldasRugosidad'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RugoLateralidad/02mCell/Rugosidad/', '%s_%s.asc' % (fileCoord, fileText))
                elif (fileText.lower()).startswith('MultiCeldas'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RugoLateralidad/10mCell/MultiCelda/', '%s_%s.asc' % (fileCoord, fileText))
                elif (fileText.lower()).startswith('MultiCeldasEstruct'.lower()):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RugoLateralidad/10mCell/MultiCelda/Auxiliar/', '%s_%s.asc' % (fileCoord, fileText))
                else:
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'RugoLateralidad/', '%s_%s.asc' % (fileCoord, fileText))

                listaFilesConRutaRugoLateralidad.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            arrayFilesSinRuta.append(listaFilesSinRutaRugoLateralidad)
            arrayFilesConRuta.append(listaFilesConRutaRugoLateralidad)
            arrayFilesNombreLote.append('RugoLateralidad')
        # ======================================================================

        # ======================================================================
        listaFilesSinRutaZonasSingulares = []
        listaFilesConRutaZonasSingulares = []
        if GLO.GLBLmasasDeAgua:
            fileText = 'CeldasMasasDeAgua'
            listaFilesSinRutaZonasSingulares.extend([fileText])  # aCeldasMasasDeAgua
            fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/Agua/', '%s_%s.asc' % (fileCoord, fileText))
            listaFilesConRutaZonasSingulares.append(fileNameConRuta)
            dictFilesSinConRuta[fileText] = fileNameConRuta
        if GLO.GLBLgrabarNucleosDeCartoRef and self.UsarNucleosUrbanos:
            fileText = 'CeldasNucleosUrbanosDeCartoRef'
            listaFilesSinRutaZonasSingulares.extend([fileText])  # cartoRefNucleosUrbanos_aCeldasLandUseCover
            fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/CartoRefNucleos/', '%s_%s.asc' % (fileCoord, fileText))
            listaFilesConRutaZonasSingulares.append(fileNameConRuta)
            dictFilesSinConRuta[fileText] = fileNameConRuta
        if GLO.GLBLgrabarSingUseDeCartoRef and self.UsarUsoSingular:
            fileText = 'CeldasUsosSingularesDeCartoRef'
            listaFilesSinRutaZonasSingulares.extend([fileText])  # cartoRefUsoSingular_aCeldasLandUseCover
            fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/CartoRefSingUse/CoverOriginal/', '%s_%s.asc' % (fileCoord, fileText))
            listaFilesConRutaZonasSingulares.append(fileNameConRuta)
            dictFilesSinConRuta[fileText] = fileNameConRuta

        if GLO.GLBLgrabarMiniSubCelClassOriginal:
            if GLO.GLBLgrabarMiniSubCelClassOrigCompleta:
                fileText = 'SubCeldasPuntoMiniSubCelPsuePsel_classOrigCompleta'
                listaFilesSinRutaZonasSingulares.extend([fileText])  # aSubCeldasPuntoMiniSubCelPsuePsel[]['lasClassOriginal']
                fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/MiniSubCelClass/ClassOriginal/Completa', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            if GLO.GLBLgrabarMiniSubCelClassOrig_2_345_6:
                fileText = 'SubCeldasPuntoMiniSubCelPsuePsel_classOrig_2_345_6'
                listaFilesSinRutaZonasSingulares.extend([fileText])  # aSubCeldasPuntoMiniSubCelPsuePsel[]['lasClass_2_345_6']
                fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/MiniSubCelClass/ClassOriginal/_2_345_6', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            if GLO.GLBLgrabarMiniSubCelClassOrig_Binaria:
                fileText = 'SubCeldasPuntoMiniSubCelPsuePsel_classOrig_Binaria'
                listaFilesSinRutaZonasSingulares.extend([fileText])  # aSubCeldasPuntoMiniSubCelPsuePsel[]['lasClass_Binaria']
                fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/MiniSubCelClass/ClassOriginal/_Binaria', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            if GLO.GLBLgrabarDiscrepanciaCartoRefVsLasClassMiniSub:
                fileText = 'SubCeldasDiscrepanciaCartoRefVsLasClassMiniSubCel'
                listaFilesSinRutaZonasSingulares.extend([fileText])  # aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['lasClassOriginal'] & aSubCeldasPuntoMiniSubCelPsuePsel[nX, nY]['usoSingular']
                fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/MiniSubCelClass/ClassOriginal/Discrepa', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
        if GLO.GLBLgrabarMiniSubCelClassPredict and GLO.GLBLcrearTilesPostVuelta1:
            fileText = 'SubCeldasMiniSubCelLasClassPredicha'
            listaFilesSinRutaZonasSingulares.extend([fileText])  # aSubCeldasMiniSubCelLasClassPredicha
            fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/MiniSubCelClass/ClassPredichaConvolucional/', '%s_%s.asc' % (fileCoord, fileText))
            listaFilesConRutaZonasSingulares.append(fileNameConRuta)
            dictFilesSinConRuta[fileText] = fileNameConRuta
            if GLO.GLBLgrabarMultiTiles:
                fileText = 'MultiTilesMiniSubCelLasClassPredicha'
                listaFilesSinRutaZonasSingulares.extend([fileText])  # aMultiTilesMiniSubCelLasClassPredicha
                fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/MiniSubCelClass/ClassPredichaMultiTiles/', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta

        if GLO.GLBLgrabarLandSubCelCoverPredict and GLO.GLBLcrearTilesPostVuelta1 and GLO.GLBLcalcularSubCeldas:
            if GLO.GLBLmodeloCartolidCartoSinguEntrenadoA:
                fileText = 'SubCeldasCartoSinguLandTypePredichaA'
                listaFilesSinRutaZonasSingulares.extend([fileText])  # aSubCeldasCartoSinguLandTypePredichaA
                fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/CartoRefSingUse/CoverPredichoASubCel', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            if GLO.GLBLmodeloCartolidCartoSinguEntrenadoB:
                fileText = 'SubCeldasCartoSinguLandTypePredichaB'
                listaFilesSinRutaZonasSingulares.extend([fileText])  # aSubCeldasCartoSinguLandTypePredichaB
                fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/CartoRefSingUse/CoverPredichoBSubCel', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            if GLO.GLBLgrabarMultiTiles:
                if GLO.GLBLmodeloCartolidCartoSinguEntrenadoA:
                    fileText = 'MultiTilesCartoSinguLandTypePredichaA'
                    listaFilesSinRutaZonasSingulares.extend([fileText])  # aMultiTilesCartoSinguLandTypePredichaA
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/CartoRefSingUse/CoverPredichoAMultiTiles', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                    dictFilesSinConRuta[fileText] = fileNameConRuta
                if GLO.GLBLmodeloCartolidCartoSinguEntrenadoB:
                    fileText = 'MultiTilesCartoSinguLandTypePredichaB'
                    listaFilesSinRutaZonasSingulares.extend([fileText])  # aMultiTilesCartoSinguLandTypePredichaB
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'convolLasClassLandCover/CartoRefSingUse/CoverPredichoBMultiTiles', '%s_%s.asc' % (fileCoord, fileText))
                    listaFilesConRutaZonasSingulares.append(fileNameConRuta)
                    dictFilesSinConRuta[fileText] = fileNameConRuta
        arrayFilesSinRuta.append(listaFilesSinRutaZonasSingulares)
        arrayFilesConRuta.append(listaFilesConRutaZonasSingulares)
        arrayFilesNombreLote.append('ZonasSingulares')
        # ======================================================================

        # ======================================================================
        if GLO.GLBLgrabarExtrasMdsMdbMdc and GLO.GLBLgrabarInterpoladoMdx:
            listaFilesSinRutaFormas = []
            listaFilesConRutaFormas = []
            # Se calculan con clidnv3.controlarCalidadTopografica{} y se guardan con:
            #  ->myLasData.guardarCalidadTopografica{}
            #  ->myLasData.guardarCalidadDelAjuste{}
            if GLO.GLBLcalcularMds and GLO.GLBLcontrolarCalidadMds:
                listaFilesSinRutaFormas.extend(['planoSuelo_NumDisrupciones0'])  # aCeldasNumDisrupciones[nX, nY, nTP=0, nFase=0]
                # En clidflow.py solo tengo etapa = 0  #'0PreInterUrb' y nFase = 0, por lo que no uso _NumDisrupciones1 
                # listaFilesSinRutaFormas.extend(['planoSuelo_NumDisrupciones1'])  # aCeldasNumDisrupciones[nX, nY, nTP=0, nFase=1]
                listaFilesSinRutaFormas.extend(['planoSuelo_NoFiable_PorCalidadDelAjuste'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=0]
                # listaFilesSinRutaFormas.extend(['planoSuelo_NoFiable_PorCausasPte1'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=0]
                # listaFilesSinRutaFormas.extend(['planoSuelo_NoFiable_PorCausasPte2'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=0]
                listaFilesSinRutaFormas.extend(['planoSuelo_RangoCotasEnCeldaConPuntosSumergidos'])
                listaFilesSinRutaFormas.extend(
                    ['planoSuelo_ConPtosSumergidos']
                )  # errorResidualMasNegativo -> miCeldaCoeficientesMdx[4] -> clidnaux.asignarCoeficientesMdxPorTipoPlanoXY(nX, nY, nTP, etc)
            if GLO.GLBLcalcularMdb and GLO.GLBLcontrolarCalidadMdb:
                listaFilesSinRutaFormas.extend(['planoBasal_NumDisrupciones0'])  # aCeldasNumDisrupciones[nX, nY, nTP=1, nFase=0]
                # En clidflow.py solo tengo etapa = 0  #'0PreInterUrb' y nFase = 0, por lo que no uso _NumDisrupciones1 
                # listaFilesSinRutaFormas.extend(['planoBasal_NumDisrupciones1'])  # aCeldasNumDisrupciones[nX, nY, nTP=1, nFase=1]
                listaFilesSinRutaFormas.extend(['planoBasal_NoFiable_PorCalidadDelAjuste'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=1]
                # listaFilesSinRutaFormas.extend(['planoBasal_NoFiable_PorCausasPte1'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=1]
                # listaFilesSinRutaFormas.extend(['planoBasal_NoFiable_PorCausasPte2'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=1]
                listaFilesSinRutaFormas.extend(
                    ['planoBasal_ConPtosSumergidos']
                )  # errorResidualMasNegativo -> miCeldaCoeficientesMdx[4] -> clidnaux.asignarCoeficientesMdxPorTipoPlanoXY(nX, nY, nTP, etc)
            if GLO.GLBLcalcularMdc and GLO.GLBLcontrolarCalidadMdc:
                listaFilesSinRutaFormas.extend(['planoCielo_NumDisrupciones0'])  # aCeldasNumDisrupciones[nX, nY, nTP=2, nFase=0]
                # En clidflow.py solo tengo etapa = 0  #'0PreInterUrb' y nFase = 0, por lo que no uso _NumDisrupciones1 
                # listaFilesSinRutaFormas.extend(['planoCielo_NumDisrupciones1'])  # aCeldasNumDisrupciones[nX, nY, nTP=2, nFase=1]
                listaFilesSinRutaFormas.extend(['planoCielo_NoFiable_PorCalidadDelAjuste'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=2]
                # listaFilesSinRutaFormas.extend(['planoCielo_NoFiable_PorCausasPte1'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=2]
                # listaFilesSinRutaFormas.extend(['planoCielo_NoFiable_PorCausasPte2'])  # aCeldasConAjusteNoFiable[nX, nY, nTP=2]
                listaFilesSinRutaFormas.extend(
                    ['planoCielo_ConPtosSumergidos']
                )  # errorResidualMasNegativo -> miCeldaCoeficientesMdx[4] -> clidnaux.asignarCoeficientesMdxPorTipoPlanoXY(nX, nY, nTP, etc)
            for fileText in listaFilesSinRutaFormas:
                if (fileText.lower()).startswith('planosuelo'):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CalidadTopoAjuste/Suelo/', '%s_%s.asc' % (fileCoord, fileText))
                elif (fileText.lower()).startswith('planobasal'):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CalidadTopoAjuste/Basal/', '%s_%s.asc' % (fileCoord, fileText))
                elif (fileText.lower()).startswith('planocielo'):
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CalidadTopoAjuste/Cielo/', '%s_%s.asc' % (fileCoord, fileText))
                else:
                    fileNameConRuta = os.path.join(GLO.MAINrutaOutput,'CalidadTopoAjuste/', '%s_%s.asc' % (fileCoord, fileText))
                listaFilesConRutaFormas.append(fileNameConRuta)
                dictFilesSinConRuta[fileText] = fileNameConRuta
            arrayFilesSinRuta.append(listaFilesSinRutaFormas)
            arrayFilesConRuta.append(listaFilesConRutaFormas)
            arrayFilesNombreLote.append('Formas')
        # ======================================================================

        # ======================================================================
        # ======================================================================
        if GLO.GLBLverbose:
            print('cliddata-> Mostrando listas de ficheros que se generan (numero de lotes de ficheros:= {}):'.format(len(arrayFilesSinRuta)))
            if len(arrayFilesSinRuta) != len(arrayFilesConRuta):
                print('cliddata-> Corregir error en lista de ficheros (1)')
                print('\tlen(arrayFilesSinRuta):', len(arrayFilesSinRuta))
                print('\tlen(arrayFilesConRuta):', len(arrayFilesConRuta))
            nContadorFicheros = 0
            for nLista in range(len(arrayFilesSinRuta)):
                print('Lote {} {}'.format(nLista, arrayFilesNombreLote[nLista]))
                listaFileType = arrayFilesSinRuta[nLista]
                listaFileName = arrayFilesConRuta[nLista]
                if len(listaFileType) > 0 and len(listaFileType) == len(listaFileName):
                    for nFichero in range(len(listaFileType)):
                        if listaFileType[nFichero] != '':
                            nContadorFicheros += 1
                            print(str(listaFileType[nFichero]).rjust(50), '->', listaFileName[nFichero])
                elif len(listaFileType) == 0 and len(listaFileName) == 0:
                    pass
                else:
                    print('cliddata-> Corregir error en lista de ficheros (2)')
                    print('\tlistaFileType:', len(listaFileType), listaFileType)
                    print('\tlistaFileName:', len(listaFileName), listaFileName)
            # Verifico que el numero de ficheros en arrayFilesConRuta y arrayFilesSinRuta es igual al de dictFilesSinConRuta
            print('cliddata-> Numero de ficheros a generar para cada bloque: {}={}'.format(nContadorFicheros, len(dictFilesSinConRuta)))
        # ======================================================================
        # ======================================================================

        # ======================================================================
        self.dictFilesSinConRuta = dictFilesSinConRuta
        self.arrayFilesSinRuta = arrayFilesSinRuta
        self.arrayFilesConRuta = arrayFilesConRuta
        self.listaFilesSinRutaAlts = listaFilesSinRutaAlts
        # ======================================================================

    
    # ==========================================================================
    def prepararOutputFiles(self):
        self.aFiles = {}
        totalFicheros = 0
        print(f'cliddata-> Creando output files con cabecera:')
        for fileSinRuta in self.dictFilesSinConRuta.keys():
            # ==================================================================
            miFileName = self.dictFilesSinConRuta[fileSinRuta]
            if os.path.exists(miFileName):
                try:
                    fileSizeKB = os.stat(miFileName).st_size / 1000
                    if (
                        GLO.GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb
                        and fileSizeKB > 1.0 # size en KB
                    ):
                        if GLO.GLBLverbose:
                            print(
                                'clidnat-> El fichero {} ya existe con {} Kb; NO se crea uno nuevo.'.format(
                                    miFileName,
                                    fileSizeKB
                                )
                            )
                        self.aFiles[fileSinRuta] = None
                        continue
                    else:
                        if GLO.GLBLverbose:
                            print(
                                'clidnat-> El fichero {} ya existe con {} Kb; se elimina para generar uno nuevo.'.format(
                                    miFileName,
                                    fileSizeKB
                                )
                            )
                        try:
                            os.remove(miFileName)
                        except:
                            print('\tRevisar si el fichero {} esta bloqueado por otra aplicacion (error al intentar borrarlo)'.format(miFileName))
                            print('\tSe cambia GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb a True')
                            GLO.GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb = True
                            # sys.exit(0)
                        if os.path.exists(miFileName):
                            print('\tNo se ha podido eliminar el fichero asc existente: {}'.format(miFileName))
                            print('\tSe cambia GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb a True')
                            GLO.GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb = True
                except:
                    if os.path.exists(miFileName):
                        try:
                            os.remove(miFileName)
                        except:
                            print('\tcliddata: Aviso: revisar si el fichero {} esta bloqueado por otra aplicacion (error al intentar borrarlo)'.format(miFileName))
            # ==================================================================

            noData = GLO.GLBLnoData
            xInfIzda = self.myLasHead.xmin
            yInfIzda = self.myLasHead.ymin

            if GLO.GLBLverbose:
                print(f'{TB}-> Creando: {totalFicheros} {fileSinRuta} {self.dictFilesSinConRuta[fileSinRuta]}')

            if (
                str(fileSinRuta) == 'MultiTilesMiniSubCelLasClassPredicha'
                or str(fileSinRuta) == 'MultiTilesCartoSinguLandTypePredichaA'
                or str(fileSinRuta) == 'MultiTilesCartoSinguLandTypePredichaB'
            ):
                metrosPixel = GLO.GLBLmetrosCelda / GLBNsubCeldasPorCelda

                GLBNtileSizeEnPixelsSubCelda = int(math.ceil(GLO.GLBLtileSizeMetros / GLO.GLBLmetrosSubCelda)) # -> 128 ($256)
                GLBNtileSemiSolapePixelsSubCelda = int(math.floor(GLO.GLBLtileSemiSolapeMetros / GLO.GLBLmetrosSubCelda)) # -> 0 ($3)
                GLBNtileKernelMetros = (GLO.GLBLtileSizeMetros - (2 * GLO.GLBLtileSemiSolapeMetros)) # -> ($500)
                GLBNtileKernelPixelsSubCelda = (GLBNtileSizeEnPixelsSubCelda - (2 * GLBNtileSemiSolapePixelsSubCelda)) # -> ($250)
                nSubCeldasBloqueY = self.nCeldasY * GLBNsubCeldasPorCelda # -> 1000 ($1000)
                nSubCeldasBloqueX = self.nCeldasX * GLBNsubCeldasPorCelda # -> 1000 ($1000)
                numTilesRows = int(math.ceil(nSubCeldasBloqueY / GLBNtileSizeEnPixelsSubCelda)) # -> 8 ($4)
                numTilesCols = int(math.ceil(nSubCeldasBloqueX / GLBNtileSizeEnPixelsSubCelda)) # -> 8 ($4)
                margenXsobresalienteMetros = GLO.GLBLtileSemiSolapeMetros + (((numTilesCols * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> ($6.0)
                margenYsobresalienteMetros = GLO.GLBLtileSemiSolapeMetros + (((numTilesRows * GLBNtileKernelMetros) - GLO.GLBLmetrosBloque) / 2) # -> ($6.0)
                margenXsobresalientePixelsScA = int(math.floor(margenXsobresalienteMetros / GLO.GLBLmetrosSubCelda)) # -> ($3)
                margenXsobresalientePixelsScB = int(math.ceil(margenXsobresalienteMetros / GLO.GLBLmetrosSubCelda)) # -> ($3)
                margenYsobresalientePixelsScA = int(math.floor(margenYsobresalienteMetros / GLO.GLBLmetrosSubCelda)) # -> ($3)
                margenYsobresalientePixelsScB = int(math.ceil(margenYsobresalienteMetros / GLO.GLBLmetrosSubCelda)) # -> ($3)

                nCeldasX = GLBNtileKernelPixelsSubCelda * numTilesCols + margenXsobresalientePixelsScA + margenXsobresalientePixelsScB # 1006
                nCeldasY = GLBNtileKernelPixelsSubCelda * numTilesRows + margenYsobresalientePixelsScA + margenYsobresalientePixelsScB # 1006
                xInfIzda = self.myLasHead.xmin - margenXsobresalienteMetros # 24
                yInfIzda = self.myLasHead.ymin - margenYsobresalienteMetros # 24

            elif 'subcelda' in str(fileSinRuta).lower():
                # Capas de subCelda
                # ['SubCeldasMdbPreInterpol', 'SubCeldasMdbPostInterpol', 'SubCeldasMdbPost2Interpol',
                #  'SubCeldasMdkCotaMed, 'SubCeldasMdkCotaMin', 'SubCeldasMdkCotaItp', 'SubCeldasMdcCotaMax',
                #  'SubCeldasMdfCotaManual', 'SubCeldasMdfCotaConvol', 'SubCeldasMdfCotaConual',
                #  'SubCeldasMdfCotaTransitoriaManual', 'SubCeldasMdfCotaTransitoriaConvol', 'SubCeldasMdfCotaTransitoriaConual',
                #  'SubCeldasMdpCotaMacroManual', 'SubCeldasMdpCotaMicroManual',
                #  'SubCeldasCotaMin', 'SubCeldasCotaMax',
                #  'SubCeldasMdgCota', 'SubCeldasMdgPteX', 'SubCeldasMdgPteY', 'SubCeldasMdgEcmr',
                #  'SubCeldasIntSRetMed', 'SubCeldasIntMRetMed',
                #  'SubCeldasEVI2', 'SubCeldasNDVI', 'SubCeldasNDWI',
                #  'SubCeldasAlt95SobreMdf', 'SubCeldasAltMaxSobreMdf', 'SubCeldasAltMinSobreMdf']
                # ['SubCeldasMdrGridPtoMinor', 'SubCeldasMdrGridNearest', 'SubCeldasMdrGridLinear', 'SubCeldasMdrGridCubic']
                # ['SubCeldasMdpTipoCotaMacroManual', 'SubCeldasMdpTipoCotaMicroManual']
                # ['SubCeldasLateralidadMinMaxMacro', 'SubCeldasLateralidadMinMaxMesos', 'SubCeldasLateralidadMinMaxMicro',
                #  'SubCeldasLateralidadMinMinMacro', 'SubCeldasLateralidadMinMinMesos', 'SubCeldasLateralidadMinMinMicro']
                # ['SubCeldasRugosidad']
                # ['SubCeldasRugosidadMacroInterCeldillas', 'SubCeldasRugosidadMesosInterCeldillas', 'SubCeldasRugosidadMicroInterCeldillas', 'SubCeldasRugosidadMegasInterCeldillas']
                # ['SubCeldasPlanoTejado']
                # ['SubCeldasMiniSubCelLasClassPredicha']
                # ['SubCeldasCartoSinguLandTypePredichaA']
                # ['SubCeldasCartoSinguLandTypePredichaB']
                # ['SubCeldasPuntoMiniSubCelPsuePsel_classOrigCompleta']
                # ['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_2_345_6']
                # ['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_Binaria']
                # ['SubCeldasDiscrepanciaCartoRefVsLasClassMiniSubCel']
                metrosPixel = GLO.GLBLmetrosCelda / GLBNsubCeldasPorCelda
                nCeldasX = self.nCeldasX * GLBNsubCeldasPorCelda
                nCeldasY = self.nCeldasY * GLBNsubCeldasPorCelda
            elif 'metrico' in str(fileSinRuta).lower():
                # Capas metricas
                # ['MetricoIntSRet', 'MetricoEVI2', 'MetricoNDVI', 'MetricoNDWI']
                # ['MetricoRugosidadMacroInterCeldillas', 'MetricoRugosidadMesosInterCeldillas', 'MetricoRugosidadMicroInterCeldillas', 'MetricoRugosidadMegasInterCeldillas']
                # ['MetricoPlanoTejado']
                # ['MetricoProp09TodosLosRetornosSueloLasOrig', 'MetricoProp09TodosLosRetornosVegetLasOrig', 'MetricoProp09PrimerosRetornosSueloLasOrig', 'MetricoProp09PrimerosRetornosVegetLasOrig']
                # ['MetricoProp09TodosLosRetornosSueloLasRecl', 'MetricoProp09TodosLosRetornosVegetLasRecl', 'MetricoProp09PrimerosRetornosSueloLasRecl', 'MetricoProp09PrimerosRetornosVegetLasRecl']
                # ['MetricoProp09TodosLosRetornosEdificioLasOrig', 'MetricoProp09PrimerosRetornosEdificioLasOrig', 'MetricoProp09TodosLosRetornosOtrosLasOrig', 'MetricoProp09PrimerosRetornosOtrosLasOrig']
                # ['MetricoProp09TodosLosRetornosEdificioLasRecl', 'MetricoProp09PrimerosRetornosEdificioLasRecl', 'MetricoProp09TodosLosRetornosOtrosLasRecl', 'MetricoProp09PrimerosRetornosOtrosLasRecl']
                metrosPixel = 1.0
                nCeldasX = self.myLasHead.metrosBloqueX
                nCeldasY = self.myLasHead.metrosBloqueY
            elif 'multiceldas' in str(fileSinRuta).lower():
                # Capas de celda
                # 'MultiCeldas***'
                # 'CeldasMdpNumPtosMiniMacro', 'CeldasMdpNumPtosMiniMicro'
                # ['CeldasRugosidadMacroInterCeldillas', 'CeldasRugosidadMesosInterCeldillas', 'CeldasRugosidadMicroInterCeldillas', 'CeldasRugosidadMegasInterCeldillas']
                # etc
                metrosPixel = GLO.GLBLmetrosCelda
                nCeldasX = self.nCeldasX
                nCeldasY = self.nCeldasY
            else:
                # Capas de celda
                # 'MultiCeldas***'
                # 'CeldasMdpNumPtosMiniMacro', 'CeldasMdpNumPtosMiniMicro'
                # ['CeldasRugosidadMacroInterCeldillas', 'CeldasRugosidadMesosInterCeldillas', 'CeldasRugosidadMicroInterCeldillas', 'CeldasRugosidadMegasInterCeldillas']
                # etc
                metrosPixel = GLO.GLBLmetrosCelda
                nCeldasX = self.nCeldasX
                nCeldasY = self.nCeldasY

            if fileSinRuta in [
                'MetricoProp09TodosLosRetornosSuelo_Orig',
                'MetricoProp09TodosLosRetornosVeget_Orig',
                'MetricoProp09PrimerosRetornosSuelo_Orig',
                'MetricoProp09PrimerosRetornosVeget_Orig',
                'MetricoProp09TodosLosRetornosEdificio_Orig',
                'MetricoProp09PrimerosRetornosEdificio_Orig',
                'MetricoProp09TodosLosRetornosOtros_Orig',
                'MetricoProp09PrimerosRetornosOtros_Orig',
                'MetricoProp09TodosLosRetornosSuelo_Recl',
                'MetricoProp09TodosLosRetornosVeget_Recl',
                'MetricoProp09PrimerosRetornosSuelo_Recl',
                'MetricoProp09PrimerosRetornosVeget_Recl',
                'MetricoProp09TodosLosRetornosEdificio_Recl',
                'MetricoProp09PrimerosRetornosEdificio_Recl',
                'MetricoProp09TodosLosRetornosOtros_Recl',
                'MetricoProp09PrimerosRetornosOtros_Recl',
                'MetricoRugosidadMacroInterCeldillas',
                'MetricoRugosidadMesosInterCeldillas',
                'MetricoRugosidadMicroInterCeldillas',
                'MetricoRugosidadMegasInterCeldillas',
                'MetricoPlanoTejado',
            ]:
                # metrico
                noData = 0
            elif fileSinRuta in ['MetricoIntSRet']:
                # metrico
                noData = 0
                pass  # noData = GLO.GLBLnoData
            elif fileSinRuta in ['MetricoEVI2', 'MetricoNDVI', 'MetricoNDWI']:
                # metrico
                noData = GLO.GLBLnoData 
                # Antes el el array era int8, pero lo cambie a float32, como en subCeldas
                # Si quiero que ocupe menos puedo pasarlo a int8, pero hay que cambiar el noData a -128
                # y cambiar la grabacion en asc de {:05.2f} a {:03}
                # Revisar tb la normalizacion para la generacion de tiles a partir de estas capas (clidcarto.normalizarCapas(<>)
                # para 'ndviMed1m', que forma parte de la imagen "png1mInputVar_int_ndvi_..."
                # -> En vez de normalizar de [-1, +1] a [0, 255], habria que normar de [-128, +127] a [0, 255] (sumar 128)
            elif fileSinRuta in ['SubCeldasIntSRetMed', 'SubCeldasIntMRetMed']:
                # subCelda
                noData = 0
            elif fileSinRuta in [
                'SubCeldasProp09TodosLosRetornosSuelo_Orig',
                'SubCeldasProp09TodosLosRetornosVeget_Orig',
                'SubCeldasProp09PrimerosRetornosSuelo_Orig',
                'SubCeldasProp09PrimerosRetornosVeget_Orig',
                'SubCeldasProp09TodosLosRetornosEdificio_Orig',
                'SubCeldasProp09PrimerosRetornosEdificio_Orig',
                'SubCeldasProp09TodosLosRetornosOtros_Orig',
                'SubCeldasProp09PrimerosRetornosOtros_Orig',
                'SubCeldasProp09TodosLosRetornosSuelo_Recl',
                'SubCeldasProp09TodosLosRetornosVeget_Recl',
                'SubCeldasProp09PrimerosRetornosSuelo_Recl',
                'SubCeldasProp09PrimerosRetornosVeget_Recl',
                'SubCeldasProp09TodosLosRetornosEdificio_Recl',
                'SubCeldasProp09PrimerosRetornosEdificio_Recl',
                'SubCeldasProp09TodosLosRetornosOtros_Recl',
                'SubCeldasProp09PrimerosRetornosOtros_Recl',
                'SubCeldasMdrGridPtoMinor',
                'SubCeldasMdrGridNearest',
                'SubCeldasMdrGridLinear',
                'SubCeldasMdrGridCubic',
                'SubCeldasMdpTipoCotaMacroManual',
                'SubCeldasMdpTipoCotaMicroManual',
                'SubCeldasLateralidadMinMaxMacro',
                'SubCeldasLateralidadMinMaxMesos',
                'SubCeldasLateralidadMinMaxMicro',
                'SubCeldasLateralidadMinMinMacro',
                'SubCeldasLateralidadMinMinMesos',
                'SubCeldasLateralidadMinMinMicro',
                'SubCeldasCotaMiniMacroEsOk',
                'SubCeldasCotaMiniMicroEsOk',
                'SubCeldasRugosidadMacroInterCeldillas',
                'SubCeldasRugosidadMesosInterCeldillas',
                'SubCeldasRugosidadMicroInterCeldillas',
                'SubCeldasRugosidadMegasInterCeldillas',
                'SubCeldasPlanoTejado',
                'CeldasNucleosUrbanosDeCartoRef',
                'CeldasUsosSingularesDeCartoRef',
                'SubCeldasCartoSinguLandTypePredichaA',
                'SubCeldasCartoSinguLandTypePredichaB',
                'MultiTilesCartoSinguLandTypePredichaA',
                'MultiTilesCartoSinguLandTypePredichaB',
                'SubCeldasMiniSubCelLasClassPredicha',
                'MultiTilesMiniSubCelLasClassPredicha',
                'SubCeldasPuntoMiniSubCelPsuePsel_classOrigCompleta',
                'SubCeldasPuntoMiniSubCelPsuePsel_classOrig_2_345_6',
                'SubCeldasPuntoMiniSubCelPsuePsel_classOrig_Binaria',
                'SubCeldasDiscrepanciaCartoRefVsLasClassMiniSubCel',
            ]:
                # SubCelda
                noData = 0
            elif str(fileSinRuta)[:18] == 'SubCeldasRugosidad':
                # SubCelda
                noData = GLO.GLBLnoData8bits
            elif fileSinRuta in [
                'CeldasApicesMicro',
                'CeldasApicesMesos',
                'CeldasApicesMacro',
                'CeldasApicesMegas',
                'CeldasPrcntjPrimerosRetornosSuelo_Orig',
                'CeldasPrcntjPrimerosRetornosVeget_Orig',
                'CeldasPrcntjPrimerosRetornosEdifi_Orig',
                'CeldasPrcntjPrimerosRetornosOverl_Orig',
                'CeldasPrcntjPrimerosRetornosOtros_Orig',
                'CeldasPrcntjPrimerosRetornosSuelo_Recl',
                'CeldasPrcntjPrimerosRetornosVeget_Recl',
                'CeldasPrcntjPrimerosRetornosEdifi_Recl',
                'CeldasPrcntjPrimerosRetornosOverl_Recl',
                'CeldasPrcntjPrimerosRetornosOtros_Recl',
                'CeldasMdpNumPtosMiniMacro',
                'CeldasMdpNumPtosMiniMicro',
                'CeldasRugosidadMacroInterCeldillas',
                'CeldasRugosidadMesosInterCeldillas',
                'CeldasRugosidadMicroInterCeldillas',
                'CeldasRugosidadMegasInterCeldillas',
                'CeldasNumeroDePlanosTejado',
                'CeldasPuntosEnPlanosTejado',
            ]:
                # Celda
                noData = 0
            elif 'Clase' in str(fileSinRuta) and 'TodasLasPasadasTodosLosRetornos_NumPuntos' in str(fileSinRuta):
                # Celda
                noData = 0
            elif 'FccRptoA' in str(fileSinRuta):
                # Celda
                noData = GLO.GLBLnoData8bits
            elif str(fileSinRuta)[:11] == 'MultiCeldas':
                # Celda
                noData = GLO.GLBLnoData8bits
            else:
                # Valores por defecto de capa de 10 m
                pass

            totalFicheros += 1
            coordXinfIzda = xInfIzda + (metrosPixel / 2)
            coordYinfIzda = yInfIzda + (metrosPixel / 2)
            clidaux.creaRutaDeFichero(miFileName)
            self.aFiles[fileSinRuta] = open(miFileName, mode='w+')
            self.cabeceraOutputFiles(
                self.aFiles[fileSinRuta],
                coordXinfIzda=coordXinfIzda,
                coordYinfIzda=coordYinfIzda,
                nCeldasX=nCeldasX,
                nCeldasY=nCeldasY,
                metrosPixel=metrosPixel,
                noData=noData,
            )


    # ==========================================================================
    def cabeceraOutputFiles(
            self,
            ascFile,
            coordXinfIzda=0, 
            coordYinfIzda=0,
            nCeldasX=200,
            nCeldasY=200,
            metrosPixel=10,
            noData=-9999
        ):
        ascFile.write('ncols %i \n' % (nCeldasX))
        ascFile.write('nrows %i \n' % (nCeldasY))
        ascFile.write('xllcenter %0.3f \n' % (coordXinfIzda))
        ascFile.write('yllcenter %0.3f \n' % (coordYinfIzda))
        ascFile.write('cellsize %0.3f \n' % (metrosPixel))
        ascFile.write('nodata_value %i \n' % (noData))


    # ==========================================================================
    def iniciaVariablesParaVuelta0rapida(self):
        self.lasPointPF99All = np.zeros(self.myLasHead.numptrecords, dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype))
        self.arrayRangoFechasDeVuelo = np.zeros((2, 4), dtype=np.uint8)
        self.listaPasadasBloque = np.full(GLO.GLBLnumMaxPasadas, GLO.GLBLnoData, dtype=np.int32)
        self.aCeldasNumPuntosEcpVuelta0Rapida = np.zeros(
            self.nCeldasX * self.nCeldasY * GLO.GLBLnumMaxPasadas, dtype=np.uint16).reshape(
                self.nCeldasX, self.nCeldasY, GLO.GLBLnumMaxPasadas)
        self.aCeldasNumPuntosTlpVuelta0Rapida = np.zeros(
            self.nCeldasX * self.nCeldasY, dtype=np.uint16).reshape(
                self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosSuperiorAlNumPtosCeldaExtremoTlrTlpVuelta0Rapida = np.zeros(
            self.nCeldasX * self.nCeldasY, dtype=np.uint8).reshape(
                self.nCeldasX, self.nCeldasY)
        self.aNumReturnsByPulseAll = np.zeros(GLO.GLBLnumeroMaximoDeRetornosPorPulso + 1, dtype=np.int64)

        self.nPuntosPorClase = np.zeros(256, dtype=np.int32)
        self.minMaxRGBIrI = np.array([[65536, 0]] * 6, dtype=np.uint64)


        # ======================================================================
        # Numero total de puntos:
        #    self.nPtosAleer
        # Debe coincidir con self.contadorPtosLeidosTotales
        # A continuacion excluimos:
        #     Filtro 0: los de pasadas transversales (coordenadas imposibles) (numPuntosDescartadosPorPasadaTransversal)
        #     Filtro 1: los de coordenadas fuera de rango (coordenadas imposibles) (numPuntosDescartadosPorCoordenadasErroneas)
        #     Filtro 2: los de coordenadas fuera de bloque (a mas de X metros del borde) (numPuntosDescartadosPorFueraDeBloque)
        #   obtenemos:
        #     self.numPuntosTodosDentroDelBloque
        #   Sobre estos puntos se hace el recuento de puntos por retorno y clase para todo el bloque:
        #     self_aNumReturnsByPulseOkBloque
        #     self_aNumReturnsTotalOkBloque
        #     self_nPuntosPorClase
        # A continuacion excluimos:
        #     Filtro 3: DescartadosPorPasadaConDemasiadosPuntos -> self_numPuntosDescartadosPorPasadaConDemasiadosPuntosUnoDeCadaN y self_numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes
        #       3a: empieza actuando con muestreo sistematico preventivo (uno de cada N)
        #           apoyandome en la contabilidad or celda hecha en vuelta0rapida
        #       3b: para los puntos que exceden ellimite a pesar del adelgazamiento previo
        #     Filtro 4: DescartadosPorCeldaConNumPuntosExtremo  -> self_numPuntosDescartadosPorCeldaConNumPuntosExtremo
        #   obtenemos:

        #   Sobre estos puntos consulto las capas de referencia para los puntos que han pasado estos dos filtros
        #   A partir de aqui, los puntos van a una de estas dos arrays (con info de cartoRef):
        #     self_aCeldasListaDePtosTlcPralPF99
        #     self_aListaDePtosDescartadosDeArrayPralPF99
        # A continuacion excluimos:
        #     Filtro 2: los outliers (numPuntosDescartadosPorOutlier)
        #   obtenemos:
        #     self.numPuntosValidosDentroDelBloque
        #   Sobre estos puntos se hacen recuentos y sumatorios varios para estas arrays:
        #     self.aCeldasNumPrimerosRetornosTlp
        #     self.aCeldasNumPrimerosRetornosNoSolape
        #     self.aCeldasNumSiguientesRetornosTlp
        #     self.aCeldasNumSingleReturnTlp
        #     self.aCeldasNumMultiReturnTlp
        #     self.aCeldasNumPrimerosRetornosSuelo
        #     self.aCeldasNumTodosLosRetornosSuelo
        #     self.aCeldasNumPrimerosRetornosVeget
        #     self.aCeldasNumTodosLosRetornosVeget
        #     self.aCeldasNumPrimerosRetornosEdificio
        #     self.aCeldasNumTodosLosRetornosEdificio
        #     self.aCeldasNumPrimerosRetornosOtros
        #     self.aCeldasNumTodosLosRetornosOtros
        #     self.aCeldasNumTodosLosRetornosOverlap
        #     self.aSubCeldasNumPtosTlcTlpTlr
        #     self.aSubCeldasNumPtosTlcTlpTr1
        #     self.aSubCeldasProp09TodosLosRetornosSuelo
        #     self.aSubCeldasProp09PrimerosRetornosSuelo
        #     self.aSubCeldasProp09TodosLosRetornosVeget
        #     self.aSubCeldasProp09PrimerosRetornosVeget
        #     self.aSubCeldasProp09TodosLosRetornosEdificio
        #     self.aSubCeldasProp09PrimerosRetornosEdificio
        #     self.aSubCeldasProp09TodosLosRetornosOtros
        #     self.aSubCeldasProp09PrimerosRetornosOtros
        #     self.aMetricoNumPtosTlcTlpTlr
        #     self.aMetricoNumPtosTlcTlpTr1
        #     self.aMetricoProp09TodosLosRetornosSuelo
        #     self.aMetricoProp09PrimerosRetornosSuelo
        #     self.aMetricoProp09TodosLosRetornosVeget
        #     self.aMetricoProp09PrimerosRetornosVeget
        #     self.aMetricoProp09TodosLosRetornosEdificio
        #     self.aMetricoProp09PrimerosRetornosEdificio
        #     self.aMetricoProp09TodosLosRetornosOtros
        #     self.aMetricoProp09PrimerosRetornosOtros
        #     self.aCeldasNumPuntosTlrSueTlpVuelta0
        #     self.aCeldasSumaCotasTlrSueTlpVuelta0
        #     self.aCeldasZmin
        #     self.aCeldasZmax
        #     self.miPtoNpMaxiMiniSubCel
        #     self.aSubCeldasPuntoMiniSubCel_Tlp
        #     self.aSubCeldasPuntoMaxiSubCel_Tlp
        #     self_aSubCeldasIntSRetMed,
        #     self_aSubCeldasIntSRetNum,
        #     self_aSubCeldasEVI2Med,
        #     self_aSubCeldasEVI2Num,
        #     self_aSubCeldasNDVIMed,
        #     self_aSubCeldasNDVINum,
        #     self_aSubCeldasNDWIMed,
        #     self_aSubCeldasNDWINum,
        #     self_aMetricoConBufferNumPuntosTlcTlpSingRet,
        #     self_aMetricoIntSRet,
        #     self_aMetricoConBufferNumPuntosTlcTlpPlurRet,
        #     self_aMetricoEVI2Med,
        #     self_aMetricoNDVIMed,
        #     self_aMetricoNDWIMed,
        #     self_minMaxRGBIrI
        #     self_listaPasadasBloque
        #     self_aCeldasNumPuntosEcpVuelta0Normal
        #     self_aCeldasNumPuntosTlpVuelta0Normal
        #     self.aCeldasNumPuntosTlrTlcEcpTlvSinFiltrar

#numPuntosTodosDentroDelBloque = contadorPtosLeidosTotales - numPuntosDescartadosPorPasadaTransversal - numPuntosDescartadosPorCoordenadasErroneas - numPuntosDescartadosPorFueraDeBloque
#numPuntosValidosDentroDelBloque = contadorPtosLeidosTotales - numPuntosDescartadosPorPasadaTransversal - numPuntosDescartadosPorCoordenadasErroneas - numPuntosDescartadosPorFueraDeBloque - numPuntosDescartadosPorOutlier



        # Si los distribuimos por celdas (excluyendo los que exceden GLBLnMaxPtosCeldaTlrTlpPrevioExtremo - numPuntosDescartadosPorCeldaConDemasiadosPuntosTotales-)
        # obtenemos:
        #    self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] -> Sfl: Sin filtrar outliers y n max ptos por pasada (aunque maximo ~10000 or celda)
        # Si los separamos por pasadas y excluimos:
        # los que exceden GLBLnMaxPtosCeldaTlrPas en la celda (numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes)
        # obtenemos:
        #    myLasData_aCeldasNumPuntosTlrTlcEcpOk[nX, nY][reCuentaPasadas]['Val']
        # Si excluimos
        # los q no caben en la celda GLBLnMaxPtosCeldaArrayPredimensionadaTodos (numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos)
        # obtenemos
        #    self.aCeldasNumPuntosTlrTlcTlpOk[nX, nY] -> para todo el bloque: self.numPuntosValidosTotalesUsables
        #    Si GLBLalmacenarPuntosComoNumpyDtype:
        #       self.numPuntosValidosTotalesUsables = self.contadorAllEnArrayPral + [self.contadorAllEnArrayAux si noNumba] (ya no uso self.contadorAllEnArrayAux)
        # ======================================================================

    # ==========================================================================
    def iniciaVariablesParaVuelta0normal(self):
        # En esta funcion se crean:
        # Las arrays con los puntos que proceda:
        #    miPtoNpArrayRecord, miPtoNpRecordPointFormatXX, miPtoNpArrayRecordMini, miPtoNpRecordMini
        #    aCeldasListaDePtosTlcPralPF99
        #    aCeldasListaDePtosSuePralPF99
        #    aCeldasListaDePtosTlcAll, aCeldasListaDePtosTlcAux
        #    aCeldasListaDePtosSueAll, aCeldasListaDePtosSueAux
        # Las arrays con el numero de puntos por celda (todas las pasadas):
        #    self.aCeldasNumPuntosTlrTlcEcpOk = np.full((self.nCeldasX, self.nCeldasY, self.numTotalPasadas), GLO.GLBLnoData, dtype=np.dtype(self.myLasHead.formatoDtypeIdValNotacionNpDtype))
        #    self.aCeldasNumPuntosTlrTlcEcpTlvSinFiltrar = np.full((self.nCeldasX, self.nCeldasY, self.numTotalPasadas), GLO.GLBLnoData, dtype=np.dtype(self.myLasHead.formatoDtypeIdValNotacionNpDtype))
        #    self.aCeldasNumPuntosTlrTlcTlpOk = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        #    self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        #    self.aCeldasNumPuntosTlrSueTlpTlvSinFiltrar = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        # Las arrays con la suma de cotas para detectar outliers (todas las pasadas):
        #    self.aCeldasSumaCotasTlrTlcTlpOk = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        #    self.aCeldasSumaCotasTlrSueTlpVuelta0 = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        # Y esta adicional para controlar las puntos que guardo (en su caso) en aCeldasListaDePtosSuePralPF99[]:
        #    self.aCeldasNumPuntosTlrSueTlpVuelta0
        # Arrays menores:
        #    aNumReturnsByPulseAll
        #    self.numRowsParaNuevoLas
        #    self.numColsParaNuevoLas
        # Diversas variables numericas (podria iniciarlas directamente en vuelta0

        # ======================================================================
        # Arrays con sitio para todas las celdas:
        # Uso una ndarray de tipo int16: si pasa de 65536 puntos empieza negativo: lo dejo en 65536
        self.aCeldasNumPuntosTlrTlcEcpOk = np.full(
            (self.nCeldasX, self.nCeldasY, self.numTotalPasadas), GLO.GLBLnoData, dtype=np.dtype(
                self.myLasHead.formatoDtypeIdValNotacionNpDtype
            )
        )
        self.aCeldasNumPuntosTlrTlcEcpTlvSinFiltrar = np.full(
            (self.nCeldasX, self.nCeldasY, self.numTotalPasadas), GLO.GLBLnoData, dtype=np.dtype(
                self.myLasHead.formatoDtypeIdValNotacionNpDtype
            )
        )
        self.aCeldasNumPuntosEcpVuelta0Normal = np.zeros(
            self.nCeldasX * self.nCeldasY * self.numTotalPasadas, dtype=np.uint16).reshape(
                self.nCeldasX, self.nCeldasY, self.numTotalPasadas)
        # Numero de puntos descartados de cada pasada en vuelta0normal (uno de cada N o superaMaxPtosCeldaTlrPas)
        self.aCeldasNumPuntosDcpVuelta0Normal = np.zeros(
            self.nCeldasX * self.nCeldasY * self.numTotalPasadas, dtype=np.uint16).reshape(
                self.nCeldasX, self.nCeldasY, self.numTotalPasadas)

        self.aCeldasNumPuntosTlpVuelta0Normal = np.zeros(
            self.nCeldasX * self.nCeldasY, dtype=np.uint16).reshape(
                self.nCeldasX, self.nCeldasY)
        # Numero de puntos que no se pueden guardar en la celda por superar LCLnMaxPtosCeldaArrayPredimensionadaTodos
        self.aCeldasNumPuntosDlpVuelta0Normal = np.zeros(
            self.nCeldasX * self.nCeldasY, dtype=np.uint16).reshape(
                self.nCeldasX, self.nCeldasY)

        self.aCeldasNumPuntosTlrTlcTlpOk = np.zeros(
            self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(
                self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar = np.zeros(
            self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(
                self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrSueTlpTlvSinFiltrar = np.zeros(
            self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(
                self.nCeldasX, self.nCeldasY)
        # self.aCeldasNumPuntosTlrTlcEcpOk = np.empty(self.nCeldasX*self.nCeldasY, dtype=np.object).reshape(self.nCeldasX, self.nCeldasY)
        # for nY in range(self.nCeldasY):
        #    for nX in range(self.nCeldasX):
        #        self.aCeldasNumPuntosTlrTlcEcpOk[nX, nY] = {}
        # Esto es solo para detectar outliers
        self.aCeldasSumaCotasTlrTlcTlpOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasSumaCotasTlrSueTlpVuelta0 = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        # Y esta adicional que no se si uso para algo:
        self.aCeldasNumPuntosTlrSueTlpVuelta0 = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        # ======================================================================

        # ======================================================================
        if (
            GLO.GLBLgrabarPrimerosVsSegundosRetornos
            or GLO.GLBLgrabarPrimerosRetornosNoSolape
            or GLO.GLBLgrabarPuntosPorClaseLasOrig and (
                GLO.GLBLgrabarCeldasClasesSueloVegetacion
                or GLO.GLBLgrabarCeldasClasesEdificio
                or GLO.GLBLgrabarCeldasClasesOtros
            )
        ):
            self.aCeldasNumPrimerosRetornosTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumPrimerosRetornosNoSolape = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumPrimerosRetornosTlp = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumPrimerosRetornosNoSolape = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
        if GLO.GLBLgrabarPrimerosVsSegundosRetornos:
            self.aCeldasNumSiguientesRetornosTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumSingleReturnTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumMultiReturnTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumSiguientesRetornosTlp = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumSingleReturnTlp = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumMultiReturnTlp = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
        # ======================================================================

        # ======================================================================
        if GLO.GLBLgrabarPropiedadTime:
            self.aCeldasRawTime = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float64).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasRawTime = np.zeros(1, dtype=np.float64).reshape(1, 1)
        if GLO.GLBLleerGrabarCeldasEdge:
            self.aCeldasEsCeldaEdge = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasEsCeldaEdge = np.zeros(1, dtype=np.int16).reshape(1, 1)
        if GLO.GLBLgrabarNumeroPuntosPorClase:
            self.aCeldasNumPtosPorClaseTlrTlp = np.zeros(self.nCeldasX * self.nCeldasY * GLO.GLBLnumMaximoDeClases, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY, GLO.GLBLnumMaximoDeClases)
        else:
            self.aCeldasNumPtosPorClaseTlrTlp = np.zeros(1 * GLO.GLBLnumMaximoDeClases, dtype=np.int16).reshape(1, 1, GLO.GLBLnumMaximoDeClases)
        # ======================================================================

        # ======================================================================
        if (GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarCeldasClasesSueloVegetacion) or GLO.GLBLgrabarAlturasRptoAzMin:
            self.aCeldasNumPrimerosRetornosSuelo = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumTodosLosRetornosSuelo = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumPrimerosRetornosVeget = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumTodosLosRetornosVeget = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumPrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumTodosLosRetornosSuelo = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumPrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumTodosLosRetornosVeget = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)

        if (GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarCeldasClasesEdificio) or GLO.GLBLgrabarAlturasRptoAzMin:
            self.aCeldasNumPrimerosRetornosEdificio = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumTodosLosRetornosEdificio = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumPrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumTodosLosRetornosEdificio = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)

        if (GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarCeldasClasesOtros) or GLO.GLBLgrabarAlturasRptoAzMin:
            self.aCeldasNumPrimerosRetornosOtros = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumTodosLosRetornosOtros = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumTodosLosRetornosOverlap = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumPrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumTodosLosRetornosOtros = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumTodosLosRetornosOverlap = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
        # ======================================================================

        self.contadorPtosLeidosTotales = 0
        self.nPuntosDescartadosIntraBloque = 0
        self.nPuntosDescartadosExtraBloque = 0

        self.contadorAllEnArrayPral = 0 # == self.numPuntosValidosTotalesUsables
        self.contadorSiGuardablesEnArrayDescartadosDePral = 0
        self.contadorNoGuardablesEnArrayDescartadosDePral= 0
        self.contadorSueEnArrayPral = 0

        self.numPuntosTodosDentroDelBloque = 0
        self.numPuntosNoExcesivosDentroDelBloque = 0
        self.numPuntosValidosDentroDelBloque = 0
        self.numPuntosValidosTotalesUsables = 0 # == self.contadorAllEnArrayPral

        self.numPuntosDescartadosPorCoordenadasNulas = 0
        self.numPuntosDescartadosPorPasadaTransversal = 0
        self.numPuntosDescartadosPorCoordenadasErroneas = 0
        self.numPuntosDescartadosPorFueraDeBloque = 0
        self.numPuntosDescartadosPorOutlier = 0
        self.numPuntosDescartadosPorPasadaConDemasiadosPuntosUnoDeCadaN = 0
        self.numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes = 0
        self.numPuntosDescartadosPorCeldaConNumPuntosExtremo = 0
        self.numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos = 0

        self.hayCeldasConDemasiadosPuntos = False
        self.hayCeldasConDemasiadosPuntosEnLaPasada = False

        self.nPuntosPorClase = np.zeros(GLO.GLBLnumMaximoDeClases, dtype=np.int32)

        self.hayOutliers = False
        #         self.hayPuntosClasificadosSuelo = False #Se calcula despues de la Vuelta0, en miLasMatrixiniciaVariablesPostVuelta0PreCargarPropiedades()

        self.aNumReturnsTotalOkBloque = np.zeros(GLO.GLBLnumeroMaximoDeRetornosPorPulso + 1, dtype=np.int64)
        self.aNumReturnsByPulseOkBloque = np.zeros(GLO.GLBLnumeroMaximoDeRetornosPorPulso + 1, dtype=np.int64)
        self.aNumReturnsByPulseParaNuevoLasSinReclasificar = np.zeros(GLO.GLBLnumeroMaximoDeRetornosPorPulso + 1, dtype=np.int64)
        self.nPuntosSiParaNuevoLasSinReclasificar = 0
        self.nPuntosNoParaNuevoLasSinReclasificar = 0
        # ======================================================================
        # self.aCeldasListaPasada = np.full((self.nCeldasX, self.nCeldasY, self.numTotalPasadas), GLO.GLBLnoData, dtype=np.int16)
        # self.aCeldasNPtosPasada = np.full((self.nCeldasX, self.nCeldasY, self.numTotalPasadas), GLO.GLBLnoData, dtype=np.int16)
        # self.aCeldasListaPasadasConPuntos = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.object).reshape(self.nCeldasX, self.nCeldasY)
        # for nY in range(self.nCeldasY):
        #    for nX in range(self.nCeldasX):
        #        self.aCeldasListaPasadasConPuntos[nX, nY] = []
        # ======================================================================
        if GLO.GLBLgenerarNuevoLaxGenerico:
            self.numRowsParaNuevoLas = min(self.nCeldasX, int(math.sqrt(GLO.GLBLnumPuntosParaNuevoLas / 50)) + 1)
            self.numColsParaNuevoLas = min(self.nCeldasY, int(math.sqrt(GLO.GLBLnumPuntosParaNuevoLas / 50)) + 1)
        else:
            self.numRowsParaNuevoLas = self.nCeldasX
            self.numColsParaNuevoLas = self.nCeldasY
        # ======================================================================

        # ======================================================================
        self.aCeldasZmin = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasZmin.fill(9999)
        self.aCeldasZmax = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasZmax.fill(-9999)


        # ======================================================================
        # Iniciando aCeldasListaDePtosTlcAll, aCeldasListaDePtosSuePralPF99 y aCeldasListaDePtosSueAux:
        # ======================================================================
        if GLO.GLBLalmacenarPuntosComoNumpyDtype:
            if GLO.GLBLverbose or True:
                print(
                    'cliddata-> Se crea el array aCeldasListaDePtosTlcPralPF99[] para guardar como dtype():'
                )
                print(
                    '\tEl array aCeldasListaDePtosTlcPralPF99 guarda un maximo de {} puntos por celda.'.format(
                        self.LCLnMaxPtosCeldaArrayPredimensionadaTodos
                    )
                )
                print('\tCon numba no puedo usar un array Aux')

            self.aCeldasListaDePtosExtrVar = np.zeros(
                self.nCeldasX * self.nCeldasY * self.LCLnMaxPtosCeldaArrayPredimensionadaTodos,
                dtype=np.dtype(self.myLasHead.formatoDtypeExtrVarNotacionNpDtype)
            ).reshape(self.nCeldasX, self.nCeldasY, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos)

            self.aCeldasListaDePtosTlcPralPF99 = np.zeros(
                self.nCeldasX * self.nCeldasY * self.LCLnMaxPtosCeldaArrayPredimensionadaTodos,
                dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)
            ).reshape(self.nCeldasX, self.nCeldasY, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos)

            self.aListaDePtosDescartadosDeArrayPralPF99 = np.zeros(GLO.GLBLnMaxPtosArrayDescartadosDeArrayPral,
                dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)
            )

            if GLO.GLBLcalcularMds and GLO.GLBLguardarPuntosSueloEnArrayPredimensionada:
                self.aCeldasListaDePtosSuePralPF99 = np.zeros(
                    self.nCeldasX * self.nCeldasY * GLO.GLBLnMaxPtosCeldaArrayPredimensionadaSuelo,
                    dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype),
                ).reshape(self.nCeldasX, self.nCeldasY, GLO.GLBLnMaxPtosCeldaArrayPredimensionadaSuelo)
            else:
                self.aCeldasListaDePtosSuePralPF99 = np.zeros(
                    1 * 1 * 1, dtype=np.dtype(
                        self.myLasHead.formatoDtypePointFormat99NotacionNpDtype
                    )
                ).reshape(1, 1, 1)

            if GLO.GLBLverbose:
                print('cliddata-> Memoria ocupada por aCeldasListaDePtosTlcPralPF99 %6.2f Mb' % (self.aCeldasListaDePtosTlcPralPF99.nbytes / 1e6))
                print('cliddata-> Memoria ocupada por aCeldasListaDePtosSuePralPF99 %6.2f Mb' % (self.aCeldasListaDePtosSuePralPF99.nbytes / 1e6))

            self.aCeldasListaDePtosTlcAux = np.zeros(
                1, dtype=np.dtype(
                    self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)).reshape(1, 1, 1)

            if GLO.GLBLcalcularMds:
                self.aCeldasListaDePtosSueAux = np.zeros(
                    1, dtype=np.dtype(
                        self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)).reshape(1, 1, 1)

            # Este array no lo uso, se podria unificar aCeldasListaDePtosTlcAll y aCeldasListaDePtosTlcPralPF99
            # cuando uso numba porque ambas tienen GLBLnMaxPtosCeldaArrayPredimensionadaTodos elementos por celda
            self.aCeldasListaDePtosTlcAll = np.zeros(self.myLasHead.pointreclen, dtype=np.ubyte).reshape(1, 1, 1, self.myLasHead.pointreclen)
            self.aCeldasListaDePtosSueAll = np.zeros(self.myLasHead.pointreclen, dtype=np.ubyte).reshape(1, 1, 1, self.myLasHead.pointreclen)
        else:
            if GLO.GLBLalmacenarPuntosComoByteString:
                print(
                    'cliddata-> Se crea el array aCeldasListaDePtosTlcAll[] para guardar como string: el array aCeldasListaDePtosTlcAll guarda un maximo de %i puntos por celda.'
                    % self.LCLnMaxPtosCeldaArrayPredimensionadaTodos
                )
                self.aCeldasListaDePtosTlcAll = np.zeros(
                    self.nCeldasX * self.nCeldasY * self.LCLnMaxPtosCeldaArrayPredimensionadaTodos * self.myLasHead.pointreclen,
                    dtype=np.ubyte
                ).reshape(self.nCeldasX, self.nCeldasY, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos, self.myLasHead.pointreclen)
                self.aCeldasListaDePtosTlcPralPF99 = np.zeros(
                    1,
                    dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)).reshape(1, 1, 1)
                self.aCeldasListaDePtosTlcAux = np.zeros(
                    1, dtype=np.dtype(
                        self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)).reshape(1, 1, 1)
                if GLO.GLBLcalcularMds:
                    if GLO.GLBLguardarPuntosSueloEnArrayPredimensionada:
                        self.aCeldasListaDePtosSueAll = np.zeros(
                            self.nCeldasX * self.nCeldasY * self.LCLnMaxPtosCeldaArrayPredimensionadaTodos * self.myLasHead.pointreclen,
                            dtype=np.ubyte
                        ).reshape(self.nCeldasX, self.nCeldasY, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos, self.myLasHead.pointreclen)
                    else:
                        self.aCeldasListaDePtosSueAll = np.zeros(
                            self.nCeldasX * self.nCeldasY * self.myLasHead.pointreclen,
                            dtype=np.ubyte
                        ).reshape(self.nCeldasX, self.nCeldasY, 1, self.myLasHead.pointreclen)
                    self.aCeldasListaDePtosSuePralPF99 = np.zeros(
                        1, dtype=np.dtype(
                            self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)
                        ).reshape(1, 1, 1)
                    self.aCeldasListaDePtosSueAux = np.zeros(
                        1, dtype=np.dtype(
                            self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)
                        ).reshape(1, 1, 1)
            else:
                print(
                    'cliddata-> No disponible con Numba: Se crearia el array aCeldasListaDePtosTlcAll[] para guardar como tipo propio: el array aCeldasListaDePtosTlcAll guarda un maximo de %i puntos por celda.'
                    % self.LCLnMaxPtosCeldaArrayPredimensionadaTodos
                )
                # Corregir esto con la estructura de array (en vez de lista) que utiliza
                self.aCeldasListaDePtosTlcAll = np.zeros(
                    self.nCeldasX * self.nCeldasY * self.LCLnMaxPtosCeldaArrayPredimensionadaTodos,
                    dtype=np.ubyte
                ).reshape(self.nCeldasX, self.nCeldasY, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos)

                self.aCeldasListaDePtosTlcPralPF99 = np.array(
                    1 * 1 * 1,
                    dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)).reshape(1, 1, 1)

                self.aCeldasListaDePtosTlcAux = np.array(
                    1 * 1 * 1,
                    dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)).reshape(1, 1, 1)

                if GLO.GLBLcalcularMds:
                    if GLO.GLBLguardarPuntosSueloEnArrayPredimensionada:
                        self.aCeldasListaDePtosSueAll = np.zeros(
                            self.nCeldasX * self.nCeldasY * self.LCLnMaxPtosCeldaArrayPredimensionadaTodos,
                            dtype=np.ubyte,
                        ).reshape(self.nCeldasX, self.nCeldasY, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos)
                    else:
                        self.aCeldasListaDePtosSueAll = np.zeros(
                            self.nCeldasX * self.nCeldasY,
                            dtype=np.ubyte
                        ).reshape(self.nCeldasX, self.nCeldasY, 1)

                    self.aCeldasListaDePtosSuePralPF99 = np.array(
                        1 * 1 * 1,
                        dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)).reshape(1, 1, 1)

                    self.aCeldasListaDePtosSueAux = np.array(
                        1 * 1 * 1,
                        dtype=np.dtype(self.myLasHead.formatoDtypePointFormat99NotacionNpDtype)).reshape(1, 1, 1)
            print('cliddata-> Memoria ocupada por aCeldasListaDePtosTlcAll %0.2f Mb' % (self.aCeldasListaDePtosTlcPralPF99.nbytes / 1e6))
            print('cliddata-> Memoria ocupada por aCeldasListaDePtosSueAll %0.2f Mb' % (self.aCeldasListaDePtosSuePralPF99.nbytes / 1e6))

        if GLO.GLBLcalcularSubCeldas:
            # Este array lo uso en vuelta4 pero lo creo ya en todo caso (aunque no haya vuelta4)
            # porque de todas formas lo guardo con guardarArraysMiniSubCel_myLasData<>
            if GLO.GLBLcalcularMdp:
                self.aSubCeldasPuntoMiniSubCelValidado = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda,
                    dtype=np.int8
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
            else:
                self.aSubCeldasPuntoMiniSubCelValidado = np.zeros(1 * 1, dtype=np.int8).reshape(1, 1)
            if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                # Punto mini -> Psel
                if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
                    # Opcion elegida siempre
                    self.aSubCeldasPuntoMiniSubCelPsuePsel = np.zeros(
                        self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda,
                        dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype
                    ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)

                    self.aSubCeldasPuntoMaxiSubCelPsuePsel = np.zeros(
                        self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda,
                        dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype
                    ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)

                    self.aSubCeldasPuntoMiniSubCelPsel = np.zeros(
                        1 * 1 * self.nCamposPorPuntoMaxiMiniSubCel,
                        dtype=np.float64).reshape(
                        1, 1, self.nCamposPorPuntoMaxiMiniSubCel
                    )
                    self.aSubCeldasPuntoMaxiSubCelPsel = np.zeros(
                        1 * 1 * self.nCamposPorPuntoMaxiMiniSubCel,
                        dtype=np.float64).reshape(
                        1, 1, self.nCamposPorPuntoMaxiMiniSubCel
                    )
                else:
                    # A extinguir
                    self.aSubCeldasPuntoMiniSubCelPsuePsel = np.zeros(
                        1 * 1,
                        dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
                    self.aSubCeldasPuntoMaxiSubCelPsuePsel = np.zeros(
                        1 * 1,
                        dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
                    # Lo mas probable es que no use esto porque gasto float64 para cada variable de cada punto: poco eficiente
                    self.aSubCeldasPuntoMiniSubCelPsel = np.zeros(
                        self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda * self.nCamposPorPuntoMaxiMiniSubCel,
                        dtype=np.float64
                    ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda, self.nCamposPorPuntoMaxiMiniSubCel)
                    self.aSubCeldasPuntoMaxiSubCelPsel = np.zeros(
                        self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda * self.nCamposPorPuntoMaxiMiniSubCel,
                        dtype=np.float64
                    ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda, self.nCamposPorPuntoMaxiMiniSubCel)
                self.aSubCeldasPuntoMiniSubCel_Tlp = np.zeros(
                    1 * 1,
                    dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
                self.aSubCeldasPuntoMaxiSubCel_Tlp = np.zeros(
                    1 * 1,
                    dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
            else:
                # Punto mini -> Tlp
                self.aSubCeldasPuntoMiniSubCelPsuePsel = np.zeros(
                    1 * 1,
                    dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
                self.aSubCeldasPuntoMaxiSubCelPsuePsel = np.zeros(
                    1 * 1,
                    dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
                self.aSubCeldasPuntoMiniSubCelPsel = np.zeros(
                    1 * 1 * self.nCamposPorPuntoMaxiMiniSubCel,
                    dtype=np.float64).reshape(
                    1, 1,
                    self.nCamposPorPuntoMaxiMiniSubCel
                )
                self.aSubCeldasPuntoMaxiSubCelPsel = np.zeros(
                    1 * 1 * self.nCamposPorPuntoMaxiMiniSubCel,
                    dtype=np.float64).reshape(
                    1, 1, self.nCamposPorPuntoMaxiMiniSubCel
                )
                self.aSubCeldasPuntoMiniSubCel_Tlp = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda,
                    dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasPuntoMaxiSubCel_Tlp = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda,
                    dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
            self.aSubCeldasCotaMinAA = np.zeros(
                self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda,
                dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasCotaMinAA.fill(9999)
            self.aSubCeldasCotaMaxAA = np.zeros(
                self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda,
                dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasCotaMaxAA.fill(GLO.GLBLnoData)
        else:
            self.aSubCeldasPuntoMiniSubCelValidado = np.zeros(1 * 1, dtype=np.int8).reshape(1, 1)
            self.aSubCeldasPuntoMiniSubCelPsuePsel = np.zeros(1 * 1, dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
            self.aSubCeldasPuntoMaxiSubCelPsuePsel = np.zeros(1 * 1, dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
            self.aSubCeldasPuntoMiniSubCelPsel = np.zeros(1 * 1 * self.nCamposPorPuntoMaxiMiniSubCel, dtype=np.float64).reshape(
                1, 1, self.nCamposPorPuntoMaxiMiniSubCel
            )
            self.aSubCeldasPuntoMaxiSubCelPsel = np.zeros(1 * 1 * self.nCamposPorPuntoMaxiMiniSubCel, dtype=np.float64).reshape(
                1, 1, self.nCamposPorPuntoMaxiMiniSubCel
            )
            self.aSubCeldasPuntoMiniSubCel_Tlp = np.zeros(1 * 1, dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
            self.aSubCeldasPuntoMaxiSubCel_Tlp = np.zeros(1 * 1, dtype=self.myLasHead.formatoDtypePointMaxMinNotacionNpDtype).reshape(1, 1)
            self.aSubCeldasCotaMinAA = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasCotaMaxAA = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)

        # ->Estos se rellenan en clidnv0.acumularIndicesRGBIrI{} al que se llama desde clidnv0.numbaMainVuelta0{}
        #  Tienen los valores medios por punto de intensity o de los indices de vegetacion (media de los puntos de cada subcelda)
        #  La intensidad media se calcula por un lado para los puntos con un solo retorno y por otro para los multi-return
        #    La que vale es la de los single-return porque no esta fraccionada (si pudiera sumarria las intensidades de los mutiples retornos de los puntos multi-return)
        if GLO.GLBLgrabarIndicesVegetacionNDVIetAlSubCelda or GLBNmuestreoAcumulativoOEntrenamientoOInferencia:
            self.aSubCeldasIntSRetMed = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasIntSRetNum = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasIntMRetMed = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasIntMRetNum = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasEVI2Med = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasEVI2Num = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasNDVIMed = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasNDVINum = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasNDWIMed = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasNDWINum = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
        else:
            self.aSubCeldasIntSRetMed = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasIntSRetNum = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasIntMRetMed = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasIntMRetNum = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasEVI2Med = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasEVI2Num = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasNDVIMed = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasNDVINum = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasNDWIMed = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasNDWINum = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLgrabarIndicesVegetacionNDVIetAlMetricos or GLBNmuestreoAcumulativoOEntrenamientoOInferencia:
            # ->Estos se rellenan en clidnv0.acumularIndicesMetrico{} al que se le llama desde clidnv0.acumularIndicesRGBIrI{} (su vez, al que se llama desde clidnv0.numbaMainVuelta0{})
            #  Una vez recorridos todos los puntos se calculan las medias por m2 al final de clidnv0.numbaMainVuelta0{}
            #  Estas arrays promedian los puntos de cada metro cuadrado (en vez de cada subCelda)
            self.aMetricoConBufferNumPuntosTlcTlpSingRet = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint16).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoConBufferNumPuntosTlcTlpPlurRet = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint16).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoIntSRet = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint64).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoEVI2Med = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.float32).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoNDVIMed = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.float32).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoNDWIMed = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.float32).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
        else:
            self.aMetricoConBufferNumPuntosTlcTlpSingRet = np.zeros(1 * 1, dtype=np.uint16).reshape(1, 1)
            self.aMetricoConBufferNumPuntosTlcTlpPlurRet = np.zeros(1 * 1, dtype=np.uint16).reshape(1, 1)
            self.aMetricoIntSRet = np.zeros(1 * 1, dtype=np.uint64).reshape(1, 1)
            self.aMetricoEVI2Med = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aMetricoNDVIMed = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aMetricoNDWIMed = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)

        if GLO.GLBLgrabarPuntosPorClaseLasOrig and (
            GLO.GLBLgrabarSubCeldasClasesSueloVegetacion
            or GLO.GLBLgrabarSubCeldasClasesEdificio
            or GLO.GLBLgrabarSubCeldasClasesOtros
        ):
            self.aSubCeldasNumPtosTlcTlpTlr = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
            )
            if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                self.aSubCeldasNumPtosTlcTlpTr1 = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                    GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
                )
            else:
                self.aSubCeldasNumPtosTlcTlpTr1 = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        else:
            self.aSubCeldasNumPtosTlcTlpTlr = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasNumPtosTlcTlpTr1 = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarSubCeldasClasesSueloVegetacion:
            self.aSubCeldasProp09TodosLosRetornosSuelo = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
            )
            self.aSubCeldasProp09TodosLosRetornosVeget = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
            )
            if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                self.aSubCeldasProp09PrimerosRetornosSuelo = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                    GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
                )
                self.aSubCeldasProp09PrimerosRetornosVeget = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                    GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
                )
            else:
                self.aSubCeldasProp09PrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
                self.aSubCeldasProp09PrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        else:
            self.aSubCeldasProp09TodosLosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasProp09PrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasProp09TodosLosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasProp09PrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        if GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarSubCeldasClasesEdificio:
            self.aSubCeldasProp09TodosLosRetornosEdificio = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
            )
            if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                self.aSubCeldasProp09PrimerosRetornosEdificio = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                    GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
                )
            else:
                self.aSubCeldasProp09PrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        else:
            self.aSubCeldasProp09TodosLosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasProp09PrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        if GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarSubCeldasClasesOtros:
            self.aSubCeldasProp09TodosLosRetornosOtros = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
            )
            if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                self.aSubCeldasProp09PrimerosRetornosOtros = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
                    GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
                )
            else:
                self.aSubCeldasProp09PrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        else:
            self.aSubCeldasProp09TodosLosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasProp09PrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)


        if GLO.GLBLgrabarPuntosPorClaseLasOrig and (
            GLO.GLBLgrabarMetricoClasesSueloVegetacion
            or GLO.GLBLgrabarMetricoClasesEdificio
            or GLO.GLBLgrabarMetricoClasesOtros
        ):
            self.aMetricoNumPtosTlcTlpTlr = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                self.aMetricoNumPtosTlcTlpTr1 = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                    self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
                )
            else:
                self.aMetricoNumPtosTlcTlpTr1 = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        else:
            self.aMetricoNumPtosTlcTlpTlr = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aMetricoNumPtosTlcTlpTr1 = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarMetricoClasesSueloVegetacion:
            self.aMetricoProp09TodosLosRetornosSuelo = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoProp09TodosLosRetornosVeget = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                self.aMetricoProp09PrimerosRetornosSuelo = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                    self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
                )
                self.aMetricoProp09PrimerosRetornosVeget = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                    self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
                )
            else:
                self.aMetricoProp09PrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
                self.aMetricoProp09PrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        else:
            self.aMetricoProp09TodosLosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aMetricoProp09PrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aMetricoProp09TodosLosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aMetricoProp09PrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        if GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarMetricoClasesEdificio:
            self.aMetricoProp09TodosLosRetornosEdificio = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                self.aMetricoProp09PrimerosRetornosEdificio = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                    self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
                )
            else:
                self.aMetricoProp09PrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        else:
            self.aMetricoProp09TodosLosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aMetricoProp09PrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        if GLO.GLBLgrabarPuntosPorClaseLasOrig and GLO.GLBLgrabarMetricoClasesOtros:
            self.aMetricoProp09TodosLosRetornosOtros = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                self.aMetricoProp09PrimerosRetornosOtros = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                    self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
                )
            else:
                self.aMetricoProp09PrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
        else:
            self.aMetricoProp09TodosLosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
            self.aMetricoProp09PrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)


    # ==========================================================================
    # ->Nota: En iniciaVariablesParaVuelta2{} se crean otras tres arrays de subcelda:
    #  que complementan a estas:
    #     self.aSubCeldasCotaMiniMacroEsOk, self.aSubCeldasCotaMiniMicroEsOk
    #     self.aSubCeldasCotaMinAA, self.aSubCeldasCotaMaxAA
    #     self.aSubCeldasMdfCotaManual
    #     self.aSubCeldasMdfCotaConvol
    #     self.aSubCeldasMdfCotaConual
    #     self.'SubCeldasMdfCotaTransitoriaManual
    #     self.'SubCeldasMdfCotaTransitoriaConvol
    #     self.'SubCeldasMdfCotaTransitoriaConual
    #     self.aSubCeldasMdpCotaMacroManual, self.aSubCeldasMdpCotaMicroManual
    #     self.aSubCeldasMdpTipoCotaMacroManual, self.aSubCeldasMdpTipoCotaMicroManual
    #     self.aMultiCeldasTipoCotaAB
    #     self.aMultiCeldasEstruct
    #     self.aCeldasMdpNumPtosMiniMacro, self.aCeldasMdpNumPtosMiniMicro
    #
    #    aSubCeldasPuntoMiniSubCelPsel
    #    self.aSubCeldasPuntoMaxiSubCelPsel
    #    self.aSubCeldasMdgAjuste
    # ==========================================================================


#     # ==========================================================================
#     def iniciaVariablesParaVueltaN(self):
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and (
#             GLO.GLBLgrabarCeldasClasesSueloVegetacion
#             or GLO.GLBLgrabarCeldasClasesEdificio
#             or GLO.GLBLgrabarCeldasClasesOtros
#         ):
#             self.aCeldasNumPrimerosRetornosTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#         else:
#             self.aCeldasNumPrimerosRetornosTlp = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
#         # ======================================================================
# 
#         # ======================================================================
#         if (GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarCeldasClasesSueloVegetacion) or GLO.GLBLgrabarAlturasRptoAzMin:
#             self.aCeldasNumPrimerosRetornosSuelo = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#             self.aCeldasNumTodosLosRetornosSuelo = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#             self.aCeldasNumPrimerosRetornosVeget = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#             self.aCeldasNumTodosLosRetornosVeget = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#         else:
#             self.aCeldasNumPrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
#             self.aCeldasNumTodosLosRetornosSuelo = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
#             self.aCeldasNumPrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
#             self.aCeldasNumTodosLosRetornosVeget = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
# 
#         if (GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarCeldasClasesEdificio) or GLO.GLBLgrabarAlturasRptoAzMin:
#             self.aCeldasNumPrimerosRetornosEdificio = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#             self.aCeldasNumTodosLosRetornosEdificio = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#         else:
#             self.aCeldasNumPrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
#             self.aCeldasNumTodosLosRetornosEdificio = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
# 
#         if (GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarCeldasClasesOtros) or GLO.GLBLgrabarAlturasRptoAzMin:
#             self.aCeldasNumPrimerosRetornosOtros = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#             self.aCeldasNumTodosLosRetornosOtros = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#             self.aCeldasNumTodosLosRetornosOverlap = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
#         else:
#             self.aCeldasNumPrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
#             self.aCeldasNumTodosLosRetornosOtros = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
#             self.aCeldasNumTodosLosRetornosOverlap = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
#         # ======================================================================
# 
#         # ======================================================================
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and (
#             GLO.GLBLgrabarSubCeldasClasesSueloVegetacion
#             or GLO.GLBLgrabarSubCeldasClasesEdificio
#             or GLO.GLBLgrabarSubCeldasClasesOtros
#         ):
#             self.aSubCeldasNumPtosTlcTlpTlr = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                 GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#             )
#             if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
#                 self.aSubCeldasNumPtosTlcTlpTr1 = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                     GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#                 )
#             else:
#                 self.aSubCeldasNumPtosTlcTlpTr1 = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         else:
#             self.aSubCeldasNumPtosTlcTlpTlr = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aSubCeldasNumPtosTlcTlpTr1 = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
# 
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarSubCeldasClasesSueloVegetacion:
#             self.aSubCeldasProp09TodosLosRetornosSuelo = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                 GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#             )
#             self.aSubCeldasProp09TodosLosRetornosVeget = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                 GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#             )
#             if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
#                 self.aSubCeldasProp09PrimerosRetornosSuelo = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                     GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#                 )
#                 self.aSubCeldasProp09PrimerosRetornosVeget = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                     GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#                 )
#             else:
#                 self.aSubCeldasProp09PrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#                 self.aSubCeldasProp09PrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         else:
#             self.aSubCeldasProp09TodosLosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aSubCeldasProp09PrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aSubCeldasProp09TodosLosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aSubCeldasProp09PrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarSubCeldasClasesEdificio:
#             self.aSubCeldasProp09TodosLosRetornosEdificio = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                 GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#             )
#             if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
#                 self.aSubCeldasProp09PrimerosRetornosEdificio = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                     GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#                 )
#             else:
#                 self.aSubCeldasProp09PrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         else:
#             self.aSubCeldasProp09TodosLosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aSubCeldasProp09PrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarSubCeldasClasesOtros:
#             self.aSubCeldasProp09TodosLosRetornosOtros = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                 GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#             )
#             if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
#                 self.aSubCeldasProp09PrimerosRetornosOtros = np.zeros((GLBNsubCeldasPorCelda * self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY), dtype=np.uint8).reshape(
#                     GLBNsubCeldasPorCelda * self.nCeldasX, GLBNsubCeldasPorCelda * self.nCeldasY
#                 )
#             else:
#                 self.aSubCeldasProp09PrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         else:
#             self.aSubCeldasProp09TodosLosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aSubCeldasProp09PrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
# 
# 
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and (
#             GLO.GLBLgrabarMetricoClasesSueloVegetacion
#             or GLO.GLBLgrabarMetricoClasesEdificio
#             or GLO.GLBLgrabarMetricoClasesOtros
#         ):
#             self.aMetricoNumPtosTlcTlpTlr = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                 self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#             )
#             if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
#                 self.aMetricoNumPtosTlcTlpTr1 = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                     self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#                 )
#             else:
#                 self.aMetricoNumPtosTlcTlpTr1 = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         else:
#             self.aMetricoNumPtosTlcTlpTlr = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aMetricoNumPtosTlcTlpTr1 = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
# 
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarMetricoClasesSueloVegetacion:
#             self.aMetricoProp09TodosLosRetornosSuelo = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                 self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#             )
#             self.aMetricoProp09TodosLosRetornosVeget = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                 self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#             )
#             if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
#                 self.aMetricoProp09PrimerosRetornosSuelo = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                     self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#                 )
#                 self.aMetricoProp09PrimerosRetornosVeget = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                     self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#                 )
#             else:
#                 self.aMetricoProp09PrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#                 self.aMetricoProp09PrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         else:
#             self.aMetricoProp09TodosLosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aMetricoProp09PrimerosRetornosSuelo = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aMetricoProp09TodosLosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aMetricoProp09PrimerosRetornosVeget = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarMetricoClasesEdificio:
#             self.aMetricoProp09TodosLosRetornosEdificio = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                 self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#             )
#             if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
#                 self.aMetricoProp09PrimerosRetornosEdificio = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                     self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#                 )
#             else:
#                 self.aMetricoProp09PrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         else:
#             self.aMetricoProp09TodosLosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aMetricoProp09PrimerosRetornosEdificio = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         if GLO.GLBLgrabarPuntosPorClaseLasRecl and GLO.GLBLgrabarMetricoClasesOtros:
#             self.aMetricoProp09TodosLosRetornosOtros = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                 self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#             )
#             if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
#                 self.aMetricoProp09PrimerosRetornosOtros = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
#                     self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
#                 )
#             else:
#                 self.aMetricoProp09PrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#         else:
#             self.aMetricoProp09TodosLosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)
#             self.aMetricoProp09PrimerosRetornosOtros = np.zeros(1 * 1, dtype=np.uint8).reshape(1, 1)


    # ==========================================================================
    def iniciaVariablesParaSeleccionaPasadaTrasVuelta0(self):
        self.IDselec = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.IDsuelo = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.IDalter = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPasadasConPuntos = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)

        # ooooooooooooooo procedente de () oooooooooooooooo
        self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrSlpPselSinFiltrarSospechosos = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrClaPselSinFiltrarSospechosos = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrSuePselSinFiltrarSospechosos = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrSlpPsueSinFiltrarSospechosos = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrClaPsueSinFiltrarSospechosos = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrSuePsueSinFiltrarSospechosos = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        # ======================================================================

        # Estas 6 arrays se recalculan para cada celda (en la misma variable) y no se usan fuera de esta funcion
        self.myCeldaNumPtosTlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaNumPtosTlrSlpPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaNumPtosTlrClaPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaNumPtosTlrSuePorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaAngAcumTlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaAngMedTlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaMinX_TlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaMaxX_TlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaMinY_TlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaMaxY_TlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaRangoX_TlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaRangoY_TlrTlcPorPasada = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        self.myCeldaPasadasElegibles = np.full((self.numTotalPasadas), GLO.GLBLnoData, dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype)
        # Esta array es dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype (por eso la creo aqui, fuera de numba. Contiene los valores de cada una de las celdas y se guardan para despues
        self.aCeldasAngMedTlrTlcPorPasada = np.full(
            (self.nCeldasX, self.nCeldasY, self.numTotalPasadas),
            GLO.GLBLnoData,
            dtype=self.myLasHead.formatoDtypeIdValNotacionNpDtype
        )


    # ==========================================================================
    def iniciaVariablesParaVuelta1(self):
        # Estos se calculan en la vuelta 0:
        #    self.aCeldasNumPuntosTlrTlcTlpOk = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        #    #self.aCeldasListaPasadasConPuntos = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.object).reshape(self.nCeldasX, self.nCeldasY)
        #    self.aCeldasNumPuntosTlrTlcEcpOk = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.object).reshape(self.nCeldasX, self.nCeldasY)
        # Estos se calculan al seleccionar pasada:
        #    self.puntosTotales = 0 #Se calcula al seleccionar pasada
        #    self.IDselec = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        #    self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        # Estos se calculan en en chequeaNumeroDePuntosPorCelda{}; no los inicio aqui:
        #    self.celdasSinPuntos = 0 #Se calcula en chequeaNumeroDePuntosPorCelda{}
        #    self.celdasConPocosPuntosTotales = 0 #Se calcula en chequeaNumeroDePuntosPorCelda{}
        self.celdasConPocosPuntosPorPasada = 0

        # ======================================================================
        if GLO.GLBLmasasDeAgua:
            self.aCeldasMasasDeAgua = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasMasasDeAgua = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
        # ======================================================================

        self.numeroDeCeldasPorIDselec = {}
        for ID in self.listaPasadasBloque:
            if ID == GLO.GLBLnoData:
                break
            self.numeroDeCeldasPorIDselec[ID] = 0

        # Estos SI los almaceno para todo el bloque porque SI se usan despues
        # Se usa para interpolar:
        self.aCeldasPuntoMinAbsTlp = np.zeros(self.nCeldasX * self.nCeldasY * 3, dtype=np.float64).reshape(self.nCeldasX, self.nCeldasY, 3)
        self.aCeldasPuntoMinAbsTlp.fill(GLO.GLBLnoData)
        # Se usan en vuelta2 y para interpolar:
        self.aCeldasCotaMinAbsTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasCotaMinAbsTlp.fill(9999)
        self.aCeldasCotaMaxAbsTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasCotaMaxAbsTlp.fill(-9999)

        self.aCeldasPuntoMinAbsPse = np.zeros(self.nCeldasX * self.nCeldasY * 3, dtype=np.float64).reshape(self.nCeldasX, self.nCeldasY, 3)
        self.aCeldasPuntoMinAbsPse.fill(GLO.GLBLnoData)
        # Se usan en vuelta2 y para interpolar:
        self.aCeldasCotaMinAbsPse = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasCotaMinAbsPse.fill(9999)
        self.aCeldasCotaMaxAbsPse = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasCotaMaxAbsPse.fill(-9999)

        '''
        #Estos se usaban para ajustar pasada, ya no hacen falta
        self.myCeldaNumPtosTlrTlcPorPasada = {}
        self.anguloAcumPasadaSeleccionada = {}
        self.myCeldaNumPtosTlrSlpPorPasada = {}
        self.myCeldaNumPtosTlrClaPorPasada = {}
        self.myCeldaNumPtosTlrSuePorPasada = {}
        for ID in listaPasadasBloque:
            self.myCeldaNumPtosTlrTlcPorPasada[ID] = np.zeros(self.nCeldasX*self.nCeldasY, dtype='int32').reshape(self.nCeldasX, self.nCeldasY)
            self.anguloAcumPasadaSeleccionada[ID] = np.zeros(self.nCeldasX*self.nCeldasY, dtype='int32').reshape(self.nCeldasX, self.nCeldasY)
            self.myCeldaNumPtosTlrSlpPorPasada[ID] = np.zeros(self.nCeldasX*self.nCeldasY, dtype='int32').reshape(self.nCeldasX, self.nCeldasY)
            self.myCeldaNumPtosTlrClaPorPasada[ID] = np.zeros(self.nCeldasX*self.nCeldasY, dtype='int32').reshape(self.nCeldasX, self.nCeldasY)
            self.myCeldaNumPtosTlrSuePorPasada[ID] = np.zeros(self.nCeldasX*self.nCeldasY, dtype='int32').reshape(self.nCeldasX, self.nCeldasY)
        '''
        '''
        #Estos los calculo para cada celda en la vuelta 1a
        if GLO.GLBLleerGrabarCeldasEdge:
            self.aCeldasEdge =    np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY) #byte
            self.aCeldasEdge.fill(-9999)
        if GLO.GLBLgrabarPropiedadTime:
            self.aCeldasRawTime = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY) #float64
        if GLO.GLBLgrabarNumeroPuntosPorClase:
            self.aCeldasNumPuntosPorClase = np.zeros(self.nCeldasX*self.nCeldasY*GLO.GLBLnumMaximoDeClases, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY, GLO.GLBLnumMaximoDeClases)
        '''

        # ======================================================================
        self.aCeldasNumPuntosTlrTlcPselOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrTlcPsueOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrSuePselOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasNumPuntosTlrSuePsueOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        # ======================================================================
        self.aCeldasNumPuntosRpriTlcPselOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        if GLO.GLBLgrabarPrimerosVsSegundosRetornos:
            self.aCeldasNumPuntosRsigTlcPselOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumPuntosRsigTlcPselOk = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)
        # ======================================================================
        self.aCeldasCotaMediaTlrTlcTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasCotaMediaTlrSueTlp = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        # ======================================================================
        if GLO.GLBLgrabarCotasDiferenciaEntrePasadas or GLO.GLBLgrabarAlturasRptoAzMin:
            # Si no uso numba el NumPuntosTlrTlcPotrOk lo guardo para cada celda con miCeldaNumPtosTodosPasadaOtra (no necesito array de tipo aCeldas...)
            self.aCeldasNumPuntosTlrTlcPotrOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasCotaMediaTlrTlcPsel = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasCotaMediaTlrTlcPotr = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumPuntosTlrTlcPotrOk = np.zeros(1, dtype=np.int16).reshape(1, 1)
            self.aCeldasCotaMediaTlrTlcPsel = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aCeldasCotaMediaTlrTlcPotr = np.zeros(1, dtype=np.float32).reshape(1, 1)
        if GLO.GLBLgrabarCotasMediasPorClase:
            self.aCeldasNumPuntosTlrVegPselOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumPuntosTlrEdiPselOk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasCotaMediaTlrVegPsel = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasCotaMediaTlrEdiPsel = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasCotaMediaTlrSuePsel = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasCotaMediaTlrSuePsue = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumPuntosTlrVegPselOk = np.zeros(1, dtype=np.int16).reshape(1, 1)
            self.aCeldasNumPuntosTlrEdiPselOk = np.zeros(1, dtype=np.int16).reshape(1, 1)
            self.aCeldasCotaMediaTlrVegPsel = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aCeldasCotaMediaTlrEdiPsel = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aCeldasCotaMediaTlrSuePsel = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aCeldasCotaMediaTlrSuePsue = np.zeros(1, dtype=np.float32).reshape(1, 1)
        # ======================================================================

        # ======================================================================
        if GLO.GLBLcalcularMdg and GLO.GLBLcalcularSubCeldas and GLO.GLBLgrabarMdgAjusteSubCelda:
            self.aSubCeldasMdgAjuste = np.zeros((self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda, 4), dtype=np.float32)
        else:
            self.aSubCeldasMdgAjuste = np.zeros((1, 1, 4), dtype=np.float32)
        # ======================================================================


    # ==========================================================================
    def iniciaVariablesParaVuelta2(self):
        self.arrayTiposDePlanoPorCuadricula = np.zeros(3, dtype=self.myLasHead.formatoDtypeTipoPlanoNotacionNpDtype)
        listaTiposDePlano = [
            [0, 'Basal', GLO.GLBLcalcularMdb],
            [1, 'Cielo', GLO.GLBLcalcularMdc],
            [2, 'Major', GLO.GLBLcalcularMdm]
        ]
        for nTP in range(len(listaTiposDePlano)):
            # self.arrayTiposDePlanoPorCuadricula[nTP]['nTP'] = listaTiposDePlano[nTP][0]
            # self.arrayTiposDePlanoPorCuadricula[nTP]['Nombre'] = listaTiposDePlano[nTP][1]
            # self.arrayTiposDePlanoPorCuadricula[nTP]['Calcular'] = listaTiposDePlano[nTP][2]
            self.arrayTiposDePlanoPorCuadricula[nTP][0] = listaTiposDePlano[nTP][0]
            self.arrayTiposDePlanoPorCuadricula[nTP][1] = listaTiposDePlano[nTP][1]
            self.arrayTiposDePlanoPorCuadricula[nTP][2] = listaTiposDePlano[nTP][2]
        if GLO.GLBLverbose:
            print(f'\ncliddata-> self.arrayTiposDePlanoPorCuadricula: {self.arrayTiposDePlanoPorCuadricula}')
            for nTP in range(len(self.arrayTiposDePlanoPorCuadricula)):
                tipoPlano = self.arrayTiposDePlanoPorCuadricula[nTP][1].decode('utf-8')
                print(f'{TB}-> {tipoPlano} -> {self.arrayTiposDePlanoPorCuadricula[nTP][2]}')

        self.nCeldasConMatrizSingular = 0
        self.aCeldasAjustableMds = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)
        self.aCeldasAjustable = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)
        if GLO.GLBLajustarTambienConCeldasColindantes:
            self.aCeldasAjustable_ = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)

        # Estas las mantego
        if GLO.GLBLcalcularMdb:
            self.ajusteBasalElegido = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)  # byte
        else:
            self.ajusteBasalElegido = np.zeros(1 * 1, dtype=np.int8).reshape(1, 1)  # byte
        if GLO.GLBLcalcularMdc:
            self.ajusteCieloElegido = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)  # byte
        else:
            self.ajusteCieloElegido = np.zeros(1 * 1, dtype=np.int8).reshape(1, 1)  # byte

        # #ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        # #oooooooooooooo Arrays con los puntos max y min de la celda oooooooooooooooooo
        # #ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
        # if GLO.GLBLcalcularMdb or GLO.GLBLcalcularMdr:
        #     self.miCeldaPuntoMinPasadaSelecPorCuadranteA = \
        #             np.zeros(nColindantes*nColindantes*GLBNsubCeldasPorCelda*GLBNsubCeldasPorCelda*3, dtype=np.float64).reshape(nColindantes, nColindantes, GLBNsubCeldasPorCelda, GLBNsubCeldasPorCelda, 3)
        #     self.miCeldaPuntoMinPasadaSelecPorCuadranteB = \
        #             np.zeros(nColindantes*nColindantes*(GLBNsubCeldasPorCelda-1)*(GLBNsubCeldasPorCelda-1)*3, dtype=np.float64).reshape(nColindantes, nColindantes, (GLBNsubCeldasPorCelda-1), (GLBNsubCeldasPorCelda-1), 3)
        # else:
        #     self.miCeldaPuntoMinPasadaSelecPorCuadranteA = np.zeros(3, dtype=np.float64).reshape(1, 1, 1, 1, 3)
        #     self.miCeldaPuntoMinPasadaSelecPorCuadranteB = np.zeros(3, dtype=np.float64).reshape(1, 1, 1, 1, 3)
        # if GLO.GLBLcalcularMdc:
        #     self.miCeldaPuntoMaxPasadaSelecPorCuadranteA = \
        #             np.zeros(nColindantes*nColindantes*GLBNsubCeldasPorCelda*GLBNsubCeldasPorCelda*3, dtype=np.float64).reshape(nColindantes, nColindantes, GLBNsubCeldasPorCelda, GLBNsubCeldasPorCelda, 3)
        #     self.miCeldaPuntoMaxPasadaSelecPorCuadranteB = \
        #             np.zeros(nColindantes*nColindantes*(GLBNsubCeldasPorCelda-1)*(GLBNsubCeldasPorCelda-1)*3, dtype=np.float64).reshape(nColindantes, nColindantes, (GLBNsubCeldasPorCelda-1), (GLBNsubCeldasPorCelda-1), 3)
        # else:
        #     self.miCeldaPuntoMaxPasadaSelecPorCuadranteA = np.zeros(3, dtype=np.float64).reshape(1, 1, 1, 1, 3)
        #     self.miCeldaPuntoMaxPasadaSelecPorCuadranteB = np.zeros(3, dtype=np.float64).reshape(1, 1, 1, 1, 3)

        # Arrays para guardar el resultado de ajustar planos
        if GLO.GLBLcalcularMds:
            self.aCeldasCoeficientesMds = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            for nX in range(self.nCeldasX):
                for nY in range(self.nCeldasY):
                    self.aCeldasCoeficientesMds[nX, nY, 0] = -9999
                    self.aCeldasCoeficientesMds[nX, nY, 3] = -1
        else:
            self.aCeldasCoeficientesMds = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)

        # Arrays para guardar el resultado de ajustar planos
        if (GLO.GLBLcalcularMdg and GLO.GLBLgrabarMdgAjusteCelda) or GLO.GLBLcalcularMdp:
            self.aCeldasCoeficientesMdg = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            for nX in range(self.nCeldasX):
                for nY in range(self.nCeldasY):
                    self.aCeldasCoeficientesMdg[nX, nY, 0] = GLO.GLBLnoData
                    self.aCeldasCoeficientesMdg[nX, nY, 3] = -1
        else:
            self.aCeldasCoeficientesMdg = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)

        # Arrays para la interpolacion de puntos minimos
        if GLO.GLBLcalcularMdr:
            self.aCeldasMdrCoeficientes = np.zeros(self.nCeldasX * self.nCeldasY * 3, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 3)
            for nX in range(self.nCeldasX):
                for nY in range(self.nCeldasY):
                    self.aCeldasMdrCoeficientes[nX, nY, 0] = -9999
            if GLO.GLBLcalcularCotaDeSubceldasConGriddata:
                self.aSubCeldasMdrCotaInterpolada = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda * 4, dtype=np.float32
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda, 4)
            else:
                self.aSubCeldasMdrCotaInterpolada = np.zeros(1 * 3, dtype=np.float32).reshape(1, 1, 3)
        else:
            self.aCeldasMdrCoeficientes = np.zeros(1 * 1 * 3, dtype=np.float32).reshape(1, 1, 3)
            self.aSubCeldasMdrCotaInterpolada = np.zeros(1 * 3, dtype=np.float32).reshape(1, 1, 3)

        # Arrays para ajustar plano Pleno
        if GLO.GLBLcalcularMdp:
            self.aCeldasMdpAjuste = np.zeros(self.nCeldasX * self.nCeldasY * 7, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 7)
            # self.aCeldasCoeficientesMdpB = np.zeros(self.nCeldasX*self.nCeldasY*7, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 7)
            # Coef [0] = intercept
            # Coef [1:3] = pte lineal en x e y
            # Coef [3:5] = pte cuadratica en x e y
            # Coef [5] =
            #    Si es positivo: error cuadratico medio, que ademas no es muy elevado (< GLBLerrorResidualMedioFinalElevado)
            #    Si es negativo: plano/paraboloide no valido
            #        -1 ->Pocos puntos para ajustar plano (< 3)
            #        -2 ->El error cuadratico medio es muy elevado (self.aCeldasMdpAjuste[nX, nY][5] > GLBLerrorResidualMedioFinalElevado)
            #        -3 ->Paraboloide muy curvo -> se invalida (el coficiente cuadratico de araboloide genera una diferencia de cotas entre el centro y la arista superior a 2.5 m)
            #        -4 ->El plano ajustado no esta dentro del rango obtenido ampliando el rango [cotaMinimaPlanoPlenoA, cotaMaximaPlanoPlenoA] con +- 1 o 2 m -> se invalida
            #        -5 ->Demasiados saltos en las esquinas
            #        -6 ->Celdas pico
            #        -7 ->Sin asignar
            #        -8 ->Sin asignar
            #        -9 ->Identificador de que se trata de una cota por miniSubCel de subcelda central
            #             Es una asignacion inicial temporal que normalmente se sobreescribe por el ecmr o los valores negativos anteriores
            #       <-9 ->He restado 10 al codigo de celda no valida para indicar que se ha recalculado
            #             self.aCeldasMdpAjuste[nX, nY][5] = self.aCeldasMdpAjuste[nX, nY][5] - 10
            # Coef [6] = octante elegido

            for nX in range(self.nCeldasX):
                for nY in range(self.nCeldasY):
                    self.aCeldasMdpAjuste[nX, nY, -1] = -1
                    # self.aCeldasCoeficientesMdpB[nX, nY, -1] = -1

            if GLO.GLBLcalcularSubCeldas:
                self.aSubCeldasCotaMiniMacroEsOk = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasCotaMiniMicroEsOk = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)

                if GLO.GLBLcalcularMdfConMiniSubCelValidadosConMetodoManualPuro:
                    self.aSubCeldasMdfCotaManual = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasMdfCotaManual.fill(GLO.GLBLnoData)
                    self.aSubCeldasMdfCotaTransitoriaManual = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasMdfCotaTransitoriaManual.fill(GLO.GLBLnoData)
                else:
                    self.aSubCeldasMdfCotaManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                    self.aSubCeldasMdfCotaTransitoriaManual = np.zeros(1, dtype=np.float32).reshape(1, 1)

                if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModeloConvolucional:
                    self.aSubCeldasMdfCotaConvol = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasMdfCotaConvol.fill(GLO.GLBLnoData)
                    self.aSubCeldasMdfCotaTransitoriaConvol = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasMdfCotaTransitoriaConvol.fill(GLO.GLBLnoData)
                else:
                    self.aSubCeldasMdfCotaConvol = np.zeros(1, dtype=np.float32).reshape(1, 1)
                    self.aSubCeldasMdfCotaTransitoriaConvol = np.zeros(1, dtype=np.float32).reshape(1, 1)

                if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModConvoManualizado:
                    self.aSubCeldasMdfCotaConual = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasMdfCotaConual.fill(GLO.GLBLnoData)
                    self.aSubCeldasMdfCotaTransitoriaConual = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasMdfCotaTransitoriaConual.fill(GLO.GLBLnoData)
                else:
                    self.aSubCeldasMdfCotaConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                    self.aSubCeldasMdfCotaTransitoriaConual = np.zeros(1, dtype=np.float32).reshape(1, 1)

                self.aSubCeldasMdpCotaMacroManual = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                    self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                )
                self.aSubCeldasMdpCotaMacroManual.fill(GLO.GLBLnoData)
                self.aSubCeldasMdpCotaMicroManual = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                    self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                )
                self.aSubCeldasMdpCotaMicroManual.fill(GLO.GLBLnoData)
                self.aSubCeldasMdpTipoCotaMacroManual = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                # self.aSubCeldasMdpTipoCotaMacroManual.fill(GLO.GLBLnoData8bits)
                self.aSubCeldasMdpTipoCotaMicroManual = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                # self.aSubCeldasMdpTipoCotaMicroManual.fill(GLO.GLBLnoData8bits)

                if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModConvoManualizado:
                    self.aSubCeldasMdpCotaMacroConual = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasMdpCotaMacroConual.fill(GLO.GLBLnoData)
                    self.aSubCeldasMdpCotaMicroConual = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasMdpCotaMicroConual.fill(GLO.GLBLnoData)
                    self.aSubCeldasMdpTipoCotaMacroConual = np.zeros(
                        self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                    ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                    # self.aSubCeldasMdpTipoCotaMacroConual.fill(GLBLnoData8bits)
                    self.aSubCeldasMdpTipoCotaMicroConual = np.zeros(
                        self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                    ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                    # self.aSubCeldasMdpTipoCotaMicroConual.fill(GLBLnoData8bits)
                else:
                    self.aSubCeldasMdpCotaMacroConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                    self.aSubCeldasMdpCotaMicroConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                    self.aSubCeldasMdpTipoCotaMacroConual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                    self.aSubCeldasMdpTipoCotaMicroConual = np.zeros(1, dtype=np.uint8).reshape(1, 1)

                self.aMultiCeldasTipoCotaAB = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)
                # self.aMultiCeldasTipoCotaAB.fill(GLO.GLBLnoData8bits)
                self.aMultiCeldasEstruct = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)
                self.aMultiCeldasEstruct.fill(GLO.GLBLnoData8bits)
                self.aCeldasMdpNumPtosMiniMacro = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)
                self.aCeldasMdpNumPtosMiniMicro = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)

                # ======================================================================oooo
                # ->Nota: en {} se crean otras tres arrays de subcelda:
                #  que complementan a estas:
                #     self.aSubCeldasIntSRetMed, self.aSubCeldasIntSRetNum,
                #     self.aSubCeldasIntMRetMed, self.aSubCeldasIntMRetNum,
                #     self.aSubCeldasEVI2Med, self.aSubCeldasEVI2Num,
                #     self.aSubCeldasNDVIMed, self.aSubCeldasNDVINum,
                #     self.aSubCeldasNDWIMed, self.aSubCeldasNDWINum,
                #     self.aMetricoConBufferNumPuntosTlcTlpSingRet,
                #     self.aMetricoIntSRet,
                #     self.aMetricoConBufferNumPuntosTlcTlpPlurRet,
                #     self.aMetricoEVI2Med,
                #     self.aMetricoNDVIMed
                #     self.aMetricoNDWIMed
                # ======================================================================oooo

            else:
                self.aSubCeldasCotaMiniMacroEsOk = np.zeros(1, dtype=np.int8).reshape(1, 1)
                self.aSubCeldasCotaMiniMicroEsOk = np.zeros(1, dtype=np.int8).reshape(1, 1)
                self.aSubCeldasMdfCotaManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdfCotaTransitoriaManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdfCotaConvol = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdfCotaTransitoriaConvol = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdfCotaConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdfCotaTransitoriaConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdpCotaMacroManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdpCotaMicroManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdpTipoCotaMacroManual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                self.aSubCeldasMdpTipoCotaMicroManual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                self.aSubCeldasMdpCotaMacroConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdpCotaMicroConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasMdpTipoCotaMacroConual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                self.aSubCeldasMdpTipoCotaMicroConual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                self.aMultiCeldasTipoCotaAB = np.zeros(1, dtype=np.int8).reshape(1, 1)
                self.aMultiCeldasEstruct = np.zeros(1, dtype=np.int8).reshape(1, 1)
                self.aCeldasMdpNumPtosMiniMacro = np.zeros(1, dtype=np.int8).reshape(1, 1)
                self.aCeldasMdpNumPtosMiniMicro = np.zeros(1, dtype=np.int8).reshape(1, 1)

            if GLO.GLBLguardarLateralidadInterSubCeldasMinMax and GLO.GLBLcalcularSubCeldas and GLO.GLBLcalcularSubCeldas:
                self.aSubCeldasLateralidadMinMaxMacro = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasLateralidadMinMaxMesos = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasLateralidadMinMaxMicro = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
            else:
                self.aSubCeldasLateralidadMinMaxMacro = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasLateralidadMinMaxMesos = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasLateralidadMinMaxMicro = np.zeros(1, dtype=np.float32).reshape(1, 1)
            if GLO.GLBLguardarLateralidadInterSubCeldasMinMin and GLO.GLBLcalcularSubCeldas and GLO.GLBLcalcularSubCeldas:
                self.aSubCeldasLateralidadMinMinMacro = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasLateralidadMinMinMesos = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasLateralidadMinMinMicro = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
            else:
                self.aSubCeldasLateralidadMinMinMacro = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasLateralidadMinMinMesos = np.zeros(1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasLateralidadMinMinMicro = np.zeros(1, dtype=np.float32).reshape(1, 1)
            if GLO.GLBLguardarRugosidadInterSubCeldas and GLO.GLBLcalcularSubCeldas and GLO.GLBLcalcularSubCeldas:
                self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas.fill(GLO.GLBLnoData8bits)
                self.aSubCeldasRugosidadMinMaxMesosInterSubCeldas = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasRugosidadMinMaxMesosInterSubCeldas.fill(GLO.GLBLnoData8bits)
                self.aSubCeldasRugosidadMinMaxMicroInterSubCeldas = np.zeros(
                    self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
                ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
                self.aSubCeldasRugosidadMinMaxMicroInterSubCeldas.fill(GLO.GLBLnoData8bits)
            else:
                self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                self.aSubCeldasRugosidadMinMaxMesosInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                self.aSubCeldasRugosidadMinMaxMicroInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            if GLO.GLBLguardarRugosidadMultiCeldas and GLO.GLBLcalcularSubCeldas and GLO.GLBLcalcularSubCeldas:
                self.aMultiCeldasRugosidadMacroInterSubCeldas = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.uint8).reshape(self.nCeldasX, self.nCeldasY)
                self.aMultiCeldasRugosidadMacroInterSubCeldas.fill(GLO.GLBLnoData8bits)
                self.aMultiCeldasRugosidadMesosInterSubCeldas = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.uint8).reshape(self.nCeldasX, self.nCeldasY)
                self.aMultiCeldasRugosidadMesosInterSubCeldas.fill(GLO.GLBLnoData8bits)
                self.aMultiCeldasRugosidadMicroInterSubCeldas = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.uint8).reshape(self.nCeldasX, self.nCeldasY)
                self.aMultiCeldasRugosidadMicroInterSubCeldas.fill(GLO.GLBLnoData8bits)
            else:
                self.aMultiCeldasRugosidadMacroInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                self.aMultiCeldasRugosidadMesosInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
                self.aMultiCeldasRugosidadMicroInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)

        else:
            self.aCeldasMdpAjuste = np.zeros(1 * 1 * 6, dtype=np.float32).reshape(1, 1, 6)

            self.aSubCeldasCotaMiniMacroEsOk = np.zeros(1, dtype=np.int8).reshape(1, 1)
            self.aSubCeldasCotaMiniMicroEsOk = np.zeros(1, dtype=np.int8).reshape(1, 1)
            self.aSubCeldasMdfCotaManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdfCotaTransitoriaManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdfCotaConvol = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdfCotaTransitoriaConvol = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdfCotaConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdfCotaTransitoriaConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdpCotaMacroManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdpCotaMicroManual = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdpTipoCotaMacroManual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasMdpTipoCotaMicroManual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasMdpCotaMacroConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdpCotaMicroConual = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdpTipoCotaMacroConual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasMdpTipoCotaMicroConual = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aMultiCeldasTipoCotaAB = np.zeros(1, dtype=np.int8).reshape(1, 1)
            self.aMultiCeldasEstruct = np.zeros(1, dtype=np.int8).reshape(1, 1)
            self.aCeldasMdpNumPtosMiniMacro = np.zeros(1, dtype=np.int8).reshape(1, 1)
            self.aCeldasMdpNumPtosMiniMicro = np.zeros(1, dtype=np.int8).reshape(1, 1)

            self.aSubCeldasLateralidadMinMaxMacro = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasLateralidadMinMaxMesos = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasLateralidadMinMaxMicro = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasLateralidadMinMinMacro = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasLateralidadMinMinMesos = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasLateralidadMinMinMicro = np.zeros(1, dtype=np.float32).reshape(1, 1)

            self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasRugosidadMinMaxMesosInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasRugosidadMinMaxMicroInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aMultiCeldasRugosidadMacroInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aMultiCeldasRugosidadMesosInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)
            self.aMultiCeldasRugosidadMicroInterSubCeldas = np.zeros(1, dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLcalcularMdb:
            self.aCeldasCoeficientesMdb_ = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            self.aCeldasCoeficientesMdbSC = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            self.aCeldasCoeficientesMdbCC = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            self.aCeldasCoeficientesMdbA = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            for nX in range(self.nCeldasX):
                for nY in range(self.nCeldasY):
                    self.aCeldasCoeficientesMdb_[nX, nY, 3] = -1
                    self.aCeldasCoeficientesMdbA[nX, nY, 3] = -1
            # Se usa para interpolar?:
            self.aCeldasCotaMediaBasal = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasRangoBasal = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            if GLO.GLBLcalcularMdbCotaSubcelda:
                self.aSubCeldasMdb = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                    self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                )
                self.aSubCeldasMdb.fill(GLO.GLBLnoData)
            else:
                self.aSubCeldasMdb = np.zeros(1, dtype=np.float32).reshape(1, 1)
        else:
            self.aCeldasCoeficientesMdb_ = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)
            self.aCeldasCoeficientesMdbSC = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)
            self.aCeldasCoeficientesMdbCC = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)
            self.aCeldasCoeficientesMdbA = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)
            self.aCeldasCotaMediaBasal = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasRangoBasal = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdb = np.zeros(1, dtype=np.float32).reshape(1, 1)
        if GLO.GLBLcalcularMdc:
            self.aCeldasCoeficientesMdc_ = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            self.aCeldasCoeficientesMdcA = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            self.aCeldasCotaMediaCielo = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasRangoCielo = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasCoeficientesMdc_ = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)
            self.aCeldasCoeficientesMdcA = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)
            self.aCeldasCotaMediaCielo = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasRangoCielo = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)

        if GLO.GLBLcalcularMdm:
            self.aCeldasCoeficientesMdm = np.zeros(self.nCeldasX * self.nCeldasY * 10, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY, 10)
            self.aCeldasCotaMediaMajor = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasNumPuntosAjusteMajor = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
            for nX in range(self.nCeldasX):
                for nY in range(self.nCeldasY):
                    self.aCeldasCoeficientesMdm[nX, nY, 3] = -1
        else:
            self.aCeldasCoeficientesMdm = np.zeros(1 * 1 * 10, dtype=np.float32).reshape(1, 1, 10)
            self.aCeldasCotaMediaMajor = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasNumPuntosAjusteMajor = np.zeros(1 * 1, dtype=np.int16).reshape(1, 1)

        if GLO.GLBLcalcularMdb or GLO.GLBLcalcularMdc or GLO.GLBLcalcularMdm:
            self.aCeldasCoeficientesMdxAll = np.full(
                (self.nCeldasX, self.nCeldasY, len(self.arrayTiposDePlanoPorCuadricula), 10), GLO.GLBLnoData, dtype=np.float32)
            for nTP in range(len(self.arrayTiposDePlanoPorCuadricula)):
                for nX in range(self.nCeldasX):
                    for nY in range(self.nCeldasY):
                        self.aCeldasCoeficientesMdxAll[nX, nY, nTP, 3] = -1

            self.aCeldasCotaMediaMdx = np.full(
                (len(self.arrayTiposDePlanoPorCuadricula), self.nCeldasX, self.nCeldasY), GLO.GLBLnoData, dtype=np.float32)
            if GLO.GLBLajustarTambienConCeldasColindantes:
                self.aCeldasCoeficientesMdxAlt = np.full(
                    (self.nCeldasX, self.nCeldasY, len(self.arrayTiposDePlanoPorCuadricula), 10), GLO.GLBLnoData, dtype=np.float32
                )
                self.aCeldasCotaMediaMdy = np.full(
                    (len(self.arrayTiposDePlanoPorCuadricula), self.nCeldasX, self.nCeldasY), GLO.GLBLnoData, dtype=np.float32
                )
            self.aCeldasCoeficientesMdxRing = np.full(
                    (self.nCeldasX, self.nCeldasY, len(self.arrayTiposDePlanoPorCuadricula), 4), GLO.GLBLnoData, dtype=np.float32)
        else:
            self.aCeldasCoeficientesMdxAll = np.full((1, 1, 1, 10), GLO.GLBLnoData, dtype=np.float32)
            self.aCeldasCotaMediaMdx = np.full((1, 1, 1), GLO.GLBLnoData, dtype=np.float32)
            if GLO.GLBLajustarTambienConCeldasColindantes:
                self.aCeldasCoeficientesMdxAlt = np.full((1, 1, 1, 10), GLO.GLBLnoData, dtype=np.float32)
                self.aCeldasCotaMediaMdy = np.full((1, 1, 1), GLO.GLBLnoData, dtype=np.float32)
            self.aCeldasCoeficientesMdxRing = np.full((1, 1, 1, 4), GLO.GLBLnoData, dtype=np.float32)

        if GLO.GLBLcalcularMdk2mConPuntosClasificados:
            self.aSubCeldasMdkCotaMed = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasMdkCotaMin = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasMdkCotaMin.fill(9999)
            self.aSubCeldasMdkCotaItp = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasMdkCotaItp.fill(GLO.GLBLnoData)
            self.aSubCeldasMdkNumPtos = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
        else:
            self.aSubCeldasMdkCotaMed = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdkCotaMin = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdkCotaItp = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdkNumPtos = np.zeros(1, dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLcalcularMdc2mConTodosLosPuntos:
            self.aSubCeldasMdcCotaMax = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasMdcNumPtos = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
        else:
            self.aSubCeldasMdcCotaMax = np.zeros(1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasMdcNumPtos = np.zeros(1, dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLcalcularApices:
            self.aCeldasApices = np.zeros(self.nCeldasX * self.nCeldasY * 4, dtype=np.uint8).reshape(self.nCeldasX, self.nCeldasY, 4)
        else:
            self.aCeldasApices = np.zeros(1 * 1 * 4, dtype=np.uint8).reshape(1, 1, 4)


    # ==========================================================================
    def iniciaVariablesParaVuelta3(self, cTP):
        # self.aCeldasUrbanasDePlanosTejadoOld = np.zeros(self.nCeldasX*self.nCeldasY*2, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY, 2)
        # self.aCeldasMegasRugosidadOld = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        # self.aCeldasRugosidadMacroOld = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        # self.aCeldasRugosidadMesosOld = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        # self.aCeldasRugosidadMicroOld = np.zeros(self.nCeldasX*self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)

        self.aCeldasNumDisrupciones = np.zeros(self.nCeldasX * self.nCeldasY * len(cTP) * 2, dtype=np.int16).reshape(
            self.nCeldasX, self.nCeldasY, len(cTP), 2
        )
        self.aCeldasGrano = np.zeros(self.nCeldasX * self.nCeldasY * len(cTP) * 2, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY, len(cTP), 2)
        self.aCeldasConAjusteNoFiable = np.zeros(self.nCeldasX * self.nCeldasY * len(cTP), dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY, len(cTP))


    # ==========================================================================
    def iniciaVariablesParaVuelta4(self):

        # Estas dos variables se crean para el caso de que no se ejecute clidnv4.procesaCeldasVuelta4{}
        # y guarde los arrays (y estas variables) en npz, para que no de error la grabacion del npz
        self.nContadorPuntosTodos = 0
        self.nPlanosEnElBloque = 0
        self.aNumPuntosEnPlanosPorLotesParaExportarConResiduos = np.array([0, 0], dtype=np.int32)

        if GLO.GLBLguardarCapaRugosidadInterCeldillasCeldas or GLBNmuestreoAcumulativoOEntrenamientoOInferencia:
            self.aCeldasRugosidadMegasInterCeldillas = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.uint8).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasRugosidadMacroInterCeldillas = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.uint8).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasRugosidadMesosInterCeldillas = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.uint8).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasRugosidadMicroInterCeldillas = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.uint8).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasRugosidadMegasInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aCeldasRugosidadMacroInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aCeldasRugosidadMesosInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aCeldasRugosidadMicroInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLguardarCapaRugosidadInterCeldillasSubCeldas or GLBNmuestreoAcumulativoOEntrenamientoOInferencia:
            self.aSubCeldasRugosidadMegasInterCeldillas = np.zeros(
                self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
            ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
            self.aSubCeldasRugosidadMacroInterCeldillas = np.zeros(
                self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
            ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
            self.aSubCeldasRugosidadMesosInterCeldillas = np.zeros(
                self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
            ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
            self.aSubCeldasRugosidadMicroInterCeldillas = np.zeros(
                self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8
            ).reshape(self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda)
            self.aSubCeldasNumPuntos = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.int16).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
        else:
            self.aSubCeldasRugosidadMegasInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasRugosidadMacroInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasRugosidadMesosInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasRugosidadMicroInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aSubCeldasNumPuntos = np.zeros((1 * 1), dtype=np.int16).reshape(1, 1)

        if GLO.GLBLguardarCapaRugosidadInterCeldillasMetrico or GLBNmuestreoAcumulativoOEntrenamientoOInferencia:
            self.aMetricoRugosidadMegasInterCeldillas = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoRugosidadMacroInterCeldillas = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoRugosidadMesosInterCeldillas = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            self.aMetricoRugosidadMicroInterCeldillas = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
        else:
            self.aMetricoRugosidadMegasInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aMetricoRugosidadMacroInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aMetricoRugosidadMesosInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aMetricoRugosidadMicroInterCeldillas = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoCeldas:
            self.aCeldasNumeroDePlanosTejado = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)
            self.aCeldasPuntosEnPlanosTejado = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY)
        else:
            self.aCeldasNumeroDePlanosTejado = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)
            self.aCeldasPuntosEnPlanosTejado = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoSubCeldas:
            self.aSubCeldasPlanoTejado = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.uint8).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
        else:
            self.aSubCeldasPlanoTejado = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)

        if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoMetrico or GLBNmuestreoAcumulativoOEntrenamientoOInferencia:
            self.aMetricoPlanoTejado = np.zeros((self.myLasHead.metrosBloqueX * self.myLasHead.metrosBloqueY), dtype=np.uint8).reshape(
                self.myLasHead.metrosBloqueX, self.myLasHead.metrosBloqueY
            )
            # self.aMetricoPlanoTejado.fill(GLO.GLBLnoData8bits)
        else:
            self.aMetricoPlanoTejado = np.zeros((1 * 1), dtype=np.uint8).reshape(1, 1)


    # ==========================================================================
    def iniciaVariablesParaVuelta5(self):
        self.aCeldaInterpolada = np.full((self.nCeldasX, self.nCeldasY), False)


    # ==========================================================================
    def iniciaVariablesParaVuelta6DasoLidar(self, soloMdk=False):
        if soloMdk:
            print('clidnat-> Iniciando VariablesParaVuelta6DasoLidar solo Mdk')
        self.totalNumRprimPsel = 0
        self.numPtosUsadosNoSospechosos = 0
        self.numPtosSospechosos = 0
        self.numPtosUsadosInclSospechosos = 0
        if not soloMdk:
            # self.aCeldasUrbanas = np.zeros(self.nCeldasX * self.nCeldasY * 2, dtype=np.int16).reshape(self.nCeldasX, self.nCeldasY, 2)
            self.aCeldasAjustable = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.int8).reshape(self.nCeldasX, self.nCeldasY)
    
            if GLO.GLBLgrabarPercentilesAbsolutos:
                self.aCeldasCotaMin10 = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                self.aCeldasCotaMax95 = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
            else:
                self.aCeldasCotaMin10 = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aCeldasCotaMax95 = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
    
            if GLO.GLBLgrabarPercentilesRelativos:
                if GLO.GLBLcalcularMds:
                    self.aCeldasAlt95SobreMds = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                    self.aCeldasAlt95SobreMds.fill(GLO.GLBLnoData)
                    if GLO.GLBLgrabarPercentilAdicional:
                        self.aCeldasAltXxSobreMds = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                        self.aCeldasAltXxSobreMds.fill(GLO.GLBLnoData)
                    else:
                        self.aCeldasAltXxSobreMds = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                else:
                    self.aCeldasAlt95SobreMds = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                    self.aCeldasAltXxSobreMds = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                if GLO.GLBLcalcularMdb:
                    self.aCeldasAlt95SobreMdb = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                    self.aCeldasAlt95SobreMdb.fill(GLO.GLBLnoData)
                    if GLO.GLBLgrabarPercentilAdicional:
                        self.aCeldasAltXxSobreMdb = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                        self.aCeldasAltXxSobreMdb.fill(GLO.GLBLnoData)
                    else:
                        self.aCeldasAltXxSobreMdb = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                else:
                    self.aCeldasAlt95SobreMdb = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                    self.aCeldasAltXxSobreMdb = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                if GLO.GLBLcalcularMdp:
                    self.aCeldasAlt95SobreMdf = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                    self.aCeldasAlt95SobreMdf.fill(GLO.GLBLnoData)
                    if GLO.GLBLgrabarPercentilAdicional:
                        self.aCeldasAltXxSobreMdf = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                        self.aCeldasAltXxSobreMdf.fill(GLO.GLBLnoData)
                    else:
                        self.aCeldasAltXxSobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                    if GLO.GLBLgrabarPercentilesSubCeldas:
                        self.aSubCeldasAlt95SobreMdf = np.zeros(
                            self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32
                        ).reshape(
                            self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                        )
                        self.aSubCeldasAlt95SobreMdf.fill(GLO.GLBLnoData)
                    else:
                        self.aSubCeldasAlt95SobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                else:
                    self.aCeldasAlt95SobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                    self.aCeldasAltXxSobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                    self.aSubCeldasAlt95SobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            else:
                self.aCeldasAlt95SobreMds = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aCeldasAltXxSobreMds = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aCeldasAlt95SobreMdb = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aCeldasAltXxSobreMdb = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aCeldasAlt95SobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aCeldasAltXxSobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasAlt95SobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
        else:
            self.aCeldasAjustable = np.zeros(1 * 1, dtype=np.int8).reshape(1, 1)
            self.aCeldasCotaMin10 = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasCotaMax95 = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasAlt95SobreMds = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasAltXxSobreMds = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasAlt95SobreMdb = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasAltXxSobreMdb = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasAlt95SobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasAltXxSobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasAlt95SobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)

        if GLO.GLBLgrabarPercentilesRelativos:
            if GLO.GLBLcalcularMdk2mConPuntosClasificados:
                self.aCeldasAlt95SobreMdk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                self.aCeldasAlt95SobreMdk.fill(GLO.GLBLnoData)
                if GLO.GLBLgrabarPercentilAdicional:
                    self.aCeldasAltXxSobreMdk = np.zeros(self.nCeldasX * self.nCeldasY, dtype=np.float32).reshape(self.nCeldasX, self.nCeldasY)
                    self.aCeldasAltXxSobreMdk.fill(GLO.GLBLnoData)
                else:
                    self.aCeldasAltXxSobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                if GLO.GLBLgrabarPercentilesSubCeldas:
                    self.aSubCeldasAlt95SobreMdk = np.zeros(
                        self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32
                    ).reshape(
                        self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                    )
                    self.aSubCeldasAlt95SobreMdk.fill(GLO.GLBLnoData)
                else:
                    self.aSubCeldasAlt95SobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            else:
                self.aCeldasAlt95SobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aCeldasAltXxSobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                self.aSubCeldasAlt95SobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
        else:
            self.aCeldasAlt95SobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aCeldasAltXxSobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
            self.aSubCeldasAlt95SobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)

        if not soloMdk:
            if len(self.listaRangos_AlturasMasDe) > 1:
                if GLO.GLBLcalcularMds:
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasMasDe) - 0), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasMasDe) - 0))
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds.fill(GLO.GLBLnoData8bits)
                else:
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                if GLO.GLBLcalcularMdb:
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasMasDe) - 0), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasMasDe) - 0))
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb.fill(GLO.GLBLnoData8bits)
                else:
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                if GLO.GLBLcalcularMdp:
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasMasDe) - 0), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasMasDe) - 0))
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf.fill(GLO.GLBLnoData8bits)
                else:
                    self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
            else:
                self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)

        if len(self.listaRangos_AlturasMasDe) > 1:
            if GLO.GLBLcalcularMdk2mConPuntosClasificados:
                self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk = np.zeros(
                    self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasMasDe) - 0), dtype=np.int8
                ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasMasDe) - 0))
                self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk.fill(GLO.GLBLnoData8bits)
            else:
                self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
        else:
            self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)

        if not soloMdk:
            if len(self.listaRangos_AlturasRango) > 1:
                if GLO.GLBLcalcularMds:
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmds = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasRango) - 1), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasRango) - 1))
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmds.fill(GLO.GLBLnoData8bits)
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmds = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasRango) - 1), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasRango) - 1))
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmds.fill(GLO.GLBLnoData8bits)
                else:
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmds = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmds = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                if GLO.GLBLcalcularMdb:
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasRango) - 1), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasRango) - 1))
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb.fill(GLO.GLBLnoData8bits)
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasRango) - 1), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasRango) - 1))
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb.fill(GLO.GLBLnoData8bits)
                else:
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                if GLO.GLBLcalcularMdp:
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasRango) - 1), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasRango) - 1))
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf.fill(GLO.GLBLnoData8bits)
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasRango) - 1), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasRango) - 1))
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf.fill(GLO.GLBLnoData8bits)
                else:
                    self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                    self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
            else:
                self.aCeldasNumTodosLosRetornosAltRangoRptoAmds = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                self.aCeldasNumPrimerosRetornosAltRangoRptoAmds = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)

        if len(self.listaRangos_AlturasRango) > 1:
            if GLO.GLBLcalcularMdk2mConPuntosClasificados:
                self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk = np.zeros(
                    self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasRango) - 1), dtype=np.int8
                ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasRango) - 1))
                self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk.fill(GLO.GLBLnoData8bits)
                self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk = np.zeros(
                    self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasRango) - 1), dtype=np.int8
                ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasRango) - 1))
                self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk.fill(GLO.GLBLnoData8bits)
            else:
                self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
                self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
        else:
            self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
            self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)

        # ======================================================================
        if not soloMdk:
            if GLO.GLBLcalcularMdb:
                if len(self.listaRangos_AlturasPctjTxt) > 1:
                    self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb = np.zeros(
                        self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasPctjTxt) - 1), dtype=np.int8
                    ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasPctjTxt) - 1))
                    self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb.fill(GLO.GLBLnoData8bits)
                else:
                    self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
            else:
                self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)

        if len(self.listaRangos_AlturasPctjTxt) > 1:
            if GLO.GLBLcalcularMdk2mConPuntosClasificados:
                self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk = np.zeros(
                    self.nCeldasX * self.nCeldasY * (len(self.listaRangos_AlturasPctjTxt) - 1), dtype=np.int8
                ).reshape(self.nCeldasX, self.nCeldasY, (len(self.listaRangos_AlturasPctjTxt) - 1))
                self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk.fill(GLO.GLBLnoData8bits)
            else:
                self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
        else:
            self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk = np.zeros(1, dtype=np.int8).reshape(1, 1, 1)
        # ======================================================================

        if not soloMdk:
            if GLO.GLBLgrabarSubCeldasAltMaxSobreMdf or (GLO.GLBLgrabarHiperFormas and GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoSubCeldas):
                self.aSubCeldasAltMaxSobreMdf = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                    self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
                )
                self.aSubCeldasAltMaxSobreMdf.fill(GLO.GLBLnoData)
            else:
                self.aSubCeldasAltMaxSobreMdf = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                
        if GLO.GLBLgrabarSubCeldasAltMaxSobreMdk:
            self.aSubCeldasAltMaxSobreMdk = np.zeros(self.nCeldasX * GLBNsubCeldasPorCelda * self.nCeldasY * GLBNsubCeldasPorCelda, dtype=np.float32).reshape(
                self.nCeldasX * GLBNsubCeldasPorCelda, self.nCeldasY * GLBNsubCeldasPorCelda
            )
            self.aSubCeldasAltMaxSobreMdk.fill(GLO.GLBLnoData)
        else:
            self.aSubCeldasAltMaxSobreMdk = np.zeros(1 * 1, dtype=np.float32).reshape(1, 1)
                

    # ==========================================================================
    def liberaArraysTrasVuelta01(
            self,
            interrumpidoPorError=False,
            completo=False,
            arraysGuardadas=False,
        ):
        if GLO.GLBLgrabarPrimerosVsSegundosRetornos:
            del self.aCeldasNumSingleReturnTlp
            del self.aCeldasNumMultiReturnTlp
            del self.aCeldasNumPrimerosRetornosTlp
            del self.aCeldasNumSiguientesRetornosTlp
        if GLO.GLBLgrabarCeldasClasesSueloVegetacion or GLO.GLBLgrabarAlturasRptoAzMin:
            del self.aCeldasNumPrimerosRetornosSuelo
            del self.aCeldasNumTodosLosRetornosSuelo # Ya no se usa en cliddata.guardarMiscelaneaDasoLidar{}
            del self.aCeldasNumPrimerosRetornosVeget
            del self.aCeldasNumTodosLosRetornosVeget # Ya no se usa en cliddata.guardarMiscelaneaDasoLidar{}
        if GLO.GLBLgrabarCeldasClasesEdificio:
            del self.aCeldasNumPrimerosRetornosEdificio # Ya no se usa en cliddata.guardarMiscelaneaDasoLidar{}
            del self.aCeldasNumTodosLosRetornosEdificio # Ya no se usa en cliddata.guardarMiscelaneaDasoLidar{}
        if GLO.GLBLgrabarCeldasClasesOtros:
            del self.aCeldasNumPrimerosRetornosOtros
            del self.aCeldasNumTodosLosRetornosOtros
            del self.aCeldasNumTodosLosRetornosOverlap

        # del self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos #Lo uso para guardarlo con grabarMiscelanea() en numPuntosPasadaSelecSinFiltrarSospechosos
        del self.aCeldasNumPuntosTlrSlpPselSinFiltrarSospechosos
        # del self.aCeldasNumPuntosTlrClaPselSinFiltrarSospechosos #La uso para saber si hay puntos clasificados y segun eso, filtrar las cotas minimas a solo celdas con suelo en interpolarPlanos<>
        # del self.aCeldasNumPuntosTlrSuePselSinFiltrarSospechosos #La uso para saber si hay puntos suelo y segun eso, filtrar las cotas minimas a solo celdas con suelo en interpolarPlanos<>
        del self.aCeldasNumPuntosTlrSlpPsueSinFiltrarSospechosos
        del self.aCeldasNumPuntosTlrClaPsueSinFiltrarSospechosos

        # del self.aCeldasNumPuntosTlrSuePsueSinFiltrarSospechosos #Lo borro tras vuelta1

        if not arraysGuardadas:
            # Estas arrays son auxiliares y se usan internamente en clidnv0.py;
            # su contenido no se devuelve a clidflow.py
            if GLO.GLBLgrabarIndicesVegetacionNDVIetAlMetricos or GLBNmuestreoAcumulativoOEntrenamientoOInferencia:
                del self.aMetricoConBufferNumPuntosTlcTlpSingRet
                del self.aMetricoConBufferNumPuntosTlcTlpPlurRet
            if GLO.GLBLgrabarIndicesVegetacionNDVIetAlSubCelda or GLBNmuestreoAcumulativoOEntrenamientoOInferencia:
                del self.aSubCeldasIntSRetNum
                del self.aSubCeldasIntMRetNum
                del self.aSubCeldasEVI2Num
                del self.aSubCeldasNDVINum
                del self.aSubCeldasNDWINum

    # ==========================================================================
    def liberaArraysTrasVuelta2(self, interrumpidoPorError=False, completo=False):
        # Estos son equivalentes con y sin numba pero sin numba ya se graban en procesaCeldasVuelta1b()
        # self.aCeldasCotaMinAbsTlp
        # self.aCeldasCotaMaxAbsTlp
        print('cliddata-> Eliminando variables de memoria tras vuelta2')

        del self.aCeldasNumPuntosTlrSuePsueSinFiltrarSospechosos

        del self.aCeldasAjustable
        del self.aCeldasAjustableMds
        del (
            self.aCeldasAngMedTlrTlcPorPasada
        )  # Si no uso Numba se guardan como dictionary en vez de ndArray -> self.aCeldasAnguloMedPasadaSel[IDsel][nX, nY]
        if GLO.GLBLcalcularMdb or GLO.GLBLcalcularMdc or GLO.GLBLcalcularMdm:
            #del self.aCeldasCoeficientesMdb
            del self.aCeldasCoeficientesMdbSC
            del self.aCeldasCoeficientesMdbCC

        # if GLO.GLBLcalcularMdb:
        #    del self.aCeldasCoeficientesMdb_
        if GLO.GLBLcalcularMdb:
            del self.aCeldasCoeficientesMdbA
            # del self.aCeldasCoeficientesMdbB
        if GLO.GLBLcalcularMdb or GLO.GLBLcalcularMdc or GLO.GLBLcalcularMdm:
            del self.aCeldasCoeficientesMdc
        # if GLO.GLBLcalcularMdc:
        #    del self.
        if GLO.GLBLcalcularMdc:
            del self.aCeldasCoeficientesMdcA
            # del self.aCeldasCoeficientesMdcB
        if (GLO.GLBLcalcularMdg and GLO.GLBLgrabarMdgAjusteCelda) or GLO.GLBLcalcularMdp:
            del self.aCeldasCoeficientesMdg
        # if GLO.GLBLcalcularMdm:
        #    del self.aCeldasCoeficientesMdm
        # if GLO.GLBLcalcularMds:
        #    del self.aCeldasCoeficientesMds
        if GLO.GLBLcalcularMdb or GLO.GLBLcalcularMdc or GLO.GLBLcalcularMdm:
            del self.aCeldasCoeficientesMdxAll
            del self.aCeldasCotaMediaMdx
        # del self.aCeldasCotaMaxAbsTlp
        del self.aCeldasCotaMediaBasal
        del self.aCeldasCotaMediaCielo
        del self.aCeldasCotaMediaMajor

        if GLO.GLBLgrabarCotasDiferenciaEntrePasadas or GLO.GLBLgrabarAlturasRptoAzMin or True:
            # del self.aCeldasCotaMediaTlrSuePsel # Se usa en clidnv6.calculaVariablesDasoLidar(). Si no uso Numba, se llama de otra forma -> self.aCeldasCotaMediaTlrSue[nX, nY]
            # del self.aCeldasCotaMediaTlrSueTlp # Se usa en clidnv6.calculaVariablesDasoLidar().
            del self.aCeldasCotaMediaTlrTlcPsel  # Si no uso Numba, se calcula y graba cada celda -> self.miCeldaCotaMediaPasadaSeleccionada
            del self.aCeldasCotaMediaTlrTlcPotr
            # del self.aCeldasCotaMediaTlrTlcTlp #Se usa en clidnv6.calculaVariablesDasoLidar()
        if GLO.GLBLgrabarCotasMediasPorClase or True:
            del self.aCeldasCotaMediaTlrVegPsel  # Si no uso Numba, se calcula y graba cada celda -> ??self.miCeldaCotaMediaV****
            del self.aCeldasCotaMediaTlrEdiPsel  # Si no uso Numba, se calcula y graba cada celda -> ??self.miCeldaCotaMedia*****
            # del self.aCeldasCotaMinAbsTlp
        if GLO.GLBLleerGrabarCeldasEdge or True:
            del self.aCeldasEsCeldaEdge  # Si no uso Numba, se calcula y graba cada celda -> self.esCeldaEdge
        # ======================================================================oooo
        # Me valdria con guardar las coordenadas, en vez de toda la info de punto
        # Revisar las propiedades que se utilizan en cada fase, especialmene de aqui en adelante
        # ======================================================================oooo
        if GLO.GLBLguardarPuntosSueloEnArrayPredimensionada:
            del self.aCeldasListaDePtosSueAll  # Importante
            del self.aCeldasListaDePtosSuePralPF99  # Importante
        # del self.aCeldasListaDePtosTlcAll #Se usa en clidnv6.calculaVariablesDasoLidar() y lasData.calculaVariablesDasoLidar()
        # del self.aCeldasListaDePtosTlcAux  # Array obsoleta; se usaba en self.calculaVariablesDasoLidar
        # del self.aCeldasListaDePtosTlcPralPF99 #Importante
        # ======================================================================oooo
        if GLO.GLBLgrabarNumIdPasada:
            del self.aCeldasNumPasadasConPuntos
        del self.aCeldasNumPtosPorClaseTlrTlp  # Si no uso Numba, se calcula y graba cada celda -> self.nPuntosPorClase[clase]
        del self.aCeldasNumPuntosAjusteMajor
        del self.aCeldasNumPuntosTlrTlcEcpOk
        del self.aCeldasNumPuntosTlrSueTlpTlvSinFiltrar
        del self.aCeldasNumPuntosTlrSuePselOk
        # del self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos
        del self.aCeldasNumPuntosTlrSuePsueOk

        del self.aCeldasNumPuntosTlrSueTlpVuelta0
        del self.aCeldasNumPuntosTlrVegPselOk
        del self.aCeldasNumPuntosTlrEdiPselOk
        del self.aCeldasNumPuntosTlrTlcPotrOk
        # del self.aCeldasNumPuntosTlrTlcPselOk
        del self.aCeldasNumPuntosTlrTlcPsueOk
        # del self.aCeldasNumPuntosTlrTlcTlpOk #Se usa en self.calculaVariablesDasoLidar() y clidnv6.calculaVariablesDasoLidar()
        # del self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar
        # del self.aCeldasPuntoMinAbsTlp #Se usa en lasData.obtenerReferenciasAnularesExtremas()
        del self.aCeldasRangoBasal
        del self.aCeldasRangoCielo
        del self.aCeldasRawTime  # Si no uso Numba, se calcula y graba cada celda -> self.miCeldaRawTime
        del self.aCeldasSumaCotasTlrSueTlpVuelta0
        del self.aCeldasSumaCotasTlrTlcTlpOk  # Se usa en self.calculaVariablesDasoLidar
        # del self.aFiles
        # del self.ajusteBasalElegido #Se usa en verificarFiabilidadDelAjuste()
        # del self.ajusteCieloElegido #Se usa en verificarFiabilidadDelAjuste()
        # del self.ajusteMdbA #Es bool y no siempre lo uso
        # del self.ajusteMdbB #Es bool y no siempre lo uso
        # del self.ajusteMdcA #Es bool y no siempre lo uso
        # del self.ajusteMdcB #Es bool y no siempre lo uso

        # del self.IDselec
        del self.IDsuelo
        del self.IDalter
        # del self.ajusteMdm #Es bool y no siempre lo uso
        del self.myCeldaNumPtosTlrTlcPorPasada
        del self.myCeldaNumPtosTlrSlpPorPasada
        del self.myCeldaNumPtosTlrClaPorPasada
        del self.myCeldaNumPtosTlrSuePorPasada
        del self.myCeldaAngAcumTlrTlcPorPasada
        del self.myCeldaAngMedTlrTlcPorPasada
        del self.myCeldaMinX_TlrTlcPorPasada
        del self.myCeldaMaxX_TlrTlcPorPasada
        del self.myCeldaMinY_TlrTlcPorPasada
        del self.myCeldaMaxY_TlrTlcPorPasada
        del self.myCeldaRangoX_TlrTlcPorPasada
        del self.myCeldaRangoY_TlrTlcPorPasada
        del self.myCeldaPasadasElegibles
        del self.arrayTiposDePlanoPorCuadricula
        ##del self.CotaDefectivaRptoAcotaMedia
        ##del self.CotaExcesivaRptoAcotaMedia
        # del self.listaRangos_AlturasMasDe
        # del self.listaRangos_AlturasRango
        # del self.myLasHead
        del self.nPuntosIgnoradosPorDemasiadosEnLaPasadaTrasGuardarlosEnArray
        # del GLBNsubCeldasPorCelda
        ##del self.numPuntosConCotaDefectivaRptoAcotaMedia #Se usa en este modulo
        ##del self.numPuntosConCotaExcesivaRptoAcotaMedia #Se usa en este modulo
        del self.seleccionOk


    # ==========================================================================
    def liberaArraysTrasVuelta6(self):
        del self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos
        del self.aCeldasCotaMediaTlrTlcTlp
        # del self.aCeldasRugosidadMacroOld
        # del self.aCeldasRugosidadMesosOld
        # del self.aCeldasRugosidadMicroOld
        # del self.aCeldasUrbanas

        # El unico array iniciada en iniciaVariablesParaVuelta4{} que se usa
        # tras la vuelta4 es aMetricoPlanoTejado[]. Este array se pasa
        # a clidtrain.entrenaLas{}; su valor metrico se asigna a los puntos de su celda.
        # Esa propiedad de cada punto es la ultima del array vectorVars[].
        # vectorVars[] se guarda con otros arrays en fichero npz acumulativo con np.savez_compressed().
        # Esos ficheros acumulativos de puntos se usan para entrenamiento
        # del self.aMetricoPlanoTejado # Se usa en clidtrain.entrenaLas{}

        if (
            (
                GLO.GLBLsoloCrearTilesNoGuardarAsc
                or GLO.GLBLsoloGuardarArraysNpzSinCrearOutputFiles
            )
            and not GLO.GLBLreDepurarMiniSubCelEnVueltaAjustesMdp
            and not GLO.GLBLcrearTilesPostVuelta2
            and not GLO.GLBLguardarArraysVuelta2a9EnNpz
        ):
            GLBNprocesarVuelta2 = False
        else:
            GLBNprocesarVuelta2 = True

        if GLO.GLBLguardarArraysVuelta2a9EnNpz or (
            GLBNprocesarVuelta2 and GLO.GLBLcalcularHiperFormas
        ):
            # Estas son las arrays de la vuelta4 (todas menos aMetricoPlanoTejado)
            del self.aMetricoPlanoTejado
            del self.aSubCeldasPlanoTejado
            del self.aCeldasNumeroDePlanosTejado
            del self.aCeldasPuntosEnPlanosTejado
            del self.aMetricoRugosidadMegasInterCeldillas
            del self.aMetricoRugosidadMacroInterCeldillas
            del self.aMetricoRugosidadMesosInterCeldillas
            del self.aMetricoRugosidadMicroInterCeldillas
            del self.aCeldasRugosidadMegasInterCeldillas
            del self.aCeldasRugosidadMacroInterCeldillas
            del self.aCeldasRugosidadMesosInterCeldillas
            del self.aCeldasRugosidadMicroInterCeldillas
            del self.aSubCeldasRugosidadMegasInterCeldillas
            del self.aSubCeldasRugosidadMacroInterCeldillas
            del self.aSubCeldasRugosidadMesosInterCeldillas
            del self.aSubCeldasRugosidadMicroInterCeldillas
            del self.aSubCeldasNumPuntos


        # del self.miCeldaNumRprimPsel #Ya no es un array
        # del self.miCeldaNumRsigPsel #Ya no es un array

        if GLO.GLBLgrabarCeldasClasesSueloVegetacion:  # $$$
            # del self.aCeldasNumPrimerosRetornosSuelo # Se elimina en liberaArraysTrasVuelta01{}
            # del self.aCeldasNumTodosLosRetornosSuelo # Se elimina en liberaArraysTrasVuelta01{}
            # del self.aCeldasNumPrimerosRetornosVeget # Se elimina en liberaArraysTrasVuelta01{}
            # del self.aCeldasNumTodosLosRetornosVeget # Se elimina en liberaArraysTrasVuelta01{}
            pass
        if GLO.GLBLgrabarCeldasClasesEdificio:  # $$$
            # del self.aCeldasNumPrimerosRetornosEdificio # Se elimina en liberaArraysTrasVuelta01{}
            # del self.aCeldasNumTodosLosRetornosEdificio # Se elimina en liberaArraysTrasVuelta01{}
            pass
        if GLO.GLBLgrabarCeldasClasesOtros:  # $$$
            # del self.aCeldasNumPrimerosRetornosOtros # Se elimina en liberaArraysTrasVuelta01{}
            # del self.aCeldasNumTodosLosRetornosOtros # Se elimina en liberaArraysTrasVuelta01{}
            # del self.aCeldasNumTodosLosRetornosOverlap # Se elimina en liberaArraysTrasVuelta01{}
            pass
        # del self.aCeldasNumPuntosTlrTlcTlpOk
        del self.aCeldasCotaMinAbsTlp
        del self.aCeldasCotaMaxAbsTlp
        del self.aCeldasCotaMinAbsPse
        del self.aCeldasCotaMaxAbsPse
        if GLO.GLBLcalcularMds:
            del self.aCeldasCotaMediaTlrSueTlp
            del self.aCeldasCotaMediaTlrSuePsel
            del self.aCeldasCotaMediaTlrSuePsue
            del self.aCeldasCoeficientesMds
            '''
            if GLO.GLBLgrabarPercentilesRelativos:
                del self.aCeldasListaAltDeTodosLosRetornosConFiltroSobreMds
                del self.aCeldasListaAltDePrimerosRetornosConFiltroSobreMds
            '''
        if GLO.GLBLcalcularMdb:
            del self.aCeldasCoeficientesMdb_  # Sigue usandose
            # del self.aCeldasCotaMediaBasal #Se borra en clidflow antes de la segunda vuelta
            '''
            if GLO.GLBLgrabarPercentilesRelativos:
                del self.aCeldasListaAltDeTodosLosRetornosConFiltroSobreMdb
                del self.aCeldasListaAltDePrimerosRetornosConFiltroSobreMdb
            '''
            if GLO.GLBLproyectarPuntosSobreMdb:
                del self.miCeldaListaCotasTlrPselFiltroOpt
                del self.miCeldaListaDistAlCentroProyectadaSobreEjeMaxPteTlrPselFiltroOpt
        if GLO.GLBLcalcularMdc:
            del self.aCeldasCoeficientesMdc_
            # del self.aCeldasCotaMediaCielo #Se borra en clidflow antes de la segunda vuelta


    # ==========================================================================
    def anularSuelo(self, inputFile_las, listaArraysParaBorrar):
        global GLD
        clidaux.printMsg('ATENCION %s no tiene puntos suelo, se desactiva todo lo relacionado con los puntos clasificados suelo.\n' % inputFile_las)
        GLO.GLBLcalcularMds = False
        GLO.GLBLgrabarNumPuntosSuelo = False
        GLO.GLBLgrabarCeldasClasesSueloVegetacion = False
        GLO.GLBLgrabarCeldasClasesEdificio = False
        GLO.GLBLgrabarCeldasClasesOtros = False
        GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmds = False
        GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmds = False
        GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmds = False
        for miArray in listaArraysParaBorrar:
            del miArray


    # ==========================================================================
    def mostrarResultadoVuelta0(self, contadorPral):
        clidaux.printMsg('\n{:_^80}'.format(''))
        clidaux.printMsg(
            'cliddata.mostrarResultadoVuelta0-> Vuelta0 finalizada: se han procesado %i puntos de un total de %i'
            % (contadorPral + 1, self.myLasHead.headDict['numptrecords'])
        )
        clidaux.printMsg('cliddata-> Numero de puntos segun cabecera:                          %i puntos' % self.myLasHead.headDict['numptrecords'])
        clidaux.printMsg('cliddata-> Numero de puntos pasados a la RAM:                        %i puntos' % self.numPuntosCargadosEnLaRAM)
        clidaux.printMsg('cliddata-> Numero de puntos a leer:                                  %i puntos (nPtosAleer)' % (self.nPtosAleer))
        clidaux.printMsg('cliddata-> Numero de puntos leidos segun contadorPral:               %i puntos' % (contadorPral + 1))
        clidaux.printMsg('cliddata-> Filtro 1: las coordenadas del punto deben: (a) ser validas y (b) estar dentro del bloque con cierto margen de error')
        clidaux.printMsg('  Puntos descartados en clidnv0 antes de asignar celda (nX, nY) -Tarea asignarCelda-:')

        clidaux.printMsg(
            '    Numero de puntos con coordenadas nulas:                 %i puntos (numPuntosDescartadosPorCoordenadasNulas)'
            % self.numPuntosDescartadosPorCoordenadasNulas
        )
        clidaux.printMsg(
            '    Numero de puntos en pasadas transversales:              %i puntos (numPuntosDescartadosPorPasadaTransversal)'
            % self.numPuntosDescartadosPorPasadaTransversal
        )
        clidaux.printMsg(
            '    Numero de puntos con coord erroneas (imposibles):       %i puntos (numPuntosDescartadosPorCoordenadasErroneas)'
            % self.numPuntosDescartadosPorCoordenadasErroneas
        )
        clidaux.printMsg(
            '    Numero de puntos fuera de bloque (>%i metro(s)):         %i puntos (numPuntosDescartadosPorFueraDeBloque)'
            % (GLO.GLBLmargenParaAdmitirPuntosFueraDeBloque, self.numPuntosDescartadosPorFueraDeBloque)
        )
        clidaux.printMsg(
            '  Numero de puntos leidos validos DENTRO DEL BLOQUE:        %i puntos (numPuntosValidosDentroDelBloque)' % self.numPuntosValidosDentroDelBloque
        )
        clidaux.printMsg(
            '    numPuntosValidosDentroDelBloque (%i) = nPtosAleer (%i) [sampleLas=%i] - (numPuntosDescartadosPorPasadaTransversal (%i) + numPuntosDescartadosPorCoordenadasErroneas (%i) + numPuntosDescartadosPorFueraDeBloque (%i))'
            % (
                self.numPuntosValidosDentroDelBloque,
                self.nPtosAleer,
                self.sampleLas,
                self.numPuntosDescartadosPorPasadaTransversal,
                self.numPuntosDescartadosPorCoordenadasErroneas,
                self.numPuntosDescartadosPorFueraDeBloque,
            )
        )
        clidaux.printMsg(
            '  Despues de dar por valido un punto dentro del bloque se le asigna celda y se empieza con los siguientes filtros de clidnv0.numbaMainVuelta0()'
        )
        clidaux.printMsg(
            'cliddata-> Filtro 2: que no supere GLBLnMaxPtosCeldaTlrTlpPrevioExtremo=%i (en principio nunca) resultando: aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar y aCeldasNumPuntosTlrSueTlpTlvSinFiltrar'
            % GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo
        )
        sumaCeldasNumPuntosTlrTlcTlpTlvSinFiltrar = 0
        for nY in range(self.nCeldasY):
            for nX in range(self.nCeldasX):
                sumaCeldasNumPuntosTlrTlcTlpTlvSinFiltrar += self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY]
        # clidaux.printMsg(
        #     '    Numero ptos descartados por mas de %i en la celda:   %i puntos (numPuntosDescartadosPorCeldaConDemasiadosPuntosTotales)'
        #     % (GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo, self.numPuntosDescartadosPorCeldaConDemasiadosPuntosTotales)
        # )
        clidaux.printMsg(
            '      Normalmente numPuntosValidosDentroDelBloque (%i) es igual a sum(aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar) (%i) porque el limite total de puntos chequeados (GLBLnMaxPtosCeldaTlrTlpPrevioExtremo) es muy alto (%i)'
            % (self.numPuntosValidosDentroDelBloque, sumaCeldasNumPuntosTlrTlcTlpTlvSinFiltrar, GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo)
        )
        clidaux.printMsg(
            'cliddata-> Filtro 3: outliersProvisionales -> fuera del rango de cotas admisibles o que se distancien rpto a la media mas de GLBLLimiteDistanciaRptoCotaMedProvisionalPuntosRuidoOutliers (%i) m'
            % GLO.GLBLLimiteDistanciaRptoCotaMedProvisionalPuntosRuidoOutliers
        )
        clidaux.printMsg(
            '    Numero ptos descartados x outliers:                     %i puntos (numPuntosDescartadosPorOutlier)' % self.numPuntosDescartadosPorOutlier
        )
        clidaux.printMsg(
            'cliddata-> Filtro 4: demasiadosPuntosEnAlgunaPasada y capacidadDelArrayPredimensionado -> que no excedan el limite de puntos por pasada (GLO.GLBLnMaxPtosCeldaTlrPas=%i) ni la capacidad total del Array (incuyendo todas las pasadas: GLBLnMaxPtosCeldaArrayPredimensionadaTodos=%i)'
            % (GLO.GLBLnMaxPtosCeldaTlrPas, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos)
        )
        clidaux.printMsg(
            '    Numero ptos descartados x demasiados en pasada (>%i):  %i puntos (numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes)'
            % (GLO.GLBLnMaxPtosCeldaTlrPas, self.numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes)
        )
        clidaux.printMsg(
            '    Numero ptos descartados x excederCapacidadArray (>%i): %i puntos (numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos)'
            % (self.LCLnMaxPtosCeldaArrayPredimensionadaTodos, self.numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos)
        )
        clidaux.printMsg(
            'cliddata-> Numero de puntos leidos VALIDOS CREIBLES ALMACENABLES:    %i puntos (numPuntosValidosTotalesUsables)'
            % self.numPuntosValidosTotalesUsables
        )
        sumaCeldasNumPuntosTlrTlcTlpOk = 0
        for nY in range(self.nCeldasY):
            for nX in range(self.nCeldasX):
                sumaCeldasNumPuntosTlrTlcTlpOk += self.aCeldasNumPuntosTlrTlcTlpOk[nX, nY]
        clidaux.printMsg('  Debe coincidir con                                      %i: sum(self.aCeldasNumPuntosTlrTlcTlpOk):' % sumaCeldasNumPuntosTlrTlcTlpOk)
        clidaux.printMsg(
            '  Debe coincidir con                                      %i: self.nPtosAleer (/self.sampleLas) - (self.numPuntosDescartadosPorPasadaTransversal + self.numPuntosDescartadosPorCoordenadasErroneas + self.numPuntosDescartadosPorFueraDeBloque + self.numPuntosDescartadosPorOutlier + self.numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes + self.numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos)'
            # + self.numPuntosDescartadosPorCeldaConDemasiadosPuntosTotales
            % (
                int(self.nPtosAleer / self.sampleLas)
                - (
                    self.numPuntosDescartadosPorPasadaTransversal
                    + self.numPuntosDescartadosPorCoordenadasNulas
                    + self.numPuntosDescartadosPorCoordenadasErroneas
                    + self.numPuntosDescartadosPorFueraDeBloque
                    # + self.numPuntosDescartadosPorCeldaConDemasiadosPuntosTotales
                    + self.numPuntosDescartadosPorOutlier
                    + self.numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes
                    # + self.numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos
                )
            )
        )

        self.numPuntosNoValidosNosuables = (
            self.numPuntosDescartadosPorCoordenadasNulas
            + self.numPuntosDescartadosPorPasadaTransversal
            + self.numPuntosDescartadosPorCoordenadasErroneas
            + self.numPuntosDescartadosPorFueraDeBloque
            # + self.numPuntosDescartadosPorCeldaConDemasiadosPuntosTotales
            + self.numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes
            + self.numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos
            + self.numPuntosDescartadosPorOutlier
        )
        # if self.numPuntosNoLeidosPorInterrumpirInterpretacion > 0:
        #     clidaux.printMsg('cliddata-> Lectura interrumpida; quedan sin leer:              %i puntos' % (self.numPuntosNoLeidosPorInterrumpirInterpretacion))
        # else:
        #     if self.numPuntosValidosTotalesUsables != self.numPuntosCargadosEnLaRAM - self.numPuntosNoValidosNosuables:
        #         clidaux.printMsg(
        #             'cliddata-> ATENCION: revisar numero de puntos validos usables: %i puntos'
        #             % (self.numPuntosCargadosEnLaRAM - self.numPuntosNoValidosNosuables)
        #         )

        if GLO.GLBLalmacenarPuntosComoNumpyDtype:
            clidaux.printMsg(
                'cliddata-> Puntos guardados para procesar (todas pasadas; dtype):    %i puntos (todos en contadorAllEnArrayPral porque con Numba no puede haber ninguno en contadorAllEnArrayAux)'
                % (self.contadorAllEnArrayPral)
            )
        else:
            clidaux.printMsg('cliddata-> Puntos guardados para procesar (todas pasadas; no dtype): %i puntos (ya no uso contadorAllEnArrayAll)' % (0))
        clidaux.printMsg('{:_^80}'.format(''))


    # ==========================================================================
    # Esta funcion tarda menos de 1 segundo, no necesito pasarla a numba
    # Posiblemente reitere cosas que he hecho en la vuelta0, pero lleva poco tiempo
    def chequeaNumeroDePuntosPorCelda(self):
        self.maxNumPuntosPorCelda = 0
        self.celdasSinPuntos = 0
        self.celdasConPocosPuntosTotales = 0
        self.nCeldasConMasDeMidLimPuntos = 0
        self.nCeldasConMasDeLowLimPuntos = 0
        self.nCeldasConMasDeHigLimPuntos = 0
        # self.nCeldasConMasDeMaxLimPuntos = 0
        self.nCeldasConMasPuntosDeLosAdmitidosEnLaCelda = 0
        self.nCeldasConDemasiadosPuntosTlrTlp = 0
        self.nCeldasConDemasiadosPuntosTlrPas = 0
        LCL_lowLimit = GLO.GLBLnMaxPtosCeldaArrayPredimensionadaTodos # 1000
        LCL_higLimit = 2 * LCL_lowLimit

        if self.hayCeldasConDemasiadosPuntos:
            clidaux.printMsg('\t-> cliddata-> ATENCION: hay celdas con mas de %i puntos:' % GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo)
        for nY in range(self.nCeldasY):
            for nX in range(self.nCeldasX):
                if nX >= self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar.shape[0] or nY >= self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar.shape[1]:
                    continue
                self.maxNumPuntosPorCelda = max(self.maxNumPuntosPorCelda, self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY])
                if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] < 0:
                    # Esto no debe pasar; si pasara tendria que redimensionar aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar
                    print('cliddata-> Demasiados puntos (mas de 2**16/2 = 32768) en', nX, nY, self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY])
                    input('cliddata-> ATENCION: Redimensionar aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar')
                    quit()

                if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] < GLO.GLBLminimoDePuntosTotales:
                    self.celdasConPocosPuntosTotales += 1
                    if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] == 0:
                        self.celdasSinPuntos += 1
                        if self.celdasSinPuntos <= 5:
                            clidaux.printMsg(
                                '\tcliddata->Celda nX: %03i, nY: %03i: No tiene puntos (posible agua; puede haber mas). Coord del centro: x:%i; y:%i'
                                % (
                                    nX,
                                    nY,
                                    int(self.myLasHead.xmin + ((nX + 0.5) * GLO.GLBLmetrosCelda)),
                                    int(self.myLasHead.ymin + ((nY + 0.5) * GLO.GLBLmetrosCelda)),
                                )
                            )
                        elif self.celdasSinPuntos == 6:
                            clidaux.printMsg('\t\t\t-> Hay mas de 5 celdas sin puntos')
                    else:
                        if self.celdasConPocosPuntosTotales <= 5:
                            clidaux.printMsg(
                                '\tcliddata->Celda nX: %03i, nY: %03i: Tiene pocos puntos (puede haber mas). Coord del centro: x:%i; y:%i'
                                % (
                                    nX,
                                    nY,
                                    int(self.myLasHead.xmin + ((nX + 0.5) * GLO.GLBLmetrosCelda)),
                                    int(self.myLasHead.ymin + ((nY + 0.5) * GLO.GLBLmetrosCelda)),
                                )
                            )
                        elif self.celdasConPocosPuntosTotales == 6:
                            clidaux.printMsg('\t\t\t-> Hay mas de 5 celdas con pocos puntos')


                # En principio self.LCLnMaxPtosCeldaArrayPredimensionadaTodos es igual que GLO.GLBLnMaxPtosCeldaArrayPredimensionadaTodos
                # Pero creo que puede diferir porque puedo ampliar el limite a la vista de los percentiles de numero de puntos.
                if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] > self.LCLnMaxPtosCeldaArrayPredimensionadaTodos:
                    self.nCeldasConMasPuntosDeLosAdmitidosEnLaCelda += 1
                    # if self.nCeldasConMasPuntosDeLosAdmitidosEnLaCelda == 1:
                    #    clidaux.printMsg('\t\t-> Celda (%i %i) con %i puntos (solo se guardan %i puntos en el array; el resto no se usan en el procesado)' % (nX, nY, self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrarPlus[nX, nY], self.LCLnMaxPtosCeldaArrayPredimensionadaTodos) )

                # Limite de puntos en el array predimensionada (LCL_lowLimit)
                # y limite indicador de mala distribucion de puntos (LCL_higLimit)
                if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] > LCL_lowLimit: # 1000
                    self.nCeldasConMasDeLowLimPuntos += 1
                    if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] > LCL_higLimit: # 2000
                        self.nCeldasConMasDeHigLimPuntos += 1
                        if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] > GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo: # 10000
                            self.nCeldasConDemasiadosPuntosTlrTlp += 1
                            # if self.nCeldasConDemasiadosPuntosTlrTlp == 1:
                            #    clidaux.printMsg('\t\t-> Celda (%i %i) con %i puntos (mas de %i puntos)' % (nX, nY, self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY], GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo) )
                if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] > GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo: # 10000
                    if self.nCeldasConDemasiadosPuntosTlrTlp <= 5:
                        clidaux.printMsg(
                            '\tcliddata->Celda nX: %03i, nY: %03i: Tiene mas de %i puntos (puede haber mas). Coord del centro: x:%i; y:%i'
                            % (
                                nX,
                                nY,
                                GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo,
                                int(self.myLasHead.xmin + ((nX + 0.5) * GLO.GLBLmetrosCelda)),
                                int(self.myLasHead.ymin + ((nY + 0.5) * GLO.GLBLmetrosCelda)),
                            )
                        )
                    elif self.nCeldasConDemasiadosPuntosTlrTlp == 6:
                        clidaux.printMsg('\t\t\t-> Hay mas de 5 celdas con mas de %i puntos' % LCL_higLimit)
                elif self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] > LCL_higLimit: # 2000
                    if self.nCeldasConMasDeHigLimPuntos <= 5:
                        clidaux.printMsg(
                            '\tcliddata->Celda nX: %03i, nY: %03i: Tiene mas de %i puntos (puede haber mas). Coord del centro: x:%i; y:%i'
                            % (
                                nX,
                                nY,
                                LCL_higLimit,
                                int(self.myLasHead.xmin + ((nX + 0.5) * GLO.GLBLmetrosCelda)),
                                int(self.myLasHead.ymin + ((nY + 0.5) * GLO.GLBLmetrosCelda)),
                            )
                        )
                    elif self.nCeldasConMasDeHigLimPuntos == 6:
                        clidaux.printMsg('\t\t\t-> Hay mas de 5 celdas con mas de %i puntos' % LCL_higLimit)
                elif self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] > LCL_lowLimit: # 1000
                    if self.nCeldasConMasDeLowLimPuntos <= 5:
                        clidaux.printMsg(
                            '\tcliddata->Celda nX: %03i, nY: %03i: Tiene mas de %i puntos (puede haber mas). Coord del centro: x:%i; y:%i'
                            % (
                                nX,
                                nY,
                                LCL_lowLimit,
                                int(self.myLasHead.xmin + ((nX + 0.5) * GLO.GLBLmetrosCelda)),
                                int(self.myLasHead.ymin + ((nY + 0.5) * GLO.GLBLmetrosCelda)),
                            )
                        )
                    elif self.nCeldasConMasDeLowLimPuntos == 6:
                        clidaux.printMsg('\t\t\t-> Hay mas de 5 celdas con mas de %i puntos' % LCL_lowLimit)

                # Uso el limite de puntos en una pasada como umbral adicional para reflejar
                # la distribucion del numero de puntos (todas las pasadas) por celda.
                # Podria ahorrarmelo porque no expresa nada concreto (ya tengo mis percentiles)
                if self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY] > GLO.GLBLnMaxPtosCeldaTlrPas: # 700
                    self.nCeldasConMasDeMidLimPuntos += 1
                    # if self.nCeldasConMasDeMidLimPuntos <= 5:
                    #     clidaux.printMsg(
                    #         '\tcliddata->Celda nX: %03i, nY: %03i: Tiene mas de %i puntos (puede haber mas). Coord del centro: x:%i; y:%i'
                    #         % (
                    #             nX,
                    #             nY,
                    #             GLO.GLBLnMaxPtosCeldaTlrPas,
                    #             int(self.myLasHead.xmin + ((nX + 0.5) * GLO.GLBLmetrosCelda)),
                    #             int(self.myLasHead.ymin + ((nY + 0.5) * GLO.GLBLmetrosCelda)),
                    #         )
                    #     )
                    # elif self.nCeldasConMasDeMidLimPuntos == 6:
                    #     clidaux.printMsg('\t\t\t-> Hay mas de 5 celdas con mas de %i puntos (limite de puntos que se guardan de cada pasada: GLBLnMaxPtosCeldaTlrPas)' % GLO.GLBLnMaxPtosCeldaTlrPas)

                for reCuentaPasadas in range(self.numTotalPasadas):
                    if self.aCeldasNumPuntosTlrTlcEcpOk[nX, nY][reCuentaPasadas]['Id'] == GLO.GLBLnoData:
                        break
                    elif self.aCeldasNumPuntosTlrTlcEcpOk[nX, nY][reCuentaPasadas]['Val'] >= GLO.GLBLnMaxPtosCeldaTlrPas:
                        self.nCeldasConDemasiadosPuntosTlrPas += 1
                        break
        if GLO.GLBLverbose or True:
            if (
                self.celdasSinPuntos > 0
                or self.celdasConPocosPuntosTotales > 0
                or self.nCeldasConMasDeLowLimPuntos > 0
                or self.nCeldasConMasDeHigLimPuntos > 0
                # or self.nCeldasConMasDeMaxLimPuntos > 0
                or self.nCeldasConMasDeMidLimPuntos > 0
                or self.nCeldasConMasPuntosDeLosAdmitidosEnLaCelda > 0
                or self.nCeldasConDemasiadosPuntosTlrPas > 0
                or self.nCeldasConDemasiadosPuntosTlrTlp > 0
            ):
                clidaux.printMsg('\t-> cliddata-> Del total de %i celdas:' % (self.nCeldasX * self.nCeldasY))
            if self.celdasSinPuntos > 0:
                clidaux.printMsg('\t\t-> Hay %5i celdas sin puntos' % (self.celdasSinPuntos))
            else:
                clidaux.printMsg('\t\t-> No hay celdas sin puntos')
            if self.celdasConPocosPuntosTotales > 0:
                clidaux.printMsg('\t\t-> Hay %5i celdas con menos de %i puntos totales (GLBLminimoDePuntosTotales)' % (self.celdasConPocosPuntosTotales, GLO.GLBLminimoDePuntosTotales))
            else:
                clidaux.printMsg('\t\t-> No hay celdas con menos de %i puntos totales (GLO.GLBLminimoDePuntosTotales)' % (GLO.GLBLminimoDePuntosTotales))
            if self.nCeldasConMasDeMidLimPuntos > 0:
                clidaux.printMsg('\t\t-> Hay %5i celdas con mas de %i puntos totales (GLBLnMaxPtosCeldaTlrPas)' % (self.nCeldasConMasDeMidLimPuntos, GLO.GLBLnMaxPtosCeldaTlrPas))
            else:
                clidaux.printMsg('\t\t-> No hay celdas con mas de %i puntos totales (GLBLnMaxPtosCeldaTlrPas)' % (GLO.GLBLnMaxPtosCeldaTlrPas))
            if self.nCeldasConMasDeLowLimPuntos > 0:
                clidaux.printMsg('\t\t-> Hay %5i celdas con mas de %i puntos totales (LCL_lowLimit)' % (self.nCeldasConMasDeLowLimPuntos, LCL_lowLimit))
            else:
                clidaux.printMsg('\t\t-> No hay celdas con mas de %i puntos totales (LCL_lowLimit)' % (LCL_lowLimit))
            if self.nCeldasConMasDeHigLimPuntos > 0:
                clidaux.printMsg('\t\t-> Hay %5i celdas con mas de %i puntos totales (LCL_higLimit)' % (self.nCeldasConMasDeHigLimPuntos, LCL_higLimit))
            else:
                clidaux.printMsg('\t\t-> No hay celdas con mas de %i puntos totales (LCL_higLimit)' % (LCL_higLimit))

            if self.nCeldasConDemasiadosPuntosTlrTlp > 0:
                clidaux.printMsg(
                    '\t\tHay %5i celdas con mas de los %i puntos que se leen como max en cada celda (todas las pasadas)'
                    % (self.nCeldasConDemasiadosPuntosTlrTlp, GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo)
                )
                # clidaux.printMsg(
                #     '\t\t\t %i puntos descartados por exceder el maximo de puntos por celda'
                #     % self.numPuntosDescartadosPorCeldaConDemasiadosPuntosTotales
                # )
            else:
                clidaux.printMsg('\t\t-> No hay celdas con mas de los %i puntos que se leen como max en cada celda (todas las pasadas) (GLBLnMaxPtosCeldaTlrTlpPrevioExtremo)' % (GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo))

            if self.nCeldasConMasPuntosDeLosAdmitidosEnLaCelda > 0:
                clidaux.printMsg(
                    '\t\tHay %5i celdas con mas de los %i puntos que se guardan en el array (en cada celda; todas las pasadas)'
                    % (self.nCeldasConMasPuntosDeLosAdmitidosEnLaCelda, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos)
                )
                clidaux.printMsg(
                    '\t\t\t-> %i puntos descartados por exceder el maximo de puntos que se guardan por celda'
                    % self.numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos
                )
            else:
                clidaux.printMsg('\t\t-> No hay celdas con mas de los %i puntos que se guardan en el array (en cada celda; todas las pasadas) (LCLnMaxPtosCeldaArrayPredimensionadaTodos)' % (self.LCLnMaxPtosCeldaArrayPredimensionadaTodos))

            if self.nCeldasConDemasiadosPuntosTlrPas > 0:
                clidaux.printMsg(
                    '\t\tHay %5i celdas con mas de %i en alguna pasada - no se guardan mas en el array'
                    % (self.nCeldasConDemasiadosPuntosTlrPas, GLO.GLBLnMaxPtosCeldaTlrPas)
                )
                clidaux.printMsg(
                    '\t\t\t %i puntos descartados por exceder el maximo de puntos por pasada'
                    % self.numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes
                )
            else:
                clidaux.printMsg('\t\t-> No hay celdas con mas de %i puntos en alguna pasada (GLBLnMaxPtosCeldaTlrPas)' % (GLO.GLBLnMaxPtosCeldaTlrPas))

            clidaux.printMsg(
                '\tcliddata->Numero de puntos contabilizados en la celda de mas puntos: %i puntos (por encima de %i no se contabilizan). Solo se guardan %i puntos por celda.'
                % (self.maxNumPuntosPorCelda, GLO.GLBLnMaxPtosCeldaTlrTlpPrevioExtremo, self.LCLnMaxPtosCeldaArrayPredimensionadaTodos)
            )


    # ==========================================================================
    def leerArraysGuardadasVueltaX(self, npzFileNameArraysVueltaX, fileCoordYear='', LCLverbose=False):
        if GLO.GLBLverbose or LCLverbose:
            print('\t-> cliddata-> Leyendo npz:', npzFileNameArraysVueltaX)
        if os.path.exists(npzFileNameArraysVueltaX):
            try:
                npzArraysVueltaX = np.load(npzFileNameArraysVueltaX, allow_pickle=True)
                if GLO.GLBLverbose or LCLverbose:
                    print('\t\t-> Lista de arrays guardadas en npz:')
                for nArray in range(len(npzArraysVueltaX.files)):
                    npzArrayName = npzArraysVueltaX.files[nArray]
                    npzArrayData = npzArraysVueltaX[npzArrayName]
                    if GLO.GLBLverbose or LCLverbose:
                        if nArray < 10:
                            print('\t\t\t-> Array:', npzArrayName, type(npzArrayData), '-> ndim:', npzArrayData.ndim, '-> shape:', npzArrayData.shape, '-> dtype:', npzArrayData.dtype)
                        elif nArray == 10:
                            print('\t\t\t-> etc.')
                            print('\t\t\t-> Total:', len(npzArraysVueltaX.files))
                    if npzArrayData.shape == (): # ndim = 0
                        setattr(self, npzArrayName, npzArrayData.item())
                        if GLO.GLBLverbose or LCLverbose:
                            if nArray < 10:
                                print('\t\t\t\t-> Valor asignado:', getattr(self, npzArrayName), type(getattr(self, npzArrayName)))
                    else:
                        setattr(self, npzArrayName, npzArrayData)
            except:
                print('cliddata-> Aviso: error intentando leer {}'.format(npzFileNameArraysVueltaX))
                print('\t-> Es probable que el fichero este corrupto por producirse una interrupcion mientras se generaba')
                print('\t-> Se salta este bloque; ejecutarlo al final; se intenta borrar el npz:')
                try:
                    os.remove(npzFileNameArraysVueltaX)
                    print('\t\t-> Fichero npz borrado ok.')
                except:
                    print('\t\t-> Aviso: no se ha podido borrar el Fichero npz.')
                return False
        # print('\tclindat.&{}-> B myLasData.IDselec: {}'.format(fileCoordYear, self.IDselec))
        return True


    # ==========================================================================
    def guardarArrayPralPF99_myLasData(self, npzFileNameArrays_myLasData):
        if os.path.exists(npzFileNameArrays_myLasData):
            print('\t-> clidnat-> Antes se va a eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
            os.remove(npzFileNameArrays_myLasData)
            if os.path.exists(npzFileNameArrays_myLasData):
                print('\tNo se ha podido eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
        np.savez_compressed(
            npzFileNameArrays_myLasData,
            # clidnv0.numbaMainVuelta0{}:
            aCeldasListaDePtosTlcAll=self.aCeldasListaDePtosTlcAll,
            aCeldasListaDePtosTlcPralPF99=self.aCeldasListaDePtosTlcPralPF99,
            aListaDePtosDescartadosDeArrayPralPF99=self.aListaDePtosDescartadosDeArrayPralPF99,
            aCeldasListaDePtosSueAll=self.aCeldasListaDePtosSueAll,
            aCeldasListaDePtosSuePralPF99=self.aCeldasListaDePtosSuePralPF99,
            miHeadScale=self.miHeadScale,
            miHeadOffset=self.miHeadOffset,
        )


    # ==========================================================================
    def guardarArrayExtrVars_myLasData(self, npzFileNameArrays_myLasData):
        if os.path.exists(npzFileNameArrays_myLasData):
            print('clidnat-> Antes se va a eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
            os.remove(npzFileNameArrays_myLasData)
            if os.path.exists(npzFileNameArrays_myLasData):
                print('\tNo se ha podido eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
        np.savez_compressed(
            npzFileNameArrays_myLasData,
            # clidnv0.numbaMainVuelta0{}:
            aCeldasListaDePtosExtrVar=self.aCeldasListaDePtosExtrVar,
        )


    # ==========================================================================
    def guardarArraysCartoSinguLandTypePredicha_myLasData(self, npzFileNameArrays_myLasData):
        if os.path.exists(npzFileNameArrays_myLasData):
            print('clidnat-> Antes se va a eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
            os.remove(npzFileNameArrays_myLasData)
            if os.path.exists(npzFileNameArrays_myLasData):
                print('\tNo se ha podido eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
        np.savez_compressed(
            npzFileNameArrays_myLasData,
            # clidtrain.predecirClasificacion<>:
            okPrediccionCartoSinguA = self.okPrediccionCartoSinguA,
            aSubCeldasCartoSinguLandTypePredichaA = self.aSubCeldasCartoSinguLandTypePredichaA,
            # aMultiTilesCartoSinguLandTypePredichaA = self.aMultiTilesCartoSinguLandTypePredichaA, # No lo uso (salvo guardar asc)
            okPrediccionCartoSinguB = self.okPrediccionCartoSinguB,
            aSubCeldasCartoSinguLandTypePredichaB = self.aSubCeldasCartoSinguLandTypePredichaB,
            # aMultiTilesCartoSinguLandTypePredichaB = self.aMultiTilesCartoSinguLandTypePredichaB, # No lo uso (salvo guardar asc)
        )


    # ==========================================================================
    def guardarArraysMiniSubCel_myLasData(self, npzFileNameArrays_myLasData):
        if os.path.exists(npzFileNameArrays_myLasData):
            print('clidnat-> Antes se va a eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
            os.remove(npzFileNameArrays_myLasData)
            if os.path.exists(npzFileNameArrays_myLasData):
                print('\tNo se ha podido eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
        np.savez_compressed(
            npzFileNameArrays_myLasData,
            # clidnv0.numbaMainVuelta0<>:
            aSubCeldasPuntoMiniSubCel_Tlp=self.aSubCeldasPuntoMiniSubCel_Tlp,
            aSubCeldasPuntoMaxiSubCel_Tlp=self.aSubCeldasPuntoMaxiSubCel_Tlp,
            # clidnv1.procesaCeldasVuelta1b<>:
            aSubCeldasPuntoMiniSubCelPsel=self.aSubCeldasPuntoMiniSubCelPsel,
            aSubCeldasPuntoMaxiSubCelPsel=self.aSubCeldasPuntoMaxiSubCelPsel,
            aSubCeldasPuntoMiniSubCelPsuePsel=self.aSubCeldasPuntoMiniSubCelPsuePsel,
            aSubCeldasPuntoMaxiSubCelPsuePsel=self.aSubCeldasPuntoMaxiSubCelPsuePsel,
            # clidtrain.predecirClasificacion<>:
            okPrediccionMiniSubCel = self.okPrediccionMiniSubCel,
            aSubCeldasMiniSubCelLasClassPredicha = self.aSubCeldasMiniSubCelLasClassPredicha,
            # clidnv2y.numbaVueltaAjustesMdp<>:
            # aSubCeldasPuntoMiniSubCel_Tlp = self.aSubCeldasPuntoMiniSubCel_Tlp, # Se guarda antes
            # aSubCeldasPuntoMiniSubCelPsuePsel = self.aSubCeldasPuntoMiniSubCelPsuePsel, # Se guarda antes
            # aSubCeldasPuntoMiniSubCelPsel = self.aSubCeldasPuntoMiniSubCelPsel, # Se guarda antes
            aSubCeldasPuntoMiniSubCelValidado = self.aSubCeldasPuntoMiniSubCelValidado,
        )


    # ==========================================================================
    def guardarArraysTrasVuelta0a1_myLasData(self, npzFileNameArrays_myLasData):
        if os.path.exists(npzFileNameArrays_myLasData):
            print('clidnat-> Antes se va a eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
            os.remove(npzFileNameArrays_myLasData)
            if os.path.exists(npzFileNameArrays_myLasData):
                print('\tNo se ha podido eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
        np.savez_compressed(
            npzFileNameArrays_myLasData,
            # clidnv0.numbaMainVuelta0<>:
            arrayRangoFechasDeVuelo=self.arrayRangoFechasDeVuelo,
            minMaxRGBIrI=self.minMaxRGBIrI,
            listaPasadasBloque=self.listaPasadasBloque,
            listaPasadasCuadrante=self.listaPasadasCuadrante,
            gpsTimeMin=self.gpsTimeMin,
            gpsTimeMax=self.gpsTimeMax,
            aIDPasadasEdge=self.aIDPasadasEdge,
            orientacionPasadaEnGrados=self.orientacionPasadaEnGrados,
            contadorPtosLeidosTotales=self.contadorPtosLeidosTotales,
            nPuntosPorClase=self.nPuntosPorClase,
            numTotalPasadas=self.numTotalPasadas,
            esFicheroClasificado=self.esFicheroClasificado,
            # aCeldasListaDePtosTlcAll=self.aCeldasListaDePtosTlcAll, # Se guarda con guardarArrayPralPF99_myLasData<>
            # aCeldasListaDePtosTlcPralPF99=self.aCeldasListaDePtosTlcPralPF99, # Se guarda con guardarArrayPralPF99_myLasData<>
            # aCeldasListaDePtosSueAll=self.aCeldasListaDePtosSueAll, # Se guarda con guardarArrayPralPF99_myLasData<>
            # aCeldasListaDePtosSuePralPF99=self.aCeldasListaDePtosSuePralPF99, # Se guarda con guardarArrayPralPF99_myLasData<>
            # aCeldasListaDePtosExtrVar=self.aCeldasListaDePtosExtrVar, # Se guarda con guardarArrayExtrVars_myLasData<>

#             aSubCeldasPuntoMiniSubCel_Tlp=self.aSubCeldasPuntoMiniSubCel_Tlp,
#             aSubCeldasPuntoMaxiSubCel_Tlp=self.aSubCeldasPuntoMaxiSubCel_Tlp,
            aSubCeldasCotaMinAA=self.aSubCeldasCotaMinAA,
            aSubCeldasCotaMaxAA=self.aSubCeldasCotaMaxAA,
            aCeldasZmin=self.aCeldasZmin,
            aCeldasZmax=self.aCeldasZmax,

            contadorAllEnArrayPral=self.contadorAllEnArrayPral, # == self.numPuntosValidosTotalesUsables
            contadorSiGuardablesEnArrayDescartadosDePral=self.contadorSiGuardablesEnArrayDescartadosDePral,
            contadorNoGuardablesEnArrayDescartadosDePral=self.contadorNoGuardablesEnArrayDescartadosDePral,
            contadorSueEnArrayPral=self.contadorSueEnArrayPral,

            numPuntosTodosDentroDelBloque=self.numPuntosTodosDentroDelBloque,
            numPuntosNoExcesivosDentroDelBloque=self.numPuntosNoExcesivosDentroDelBloque,
            numPuntosValidosDentroDelBloque=self.numPuntosValidosDentroDelBloque,
            numPuntosValidosTotalesUsables=self.numPuntosValidosTotalesUsables, # == self.contadorAllEnArrayPral

            numPuntosDescartadosPorCoordenadasNulas = self.numPuntosDescartadosPorCoordenadasNulas,
            numPuntosDescartadosPorPasadaTransversal=self.numPuntosDescartadosPorPasadaTransversal,
            numPuntosDescartadosPorCoordenadasErroneas=self.numPuntosDescartadosPorCoordenadasErroneas,
            numPuntosDescartadosPorFueraDeBloque=self.numPuntosDescartadosPorFueraDeBloque,
            numPuntosDescartadosPorOutlier=self.numPuntosDescartadosPorOutlier,
            numPuntosDescartadosPorPasadaConDemasiadosPuntosUnoDeCadaN=self.numPuntosDescartadosPorPasadaConDemasiadosPuntosUnoDeCadaN,
            numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes=self.numPuntosDescartadosPorPasadaConDemasiadosPuntosRestantes,
            numPuntosDescartadosPorCeldaConNumPuntosExtremo=self.numPuntosDescartadosPorCeldaConNumPuntosExtremo,
            numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos=self.numPuntosDescartadosPorMaxPtosCeldaArrayPredimensionadaTodos,

            hayCeldasConDemasiadosPuntos=self.hayCeldasConDemasiadosPuntos,
            hayCeldasConDemasiadosPuntosEnLaPasada=self.hayCeldasConDemasiadosPuntosEnLaPasada,
            nPuntosSiParaNuevoLasSinReclasificar=self.nPuntosSiParaNuevoLasSinReclasificar,
            nPuntosNoParaNuevoLasSinReclasificar=self.nPuntosNoParaNuevoLasSinReclasificar,
            aNumReturnsTotalOkBloque=self.aNumReturnsTotalOkBloque,
            aNumReturnsByPulseOkBloque=self.aNumReturnsByPulseOkBloque,
            aNumReturnsByPulseAll=self.aNumReturnsByPulseAll,
            aNumReturnsByPulseParaNuevoLasSinReclasificar=self.aNumReturnsByPulseParaNuevoLasSinReclasificar,

            aCeldasNumPuntosTlrTlcEcpTlvSinFiltrar=self.aCeldasNumPuntosTlrTlcEcpTlvSinFiltrar,
            aCeldasNumPuntosTlrTlcEcpOk=self.aCeldasNumPuntosTlrTlcEcpOk,
            aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar=self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar,
            aCeldasNumPuntosTlrTlcTlpOk=self.aCeldasNumPuntosTlrTlcTlpOk,
            aCeldasNumPuntosTlrSueTlpTlvSinFiltrar=self.aCeldasNumPuntosTlrSueTlpTlvSinFiltrar,
            aCeldasNumPuntosTlrSueTlpVuelta0=self.aCeldasNumPuntosTlrSueTlpVuelta0,
            aCeldasSumaCotasTlrTlcTlpOk=self.aCeldasSumaCotasTlrTlcTlpOk,
            aCeldasSumaCotasTlrSueTlpVuelta0=self.aCeldasSumaCotasTlrSueTlpVuelta0,
            aCeldasNumSingleReturnTlp=self.aCeldasNumSingleReturnTlp,
            aCeldasNumMultiReturnTlp=self.aCeldasNumMultiReturnTlp,
            aCeldasNumPrimerosRetornosNoSolape=self.aCeldasNumPrimerosRetornosNoSolape,
            aCeldasNumPrimerosRetornosTlp=self.aCeldasNumPrimerosRetornosTlp,
            aCeldasNumSiguientesRetornosTlp=self.aCeldasNumSiguientesRetornosTlp,
            aCeldasNumTodosLosRetornosSuelo=self.aCeldasNumTodosLosRetornosSuelo,
            aCeldasNumPrimerosRetornosSuelo=self.aCeldasNumPrimerosRetornosSuelo,
            aCeldasNumTodosLosRetornosVeget=self.aCeldasNumTodosLosRetornosVeget,
            aCeldasNumPrimerosRetornosVeget=self.aCeldasNumPrimerosRetornosVeget,
            aCeldasNumTodosLosRetornosEdificio=self.aCeldasNumTodosLosRetornosEdificio,
            aCeldasNumPrimerosRetornosEdificio=self.aCeldasNumPrimerosRetornosEdificio,
            aCeldasNumTodosLosRetornosOverlap=self.aCeldasNumTodosLosRetornosOverlap,
            aCeldasNumTodosLosRetornosOtros=self.aCeldasNumTodosLosRetornosOtros,
            aCeldasNumPrimerosRetornosOtros=self.aCeldasNumPrimerosRetornosOtros,

            aSubCeldasNumPtosTlcTlpTlr=self.aSubCeldasNumPtosTlcTlpTlr,
            aSubCeldasNumPtosTlcTlpTr1=self.aSubCeldasNumPtosTlcTlpTr1,
            aSubCeldasProp09TodosLosRetornosSuelo=self.aSubCeldasProp09TodosLosRetornosSuelo,
            aSubCeldasProp09PrimerosRetornosSuelo=self.aSubCeldasProp09PrimerosRetornosSuelo,
            aSubCeldasProp09TodosLosRetornosVeget=self.aSubCeldasProp09TodosLosRetornosVeget,
            aSubCeldasProp09PrimerosRetornosVeget=self.aSubCeldasProp09PrimerosRetornosVeget,
            aSubCeldasProp09TodosLosRetornosEdificio=self.aSubCeldasProp09TodosLosRetornosEdificio,
            aSubCeldasProp09PrimerosRetornosEdificio=self.aSubCeldasProp09PrimerosRetornosEdificio,
            aSubCeldasProp09TodosLosRetornosOtros=self.aSubCeldasProp09TodosLosRetornosOtros,
            aSubCeldasProp09PrimerosRetornosOtros=self.aSubCeldasProp09PrimerosRetornosOtros,
            aMetricoNumPtosTlcTlpTlr=self.aMetricoNumPtosTlcTlpTlr,
            aMetricoNumPtosTlcTlpTr1=self.aMetricoNumPtosTlcTlpTr1,
            aMetricoProp09TodosLosRetornosSuelo=self.aMetricoProp09TodosLosRetornosSuelo,
            aMetricoProp09PrimerosRetornosSuelo=self.aMetricoProp09PrimerosRetornosSuelo,
            aMetricoProp09TodosLosRetornosVeget=self.aMetricoProp09TodosLosRetornosVeget,
            aMetricoProp09PrimerosRetornosVeget=self.aMetricoProp09PrimerosRetornosVeget,
            aMetricoProp09TodosLosRetornosEdificio=self.aMetricoProp09TodosLosRetornosEdificio,
            aMetricoProp09PrimerosRetornosEdificio=self.aMetricoProp09PrimerosRetornosEdificio,
            aMetricoProp09TodosLosRetornosOtros=self.aMetricoProp09TodosLosRetornosOtros,
            aMetricoProp09PrimerosRetornosOtros=self.aMetricoProp09PrimerosRetornosOtros,
            aSubCeldasIntSRetMed=self.aSubCeldasIntSRetMed,
            aSubCeldasIntMRetMed=self.aSubCeldasIntMRetMed,
            aSubCeldasEVI2Med=self.aSubCeldasEVI2Med,
            aSubCeldasNDVIMed=self.aSubCeldasNDVIMed,
            aSubCeldasNDWIMed=self.aSubCeldasNDWIMed,
            aMetricoIntSRet=self.aMetricoIntSRet,
            aMetricoEVI2Med=self.aMetricoEVI2Med,
            aMetricoNDVIMed=self.aMetricoNDVIMed,
            aMetricoNDWIMed=self.aMetricoNDWIMed,
            # clidnv0.numbaSeleccionaPasadaTrasVuelta0<>:
            seleccionOk=self.seleccionOk,
            IDselec=self.IDselec,
            IDsuelo=self.IDsuelo,
            IDalter=self.IDalter,
            aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos=self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos,
            aCeldasNumPuntosTlrSlpPselSinFiltrarSospechosos=self.aCeldasNumPuntosTlrSlpPselSinFiltrarSospechosos,
            aCeldasNumPuntosTlrClaPselSinFiltrarSospechosos=self.aCeldasNumPuntosTlrClaPselSinFiltrarSospechosos,
            aCeldasNumPuntosTlrSuePselSinFiltrarSospechosos=self.aCeldasNumPuntosTlrSuePselSinFiltrarSospechosos,
            aCeldasNumPuntosTlrSlpPsueSinFiltrarSospechosos=self.aCeldasNumPuntosTlrSlpPsueSinFiltrarSospechosos,
            aCeldasNumPuntosTlrClaPsueSinFiltrarSospechosos=self.aCeldasNumPuntosTlrClaPsueSinFiltrarSospechosos,
            aCeldasNumPuntosTlrSuePsueSinFiltrarSospechosos=self.aCeldasNumPuntosTlrSuePsueSinFiltrarSospechosos,
            aCeldasNumPasadasConPuntos=self.aCeldasNumPasadasConPuntos,
            aCeldasAngMedTlrTlcPorPasada=self.aCeldasAngMedTlrTlcPorPasada,
            nCeldasEnLasQueSeHanIgnoradoPuntosPorDemasiadosEnLaPasadaTrasGuardarlosEnArray=self.nCeldasEnLasQueSeHanIgnoradoPuntosPorDemasiadosEnLaPasadaTrasGuardarlosEnArray,
            nPuntosIgnoradosPorDemasiadosEnLaPasadaTrasGuardarlosEnArray=self.nPuntosIgnoradosPorDemasiadosEnLaPasadaTrasGuardarlosEnArray,
            aCeldasRawTime=self.aCeldasRawTime,
            aCeldasEsCeldaEdge=self.aCeldasEsCeldaEdge,
            aCeldasNumPtosPorClaseTlrTlp=self.aCeldasNumPtosPorClaseTlrTlp,
            # clidnv1.detectarAgua<>:
            aCeldasMasasDeAgua = self.aCeldasMasasDeAgua,
            # clidnv1.procesaCeldasVuelta1a<>:
            nPtosSospechosos=self.nPtosSospechosos,
            numPuntosConCotaDefectivaRptoAcotaMedia=self.numPuntosConCotaDefectivaRptoAcotaMedia,
            CotaDefectivaRptoAcotaMedia=self.CotaDefectivaRptoAcotaMedia,
            numPuntosConCotaExcesivaRptoAcotaMedia=self.numPuntosConCotaExcesivaRptoAcotaMedia,
            CotaExcesivaRptoAcotaMedia=self.CotaExcesivaRptoAcotaMedia,
            nCeldasConCotaSueloSuperiorAMedia=self.nCeldasConCotaSueloSuperiorAMedia,
            aCeldasNumPuntosTlrTlcPselOk=self.aCeldasNumPuntosTlrTlcPselOk,
            aCeldasNumPuntosTlrTlcPsueOk=self.aCeldasNumPuntosTlrTlcPsueOk,
            aCeldasNumPuntosTlrSuePselOk=self.aCeldasNumPuntosTlrSuePselOk,
            aCeldasNumPuntosTlrSuePsueOk=self.aCeldasNumPuntosTlrSuePsueOk,
            aCeldasNumPuntosTlrVegPselOk=self.aCeldasNumPuntosTlrVegPselOk,
            aCeldasNumPuntosTlrEdiPselOk=self.aCeldasNumPuntosTlrEdiPselOk,
            aCeldasNumPuntosRpriTlcPselOk=self.aCeldasNumPuntosRpriTlcPselOk,
            aCeldasNumPuntosRsigTlcPselOk=self.aCeldasNumPuntosRsigTlcPselOk,
            aCeldasCotaMediaTlrTlcTlp=self.aCeldasCotaMediaTlrTlcTlp,
            aCeldasCotaMediaTlrSueTlp=self.aCeldasCotaMediaTlrSueTlp,
            aCeldasCotaMediaTlrTlcPsel=self.aCeldasCotaMediaTlrTlcPsel,
            aCeldasCotaMediaTlrTlcPotr=self.aCeldasCotaMediaTlrTlcPotr,
            aCeldasCotaMediaTlrSuePsel=self.aCeldasCotaMediaTlrSuePsel,
            aCeldasCotaMediaTlrSuePsue=self.aCeldasCotaMediaTlrSuePsue,
            aCeldasCotaMediaTlrVegPsel=self.aCeldasCotaMediaTlrVegPsel,
            aCeldasCotaMediaTlrEdiPsel=self.aCeldasCotaMediaTlrEdiPsel,
            aCeldasPuntoMinAbsTlp=self.aCeldasPuntoMinAbsTlp,
            aCeldasCotaMinAbsTlp=self.aCeldasCotaMinAbsTlp,
            aCeldasCotaMaxAbsTlp=self.aCeldasCotaMaxAbsTlp,
            aCeldasPuntoMinAbsPse=self.aCeldasPuntoMinAbsPse,
            aCeldasCotaMinAbsPse=self.aCeldasCotaMinAbsPse,
            aCeldasCotaMaxAbsPse=self.aCeldasCotaMaxAbsPse,
            # clidnv1.procesaCeldasVuelta1b<>:
#             aSubCeldasPuntoMiniSubCelPsel=self.aSubCeldasPuntoMiniSubCelPsel,
#             aSubCeldasPuntoMaxiSubCelPsel=self.aSubCeldasPuntoMaxiSubCelPsel,
#             aSubCeldasPuntoMiniSubCelPsuePsel=self.aSubCeldasPuntoMiniSubCelPsuePsel,
#             aSubCeldasPuntoMaxiSubCelPsuePsel=self.aSubCeldasPuntoMaxiSubCelPsuePsel,
            # clidnv1.procesaCeldasVuelta1b<> post:
            nPuntosTotalPsel = self.nPuntosTotalPsel,
            # aSubCeldasCotaMinAA=self.aSubCeldasCotaMinAA,
            # aSubCeldasCotaMaxAA=self.aSubCeldasCotaMaxAA,
            aSubCeldasMdgAjuste=self.aSubCeldasMdgAjuste,
            # aCeldasListaDePtosExtrVar=self.aCeldasListaDePtosExtrVar, # Se guarda con guardarArrayExtrVars_myLasData<>
            # clidtrain.predecirClasificacion<>:
#             okPrediccionMiniSubCel = self.okPrediccionMiniSubCel,
#             aSubCeldasMiniSubCelLasClassPredicha = self.aSubCeldasMiniSubCelLasClassPredicha,
            # aMultiTilesMiniSubCelLasClassPredicha = self.aMultiTilesMiniSubCelLasClassPredicha, # No lo uso (salvo guardar asc)
            # clidtrain.guardarPrediccionMiniSubCel<>:
            # aSubCeldasPuntoMiniSubCel_Tlp = self.aSubCeldasPuntoMiniSubCel_Tlp, # Ya esta mas arriba
            # aSubCeldasPuntoMiniSubCelPsel = self.aSubCeldasPuntoMiniSubCelPsel, # Ya esta mas arriba
            # aSubCeldasPuntoMiniSubCelPsuePsel = self.aSubCeldasPuntoMiniSubCelPsuePsel, # Ya esta mas arriba
            # clidtrain.transferirInfoDeMiniSubCelCircundantesAlArrayPral<>:
            # aCeldasListaDePtosTlcPralPF99 = self.aCeldasListaDePtosTlcPralPF99, # Se guarda con guardarArrayPralPF99_myLasData<>
            # aCeldasListaDePtosExtrVar = self.aCeldasListaDePtosExtrVar, # Se guarda con guardarArrayExtrVars_myLasData<>
#             # clidtrain.predecirClasificacion<>:
#             okPrediccionCartoSinguA = self.okPrediccionCartoSinguA,
#             aSubCeldasCartoSinguLandTypePredichaA = self.aSubCeldasCartoSinguLandTypePredichaA,
#             # aMultiTilesCartoSinguLandTypePredichaA = self.aMultiTilesCartoSinguLandTypePredichaA, # No lo uso (salvo guardar asc)
#             okPrediccionCartoSinguB = self.okPrediccionCartoSinguB,
#             aSubCeldasCartoSinguLandTypePredichaB = self.aSubCeldasCartoSinguLandTypePredichaB,
#             # aMultiTilesCartoSinguLandTypePredichaB = self.aMultiTilesCartoSinguLandTypePredichaB, # No lo uso (salvo guardar asc)
            # clidtrain.transferirUsoSingCartoSinguPredichaAlArrayPral<>:
            # aCeldasListaDePtosTlcPralPF99 = self.aCeldasListaDePtosTlcPralPF99, # Se guarda con guardarArrayPralPF99_myLasData<>
            # aCeldasListaDePtosExtrVar = self.aCeldasListaDePtosExtrVar, # Se guarda con guardarArrayExtrVars_myLasData<>
        )
        '''
        # Arrays que se crean en iniciaVariablesParaVuelta0<> pero son de 
        # uso interno en clidnv0.py y no se devuelven a clidflow.py
        aSubCeldasIntSRetNum=self.aSubCeldasIntSRetNum,
        aSubCeldasIntMRetNum=self.aSubCeldasIntMRetNum,
        aSubCeldasEVI2Num=self.aSubCeldasEVI2Num,
        aSubCeldasNDVINum=self.aSubCeldasNDVINum,
        aSubCeldasNDWINum=self.aSubCeldasNDWINum,
        '''

    # ==========================================================================
    def guardarArraysTrasVuelta2a9_myLasData(self, npzFileNameArrays_myLasData):
        if os.path.exists(npzFileNameArrays_myLasData):
            print('clidnat-> Antes se va a eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
            os.remove(npzFileNameArrays_myLasData)
            if os.path.exists(npzFileNameArrays_myLasData):
                print('\tNo se ha podido eliminar el fichero npz existente: {}'.format(npzFileNameArrays_myLasData))
        np.savez_compressed(
            npzFileNameArrays_myLasData,
            # clidnv2s.numbaVueltaAjustesMdg<>:
            ejecutadaVuelta2Mdg = self.ejecutadaVuelta2Mdg,
            aCeldasCoeficientesMdg = self.aCeldasCoeficientesMdg,
            nCeldasConMatrizSingular = self.nCeldasConMatrizSingular,
            # clidnv2y.numbaVueltaAjustesMds<>:
            ejecutadaVuelta2Mds = self.ejecutadaVuelta2Mds,
            aCeldasCoeficientesMds = self.aCeldasCoeficientesMds,
            aCeldasAjustableMds = self.aCeldasAjustableMds,
            # nCeldasConMatrizSingular = self.nCeldasConMatrizSingular, # -> Ya esta en la lista
            # clidnv2y.numbaVueltaAjustesMdx<>:
            ejecutadaVuelta2Mdb = self.ejecutadaVuelta2Mdb,
            aCeldasAjustable = self.aCeldasAjustable,
            aCeldasCoeficientesMdxAll = self.aCeldasCoeficientesMdxAll, # -> No se usa despues de guardarlo en asc, (pero si para guardarlo en asc)
            aCeldasCoeficientesMdb_ = self.aCeldasCoeficientesMdb_,
            # aCeldasCoeficientesMdbSC = self.aCeldasCoeficientesMdbSC,
            # aCeldasCoeficientesMdbCC = self.aCeldasCoeficientesMdbCC,
            aSubCeldasMdb = self.aSubCeldasMdb, # Creado en 2021/06, se usa para guardarlo en asc con guardarAjustesMdxPreInterpol<> y para validar puntos no suelo en clidtrain.leerPuntosParaDepurarManualmentePostInferencia<>

            # Estas array las creo en 2021/07, con la cota de los puntos suelo, road, rail o agua
            #  No las uso despues y las guardo en fichero dentro del mismo if
            #  Pero las guardo en ArraysTrasVuelta2a9 por si las usara en el futuro 
            aCeldasApices = self.aCeldasApices, # La guardo con cliddata.guardarApices<>
            aSubCeldasMdkCotaMed = self.aSubCeldasMdkCotaMed, # La guardo con cliddata.guardarMdkSubCeldaPreInterpol<>
            aSubCeldasMdkCotaMin = self.aSubCeldasMdkCotaMin, # La guardo con cliddata.guardarMdkSubCeldaPreInterpol<>
            # aSubCeldasMdkNumPtos = self.aSubCeldasMdkNumPtos,
            aSubCeldasMdcCotaMax = self.aSubCeldasMdcCotaMax, # La guardo con cliddata.guardarMdcSubCelda<>
            # aSubCeldasMdcNumPtos = self.aSubCeldasMdcNumPtos,
            aSubCeldasMdkCotaItp = self.aSubCeldasMdkCotaItp, # La guardo con cliddata.guardarMdkSubCeldaPosInterpol<>
            ejecutadaVuelta2Mdk = self.ejecutadaVuelta2Mdk,

            ajusteBasalElegido = self.ajusteBasalElegido,
            aCeldasCoeficientesMdc_ = self.aCeldasCoeficientesMdc_,
            ajusteCieloElegido = self.ajusteCieloElegido,
            aCeldasCoeficientesMdm = self.aCeldasCoeficientesMdm,
            aCeldasCoeficientesMdxRing = self.aCeldasCoeficientesMdxRing,
            # aCeldasCotaMediaBasal = self.aCeldasCotaMediaBasal, # -> No se usa desppues de guardarlo en asc
            # aCeldasRangoBasal = self.aCeldasRangoBasal, # -> No se usa desppues de guardarlo en asc
            # aCeldasCotaMediaCielo = self.aCeldasCotaMediaCielo, # -> No se usa desppues de guardarlo en asc
            # aCeldasRangoCielo = self.aCeldasRangoCielo, # -> No se usa desppues de guardarlo en asc
            # aCeldasCotaMediaMajor = self.aCeldasCotaMediaMajor, # -> No se usa desppues de guardarlo en asc
            #aCeldasNumPuntosAjusteMajor = self.aCeldasNumPuntosAjusteMajor, # -> No se usa desppues de guardarlo en asc
            # aCeldasCotaMediaMdx = self.aCeldasCotaMediaMdx, # -> No se usa desppues de guardarlo en asc
            # clidnv2y.numbaVueltaAjustesMdp<>:
            ejecutadaVuelta2Mdp = self.ejecutadaVuelta2Mdp,
            aSubCeldasMdfCotaManual = self.aSubCeldasMdfCotaManual,
            aSubCeldasMdfCotaConvol = self.aSubCeldasMdfCotaConvol,
            aSubCeldasMdfCotaConual = self.aSubCeldasMdfCotaConual,
            aSubCeldasMdfCotaTransitoriaManual = self.aSubCeldasMdfCotaTransitoriaManual,
            aSubCeldasMdfCotaTransitoriaConvol = self.aSubCeldasMdfCotaTransitoriaConvol,
            aSubCeldasMdfCotaTransitoriaConual = self.aSubCeldasMdfCotaTransitoriaConual,
            aSubCeldasMdpCotaMacroManual = self.aSubCeldasMdpCotaMacroManual,
            aSubCeldasMdpCotaMicroManual = self.aSubCeldasMdpCotaMicroManual,
            aSubCeldasMdpCotaMacroConual = self.aSubCeldasMdpCotaMacroConual,
            aSubCeldasMdpCotaMicroConual = self.aSubCeldasMdpCotaMicroConual,
            aSubCeldasMdpTipoCotaMacroManual = self.aSubCeldasMdpTipoCotaMacroManual,
            aSubCeldasMdpTipoCotaMicroManual = self.aSubCeldasMdpTipoCotaMicroManual,
            aSubCeldasMdpTipoCotaMacroConual = self.aSubCeldasMdpTipoCotaMacroConual,
            aSubCeldasMdpTipoCotaMicroConual = self.aSubCeldasMdpTipoCotaMicroConual,
            aMultiCeldasTipoCotaAB = self.aMultiCeldasTipoCotaAB,
            aMultiCeldasEstruct = self.aMultiCeldasEstruct,
            aCeldasMdpNumPtosMiniMacro = self.aCeldasMdpNumPtosMiniMacro,
            aCeldasMdpNumPtosMiniMicro = self.aCeldasMdpNumPtosMiniMicro,
            aSubCeldasCotaMiniMacroEsOk = self.aSubCeldasCotaMiniMacroEsOk,
            aSubCeldasCotaMiniMicroEsOk = self.aSubCeldasCotaMiniMicroEsOk,
            aCeldasMdpAjuste = self.aCeldasMdpAjuste,
            aCeldasMdrCoeficientes = self.aCeldasMdrCoeficientes,
            aSubCeldasMdrCotaInterpolada = self.aSubCeldasMdrCotaInterpolada,
            aSubCeldasLateralidadMinMaxMacro = self.aSubCeldasLateralidadMinMaxMacro,
            aSubCeldasLateralidadMinMaxMesos = self.aSubCeldasLateralidadMinMaxMesos,
            aSubCeldasLateralidadMinMaxMicro = self.aSubCeldasLateralidadMinMaxMicro,
            aSubCeldasLateralidadMinMinMacro = self.aSubCeldasLateralidadMinMinMacro,
            aSubCeldasLateralidadMinMinMesos = self.aSubCeldasLateralidadMinMinMesos,
            aSubCeldasLateralidadMinMinMicro = self.aSubCeldasLateralidadMinMinMicro,
            aSubCeldasRugosidadMinMaxMacroInterSubCeldas = self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas,
            aSubCeldasRugosidadMinMaxMesosInterSubCeldas = self.aSubCeldasRugosidadMinMaxMesosInterSubCeldas,
            aSubCeldasRugosidadMinMaxMicroInterSubCeldas = self.aSubCeldasRugosidadMinMaxMicroInterSubCeldas,
            aMultiCeldasRugosidadMacroInterSubCeldas = self.aMultiCeldasRugosidadMacroInterSubCeldas,
            aMultiCeldasRugosidadMesosInterSubCeldas = self.aMultiCeldasRugosidadMesosInterSubCeldas,
            aMultiCeldasRugosidadMicroInterSubCeldas = self.aMultiCeldasRugosidadMicroInterSubCeldas,
#             aSubCeldasPuntoMiniSubCel_Tlp = self.aSubCeldasPuntoMiniSubCel_Tlp,
#             aSubCeldasPuntoMiniSubCelPsuePsel = self.aSubCeldasPuntoMiniSubCelPsuePsel,
#             aSubCeldasPuntoMiniSubCelPsel = self.aSubCeldasPuntoMiniSubCelPsel,
#             aSubCeldasPuntoMiniSubCelValidado = self.aSubCeldasPuntoMiniSubCelValidado,
            # clidnv2y.asignaCotaSobreMdfParaListaDePtosTlcPralPF99<>:
            # aCeldasListaDePtosTlcPralPF99 = self.aCeldasListaDePtosTlcPralPF99,  # Se guarda con guardarArrayPralPF99_myLasData<>
            # clidnv3.controlarCalidadTopografica<>:
            ejecutadaVuelta3CalidadTopografica = self.ejecutadaVuelta3CalidadTopografica,
            aCeldasGrano = self.aCeldasGrano,
            aCeldasNumDisrupciones = self.aCeldasNumDisrupciones,
            # clidnv3.controlarCalidadDelAjuste<>:
            ejecutadaVuelta3DelAjuste = self.ejecutadaVuelta3DelAjuste,
            aCeldasConAjusteNoFiable = self.aCeldasConAjusteNoFiable,
            # clidnv4.procesaCeldasVuelta4<>:
            ejecutadaVuelta4 = self.ejecutadaVuelta4,
            nContadorPuntosTodos = self.nContadorPuntosTodos,
            nPlanosEnElBloque = self.nPlanosEnElBloque,
            aCeldasRugosidadMegasInterCeldillas = self.aCeldasRugosidadMegasInterCeldillas,
            aCeldasRugosidadMacroInterCeldillas = self.aCeldasRugosidadMacroInterCeldillas,
            aCeldasRugosidadMesosInterCeldillas = self.aCeldasRugosidadMesosInterCeldillas,
            aCeldasRugosidadMicroInterCeldillas = self.aCeldasRugosidadMicroInterCeldillas,
            aCeldasNumeroDePlanosTejado = self.aCeldasNumeroDePlanosTejado,
            aCeldasPuntosEnPlanosTejado = self.aCeldasPuntosEnPlanosTejado,
            aSubCeldasRugosidadMegasInterCeldillas = self.aSubCeldasRugosidadMegasInterCeldillas,
            aSubCeldasRugosidadMacroInterCeldillas = self.aSubCeldasRugosidadMacroInterCeldillas,
            aSubCeldasRugosidadMesosInterCeldillas = self.aSubCeldasRugosidadMesosInterCeldillas,
            aSubCeldasRugosidadMicroInterCeldillas = self.aSubCeldasRugosidadMicroInterCeldillas,
            aSubCeldasPlanoTejado = self.aSubCeldasPlanoTejado,
            aMetricoRugosidadMegasInterCeldillas = self.aMetricoRugosidadMegasInterCeldillas,
            aMetricoRugosidadMacroInterCeldillas = self.aMetricoRugosidadMacroInterCeldillas,
            aMetricoRugosidadMesosInterCeldillas = self.aMetricoRugosidadMesosInterCeldillas,
            aMetricoRugosidadMicroInterCeldillas = self.aMetricoRugosidadMicroInterCeldillas,
            aMetricoPlanoTejado = self.aMetricoPlanoTejado,
            aNumPuntosEnPlanosPorLotesParaExportarConResiduos = self.aNumPuntosEnPlanosPorLotesParaExportarConResiduos,
            aSubCeldasNumPuntos = self.aSubCeldasNumPuntos,
            # clidnv5.interpolarPlanos<>:
            ejecutadaVuelta5 = self.ejecutadaVuelta5,
            aCeldaInterpolada = self.aCeldaInterpolada,
            # clidnv3.controlarCalidadTopografica
            # aCeldasGrano = self.aCeldasGrano, # -> Ya esta en la lista
            # aCeldasNumDisrupciones = self.aCeldasNumDisrupciones, # -> Ya esta en la lista
            # clidnv6.calculaVariablesDasoLidar
            ejecutadaVuelta6 = self.ejecutadaVuelta6,
            aCeldasCotaMin10 = self.aCeldasCotaMin10,
            aCeldasCotaMax95 = self.aCeldasCotaMax95,
            aCeldasAlt95SobreMds = self.aCeldasAlt95SobreMds,
            aCeldasAltXxSobreMds = self.aCeldasAltXxSobreMds,
            aCeldasAlt95SobreMdb = self.aCeldasAlt95SobreMdb,
            aCeldasAltXxSobreMdb = self.aCeldasAltXxSobreMdb,
            aCeldasAlt95SobreMdf = self.aCeldasAlt95SobreMdf,
            aCeldasAltXxSobreMdf = self.aCeldasAltXxSobreMdf,
            aCeldasNumPrimerosRetornosAltSuperiorRptoAmds = self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds,
            aCeldasNumTodosLosRetornosAltRangoRptoAmds = self.aCeldasNumTodosLosRetornosAltRangoRptoAmds,
            aCeldasNumPrimerosRetornosAltRangoRptoAmds = self.aCeldasNumPrimerosRetornosAltRangoRptoAmds,
            aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb = self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb,
            aCeldasNumTodosLosRetornosAltRangoRptoAmdb = self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb,
            aCeldasNumPrimerosRetornosAltRangoRptoAmdb = self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb,
            aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf = self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf,
            aCeldasNumTodosLosRetornosAltRangoRptoAmdf = self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf,
            aCeldasNumPrimerosRetornosAltRangoRptoAmdf = self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf,
            aSubCeldasAlt95SobreMdf = self.aSubCeldasAlt95SobreMdf,
            aSubCeldasAltMaxSobreMdf = self.aSubCeldasAltMaxSobreMdf,
            aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk = self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk,
            aCeldasNumTodosLosRetornosAltRangoRptoAmdk = self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk,
            aCeldasNumPrimerosRetornosAltRangoRptoAmdk = self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk,
            aCeldasNumTodosLosRetornosAltPctjRptoAmdb = self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb,
            aCeldasNumTodosLosRetornosAltPctjRptoAmdk = self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk,
            aSubCeldasAlt95SobreMdk = self.aSubCeldasAlt95SobreMdk,
            aSubCeldasAltMaxSobreMdk = self.aSubCeldasAltMaxSobreMdk,
            # clidtrain.entrenaLas<>:
            # aCeldasListaDePtosTlcPralPF99 = self.aCeldasListaDePtosTlcPralPF99, # Se guarda con guardarArrayPralPF99_myLasData<>
#             aCeldasListaDePtosExtrVar = self.aCeldasListaDePtosExtrVar, # -> Ya no lo actualizo con entrenaLas<>
        )

    
    # ==========================================================================
    def guardarMiscelaneaVuelta1(self):
#         myClassArray = getattr(self, 'aCeldasCotaMediaTlrTlcPsel', None)
#         if callable(myClassArray):
#             print('clidnat-> aCeldasCotaMediaTlrTlcPsel es callable')
#         elif myClassArray is None:
#             print('clidnat-> aCeldasCotaMediaTlrTlcPsel es None')
#         elif isinstance(myClassArray, np.ndarray):
#             print('clidnat-> aCeldasCotaMediaTlrTlcPsel es np.ndarray')
#         else:
#             print('clidnat-> aCeldasCotaMediaTlrTlcPsel es...', type(myClassArray))

        self.nCeldasConDemasiadosPuntosTlrPas = 0
        myClassArray1 = getattr(self, 'aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos', None)
        myClassArray2 = getattr(self, 'aCeldasCotaMediaTlrTlcPsel', None)
        myClassArray3 = getattr(self, 'aCeldasCotaMediaTlrTlcPotr', None)
        # ======================================================================
        for nY in reversed(range(self.nCeldasY)):
            for nX in range(self.nCeldasX):
                if not myClassArray1 is None and isinstance(myClassArray1, np.ndarray) and (
                    nX >= self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos.shape[0]
                    or nY >= self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos.shape[1]
                ):
                    continue
                if GLO.GLBLgrabarCotasDiferenciaEntrePasadas:
                    if not myClassArray2 is None and isinstance(myClassArray2, np.ndarray) and (
                        nX >= self.aCeldasCotaMediaTlrTlcPsel.shape[0]
                        or nY >= self.aCeldasCotaMediaTlrTlcPsel.shape[1]
                    ):
                        continue
                    if not myClassArray3 is None and isinstance(myClassArray3, np.ndarray) and (
                        nX >= self.aCeldasCotaMediaTlrTlcPotr.shape[0]
                        or nY >= self.aCeldasCotaMediaTlrTlcPotr.shape[1]
                    ):
                        continue

                if GLO.GLBLgrabarPrimerosVsSegundosRetornos:
                    if not self.aFiles['SingleReturnTodasLasPasadas'] is None and self.aCeldasNumSingleReturnTlp.shape[0] > 1:
                        self.aFiles['SingleReturnTodasLasPasadas'].write(str(self.aCeldasNumSingleReturnTlp[nX, nY]) + ' ')
                    if not self.aFiles['MultiReturnTodasLasPasadas'] is None and self.aCeldasNumMultiReturnTlp.shape[0] > 1:
                        self.aFiles['MultiReturnTodasLasPasadas'].write(str(self.aCeldasNumMultiReturnTlp[nX, nY]) + ' ')
                    if not self.aFiles['RetornosPrimerosTodasLasPasadas'] is None and self.aCeldasNumPrimerosRetornosTlp.shape[0] > 1:
                        self.aFiles['RetornosPrimerosTodasLasPasadas'].write(str(self.aCeldasNumPrimerosRetornosTlp[nX, nY]) + ' ')
                    if not self.aFiles['RetornosSiguientesTodasLasPasadas'] is None and self.aCeldasNumSiguientesRetornosTlp.shape[0] > 1:
                        self.aFiles['RetornosSiguientesTodasLasPasadas'].write(str(self.aCeldasNumSiguientesRetornosTlp[nX, nY]) + ' ')
                    if not self.aFiles['RetornosPrimerosPasadaSel'] is None and self.aCeldasNumPuntosRpriTlcPselOk.shape[0] > 1:
                        self.aFiles['RetornosPrimerosPasadaSel'].write(str(self.aCeldasNumPuntosRpriTlcPselOk[nX, nY]) + ' ')
                    if not self.aFiles['RetornosSiguientesPasadaSel'] is None and self.aCeldasNumPuntosRsigTlcPselOk.shape[0] > 1:
                        self.aFiles['RetornosSiguientesPasadaSel'].write(str(self.aCeldasNumPuntosRsigTlcPselOk[nX, nY]) + ' ')

                # Angulo medio de la pasada seleccionada
                if GLO.GLBLgrabarAngulos:
                    # print('aCeldasAngMedTlrTlcPorPasada:', self.aCeldasAngMedTlrTlcPorPasada, type(self.aCeldasAngMedTlrTlcPorPasada))
                    # print('self.aCeldasAngMedTlrTlcPorPasada.shape:', self.aCeldasAngMedTlrTlcPorPasada.shape)
                    if not self.aFiles['Ang'] is None and self.aCeldasAngMedTlrTlcPorPasada.shape[0] > 1:
                        miCeldaAnguloMedio = int(clidnv0.leerEscalarEnNdarrayId(self.aCeldasAngMedTlrTlcPorPasada[nX, nY], self.IDselec[nX, nY]))
                        self.aFiles['Ang'].write('%02i ' % miCeldaAnguloMedio)
                    # for reCuentaPasadas in range(self.numTotalPasadas):
                    #    ID_nPtos = self.aCeldasNumPuntosTlrTlcEcpOk[nX, nY][reCuentaPasadas]
                    #    if ID_nPtos['Id'] == self.IDselec[nX, nY]:
                    #        nPasadaSel = reCuentaPasadas
                    #        break
                    #    elif ID_nPtos['Id'] == GLO.GLBLnoData:
                    #        print('ATENCION: Error al buscar la pasada seleccionada en la celda', nX, nY, 'Pasada', self.IDselec[nX, nY])
                    #        nPasadaSel = 0
                    #        break
                    # miCeldaAnguloMedioBis = self.aCeldasAngMedTlrTlcPorPasada[nX, nY, nPasadaSel][1]
                    # if miCeldaAnguloMedio != miCeldaAnguloMedioBis:
                    #    print('miCeldaAnguloMedio != miCeldaAnguloMedioBis', miCeldaAnguloMedio, miCeldaAnguloMedioBis)

                # Cotas medias
                if GLO.GLBLgrabarCotasDiferenciaEntrePasadas:
                    if (
                        not self.aFiles['zMediaPtsTodosDiferenciaEntrePasadas'] is None
                        and self.aCeldasCotaMediaTlrTlcPsel.shape[0] > 1
                        and self.aCeldasCotaMediaTlrTlcPotr.shape[0] > 1
                    ):
                        if self.aCeldasCotaMediaTlrTlcPsel[nX, nY] != GLO.GLBLnoData and self.aCeldasCotaMediaTlrTlcPotr[nX, nY] != GLO.GLBLnoData:
                            self.aFiles['zMediaPtsTodosDiferenciaEntrePasadas'].write(
                                '%05.02f ' % (self.aCeldasCotaMediaTlrTlcPsel[nX, nY] - self.aCeldasCotaMediaTlrTlcPotr[nX, nY])
                            )
                        else:
                            self.aFiles['zMediaPtsTodosDiferenciaEntrePasadas'].write(str(GLO.GLBLnoData) + ' ')
                            if GLO.GLBLgrabarCotasDiferenciaEntrePasadas:
                                mostrarCelda = clidnaux.celdaDeControl(nX, nY)
                                if mostrarCelda:
                                    print('cliddata-> ATENCION: Analizar si no se guarda la diferencia de cota entre pasadas simplemente porque en esta celda no hay dos pasadas.')
                                    print('\t-> GLBLgrabarCotasDiferenciaEntrePasadas:', GLO.GLBLgrabarCotasDiferenciaEntrePasadas)
                                    print('\t-> aFiles:', self.aFiles['zMediaPtsTodosDiferenciaEntrePasadas'])
                                    print('\t-> aCeldasCotaMediaTlrTlcPsel.shape[0]:', self.aCeldasCotaMediaTlrTlcPsel.shape[0])
                                    print('\t-> aCeldasCotaMediaTlrTlcPotr.shape[0]:', self.aCeldasCotaMediaTlrTlcPotr.shape[0])
                                    print('\t->', nX, nY, 'self.aCeldasCotaMediaTlrTlcPotr[nX, nY]:', self.aCeldasCotaMediaTlrTlcPotr[nX, nY], 'self.aCeldasCotaMediaTlrTlcPsel[nX, nY]:', self.aCeldasCotaMediaTlrTlcPsel[nX, nY])

                if GLO.GLBLgrabarCotasMediasPorClase:
                    if not self.aFiles['zMediaPtsVegetPsel'] is None and self.aCeldasCotaMediaTlrVegPsel.shape[0] > 1:
                        self.aFiles['zMediaPtsVegetPsel'].write('%07.02f ' % self.aCeldasCotaMediaTlrVegPsel[nX, nY])
                    if not self.aFiles['zMediaPtsEdifiPsel'] is None and self.aCeldasCotaMediaTlrEdiPsel.shape[0] > 1:
                        self.aFiles['zMediaPtsEdifiPsel'].write('%07.02f ' % self.aCeldasCotaMediaTlrEdiPsel[nX, nY])
                    if GLO.GLBLcalcularMds:
                        if not self.aFiles['zMediaPtsSueloPsel'] is None and self.aCeldasCotaMediaTlrSuePsel.shape[0] > 1:
                            self.aFiles['zMediaPtsSueloPsel'].write('%07.02f ' % self.aCeldasCotaMediaTlrSuePsel[nX, nY])
                        if not self.aFiles['zMediaPtsSueloPsue'] is None and self.aCeldasCotaMediaTlrSuePsue.shape[0] > 1:
                            self.aFiles['zMediaPtsSueloPsue'].write('%07.02f ' % self.aCeldasCotaMediaTlrSuePsue[nX, nY])

                # Cotas max y min absolutas
                if GLO.GLBLgrabarCotaMinMaxCelda:
                    if not self.aFiles['CeldasCotaMinAbsTlp'] is None and self.aCeldasCotaMinAbsTlp.shape[0] > 1:
                        self.aFiles['CeldasCotaMinAbsTlp'].write('%07.02f ' % round(self.aCeldasCotaMinAbsTlp[nX, nY], 2))
                    if not self.aFiles['CeldasCotaMaxAbsTlp'] is None and self.aCeldasCotaMaxAbsTlp.shape[0] > 1:
                        self.aFiles['CeldasCotaMaxAbsTlp'].write('%07.02f ' % round(self.aCeldasCotaMaxAbsTlp[nX, nY], 2))

                # Esto estaba en la vuelta 6 y pasa a la vuela 1, pero calculado como resta de arrays
                if GLO.GLBLgrabarAlturasRptoAzMin:
                    # ClasesAltura/
                    # listaFilesSinRutaAlts -> 'AltClaseSueloRptAzMin' 'AltClaseEdificiosRptoAzMin' 'AltClasesVegetacionRptoAzMin'
                    if not self.aFiles['AltClaseSueloRptAzMin'] is None and self.aCeldasCotaMediaTlrSuePsel.shape[0] > 1:
                        if self.aCeldasNumTodosLosRetornosSuelo[nX, nY] > 0:
                            self.aFiles['AltClaseSueloRptAzMin'].write(
                                '%0.02f ' % (round(self.aCeldasCotaMediaTlrSuePsel[nX, nY] - self.aCeldasCotaMinAbsPse[nX, nY], 2))
                            )
                        else:
                            self.aFiles['AltClaseSueloRptAzMin'].write(str(GLO.GLBLnoData) + ' ')
                    if not self.aFiles['AltClasesVegetacionRptoAzMin'] is None and self.aCeldasCotaMediaTlrVegPsel.shape[0] > 1:
                        if self.aCeldasNumTodosLosRetornosVeget[nX, nY] > 0:
                            self.aFiles['AltClasesVegetacionRptoAzMin'].write(
                                '%0.02f ' % (round(self.aCeldasCotaMediaTlrVegPsel[nX, nY] - self.aCeldasCotaMinAbsPse[nX, nY], 2))
                            )
                        else:
                            self.aFiles['AltClasesVegetacionRptoAzMin'].write(str(GLO.GLBLnoData) + ' ')
                    if not self.aFiles['AltClaseEdificiosRptoAzMin'] is None and self.aCeldasCotaMediaTlrEdiPsel.shape[0] > 1:
                        if self.aCeldasNumTodosLosRetornosEdificio[nX, nY] > 0:
                            self.aFiles['AltClaseEdificiosRptoAzMin'].write(
                                '%0.02f ' % (round(self.aCeldasCotaMediaTlrEdiPsel[nX, nY] - self.aCeldasCotaMinAbsPse[nX, nY], 2))
                            )
                        else:
                            self.aFiles['AltClaseEdificiosRptoAzMin'].write(str(GLO.GLBLnoData) + ' ')

                # Numero de puntos suelo en la pasada seleccionada para el suelo
                if GLO.GLBLcalcularMds and GLO.GLBLgrabarNumPuntosSuelo:
                    if not self.aFiles['numPuntosSueloTodasLasPasadas'] is None and self.aCeldasNumPuntosTlrSueTlpTlvSinFiltrar.shape[0] > 1:
                        self.aFiles['numPuntosSueloTodasLasPasadas'].write(str(self.aCeldasNumPuntosTlrSueTlpTlvSinFiltrar[nX, nY]) + ' ')
                    if not self.aFiles['numPuntosSueloPsue'] is None and self.aCeldasNumPuntosTlrSuePsueOk.shape[0] > 1:
                        self.aFiles['numPuntosSueloPsue'].write(str(self.aCeldasNumPuntosTlrSuePsueOk[nX, nY]) + ' ')
                    if not self.aFiles['numPuntosSueloPselOk'] is None and self.aCeldasNumPuntosTlrSuePselOk.shape[0] > 1:
                        self.aFiles['numPuntosSueloPselOk'].write(str(self.aCeldasNumPuntosTlrSuePselOk[nX, nY]) + ' ')
                if GLO.GLBLgrabarNumPuntosTotales:
                    if not self.aFiles['numPuntosTotalesDentroDeBloque'] is None and self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar.shape[0] > 1:
                        self.aFiles['numPuntosTotalesDentroDeBloque'].write(str(self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY]) + ' ')
                    if not self.aFiles['numPuntosPasadaSelecOk'] is None and self.aCeldasNumPuntosTlrTlcPselOk.shape[0] > 1:
                        self.aFiles['numPuntosPasadaSelecOk'].write(str(self.aCeldasNumPuntosTlrTlcPselOk[nX, nY]) + ' ')
                if GLO.GLBLgrabarPrimerosRetornosNoSolape:
                    if not self.aFiles['numPuntosPrimRetSinSolape'] is None and self.aCeldasNumPrimerosRetornosNoSolape.shape[0] > 1:
                        self.aFiles['numPuntosPrimRetSinSolape'].write(str(self.aCeldasNumPrimerosRetornosNoSolape[nX, nY]) + ' ')
                if GLO.GLBLgrabarNumPuntosAuxiliar:
                    if not self.aFiles['numPuntosAlmacenablesSinOutliers'] is None and self.aCeldasNumPuntosTlrTlcTlpOk.shape[0] > 1:
                        self.aFiles['numPuntosAlmacenablesSinOutliers'].write(str(self.aCeldasNumPuntosTlrTlcTlpOk[nX, nY]) + ' ')
                    if not self.aFiles['numPuntosPasadaSelecSinFiltrarSospechosos'] is None and self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos.shape[0] > 1:
                        self.aFiles['numPuntosPasadaSelecSinFiltrarSospechosos'].write(str(self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos[nX, nY]) + ' ')
                if GLO.GLBLgrabarNumIdPasada:
                    if not self.aFiles['numPasadas'] is None and self.aCeldasNumPasadasConPuntos.shape[0] > 1:
                        self.aFiles['numPasadas'].write(str(self.aCeldasNumPasadasConPuntos[nX, nY]) + ' ')
                    if not self.aFiles['idPasadaBasalSeleccionada'] is None and self.IDselec.shape[0] > 1:
                        self.aFiles['idPasadaBasalSeleccionada'].write(str(self.IDselec[nX, nY]) + ' ')
                    if not self.aFiles['idPasadaSueloSeleccionada'] is None and self.IDsuelo.shape[0] > 1:
                        self.aFiles['idPasadaSueloSeleccionada'].write(str(self.IDsuelo[nX, nY]) + ' ')

                if self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos[nX, nY] > GLO.GLBLnMaxPtosCeldaTlrPas:
                    self.nCeldasConDemasiadosPuntosTlrPas += 1
                    if self.nCeldasConDemasiadosPuntosTlrPas < 10:
                        print(
                            'cliddata->', nX, nY,
                            'Hay mas de %i puntos en una celda en la pasada seleccionada' % GLO.GLBLnMaxPtosCeldaTlrPas,
                            '-> self.aCeldasNumPuntosTlrTlcTlpOk[nX, nY]', self.aCeldasNumPuntosTlrTlcTlpOk[nX, nY],
                        )
                        print(
                            '\t-> Celda (%i %i) con %i puntos totales y %i en la pasada sel (y mas de %i puntos en la pasada seleccionada)'
                            % (nX, nY,
                               self.aCeldasNumPuntosTlrTlcTlpTlvSinFiltrar[nX, nY],
                               self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos[nX, nY],
                               GLO.GLBLnMaxPtosCeldaTlrPas)
                        )
                    elif self.nCeldasConDemasiadosPuntosTlrPas == 10:
                        print(
                            'cliddata-> Revisar la seleccion de la pasada-> aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos[nX, nY]',
                            self.aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos[nX, nY],
                        )
                    # input('Revisar aCeldasNumPuntosTlrTlcPselSinFiltrarSospechosos[nX, nY]')

            if GLO.GLBLgrabarCotasDiferenciaEntrePasadas:
                if not self.aFiles['zMediaPtsTodosDiferenciaEntrePasadas'] is None:
                    self.aFiles['zMediaPtsTodosDiferenciaEntrePasadas'].write('\n')
            if GLO.GLBLgrabarCotasMediasPorClase:
                if not self.aFiles['zMediaPtsVegetPsel'] is None:
                    self.aFiles['zMediaPtsVegetPsel'].write('\n')
                if not self.aFiles['zMediaPtsEdifiPsel'] is None:
                    self.aFiles['zMediaPtsEdifiPsel'].write('\n')
                if GLO.GLBLcalcularMds:
                    if not self.aFiles['zMediaPtsSueloPsel'] is None:
                        self.aFiles['zMediaPtsSueloPsel'].write('\n')
                    if not self.aFiles['zMediaPtsSueloPsue'] is None:
                        self.aFiles['zMediaPtsSueloPsue'].write('\n')

            if GLO.GLBLgrabarPropiedadTime:
                if not self.aFiles['rawTime'] is None:
                    self.aFiles['rawTime'].write('\n')
            if GLO.GLBLleerGrabarCeldasEdge:
                if not self.aFiles['scanEdge'] is None:
                    self.aFiles['scanEdge'].write('\n')
            if GLO.GLBLgrabarAngulos:
                if not self.aFiles['Ang'] is None:
                    self.aFiles['Ang'].write('\n')
            if GLO.GLBLgrabarCotaMinMaxCelda:
                if not self.aFiles['CeldasCotaMinAbsTlp'] is None:
                    self.aFiles['CeldasCotaMinAbsTlp'].write('\n')
                if not self.aFiles['CeldasCotaMaxAbsTlp'] is None:
                    self.aFiles['CeldasCotaMaxAbsTlp'].write('\n')

            if GLO.GLBLgrabarAlturasRptoAzMin:
                # listaFilesSinRutaAlts -> 'AltClaseSueloRptAzMin' 'AltClaseEdificiosRptoAzMin' 'AltClasesVegetacionRptoAzMin'
                for tipoAltura in self.listaFilesSinRutaAlts:
                    if not self.aFiles['ipoAltur'] is None:
                        self.aFiles[tipoAltura].write('\n')

            if GLO.GLBLgrabarPrimerosVsSegundosRetornos:
                if not self.aFiles['SingleReturnTodasLasPasadas'] is None:
                    self.aFiles['SingleReturnTodasLasPasadas'].write('\n')
                if not self.aFiles['MultiReturnTodasLasPasadas'] is None:
                    self.aFiles['MultiReturnTodasLasPasadas'].write('\n')
                if not self.aFiles['RetornosPrimerosTodasLasPasadas'] is None:
                    self.aFiles['RetornosPrimerosTodasLasPasadas'].write('\n')
                if not self.aFiles['RetornosSiguientesTodasLasPasadas'] is None:
                    self.aFiles['RetornosSiguientesTodasLasPasadas'].write('\n')
                if not self.aFiles['RetornosPrimerosPasadaSel'] is None:
                    self.aFiles['RetornosPrimerosPasadaSel'].write('\n')
                if not self.aFiles['RetornosSiguientesPasadaSel'] is None:
                    self.aFiles['RetornosSiguientesPasadaSel'].write('\n')

            if GLO.GLBLcalcularMds and GLO.GLBLgrabarNumPuntosSuelo:
                if not self.aFiles['numPuntosSueloTodasLasPasadas'] is None:
                    self.aFiles['numPuntosSueloTodasLasPasadas'].write('\n')
                if not self.aFiles['numPuntosSueloPsue'] is None:
                    self.aFiles['numPuntosSueloPsue'].write('\n')
                if not self.aFiles['numPuntosSueloPselOk'] is None:
                    self.aFiles['numPuntosSueloPselOk'].write('\n')

            if GLO.GLBLgrabarNumPuntosTotales:
                if not self.aFiles['numPuntosTotalesDentroDeBloque'] is None:
                    self.aFiles['numPuntosTotalesDentroDeBloque'].write('\n')
                if not self.aFiles['numPuntosPasadaSelecOk'] is None:
                    self.aFiles['numPuntosPasadaSelecOk'].write('\n')
            if GLO.GLBLgrabarPrimerosRetornosNoSolape:
                if not self.aFiles['numPuntosPrimRetSinSolape'] is None:
                    self.aFiles['numPuntosPrimRetSinSolape'].write('\n')
            if GLO.GLBLgrabarNumPuntosAuxiliar:
                if not self.aFiles['numPuntosAlmacenablesSinOutliers'] is None:
                    self.aFiles['numPuntosAlmacenablesSinOutliers'].write('\n')
                if not self.aFiles['numPuntosPasadaSelecSinFiltrarSospechosos'] is None:
                    self.aFiles['numPuntosPasadaSelecSinFiltrarSospechosos'].write('\n')
            if GLO.GLBLgrabarNumIdPasada:
                if not self.aFiles['numPasadas'] is None:
                    self.aFiles['numPasadas'].write('\n')
                if not self.aFiles['idPasadaBasalSeleccionada'] is None:
                    self.aFiles['idPasadaBasalSeleccionada'].write('\n')
                if not self.aFiles['idPasadaSueloSeleccionada'] is None:
                    self.aFiles['idPasadaSueloSeleccionada'].write('\n')

        if GLO.GLBLgrabarCotasDiferenciaEntrePasadas:
            if not self.aFiles['zMediaPtsTodosDiferenciaEntrePasadas'] is None:
                self.aFiles['zMediaPtsTodosDiferenciaEntrePasadas'].close()
        if GLO.GLBLgrabarCotasMediasPorClase:
            if not self.aFiles['zMediaPtsVegetPsel'] is None:
                self.aFiles['zMediaPtsVegetPsel'].close()
            if not self.aFiles['zMediaPtsEdifiPsel'] is None:
                self.aFiles['zMediaPtsEdifiPsel'].close()
            if GLO.GLBLcalcularMds:
                if not self.aFiles['zMediaPtsSueloPsel'] is None:
                    self.aFiles['zMediaPtsSueloPsel'].close()
                if not self.aFiles['zMediaPtsSueloPsue'] is None:
                    self.aFiles['zMediaPtsSueloPsue'].close()

        if GLO.GLBLgrabarPropiedadTime:
            if not self.aFiles['rawTime'] is None:
                self.aFiles['rawTime'].close()
        if GLO.GLBLleerGrabarCeldasEdge:
            if not self.aFiles['scanEdge'] is None:
                self.aFiles['scanEdge'].close()
        if GLO.GLBLgrabarAngulos:
            if not self.aFiles['Ang'] is None:
                self.aFiles['Ang'].close()
        if GLO.GLBLgrabarCotaMinMaxCelda:
            if not self.aFiles['CeldasCotaMinAbsTlp'] is None:
                self.aFiles['CeldasCotaMinAbsTlp'].close()
            if not self.aFiles['CeldasCotaMaxAbsTlp'] is None:
                self.aFiles['CeldasCotaMaxAbsTlp'].close()

        if GLO.GLBLgrabarAlturasRptoAzMin:
            # listaFilesSinRutaAlts -> 'AltClaseSueloRptAzMin' 'AltClaseEdificiosRptoAzMin' 'AltClasesVegetacionRptoAzMin'
            for tipoAltura in self.listaFilesSinRutaAlts:
                if not self.aFiles['ipoAltur'] is None:
                    self.aFiles[tipoAltura].close()

        if GLO.GLBLgrabarPrimerosVsSegundosRetornos:
            if not self.aFiles['SingleReturnTodasLasPasadas'] is None:
                self.aFiles['SingleReturnTodasLasPasadas'].close()
            if not self.aFiles['MultiReturnTodasLasPasadas'] is None:
                self.aFiles['MultiReturnTodasLasPasadas'].close()
            if not self.aFiles['RetornosPrimerosTodasLasPasadas'] is None:
                self.aFiles['RetornosPrimerosTodasLasPasadas'].close()
            if not self.aFiles['RetornosSiguientesTodasLasPasadas'] is None:
                self.aFiles['RetornosSiguientesTodasLasPasadas'].close()
            if not self.aFiles['RetornosPrimerosPasadaSel'] is None:
                self.aFiles['RetornosPrimerosPasadaSel'].close()
            if not self.aFiles['RetornosSiguientesPasadaSel'] is None:
                self.aFiles['RetornosSiguientesPasadaSel'].close()

        if GLO.GLBLcalcularMds and GLO.GLBLgrabarNumPuntosSuelo:
            if not self.aFiles['numPuntosSueloTodasLasPasadas'] is None:
                self.aFiles['numPuntosSueloTodasLasPasadas'].close()
            if not self.aFiles['numPuntosSueloPsue'] is None:
                self.aFiles['numPuntosSueloPsue'].close()
            if not self.aFiles['numPuntosSueloPselOk'] is None:
                self.aFiles['numPuntosSueloPselOk'].close()

        if GLO.GLBLgrabarNumPuntosTotales:
            if not self.aFiles['numPuntosTotalesDentroDeBloque'] is None:
                self.aFiles['numPuntosTotalesDentroDeBloque'].close()
            if not self.aFiles['numPuntosPasadaSelecOk'] is None:
                self.aFiles['numPuntosPasadaSelecOk'].close()
        if GLO.GLBLgrabarPrimerosRetornosNoSolape:
            if not self.aFiles['numPuntosPrimRetSinSolape'] is None:
                self.aFiles['numPuntosPrimRetSinSolape'].close()
        if GLO.GLBLgrabarNumPuntosAuxiliar:
            if not self.aFiles['numPuntosAlmacenablesSinOutliers'] is None:
                self.aFiles['numPuntosAlmacenablesSinOutliers'].close()
            if not self.aFiles['numPuntosPasadaSelecSinFiltrarSospechosos'] is None:
                self.aFiles['numPuntosPasadaSelecSinFiltrarSospechosos'].close()
        if GLO.GLBLgrabarNumIdPasada:
            if not self.aFiles['numPasadas'] is None:
                self.aFiles['numPasadas'].close()
            if not self.aFiles['idPasadaBasalSeleccionada'] is None:
                self.aFiles['idPasadaBasalSeleccionada'].close()
            if not self.aFiles['idPasadaSueloSeleccionada'] is None:
                self.aFiles['idPasadaSueloSeleccionada'].close()
        # ======================================================================

        # ======================================================================
        if GLO.GLBLcalcularSubCeldas:
            # ==================================================================
            if GLO.GLBLgrabarCotaMinMaxSubCelda:
                # CotaMinMax/02mCell/CotaMin
                if not self.aFiles['SubCeldasCotaMin'] is None and self.aSubCeldasCotaMinAA.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasCotaMin')
                    for nY in reversed(range(self.aSubCeldasCotaMinAA.shape[1])):
                        for nX in range(self.aSubCeldasCotaMinAA.shape[0]):
                            if (
                                self.aSubCeldasCotaMinAA[nX, nY] != 0
                                and self.aSubCeldasCotaMinAA[nX, nY] != 9999
                                and self.aSubCeldasCotaMinAA[nX, nY] != GLO.GLBLnoData
                            ):
                                self.aFiles['SubCeldasCotaMin'].write('%07.02f' % round(self.aSubCeldasCotaMinAA[nX, nY], 2) + ' ')
                            else:
                                self.aFiles['SubCeldasCotaMin'].write('%07.01f ' % GLO.GLBLnoData)
                        self.aFiles['SubCeldasCotaMin'].write('\n')
                    self.aFiles['SubCeldasCotaMin'].close()
                # CotaMinMax/02mCell/CotaMax
                if not self.aFiles['SubCeldasCotaMax'] is None and self.aSubCeldasCotaMaxAA.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasCotaMax')
                    for nY in reversed(range(self.aSubCeldasCotaMaxAA.shape[1])):
                        for nX in range(self.aSubCeldasCotaMaxAA.shape[0]):
                            if (
                                self.aSubCeldasCotaMaxAA[nX, nY] != 0
                                and self.aSubCeldasCotaMaxAA[nX, nY] != 9999
                                and self.aSubCeldasCotaMaxAA[nX, nY] != GLO.GLBLnoData
                            ):
                                self.aFiles['SubCeldasCotaMax'].write('%06.02f' % round(self.aSubCeldasCotaMaxAA[nX, nY], 2) + ' ')
                            else:
                                self.aFiles['SubCeldasCotaMax'].write('%06.01f ' % GLO.GLBLnoData)
                        self.aFiles['SubCeldasCotaMax'].write('\n')
                    self.aFiles['SubCeldasCotaMax'].close()
            else:
                print('cliddata-> No se graban cotas MinMax de subcelda-> GLBLgrabarCotaMinMaxSubCelda:', GLO.GLBLgrabarCotaMinMaxSubCelda)



    # ==========================================================================
    # if GLO.GLBLcalcularApices and GLBNcrearOutputFiles # Apices/10mCell
    def guardarApices(self):
        if (
            not self.aFiles['CeldasApicesMicro'] is None
            and not self.aFiles['CeldasApicesMesos'] is None
            and not self.aFiles['CeldasApicesMacro'] is None
            and not self.aFiles['CeldasApicesMegas'] is None
            and self.aCeldasApices.shape[0] > 1
        ):
            # myClassArray = getattr(self, 'aCeldasApices', None)
            for nY in range(self.nCeldasY - 1, 0 - 1, -1):
                for nX in range(self.nCeldasX):
                    if nX >= self.aCeldasApices.shape[0] or nY >= self.aCeldasApices.shape[1]:
                        continue
                    self.aFiles['CeldasApicesMicro'].write(str(self.aCeldasApices[nX, nY, 0]) + ' ')
                    self.aFiles['CeldasApicesMesos'].write(str(self.aCeldasApices[nX, nY, 1]) + ' ')
                    self.aFiles['CeldasApicesMacro'].write(str(self.aCeldasApices[nX, nY, 2]) + ' ')
                    self.aFiles['CeldasApicesMegas'].write(str(self.aCeldasApices[nX, nY, 3]) + ' ')
                self.aFiles['CeldasApicesMicro'].write('\n')
                self.aFiles['CeldasApicesMesos'].write('\n')
                self.aFiles['CeldasApicesMacro'].write('\n')
                self.aFiles['CeldasApicesMegas'].write('\n')
            self.aFiles['CeldasApicesMicro'].close()
            self.aFiles['CeldasApicesMesos'].close()
            self.aFiles['CeldasApicesMacro'].close()
            self.aFiles['CeldasApicesMegas'].close()


    # ==========================================================================
    # if GLBLcalcularSubCeldas and GLBLgrabarMdgAjusteSubCelda:  # Mde/02mCell/Global/
    def guardarMdgSubCelda(self):
        myClassArray = getattr(self, 'aSubCeldasMdgAjuste', None)
        for nY in reversed(range(self.aSubCeldasMdgAjuste.shape[1])):
            for nX in range(self.aSubCeldasMdgAjuste.shape[0]):
                if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                    nX >= self.aSubCeldasMdgAjuste.shape[0]
                    or nY >= self.aSubCeldasMdgAjuste.shape[1]
                ):
                    continue
                if (
                    self.aSubCeldasMdgAjuste[nX, nY, 0] != 0
                    and self.aSubCeldasMdgAjuste[nX, nY, 0] != 9999
                    and self.aSubCeldasMdgAjuste[nX, nY, 0] != GLO.GLBLnoData
                ):
                    if GLO.GLBLgrabarInterceptMdg:
                        if not self.aFiles['SubCeldasMdgCota'] is None and self.aSubCeldasMdgAjuste.shape[0] > 1:
                            self.aFiles['SubCeldasMdgCota'].write('%07.02f' % round(self.aSubCeldasMdgAjuste[nX, nY, 0], 2) + ' ')
                    if GLO.GLBLgrabarCoeficientesXYMdg:
                        if not self.aFiles['SubCeldasMdgPteX'] is None and self.aSubCeldasMdgAjuste.shape[0] > 1:
                            self.aFiles['SubCeldasMdgPteX'].write('%05.02f' % round(self.aSubCeldasMdgAjuste[nX, nY, 1], 2) + ' ')
                        if not self.aFiles['SubCeldasMdgPteY'] is None and self.aSubCeldasMdgAjuste.shape[0] > 1:
                            self.aFiles['SubCeldasMdgPteY'].write('%05.02f' % round(self.aSubCeldasMdgAjuste[nX, nY, 2], 2) + ' ')
                    if GLO.GLBLgrabarEcmrMdg:
                        if not self.aFiles['SubCeldasMdgEcmr'] is None and self.aSubCeldasMdgAjuste.shape[0] > 1:
                            self.aFiles['SubCeldasMdgEcmr'].write('%04.02f' % round(self.aSubCeldasMdgAjuste[nX, nY, 3], 2) + ' ')
                else:
                    if GLO.GLBLgrabarInterceptMdg:
                        if not self.aFiles['SubCeldasMdgCota'] is None:
                            self.aFiles['SubCeldasMdgCota'].write('%07.0f ' % GLO.GLBLnoData)
                    if GLO.GLBLgrabarCoeficientesXYMdg:
                        if not self.aFiles['SubCeldasMdgPteX'] is None:
                            self.aFiles['SubCeldasMdgPteX'].write('%05.0f ' % GLO.GLBLnoData)
                        if not self.aFiles['SubCeldasMdgPteY'] is None:
                            self.aFiles['SubCeldasMdgPteY'].write('%05.0f ' % GLO.GLBLnoData)
                    if GLO.GLBLgrabarEcmrMdg:
                        if not self.aFiles['SubCeldasMdgEcmr'] is None:
                            self.aFiles['SubCeldasMdgEcmr'].write('%04.0f ' % GLO.GLBLnoData)
            if GLO.GLBLgrabarInterceptMdg:
                if not self.aFiles['SubCeldasMdgCota'] is None:
                    self.aFiles['SubCeldasMdgCota'].write('\n')
            if GLO.GLBLgrabarCoeficientesXYMdg:
                if not self.aFiles['SubCeldasMdgPteX'] is None:
                    self.aFiles['SubCeldasMdgPteX'].write('\n')
                if not self.aFiles['SubCeldasMdgPteY'] is None:
                    self.aFiles['SubCeldasMdgPteY'].write('\n')
            if GLO.GLBLgrabarEcmrMdg:
                if not self.aFiles['SubCeldasMdgEcmr'] is None:
                    self.aFiles['SubCeldasMdgEcmr'].write('\n')
        if GLO.GLBLgrabarInterceptMdg:
            if not self.aFiles['SubCeldasMdgCota'] is None:
                self.aFiles['SubCeldasMdgCota'].close()
        if GLO.GLBLgrabarCoeficientesXYMdg:
            if not self.aFiles['SubCeldasMdgPteX'] is None:
                self.aFiles['SubCeldasMdgPteX'].close()
            if not self.aFiles['SubCeldasMdgPteY'] is None:
                self.aFiles['SubCeldasMdgPteY'].close()
        if GLO.GLBLgrabarEcmrMdg:
            if not self.aFiles['SubCeldasMdgEcmr'] is None:
                self.aFiles['SubCeldasMdgEcmr'].close()

    # ==========================================================================
    # if GLO.GLBLgrabarIndicesVegetacionNDVIetAlSubCelda: #RGBI/02mCell/
    def guardarIndicesIRGBIrISubCelda(self):
        # Guardo los valores medios de intensity e indices RGBIr por subCelda
        print('\t\t\tcliddata-> guardando indices de subceldas')
        if GLO.GLBLgrabarIndicesVegetacionIntSRet:  # RGBI/02mCellIntSRet/
            if not self.aFiles['SubCeldasIntSRetMed'] is None and self.aSubCeldasIntSRetMed.shape[0] > 1:
                for nSubY in reversed(range(self.aSubCeldasIntSRetMed.shape[1])):
                    for nSubX in range(self.aSubCeldasIntSRetMed.shape[0]):
                        self.aFiles['SubCeldasIntSRetMed'].write('%05i ' % round(self.aSubCeldasIntSRetMed[nSubX, nSubY], 2))
                    self.aFiles['SubCeldasIntSRetMed'].write('\n')
                self.aFiles['SubCeldasIntSRetMed'].close()
        if GLO.GLBLgrabarIndicesVegetacionIntMRet:  # RGBI/02mCellIntMRet/
            if not self.aFiles['SubCeldasIntMRetMed'] is None and self.aSubCeldasIntMRetMed.shape[0] > 1:
                for nSubY in reversed(range(self.aSubCeldasIntMRetMed.shape[1])):
                    for nSubX in range(self.aSubCeldasIntMRetMed.shape[0]):
                        self.aFiles['SubCeldasIntMRetMed'].write('%05i ' % round(self.aSubCeldasIntMRetMed[nSubX, nSubY], 2))
                    self.aFiles['SubCeldasIntMRetMed'].write('\n')
                self.aFiles['SubCeldasIntMRetMed'].close()
        if GLO.GLBLgrabarIndicesVegetacionEVI2:  # RGBI/02mCellEVI2/
            if not self.aFiles['SubCeldasEVI2'] is None and self.aSubCeldasEVI2Med.shape[0] > 1:
                for nSubY in reversed(range(self.aSubCeldasEVI2Med.shape[1])):
                    for nSubX in range(self.aSubCeldasEVI2Med.shape[0]):
                        if self.aSubCeldasEVI2Med[nSubX, nSubY] == GLO.GLBLnoData:
                            self.aFiles['SubCeldasEVI2'].write('{:05} '.format(GLO.GLBLnoData))
                        else:
                            self.aFiles['SubCeldasEVI2'].write('{:05.2f} '.format(round(self.aSubCeldasEVI2Med[nSubX, nSubY], 2)))
                    self.aFiles['SubCeldasEVI2'].write('\n')
                self.aFiles['SubCeldasEVI2'].close()
        if GLO.GLBLgrabarIndicesVegetacionNDVI:  # RGBI/02mCellNDVI/
            if not self.aFiles['SubCeldasNDVI'] is None and self.aSubCeldasNDVIMed.shape[0] > 1:
                for nSubY in reversed(range(self.aSubCeldasNDVIMed.shape[1])):
                    for nSubX in range(self.aSubCeldasNDVIMed.shape[0]):
                        if self.aSubCeldasNDVIMed[nSubX, nSubY] == GLO.GLBLnoData:
                            self.aFiles['SubCeldasNDVI'].write('{:05} '.format(GLO.GLBLnoData))
                        else:
                            self.aFiles['SubCeldasNDVI'].write('{:05.2f} '.format(round(self.aSubCeldasNDVIMed[nSubX, nSubY], 2)))
                    self.aFiles['SubCeldasNDVI'].write('\n')
                self.aFiles['SubCeldasNDVI'].close()
        if GLO.GLBLgrabarIndicesVegetacionNDWI:  # RGBI/02mCellNDWI/
            if not self.aFiles['SubCeldasNDWI'] is None and self.aSubCeldasNDWIMed.shape[0] > 1:
                for nSubY in reversed(range(self.aSubCeldasNDWIMed.shape[1])):
                    for nSubX in range(self.aSubCeldasIntSRetMed.shape[0]):
                        if self.aSubCeldasNDWIMed[nSubX, nSubY] == GLO.GLBLnoData:
                            self.aFiles['SubCeldasNDWI'].write('{:05} '.format(GLO.GLBLnoData))
                        else:
                            self.aFiles['SubCeldasNDWI'].write('{:05.2f} '.format(round(self.aSubCeldasNDWIMed[nSubX, nSubY], 2)))
                    self.aFiles['SubCeldasNDWI'].write('\n')
                self.aFiles['SubCeldasNDWI'].close()


    # ==========================================================================
    # if GLO.GLBLgrabarIndicesVegetacionNDVIetAlMetricos: #RGBI/01mCell/
    def guardarIndicesIRGBIrIMetricos(self):
        # Guardo los valores medios de intensity e indices RGBIr por metrico
        print('\t\t\tcliddata-> guardando indices metricos')
        if GLO.GLBLgrabarIndicesVegetacionIntSRet:  # RGBI/01mCellIntSRet/
            if not self.aFiles['MetricoIntSRet'] is None and self.aMetricoIntSRet.shape[0] > 1:
                for metrY in reversed(range(self.aMetricoIntSRet.shape[1])):
                    for metrX in range(self.aMetricoIntSRet.shape[0]):
                        self.aFiles['MetricoIntSRet'].write('%05i ' % round(self.aMetricoIntSRet[metrX, metrY], 0))
                    self.aFiles['MetricoIntSRet'].write('\n')
                self.aFiles['MetricoIntSRet'].close()
        if GLO.GLBLgrabarIndicesVegetacionIntMRet:  # RGBI/01mCellIntMRet/
            if not self.aFiles['MetricoEVI2'] is None and self.aMetricoEVI2Med.shape[0] > 1:
                for metrY in reversed(range(self.aMetricoEVI2Med.shape[1])):
                    for metrX in range(self.aMetricoEVI2Med.shape[0]):
                        if self.aMetricoEVI2Med[metrX, metrY] == GLO.GLBLnoData:
                            self.aFiles['MetricoEVI2'].write('{:05} '.format(GLO.GLBLnoData))
                        else:
                            self.aFiles['MetricoEVI2'].write('{:05.2f} '.format(self.aMetricoEVI2Med[metrX, metrY]))
                    self.aFiles['MetricoEVI2'].write('\n')
                self.aFiles['MetricoEVI2'].close()
        if GLO.GLBLgrabarIndicesVegetacionNDVI:  # RGBI/01mCellNDVI/
            if not self.aFiles['MetricoNDVI'] is None and self.aMetricoNDVIMed.shape[0] > 1:
                for metrY in reversed(range(self.aMetricoNDVIMed.shape[1])):
                    for metrX in range(self.aMetricoNDVIMed.shape[0]):
                        if self.aMetricoNDVIMed[metrX, metrY] == GLO.GLBLnoData:
                            self.aFiles['MetricoNDVI'].write('{:05} '.format(GLO.GLBLnoData))
                        else:
                            self.aFiles['MetricoNDVI'].write('{:05.2f} '.format(self.aMetricoNDVIMed[metrX, metrY]))
                    self.aFiles['MetricoNDVI'].write('\n')
                self.aFiles['MetricoNDVI'].close()
        if GLO.GLBLgrabarIndicesVegetacionNDWI:  # RGBI/01mCellNDWI/
            if not self.aFiles['MetricoNDWI'] is None and self.aMetricoNDWIMed.shape[0] > 1:
                for metrY in reversed(range(self.aMetricoNDWIMed.shape[1])):
                    for metrX in range(self.aMetricoNDWIMed.shape[0]):
                        if self.aMetricoNDWIMed[metrX, metrY] == GLO.GLBLnoData:
                            self.aFiles['MetricoNDWI'].write('{:05} '.format(GLO.GLBLnoData))
                        else:
                            self.aFiles['MetricoNDWI'].write('{:05.2f} '.format(self.aMetricoNDWIMed[metrX, metrY]))
                    self.aFiles['MetricoNDWI'].write('\n')
                self.aFiles['MetricoNDWI'].close()


    # ==========================================================================
    # if GLO.GLBLgrabarPuntosPorClaseLasOrig:
    # if GLO.GLBLgrabarNumeroPuntosPorClase:
    def guardarNumPuntosPorClasesCeldas(self, lasOrigRecl):
        # Numero de puntos por clase en cada celda (no necesito guardarlo para mas adelante)
        # PointClass/Orig/10mCell/NumPtos/
        print('\t\t\tcliddata-> guardando numero de puntos por clase en Celdas (lasFile{})'.format(lasOrigRecl))
        for nY in reversed(range(self.aCeldasNumPtosPorClaseTlrTlp.shape[1])):
            for nX in reversed(range(self.aCeldasNumPtosPorClaseTlrTlp.shape[0])):
                for lasClassNum in range(GLO.GLBLnumMaximoDeClases):
                    fileNameSinRuta = 'Clase{:02}_TodasLasPasadasTodosLosRetornos_NumPuntos_{}'.format(lasClassNum, lasOrigRecl)
                    if not self.aFiles[fileNameSinRuta] is None and self.aCeldasNumPtosPorClaseTlrTlp.shape[0] > 1:
                        self.aFiles[fileNameSinRuta].write(str(self.aCeldasNumPtosPorClaseTlrTlp[nX, nY][lasClassNum]) + ' ')
            for lasClassNum in range(GLO.GLBLnumMaximoDeClases):
                fileNameSinRuta = 'Clase{:02}_TodasLasPasadasTodosLosRetornos_NumPuntos_{}'.format(lasClassNum, lasOrigRecl)
                if not self.aFiles[fileNameSinRuta] is None:
                    self.aFiles[fileNameSinRuta].write('\n')
        for lasClassNum in range(GLO.GLBLnumMaximoDeClases):
            fileNameSinRuta = 'Clase{:02}_TodasLasPasadasTodosLosRetornos_NumPuntos_{}'.format(lasClassNum, lasOrigRecl)
            if not self.aFiles[fileNameSinRuta] is None:
                self.aFiles[fileNameSinRuta].close()

 
    # ==========================================================================
    # if GLO.GLBLgrabarPuntosPorClaseLasOrig:
    # if GLO.GLBLgrabarCeldasClasesSueloVegetacion or GLO.GLBLgrabarCeldasClasesEdificio or GLO.GLBLgrabarCeldasClasesOtros:
    def guardarClasesCeldas(self, lasOrigRecl):
        print('\t\t\tcliddata-> guardando clases Celdas (lasFile{})'.format(lasOrigRecl))
        for nY in reversed(range(self.aCeldasNumPrimerosRetornosSuelo.shape[1])):
            for nX in reversed(range(self.aCeldasNumPrimerosRetornosSuelo.shape[0])):

                if GLO.GLBLgrabarCeldasClasesSueloVegetacion:
                    # PointClass/Orig/10mCell/PorcentajePtosSuelo/, PointClass/Orig/10mCell/PorcentajePtosVeget/
                    if not self.aFiles['CeldasPrcntjPrimerosRetornosSuelo_{}'.format(lasOrigRecl)] is None and self.aCeldasNumPrimerosRetornosSuelo.shape[0] > 1:
                        if self.aCeldasNumPrimerosRetornosTlp[nX, nY] > 0:
                            self.aFiles['CeldasPrcntjPrimerosRetornosSuelo_{}'.format(lasOrigRecl)].write(
                                str(int(100 * self.aCeldasNumPrimerosRetornosSuelo[nX, nY] / self.aCeldasNumPrimerosRetornosTlp[nX, nY])) + ' '
                            )
                        else:
                            self.aFiles['CeldasPrcntjPrimerosRetornosSuelo_{}'.format(lasOrigRecl)].write('0 ')
                    if not self.aFiles['CeldasPrcntjPrimerosRetornosVeget_{}'.format(lasOrigRecl)] is None and self.aCeldasNumPrimerosRetornosVeget.shape[0] > 1:
                        if self.aCeldasNumPrimerosRetornosTlp[nX, nY] > 0:
                            self.aFiles['CeldasPrcntjPrimerosRetornosVeget_{}'.format(lasOrigRecl)].write(
                                str(int(100 * self.aCeldasNumPrimerosRetornosVeget[nX, nY] / self.aCeldasNumPrimerosRetornosTlp[nX, nY])) + ' '
                            )
                        else:
                            self.aFiles['CeldasPrcntjPrimerosRetornosVeget_{}'.format(lasOrigRecl)].write('0 ')

                if GLO.GLBLgrabarCeldasClasesEdificio:
                    # PointClass/Orig/10mCell/PorcentajePtosEdificio/
                    if not self.aFiles['CeldasPrcntjPrimerosRetornosEdifi_{}'.format(lasOrigRecl)] is None and self.aCeldasNumPrimerosRetornosEdificio.shape[0] > 1:
                        if self.aCeldasNumPrimerosRetornosTlp[nX, nY] > 0:
                            self.aFiles['CeldasPrcntjPrimerosRetornosEdifi_{}'.format(lasOrigRecl)].write(
                                str(int(100 * self.aCeldasNumPrimerosRetornosEdificio[nX, nY] / self.aCeldasNumPrimerosRetornosTlp[nX, nY])) + ' '
                            )
                        else:
                            self.aFiles['CeldasPrcntjPrimerosRetornosEdifi_{}'.format(lasOrigRecl)].write('0 ')

                if GLO.GLBLgrabarCeldasClasesOtros:
                    # PointClass/Orig/10mCell/PorcentajePtosOtros/
                    if not self.aFiles['CeldasPrcntjPrimerosRetornosOverl_{}'.format(lasOrigRecl)] is None and self.aCeldasNumTodosLosRetornosOverlap.shape[0] > 1:
                        if self.aCeldasNumPrimerosRetornosTlp[nX, nY] > 0:
                            self.aFiles['CeldasPrcntjPrimerosRetornosOverl_{}'.format(lasOrigRecl)].write(
                                str(int(100 * self.aCeldasNumTodosLosRetornosOverlap[nX, nY] / self.aCeldasNumPrimerosRetornosTlp[nX, nY])) + ' '
                            )
                        else:
                            self.aFiles['CeldasPrcntjPrimerosRetornosOverl_{}'.format(lasOrigRecl)].write('0 ')
                    if not self.aFiles['CeldasPrcntjPrimerosRetornosOtros_{}'.format(lasOrigRecl)] is None and self.aCeldasNumPrimerosRetornosOtros.shape[0] > 1:
                        if self.aCeldasNumPrimerosRetornosTlp[nX, nY] > 0:
                            self.aFiles['CeldasPrcntjPrimerosRetornosOtros_{}'.format(lasOrigRecl)].write(
                                str(int(100 * self.aCeldasNumPrimerosRetornosOtros[nX, nY] / self.aCeldasNumPrimerosRetornosTlp[nX, nY])) + ' '
                            )
                        else:
                            self.aFiles['CeldasPrcntjPrimerosRetornosOtros_{}'.format(lasOrigRecl)].write('0 ')

            if GLO.GLBLgrabarCeldasClasesSueloVegetacion:
                if not self.aFiles['CeldasPrcntjPrimerosRetornosSuelo'] is None:
                    self.aFiles['CeldasPrcntjPrimerosRetornosSuelo'].write('\n')
                if not self.aFiles['CeldasPrcntjPrimerosRetornosVeget'] is None:
                    self.aFiles['CeldasPrcntjPrimerosRetornosVeget'].write('\n')
            if GLO.GLBLgrabarCeldasClasesEdificio:
                if not self.aFiles['CeldasPrcntjPrimerosRetornosEdifi'] is None:
                    self.aFiles['CeldasPrcntjPrimerosRetornosEdifi'].write('\n')
            if GLO.GLBLgrabarCeldasClasesOtros:
                if not self.aFiles['CeldasPrcntjPrimerosRetornosOverl'] is None:
                    self.aFiles['CeldasPrcntjPrimerosRetornosOverl'].write('\n')
                if not self.aFiles['CeldasPrcntjPrimerosRetornosOtros'] is None:
                    self.aFiles['CeldasPrcntjPrimerosRetornosOtros'].write('\n')

        if GLO.GLBLgrabarCeldasClasesSueloVegetacion:
            if not self.aFiles['CeldasPrcntjPrimerosRetornosSuelo'] is None:
                self.aFiles['CeldasPrcntjPrimerosRetornosSuelo'].close()
            if not self.aFiles['CeldasPrcntjPrimerosRetornosVeget'] is None:
                self.aFiles['CeldasPrcntjPrimerosRetornosVeget'].close()
        if GLO.GLBLgrabarCeldasClasesEdificio:
            if not self.aFiles['CeldasPrcntjPrimerosRetornosEdifi'] is None:
                self.aFiles['CeldasPrcntjPrimerosRetornosEdifi'].close()
        if GLO.GLBLgrabarCeldasClasesOtros:
            if not self.aFiles['CeldasPrcntjPrimerosRetornosOverl'] is None:
                self.aFiles['CeldasPrcntjPrimerosRetornosOverl'].close()
            if not self.aFiles['CeldasPrcntjPrimerosRetornosOtros'] is None:
                self.aFiles['CeldasPrcntjPrimerosRetornosOtros'].close()


    # ==========================================================================
    # if GLO.GLBLgrabarPuntosPorClaseLasOrig:
    # if GLBLgrabarSubCeldasClasesSueloVegetacion or GLBLgrabarSubCeldasClasesEdificio or GLBLgrabarSubCeldasClasesOtros:
    def guardarClasesSubCeldas(self, lasOrigRecl):
        # Guardo el numero de retornos por clase
        print('\t\t\tcliddata-> guardando clases SubCeldas (lasFile{})'.format(lasOrigRecl))
        if GLO.GLBLgrabarSubCeldasClasesSueloVegetacion:  # PointClass/Orig/02mCell/Suelo/
            for sCelY in reversed(range(self.aSubCeldasProp09TodosLosRetornosSuelo.shape[1])):
                for sCelX in range(self.aSubCeldasProp09TodosLosRetornosSuelo.shape[0]):

                    if not self.aFiles['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)] is None and self.aSubCeldasProp09TodosLosRetornosSuelo.shape[0] > 1:
                        self.aFiles['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)].write('%01i ' % self.aSubCeldasProp09TodosLosRetornosSuelo[sCelX, sCelY])
                    elif not self.aFiles['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)].write('%01i ' % 0)
                    if not self.aFiles['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)] is None and self.aSubCeldasProp09TodosLosRetornosVeget.shape[0] > 1:
                        self.aFiles['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)].write('%01i ' % self.aSubCeldasProp09TodosLosRetornosVeget[sCelX, sCelY])
                    elif not self.aFiles['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)].write('%01i ' % 0)
                    if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                        if not self.aFiles['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)] is None and self.aSubCeldasProp09PrimerosRetornosSuelo.shape[0] > 1:
                            self.aFiles['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)].write('%01i ' % self.aSubCeldasProp09PrimerosRetornosSuelo[sCelX, sCelY])
                        elif not self.aFiles['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                            self.aFiles['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)].write('%01i ' % 0)
                        if not self.aFiles['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)] is None and self.aSubCeldasProp09PrimerosRetornosVeget.shape[0] > 1:
                            self.aFiles['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)].write('%01i ' % self.aSubCeldasProp09PrimerosRetornosVeget[sCelX, sCelY])
                        elif not self.aFiles['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                            self.aFiles['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)].write('%01i ' % 0)
                if not self.aFiles['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)].write('\n')
                if not self.aFiles['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)].write('\n')
                if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                    if not self.aFiles['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)].write('\n')
                    if not self.aFiles['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)].write('\n')
            if not self.aFiles['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                self.aFiles['SubCeldasProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)].close()
            if not self.aFiles['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                self.aFiles['SubCeldasProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)].close()
            if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                if not self.aFiles['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['SubCeldasProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)].close()
                if not self.aFiles['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['SubCeldasProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)].close()

        if GLO.GLBLgrabarSubCeldasClasesEdificio:  # PointClass/Orig/02mCell/Edificio/
            for sCelY in reversed(range(self.aSubCeldasProp09TodosLosRetornosEdificio.shape[1])):
                for sCelX in range(self.aSubCeldasProp09TodosLosRetornosEdificio.shape[0]):
                    if not self.aFiles['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)] is None and self.aSubCeldasProp09TodosLosRetornosEdificio.shape[0] > 1:
                        self.aFiles['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)].write('%01i ' % self.aSubCeldasProp09TodosLosRetornosEdificio[sCelX, sCelY])
                    elif not self.aFiles['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)].write('%01i ' % 0)
                    if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                        if not self.aFiles['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)] is None and self.aSubCeldasProp09PrimerosRetornosEdificio.shape[0] > 1:
                            self.aFiles['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)].write('%01i ' % self.aSubCeldasProp09PrimerosRetornosEdificio[sCelX, sCelY])
                        elif not self.aFiles['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                            self.aFiles['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)].write('%01i ' % 0)
                if not self.aFiles['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)].write('\n')
                if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                    if not self.aFiles['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)].write('\n')
            if not self.aFiles['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                self.aFiles['SubCeldasProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)].close()
            if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                if not self.aFiles['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['SubCeldasProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)].close()

        if GLO.GLBLgrabarSubCeldasClasesOtros:  # PointClass/Orig/02mCell/Otros/
            for sCelY in reversed(range(self.aSubCeldasProp09TodosLosRetornosOtros.shape[1])):
                for sCelX in range(self.aSubCeldasProp09TodosLosRetornosOtros.shape[0]):
                    if not self.aFiles['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)] is None and self.aSubCeldasProp09TodosLosRetornosOtros.shape[0] > 1:
                        self.aFiles['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)].write('%01i ' % self.aSubCeldasProp09TodosLosRetornosOtros[sCelX, sCelY])
                    elif not self.aFiles['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)].write('%01i ' % 0)
                    if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                        if not self.aFiles['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)] is None and self.aSubCeldasProp09PrimerosRetornosOtros.shape[0] > 1:
                            self.aFiles['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)].write('%01i ' % self.aSubCeldasProp09PrimerosRetornosOtros[sCelX, sCelY])
                        elif not self.aFiles['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                            self.aFiles['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)].write('%01i ' % 0)
                if not self.aFiles['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)].write('\n')
                if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                    if not self.aFiles['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)].write('\n')
            if not self.aFiles['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                self.aFiles['SubCeldasProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)].close()
            if GLO.GLBLgrabarSubCeldasClasesConPrimerosRetornos:
                if not self.aFiles['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['SubCeldasProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)].close()


    # ==========================================================================
    # if GLO.GLBLgrabarPuntosPorClaseLasOrig:
    # if GLBLgrabarMetricoClasesSueloVegetacion or GLBLgrabarMetricoClasesEdificio or GLBLgrabarMetricoClasesOtros:
    def guardarClasesMetricos(self, lasOrigRecl):
        # Guardo el numero de retornos por clase
        print('\t\t\tcliddata-> guardando clases metricos (lasFile{})'.format(lasOrigRecl))
        if GLO.GLBLgrabarMetricoClasesSueloVegetacion:  # PointClass/Orig/01mCell/Suelo/
            for metrY in reversed(range(self.aMetricoProp09TodosLosRetornosSuelo.shape[1])):
                for metrX in range(self.aMetricoProp09TodosLosRetornosSuelo.shape[0]):

                    if not self.aFiles['MetricoProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)] is None and self.aMetricoProp09TodosLosRetornosSuelo.shape[0] > 1:
                        self.aFiles['MetricoProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)].write('%01i ' % self.aMetricoProp09TodosLosRetornosSuelo[metrX, metrY])
                    if not self.aFiles['MetricoProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)] is None and self.aMetricoProp09TodosLosRetornosVeget.shape[0] > 1:
                        self.aFiles['MetricoProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)].write('%01i ' % self.aMetricoProp09TodosLosRetornosVeget[metrX, metrY])
                    if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                        if not self.aFiles['MetricoProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)] is None and self.aMetricoProp09PrimerosRetornosSuelo.shape[0] > 1:
                            self.aFiles['MetricoProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)].write('%01i ' % self.aMetricoProp09PrimerosRetornosSuelo[metrX, metrY])
                        if not self.aFiles['MetricoProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)] is None and self.aMetricoProp09PrimerosRetornosVeget.shape[0] > 1:
                            self.aFiles['MetricoProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)].write('%01i ' % self.aMetricoProp09PrimerosRetornosVeget[metrX, metrY])
                if not self.aFiles['MetricoProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['MetricoProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)].write('\n')
                if not self.aFiles['MetricoProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['MetricoProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)].write('\n')
                if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                    if not self.aFiles['MetricoProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['MetricoProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)].write('\n')
                    if not self.aFiles['MetricoProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['MetricoProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)].write('\n')
            if not self.aFiles['MetricoProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                self.aFiles['MetricoProp09TodosLosRetornosSuelo_{}'.format(lasOrigRecl)].close()
            if not self.aFiles['MetricoProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                self.aFiles['MetricoProp09TodosLosRetornosVeget_{}'.format(lasOrigRecl)].close()
            if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                if not self.aFiles['MetricoProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['MetricoProp09PrimerosRetornosSuelo_{}'.format(lasOrigRecl)].close()
                if not self.aFiles['MetricoProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['MetricoProp09PrimerosRetornosVeget_{}'.format(lasOrigRecl)].close()

        if GLO.GLBLgrabarMetricoClasesEdificio:  # PointClass/Orig/01mCell/Edificio/
            for metrY in reversed(range(self.aMetricoProp09TodosLosRetornosEdificio.shape[1])):
                for metrX in range(self.aMetricoProp09TodosLosRetornosEdificio.shape[0]):
                    if not self.aFiles['MetricoProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)] is None and self.aMetricoProp09TodosLosRetornosEdificio.shape[0] > 1:
                        self.aFiles['MetricoProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)].write('%01i ' % self.aMetricoProp09TodosLosRetornosEdificio[metrX, metrY])
                    if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                        if not self.aFiles['MetricoProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)] is None and self.aMetricoProp09PrimerosRetornosEdificio.shape[0] > 1:
                            self.aFiles['MetricoProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)].write('%01i ' % self.aMetricoProp09PrimerosRetornosEdificio[metrX, metrY])
                if not self.aFiles['MetricoProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['MetricoProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)].write('\n')
                if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                    if not self.aFiles['MetricoProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['MetricoProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)].write('\n')
            if not self.aFiles['MetricoProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                self.aFiles['MetricoProp09TodosLosRetornosEdificio_{}'.format(lasOrigRecl)].close()
            if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                if not self.aFiles['MetricoProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['MetricoProp09PrimerosRetornosEdificio_{}'.format(lasOrigRecl)].close()

        if GLO.GLBLgrabarMetricoClasesOtros:  # PointClass/Orig/01mCell/Otros/
            for metrY in reversed(range(self.aMetricoProp09TodosLosRetornosOtros.shape[1])):
                for metrX in range(self.aMetricoProp09TodosLosRetornosOtros.shape[0]):
                    if not self.aFiles['MetricoProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)] is None and self.aMetricoProp09TodosLosRetornosOtros.shape[0] > 1:
                        self.aFiles['MetricoProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)].write('%01i ' % self.aMetricoProp09TodosLosRetornosOtros[metrX, metrY])
                    if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                        if not self.aFiles['MetricoProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)] is None and self.aMetricoProp09PrimerosRetornosOtros.shape[0] > 1:
                            self.aFiles['MetricoProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)].write('%01i ' % self.aMetricoProp09PrimerosRetornosOtros[metrX, metrY])
                if not self.aFiles['MetricoProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['MetricoProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)].write('\n')
                if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                    if not self.aFiles['MetricoProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                        self.aFiles['MetricoProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)].write('\n')
            if not self.aFiles['MetricoProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                self.aFiles['MetricoProp09TodosLosRetornosOtros_{}'.format(lasOrigRecl)].close()
            if GLO.GLBLgrabarMetricoClasesConPrimerosRetornos:
                if not self.aFiles['MetricoProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)] is None:
                    self.aFiles['MetricoProp09PrimerosRetornosOtros_{}'.format(lasOrigRecl)].close()


    # ==========================================================================
    def guardarMiscelaneaVuelta0(self):
        for nY in reversed(range(self.nCeldasY)):
            for nX in range(self.nCeldasX):
                # rawTime medio por celda
                if GLO.GLBLgrabarPropiedadTime:
                    if not self.aFiles['rawTime'] is None and self.aCeldasRawTime.shape[0] > 1:
                        if self.aCeldasNumPuntosTlrTlcTlpOk[nX, nY] != 0:
                            self.aFiles['rawTime'].write(str(float(self.aCeldasRawTime[nX, nY]) / self.aCeldasNumPuntosTlrTlcTlpOk[nX, nY]) + ' ')
                        else:
                            self.aFiles['rawTime'].write(str(0) + ' ')

                if GLO.GLBLleerGrabarCeldasEdge:
                    # Hay algun punto de borde de escaneo (no necesito guardarlo para mas adelante)
                    if not self.aCeldasEsCeldaEdge is None and not self.aFiles['scanEdge'] is None and self.aCeldasEsCeldaEdge.shape[0] > 1:
                        self.aFiles['scanEdge'].write(str(self.aCeldasEsCeldaEdge[nX, nY]) + ' ')


    # ==========================================================================
    def guardarAgua(self):
        # convolLasClassLandCover/Agua/
        if not self.aFiles['CeldasMasasDeAgua'] is None and self.aCeldasMasasDeAgua.shape[0] > 1:
            myClassArray = getattr(self, 'aCeldasMasasDeAgua', None)
            for nY in range(self.nCeldasY - 1, 0 - 1, -1):
                for nX in range(self.nCeldasX):
                    if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                        nX >= self.aCeldasMasasDeAgua.shape[0]
                        or nY >= self.aCeldasMasasDeAgua.shape[1]
                    ):
                        continue
                    self.aFiles['CeldasMasasDeAgua'].write(str(self.aCeldasMasasDeAgua[nX, nY]) + ' ')
                self.aFiles['CeldasMasasDeAgua'].write('\n')
            self.aFiles['CeldasMasasDeAgua'].close()


    # ==========================================================================
    def guardarCalidadTopografica(self, etapa, nTPini, nTPfin, cTP):
        # CalidadTopoAjuste/Suelo/
        # CalidadTopoAjuste/Basal/
        # CalidadTopoAjuste/Cielo/

        # etapas: '0PreInterUrb', '1PostInterpol'
        # nFase 0: etapa 0 o 1
        # nFase 1: etapa 2
        nFase = int(round((etapa - 0.1) / 2, 0))
        # No controlo los planos Major y Global
        calcularMdx = [GLO.GLBLcalcularMds, GLO.GLBLcalcularMdb, GLO.GLBLcalcularMdc]
        for nTP in range(nTPini, nTPfin):
            # cTP es una variable global
            tipoPlano = cTP[nTP]
            if calcularMdx[nTP]:
                myClassArray = getattr(self, 'aCeldasNumDisrupciones', None)
                print('Plano', tipoPlano, 'Etapa', etapa, '\tclindat-> fichero: plano%s_NumDisrupciones%s' % (tipoPlano, etapa))
                if (
                    not myClassArray is None
                    and isinstance(myClassArray, np.ndarray) 
                    and self.aCeldasNumDisrupciones.shape[0] > 1
                    and (
                        'plano%s_NumDisrupciones%i' % (tipoPlano, nFase) in self.aFiles.keys()
                        and not self.aFiles['plano%s_NumDisrupciones%i' % (tipoPlano, nFase)] is None
                    )
                ):
                    for nY in range(self.nCeldasY - 1, 0 - 1, -1):
                        for nX in range(self.nCeldasX):
                            if (
                                nX >= self.aCeldasNumDisrupciones.shape[0]
                                or nY >= self.aCeldasNumDisrupciones.shape[1]
                            ):
                                continue
                            # Solo considero borde de tejado si numAristasDisruptoras + numVerticesDisruptores (self.aCeldasNumDisrupciones[nX, nY, nTP, nFase]) > GLO.GLBLverticesDisruptoresAdmisibles
                            ##if numAristasDisruptoras + numVerticesDisruptores > GLO.GLBLverticesDisruptoresAdmisibles:
                            if self.aCeldasNumDisrupciones[nX, nY, nTP, nFase] > GLO.GLBLverticesDisruptoresAdmisibles:
                                self.aFiles['plano%s_NumDisrupciones%i' % (tipoPlano, nFase)].write(str(self.aCeldasNumDisrupciones[nX, nY, nTP, nFase]) + ' ')
                                ##self.aFiles['plano%s_NumDisrupciones%i' % (tipoPlano, nFase)].write(str(numAristasDisruptoras + numVerticesDisruptores) + ' ')
                            else:
                                self.aFiles['plano%s_NumDisrupciones%i' % (tipoPlano, nFase)].write(str(GLO.GLBLnoData) + ' ')
                        self.aFiles['plano%s_NumDisrupciones%i' % (tipoPlano, nFase)].write('\n')
                    self.aFiles['plano%s_NumDisrupciones%i' % (tipoPlano, nFase)].close()
                else:
                    print('\tclindat-> Plano', tipoPlano, 'Etapa', etapa, 'No se graba porque:')
                    print('\t\t-> myClassArray es None->', myClassArray is None)
                    if not myClassArray is None and isinstance(myClassArray, np.ndarray):
                        print('\t\t-> myClassArray.shape->', self.aCeldasConAjusteNoFiable.shape)
                    print('\t\t-> plano%s_NumDisrupciones%i' % (tipoPlano, nFase), ' Esta en aFiles->', 'plano%s_NumDisrupciones%i' % (tipoPlano, nFase) in self.aFiles.keys())
                    if 'plano%s_NumDisrupciones%i' % (tipoPlano, nFase) in self.aFiles.keys():
                        print('\t\t-> plano%s_NumDisrupciones%i' % (tipoPlano, nFase), ' es None->', self.aFiles['plano%s_NumDisrupciones%i' % (tipoPlano, nFase)] is None)


    # ==========================================================================
    def guardarCalidadDelAjuste(self, etapa, nTPini, nTPfin, cTP):
        # CalidadTopoAjuste/Suelo/
        # CalidadTopoAjuste/Basal/
        # CalidadTopoAjuste/Cielo/

        # No controlo los planos Major y Global
        if etapa == 0:
            causaNoFiabilidad = 'PorCalidadDelAjuste'
        elif etapa == 1:
            causaNoFiabilidad = 'PorCausasPte1'
        elif etapa == 2:
            causaNoFiabilidad = 'PorCausasPte2'

        calcularMdx = [GLO.GLBLcalcularMds, GLO.GLBLcalcularMdb, GLO.GLBLcalcularMdc]
        print('\tclindat-> aCeldasConAjusteNoFiable.shape:', self.aCeldasConAjusteNoFiable.shape)
        print('\tclindat-> cTP:', cTP)
        print('\tclindat-> nTPini, nTPfin:', nTPini, nTPfin)
        for nTP in range(nTPini, nTPfin):
            tipoPlano = cTP[nTP]
            if calcularMdx[nTP]:
                print('\tclindat-> Plano', tipoPlano, 'Etapa', etapa, '-> plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad))
                myClassArray = getattr(self, 'aCeldasConAjusteNoFiable', None)
                if (
                    not myClassArray is None
                    and isinstance(myClassArray, np.ndarray) 
                    and self.aCeldasConAjusteNoFiable.shape[0] > 1
                    and (
                        'plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad) in self.aFiles.keys()
                        and not self.aFiles['plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad)] is None
                    )
                ):
                    for nY in range(self.nCeldasY - 1, 0 - 1, -1):
                        for nX in range(self.nCeldasX):
                            if (
                                nX >= self.aCeldasConAjusteNoFiable.shape[0]
                                or nY >= self.aCeldasConAjusteNoFiable.shape[1]
                            ):
                                continue
                            # Esta info tb la puedo obtener de self.consultarFiabilidad{nX, nY, nTP, (...) nFase, 0}
                            # El array aCeldasConAjusteNoFiable[] lo obtengo en clidnv3.controlarCalidadDelAjuste{}
                            celdaNoFiableEnElAjuste = self.aCeldasConAjusteNoFiable[nX, nY, nTP]
                            if celdaNoFiableEnElAjuste != 0:
                                codigoInvalidezDelAjuste = celdaNoFiableEnElAjuste
                                if celdaNoFiableEnElAjuste == 4:
                                    # motivo = 'hayPuntosSumergidos'
                                    miCeldaCoeficientesMdx = clidnaux.asignarCoeficientesMdxPorTipoPlanoXY(
                                        nX,
                                        nY,
                                        nTP,
                                        self.aCeldasCoeficientesMds,
                                        self.aCeldasCoeficientesMdb_,
                                        self.aCeldasCoeficientesMdc_,
                                        self.aCeldasCoeficientesMdm,
                                    )
                                    errorResidualMasNegativo = miCeldaCoeficientesMdx[4]
                                else:
                                    errorResidualMasNegativo = GLO.GLBLnoData
                            else:
                                codigoInvalidezDelAjuste = GLO.GLBLnoData
                                errorResidualMasNegativo = GLO.GLBLnoData
                            # El plano******_NoFiable_0EnElAjuste es un poco redundante con el 1. Lo guardo para facilitar visualizacion
                            if not self.aFiles['plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad)] is None:
                                self.aFiles['plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad)].write(str(codigoInvalidezDelAjuste) + ' ')
                            if not self.aFiles['plano%s_ConPtosSumergidos' % tipoPlano] is None:
                                self.aFiles['plano%s_ConPtosSumergidos' % tipoPlano].write(str(errorResidualMasNegativo) + ' ')
                        if not self.aFiles['plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad)] is None:
                            self.aFiles['plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad)].write('\n')
                        if not self.aFiles['plano%s_ConPtosSumergidos' % tipoPlano] is None:
                            self.aFiles['plano%s_ConPtosSumergidos' % tipoPlano].write('\n')
                    if not self.aFiles['plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad)] is None:
                        self.aFiles['plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad)].close()
                    if not self.aFiles['plano%s_ConPtosSumergidos' % tipoPlano] is None:
                        self.aFiles['plano%s_ConPtosSumergidos' % tipoPlano].close()
                else:
                    print('\tclindat-> Plano', tipoPlano, 'Etapa', etapa, 'No se graba porque:')
                    print('\t\t-> myClassArray es None->', myClassArray is None)
                    if not myClassArray is None and isinstance(myClassArray, np.ndarray):
                        print('\t\t-> myClassArray.shape->', self.aCeldasConAjusteNoFiable.shape)
                    print('\t\t-> plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad), ' Esta en aFiles->', 'plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad) in self.aFiles.keys())
                    if 'plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad) in self.aFiles.keys():
                        print('\t\t-> plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad), ' es None->', self.aFiles['plano%s_NoFiable_%s' % (tipoPlano, causaNoFiabilidad)] is None)


    # ==========================================================================
    def guardarAjustesMds(self):
        myClassArray = getattr(self, 'aCeldasCoeficientesMds', None)
        for nY in reversed(range(self.nCeldasY)):
            for nX in range(self.nCeldasX):
                if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                    nX >= self.aCeldasCoeficientesMds.shape[0]
                    or nY >= self.aCeldasCoeficientesMds.shape[1]
                ):
                    continue
                if self.aCeldasAjustableMds[nX, nY] and self.aCeldasCoeficientesMds[nX, nY, 0] != -9999:
                    if not self.aFiles['planoSuelo_intercept'] is None and self.aCeldasCoeficientesMds.shape[0] > 1:
                        self.aFiles['planoSuelo_intercept'].write('%07.02f' % round(self.aCeldasCoeficientesMds[nX, nY, 0], 2) + ' ')
                    if GLO.GLBLgrabarCoeficientesXY:
                        if not self.aFiles['planoSuelo_coefX'] is None and self.aCeldasCoeficientesMds.shape[0] > 1:
                            self.aFiles['planoSuelo_coefX'].write(str(round(self.aCeldasCoeficientesMds[nX, nY, 1], 3)) + ' ')
                        if not self.aFiles['planoSuelo_coefY'] is None and self.aCeldasCoeficientesMds.shape[0] > 1:
                            self.aFiles['planoSuelo_coefY'].write(str(round(self.aCeldasCoeficientesMds[nX, nY, 2], 3)) + ' ')
                    if GLO.GLBLgrabarEcmr:
                        if not self.aFiles['planoSuelo_Ecmr'] is None and self.aCeldasCoeficientesMds.shape[0] > 1:
                            self.aFiles['planoSuelo_Ecmr'].write('%05.02f' % round(self.aCeldasCoeficientesMds[nX, nY, 3], 2) + ' ')
                else:
                    # self.anotaCeldasConPocosPuntosSueloConNumba(nX, nY, llamadoDesde='Mds')
                    if not self.aFiles['planoSuelo_intercept'] is None:
                        self.aFiles['planoSuelo_intercept'].write('%05i ' % GLO.GLBLnoData)
                    if GLO.GLBLgrabarCoeficientesXY:
                        if not self.aFiles['planoSuelo_coefX'] is None:
                            self.aFiles['planoSuelo_coefX'].write('%05i ' % GLO.GLBLnoData)
                        if not self.aFiles['planoSuelo_coefY'] is None:
                            self.aFiles['planoSuelo_coefY'].write('%05i ' % GLO.GLBLnoData)
                    if GLO.GLBLgrabarEcmr:
                        if not self.aFiles['planoSuelo_Ecmr'] is None:
                            self.aFiles['planoSuelo_Ecmr'].write('%05i ' % GLO.GLBLnoData)
            if not self.aFiles['planoSuelo_intercept'] is None:
                self.aFiles['planoSuelo_intercept'].write('\n')
            if GLO.GLBLgrabarCoeficientesXY:
                if not self.aFiles['planoSuelo_coefX'] is None:
                    self.aFiles['planoSuelo_coefX'].write('\n')
                if not self.aFiles['planoSuelo_coefY'] is None:
                    self.aFiles['planoSuelo_coefY'].write('\n')
            if GLO.GLBLgrabarEcmr:
                if not self.aFiles['planoSuelo_Ecmr'] is None:
                    self.aFiles['planoSuelo_Ecmr'].write('\n')
        if not self.aFiles['planoSuelo_intercept'] is None:
            self.aFiles['planoSuelo_intercept'].close()
        if GLO.GLBLgrabarCoeficientesXY:
            if not self.aFiles['planoSuelo_coefX'] is None:
                self.aFiles['planoSuelo_coefX'].close()
            if not self.aFiles['planoSuelo_coefY'] is None:
                self.aFiles['planoSuelo_coefY'].close()
        if GLO.GLBLgrabarEcmr:
            if not self.aFiles['planoSuelo_Ecmr'] is None:
                self.aFiles['planoSuelo_Ecmr'].close()


    # ==========================================================================
    # if GLO.GLBLcalcularMdg or GLO.GLBLcalcularMdp:
    #    if GLO.GLBLgrabarMdgAjusteCelda:
    def guardarAjustesMdg(self):
        myClassArray = getattr(self, 'aCeldasCoeficientesMdg', None)
        for nY in reversed(range(self.nCeldasY)):
            for nX in range(self.nCeldasX):
                if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                    nX >= self.aCeldasCoeficientesMdg.shape[0]
                    or nY >= self.aCeldasCoeficientesMdg.shape[1]
                ):
                    continue
                if self.aCeldasCoeficientesMdg[nX, nY, 0] != GLO.GLBLnoData and self.aCeldasCoeficientesMdg[nX, nY, 3] != -1:
                    if GLO.GLBLgrabarInterceptMdg:
                        if not self.aFiles['CeldasMdgCota'] is None and self.aCeldasCoeficientesMdg.shape[0] > 1:
                            self.aFiles['CeldasMdgCota'].write('%07.02f' % round(self.aCeldasCoeficientesMdg[nX, nY, 0], 2) + ' ')
                    if GLO.GLBLgrabarCoeficientesXY:
                        if not self.aFiles['CeldasMdgPteX'] is None and self.aCeldasCoeficientesMdg.shape[0] > 1:
                            self.aFiles['CeldasMdgPteX'].write(str(round(self.aCeldasCoeficientesMdg[nX, nY, 1], 3)) + ' ')
                        if not self.aFiles['CeldasMdgPteY'] is None and self.aCeldasCoeficientesMdg.shape[0] > 1:
                            self.aFiles['CeldasMdgPteY'].write(str(round(self.aCeldasCoeficientesMdg[nX, nY, 2], 3)) + ' ')
                    if GLO.GLBLgrabarEcmrMdg:
                        if not self.aFiles['CeldasMdgEcmr'] is None and self.aCeldasCoeficientesMdg.shape[0] > 1:
                            self.aFiles['CeldasMdgEcmr'].write('%05.02f' % round(self.aCeldasCoeficientesMdg[nX, nY, 3], 2) + ' ')
                        if not self.aFiles['CeldasMdgUnderPoint'] is None and self.aCeldasCoeficientesMdg.shape[0] > 1:
                            self.aFiles['CeldasMdgUnderPoint'].write('%06.02f' % round(self.aCeldasCoeficientesMdg[nX, nY, 4], 2) + ' ')
                else:
                    # anotaCeldasConPocosPuntosGlobalesConNumba
                    if GLO.GLBLgrabarInterceptMdg:
                        if not self.aFiles['CeldasMdgCota'] is None:
                            self.aFiles['CeldasMdgCota'].write('%06.00f ' % GLO.GLBLnoData)
                    if GLO.GLBLgrabarCoeficientesXY:
                        if not self.aFiles['CeldasMdgPteX'] is None:
                            self.aFiles['CeldasMdgPteX'].write('%06.00f ' % GLO.GLBLnoData)
                        if not self.aFiles['CeldasMdgPteY'] is None:
                            self.aFiles['CeldasMdgPteY'].write('%06.00f ' % GLO.GLBLnoData)
                    if GLO.GLBLgrabarEcmrMdg:
                        if not self.aFiles['CeldasMdgEcmr'] is None:
                            self.aFiles['CeldasMdgEcmr'].write('%05.00f ' % GLO.GLBLnoData)
                        if not self.aFiles['CeldasMdgUnderPoint'] is None:
                            self.aFiles['CeldasMdgUnderPoint'].write('%06.00f ' % GLO.GLBLnoData)
            if GLO.GLBLgrabarInterceptMdg:
                if not self.aFiles['CeldasMdgCota'] is None:
                    self.aFiles['CeldasMdgCota'].write('\n')
            if GLO.GLBLgrabarCoeficientesXY:
                if not self.aFiles['CeldasMdgPteX'] is None:
                    self.aFiles['CeldasMdgPteX'].write('\n')
                if not self.aFiles['CeldasMdgPteY'] is None:
                    self.aFiles['CeldasMdgPteY'].write('\n')
            if GLO.GLBLgrabarEcmrMdg:
                if not self.aFiles['CeldasMdgEcmr'] is None:
                    self.aFiles['CeldasMdgEcmr'].write('\n')
                if not self.aFiles['CeldasMdgUnderPoint'] is None:
                    self.aFiles['CeldasMdgUnderPoint'].write('\n')
        if GLO.GLBLgrabarInterceptMdg:
            if not self.aFiles['CeldasMdgCota'] is None:
                self.aFiles['CeldasMdgCota'].close()
        if GLO.GLBLgrabarCoeficientesXY:
            if not self.aFiles['CeldasMdgPteX'] is None:
                self.aFiles['CeldasMdgPteX'].close()
            if not self.aFiles['CeldasMdgPteY'] is None:
                self.aFiles['CeldasMdgPteY'].close()
        if GLO.GLBLgrabarEcmrMdg:
            if not self.aFiles['CeldasMdgEcmr'] is None:
                self.aFiles['CeldasMdgEcmr'].close()
            if not self.aFiles['CeldasMdgUnderPoint'] is None:
                self.aFiles['CeldasMdgUnderPoint'].close()


    # ==========================================================================
    def guardarAjustesMdxPreInterpol(self):
        # nTP en aCeldasCoeficientesMdxAll[]
        #  nTP 0 -> 'Basal', GLO.GLBLcalcularMdb, GLO.GLBLgrabarMdbPreInterpol
        #  nTP 1 -> 'Cielo', GLO.GLBLcalcularMdc, GLO.GLBLgrabarMdc
        #  nTP 2 -> 'Major', GLO.GLBLcalcularMdm, GLO.GLBLgrabarMdm
        nombreTP = ['Basal', 'Cielo', 'Major']
        guardaTP = [
            GLO.GLBLcalcularMdb and GLO.GLBLgrabarMdbPreInterpol,
            GLO.GLBLcalcularMdc and GLO.GLBLgrabarMdc,
            GLO.GLBLcalcularMdm and GLO.GLBLgrabarMdm
        ]

        myClassArray = getattr(self, 'aCeldasCoeficientesMdxAll', None)
        if myClassArray is None or not isinstance(myClassArray, np.ndarray):
            print('cliddata-> ATENCION: revisar error en aCeldasCoeficientesMdxAll')
            print('cliddata-> Chequeando aCeldasCoeficientesMdxAll:', myClassArray)
            return
        # tipoPlano == 'Basal'
        for nTP in range(3):
            nombrePlano =  nombreTP[nTP]
            guardaPlano =  guardaTP[nTP]
            if guardaPlano:
                print('cliddata-> Calcular+Guardar plano {}: {}'.format(nombrePlano, guardaPlano))
                # if 'plano{}_intercept'.format(nombrePlano) in self.aFiles.keys():
                #     print('\t->', self.aFiles['plano{}_intercept'.format(nombrePlano)])
                # if GLO.GLBLgrabarCoeficientesXY and 'plano{}_coefX'.format(nombrePlano) in self.aFiles.keys():
                #     print('\t->', self.aFiles['plano{}_coefX'.format(nombrePlano)])

                for nY in reversed(range(self.nCeldasY)):
                    for nX in range(self.nCeldasX):
                        if (
                            nX >= self.aCeldasCoeficientesMdxAll.shape[0]
                            or nY >= self.aCeldasCoeficientesMdxAll.shape[1]
                        ):
                            continue
                        # ajusteElegido = self.ajusteBasalElegido[nX, nY]
                        if self.aCeldasCoeficientesMdxAll[nX, nY, nTP, 3] != -1:
                            miIntercept = self.aCeldasCoeficientesMdxAll[nX, nY, nTP, 0]
                            miCoefX = self.aCeldasCoeficientesMdxAll[nX, nY, nTP, 1]
                            miCoefY = self.aCeldasCoeficientesMdxAll[nX, nY, nTP, 2]
                            miEcmr = self.aCeldasCoeficientesMdxAll[nX, nY, nTP, 3]
                            miEcmr_inicial = self.aCeldasCoeficientesMdxAll[nX, nY, nTP, 5]
                        else:
                            miIntercept = GLO.GLBLnoData
                            miCoefX = GLO.GLBLnoData
                            miCoefY = GLO.GLBLnoData
                            miEcmr = -1
                            miEcmr_inicial = -1

                        if 'plano{}_intercept'.format(nombrePlano) in self.aFiles.keys() and not self.aFiles['plano{}_intercept'.format(nombrePlano)] is None:
                            self.aFiles['plano{}_intercept'.format(nombrePlano)].write('%07.02f ' % round(miIntercept, 2))
                        if GLO.GLBLgrabarCoeficientesXY:
                            if 'plano{}_coefX'.format(nombrePlano) in self.aFiles.keys() and not self.aFiles['plano{}_coefX'.format(nombrePlano)] is None:
                                self.aFiles['plano{}_coefX'.format(nombrePlano)].write('%06.03f ' % round(miCoefX, 3))
                            if 'plano{}_coefY'.format(nombrePlano) in self.aFiles.keys() and not self.aFiles['plano{}_coefY'.format(nombrePlano)] is None:
                                self.aFiles['plano{}_coefY'.format(nombrePlano)].write('%06.03f ' % round(miCoefY, 3))
                        if nombrePlano == 'Cielo':
                            if (
                                GLO.GLBLgrabarEcmrMdcInicial
                                and 'plano{}_EcmrInicial'.format(nombrePlano) in self.aFiles.keys()
                                and not self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)] is None
                            ):
                                if miEcmr_inicial > GLO.GLBLerrorResidualMedioInicialElevado:
                                    # Incluye las celdas en las que no se ha conseguido ajustar un plano porque ni el A ni el B cumplen
                                    # No incluye las celdas con pocos puntos por pasada porque en ellas no se calcula el rangoPuntosBasales
                                    self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)].write('%05.02f ' % round(miEcmr_inicial, 2))
                                else:
                                    self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)].write('%05.02f ' % GLO.GLBLnoData)
                            elif (
                                GLO.GLBLgrabarEcmrMdcFinal
                                and 'plano{}_EcmrFinal'.format(nombrePlano) in self.aFiles.keys()
                                and not self.aFiles['plano{}_EcmrFinal'.format(nombrePlano)] is None
                            ):
                                if miEcmr > GLO.GLBLerrorResidualMedioInicialElevado:
                                    # Incluye las celdas en las que no se ha conseguido ajustar un plano porque ni el A ni el B cumplen
                                    # No incluye las celdas con pocos puntos por pasada porque en ellas no se calcula el rangoPuntosBasales
                                    self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)].write('%05.02f ' % round(miEcmr, 2))
                                else:
                                    self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)].write('%05.02f ' % GLO.GLBLnoData)
                        else:
                            if (
                                GLO.GLBLgrabarEcmr
                                and 'plano{}_Ecmr'.format(nombrePlano) in self.aFiles.keys()
                                and not self.aFiles['plano{}_Ecmr'.format(nombrePlano)] is None
                            ):
                                self.aFiles['plano{}_Ecmr'.format(nombrePlano)].write('%05.02f ' % round(miEcmr, 2))


                    if (
                        'plano{}_intercept'.format(nombrePlano) in self.aFiles.keys()
                        and not self.aFiles['plano{}_intercept'.format(nombrePlano)] is None
                    ):
                        self.aFiles['plano{}_intercept'.format(nombrePlano)].write('\n')
                    if GLO.GLBLgrabarCoeficientesXY:
                        if 'plano{}_coefX'.format(nombrePlano) in self.aFiles.keys() and not self.aFiles['plano{}_coefX'.format(nombrePlano)] is None:
                            self.aFiles['plano{}_coefX'.format(nombrePlano)].write('\n')
                        if 'plano{}_coefY'.format(nombrePlano) in self.aFiles.keys() and not self.aFiles['plano{}_coefY'.format(nombrePlano)] is None:
                            self.aFiles['plano{}_coefY'.format(nombrePlano)].write('\n')
                    if nombrePlano == 'Cielo':
                        if (
                            GLO.GLBLgrabarEcmrMdcInicial
                            and 'plano{}_EcmrInicial'.format(nombrePlano) in self.aFiles.keys()
                            and not self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)] is None
                        ):
                            if (
                                GLO.GLBLgrabarEcmrMdcInicial
                                and 'plano{}_EcmrInicial'.format(nombrePlano) in self.aFiles.keys()
                                and not self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)] is None
                            ):
                                self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)].write('\n')
                            elif (
                                GLO.GLBLgrabarEcmrMdcFinal
                                and 'plano{}_EcmrFinal'.format(nombrePlano) in self.aFiles.keys()
                                and not self.aFiles['plano{}_EcmrFinal'.format(nombrePlano)] is None
                            ):
                                self.aFiles['plano{}_EcmrFinal'.format(nombrePlano)].write('\n')
                        else:
                            if (
                                GLO.GLBLgrabarEcmr
                                and 'plano{}_Ecmr'.format(nombrePlano) in self.aFiles.keys()
                                and not self.aFiles['plano{}_Ecmr'.format(nombrePlano)] is None
                            ):
                                self.aFiles['plano{}_Ecmr'.format(nombrePlano)].write('\n')
                if not self.aFiles['plano{}_intercept'.format(nombrePlano)] is None:
                    self.aFiles['plano{}_intercept'.format(nombrePlano)].close()
                if GLO.GLBLgrabarCoeficientesXY:
                    if 'plano{}_coefX'.format(nombrePlano) in self.aFiles.keys() and not self.aFiles['plano{}_coefX'.format(nombrePlano)] is None:
                        self.aFiles['plano{}_coefX'.format(nombrePlano)].close()
                    if 'plano{}_coefY'.format(nombrePlano) in self.aFiles.keys() and not self.aFiles['plano{}_coefY'.format(nombrePlano)] is None:
                        self.aFiles['plano{}_coefY'.format(nombrePlano)].close()
                if nombrePlano == 'Cielo':
                    if (
                        GLO.GLBLgrabarEcmrMdcInicial
                        and 'plano{}_EcmrInicial'.format(nombrePlano) in self.aFiles.keys()
                        and not self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)] is None
                    ):
                        if (
                            GLO.GLBLgrabarEcmrMdcInicial
                            and 'plano{}_EcmrInicial'.format(nombrePlano) in self.aFiles.keys()
                            and not self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)] is None
                        ):
                            self.aFiles['plano{}_EcmrInicial'.format(nombrePlano)].close()
                        elif (
                            GLO.GLBLgrabarEcmrMdcFinal
                            and 'plano{}_EcmrFinal'.format(nombrePlano) in self.aFiles.keys()
                            and not self.aFiles['plano{}_EcmrFinal'.format(nombrePlano)] is None
                        ):
                            self.aFiles['plano{}_EcmrFinal'.format(nombrePlano)].close()
                    else:
                        if (
                            GLO.GLBLgrabarEcmr
                            and 'plano{}_Ecmr'.format(nombrePlano) in self.aFiles.keys()
                            and not self.aFiles['plano{}_Ecmr'.format(nombrePlano)] is None
                        ):
                            self.aFiles['plano{}_Ecmr'.format(nombrePlano)].close()


    # ==========================================================================
    def guardarAjustesMdsPostInterpol(self, nInterpol):
        if nInterpol > 0:
            print('cliddata-> No se guarda el interpolado 1 (lo he deshabilitado)')
            return
        print('cliddata-> Guardando plano suelo interpolado')
        print('\t-> aCeldasCoeficientesMds.shape:', self.aCeldasCoeficientesMds.shape[0])

        if self.aCeldasCoeficientesMds.shape[0] > 1 and not self.aFiles['planoSuelo_intercept_interpolado'] is None:
            print('cliddata-> grabando planoSuelo_intercept_interpolado: {}'.format(self.aFiles['planoSuelo_intercept_interpolado']))
            for nY in range(self.aCeldasCoeficientesMds.shape[1] - 1, 0 - 1, -1):
                for nX in range(self.aCeldasCoeficientesMds.shape[0]):
                    self.aFiles['planoSuelo_intercept_interpolado'].write(str(round(self.aCeldasCoeficientesMds[nX, nY, 0], 2)) + ' ')
                self.aFiles['planoSuelo_intercept_interpolado'].write('\n')
            self.aFiles['planoSuelo_intercept_interpolado'].close()
            if GLO.GLBLgrabarCoeficientesXY:
                print('cliddata-> grabando filePlano_coefX:', self.aFiles['planoSuelo_coefX_interpolado'])
                if not self.aFiles['planoSuelo_coefX_interpolado'] is None:
                    for nY in range(self.aCeldasCoeficientesMds.shape[1] - 1, 0 - 1, -1):
                        for nX in range(self.aCeldasCoeficientesMds.shape[0]):
                            self.aFiles['planoSuelo_coefX_interpolado'].write(str(round(self.aCeldasCoeficientesMds[nX, nY, 2], 3)) + ' ')
                        self.aFiles['planoSuelo_coefX_interpolado'].write('\n')
                    self.aFiles['planoSuelo_coefX_interpolado'].close()
                print('cliddata-> grabando filePlano_coefY:', self.aFiles['planoSuelo_coefY_interpolado'])
                if not self.aFiles['planoSuelo_coefY_interpolado'] is None:
                    for nY in range(self.aCeldasCoeficientesMds.shape[1] - 1, 0 - 1, -1):
                        for nX in range(self.aCeldasCoeficientesMds.shape[0]):
                            self.aFiles['planoSuelo_coefY_interpolado'].write(str(round(self.aCeldasCoeficientesMds[nX, nY, 2], 3)) + ' ')
                        self.aFiles['planoSuelo_coefY_interpolado'].write('\n')
                    self.aFiles['planoSuelo_coefY_interpolado'].close()


    # ==========================================================================
    def guardarAjustesMdbPostInterpol(self, nInterpol):
        if nInterpol > 0:
            print('cliddata-> No se guarda el interpolado 1 (lo he deshabilitado)')
            return
        print('cliddata-> Guardando plano basal interpolado')
        print('\t-> aCeldasCoeficientesMdb_.shape:', self.aCeldasCoeficientesMdb_.shape[0])

        if self.aCeldasCoeficientesMdb_.shape[0] > 1 and not self.aFiles['planoBasal_intercept_interpolado'] is None:
            print('cliddata-> grabando planoBasal_intercept_interpolado: {}'.format(self.aFiles['planoBasal_intercept_interpolado']))
            for nY in range(self.aCeldasCoeficientesMdb_.shape[1] - 1, 0 - 1, -1):
                for nX in range(self.aCeldasCoeficientesMdb_.shape[0]):
                    self.aFiles['planoBasal_intercept_interpolado'].write(str(round(self.aCeldasCoeficientesMdb_[nX, nY, 0], 2)) + ' ')
                    if nY == 198 and nX == 2:
                        print('cliddata->', nX, nY, 'Valor guardado:', self.aCeldasCoeficientesMdb_[nX, nY, 0])
                self.aFiles['planoBasal_intercept_interpolado'].write('\n')
            self.aFiles['planoBasal_intercept_interpolado'].close()
            if GLO.GLBLgrabarCoeficientesXY:
                print('cliddata-> grabando filePlano_coefX:', self.aFiles['planoBasal_coefX_interpolado'])
                if not self.aFiles['planoBasal_coefX_interpolado'] is None:
                    for nY in range(self.aCeldasCoeficientesMdb_.shape[1] - 1, 0 - 1, -1):
                        for nX in range(self.aCeldasCoeficientesMdb_.shape[0]):
                            self.aFiles['planoBasal_coefX_interpolado'].write(str(round(self.aCeldasCoeficientesMdb_[nX, nY, 2], 3)) + ' ')
                        self.aFiles['planoBasal_coefX_interpolado'].write('\n')
                    self.aFiles['planoBasal_coefX_interpolado'].close()
                print('cliddata-> grabando filePlano_coefY:', self.aFiles['planoBasal_coefY_interpolado'])
                if not self.aFiles['planoBasal_coefY_interpolado'] is None:
                    for nY in range(self.aCeldasCoeficientesMdb_.shape[1] - 1, 0 - 1, -1):
                        for nX in range(self.aCeldasCoeficientesMdb_.shape[0]):
                            self.aFiles['planoBasal_coefY_interpolado'].write(str(round(self.aCeldasCoeficientesMdb_[nX, nY, 2], 3)) + ' ')
                        self.aFiles['planoBasal_coefY_interpolado'].write('\n')
                    self.aFiles['planoBasal_coefY_interpolado'].close()


    # ==========================================================================
    # if GLO.GLBLcalcularMdc2mConTodosLosPuntos:
    def guardarMdcSubCelda(self):
        # Guardo la cota maxima de los puntos en cada subcelda
        print('\t\t\tcliddata-> guardando Mdc subCelda')
        if not self.aFiles['SubCeldasMdcCotaMax'] is None and self.aSubCeldasMdcCotaMax.shape[0] > 1:
            for nSubY in reversed(range(self.aSubCeldasMdcCotaMax.shape[1])):
                for nSubX in range(self.aSubCeldasMdcCotaMax.shape[0]):
                    if self.aSubCeldasMdcCotaMax[nSubX, nSubY] == 0:
                        self.aFiles['SubCeldasMdcCotaMax'].write('-9999.0 ')
                    else:
                        self.aFiles['SubCeldasMdcCotaMax'].write('%07.02f ' % round(self.aSubCeldasMdcCotaMax[nSubX, nSubY], 2))
                self.aFiles['SubCeldasMdcCotaMax'].write('\n')
            self.aFiles['SubCeldasMdcCotaMax'].close()


    # ==========================================================================
    # if GLO.GLBLcalcularMdk2mConPuntosClasificados:
    def guardarMdkSubCeldaPreInterpol(self):
        # Guardo las cotas medias y minimas de los puntos clasificados 2, 9, 10, 11 en cada subcelda
        print('\t\t\tcliddata-> guardando Mdk preInterpol')
        if not self.aFiles['SubCeldasMdkCotaMed'] is None and self.aSubCeldasMdkCotaMed.shape[0] > 1:
            for nSubY in reversed(range(self.aSubCeldasMdkCotaMed.shape[1])):
                for nSubX in range(self.aSubCeldasMdkCotaMed.shape[0]):
                    self.aFiles['SubCeldasMdkCotaMed'].write('%07.02f ' % round(self.aSubCeldasMdkCotaMed[nSubX, nSubY], 2))
                self.aFiles['SubCeldasMdkCotaMed'].write('\n')
            self.aFiles['SubCeldasMdkCotaMed'].close()
        if not self.aFiles['SubCeldasMdkCotaMin'] is None and self.aSubCeldasMdkCotaMin.shape[0] > 1:
            for nSubY in reversed(range(self.aSubCeldasMdkCotaMin.shape[1])):
                for nSubX in range(self.aSubCeldasMdkCotaMin.shape[0]):
                    self.aFiles['SubCeldasMdkCotaMin'].write('%07.02f ' % round(self.aSubCeldasMdkCotaMin[nSubX, nSubY], 2))
                self.aFiles['SubCeldasMdkCotaMin'].write('\n')
            self.aFiles['SubCeldasMdkCotaMin'].close()


    # ==========================================================================
    # if GLO.GLBLcalcularMdk2mConPuntosClasificados:
    def guardarMdkSubCeldaPosInterpol(self):
        # Guardo las cotas medias y minimas de los puntos clasificados 2, 9, 10, 11 en cada subcelda
        print('\t\t\tcliddata-> guardando Mdk posInterpol')
        if not self.aFiles['SubCeldasMdkCotaItp'] is None and self.aSubCeldasMdkCotaItp.shape[0] > 1:
            for nSubY in reversed(range(self.aSubCeldasMdkCotaItp.shape[1])):
                for nSubX in range(self.aSubCeldasMdkCotaItp.shape[0]):
                    self.aFiles['SubCeldasMdkCotaItp'].write('%07.02f ' % round(self.aSubCeldasMdkCotaItp[nSubX, nSubY], 2))
                self.aFiles['SubCeldasMdkCotaItp'].write('\n')
            self.aFiles['SubCeldasMdkCotaItp'].close()



    # ==========================================================================
    def guardarAjustesMdbSubCelda(self, prePostInterpol):
        SubCeldasMdbPrePostInterpol = 'SubCeldasMdb{}Interpol'.format(prePostInterpol)
        #aSubCeldasMdbPrePostInterpol = 'aSubCeldasMdb{}Interpol'.format(prePostInterpol)
        aSubCeldasMdbPrePostInterpol = 'aSubCeldasMdb'

        if prePostInterpol != 'Pre' and prePostInterpol != 'Post':
            print('clindat-> ATENCION: revisar el argumento prePostInterpol:', prePostInterpol)
            return

        # Mde/02mCell/Basal/
        if hasattr(self, aSubCeldasMdbPrePostInterpol) and not self.aSubCeldasMdb is None:
            print('clindat-> Se va a guardar en asc el array SubCeldasMdb:', self.aFiles[SubCeldasMdbPrePostInterpol])
            if not self.aFiles[SubCeldasMdbPrePostInterpol] is None and self.aSubCeldasMdb.shape[0] > 1:
                for nSubY in reversed(range(self.aSubCeldasMdb.shape[1])):
                    for nSubX in range(self.aSubCeldasMdb.shape[0]):
                        # if nSubX >= 112*5 and nSubX < 114*5 and nSubY >= 5*5 and nSubY < 6*5:
                        #     print('cliddata-> Grabacion de aSubCeldasMdb:', nSubX, nSubY, '->', self.aSubCeldasMdb[nSubX, nSubY])
                        if self.aSubCeldasMdb[nSubX, nSubY] != GLO.GLBLnoData:
                            self.aFiles[SubCeldasMdbPrePostInterpol].write('%07.02f' % round(self.aSubCeldasMdb[nSubX, nSubY], 2) + ' ')
                        else:
                            self.aFiles[SubCeldasMdbPrePostInterpol].write('%07.01f ' % GLO.GLBLnoData)
                    self.aFiles[SubCeldasMdbPrePostInterpol].write('\n')
                self.aFiles[SubCeldasMdbPrePostInterpol].close()
            else:
                print('clindat-> Revisar esto-> SubCeldasMdb:', self.aFiles[SubCeldasMdbPrePostInterpol])
                print('\tEl fichero SubCeldasMdb ya existe. GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb'.format(GLO.GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb))
        else:
            print('clindat-> No se dispone del array SubCeldasMdb:', self.aFiles[SubCeldasMdbPrePostInterpol])
            print('\tPuede deberse a que se han leido un el fichero ...clidV2a9.npz antiguo y no incluye este array')

    # ==========================================================================
    def guardarAjustesMdpConvol(self):
        # print('\t\taSubCeldasMdfCotaConvol', self.aSubCeldasMdfCotaConvol.shape)
        # print(self.aSubCeldasMdfCotaConvol)
        if GLO.GLBLcalcularSubCeldas:
            if GLO.GLBLgrabarMdfCotaSubcelda:  # Mde/02mCell/Final/
                if not self.aFiles['SubCeldasMdfCotaConvol'] is None and self.aSubCeldasMdfCotaConvol.shape[0] > 1:
                    for nY in reversed(range(self.aSubCeldasMdfCotaConvol.shape[1])):
                        for nX in range(self.aSubCeldasMdfCotaConvol.shape[0]):
                            if (
                                self.aSubCeldasMdfCotaConvol[nX, nY] != 0
                                and self.aSubCeldasMdfCotaConvol[nX, nY] != -1
                                and self.aSubCeldasMdfCotaConvol[nX, nY] != 9999
                                and self.aSubCeldasMdfCotaConvol[nX, nY] != GLO.GLBLnoData
                            ):
                                self.aFiles['SubCeldasMdfCotaConvol'].write('%07.02f' % round(self.aSubCeldasMdfCotaConvol[nX, nY], 2) + ' ')
                            else:
                                self.aFiles['SubCeldasMdfCotaConvol'].write('%07.01f ' % GLO.GLBLnoData)
                        self.aFiles['SubCeldasMdfCotaConvol'].write('\n')
                    self.aFiles['SubCeldasMdfCotaConvol'].close()
                else:
                    print('clindat-> Revisar esto-> SubCeldasMdfCotaConvol:', self.aFiles['SubCeldasMdfCotaConvol'])
                    print('\tEl fichero SubCeldasMdfCotaConvol ya existe. GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb'.format(GLO.GLBLmantenerAscGuardadosPreviamenteSiMasDe1Kb))

            if GLO.GLBLgrabarMdfCotaSubceldaTransitoria:  # Mde/02mCell/Final/
                if not self.aFiles['SubCeldasMdfCotaTransitoriaConvol'] is None and self.aSubCeldasMdfCotaTransitoriaConvol.shape[0] > 1:
                    for nY in reversed(range(self.aSubCeldasMdfCotaTransitoriaConvol.shape[1])):
                        for nX in range(self.aSubCeldasMdfCotaTransitoriaConvol.shape[0]):
                            if (
                                self.aSubCeldasMdfCotaTransitoriaConvol[nX, nY] != 0
                                and self.aSubCeldasMdfCotaTransitoriaConvol[nX, nY] != -1
                                and self.aSubCeldasMdfCotaTransitoriaConvol[nX, nY] != 9999
                                and self.aSubCeldasMdfCotaTransitoriaConvol[nX, nY] != GLO.GLBLnoData
                            ):
                                self.aFiles['SubCeldasMdfCotaTransitoriaConvol'].write('%07.02f' % round(self.aSubCeldasMdfCotaTransitoriaConvol[nX, nY], 2) + ' ')
                            else:
                                self.aFiles['SubCeldasMdfCotaTransitoriaConvol'].write('%07.01f ' % GLO.GLBLnoData)
                        self.aFiles['SubCeldasMdfCotaTransitoriaConvol'].write('\n')
                    self.aFiles['SubCeldasMdfCotaTransitoriaConvol'].close()


    # ==========================================================================
    def guardarAjustesMdpConual(self):
        # print('\t\taSubCeldasMdfCotaConual', self.aSubCeldasMdfCotaConual.shape)
        # print(self.aSubCeldasMdfCotaConual)
        if GLO.GLBLcalcularSubCeldas:
            if GLO.GLBLgrabarMdfCotaSubcelda:  # Mde/02mCell/Final/
                if not self.aFiles['SubCeldasMdfCotaConual'] is None and self.aSubCeldasMdfCotaConual.shape[0] > 1:
                    for nY in reversed(range(self.aSubCeldasMdfCotaConual.shape[1])):
                        for nX in range(self.aSubCeldasMdfCotaConual.shape[0]):
                            if (
                                self.aSubCeldasMdfCotaConual[nX, nY] != 0
                                and self.aSubCeldasMdfCotaConual[nX, nY] != -1
                                and self.aSubCeldasMdfCotaConual[nX, nY] != 9999
                                and self.aSubCeldasMdfCotaConual[nX, nY] != GLO.GLBLnoData
                            ):
                                self.aFiles['SubCeldasMdfCotaConual'].write('%07.02f' % round(self.aSubCeldasMdfCotaConual[nX, nY], 2) + ' ')
                            else:
                                self.aFiles['SubCeldasMdfCotaConual'].write('%07.01f ' % GLO.GLBLnoData)
                        self.aFiles['SubCeldasMdfCotaConual'].write('\n')
                    self.aFiles['SubCeldasMdfCotaConual'].close()

            if GLO.GLBLgrabarMdfCotaSubceldaTransitoria:  # Mde/02mCell/Final/
                if not self.aFiles['SubCeldasMdfCotaTransitoriaConual'] is None and self.aSubCeldasMdfCotaTransitoriaConual.shape[0] > 1:
                    for nY in reversed(range(self.aSubCeldasMdfCotaTransitoriaConual.shape[1])):
                        for nX in range(self.aSubCeldasMdfCotaTransitoriaConual.shape[0]):
                            if (
                                self.aSubCeldasMdfCotaTransitoriaConual[nX, nY] != 0
                                and self.aSubCeldasMdfCotaTransitoriaConual[nX, nY] != -1
                                and self.aSubCeldasMdfCotaTransitoriaConual[nX, nY] != 9999
                                and self.aSubCeldasMdfCotaTransitoriaConual[nX, nY] != GLO.GLBLnoData
                            ):
                                self.aFiles['SubCeldasMdfCotaTransitoriaConual'].write('%07.02f' % round(self.aSubCeldasMdfCotaTransitoriaConual[nX, nY], 2) + ' ')
                            else:
                                self.aFiles['SubCeldasMdfCotaTransitoriaConual'].write('%07.01f ' % GLO.GLBLnoData)
                        self.aFiles['SubCeldasMdfCotaTransitoriaConual'].write('\n')
                    self.aFiles['SubCeldasMdfCotaTransitoriaConual'].close()


    # ==========================================================================
    def guardarAjustesMdpManual(self, usarModeloConvolucional=False):
        if GLO.GLBLgrabarMdpAjusteCelda:  # Mde/02mCell/Pleno/
            clidaux.printMsg('\t\t-> cliddata-> Guardando CeldasMdpCota, CeldasMdpPteX, CeldasMdpPteY, CeldasMdpEcmr, CeldasMdpOctn')
            myClassArray = getattr(self, 'aCeldasMdpAjuste', None)
            for nY in reversed(range(self.nCeldasY)):
                for nX in range(self.nCeldasX):
                    if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                        nX >= self.aCeldasMdpAjuste.shape[0]
                        or nY >= self.aCeldasMdpAjuste.shape[1]
                    ):
                        continue
                    if (
                        self.aCeldasMdpAjuste[nX, nY, 0] != 0
                        and self.aCeldasMdpAjuste[nX, nY, 0] != 9999
                        and self.aCeldasMdpAjuste[nX, nY, 0] != GLO.GLBLnoData
                        and self.aCeldasMdpAjuste[nX, nY, 5] != -1
                    ):
                        if not self.aFiles['CeldasMdpCota'] is None and self.aCeldasMdpAjuste.shape[0] > 1:
                            self.aFiles['CeldasMdpCota'].write('%07.02f' % round(self.aCeldasMdpAjuste[nX, nY, 0], 2) + ' ')
                        if GLO.GLBLgrabarCoeficientesXYMdp:
                            if not self.aFiles['CeldasMdpPteX'] is None and self.aCeldasMdpAjuste.shape[0] > 1:
                                self.aFiles['CeldasMdpPteX'].write(str(round(self.aCeldasMdpAjuste[nX, nY, 1], 3)) + ' ')
                            if not self.aFiles['CeldasMdpPteY'] is None and self.aCeldasMdpAjuste.shape[0] > 1:
                                self.aFiles['CeldasMdpPteY'].write(str(round(self.aCeldasMdpAjuste[nX, nY, 2], 3)) + ' ')
                            # No guardo los coeficientes dextras del parabooide: self.aCeldasMdpAjuste[nX, nY, 3:5]
                        if GLO.GLBLgrabarEcmrMdp:
                            if not self.aFiles['CeldasMdpEcmr'] is None and self.aCeldasMdpAjuste.shape[0] > 1:
                                self.aFiles['CeldasMdpEcmr'].write('%05.02f' % round(self.aCeldasMdpAjuste[nX, nY, 5], 2) + ' ')
                            if not self.aFiles['CeldasMdpOctn'] is None and self.aCeldasMdpAjuste.shape[0] > 1:
                                self.aFiles['CeldasMdpOctn'].write('%02i' % int(self.aCeldasMdpAjuste[nX, nY, 6]) + ' ')
                    else:
                        if not self.aFiles['CeldasMdpCota'] is None:
                            self.aFiles['CeldasMdpCota'].write('%07.01f ' % GLO.GLBLnoData)
                        if GLO.GLBLgrabarCoeficientesXYMdp:
                            if not self.aFiles['CeldasMdpPteX'] is None:
                                self.aFiles['CeldasMdpPteX'].write('%07.01f ' % GLO.GLBLnoData)
                            if not self.aFiles['CeldasMdpPteY'] is None:
                                self.aFiles['CeldasMdpPteY'].write('%07.01f ' % GLO.GLBLnoData)
                        if GLO.GLBLgrabarEcmrMdp:
                            if not self.aFiles['CeldasMdpEcmr'] is None:
                                self.aFiles['CeldasMdpEcmr'].write('%05.02f ' % GLO.GLBLnoData)
                            if not self.aFiles['CeldasMdpOctn'] is None:
                                self.aFiles['CeldasMdpOctn'].write('%05i ' % GLO.GLBLnoData)
                if not self.aFiles['CeldasMdpCota'] is None:
                    self.aFiles['CeldasMdpCota'].write('\n')
                if GLO.GLBLgrabarCoeficientesXYMdp:
                    if not self.aFiles['CeldasMdpPteX'] is None:
                        self.aFiles['CeldasMdpPteX'].write('\n')
                    if not self.aFiles['CeldasMdpPteY'] is None:
                        self.aFiles['CeldasMdpPteY'].write('\n')
                if GLO.GLBLgrabarEcmrMdp:
                    if not self.aFiles['CeldasMdpEcmr'] is None:
                        self.aFiles['CeldasMdpEcmr'].write('\n')
                    if not self.aFiles['CeldasMdpOctn'] is None:
                        self.aFiles['CeldasMdpOctn'].write('\n')
            if not self.aFiles['CeldasMdpCota'] is None:
                self.aFiles['CeldasMdpCota'].close()
            if GLO.GLBLgrabarCoeficientesXYMdp:
                if not self.aFiles['CeldasMdpPteX'] is None:
                    self.aFiles['CeldasMdpPteX'].close()
                if not self.aFiles['CeldasMdpPteY'] is None:
                    self.aFiles['CeldasMdpPteY'].close()
            if GLO.GLBLgrabarEcmrMdp:
                if not self.aFiles['CeldasMdpEcmr'] is None:
                    self.aFiles['CeldasMdpEcmr'].close()
                if not self.aFiles['CeldasMdpOctn'] is None:
                    self.aFiles['CeldasMdpOctn'].close()


    # ==========================================================================
    def guardarAjustesMdpExtras(self):
        if GLO.GLBLgrabarMdpInfoAuxiliar:  # Mde/02mCell/Pleno/Auxiliar/
            clidaux.printMsg('\t\t-> cliddata-> Guardando CeldasMdpNumPtosMiniMacro, CeldasMdpNumPtosMiniMicro')
            if not self.aFiles['CeldasMdpNumPtosMiniMacro'] is None and self.aCeldasMdpNumPtosMiniMacro.shape[0] > 1:
                for nY in reversed(range(self.aCeldasMdpNumPtosMiniMacro.shape[1])):
                    for nX in range(self.aCeldasMdpNumPtosMiniMacro.shape[0]):
                        self.aFiles['CeldasMdpNumPtosMiniMacro'].write('%03i' % self.aCeldasMdpNumPtosMiniMacro[nX, nY] + ' ')
                    self.aFiles['CeldasMdpNumPtosMiniMacro'].write('\n')
                self.aFiles['CeldasMdpNumPtosMiniMacro'].close()

            if not self.aFiles['CeldasMdpNumPtosMiniMicro'] is None and self.aCeldasMdpNumPtosMiniMicro.shape[0] > 1:
                for nY in reversed(range(self.aCeldasMdpNumPtosMiniMicro.shape[1])):
                    for nX in range(self.aCeldasMdpNumPtosMiniMicro.shape[0]):
                        self.aFiles['CeldasMdpNumPtosMiniMicro'].write('%03i' % self.aCeldasMdpNumPtosMiniMicro[nX, nY] + ' ')
                    self.aFiles['CeldasMdpNumPtosMiniMicro'].write('\n')
                self.aFiles['CeldasMdpNumPtosMiniMicro'].close()
        # ======================================================================

        # ======================================================================
        if GLO.GLBLcalcularSubCeldas:
            # ==================================================================
            if GLO.GLBLgrabarCotaMinMaxSubCelda:
                # CotaMinMax/02mCell/CotaMiniOk/
                if not self.aFiles['SubCeldasCotaMiniMacroEsOk'] is None and self.aSubCeldasCotaMiniMacroEsOk.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasCotaMiniMacroEsOk')
                    for nY in reversed(range(self.aSubCeldasCotaMiniMacroEsOk.shape[1])):
                        for nX in range(self.aSubCeldasCotaMiniMacroEsOk.shape[0]):
                            self.aFiles['SubCeldasCotaMiniMacroEsOk'].write('%01i' % self.aSubCeldasCotaMiniMacroEsOk[nX, nY] + ' ')
                        self.aFiles['SubCeldasCotaMiniMacroEsOk'].write('\n')
                    self.aFiles['SubCeldasCotaMiniMacroEsOk'].close()
                if not self.aFiles['SubCeldasCotaMiniMicroEsOk'] is None and self.aSubCeldasCotaMiniMicroEsOk.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasCotaMiniMicroEsOk')
                    for nY in reversed(range(self.aSubCeldasCotaMiniMicroEsOk.shape[1])):
                        for nX in range(self.aSubCeldasCotaMiniMicroEsOk.shape[0]):
                            self.aFiles['SubCeldasCotaMiniMicroEsOk'].write('%01i' % self.aSubCeldasCotaMiniMicroEsOk[nX, nY] + ' ')
                        self.aFiles['SubCeldasCotaMiniMicroEsOk'].write('\n')
                    self.aFiles['SubCeldasCotaMiniMicroEsOk'].close()
            # ==================================================================
            if GLO.GLBLgrabarMdpCotaSubceldaMacroMicro:  # Mde/02mCell/Pleno/
                if not self.aFiles['SubCeldasMdpCotaMacroManual'] is None and self.aSubCeldasMdpCotaMacroManual.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasMdpCotaMacroManual')
                    for nY in reversed(range(self.aSubCeldasMdpCotaMacroManual.shape[1])):
                        for nX in range(self.aSubCeldasMdpCotaMacroManual.shape[0]):
                            if (
                                self.aSubCeldasMdpCotaMacroManual[nX, nY] != 0
                                and self.aSubCeldasMdpCotaMacroManual[nX, nY] != 9999
                                and self.aSubCeldasMdpCotaMacroManual[nX, nY] != GLO.GLBLnoData
                            ):
                                self.aFiles['SubCeldasMdpCotaMacroManual'].write('%07.02f' % round(self.aSubCeldasMdpCotaMacroManual[nX, nY], 2) + ' ')
                            else:
                                self.aFiles['SubCeldasMdpCotaMacroManual'].write('%07.01f ' % GLO.GLBLnoData)
                        self.aFiles['SubCeldasMdpCotaMacroManual'].write('\n')
                    self.aFiles['SubCeldasMdpCotaMacroManual'].close()
                if not self.aFiles['SubCeldasMdpCotaMicroManual'] is None and self.aSubCeldasMdpCotaMicroManual.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasMdpCotaMicroManual')
                    for nY in reversed(range(self.aSubCeldasMdpCotaMicroManual.shape[1])):
                        for nX in range(self.aSubCeldasMdpCotaMicroManual.shape[0]):
                            if (
                                self.aSubCeldasMdpCotaMicroManual[nX, nY] != 0
                                and self.aSubCeldasMdpCotaMicroManual[nX, nY] != 9999
                                and self.aSubCeldasMdpCotaMicroManual[nX, nY] != GLO.GLBLnoData
                            ):
                                self.aFiles['SubCeldasMdpCotaMicroManual'].write('%07.02f' % round(self.aSubCeldasMdpCotaMicroManual[nX, nY], 2) + ' ')
                            else:
                                self.aFiles['SubCeldasMdpCotaMicroManual'].write('%07.01f ' % GLO.GLBLnoData)
                        self.aFiles['SubCeldasMdpCotaMicroManual'].write('\n')
                    self.aFiles['SubCeldasMdpCotaMicroManual'].close()
            # ==================================================================
            if GLO.GLBLcalcularMdfConMiniSubCelValidadosConMetodoManualPuro:
                if GLO.GLBLgrabarMdfCotaSubcelda:  # Mde/02mCell/Final/
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasMdfCotaManual')
                    if not self.aFiles['SubCeldasMdfCotaManual'] is None and self.aSubCeldasMdfCotaManual.shape[0] > 1:
                        for nY in reversed(range(self.aSubCeldasMdfCotaManual.shape[1])):
                            for nX in range(self.aSubCeldasMdfCotaManual.shape[0]):
                                if (
                                    self.aSubCeldasMdfCotaManual[nX, nY] != 0
                                    and self.aSubCeldasMdfCotaManual[nX, nY] != -1
                                    and self.aSubCeldasMdfCotaManual[nX, nY] != 9999
                                    and self.aSubCeldasMdfCotaManual[nX, nY] != GLO.GLBLnoData
                                ):
                                    self.aFiles['SubCeldasMdfCotaManual'].write('%07.02f' % round(self.aSubCeldasMdfCotaManual[nX, nY], 2) + ' ')
                                else:
                                    self.aFiles['SubCeldasMdfCotaManual'].write('%07.01f ' % GLO.GLBLnoData)
                            self.aFiles['SubCeldasMdfCotaManual'].write('\n')
                        self.aFiles['SubCeldasMdfCotaManual'].close()

                if GLO.GLBLgrabarMdfCotaSubceldaTransitoria:  # Mde/02mCell/Final/
                    if not self.aFiles['SubCeldasMdfCotaTransitoriaManual'] is None and self.aSubCeldasMdfCotaTransitoriaManual.shape[0] > 1:
                        clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasMdfCotaTransitoriaManual')
                        for nY in reversed(range(self.aSubCeldasMdfCotaTransitoriaManual.shape[1])):
                            for nX in range(self.aSubCeldasMdfCotaTransitoriaManual.shape[0]):
                                if (
                                    self.aSubCeldasMdfCotaTransitoriaManual[nX, nY] != 0
                                    and self.aSubCeldasMdfCotaTransitoriaManual[nX, nY] != -1
                                    and self.aSubCeldasMdfCotaTransitoriaManual[nX, nY] != 9999
                                    and self.aSubCeldasMdfCotaTransitoriaManual[nX, nY] != GLO.GLBLnoData
                                ):
                                    self.aFiles['SubCeldasMdfCotaTransitoriaManual'].write('%07.02f' % round(self.aSubCeldasMdfCotaTransitoriaManual[nX, nY], 2) + ' ')
                                else:
                                    self.aFiles['SubCeldasMdfCotaTransitoriaManual'].write('%07.01f ' % GLO.GLBLnoData)
                            self.aFiles['SubCeldasMdfCotaTransitoriaManual'].write('\n')
                        self.aFiles['SubCeldasMdfCotaTransitoriaManual'].close()
            else:
                clidaux.printMsg('\t\t-> cliddata-> No se guarda el SubCeldasMdfCotaManual propiamente dicho')
            # ==================================================================
            if GLO.GLBLgrabarMdpInfoAuxiliar:  # Mde/02mCell/Pleno/Auxiliar/
                if not self.aFiles['SubCeldasMdpTipoCotaMacroManual'] is None and self.aSubCeldasMdpTipoCotaMacroManual.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasMdpTipoCotaMacroManual')
                    for nY in reversed(range(self.aSubCeldasMdpTipoCotaMacroManual.shape[1])):
                        for nX in range(self.aSubCeldasMdpTipoCotaMacroManual.shape[0]):
                            self.aFiles['SubCeldasMdpTipoCotaMacroManual'].write('%03i' % self.aSubCeldasMdpTipoCotaMacroManual[nX, nY] + ' ')
                        self.aFiles['SubCeldasMdpTipoCotaMacroManual'].write('\n')
                    self.aFiles['SubCeldasMdpTipoCotaMacroManual'].close()
    
                if not self.aFiles['SubCeldasMdpTipoCotaMicroManual'] is None and self.aSubCeldasMdpTipoCotaMicroManual.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasMdpTipoCotaMicroManual')
                    for nY in reversed(range(self.aSubCeldasMdpTipoCotaMicroManual.shape[1])):
                        for nX in range(self.aSubCeldasMdpTipoCotaMicroManual.shape[0]):
                            self.aFiles['SubCeldasMdpTipoCotaMicroManual'].write('%03i' % self.aSubCeldasMdpTipoCotaMicroManual[nX, nY] + ' ')
                        self.aFiles['SubCeldasMdpTipoCotaMicroManual'].write('\n')
                    self.aFiles['SubCeldasMdpTipoCotaMicroManual'].close()
            # ==================================================================

            # ==================================================================
            if GLO.GLBLguardarLateralidadInterSubCeldasMinMax and GLO.GLBLcalcularSubCeldas and GLO.GLBLcalcularSubCeldas:
                # ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
                # RugoLateralidad/02mCell/LateralidadMinMax/
                if not self.aFiles['SubCeldasLateralidadMinMaxMacro'] is None and self.aSubCeldasLateralidadMinMaxMacro.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasLateralidadMinMaxMacro')
                    for nY in reversed(range(self.aSubCeldasLateralidadMinMaxMacro.shape[1])):
                        for nX in range(self.aSubCeldasLateralidadMinMaxMacro.shape[0]):
                            self.aFiles['SubCeldasLateralidadMinMaxMacro'].write('%04.2f' % self.aSubCeldasLateralidadMinMaxMacro[nX, nY] + ' ')
                        self.aFiles['SubCeldasLateralidadMinMaxMacro'].write('\n')
                    self.aFiles['SubCeldasLateralidadMinMaxMacro'].close()
                if not self.aFiles['SubCeldasLateralidadMinMaxMesos'] is None and self.aSubCeldasLateralidadMinMaxMesos.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasLateralidadMinMaxMesos')
                    for nY in reversed(range(self.aSubCeldasLateralidadMinMaxMacro.shape[1])):
                        for nX in range(self.aSubCeldasLateralidadMinMaxMacro.shape[0]):
                            self.aFiles['SubCeldasLateralidadMinMaxMesos'].write('%04.2f' % self.aSubCeldasLateralidadMinMaxMesos[nX, nY] + ' ')
                        self.aFiles['SubCeldasLateralidadMinMaxMesos'].write('\n')
                    self.aFiles['SubCeldasLateralidadMinMaxMesos'].close()
                if not self.aFiles['SubCeldasLateralidadMinMaxMicro'] is None and self.aSubCeldasLateralidadMinMaxMicro.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasLateralidadMinMaxMicro')
                    for nY in reversed(range(self.aSubCeldasLateralidadMinMaxMacro.shape[1])):
                        for nX in range(self.aSubCeldasLateralidadMinMaxMacro.shape[0]):
                            self.aFiles['SubCeldasLateralidadMinMaxMicro'].write('%04.2f' % self.aSubCeldasLateralidadMinMaxMicro[nX, nY] + ' ')
                        self.aFiles['SubCeldasLateralidadMinMaxMicro'].write('\n')
                    self.aFiles['SubCeldasLateralidadMinMaxMicro'].close()
            # ==================================================================
            if GLO.GLBLguardarLateralidadInterSubCeldasMinMin and GLO.GLBLcalcularSubCeldas and GLO.GLBLcalcularSubCeldas:
                # RugoLateralidad/02mCell/LateralidadMinMin/
                if not self.aFiles['SubCeldasLateralidadMinMinMacro'] is None and self.aSubCeldasLateralidadMinMinMacro.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasLateralidadMinMinMacro')
                    for nY in reversed(range(self.aSubCeldasLateralidadMinMinMacro.shape[1])):
                        for nX in range(self.aSubCeldasLateralidadMinMinMacro.shape[0]):
                            self.aFiles['SubCeldasLateralidadMinMinMacro'].write('%04.2f' % self.aSubCeldasLateralidadMinMinMacro[nX, nY] + ' ')
                        self.aFiles['SubCeldasLateralidadMinMinMacro'].write('\n')
                    self.aFiles['SubCeldasLateralidadMinMinMacro'].close()
                if not self.aFiles['SubCeldasLateralidadMinMinMesos'] is None and self.aSubCeldasLateralidadMinMinMesos.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasLateralidadMinMinMesos')
                    for nY in reversed(range(self.aSubCeldasLateralidadMinMinMacro.shape[1])):
                        for nX in range(self.aSubCeldasLateralidadMinMinMacro.shape[0]):
                            self.aFiles['SubCeldasLateralidadMinMinMesos'].write('%04.2f' % self.aSubCeldasLateralidadMinMinMesos[nX, nY] + ' ')
                        self.aFiles['SubCeldasLateralidadMinMinMesos'].write('\n')
                    self.aFiles['SubCeldasLateralidadMinMinMesos'].close()
                if not self.aFiles['SubCeldasLateralidadMinMinMicro'] is None and self.aSubCeldasLateralidadMinMinMicro.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasLateralidadMinMinMicro')
                    for nY in reversed(range(self.aSubCeldasLateralidadMinMinMacro.shape[1])):
                        for nX in range(self.aSubCeldasLateralidadMinMinMacro.shape[0]):
                            self.aFiles['SubCeldasLateralidadMinMinMicro'].write('%04.2f' % self.aSubCeldasLateralidadMinMinMicro[nX, nY] + ' ')
                        self.aFiles['SubCeldasLateralidadMinMinMicro'].write('\n')
                    self.aFiles['SubCeldasLateralidadMinMinMicro'].close()
            # ==================================================================
            if GLO.GLBLguardarRugosidadInterSubCeldas and GLO.GLBLcalcularSubCeldas and GLO.GLBLcalcularSubCeldas:
                # RugoLateralidad/02mCell/Rugosidad/
                if not self.aFiles['SubCeldasRugosidadMacroInterSubCeldas'] is None and self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasRugosidadMicroInterSubCeldas')
                    for nY in reversed(range(self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas.shape[1])):
                        for nX in range(self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas.shape[0]):
                            self.aFiles['SubCeldasRugosidadMacroInterSubCeldas'].write('%03i' % self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas[nX, nY] + ' ')
                        self.aFiles['SubCeldasRugosidadMacroInterSubCeldas'].write('\n')
                    self.aFiles['SubCeldasRugosidadMacroInterSubCeldas'].close()
                if not self.aFiles['SubCeldasRugosidadMesosInterSubCeldas'] is None and self.aSubCeldasRugosidadMinMaxMesosInterSubCeldas.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasRugosidadMesosInterSubCeldas')
                    for nY in reversed(range(self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas.shape[1])):
                        for nX in range(self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas.shape[0]):
                            self.aFiles['SubCeldasRugosidadMesosInterSubCeldas'].write('%03i' % self.aSubCeldasRugosidadMinMaxMesosInterSubCeldas[nX, nY] + ' ')
                        self.aFiles['SubCeldasRugosidadMesosInterSubCeldas'].write('\n')
                    self.aFiles['SubCeldasRugosidadMesosInterSubCeldas'].close()
                if not self.aFiles['SubCeldasRugosidadMicroInterSubCeldas'] is None and self.aSubCeldasRugosidadMinMaxMicroInterSubCeldas.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando SubCeldasRugosidadMicroInterSubCeldas')
                    for nY in reversed(range(self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas.shape[1])):
                        for nX in range(self.aSubCeldasRugosidadMinMaxMacroInterSubCeldas.shape[0]):
                            self.aFiles['SubCeldasRugosidadMicroInterSubCeldas'].write('%03i' % self.aSubCeldasRugosidadMinMaxMicroInterSubCeldas[nX, nY] + ' ')
                        self.aFiles['SubCeldasRugosidadMicroInterSubCeldas'].write('\n')
                    self.aFiles['SubCeldasRugosidadMicroInterSubCeldas'].close()
            # ==================================================================
            if GLO.GLBLguardarRugosidadMultiCeldas and GLO.GLBLcalcularSubCeldas and GLO.GLBLcalcularSubCeldas:
                # RugoLateralidad/MultiCelda/
                if GLO.GLBLrugosidadExplorandoCeldasColindantes:
                    conSincolindantes = 'InclColindantes'
                else:
                    conSincolindantes = 'ExclColindantes'
                capaMultiCeldasRugosidadMacroInterSubCeldas = 'MultiCeldasRugosidadMacroInterSubCeldasCrit%i%s' % (
                    GLO.GLBLcriterioParaEvaluarLaRugosidad,
                    conSincolindantes,
                )
                capaMultiCeldasRugosidadMesosInterSubCeldas = 'MultiCeldasRugosidadMesosInterSubCeldasCrit%i%s' % (
                    GLO.GLBLcriterioParaEvaluarLaRugosidad,
                    conSincolindantes,
                )
                capaMultiCeldasRugosidadMicroInterSubCeldas = 'MultiCeldasRugosidadMicroInterSubCeldasCrit%i%s' % (
                    GLO.GLBLcriterioParaEvaluarLaRugosidad,
                    conSincolindantes,
                )
                if not self.aFiles[capaMultiCeldasRugosidadMacroInterSubCeldas] is None and self.aMultiCeldasRugosidadMacroInterSubCeldas.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando {}, {}, {}'.format(capaMultiCeldasRugosidadMacroInterSubCeldas))
                    for nY in reversed(range(self.aMultiCeldasRugosidadMacroInterSubCeldas.shape[1])):
                        for nX in range(self.aMultiCeldasRugosidadMacroInterSubCeldas.shape[0]):
                            self.aFiles[capaMultiCeldasRugosidadMacroInterSubCeldas].write('%03i' % self.aMultiCeldasRugosidadMacroInterSubCeldas[nX, nY] + ' ')
                        self.aFiles[capaMultiCeldasRugosidadMacroInterSubCeldas].write('\n')
                    self.aFiles[capaMultiCeldasRugosidadMacroInterSubCeldas].close()
                if not self.aFiles[capaMultiCeldasRugosidadMesosInterSubCeldas] is None and self.aMultiCeldasRugosidadMesosInterSubCeldas.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando {}, {}, {}'.format(capaMultiCeldasRugosidadMesosInterSubCeldas))
                    for nY in reversed(range(self.aMultiCeldasRugosidadMesosInterSubCeldas.shape[1])):
                        for nX in range(self.aMultiCeldasRugosidadMesosInterSubCeldas.shape[0]):
                            self.aFiles[capaMultiCeldasRugosidadMesosInterSubCeldas].write('%03i' % self.aMultiCeldasRugosidadMesosInterSubCeldas[nX, nY] + ' ')
                        self.aFiles[capaMultiCeldasRugosidadMesosInterSubCeldas].write('\n')
                    self.aFiles[capaMultiCeldasRugosidadMesosInterSubCeldas].close()
                if not self.aFiles[capaMultiCeldasRugosidadMicroInterSubCeldas] is None and self.aMultiCeldasRugosidadMicroInterSubCeldas.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando {}, {}, {}'.format(capaMultiCeldasRugosidadMicroInterSubCeldas))
                    for nY in reversed(range(self.aMultiCeldasRugosidadMicroInterSubCeldas.shape[1])):
                        for nX in range(self.aMultiCeldasRugosidadMicroInterSubCeldas.shape[0]):
                            self.aFiles[capaMultiCeldasRugosidadMicroInterSubCeldas].write('%03i' % self.aMultiCeldasRugosidadMicroInterSubCeldas[nX, nY] + ' ')
                        self.aFiles[capaMultiCeldasRugosidadMicroInterSubCeldas].write('\n')
                    self.aFiles[capaMultiCeldasRugosidadMicroInterSubCeldas].close()
            # ==================================================================

            # ==================================================================
            if GLO.GLBLgrabarMdpInfoAuxiliar:
                # RugoLateralidad/MultiCelda/Auxiliar/
                if not self.aFiles['MultiCeldasEstruct'] is None and self.aMultiCeldasEstruct.shape[0] > 1:
                    clidaux.printMsg('\t\t-> cliddata-> Guardando MultiCeldasEstruct')
                    for nY in reversed(range(self.aMultiCeldasEstruct.shape[1])):
                        for nX in range(self.aMultiCeldasEstruct.shape[0]):
                            if (
                                self.aMultiCeldasEstruct[nX, nY] != 0
                                and self.aMultiCeldasEstruct[nX, nY] != 9999
                                and self.aMultiCeldasEstruct[nX, nY] != GLO.GLBLnoData8bits
                            ):
                                self.aFiles['MultiCeldasEstruct'].write('%07.02f' % self.aMultiCeldasEstruct[nX, nY] + ' ')
                            else:
                                self.aFiles['MultiCeldasEstruct'].write('%07.01f ' % GLO.GLBLnoData8bits)
                        self.aFiles['MultiCeldasEstruct'].write('\n')
                    self.aFiles['MultiCeldasEstruct'].close()


    # ==========================================================================
    # if GLO.GLBLcalcularMdr and GLO.GLBLgrabarMdr: #Mde/Grid/10mCell/
    def guardarAjustesMdr(self):
        if not self.aFiles['CeldasMdrGridNearest'] is None and self.aCeldasMdrCoeficientes.shape[0] > 1:
            for nY in reversed(range(self.nCeldasY)):
                for nX in range(self.nCeldasX):
                    if self.aCeldasMdrCoeficientes[nX, nY, 0] != 9999:
                        self.aFiles['CeldasMdrGridNearest'].write('%07.02f' % round(self.aCeldasMdrCoeficientes[nX, nY, 0], 2) + ' ')
                    else:
                        self.aFiles['CeldasMdrGridNearest'].write('0000.00 ')
                self.aFiles['CeldasMdrGridNearest'].write('\n')
            self.aFiles['CeldasMdrGridNearest'].close()
        if not self.aFiles['CeldasMdrGridLinear'] is None and self.aCeldasMdrCoeficientes.shape[0] > 1:
            for nY in reversed(range(self.nCeldasY)):
                for nX in range(self.nCeldasX):
                    if self.aCeldasMdrCoeficientes[nX, nY, 1] != 9999:
                        self.aFiles['CeldasMdrGridLinear'].write('%07.02f' % round(self.aCeldasMdrCoeficientes[nX, nY, 1], 2) + ' ')
                    else:
                        self.aFiles['CeldasMdrGridLinear'].write('0000.00 ')
                self.aFiles['CeldasMdrGridLinear'].write('\n')
            self.aFiles['CeldasMdrGridLinear'].close()
        if not self.aFiles['CeldasMdrGridCubic'] is None and self.aCeldasMdrCoeficientes.shape[0] > 1:
            for nY in reversed(range(self.nCeldasY)):
                for nX in range(self.nCeldasX):
                    if self.aCeldasMdrCoeficientes[nX, nY, 2] != 9999:
                        self.aFiles['CeldasMdrGridCubic'].write('%07.02f' % round(self.aCeldasMdrCoeficientes[nX, nY, 2], 2) + ' ')
                    else:
                        self.aFiles['CeldasMdrGridCubic'].write('0000.00 ')
                self.aFiles['CeldasMdrGridCubic'].write('\n')
            self.aFiles['CeldasMdrGridCubic'].close()


        if GLO.GLBLcalcularCotaDeSubceldasConGriddata:  # Mde/02mCell/Grid/
            if not self.aFiles['SubCeldasMdrGridPtoMinor'] is None and self.aSubCeldasMdrCotaInterpolada.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasMdrCotaInterpolada.shape[1])):
                    for nX in range(self.aSubCeldasMdrCotaInterpolada.shape[0]):
                        if self.aSubCeldasMdrCotaInterpolada[nX, nY, 0] != 9999:
                            self.aFiles['SubCeldasMdrGridPtoMinor'].write('%07.02f' % round(self.aSubCeldasMdrCotaInterpolada[nX, nY, 0], 2) + ' ')
                        else:
                            self.aFiles['SubCeldasMdrGridPtoMinor'].write('0000.00 ')
                    self.aFiles['SubCeldasMdrGridPtoMinor'].write('\n')
                self.aFiles['SubCeldasMdrGridPtoMinor'].close()
            if not self.aFiles['SubCeldasMdrGridNearest'] is None and self.aSubCeldasMdrCotaInterpolada.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasMdrCotaInterpolada.shape[1])):
                    for nX in range(self.aSubCeldasMdrCotaInterpolada.shape[0]):
                        if self.aSubCeldasMdrCotaInterpolada[nX, nY, 1] != 9999:
                            self.aFiles['SubCeldasMdrGridNearest'].write('%07.02f' % round(self.aSubCeldasMdrCotaInterpolada[nX, nY, 1], 2) + ' ')
                        else:
                            self.aFiles['SubCeldasMdrGridNearest'].write('0000.00 ')
                    self.aFiles['SubCeldasMdrGridNearest'].write('\n')
                self.aFiles['SubCeldasMdrGridNearest'].close()
            if not self.aFiles['SubCeldasMdrGridLinear'] is None and self.aSubCeldasMdrCotaInterpolada.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasMdrCotaInterpolada.shape[1])):
                    for nX in range(self.aSubCeldasMdrCotaInterpolada.shape[0]):
                        if self.aSubCeldasMdrCotaInterpolada[nX, nY, 2] != 9999:
                            self.aFiles['SubCeldasMdrGridLinear'].write('%07.02f' % round(self.aSubCeldasMdrCotaInterpolada[nX, nY, 2], 2) + ' ')
                        else:
                            self.aFiles['SubCeldasMdrGridLinear'].write('0000.00 ')
                    self.aFiles['SubCeldasMdrGridLinear'].write('\n')
                self.aFiles['SubCeldasMdrGridLinear'].close()
            if not self.aFiles['SubCeldasMdrGridCubic'] is None and self.aSubCeldasMdrCotaInterpolada.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasMdrCotaInterpolada.shape[1])):
                    for nX in range(self.aSubCeldasMdrCotaInterpolada.shape[0]):
                        if self.aSubCeldasMdrCotaInterpolada[nX, nY, 3] != 9999:
                            self.aFiles['SubCeldasMdrGridCubic'].write('%07.02f' % round(self.aSubCeldasMdrCotaInterpolada[nX, nY, 3], 2) + ' ')
                        else:
                            self.aFiles['SubCeldasMdrGridCubic'].write('0000.00 ')
                    self.aFiles['SubCeldasMdrGridCubic'].write('\n')
                self.aFiles['SubCeldasMdrGridCubic'].close()


    # ==========================================================================
    def guardarVuelta4(self):
        if GLO.GLBLguardarCapaRugosidadInterCeldillasCeldas:  # HiperCubo/Rugosidad/10mCell/
            if not self.aFiles['CeldasRugosidadMegasInterCeldillas'] is None and self.aCeldasRugosidadMegasInterCeldillas.shape[0] > 1:
                for nY in range(self.aCeldasRugosidadMegasInterCeldillas.shape[1] - 1, 0 - 1, -1):
                    for nX in range(self.aCeldasRugosidadMegasInterCeldillas.shape[0]):
                        self.aFiles['CeldasRugosidadMegasInterCeldillas'].write(str('%02i ' % self.aCeldasRugosidadMegasInterCeldillas[nX, nY]))
                    self.aFiles['CeldasRugosidadMegasInterCeldillas'].write('\n')
                self.aFiles['CeldasRugosidadMegasInterCeldillas'].close()
            if not self.aFiles['CeldasRugosidadMacroInterCeldillas'] is None and self.aCeldasRugosidadMacroInterCeldillas.shape[0] > 1:
                for nY in range(self.aCeldasRugosidadMacroInterCeldillas.shape[1] - 1, 0 - 1, -1):
                    for nX in range(self.aCeldasRugosidadMacroInterCeldillas.shape[0]):
                        self.aFiles['CeldasRugosidadMacroInterCeldillas'].write(str('%02i ' % self.aCeldasRugosidadMacroInterCeldillas[nX, nY]))
                    self.aFiles['CeldasRugosidadMacroInterCeldillas'].write('\n')
                self.aFiles['CeldasRugosidadMesosInterCeldillas'].close()
            if not self.aFiles['CeldasRugosidadMesosInterCeldillas'] is None and self.aCeldasRugosidadMesosInterCeldillas.shape[0] > 1:
                for nY in range(self.aCeldasRugosidadMesosInterCeldillas.shape[1] - 1, 0 - 1, -1):
                    for nX in range(self.aCeldasRugosidadMesosInterCeldillas.shape[0]):
                        self.aFiles['CeldasRugosidadMesosInterCeldillas'].write(str('%02i ' % self.aCeldasRugosidadMesosInterCeldillas[nX, nY]))
                    self.aFiles['CeldasRugosidadMesosInterCeldillas'].write('\n')
                self.aFiles['CeldasRugosidadMesosInterCeldillas'].close()
            if not self.aFiles['CeldasRugosidadMicroInterCeldillas'] is None and self.aCeldasRugosidadMicroInterCeldillas.shape[0] > 1:
                for nY in range(self.aCeldasRugosidadMicroInterCeldillas.shape[1] - 1, 0 - 1, -1):
                    for nX in range(self.aCeldasRugosidadMicroInterCeldillas.shape[0]):
                        self.aFiles['CeldasRugosidadMicroInterCeldillas'].write(str('%02i ' % self.aCeldasRugosidadMicroInterCeldillas[nX, nY]))
                    self.aFiles['CeldasRugosidadMicroInterCeldillas'].write('\n')
                self.aFiles['CeldasRugosidadMicroInterCeldillas'].close()
        # ======================================================================
        if GLO.GLBLguardarCapaRugosidadInterCeldillasSubCeldas:  # HiperCubo/Rugosidad/02mCell/
            if not self.aFiles['SubCeldasRugosidadMacroInterCeldillas'] is None and self.aSubCeldasRugosidadMacroInterCeldillas.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasRugosidadMacroInterCeldillas.shape[1])):
                    for nX in range(self.aSubCeldasRugosidadMacroInterCeldillas.shape[0]):
                        self.aFiles['SubCeldasRugosidadMacroInterCeldillas'].write('%02i ' % self.aSubCeldasRugosidadMacroInterCeldillas[nX, nY])
                    self.aFiles['SubCeldasRugosidadMacroInterCeldillas'].write('\n')
                self.aFiles['SubCeldasRugosidadMacroInterCeldillas'].close()
            if not self.aFiles['SubCeldasRugosidadMesosInterCeldillas'] is None and self.aSubCeldasRugosidadMesosInterCeldillas.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasRugosidadMesosInterCeldillas.shape[1])):
                    for nX in range(self.aSubCeldasRugosidadMesosInterCeldillas.shape[0]):
                        self.aFiles['SubCeldasRugosidadMesosInterCeldillas'].write('%02i ' % self.aSubCeldasRugosidadMesosInterCeldillas[nX, nY])
                    self.aFiles['SubCeldasRugosidadMesosInterCeldillas'].write('\n')
                self.aFiles['SubCeldasRugosidadMesosInterCeldillas'].close()
            if not self.aFiles['SubCeldasRugosidadMicroInterCeldillas'] is None and self.aSubCeldasRugosidadMicroInterCeldillas.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasRugosidadMicroInterCeldillas.shape[1])):
                    for nX in range(self.aSubCeldasRugosidadMicroInterCeldillas.shape[0]):
                        self.aFiles['SubCeldasRugosidadMicroInterCeldillas'].write('%02i ' % self.aSubCeldasRugosidadMicroInterCeldillas[nX, nY])
                    self.aFiles['SubCeldasRugosidadMicroInterCeldillas'].write('\n')
                self.aFiles['SubCeldasRugosidadMicroInterCeldillas'].close()
            if not self.aFiles['SubCeldasRugosidadMegasInterCeldillas'] is None and self.aSubCeldasRugosidadMegasInterCeldillas.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasRugosidadMegasInterCeldillas.shape[1])):
                    for nX in range(self.aSubCeldasRugosidadMegasInterCeldillas.shape[0]):
                        self.aFiles['SubCeldasRugosidadMegasInterCeldillas'].write('%02i ' % self.aSubCeldasRugosidadMegasInterCeldillas[nX, nY])
                    self.aFiles['SubCeldasRugosidadMegasInterCeldillas'].write('\n')
                self.aFiles['SubCeldasRugosidadMegasInterCeldillas'].close()
        # ======================================================================
        if GLO.GLBLguardarCapaRugosidadInterCeldillasMetrico:  # HiperCubo/Rugosidad/01mCell/
            if not self.aFiles['MetricoRugosidadMacroInterCeldillas'] is None and self.aMetricoRugosidadMacroInterCeldillas.shape[0] > 1:
                for nY in reversed(range(self.aMetricoRugosidadMacroInterCeldillas.shape[1])):
                    for nX in range(self.aMetricoRugosidadMacroInterCeldillas.shape[0]):
                        self.aFiles['MetricoRugosidadMacroInterCeldillas'].write('%01i ' % self.aMetricoRugosidadMacroInterCeldillas[nX, nY])
                    self.aFiles['MetricoRugosidadMacroInterCeldillas'].write('\n')
                self.aFiles['MetricoRugosidadMacroInterCeldillas'].close()
            if not self.aFiles['MetricoRugosidadMesosInterCeldillas'] is None and self.aMetricoRugosidadMesosInterCeldillas.shape[0] > 1:
                for nY in reversed(range(self.aMetricoRugosidadMesosInterCeldillas.shape[1])):
                    for nX in range(self.aMetricoRugosidadMesosInterCeldillas.shape[0]):
                        self.aFiles['MetricoRugosidadMesosInterCeldillas'].write('%01i ' % self.aMetricoRugosidadMesosInterCeldillas[nX, nY])
                    self.aFiles['MetricoRugosidadMesosInterCeldillas'].write('\n')
                self.aFiles['MetricoRugosidadMesosInterCeldillas'].close()
            if not self.aFiles['MetricoRugosidadMicroInterCeldillas'] is None and self.aMetricoRugosidadMicroInterCeldillas.shape[0] > 1:
                for nY in reversed(range(self.aMetricoRugosidadMicroInterCeldillas.shape[1])):
                    for nX in range(self.aMetricoRugosidadMicroInterCeldillas.shape[0]):
                        self.aFiles['MetricoRugosidadMicroInterCeldillas'].write('%01i ' % self.aMetricoRugosidadMicroInterCeldillas[nX, nY])
                    self.aFiles['MetricoRugosidadMicroInterCeldillas'].write('\n')
                self.aFiles['MetricoRugosidadMicroInterCeldillas'].close()
            if not self.aFiles['MetricoRugosidadMegasInterCeldillas'] is None and self.aMetricoRugosidadMegasInterCeldillas.shape[0] > 1:
                for nY in reversed(range(self.aMetricoRugosidadMegasInterCeldillas.shape[1])):
                    for nX in range(self.aMetricoRugosidadMegasInterCeldillas.shape[0]):
                        self.aFiles['MetricoRugosidadMegasInterCeldillas'].write('%1i ' % self.aMetricoRugosidadMegasInterCeldillas[nX, nY])
                    self.aFiles['MetricoRugosidadMegasInterCeldillas'].write('\n')
                self.aFiles['MetricoRugosidadMegasInterCeldillas'].close()
        # ======================================================================

        # ======================================================================
        if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoCeldas:  # HiperCubo/Tejado/10mCell/
            if not self.aFiles['CeldasNumeroDePlanosTejado'] is None and self.aCeldasNumeroDePlanosTejado.shape[0] > 1:
                for nY in range(self.aCeldasNumeroDePlanosTejado.shape[0] - 1, 0 - 1, -1):
                    for nX in range(self.aCeldasNumeroDePlanosTejado.shape[0]):
                        self.aFiles['CeldasNumeroDePlanosTejado'].write(str('%02i ' % self.aCeldasNumeroDePlanosTejado[nX, nY]))
                    self.aFiles['CeldasNumeroDePlanosTejado'].write('\n')
                self.aFiles['CeldasNumeroDePlanosTejado'].close()
            if not self.aFiles['CeldasPuntosEnPlanosTejado'] is None and self.aCeldasPuntosEnPlanosTejado.shape[0] > 1:
                for nY in range(self.aCeldasPuntosEnPlanosTejado.shape[1] - 1, 0 - 1, -1):
                    for nX in range(self.aCeldasPuntosEnPlanosTejado.shape[0]):
                        self.aFiles['CeldasPuntosEnPlanosTejado'].write(str('%03i ' % self.aCeldasPuntosEnPlanosTejado[nX, nY]))
                    self.aFiles['CeldasPuntosEnPlanosTejado'].write('\n')
                self.aFiles['CeldasPuntosEnPlanosTejado'].close()
        # ======================================================================
        if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoSubCeldas:  # HiperCubo/Tejado/02mCell/
            if not self.aFiles['SubCeldasPlanoTejado'] is None and self.aSubCeldasPlanoTejado.shape[0] > 1:
                for nY in reversed(range(self.aSubCeldasPlanoTejado.shape[1])):
                    for nX in range(self.aSubCeldasPlanoTejado.shape[0]):
                        self.aFiles['SubCeldasPlanoTejado'].write('%03i ' % self.aSubCeldasPlanoTejado[nX, nY])
                    self.aFiles['SubCeldasPlanoTejado'].write('\n')
                self.aFiles['SubCeldasPlanoTejado'].close()
        # ======================================================================
        if GLO.GLBLidentificarPlanos and GLO.GLBLguardarPlanosTejadoMetrico:  # HiperCubo/Tejado/01mCell/
            if not self.aFiles['MetricoPlanoTejado'] is None and self.aMetricoPlanoTejado.shape[0] > 1:
                for nY in reversed(range(self.aMetricoPlanoTejado.shape[1])):
                    for nX in range(self.aMetricoPlanoTejado.shape[0]):
                        self.aFiles['MetricoPlanoTejado'].write('%03i ' % self.aMetricoPlanoTejado[nX, nY])
                    self.aFiles['MetricoPlanoTejado'].write('\n')
                self.aFiles['MetricoPlanoTejado'].close()
        # ======================================================================


    # ==========================================================================
    # if GLO.GLBLgrabarNucleosCartoRef and cartoRefNucleosUrbanos.usarVectorRef:
    def guardarNucleosDeCartoRef(self, cartoRefNucleosUrbanos_aCeldasLandUseCover):
        # convolLasClassLandCover/Nucleos/
        if not self.aFiles['CeldasNucleosUrbanosDeCartoRef'] is None and cartoRefNucleosUrbanos_aCeldasLandUseCover.shape[0] > 1:
            for nY in range(cartoRefNucleosUrbanos_aCeldasLandUseCover.shape[1] - 1, 0 - 1, -1):
                for nX in range(cartoRefNucleosUrbanos_aCeldasLandUseCover[0]):
                    self.aFiles['CeldasNucleosUrbanosDeCartoRef'].write(str('%01i ' % cartoRefNucleosUrbanos_aCeldasLandUseCover[nX, nY]) + ' ')
                self.aFiles['CeldasNucleosUrbanosDeCartoRef'].write('\n')
            self.aFiles['CeldasNucleosUrbanosDeCartoRef'].close()
        else:
            print('\t\t-> No es necesario guardar nucleos urbanos de cartografia de referencia xq ya existen esos ficheros')


    # ==========================================================================
    # if GLO.GLBLgrabarSingUseCartoRef and cartoRefUsoSingular.usarVectorRef:
    def guardarSingUseDeCartoRef(self, cartoRefUsoSingular_aCeldasLandUseCover):
        # convolLasClassLandCover/CartoRefSingUse/CoverOriginal/
        if not self.aFiles['CeldasUsosSingularesDeCartoRef'] is None and cartoRefUsoSingular_aCeldasLandUseCover.shape[0] > 1:
            for nY in range(cartoRefUsoSingular_aCeldasLandUseCover.shape[1] - 1, 0 - 1, -1):
                for nX in range(cartoRefUsoSingular_aCeldasLandUseCover.shape[0]):
                    self.aFiles['CeldasUsosSingularesDeCartoRef'].write(str('%i ' % cartoRefUsoSingular_aCeldasLandUseCover[nX, nY]) + ' ')
                self.aFiles['CeldasUsosSingularesDeCartoRef'].write('\n')
            self.aFiles['CeldasUsosSingularesDeCartoRef'].close()
        else:
            print('\t\t-> No es necesario guardar usos singulares de cartografia de referencia xq ya existen esos ficheros')

    # ==========================================================================
    # if GLO.GLBLcalcularMdp and GLO.GLBLcalcularSubCeldas:
    def guardarMiniSubCelSueloValidadoPorMdp(self):
        if not self.aFiles['SubCeldasPuntoMiniSubCelValidado'] is None and self.aSubCeldasPuntoMiniSubCelValidado.shape[0] > 1:
            for nY in reversed(range(self.aSubCeldasPuntoMiniSubCelValidado.shape[1])):
                for nX in range(self.aSubCeldasPuntoMiniSubCelValidado.shape[0]):
                    self.aFiles['SubCeldasPuntoMiniSubCelValidado'].write(str('%i ' % self.aSubCeldasPuntoMiniSubCelValidado[nX, nY]))
                self.aFiles['SubCeldasPuntoMiniSubCelValidado'].write('\n')
            self.aFiles['SubCeldasPuntoMiniSubCelValidado'].close()


    # ==========================================================================
    # if GLO.GLBLgrabarMiniSubCelClassPredict and myLasData.okPrediccionMiniSubCel: # Requiere GLO.GLBLcrearTilesPostVuelta1 and GLO.GLBLcalcularSubCeldas
    def guardarMiniSubCelClassPredict(self):
        if not self.aFiles['SubCeldasMiniSubCelLasClassPredicha'] is None and self.aSubCeldasMiniSubCelLasClassPredicha.shape[0] > 1:
            for nY in reversed(range(self.aSubCeldasMiniSubCelLasClassPredicha.shape[1])):
                for nX in range(self.aSubCeldasMiniSubCelLasClassPredicha.shape[0]):
                    self.aFiles['SubCeldasMiniSubCelLasClassPredicha'].write(str('%i ' % self.aSubCeldasMiniSubCelLasClassPredicha[nX, nY]))
                self.aFiles['SubCeldasMiniSubCelLasClassPredicha'].write('\n')
            self.aFiles['SubCeldasMiniSubCelLasClassPredicha'].close()
        if GLO.GLBLgrabarMultiTiles:
            if not self.aFiles['MultiTilesMiniSubCelLasClassPredicha'] is None and self.aMultiTilesMiniSubCelLasClassPredicha.shape[0] > 1:
                for nY in reversed(range(self.aMultiTilesMiniSubCelLasClassPredicha.shape[1])):
                    for nX in range(self.aMultiTilesMiniSubCelLasClassPredicha.shape[0]):
                        self.aFiles['MultiTilesMiniSubCelLasClassPredicha'].write(str('%i ' % self.aMultiTilesMiniSubCelLasClassPredicha[nX, nY]))
                    self.aFiles['MultiTilesMiniSubCelLasClassPredicha'].write('\n')
                self.aFiles['MultiTilesMiniSubCelLasClassPredicha'].close()


    # ==========================================================================
    # OBSOLETA xq tarda 30-60", la traslado a clidnv0.py como funcion independiente (no metodo de clase) y la compilo con numba (asi tarda menos de 5")
    # if GLO.GLBLanularTriClassDePuntosMiniSubCelNoCoherentesConCartoRef or GLO.GLBLanularBinClassDePuntosMiniSubCelNoCoherentesConCartoRef:
#     def asignarLasClassAgrupadaDePuntosMiniSubCel(self):
#         for nSubY in reversed(range(self.nCeldasY * GLBNsubCeldasPorCelda)):
#             for nSubX in range(self.nCeldasX * GLBNsubCeldasPorCelda):
#                 if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
#                     if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
#                         self_miPtoNpMaxiMiniSubCel = self.aSubCeldasPuntoMiniSubCelPsuePsel[nSubX, nSubY]
#                         lasClassOriginal = np.uint8(self_miPtoNpMaxiMiniSubCel['lasClassOriginal'])
#                         # miPtoClase_2_345_6 = np.uint8(self_miPtoNpMaxiMiniSubCel['lasClass_2_345_6'])
#                         # miPtoClase_Binaria = np.uint8(self_miPtoNpMaxiMiniSubCel['lasClass_Binaria'])
#                         singularUse8bits = np.uint8(self_miPtoNpMaxiMiniSubCel['usoSingular'])
#                     else:
#                         lasClassOriginal = np.uint8(self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 8])
#                         # miPtoClase_2_345_6 = np.uint8(self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 9])
#                         # miPtoClase_Binaria = np.uint8(self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 10])
#                         singularUse8bits = np.uint8(self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 12])
#                 else:
#                     self_miPtoNpMaxiMiniSubCel = self.aSubCeldasPuntoMiniSubCel_Tlp[nSubX, nSubY]
#                     lasClassOriginal = np.uint8(self_miPtoNpMaxiMiniSubCel['lasClassOriginal'])
#                     # miPtoClase_2_345_6 = np.uint8(self_miPtoNpMaxiMiniSubCel['lasClass_2_345_6'])
#                     # miPtoClase_Binaria = np.uint8(self_miPtoNpMaxiMiniSubCel['lasClass_Binaria'])
#                     singularUse8bits = np.uint8(self_miPtoNpMaxiMiniSubCel['usoSingular'])
# 
#                 if GLO.GLBLanularBinClassDePuntosMiniSubCelNoCoherentesConCartoRef:
#                     if GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase == 2:
#                         if lasClassOriginal == 2 and singularUse8bits < 100:
#                             miPtoClase_Binaria = 1
#                         else:
#                             miPtoClase_Binaria = 0
#                     elif GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase == 6:
#                         if lasClassOriginal == 6 and singularUse8bits >= 100:
#                             miPtoClase_Binaria = 1
#                         else:
#                             miPtoClase_Binaria = 0
#                     else:
#                         if lasClassOriginal == GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
#                             miPtoClase_Binaria = 1
#                         else:
#                             miPtoClase_Binaria = 0
#                 else:
#                     if lasClassOriginal == GLO.GLBLreorganizaLasClassParaGenerarTilesBinariosMonoClase:
#                         miPtoClase_Binaria = 1
#                     else:
#                         miPtoClase_Binaria = 0
# 
#                 if lasClassOriginal == 6:
#                     if GLO.GLBLanularTriClassDePuntosMiniSubCelNoCoherentesConCartoRef:
#                         if singularUse8bits >= 100:
#                             miPtoClase_2_345_6 = 1 # lasClass_edificio vs cartoRef_edificio
#                         else:
#                             miPtoClase_2_345_6 = 0 # Excluir # lasClass_edificio vs cartoRef_noEdificio
#                     else:
#                         miPtoClase_2_345_6 = 1 # Edificio
#                 elif lasClassOriginal == 2:
#                     if GLO.GLBLanularTriClassDePuntosMiniSubCelNoCoherentesConCartoRef:
#                         if singularUse8bits < 100:
#                             miPtoClase_2_345_6 = 2 # lasClass_suelo vs cartoRef_noEdificio
#                         else:
#                             miPtoClase_2_345_6 = 0 # Excluir # lasClass_Suelo vs cartoRef_edificio
#                     else:
#                         miPtoClase_2_345_6 = 2 # Suelo
#                 elif lasClassOriginal in  [3, 4, 5]:
#                     if GLO.GLBLanularTriClassDePuntosMiniSubCelNoCoherentesConCartoRef:
#                         if singularUse8bits < 100:
#                             miPtoClase_2_345_6 = 3 # lasClass_vegetacion vs cartoRef_noEdificio
#                         else:
#                             miPtoClase_2_345_6 = 0 # Excluir # lasClass_vegetacion vs cartoRef_edificio
#                     else:
#                         miPtoClase_2_345_6 = 3 # Vegetacion
#                 else:
#                     miPtoClase_2_345_6 = 0 # Excluir # lasClass no es suelo, edificio ni vegetacion
# 
#                 if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
#                     if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel:
#                         self_miPtoNpMaxiMiniSubCel['lasClass_2_345_6'] = miPtoClase_2_345_6
#                         self_miPtoNpMaxiMiniSubCel['lasClass_Binaria'] = miPtoClase_Binaria
#                         self.aSubCeldasPuntoMiniSubCelPsuePsel[nSubX, nSubY] = self_miPtoNpMaxiMiniSubCel
#                     else:
#                         self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 9] = miPtoClase_2_345_6
#                         self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 10] = miPtoClase_Binaria
#                 else:
#                     self_miPtoNpMaxiMiniSubCel['lasClass_2_345_6'] = miPtoClase_2_345_6
#                     self_miPtoNpMaxiMiniSubCel['lasClass_Binaria'] = miPtoClase_Binaria
#                     self.aSubCeldasPuntoMiniSubCel_Tlp[nSubX, nSubY] = self_miPtoNpMaxiMiniSubCel


    # ==========================================================================
    # if GLO.GLBLgrabarMiniSubCelClassOriginal:
    def guardarMiniSubCelClassOriginal(self):
        if GLO.GLBLgrabarMiniSubCelClassOrigCompleta:
            if not self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrigCompleta'] is None:
                myClassArray = getattr(self, 'aSubCeldasPuntoMiniSubCelPsuePsel', None)
                for nSubY in reversed(range(self.nCeldasY * GLBNsubCeldasPorCelda)):
                    for nSubX in range(self.nCeldasX * GLBNsubCeldasPorCelda):
                        if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                            nSubX >= self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]
                            or nSubY >= self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]
                        ):
                            continue
                        if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                            if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel and self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0] > 1:
                                subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCelPsuePsel[nSubX, nSubY]['lasClassOriginal']
                            elif self.aSubCeldasPuntoMiniSubCelPsel.shape[0]: # A extinguir
                                subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 8]
                        elif self.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]:
                            subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCel_Tlp[nSubX, nSubY]['lasClassOriginal']
                        self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrigCompleta'].write(str('%i ' % subCeldaPuntoMiniSubCel))
                    self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrigCompleta'].write('\n')
                self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrigCompleta'].close()

        if GLO.GLBLgrabarMiniSubCelClassOrig_2_345_6:
            if not self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_2_345_6'] is None:
                myClassArray = getattr(self, 'aSubCeldasPuntoMiniSubCelPsuePsel', None)
                for nSubY in reversed(range(self.nCeldasY * GLBNsubCeldasPorCelda)):
                    for nSubX in range(self.nCeldasX * GLBNsubCeldasPorCelda):
                        if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                            nSubX >= self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]
                            or nSubY >= self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]
                        ):
                            continue
                        if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                            if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel and self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0] > 1:
                                subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCelPsuePsel[nSubX, nSubY]['lasClass_2_345_6']
                            elif self.aSubCeldasPuntoMiniSubCelPsel.shape[0]: # A extinguir
                                subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 9]
                        elif self.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]:
                            subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCel_Tlp[nSubX, nSubY]['lasClass_2_345_6']
                        self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_2_345_6'].write(str('%i ' % subCeldaPuntoMiniSubCel))
                    self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_2_345_6'].write('\n')
                self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_2_345_6'].close()

        if GLO.GLBLgrabarMiniSubCelClassOrig_Binaria:
            if not self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_Binaria'] is None:
                myClassArray = getattr(self, 'aSubCeldasPuntoMiniSubCelPsuePsel', None)
                for nSubY in reversed(range(self.nCeldasY * GLBNsubCeldasPorCelda)):
                    for nSubX in range(self.nCeldasX * GLBNsubCeldasPorCelda):
                        if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                            nSubX >= self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]
                            or nSubY >= self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]
                        ):
                            continue
                        if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                            if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel and self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0] > 1:
                                subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCelPsuePsel[nSubX, nSubY]['lasClass_Binaria']
                            elif self.aSubCeldasPuntoMiniSubCelPsel.shape[0]: # A extinguir
                                subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 10]
                        elif self.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]:
                            subCeldaPuntoMiniSubCel = self.aSubCeldasPuntoMiniSubCel_Tlp[nSubX, nSubY]['lasClass_Binaria']
                        self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_Binaria'].write(str('%i ' % subCeldaPuntoMiniSubCel))
                    self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_Binaria'].write('\n')
                self.aFiles['SubCeldasPuntoMiniSubCelPsuePsel_classOrig_Binaria'].close()

        if GLO.GLBLgrabarDiscrepanciaCartoRefVsLasClassMiniSub:
            if not self.aFiles['SubCeldasDiscrepanciaCartoRefVsLasClassMiniSubCel'] is None:
                myClassArray = getattr(self, 'aSubCeldasPuntoMiniSubCelPsuePsel', None)
                for nSubY in reversed(range(self.nCeldasY * GLBNsubCeldasPorCelda)):
                    for nSubX in range(self.nCeldasX * GLBNsubCeldasPorCelda):
                        if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                            nSubX >= self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0]
                            or nSubY >= self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[1]
                        ):
                            continue
                        if GLO.GLBLusarMiniSubCelPselEnVezDeTlp:
                            if GLO.GLBLusarFormatoDtypeMaxiMiniSubCel and self.aSubCeldasPuntoMiniSubCelPsuePsel.shape[0] > 1:
                                lasClassOriginal = np.uint8(self.aSubCeldasPuntoMiniSubCelPsuePsel[nSubX, nSubY]['lasClassOriginal'])
                                singularUse8bits = np.uint8(self.aSubCeldasPuntoMiniSubCelPsuePsel[nSubX, nSubY]['usoSingular'])
                            elif self.aSubCeldasPuntoMiniSubCelPsel.shape[0]: # A extinguir
                                lasClassOriginal = np.uint8(self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 8])
                                singularUse8bits = np.uint8(self.aSubCeldasPuntoMiniSubCelPsel[nSubX, nSubY, 12])
                        elif self.aSubCeldasPuntoMiniSubCel_Tlp.shape[0]:
                            lasClassOriginal = np.uint8(self.aSubCeldasPuntoMiniSubCel_Tlp[nSubX, nSubY]['lasClassOriginal'])
                            singularUse8bits = np.uint8(self.aSubCeldasPuntoMiniSubCel_Tlp[nSubX, nSubY]['usoSingular'])
                        if lasClassOriginal == 6:
                            if singularUse8bits >= 100:
                                discrepancia = lasClassOriginal # lasClass_edificio vs cartoRef_edificio
                            else:
                                discrepancia = (lasClassOriginal * 10) + 2 # lasClass_edificio vs cartoRef_noEdificio
                        elif lasClassOriginal == 2:
                            if singularUse8bits < 100:
                                discrepancia = lasClassOriginal # lasClass_suelo vs cartoRef_noEdificio
                            else:
                                discrepancia = (lasClassOriginal * 10) + 6 # lasClass_Suelo vs cartoRef_edificio
                        elif lasClassOriginal == 3 or lasClassOriginal == 4 or lasClassOriginal == 5:
                            if singularUse8bits < 100:
                                discrepancia = lasClassOriginal # lasClass_vegetacion vs cartoRef_noEdificio
                            else:
                                discrepancia = (lasClassOriginal * 10) + 6 # lasClass_vegetacion vs cartoRef_edificio
                        else:
                            discrepancia = lasClassOriginal
                        self.aFiles['SubCeldasDiscrepanciaCartoRefVsLasClassMiniSubCel'].write(str('%i ' % discrepancia))
                    self.aFiles['SubCeldasDiscrepanciaCartoRefVsLasClassMiniSubCel'].write('\n')
                self.aFiles['SubCeldasDiscrepanciaCartoRefVsLasClassMiniSubCel'].close()


    # ==========================================================================
    # if GLO.GLBLcalcularMdp and GLO.GLBLcrearTilesPostVuelta1 and GLO.GLBLgrabarLandSubCelCoverPredict:
    def guardarLandSubCelCoverPredictA(self):
        # convolLasClassLandCover/CartoRefSingUse/CoverPredichoASubCel
        if not self.aFiles['SubCeldasCartoSinguLandTypePredichaA'] is None and self.aSubCeldasCartoSinguLandTypePredichaA.shape[0] > 1:
            for nY in reversed(range(self.aSubCeldasCartoSinguLandTypePredichaA.shape[1])):
                for nX in range(self.aSubCeldasCartoSinguLandTypePredichaA.shape[0]):
                    self.aFiles['SubCeldasCartoSinguLandTypePredichaA'].write(str('%i ' % self.aSubCeldasCartoSinguLandTypePredichaA[nX, nY]))
                self.aFiles['SubCeldasCartoSinguLandTypePredichaA'].write('\n')
            self.aFiles['SubCeldasCartoSinguLandTypePredichaA'].close()
        else:
            print('\t\t-> No es necesario guardar CoverPredichoASubCel xq ya existen esos ficheros')
        if GLO.GLBLgrabarMultiTiles:
            # convolLasClassLandCover/CartoRefSingUse/CoverPredichoBMultiTiles
            if not self.aFiles['MultiTilesCartoSinguLandTypePredichaB'] is None and self.aMultiTilesCartoSinguLandTypePredichaB.shape[0] > 1:
                for nY in reversed(range(self.aMultiTilesCartoSinguLandTypePredichaB.shape[1])):
                    for nX in range(self.aMultiTilesCartoSinguLandTypePredichaB.shape[0]):
                        self.aFiles['MultiTilesCartoSinguLandTypePredichaB'].write(str('%i ' % self.aMultiTilesCartoSinguLandTypePredichaB[nX, nY]))
                    self.aFiles['MultiTilesCartoSinguLandTypePredichaB'].write('\n')
                self.aFiles['MultiTilesCartoSinguLandTypePredichaB'].close()


    # ==========================================================================
    # if GLO.GLBLcalcularMdp and GLO.GLBLcrearTilesPostVuelta1 and GLO.GLBLgrabarLandSubCelCoverPredict:
    def guardarLandSubCelCoverPredictB(self):
        # convolLasClassLandCover/CartoRefSingUse/CoverPredichoBSubCel
        if not self.aFiles['SubCeldasCartoSinguLandTypePredichaB'] is None and self.aSubCeldasCartoSinguLandTypePredichaB.shape[0] > 1:
            for nY in reversed(range(self.aSubCeldasCartoSinguLandTypePredichaB.shape[1])):
                for nX in range(self.aSubCeldasCartoSinguLandTypePredichaB.shape[0]):
                    self.aFiles['SubCeldasCartoSinguLandTypePredichaB'].write(str('%i ' % self.aSubCeldasCartoSinguLandTypePredichaB[nX, nY]))
                self.aFiles['SubCeldasCartoSinguLandTypePredichaB'].write('\n')
            self.aFiles['SubCeldasCartoSinguLandTypePredichaB'].close()
        else:
            print('\t\t-> No es necesario guardar CoverPredichoBSubCel xq ya existen esos ficheros')
        if GLO.GLBLgrabarMultiTiles:
            # convolLasClassLandCover/CartoRefSingUse/CoverPredichoBMultiTiles
            if not self.aFiles['MultiTilesCartoSinguLandTypePredichaB'] is None and self.aMultiTilesCartoSinguLandTypePredichaB.shape[0] > 1:
                for nY in reversed(range(self.aMultiTilesCartoSinguLandTypePredichaB.shape[1])):
                    for nX in range(self.aMultiTilesCartoSinguLandTypePredichaB.shape[0]):
                        self.aFiles['MultiTilesCartoSinguLandTypePredichaB'].write(str('%i ' % self.aMultiTilesCartoSinguLandTypePredichaB[nX, nY]))
                    self.aFiles['MultiTilesCartoSinguLandTypePredichaB'].write('\n')
                self.aFiles['MultiTilesCartoSinguLandTypePredichaB'].close()


    # ==========================================================================
    def guardarMiscelaneaDasoLidar(self):

#         myClassArray = getattr(self, 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', None)
#                 if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
#                     nX >= self.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.shape[0]
#                     or nY >= self.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.shape[1]
#                 ):
#                     continue

        if GLO.GLBLgrabarPercentilesAbsolutos:
            if not self.aFiles['zMin10'] is None and self.aCeldasCotaMin10.shape[0] > 1:
                for nY in reversed(range(self.aCeldasCotaMin10.shape[1])):
                    for nX in range(self.aCeldasCotaMin10.shape[0]):
                        self.aFiles['zMin10'].write('%0.02f ' % self.aCeldasCotaMin10[nX, nY])
                    self.aFiles['zMin10'].write('\n')
                self.aFiles['zMin10'].close()
            if not self.aFiles['zMax95'] is None and self.aCeldasCotaMax95.shape[0] > 1:
                for nY in reversed(range(self.aCeldasCotaMax95.shape[1])):
                    for nX in range(self.aCeldasCotaMax95.shape[0]):
                        self.aFiles['zMax95'].write('%0.02f ' % self.aCeldasCotaMax95[nX, nY])
                    self.aFiles['zMax95'].write('\n')
                self.aFiles['zMax95'].close()
            if not self.aFiles['zRango10a95'] is None and self.aCeldasCotaMax95.shape[0] > 1:
                for nY in reversed(range(self.aCeldasCotaMax95.shape[1])):
                    for nX in range(self.aCeldasCotaMax95.shape[0]):
                        if self.aCeldasCotaMax95[nX, nY] != -9999:
                            self.aFiles['zRango10a95'].write('%0.02f ' % (self.aCeldasCotaMax95[nX, nY] - self.aCeldasCotaMin10[nX, nY]))
                        else:
                            self.aFiles['zRango10a95'].write(str(GLO.GLBLnoData) + ' ')
                    self.aFiles['zRango10a95'].write('\n')
                self.aFiles['zRango10a95'].close()
            if GLO.GLBLcalcularMds:
                if not self.aFiles['zRangoDesdeMediaSueloHasta95'] is None and self.aCeldasCotaMax95.shape[0] > 1:
                    for nY in reversed(range(self.aCeldasCotaMax95.shape[1])):
                        for nX in range(self.aCeldasCotaMax95.shape[0]):
                            if self.aCeldasCotaMax95[nX, nY] != -9999 and self.aCeldasCotaMediaTlrSueTlp[nX, nY] != -9999:
                                self.aFiles['zRangoDesdeMediaSueloHasta95'].write('%0.02f ' % (self.aCeldasCotaMax95[nX, nY] - self.aCeldasCotaMediaTlrSueTlp[nX, nY]))
                            else:
                                self.aFiles['zRangoDesdeMediaSueloHasta95'].write(str(GLO.GLBLnoData) + ' ')
                        self.aFiles['zRangoDesdeMediaSueloHasta95'].write('\n')
                    self.aFiles['zRangoDesdeMediaSueloHasta95'].close()


        if GLO.GLBLcalcularMds:
            # 1. Cobertura en porcentaje de primeros retornos que estan por encima de cada altura (para ordenRango = 0: 100%)
            if GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmds:
                # FccRptoAmds_MasDeXXXX_PrimerosRetornos
                tipoFCC = 'FccRptoAmds_PrimeRets_MasDe'
                ordenRango = 0
                for miAltura in self.listaRangos_AlturasMasDe[:-1]:
                    fileText = '{}{:04}'.format(
                        tipoFCC,
                        int(miAltura * 100)
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds.shape[1])):
                            for nX in range(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds.shape[0]):
                                if self.aCeldasCoeficientesMds[nX, nY, 3] != -1 and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccSobreAltInferiorAporcentaje
                                        and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds[nX, nY, ordenRango] < GLO.GLBLdescartarFccSobreAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmds[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 2. Cobertura en porcentaje de primeros retornos que estan entre esa altura y la siguiente del rango
            if GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmds:
                # FccRptoAmds_XXXX-YYYY_PrimerosRetornos
                tipoFCC = 'FccRptoAmds_PrimeRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                    miAltura1 = self.listaRangos_AlturasRango[nRango]
                    miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                    fileText = '{}_{:04}_{:04}'.format(
                        tipoFCC,
                        int(miAltura1 * 100),
                        int(miAltura2 * 100),
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumPrimerosRetornosAltRangoRptoAmds.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumPrimerosRetornosAltRangoRptoAmds.shape[1])):
                            for nX in range(self.aCeldasNumPrimerosRetornosAltRangoRptoAmds.shape[0]):
                                if self.aCeldasCoeficientesMds[nX, nY, 3] != -1 and self.aCeldasNumPrimerosRetornosAltRangoRptoAmds[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumPrimerosRetornosAltRangoRptoAmds[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write(str(self.aCeldasNumPrimerosRetornosAltRangoRptoAmds[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 3. Cobertura en porcentaje de todos retornos que estan entre esa altura y la siguiente del rango
            if GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmds:
                # FccRptoAmds_XXXX-YYYY_TodosLosRetornos
                tipoFCC = 'FccRptoAmds_TodosRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                    miAltura1 = self.listaRangos_AlturasRango[nRango]
                    miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                    fileText = '{}_{:04}_{:04}'.format(
                        tipoFCC,
                        int(miAltura1 * 100),
                        int(miAltura2 * 100),
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumTodosLosRetornosAltRangoRptoAmds.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumTodosLosRetornosAltRangoRptoAmds.shape[1])):
                            for nX in range(self.aCeldasNumTodosLosRetornosAltRangoRptoAmds.shape[0]):
                                if self.aCeldasCoeficientesMds[nX, nY, 3] != -1 and self.aCeldasNumTodosLosRetornosAltRangoRptoAmds[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumTodosLosRetornosAltRangoRptoAmds[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumTodosLosRetornosAltRangoRptoAmds[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1

        if GLO.GLBLcalcularMdb:
            # 1. Cobertura en porcentaje de primeros retornos que estan por encima de cada altura (para ordenRango = 0: 100%)
            if GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmdb:
                # FccRptoAmdb_MasDeXXXX_PrimerosRetornos
                tipoFCC = 'FccRptoAmdb_PrimeRets_MasDe'
                ordenRango = 0
                for miAltura in self.listaRangos_AlturasMasDe[:-1]:
                    fileText = '{}{:04}'.format(
                        tipoFCC,
                        int(miAltura * 100)
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb.shape[1])):
                            for nX in range(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb.shape[0]):
                                if self.aCeldasCoeficientesMdb_[nX, nY, 3] != -1 and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccSobreAltInferiorAporcentaje
                                        and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb[nX, nY, ordenRango] < GLO.GLBLdescartarFccSobreAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdb[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 2. Cobertura en porcentaje de primeros retornos que estan entre esa altura y la siguiente del rango
            if GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmdb:
                # FccRptoAmdb_XXXX-YYYY_PrimerosRetornos
                tipoFCC = 'FccRptoAmdb_PrimeRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                    miAltura1 = self.listaRangos_AlturasRango[nRango]
                    miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                    fileText = '{}_{:04}_{:04}'.format(
                        tipoFCC,
                        int(miAltura1 * 100),
                        int(miAltura2 * 100),
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb.shape[1])):
                            for nX in range(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb.shape[0]):
                                if self.aCeldasCoeficientesMdb_[nX, nY, 3] != -1 and self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdb[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 3. Cobertura en porcentaje de todos retornos que estan entre esa altura y la siguiente del rango
            if GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmdb:
                # FccRptoAmdb_XXXX-YYYY_TodosLosRetornos
                tipoFCC = 'FccRptoAmdb_TodosRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                    miAltura1 = self.listaRangos_AlturasRango[nRango]
                    miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                    fileText = '{}_{:04}_{:04}'.format(
                        tipoFCC,
                        int(miAltura1 * 100),
                        int(miAltura2 * 100),
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb.shape[1])):
                            for nX in range(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb.shape[0]):
                                if self.aCeldasCoeficientesMdb_[nX, nY, 3] != -1 and self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdb[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 4. Cobertura en porcentaje de todos retornos rpto a puntos en dosel superior que estan entre una altura y la siguiente del rango, con algunos rangos en % de Hdom
            # Rangos usados:
            #   listaRangos_AlturasPctjNum = [50, 200, 10050, 10100]
            #   listaRangos_AlturasPctjTxt = ['050cm', '200cm', '50%HD', 'TopHD']
            if GLO.GLBLgrabarFccPorPctjDeAltDomConTodosLosRetRptoAmdb:
                # FccRptoAmdb_XXXX-YYYY_TodosLosRetornos
                tipoFCC = 'FccRptoAmdb_TodosRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasPctjTxt) - 1):
                    miAltura1Txt = self.listaRangos_AlturasPctjTxt[nRango]
                    miAltura2Txt = self.listaRangos_AlturasPctjTxt[nRango + 1]
                    fileText = '{}_{}_{}'.format(tipoFCC, miAltura1Txt, miAltura2Txt)
                    if not self.aFiles[fileText] is None and self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb.shape[1])):
                            for nX in range(self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb.shape[0]):
                                if self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumTodosLosRetornosAltPctjRptoAmdb[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1

        if GLO.GLBLcalcularMdp:
            # 1. Cobertura en porcentaje de primeros retornos que estan por encima de cada altura (para ordenRango = 0: 100%)
            if GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmdf:
                # FccRptoAmdf_MasDeXXXX_PrimerosRetornos
                tipoFCC = 'FccRptoAmdf_PrimeRets_MasDe'
                ordenRango = 0
                for miAltura in self.listaRangos_AlturasMasDe[:-1]:
                    fileText = '{}{:04}'.format(
                        tipoFCC,
                        int(miAltura * 100)
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf.shape[0] > 1:
                        myClassArray = getattr(self, 'aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf', None)
                        for nY in reversed(range(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf.shape[1])):
                            for nX in range(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf.shape[0]):
                                if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                                    nX >= self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf.shape[0]
                                    or nY >= self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf.shape[1]
                                ):
                                    continue
                                if self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccSobreAltInferiorAporcentaje
                                        and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf[nX, nY, ordenRango] < GLO.GLBLdescartarFccSobreAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdf[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 2. Cobertura en porcentaje de primeros retornos que estan entre esa altura y la siguiente del rango
            if GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmdf:
                # FccRptoAmdf_XXXX-YYYY_PrimerosRetornos
                tipoFCC = 'FccRptoAmdf_PrimeRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                    miAltura1 = self.listaRangos_AlturasRango[nRango]
                    miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                    fileText = '{}_{:04}_{:04}'.format(
                        tipoFCC,
                        int(miAltura1 * 100),
                        int(miAltura2 * 100),
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf.shape[1])):
                            for nX in range(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf.shape[0]):
                                if self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdf[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 3. Cobertura en porcentaje de todos retornos que estan entre esa altura y la siguiente del rango
            if GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmdf:
                # FccRptoAmdf_XXXX-YYYY_TodosLosRetornos
                tipoFCC = 'FccRptoAmdf_TodosRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                    miAltura1 = self.listaRangos_AlturasRango[nRango]
                    miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                    fileText = '{}_{:04}_{:04}'.format(
                        tipoFCC,
                        int(miAltura1 * 100),
                        int(miAltura2 * 100),
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf.shape[1])):
                            for nX in range(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf.shape[0]):
                                if self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdf[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1

        if GLO.GLBLcalcularMdk2mConPuntosClasificados:
            # 1. Cobertura en porcentaje de primeros retornos que estan por encima de cada altura (para ordenRango = 0: 100%)
            if GLO.GLBLgrabarFccPorMayorDeAltConPrimerosRetRptoAmdk:
                # FccRptoAmdk_MasDeXXXX_PrimerosRetornos
                tipoFCC = 'FccRptoAmdk_PrimeRets_MasDe'
                ordenRango = 0
                for miAltura in self.listaRangos_AlturasMasDe[:-1]:
                    fileText = '{}{:04}'.format(
                        tipoFCC,
                        int(miAltura * 100)
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk.shape[0] > 1:
                        myClassArray = getattr(self, 'aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk', None)
                        for nY in reversed(range(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk.shape[1])):
                            for nX in range(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk.shape[0]):
                                if not myClassArray is None and isinstance(myClassArray, np.ndarray) and (
                                    nX >= self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk.shape[0]
                                    or nY >= self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk.shape[1]
                                ):
                                    continue
                                if self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccSobreAltInferiorAporcentaje
                                        and self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk[nX, nY, ordenRango] < GLO.GLBLdescartarFccSobreAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumPrimerosRetornosAltSuperiorRptoAmdk[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 2. Cobertura en porcentaje de primeros retornos que estan entre esa altura y la siguiente del rango
            if GLO.GLBLgrabarFccPorRangoDeAltConPrimerosRetRptoAmdk:
                # FccRptoAmdk_XXXX-YYYY_PrimerosRetornos
                tipoFCC = 'FccRptoAmdk_PrimeRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                    miAltura1 = self.listaRangos_AlturasRango[nRango]
                    miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                    fileText = '{}_{:04}_{:04}'.format(
                        tipoFCC,
                        int(miAltura1 * 100),
                        int(miAltura2 * 100),
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk.shape[1])):
                            for nX in range(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk.shape[0]):
                                if self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumPrimerosRetornosAltRangoRptoAmdk[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1
            # 3. Cobertura en porcentaje de todos retornos que estan entre esa altura y la siguiente del rango
            if GLO.GLBLgrabarFccPorRangoDeAltConTodosLosRetRptoAmdk:
                # FccRptoAmdk_XXXX-YYYY_TodosLosRetornos
                tipoFCC = 'FccRptoAmdk_TodosRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasRango) - 1):
                    miAltura1 = self.listaRangos_AlturasRango[nRango]
                    miAltura2 = self.listaRangos_AlturasRango[nRango + 1]
                    fileText = '{}_{:04}_{:04}'.format(
                        tipoFCC,
                        int(miAltura1 * 100),
                        int(miAltura2 * 100),
                    )
                    if not self.aFiles[fileText] is None and self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk.shape[1])):
                            for nX in range(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk.shape[0]):
                                if self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumTodosLosRetornosAltRangoRptoAmdk[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1

            listaGrabarFccPorPctjDe = [
                GLO.GLBLgrabarFccPorPctjDeAltDomConTodosLosRetRptoAmdb,
                GLO.GLBLgrabarFccPorPctjDeAltDomConTodosLosRetRptoAmdk
            ]
            # 4. Cobertura en porcentaje de todos retornos rpto a puntos en dosel superior que estan entre una altura y la siguiente del rango, con algunos rangos en % de Hdom
            # Rangos usados:
            #   listaRangos_AlturasPctjNum = [50, 200, 10050, 10100]
            #   listaRangos_AlturasPctjTxt = ['050cm', '200cm', '50%HD', 'TopHD']
            if GLO.GLBLgrabarFccPorPctjDeAltDomConTodosLosRetRptoAmdk:
                # FccRptoAmdk_XXXX-YYYY_TodosLosRetornos
                tipoFCC = 'FccRptoAmdk_TodosRets'
                ordenRango = 0
                for nRango in range(len(self.listaRangos_AlturasPctjTxt) - 1):
                    miAltura1Txt = self.listaRangos_AlturasPctjTxt[nRango]
                    miAltura2Txt = self.listaRangos_AlturasPctjTxt[nRango + 1]
                    fileText = '{}_{}_{}'.format(tipoFCC, miAltura1Txt, miAltura2Txt)
                    if not self.aFiles[fileText] is None and self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk.shape[0] > 1:
                        for nY in reversed(range(self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk.shape[1])):
                            for nX in range(self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk.shape[0]):
                                if self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk[nX, nY, ordenRango] >= 0:
                                    if (
                                        GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                        and self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk[nX, nY, ordenRango] < GLO.GLBLdescartarFccRangoAltInferiorAporcentaje
                                    ):
                                        self.aFiles[fileText].write('0 ')
                                    else:
                                        self.aFiles[fileText].write('{:02} '.format(self.aCeldasNumTodosLosRetornosAltPctjRptoAmdk[nX, nY, ordenRango]))
                                else:
                                    self.aFiles[fileText].write(str(GLO.GLBLnoData8bits) + ' ')
                            self.aFiles[fileText].write('\n')
                        self.aFiles[fileText].close()
                    ordenRango += 1


        if GLO.GLBLgrabarPercentilesRelativos and GLO.GLBLcalcularMds:
            if not self.aFiles['CeldasAlt95SobreMds'] is None and self.aCeldasAlt95SobreMds.shape[0] > 1:
                for nY in reversed(range(self.aCeldasAlt95SobreMds.shape[1])):
                    for nX in range(self.aCeldasAlt95SobreMds.shape[0]):
                        # AltSobreTerreno/10mCell/
                        if self.aCeldasAlt95SobreMds[nX, nY] == GLO.GLBLnoData:
                            self.aFiles['CeldasAlt95SobreMds'].write('%0.0f ' % GLO.GLBLnoData)
                        elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aCeldasAlt95SobreMds[nX, nY] < 0:
                            self.aFiles['CeldasAlt95SobreMds'].write('0.00 ')
                        else:
                            self.aFiles['CeldasAlt95SobreMds'].write('%0.02f ' % self.aCeldasAlt95SobreMds[nX, nY])
                    self.aFiles['CeldasAlt95SobreMds'].write('\n')
                self.aFiles['CeldasAlt95SobreMds'].close()
            if GLO.GLBLgrabarPercentilAdicional:
                if not self.aFiles['CeldasAlt{:02}SobreMds'.format(GLO.GLBLgrabarPercentilAdicional)] is None and self.aCeldasAltXxSobreMds.shape[0] > 1:
                    for nY in reversed(range(self.aCeldasAltXxSobreMds.shape[1])):
                        for nX in range(self.aCeldasAltXxSobreMds.shape[0]):
                            if self.aCeldasAltXxSobreMds[nX, nY] == GLO.GLBLnoData:
                                self.aFiles['CeldasAlt{:02}SobreMds'.format(GLO.GLBLgrabarPercentilAdicional)].write('%0.0f ' % GLO.GLBLnoData)
                            elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aCeldasAltXxSobreMds[nX, nY] < 0:
                                self.aFiles['CeldasAlt{:02}SobreMds'.format(GLO.GLBLgrabarPercentilAdicional)].write('0.00 ')
                            else:
                                self.aFiles['CeldasAlt{:02}SobreMds'.format(GLO.GLBLgrabarPercentilAdicional)].write('%0.02f ' % self.aCeldasAltXxSobreMds[nX, nY])
                        self.aFiles['CeldasAlt{:02}SobreMds'.format(GLO.GLBLgrabarPercentilAdicional)].write('\n')
                    self.aFiles['CeldasAlt{:02}SobreMds'.format(GLO.GLBLgrabarPercentilAdicional)].close()

        if GLO.GLBLgrabarPercentilesRelativos and GLO.GLBLcalcularMdb:
            if not self.aFiles['CeldasAlt95SobreMdb'] is None and self.aCeldasAlt95SobreMdb.shape[0] > 1:
                for nY in reversed(range(self.aCeldasAlt95SobreMdb.shape[1])):
                    for nX in range(self.aCeldasAlt95SobreMdb.shape[0]):
                        # AltSobreTerreno/10mCell/
                        if self.aCeldasAlt95SobreMdb[nX, nY] == GLO.GLBLnoData:
                            self.aFiles['CeldasAlt95SobreMdb'].write('%0.0f ' % GLO.GLBLnoData)
                        elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aCeldasAlt95SobreMdb[nX, nY] < 0:
                            self.aFiles['CeldasAlt95SobreMdb'].write('0.00 ')
                        else:
                            self.aFiles['CeldasAlt95SobreMdb'].write('%0.02f ' % self.aCeldasAlt95SobreMdb[nX, nY])
                    self.aFiles['CeldasAlt95SobreMdb'].write('\n')
                self.aFiles['CeldasAlt95SobreMdb'].close()
            if GLO.GLBLgrabarPercentilAdicional:
                if not self.aFiles['CeldasAlt{:02}SobreMdb'.format(GLO.GLBLgrabarPercentilAdicional)] is None and self.aCeldasAltXxSobreMdb.shape[0] > 1:
                    for nY in reversed(range(self.aCeldasAltXxSobreMdb.shape[1])):
                        for nX in range(self.aCeldasAltXxSobreMdb.shape[0]):
                        # AltSobreTerreno/10mCell/
                            if self.aCeldasAltXxSobreMdb[nX, nY] == GLO.GLBLnoData:
                                self.aFiles['CeldasAlt{:02}SobreMdb'.format(GLO.GLBLgrabarPercentilAdicional)].write('%0.0f ' % GLO.GLBLnoData)
                            elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aCeldasAltXxSobreMdb[nX, nY] < 0:
                                self.aFiles['CeldasAlt{:02}SobreMdb'.format(GLO.GLBLgrabarPercentilAdicional)].write('0.00 ')
                            else:
                                self.aFiles['CeldasAlt{:02}SobreMdb'.format(GLO.GLBLgrabarPercentilAdicional)].write('%0.02f ' % self.aCeldasAltXxSobreMdb[nX, nY])
                        self.aFiles['CeldasAlt{:02}SobreMdb'.format(GLO.GLBLgrabarPercentilAdicional)].write('\n')
                    self.aFiles['CeldasAlt{:02}SobreMdb'.format(GLO.GLBLgrabarPercentilAdicional)].close()

        if GLO.GLBLgrabarPercentilesRelativos and GLO.GLBLcalcularMdp:
            if not self.aFiles['CeldasAlt95SobreMdf'] is None and self.aCeldasAlt95SobreMdf.shape[0] > 1:
                for nY in reversed(range(self.aCeldasAlt95SobreMdf.shape[1])):
                    for nX in range(self.aCeldasAlt95SobreMdf.shape[0]):
                        # AltSobreTerreno/10mCell/
                        if self.aCeldasAlt95SobreMdf[nX, nY] == GLO.GLBLnoData:
                            self.aFiles['CeldasAlt95SobreMdf'].write('%0.0f ' % GLO.GLBLnoData)
                        elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aCeldasAlt95SobreMdf[nX, nY] < 0:
                            self.aFiles['CeldasAlt95SobreMdf'].write('0.00 ')
                        else:
                            self.aFiles['CeldasAlt95SobreMdf'].write('%0.02f ' % self.aCeldasAlt95SobreMdf[nX, nY])
                    self.aFiles['CeldasAlt95SobreMdf'].write('\n')
                self.aFiles['CeldasAlt95SobreMdf'].close()
            if GLO.GLBLgrabarPercentilAdicional:
                if not self.aFiles['CeldasAlt{:02}SobreMdf'.format(GLO.GLBLgrabarPercentilAdicional)] is None and self.aCeldasAltXxSobreMdf.shape[0] > 1:
                    for nY in reversed(range(self.aCeldasAltXxSobreMdf.shape[1])):
                        for nX in range(self.aCeldasAltXxSobreMdf.shape[0]):
                            # AltSobreTerreno/10mCell/
                            if self.aCeldasAltXxSobreMdf[nX, nY] == GLO.GLBLnoData:
                                self.aFiles['CeldasAlt{:02}SobreMdf'.format(GLO.GLBLgrabarPercentilAdicional)].write('%0.0f ' % GLO.GLBLnoData)
                            elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aCeldasAltXxSobreMdf[nX, nY] < 0:
                                self.aFiles['CeldasAlt{:02}SobreMdf'.format(GLO.GLBLgrabarPercentilAdicional)].write('0.00 ')
                            else:
                                self.aFiles['CeldasAlt{:02}SobreMdf'.format(GLO.GLBLgrabarPercentilAdicional)].write('%0.02f ' % self.aCeldasAltXxSobreMdf[nX, nY])
                        self.aFiles['CeldasAlt{:02}SobreMdf'.format(GLO.GLBLgrabarPercentilAdicional)].write('\n')
                    self.aFiles['CeldasAlt{:02}SobreMdf'.format(GLO.GLBLgrabarPercentilAdicional)].close()

        if GLO.GLBLgrabarPercentilesRelativos and GLO.GLBLcalcularMdk2mConPuntosClasificados:
            if not self.aFiles['CeldasAlt95SobreMdk'] is None and self.aCeldasAlt95SobreMdk.shape[0] > 1:
                for nY in reversed(range(self.aCeldasAlt95SobreMdk.shape[1])):
                    for nX in range(self.aCeldasAlt95SobreMdk.shape[0]):
                        # AltSobreTerreno/10mCell/
                        if self.aCeldasAlt95SobreMdk[nX, nY] == GLO.GLBLnoData:
                            self.aFiles['CeldasAlt95SobreMdk'].write('%0.0f ' % GLO.GLBLnoData)
                        elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aCeldasAlt95SobreMdk[nX, nY] < 0:
                            self.aFiles['CeldasAlt95SobreMdk'].write('0.00 ')
                        else:
                            self.aFiles['CeldasAlt95SobreMdk'].write('%0.02f ' % self.aCeldasAlt95SobreMdk[nX, nY])
                    self.aFiles['CeldasAlt95SobreMdk'].write('\n')
                self.aFiles['CeldasAlt95SobreMdk'].close()
            if GLO.GLBLgrabarPercentilAdicional:
                if not self.aFiles['CeldasAlt{:02}SobreMdk'.format(GLO.GLBLgrabarPercentilAdicional)] is None and self.aCeldasAltXxSobreMdk.shape[0] > 1:
                    for nY in reversed(range(self.aCeldasAltXxSobreMdk.shape[1])):
                        for nX in range(self.aCeldasAltXxSobreMdk.shape[0]):
                            # AltSobreTerreno/10mCell/
                            if self.aCeldasAltXxSobreMdk[nX, nY] == GLO.GLBLnoData:
                                self.aFiles['CeldasAlt{:02}SobreMdk'.format(GLO.GLBLgrabarPercentilAdicional)].write('%0.0f ' % GLO.GLBLnoData)
                            elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aCeldasAltXxSobreMdk[nX, nY] < 0:
                                self.aFiles['CeldasAlt{:02}SobreMdk'.format(GLO.GLBLgrabarPercentilAdicional)].write('0.00 ')
                            else:
                                self.aFiles['CeldasAlt{:02}SobreMdk'.format(GLO.GLBLgrabarPercentilAdicional)].write('%0.02f ' % self.aCeldasAltXxSobreMdk[nX, nY])
                        self.aFiles['CeldasAlt{:02}SobreMdk'.format(GLO.GLBLgrabarPercentilAdicional)].write('\n')
                    self.aFiles['CeldasAlt{:02}SobreMdk'.format(GLO.GLBLgrabarPercentilAdicional)].close()

        if GLO.GLBLcalcularMdp:
            if GLO.GLBLgrabarPercentilesSubCeldas:
                # AltSobreTerreno/02mCell95/
                if not self.aFiles['SubCeldasAlt95SobreMdf'] is None and self.aSubCeldasAlt95SobreMdf.shape[0] > 1:
                    for nY in reversed(range(self.aSubCeldasAlt95SobreMdf.shape[1])):
                        for nX in range(self.aSubCeldasAlt95SobreMdf.shape[0]):
                            if self.aSubCeldasAlt95SobreMdf[nX, nY] == GLO.GLBLnoData:
                                self.aFiles['SubCeldasAlt95SobreMdf'].write('%0.0f ' % GLO.GLBLnoData)
                            elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aSubCeldasAlt95SobreMdf[nX, nY] < 0:
                                self.aFiles['SubCeldasAlt95SobreMdf'].write('0.00 ')
                            else:
                                self.aFiles['SubCeldasAlt95SobreMdf'].write('%0.02f ' % round(self.aSubCeldasAlt95SobreMdf[nX, nY], 2))
                        self.aFiles['SubCeldasAlt95SobreMdf'].write('\n')
                    self.aFiles['SubCeldasAlt95SobreMdf'].close()

            if GLO.GLBLgrabarSubCeldasAltMaxSobreMdf:
                # AltSobreTerreno/02mCellMinMax/
                if not self.aFiles['SubCeldasAltMaxSobreMdf'] is None and self.aSubCeldasAltMaxSobreMdf.shape[0] > 1:
                    for nY in reversed(range(self.aSubCeldasAltMaxSobreMdf.shape[1])):
                        for nX in range(self.aSubCeldasAltMaxSobreMdf.shape[0]):
                            if self.aSubCeldasAltMaxSobreMdf[nX, nY] == GLO.GLBLnoData:
                                self.aFiles['SubCeldasAltMaxSobreMdf'].write('%0.0f ' % GLO.GLBLnoData)
                            elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aSubCeldasAltMaxSobreMdf[nX, nY] < 0:
                                self.aFiles['SubCeldasAltMaxSobreMdf'].write('0.00 ')
                            else:
                                self.aFiles['SubCeldasAltMaxSobreMdf'].write('%0.02f ' % round(self.aSubCeldasAltMaxSobreMdf[nX, nY], 2))
                        self.aFiles['SubCeldasAltMaxSobreMdf'].write('\n')
                    self.aFiles['SubCeldasAltMaxSobreMdf'].close()


        if GLO.GLBLcalcularMdk2mConPuntosClasificados:
            if GLO.GLBLgrabarPercentilesSubCeldas:
                # AltSobreTerreno/02mCell95/
                if not self.aFiles['SubCeldasAlt95SobreMdk'] is None and self.aSubCeldasAlt95SobreMdk.shape[0] > 1:
                    for nY in reversed(range(self.aSubCeldasAlt95SobreMdk.shape[1])):
                        for nX in range(self.aSubCeldasAlt95SobreMdk.shape[0]):
                            if self.aSubCeldasAlt95SobreMdk[nX, nY] == GLO.GLBLnoData:
                                self.aFiles['SubCeldasAlt95SobreMdk'].write('%0.0f ' % GLO.GLBLnoData)
                            elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aSubCeldasAlt95SobreMdk[nX, nY] < 0:
                                self.aFiles['SubCeldasAlt95SobreMdk'].write('0.00 ')
                            else:
                                self.aFiles['SubCeldasAlt95SobreMdk'].write('%0.02f ' % round(self.aSubCeldasAlt95SobreMdk[nX, nY], 2))
                        self.aFiles['SubCeldasAlt95SobreMdk'].write('\n')
                    self.aFiles['SubCeldasAlt95SobreMdk'].close()

            if GLO.GLBLgrabarSubCeldasAltMaxSobreMdk:
                # AltSobreTerreno/02mCellMinMax/
                if not self.aFiles['SubCeldasAltMaxSobreMdk'] is None and self.aSubCeldasAltMaxSobreMdk.shape[0] > 1:
                    for nY in reversed(range(self.aSubCeldasAltMaxSobreMdk.shape[1])):
                        for nX in range(self.aSubCeldasAltMaxSobreMdk.shape[0]):
                            if self.aSubCeldasAltMaxSobreMdk[nX, nY] == GLO.GLBLnoData:
                                self.aFiles['SubCeldasAltMaxSobreMdk'].write('%0.0f ' % GLO.GLBLnoData)
                            elif GLO.GLBLgrabarAlturasNegativasSobreTerrenoA0 and self.aSubCeldasAltMaxSobreMdk[nX, nY] < 0:
                                self.aFiles['SubCeldasAltMaxSobreMdk'].write('0.00 ')
                            else:
                                self.aFiles['SubCeldasAltMaxSobreMdk'].write('%0.02f ' % round(self.aSubCeldasAltMaxSobreMdk[nX, nY], 2))
                        self.aFiles['SubCeldasAltMaxSobreMdk'].write('\n')
                    self.aFiles['SubCeldasAltMaxSobreMdk'].close()


    # ==========================================================================
    def escribirEnDisco(
            self,
            escribirLote='',
            cartoRefClass=None,
            npzFileNameArrays_myLasData='',
            npzFileNameArrayPralPF99_myLasData='',
            npzFileNameArraysVuelta0a1_myLasData='',
            npzFileNameArraysVuelta2a9_myLasData='',
            etapa=0, nTPini=0, nTPfin=0, cTP=None,
            nInterpol=0,
            prePostInterpol=0,
            lasOrigRecl='Orig',
            fileCoordYear='',
        ):

        nIntentosEscritura = 0
        while True:
            nIntentosEscritura += 1
#             breakPoint = escribirLote
#             try:
            if True:
                # ==============================================================
                if escribirLote == 'guardarNucleosDeCartoRef':
                    if GLO.GLBLgrabarNucleosDeCartoRef and cartoRefClass.usarVectorRef:
                        print('\tcliddata.&{}-> SI se guardan los nucleos urbanos de cartografia de referencia.'.format(fileCoordYear))
                        self.guardarNucleosDeCartoRef(cartoRefClass.aCeldasLandUseCover)
                    else:
                        print('\tcliddata.&{}-> No se guardan los nucleos urbanos de cartografia de referencia.'.format(fileCoordYear))

                # ==============================================================
                elif escribirLote == 'guardarSingUseDeCartoRef':
                    if GLO.GLBLgrabarSingUseDeCartoRef and cartoRefClass.usarVectorRef:
                        print('\tcliddata.&{}-> SI se guardan los usos singulares de cartografia de referencia.'.format(fileCoordYear))
                        self.guardarSingUseDeCartoRef(cartoRefClass.aCeldasLandUseCover)
                    else:
                        print('\tcliddata.&{}-> NO se guardan usos singulares de cartografia de referencia.'.format(fileCoordYear))

                # ==============================================================
                elif escribirLote == 'guardarIndicesIRGBIrISubCelda':
                    if GLO.GLBLgrabarIndicesVegetacionNDVIetAlSubCelda:  # GBI/SubCelda***/
                        clidaux.printMsg('cliddata.&{}-> Se van a guardar en fichero ASC los indices de subCelda basados en RGB Ir e intensity en las capas correspondientes'.format(fileCoordYear))
                        clidaux.printMsg('\t\t-> Ficheros RGBI/02mCell/***: SubCeldasIntSRetMed, SubCeldasIntMRetMed, subCeldasEVI2, subCeldasNDVI, subCeldasNDWI')
                        tiempoPreGuardarIndicesIRGBIrI = time.time()
                        # ==============================================================
                        self.guardarIndicesIRGBIrISubCelda()
                        # ==============================================================
                        tiempoPostGuardarIndicesIRGBIrI = time.time()
                        segundosDuracion = round(tiempoPostGuardarIndicesIRGBIrI - tiempoPreGuardarIndicesIRGBIrI, 1)
                        minutosDuracion = round(segundosDuracion / 60.0, 1)
                        clidaux.printMsg(
                            '\t\tTiempo para guardar los indices basados en RGB Ir e intensity en las capas de subcelda correspondientes: {:0.1f} segundos ({:0.1f} minutos)'
                           .format(segundosDuracion, minutosDuracion)
                        )
                    else:
                        print(
                            'cliddata.&{}-> No se guardan en fichero los indices basados en RGB Ir e intensity de cada subcelda (cambiar GLBLgrabarIndicesVegetacionNDVIetAlSubCelda para guardarlos)'.format(fileCoordYear)
                        )

                # ==============================================================
                elif escribirLote == 'guardarIndicesIRGBIrIMetricos':
                    if GLO.GLBLgrabarIndicesVegetacionNDVIetAlMetricos:  # RGBI/Metrico***/
                        clidaux.printMsg('\t-> cliddata.&{}-> Se van a guardar en fichero los indices metricos basados en RGB Ir e intensity en las capas correspondientes'.format(fileCoordYear))
                        clidaux.printMsg('\t\t-> Ficheros RGBI/01mCell/***: MetricoIntSRetMed, MetricoIntMRetMed, MetricoEVI2, MetricoNDVI, MetricoNDWI')
                        tiempoPreGuardarIndicesIRGBIrI = time.time()
                        # ==============================================================
                        self.guardarIndicesIRGBIrIMetricos()
                        # ==============================================================
                        tiempoPostGuardarIndicesIRGBIrI = time.time()
                        segundosDuracion = round(tiempoPostGuardarIndicesIRGBIrI - tiempoPreGuardarIndicesIRGBIrI, 1)
                        minutosDuracion = round(segundosDuracion / 60.0, 1)
                        clidaux.printMsg(
                            '\t\tTiempo para guardar los indices basados en RGB Ir e intensity en las capas correspondientes: {:0.1f} segundos ({:0.1f} minutos)'
                           .format(segundosDuracion, minutosDuracion)
                        )
                    else:
                        print(
                            'cliddata.&{}-> No se guardan en fichero los indices basados en RGB Ir e intensity por metro cuadrado (cambiar GLBLgrabarIndicesVegetacionNDVIetAlMetricos para guardarlos).format(fileCoordYear).format(fileCoordYear)'.format(fileCoordYear)
                        )

                # ==============================================================
                elif escribirLote == 'guardarNumPuntosPorClasesCeldas':
                    if GLO.GLBLgrabarNumeroPuntosPorClase:
                        clidaux.printMsg('\t-> cliddata.&{}-> Se van a guardar en fichero datos de numero de puntos por clase original por celda, tras la vuelta 0'.format(fileCoordYear))
                        clidaux.printMsg('\t\t-> Ficheros PointClass/Orig/10mCell/Suelo/***, PointClass/Orig/10mCell/Edificio/***, PointClass/Orig/10mCell/Otros/***')
                        tiempoPreGuardarNumPuntosPorClasesCeldas = time.time()
                        # ==============================================================
                        self.guardarNumPuntosPorClasesCeldas(lasOrigRecl)
                        # ==============================================================
                        tiempoPostGuardarNumPuntosPorClasesCeldas = time.time()
                        segundosDuracion = round(tiempoPostGuardarNumPuntosPorClasesCeldas - tiempoPreGuardarNumPuntosPorClasesCeldas, 1)
                        minutosDuracion = round(segundosDuracion / 60.0, 1)
                        clidaux.printMsg(
                            '\t\tTiempo para guardar las clases en las capas de celda correspondientes: {:0.1f} segundos ({:0.1f} minutos)'.format(
                                segundosDuracion, minutosDuracion))
                    else:
                        print(
                            'cliddata.&{}-> No se guardan en fichero las clases en capas Celdas: {} {} {}'.format(
                                fileCoordYear,
                                GLO.GLBLgrabarSubCeldasClasesSueloVegetacion,
                                GLO.GLBLgrabarSubCeldasClasesEdificio,
                                GLO.GLBLgrabarSubCeldasClasesOtros
                            )
                        )

                # ==============================================================
                elif escribirLote == 'guardarClasesCeldas':
                    if GLO.GLBLgrabarCeldasClasesSueloVegetacion or GLO.GLBLgrabarCeldasClasesEdificio or GLO.GLBLgrabarCeldasClasesOtros:
                        clidaux.printMsg('\t-> cliddata.&{}-> Se van a guardar en fichero datos de numero de puntos por clase original por celda, tras la vuelta 0'.format(fileCoordYear))
                        clidaux.printMsg('\t\t-> Ficheros PointClass/Orig/10mCell/Suelo/***, PointClass/Orig/10mCell/Edificio/***, PointClass/Orig/10mCell/Otros/***')
                        tiempoPreGuardarClasesCeldas = time.time()
                        # ==============================================================
                        self.guardarClasesCeldas(lasOrigRecl)
                        # ==============================================================
                        tiempoPostGuardarClasesCeldas = time.time()
                        segundosDuracion = round(tiempoPostGuardarClasesCeldas - tiempoPreGuardarClasesCeldas, 1)
                        minutosDuracion = round(segundosDuracion / 60.0, 1)
                        clidaux.printMsg(
                            '\t\tTiempo para guardar las clases en las capas de celda correspondientes: {:0.1f} segundos ({:0.1f} minutos)'.format(
                                segundosDuracion, minutosDuracion))
                    else:
                        print(
                            'cliddata.&{}-> No se guardan en fichero las clases en capas Celdas: {} {} {}'.format(
                                fileCoordYear,
                                GLO.GLBLgrabarSubCeldasClasesSueloVegetacion,
                                GLO.GLBLgrabarSubCeldasClasesEdificio,
                                GLO.GLBLgrabarSubCeldasClasesOtros
                            )
                        )

                # ==============================================================
                elif escribirLote == 'guardarClasesSubCeldas':
                    if GLO.GLBLgrabarSubCeldasClasesSueloVegetacion or GLO.GLBLgrabarSubCeldasClasesEdificio or GLO.GLBLgrabarSubCeldasClasesOtros:
                        clidaux.printMsg('\t-> cliddata.&{}-> Se van a guardar en fichero las clases en capas subCeldas en PointClass/Orig/SubCeldas/...'.format(fileCoordYear))
                        clidaux.printMsg('\t\t-> Ficheros PointClass/Orig/02mCell/Suelo/***, PointClass/Orig/02mCell/Edificio/***, PointClass/Orig/02mCell/Otros/***')
                        tiempoPreGuardarClasesSubCeldas = time.time()
                        # ==============================================================
                        self.guardarClasesSubCeldas(lasOrigRecl)
                        # ==============================================================
                        tiempoPostGuardarClasesSubCeldas = time.time()
                        segundosDuracion = round(tiempoPostGuardarClasesSubCeldas - tiempoPreGuardarClasesSubCeldas, 1)
                        minutosDuracion = round(segundosDuracion / 60.0, 1)
                        clidaux.printMsg(
                            '\t\tTiempo para guardar las clases en las capas de subcelda correspondientes: {:0.1f} segundos ({:0.1f} minutos)'.format(
                                segundosDuracion, minutosDuracion))
                    else:
                        print(
                            'cliddata.&{}-> No se guardan en fichero las clases en capas subCeldas: {} {} {}'.format(
                                fileCoordYear,
                                GLO.GLBLgrabarSubCeldasClasesSueloVegetacion,
                                GLO.GLBLgrabarSubCeldasClasesEdificio,
                                GLO.GLBLgrabarSubCeldasClasesOtros
                            )
                        )

                # ==============================================================
                elif escribirLote == 'guardarClasesMetricos':
                    if GLO.GLBLgrabarMetricoClasesSueloVegetacion or GLO.GLBLgrabarMetricoClasesEdificio or GLO.GLBLgrabarMetricoClasesOtros:
                        clidaux.printMsg('\t-> cliddata.&{}-> Se van a guardar en fichero las clases en capas metricas en PointClass/Orig/metrico/...'.format(fileCoordYear))
                        clidaux.printMsg('\t\t-> Ficheros PointClass/Orig/01mCell/Suelo/***, PointClass/Orig/01mCell/Edificio/***, PointClass/Orig/01mCell/Otros/***')
                        tiempoPreGuardarClasesMetricos = time.time()
                        # ==============================================================
                        self.guardarClasesMetricos(lasOrigRecl)
                        # ==============================================================
                        tiempoPostGuardarClasesMetricos = time.time()
                        segundosDuracion = round(tiempoPostGuardarClasesMetricos - tiempoPreGuardarClasesMetricos, 1)
                        minutosDuracion = round(segundosDuracion / 60.0, 1)
                        clidaux.printMsg(
                            '\t\tTiempo para guardar las clases en capas metricas: {:0.1f} segundos ({:0.1f} minutos)'.format(
                                segundosDuracion, minutosDuracion))
                    else:
                        print('\tcliddata.&{}-> No se guardan en fichero las clases en capas metricas'.format(fileCoordYear))

                # ==============================================================
                elif escribirLote == 'guardarMiscelaneaVuelta0':
                    self.guardarMiscelaneaVuelta0()

                # ==============================================================
                elif escribirLote == 'guardarArrayPralPF99_myLasData':
                    self.guardarArrayPralPF99_myLasData(npzFileNameArrays_myLasData)

                # ==============================================================
                elif escribirLote == 'guardarArrayExtrVars_myLasData':
                    self.guardarArrayExtrVars_myLasData(npzFileNameArrays_myLasData)

                # ==============================================================
                elif escribirLote == 'guardarArraysCartoSinguLandTypePredicha_myLasData':
                    self.guardarArraysCartoSinguLandTypePredicha_myLasData(npzFileNameArrays_myLasData)

                # ==============================================================
                elif escribirLote == 'guardarArraysMiniSubCel_myLasData':
                    self.guardarArraysMiniSubCel_myLasData(npzFileNameArrays_myLasData)

                # ==============================================================
                elif escribirLote == 'guardarArraysTrasVuelta0a1_myLasData':
                    self.guardarArraysTrasVuelta0a1_myLasData(npzFileNameArrays_myLasData)

                # ==============================================================
                elif escribirLote == 'guardarArraysTrasVuelta2a9_myLasData':
                    self.guardarArraysTrasVuelta2a9_myLasData(npzFileNameArrays_myLasData)

                # ==============================================================
                elif escribirLote == 'guardarAgua':
                    self.guardarAgua()

                # ==============================================================
                elif escribirLote == 'guardarMdgSubCelda':
                    self.guardarMdgSubCelda()

                # ==============================================================
                elif escribirLote == 'guardarMiscelaneaVuelta1':
                    self.guardarMiscelaneaVuelta1()

                # ==============================================================
                elif escribirLote == 'guardarMiniSubCelClassOriginal':
                    print('\tcliddata.&{}-> Guardando en ASC miniSubCel class original'.format(fileCoordYear))
                    self.guardarMiniSubCelClassOriginal()

                # ==============================================================
                elif escribirLote == 'guardarMiniSubCelClassPredict':
                    print('\tcliddata.&{}-> Guardando en ASC miniSubCel class predicha con el modelo CNN y los tiles creados'.format(fileCoordYear))
                    self.guardarMiniSubCelClassPredict()

                # ==============================================================
                elif escribirLote == 'guardarLandSubCelCoverPredictA':
                    print('\tcliddata.&{}-> Guardando en ASC usos singulares predichos A con el modelo CNN y los tiles creados'.format(fileCoordYear))
                    self.guardarLandSubCelCoverPredictA()

                # ==============================================================
                elif escribirLote == 'guardarLandSubCelCoverPredictB':
                    print('\tcliddata.&{}-> Guardando en ASC usos singulares predichos B con el modelo CNN y los tiles creados'.format(fileCoordYear))
                    self.guardarLandSubCelCoverPredictB()

                # ==============================================================
                elif escribirLote == 'guardarAjustesMdg':
                    print('\tcliddata.&{}-> Se van a guardar los datos de los planos global'. format(fileCoordYear))
                    self.guardarAjustesMdg()

                # ==============================================================
                elif escribirLote == 'guardarAjustesMds':
                    print('\tcliddata.&{}-> Se van a guardar los datos de los planos suelo'. format(fileCoordYear))
                    self.guardarAjustesMds()

                # ==============================================================
                elif escribirLote == 'guardarAjustesMdxPreInterpol':
                    print('\tcliddata.&{}-> Se van a guardar los datos de los planos basal, major, cielo'. format(fileCoordYear))
                    self.guardarAjustesMdxPreInterpol()

                # ==============================================================
                elif escribirLote == 'guardarAjustesMdsPostInterpol':
                    self.guardarAjustesMdsPostInterpol(nInterpol)

                # ==============================================================
                elif escribirLote == 'guardarAjustesMdbPostInterpol':
                    self.guardarAjustesMdbPostInterpol(nInterpol)

                # ==============================================================
                elif escribirLote == 'guardarAjustesMdbSubCelda':
                    print('\tcliddata.&{}-> Se van a guardar los datos de subCelda del plano basal'. format(fileCoordYear))
                    self.guardarAjustesMdbSubCelda(prePostInterpol)

                # ==============================================================
                elif escribirLote == 'guardarMdcSubCelda':
                    self.guardarMdcSubCelda()

                # ==============================================================
                elif escribirLote == 'guardarMdkSubCeldaPreInterpol':
                    self.guardarMdkSubCeldaPreInterpol()

                # ==============================================================
                elif escribirLote == 'guardarMdkSubCeldaPosInterpol':
                    self.guardarMdkSubCeldaPosInterpol()

                # ==============================================================
                elif escribirLote == 'guardarApices':
                    self.guardarApices()

                # ==============================================================
                elif escribirLote == 'guardarMiniSubCelSueloValidadoPorMdp':
                    if GLO.GLBLcalcularSubCeldas: # Requiere tb GLO.GLBLcalcularMdp
                        clidaux.printMsg('\t-> cliddata-> Guardando SubCeldasPuntoMiniSubCelValidado: validacion de los puntos miniSubCel como suelo (obtenida con numbaVueltaAjustesMdp<>)...')
                        self.guardarMiniSubCelSueloValidadoPorMdp()
                    else:
                        clidaux.printMsg('\t-> clidnat-> No se guarda la validacion de los puntos miniSubCel como suelo (obtenida con numbaVueltaAjustesMdp<>)')
                # ==============================================================
                elif escribirLote == 'guardarAjustesMdp':
                    if (GLO.GLBLcalcularSubCeldas and GLO.GLBLgrabarCotaMinMaxSubCelda) or (
                        GLO.GLBLcalcularMdp
                        and (
                            GLO.GLBLgrabarMdpAjusteCelda
                            or GLO.GLBLcalcularSubCeldas
                            or GLO.GLBLgrabarMdfCotaSubcelda
                            or GLO.GLBLgrabarMdpInfoAuxiliar
                            or GLO.GLBLgrabarMdpCotaSubceldaMacroMicro
                        )
                    ):
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConMetodoManualPuro:
                            clidaux.printMsg('\t-> cliddata-> Guardando ficheros asociados al plano pleno...')
                            self.guardarAjustesMdpManual()
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModeloConvolucional:
                            clidaux.printMsg('\t-> cliddata-> Guardando plano pleno obtenido con modelo convolucional...')
                            self.guardarAjustesMdpConvol()
                        if GLO.GLBLcalcularMdfConMiniSubCelValidadosConModConvoManualizado:
                            clidaux.printMsg('\t-> cliddata-> Guardando plano pleno obtenido con metodo manual + modelo convolucional...')
                            self.guardarAjustesMdpConual()
                        if (
                            GLO.GLBLcalcularMdfConMiniSubCelValidadosConMetodoManualPuro
                            or GLO.GLBLcalcularMdfConMiniSubCelValidadosConModConvoManualizado
                        ):
                            self.guardarAjustesMdpExtras()

                # ==============================================================
                elif escribirLote == 'guardarAjustesMdr':
                    if GLO.GLBLcalcularMdr and GLO.GLBLgrabarMdr:
                        print('\tcliddata.&{}-> Se van a guardar los datos de los planos gridd'. format(fileCoordYear))
                        self.guardarAjustesMdr()

                # ==============================================================
                elif escribirLote == 'guardarCalidadTopografica':
                    self.guardarCalidadTopografica(etapa, nTPini, nTPfin, cTP)

                # ==============================================================
                elif escribirLote == 'guardarCalidadDelAjuste':
                    self.guardarCalidadDelAjuste(etapa, nTPini, nTPfin, cTP)

                # ==============================================================
                elif escribirLote == 'guardarVuelta4':
                    self.guardarVuelta4()

                # ==============================================================
                elif escribirLote == 'guardarMiscelaneaDasoLidar':
                    self.guardarMiscelaneaDasoLidar()

                # ==============================================================
                else:
                    print('\ncliddata-> Revisar este escribirEnDisco no previsto-> escribirLote:', escribirLote)
                # ==============================================================

                break
#             except IOError as thisError:
#                 if nIntentosEscritura > 5:
#                     clidaux.printMsg(
#                         'cliddata.&{}-> BP{} ATENCION!!!: IOError ({}): {}'.format(
#                             fileCoordYear, breakPoint, thisError.errno, thisError.strerror
#                         )
#                     )
#                     break
#                 print(
#                     '\ncliddata.&{}-> BP{} ATENCION: error al escribir en disco duro o unidad de red 01. Reintentado...'.format(
#                         fileCoordYear, breakPoint
#                     )
#                 )
#                 time.sleep(30)
#             except (OSError, SystemError) as thisError:  # Raised for operating system related errors.
#                 if nIntentosEscritura > 5:
#                     clidaux.printMsg(
#                         'cliddata.&{}-> BP{} ATENCION!!!: OSError ({}): {}'.format(
#                             fileCoordYear, breakPoint, thisError.errno, thisError.strerror
#                         )
#                     )
#                     break
#                 print(
#                     '\ncliddata.&{}-> BP{} ATENCION: error de sistema operativo. Reintentado...'.format(
#                         fileCoordYear, breakPoint
#                     )
#                 )
#                 time.sleep(30)
#             except (OverflowError, ArithmeticError, FloatingPointError, NameError, ValueError) as thisError:
#                 if nIntentosEscritura > 5:
#                     clidaux.printMsg(
#                         'cliddata.&{}-> BP{} ATENCION!!!: OverflowError ({}): {}'.format(
#                             fileCoordYear, breakPoint, thisError.errno, thisError.strerror
#                         )
#                     )
#                     break
#                 print(
#                     '\ncliddata.&{}-> BP{} ATENCION: error de overflow. Reintentado...'.format(
#                         fileCoordYear, breakPoint
#                     )
#                 )
#                 time.sleep(30)
#             except (Exception) as thisError: # Raised when a generated error does not fall into any category.
#                 if nIntentosEscritura > 5:
#                     clidaux.printMsg(
#                             'cliddata.&{}-> BP{} ATENCION!!!: Error exception: {}'.format(
#                             fileCoordYear, breakPoint, thisError
#                         )
#                     )
#                     break
#                 print(
#                     '\ncliddata.&{}-> BP{} ATENCION: error desconocido. Reintentado...'.format(
#                         fileCoordYear, breakPoint
#                     )
#                 )
#                 time.sleep(30)


# ==============================================================================
if __name__ == '__main__':
    pass
    # import clidbase
