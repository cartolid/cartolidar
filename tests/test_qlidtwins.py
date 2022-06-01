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

listaInputs = ['S',]
monkeypatch = MonkeyPatch()
# print(f'monkeypatch: {type(monkeypatch)} {monkeypatch}')
monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))

from cartolidar import qlidtwins

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
    args = qlidtwins.leerConfiguracion()
    assert type(args) == argparse.Namespace, 'La funcion debe devolver un objeto de la clase <class "argparse.Namespace">.'
    assert len(args.__dict__) > 0, 'Deberia haber algun argumento en linea de comandos.'
    for myMainArg in listaMainArgs:
        assert myMainArg in dir(args), 'Revisar lectura de argumentos main en linea de comandos o por defecto'
    for myExtraArg in listaExtraArgs:
        assert  myExtraArg in dir(args), 'Revisar lectura de argumentos extras en linea de comandos o por defecto'
    print('\ntest_leerArgumentos ok')

# ==============================================================================
def test_saveAgrs(monkeypatch: MonkeyPatch) -> None:
    listaInputs = [True,]
    monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
    argsConfig = qlidtwins.leerConfiguracion()
    argsFileName = qlidtwins.saveArgs(argsConfig)
    assert os.path.exists(argsFileName), 'No se ha podido crear un fichero con los argmentos en linea de comandos. Revisar derechos de escritura.'
    print('\ntest_saveAgrs ok')


def test_UseCase_1(monkeypatch: MonkeyPatch) -> None:
    listaInputs = [True,]
    monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
    argsConfig = qlidtwins.leerConfiguracion()
    cfgDict = qlidtwins.creaConfigDict(argsConfig)
    # cfgDict['mainAction'] = 1
    (
        tipoBosqueOk,
        nVariablesNoOk,
        distanciaEuclideaMedia,
        pctjPorcentajeDeProximidad,
        matrizDeDistancias,
    ) = qlidtwins.clidtwinsUseCase(cfgDict, accionPral=1)
    assert tipoBosqueOk == 10, 'El match de ejemplo debe dar correspondencia plena en tipo de bosque (tipoBosqueOk=10)'
    assert nVariablesNoOk == 0
    assert int(distanciaEuclideaMedia) == 19
    assert int(pctjPorcentajeDeProximidad) == 65
    assert matrizDeDistancias.shape == (302, 837)
    print('\ntest_UseCase_1 ok')


# def test_UseCase_2(monkeypatch: MonkeyPatch) -> None:
#     listaInputs = [True,]
#     monkeypatch.setattr('builtins.input', lambda _: listaInputs.pop(0))
#     argsConfig = qlidtwins.leerConfiguracion()
#     cfgDict = qlidtwins.creaConfigDict(argsConfig)
#     cfgDict['mainAction'] = 2
#     qlidtwins.clidtwinsUseCase(cfgDict)
#     print('\ntest_UseCase_2 ok')

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
