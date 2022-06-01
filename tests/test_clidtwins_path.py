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
import unittest

import pytest
# from pytest import raises
from pytest import MonkeyPatch

# https://pypi.org/project/python-dotenv/
# https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1
# from dotenv import load_dotenv
# load_dotenv()

from cartolidar.clidtools.clidtwins import DasoLidarSource

# unittest:
# https://realpython.com/python-testing/

# pytest:
# https://docs.pytest.org/en/latest/getting-started.html
#    conda install pytest
#        Actualiza numpy a 1.19.1
#        Actualiza scipy a 1.4.1
#    Altenativa:
#        pip install pytest
#    pip install pytest-cov
#    $ pytest --cov
# https://www.youtube.com/watch?v=ULxMQ57engo
# https://github.com/ArjanCodes/2022-test-existing-code

# Para instalar monkeypatch intento:
#    conda install monkeypatch
# Pero no lo encuentra. Lo que si funciona es:
#    pip install monkeypatch
# Aunque en la instalacion da errores del tipo:
#       File "C:\Users\benmarjo\AppData\Local\Temp\pip-install-iez_dy98\monkeypatch_e1e1f94f893f4f96a80c7ec4418b0981\setup.py", line 99
#         except ImportError, e:

# Descartado:
#    https://failedtofunction.com/test-coverage-with-pytest/
#        pip install coverage


def test_files_in_path():
    myDasolidar = DasoLidarSource()
    miRuta = os.path.abspath('../data')
    myDasolidar.searchSourceFiles(LCL_rutaAscRaizBase=miRuta)
    assert len(myDasolidar.inFilesListAllTypes) != 0, 'Debería haber algún fichero que cumpla requisitos en la ruta indicada.'
    print('\ntest_files_in_path ok')

# def test_no_files_in_path():
#     with pytest.raises(ValueError):
#         myDasolidar = DasoLidarSource()
#         miRuta = 'D'
#         myDasolidar.searchSourceFiles(LCL_rutaAscRaizBase=miRuta)
#         assert len(myDasolidar.inFilesListAllTypes) != 0, 'Debería haber algún fichero que cumpla requisitos en la ruta indicada.'
#     print('\ntest_files_in_path ok')


# class Test(unittest.TestCase):
#
#     def test_files_in_path(self):
#         myDasolidar = DasoLidarSource()
#         # miRuta = 'D:/'
#         miRuta = r'O:\Sigmena\usuarios\COMUNES\Bengoa\Lidar\cartoLidar\Sg_PinoSilvestre'
#         myDasolidar.searchSourceFiles(LCL_rutaAscRaizBase=miRuta)
#         self.assertNotEqual(len(myDasolidar.inFilesListAllTypes), 0, 'Debería haber algún fichero que cumpla requisitos en la ruta indicada.')
#         print('\ntest_files_in_path ok')
#
# if __name__ == "__main__":
#     import sys
#     sys.argv = ['', 'Test.test_files_in_path']
#     unittest.main()
#     print('\nTodos los tests ok')


r'''
(clid) D:\_clid\cartolidar>conda install pytest
Collecting package metadata (current_repodata.json): done
Solving environment: /
The environment is inconsistent, please check the package plan carefully
The following packages are causing the inconsistency:

  - defaults/win-64::aiohttp==3.8.1=py37h2bbff1b_0
  - defaults/noarch::async-timeout==4.0.1=pyhd3eb1b0_0
  - defaults/win-64::gdal==3.0.2=py37hdf43c64_0
  - defaults/noarch::google-auth==1.33.0=pyhd3eb1b0_0
  - defaults/noarch::google-auth-oauthlib==0.4.4=pyhd3eb1b0_0
  - defaults/win-64::h5py==2.10.0=py37h5e291fa_0
  - defaults/noarch::imageio==2.9.0=pyhd3eb1b0_0
  - defaults/win-64::importlib-metadata==4.8.2=py37haa95532_0
  - defaults/win-64::keras==2.3.1=0
  - defaults/noarch::keras-applications==1.0.8=py_1
  - defaults/win-64::keras-base==2.3.1=py37_0
  - defaults/noarch::keras-preprocessing==1.1.2=pyhd3eb1b0_0
  - defaults/win-64::markdown==3.3.4=py37haa95532_0
  - defaults/win-64::matplotlib==3.2.2=0
  - defaults/win-64::matplotlib-base==3.2.2=py37h64f37c6_0
  - defaults/win-64::mkl_fft==1.3.0=py37h46781fe_0
  - defaults/win-64::mkl_random==1.1.1=py37h47e9c7a_0
  - defaults/win-64::numba==0.50.1=py37h47e9c7a_0
  - defaults/win-64::numpy==1.19.1=py37h5510c5b_0
  - defaults/noarch::opt_einsum==3.3.0=pyhd3eb1b0_1
  - defaults/win-64::pandas==1.0.5=py37h47e9c7a_0
  - defaults/win-64::scikit-learn==0.23.1=py37h25d0782_0
  - defaults/win-64::scipy==1.4.1=py37h9439919_0
  - defaults/noarch::seaborn==0.10.1=py_0
  - defaults/noarch::tensorboard==2.4.0=pyhc547734_0
  - defaults/win-64::tensorflow==2.3.0=mkl_py37h04bc1aa_0
  - defaults/win-64::tensorflow-base==2.3.0=eigen_py37h17acbac_0
  - defaults/noarch::tensorflow-estimator==2.6.0=pyh7b7c402_0
  - defaults/noarch::typing-extensions==3.10.0.2=hd3eb1b0_0
done


==> WARNING: A newer version of conda exists. <==
  current version: 4.11.0
  latest version: 4.13.0

Please update conda by running

    $ conda update -n base -c defaults conda



## Package Plan ##

  environment location: C:\conda\py37\envs\clid

  added / updated specs:
    - pytest


The following packages will be downloaded:

    package                    |            build
    ---------------------------|-----------------
    atomicwrites-1.4.0         |             py_0          11 KB
    certifi-2022.5.18.1        |   py37haa95532_0         157 KB
    colorama-0.4.4             |     pyhd3eb1b0_0          21 KB
    importlib_metadata-1.5.0   |           py37_0          49 KB
    iniconfig-1.1.1            |     pyhd3eb1b0_0           8 KB
    mkl-2021.4.0               |     haa95532_640       114.9 MB
    mkl-service-2.4.0          |   py37h2bbff1b_0          49 KB
    mkl_fft-1.3.1              |   py37h277e83a_0         135 KB
    mkl_random-1.2.2           |   py37hf11a4ad_0         216 KB
    numpy-1.21.5               |   py37h7a0a035_2          25 KB
    numpy-base-1.21.5          |   py37hca35cd5_2         4.4 MB
    packaging-21.3             |     pyhd3eb1b0_0          36 KB
    pluggy-1.0.0               |   py37haa95532_1          29 KB
    py-1.11.0                  |     pyhd3eb1b0_0          76 KB
    pytest-7.1.1               |   py37haa95532_0         471 KB
    scikit-learn-1.0.2         |   py37hf11a4ad_1         4.9 MB
    scipy-1.7.3                |   py37h0a974cb_0        13.8 MB
    tomli-1.2.2                |     pyhd3eb1b0_0          17 KB
    typing-extensions-4.1.1    |       hd3eb1b0_0           8 KB
    typing_extensions-4.1.1    |     pyh06a4308_0          28 KB
    ------------------------------------------------------------
                                           Total:       139.3 MB

The following NEW packages will be INSTALLED:

  atomicwrites       pkgs/main/noarch::atomicwrites-1.4.0-py_0
  colorama           pkgs/main/noarch::colorama-0.4.4-pyhd3eb1b0_0
  importlib_metadata pkgs/main/win-64::importlib_metadata-1.5.0-py37_0
  iniconfig          pkgs/main/noarch::iniconfig-1.1.1-pyhd3eb1b0_0
  numpy-base         pkgs/main/win-64::numpy-base-1.21.5-py37hca35cd5_2
  packaging          pkgs/main/noarch::packaging-21.3-pyhd3eb1b0_0
  pluggy             pkgs/main/win-64::pluggy-1.0.0-py37haa95532_1
  py                 pkgs/main/noarch::py-1.11.0-pyhd3eb1b0_0
  pytest             pkgs/main/win-64::pytest-7.1.1-py37haa95532_0
  tomli              pkgs/main/noarch::tomli-1.2.2-pyhd3eb1b0_0
  typing_extensions  pkgs/main/noarch::typing_extensions-4.1.1-pyh06a4308_0

The following packages will be UPDATED:

  ca-certificates                     2021.10.26-haa95532_2 --> 2022.4.26-haa95532_0
  certifi                          2021.10.8-py37haa95532_0 --> 2022.5.18.1-py37haa95532_0
  mkl                                            2020.2-256 --> 2021.4.0-haa95532_640
  mkl-service                          2.3.0-py37h196d8e1_0 --> 2.4.0-py37h2bbff1b_0
  mkl_fft                              1.3.0-py37h46781fe_0 --> 1.3.1-py37h277e83a_0
  mkl_random                           1.1.1-py37h47e9c7a_0 --> 1.2.2-py37hf11a4ad_0
  numpy                               1.19.1-py37h5510c5b_0 --> 1.21.5-py37h7a0a035_2
  openssl                                 1.1.1l-h2bbff1b_0 --> 1.1.1o-h2bbff1b_0
  scikit-learn                        0.23.1-py37h25d0782_0 --> 1.0.2-py37hf11a4ad_1
  scipy                                1.4.1-py37h9439919_0 --> 1.7.3-py37h0a974cb_0
  typing-extensions                     3.10.0.2-hd3eb1b0_0 --> 4.1.1-hd3eb1b0_0
'''
