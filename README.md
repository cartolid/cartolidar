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

>DEM (Digital Elevation Model): modelos digitales de elevaciones (MDT, MDS)
>DLV (Daso Lidar Variables): variables dasoLidar, que representan diversos
>aspectos de la estructura de una formación arbolada, arbustiva o de matorral.

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
>DLV: Lidar variables that describe or characterize forest structure (or vegetation in general).


Consultar documentación en: [Read the Docs - cartolidar](http://cartolidar-docs.readthedocs.io/en/latest/)
(página en construcción)


Install
--------

1. Install official version from [pypi - cartolidar](https://pypi.org/project/cartolidar/):
```
pip install cartolidar
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
It is also possible the older way, but is not recommendable:
```
$ python setup.py install
```

If you download any distribution package (wheel or sdist) from elsewhere you can install it:
```
$ pip install cartolidar-X.Y.Z-py3-none-any.whl
```
or 
```
$ pip install cartolidar-X.Y.Z.tar.gz
```
&nbsp;&nbsp;&nbsp;&nbsp;where: X.Y.Z is the actual version



Requeriments
------------
cartolidar requires Python 3.7 or higher.

See other package requirements at requirements.txt.


Use
--------

### Command line (cmd or bash)
a) Execute the package cartolidar:
```
python -m cartolidar [options]
```
Se inicia el menu principal con las herramientas disponibles en cartolidar:
&nbsp;&nbsp;&nbsp;&nbsp;Inicialmente solo está disponible la herramienta qlidtwins

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

b) Execute directly a tool (a module), like qlidtwins.py (if it is accesible):
```
python qlidtwins.py [options]
```
&nbsp;&nbsp;&nbsp;&nbsp;You can check options with:
```
python qlidtwins.py -h
```
To be accesible: it's called from its folder, called with path_to_module or it is in the PATH environmental variable.


### Import cartolider package or its modules or classes (python code)
```
import cartolidar
from cartolidar import clidtools
from cartolidar.clidtools import clidtwins
from cartolidar.clidtools.clidtwins import DasoLidarSource
```


to be continued...



[Ayuda Markdown](https://guides.github.com/features/mastering-markdown/)

[![Actions Status](https://github.com/cartolidar/cartolidar/workflows/Tests/badge.svg)](https://github.com/cartolidar/cartolidar/actions?query=workflow%3ATests)
