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
generate useful information for forestry and natural environment management (dasoLidar variables, DLVs).

This project is in alpha version and, for now, only includes the "clidtwins" tool.

"clidtwins" searchs for similar areas to a reference one in terms of dasoLidar variables (DLVs).

This tool requires, as inputs, raster files with dasoLidar variables in asc format and a reference area (vector layer in shp or gpkg).

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
> DLV (DasoLidar Variables): variables dasométricas, que representan diversos 
> aspectos de la estructura de una formación arbolada, arbustiva o de matorral
> como son la altura dominante, la cobertura, etc.
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
> Clidtwins requiere disponer de ráster(s) con variables dasoLidar (en formato asc)
> y de una capa vectorial con la(s) zona(s) de referencia en formato shp o gpkg.


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
and you can install it for your python environment or run that version from that directory:

- Installation of downloaded files:
```
cd C:\users\yourUser\Downloads\cartolidar-main\
pip install .
```
- Runing downloaded version from github:
```
cd C:\users\yourUser\Downloads\cartolidar-main\
python -m cartolidar [options]
```


Requeriments
----
cartolidar requires Python 3.7 or higher.

See other package requirements in requirements.txt.

Numba requirement (0.53.0) is optional but advisable for speeding up some tasks.


Use
----

### Command line (cmd or bash)
a) Run cartolidar package and select a tool from the main menu (or with the -o flag):
```
python -m {path-to-cartolidar/}cartolidar [options]
```
It starts the main menu with the avaliable tools (or executes the selected option if -o flag is used).

b) Run directly a tool, without displaying the main menu:
```
python {path-to-cartolidar/clidtools/}qlidtwins.py [options]
```

This alpha version includes only qlidtwins tools.

Before runing a tool it's necesary to prepare the required inputs for that tool.

See required inputs and examples below.


>Hay dos opciones para ejecutar una herramienta de clidtools en linea de comandos:
>
>a) Lanzar el paquete cartolidar para mostrar el menu principal y seleccionar una herramienta (o indicar la herramienta con la opción -o).
>
>b) Lanzar directamente la herramienta.
>
>Inicialmente solo está disponible la herramienta qlidtwins.
>
>Antes de ejecutar una herramienta se deben de preparar los inputs que requiere esa herramienta.
>
>Ver mas abajo info sobre los inputs que require cada herramienta (normalmente capas vectoriales o raster) y algunos ejemplos.


[options] for cartolidar package
<pre>
cartolidar general options:
        -h, --help     show this help message and exit
        -V, --version  show program's version number and exit
        -v, --verbose  set verbosity level [default: False]
        -H toolHelp    show help for a cartolidar tool.
                       toolHelp: qlidtwins / clidmerge / etc.
                       By defaut, help is shown without extended args.
        -I, --menuInteracivo  Runs in interactive mode.
        -e             Changes -H behaviour to extended arguments.
        -o menuOption  0. Show main menu; 1. qlidtwins: buscar o verificar
                       zonas analogas a una de referencia (con un determinado
                       patron dasoLidar); 2. qlidmerge: integrar ficheros asc
                       de 2x2 km en una capa tif unica (componer mosaico:
                       merge). Default: 0

    You can show tool-specific help with -H flag. Example:
      python -m cartolidar -H qlidtwins
</pre>


[options] for qlidtwins.py module
<pre>
usage: qlidtwins.py [-h] [-V] [-v] [-q] [-e] [-a MAINACTION]
                    [-i RUTAASCRAIZBASE] [-m RUTACOMPLETAMFE]
                    [-f CARTOMFECAMPOSP] [-p PATRONVECTRNAME]
                    [-l PATRONLAYERNAME] [-c PATRONFIELDNAME]
                    [-t TESTEOVECTRNAME] [-y TESTEOLAYERNAME]
                    [--idProceso IDPROCESO]
                    [listTxtDasoVars [listTxtDasoVars ...]]

positional arguments:
  listTxtDasoVars       Lista de variables dasoLidar: Secuencia de cadenas de
                        texto (uno por variable), del tipo: "texto1",
                        "texto2", etc. de forma que: Opcion a: cada texto es
                        un identificador de DLV. Ejemplo: alt95 fcc05 fcc03
                        (no llevan comas ni comillas) Opcion b: cada texto es
                        una secuencia de cinco elementos separados por comas
                        del tipo: "FileTypeId, NickName, RangoLinf, RangoLsup,
                        NumClases, Movilidad(0-100), Ponderacion(0-10)"
                        Ejemplo: ["alt95,hDom,0,36,18,40,10",
                        "fcc05,FCC,0,100,5,30,8"] [default:
                        ['alt95,Alt95,0,36,18,40,10',
                        'fcc3m,Fcc3m,0,100,5,25,8',
                        'cob050_200cm,CobMt,0,100,5,35,5',
                        'MFE25,MFE25,0,255,255,0,0',
                        'TMasa,TMasa,0,255,255,0,0']]

optional main arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         set verbosity level [default: 2]
  -q, --quiet           Activates quiet mode (mude, not output). Default: 0
  -e, --extraArguments  Activates extra arguments in command line. Default:
                        False
  -I, --menuInteracivo  Runs in interactive mode.
  -a MAINACTION         Accion a ejecutar: 1. Verificar analogia con un
                        determinado patron dasoLidar; 2. Generar raster con
                        presencia de un determinado patron dasoLidar. Default:
                        1
  -i RUTAASCRAIZBASE    Ruta (path) en la que estan los ficheros de entrada
                        con las variables dasolidar. Default:
                        data/asc/PuenteDuero
  -p PATRONVECTRNAME    Nombre del poligono de referencia (patron) para
                        caracterizacion dasoLidar. Default:
                        data/ref/clid_PuenteDuero.gpkg
  -l PATRONLAYERNAME    Nombre del layer del gpkg (en su caso) de referencia
                        (patron) para caracterizacion dasoLidar. Default:
                        vectorPatron
  -c PATRONFIELDNAME    Nombre del campo de la capa de referencia (patron) con
                        el tipo de masa para caracterizacion dasoLidar.
                        Default: TM
  -t TESTEOVECTRNAME    Nombre del poligono de contraste (testeo) para
                        verificar su analogia con el patron dasoLidar.
                        Default: data/ref/clid_PuenteDuero.gpkg
  -y TESTEOLAYERNAME    Nombre del layer del gpkg (en su caso) de contraste
                        (testeo) para verificar su analogia con el patron
                        dasoLidar. Default: vectorTesteo
  -m RUTACOMPLETAMFE    Nombre (con ruta y extension) del fichero con la capa
                        MFE. Default: data/mfe/PuenteDuero/MFE_PuenteDuero.shp
  -f CARTOMFECAMPOSP    Nombre del campo con el codigo numerico de la especie
                        principal o tipo de bosque en la capa MFE. Default:
                        SP1
  --idProceso IDPROCESO
                        Numero aleatorio para identificar el proceso que se
                        esta ejecutando (se asigna automaticamente; no usar
                        este argumento)

See optional extra arguments with -h -e flags or in [Read the Docs - cartolidar](http://cartolidar-docs.readthedocs.io/en/latest/).
</pre>


### Python code
You can import packages, modules, classes of functions from a script.py or
within the python interactive interpreter:
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


Required inputs for qlidtwins or clidtwins
----

See [Read the Docs - cartolidar](http://cartolidar-docs.readthedocs.io/en/latest/) for details.

### Raster input files

This tool requires raster files ("asc" format) with dasoLidarVariables that are used to look for areas similar to a reference one.

These files have to be placed in the path indicated with -i flag.

Each raster file has a dasoLidar variable (DLV): one file <=> one DLV.

> The raster files have to be named as: XXX_YYYY_\*IdFileType\*.asc where:
> - XXX, YYYY are UTM coordinates (miles) that identifies the location (the block).
>   - XXX, YYYY are usually the upper-left corner of a 2x2 km square area
> - \*IdFileType\* is any text that includes a DVL identifier (like alt95, fcc05, etc.).
> 
> Example: 318_4738_alt95.asc and 320_4738_alt95.asc are two files with alt95 variable (blocks: 318_4738 and 320_4738).
> 
> If we want to process two blocks (318_4738 and 320_4738) with two DLVs (e.g. alt95 and fcc05),
> we need these files: 318_4738_alt95.asc, 318_4738_fcc05.asc, 320_4738_alt95.asc, 320_4738_fcc05.asc

The project includes several raster files from Valladolid (data/asc/PuenteDuero/348_4600_2017_alt95.asc, etc.) that can be used as example of use.


### Reference area

The reference area is a vector file (name with path) with one or several polygons (shp or gpkg).

Path: absolute path or relative path refered to working dir (e.g. the one from where the tools is called). 

Indicate this information with -p, -l and -c flags (-l only for gpkg; not for shp)

The cartolidar project includes a vector layer from Valladolid (data/ref/clid_PuenteDuero.gpkg) that can be used as example of use.


### Aditional inputs

It's also advisable to include a layer with forest type codes (forest-type = combination of forest species).

> - This forest-type layer is a vector layer (shp or gpkg)
> - It has to include one field that has the forest type code (type int).
> - Spanish Forest Map (MFE) is usefull for this function. Requires a numeric field wuth forest-type codes.


Outputs
----
Ouput files are placed in a subdirectory of the raster input files directory.

Default name of this subdir is dasoLayers (can be changed with -S flag).



### Use example with python code
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
This method creates a property named "inFilesListAllTypes":
```
myDasolidar.inFilesListAllTypes
```
It is a list that includes, for every DLV, one list of found files corresponding to that DLV.
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
