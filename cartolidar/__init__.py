#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Utilities included in cartolidar project 
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidtools incldes ancillary tools that work on raster outputs of cartolidar
Most of those raster represent dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
@deffield    updated: 2022-06-01
'''
# -*- coding: cp1252 -*-
# Ver https://docs.python.org/3/reference/lexical_analysis.html#encoding-declarations

'''
Inhabilito esto porque para ejecutar clidbase necesito cargar
la configuracion de clidbase.xlsx antes de importar modulos.
Sin embargo, al importar clidtwcfg se desencadena una secuencia de imports
de modulos que acaba en clidraster y clidcarto que no debe iniciarse hasta
que la configuracion esta perfilada y guardad en el fichero .cfg
clidtools (__init__.py) -> clidtwcfg + clidtwins + clidtwinx -> clidraster -> clidcarto
'''

# import os
# import sys
#
# from cartolidar.clidtools.clidtwcfg import GLO
# __version__ = GLO.__version__
# __date__ = GLO.__date__
# __updated__ = GLO.__updated__
# __all__ = [
#     'qlidtwins',
#     'clidtools.clidtwins'
#     ]
