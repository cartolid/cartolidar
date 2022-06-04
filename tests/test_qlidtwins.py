#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Test DasoLidarSource and its methods

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''
import os
import sys
import unittest
import argparse
import pytest
# from pytest import raises
from pytest import MonkeyPatch
import importlib

from cartolidar import qlidtwins


listaInputs = ['S',]
monkeypatch = MonkeyPatch()
# print(f'monkeypatch: {type(monkeypatch)} {monkeypatch}')
monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))

from cartolidar.clidax import clidconfig
if '--idProceso' in sys.argv and len(sys.argv) > sys.argv.index('--idProceso') + 1:
    MAIN_idProceso = sys.argv[sys.argv.index('--idProceso') + 1]
else:
    MAIN_idProceso = 0
configFileNameCfg = clidconfig.getConfigFileName(MAIN_idProceso)

listaVerbose = ['', '-v', '-vv', '-vvv']
listaExtras = ['-e']

for numTest, myVerbose in enumerate(listaVerbose):
    if numTest == 0:
        # La primera vez se testea sin fichero de configuracion; el resto con.
        if os.path.exists(configFileNameCfg):
            os.remove(configFileNameCfg)

    if numTest < len(listaExtras):
        myExtra = listaExtras[numTest]
    else:
        myExtra = ''

    for numArgv, valArgv in enumerate(sys.argv[:: -1]):
        if valArgv in listaVerbose:
            sys.argv.pop(-numArgv - 1)
    if myVerbose != '':
        sys.argv.append(myVerbose)

    for numArgv, valArgv in enumerate(sys.argv[:: -1]):
        if valArgv in listaExtras:
            sys.argv.pop(-numArgv - 1)
    if myExtra != '':
        sys.argv.append(myExtra)

    print('\n{:>^80}'.format(''))
    print(f'test_qlidtwins-> {numTest} -> sys.argv: {sys.argv}')
    print('{:<^80}'.format(''))

    qlidtwins = importlib.reload(qlidtwins)

    # Argumentos requeridos:
    listaMainArgs = (
        'extraArguments', 'mainAction',
        'rutaAscRaizBase', 'rutaCompletaMFE', 'cartoMFEcampoSp',
        'patronVectrName', 'patronLayerName',
        'testeoVectrName', 'testeoLayerName',
    )
    listaExtraArgs = (
        'menuInteractivo', 'marcoCoordMiniX', 'marcoCoordMaxiX', 'marcoCoordMiniY',
        'marcoCoordMaxiY', 'marcoPatronTest', 'nPatronDasoVars', 'rasterPixelSize',
        'radioClusterPix', 'nivelSubdirExpl', 'outRasterDriver', 'outputSubdirNew',
        'cartoMFErecorte', 'varsTxtFileName', 'ambitoTiffNuevo', 'noDataTiffProvi',
        'noDataTiffFiles', 'noDataTipoDMasa', 'umbralMatriDist')


    # ==============================================================================
    def test_checkRun(monkeypatch: MonkeyPatch) -> None:
        listaInputs = [True,]
        monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
        tipoEjecucion = qlidtwins.checkRun()
        # qlidtwins.testRun()
        assert tipoEjecucion > 0, 'No se ha identificado el tipo de ejecucion.'
        print('\test_checkRun ok')
    
    # ==============================================================================
    def test_testRun(monkeypatch: MonkeyPatch) -> None:
        listaInputs = [True,]
        monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
        qlidtwins.testRun()
        # assert tipoEjecucion > 0, 'No se ha identificado el tipo de ejecucion.'
        print('\test_testRun ok')
    
    # ==============================================================================
    def test_leerArgumentos(monkeypatch: MonkeyPatch) -> None:
        listaInputs = [True,]
        monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
        argsConfig = qlidtwins.leerConfiguracion()
        assert type(argsConfig) == argparse.Namespace, 'La funcion debe devolver un objeto de la clase <class "argparse.Namespace">.'
        assert len(argsConfig.__dict__) > 0, 'Deberia haber algun argumento en linea de comandos.'
        for myMainArg in listaMainArgs:
            assert myMainArg in dir(argsConfig), 'Revisar lectura de argumentos main en linea de comandos o por defecto'
        for myExtraArg in listaExtraArgs:
            assert  myExtraArg in dir(argsConfig), 'Revisar lectura de argumentos extras en linea de comandos o por defecto'
        print('\ntest_leerArgumentos ok')
    
    # ==============================================================================
    def test_saveAgrs(monkeypatch: MonkeyPatch) -> None:
        listaInputs = [True,]
        monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
        argsConfig = qlidtwins.leerConfiguracion()
        argsFileName = qlidtwins.saveArgs(argsConfig)
        assert os.path.exists(argsFileName), 'No se ha podido crear un fichero con los argmentos en linea de comandos. Revisar derechos de escritura.'
        print('\ntest_saveAgrs ok')
    
    def test_UseCase_0(monkeypatch: MonkeyPatch) -> None:
        listaInputs = [True,]
        monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
        argsConfig = qlidtwins.leerConfiguracion()
        cfgDict = qlidtwins.creaConfigDict(argsConfig)
        myDasolidar = qlidtwins.clidtwinsUseCase(cfgDict, accionPral=0)

        print('test_qlidtwins-> DasoLidarSource')
        assert myDasolidar is not None, 'Se debe crear el objeto de la clase DasoLidarSource'
        assert hasattr(myDasolidar, 'GLBLmenuInteractivo'), 'El objeto DasoLidarSource debe tener las propiedades extra asignadas desde su creacion.'
        assert hasattr(myDasolidar, 'LOCLmarcoCoordMiniX'), 'El objeto DasoLidarSource debe tener algunas propiedades asignadas desde su creacion.'
        assert hasattr(myDasolidar, 'LOCLmarcoCoordMaxiY'), 'El objeto DasoLidarSource debe tener algunas propiedades asignadas desde su creacion.'
        print('test_qlidtwins-> setRangeUTM')
        assert hasattr(myDasolidar, 'GLBLmarcoPatronTest'), 'El objeto DasoLidarSource debe tener la propiedad GLBLmarcoPatronTest.'
        assert myDasolidar.LOCLmarcoCoordMiniX > 0, 'El objeto DasoLidarSource debe tener coordenadas de marco definidas.'
        assert myDasolidar.LOCLmarcoCoordMaxiY > 0, 'El objeto DasoLidarSource debe tener coordenadas de marco definidas.'
        print('test_qlidtwins-> searchSourceFiles')
        # assert len(myDasolidar.inFilesListAllTypes) == 2, 'El match de ejemplo debe encontrar 2 ficheros asc con variables dasoLidar'
        assert len(myDasolidar.inFilesListAllTypes) == 3, 'El match de ejemplo debe encontrar 3 tipos de fichero asc con variables dasoLidar'
        assert len(myDasolidar.inFilesListAllTypes[0]) == 2, 'El match de ejemplo debe encontrar 2 ficheros asc de cada tipo con variables dasoLidar'
        # assert myDasolidar.inFilesListAllTypes[0][0][1] == '454_4576_2017_Alt95.asc', 'Debe encontrar estos dos ficheros asc 454_4576_2017_Alt95.asc y 454_4576_2017_Fcc5m.asc'
        # assert myDasolidar.inFilesListAllTypes[1][0][1] == '454_4576_2017_Fcc5m.asc', 'Debe encontrar estos dos ficheros asc 454_4576_2017_Alt95.asc y 454_4576_2017_Fcc5m.asc'
        assert myDasolidar.inFilesListAllTypes[0][0][1] == '348_4600_2017_alt95.asc', 'Debe encontrar dos bloques de cada tipo de fichero'
        assert myDasolidar.inFilesListAllTypes[0][1][1] == '348_4602_2017_alt95.asc', 'Debe encontrar dos bloques de cada tipo de fichero'
        assert myDasolidar.inFilesListAllTypes[1][0][1] == '348_4600_2017_fcc3m.asc', 'Debe encontrar dos bloques de cada tipo de fichero'
        assert myDasolidar.inFilesListAllTypes[1][1][1] == '348_4602_2017_fcc3m.asc', 'Debe encontrar dos bloques de cada tipo de fichero'
        assert myDasolidar.inFilesListAllTypes[2][0][1] == '348_4600_2017_cob05_200cm.asc', 'Debe encontrar dos bloques de cada tipo de fichero'
        assert myDasolidar.inFilesListAllTypes[2][1][1] == '348_4602_2017_cob05_200cm.asc', 'Debe encontrar dos bloques de cada tipo de fichero'
        print('test_qlidtwins-> Verifica que se ha creado el raster:')
        assert os.path.exists(os.path.join(myDasolidar.LOCLoutPathNameRuta, myDasolidar.LOCLoutFileNameWExt_mergedUniCellAllDasoVars)), 'Debe crear un fichero raster unicell con todas las variables dasoLidar'
        print('test_qlidtwins-> Verifica los tipos de bosque mas frecuentes en zona patron:')
        # assert myDasolidar.pctjTipoBosquePatronMasFrecuente1 == 100, 'Solo debe encontrar un tipoBosque con 100% de ocupacion'
        # assert myDasolidar.codeTipoBosquePatronMasFrecuente1 == 43, 'El tipoBosque mas frecuuente debe ser 43 (Quercs pyurenaica)'
        # assert myDasolidar.pctjTipoBosquePatronMasFrecuente2 == 0, 'No debe haber un tipoBosque secundario'
        # assert myDasolidar.codeTipoBosquePatronMasFrecuente2 == 0, 'No debe haber un tipoBosque secundario'
        assert myDasolidar.pctjTipoBosquePatronMasFrecuente1 == 87, 'Solo debe encontrar un tipoBosque con 100% de ocupacion'
        assert myDasolidar.codeTipoBosquePatronMasFrecuente1 == 23, 'El tipoBosque mas frecuuente debe ser 43 (Quercs pyurenaica)'
        assert myDasolidar.pctjTipoBosquePatronMasFrecuente2 == 13, 'No debe haber un tipoBosque secundario'
        assert myDasolidar.codeTipoBosquePatronMasFrecuente2 == 45, 'No debe haber un tipoBosque secundario'
        print('test_qlidtwins->Verifica que los rangos son correctos:')
        assert (myDasolidar.dictHistProb01['0_Alt95_ref'][:7] == [0.058, 0.238, 0.027, 0.062, 0.229, 0.352, 0.033]).all(), 'El histograma de alt95 debe tener determinados valores'
        assert (myDasolidar.dictHistProb01['1_Fcc3m_ref'] == [0.343, 0.278, 0.207, 0.116, 0.056]).all(), 'El histograma de Fcc3m debe tener determinados valores'
        assert (myDasolidar.dictHistProb01['2_CobMt_ref'] == [0.688, 0.182, 0.078, 0.042, 0.01]).all(), 'El histograma de CobMt debe tener determinados valores'
        print('test_qlidtwins-> Verifica que se ha creado el txt con los rangos:')
        assert os.path.exists(os.path.join(myDasolidar.LOCLoutPathNameRuta, myDasolidar.outputRangosFileTxtSinPath)), 'Debe crear un fichero txt con los rangps admitidos de las variables dasoLidar'
        print('\ntest_UseCase_0 ok')
    
    
    def test_UseCase_1(monkeypatch: MonkeyPatch) -> None:
        listaInputs = [True,]
        monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
        argsConfig = qlidtwins.leerConfiguracion()
        cfgDict = qlidtwins.creaConfigDict(argsConfig)
        # cfgDict['mainAction'] = 1
        # (
        #     tipoBosqueOk,
        #     nVariablesNoOk,
        #     distanciaEuclideaMedia,
        #     pctjPorcentajeDeProximidad,
        #     matrizDeDistancias,
        # )
        myDasolidar = qlidtwins.clidtwinsUseCase(cfgDict, accionPral=1)
        assert myDasolidar.tipoBosqueOk == 10, 'El match de ejemplo debe dar correspondencia plena en tipo de bosque (tipoBosqueOk=10)'
        # assert myDasolidar.nVariablesNoOk == 0, 'El match de ejemplo no debe debe dar ninguna variable no ok'
        assert myDasolidar.nVariablesNoOk == 3, 'El match de ejemplo debe debe dar 3 variables no ok'
        # assert int(myDasolidar.distanciaEuclideaMedia) == 19, 'El match de ejemplo debe dar una distanciaEuclideaMedia = 19'
        assert int(myDasolidar.distanciaEuclideaMedia) == 38, 'El match de ejemplo debe dar una distanciaEuclideaMedia = 38'
        # assert int(myDasolidar.pctjPorcentajeDeProximidad) == 65, 'El match de ejemplo debe dar un pctjPorcentajeDeProximidad = 65'
        assert int(myDasolidar.pctjPorcentajeDeProximidad) == 25, 'El match de ejemplo debe dar un pctjPorcentajeDeProximidad = 25'
        # assert (myDasolidar.matrizDeDistancias).shape == (302, 837), 'El match de ejemplo debe dar una matrizDeDistancias con shape (302, 837)'
        assert (myDasolidar.matrizDeDistancias).shape == (409, 407), 'El match de ejemplo debe dar una matrizDeDistancias con shape (409, 407)'
        print('\ntest_UseCase_1 ok')


    def test_UseCase_2(monkeypatch: MonkeyPatch) -> None:
        listaInputs = [True,]
        monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
        argsConfig = qlidtwins.leerConfiguracion()
        cfgDict = qlidtwins.creaConfigDict(argsConfig)
        # cfgDict['mainAction'] = 2
        myDasolidar = qlidtwins.clidtwinsUseCase(cfgDict, accionPral=2)
        assert os.path.exists(os.path.join(myDasolidar.LOCLoutPathNameRuta, myDasolidar.outputClusterAllDasoVarsFileNameSinPath)), 'Debe crear un raster con todas las variables clusterizadas para toda la zona de analisis'
        assert os.path.exists(os.path.join(myDasolidar.LOCLoutPathNameRuta, myDasolidar.outputClusterTiposDeMasaFileNameSinPath)), 'Debe crear un raster con los tipos de masa para toda la zona de analisis'
        assert os.path.exists(os.path.join(myDasolidar.LOCLoutPathNameRuta, myDasolidar.outputClusterFactorProxiFileNameSinPath)), 'Debe crear un raster con el factor de proximidad para toda la zona de analisis'
        assert os.path.exists(os.path.join(myDasolidar.LOCLoutPathNameRuta, myDasolidar.outputClusterDistanciaEuFileNameSinPath)), 'Debe crear un raster con la distancia euclidea para toda la zona de analisis'
        print('\ntest_UseCase_2 ok')


    # if __name__ == "__main__":
    #     test_UseCase_0(monkeypatch)
    #     test_UseCase_1(monkeypatch)
    #     test_UseCase_2(monkeypatch)


# # ==============================================================================
# class Test(unittest.TestCase):
#
#     def testLeerArgumentos(self) -> None:
#         args = qlidtwins.leerConfiguracion()
#         # print('test_input-> args:', type(args), dir(args))  # <class 'argparse.Namespace'>
#         # print(dir(args))  # ['__class__', '__contains__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__','__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_get_args', '_get_kwargs', etc.]
#         self.assertEqual(type(args), argparse.Namespace, 'La funcion debe devolver un objeto de la clase <class "argparse.Namespace">.')
#         self.assertNotEqual(len(args.__dict__), 0, 'Deberia haber algun argumento en linea de comandos.')
#
#         for myMainArg in listaMainArgs:
#             self.assertEqual(myMainArg in dir(args), True, 'Revisar lectura de argumentos main en linea de comandos o por defecto')
#         for myExtraArg in listaExtraArgs:
#             self.assertEqual(myExtraArg in dir(args), True, 'Revisar lectura de argumentos extras en linea de comandos o por defecto')
#
#         print('\ntestLeerArgumentos ok')
#
#
# if __name__ == "__main__":
#     sys.argv = ['', 'Test.testLeerArgumentos']
#     unittest.main()
#     print('\nTodos los tests test_qlidtwins ok')
