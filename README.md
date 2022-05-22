[![pypi](https://img.shields.io/pypi/v/cartolidar.svg)](https://pypi.org/project/cartolidar/)
[![Coverage Status](https://codecov.io/gh/cartolidar/cartolidar/branch/main/graph/badge.svg)](https://codecov.io/gh/cartolidar/cartolidar)
[![Join the chat at https://gitter.im/cartolidar/cartolidar](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/cartolidar/cartolidar?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/cartolidar/cartolidar/main)

![cartolidar Logo](https://secure.gravatar.com/avatar/ea09c6d439dc57633702164f23b264e5 "clid image")


CartoLidar
----------

Lidar data processing tools focused on Spanish PNOA datasets

Herramientas para procesado de datos Lidar del PNOA

Lidar PNOA: https://pnoa.ign.es/el-proyecto-pnoa-lidar


Introduction
------------

CartoLidar es una colección de herramientas destinadas a procesar ficheros lidar
(las y laz) para clasificar los puntos y generar ficheros ráster con DEM y DLVs.

DEM (Digital Elevation Model): modelos digitales de elevaciones (MDT, MDS)

DLV (Daso Lidar Variables): variables dasoLidar, que representan diversos
aspectos de la estructura de una formación arbolada, arbustiva o de matorral.

CartoLidar también proporciona herramientas adicionales para generar otros
productos de utilidad en selvicultura y otras areas de gestión del medio
natural a partir de los ficheros ráster con las DLVs. 

El proyecto está en fase alpha e incluye únicamente la herramienta "clidtwins".

clidtwins está destinada a buscar zonas similares a una(s) de referencia en
términos de determinadas variables dasoLidar (DLVs).


>CartoLidar is a collection of tools to process lidar files "las" and "laz" and
>generate other products aimed to forestry and natural environment management.
>
>This project is in alpha version and includes only the "clidtwins" tool.
>
>"clidtwins" searchs for similar areas to a reference one in terms of dasoLidar Variables (DLVs)
>DLV: Lidar variables that describe or characterize forest or land cover structure.


Consultar documentación en: [Read the Docs - cartolidar](http://cartolidar-docs.readthedocs.io/en/latest/)
(página en construcción)


Install
--------

1. Install official version from [pypi - cartolidar](https://pypi.org/project/cartolidar/):
```
pip install cartolidar
```
or
```
pip install cartolidar --proxy https://user:password@proxyserver:port
```

2. Download development version from [github - cartolidar](https://github.com/cartolid/cartolidar)

You can download the zip version, uncompress it somewhere, i.e.:
```
C:\users\yourUser\Downloads\cartolidar-main\
```
That folder contains a setup.py file (and the other components of the project)
and you can install cartolidar from there for your python environment:
```
cd C:\users\yourUser\Downloads\cartolidar-main\
pip install .
```


Requeriments
------------
cartolidar requires Python 3.7 or higher.

See other package requirements in requirements.txt.


Use
--------

### From the command line (cmd or bash)
a) Run cartolidar package:
```
python -m cartolidar [options]
```
Se inicia el menu principal con las herramientas disponibles en cartolidar:

&nbsp;&nbsp;&nbsp;&nbsp;Inicialmente solo está disponible la herramienta qlidtwins

>It starts the main menu with the avaliable tools

&nbsp;&nbsp;&nbsp;&nbsp;options:

&nbsp;&nbsp;&nbsp;&nbsp;-h, --help          show this help message and exit

&nbsp;&nbsp;&nbsp;&nbsp;-v, --verbose       set verbosity level [default: False]

&nbsp;&nbsp;&nbsp;&nbsp;-V, --version       show program's version number and exit

&nbsp;&nbsp;&nbsp;&nbsp;-a ACCIONPRINCIPAL  0. Show main menu; 1. qlidtwins: buscar o verificar

&nbsp;&nbsp;&nbsp;&nbsp;                      zonas analogas a una de referencia (con un determinado

&nbsp;&nbsp;&nbsp;&nbsp;                      patron dasoLidar); 2. qlidmerge: integrar ficheros asc

&nbsp;&nbsp;&nbsp;&nbsp;                      de 2x2 km en una capa tif unica (componer mosaico:

&nbsp;&nbsp;&nbsp;&nbsp;                      merge). Default: 0

&nbsp;&nbsp;&nbsp;&nbsp;other options       are tool-specific (see below).


b) It is also possible to run a tool (a module) without displayin the main menu (if the module is accesible). E.g.:
```
python qlidtwins.py [options]
```
&nbsp;&nbsp;&nbsp;&nbsp;You can check options with:
```
python qlidtwins.py -h
```
A module is accesible if is called from its folder, is called with path_to_module or its folder is in the PATH environmental variable.


### From python code
You can import packages, modules, classes of functions from a script.py or
within the python interactive interpreter. Examples:
```
import cartolidar
from cartolidar import clidtools
from cartolidar.clidtools import clidtwins
from cartolidar.clidtools.clidtwins import DasoLidarSource
```
To execute module qlidtwins.py from python code:
```
from cartolidar import qlidteins
```
In this case, there are no options: it runs with qlidtwins.cfg configuration (if exists) or by default.


Use examples
------------
Read [Read the Docs - cartolidar](http://cartolidar-docs.readthedocs.io/en/latest/) for details.

clidtwins reads files in "asc" format (single vector layers) each with a dasoLidar variable (DLV).

# Those files have to be named as: XXX_YYYY_*IdFileType*.asc where:
# - XXX, YYYY are UTM coordinates (miles) that identifies the location (the block)
# -- Usually the upper-left corner of a 2x2 km square area
# - *IdFileType* is any string that includes a DVL identifier (like alt95, fcc05, etc.).
# 
# Example: 318_4738_alt95.asc and 320_4738_alt95.asc are two files with alt95 variable.
# 
# If we select two DLVs (e.g. alt95, fcc05), we need two files for every XXX_YYYY:
# 318_4738_alt95.asc, 318_4738_fcc05.asc, 320_4738_alt95.asc, 320_4738_fcc05.asc


Procedure:

1. Import package or Class and instantiate DasoLidarSource class:
```
from cartolidar.clidtools.clidtwins import DasoLidarSource
myDasolidar = DasoLidarSource()
```


2. Set the analysis zone (optional):
```
myDasolidar.setRangeUTM(
    LCL_marcoCoordMiniX=CFG_marcoCoordMiniX,
    LCL_marcoCoordMaxiX=CFG_marcoCoordMaxiX,
    LCL_marcoCoordMiniY=CFG_marcoCoordMiniY,
    LCL_marcoCoordMaxiY=CFG_marcoCoordMaxiY,
)
```


3. Search for dasoLidar files:
<!-- First argument (LCL_listLstDasoVars) is a string with a sequence of DLV identifiers
and second one (LCL_rutaAscRaizBase) is a path to look for the files.
 -->
```
myDasolidar.searchSourceFiles(
    LCL_listLstDasoVars='Alt95,Fcc05,Fcc03',
    LCL_rutaAscRaizBase='C:/myAscFiles',
)
```
This method creates a property named inFilesListAllTypes with one list of files for every DLV.
It only includes blocks that have all the file types. For every file, a tuple of file path and file name is included.


4. Create a Tiff file from the DLV files found and analyze the ranges of every DLV in the reference area:

The createMultiDasoLayerRasterFile method requires the name (with path)
of the forest or land cover vector layer (e.g. Spanish Forest Map -MFE25-)
and the name of the field (type int) with the forest or land cover type
identifier (e.g. main species code).
```
myDasolidar.createMultiDasoLayerRasterFile(
    LCL_rutaCompletaMFE='C:/mfe25/24_mfe25.shp',
    LCL_cartoMFEcampoSp='SP1',
)
```

The analyzeMultiDasoLayerRasterFile method requires the name (with path)
of the vector file with the reference polygon gor macthing (shp or gpkg).
If it is ageopackage, also the layer name is required.
```
myDasolidar.analyzeMultiDasoLayerRasterFile(
    LCL_patronVectrName='C:/vector/CorralesPlots.gpkg,
    LCL_patronLayerName='plot01Quercus',
)
```


5. Create new Tiff files with similar zones and proximity to reference one (patron):
```
myDasolidar.generarRasterCluster()
```


to be continued...



[Ayuda Markdown](https://guides.github.com/features/mastering-markdown/)

[![Actions Status](https://github.com/cartolidar/cartolidar/workflows/Tests/badge.svg)](https://github.com/cartolidar/cartolidar/actions?query=workflow%3ATests)
