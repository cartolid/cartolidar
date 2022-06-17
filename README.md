[![pypi](https://img.shields.io/pypi/v/cartolidar.svg)](https://pypi.org/project/cartolidar/)
[![py](https://img.shields.io/pypi/pyversions/cartolidar.svg)](https://pypi.org/project/cartolidar/)
[![Coverage Status](https://codecov.io/gh/cartolidar/cartolidar/branch/main/graph/badge.svg)](https://codecov.io/gh/cartolidar/cartolidar)
[![Join the chat at https://gitter.im/cartolidar/cartolidar](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/cartolidar/cartolidar?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/cartolidar/cartolidar/main)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![cartolidar Logo](https://secure.gravatar.com/avatar/ea09c6d439dc57633702164f23b264e5 "clid image")


CartoLidar
----------

Lidar data processing tools focused on Spanish PNOA datasets

> Herramientas para procesado de datos Lidar del PNOA

Lidar PNOA: https://pnoa.ign.es/el-proyecto-pnoa-lidar


Introduction
------------

CartoLidar is a collection of tools to process lidar files ("las" and "laz") and 
generate other products related to forestry and natural environment management.

This project is in alpha version and includes only the "clidtwins" tool.

"clidtwins" searchs for similar areas to a reference one in terms of dasoLidar variables (DLVs)

DLV: Lidar variables that describe or characterize forest or land cover structure.

> CartoLidar es una colección de herramientas destinadas a procesar ficheros lidar 
> ("las" y "laz") para clasificar los puntos mediante inteligencia artificial (GANs)
> y generar ficheros ráster con DEM y DLVs.
> 
> GAN (Generative Adversarial Networks): arquitectura de DL basada en redes neuronales en la que
> se optimiza simultanemante un discriminador y un generador para obtener imágenes verosímiles
> a partir de inputs que, en este caso, no son aleatorios (sino variables lidar).
> 
> DEM (Digital Elevation Model): modelos digitales de elevaciones (MDT, MDS)
> 
> DLV (Daso Lidar Variables): variables dasoLidar, que representan diversos 
> aspectos de la estructura de una formación arbolada, arbustiva o de matorral.
> 
> CartoLidar también incluye herramientas adicionales para generar otros 
> productos de utilidad en selvicultura y otras areas de gestión del medio 
> natural a partir de los ficheros ráster con las DLVs. 
> 
> El proyecto está en fase alpha e incluye únicamente la herramienta adicional "clidtwins". 
> Las herramientas de procesado de ficheros Lidar (clasificación de puntos, generación de DEM y DLVs)) 
> se incorporará a github a partir del cuarto trimestre de 2022.
> 
> La herramienta clidtwins está destinada a buscar zonas similares a una(s) 
> de referencia en términos de determinadas variables dasoLidar (DLVs).


\+ info: [Read the Docs - cartolidar](http://cartolidar-docs.readthedocs.io/en/latest/)
(página en construcción)


Install
--------

1. Official version from [pypi - cartolidar](https://pypi.org/project/cartolidar/):
```
pip install cartolidar
```
or (in case you are working through a proxy server):
```
pip install cartolidar --proxy https://user:password@proxyserver:port
```

2. Development version from [github - cartolidar](https://github.com/cartolid/cartolidar):

You can download the zip version, uncompress it somewhere, i.e.:
```
C:\users\yourUser\Downloads\cartolidar-main\
```
That folder contains a setup.py file (and the other components of the project)
and you can install cartolidar from that directory for your python environment:
```
cd C:\users\yourUser\Downloads\cartolidar-main\
pip install .
```


Requeriments
----
cartolidar requires Python 3.7 or higher.

See other package requirements in requirements.txt.

Numba requirement (0.53.0) is optional but advisable for speeding up some tasks.


Use
---

### Command line (cmd or bash)
a) Run cartolidar package:
```
python -m cartolidar [options]
```
It starts the main menu with the avaliable tools.

This alpha version includes only qlidtwins tools, wich make use of clidtwins package.

>Se inicia el menu principal con las herramientas disponibles en cartolidar.
>
>Inicialmente solo está disponible la herramienta qlidtwins que utliza el paquete clidtwins.

[options] 
<pre>
cartolidar general options:
        -h, --help     show this help message and exit
        -V, --version  show program's version number and exit
        -v, --verbose  set verbosity level [default: False]
        -H toolHelp    show help for a cartolidar tool.
                       toolHelp: qlidtwins / clidmerge / etc.
                       By defaut, help is shown without extended args.
        -e             Changes -H behaviour to extended arguments.
        -o menuOption  0. Show main menu; 1. qlidtwins: buscar o verificar
                       zonas analogas a una de referencia (con un determinado
                       patron dasoLidar); 2. qlidmerge: integrar ficheros asc
                       de 2x2 km en una capa tif unica (componer mosaico:
                       merge). Default: 0

    You can show tool-specific help with -H flag. Example:
      python -m cartolidar -H qlidtwins
</pre>


b) It is also possible to run a tool without displaying the main menu (if the module is accesible). E.g.:
```
python qlidtwins.py [options]
```
or
```
python {path-to-cartolidar}/qlidtwins.py [options]
```
example:
```
python D:\cartolidar\cartolidar/qlidwins.py [options]
```
A module is accesible if is called from its folder, is called with path_to_module or its folder is in the PATH environmental variable.


Use -h to show help for a cartolidar tool. Example for qlidtwins (qlidtwins.py has to be accesible):
```
python qlidtwins.py -h
```

A module is accesible if is called from its folder, is called with path_to_module or its folder is in the PATH environmental variable.


### Python code
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
from cartolidar import qlidtwins
```
In this case, there are no options: it runs with qlidtwins.cfg configuration (if exists) or default configuration.


Required inputs
----
Read [Read the Docs - cartolidar](http://cartolidar-docs.readthedocs.io/en/latest/) for details.

clidtwins reads files in "asc" format (single vector layers) each with a dasoLidar variable (DLV).

> Those files have to be named as: XXX_YYYY_\*IdFileType\*.asc where:
> - XXX, YYYY are UTM coordinates (miles) that identifies the location (the block).
>   - XXX, YYYY are usually the upper-left corner of a 2x2 km square area
> - \*IdFileType\* is any string that includes a DVL identifier (like alt95, fcc05, etc.).
> 
> Example: 318_4738_alt95.asc and 320_4738_alt95.asc are two files with alt95 variable (blocks: 318_4738 and 320_4738).
> 
> If we want to process two blocks (318_4738 and 320_4738) with two DLVs (e.g. alt95 and fcc05), we need these files:
> 318_4738_alt95.asc, 318_4738_fcc05.asc, 320_4738_alt95.asc, 320_4738_fcc05.asc


It's also advisable to include a layer with forest type codes.

> TODO: describe procedure



Use example with python code
----
Procedure:

1. Import package (or Class) and instantiate DasoLidarSource Class:
```
from cartolidar.clidtools.clidtwins import DasoLidarSource
myDasolidar = DasoLidarSource()
```


2. Delimit the prospecting area (optional):
```
myDasolidar.setRangeUTM(
    LCL_marcoCoordMiniX=348000,
    LCL_marcoCoordMaxiX=350000,
    LCL_marcoCoordMiniY=4598000,
    LCL_marcoCoordMaxiY=4602000,
)
```


3. Search for dasoLidar files in the prospecting zone (if any):
> First argument (LCL_listLstDasoVars) is a string with a sequence of DLV identifiers
> and second one (LCL_rutaAscRaizBase) is a path to look for the files with those DLV ids.
```
myDasolidar.searchSourceFiles(
    LCL_listLstDasoVars='Alt95,Fcc05,Fcc03',
    LCL_rutaAscRaizBase='C:/myAscFiles',
)
```
This method creates a property named inFilesListAllTypes. It is a list for every DLV,
each with the list of found file tuples for that file type.
It only includes files of blocks that have all the file types (one file type = one DLV).
Every file tuple consist of a file path and file name.


4. Create a raster (Tiff) file from the DLV found files:

> The createMultiDasoLayerRasterFile method requires the name (with path)
> of the forest type or land cover type vector layer (e.g. Spanish Forest Map -MFE25-)
> and the name of the field (type int) with the forest or land cover type
> identifier (e.g. main species code).
```
myDasolidar.createMultiDasoLayerRasterFile(
    LCL_rutaCompletaMFE='C:/mfe25/24_mfe25.shp',
    LCL_cartoMFEcampoSp='SP1',
)
```

5. Analyze the ranges of every DLV in the reference area:

> The analyzeMultiDasoLayerRasterFile method requires the name (with path)
> of the vector file with the reference polygon for macthing (shp or gpkg).
> If it is ageopackage, the layer name is also required.
```
myDasolidar.analyzeMultiDasoLayerRasterFile(
    LCL_patronVectrName='C:/vector/CorralesPlots.gpkg,
    LCL_patronLayerName='plot01Quercus',
)
```


6. Create new Tiff files with similar zones and proximity to reference one (patron):
```
myDasolidar.generarRasterCluster()
```



7. After carrying out steps 5 and 6 for several reference ones (example 1, 2, 3):
```
listaTM = [1, 2, 3]
myDasolidar.asignarTipoDeMasaConDistanciaMinima(listaTM)
```


to be continued...

<!-- This content will not appear in the rendered Markdown -->


[Ayuda Markdown de github](https://guides.github.com/features/mastering-markdown/)
[Ayuda Markdown de github](https://docs.github.com/es/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
[Ayuda Markdown de markdownguide](https://www.markdownguide.org/getting-started)


[![Actions Status](https://github.com/cartolidar/cartolidar/workflows/Tests/badge.svg)](https://github.com/cartolidar/cartolidar/actions?query=workflow%3ATests)
