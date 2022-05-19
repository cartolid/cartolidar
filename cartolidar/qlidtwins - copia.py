#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Utility included in cartolidar project 
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

qlidtwins is an example that uses clidtwins within the cartolidar configuration.
clidtwins provides classes and functions that can be used to search for
areas similar to a reference one in terms of dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''

import sys
import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import pathlib
import time
# import random

__date__ = '2016-2022'
__updated__ = '2022-05-18'
# No se importa nada con: from qlidtwins import *
__all__ = []

# ==============================================================================
# Verbose provisional para la version alpha
if '-vvv' in sys.argv:
    __verbose__ = 3
elif '-vv' in sys.argv:
    __verbose__ = 2
elif '-v' in sys.argv or '--verbose' in sys.argv:
    __verbose__ = 1
else:
    __verbose__ = 0
if __verbose__ > 2:
    print(f'qlidtwins-> __name__:     <{__name__}>')
    print(f'qlidtwins-> __package__ : <{__package__ }>')
# ==============================================================================


# ==============================================================================
# El idProceso sirve para dar nombres unicos a los ficheros de configracion y
# asi poder lanzar trabajos paralelos con distintas configuraciones.
# Sin embargo, qlidtwins no esta pensada para lanzar trabajos en paralelo.
# Mantengo el idProceso por si acaso
if '--idProceso' in sys.argv and len(sys.argv) > sys.argv.index('--idProceso') + 1:
    MAIN_idProceso = sys.argv[sys.argv.index('--idProceso') + 1]
else:
    # MAIN_idProceso = random.randint(1, 999998)
    MAIN_idProceso = 0
    sys.argv.append('--idProceso')
    sys.argv.append(MAIN_idProceso)
# ==============================================================================


# ==============================================================================
try:
    # from clidtools import clidtwins_config as GLO
    from cartolidar.clidtools.clidtwins_config import GLO
    from cartolidar.clidtools.clidtwins import DasoLidarSource
except ModuleNotFoundError:
    sys.stderr.write(f'\nATENCION: para lanzar el modulo qlidtwins.py desde linea de comandos ejecutar:\n')
    sys.stderr.write(f'              $ python -m cartolidar\n')
    sys.stderr.write(f'          Para ver las opciones en linea de comandos:\n')
    sys.stderr.write(f'              $ python -m cartolidar -h\n')
    sys.exit(0)
except Exception as e:
    program_name = 'qlidtwins.py'
    indent = len(program_name) * " "
    sys.stderr.write(program_name + ": " + repr(e) + "\n")
    sys.stderr.write(indent + "  for help use --help")
    sys.exit(0)
# ==============================================================================


# ==============================================================================
# Gestion de errores de argumentos en linea de comandos con argparse
class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


# ==============================================================================
def leerArgumentosEnLineaDeComandos(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = 'v{}'.format(__version__)
    program_build_date = str(__updated__)
    program_version_message = '{} {} ({})'.format(program_name, program_version, program_build_date)
    # program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    # program_shortdesc = __import__('__main__').__doc__
    program_shortdesc = '''  qlidtwins searchs for similar areas to a reference one in terms of
  lidar variables that characterize forest structure (dasoLidar variables).
  Utility included in cartolidar suite.'''

    program_license = '''{}

  Created by @clid {}.
  Licensed GNU General Public License v3 (GPLv3) https://fsf.org/
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.
'''.format(program_shortdesc, str(__date__))

    # ==========================================================================
    # https://docs.python.org/es/3/howto/argparse.html
    # https://docs.python.org/3/library/argparse.html
    # https://ellibrodepython.com/python-argparse
    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license,
            formatter_class=RawDescriptionHelpFormatter,
            fromfile_prefix_chars='@',
            )

        # Opciones:
        parser.add_argument('-v', '--verbose',
                            dest='verbose',
                            action='count', # Cuenta el numero de veces que aparece la v (-v, -vv, -vvv, etc.)
                            # action="store_true",
                            help='set verbosity level [default: %(default)s]',
                            default = GLO.GLBLverbose,)
        parser.add_argument('-V', '--version',
                            action='version',
                            version=program_version_message)

        parser.add_argument('-a',  # '--action',
                            dest='accionPrincipal',
                            type=int,
                            help='Accion a ejecutar: \n1. Verificar analogia con un determinado patron dasoLidar; \n2. Generar raster con presencia de un determinado patron dasoLidar. Default: %(default)s',
                            default = GLO.GLBLaccionPrincipalPorDefecto,)
        parser.add_argument('-i',  # '--inputpath',
                            dest='rutaAscRaizBase',
                            help='Ruta (path) en la que estan los ficheros de entrada con las variables dasolidar. Default: %(default)s',
                            default = GLO.GLBLrutaAscRaizBasePorDefecto,)

        parser.add_argument('-m',  # '--mfepath',
                            dest='rutaCompletaMFE',
                            help='Nombre (con ruta y extension) del fichero con la capa MFE. Default: %(default)s',
                            default = GLO.GLBLrutaCompletaMFEPorDefecto,)
        parser.add_argument('-f',  # '--mfefield',
                            dest='cartoMFEcampoSp',
                            help='Nombre del campo con el codigo numerico de la especie principal o tipo de bosque en la capa MFE. Default: %(default)s',
                            default = GLO.GLBLcartoMFEcampoSpPorDefecto,)

        parser.add_argument('-p',  # '--patron',
                            dest='patronVectrName',
                            help='Nombre del poligono de referencia (patron) para caracterizacion dasoLidar. Default: %(default)s',
                            default = GLO.GLBLpatronVectrNamePorDefecto,)
        parser.add_argument('-l',  # '--patronLayer',
                            dest='patronLayerName',
                            help='Nombre del layer del gpkg (en su caso) de referencia (patron) para caracterizacion dasoLidar. Default: %(default)s',
                            default = GLO.GLBLpatronLayerNamePorDefecto,)
        parser.add_argument('-t',  # '--testeo',
                            dest='testeoVectrName',
                            help='Nombre del poligono de contraste (testeo) para verificar su analogia con el patron dasoLidar. Default: %(default)s',
                            default = GLO.GLBLtesteoVectrNamePorDefecto,)
        parser.add_argument('-y',  # '--testeoLayer',
                            dest='testeoLayerName',
                            help='Nombre del layer del gpkg (en su caso) de contraste (testeo) para verificar su analogia con el patron dasoLidar. Default: %(default)s',
                            default = GLO.GLBLtesteoLayerNamePorDefecto,)

        # ======================================================================
        if TRNS_LEER_EXTRA_ARGS:
            parser.add_argument('-0',  # '--menuInteractivo',
                                dest='menuInteractivo',
                                type=int,
                                help='La aplicacion pregunta en tiempo de ejecucion para elegir o confirmar opciones. Default: %(default)s',
                                default = GLO.GLBLmenuInteractivoPorDefecto,)

            parser.add_argument('-Z',  # '--marcoPatronTest',
                                dest='marcoPatronTest',
                                type=int,
                                help='Zona de analisis definida por la envolvente de los poligonos de referencia (patron) y de chequeo (testeo). Default: %(default)s',
                                default = GLO.GLBLmarcoPatronTestPorDefecto,)
            parser.add_argument('-X',  # '--pixelsize',
                                dest='rasterPixelSize',
                                type=int,
                                help='Lado del pixel dasometrico en metros (pte ver diferencia con GLBLmetrosCelda). Default: %(default)s',
                                default = GLO.GLBLrasterPixelSizePorDefecto,)
            parser.add_argument('-C',  # '--clustersize',
                                dest='radioClusterPix',
                                type=int,
                                help='Numero de anillos de pixeles que tiene el cluster, ademas del central. Default: %(default)s',
                                default = GLO.GLBLradioClusterPixPorDefecto,)

            parser.add_argument('-N',  # '--numvars',
                                dest='nPatronDasoVars',
                                type=int,
                                help='Si es distinto de cero, numero de dasoVars con las que se caracteriza el patron (n primeras dasoVars). Default: %(default)s',
                                default = GLO.GLBLnPatronDasoVarsPorDefecto,)
            parser.add_argument('-L',  # '--level',
                                dest='nivelSubdirExpl',
                                type=int,
                                help='nivel de subdirectorios a explorar para buscar ficheros de entrada con las variables dasolidar. Default: %(default)s',
                                default = GLO.GLBLnivelSubdirExplPorDefecto,)
            parser.add_argument('-D',  # '--outrasterdriver',
                                dest='outRasterDriver',
                                type=int,
                                help='Nombre gdal del driver para el formato de fichero raster de salida para el dasolidar. Default: %(default)s',
                                default = GLO.GLBLoutRasterDriverPorDefecto,)
            parser.add_argument('-S',  # '--outsubdir',
                                dest='outputSubdirNew',
                                type=int,
                                help='Subdirectorio de GLBLrutaAscRaizBasePorDefecto donde se guardan los resultados. Default: %(default)s',
                                default = GLO.GLBLoutputSubdirNewPorDefecto,)
            parser.add_argument('-M',  # '--clipMFEfilename',
                                dest='cartoMFErecorte',
                                type=int,
                                help='Nombre del fichero en el que se guarda la version recortada raster del MFE. Default: %(default)s',
                                default = GLO.GLBLcartoMFErecortePorDefecto,)
            parser.add_argument('-R',  # '--rangovarsfilename',
                                dest='varsTxtFileName',
                                help='Nombre de fichero en el que se guardan los intervalos calculados para todas las variables. Default: %(default)s',
                                default = GLO.GLBLvarsTxtFileNamePorDefecto,)
    
            parser.add_argument('-A',  # '--ambitoTiffNuevo',
                                dest='ambitoTiffNuevo',
                                help='Tipo de ambito para el rango de coordenadas (loteASC, CyL, CyL_nw, etc). Default: %(default)s',
                                default = GLO.GLBLambitoTiffNuevoPorDefecto,)
    
            parser.add_argument('-P',  # '--noDataTiffProvi',
                                dest='noDataTiffProvi',
                                help='NoData temporal para los ficheros raster de salida para el dasolidar. Default: %(default)s',
                                default = GLO.GLBLnoDataTiffProviPorDefecto,)
            parser.add_argument('-T',  # '--noDataTiffFiles',
                                dest='noDataTiffFiles',
                                help='NoData definitivo para los ficheros raster de salida para el dasolidar. Default: %(default)s',
                                default = GLO.GLBLnoDataTiffFilesPorDefecto,)
            parser.add_argument('-O',  # '--noDataTipoDMasa',
                                dest='noDataTipoDMasa',
                                help='NoData definitivo para el raster de salida con el tipo de masa para el dasolidar. Default: %(default)s',
                                default = GLO.GLBLnoDataTipoDMasaPorDefecto,)
            parser.add_argument('-U',  # '--umbralMatriDist',
                                dest='umbralMatriDist',
                                help='Umbral de distancia por debajo del cual se considera que una celda es parecida a otra enla matriz de distancias entre dasoVars. Default: %(default)s',
                                default = GLO.GLBLumbralMatriDistPorDefecto,)

        parser.add_argument('-I', '--idProceso',
                            dest='idProceso',
                            type=int,
                            help='Numero aleatorio para identificar el proceso que se esta ejecutando (se asigna automaticamente; no usar este argumento)',)

        # Argumentos posicionales:
        # Opcionales
        parser.add_argument(dest='listTxtDasoVars',
                            help='Lista de variables dasoLidar: lista de cadenas de texto, del tipo '
                            '["texto1", "texto2", etc] con cada texto consistente en cinco elementos '
                            'separados por comas (elementos que identifican a la variable), con el formato: '
                            '["nick_name, file_type, limite_inf, limite_sup, num_clases, movilidad_interclases_(0-100), ponderacion_(0-10)", etc.]. '
                            '[default: %(default)s]',
                            default = GLO.GLBLlistTxtDasoVarsPorDefecto,
                            nargs='*') # Admite entre 0 y n valores
        # Obligatorios:
        # parser.add_argument('uniParam',
        #                     help='Un parametro unico.',)
        # parser.add_argument(dest='paths',
        #                     help='paths to folder(s) with source file(s)',
        #                     metavar='path',
        #                     nargs='+') # Admite entre 0 y n valores

        # Process arguments
        args = parser.parse_args()

        return args
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return None
    except Exception as e:
        if TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return None



# ==============================================================================
def foo1():
    # Variables globales
    pass


# ==============================================================================
if __verbose__ > 1:
    print(f'\nqlidtwins-> sys.argv (a): {sys.argv}')
try:
    if len(sys.argv) == 0:
        print(f'\nqlidtwins-> Revisar esta forma de ejecucion. sys.argv: <{sys.argv}>')
        sys.exit(0)
    elif sys.argv[0].endswith('__main__.py') and 'cartolidar' in sys.argv[0]:
        if __verbose__ > 1:
            print('\nqlidtwins.py se ha lanzado tras ejecutar el paquete cartolidar desde linea de comandos:')
            print('\t  python -m cartolidar')
        MAIN_configFileNameCfg = 'cartolidar.cfg'
    elif sys.argv[0].endswith('qlidtwins.py'):
        if __verbose__ > 1:
            print('\nqlidtwins.py se esta ejecutando desde linea de comandos:')
            print('\t  python qlidtwins.py')
        MAIN_configFileNameCfg = 'qlidtwins.cfg'
    elif sys.argv[0] == '':
        MAIN_configFileNameCfg = 'qlidtwins.cfg'
        if __verbose__ > 1 or True:
            # Al importar el modulo no se pueden incluir el argumento -v (ni ningun otro)
            print('\nqlidtwins se esta importando desde el interprete interactivo:')
            print('\t>>> from cartolidar import qlidtwins')
            print('o, si esta accesible (en el path):')
            print('\t>>> import qlidtwins')
            print(f'Se ejecuta con las opciones de {MAIN_configFileNameCfg} (o por defecto).')
    else:
        if MAIN_idProceso:
            MAIN_configFileNameCfg = sys.argv[0].replace('.py', '{:006}.cfg'.format(MAIN_idProceso))
        else:
            MAIN_configFileNameCfg = sys.argv[0].replace('.py', '.cfg')
        if __verbose__ > 1 or True:
            print(f'\nqlidtwins.py se esta importando desde el modulo: {sys.argv[0]}')
            print(f'qlidtwins se ejecuta con las opciones de {MAIN_configFileNameCfg} (o por defecto).')
except:
    print('\nqlidtwins-> Revisar MAIN_idProceso:')
    print(f'MAIN_idProceso: <{MAIN_idProceso}> type: {type(MAIN_idProceso)}')
    print(f'sys.argv:       <{sys.argv}>')
    print(f'sys.argv[0]:    <{sys.argv[0]}>')
# ==============================================================================
print(f'\nqlidtwins-> sys.argv (c): {sys.argv}')
print('qlidtwins- Hasta aqui')
quit()

# ==============================================================================
# ========================== Variables globales TRNS ===========================
# ==============================================================================
TRNS_preguntarPorArgumentosEnLineaDeComandos = False
TRNS_LEER_EXTRA_ARGS = False
# ==============================================================================

# ==============================================================================
# ========================== Variables globales MAIN ===========================
# ==============================================================================
MAIN_nombreUsuario = infoUsuario()
# Directorio que depende del entorno:
MAIN_HOME_DIR = str(pathlib.Path.home())
# Directorios de la aplicacion:
MAIN_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PROJ_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))
# Cuando estoy en un modulo dentro de un paquete (subdirectorio):
# MAIN_PROJ_DIR = os.path.abspath(os.path.join(MAIN_FILE_DIR, '..'))  # Equivale a FILE_DIR = pathlib.Path(__file__).parent
MAIN_RAIZ_DIR = os.path.abspath(os.path.join(MAIN_PROJ_DIR, '..'))
MAIN_MDLS_DIR = os.path.join(MAIN_RAIZ_DIR, 'data')
# Directorio desde el que se lanza la app (estos dos coinciden):
MAIN_BASE_DIR = os.path.abspath('.')
MAIN_THIS_DIR = os.getcwd()
# ==============================================================================
# Unidad de disco si MAIN_ENTORNO = 'windows'
MAIN_DRIVE = os.path.splitdrive(MAIN_FILE_DIR)[0]  # 'D:' o 'C:'
# ==============================================================================
if MAIN_FILE_DIR[:12] == '/LUSTRE/HOME':
    MAIN_ENTORNO = 'calendula'
    MAIN_PC = 'calendula'
elif MAIN_FILE_DIR[:8] == '/content':
    MAIN_ENTORNO = 'colab'
    MAIN_PC = 'colab'
else:
    MAIN_ENTORNO = 'windows'
    try:
        if MAIN_nombreUsuario == 'benmarjo':
            MAIN_PC = 'JCyL'
        else:
            MAIN_PC = 'Casa'
    except:
        MAIN_ENTORNO = 'calendula'
        MAIN_PC = 'calendula'


# ==============================================================================
def foo2():
    pass


if __name__ == '__main__' or 'qlidtwins' in __name__:
    # ==========================================================================
    # ========================== Inicio de aplicacion ==========================
    # ==========================================================================
    if __verbose__:
        print('\n{:_^80}'.format(''))
        print('Arrancando qlidtwins')
        print('\t-> ENTORNO:          {}'.format(MAIN_ENTORNO))
        print('\t-> MAIN_PC:          {}'.format(MAIN_PC))
        print('\t-> Usuario:          {}'.format(MAIN_nombreUsuario))
        print('\t-> Modulo principal: {}'.format(sys.argv[0])) # = __file__
        
    # ==========================================================================
    TESTRUN = 0
    PROFILE = 0
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'qlidtwins_profile.txt'
        cProfile.run('leerArgumentosEnLineaDeComandos()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)

    # ==========================================================================
    if (
        'qlidtwins' in __name__
        or len(sys.argv) == 3 and TRNS_preguntarPorArgumentosEnLineaDeComandos
    ):
        if 'qlidtwins' in __name__:
            # El modulo se esta cargando mediante import desde otro modulo o desde el interprete interactivo
            print('\nAVISO: clidqins.py es un modulo escrito para ejecutarse desde linea de comandos:')
            print('\t  python qlidtwins.py')
            print('\tSin embargo, se esta importando desde codigo python.')
            selec = input('\nLanzar el modulo como si se ejecutara desde linea de comandos (S/n): ')
        if len(sys.argv) == 3 and TRNS_preguntarPorArgumentosEnLineaDeComandos:
            print('\nAVISO: no se han introducido argumentos en linea de comandos')
            print('\t-> Para obtener ayuda sobre estos argumentos escribir:')
            print('\t\tpython {} -h'.format(os.path.basename(sys.argv[0])))
            selec = input('\nContinuar con la configuracion por defecto? (S/n): ')
        try:
            if selec.upper() == 'N':
                sys.argv.append("-h")
                print('')
                # print('Fin')
                # sys.exit(0)
            else:
                print('')
        except (Exception) as thisError: # Raised when a generated error does not fall into any category.
            print(f'\nqlidtwins-> ATENCION: revisar codigo. selec: {type(selec)}´<{selec}>')
            print(f'\tRevisar error: {thisError}')
            sys.exit(0)
    
        print('{:=^80}'.format(''))
    # ==========================================================================

    # ==========================================================================
    # ===================== Argumentos en linea de comandos ====================
    # ============ Prevalecen sobre los parametros de configuracion ============
    # ==========================================================================
    if __verbose__ > 1:
        print(f'qlidtwins-> sys.argv (b): {sys.argv}')
    args = leerArgumentosEnLineaDeComandos()
    if args is None:
        print('qlidtwins-> Revisar error en argumentos en linea')
        print('\t-> La funcion leerArgumentosEnLineaDeComandos<> ha dado error')
        sys.exit(0)

    CFG_verbose = args.verbose
    CFG_accionPrincipal = args.accionPrincipal
    if args.rutaAscRaizBase == '':
        CFG_rutaAscRaizBase = MAIN_FILE_DIR
    else:
        CFG_rutaAscRaizBase = args.rutaAscRaizBase
    CFG_rutaCompletaMFE = args.rutaCompletaMFE
    CFG_cartoMFEcampoSp = args.cartoMFEcampoSp
    CFG_patronVectrName = args.patronVectrName
    if args.patronLayerName == 'None':
        CFG_patronLayerName = None
    else:
        CFG_patronLayerName = args.patronLayerName
    CFG_testeoVectrName = args.testeoVectrName
    if args.testeoLayerName == 'None':
        CFG_testeoLayerName = None
    else:
        CFG_testeoLayerName = args.testeoLayerName

    args_listLstDasoVars = []
    for numDasoVar, txtListaDasovar in enumerate(args.listTxtDasoVars):
        listDasoVar = [item.strip() for item in txtListaDasovar.split(',')]
        if len(listDasoVar) <= 5:
            print(f'\nqlidtwins-> ATENCION: el argumento posicional (listTxtDasoVars) debe ser una')
            print(f'\t lista de cadenas de texto (uno por variable), del tipo ["texto1", "texto2", etc]')
            print(f'\t cada uno consistente en cinco elementos separados por comas:')
            print(f'\t\t ["NickName, FileType, RangoLinf, RangoLsup, NumClases, Movilidad(0-100), Ponderacion(0-10)"]')
            print(f'\t Ejemplo: {GLO.GLBLlistTxtDasoVarsPorDefecto}')
            print(f'\t-> La variable {numDasoVar} ({listDasoVar[0]}) solo tiene {len(listDasoVar)} elementos: {listDasoVar}')
            sys.exit(0)
        listDasoVar[2] = int(listDasoVar[2])
        listDasoVar[3] = int(listDasoVar[3])
        listDasoVar[4] = int(listDasoVar[4])
        listDasoVar[5] = int(listDasoVar[5])
        if len(listDasoVar) > 6:
            listDasoVar[6] = int(listDasoVar[6])
        else:
            listDasoVar[6] = 10
        args_listLstDasoVars.append(listDasoVar)
    CFG_listLstDasoVars = args_listLstDasoVars
    # ==========================================================================
    if not 'menuInteractivo' in dir(args):
        args.menuInteractivo = GLO.GLBLmenuInteractivoPorDefecto
    if not 'marcoPatronTest' in dir(args):
        args.marcoPatronTest = GLO.GLBLmarcoPatronTestPorDefecto
    if not 'nPatronDasoVars' in dir(args):
        args.nPatronDasoVars = GLO.GLBLnPatronDasoVarsPorDefecto
    if not 'rasterPixelSize' in dir(args):
        args.rasterPixelSize = GLO.GLBLrasterPixelSizePorDefecto
    if not 'radioClusterPix' in dir(args):
        args.radioClusterPix = GLO.GLBLradioClusterPixPorDefecto
    if not 'nivelSubdirExpl' in dir(args):
        args.nivelSubdirExpl = GLO.GLBLnivelSubdirExplPorDefecto
    if not 'outRasterDriver' in dir(args):
        args.outRasterDriver = GLO.GLBLoutRasterDriverPorDefecto
    if not 'outputSubdirNew' in dir(args):
        args.outputSubdirNew = GLO.GLBLoutputSubdirNewPorDefecto
    if not 'cartoMFErecorte' in dir(args):
        args.cartoMFErecorte = GLO.GLBLcartoMFErecortePorDefecto
    if not 'varsTxtFileName' in dir(args):
        args.varsTxtFileName = GLO.GLBLvarsTxtFileNamePorDefecto
    if not 'ambitoTiffNuevo' in dir(args):
        args.ambitoTiffNuevo = GLO.GLBLambitoTiffNuevoPorDefecto
    if not 'noDataTiffProvi' in dir(args):
        args.noDataTiffProvi = GLO.GLBLnoDataTiffProviPorDefecto
    if not 'noDataTiffFiles' in dir(args):
        args.noDataTiffFiles = GLO.GLBLnoDataTiffFilesPorDefecto
    if not 'noDataTipoDMasa' in dir(args):
        args.noDataTipoDMasa = GLO.GLBLnoDataTipoDMasaPorDefecto
    if not 'umbralMatriDist' in dir(args):
        args.umbralMatriDist = GLO.GLBLumbralMatriDistPorDefecto

    CFG_menuInteractivo = args.menuInteractivo
    CFG_marcoPatronTest = args.marcoPatronTest
    CFG_nPatronDasoVars = args.nPatronDasoVars
    CFG_rasterPixelSize = args.rasterPixelSize
    CFG_radioClusterPix = args.radioClusterPix
    CFG_nivelSubdirExpl = args.nivelSubdirExpl
    CFG_outRasterDriver = args.outRasterDriver
    CFG_outputSubdirNew = args.outputSubdirNew
    CFG_cartoMFErecorte = args.cartoMFErecorte
    CFG_varsTxtFileName = args.varsTxtFileName
    CFG_ambitoTiffNuevo = args.ambitoTiffNuevo
    CFG_noDataTiffProvi = args.noDataTiffProvi
    CFG_noDataTiffFiles = args.noDataTiffFiles
    CFG_noDataTipoDMasa = args.noDataTipoDMasa
    CFG_umbralMatriDist = args.umbralMatriDist
    # ==========================================================================

    # ==========================================================================
    # ======== Provisionalmente pongo aqui un rango de coordenadas UTM =========
    # === Pte rematar que se puedan definir con el parametro ambitoTiffNuevo, ==
    # ============ en linea de comandos o a partir de los shapes ===============
    # ==========================================================================
    CFG_marcoCoordMinX = 318000
    CFG_marcoCoordMaxX = 322000
    CFG_marcoCoordMinY = 4734000
    CFG_marcoCoordMaxY = 4740000
    # ==========================================================================

    # ==========================================================================
    if args.verbose:
        if args.verbose > 1:
            if len(sys.argv) == 3:
                if os.path.exists(MAIN_configFileNameCfg):
                    infoConfiguracionUsada = f' (valores leidos del fichero de configuracion, {MAIN_configFileNameCfg})'
                else:
                    infoConfiguracionUsada = ' (valores "de fabrica" incluidos en codigo, clidtwins_config.py)'
            else:
                infoConfiguracionUsada = ' (de linea de comandos, o de config por defecto)'
        else:
            infoConfiguracionUsada = ''
        print('\n{:_^80}'.format(''))
        print(f'Parametros de configuracion principales{infoConfiguracionUsada}:')
        accionesPrincipales = ['1. Verificar analogia con un determinado patron dasoLidar.', '2. Generar raster con presencia de un determinado patron dasoLidar.']
        print('\t--> Accion: {}'.format(accionesPrincipales[CFG_accionPrincipal - 1]))
        print('\t--> Listado de dasoVars [nombre, codigo fichero, limite inf, limite sup, num clases, movilidad_interclases (0-100), ponderacion (0-10)]:')
        for numDasoVar, listDasoVar in enumerate(args_listLstDasoVars):
            print('\t\tVariable {}: {}'.format(numDasoVar, listDasoVar))
        print('\t--> Rango de coordenadas UTM:')
        if CFG_marcoPatronTest:
            print('\t\tSe adopta la envolvente de los shapes de referenia (patron) y chequeo (testeo).')
            print('\t\tVer valores mas adelante.')
        elif (
            CFG_marcoCoordMinX == 0
            or CFG_marcoCoordMaxX == 0
            or CFG_marcoCoordMinY == 0
            or CFG_marcoCoordMaxY == 0
            ):
            print('\t\tNo se han establecido coordenadas para la zona de estudio.')
            print('\t\tSe adopta la envolvente de los ficheros con variables dasoLidar.')
        else:
            print(
                '\t\tX {:07f} - {:07f} -> {:04.0f} m:'.format(
                    CFG_marcoCoordMinX, CFG_marcoCoordMaxX,
                    CFG_marcoCoordMaxX - CFG_marcoCoordMinX
                )
            )
            print(
                '\t\tY {:07f} - {:07f} -> {:04.0f} m:'.format(
                    CFG_marcoCoordMinY, CFG_marcoCoordMaxY,
                    CFG_marcoCoordMaxY - CFG_marcoCoordMinY
                )
            )
        print('\t--> Ruta base (raiz) y ficheros:')
        print('\t\trutaAscRaizBase: {}'.format(CFG_rutaAscRaizBase))
        print('\t\tpatronVectrName: {}'.format(CFG_patronVectrName))
        print('\t\tpatronLayerName: {} {}'.format(CFG_patronLayerName, type(CFG_patronLayerName)))
        print('\t\ttesteoVectrName: {}'.format(CFG_testeoVectrName))
        print('\t\ttesteoLayerName: {}'.format(CFG_testeoLayerName))
        print('\t--> Cartografia de cubiertas (MFE):')
        print('\t\trutaCompletaMFE: {}'.format(CFG_rutaCompletaMFE))
        print('\t\tcartoMFEcampoSp: {}'.format(CFG_cartoMFEcampoSp))
        if args.verbose > 1:
            print('\t--> verbose: {}'.format(CFG_verbose))
        print('{:=^80}'.format(''))
    if args.verbose > 1:
        print('->> qlidtwins-> args:', args)
        # print('\t->> dir(args):', dir(args))
        CFG_listTxtDasoVars = args.listTxtDasoVars
        print('->> Lista de dasoVars en formato para linea de comandos:')
        print('\t{}'.format(CFG_listTxtDasoVars))
        print('{:=^80}'.format(''))

    argsFileName = sys.argv[0].replace('.py', '.args')
    try:
        with open(argsFileName, mode='w+') as argsFileControl:
            if 'accionPrincipal' in dir(args):
                argsFileControl.write(f'-a={args.accionPrincipal}\n')
            if 'rutaAscRaizBase' in dir(args):
                argsFileControl.write(f'-i={args.rutaAscRaizBase}\n')
            if 'rutaCompletaMFE' in dir(args):
                argsFileControl.write(f'-m={args.rutaCompletaMFE}\n')
            if 'cartoMFEcampoSp' in dir(args):
                argsFileControl.write(f'-f={args.cartoMFEcampoSp}\n')
            if 'patronVectrName' in dir(args):
                argsFileControl.write(f'-p={args.patronVectrName}\n')
            if 'patronLayerName' in dir(args):
                argsFileControl.write(f'-l={args.patronLayerName}\n')
            if 'testeoVectrName' in dir(args):
                argsFileControl.write(f'-t={args.testeoVectrName}\n')
            if 'testeoLayerName' in dir(args):
                argsFileControl.write(f'-y={args.testeoLayerName}\n')
            if 'verbose' in dir(args):
                argsFileControl.write(f'-v={args.verbose}\n')

            if 'menuInteractivo' in dir(args):
                argsFileControl.write(f'-0={args.menuInteractivo}\n')
            if 'marcoPatronTest' in dir(args):
                argsFileControl.write(f'-Z={args.marcoPatronTest}\n')
            if 'rasterPixelSize' in dir(args):
                argsFileControl.write(f'-X={args.rasterPixelSize}\n')
            if 'radioClusterPix' in dir(args):
                argsFileControl.write(f'-C={args.radioClusterPix}\n')
            if 'nPatronDasoVars' in dir(args):
                argsFileControl.write(f'-N={args.nPatronDasoVars}\n')
            if 'nivelSubdirExpl' in dir(args):
                argsFileControl.write(f'-L={args.nivelSubdirExpl}\n')
            if 'outRasterDriver' in dir(args):
                argsFileControl.write(f'-D={args.outRasterDriver}\n')
            if 'outputSubdirNew' in dir(args):
                argsFileControl.write(f'-S={args.outputSubdirNew}\n')
            if 'cartoMFErecorte' in dir(args):
                argsFileControl.write(f'-M={args.cartoMFErecorte}\n')
            if 'varsTxtFileName' in dir(args):
                argsFileControl.write(f'-R={args.varsTxtFileName}\n')
            if 'ambitoTiffNuevo' in dir(args):
                argsFileControl.write(f'-A={args.ambitoTiffNuevo}\n')
            if 'noDataTiffProvi' in dir(args):
                argsFileControl.write(f'-P={args.noDataTiffProvi}\n')
            if 'noDataTiffFiles' in dir(args):
                argsFileControl.write(f'-T={args.noDataTiffFiles}\n')
            if 'noDataTipoDMasa' in dir(args):
                argsFileControl.write(f'-O={args.noDataTipoDMasa}\n')
            if 'umbralMatriDist' in dir(args):
                argsFileControl.write(f'-U={args.umbralMatriDist}\n')

            for miDasoVar in args.listTxtDasoVars:
                argsFileControl.write(f'{miDasoVar}\n')
    except:
        if args.verbose > 1:
            print(f'qlidtwins-> No se ha podido crear el fichero de argumentos para linea de comandos: {argsFileName}')

    if args.verbose > 1:
        if args.verbose > 1:
            if len(sys.argv) == 3 or not TRNS_LEER_EXTRA_ARGS:
                if os.path.exists(MAIN_configFileNameCfg):
                    infoConfiguracionUsada = f' (valores leidos del fichero de configuracion, {MAIN_configFileNameCfg})'
                else:
                    infoConfiguracionUsada = ' (valores "de fabrica" incluidos en codigo, clidtwins_config.py)'
            else:
                infoConfiguracionUsada = ' (de linea de comandos, o de config por defecto)'
        else:
            infoConfiguracionUsada = ''
        print('\n{:_^80}'.format(''))
        print(f'Parametros de configuracion adicionales{infoConfiguracionUsada}:')
        print('\t--> menuInteractivo: {}'.format(CFG_menuInteractivo))
        print('\t--> marcoPatronTest: {}'.format(CFG_marcoPatronTest))
        print('\t--> nPatronDasoVars: {}'.format(CFG_nPatronDasoVars))
        print('\t--> rasterPixelSize: {}'.format(CFG_rasterPixelSize))
        print('\t--> radioClusterPix: {}'.format(CFG_radioClusterPix))
        print('\t--> nivelSubdirExpl: {}'.format(CFG_nivelSubdirExpl))
        print('\t--> outRasterDriver: {}'.format(CFG_outRasterDriver))
        print('\t--> outputSubdirNew: {}'.format(CFG_outputSubdirNew))
        print('\t--> cartoMFErecorte: {}'.format(CFG_cartoMFErecorte))
        print('\t--> varsTxtFileName: {}'.format(CFG_varsTxtFileName))
        print('\t--> ambitoTiffNuevo: {}'.format(CFG_ambitoTiffNuevo))
        print('\t--> noDataTiffProvi: {}'.format(CFG_noDataTiffProvi))
        print('\t--> noDataTiffFiles: {}'.format(CFG_noDataTiffFiles))
        print('\t--> noDataTipoDMasa: {}'.format(CFG_noDataTipoDMasa))
        print('\t--> umbralMatriDist: {}'.format(CFG_umbralMatriDist))
        print('{:=^80}'.format(''))

    # ==========================================================================
    # ============================ Inicio diferido =============================
    # ==========================================================================
    # Inicio diferido en Calendula
    print('\n{:_^80}'.format(''))
    if MAIN_ENTORNO != 'windows' or (CFG_accionPrincipal != 0 and not CFG_menuInteractivo):
        print('qlidtwins-> Ejecucion automatizada, sin intervencion de usuario')
        if False:
            esperar = 60 * 60 * 0.001
            print(
                '\tIniciando qlidtwins-> Hora: {}'.format(
                    time.asctime(time.localtime(time.time()))
                )
            )
            print(
                '\tEjecucion diferida hasta: {}'.format(
                    time.asctime(time.localtime(time.time() + esperar))
                )
            )
            print('\tEsperando {} minutos ({} horas) ...'.format(int(esperar/60), round(esperar/3600,2)))
            time.sleep(esperar)
            timeInicio = time.asctime(time.localtime(time.time()))
            print('\tInicio efectivo:        {}'.format(str(timeInicio)))
    else:
        print('qlidtwins-> Ejecucion interactiva, con intervencion de usuario. ARGSopcioGLBLaccionPrincipalnElegida:', CFG_accionPrincipal, CFG_menuInteractivo)
    print('{:=^80}'.format(''))
    # ==========================================================================

    if CFG_verbose:
        print('\n{:_^80}'.format(''))
        print('qlidtwins-> Creando objeto de la clase DasoLidarSource...')
    myDasolidar = DasoLidarSource(
        LCL_listLstDasoVars=CFG_listLstDasoVars,
        LCL_nPatronDasoVars=CFG_nPatronDasoVars,  # opcional
        LCL_verboseProgress=CFG_verbose,  # opcional
        LCL_leer_extra_args=TRNS_LEER_EXTRA_ARGS,  # opcional
    )
    if CFG_verbose:
        print('{:=^80}'.format(''))

    if CFG_verbose:
        print('\n{:_^80}'.format(''))
        print('qlidtwins-> Ejecutando rangeUTM...')
    myDasolidar.rangeUTM(
        LCL_marcoCoordMinX=CFG_marcoCoordMinX,
        LCL_marcoCoordMaxX=CFG_marcoCoordMaxX,
        LCL_marcoCoordMinY=CFG_marcoCoordMinY,
        LCL_marcoCoordMaxY=CFG_marcoCoordMaxY,
    )
    if CFG_verbose:
        print('{:=^80}'.format(''))

    if CFG_verbose:
        print('\n{:_^80}'.format(''))
        print('qlidtwins-> Ejecutando searchSourceFiles...')
    myDasolidar.searchSourceFiles(
        LCL_rutaAscRaizBase=CFG_rutaAscRaizBase,
        LCL_nivelSubdirExpl=CFG_nivelSubdirExpl,  # opcional
        LCL_outputSubdirNew=CFG_outputSubdirNew,  # opcional
    )
    if CFG_verbose:
        print('{:=^80}'.format(''))

    if CFG_verbose:
        print('\n{:_^80}'.format(''))
        print('qlidtwins-> Ejecutando createAnalizeMultiDasoLayerRasterFile...')
    myDasolidar.createAnalizeMultiDasoLayerRasterFile(
        LCL_rasterPixelSize=CFG_rasterPixelSize,
        LCL_rutaCompletaMFE=CFG_rutaCompletaMFE,
        LCL_cartoMFEcampoSp=CFG_cartoMFEcampoSp,
        LCL_patronVectrName=CFG_patronVectrName,
        LCL_patronLayerName=CFG_patronLayerName,
        # LCL_outRasterDriver=CFG_outRasterDriver,
        # LCL_cartoMFErecorte=CFG_cartoMFErecorte,
        # LCL_varsTxtFileName=CFG_varsTxtFileName,
    )
    if CFG_verbose:
        print('{:=^80}'.format(''))

    if CFG_accionPrincipal == 0 or CFG_menuInteractivo:
        pass
    elif CFG_accionPrincipal == 1:
        if CFG_verbose:
            print('\n{:_^80}'.format(''))
            print('qlidtwins-> Ejecutando chequearCompatibilidadConTesteoShape...')
        myDasolidar.chequearCompatibilidadConTesteoVector(
            LCL_testeoVectrName=CFG_testeoVectrName,
            LCL_testeoLayerName=CFG_testeoLayerName,
            )
    elif CFG_accionPrincipal == 2:
        if CFG_verbose:
            print('\n{:_^80}'.format(''))
            print('qlidtwins-> Ejecutando generarRasterCluster...')
        myDasolidar.generarRasterCluster(
            LCL_radioClusterPix=CFG_radioClusterPix,
        )
    if CFG_accionPrincipal:
        if CFG_verbose:
            print('{:=^80}'.format(''))
    print('\nqlidtwins-> Fin.')
