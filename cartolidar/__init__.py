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

import os
import sys

from cartolidar.clidtools.clidtwcfg import GLO
__version__ = GLO.__version__
__date__ = GLO.__date__
__updated__ = GLO.__updated__
__all__ = [
    'qlidtwins',
    'clidtools.clidtwins'
    ]
